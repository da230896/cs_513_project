#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import re
import pandas as pd
from datetime import datetime
from IPython.display import display
from Utils import parse_date, FMID, simple_date_pattern, year_pattern, parse_complex_date, ZIP, validate_zip_code

# we should convert this notebook to open refine and then convert the steps to workflow using yes workflow

S_DATE = "Season3Date"
S_DATE_LIST = "Season3DateList"
FILE_NAME = "cl_farmers_s3date.csv"

df = pd.read_csv(os.path.join("..", "dataset", "input", "farmers_market.csv"))
assert df[FMID].nunique() == df.shape[0]


# Setting up basic util data frames

# In[ ]:


date = df[[FMID, S_DATE, ZIP]].dropna()
date[S_DATE] = date[S_DATE].astype(str)

date[ZIP] = date[ZIP].astype(str)
# should have valid zip code
print("invalid zip code row count-1", len(date.loc[date[ZIP].apply(validate_zip_code) == False]))
date = date.loc[date[ZIP].apply(validate_zip_code) == True]

date = date.loc[date[S_DATE].str.contains(" to ") == True] # should contain "to"
date = date.loc[date[S_DATE].str.replace(" ", "").str.isalpha() == False] # should contain some numeric data and should not be completely alphabetical


# Extracting simple and complex dates

# In[ ]:


date_simple = date.loc[date[S_DATE].apply(lambda x: re.search(simple_date_pattern, x))                    .apply(lambda x: x is not None)] # extracting simple dates  
date_complex = date.loc[date[FMID].isin(date_simple[FMID]) != True] # extracting complex dates 


# In[ ]:


date_simple[S_DATE_LIST] = date_simple[S_DATE].str.split(" to ")
date_simple[S_DATE_LIST] = date_simple.apply(parse_date, axis=1, args=(S_DATE,))
date_simple = date_simple.loc[date_simple[S_DATE_LIST].apply(len) == 2]


# Pick only those FM id which have more that 2 dates in list

# In[ ]:


# flattening
date_simple["start"] = [""]*date_simple.shape[0]
date_simple["end"] = [""]*date_simple.shape[0]
def flatten(r: pd.Series):
    r["start"] = r[S_DATE_LIST][0]
    r["end"] = r[S_DATE_LIST][1]
    return r
date_simple = date_simple.apply(flatten, axis=1)


# In[ ]:


df_to_save1 = date_simple[[FMID, "start", "end", ZIP]].reset_index(drop=True)
display(df_to_save1)


# In[ ]:


display(date_complex)
# we can simply ignore these FMIDs where there is no 4 digit year
date_complex_without_year = date_complex.loc[date_complex[S_DATE]    .apply(lambda x: re.search(year_pattern, x)).apply(lambda x: x is None) == True]
display(date_complex_without_year)
 # we need cleaning over these
date_complex_with_year = date_complex.loc[date_complex[FMID].isin(date_complex_without_year[FMID]) == False]
display(date_complex_with_year)


# In[ ]:


if date_complex_with_year.shape[0] > 0:
    date_complex_with_year[S_DATE_LIST] = date_complex_with_year.apply(parse_complex_date, axis=1, args=(S_DATE,))

display(date_complex_with_year)


# In[ ]:


if date_complex_with_year.shape[0] > 0:
    date_complex_with_year = date_complex_with_year.loc[date_complex_with_year[S_DATE_LIST].apply(len) == 2]
else:
    date_complex_with_year = date_complex_with_year
# flattening
date_complex_with_year["start"] = [""]*date_complex_with_year.shape[0]
date_complex_with_year["end"] = [""]*date_complex_with_year.shape[0]
def flatten(r: pd.Series):
    r["start"] = r[S_DATE_LIST][0]
    r["end"] = r[S_DATE_LIST][1]
    return r
date_complex_with_year = date_complex_with_year.apply(flatten, axis=1)


# In[ ]:


df_to_save2 = date_complex_with_year[[FMID, "start", "end", ZIP]]
df_to_save2 = df_to_save2.reset_index(drop=True)


# In[ ]:


display(df_to_save1)


# In[ ]:


# pd.concat([df_to_save1, df_to_save2]).to_csv(os.path.join("..", "dataset", "output", FILE_NAME))

