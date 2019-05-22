#!/usr/bin/env python
# md5: 43444d154b42c13f17616a747a07d541
#!/usr/bin/env python
# coding: utf-8



import imp
import cost_utils_libs
imp.reload(cost_utils_libs)
from cost_utils_libs import *














def plot_time_since_last_impression_by_action():
  time_since_last_impression_and_action_status = get_time_since_last_impression_and_action_status()
  plot_histogram([x for x,y in time_since_last_impression_and_action_status if y == 'none' and x < 10000])
  plot_histogram([x for x,y in time_since_last_impression_and_action_status if y == 'choice' and x < 10000])
  plot_histogram([x for x,y in time_since_last_impression_and_action_status if y == 'random' and x < 10000])
















# def plot_latency_for_individual_user():
#   impressions_info_list,actions_info_list,tab_id_to_session_id_to_impressions,tab_id_to_session_id_to_actions = get_impressions_paired_with_actions('8d2c9eb27dee2dc85bca705b')
#   #print(tab_id_to_session_id_to_impressions.keys())
#   latency_list = []
#   for x in actions_info_list:
#     if not x['is_paired']:
#       continue
#     tab_id = x['tab_id']
#     session_id = x['session_id']
#     action_timestamp = x['timestamp_local']
#     impression_info = tab_id_to_session_id_to_impressions[tab_id][session_id][0]
#     impression_timestamp = impression_info['timestamp_local']
#     latency = (action_timestamp - impression_timestamp) / 1000
#     if latency > 30:
#       continue
#     latency_list.append(latency)
#   from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#   import plotly.graph_objs as go

#   import numpy as np
#   #x = np.random.randn(500)
#   data = [go.Histogram(x=latency_list)]

#   iplot(data)

#plot_latency_for_individual_user()






# almost everything below this is broken

def print_misc_computations_cost_utils():
  prev_timestamp = 0
  for x in impressions_info_list:
    print(x['is_paired'], x['install_id'], x['url'], x['tab_id'], x['session_id'], (x['timestamp_local'] - prev_timestamp) / 1000)
    prev_timestamp = x['timestamp_local']

def print_misc_computations_cost_utils_2():
  for user in get_users():
    response_rate = get_non_response_rates_for_user(user)
    if response_rate == None:
      continue
    print(response_rate)




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




def get_response_latencies_for_user(user):
  difficulty_items = get_choose_difficulty_items_for_user(user)
  for x in difficulty_items:
    is_random = x.get('is_random', None)
    if is_random == False:
      pass
      # TODO finish writing





