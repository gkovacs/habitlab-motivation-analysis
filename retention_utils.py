#!/usr/bin/env python
# md5: 2c7f0ecfb8594cd2bce648a68b9a92a3
#!/usr/bin/env python
# coding: utf-8



from r_utils import r, r_assign



from train_utils import *



@msgpackmemo
def get_install_to_dates_active_list():
  output = {}
  for install,dates_active_set in get_install_to_dates_active_set().items():
    dates_active_list = sorted(list(dates_active_set))
    output[install] = dates_active_list
  return output



def get_install_to_dates_active_set():
  install_active_dates = get_collection_items('install_active_dates')
  output = {}
  #weird_items = []
  for item in install_active_dates:
    if 'day' not in item or 'install' not in item:
      #weird_items.append(item)
      continue
    day = item['day']
    install = item['install']
    if install not in output:
      output[install] = set()
    output[install].add(day)
  #print(len(weird_items))
  #print(weird_items[:100])
  return output

#print(user_active_dates[0])



@msgpackmemo
def get_user_to_dates_active_list():
  output = {}
  for user,dates_active_set in get_user_to_dates_active_set().items():
    dates_active_list = sorted(list(dates_active_set))
    output[user] = dates_active_list
  return output



def get_user_to_dates_active_set():
  user_active_dates = get_collection_items('user_active_dates')
  output = {}
  #weird_items = []
  for item in user_active_dates:
    if 'day' not in item or 'user' not in item:
      #weird_items.append(item)
      continue
    day = item['day']
    user = item['user']
    if user not in output:
      output[user] = set()
    output[user].add(day)
  #print(len(weird_items))
  #print(weird_items[:100])
  return output

#print(user_active_dates[0])



def get_date_to_users_active_set():
  output = {}
  for user,dates_active_list in get_user_to_dates_active_list().items():
    for date in dates_active_list:
      if date not in output:
        output[date] = set()
      output[date].add(user)
  return output



@msgpackmemo
def get_date_to_users_active_list():
  output = {}
  for date,users_active_set in get_date_to_users_active_set().items():
    output[date] = sorted(list(users_active_set))
  return output



def get_date_to_installs_active_set():
  output = {}
  for install,dates_active_list in get_install_to_dates_active_list().items():
    for date in dates_active_list:
      if date not in output:
        output[date] = set()
      output[date].add(install)
  return output



@msgpackmemo
def get_date_to_installs_active_list():
  output = {}
  for date,installs_active_set in get_date_to_installs_active_set().items():
    output[date] = sorted(list(installs_active_set))
  return output



from datetime import datetime
from dateutil import tz

def get_epoch_start_arrowdate():
  return arrow.get(datetime(2016, 1, 1)) #, tz.gettz('US/Pacific'))

def convert_date_to_arrowdate(date):
  year = int(date[0:4])
  month = int(date[4:6])
  day = int(date[6:8])
  return arrow.get(datetime(year, month, day)) #, tz.gettz('US/Pacific'))

def get_dump_date():
  return sorted(list(get_date_to_users_active_list().keys()))[-1]

def get_dump_arrowdate():
  dump_date = get_dump_date()
  return convert_date_to_arrowdate(dump_date)

def get_dump_epoch():
  dump_arrowdate = get_dump_arrowdate()
  return convert_arrowdate_to_epoch(dump_arrowdate)

def convert_arrowdate_to_epoch(arrowdate):
  return (arrowdate - get_epoch_start_arrowdate()).days

def convert_date_to_epoch(date):
  arrowdate = convert_date_to_arrowdate(date)
  return convert_arrowdate_to_epoch(arrowdate)



@msgpackmemo
def get_user_to_retention_info():
  output = {}
  dump_epoch = get_dump_epoch()
  for user,dates_active in get_user_to_dates_active_list().items():
    epochs_active = sorted([convert_date_to_epoch(x) for x in dates_active])
    first_active = epochs_active[0]
    last_active = epochs_active[-1]
    days_alive = last_active - first_active
    is_alive = (dump_epoch - last_active) <= 4
    attritioned = not is_alive
    output[user] = {'lifetime': days_alive, 'attritioned': attritioned}
  return output











def to_dataframe(list_of_dict):
  columns = list(list_of_dict[0].keys())
  d = {}
  for column in columns:
    d[column] = []
    for item in list_of_dict:
      d[column].append(item[column])
  return pd.DataFrame(d)



def get_all_user_retentions_dataframe():
  user_retentions = []
  for user,retention_info in get_user_to_retention_info().items():
    user_retentions.append(retention_info)
  return to_dataframe(user_retentions)



def get_abtest_experiment_conditions(user):
  items = get_collection_for_user(user, 'synced:experiment_vars')
  output = {}
  for x in items:
    if 'conditions' not in x:
      continue
    key = x['key']
    conditions = x['conditions']
    output[key] = conditions
  return output



def get_retention_info_by_frequency_of_choose_difficulty():
  output = []
  user_list = get_users_with_choose_difficulty()
  user_to_retention_info = get_user_to_retention_info()
  for user in user_list:
    abtest_settings = get_abtest_settings(user)
    frequency_of_choose_difficulty = abtest_settings.get('frequency_of_choose_difficulty')
    if frequency_of_choose_difficulty == None:
      continue
    conditions = get_abtest_experiment_conditions(user).get('frequency_of_choose_difficulty')
    if conditions != ['0.0', '0.25', '0.5', '1.0']:
      continue
    retention_info = user_to_retention_info[user]
    output.append({
      'lifetime': retention_info['lifetime'],
      'attritioned': retention_info['attritioned'],
      'frequency_of_choose_difficulty': frequency_of_choose_difficulty,
    })
  return to_dataframe(output)



























def plot_attrition(pandas_df, varname):
  r_assign('plot_attrition_df', pandas_df)
  r(f"""
  plot_attrition_df$lifetime <- as.numeric(plot_attrition_df$lifetime)
  plot_attrition_df$attritioned <- as.logical(plot_attrition_df$attritioned)
  plot_attrition_df${varname} <- as.factor(plot_attrition_df${varname})
  library("survival")
  library("survminer")
  fit <- survfit(Surv(lifetime, attritioned) ~ {varname}, data=plot_attrition_df)
  summary(fit)
  ggsurvplot(fit,
    pval = TRUE, conf.int = TRUE,
    risk.table = TRUE, # Add risk table
    risk.table.col = "strata", # Change risk table color by groups
    linetype = "strata", # Change line type by groups
    surv.median.line = "hv", # Specify median survival
    ggtheme = theme_bw(), # Change ggplot2 theme
  )
  """)
#   r(f"""
#   plot_attrition_df$lifetime <- as.numeric(plot_attrition_df$lifetime)
#   plot_attrition_df$attritioned <- as.logical(plot_attrition_df$attritioned)
#   plot_attrition_df${varname} <- as.factor(plot_attrition_df${varname})
#   library("survival")
#   library("survminer")
#   fit <- survfit(Surv(lifetime, attritioned) ~ {varname}, data=plot_attrition_df)
#   summary(fit)
#   plot_attrition_func <- function() {{
    
#   }}
#   """)
#   %R -w 1000 print(plot_attrition_func())



def make_retention_info_for_user_groups(group_name_to_user_list):
  

def compare_attrition_for_user_groups(group_name_to_user_list):
  



plot_attrition(get_retention_info_by_frequency_of_choose_difficulty(), 'frequency_of_choose_difficulty')



df = get_retention_info_by_frequency_of_choose_difficulty()







r('''
library("survival")
library("survminer")
''')



#def plot_retention(df):
  



#df = get_all_user_retentions_dataframe()
#r.assign('df', df)



print(df)



#r('''
#install.packages("survival")
#''')







r('''
library("survival")
library("survminer")
fit <- survfit(Surv(lifetime, attritioned) ~ frequency_of_choose_difficulty, data=df)
summary(fit)
''')



get_ipython().run_line_magic('load_ext', 'rpy2.ipython')



get_ipython().run_cell_magic('R', '', 'df$lifetime <- as.numeric(df$lifetime)\ndf$attritioned <- as.logical(df$attritioned)\ndf$frequency_of_choose_difficulty <- as.factor(df$frequency_of_choose_difficulty)')



get_ipython().run_cell_magic('R', '', 'summary(df)')



get_ipython().run_cell_magic('R', '-w 1000', 'ggsurvplot(fit,\n          pval = TRUE, conf.int = TRUE,\n          risk.table = TRUE, # Add risk table\n          risk.table.col = "strata", # Change risk table color by groups\n          linetype = "strata", # Change line type by groups\n          surv.median.line = "hv", # Specify median survival\n          ggtheme = theme_bw(), # Change ggplot2 theme\n)')



print(get_all_user_retentions_dataframe())



to_dataframe([{'a': 3, 'b': 5}, {'a': 4, 'b': 6}])



r.assign('a', to_dataframe([{'a': 3, 'b': 5}, {'a': 4, 'b': 6}]))



#r.assign('a', 5)
r('''show(a)''')



r('''a <- 3''')

