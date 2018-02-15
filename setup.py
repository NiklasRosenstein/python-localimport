import os
import sys

from setuptools import setup


def restify():
    if os.path.isfile('README.md'):
        if os.system('pandoc -s README.md -o README.rst') != 0:
            print('----------------------------------------------------------')
            print(
                'WARNING: pandoc command failed, could not restify README.md')
            print('----------------------------------------------------------')
            if sys.stdout.isatty():
                if sys.version_info[0] >= 3:
                    input("Enter to continue... ")
                else:
                    raw_input("Enter to continue... ")
        else:
            with open('README.rst') as fp:
                return fp.read()


setup(
    name="localimport",
    version="1.5.2",
    description="Isolated import of Python Modules",
    long_description=restify(),
    author="Niklas Rosenstein",
    author_email="rosensteinniklas@gmail.com",
    py_modules=["localimport"],
    keywords=["import", "embedded", "modules", "packages"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment', 'Environment :: Plugins',
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
    ])
