#!/usr/bin/env python
# md5: 5412eee5ef178efdd2fd84872da557c9
#!/usr/bin/env python
# coding: utf-8



from initial_difficulty_choice_utils import plot_initial_chosen_difficulties
plot_initial_chosen_difficulties()


# First study: all users are in the 10-second countdown version of the interface. We vary the frequency with which they are shown the prompt. 4 conditions: shown prompt on 100% of visits, 50%, 25%, 0%.
# 
# Are there costs to asking what difficulty the user wants? (If there aren’t we can just ask every visit and declare mission accomplished)
# 
# The actual time cost is actually rather low, a mode of 1.2 seconds time to answer the question
# 


from cost_utils_libs import plot_latency_for_all_users_nonrandom
plot_latency_for_all_users_nonrandom()


# Unfortunately conditions where you ask users have significantly higher attrition rates. Key difference seems to be more of “do you ask them at all” rather than how often (doesn’t seem to be much difference between 1.0 and 0.5).


from retention_utils import make_attrition_plot_by_install_for_frequency_of_choose_difficulty
make_attrition_plot_by_install_for_frequency_of_choose_difficulty()

