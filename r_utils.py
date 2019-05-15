#!/usr/bin/env python
# md5: a6479d27a64b157573bca220a5297ae5
#!/usr/bin/env python
# coding: utf-8



get_ipython().run_line_magic('load_ext', 'rpy2.ipython') # type: ignore
# %load_ext rpy2.ipython



import pandas as pd

import rpy2.situation
rpy2.situation.get_r_home()

import rpy2
from rpy2.robjects import r as r_obj

from rpy2.robjects import pandas2ri
pandas2ri.activate()

def r_assign(var_name, value):
  r_obj.assign(var_name, value)

def r(r_code):
  r_obj(f"""rg_func <- function() {{
    {r_code}
  }}""")
  get_ipython().run_line_magic('R', '-w 1000 print(rg_func())') # type: ignore
  # %R -w 1000 print(rg_func())

