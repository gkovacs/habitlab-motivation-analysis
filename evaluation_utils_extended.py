#!/usr/bin/env python
# md5: df95fe1c26fe4857e43e0c099da11a30
#!/usr/bin/env python
# coding: utf-8



from evaluation_utils import *



def get_difficulty_first_chosen_by_user(user):
  user_to_features_data = get_all_features_data()
  features_data = user_to_features_data.get(user, None)
  if features_data == None:
    return 'nothing'
  if len(features_data['difficulty_items']) == 0:
    return 'nothing'
  return features_data['difficulty_items'][0]['difficulty']



def get_difficulty_chosen_by_user_at_idx(user, idx):
  user_to_features_data = get_all_features_data()
  features_data = user_to_features_data.get(user, None)
  if features_data == None:
    return 'nothing'
  return features_data['difficulty_items'][idx]['difficulty']





def get_initial_difficulty_v2(tensor, parameter_info_list):
  feature = tensor['feature']
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

def get_first_chosen_difficulty_v2(tensor, parameter_info_list):
  user = tensor['user']
  feature = tensor['feature']
  history_length = feature.size()[0]
  if history_length < 2:
    return 'nothing'
  return get_difficulty_first_chosen_by_user(user)

def always_predict_most_common_previous_v2(tensor, parameter_info_list):
  feature = tensor['feature']
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



def evaluate_function_model_on_dataset_v2(parameter_info_list, func, dataset, prefix='dev_') -> Dict[str, Any]:
  confusion = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
  correct = 0
  total = 0
  for item in dataset:
    category_tensor = item['category']
    feature_tensor = item['feature']
    #if feature_tensor.size()[0] == 0:
    #    continue
    difficulty = tensor_to_difficulty(category_tensor)
    difficulty_idx = get_difficulty_idx(difficulty)
    #predicted_tensor = make_prediction(model, feature_tensor.cuda())
    #predicted_difficulty = prediction_to_difficulty(predicted_tensor)
    predicted_difficulty = func(item, parameter_info_list)
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



def get_baseline_names():
  return [
    'initial_difficulty',
    'first_chosen',
    'always_nothing',
    'most_common_previous',
  ]

@jsonmemo1arg
def get_evaluation_results_for_named_baseline_v4(baseline_name):
  baseline_name_to_func = {
    'initial_difficulty': get_initial_difficulty_v2,
    'first_chosen': get_first_chosen_difficulty_v2,
    'always_nothing': always_predict_nothing,
    'most_common_previous': always_predict_most_common_previous_v2,
  }
  true = True
  false = False
  parameter_info_list : List[Dict[str, Any]] = get_default_parameter_info_list()
  #train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)
  train_data,dev_data,test_data = get_default_train_dev_test_data()
  baseline_func = baseline_name_to_func[baseline_name]
  return evaluate_function_model_on_dataset_v2(parameter_info_list, baseline_func, dev_data)



def get_default_parameter_info_list():
  true = True
  false = False
  return [{"name": "dataset_name", "type": "dataset", "values": ["2019_04_11"], "value": "2019_04_11"}, {"name": "model_name", "type": "model", "values": ["selfattentionlstm"], "value": "selfattentionlstm"}, {"name": "criterion", "type": "model", "values": ["NLLLoss"], "value": "NLLLoss"}, {"name": "learning_rate", "type": "model", "values": [0.005, 0.05, 0.0005, 5e-05], "value": 5e-05}, {"name": "window_embed_size", "type": "model", "values": [64, 128, 256, 512], "value": 256}, {"name": "difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "time_of_day", "type": "feature", "values": [true, false], "value": true}, {"name": "day_of_week", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_productivity", "type": "feature", "values": [true, false], "value": true}, {"name": "domain_category", "type": "feature", "values": [true, false], "value": true}, {"name": "initial_difficulty", "type": "feature", "values": [true, false], "value": true}, {"name": "languages", "type": "feature", "values": [true, false], "value": true}, {"name": "num_prior_entries", "type": "dataparam", "values": [10, 20, 30, 40], "value": 10}, {"name": "sample_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "sample_difficulty_every_n_visits", "type": "dataparam", "values": [1], "value": 1}, {"name": "disable_prior_visit_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "disable_difficulty_history", "type": "dataparam", "values": [false, true], "value": false}, {"name": "enable_current_difficulty", "type": "dataparam", "values": [false, true], "value": false}, {"name": "num_features", "type": "model", "values": [277], "value": 277}]

@msgpackmemo
def get_default_train_dev_test_data():
  parameter_info_list = get_default_parameter_info_list()
  #set_parameter_in_parameter_info_list(parameter_info_list, 'sample_every_n_visits', 1)
  train_data,dev_data,test_data = get_data_for_parameters(parameter_info_list)
  return train_data,dev_data,test_data




#print(type(train_data))
#print((train_data[0][list(train_data[0].keys())[0]]))
#pytorch_tensor = train_data[0]['feature']



#pytorch_serialized = json.dumps(pytorch_tensor.numpy().tolist())



#import numpy



#pytorch_new = torch.tensor(numpy.array(json.loads(pytorch_serialized), dtype='float32'), dtype=torch.float32)



#pytorch_new.numpy().dtype



# print(type(pytorch_tensor))
# print(pytorch_tensor.type())
# print(pytorch_tensor.numpy().dtype == numpy.float32)








def get_nearest_visit_idx_for_sample_rate(visit_idx, sample_rate):
  num_visits_ago = visit_idx % sample_rate
  return visit_idx - num_visits_ago



@jsonmemo1arg
def get_evaluation_results_for_sample_every_n_visits_v3(sample_every_n_visits):
  true = True
  false = False
  def evaluation_func(tensor, parameter_info_list):
    user = tensor['user']
    visit_idx = tensor['visit_idx']
    if visit_idx < 1:
      return 'nothing'
    sampled_visit_idx = get_nearest_visit_idx_for_sample_rate(visit_idx - 1, sample_every_n_visits)
    return get_difficulty_chosen_by_user_at_idx(user, sampled_visit_idx)
  parameter_info_list = get_default_parameter_info_list()
  train_data,dev_data,test_data = get_default_train_dev_test_data()
  return evaluate_function_model_on_dataset_v2(parameter_info_list, evaluation_func, dev_data)
  



@jsonmemo1arg
def get_evaluation_results_for_sample_every_n_seconds_v2(sample_every_n_seconds):
  true = True
  false = False
  user_to_idx_to_difficulty = {}
  def evaluation_func(tensor, parameter_info_list):
    user = tensor['user']
    visit_idx = tensor['visit_idx']
    if user not in user_to_idx_to_difficulty:
      user_to_idx_to_difficulty[user] = get_visit_idx_to_predictions_for_timed_sampling_rate(user, sample_every_n_seconds)
    #if visit_idx < 1:
    #  return 'nothing'
    #sampled_visit_idx = get_nearest_visit_idx_for_sample_rate(visit_idx - 1, sample_every_n_visits)
    return user_to_idx_to_difficulty[user][visit_idx]
  parameter_info_list = get_default_parameter_info_list()
  train_data,dev_data,test_data = get_default_train_dev_test_data()
  return evaluate_function_model_on_dataset_v2(parameter_info_list, evaluation_func, dev_data)
  



@jsonmemo1arg
def get_evaluation_results_for_sample_every_n_seconds_v3(sample_every_n_seconds):
  true = True
  false = False
  user_to_idx_to_difficulty = {}
  def evaluation_func(tensor, parameter_info_list):
    user = tensor['user']
    visit_idx = tensor['visit_idx']
    if user not in user_to_idx_to_difficulty:
      user_to_idx_to_difficulty[user] = get_visit_idx_to_predictions_for_timed_sampling_rate_v2(user, sample_every_n_seconds)
    #if visit_idx < 1:
    #  return 'nothing'
    #sampled_visit_idx = get_nearest_visit_idx_for_sample_rate(visit_idx - 1, sample_every_n_visits)
    return user_to_idx_to_difficulty[user][visit_idx]
  parameter_info_list = get_default_parameter_info_list()
  train_data,dev_data,test_data = get_default_train_dev_test_data()
  return evaluate_function_model_on_dataset_v2(parameter_info_list, evaluation_func, dev_data)
  



def get_visit_idx_to_predictions_for_timed_sampling_rate_v2(user, sampling_rate_seconds):
  user_to_features_data = get_all_features_data()
  features_data = user_to_features_data.get(user, None)
  if features_data == None:
    return 'nothing'
  sampled_according_to_time = []
  last_sampled_time = None
  last_sampled_value = 'nothing'
  for idx,item in enumerate(features_data['difficulty_items']):
    difficulty = item['difficulty']
    arrow_time = item['arrow_time']
    sampled_according_to_time.append(last_sampled_value)
    if last_sampled_time != None:
      seconds_since_last_sample = (arrow_time - last_sampled_time).total_seconds()
      if seconds_since_last_sample >= sampling_rate_seconds:
        last_sampled_time = arrow_time
        last_sampled_value = difficulty
    else:
      last_sampled_time = arrow_time
      last_sampled_value = difficulty
  return sampled_according_to_time



def get_visit_idx_to_predictions_for_timed_sampling_rate(user, sampling_rate_seconds):
  user_to_features_data = get_all_features_data()
  features_data = user_to_features_data.get(user, None)
  if features_data == None:
    return 'nothing'
  sampled_according_to_time = []
  last_sampled_time = None
  last_sampled_value = 'nothing'
  for idx,item in enumerate(features_data['difficulty_items']):
    difficulty = item['difficulty']
    arrow_time = item['arrow_time']
    sampled_according_to_time.append(last_sampled_value)
    if last_sampled_time != None:
      seconds_since_last_sample = (arrow_time - last_sampled_time).total_seconds()
      if seconds_since_last_sample >= sampling_rate_seconds:
        last_sampled_time = arrow_time
        last_sampled_value = difficulty
    else:
      last_sampled_time = arrow_time
      last_sampled_value = difficulty
  return sampled_according_to_time






# scatterplot = []
# for sample_every_n_visits in range(1, 200):
#   results = get_evaluation_results_for_sample_every_n_visits_v3(sample_every_n_visits)
#   scatterplot.append([sample_every_n_visits, results['dev_correct'] / results['dev_total']])




# # Create a trace
# trace = go.Scatter(
#     x = [x[0] for x in scatterplot],
#     y = [x[1] for x in scatterplot],
#     mode = 'markers'
# )

# data = [trace]

# # Plot and embed in ipython notebook!
# iplot(data)



