#!/usr/bin/env python
# md5: b36cd10cb9eb8eb5500687bce9157866
#!/usr/bin/env python
# coding: utf-8



from typing import Dict, List, Tuple, Set, Any



import sys
#sys.version
from copy import copy



from importlib import reload
from getsecret import getsecret



from memoize import memoize # pip install memoize2
#import diskmemo
#reload(diskmemo)
#from diskmemo import diskmemo
#import jsonmemo
#reload(jsonmemo)
#from jsonmemo import set_cache_dirname as set_jsonmemo_cache_dirname
#from jsonmemo import jsonmemo
#set_jsonmemo_cache_dirname(getsecret('DATA_DUMP'))
import jsonmemo as jsonmemo_module
jsonmemo_funcs = jsonmemo_module.create_jsonmemo_funcs(getsecret('DATA_DUMP'))
jsonmemo1arg = jsonmemo_funcs['jsonmemo1arg']
jsonmemo = jsonmemo_funcs['jsonmemo']
mparrmemo = jsonmemo_funcs['mparrmemo']
msgpackmemo = jsonmemo_funcs['msgpackmemo']



import torch



#import libmotivation
#reload(libmotivation)
from libmotivation import *



from browser_libs import get_collection_items, get_collection_names, get_collection_for_user



#collection_names = get_collection_names()
#print(collection_names[0:30])



# for collection_name in collection_names:
#   if 'install' in collection_name:
#     if collection_name in ['uninstalls', 'uninstall_feedback']:
#       continue
#     print(collection_name)
#     break



#installs_collection = get_collection_items('installs')



#print(len(installs_collection))
#print(installs_collection[len(installs_collection) - 1])











@msgpackmemo
def get_users():
  return get_users_with_choose_difficulty()

@msgpackmemo
def get_user_to_install_logs():
  installs_collection = get_collection_items('installs')
  output = {}
  for item in installs_collection:
    if 'user_id' not in item:
      continue
    user = item['user_id']
    if user not in output:
      output[user] = []
    output[user].append(item)
  return output

def get_install_logs_for_user(user):
  user_to_install_logs = get_user_to_install_logs()
  return user_to_install_logs.get(user, [])

@memoize
def get_languages_for_user(user):
  output = set()
  for item in get_install_logs_for_user(user):
    for language in item.get('languages', []):
      output.add(language)
  return sorted(list(output))



#print((get_user_to_install_logs())[0])
#print(get_collection_items('installs')[0])







@msgpackmemo
def get_language_list():
  user_list = get_users()
  output = set()
  for user in user_list:
    for language in get_languages_for_user(user):
      output.add(language)
  return sorted(list(output))

@memoize
def get_num_languages():
  return len(get_language_list())

@memoize
def get_language_to_index():
  language_list = get_language_list()
  output = {}
  for idx,language in enumerate(language_list):
    output[language] = idx
  return output



def convert_language_list_to_language_indexes(languages):
  language_to_idx = get_language_to_index()
  return [language_to_idx[language] for language in languages]

def get_language_indexes_for_user(user):
  language_to_idx = get_language_to_index()
  languages = get_languages_for_user(user)
  return [language_to_idx[language] for language in languages]



def get_initial_difficulty_for_install(install):
  abtest_settings = get_abtest_settings_for_install(install)
  #return abtest_settings.get('user_chosen_difficulty_survey', None)
  difficulty = abtest_settings.get('user_chosen_difficulty', None)
  #if difficulty == None:
  #  difficulty = abtest_settings.get('user_chosen_difficulty_survey', None)
  return difficulty



def get_initial_difficulty_for_user(user):
  abtest_settings = get_abtest_settings(user)
  #return abtest_settings.get('user_chosen_difficulty_survey', None)
  difficulty = abtest_settings.get('user_chosen_difficulty', None)
  #if difficulty == None:
  #  difficulty = abtest_settings.get('user_chosen_difficulty_survey', None)
  return difficulty

def get_initial_difficulty_idx_for_user(user):
  difficulty = get_initial_difficulty_for_user(user)
  if difficulty == None:
    return -1
  return ['nothing', 'easy', 'medium', 'hard'].index(difficulty)

#for user in get_users_with_choose_difficulty():
#  abtest_settings = get_abtest_settings(user)
#  print(abtest_settings)
#  break



# difficulty_choices = Counter()
# for user in get_users_with_choose_difficulty():
#   difficulty = get_initial_difficulty_for_user(user)
#   difficulty_choices[difficulty] += 1
# print(difficulty_choices)



#language_list = get_language_list()







import arrow
from dateutil import tz

#timezone_list = list(timezone_set)
#print(timezone_list)
#print(list(map(to_hours_and_minutes, timezone_list)))

def parse_timezone_offset(datestr):
  date_parts = datestr.split(' ')
  for x in date_parts:
    if 'GMT' in x:
      output = (x.replace('GMT', ''))
      #timezone_set.add(output)
      return output
  raise Exception(datestr)

def to_hours_and_minutes(offset):
  if len(offset) != 5:
    raise Exception(offset)
  sign = offset[0]
  hours = int(offset[1:3])
  minutes = int(offset[3:])
  if sign == '+':
    return hours,minutes
  if sign == '-':
    return -hours,-minutes
  raise Exception(offset)

def adjust_timestamp_to_timezone_offset(timestamp, offset):
  hours,minutes = to_hours_and_minutes(offset)
  #print(hours, minutes)
  ar = arrow.get(timestamp / 1000.0)
  return ar.shift(hours=hours, minutes=minutes)

def get_time_adjusted_for_timezone(timestamp, datestr):
  offset = parse_timezone_offset(datestr)
  return adjust_timestamp_to_timezone_offset(timestamp, offset)

#print(adjust_timestamp_to_timezone(1548789649098.0,'-0600')) # 'Tue Jan 29 2019 13:20:49 GMT-0600 (Central Standard Time)',
#print(get_time_adjusted_for_timezone(1548789649098.0, 'Tue Jan 29 2019 13:20:49 GMT-0600 (Central Standard Time)'))



def url_to_domain(url):
  #url='https://www.hello.org/bye/'
  domain=url.split('//')[-1].split('/')[0]
  #print (domain)
  return domain

#print(url_to_domain('https://www.hello.org/bye/'))



import json

@memoize
def get_domain_to_productivity():
  return json.load(open('domain_to_productivity.json'))

@memoize
def get_domain_to_category():
  return json.load(open('domain_to_category.json'))

@memoize
def get_domain_category_list():
  return list(set(get_domain_to_category().values()))

@memoize
def get_domain_productivity_list():
  return list(set(get_domain_to_productivity().values()))

@memoize
def get_domain_to_category_idx():
  category_list = get_domain_category_list()
  domain_to_category = get_domain_to_category()
  domain_to_category_idx = {}
  for domain,category in domain_to_category.items():
    # should we do something about domains where category = ''?
    category_idx = category_list.index(category)
    domain_to_category_idx[domain] = category_idx
  return domain_to_category_idx

@memoize
def get_domain_to_productivity_idx():
  domain_to_productivity = get_domain_to_productivity()
  domain_to_productivity_idx = {}
  for domain,productivity in domain_to_productivity.items():
    # should we do something about domains where productivity = 0?
    domain_to_productivity_idx[domain] = productivity + 2
  return domain_to_productivity_idx







#history_length = 100

def make_features_for_user_v1(user):
  output = []
  difficulty_items = get_choose_difficulty_items_for_user(user)
  prior_entries = []
  languages = get_languages_for_user(user)
  initial_difficulty = get_initial_difficulty_for_user(user)
  if initial_difficulty == None:
    return []
  idx = 0
  for item in difficulty_items:
    if 'is_random' in item and item['is_random'] == True:
      continue
    if 'type' not in item:
      continue
    if item['type'] != 'action':
      continue
    if 'difficulty' not in item:
      continue
    difficulty = item['difficulty']
    url = item['url']
    arrow_time = get_time_adjusted_for_timezone(item['timestamp_local'], item['localtime'])
    output.append({
      'url': url,
      'user': user,
      'initial_difficulty': initial_difficulty,
      'languages': languages,
      'difficulty': difficulty,
      'arrow_time': arrow_time,
      'prior_entries': prior_entries[:],
      'idx': idx,
    })
    prior_entries.append({
      'url': url,
      'difficulty': difficulty,
      'arrow_time': arrow_time,
      'idx': idx,
    })
    #if len(prior_entries) > history_length:
    #  prior_entries = prior_entries[-history_length:]
    idx += 1
  return output



def make_features_for_user(user):
  initial_difficulty = get_initial_difficulty_for_user(user)
  if initial_difficulty == None:
    return None
  difficulty_items_raw = get_choose_difficulty_items_for_user(user)
  difficulty_items = []
  for item in difficulty_items_raw:
    if 'is_random' in item and item['is_random'] == True:
      continue
    if 'type' not in item:
      continue
    if item['type'] != 'action':
      continue
    if 'difficulty' not in item:
      continue
    difficulty = item['difficulty']
    url = item['url']
    arrow_time = get_time_adjusted_for_timezone(item['timestamp_local'], item['localtime'])
    difficulty_items.append({
      'difficulty': difficulty,
      'url': url,
      'arrow_time': arrow_time,
    })
  if len(difficulty_items) == 0:
    return None
  languages = get_languages_for_user(user)
  output = {
    'initial_difficulty': initial_difficulty,
    'languages': languages,
    'difficulty_items': difficulty_items,
  }
  return output























@msgpackmemo
def get_all_features_data():
  user_to_features_data = {}
  for user in get_users():
    print(user)
    features_data = make_features_for_user(user)
    if features_data == None:
      continue
    user_to_features_data[user] = features_data
  return user_to_features_data











# @msgpackmemo
# def get_all_features_data():
#   all_features_data = []
#   for user in get_users():
#     print(user)
#     #tensors = make_tensors_for_user(user)
#     feature_list = make_features_for_user(user)
#     for features in feature_list:
#       all_features_data.append(features)
#   return all_features_data



#print(len(get_users()))



#all_features_data = get_all_features_data()
#print(len(all_features_data))



def split_into_train_dev_test(all_data):
  training_data = all_data[:int(math.floor(len(all_data)*9/10))]
  dev_and_test_data = all_data[len(training_data):]
  dev_data = dev_and_test_data[:int(math.floor(len(dev_and_test_data)/2))]
  test_data = dev_and_test_data[len(dev_data):]
  return training_data,dev_data,test_data



#all_features_data = get_all_features_data()



# def make_tensors_from_features_v1(features):
#   output = []
#   for feature in features:
#     chosen_difficulty = feature['difficulty']
#     prior_difficulties = feature['prior_difficulties']
#     user = feature['user']
#     category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
#     feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 4 in this version
#     for idx,difficulty in enumerate(prior_difficulties):
#       difficulty_idx = difficulty_to_idx[difficulty]
#       feature_tensor[idx][0][difficulty_idx] = 1
#     #feature_tensor = make_tensor_from_prior_difficulties_list(prior_difficulties)
#     output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
#   return output

# def make_tensors_from_features_v2(features):
#   output = []
#   for feature in features:
#     hour = feature['arrow_time'].hour
#     chosen_difficulty = feature['difficulty']
#     prior_difficulties = feature['prior_difficulties']
#     user = feature['user']
#     category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
#     feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 1 in this version
#     for idx,difficulty in enumerate(prior_difficulties):
#       difficulty_idx = difficulty_to_idx[difficulty]
#       feature_tensor[idx][0][0] = difficulty_idx
#     output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
#   return output

# def make_tensors_from_features_v3(features):
#   output = []
#   for feature in features:
#     hour = feature['arrow_time'].hour
#     hour_idx = hour_to_hour_idx_4cat(hour)
#     weekday_idx = feature['arrow_time'].weekday()
#     chosen_difficulty = feature['difficulty']
#     prior_difficulties = feature['prior_difficulties']
#     user = feature['user']
#     category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
#     feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 15 in this version
#     for idx,difficulty in enumerate(prior_difficulties):
#       difficulty_idx = difficulty_to_idx[difficulty]
#       feature_tensor[idx][0][difficulty_idx] = 1
#       feature_tensor[idx][0][4 + hour_idx] = 1
#       feature_tensor[idx][0][8 + weekday_idx] = 1
#     output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
#   return output

# def make_tensors_from_features_v4(features):
#   output = []
#   for feature in features:
#     url = feature['url']
#     domain = url_to_domain(url)
#     have_productivity_idx = False
#     if domain in domain_to_productivity_idx:
#       domain_productivity_idx = domain_to_productivity_idx[domain]
#       have_productivity_idx = True
#     else:
#       domain_productivity_idx = None
#     have_category_idx = False
#     if domain in domain_to_category_idx:
#       domain_category_idx = domain_to_productivity_idx[domain]
#       have_category_idx = True
#     else:
#       domain_category_idx = None
#     hour = feature['arrow_time'].hour
#     hour_idx = hour_to_hour_idx_4cat(hour)
#     weekday_idx = feature['arrow_time'].weekday()
#     chosen_difficulty = feature['difficulty']
#     prior_difficulties = feature['prior_difficulties']
#     user = feature['user']
#     category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
#     feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 15 in this version
#     for idx,difficulty in enumerate(prior_difficulties):
#       difficulty_idx = difficulty_to_idx[difficulty]
#       feature_tensor[idx][0][difficulty_idx] = 1
#       feature_tensor[idx][0][4 + hour_idx] = 1
#       feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
#       if have_productivity_idx:
#         feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
#       if have_category_idx:
#         feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
#     output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
#   return output

# def make_tensors_from_features_v5(features): # this one cheats because we have the reference information included
#   output = []
#   for feature in features:
#     url = feature['url']
#     domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(url)
#     hour_idx,weekday_idx = get_time_features_from_arrow(feature['arrow_time'])
#     chosen_difficulty = feature['difficulty']
#     prior_difficulties = feature['prior_difficulties']
#     user = feature['user']
#     category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
#     feature_tensor = torch.zeros(len(prior_difficulties)+1, 1, n_features) # n_features = 15 in this version
#     # features for current timestep
#     idx = len(prior_difficulties)
#     difficulty = feature['difficulty']
#     difficulty_idx = difficulty_to_idx[difficulty]
#     #if len(prior_difficulties) > 0:
#     #  feature_tensor[idx][0][difficulty_to_idx[prior_difficulties[-1]]] = 1
#     #feature_tensor[idx][0][difficulty_idx] = 1 # this is an impossible feature. see whether it learns corectly
#     feature_tensor[idx][0][4 + hour_idx] = 1
#     feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
#     if have_productivity_idx:
#       feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
#     if have_category_idx:
#       feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
#     # features for previous timesteps
#     for idx,difficulty in enumerate(prior_difficulties):
#       difficulty_idx = difficulty_to_idx[difficulty]
#       #feature_tensor[idx][0][difficulty_idx] = 1
#       hour_idx,weekday_idx = get_time_features_from_arrow(feature['prior_arrow_times'][idx])
#       domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(feature['prior_urls'][idx])
#       feature_tensor[idx][0][4 + hour_idx] = 1
#       feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
#       if have_productivity_idx:
#         feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
#       if have_category_idx:
#         feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
#     output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
#   return output

# def make_tensors_from_features_v6(features): # this one cheats because we have the reference information included
#   output = []
#   for feature in features:
#     url = feature['url']
#     domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(url)
#     hour_idx,weekday_idx = get_time_features_from_arrow(feature['arrow_time'])
#     chosen_difficulty = feature['difficulty']
#     language_indexes = convert_language_list_to_language_indexes(feature['languages'])
#     prior_difficulties = feature['prior_difficulties']
#     user = feature['user']
#     category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
#     feature_tensor = torch.zeros(len(prior_difficulties)+1, 1, n_features) # n_features = 15 in this version
#     # features for current timestep
#     idx = len(prior_difficulties)
#     difficulty = feature['difficulty']
#     difficulty_idx = difficulty_to_idx[difficulty]
#     #if len(prior_difficulties) > 0:
#     #  feature_tensor[idx][0][difficulty_to_idx[prior_difficulties[-1]]] = 1
#     #feature_tensor[idx][0][difficulty_idx] = 1 # this is an impossible feature. see whether it learns corectly
#     feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
#     for language_index in language_indexes:
#       feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
#     feature_tensor[idx][0][4 + hour_idx] = 1
#     feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
#     if have_productivity_idx:
#       feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
#     if have_category_idx:
#       feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
#     # features for previous timesteps
#     for idx,difficulty in enumerate(prior_difficulties):
#       difficulty_idx = difficulty_to_idx[difficulty]
#       #feature_tensor[idx][0][difficulty_idx] = 1
#       hour_idx,weekday_idx = get_time_features_from_arrow(feature['prior_arrow_times'][idx])
#       domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(feature['prior_urls'][idx])
#       feature_tensor[idx][0][4 + hour_idx] = 1
#       feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
#       if have_productivity_idx:
#         feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
#       if have_category_idx:
#         feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
#       feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
#       for language_index in language_indexes:
#         feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
#     output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
#   return output









#def make_tensors_for_user(user):
#  features = make_features_for_user(user)
#  return make_tensors_from_features(features)

# def make_tensor_from_prior_difficulties_list(prior_difficulties):
#   tensor = torch.zeros(len(prior_difficulties), 1, n_features)
#   for idx,difficulty in enumerate(prior_difficulties):
#     difficulty_idx = difficulty_to_idx[difficulty]
#     tensor[idx][0][difficulty_idx] = 1
#   return tensor







def make_tensor_from_chosen_difficulty(chosen_difficulty : str):
  difficulty_idx = get_difficulty_idx(chosen_difficulty)
  tensor = torch.tensor([difficulty_idx], dtype=torch.long)
  return tensor

def get_domain_features_from_url(url : str) -> Tuple[int, bool, int, bool]:
  domain_to_productivity_idx = get_domain_to_productivity_idx()
  domain_to_category_idx = get_domain_to_category_idx()
  domain = url_to_domain(url)
  have_productivity_idx = False
  if domain in domain_to_productivity_idx:
    domain_productivity_idx = domain_to_productivity_idx[domain]
    have_productivity_idx = True
  else:
    domain_productivity_idx = None
  have_category_idx = False
  if domain in domain_to_category_idx:
    domain_category_idx = domain_to_productivity_idx[domain]
    have_category_idx = True
  else:
    domain_category_idx = None
  return domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx

def hour_to_hour_idx_4cat(hour : int) -> int: # hour: 0 to 24
  if 0 <= hour <= 6:
    return 0
  if 6 < hour <= 12:
    return 1
  if 12 < hour <= 18:
    return 2
  if 18 < hour <= 24:
    return 3
  raise Exception(hour)

def get_time_features_from_arrow(arrow_time) -> Tuple[int, int]:
  hour = arrow_time.hour
  hour_idx = hour_to_hour_idx_4cat(hour)
  weekday_idx = arrow_time.weekday()
  return hour_idx,weekday_idx



@memoize
def get_enabled_feature_info_list(enabled_features_list : List[str]) -> List[Dict[str, Any]]:
  output = []
  enabled_features = set(enabled_features_list)
  all_features = get_feature_info_list()
  for item in all_features:
    feature = item['name']
    if feature not in enabled_features:
      continue
    output.append(item)
  return output

@memoize
def get_num_features(enabled_features_list: List[str]) -> int:
  return sum([x['size'] for x in get_enabled_feature_info_list(enabled_features_list)])

@memoize
def make_get_index(enabled_feature_list : List[str]):
  current_idx = 0
  feature_name_to_idx = {}
  feature_info_list = get_enabled_feature_info_list(enabled_feature_list)
  for item in feature_info_list:
    feature = item['name']
    size = item['size']
    feature_name_to_idx[feature] = current_idx
    current_idx += size
  def get_index(feature : str) -> int:
    return feature_name_to_idx[feature]
  return get_index

def make_feature_setter(feature_tensor, enabled_feature_list : List[str]):
  enabled_feature_set = set(enabled_feature_list)
  get_index = make_get_index(enabled_feature_list)
  def get_feature_setter(time_idx, feature_name : str, offset : Any, value : int = 1):
    if feature_name not in enabled_feature_set:
      return
    offset_idx = get_offset_computer(feature_name)(offset)
    if offset_idx == None:
      return
    feature_idx = get_index(feature_name)
    feature_tensor[time_idx][0][feature_idx + offset_idx] = value
  return get_feature_setter



def identity(x : int) -> int:
  return x

def get_difficulty_idx(difficulty : str) -> int:
  difficulty_to_idx = {
    'nothing': 0,
    'easy': 1,
    'medium': 2,
    'hard': 3,
  }
  return difficulty_to_idx[difficulty]

def get_language_idx(language : str) -> int:
  language_to_index = get_language_to_index()
  return language_to_index[language]

def get_time_of_day_idx(arrow_time) -> int:
  hour = arrow_time.hour
  if 0 <= hour <= 6:
    return 0
  if 6 < hour <= 12:
    return 1
  if 12 < hour <= 18:
    return 2
  if 18 < hour <= 24:
    return 3
  raise Exception(hour)

def get_day_of_week_idx(arrow_time) -> int:
  weekday_idx = arrow_time.weekday()
  return weekday_idx

def get_domain_productivity_idx(url : str) -> int:
  domain = url_to_domain(url)
  domain_to_productivity_idx = get_domain_to_productivity_idx()
  return domain_to_productivity_idx.get(domain, None)

def get_domain_category_idx(url : str) -> int:
  domain = url_to_domain(url)
  domain_to_category_idx = get_domain_to_category_idx()
  return domain_to_category_idx.get(domain, None)



def get_features_concise():
  return [
    ('difficulty', 4, get_difficulty_idx),
    ('time_of_day', 4, get_time_of_day_idx),
    ('day_of_week', 7, get_day_of_week_idx),
    ('domain_productivity', len(get_domain_productivity_list()), get_domain_productivity_idx),
    ('domain_category', len(get_domain_category_list()), get_domain_category_idx),
    ('initial_difficulty', 4, get_difficulty_idx),
    ('languages', get_num_languages(), get_language_idx)
  ]

@memoize
def get_feature_info_list():
  output = []
  for item in get_features_concise():
    name = item[0]
    size = item[1]
    if len(item) == 2:
      compute = identity
    else:
      compute = item[2]
    output.append({
      'name': name,
      'size': size,
      'compute': compute,
    })
  return output

@memoize
def get_feature_names():
  return [x['name'] for x in get_feature_info_list()]

def get_name_to_feature_info():
  output = {}
  for feature_info in get_feature_info_list():
    output[feature_info['name']] = feature_info
  return output

def get_feature(feature_name):
  return get_name_to_feature_info()[feature_name]

@memoize
def get_offset_computer(feature_name):
  return get_feature(feature_name)['compute']



#def last_n_entries(l, n):
#  return l[-n:]

#print(last_n_entries([1,2,3,4,5,6], 3))



def sample_prior_visits_every_n_visits(l, n):
  output = []
  for x in l:
    if (x['idx'] % n) == 0:
      output.append(x)
  return output

# todo attach a num_prior_entries entry. so that we only use that many prior entries
def make_tensors_from_features_v7(features, parameters):
  print('running make_tensors_from_features')
  enabled_feature_list = parameters['enabled_feature_list']
  num_prior_entries = parameters.get('num_prior_entries', 10)
  sample_every_n_visits = parameters.get('sample_every_n_visits', 1)
  sample_difficulty_every_n_visits = parameters.get('sample_difficulty_every_n_visits', 1)
  disable_prior_visit_history = parameters.get('disable_prior_visit_history', False)
  disable_difficulty_history = parameters.get('disable_difficulty_history', False)
  enable_current_difficulty = parameters.get('enable_current_difficulty', False)
  output = []
  for featurenum,feature in enumerate(features):
    #print(featurenum, 'of', len(features))
    #url = feature['url']
    #domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(url)
    #hour_idx,weekday_idx = get_time_features_from_arrow(feature['arrow_time'])
    #chosen_difficulty = feature['difficulty']
    #language_indexes = convert_language_list_to_language_indexes(feature['languages'])
    #prior_difficulties = feature['prior_difficulties']
    #user = feature['user']
    prior_entries = []
    if not disable_prior_visit_history:
      prior_entries = sample_prior_visits_every_n_visits(feature['prior_entries'], sample_every_n_visits)
    history_length_current = min(num_prior_entries, len(prior_entries))
    category_tensor = make_tensor_from_chosen_difficulty(feature['difficulty'])
    feature_tensor = torch.zeros(history_length_current+1, 1, get_num_features(enabled_feature_list)) # n_features = 15 in this version
    f = make_feature_setter(feature_tensor, enabled_feature_list)
    # features for current timestep
    idx = history_length_current # len(feature['prior_entries'])
    #difficulty = feature['difficulty']
    #difficulty_idx = difficulty_to_idx[difficulty]
    #if len(prior_difficulties) > 0:
    #  feature_tensor[idx][0][difficulty_to_idx[prior_difficulties[-1]]] = 1
    if enable_current_difficulty:
      f(idx, 'difficulty', feature['difficulty']) # this is an impossible feature. see whether it learns correctly
    #feature_tensor[idx][0][difficulty_idx] = 1 # this is an impossible feature. see whether it learns corectly
    f(idx, 'initial_difficulty', feature['initial_difficulty'])
    #feature_tensor[idx][0][fi('initial_difficulty') + difficulty_to_idx[feature['initial_difficulty']]] = 1
    for language in feature['languages']:
      f(idx, 'languages', language)
    #for language_index in language_indexes:
    #  feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
    #feature_tensor[idx][0][4 + hour_idx] = 1
    f(idx, 'time_of_day', feature['arrow_time'])
    #feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
    f(idx, 'day_of_week', feature['arrow_time'])
    #if have_productivity_idx:
    #  feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
    f(idx, 'domain_productivity', feature['url'])
    #if have_category_idx:
    #  feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
    f(idx, 'domain_category', feature['url'])
    # features for previous timesteps
    for idx,prior_entry in enumerate(prior_entries[-history_length_current:]):
      #difficulty_idx = difficulty_to_idx[difficulty]
      #feature_tensor[idx][0][difficulty_idx] = 1
      if (not disable_difficulty_history) and ((prior_entry['idx'] % sample_difficulty_every_n_visits) == 0):
        f(idx, 'difficulty', prior_entry['difficulty'])
      f(idx, 'initial_difficulty', feature['initial_difficulty'])
      for language in feature['languages']:
        f(idx, 'languages', language)
      #hour_idx,weekday_idx = get_time_features_from_arrow(feature['prior_arrow_times'][idx])
      #domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(feature['prior_urls'][idx])
      #feature_tensor[idx][0][4 + hour_idx] = 1
      f(idx, 'time_of_day', prior_entry['arrow_time'])
      f(idx, 'day_of_week', prior_entry['arrow_time'])
      #feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
      #if have_productivity_idx:
      #  feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
      f(idx, 'domain_productivity', prior_entry['url'])
      #if have_category_idx:
      #  feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
      f(idx, 'domain_category', prior_entry['url'])
      #feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
      #for language_index in language_indexes:
      #  feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
    output.append({'user': feature['user'], 'chosen_difficulty': feature['difficulty'], 'category': category_tensor, 'feature': feature_tensor})
  return output

#make_tensors_from_features = make_tensors_from_features_v7









# todo attach a num_prior_entries entry. so that we only use that many prior entries
def make_tensors_from_features_for_user_v8(user, features, parameters):
  enabled_feature_list = parameters['enabled_feature_list']
  num_prior_entries = parameters.get('num_prior_entries', 10)
  sample_every_n_visits = parameters.get('sample_every_n_visits', 1)
  sample_difficulty_every_n_visits = parameters.get('sample_difficulty_every_n_visits', 1)
  disable_prior_visit_history = parameters.get('disable_prior_visit_history', False)
  disable_difficulty_history = parameters.get('disable_difficulty_history', False)
  enable_current_difficulty = parameters.get('enable_current_difficulty', False)
  output = []
  if len(features['difficulty_items']) < 1:
    raise Exception('length of difficulty_items must be at least 1')
  difficulty_items = []
  for idx,difficulty_item in enumerate(features['difficulty_items']):
    difficulty_item = copy(difficulty_item)
    difficulty_item['idx'] = idx
    difficulty_items.append(difficulty_item)
  difficulty_items_filtered = []
  if sample_every_n_visits > 1:
    difficulty_items_filtered = sample_prior_visits_every_n_visits(difficulty_items, sample_every_n_visits)
  else:
    difficulty_items_filtered = difficulty_items
  for visit_idx,difficulty_item in enumerate(difficulty_items):
    history_length_current = min(visit_idx, num_prior_entries)
    category_tensor = make_tensor_from_chosen_difficulty(difficulty_item['difficulty'])
    feature_tensor = torch.zeros(history_length_current+1, 1, get_num_features(enabled_feature_list)) # n_features = 15 in this version
    f = make_feature_setter(feature_tensor, enabled_feature_list)
    # features for current timestep
    idx = history_length_current # len(feature['prior_entries'])
    # features contains initial_difficulty, languages, difficulty_items
    # difficulty_item contains difficulty, url, arrow_time
    if enable_current_difficulty:
      f(idx, 'difficulty', difficulty_item['difficulty'])
    f(idx, 'initial_difficulty', features['initial_difficulty'])
    for language in features['languages']:
      f(idx, 'languages', language)
    f(idx, 'time_of_day', difficulty_item['arrow_time'])
    f(idx, 'day_of_week', difficulty_item['arrow_time'])
    f(idx, 'domain_productivity', difficulty_item['url'])
    f(idx, 'domain_category', difficulty_item['url'])
    # features for previous timesteps
    prior_entries = []
    if not disable_prior_visit_history:
      #prior_entries = sample_prior_visits_every_n_visits(prior_entries, sample_every_n_visits)
      #for idx,prior_entry in enumerate(features['difficulty_items'][:visit_idx]):
      #  prior_entry = copy(prior_entry)
      #  prior_entry['idx'] = idx
      #  prior_entries.append(prior_entry)
      for idx,prior_entry in enumerate(difficulty_items[visit_idx - (history_length_current*sample_every_n_visits) : visit_idx : sample_every_n_visits]):
        if (not disable_difficulty_history) and ((prior_entry['idx'] % sample_difficulty_every_n_visits) == 0):
          f(idx, 'difficulty', prior_entry['difficulty'])
        f(idx, 'initial_difficulty', features['initial_difficulty'])
        for language in features['languages']:
          f(idx, 'languages', language)
        f(idx, 'time_of_day', prior_entry['arrow_time'])
        f(idx, 'day_of_week', prior_entry['arrow_time'])
        f(idx, 'domain_productivity', prior_entry['url'])
        f(idx, 'domain_category', prior_entry['url'])
    output.append({'user': user, 'visit_idx': visit_idx, 'chosen_difficulty': difficulty_item['difficulty'], 'category': category_tensor, 'feature': feature_tensor})
  return output

# import time
# start = time.time()
# foobar = make_tensors_from_features_for_user_v8('8d2c9eb27dee2dc85bca705b', all_features_data['8d2c9eb27dee2dc85bca705b'], {'enabled_feature_list': ['time_of_day']})
# end = time.time()
# print(end - start)



def make_tensors_from_features_v8(features, parameters):
  output = []
  for user,user_features in features.items():
    for x in make_tensors_from_features_for_user_v8(user, user_features, parameters):
      output.append(x)
  return output

make_tensors_from_features = make_tensors_from_features_v8



#print(get_feature_names())
#print(get_num_features(get_feature_names()))



#all_data_tensors = make_tensors_from_features(all_features_data, {'enabled_feature_list': ['time_of_day']})













