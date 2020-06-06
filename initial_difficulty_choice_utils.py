#!/usr/bin/env python
# md5: 7bb92fc38ab879eed40d97f6ae2e894c
#!/usr/bin/env python
# coding: utf-8



from mkdata import *
from plot_utils import *
import itertools
from scipy.stats import chi2_contingency



def plot_initial_chosen_difficulties_per_user():
  chosen_difficulties = Counter()
  for user in get_users_with_choose_difficulty():
    initial_difficulty = get_initial_difficulty_for_user(user)
    if initial_difficulty is None:
      continue
    chosen_difficulties[initial_difficulty] += 1
  print('sample size: ', sum(chosen_difficulties.values()))
  print(chosen_difficulties)
  plot_dict_as_bar(
    chosen_difficulties,
    title = 'Initial difficulty chosen during onboarding',
    xlabel = 'Difficulty level',
    ylabel = 'Number of users',
  )



def plot_initial_chosen_difficulties_per_install():
  chosen_difficulties = Counter()
  for install in get_installs_with_choose_difficulty():
    initial_difficulty = get_initial_difficulty_for_install(install)
    if initial_difficulty is None:
      continue
    chosen_difficulties[initial_difficulty] += 1
  plot_dict_as_bar(
    chosen_difficulties,
    title = 'Initial difficulty chosen during onboarding',
    xlabel = 'Difficulty level',
    ylabel = 'Number of users',
    remap_labels = {'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard', 'nothing': 'No Intervention'},
    #font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
    font=dict(size=20),
  )



def plot_initial_chosen_difficulties_per_install_percent():
  chosen_difficulties = Counter()
  for install in get_installs_with_choose_difficulty():
    initial_difficulty = get_initial_difficulty_for_install(install)
    if initial_difficulty is None:
      continue
    chosen_difficulties[initial_difficulty] += 1
  print('sample size: ', sum(chosen_difficulties.values()))
  print(chosen_difficulties)
  for pair in itertools.combinations(chosen_difficulties.keys(), 2):
    counts1 = chosen_difficulties[pair[0]]
    counts2 = chosen_difficulties[pair[1]]
    counts_total = counts1 + counts2
    print('')
    print(pair)
    print(chi2_contingency([[counts1, counts2], [counts_total, counts_total]]))
    print('')
  plot_dict_as_bar_percent(
    chosen_difficulties,
    title = 'Initial difficulty chosen during onboarding',
    xlabel = 'Difficulty level',
    ylabel = 'Percent of users',
    remap_labels = {'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard', 'nothing': 'No Intervention'},
    font=dict(size=22),
  )






# from r_utils import r

# # https://stackoverflow.com/questions/51469801/confidence-interval-for-a-chi-square-in-r
# r('''
# prop.test(x=c(70,30),n=c(100,100))
# ''')



# 

# obs = np.array([[70, 30], [100, 100]])

# chi2, p, dof, expected = chi2_contingency(obs)

# print(chi2)
# print(p)
# print(dof)
# print(expected)

# # chosen_difficulties = Counter()
# #   for install in get_installs_with_choose_difficulty():
# #     initial_difficulty = get_initial_difficulty_for_install(install)
# #     chosen_difficulties[initial_difficulty] += 1

