#!/usr/bin/env python
# md5: 90c142e9afd2a3769821a3c5d2ed9f6f
#!/usr/bin/env python
# coding: utf-8



from train_utils import *



#import plot_utils
#reload(plot_utils)
from plot_utils import *



def get_difficulty_choices_heatmap():
  users_with_difficulty = get_users_with_choose_difficulty()
  user_to_difficulty_items = {}
  for user in users_with_difficulty:
    difficulty_items = get_choose_difficulty_items_for_user(user)
    difficulty_items = [x for x in difficulty_items if x.get('is_random') == False]
    if len(difficulty_items) < 200:
      continue
    user_to_difficulty_items[user] = difficulty_items
  user_to_heatmap_row = {}
  user_to_mean_difficulty = {}
  for user,difficulty_items in user_to_difficulty_items.items():
    heatmap_row = []
    for item in difficulty_items[:200]:
      difficulty = item['difficulty']
      difficulty_idx = ['nothing', 'easy', 'medium', 'hard'].index(difficulty)
      heatmap_row.append(difficulty_idx)
    user_to_heatmap_row[user] = heatmap_row
    user_to_mean_difficulty[user] = np.mean(heatmap_row)
  user_list = list(user_to_heatmap_row.keys())
  user_list.sort(key = lambda x: user_to_mean_difficulty[x])
  heatmap_data = []
  for user in user_list:
    heatmap_data.append(user_to_heatmap_row[user])
  return heatmap_data











def get_israndom_choices_heatmap_everytime():
  users_with_difficulty = get_users_with_choose_difficulty()
  user_to_israndom_items = {}
  for user in users_with_difficulty:
    abtest_settings = get_abtest_settings(user)
    if abtest_settings.get('frequency_of_choose_difficulty') != '1.0':
      continue
    difficulty_items = get_choose_difficulty_items_for_user(user)
    difficulty_items = [x for x in difficulty_items if 'is_random' in x]
    israndom_items = [int(x['is_random'] == False) for x in difficulty_items]
    if len(israndom_items) < 400:
      continue
    user_to_israndom_items[user] = israndom_items
  user_to_heatmap_row = {}
  user_to_mean = {}
  for user,israndom_items in user_to_israndom_items.items():
    heatmap_row = israndom_items[:400]
    user_to_heatmap_row[user] = heatmap_row
    user_to_mean[user] = np.mean(heatmap_row)
  user_list = list(user_to_heatmap_row.keys())
  user_list.sort(key = lambda x: user_to_mean[x])
  heatmap_data = []
  for user in user_list:
    heatmap_data.append(user_to_heatmap_row[user])
  return heatmap_data







def get_israndom_choices_heatmap():
  users_with_difficulty = get_users_with_choose_difficulty()
  user_to_israndom_items = {}
  for user in users_with_difficulty:
    abtest_settings = get_abtest_settings(user)
    if abtest_settings.get('frequency_of_choose_difficulty') != '0.5':
      continue
    difficulty_items = get_choose_difficulty_items_for_user(user)
    difficulty_items = [x for x in difficulty_items if 'is_random' in x]
    israndom_items = [int(x['is_random'] == False) for x in difficulty_items]
    if len(israndom_items) < 400:
      continue
    user_to_israndom_items[user] = israndom_items
  user_to_heatmap_row = {}
  user_to_mean = {}
  for user,israndom_items in user_to_israndom_items.items():
    heatmap_row = israndom_items[:400]
    user_to_heatmap_row[user] = heatmap_row
    user_to_mean[user] = np.mean(heatmap_row)
  user_list = list(user_to_heatmap_row.keys())
  user_list.sort(key = lambda x: user_to_mean[x])
  heatmap_data = []
  for user in user_list:
    heatmap_data.append(user_to_heatmap_row[user])
  return heatmap_data



import plot_utils
reload(plot_utils)
from plot_utils import *

def plot_israndom_choices_heatmap():
  heatmap_data = get_israndom_choices_heatmap()
  plot_heatmap(
    heatmap_data,
    title = 'Changes in user willingness to choose intervention difficulty over time',
    xlabel = 'How manyth time the user is seeing the difficulty selection prompt',
    ylabel = 'User index',
    #colorscale = 'Greys',
    ticktext = ['User chose', 'No choice (random)'],
  )




def plot_difficulty_choices_heatmap():
  heatmap_data = get_difficulty_choices_heatmap()
  plot_heatmap(
    heatmap_data,
    title = 'Changes in user difficulty choices over time',
    xlabel = 'How manyth time the user is choosing difficulty',
    ylabel = 'User index',
    #colorscale = 'Greys',
    ticktext = ['Nothing', 'Easy', 'Medium', 'Hard'],
  )



