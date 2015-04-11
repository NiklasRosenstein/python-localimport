localimport
===========

**Secure and optimized imports for Python applications in embedded
environments.**

``_localimport(path, [parent_dir, [eggs]])``
--------------------------------------------

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
