#!/usr/bin/env python
# md5: a20b17af3afa9cad6ac6ee30cf34d35f
#!/usr/bin/env python
# coding: utf-8



import sys
#sys.version



from memoize import memoize # pip install memoize2



from importlib import reload



import libmotivation
reload(libmotivation)
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





