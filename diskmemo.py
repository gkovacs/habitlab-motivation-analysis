#!/usr/bin/env python
# md5: 0bcfe4e6556c6229c2da6ec12409b373
#!/usr/bin/env python
# coding: utf-8



import numpy as np
import os, shelve, inspect, functools, hashlib

# doesn't work with nested stuff (like dicts in argument lists)

cache_dirname = 'cached_func_calls'
path_to_shelve = {}

def diskmemo(f):
    if not os.path.isdir(cache_dirname):
        os.mkdir(cache_dirname)
        print('Created cache directory %s' % os.path.join(os.path.abspath(__file__),cache_dirname))

    cache_filename = f.__module__ + f.__name__
    cachepath = os.path.join(cache_dirname, cache_filename)
    memcache = {}
    cache = path_to_shelve.get(cachepath, None)
    if cache == None:
      try:
        cache = shelve.open(cachepath,protocol=2)
        print('successfully opened %s' % cachepath)
        path_to_shelve[cachepath] = cache
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

