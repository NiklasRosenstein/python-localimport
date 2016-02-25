
<p align="center">Isolated import of Python Modules for embedded applications.
  </p>
<h1 align="center">localimport
  <img src="http://i.imgur.com/uuTtLzU.png"/>
  <a href="https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556"><img src="http://i.imgur.com/oMcIOs2.png"/></a></h1>

`localimport` is a Python class that is used as a context manager to hook into
the Python module importer mechanism and ensure a safe and isolated import of
third-party modules. This is especially useful for embedded Python applications
that are packaged with their dependencies to keep the global importer state
clean and to avoid package collisions between plugins.

## Features

* Takes `pkg_resources` namespaces into account
* Mocks `pkgutil.extend_path()` to support zipped Python Eggs
* Emulates a partly isolated environment for local modules
* Evaluates `*.pth` files

## Example

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
with _localimport('res/modules') as _importer:
    import some_package
assert 'some_package' not in sys.modules
```

> **Note**: It is very important that you keep the reference to the
> created `_localimport` object alive, especially if you do use
> `from xx import yy` imports.

----

Copyright (C) 2015 Niklas Rosenstein. Licensed under MIT
