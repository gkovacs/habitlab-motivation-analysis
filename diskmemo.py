#!/usr/bin/env python
# md5: ac3dbb8891049afe7000ca2a02be8e4f
#!/usr/bin/env python
# coding: utf-8



try:
  from typing import Dict, Any
except ImportError:
  pass

import numpy as np
import os, shelve, inspect, functools, hashlib

# doesn't work with nested stuff (like dicts in argument lists)

cache_dirname = None

def set_cache_dirname(new_cache_dirname):
  global cache_dirname
  cache_dirname = new_cache_dirname

def get_cache_dirname():
  if cache_dirname == None:
    return 'cached_func_calls'
  return cache_dirname

path_to_shelve = {} # type: Dict[str, Any]

def diskmemo(f):
    if not os.path.isdir(cache_dirname):
        os.mkdir(cache_dirname)
        print('Created cache directory %s' % os.path.join(os.path.abspath(__file__), get_cache_dirname()))

    cache_filename = f.__module__ + f.__name__
    cachepath = os.path.join(get_cache_dirname(), cache_filename)
    memcache = {}
    cache = path_to_shelve.get(cache_filename, None)
    if cache == None:
      try:
        cache = shelve.open(cachepath,protocol=2)
        print('successfully opened %s' % cachepath)
        path_to_shelve[cache_filename] = cache
      except Exception as e:
        print('Could not open cache file %s, maybe name collision' % cachepath)
        print(e)

    @functools.wraps(f)
    def wrapped(*args,**kwargs):
        argdict = {}

        # handle instance methods
        if hasattr(f,'__self__'):
            args = args[1:]
            # argdict['classname'] = f.__self__.__class__

        tempargdict = inspect.getcallargs(f,*args,**kwargs)

        # handle numpy arrays
        for k,v in tempargdict.items():
            if isinstance(v,np.ndarray):
                argdict[k] = hashlib.sha1(v).hexdigest()
            else:
                argdict[k] = v

        key = str(hash(frozenset(argdict.items())))
        try:
          return memcache[key]
        except KeyError:
          try:
              return cache[key]
          except KeyError:
              value = f(*args,**kwargs)
              cache[key] = value
              cache.sync()
              return value
        except TypeError:
            print('Warning: could not disk cache call to %s; it probably has unhashable args' % (f.__module__ + '.' + f.__name__))
            return f(*args,**kwargs)

    return wrapped

