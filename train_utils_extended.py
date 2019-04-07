#!/usr/bin/env python
# md5: bd688538dc43d3d971df6c1c6284682e
#!/usr/bin/env python
# coding: utf-8



from train_utils import *



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



def main():
  while True:
    #parameters = sample_random_parameters(['learning_rate', 'window_embed_size', 'num_prior_entries'])
    parameters = sample_random_parameters(['sample_difficulty_every_n_visits'])
    train_model_for_parameters(parameters)
    parameters = sample_random_parameters(['sample_every_n_visits'])
    train_model_for_parameters(parameters)
    



main()

