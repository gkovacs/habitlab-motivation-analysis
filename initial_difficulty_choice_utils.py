#!/usr/bin/env python
# md5: 3a82913dfc10835afc6303aceab15dc8
#!/usr/bin/env python
# coding: utf-8



from mkdata import *
from plot_utils import *



def plot_initial_chosen_difficulties():
  chosen_difficulties = Counter()
  for user in get_users_with_choose_difficulty():
    initial_difficulty = get_initial_difficulty_for_user(user)
    chosen_difficulties[initial_difficulty] += 1
  plot_dict_as_bar(chosen_difficulties)



