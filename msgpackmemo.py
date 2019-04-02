#!/usr/bin/env python
# md5: e975f50c2b8203e4eab04e2b8ef4f361
#!/usr/bin/env python
# coding: utf-8



try:
  from typing import Dict, Any
except ImportError:
  pass

import msgpack
import os, functools

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

def msgpackmemo(f):
  if not os.path.isdir(cache_dirname):
    os.mkdir(cache_dirname)
    print('Created cache directory %s' % os.path.join(os.path.abspath(__file__), get_cache_dirname()))

  cache_filename = f.__module__ + f.__name__ + '.msgpack'
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
      cache = msgpack.load(open(cachepath))
      path_to_cache[cache_filename] = cache
      return cache
    except Exception as e:
      pass
    print('performing computation ' + cache_filename)
    cache = f()
    print('done with computation ' + cache_filename)
    path_to_cache[cache_filename] = cache
    msgpack.dump(cache, open(cachepath, 'w'))
    return cache
  return wrapped

