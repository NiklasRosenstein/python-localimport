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
