## Changelog

__v1.4.11__

* Fixed a bug where re-using the `_localimport` context added local modules
  back to `sys.modules` but removed them immediately (#15)

__v1.4.10__

* Fix #13, `_extend_path()` now keeps order of the paths
* Updat class docstrings
* Add `do_eggs` and `do_pth` parameters to the constructor
* Fix #12, add `_discover()` method and automatic disabling of modules
  that could conflict with modules from the `_localimport` site

__v1.4.9__

* Fix #11, remove `None`-entries of namespace packages in `sys.modules`
* `_localimport._extend_path()` is is now less tolerant about extending
  the namespace path and only does so when a `__init__.{py,pyc,pyo}` file
  exists in the parsed directory

__v1.4.8__

* Now checks any path for being a zipfile rather than just .egg files
