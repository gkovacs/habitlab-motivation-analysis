#!/usr/bin/env python
# md5: b17a3197b99ede071f14dbe5053c0a46
#!/usr/bin/env python
# coding: utf-8



try:
  from typing import Dict, Any
except ImportError:
  pass

import arrow
import json
import os, functools

def decode_custom(obj):
  if '__arrow__' in obj:
    obj = arrow.get(obj['as_str'])
  return obj

def encode_custom(obj):
  if isinstance(obj, arrow.Arrow):
    return {'__arrow__': True, 'as_str': str(obj)}
  return obj

# # doesn't work with nested stuff (like dicts in argument lists)

# cache_dirname = None

# def set_cache_dirname(new_cache_dirname):
#   global cache_dirname
#   cache_dirname = new_cache_dirname

# def get_cache_dirname():
#   if cache_dirname == None:
#     return 'cached_func_calls'
#   return cache_dirname


def create_jsonmemo_funcs(cache_dirname):
  path_to_cache = {} # type: Dict[str, Any]

  def jsonmemo(f):
    if not os.path.isdir(cache_dirname):
      os.mkdir(cache_dirname)
      print('Created cache directory %s' % os.path.join(os.path.abspath(__file__), cache_dirname))

    funcname = f.__name__
    #cache_filename = f.__module__ + f.__name__ + '.json'
    cache_filename = funcname + '.json'
    cachepath = os.path.join(cache_dirname, cache_filename)
    cache = None

    @functools.wraps(f)
    def wrapped():
      nonlocal cache
      if cache != None:
        return cache
      cache = path_to_cache.get(funcname, None)
      if cache != None:
        return cache
      try:
        cache = json.load(open(cachepath), object_hook=decode_custom)
        path_to_cache[cache_filename] = cache
        return cache
      except Exception as e:
        print('exception in jsonmemo for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath)
      cache = f()
      print('done with computation ' + cachepath)
      path_to_cache[funcname] = cache
      json.dump(cache, open(cachepath, 'w'), default=encode_custom)
      return cache
    return wrapped

  path_to_cache_1arg = {} # type: Dict[str, Dict[Any, Any]]

  def jsonmemo1arg(f):
    if not os.path.isdir(cache_dirname):
      os.mkdir(cache_dirname)
      print('Created cache directory %s' % cache_dirname)
    funcname = f.__name__
    func_cache_dir = os.path.join(cache_dirname, funcname)
    if not os.path.isdir(func_cache_dir):
      os.mkdir(func_cache_dir)
      print('Created cache directory %s' % func_cache_dir)

    if funcname in path_to_cache_1arg:
      cache = path_to_cache_1arg[funcname]
    else:
      cache = {}
      path_to_cache_1arg[funcname] = cache

    @functools.wraps(f)
    def wrapped(arg1):
      nonlocal cache
      val = cache.get(arg1, None)
      if val != None:
        return val
      cachepath = os.path.join(func_cache_dir, str(arg1) + '.json')
      try:
        cache = json.load(open(cachepath), object_hook=decode_custom)
        path_to_cache_1arg[funcname][arg1] = cache
        return cache
      except Exception as e:
        print('exception in jsonmemo1arg for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath + ' for arg ' + str(arg1))
      cache = f(arg1)
      print('done with computation ' + cachepath)
      path_to_cache_1arg[funcname][arg1] = cache
      json.dump(cache, open(cachepath, 'w'), default=encode_custom)
      return cache
    return wrapped
  
  return {
    'jsonmemo': jsonmemo,
    'jsonmemo1arg': jsonmemo1arg,
  }







# jsonmemo1arg = create_jsonmemo_funcs('somedir')['jsonmemo1arg']

# @jsonmemo1arg
# def foobar(x):
#   return x+2

# foobar(6)

