#!/usr/bin/env python
# md5: 89ec3820a66fd05506b5fba9c4c1a635
#!/usr/bin/env python
# coding: utf-8



from mkdata import *



#print(get_num_features(get_feature_names()))



import model_selfattentionlstm
reload(model_selfattentionlstm)
from model_selfattentionlstm import SelfAttentionLSTM



import os
import torch
import math



all_features_data = get_all_features_data()



training_data_all_features,dev_data_all_features,test_data_all_features = split_into_train_dev_test(all_features_data)



feature_names = get_feature_names()
num_prior_entries = 10


learning_rate = 0.005 # If you set this too high, it might explode. If too low, it might not learn

dev_data = make_tensors_from_features(dev_data_all_features, {'enabled_feature_list': feature_names, 'num_prior_entries': num_prior_entries})
training_data = make_tensors_from_features(training_data_all_features, {'enabled_feature_list': feature_names, 'num_prior_entries': num_prior_entries})



def categoryFromOutput(output):
  top_n,top_i = output.topk(1)
  category_i = top_i[0].item()
  return ['nothing','easy','medium','hard'][category_i],category_i
#print(output.topk(1))
#print(categoryFromOutput(output))



def evaluate3(model, line_tensor):
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



def evaluate_model_on_dataset(model, dataset):
  num_correct = 0
  num_incorrect = 0
  for item in dataset:
    category_tensor = item['category']
    feature_tensor = item['feature']
    if feature_tensor.size()[0] == 0:
        continue
    difficulty = tensor_to_difficulty(category_tensor)
    difficulty_idx = get_difficulty_idx(difficulty)
    predicted_tensor = evaluate3(model, feature_tensor.cuda())
    predicted_difficulty,predicted_difficulty_idx = categoryFromOutput(predicted_tensor)
    if predicted_difficulty_idx == difficulty_idx:
      num_correct += 1
    else:
      num_incorrect += 1
    #confusion[difficulty_idx][predicted_difficulty_idx] += 1
    #print(predicted_difficulty)
    #print(difficulty)
    #break

  print('num correct: ' + str(num_correct))
  print('num incorrect: ' + str(num_incorrect))
  print('percentage correct: ' + str(num_correct / (num_correct + num_incorrect)))



def tensor_to_difficulty(tensor):
  difficulty_idx = tensor[0].data.cpu().numpy()
  return ['nothing', 'easy', 'medium', 'hard'][difficulty_idx]

print(make_tensor_from_chosen_difficulty('hard'))
print(tensor_to_difficulty((make_tensor_from_chosen_difficulty('hard'))))



n_iters = 100
print_every = 1
plot_every = 1
all_losses = []
num_features = get_num_features(get_feature_names())

for sample_every_n_visits in range(1, 11):
  print('making training data for sample_every_n_visits', sample_every_n_visits)
  #training_data = make_tensors_from_features(training_data_all_features[:int(len(training_data_all_features) / 100)], {
  #  'enabled_feature_list': feature_names,
  #  'num_prior_entries': num_prior_entries,
  #  'enable_current_difficulty': enable_current_difficulty,
  #  'sample_every_n_visits': sample_every_n_visits,
  #})
  model = SelfAttentionLSTM({'word_embed_size': num_features, 'window_embed_size': 128})
  model_filename = 'model_attention_nohistory_fractiondata10_nhidden512_sample_every_n_visits_' + str(sample_every_n_visits) + '_v10_epoch1.pt'
  model_state = torch.load(model_filename)
  model.load_state_dict(model_state['model_state_dict'])
  model.eval()
  evaluate_model_on_dataset(model, dev_data)



parameters = {
  'word_embed_size': 277,
  'window_embed_size': 128,
}
epoch = 0
while True:
  epoch += 1
  model_filename = 'model_attention_nohistory_nhidden512_v10_epoch' + str(epoch) + '.pt'
  if not os.path.isfile(model_filename):
    break
  print(model_filename)
  model = SelfAttentionLSTM(parameters)
  model_state = torch.load(model_filename)
  model.load_state_dict(model_state['model_state_dict'])
  model.eval()
  evaluate_model_on_dataset(model, dev_data)
  #break







parameters = {
  'word_embed_size': 277,
  'window_embed_size': 128,
}
epoch = 0
while True:
  epoch += 1
  model_filename = 'model_attention_nohistory_nhidden512_v10_epoch' + str(epoch) + '.pt'
  if not os.path.isfile(model_filename):
    break
  print(model_filename)
  model = SelfAttentionLSTM(parameters)
  model_state = torch.load(model_filename)
  model.load_state_dict(model_state['model_state_dict'])
  model.eval()
  evaluate_model_on_dataset(model, training_data)
  #break

