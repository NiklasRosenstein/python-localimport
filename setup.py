
from __future__ import print_function
import base64, os, sys, textwrap, tempfile, subprocess, zlib
from functools import partial
from setuptools import setup, Command

def perr(*args, **kwargs):
  kwargs.setdefault('file', sys.stderr)
  print(*args, **kwargs)

def minify(code):
  with tempfile.NamedTemporaryFile() as fp:
    fp.write(code.encode('utf8'))
    popen = subprocess.Popen(['pyminifier', fp.name],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = popen.communicate()[0].decode('utf8')
  if popen.returncode != 0:
    raise OSError('pyminifier exited with returncode {0!r}'.format(popen.returncode))
  return result

def get_important_code_section():
  lines = []
  with open('localimport.py') as fp:
    start = False
    for line in fp:
      if line.startswith('import'):
        start = True
        lines.append(line)
      elif line.startswith('#<endmin'):
        break
      elif start:
        lines.append(line)
  return ''.join(lines)


class make_b64(Command):
  description = "Create an inline base64 encoded version of localimport"
  user_options = [
    ('lw=', None, 'Line-width to format the base64 encoded data'),
    ('outfile=', None, 'The file to write the output to. Defaults to stdout')
  ]

  def initialize_options(self): self.lw = 79; self.outfile = None
  def finalize_options(self): pass
  def run(self):
    self.lw = int(self.lw)

    code = get_important_code_section()
    try:
      code = minify(code)
    except OSError as exc:
      perr("make_b64: warning: could not minify code ({0})".format(exc))
      perr("make_b64: warning: resulting blob is larger than necessary")

    data = zlib.compress(code.encode('utf8'))
    data = base64.b64encode(data).decode('ascii')
    lines = list(textwrap.wrap(data, self.lw))

    file = sys.stdout
    if self.outfile:
      file = open(self.outfile, 'w')
    write = partial(print, file=file)
    try:
      write('exec("""import base64 as b, zlib as z; s={}; blob=b"\\')
      for i, line in enumerate(lines):
        le, re = ('\\', '\n') if i < (len(lines)-1) else ('', '')
        write(line + le, end=re)
      write('"')
      write('exec(z.decompress(b.b64decode(blob)), s)')
      write('localimport=s["localimport"]; del blob, b, z, s;""")')
    finally:
      if self.outfile:
        file.close()


class make_min(Command):
  description = "Create an inline minified version of localimport"
  user_options = [
    ('outfile=', None, 'The file to write the output to. Defaults to stdout')
  ]

  def initialize_options(self): self.outfile = None
  def finalize_options(self): pass
  def run(self):
    code = minify(get_important_code_section())
    if self.outfile:
      with open(self.outfile, 'w') as fp:
        fp.write(code)
    else:
      print(code)

def restify():
  if os.path.isfile('README.md'):
    if os.system('pandoc -s README.md -o README.rst') != 0:
      print('-----------------------------------------------------------')
      print('WARNING: pandoc command failed, could not restify README.md')
      print('-----------------------------------------------------------')
      if sys.stdout.isatty():
        input("Enter to continue... ")
  with open('README.rst') as fp:
    return fp.read()

setup(
  name = "localimport",
  version = "1.5",
  description = "Isolated import of Python Modules",
  long_description = restify(),
  author = "Niklas Rosenstein",
  author_email = "rosensteinniklas@gmail.com",
  py_modules = ["localimport"],
  keywords = ["import", "embedded", "modules", "packages"],
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Other Environment',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: Jython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  cmdclass = {
    'make_b64': make_b64,
    'make_min': make_min
  }
)
