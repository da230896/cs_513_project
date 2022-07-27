#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import re
import datetime
import pandas as pd
from IPython.display import display
from Utils import parse_date, FMID, simple_date_pattern, year_pattern, parse_complex_date, ZIP, zip_code_db, parse_time,    validate_zip_code

# we should convert this notebook to open refine and then convert the steps to workflow using yes workflow

S_TIME = "Season4Time"
S_TIME_DICT = "Season4TimeDict" # remember to use pickl
S_TIME_LIST = "Season4TimeList" # remember to use pickl
FILE_NAME = "cl_farmers_s4time.csv"
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# @begin cleaning_time @desc cleaning time
# @PARAM DATASET_LOC
# @PARAM zip_code_db
# @IN farmers_market @URI file:{DATASET_LOC}/input/farmers_markets.csv
# @OUT result_farmers_market @uri file:{DATASET_LOC}/output/farmers_market.csv
# @OUT cleaned_time

# @BEGIN load_farmers
# @PARAM DATASET_LOC
# @IN g @AS farmers_market @uri file:{DATASET_LOC}/input/farmers_markets.csv
# @OUT df
# @END load_farmers

df = pd.read_csv(os.path.join("..", "dataset", "input", "farmers_market.csv"))
print("df.shape[0]", df.shape[0])


# @BEGIN assert_unique_records @desc asserting the unique records
# @IN df
# @OUT df @as asserted_df
# @END assert_unique_records
assert df[FMID].nunique() == df.shape[0]


# Setting up basic util data frames

# In[ ]:


# @BEGIN drop_na @desc removing all the records where FMID, S_DATE, ZIP is NA
# @IN df @as asserted_df
# @OUT df @as time_df
# @END drop_na
time = df[[FMID, S_TIME, ZIP]].dropna()

# @BEGIN converting_date_and_zip_to_string @desc converting the S_TIME,ZIP to string
# @IN df @as time_df
# @OUT time_df @as date_zip_to_string
# @END converting_date_and_zip_to_string
time[S_TIME] = time[S_TIME].astype(str)
time[ZIP] = time[ZIP].astype(str)

# should have valid zip code
print("invalid zip code row count", len(time.loc[time[ZIP].apply(validate_zip_code) == False]))

# @BEGIN validate_zip_code @desc filtering time df on ZIP should be numeric and present in zip_code_db
# @IN  time_df @as date_zip_to_string
# @PARAM zip_code_db
# @OUT time_df @as validated_zip
# @END validate_zip_code
time = time.loc[time[ZIP].apply(validate_zip_code) == True]

print("Number of FMIDs with improper timings(without ;)", len(time.loc[time[S_TIME].str.contains(";") == False]))

# @BEGIN should_contain @desc time field in df should contain ':'
# @IN time_df @as validated_zip
# @OUT time_df @as time[S_TIME]_contains_to
# @END should_contain
time = time.loc[time[S_TIME].str.contains(";") == True] # should contain ";"

# @BEGIN is_aplhanumeric @desc time field in df should contain ':'
# @IN time_df @as time[S_TIME]_contains_to
# @OUT time_df @as time[S_TIME]_is_alphanumeric
# @END is_aplhanumeric
time = time.loc[time[S_TIME].str.replace(" ", "").str.isalpha() == False] # should contain some numeric data and should not be completely alphabetical
# print(time.shape[0])


# In[ ]:

# @BEGIN split_STIME @desc time splitting STIME field on ' ; '
# @IN time_df @as time[S_TIME]_is_alphanumeric
# @OUT time_df @as splitted_STIME
# @END split_STIME
time[S_TIME_LIST] = time.apply(lambda r: r[S_TIME].split(";"), axis=1)
display(time)


# In[ ]:

# @BEGIN parse_time @desc parsing time 
# @IN time_df @as splitted_STIME
# @OUT time_df @as parsed_S_TIME_DICT
# @END parse_time
time[S_TIME_DICT] = time.apply(parse_time, axis=1, args=(S_TIME_LIST,))


# Defining columns for weekdays

# In[ ]:

# @BEGIN adding_start_end @desc adding _start and _end 
# @IN time_df @as parsed_S_TIME_DICT
# @OUT time_df @as added_weekday
# @END adding_start_end
for weekday in WEEKDAYS:
    time[weekday+"_start"] = [""]*time.shape[0]
    time[weekday+"_end"] = [""]*time.shape[0]


# In[ ]:

# @BEGIN flatten_time_simple @desc flattening S_TIME_DICT df
# @IN time_df @As added_weekday
# @OUT time_df @As flatten_time
# @END flatten_time_simple
def flatten_data(r: pd.Series):
    data = r[S_TIME_DICT]
    for key, value in data.items():
        r[key+"_start"] = value[0]
        r[key+"_end"] = value[1]
    return r

time = time.apply(flatten_data, axis=1)    


# In[ ]:


display(time)

# @BEGIN saving_simple_time_df @desc saving simple date df 
# @IN time_df @As flatten_time
# @OUT time_df @as df_to_save
# @END saving_simple_time_df
df_to_save = time.drop([S_TIME, S_TIME_LIST, S_TIME_DICT], axis=1)


# In[ ]:


df_to_save

# @END cleaning_time
# In[ ]:


# df_to_save.to_csv(os.path.join("..", "dataset", "output", FILE_NAME))

