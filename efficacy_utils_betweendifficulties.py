#!/usr/bin/env python
# md5: 3a107cc179d1966421dc078d1e47f022
#!/usr/bin/env python
# coding: utf-8



from retention_utils import *



import jsonmemo as jsonmemo_module
jsonmemo_module.set_lowmem(True)



#installs_with_experiment_vars = get_installs_with_experiment_vars()



#print(installs_with_experiment_vars[0])





def get_condition_to_installs_for_random_assignment_abtest():
  abtest_name = 'difficulty_selection_screen'
  groups = ['survey_nochoice_nothing', 'survey_nochoice_easy', 'survey_nochoice_medium', 'survey_nochoice_hard']
  condition_to_installs = get_conditions_to_install_list_in_abtest_unstrict(abtest_name)
  for k in list(condition_to_installs.keys()):
    if k not in groups:
      del condition_to_installs[k]
  return condition_to_installs





# def get_condition_to_installs_for_random_assignment_abtest():
#   abtest_name = 'difficulty_selection_screen_and_choose_difficulty_frequency'
#   groups = ['survey', 'nodefault_forcedchoice_userchoice', 'survey_nochoice_nothing', 'survey_nochoice_easy', 'survey_nochoice_medium', 'survey_nochoice_hard']
#   condition_to_installs = get_conditions_to_install_list_in_abtest_unstrict(abtest_name)
#   for k in list(condition_to_installs.keys()):
#     if k not in groups:
#       del condition_to_installs[k]
#   return condition_to_installs




#for install in installs_with_experiment_vars:
@msgpackmemo1arg
def get_domain_to_intervention_to_session_lengths_for_install(install):
  seconds_on_domain_per_session = get_collection_for_install(install, 'synced:seconds_on_domain_per_session')
  interventions_active_for_domain_and_session = get_collection_for_install(install, 'synced:interventions_active_for_domain_and_session')
  
  domain_to_session_to_intervention = {}
  for x in interventions_active_for_domain_and_session:
    if x.get('val') is None:
      continue
    interventions_active = json.loads(x['val'])
    if len(interventions_active) == 0:
      continue
    intervention_name = interventions_active[0]
    domain = x['key']
    session_id = x['key2']
    if domain not in domain_to_session_to_intervention:
      domain_to_session_to_intervention[domain] = {}
    domain_to_session_to_intervention[domain][session_id] = intervention_name
  
  domain_to_intervention_to_session_lengths = {}
  for x in seconds_on_domain_per_session:
    if 'key' not in x:
      print('missing key in seconds_on_domain_per_session')
      print(x)
      continue
    domain = x['key']
    session_id = x['key2']
    time_spent = x['val']
    if domain not in domain_to_session_to_intervention:
      continue
    intervention_name = domain_to_session_to_intervention[domain].get(session_id)
    if intervention_name is None:
      continue
    if domain not in domain_to_intervention_to_session_lengths:
      domain_to_intervention_to_session_lengths[domain] = {}
    if intervention_name not in domain_to_intervention_to_session_lengths[domain]:
      domain_to_intervention_to_session_lengths[domain][intervention_name] = []
    domain_to_intervention_to_session_lengths[domain][intervention_name].append(time_spent)
  return domain_to_intervention_to_session_lengths
  




@msgpackmemo1arg
def get_epoch_to_domain_to_time_spent(install):
  seconds_on_domain_per_day = get_collection_for_install(install, 'synced:seconds_on_domain_per_day')
  output = {}
  for x in seconds_on_domain_per_day:
    if 'key' not in x:
      print('missing key in seconds_on_domain_per_day')
      print(x)
      continue
    domain = x['key']
    epoch = x['key2']
    seconds = x['val']
    if epoch not in output:
      output[epoch] = {}
    output[epoch][domain] = seconds
  return output









import math

def make_domain_to_daily_time_dataframe():
  output = []
  for condition,installs in condition_to_installs.items():
    #condition_to_lengths[condition] = []
    for install in installs:
      for epoch,domain_to_time_spent in get_epoch_to_domain_to_time_spent(install).items():
#         total_time_spent = sum(domain_to_time_spent.values())
#         output.append({
#           'user': install,
#           'epoch': epoch,
#           'time': total_time_spent,
#           'logtime': math.log(total_time_spent),
#           'condition': condition,
#         })
        for domain,total_time_spent in  domain_to_time_spent.items():
          output.append({
            'domain': domain,
            'user': install,
            'epoch': epoch,
            'time': total_time_spent,
            'logtime': math.log(total_time_spent),
            'condition': condition,
          })
  return to_dataframe(output)




#print(df)




#%%R
#install.library




# %%R

# df$user <- as.factor(df$user)
# #df$domain <- as.factor(df$domain)
# df$condition <- as.factor(df$condition)
# df$condition <- factor(df$condition, levels = c("survey_nochoice_nothing", "survey_nochoice_easy", "survey_nochoice_medium", "survey_nochoice_hard"))
# df$epoch <- as.factor(df$epoch)
# df$logtime <- as.numeric(df$logtime)
# df$time <- as.numeric(df$time)
# summary(df)












# for install in installs_with_experiment_vars:
#   #seconds_on_domain_per_session = get_collection_for_install(install, 'synced:seconds_on_domain_per_session')
#   #interventions_active_for_domain_and_session = get_collection_for_install(install, 'synced:interventions_active_for_domain_and_session')
#   res = get_domain_to_intervention_to_session_lengths_for_install(install)
#   #if len(res) > 0:
#   #  print(res)
#   #  break

