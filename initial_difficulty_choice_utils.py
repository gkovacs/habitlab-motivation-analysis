#!/usr/bin/env python
# md5: e3e32cd7bdfa7e14fc90cf3e65d15cdb
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



