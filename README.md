# localimport

*Minified Version at https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556.*

Secure import mechanism that restores the previous global importer
state after the context-manager exits. Modules imported from the local
site will be moved into :attr:`modules`.

__Features__

* Takes `pkg_resources` namespaces into account
* Mocks `pkgutil.extend_path()` to support zipped Python Eggs
* Emulates a partly isolated environment for local modules
* Evaluates `*.pth` files

__Example__

```python
with _localimport('res/modules'):
    import some_package
assert 'some_package' not in sys.modules
```

# Changelog

__v1.4.9__

* `_localimport._extend_path()` is is now less tolerant about extending
  the namespace path and only does so when a `__init__.{py,pyc,pyo}` file
  exists in the parsed directory

__v1.4.8__

* Now checks any path for being a zipfile rather than just .egg files

----

Copyright (C) 2015 Niklas Rosenstein. Licensed under MIT
