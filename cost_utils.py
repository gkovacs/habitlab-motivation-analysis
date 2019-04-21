#!/usr/bin/env python
# md5: 3f62b20a4dea64e4223af5c9227e97c3
#!/usr/bin/env python
# coding: utf-8



# proposede costs of sampling

# time spent in answering the question (limit to instances where they do answers). how much time are we wasting for user each time they ask

# non-response rate. propobability of not responding within 30 seconds and going for the default radnom choice

# entropy over responses. window if they are in groups according to time spent on habitlab



from train_utils import *



print(len(get_users()))



for user in get_users():
  install_logs = get_install_logs_for_user(user)







print((get_collection_items('collections'))[0])



for x in get_collection_names():
  if 'nternal:choose_difficulty' in x:
    print(x)
    break



#a = get_all_features_data()

for user in get_users():
  user_to_difficulty_items = get_choose_difficulty_items_for_user(user)
  if len(user_to_difficulty_items) > 0:
    print(user)
    break



difficulty_items = get_choose_difficulty_items_for_user('0a0e30452f272c10a9c2675d')
print(len(difficulty_items))



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
print(get_choose_difficulty_items_for_user('0a0e30452f272c10a9c2675d'))



for x in difficulty_items:
  if 'is_random' not in x:
    continue
  print(x)
  break



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



unpaired_actions = 0
paired_actions = 0
unpaired_impressions = 0
paired_impressions = 0
impression_lengths = Counter()

def get_impressions_paired_with_actions(user):
  global paired_actions
  global unpaired_actions
  global paired_impressions
  global unpaired_impressions
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
  for tab_id,session_id_to_actions in tab_id_to_action_id_to_
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
  impressions_info_list.sort(key=lambda x: x['timestamp_local'])
  return impressions_info_list
      

for user in get_users():
  get_impressions_paired_with_actions(user)
#impressions_info_list = get_impressions_paired_with_actions('8d2c9eb27dee2dc85bca705b')
print('paired_actions', paired_actions)
print('unpaired_actions', unpaired_actions)
print('paired impressions', paired_impressions)
print('unpaired impressions', unpaired_impressions)
print('impression lengths')
print(impression_lengths)



prev_timestamp = 0
for x in impressions_info_list:
  print(x['is_paired'], x['install_id'], x['url'], x['tab_id'], x['session_id'], (x['timestamp_local'] - prev_timestamp) / 1000)
  prev_timestamp = x['timestamp_local']



def get_impression_times_prompted_for_user(user):
  difficulty_items = get_choose_difficulty_items_for_user(user)
  output = []
  for x in difficulty_items:
    #print(x['type'])
    print(x)
    impression_time = get_time_adjusted_for_timezone(x['timestamp'], x['localtime'])
    print(impression_time)
    if x['type'] == 'action': #'impression'
      break
    output.append(impression_time)
  return output

get_impression_times_prompted_for_user('8d2c9eb27dee2dc85bca705b')



def get_response_latencies_for_user(user):
  difficulty_items = get_choose_difficulty_items_for_user(user)
  for x in difficulty_items:
    is_random = x.get('is_random', None)
    if is_random == False:
      pass
      # TODO finish writing



for user in get_users():
  response_rate = get_non_response_rates_for_user(user)
  if response_rate == None:
    continue
  print(response_rate)

