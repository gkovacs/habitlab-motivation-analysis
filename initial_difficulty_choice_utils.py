#!/usr/bin/env python
# md5: 4a6e4975414883502a47163989f5e66b
#!/usr/bin/env python
# coding: utf-8



from mkdata import *
from plot_utils import *



def plot_initial_chosen_difficulties_per_user():
  chosen_difficulties = Counter()
  for user in get_users_with_choose_difficulty():
    initial_difficulty = get_initial_difficulty_for_user(user)
    chosen_difficulties[initial_difficulty] += 1
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
    chosen_difficulties[initial_difficulty] += 1
  plot_dict_as_bar(
    chosen_difficulties,
    title = 'Initial difficulty chosen during onboarding',
    xlabel = 'Difficulty level',
    ylabel = 'Number of users',
  )




