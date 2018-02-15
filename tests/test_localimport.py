
from nose.tools import *
from localimport import localimport
import os
import sys

modules_dir = os.path.join(os.path.dirname(__file__), 'modules')


def test_localimport():
  with localimport('modules') as _imp:
    import some_module
  assert 'some_module' not in sys.modules
  assert 'another_module' not in sys.modules


def test_localimpot_parent_dir():
  with localimport('.', parent_dir=modules_dir) as _imp:
    import some_module
  assert 'some_module' not in sys.modules
  assert 'another_module' not in sys.modules


def test_localimpot_curdir():
  with localimport('.') as _imp:
    import some_module
  assert 'some_module' not in sys.modules
  assert 'another_module' not in sys.modules
