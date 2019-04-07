#!/usr/bin/env python
# md5: d809ff8d6e74fa054b236f14b665ca78
#!/usr/bin/env python
# coding: utf-8



import random
from memoize import memoize
import copy
import importlib
from os import path
import os
import torch
import torch.nn as nn



from mkdata import *



dataset_name = '2019_04_01'



def get_parameter_info_list():
  output = [
    {
      'name': 'dataset_name',
      'type': 'dataset',
      'values': [dataset_name],
    },
    {
      'name': 'model_name',
      'type': 'model',
      'values': ['selfattentionlstm'],
    },
    {
      'name': 'criterion',
      'type': 'model',
      'values': ['NLLLoss'],
    },
    {
      'name': 'learning_rate',
      'type': 'model',
      'values': [0.005, 0.05, 0.0005, 0.00005],
    },
    {
      'name': 'window_embed_size',
      'type': 'model',
      'values': [64, 128, 256, 512],
    },
    {
      'name': 'difficulty',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'time_of_day',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'day_of_week',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'domain_productivity',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'domain_category',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'initial_difficulty',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'languages',
      'type': 'feature',
      'values': [True, False],
    },
    {
      'name': 'num_prior_entries',
      'type': 'dataparam',
      'values': [10, 20, 30, 40],
    },
    {
      'name': 'sample_every_n_visits',
      'type': 'dataparam',
      'values': [1],
    },
    {
      'name': 'sample_difficulty_every_n_visits',
      'type': 'dataparam',
      'values': [1],
    },
    {
      'name': 'disable_prior_visit_history',
      'type': 'dataparam',
      'values': [False, True],
    },
    {
      'name': 'disable_difficulty_history',
      'type': 'dataparam',
      'values': [False, True],
    },
    {
      'name': 'enable_current_difficulty',
      'type': 'dataparam',
      'values': [False, True],
    },
  ]
  return output

@memoize
def get_parameter_name_to_info():
  output = {}
  for parameter_info in get_parameter_info_list():
    parameter_name = parameter_info['name']
    output[parameter_name] = parameter_info
  return output

def is_valid_parameter(parameter_name):
  return parameter_name in get_parameter_name_to_info()

def is_valid_parameter_value(parameter_name, parameter_value):
  return parameter_value in get_parameter_values(parameter_name)

def get_parameter_names():
  return [x['name'] for x in get_parameter_info_list()]

def get_parameter_info(parameter_name):
  return get_parameter_name_to_info().get(parameter_name, None)

def get_parameter_type(parameter_name):
  return get_parameter_info(parameter_name)['type']

def get_parameter_values(parameter_name):
  return get_parameter_info(parameter_name)['values']

def get_parameter_default(parameter_name):
  return get_parameter_values(parameter_name)[0]

def get_parameter_random_value(parameter_name):
  values = get_parameter_values(parameter_name)
  return random.choice(values)

#   enabled_feature_list = parameters['enabled_feature_list']
#   num_prior_entries = parameters.get('num_prior_entries', 10)
#   sample_every_n_visits = parameters.get('sample_every_n_visits', 1)
#   sample_difficulty_every_n_visits = parameters.get('sample_difficulty_every_n_visits', 1)
#   disable_prior_visit_history = parameters.get('disable_prior_visit_history', False)
#   disable_difficulty_history = parameters.get('disable_difficulty_history', False)
#   enable_current_difficulty = parameters.get('enable_current_difficulty', False)

# ['difficulty', 'time_of_day', 'day_of_week', 'domain_productivity', 'domain_category', 'initial_difficulty', 'languages']







def sample_random_parameters(list_of_parameters_to_sample):
  output = []
  set_of_parameters_to_sample = set(list_of_parameters_to_sample)
  for parameter_name in get_parameter_names():
    if not is_valid_parameter(parameter_name):
      print('invalid parameter ' + parameter_name)
      continue
    if parameter_name in set_of_parameters_to_sample:
      val = get_parameter_random_value(parameter_name)
    else:
      val = get_parameter_default(parameter_name)
    parameter_info = copy.copy(get_parameter_info(parameter_name))
    parameter_info['value'] = val
    output.append(parameter_info)
  enabled_features_list = get_enabled_features_list_from_parameter_info_list(output)
  num_features = get_num_features(enabled_features_list)
  output.append({
    'name': 'num_features',
    'type': 'model',
    'values': [num_features],
    'value': num_features,
  })
  return output

#print(sample_random_parameters(['difficulty']))

def get_parameter_map_for_type(parameter_info_list, parameter_type):
  output = {}
  for parameter_info in parameter_info_list:
    if parameter_info['type'] == parameter_type:
      print(parameter_info)
      val = parameter_info['value']
      name = parameter_info['name']
      output[name] = val
  return output

def get_enabled_features_list_from_parameter_info_list(parameter_info_list):
  output = []
  for parameter_info in parameter_info_list:
    if parameter_info['type'] == 'feature':
      val = parameter_info['value']
      if val != True:
        continue
      name = parameter_info['name']
      output.append(name)
  return output


def get_data_for_parameters(parameter_info_list):
  dataparams = get_parameter_map_for_type(parameter_info_list, 'dataparam')
  enabled_feature_list = get_enabled_features_list_from_parameter_info_list(parameter_info_list)
  dataparams['enabled_feature_list'] = enabled_feature_list
  all_data_tensors = make_tensors_from_features(get_all_features_data(), dataparams)
  return split_into_train_dev_test(all_data_tensors) # training,dev,test

def get_model_for_parameter_map(model_params):
  learning_rate = model_params['learning_rate']
  model_name = model_params['model_name']
  model_constructor = importlib.import_module('models.' + model_name).HLModel
  model = model_constructor(model_params)
  return model

def get_model_for_parameters(parameter_info_list):
  model_params = get_parameter_map_for_type(parameter_info_list, 'model')
  #enabled_feature_list = get_enabled_features_list_from_parameter_info_list(parameter_info_list)
  #num_features = get_num_features(enabled_feature_list)
  return get_model_for_parameter_map(model_params)

def get_parameter_value_for_info_list(parameter_info_list, parameter_name):
  for parameter_info in parameter_info_list:
    if parameter_info['name'] == parameter_name:
      return parameter_info['value']

#get_parameter_map_for_type(sample_random_parameters(['difficulty']), 'dataparam')
#get_all_data_for_parameters(sample_random_parameters(['difficulty']))



#sample_random_parameters([])



#get_model_for_parameters(sample_random_parameters([]))



def tensor_to_difficulty(tensor):
  difficulty_idx = tensor[0].data.cpu().numpy()
  return ['nothing', 'easy', 'medium', 'hard'][difficulty_idx]

def prediction_to_difficulty(output):
  top_n,top_i = output.topk(1)
  category_i = top_i[0].item()
  return ['nothing','easy','medium','hard'][category_i]

def save_model(model, criterion, epoch, loss, filename):
  torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': criterion.state_dict(),
    'loss': loss,
  }, filename)


def train_transformer(model, criterion, category_tensor, line_tensor, learning_rate):
    
    model.zero_grad()
    
    # TODO: construct mask and lengths for batch size == 1
    lengths = torch.tensor([line_tensor.size()[0]])
    mask = torch.zeros(line_tensor.size()[0], line_tensor.size()[1], 1, dtype=torch.float)
    device = (torch.device('cuda') if torch.cuda.is_available() else
                   torch.device('cpu'))
    mask = mask.to(device)
    line_tensor = line_tensor.to(device)
    category_tensor = category_tensor.to(device)
    # END TODO
#     print(line_tensor.size())
#     print(category_tensor.size())
#     print(lengths.size())
#     print(mask.size())
    output = model(line_tensor, lengths, mask)
    # print(category_tensor.size())
    loss = criterion(output, category_tensor)
    loss.backward()

    # Add parameters' gradients to their values, multiplied by learning rate
    for p in model.parameters():
        if p.grad is None:
          continue
        p.data.add_(-learning_rate, p.grad.data)

    return output, loss.item()

def make_prediction(model, line_tensor):
    line_tensor = line_tensor.permute(1,0,2)
    #model.zero_grad()
    
    # TODO: construct mask and lengths for batch size == 1
    lengths = torch.tensor([line_tensor.size()[0]])
    mask = torch.zeros(line_tensor.size()[0], line_tensor.size()[1], 1, dtype=torch.float)
    device = (torch.device('cuda') if torch.cuda.is_available() else
                   torch.device('cpu'))
    mask = mask.to(device)
    line_tensor = line_tensor.to(device)
    #category_tensor = category_tensor.to(device)
    # END TODO
#     print(line_tensor.size())
#     print(category_tensor.size())
#     print(lengths.size())
#     print(mask.size())
    output = model(line_tensor, lengths, mask)
    # print(category_tensor.size())
    #loss = criterion(output, category_tensor)
    #loss.backward()
    return output

def evaluate_model_on_dataset(model, dataset, prefix='dev_'):
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
    predicted_tensor = make_prediction(model, feature_tensor.cuda())
    predicted_difficulty = prediction_to_difficulty(predicted_tensor)
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



import hashlib
import base64
import arrow

def convert_string_to_hash(word):
    return hashlib.sha1(word.encode('utf-8')).hexdigest()

def get_path_for_parameters(parameter_info_list):
  output = []
  for parameter_info in parameter_info_list:
    name = parameter_info['name']
    value = parameter_info['value']
    output.append("'".join([name, str(value)]))
  return ' '.join(output)

def train_one_epoch(model, criterion, learning_rate, train_data):
  total_loss = 0
  confusion = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
  correct = 0
  total = 0
  for idx,item in enumerate(train_data):
    category_tensor = item['category']
    line_tensor = item['feature']
    category = tensor_to_difficulty(item['category'])
    category_i = get_difficulty_idx(category)
    if line_tensor.size()[0] == 0:
      continue
    output,loss = train_transformer(model, criterion, category_tensor, line_tensor.permute(1,0,2), learning_rate)
    total_loss += loss
    guess = prediction_to_difficulty(output)
    guess_i = get_difficulty_idx(guess)
    if guess_i == category_i:
      correct += 1
    confusion[category_i][guess_i] += 1
    total += 1
  return {
    'train_loss': total_loss,
    'train_correct': correct,
    'train_total': total,
    'train_confusion': confusion,
  }

def train_model_for_parameters(parameter_info_list, num_epochs=3):
  base_path_full = get_path_for_parameters(parameter_info_list)
  base_path = 'tm_' + convert_string_to_hash(base_path_full)
  if path.exists(base_path):
    # todo check status file and resume training
    return
  else:
    os.mkdir(base_path)
  json.dump({'base_path': base_path}, open('current.json', 'w'))
  status_info = {
    'status': 'training',
    'epoch': 0,
    'base_path': base_path,
    'base_path_full': base_path_full,
    'dataset_name': dataset_name,
    'start_time': str(arrow.get()),
    'start_timestamp': arrow.get().timestamp,
  }
  print(base_path)
  json.dump(parameter_info_list, open(path.join(base_path, 'parameters.json'), 'w'))
  model = get_model_for_parameters(parameter_info_list)
  learning_rate = get_parameter_value_for_info_list(parameter_info_list, 'learning_rate')
  train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)
  criterion = nn.NLLLoss()
  for epoch in range(1, 1 + num_epochs):
    status_info['epoch'] = epoch
    json.dump(status_info, open(path.join(base_path, 'status.json'), 'w'))
    print(status_info)
    epoch_start_time = str(arrow.get())
    epoch_start_timestamp = arrow.get().timestamp
    model_path = path.join(base_path, 'model_' + str(epoch) + '.pt')
    if path.exists(model_path):
      continue
    train_info = train_one_epoch(model, criterion, learning_rate, train_data)
    save_model(model, criterion, epoch, train_info['train_loss'], model_path)
    dev_info = evaluate_model_on_dataset(model, dev_data, 'dev_')
    test_info = evaluate_model_on_dataset(model, test_data, 'test_')
    for k,v in dev_info.items():
      train_info[k] = v
    for k,v in test_info.items():
      train_info[k] = v
    train_info['epoch_start_time'] = epoch_start_time
    train_info['epoch_start_timestamp'] = epoch_start_timestamp
    train_info['epoch_end_time'] = str(arrow.get())
    train_info['epoch_end_timestamp'] = arrow.get().timestamp
    training_start_timestamp = arrow.get().timestamp
    info_path = path.join(base_path, 'info_' + str(epoch) + '.json')
    json.dump(train_info, open(info_path, 'w'))
  status_info['status'] = 'done'
  status_info['end_time'] = str(arrow.get())
  status_info['end_timestamp'] = arrow.get().timestamp
  json.dump(status_info, open(path.join(base_path, 'status.json'), 'w'))
  print(status_info)

#get_path_for_parameters(sample_random_parameters([]))



def main():
  while True:
    parameters = sample_random_parameters(['learning_rate', 'window_embed_size', 'num_prior_entries'])
    train_model_for_parameters(parameters)
    



#convert_string_to_hash('foobar')



