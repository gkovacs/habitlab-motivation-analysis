#!/usr/bin/env python
# md5: 216ab487220ce5fe66854366c8c0668b
#!/usr/bin/env python
# coding: utf-8



from train_utils import *
from plot_utils import *
from scipy.stats import chisquare



def get_most_common_key_in_dict(d):
  most_common = None
  for k in sorted(d.keys()):
    if most_common == None:
      most_common = k
    elif d[k] > d[most_common]:
      most_common = k
  return most_common

def get_most_common_survey_result_for_user(user):
  results = get_survey_results_for_user(user)
  return get_most_common_key_in_dict(results)

def get_most_common_survey_result_for_install(install):
  results = get_survey_results_for_install(install)
  return get_most_common_key_in_dict(results)



def get_survey_results_across_all_installs():
  output = Counter()
  for install in get_installs_with_asknext_survey():
    for k,v in get_survey_results_for_install(install).items():
      output[k] += v
  return output

def get_survey_results_across_all_users():
  output = Counter()
  for user in get_users_with_asknext_survey():
    for k,v in get_survey_results_for_user(user).items():
      output[k] += v
  return output



def get_survey_results_for_install(install):
  output = Counter()
  collection_items = get_collection_for_install(install, 'internal:choose_difficulty')
  for item in collection_items:
    if ('developer_mode' in item) and (item['developer_mode'] == True):
      continue
    if ('unofficial_version' in item):
      continue
    if 'action_type' in item and item['action_type'] == 'asknext_chosen':
      asknext = item['asknext']
      output[asknext] += 1
  return output

def get_survey_results_for_user(user):
  output = Counter()
  collection_items = get_collection_for_user(user, 'internal:choose_difficulty')
  for item in collection_items:
    if ('developer_mode' in item) and (item['developer_mode'] == True):
      continue
    if ('unofficial_version' in item):
      continue
    if 'action_type' in item and item['action_type'] == 'asknext_chosen':
      asknext = item['asknext']
      output[asknext] += 1
  return output



def get_installs_with_asknext_survey():
  output = []
  installs_with_difficulty = get_installs_with_choose_difficulty()
  for install in installs_with_difficulty:
    abtest_settings = get_abtest_settings_for_install(install)
    if abtest_settings.get('frequency_of_choose_difficulty') == 'survey':
      output.append(install)
  return output

def get_users_with_asknext_survey():
  output = []
  users_with_difficulty = get_users_with_choose_difficulty()
  for user in users_with_difficulty:
    abtest_settings = get_abtest_settings(user)
    if abtest_settings.get('frequency_of_choose_difficulty') == 'survey':
      output.append(user)
  return output



def get_survey_choice_to_num_installs_who_choose_it_most_commonly():
  output = Counter()
  for install in get_installs_with_asknext_survey():
    most_common_result = get_most_common_survey_result_for_install(install)
    if most_common_result == None:
      continue
    output[most_common_result] += 1
  return output

def get_survey_choice_to_num_users_who_choose_it_most_commonly():
  output = Counter()
  for user in get_users_with_asknext_survey():
    most_common_result = get_most_common_survey_result_for_user(user)
    if most_common_result == None:
      continue
    output[most_common_result] += 1
  return output



def get_most_common_difficulty_for_user(user):
  difficulty_counts = get_choose_difficulty_counts_for_user(user)
  max_count = 0
  max_difficulty = None
  for difficulty,count in difficulty_counts.items():
    if count > max_count:
      max_count = count
      max_difficulty = difficulty
  return max_difficulty

def get_survey_choice_to_difficulty_choice_counts():
  output = {
    'nextvisit': Counter(),
    'hour': Counter(),
    'day': Counter(),
    'week': Counter(),
  }
  for user in get_users_with_asknext_survey():
    collection_items = get_collection_for_user(user, 'internal:choose_difficulty')
    for item in collection_items:
      if ('developer_mode' in item) and (item['developer_mode'] == True):
        continue
      if ('unofficial_version' in item):
        continue
      if 'action_type' in item and item['action_type'] == 'asknext_chosen':
        asknext = item['asknext']
        difficulty = item['difficulty']
        output[asknext][difficulty] += 1
        #output[asknext] += 1
  return output

def plot_survey_choice_to_difficulty_choice_counts():
  plot_dictdict_as_bar(
    get_survey_choice_to_difficulty_choice_counts(),
    ylabel = 'Number of times chosen',
    xlabel = 'Intervention difficulty chosen, along with when to ask about difficulty again',
    title = 'Choices for intervention difficulty and when to ask about difficulty again',
  )

def plot_survey_choice_counts_raw_per_user():
  survey_results = get_survey_results_across_all_users()
  print(survey_results)
  print(chisquare(list(survey_results.values())))
  plot_dict_as_bar(
    survey_results,
    ylabel = 'Number of times chosen',
    xlabel = 'Choice for when to ask next about intervention difficulty',
    title = 'Choice for when to ask next about intervention difficulty, raw counts'
  )

def plot_survey_choice_counts_raw_per_install():
  survey_results = get_survey_results_across_all_installs()
  print(survey_results)
  print(chisquare(list(survey_results.values())))
  plot_dict_as_bar(
    survey_results,
    ylabel = 'Number of times chosen',
    xlabel = 'Choice for when to ask next about intervention difficulty',
    title = 'Choice for when to ask next about intervention difficulty, raw counts'
  )

def plot_survey_choice_counts_install_normalized():
  survey_choice_to_num_installs_who_choose_it_most_commonly = get_survey_choice_to_num_installs_who_choose_it_most_commonly()
  print(survey_choice_to_num_installs_who_choose_it_most_commonly)
  print(chisquare(list(survey_choice_to_num_installs_who_choose_it_most_commonly.values())))
  plot_dict_as_bar(
    survey_choice_to_num_installs_who_choose_it_most_commonly,
    ylabel = 'Number of users',
    xlabel = 'User\'s most frequent choice for when to next ask about intervention difficulty',
    title = 'Most frequent choice for when to ask next about intervention difficulty, by number of users',
  )

def plot_survey_choice_counts_user_normalized():
  survey_choice_to_num_users_who_choose_it_most_commonly = get_survey_choice_to_num_users_who_choose_it_most_commonly()
  print(survey_choice_to_num_users_who_choose_it_most_commonly)
  print(chisquare(list(survey_choice_to_num_users_who_choose_it_most_commonly.values())))
  plot_dict_as_bar(
    survey_choice_to_num_users_who_choose_it_most_commonly,
    ylabel = 'Number of users',
    xlabel = 'User\'s most frequent choice for when to next ask about intervention difficulty',
    title = 'Most frequent choice for when to ask next about intervention difficulty, by number of users',
  )







