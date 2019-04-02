#!/usr/bin/env python
# md5: 6caaa30e456d2ad82e07fcaecf4c2449
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

# doesn't work with nested stuff (like dicts in argument lists)

cache_dirname = None

def set_cache_dirname(new_cache_dirname):
  global cache_dirname
  cache_dirname = new_cache_dirname

def get_cache_dirname():
  if cache_dirname == None:
    return 'cached_func_calls'
  return cache_dirname

path_to_cache = {} # type: Dict[str, Any]

def jsonmemo(f):
  if not os.path.isdir(cache_dirname):
    os.mkdir(cache_dirname)
    print('Created cache directory %s' % os.path.join(os.path.abspath(__file__), get_cache_dirname()))

  #cache_filename = f.__module__ + f.__name__ + '.json'
  cache_filename = f.__name__ + '.json'
  cachepath = os.path.join(get_cache_dirname(), cache_filename)
  memcache = {}
  cache = None

  @functools.wraps(f)
  def wrapped():
    nonlocal cache
    if cache != None:
      return cache
    cache = path_to_cache.get(cache_filename, None)
    if cache != None:
      return cache
    try:
      cache = json.load(open(cachepath), object_hook=decode_custom)
      path_to_cache[cache_filename] = cache
      return cache
    except Exception as e:
      pass
    print('performing computation ' + cache_filename)
    cache = f()
    print('done with computation ' + cache_filename)
    path_to_cache[cache_filename] = cache
    json.dump(cache, open(cachepath, 'w'), default=encode_custom)
    return cache
  return wrapped

