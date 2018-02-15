## localimport

<img src="https://img.shields.io/badge/License-MIT-yellow.svg" align="right">

&ndash; Isolated import of Python modules

### Features

- Emulates a partly isolated environment for local modules
- Evaluates `*.pth` files
- Supports `pkg_resources` namespaces
- Mocks `pkgutil.extend_path()` to support zipped Python eggs

### Example

Given your Python script, application or plugin comes with a directory that
contains modules for import, you can use localimport to keep the global
importer state clean.

```
app.py
res/modules/
  some_package/
    __init__.py
```

```python
# app.py
with localimport('res/modules') as _importer:
  import some_package
assert 'some_package' not in sys.modules
```

> **Important**: You must keep the reference to the `localimport` object alive,
> especially if you use `from xx import yy` imports.

### Building a minified version

In many cases it doesn't make much sense to use localimport as yet another
Python package, thus you might want to include an inlined and minified
version of it into your codebase. For this you can use either [pyminifier][]
or [py-blobbify][] depending on what format you want to include into your
code.

    pyminifier localimport.py
    py-blobbify localimport.py --export-symbol=localimport -mc

You can find pre-minified versions [here][pre-minified].

[pyminifier]: https://pypi.python.org/pypi/pyminifier
[py-blobbify]: https://pypi.python.org/pypi/py-blobbify
[pre-minified]: http://bitly.com/localimport-min

## Changelog

#### v1.5.3 (current)

- fix issue when the current working directory is used as one of the
  localimport paths
- move non-member functions to global scope, out of the localimport class

#### v1.5.2

- fix #17 where `sys.modules` changed size during iteration in
  `localimport.__enter__()` (Python 3)

#### v1.5.1

- add Python 3 compatibility

#### v1.5

- add `setup.py`
- add `make_min` and `make_b64` commands to `setup.py`
- fix possible error when `localimport(parent_dir)` parameter is
  not specified and the `__file__` of the Python module that uses
  localimport is in the current working directory

#### v1.4.16
- fix possible `KeyError` when restoring namespace module paths
- renamed `_localimport` class to `localimport`
- `localimport(parent_dir)` parameter is now determined dynamically
  using `sys._getframe()`
- support for [py-require][require]

#### v1.4.14
- Mockup `pkg_resources.declare_namespace()`, making it call
  `pkgutil.extend_path()` afterwards to ensure we find all available
  namespace paths

#### v1.4.13
- fixed possible KeyError and AttributeError when using
  the `_localimport.disable()` method

#### v1.4.12
- Removed auto discovering of modules importable from the local site
- Add `_localimport.disable()` method

#### v1.4.11
- Fixed a bug where re-using the `_localimport` context added local modules
  back to `sys.modules` but removed them immediately (#15)

#### v1.4.10
- Fix #13, `_extend_path()` now keeps order of the paths
- Updat class docstrings
- Add `do_eggs` and `do_pth` parameters to the constructor
- Fix #12, add `_discover()` method and automatic disabling of modules  that could conflict with modules from the `_localimport` site

#### v1.4.9

- Fix #11, remove `None`-entries of namespace packages in `sys.modules`
- `_localimport._extend_path()` is is now less tolerant about extending
  the namespace path and only does so when a `__init__.{py,pyc,pyo}` file
  exists in the parsed directory

#### v1.4.8

* Now checks any path for being a zipfile rather than just .egg files
