#!/usr/bin/env python
# md5: 17bab155bbf0b51325e0f96fb4c9f93b
#!/usr/bin/env python
# coding: utf-8



from getsecret import getsecret



import jsonmemo as jsonmemo_module
jsonmemo_module.set_lowmem(True)
jsonmemo_funcs = jsonmemo_module.create_jsonmemo_funcs(getsecret('DATA_DUMP'))
#jsonmemo_funcs = jsonmemo_module.create_jsonmemo_funcs(getsecret('DATA_DUMP'))
jsonmemo1arg = jsonmemo_funcs['jsonmemo1arg']
jsonmemo = jsonmemo_funcs['jsonmemo']
mparrmemo = jsonmemo_funcs['mparrmemo']
msgpackmemo1arg = jsonmemo_funcs['msgpackmemo1arg']
msgpackmemo = jsonmemo_funcs['msgpackmemo']



from train_utils import *



from browser_libs import get_user_to_all_install_ids_precise, get_install_id_to_user







def compute_cached_data():
  print('running compute_cached_data')
  a=get_user_to_all_install_ids_precise()
  print(len(a))
  a = get_install_id_to_user()
  for user in get_users():
    install_logs = get_install_logs_for_user(user)
  from evaluation_utils_extended import main as main_evaluation_utils_extended
  main_evaluation_utils_extended()
  from cost_utils import get_impressions_paired_with_actions
  for user in get_users():
    impressions_paired_with_actions = get_impressions_paired_with_actions(user)
  print('finished running compute_cached_data')



if __name__ == '__main__':
  compute_cached_data()





