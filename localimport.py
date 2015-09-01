# Copyright (C) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '1.4.4'

import glob, os, pkgutil, sys, traceback
class _localimport(object):
    """
    Secure import mechanism that restores the previous global importer
    state after the context-manager exits. Modules imported from the local
    site will be moved into :attr:`modules`.
    Features:
        - Takes :mod:`pkg_resources` namespace package dictionary into
          account.
        - Removes modules from the global scope, but only if they were
          import from the local site (determined by :attr:`path`).
    .. code-block:: python
        with _localimport('res/modules'):
            import some_package
    *New in Version 1.4.0*:
        - .pth files are now evaluated
        - .egg files/folders are automatically expanded
        - removed *eggs* parameter of constructor
    .. author:: Niklas Rosenstein <rosensteinniklas@gmail.com>
    .. license:: MIT
    Attributes:
        path (list of str):
            The paths from which modules should be imported. These
            will also be used to determine if a module was imported
            from the local site and wether it should be released after
            the localimport is complete.
        meta_path (list of importers):
            A list of importer objects that will be prepended to
            :data:`sys.meta_path` during the localimport. Use of meta
            importers is discouraged as it could lead to problems
            determining whether a module is from the local site.
        modules (dict of str: module):
            Dictionary of the modules imported from the local site.
        in_context (bool):
            True when the localimport context-manager is active.
    """

    _py3k = sys.version_info[0] >= 3
    _string_types = (str,) if _py3k else (basestring,)

    def __init__(self, path, parent_dir=os.path.dirname(__file__)):
        super(_localimport, self).__init__()
        self.path = []
        if isinstance(path, self._string_types):
            path = [path]
        for path_name in path:
            if not os.path.isabs(path_name):
                path_name = os.path.join(parent_dir, path_name)

            self.path.append(path_name)
            self.path.extend(glob.glob(os.path.join(path_name, '*.egg')))

        self.meta_path = []
        self.modules = {}
        self.in_context = False

    def __enter__(self):
        # pkg_resources comes with setuptools.
        try: import pkg_resources; nsdict = pkg_resources._namespace_packages.copy()
        except ImportError: nsdict = None

        # Save the global importer state.
        self.state = {
            'nsdict': nsdict,
            'nspaths': {},
            'path': sys.path[:],
            'meta_path': sys.meta_path[:],
            'disables': {},
        }

        # Update the systems meta path.
        sys.path[:] = self.path + sys.path
        sys.meta_path[:] = self.meta_path + sys.meta_path

        # If this function is called not the first time, we need to
        # restore the modules that have been imported with it and
        # temporarily disable the ones that would be shadowed.
        for key, mod in self.modules.items():
            try: self.state['disables'][key] = sys.modules.pop(key)
            except KeyError: pass
            sys.modules[key] = mod

        # Update the __path__ of all namespace modules.
        for key, mod in sys.modules.items():
            if hasattr(mod, '__path__'):
                self.state['nspaths'][key] = mod.__path__[:]
                mod.__path__ = pkgutil.extend_path(mod.__path__, mod.__name__)
                new = mod.__path__[:]

        # Evaluate .pth files.
        for path_name in self.path:
            for fn in glob.glob(os.path.join(path_name, '*.pth')):
                self._eval_pth(fn, path_name)

        self.in_context = True
        return self

    def __exit__(self, *__):
        if not self.in_context:
            raise RuntimeError('context not entered')

        # Restore the original __path__ value of namespace packages.
        for key, path in self.state['nspaths'].items():
            sys.modules[key].__path__ = path

        # Move all meta path objects to self.meta_path that have not
        # been there before and have not been in the list before.
        for meta in sys.meta_path:
            if meta is not self and meta not in self.state['meta_path']:
                if meta not in self.meta_path:
                    self.meta_path.append(meta)

        # Move all modules that shadow modules of the original system
        # state or modules that are from any of the _localimport context
        # paths away.
        modules = sys.modules.copy()
        for key, mod in modules.items():
            force_pop = False
            filename = getattr(mod, '__file__', None)
            if not filename and key not in sys.builtin_module_names:
                parent = key.rsplit('.', 1)[0]
                if parent in modules:
                    filename = getattr(modules[parent], '__file__', None)
                else:
                    force_pop = True
            if force_pop or (filename and self._is_local(filename)):
                self.modules[key] = sys.modules.pop(key)

        # Bring all disabled modules back and restore the
        # the original state.
        sys.modules.update(self.state['disables'])
        sys.path[:] = self.state['path']
        sys.meta_path[:] = self.state['meta_path']
        try:
            import pkg_resources
            pkg_resources._namespace_packages.clear()
            pkg_resources._namespace_packages.update(self.state['nsdict'])
        except ImportError: pass

        self.in_context = False
        del self.state

    def _is_local(self, filename):
        """
        _is_local(filename) -> bool.
        Returns True if *filename* is the subpath of any of the paths
        in :attr:`path` and False if not.
        """

        filename = os.path.abspath(filename)
        for path_name in self.path:
            path_name = os.path.abspath(path_name)
            if self._is_subpath(filename, path_name):
                return True
        return False

    def _eval_pth(self, filename, sitedir):
        """
        Evaluates the ``*.pth`` file *filename* and appends the
        paths to :attr:`self.path`.
        """

        if not os.path.isfile(filename):
            return
        with open(filename, 'r') as fp:
            for index, line in enumerate(fp):
                if line.startswith('import'):
                    line_fn = '{0}#{1}'.format(filename, index + 1)
                    try:
                        exec compile(line, line_fn, 'exec')
                    except BaseException:
                        traceback.print_exc()
                else:
                    index = line.find('#')
                    if index > 0: line = line[:index]
                    line = line.strip()
                    if not os.path.isabs(line):
                        line = os.path.join(os.path.dirname(filename), line)
                    line = os.path.normpath(line)
                    if line and line not in self.path:
                        self.path.append(line)

    @staticmethod
    def _is_subpath(path, ask_dir):
        """
        _is_subpath(path, ask_dir) -> bool
        Returns True if *path* points to the same or a subpath of
        *ask_dir*.
        """

        try:
            relpath = os.path.relpath(path, ask_dir)
        except ValueError:
            return False  # on Windows if the drive letters don't match
        return relpath == os.curdir or not relpath.startswith(os.pardir)
