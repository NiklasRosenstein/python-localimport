exec("""
#__author__='Niklas Rosenstein <rosensteinniklas@gmail.com>'
#__version__='1.2'
import glob,os,sys
class _localimport(object):
 _py3k=sys.version_info[0]>=3
 _string_types=(str,)if _py3k else(basestring,)
 def __init__(self,path,parent_dir=os.path.dirname(__file__),eggs=False):
  super(_localimport,self).__init__()
  self.path=[]
  if isinstance(path,self._string_types):
   path=[path]
  for path_name in path:
   if not os.path.isabs(path_name):
    path_name=os.path.join(parent_dir,path_name)
   self.path.append(path_name)
   if eggs:
    self.path.extend(glob.glob(os.path.join(path_name,'*.egg')))
  self.meta_path=[]
  self.modules={}
  self.in_context=False
 def __enter__(self):
  try:import pkg_resources;nsdict=pkg_resources._namespace_packages
  except ImportError:nsdict=None
  self.state={'nsdict':nsdict,'path':sys.path[:],'meta_path':sys.meta_path[:],'disables':{},}
  sys.path[:]=self.path+sys.path
  sys.meta_path[:]=self.meta_path+sys.meta_path
  for key,mod in self.modules.items():
   try:self.state['disables'][key]=sys.modules.pop(key)
   except KeyError:pass
   sys.modules[key]=mod
  self.in_context=True
  return self
 def __exit__(self,*__):
  if not self.in_context:
   raise RuntimeError('context not entered')
  for meta in sys.meta_path:
   if meta is not self and meta not in self.state['meta_path']:
    if meta not in self.meta_path:
     self.meta_path.append(meta)
  modules=sys.modules.copy()
  for key,mod in modules.items():
   force_pop=False
   filename=getattr(mod,'__file__',None)
   if not filename and key not in sys.builtin_module_names:
    parent=key.rsplit('.',1)[0]
    if parent in modules:
     filename=getattr(modules[parent],'__file__',None)
    else:
     force_pop=True
   if force_pop or(filename and self._is_local(filename)):
    self.modules[key]=sys.modules.pop(key)
  sys.modules.update(self.state['disables'])
  sys.path[:]=self.state['path']
  sys.meta_path[:]=self.state['meta_path']
  try:
   import pkg_resources
   pkg_resources._namespace_packages.clear()
   pkg_resources._namespace_packages.update(self.state['nsdict'])
  except ImportError:pass
  self.in_context=False
  del self.state
 def _is_local(self,filename):
  filename=os.path.abspath(filename)
  for path_name in self.path:
   path_name=os.path.abspath(path_name)
   if self._is_subpath(filename,path_name):
    return True
  return False
 @staticmethod
 def _is_subpath(path,ask_dir):
  try:
   relpath=os.path.relpath(path,ask_dir)
  except ValueError:
   return False
  return relpath==os.curdir or not relpath.startswith(os.pardir)
""")
