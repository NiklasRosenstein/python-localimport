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
__version__ = '1.1'

import glob, os, sys
class _localimport(object):
    """
    This class provides a secure import mechanism to prevent name
    clashes in the global module space and allow add-on Python code
    and applications to import their own local modules even in
    embedded environments. Client code is supposed to use a source
    copy of this class directly in the application.

    The *path* parameter can be either a string or list of strings
    that will be prepended to :data:`sys.path`. All paths are, if not
    absolute, relative to the specified *parent_dir* which defaults
    to ``os.path.dirname(__file__)``.

    If *eggs* is True, files and folders inside any path of the
    specified *paths* that end with ``.egg`` will be used in addition
    to the specified *path*.

    .. code-block:: python

      with _localimport('lib') as importer:
          some_package = importer.load('some_package')
      # // or //
      with _localimport('lib', eggs=True) as importer:
          import some_package

    Inside the with-context of the *_localimport*, the builtin
    ``__import__()`` function is hooked to allow capturing the
    ``import ...`` statements inside the with-context, automatically
    disabling existing modules that could shadow the import from the
    local directory.

    .. codeauthor:: Niklas Rosenstein <rosensteinniklas@gmail.com>
    .. license:: MIT

    -------------------------------------------------------------------

    .. attribute:: path

        A list of paths that will be used to import modules from.

    .. attribute:: meta_path

        A list of importer objects that will be prepended to
        :data:`sys.path`. When leaving the *_localimport* context,
        this list will be updated to contain all importer objects that
        have been added from imported modules.

    .. attribute:: modules

        A dictionary like :data:`sys.modules` that contains all
        modules imported via the *_localimport* context from the paths
        in the :attr:`path` list.

    .. attribute:: in_context

        True if the importer has entered the context, False if not.
    """

    _py3k = sys.version_info[0] >= 3
    _builtins = __import__('builtins') if _py3k else __import__('__builtin__')
    _string_types = (str,) if _py3k else (basestring,)

    def __init__(self, path, parent_dir=os.path.dirname(__file__), eggs=False):
        super(_localimport, self).__init__()
        self.path = []
        if isinstance(path, self._string_types):
            path = [path]
        for path_name in path:
            if not os.path.isabs(path_name):
                path_name = os.path.join(parent_dir, path_name)
            self.path.append(path_name)
            if eggs:
                self.path.extend(glob.glob(os.path.join(path_name, '*.egg')))
        self.meta_path = []
        self.modules = {}
        self.in_context = False

    def __enter__(self):
        """
        Called when the with-context is entered. Saves the global
        importer state which will be restored in :meth:`__exit__`.
        Also adds *self* to :data:`sys.meta_path` so it can check
        on-demand if a module would shadow another.
        """

        # Override the builtin import mechanism and save the old.
        self.original_import = self._builtins.__import__
        import_hook = self._get_import_hook(self._builtins.__import__)
        self._mock(self._builtins, '__import__')(import_hook)

        self.state = {
            'captured_globals': globals(),
            'path': sys.path[:],
            'meta_path': sys.meta_path[:],
            'disables': {},
        }

        sys.path[:] = self.path + sys.path
        sys.meta_path[:] = self.meta_path

        # Restore all existing imported modules from the _localimport
        # and disables those that would be overwritten.
        # todo: what about None-modules?
        for key, mod in self.modules.items():
            try:
                self.state['disables'][key] = sys.modules.pop(key)
            except KeyError:
                pass
            sys.modules[key] = mod

        self.in_context = True
        return self

    def __exit__(self, *__):
        """
        Restore the global importer state and move newly imported
        modules and added *meta_path* objects to the *_localimport*
        object.
        """

        if not self.in_context:
            raise RuntimeError('context not entered')

        # Unmock the import hook that we created in __enter__().
        self._unmock(self._builtins, '__import__')
        del self.original_import

        # Move all meta path objects to self.meta_path that have not
        # been there before and have not been in the list before.
        for meta in sys.meta_path:
            if meta is not self and meta not in self.state['meta_path']:
                if meta not in self.meta_path:
                    self.meta_path.append(meta)

        # Move all modules that shadow modules of the original system
        # state or modules that are from any of the _localimport context
        # paths away.
        for key, mod in sys.modules.items():
            filename = getattr(mod, '__file__', None)
            if not filename:
                continue
            if key in self.state['disables'] or self._is_local(filename):
                self.modules[key] = sys.modules.pop(key)

        # Bring all disabled modules back and restore the
        # the original state.
        sys.modules.update(self.state['disables'])
        sys.path[:] = self.state['path']
        sys.meta_path[:] = self.state['meta_path']

        self.in_context = False
        del self.state

    def load(self, fullname, return_root=True):
        """
        load(fullname) -> module.

        Loads the module specified by *fullname* and returns it. If
        *return_root* is True, returns the root module, otherwise it
        returns the lowest sub-module.

        Disables all existing modules that could shadow the import by
        taking the name of the root module of *fullname*. Also handles
        built-in modules correctly to not accidentally disable them.

        .. note:: This method should be called within the context
            manager of *self* to optimize the import process.

        :raise ImportError: If *fullname* can not be imported.
        """

        if not self.in_context:
            with self:
                return self.load(fullname, return_root)

        parts = fullname.split('.')
        if parts[0] not in sys.builtin_module_names:
            self._disable_module(parts[0])

        root = module = self.original_import(fullname)
        if not return_root:
            for part in parts[1:]:
                module = getattr(module, part)

        return module

    def _disable_module(self, fullname):
        """
        Disables the module *fullname* and all its submodules to
        prevent shadowing of an import that will follow this function
        call. The modules will be moved away from :data:`sys.modules`
        and restored in :meth:`__exit__`.

        Modules that are assumed "local" (ie. are imported from any
        of the :attr:`path` names) are not disabled.

        .. important:: This function does not check if *fullname*
            is a built-in module. Disabling a built-in module can
            be dangerous and disrupt the import mechanism.
        """

        if not self.in_context:
            raise RuntimeError('_localimport context not entered')

        for key, mod in sys.modules.items():
            if key == fullname or key.startswith(fullname + '.'):
                filename = getattr(mod, '__file__', None)
                if filename and self._is_local(filename):
                    continue
                self.state['disables'][key] = sys.modules.pop(key)

    def _get_import_hook(self, original):
        """
        _get_import_hook(original) -> function.

        Returns a function that can be used to hook the builtin
        ``__import__()`` function. The returned function will capture
        all imports made from the same module as the module that
        entered the *_localimport* context by comparing the ID of the
        globals dictionary.

        The captured module names will be disabled unless they're
        built-in modules.
        """

        def import_hook(name, *args, **kwargs):
            if not self.in_context:
                raise RuntimeError('_localimport context not entered')

            # Check if we should capture this import as a name that
            # we need to disable to prevent shadowing.
            captured_globals = self.state['captured_globals']
            if sys._getframe().f_back.f_globals is captured_globals:
                # Only disable if the name is not a built-in module.
                if name not in sys.builtin_module_names:
                    self._disable_module(name.split('.')[0])

            return original(name, *args, **kwargs)

        return import_hook

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

    @staticmethod
    def _mock(obj, attr):
        """
        _mock(obj, attr) -> decorator.
        decorator(func) -> function.

        Decorator to mock the attribute *attr* in *obj* with the
        decorated function. The function will get an attribute called
        ``'original'`` that contains the original attribute value.
        """

        def decorator(func):
            func.original = getattr(obj, attr)
            setattr(obj, attr, func)
            return func
        return decorator

    @staticmethod
    def _unmock(obj, attr):
        """
        _unmock(obj, attr) -> object.

        Unmocks the attribute *attr* of *obj* reverting to the original
        state one mocking level earlier.
        """

        data = getattr(obj, attr)
        setattr(obj, attr, getattr(data, 'original'))
        return data
