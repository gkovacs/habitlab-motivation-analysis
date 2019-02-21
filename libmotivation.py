#!/usr/bin/env python
# md5: 29c61ff8ffc6c6c1726bca72086fc7fc
#!/usr/bin/env python
# coding: utf-8



import math
from browser_libs import get_collection_items, get_collection_names, get_collection_for_user
from memoize import memoize # pip install memoize2
from collections import Counter
import pandas as pd
import numpy as np
import scipy as sp
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)



@memoize
def get_users_with_choose_difficulty():
  collection_names = get_collection_names()
  output = []
  for x in collection_names:
    if x.endswith('_internal:choose_difficulty'):
      user = x.replace('_internal:choose_difficulty', '')
      output.append(user)
  return output



@memoize
def get_most_common_difficulty_for_user(user):
  difficulty_counts = get_choose_difficulty_counts_for_user(user)
  max_count = 0
  max_difficulty = None
  for difficulty,count in difficulty_counts.items():
    if count > max_count:
      max_count = count
      max_difficulty = difficulty
  return max_difficulty



@memoize
def get_most_common_difficulty_overall():
  counts = Counter()
  for user in get_users_with_choose_difficulty():
    difficulty = get_most_common_difficulty_for_user(user)
    if difficulty == None:
      continue
    counts[difficulty] += 1
  return max(counts, key=counts.get)



@memoize
def get_choose_difficulty_items_for_user(user):
  collection_items = get_collection_for_user(user, 'internal:choose_difficulty')
  output = []
  for x in collection_items:
    if 'is_new_session' not in x:
      continue
    if x['is_new_session'] != True:
      continue
    if ('developer_mode' in x) and (x['developer_mode'] == True):
      continue
    if ('is_preview_mode' in x) and (x['is_preview_mode'] == True):
      continue
    if ('is_suggestion_mode' in x) and (x['is_suggestion_mode'] == True):
      continue
    if ('unofficial_version' in x):
      continue
    output.append(x)
  return output



def get_choose_difficulty_counts_for_user(user):
  collection_items = get_choose_difficulty_items_for_user(user)
  output = {}
  for x in collection_items:
    if 'type' not in x:
      continue
    if x['type'] != 'action':
      continue
    if 'difficulty' not in x:
      continue
    difficulty = x['difficulty']
    if difficulty not in output:
      output[difficulty] = 1
    else:
      output[difficulty] += 1
  return output



def get_choose_difficulty_counts_for_user_list(user_list):
  output = Counter()
  for user in user_list:
    difficulty_counts = get_choose_difficulty_counts_for_user(user)
    for difficulty,count in difficulty_counts.items():
      output[difficulty] += count
  return output



def get_choose_difficulty_counts_for_user_list_user_normalized(user_list):
  output = Counter()
  for user in user_list:
    difficulty_counts = get_choose_difficulty_counts_for_user(user)
    difficulty_counts = to_percent_dict(difficulty_counts)
    for difficulty,count in difficulty_counts.items():
      output[difficulty] += count
  return to_percent_dict(output)



def get_random_counts():
  user_list = get_users_with_choose_difficulty()
  random_counts = Counter()
  for user in user_list:
    collection_items = get_choose_difficulty_items_for_user(user)
    for item in collection_items:
      if 'is_random' in item:
        is_random = item['is_random']
        random_counts[is_random] += 1
  return random_counts



def get_choose_difficulty_counts_for_all_users():
  user_list = get_users_with_choose_difficulty()
  return get_choose_difficulty_counts_for_user_list(user_list)



def get_total_counts_for_user(user):
  difficulty_counts = get_choose_difficulty_counts_for_user(user)
  return sum(difficulty_counts.values())



def num_types_tried(user):
  difficulty_counts = get_choose_difficulty_counts_for_user(user)
  return len(difficulty_counts.keys())



def did_user_try_multiple(user):
  return num_types_tried(user) > 1



def get_try_multiple_counts_for_all_users():
  output = {
    'none_total': 0,
    'one_total': 0,
    'one_tried': 0,
    'multiple_tried': 0,
  }
  for user in get_users_with_choose_difficulty():
    total_counts = get_total_counts_for_user(user)
    if total_counts == 0:
      output['none_total'] += 1
      continue
    if total_counts == 1:
      output['one_total'] += 1
      continue
    if did_user_try_multiple(user):
      output['multiple_tried'] += 1
    else:
      output['one_tried'] += 1
  return output



def get_breakdown_for_one_tried():
  output = Counter()
  for user in get_users_with_choose_difficulty():
    total_counts = get_total_counts_for_user(user)
    if total_counts <= 1:
      continue
    if did_user_try_multiple(user):
      continue
    difficulty_counts = get_choose_difficulty_counts_for_user(user)
    chosen_difficulty = list(difficulty_counts.keys())[0]
    output[chosen_difficulty] += difficulty_counts[chosen_difficulty]
  return output



@memoize
def get_abtest_settings(user):
  output = {}
  collection_items = get_collection_for_user(user, 'synced:experiment_vars')
  for item in collection_items:
    if 'key' not in item:
      continue
    if 'val' not in item:
      continue
    key = item['key']
    val = item['val']
    output[key] = val
  return output



def get_abtest_options_for_group(user_list):
  conditions = {}
  for user in user_list:
    abtest_settings = get_abtest_settings(user)
    for k,v in abtest_settings.items():
      if k == 'intervention_firstimpression_notice_seenlist':
        continue
      if k not in conditions:
        conditions[k] = []
      if v not in conditions[k]:
        conditions[k].append(v)
  output = {}
  for abtest_name,options in conditions.items():
    if len(options) > 1:
      output[abtest_name] = options
  return output



def get_abtest_condition_to_user_list(abtest_name):
  # note this only applies to users in the get_users_with_choose_difficulty experiment currently
  output = {}
  for user in get_users_with_choose_difficulty():
    abtest_settings = get_abtest_settings(user)
    if abtest_name not in abtest_settings:
      continue
    abtest_option = abtest_settings[abtest_name]
    if abtest_option not in output:
      output[abtest_option] = []
    output[abtest_option].append(user)
  return output



def get_choose_difficulty_level_mean_for_user_list(users):
  difficulty_to_counts = get_choose_difficulty_counts_for_user_list(users)
  difficulty_to_value = {
    'nothing': 0,
    'easy': 1,
    'medium': 2,
    'hard': 3,
  }
  values = []
  for difficulty,count in difficulty_to_counts.items():
    value = difficulty_to_value[difficulty]
    values.append(value)
  return np.mean(values)



def get_choose_difficulty_level_mean_by_abtest(abtest_name):
  condition_to_user_list = get_abtest_condition_to_user_list(abtest_name)
  for condition,user_list in condition_to_user_list.items():
    print(condition + ':' + str(get_choose_difficulty_level_mean_for_user_list(user_list)))



def get_key_to_ordering_mappings():
  key_orderings = [
    [
      'this_intervention',
      'time_afford',
      'settings_update',
    ],
    [
      'nothing',
      'easy',
      'medium',
      'hard',
    ],
  ]
  key_to_ordering = {}
  for ordering in key_orderings:
    key = ' '.join(sorted(ordering))
    key_to_ordering[key] = ordering
  return key_to_ordering

def order_list(keys):
  key = ' '.join(sorted(keys))
  key_to_ordering_mappings = get_key_to_ordering_mappings()
  return get_key_to_ordering_mappings()[key]

def printdict(d):
  keys = order_list(d.keys())
  for x in keys:
    print(x + ': ' + str(d[x]))

def to_percent_dict(d):
  output = {}
  total = sum(d.values())
  for k,v in d.items():
    output[k] = v / total
  return output

def printdict_percent(d):
  d = to_percent_dict(d)
  printdict(d)



def plotbar(values, labels=None, title=''):
  data = [go.Bar(
    x=labels,
    y=values,
  )]
  layout = go.Layout(title=title)
  fig = go.Figure(data=data, layout=layout)
  iplot(fig)

def plotbarh(values, labels=None, title=''):
  data = [go.Bar(
    y=labels,
    x=values,
    orientation='h',
  )]
  layout = go.Layout(title=title)
  fig = go.Figure(data=data, layout=layout)
  iplot(fig)

def plothist(values, title=''):
  data = [go.Histogram(x=values)]
  layout = go.Layout(title=title)
  fig = go.Figure(data=data, layout=layout)
  iplot(fig)



def plotdict(d, title=''):
  keys = order_list(d.keys())
  values = [d[k] for k in keys]
  plotbarh(values, keys, title)



def get_daynum_to_difficulty_choices(user):
  difficulty_choices = get_choose_difficulty_items_for_user(user)
  first_timestamp = None
  output = {}
  for item in difficulty_choices:
    if 'type' not in item:
      continue
    if item['type'] != 'action':
      continue
    if 'difficulty' not in item:
      continue
    difficulty = item['difficulty']
    timestamp = item['timestamp_local']
    if first_timestamp == None or timestamp < first_timestamp:
      first_timestamp = timestamp
  for item in difficulty_choices:
    if 'type' not in item:
      continue
    if item['type'] != 'action':
      continue
    if 'difficulty' not in item:
      continue
    difficulty = item['difficulty']
    timestamp = item['timestamp_local']
    daynum = (timestamp - first_timestamp) / (1000 * 3600 * 24)
    daynum = int(math.floor(daynum))
    if daynum not in output:
      output[daynum] = {}
    if difficulty not in output[daynum]:
      output[daynum][difficulty] = 0
    output[daynum][difficulty] += 1
  return output

def get_user_to_daynum_to_difficulty_choices():
  output = {}
  user_list = get_users_with_choose_difficulty()
  for user in user_list:
    difficulty_counts = get_choose_difficulty_counts_for_user(user)
    if len(difficulty_counts.keys()) == 0:
      continue
    daynum_to_difficulty_choices = get_daynum_to_difficulty_choices(user)
    if len(daynum_to_difficulty_choices.keys()) == 0:
      continue
    output[user] = daynum_to_difficulty_choices
  return output

def get_daynum_to_difficulty_choices_over_n_days(num_days):
  user_to_daynum_to_difficulty_choices = get_user_to_daynum_to_difficulty_choices()
  output = []
  for daynum in range(num_days):
    item = {}
    for x in 'nothing easy medium hard'.split(' '):
      item[x] = 0
    output.append(item)
  for user,daynum_to_difficulty_choices in user_to_daynum_to_difficulty_choices.items():
    has_data = True
    for daynum in range(num_days):
      if not daynum in daynum_to_difficulty_choices:
        has_data = False
        break
    if not has_data:
      continue
    for daynum in range(num_days):
      for difficulty,num_chosen in to_percent_dict(daynum_to_difficulty_choices[daynum]).items():
        output[daynum][difficulty] += num_chosen
      output[daynum] = to_percent_dict(output[daynum])
  return output

def list_of_dictionaries_to_dictionary_with_list_values(dlist):
  output = {}
  keys = dlist[0].keys()
  for k in keys:
    output[k] = []
  for d in dlist:
    for k,v in d.items():
      output[k].append(v)
  return output

def plotline(values, title=''):
  trace = go.Scatter(
    x = list(range(len(values))),
    y=values,
  )
  data = [trace]
  layout = go.Layout(title=title)
  fig = go.Figure(data=data, layout=layout)
  iplot(fig)

def plotlines(dict_to_values, title=''):
  data = []
  for label,values in dict_to_values.items():
    trace = go.Scatter(
      x = list(range(len(values))),
      y=values,
      name=label,
    )
    data.append(trace)
  layout = go.Layout(title=title)
  fig = go.Figure(data=data, layout=layout)
  iplot(fig)

#plotline([3,5,2])
#plotlines({'a': [3,5,2], 'b': [7,7,7]})



def compute_entropy_for_difficulty_selections(difficulty_selection_dict):
  if len(difficulty_selection_dict.keys()) == 0:
    return None
  probs = to_percent_dict(difficulty_selection_dict)
  items_to_sum = []
  for k,prob in probs.items():
    items_to_sum.append(prob * math.log(prob)/math.log(2))
  return -sum(items_to_sum)

def compute_entropy_for_difficulty_selections_for_user(user):
    difficulty_counts = get_choose_difficulty_counts_for_user(user)
    return compute_entropy_for_difficulty_selections(difficulty_counts)

def get_entropies_for_user_list(user_list):
  entropies = []
  for user in user_list:
    entropy = compute_entropy_for_difficulty_selections_for_user(user)
    if entropy == None:
      continue
    entropies.append(entropy)
  return entropies

def get_entropies_for_all_users():
  user_list = get_users_with_choose_difficulty()
  return get_entropies_for_user_list(user_list)

def get_entropies_for_all_users_more_than_5():
  user_list = get_users_with_choose_difficulty()
  return get_entropies_for_user_list_with_more_than_5(user_list)

def get_entropies_for_all_users_with_10_first_days():
  user_list = get_users_with_choose_difficulty()
  return get_entropies_for_user_list_with_10_first_days(user_list)

def get_entropies_for_user_list_with_more_than_5(user_list):
  entropies = []
  for user in user_list:
    difficulty_counts = get_choose_difficulty_counts_for_user(user)
    total = sum(difficulty_counts.values())
    if total < 5:
      continue
    entropy = compute_entropy_for_difficulty_selections_for_user(user)
    if entropy == None:
      continue
    entropies.append(entropy)
  return entropies


#print(user_list[0])
#print(compute_entropy_for_difficulty_selections({'a': 0.25, 'b': 0.75}))

def get_entropies_for_user_list_with_10_first_days(user_list):
  entropies = []
  user_to_daynum_to_difficulty_choices = get_user_to_daynum_to_difficulty_choices()
  for user in user_list:
    #difficulty_counts = get_choose_difficulty_counts_for_user(user)
    if user not in user_to_daynum_to_difficulty_choices:
      continue
    daynum_to_difficulty_choices = user_to_daynum_to_difficulty_choices[user]
    is_valid = True
    for i in range(10):
      if i not in daynum_to_difficulty_choices:
        is_valid = False
        break
    if not is_valid:
      continue
    #total = sum(difficulty_counts.values())
    #if total < 5:
    #  continue
    entropy = compute_entropy_for_difficulty_selections_for_user(user)
    if entropy == None:
      continue
    entropies.append(entropy)
  return entropies



def compute_entropy_over_n_days(num_days):
  daynum_to_difficulty_choices = get_daynum_to_difficulty_choices_over_n_days(num_days)
  output = []
  for daynum in range(num_days):
    difficulty_choices = daynum_to_difficulty_choices[daynum]
    entropy_for_day = compute_entropy_for_difficulty_selections(difficulty_choices)
    output.append(entropy_for_day)
  return output

