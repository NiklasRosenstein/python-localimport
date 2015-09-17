localimport
===========

*Minified Version at https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556.*

Secure import mechanism that restores the previous global importer
state after the context-manager exits. Modules imported from the local
site will be moved into :attr:`modules`.

Features:
    - Takes :mod:`pkg_resources` namespace package dictionary into
      account.
    - Removes modules from the global scope, but only if they were
      import from the local site (determined by :attr:`path`).
    - Automatically extends the path with `*.egg` files/folders that
      are detected in the specified paths
    - Automatically evaluates `*.pth` files in the specified paths

Example:

.. code-block:: python

    with _localimport('res/modules'):
        import some_package

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

Changelog
=========

__v1.4.8__

- Now checks any path for being a zipfile rather than just .egg files

.. author:: Niklas Rosenstein <rosensteinniklas@gmail.com>
.. license:: MIT
