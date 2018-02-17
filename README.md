
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

### Usage

In most cases it would not make sense to use `localimport` as a Python module
when you actually want to import Python modules since the import of the
`localimport` module itself would not be isolated.  
The solution is to use the `localimport` source code directly in your
application code. Usually you will use a minified version.

Pre-minified versions of `localimport` can be found in this [Gist][pre-minified].
Of course you can minify the code by yourself, for example using the [`nr`][nr]
command-line tools.

    nr py.blob localimport.py -cm > localimport-gzb64-w80.py

Depending on your application, you may want to use a bootstrapper entry point.

```python
# @@@ minified localimport here @@@

with localimport('.') as _importer:
  _importer.disable('my_application_package')
  from my_application_package.__main__ import main
  main()
```


[pyminifier]: https://pypi.python.org/pypi/pyminifier
[py-blobbify]: https://pypi.python.org/pypi/py-blobbify
[pre-minified]: http://bitly.com/localimport-min
[nr]: https://github.com/NiklasRosenstein/py-nr

---

<p align="center">Copyright &copy; 2018 Niklas Rosenstein</p>
