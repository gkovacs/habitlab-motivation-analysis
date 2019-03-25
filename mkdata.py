#!/usr/bin/env python
# md5: 32f948153c626a6de9b599cb70af69cf
#!/usr/bin/env python
# coding: utf-8



from typing import Dict, List, Tuple



import sys
#sys.version



from importlib import reload



from memoize import memoize # pip install memoize2
#import diskmemo
#reload(diskmemo)
from diskmemo import diskmemo



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



@memoize
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



@memoize
def get_language_list():
  user_list = get_users_with_choose_difficulty()
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



#print(len(language_list))



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



difficulty_to_idx = {
  'nothing': 0,
  'easy': 1,
  'medium': 2,
  'hard': 3,
}



history_length = 100

def make_features_for_user(user):
  output = []
  difficulty_items = get_choose_difficulty_items_for_user(user)
  prior_entries = []
  languages = get_languages_for_user(user)
  initial_difficulty = get_initial_difficulty_for_user(user)
  if initial_difficulty == None:
    return []
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
    })
    prior_entries.append({
      'url': url,
      'difficulty': difficulty,
      'arrow_time': arrow_time,
    })
    if len(prior_entries) > history_length:
      prior_entries = prior_entries[-history_length:]
  return output



@diskmemo
def get_users():
  return get_users_with_choose_difficulty()

@diskmemo
def get_all_features_data():
  all_features_data = []
  for user in get_users():
    print(user)
    #tensors = make_tensors_for_user(user)
    feature_list = make_features_for_user(user)
    for features in feature_list:
      all_features_data.append(features)
  return all_features_data







all_features_data = get_all_features_data()



def make_tensors_from_features_v1(features):
  output = []
  for feature in features:
    chosen_difficulty = feature['difficulty']
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 4 in this version
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      feature_tensor[idx][0][difficulty_idx] = 1
    #feature_tensor = make_tensor_from_prior_difficulties_list(prior_difficulties)
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output

def make_tensors_from_features_v2(features):
  output = []
  for feature in features:
    hour = feature['arrow_time'].hour
    chosen_difficulty = feature['difficulty']
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 1 in this version
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      feature_tensor[idx][0][0] = difficulty_idx
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output

def make_tensors_from_features_v3(features):
  output = []
  for feature in features:
    hour = feature['arrow_time'].hour
    hour_idx = hour_to_hour_idx_4cat(hour)
    weekday_idx = feature['arrow_time'].weekday()
    chosen_difficulty = feature['difficulty']
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 15 in this version
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      feature_tensor[idx][0][difficulty_idx] = 1
      feature_tensor[idx][0][4 + hour_idx] = 1
      feature_tensor[idx][0][8 + weekday_idx] = 1
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output

def make_tensors_from_features_v4(features):
  output = []
  for feature in features:
    url = feature['url']
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
    hour = feature['arrow_time'].hour
    hour_idx = hour_to_hour_idx_4cat(hour)
    weekday_idx = feature['arrow_time'].weekday()
    chosen_difficulty = feature['difficulty']
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties), 1, n_features) # n_features = 15 in this version
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      feature_tensor[idx][0][difficulty_idx] = 1
      feature_tensor[idx][0][4 + hour_idx] = 1
      feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
      if have_productivity_idx:
        feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
      if have_category_idx:
        feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output

def make_tensors_from_features_v5(features): # this one cheats because we have the reference information included
  output = []
  for feature in features:
    url = feature['url']
    domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(url)
    hour_idx,weekday_idx = get_time_features_from_arrow(feature['arrow_time'])
    chosen_difficulty = feature['difficulty']
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties)+1, 1, n_features) # n_features = 15 in this version
    # features for current timestep
    idx = len(prior_difficulties)
    difficulty = feature['difficulty']
    difficulty_idx = difficulty_to_idx[difficulty]
    #if len(prior_difficulties) > 0:
    #  feature_tensor[idx][0][difficulty_to_idx[prior_difficulties[-1]]] = 1
    #feature_tensor[idx][0][difficulty_idx] = 1 # this is an impossible feature. see whether it learns corectly
    feature_tensor[idx][0][4 + hour_idx] = 1
    feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
    if have_productivity_idx:
      feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
    if have_category_idx:
      feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
    # features for previous timesteps
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      #feature_tensor[idx][0][difficulty_idx] = 1
      hour_idx,weekday_idx = get_time_features_from_arrow(feature['prior_arrow_times'][idx])
      domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(feature['prior_urls'][idx])
      feature_tensor[idx][0][4 + hour_idx] = 1
      feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
      if have_productivity_idx:
        feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
      if have_category_idx:
        feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output

def make_tensors_from_features_v6(features): # this one cheats because we have the reference information included
  output = []
  for feature in features:
    url = feature['url']
    domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(url)
    hour_idx,weekday_idx = get_time_features_from_arrow(feature['arrow_time'])
    chosen_difficulty = feature['difficulty']
    language_indexes = convert_language_list_to_language_indexes(feature['languages'])
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties)+1, 1, n_features) # n_features = 15 in this version
    # features for current timestep
    idx = len(prior_difficulties)
    difficulty = feature['difficulty']
    difficulty_idx = difficulty_to_idx[difficulty]
    #if len(prior_difficulties) > 0:
    #  feature_tensor[idx][0][difficulty_to_idx[prior_difficulties[-1]]] = 1
    #feature_tensor[idx][0][difficulty_idx] = 1 # this is an impossible feature. see whether it learns corectly
    feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
    for language_index in language_indexes:
      feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
    feature_tensor[idx][0][4 + hour_idx] = 1
    feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
    if have_productivity_idx:
      feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
    if have_category_idx:
      feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
    # features for previous timesteps
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      #feature_tensor[idx][0][difficulty_idx] = 1
      hour_idx,weekday_idx = get_time_features_from_arrow(feature['prior_arrow_times'][idx])
      domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(feature['prior_urls'][idx])
      feature_tensor[idx][0][4 + hour_idx] = 1
      feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
      if have_productivity_idx:
        feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
      if have_category_idx:
        feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
      feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
      for language_index in language_indexes:
        feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output









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
  difficulty_idx = difficulty_to_idx[chosen_difficulty]
  tensor = torch.tensor([difficulty_idx], dtype=torch.long)
  return tensor

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

def get_domain_features_from_url(url : str):
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

def get_time_features_from_arrow(arrow_time):
  hour = arrow_time.hour
  hour_idx = hour_to_hour_idx_4cat(hour)
  weekday_idx = arrow_time.weekday()
  return hour_idx,weekday_idx



#%%typecheck --ignore-missing-imports

#hour_to_hour_idx_4cat(6)








def get_features_and_sizes() -> List[Tuple[str, int]]:
  return [
    ('difficulty', 4),
    ('time_of_day_4', 4),
    ('day_of_week', 7),
    ('domain_productivity', len(get_domain_productivity_list())),
    ('domain_category', len(get_domain_category_list())),
    #[],
  ]

@memoize
def get_enabled_features_with_sizes(enabled_features : Dict[str, bool]) -> List[Tuple[str, int]]:
  output = []
  features_and_sizes = get_features_and_sizes()
  for feature,size in features_and_sizes:
    if enabled_features.get(feature, False) == False:
      continue
    output.append((feature, size))
  return output

@memoize
def get_num_features():
  return len(get_enabled_features_with_sizes())

def make_get_index(enabled_features):
  current_idx = 0
  feature_name_to_idx = {}
  features_and_sizes = get_enabled_features_with_sizes(enabled_features)
  for feature,size in features_and_sizes:
    if enabled_features.get(feature, False) == False:
      continue
    feature_name_to_idx[feature] = current_idx
    current_idx += size
  def get_index(feature):
    return feature_name_to_idx[feature]
  return get_index

def make_tensors_from_features_v7(features): # this one cheats because we have the reference information included
  output = []
  for feature in features:
    url = feature['url']
    domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(url)
    hour_idx,weekday_idx = get_time_features_from_arrow(feature['arrow_time'])
    chosen_difficulty = feature['difficulty']
    language_indexes = convert_language_list_to_language_indexes(feature['languages'])
    prior_difficulties = feature['prior_difficulties']
    user = feature['user']
    category_tensor = make_tensor_from_chosen_difficulty(chosen_difficulty)
    feature_tensor = torch.zeros(len(prior_difficulties)+1, 1, n_features) # n_features = 15 in this version
    # features for current timestep
    idx = len(prior_difficulties)
    difficulty = feature['difficulty']
    difficulty_idx = difficulty_to_idx[difficulty]
    #if len(prior_difficulties) > 0:
    #  feature_tensor[idx][0][difficulty_to_idx[prior_difficulties[-1]]] = 1
    #feature_tensor[idx][0][difficulty_idx] = 1 # this is an impossible feature. see whether it learns corectly
    feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
    for language_index in language_indexes:
      feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
    feature_tensor[idx][0][4 + hour_idx] = 1
    feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
    if have_productivity_idx:
      feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
    if have_category_idx:
      feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
    # features for previous timesteps
    for idx,difficulty in enumerate(prior_difficulties):
      difficulty_idx = difficulty_to_idx[difficulty]
      #feature_tensor[idx][0][difficulty_idx] = 1
      hour_idx,weekday_idx = get_time_features_from_arrow(feature['prior_arrow_times'][idx])
      domain_productivity_idx,have_productivity_idx,domain_category_idx,have_category_idx = get_domain_features_from_url(feature['prior_urls'][idx])
      feature_tensor[idx][0][4 + hour_idx] = 1
      feature_tensor[idx][0][4 + 4 + weekday_idx] = 1
      if have_productivity_idx:
        feature_tensor[idx][0][4 + 4 + 7 + domain_productivity_idx] = 1
      if have_category_idx:
        feature_tensor[idx][0][4 + 4 + 7 + 5 + domain_category_idx] = 1
      feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + difficulty_to_idx[feature['initial_difficulty']]] = 1
      for language_index in language_indexes:
        feature_tensor[idx][0][4 + 4 + 7 + 5 + 69 + 5 + language_index] = 1
    output.append({'user': user, 'chosen_difficulty': chosen_difficulty, 'category': category_tensor, 'feature': feature_tensor})
  return output

make_tensors_from_features = make_tensors_from_features_v7

















