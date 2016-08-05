
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
with localimport('res/modules') as _importer:
    import some_package
assert 'some_package' not in sys.modules
```

> **Note**: It is very important that you keep the reference to the
> `localimport` object alive, especially if you use `from xx import yy` imports.

## Use with [shroud][]

The `localimport` class is defines as `exports` symbols, thus when you
`require()` the module, what you get is the class directly rather then
the module.

```python
from shroud import require
localimport = require('./localimport')

with localimport('res/modules') as _importer:
  # ...
```

[shroud]: https://github.com/NiklasRosenstein/py-shroud

## License

The MIT License (MIT)

Copyright (c) 2015-2016  Niklas Rosenstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
