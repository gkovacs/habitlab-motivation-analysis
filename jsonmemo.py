#!/usr/bin/env python
# md5: a5d02c5d927151aa65c4130285188bf6
#!/usr/bin/env python
# coding: utf-8



try:
  from typing import Dict, Any
except ImportError:
  pass

import arrow
import json
import os, functools
import msgpack
import bson
import torch
import numpy

def encode_custom(obj):
  if isinstance(obj, arrow.Arrow):
    return {'__arrow__': True, 'as_str': str(obj)}
  if isinstance(obj, bson.objectid.ObjectId):
    return {'__bsonid__': True, 'as_str': str(obj)}
  if isinstance(obj, torch.Tensor):
    torch_type = obj.type()
    if torch_type == 'torch.FloatTensor':
      numpy_obj = obj.numpy()
      numpy_type = numpy_obj.dtype
      if numpy_type == numpy.float32:
        return {'__torch_tensor_float32__': True, 'as_str': json.dumps(numpy_obj.tolist())}
    if torch_type == 'torch.LongTensor':
      numpy_obj = obj.numpy()
      numpy_type = numpy_obj.dtype
      if numpy_type == numpy.int64:
        return {'__torch_tensor_int64__': True, 'as_str': json.dumps(numpy_obj.tolist())}
  return obj

def decode_custom(obj):
  if '__arrow__' in obj:
    return arrow.get(obj['as_str'])
  if '__bsonid__' in obj:
    return bson.objectid.ObjectId(obj['as_str'])
  if '__torch_tensor_float32__' in obj:
    return torch.tensor(numpy.array(json.loads(obj['as_str']), dtype='float32'), dtype=torch.float32)
  if '__torch_tensor_int64__' in obj:
    return torch.tensor(numpy.array(json.loads(obj['as_str']), dtype='int64'), dtype=torch.int64)
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

lowmem = False

def set_lowmem(is_lowmem):
  global lowmem
  lowmem = is_lowmem

funcname_to_is_lowmem = {} # type: Dict[str, bool]
  
def is_lowmem_funcname(funcname):
  is_lowmem = funcname_to_is_lowmem.get(funcname, None)
  if is_lowmem is not None:
    return is_lowmem
  return lowmem

def set_lowmem_funcname(funcname, is_lowmem):
  funcname_to_is_lowmem[funcname] = is_lowmem

cached_jsonmemo_funcs = {} # type: Dict[str, Any]

def create_jsonmemo_funcs(cache_dirname):
  if cache_dirname in cached_jsonmemo_funcs:
    return cached_jsonmemo_funcs[cache_dirname]
  path_to_cache_mparr = {} # type: Dict[str, Any]
  def mparrmemo(f):
    if not os.path.isdir(cache_dirname):
      os.mkdir(cache_dirname)
      print('Created cache directory %s' % os.path.join(os.path.abspath(__file__), cache_dirname))

    funcname = f.__name__
    #cache_filename = f.__module__ + f.__name__ + '.json'
    cache_filename = funcname + '.mparr'
    cachepath = os.path.join(cache_dirname, cache_filename)
    cache = None

    @functools.wraps(f)
    def wrapped():
      nonlocal cache
      if cache is not None:
        #for x in cache:
        #  yield cache
        #return
        return cache
      cache = path_to_cache_mparr.get(funcname, None)
      if cache is not None:
        #for x in cache:
        #  yield cache
        #return
        return cache
      try:
        cache = []
        unpacker = msgpack.Unpacker(open(cachepath, 'rb'), raw=False, object_hook=decode_custom)
        for unpacked in unpacker:
          cache.append(unpacked)
          #yield unpacked
        #cache = json.load(open(cachepath), object_hook=decode_custom)
        if not is_lowmem_funcname(funcname):
          path_to_cache_mparr[funcname] = cache
        return cache
      except Exception as e:
        print('exception in mparrmemo for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath)
      #cache = f()
      cache = []
      outfile = open(cachepath + '.tmp', 'wb')
      for line in f():
        cache.append(line)
        outfile.write(msgpack.packb(line, default=encode_custom))
      outfile.flush()
      outfile.close()
      os.replace(cachepath + '.tmp', cachepath)
      print('done with computation ' + cachepath)
      if not is_lowmem_funcname(funcname):
        path_to_cache_mparr[funcname] = cache
      #json.dump(cache, open(cachepath, 'w'), default=encode_custom)
      #return cache
      #for line in cache:
      #  yield line
      return cache
    return wrapped

  path_to_cache_msgpackmemo = {} # type: Dict[str, Any]
  def msgpackmemo(f):
    if not os.path.isdir(cache_dirname):
      os.mkdir(cache_dirname)
      print('Created cache directory %s' % os.path.join(os.path.abspath(__file__), cache_dirname))

    funcname = f.__name__
    #cache_filename = f.__module__ + f.__name__ + '.json'
    cache_filename = funcname + '.msgpack'
    cachepath = os.path.join(cache_dirname, cache_filename)
    cache = None

    @functools.wraps(f)
    def wrapped():
      nonlocal cache
      if cache is not None:
        return cache
      cache = path_to_cache_msgpackmemo.get(funcname, None)
      if cache is not None:
        return cache
      try:
        cache = msgpack.load(open(cachepath, 'rb'), raw=False, object_hook=decode_custom)
        if not is_lowmem_funcname(funcname):
          path_to_cache_msgpackmemo[funcname] = cache
        return cache
      except Exception as e:
        print('exception in msgpackmemo for file ' + cachepath)
        print(e)
        pass
      cache = f()
      if not is_lowmem_funcname(funcname):
        path_to_cache_msgpackmemo[funcname] = cache
      msgpack.dump(cache, open(cachepath, 'wb'), default=encode_custom)
      return cache
    return wrapped
  
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
      if cache is not None:
        return cache
      cache = path_to_cache.get(funcname, None)
      if cache is not None:
        return cache
      try:
        cache = json.load(open(cachepath, 'rt'), object_hook=decode_custom)
        if not is_lowmem_funcname(funcname):
          path_to_cache[funcname] = cache
        return cache
      except Exception as e:
        print('exception in jsonmemo for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath)
      cache = f()
      print('done with computation ' + cachepath)
      if not is_lowmem_funcname(funcname):
        path_to_cache[funcname] = cache
      json.dump(cache, open(cachepath, 'wt'), default=encode_custom)
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
      if val is not None:
        return val
      cachepath = os.path.join(func_cache_dir, str(arg1) + '.json')
      try:
        cacheitem = json.load(open(cachepath, 'rt'), object_hook=decode_custom)
        if not is_lowmem_funcname(funcname):
          path_to_cache_1arg[funcname][arg1] = cacheitem
        return cacheitem
      except Exception as e:
        print('exception in jsonmemo1arg for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath + ' for arg ' + str(arg1))
      cacheitem = f(arg1)
      print('done with computation ' + cachepath)
      if not is_lowmem_funcname(funcname):
        path_to_cache_1arg[funcname][arg1] = cacheitem
      json.dump(cacheitem, open(cachepath, 'wt'), default=encode_custom)
      return cacheitem
    return wrapped

  path_to_cache_msgpack1arg = {} # type: Dict[str, Dict[Any, Any]]
  
  def msgpackmemo1arg(f):
    if not os.path.isdir(cache_dirname):
      os.mkdir(cache_dirname)
      print('Created cache directory %s' % cache_dirname)
    funcname = f.__name__
    func_cache_dir = os.path.join(cache_dirname, funcname)
    if not os.path.isdir(func_cache_dir):
      os.mkdir(func_cache_dir)
      print('Created cache directory %s' % func_cache_dir)

    if funcname in path_to_cache_msgpack1arg:
      cache = path_to_cache_msgpack1arg[funcname]
    else:
      cache = {}
      path_to_cache_msgpack1arg[funcname] = cache

    @functools.wraps(f)
    def wrapped(arg1):
      nonlocal cache
      val = cache.get(arg1, None)
      if val is not None:
        return val
      cachepath = os.path.join(func_cache_dir, str(arg1) + '.msgpack')
      try:
        cacheitem = msgpack.load(open(cachepath, 'rb'), raw=False, object_hook=decode_custom)
        if not is_lowmem_funcname(funcname):
          path_to_cache_msgpack1arg[funcname][arg1] = cacheitem
        return cacheitem
      except Exception as e:
        print('exception in msgpackmemo1arg for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath + ' for arg ' + str(arg1))
      cacheitem = f(arg1)
      print('done with computation ' + cachepath)
      if not is_lowmem_funcname(funcname):
        path_to_cache_msgpack1arg[funcname][arg1] = cacheitem
      msgpack.dump(cacheitem, open(cachepath, 'wb'), default=encode_custom)
      return cacheitem
    return wrapped
  
  path_to_cache_msgpack2arg = {} # type: Dict[str, Dict[Any, Dict[Any, Any]]]
  
  def msgpackmemo2arg(f):
    if not os.path.isdir(cache_dirname):
      os.mkdir(cache_dirname)
      print('Created cache directory %s' % cache_dirname)
    funcname = f.__name__
    func_cache_dir = os.path.join(cache_dirname, funcname)
    if not os.path.isdir(func_cache_dir):
      os.mkdir(func_cache_dir)
      print('Created cache directory %s' % func_cache_dir)

    if funcname in path_to_cache_msgpack2arg:
      cache = path_to_cache_msgpack2arg[funcname]
    else:
      cache = {}
      path_to_cache_msgpack2arg[funcname] = cache

    @functools.wraps(f)
    def wrapped(arg1, arg2):
      nonlocal cache
      val = cache.get(arg1, None)
      if val is not None:
        return val
      cachepath = os.path.join(func_cache_dir, str(arg1), str(arg2) + '.msgpack')
      try:
        cacheitem = msgpack.load(open(cachepath, 'rb'), raw=False, object_hook=decode_custom)
        if not is_lowmem_funcname(funcname):
          if arg1 not in path_to_cache_msgpack2arg[funcname]:
            path_to_cache_msgpack2arg[funcname][arg1] = {}
          path_to_cache_msgpack2arg[funcname][arg1][arg2] = cacheitem
        return cacheitem
      except Exception as e:
        print('exception in msgpackmemo1arg for file ' + cachepath)
        print(e)
        pass
      print('performing computation ' + cachepath + ' for arg ' + str(arg1))
      cacheitem = f(arg1, arg2)
      print('done with computation ' + cachepath)
      if not is_lowmem_funcname(funcname):
        if arg1 not in path_to_cache_msgpack2arg[funcname]:
          path_to_cache_msgpack2arg[funcname][arg1] = {}
        path_to_cache_msgpack2arg[funcname][arg1][arg2] = cacheitem
      msgpack.dump(cacheitem, open(cachepath, 'wb'), default=encode_custom)
      return cacheitem
    return wrapped
  
  output = {
    'jsonmemo': jsonmemo,
    'jsonmemo1arg': jsonmemo1arg,
    'mparrmemo': mparrmemo,
    'msgpackmemo': msgpackmemo,
    'msgpackmemo1arg': msgpackmemo1arg,
    'msgpackmemo2arg': msgpackmemo2arg,
  }
  cached_jsonmemo_funcs[cache_dirname] = output
  return output



# from getsecret import getsecret
# jsonmemo_funcs = create_jsonmemo_funcs(getsecret('DATA_DUMP'))
# jsonmemo = jsonmemo_funcs['jsonmemo']
# msgpackmemo = jsonmemo_funcs['msgpackmemo']



# from evaluation_utils import *



# true = True
# false = False
# parameter_info_list = [{"name": "dataset_name", "type": "dataset", "values": ["2019_04_11"], "value": "2019_04_11"}, {"name": "model_name", "type": "model", "values": ["selfattentionlstm"], "value": "selfattentionlstm"}, {"name": "criterion", "type": "model", "values": ["NLLLoss"], "value": "NLLLoss"}, {"name": "learning_rate", "type": "model", "values": [0.005, 0.05, 0.0005, 5e-05], "value": 5e-05}, {"name": "window_embed_size", "type": "model", "values": [64, 128, 256, 512], "value": 256}, {"name": "difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "time_of_day", "type": "feature", "values": [true, false], "value": true}, {"name": "day_of_week", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_productivity", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_category", "type": "feature", "values": [true, false], "value": true}, {"name": "initial_difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "languages", "type": "feature", "values": [true, false], "value": true}, {"name": "num_prior_entries", "type": "dataparam", "values": [10, 20, 30, 40], "value": 10}, {"name": "sample_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "sample_difficulty_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "disable_prior_visit_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "disable_difficulty_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "enable_current_difficulty", "type": "dataparam", "values": [false, true], "value": false}, {"name": "num_features", "type": "model", "values": [277], "value": 277}]
# set_parameter_in_parameter_info_list(parameter_info_list, 'sample_every_n_visits', 1)
# train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)



# data_to_cache = train_data,dev_data,test_data



# print((data_to_cache[0][0]['feature'].numpy().dtype))



# print(data_to_cache[0][0]['category'].numpy().dtype == numpy.int64)



# print(data_to_cache[0][0]['category'].numpy().dtype)



# print(data_to_cache[0][0]['feature'].type())



# def encode_custom(obj):
#   if isinstance(obj, arrow.Arrow):
#     return {'__arrow__': True, 'as_str': str(obj)}
#   if isinstance(obj, bson.objectid.ObjectId):
#     return {'__bsonid__': True, 'as_str': str(obj)}
#   if isinstance(obj, torch.Tensor):
#     torch_type = obj.type()
#     if torch_type == 'torch.FloatTensor':
#       numpy_obj = obj.numpy()
#       numpy_type = numpy_obj.dtype
#       if numpy_type == numpy.float32:
#         return {'__torch_tensor_float32__': True, 'as_str': json.dumps(numpy_obj.tolist())}
#     if torch_type == 'torch.LongTensor':
#       numpy_obj = obj.numpy()
#       numpy_type = numpy_obj.dtype
#       if numpy_type == numpy.int64:
#         return {'__torch_tensor_int64__': True, 'as_str': json.dumps(numpy_obj.tolist())}
#   return obj



# #msgpack.dump([3, [1,arrow.get()]], open('testfile.msgpack', 'wb'), default=encode_custom)
# msgpack.dump(data_to_cache, open('testfile.msgpack', 'wb'), default=encode_custom)



# @msgpackmemo
# def get_default_train_dev_test_data():
#   true = True
#   false = False
#   parameter_info_list = [{"name": "dataset_name", "type": "dataset", "values": ["2019_04_11"], "value": "2019_04_11"}, {"name": "model_name", "type": "model", "values": ["selfattentionlstm"], "value": "selfattentionlstm"}, {"name": "criterion", "type": "model", "values": ["NLLLoss"], "value": "NLLLoss"}, {"name": "learning_rate", "type": "model", "values": [0.005, 0.05, 0.0005, 5e-05], "value": 5e-05}, {"name": "window_embed_size", "type": "model", "values": [64, 128, 256, 512], "value": 256}, {"name": "difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "time_of_day", "type": "feature", "values": [true, false], "value": true}, {"name": "day_of_week", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_productivity", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_category", "type": "feature", "values": [true, false], "value": true}, {"name": "initial_difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "languages", "type": "feature", "values": [true, false], "value": true}, {"name": "num_prior_entries", "type": "dataparam", "values": [10, 20, 30, 40], "value": 10}, {"name": "sample_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "sample_difficulty_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "disable_prior_visit_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "disable_difficulty_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "enable_current_difficulty", "type": "dataparam", "values": [false, true], "value": false}, {"name": "num_features", "type": "model", "values": [277], "value": 277}]
#   set_parameter_in_parameter_info_list(parameter_info_list, 'sample_every_n_visits', 1)
#   train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)
#   return train_data,dev_data,test_data




# from getsecret import getsecret
# jsonmemo_funcs = create_jsonmemo_funcs(getsecret('DATA_DUMP'))
# jsonmemo = jsonmemo_funcs['jsonmemo']
# msgpackmemo = jsonmemo_funcs['msgpackmemo']


# @msgpackmemo
# def get_tensor_sample():
#   a=torch.tensor([1], dtype=torch.float32)
#   b=torch.tensor([2], dtype=torch.float32)
#   c=torch.tensor([3], dtype=torch.float32)
#   return [{'features': a}],[{'features': b}],[{'features': c}]

# get_tensor_sample()



# cache = json.load(open('/home/geza/motivation/2019_04_25/get_tensor_sample.json', 'rt'), object_hook=decode_custom)







# a=json.loads(json.loads(open('/home/geza/motivation/2019_04_25/get_tensor_sample.json', 'rt').read())['as_str'])
# b=numpy.array(a, dtype='float32')
# c=torch.tensor(b, dtype=torch.float32)
# #torch.tensor(numpy.array(json.load(open('/home/geza/motivation/2019_04_25/get_tensor_sample.json', 'rt')), dtype='float32'), dtype=torch.float32)



# from getsecret import getsecret
# jsonmemo_funcs = create_jsonmemo_funcs(getsecret('DATA_DUMP'))
# jsonmemo1arg = jsonmemo_funcs['jsonmemo1arg']
# jsonmemo = jsonmemo_funcs['jsonmemo']
# mparrmemo = jsonmemo_funcs['mparrmemo']



# @mparrmemo
# def get_all_features_data():
#   print('get all features data should not be running')
#   return []



# print(get_all_features_data())



# cache = []
# print('unpacker not yet started')
# unpacker = msgpack.Unpacker(open('2019_04_08/get_all_features_data.mparr', 'rb'), raw=False, object_hook=decode_custom)
# print('unpacker started')
# print(type(unpacker))
# for unpacked in unpacker:
#   print(unpacked)
#   break
#   cache.append(unpacked)
#   #yield unpacked
# print('unpacker finished')



# import msgpack

# print('getting data_to_dump')
# data_to_dump = msgpack.load(open('2019_04_08/get_all_features_data.msgpack', 'rb'))

# print('starting to write outfile')
# outfile = open('2019_04_08/get_all_features_data_v2.mparr', 'wb')
# for line in data_to_dump:
#   outfile.write(msgpack.packb(line))
#   #outfile.write(msgpack.packb(line, use_bin_type=True)) #, default=encode_custom))
# print('flushing')
# outfile.flush()
# outfile.close()
# print('done')
# #outfile.write()



# unpacker = msgpack.Unpacker(open('2019_04_08/get_all_features_data.mparr', 'rb'), raw=False, object_hook=decode_custom) #, encoding='utf8')#, object_hook=decode_custom_msgpack)
# for unpacked in unpacker:
#   print(unpacked)
#   #print(json.loads(json.dumps(unpacked)))
#   break













