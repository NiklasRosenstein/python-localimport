
<img src="https://img.shields.io/badge/License-MIT-yellow.svg" align="right">
<p align="center">
  <b>localimport</b> allows you to import Python modules in an</br>
  isolated environment, preserving the global importer state.
</p>

### Features

- Emulates an isolated environment for Python module imports
- Evaluates `*.pth` files
- Compatible with `pkg_resources` namespaces
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
