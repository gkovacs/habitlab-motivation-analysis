#!/usr/bin/env python
# md5: 63a2b5c08b777cc89901b5a84a8d6178
#!/usr/bin/env python
# coding: utf-8



from evaluation_utils_extended import get_evaluation_results_for_sample_every_n_seconds_v2



from train_utils import *



import jsonmemo as jsonmemo_module
#jsonmemo_funcs = jsonmemo_module.create_jsonmemo_funcs(getsecret('DATA_DUMP'), lowmem=True)
jsonmemo_funcs = jsonmemo_module.create_jsonmemo_funcs(getsecret('DATA_DUMP'))
jsonmemo1arg = jsonmemo_funcs['jsonmemo1arg']
jsonmemo = jsonmemo_funcs['jsonmemo']
mparrmemo = jsonmemo_funcs['mparrmemo']
msgpackmemo1arg = jsonmemo_funcs['msgpackmemo1arg']
msgpackmemo = jsonmemo_funcs['msgpackmemo']



from browser_libs import get_user_to_all_install_ids

#user_to_install_ids = get_user_to_all_install_ids()



# proposede costs of sampling

# time spent in answering the question (limit to instances where they do answers). how much time are we wasting for user each time they ask

# non-response rate. propobability of not responding within 30 seconds and going for the default radnom choice

# entropy over responses. window if they are in groups according to time spent on habitlab











# print(len(get_users()))



# for user in get_users():
#   install_logs = get_install_logs_for_user(user)







# print((get_collection_items('collections'))[0])



# for x in get_collection_names():
#   if 'nternal:choose_difficulty' in x:
#     print(x)
#     break



#a = get_all_features_data()

# for user in get_users():
#   user_to_difficulty_items = get_choose_difficulty_items_for_user(user)
  #if len(user_to_difficulty_items) > 0:
    #print(user)
    #break



# difficulty_items = get_choose_difficulty_items_for_user('0a0e30452f272c10a9c2675d')
# print(len(difficulty_items))



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

#collection_items = get_collection_for_user('0a0e30452f272c10a9c2675d', 'internal:choose_difficulty')
#print((collection_items))
#print(get_choose_difficulty_items_for_user('0a0e30452f272c10a9c2675d'))



# for x in difficulty_items:
#   if 'is_random' not in x:
#     continue
#   print(x)
#   break



def get_non_response_rates_for_user(user):
  non_response = 0
  have_response = 0
  difficulty_items = get_choose_difficulty_items_for_user(user)
  for x in difficulty_items:
    is_random = x.get('is_random', None)
    if is_random == None:
      continue
    if is_random == True:
      non_response += 1
      continue
    if is_random == False:
      have_response += 1
      continue
  if (non_response + have_response) == 0:
    return None
  return non_response / (non_response + have_response)

#print(get_non_response_rates_for_user('8d2c9eb27dee2dc85bca705b'))



def set_dict(d, value, *dpath):
  for x in dpath[:-1]:
    if x not in d:
      d[x] = {}
    d = d[x]
  d[dpath[-1]] = value

def append_dict_list(d, value, *dpath):
  for x in dpath[:-1]:
    if x not in d:
      d[x] = {}
    d = d[x]
  if dpath[-1] not in d:
    d[dpath[-1]] = []
  d[dpath[-1]].append(value)











# unpaired_actions = 0
# paired_actions = 0
# unpaired_impressions = 0
# paired_impressions = 0
# impression_lengths = Counter()

@msgpackmemo1arg
def get_impressions_paired_with_actions(user):
#   global paired_actions
#   global unpaired_actions
#   global paired_impressions
#   global unpaired_impressions
  unpaired_actions = 0
  paired_actions = 0
  unpaired_impressions = 0
  paired_impressions = 0
  impression_lengths = Counter()
  
  difficulty_items = get_choose_difficulty_items_for_user(user)
  output = []
  tab_id_to_session_id_to_impressions = {}
  tab_id_to_session_id_to_actions = {}
  #print(len(difficulty_items))
  for x in difficulty_items:
    tab_id = x['tab_id']
    session_id = x['session_id']
    if x['type'] == 'impression':
      append_dict_list(tab_id_to_session_id_to_impressions, x, tab_id, session_id)
    if x['type'] == 'action':
      append_dict_list(tab_id_to_session_id_to_actions, x, tab_id, session_id)
  #print(tab_id_to_session_id_to_impressions)
  for tab_id,session_id_to_actions in tab_id_to_session_id_to_actions.items():
    for session_id,actions in session_id_to_actions.items():
      if tab_id not in tab_id_to_session_id_to_impressions or (session_id not in tab_id_to_session_id_to_impressions[tab_id]):
        #print('missing impression for action:', tab_id, session_id)
        unpaired_actions += 1
      else:
        paired_actions += 1
  impressions_info_list = []
  actions_info_list = []
  for tab_id,session_id_to_actions in tab_id_to_session_id_to_actions.items():
    for session_id,actions in session_id_to_actions.items():
      is_paired = False
      if tab_id not in tab_id_to_session_id_to_impressions or (session_id not in tab_id_to_session_id_to_impressions[tab_id]):
        # action but no impression
        unpaired_actions += 1
        is_paired = False
      else:
        # action with corresponding impression
        paired_actions += 1
        is_paired = True
      if len(actions) != 1:
        continue
      action_info = copy(actions[0])
      action_info['is_paired'] = is_paired
      actions_info_list.append(action_info)
  for tab_id,session_id_to_impressions in tab_id_to_session_id_to_impressions.items():
    for session_id,impressions in session_id_to_impressions.items():
      is_paired = False
      if tab_id not in tab_id_to_session_id_to_actions or (session_id not in tab_id_to_session_id_to_actions[tab_id]):
        # impression but no selection
        unpaired_impressions += 1
        is_paired = False
      else:
        # impression with no corresponding action
        #print(impressions[0]['intervention'])
        paired_impressions += 1
        is_paired = True
      impression_lengths[len(impressions)] += 1
      if len(impressions) != 1:
        continue
      impression_info = copy(impressions[0])
      impression_info['is_paired'] = is_paired
      impressions_info_list.append(impression_info)
  actions_info_list.sort(key=lambda x: x['timestamp_local'])
  impressions_info_list.sort(key=lambda x: x['timestamp_local'])
  return impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions


# for user in get_users():
#   if user not in user_to_install_ids:
#     continue
#   if len(user_to_install_ids[user]) != 1:
#     continue
#   a = get_impressions_paired_with_actions(user)
#   continue
#impressions_info_list = get_impressions_paired_with_actions('8d2c9eb27dee2dc85bca705b')
# print('paired_actions', paired_actions)
# print('unpaired_actions', unpaired_actions)
# print('paired impressions', paired_impressions)
# print('unpaired impressions', unpaired_impressions)
# print('impression lengths')
# print(impression_lengths)



@memoize
def get_time_since_first_impression_and_action_status():
  time_since_first_impression_and_action_status = []
  user_to_install_ids = get_user_to_all_install_ids()

  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    earliest_timestamp = None
    latest_timestamp = None
    for x in impressions_info_list:
      timestamp = x['timestamp_local']
      if earliest_timestamp == None:
        earliest_timestamp = timestamp
        latest_timestamp = timestamp
      earliest_timestamp = min(timestamp, earliest_timestamp)
      latest_timestamp = max(timestamp, latest_timestamp)
    if earliest_timestamp == None:
      continue
    num_days_of_data = (latest_timestamp - earliest_timestamp) / (3600 * 24)
    if num_days_of_data < 7*8:
      continue
    for x in impressions_info_list:
      tab_id = x['tab_id']
      session_id = x['session_id']
      timestamp = x['timestamp_local']
      have_actions = True
      if tab_id not in tab_id_to_session_id_to_actions:
        have_actions = False
      elif session_id not in tab_id_to_session_id_to_actions[tab_id]:
        have_actions = False
      if have_actions:
        actions = tab_id_to_session_id_to_actions[tab_id][session_id]
        action_info = actions[0]
        action_type = 'random'
        if 'is_random' not in action_info:
          continue
        if action_info['is_random'] == True:
          action_type = 'random'
        else:
          action_type = 'choice'
          difficulty = action_info['difficulty']
          #time_since_first_impression_and_difficulty_chosen.append((time_since_first_impression, difficulty))
        time_since_first_impression = timestamp - earliest_timestamp
        time_since_first_impression_and_action_status.append((time_since_first_impression, action_type))
      else:
        actions = []
        action_type = 'none'
        time_since_first_impression = timestamp - earliest_timestamp
        time_since_first_impression_and_action_status.append((time_since_first_impression, action_type))
  return time_since_first_impression_and_action_status



@memoize
def get_time_since_first_impression_and_difficulty_chosen():
  time_since_first_impression_and_difficulty_chosen = []
  user_to_install_ids = get_user_to_all_install_ids()

  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    earliest_timestamp = None
    latest_timestamp = None
    for x in impressions_info_list:
      timestamp = x['timestamp_local']
      if earliest_timestamp == None:
        earliest_timestamp = timestamp
        latest_timestamp = timestamp
      earliest_timestamp = min(timestamp, earliest_timestamp)
      latest_timestamp = max(timestamp, latest_timestamp)
    if earliest_timestamp == None:
      continue
    num_days_of_data = (latest_timestamp - earliest_timestamp) / (3600 * 24)
    if num_days_of_data < 7*8:
      continue
    for x in impressions_info_list:
      tab_id = x['tab_id']
      session_id = x['session_id']
      timestamp = x['timestamp_local']
      have_actions = True
      if tab_id not in tab_id_to_session_id_to_actions:
        have_actions = False
      elif session_id not in tab_id_to_session_id_to_actions[tab_id]:
        have_actions = False
      if have_actions:
        actions = tab_id_to_session_id_to_actions[tab_id][session_id]
        action_info = actions[0]
        action_type = 'random'
        if 'is_random' not in action_info:
          continue
        if action_info['is_random'] == True:
          action_type = 'random'
        else:
          action_type = 'choice'
          difficulty = action_info['difficulty']
          time_since_first_impression = timestamp - earliest_timestamp
          time_since_first_impression_and_difficulty_chosen.append((time_since_first_impression, difficulty))
        #if time_since_last_impression != None:
        #  time_since_last_impression_and_action_status.append((time_since_last_impression, action_type))
      else:
        actions = []
        action_type = 'none'
        #if time_since_last_impression != None:
        #  time_since_last_impression_and_action_status.append((time_since_last_impression, action_type))
  return time_since_first_impression_and_difficulty_chosen



@memoize
def get_time_since_last_impression_and_difficulty_chosen():
  time_since_last_impression_and_difficulty_chosen = []
  user_to_install_ids = get_user_to_all_install_ids()

  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    #get_impressions_paired_with_actions(user)
    prev_impression_timestamp = None
    for x in impressions_info_list:
      tab_id = x['tab_id']
      session_id = x['session_id']
      timestamp = x['timestamp_local']
      if prev_impression_timestamp != None:
        time_since_last_impression = timestamp - prev_impression_timestamp
      else:
        time_since_last_impression = None
      prev_impression_timestamp = timestamp
      have_actions = True
      if tab_id not in tab_id_to_session_id_to_actions:
        have_actions = False
      elif session_id not in tab_id_to_session_id_to_actions[tab_id]:
        have_actions = False
      if have_actions:
        actions = tab_id_to_session_id_to_actions[tab_id][session_id]
        action_info = actions[0]
        action_type = 'random'
        if 'is_random' not in action_info:
          continue
        if action_info['is_random'] == True:
          action_type = 'random'
        else:
          action_type = 'choice'
          difficulty = action_info['difficulty']
          if time_since_last_impression != None:
            time_since_last_impression_and_difficulty_chosen.append((time_since_last_impression, difficulty))
        #if time_since_last_impression != None:
        #  time_since_last_impression_and_action_status.append((time_since_last_impression, action_type))
      else:
        actions = []
        action_type = 'none'
        #if time_since_last_impression != None:
        #  time_since_last_impression_and_action_status.append((time_since_last_impression, action_type))
  return time_since_last_impression_and_difficulty_chosen



@memoize
def get_time_since_last_impression_and_action_status():
  time_since_last_impression_and_action_status = []
  user_to_install_ids = get_user_to_all_install_ids()

  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    #get_impressions_paired_with_actions(user)
    prev_impression_timestamp = None
    for x in impressions_info_list:
      tab_id = x['tab_id']
      session_id = x['session_id']
      timestamp = x['timestamp_local']
      if prev_impression_timestamp != None:
        time_since_last_impression = timestamp - prev_impression_timestamp
      else:
        time_since_last_impression = None
      prev_impression_timestamp = timestamp
      have_actions = True
      if tab_id not in tab_id_to_session_id_to_actions:
        have_actions = False
      elif session_id not in tab_id_to_session_id_to_actions[tab_id]:
        have_actions = False
      if have_actions:
        actions = tab_id_to_session_id_to_actions[tab_id][session_id]
        action_info = actions[0]
        action_type = 'random'
        if 'is_random' not in action_info:
          continue
        if action_info['is_random'] == True:
          action_type = 'random'
        else:
          action_type = 'choice'
        if time_since_last_impression != None:
          time_since_last_impression_and_action_status.append((time_since_last_impression, action_type))
      else:
        actions = []
        action_type = 'none'
        if time_since_last_impression != None:
          time_since_last_impression_and_action_status.append((time_since_last_impression, action_type))
  return time_since_last_impression_and_action_status



def group_as_difficulty_per_hour(time_since_last_impression_and_difficulty_chosen):
  difficulty_to_hour_to_counts = {
    'nothing': Counter(),
    'easy': Counter(),
    'medium': Counter(),
    'hard': Counter(),
  }
  for x,difficulty in time_since_last_impression_and_difficulty_chosen:
    hour = round(x / 3600)
    if hour > 24:
      continue
    difficulty_to_hour_to_counts[difficulty][hour] += 1
  output = []
  for difficulty in 'nothing easy medium hard'.split(' '):
    difficulty_points = []
    for hour in sorted(list(difficulty_to_hour_to_counts[difficulty].keys())):
      counts = difficulty_to_hour_to_counts[difficulty][hour]
      total_counts = 0
      for other_difficulty in 'nothing easy medium hard'.split(' '):
        total_counts += difficulty_to_hour_to_counts[other_difficulty].get(hour, 0)
      fraction = counts / total_counts
      difficulty_points.append((hour, fraction))
    output.append((difficulty, difficulty_points))
  return output

def group_as_difficulty_per_hour_oneweek(time_since_last_impression_and_difficulty_chosen):
  difficulty_to_hour_to_counts = {
    'nothing': Counter(),
    'easy': Counter(),
    'medium': Counter(),
    'hard': Counter(),
  }
  for x,difficulty in time_since_last_impression_and_difficulty_chosen:
    hour = round(x / 3600)
    if hour > 24 * 7:
      continue
    difficulty_to_hour_to_counts[difficulty][hour] += 1
  output = []
  for difficulty in 'nothing easy medium hard'.split(' '):
    difficulty_points = []
    for hour in sorted(list(difficulty_to_hour_to_counts[difficulty].keys())):
      counts = difficulty_to_hour_to_counts[difficulty][hour]
      total_counts = 0
      for other_difficulty in 'nothing easy medium hard'.split(' '):
        total_counts += difficulty_to_hour_to_counts[other_difficulty].get(hour, 0)
      fraction = counts / total_counts
      difficulty_points.append((hour, fraction))
    output.append((difficulty, difficulty_points))
  return output


def group_as_difficulty_per_day(time_since_last_impression_and_difficulty_chosen):
  difficulty_to_hour_to_counts = {
    'nothing': Counter(),
    'easy': Counter(),
    'medium': Counter(),
    'hard': Counter(),
  }
  for x,difficulty in time_since_last_impression_and_difficulty_chosen:
    hour = round(x / (3600*24))
    if hour > 7:
      continue
    difficulty_to_hour_to_counts[difficulty][hour] += 1
  output = []
  for difficulty in 'nothing easy medium hard'.split(' '):
    difficulty_points = []
    for hour in sorted(list(difficulty_to_hour_to_counts[difficulty].keys())):
      counts = difficulty_to_hour_to_counts[difficulty][hour]
      total_counts = 0
      for other_difficulty in 'nothing easy medium hard'.split(' '):
        total_counts += difficulty_to_hour_to_counts[other_difficulty].get(hour, 0)
      fraction = counts / total_counts
      difficulty_points.append((hour, fraction))
    output.append((difficulty, difficulty_points))
  return output



def group_as_difficulty_per_week(time_since_last_impression_and_difficulty_chosen):
  difficulty_to_hour_to_counts = {
    'nothing': Counter(),
    'easy': Counter(),
    'medium': Counter(),
    'hard': Counter(),
  }
  for x,difficulty in time_since_last_impression_and_difficulty_chosen:
    hour = round(x / (3600*24*7))
    if hour > 7:
      continue
    difficulty_to_hour_to_counts[difficulty][hour] += 1
  output = []
  for difficulty in 'nothing easy medium hard'.split(' '):
    difficulty_points = []
    for hour in sorted(list(difficulty_to_hour_to_counts[difficulty].keys())):
      counts = difficulty_to_hour_to_counts[difficulty][hour]
      total_counts = 0
      for other_difficulty in 'nothing easy medium hard'.split(' '):
        total_counts += difficulty_to_hour_to_counts[other_difficulty].get(hour, 0)
      fraction = counts / total_counts
      difficulty_points.append((hour, fraction))
    output.append((difficulty, difficulty_points))
  return output



def group_as_response_rate_per_hour(time_since_last_impression_and_action_status):
  hour_to_choice_counts = Counter()
  hour_to_random_counts = Counter()
  for x,y in time_since_last_impression_and_action_status:
    hour = round(x / 3600)
    if hour > 24:
      continue
    if y == 'choice':
      hour_to_choice_counts[hour] += 1
    elif y == 'random':
      hour_to_random_counts[hour] += 1
  hours_with_data = set()
  for x in hour_to_choice_counts.keys():
    hours_with_data.add(x)
  for x in hour_to_random_counts.keys():
    hours_with_data.add(x)
  output = []
  for hour in sorted(list(hours_with_data)):
    response_rate = hour_to_choice_counts[hour] / (hour_to_choice_counts[hour] + hour_to_random_counts[hour])
    output.append((hour, response_rate))
  return output

def group_as_response_rate_per_hour_oneweek(time_since_last_impression_and_action_status):
  hour_to_choice_counts = Counter()
  hour_to_random_counts = Counter()
  for x,y in time_since_last_impression_and_action_status:
    hour = round(x / 3600)
    if hour > 24*7:
      continue
    if y == 'choice':
      hour_to_choice_counts[hour] += 1
    elif y == 'random':
      hour_to_random_counts[hour] += 1
  hours_with_data = set()
  for x in hour_to_choice_counts.keys():
    hours_with_data.add(x)
  for x in hour_to_random_counts.keys():
    hours_with_data.add(x)
  output = []
  for hour in sorted(list(hours_with_data)):
    response_rate = hour_to_choice_counts[hour] / (hour_to_choice_counts[hour] + hour_to_random_counts[hour])
    output.append((hour, response_rate))
  return output

def group_as_response_rate_per_day(time_since_last_impression_and_action_status):
  hour_to_choice_counts = Counter()
  hour_to_random_counts = Counter()
  for x,y in time_since_last_impression_and_action_status:
    hour = round(x / (3600*24))
    if hour > 7:
      continue
    if y == 'choice':
      hour_to_choice_counts[hour] += 1
    elif y == 'random':
      hour_to_random_counts[hour] += 1
  hours_with_data = set()
  for x in hour_to_choice_counts.keys():
    hours_with_data.add(x)
  for x in hour_to_random_counts.keys():
    hours_with_data.add(x)
  output = []
  for hour in sorted(list(hours_with_data)):
    response_rate = hour_to_choice_counts[hour] / (hour_to_choice_counts[hour] + hour_to_random_counts[hour])
    output.append((hour, response_rate))
  return output

def group_as_response_rate_per_week(time_since_last_impression_and_action_status):
  hour_to_choice_counts = Counter()
  hour_to_random_counts = Counter()
  for x,y in time_since_last_impression_and_action_status:
    hour = round(x / (3600*24*7))
    if hour > 7:
      continue
    if y == 'choice':
      hour_to_choice_counts[hour] += 1
    elif y == 'random':
      hour_to_random_counts[hour] += 1
  hours_with_data = set()
  for x in hour_to_choice_counts.keys():
    hours_with_data.add(x)
  for x in hour_to_random_counts.keys():
    hours_with_data.add(x)
  output = []
  for hour in sorted(list(hours_with_data)):
    response_rate = hour_to_choice_counts[hour] / (hour_to_choice_counts[hour] + hour_to_random_counts[hour])
    output.append((hour, response_rate))
  return output



# def plot_histogram(x_values):
#   data = [go.Histogram(x=x_values)]
#   iplot(data)

# def plot_points(points):
#   data = [go.Scatter(x=[x for x,y in points], y=[y for x,y in points])]
#   iplot(data)

# def plot_several_points(points_list):
#   data = []
#   for label,points in points_list:
#     data.append(go.Scatter(x=[x for x,y in points], y=[y for x,y in points], name=label))
#   iplot(data)

from plot_utils import *



#print(len(time_since_first_impression_and_difficulty_chosen))







def plot_difficulty_chosen_since_first_impression_per_week():
  difficulty_with_hours_and_fractions = group_as_difficulty_per_week(get_time_since_first_impression_and_difficulty_chosen())
  plot_several_points(difficulty_with_hours_and_fractions)

def plot_difficulty_chosen_since_first_impression_per_hour():
  difficulty_with_hours_and_fractions = group_as_difficulty_per_hour(get_time_since_last_impression_and_difficulty_chosen())
  plot_several_points(difficulty_with_hours_and_fractions)

def plot_difficulty_chosen_since_first_impression_per_hour_oneweek():
  difficulty_with_hours_and_fractions = group_as_difficulty_per_hour_oneweek(get_time_since_last_impression_and_difficulty_chosen())
  plot_several_points(difficulty_with_hours_and_fractions)

def plot_response_rate_since_first_impression_per_day():
  response_rate_per_day = group_as_response_rate_per_day(get_time_since_first_impression_and_action_status())
  plot_points(response_rate_per_day)

def plot_response_rate_since_first_impression_per_week():
  response_rate_per_week = group_as_response_rate_per_week(get_time_since_first_impression_and_action_status())
  plot_points(response_rate_per_week)

def plot_response_rate_since_last_impression_per_hour():
  response_rate_per_hour = group_as_response_rate_per_hour(get_time_since_last_impression_and_action_status())
  plot_points(response_rate_per_hour)

def plot_response_rate_since_last_impression_per_hour_oneweek():
  response_rate_per_hour_oneweek = group_as_response_rate_per_hour_oneweek(get_time_since_last_impression_and_action_status())
  plot_points(response_rate_per_hour_oneweek)



def plot_response_rate_correctness_per_hour():
  #print((time_since_last_impression_and_action_status)[0])
  response_rate_per_hour_oneweek = group_as_response_rate_per_hour_oneweek(get_time_since_last_impression_and_action_status())
  response_rate_correctness_per_hour = []
  correctness_per_hour = []
  for hour,response_rate in response_rate_per_hour_oneweek:
    results = get_evaluation_results_for_sample_every_n_seconds_v2(hour * 3600)
    correct_percent = results['dev_correct'] / results['dev_total']
    response_rate_correctness = correct_percent * response_rate
    response_rate_correctness_per_hour.append((hour, response_rate_correctness))
    correctness_per_hour.append((hour, correct_percent))
  plot_several_points([('response rate * correctness', response_rate_correctness_per_hour), ('response rate', response_rate_per_hour_oneweek), ('correctness', correctness_per_hour)])
  #plot_points(response_rate_per_hour)
  #plot_points(response_rate_per_hour_oneweek)



def plot_latency_for_all_users_nonrandom():
  latency_list_all = []
  user_to_install_ids = get_user_to_all_install_ids()
  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    #get_impressions_paired_with_actions(user)
    for x in actions_info_list:
      if not x['is_paired']:
        continue
      if 'is_random' not in x:
        continue
      if x['is_random'] == True:
        continue
      tab_id = x['tab_id']
      session_id = x['session_id']
      action_timestamp = x['timestamp_local']
      impression_info = tab_id_to_session_id_to_impressions[tab_id][session_id][0]
      impression_timestamp = impression_info['timestamp_local']
      latency = (action_timestamp - impression_timestamp) / 1000
      if not (0 < latency < 30):
        continue
      latency_list_all.append(latency)
  #x = np.random.randn(500)
  data = [go.Histogram(x=latency_list_all)]
  iplot(data)



def plot_latency_for_all_users_random():
  latency_list_all = []
  user_to_install_ids = get_user_to_all_install_ids()
  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    #get_impressions_paired_with_actions(user)
    for x in actions_info_list:
      if not x['is_paired']:
        continue
      if 'is_random' not in x:
        continue
      if x['is_random'] == False:
        continue
      tab_id = x['tab_id']
      session_id = x['session_id']
      action_timestamp = x['timestamp_local']
      impression_info = tab_id_to_session_id_to_impressions[tab_id][session_id][0]
      impression_timestamp = impression_info['timestamp_local']
      latency = (action_timestamp - impression_timestamp) / 1000
      if not (0 < latency < 30):
        continue
      latency_list_all.append(latency)
  data = [go.Histogram(x=latency_list_all)]
  iplot(data)



def plot_latency_for_all_users_random_and_nonrandom():
  latency_list_all = []
  user_to_install_ids = get_user_to_all_install_ids()
  for user in get_users():
    if user not in user_to_install_ids:
      continue
    if len(user_to_install_ids[user]) != 1:
      continue
    impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions(user)
    #get_impressions_paired_with_actions(user)
    for x in actions_info_list:
      if not x['is_paired']:
        continue
      tab_id = x['tab_id']
      session_id = x['session_id']
      action_timestamp = x['timestamp_local']
      impression_info = tab_id_to_session_id_to_impressions[tab_id][session_id][0]
      impression_timestamp = impression_info['timestamp_local']
      latency = (action_timestamp - impression_timestamp) / 1000
      if not (0 < latency < 30):
        continue
      latency_list_all.append(latency)
  data = [go.Histogram(x=latency_list_all)]
  iplot(data)

