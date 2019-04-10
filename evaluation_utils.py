#!/usr/bin/env python
# md5: 2240b6a05a737013537e822bce3c53f0
#!/usr/bin/env python
# coding: utf-8



from typing import Dict, List, Tuple, Any



from train_utils import *



from getsecret import getsecret
import subprocess
import json



#print(get_models_currently_training())



def get_models_currently_training():
  output = []
  local_info = json.load(open('current.json'))
  output.append(local_info['base_path'])
  remote_info = json.loads(subprocess.check_output(getsecret('REMOTE_SSH_COMMAND'), shell=True))
  output.append(remote_info['base_path'])
  return output



from glob import glob
import os
from os import path



def find_last_completed_epoch(model_name):
  return len(glob(path.join(model_name, 'info_*.json')))



#print(get_models_with_training_status())





def get_models_with_training_status():
  output = []
  models_currently_training = set(get_models_currently_training())
  for x in glob('tm_*'):
    model_status = {
      'name': x,
      'epochs_done': find_last_completed_epoch(x),
      'status': 'incomplete'
    }
    status_file_path = path.join(x, 'status.json')
    if not os.path.exists(status_file_path):
      output.append(model_status)
      continue
    status_info = json.load(open(status_file_path))
    if status_info['status'] == 'done':
      #model_status['epochs_done'] = find_last_completed_epoch(x)
      model_status['status'] = status_info['status']
      output.append(model_status)
      continue
    if status_info['status'] == 'training':
      if x in models_currently_training:
        model_status['status'] = status_info['status']
      output.append(model_status)
      continue
    raise Exception('invalid status for model', x, status_info['status'])
    #output.append(model_status)
  return output



import shutil

def remove_incomplete_models():
  for status_info in get_models_with_training_status():
    if status_info['epochs_done'] == 0 and status_info['status'] == 'incomplete':
      model_name = status_info['name']
      shutil.rmtree(model_name)
      #print(status_info)

remove_incomplete_models()



def get_parameter_info_list_for_model(model_name):
  parameters_file_path = path.join(model_name, 'parameters.json')
  return json.load(open(parameters_file_path))

def get_parameter_map_for_model(model_name):
  output = {}
  for parameter_info in get_parameter_info_list_for_model(model_name):
    parameter_name = parameter_info['name']
    parameter_value = parameter_info['value']
    output[parameter_name] = parameter_value
  return output

def list_models_finished_training():
  output = []
  for x in glob('tm_*'):
    status_file_path = path.join(x, 'status.json')
    if not os.path.exists(status_file_path):
      continue
    status_info = json.load(open(status_file_path))
    #print(status_info)
    if status_info['status'] != 'done':
      continue
    output.append(x)
  return output

def list_models_matching_parameters(parameters_map):
  output = []
  for model_name in list_models_finished_training():
    parameters_map_cur = get_parameter_map_for_model(model_name)
    is_match = True
    for k,v in parameters_map.items():
      if parameters_map_cur.get(k, None) != v:
        is_match = False
        break
    if is_match:
      output.append(model_name)
  return output


def get_models_with_dev_correct_fraction():
  #for x in list_models_finished_training():
  #  get_parameter_map_for_model(x))
  output = []
  for model_name in list_models_matching_parameters({'enable_current_difficulty': False}):
    for info_file_name in glob(path.join(model_name, 'info_*.json')):
      model_info = json.load(open(info_file_name))
      #print(model_info)
      dev_correct = model_info['dev_correct']
      dev_total = model_info['dev_total']
      dev_correct_fraction = dev_correct / dev_total
      output.append([dev_correct_fraction, info_file_name])
  output.sort()
  output.reverse()
  return output

get_models_with_dev_correct_fraction()



# true = True
# false = False
# parameter_info_list : List[Dict[str, Any]] = [{"name": "dataset_name", "type": "dataset", "values": ["2019_04_01"], "value": "2019_04_01"}, {"name": "model_name", "type": "model", "values": ["selfattentionlstm"], "value": "selfattentionlstm"}, {"name": "criterion", "type": "model", "values": ["NLLLoss"], "value": "NLLLoss"}, {"name": "learning_rate", "type": "model", "values": [0.005, 0.05, 0.0005, 5e-05], "value": 5e-05}, {"name": "window_embed_size", "type": "model", "values": [64, 128, 256, 512], "value": 256}, {"name": "difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "time_of_day", "type": "feature", "values": [true, false], "value": true}, {"name": "day_of_week", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_productivity", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_category", "type": "feature", "values": [true, false], "value": true}, {"name": "initial_difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "languages", "type": "feature", "values": [true, false], "value": true}, {"name": "num_prior_entries", "type": "dataparam", "values": [10, 20, 30, 40], "value": 10}, {"name": "sample_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "sample_difficulty_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "disable_prior_visit_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "disable_difficulty_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "enable_current_difficulty", "type": "dataparam", "values": [false, true], "value": false}, {"name": "num_features", "type": "model", "values": [277], "value": 277}]

# train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)





#def get_current_difficulty(tensor):
#  return tensor['chosen_difficulty']
# will actually always return nothing unless we enabled it in training data
#   feature = tensor['feature']
#   history_length = feature.size()[0]
#   timestep = history_length - 1
#   difficulty_feature_idx = get_feature_index('difficulty')
#   for difficulty_idx,difficulty in enumerate(['nothing', 'easy', 'medium', 'hard']):
#     if feature[timestep][0][difficulty_feature_idx + difficulty_idx].item() > 0:
#       return difficulty
#   return 'nothing'

def get_most_recently_chosen_difficulty(feature, parameter_info_list):
  #feature = tensor['feature']
  history_length = feature.size()[0]
  timestep = history_length - 2
  if len(feature) < 2:
    return 'nothing'
  enabled_feature_list = get_enabled_features_list_from_parameter_info_list(parameter_info_list)
  get_feature_index = make_get_index(enabled_feature_list)
  difficulty_feature_idx = get_feature_index('difficulty')
  for difficulty_idx,difficulty in enumerate(['nothing', 'easy', 'medium', 'hard']):
    if feature[timestep][0][difficulty_feature_idx + difficulty_idx].item() > 0:
      return difficulty
  return 'nothing'

def get_first_chosen_difficulty(feature, parameter_info_list):
  #feature = tensor['feature']
  history_length = feature.size()[0]
  timestep = 0
  if len(feature) < 2:
    return 'nothing'
  enabled_feature_list = get_enabled_features_list_from_parameter_info_list(parameter_info_list)
  get_feature_index = make_get_index(enabled_feature_list)
  difficulty_feature_idx = get_feature_index('difficulty')
  for difficulty_idx,difficulty in enumerate(['nothing', 'easy', 'medium', 'hard']):
    if feature[timestep][0][difficulty_feature_idx + difficulty_idx].item() > 0:
      return difficulty
  return 'nothing'

def get_initial_difficulty(feature, parameter_info_list):
  #feature = tensor['feature']
  history_length = feature.size()[0]
  timestep = 0
  #if len(feature) < 2:
  #  return 'nothing'
  enabled_feature_list = get_enabled_features_list_from_parameter_info_list(parameter_info_list)
  get_feature_index = make_get_index(enabled_feature_list)
  difficulty_feature_idx = get_feature_index('initial_difficulty')
  for difficulty_idx,difficulty in enumerate(['nothing', 'easy', 'medium', 'hard']):
    if feature[timestep][0][difficulty_feature_idx + difficulty_idx].item() > 0:
      return difficulty
  return 'nothing'

def always_predict_nothing(feature, parameter_info_list):
  return 'nothing'

def most_common_key_for_counter(c):
  best_key = None
  for k,v in c.items():
    if best_key == None:
      best_key = k
      continue
    if c[k] > c[best_key]:
      best_key = k
  return best_key

def always_predict_most_common_previous(feature, parameter_info_list):
  history_length = feature.size()[0]
  if len(feature) < 2:
    return 'nothing'
  enabled_feature_list = get_enabled_features_list_from_parameter_info_list(parameter_info_list)
  get_feature_index = make_get_index(enabled_feature_list)
  difficulty_feature_idx = get_feature_index('difficulty')
  difficulty_choices = Counter()
  for timestep in range(0, history_length - 1):
    for difficulty_idx,difficulty in enumerate(['nothing', 'easy', 'medium', 'hard']):
      if feature[timestep][0][difficulty_feature_idx + difficulty_idx].item() > 0:
        difficulty_choices[difficulty] += 1
  output = most_common_key_for_counter(difficulty_choices)
  if output == None:
    return 'nothing'
  return output
  #return 'nothing'

#print(get_current_difficulty(train_data[299]))
#print(get_most_recently_chosen_difficulty(train_data[299]))
# counts = Counter()
# for x in train_data:
#   current_difficulty = get_most_recently_chosen_difficulty(x['feature'])
#   counts[current_difficulty] += 1
# print(counts)



#print(train_data[0])



def evaluate_function_model_on_dataset(parameter_info_list, func, dataset, prefix='dev_') -> Dict[str, Any]:
  confusion = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
  correct = 0
  total = 0
  for item in dataset:
    category_tensor = item['category']
    feature_tensor = item['feature']
    if feature_tensor.size()[0] == 0:
        continue
    difficulty = tensor_to_difficulty(category_tensor)
    difficulty_idx = get_difficulty_idx(difficulty)
    #predicted_tensor = make_prediction(model, feature_tensor.cuda())
    #predicted_difficulty = prediction_to_difficulty(predicted_tensor)
    predicted_difficulty = func(feature_tensor, parameter_info_list)
    predicted_difficulty_idx = get_difficulty_idx(predicted_difficulty)
    if predicted_difficulty_idx == difficulty_idx:
      correct += 1
    total += 1
    confusion[difficulty_idx][predicted_difficulty_idx] += 1
  return {
    prefix + 'correct': correct,
    prefix + 'total': total,
    prefix + 'confusion': confusion,
  }



def evaluate_baseline_model_on_dataset(parameter_info_list, dataset, prefix='dev_'):
  confusion = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
  correct = 0
  total = 0
  for item in dataset:
    category_tensor = item['category']
    feature_tensor = item['feature']
    if feature_tensor.size()[0] == 0:
        continue
    difficulty = tensor_to_difficulty(category_tensor)
    difficulty_idx = get_difficulty_idx(difficulty)
    #predicted_tensor = make_prediction(model, feature_tensor.cuda())
    #predicted_difficulty = prediction_to_difficulty(predicted_tensor)
    predicted_difficulty = get_most_recently_chosen_difficulty(feature_tensor, parameter_info_list)
    predicted_difficulty_idx = get_difficulty_idx(predicted_difficulty)
    if predicted_difficulty_idx == difficulty_idx:
      correct += 1
    total += 1
    confusion[difficulty_idx][predicted_difficulty_idx] += 1
  return {
    prefix + 'correct': correct,
    prefix + 'total': total,
    prefix + 'confusion': confusion,
  }







#print(evaluate_baseline_model_on_dataset(dev_data))







every_n_visits_to_dev_evaluation_results : Dict[int, Dict[str, Any]] = {}
every_n_visits_to_train_evaluation_results : Dict[int, Dict[str, Any]] = {}



true = True
false = False
parameter_info_list : List[Dict[str, Any]] = [{"name": "dataset_name", "type": "dataset", "values": ["2019_04_01"], "value": "2019_04_01"}, {"name": "model_name", "type": "model", "values": ["selfattentionlstm"], "value": "selfattentionlstm"}, {"name": "criterion", "type": "model", "values": ["NLLLoss"], "value": "NLLLoss"}, {"name": "learning_rate", "type": "model", "values": [0.005, 0.05, 0.0005, 5e-05], "value": 5e-05}, {"name": "window_embed_size", "type": "model", "values": [64, 128, 256, 512], "value": 256}, {"name": "difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "time_of_day", "type": "feature", "values": [true, false], "value": true}, {"name": "day_of_week", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_productivity", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_category", "type": "feature", "values": [true, false], "value": true}, {"name": "initial_difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "languages", "type": "feature", "values": [true, false], "value": true}, {"name": "num_prior_entries", "type": "dataparam", "values": [10, 20, 30, 40], "value": 10}, {"name": "sample_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "sample_difficulty_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "disable_prior_visit_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "disable_difficulty_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "enable_current_difficulty", "type": "dataparam", "values": [false, true], "value": false}, {"name": "num_features", "type": "model", "values": [277], "value": 277}]
train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)



initial_difficulty_stats = evaluate_function_model_on_dataset(parameter_info_list, get_initial_difficulty, dev_data)
print(initial_difficulty_stats)



first_chosen_difficulty_stats = evaluate_function_model_on_dataset(parameter_info_list, get_first_chosen_difficulty, dev_data)
print(first_chosen_difficulty_stats)



always_nothing_stats = evaluate_function_model_on_dataset(parameter_info_list, always_predict_nothing, dev_data)
print(always_nothing_stats)



most_common_previous_stats = evaluate_function_model_on_dataset(parameter_info_list, always_predict_most_common_previous, dev_data)
print(most_common_previous_stats)



baseline_name_to_stats : Dict[str, Dict[str, Any]] = {}
name_and_func : List[Tuple[str, Any]] = [
  ('initial_difficulty', get_initial_difficulty),
  ('first_chosen', get_first_chosen_difficulty),
  ('always_nothing', always_predict_nothing),
  ('most_common_previous', always_predict_most_common_previous),
]
for [baseline_name,baseline_func] in name_and_func:
  baseline_name_to_stats[baseline_name] = evaluate_function_model_on_dataset(parameter_info_list, baseline_func, dev_data)



sample_every_n_visits_options : List[int] = list(range(1, 1000))

true = True
false = False
for sample_every_n_visits in sample_every_n_visits_options:
  if sample_every_n_visits in every_n_visits_to_dev_evaluation_results:
    continue
  parameter_info_list = [{"name": "dataset_name", "type": "dataset", "values": ["2019_04_01"], "value": "2019_04_01"}, {"name": "model_name", "type": "model", "values": ["selfattentionlstm"], "value": "selfattentionlstm"}, {"name": "criterion", "type": "model", "values": ["NLLLoss"], "value": "NLLLoss"}, {"name": "learning_rate", "type": "model", "values": [0.005, 0.05, 0.0005, 5e-05], "value": 5e-05}, {"name": "window_embed_size", "type": "model", "values": [64, 128, 256, 512], "value": 256}, {"name": "difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "time_of_day", "type": "feature", "values": [true, false], "value": true}, {"name": "day_of_week", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_productivity", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_category", "type": "feature", "values": [true, false], "value": true}, {"name": "initial_difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "languages", "type": "feature", "values": [true, false], "value": true}, {"name": "num_prior_entries", "type": "dataparam", "values": [10, 20, 30, 40], "value": 10}, {"name": "sample_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "sample_difficulty_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "disable_prior_visit_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "disable_difficulty_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "enable_current_difficulty", "type": "dataparam", "values": [false, true], "value": false}, {"name": "num_features", "type": "model", "values": [277], "value": 277}]
  for parameter_info in parameter_info_list:
    if parameter_info['name'] == 'sample_every_n_visits':
      parameter_info['values'] = [sample_every_n_visits]
      parameter_info['value'] = sample_every_n_visits
  train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)
  print(sample_every_n_visits)
  evaluation_results = evaluate_baseline_model_on_dataset(parameter_info_list, dev_data)
  every_n_visits_to_dev_evaluation_results[sample_every_n_visits] = evaluation_results
  print(evaluation_results)
  #evaluation_results = evaluate_baseline_model_on_dataset(parameter_info_list, train_data)
  #every_n_visits_to_train_evaluation_results[sample_every_n_visits] = evaluation_results
  #print(evaluation_results)





scatterplot = []
for k,v in every_n_visits_to_dev_evaluation_results.items():
  scatterplot.append([k,v['dev_correct'] / v['dev_total']])



import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot



print(scatterplot)





# Create a trace
trace = go.Scatter(
    x = [x[0] for x in scatterplot],
    y = [x[1] for x in scatterplot],
    mode = 'markers'
)

data = [trace]

# Plot and embed in ipython notebook!
iplot(data)



baseline_name_and_correctness : List[Tuple[str, float]] = []
for k2,v2 in baseline_name_to_stats.items():
  correctness : float = float(v2['dev_correct'] / v2['dev_total'])
  baseline_name_and_correctness.append((k2, correctness))
print(baseline_name_and_correctness)

