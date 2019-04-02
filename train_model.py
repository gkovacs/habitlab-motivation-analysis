#!/usr/bin/env python
# md5: 8b2eceac7045d1ec92fa5171e8a60b7a
#!/usr/bin/env python
# coding: utf-8



from mkdata import *



import torch
import torch.nn as nn
import numpy as np
import os
import os.path



from model_selfattentionlstm import SelfAttentionLSTM



all_features_data = get_all_features_data()



training_data_all_features,dev_data_all_features,test_data_all_features = split_into_train_dev_test(all_features_data)







def iterateTrainingData(training_data):
  output = []
  for data in training_data:
    category = tensor_to_difficulty(data['category'])
    #yield category,data['category'],data['feature']
    output.append((category,data['category'],data['feature']))
  np.random.shuffle(output)
  return output

criterion = nn.NLLLoss()



torch.cuda.device_count()











def save_model(rnn, criterion, epoch, loss, filename):
  torch.save({
    'epoch': epoch,
    'model_state_dict': rnn.state_dict(),
    'optimizer_state_dict': criterion.state_dict(),
    'loss': loss,
  }, filename)

#print(criterion.state_dict())



def tensor_to_difficulty(tensor):
  difficulty_idx = tensor[0].data.cpu().numpy()
  return ['nothing', 'easy', 'medium', 'hard'][difficulty_idx]

def categoryFromOutput(output):
  top_n,top_i = output.topk(1)
  category_i = top_i[0].item()
  return ['nothing','easy','medium','hard'][category_i],category_i

#print(output.topk(1))
#print(categoryFromOutput(output))

print(make_tensor_from_chosen_difficulty('hard'))
print(tensor_to_difficulty((make_tensor_from_chosen_difficulty('hard'))))



def trainTransformer(category_tensor, line_tensor):
    
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



learning_rate = 0.005 # If you set this too high, it might explode. If too low, it might not learn



feature_names = get_feature_names()
num_features = get_num_features(feature_names)
num_prior_entries = 10
enable_current_difficulty = False



n_iters = 100
print_every = 1
plot_every = 1
all_losses = []

for sample_difficulty_every_n_visits in range(1, 1001):
  outfile = 'model_attention_nohistory_fulldata_nhidden512_sample_difficulty_every_n_visits_' + str(sample_difficulty_every_n_visits) + '_v10_epoch' + str(epoch) + '.pt'
  if os.path.exists(outfile):
    continue
  print('making training data for sample_difficulty_every_n_visits', sample_difficulty_every_n_visits)
  training_data = make_tensors_from_features(training_data_all_features, {
    'enabled_feature_list': feature_names,
    'num_prior_entries': num_prior_entries,
    'enable_current_difficulty': enable_current_difficulty,
    'sample_difficulty_every_n_visits': sample_difficulty_every_n_visits,
  })
  model = SelfAttentionLSTM({'word_embed_size': num_features, 'window_embed_size': 128})
  epoch = 1
  all_training_items = iterateTrainingData(training_data)
  print('sample_difficulty_every_n_visits', sample_difficulty_every_n_visits)
  current_loss = 0
  for idx,training_item in enumerate(all_training_items):
    (category,category_tensor, line_tensor) = training_item
    #print(line_tensor.size())
    if line_tensor.size()[0] == 0:
      continue
    output, loss = trainTransformer(category_tensor, line_tensor.permute(1,0,2))
    current_loss += loss
    if idx % 1000 == 0:
      #pass
      print(epoch, ':', idx, '/', len(all_training_items))
      # Print iter number, loss, name and guess
    if epoch % print_every == 0:
        guess, guess_i = categoryFromOutput(output)
        correct = '✓' if guess == category else '✗ (%s)' % category
        #print('%d %d%% (%s) %.4f / %s %s' % (iter, iter / n_iters * 100, timeSince(start), loss, guess, correct))

    # Add current loss avg to list of losses
    #if iter % plot_every == 0:
    #    all_losses.append(current_loss / plot_every)
    #    #current_loss = 0
  #rnn.zero_grad()
  all_losses.append(current_loss / plot_every)
  save_model(model, criterion, epoch, current_loss, outfile)



n_iters = 100
print_every = 1
plot_every = 1
all_losses = []

for sample_every_n_visits in range(1, 11):
  print('making training data for sample_every_n_visits', sample_every_n_visits)
  training_data = make_tensors_from_features(training_data_all_features[:int(len(training_data_all_features) / 10)], {
    'enabled_feature_list': feature_names,
    'num_prior_entries': num_prior_entries,
    'enable_current_difficulty': enable_current_difficulty,
    'sample_every_n_visits': sample_every_n_visits,
  })
  model = SelfAttentionLSTM({'word_embed_size': num_features, 'window_embed_size': 128})
  epoch = 1
  all_training_items = iterateTrainingData(training_data)
  print('sample_every_n_visits', sample_every_n_visits)
  current_loss = 0
  for idx,training_item in enumerate(all_training_items):
    (category,category_tensor, line_tensor) = training_item
    #print(line_tensor.size())
    if line_tensor.size()[0] == 0:
      continue
    output, loss = trainTransformer(category_tensor, line_tensor.permute(1,0,2))
    current_loss += loss
    if idx % 1000 == 0:
      #pass
      print(epoch, ':', idx, '/', len(all_training_items))
      # Print iter number, loss, name and guess
    if epoch % print_every == 0:
        guess, guess_i = categoryFromOutput(output)
        correct = '✓' if guess == category else '✗ (%s)' % category
        #print('%d %d%% (%s) %.4f / %s %s' % (iter, iter / n_iters * 100, timeSince(start), loss, guess, correct))

    # Add current loss avg to list of losses
    #if iter % plot_every == 0:
    #    all_losses.append(current_loss / plot_every)
    #    #current_loss = 0
  #rnn.zero_grad()
  all_losses.append(current_loss / plot_every)
  save_model(model, criterion, epoch, current_loss, 'model_attention_nohistory_fractiondata10_nhidden512_sample_every_n_visits_' + str(sample_every_n_visits) + '_v10_epoch' + str(epoch) + '.pt')



n_iters = 100
print_every = 1
plot_every = 1
all_losses = []
disable_difficulty_history = True
sample_every_n_visits = 1

#for sample_every_n_visits in range(1, 11):
if True:
  print('making training data for disable_difficulty_history', disable_difficulty_history)
  training_data = make_tensors_from_features(training_data_all_features[:int(len(training_data_all_features) / 10)], {
    'enabled_feature_list': feature_names,
    'num_prior_entries': num_prior_entries,
    'enable_current_difficulty': enable_current_difficulty,
    'sample_every_n_visits': sample_every_n_visits,
    'disable_difficulty_history': disable_difficulty_history,
  })
  model = SelfAttentionLSTM({'word_embed_size': num_features, 'window_embed_size': 128})
  epoch = 1
  all_training_items = iterateTrainingData(training_data)
  print('sample_every_n_visits', sample_every_n_visits)
  current_loss = 0
  for idx,training_item in enumerate(all_training_items):
    (category,category_tensor, line_tensor) = training_item
    #print(line_tensor.size())
    if line_tensor.size()[0] == 0:
      continue
    output, loss = trainTransformer(category_tensor, line_tensor.permute(1,0,2))
    current_loss += loss
    if idx % 1000 == 0:
      #pass
      print(epoch, ':', idx, '/', len(all_training_items))
      # Print iter number, loss, name and guess
    if epoch % print_every == 0:
        guess, guess_i = categoryFromOutput(output)
        correct = '✓' if guess == category else '✗ (%s)' % category
        #print('%d %d%% (%s) %.4f / %s %s' % (iter, iter / n_iters * 100, timeSince(start), loss, guess, correct))

    # Add current loss avg to list of losses
    #if iter % plot_every == 0:
    #    all_losses.append(current_loss / plot_every)
    #    #current_loss = 0
  #rnn.zero_grad()
  all_losses.append(current_loss / plot_every)
  save_model(model, criterion, epoch, current_loss, 'model_attention_nohistory_fractiondata10_nhidden512_disable_difficulty_history_v10_epoch' + str(epoch) + '.pt')







n_iters = 100
print_every = 1
plot_every = 1
all_losses = []
disable_prior_visit_history = True

#for sample_every_n_visits in range(1, 11):
if True:
  print('making training data for disable_prior_visit_history', disable_prior_visit_history)
  training_data = make_tensors_from_features(training_data_all_features[:int(len(training_data_all_features) / 10)], {
    'enabled_feature_list': feature_names,
    'num_prior_entries': num_prior_entries,
    'enable_current_difficulty': enable_current_difficulty,
    'sample_every_n_visits': sample_every_n_visits,
    'disable_prior_visit_history': disable_prior_visit_history,
  })
  model = SelfAttentionLSTM({'word_embed_size': num_features, 'window_embed_size': 128})
  epoch = 1
  all_training_items = iterateTrainingData(training_data)
  print('sample_every_n_visits', sample_every_n_visits)
  current_loss = 0
  for idx,training_item in enumerate(all_training_items):
    (category,category_tensor, line_tensor) = training_item
    #print(line_tensor.size())
    if line_tensor.size()[0] == 0:
      continue
    output, loss = trainTransformer(category_tensor, line_tensor.permute(1,0,2))
    current_loss += loss
    if idx % 1000 == 0:
      #pass
      print(epoch, ':', idx, '/', len(all_training_items))
      # Print iter number, loss, name and guess
    if epoch % print_every == 0:
        guess, guess_i = categoryFromOutput(output)
        correct = '✓' if guess == category else '✗ (%s)' % category
        #print('%d %d%% (%s) %.4f / %s %s' % (iter, iter / n_iters * 100, timeSince(start), loss, guess, correct))

    # Add current loss avg to list of losses
    #if iter % plot_every == 0:
    #    all_losses.append(current_loss / plot_every)
    #    #current_loss = 0
  #rnn.zero_grad()
  all_losses.append(current_loss / plot_every)
  save_model(model, criterion, epoch, current_loss, 'model_attention_nohistory_fractiondata10_nhidden512_disable_prior_visit_history_v10_epoch' + str(epoch) + '.pt')



n_iters = 100
print_every = 1
plot_every = 1
all_losses = []

model.train()
for epoch in range(1, n_iters + 1):
  all_training_items = iterateTrainingData()
  print('iteration', epoch)
  current_loss = 0
  for idx,training_item in enumerate(all_training_items):
    (category,category_tensor, line_tensor) = training_item
    #print(line_tensor.size())
    if line_tensor.size()[0] == 0:
      continue
    output, loss = trainTransformer(category_tensor, line_tensor.permute(1,0,2))
    current_loss += loss
    if idx % 1000 == 0:
      #pass
      print(epoch, ':', idx, '/', len(all_training_items))
      # Print iter number, loss, name and guess
    if epoch % print_every == 0:
        guess, guess_i = categoryFromOutput(output)
        correct = '✓' if guess == category else '✗ (%s)' % category
        #print('%d %d%% (%s) %.4f / %s %s' % (iter, iter / n_iters * 100, timeSince(start), loss, guess, correct))

    # Add current loss avg to list of losses
    #if iter % plot_every == 0:
    #    all_losses.append(current_loss / plot_every)
    #    #current_loss = 0
  #rnn.zero_grad()
  all_losses.append(current_loss / plot_every)
  save_model(model, criterion, epoch, current_loss, 'model_attention_nohistory_nhidden512_v10_epoch' + str(epoch) + '.pt')





