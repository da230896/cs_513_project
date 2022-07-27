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


# @begin cleaning_date @desc cleaning date
# @PARAM DATASET_LOC
# @PARAM zip_code_db
# @IN farmers_market @URI file:{DATASET_LOC}/input/farmers_markets.csv
# @OUT result_farmers_market @uri file:{DATASET_LOC}/output/farmers_market.csv
# @OUT cleaned_simple_date
# @OUT cleaned_complex_date
# @BEGIN load_farmers
# @PARAM DATASET_LOC
# @IN g @AS farmers_market @uri file:{DATASET_LOC}/input/farmers_markets.csv
# @OUT df
# @END load_farmers
df = pd.read_csv(os.path.join("..", "dataset", "input", "farmers_market.csv"))
assert df[FMID].nunique() == df.shape[0]


# Setting up basic util data frames

# In[ ]:

# @BEGIN drop_na @desc removing all the records where FMID, S_DATE, ZIP is NA
# @IN df
# @OUT date
# @END drop_na
date = df[[FMID, S_DATE, ZIP]].dropna()

# @BEGIN converting_date_and_zip_to_string @desc converting the S_DATE,ZIP to string
# @IN date
# @OUT date @as date_zip_to_string
# @END converting_date_and_zip_to_string
date[S_DATE] = date[S_DATE].astype(str)
date[ZIP] = date[ZIP].astype(str)

# should have valid zip code
print("invalid zip code row count-1", len(date.loc[date[ZIP].apply(validate_zip_code) == False]))

# @BEGIN validate_zip_code @desc filtering date df on ZIP should be numeric and present in zip_code_db
# @IN  date @as date_zip_to_string
# @PARAM zip_code_db
# @OUT date @as validated_zip
# @END validate_zip_code
date = date.loc[date[ZIP].apply(validate_zip_code) == True]

# @BEGIN should_contain_to @desc date field in df should contain ' to '
# @IN date @as validated_zip
# @OUT date @as date[S_DATE]_contains_to
# @END should_contain_to
date = date.loc[date[S_DATE].str.contains(" to ") == True] # should contain "to"

# @BEGIN date_should_contain_numeric @desc filtering date df on date field should contain numeric data
# @IN date @As date[S_DATE]_contains_to
# @OUT date @As cleaned_date
# @END date_should_contain_numeric
date = date.loc[date[S_DATE].str.replace(" ", "").str.isalpha() == False] # should contain some numeric data and should not be completely alphabetical


# Extracting simple and complex dates

# In[ ]:
# @BEGIN extract_simple_date @desc splitting date df on  ../../YYYY or ../../YY as date_simple df
# @IN date @As cleaned_date
# @OUT date_simple
# @END extract_simple_date
date_simple = date.loc[date[S_DATE].apply(lambda x: re.search(simple_date_pattern, x)) .apply(lambda x: x is not None)] # extracting simple dates  

# @BEGIN extract_complex_date @desc splitting date df not of  ../../YYYY or ../../YY as date_simple df  
# @IN date @As cleaned_date
# @OUT date_complex
# @END extract_complex_date
date_complex = date.loc[date[FMID].isin(date_simple[FMID]) != True] # extracting complex dates 


# In[ ]:

# @BEGIN spliting_date_on_to @desc splitting S_DATE_LIST field on ' to ' 
# @IN date_simple
# @OUT date_simple @AS date_simple_splitted_on_to
# @END spliting_date_on_to
date_simple[S_DATE_LIST] = date_simple[S_DATE].str.split(" to ")

# @BEGIN parsing_date @desc Given a simple string ../../.... to ../../.... parse and give the list
# @IN date_simple @AS date_simple_splitted_on_to
# @OUT date_simple @As parsed_date
# @END parsing_date
date_simple[S_DATE_LIST] = date_simple.apply(parse_date, axis=1, args=(S_DATE,))


# @BEGIN filtering_date @desc filtering date_simple df on S_DATE_LIST where length is 2 signifies, it contains from and to date
# @IN date_simple @AS parsed_date
# @IN date_simple
# @OUT date_simple @AS filtered_date
# @END filtering_date
date_simple = date_simple.loc[date_simple[S_DATE_LIST].apply(len) == 2]


# Pick only those FM id which have more that 2 dates in list

# In[ ]:

# @BEGIN flatten_date_simple @desc flattening date_simple df
# @IN date_simple @As filtered_date
# @OUT date_simple @As cleaned_date_simple
# @END flatten_date_simple
# flattening
date_simple["start"] = [""]*date_simple.shape[0]
date_simple["end"] = [""]*date_simple.shape[0]
def flatten(r: pd.Series):
    r["start"] = r[S_DATE_LIST][0]
    r["end"] = r[S_DATE_LIST][1]
    return r
date_simple = date_simple.apply(flatten, axis=1)


# In[ ]:

# @BEGIN saving_simple_date_df @desc saving simple date df 
# @IN date_simple @As cleaned_date_simple
# @OUT cleaned_simple_date
# @END saving_simple_date_df
df_to_save1 = date_simple[[FMID, "start", "end", ZIP]].reset_index(drop=True)
display(df_to_save1)


# In[ ]:


display(date_complex)
# we can simply ignore these FMIDs where there is no 4 digit year

# @BEGIN cleaning_date_without_year @desc cleaning date without year 
# @IN date_complex 
# @OUT date_complex @AS date_complex_without_year
# @END cleaning_date_without_year
date_complex_without_year = date_complex.loc[date_complex[S_DATE].apply(lambda x: re.search(year_pattern, x)).apply(lambda x: x is None) == True]
display(date_complex_without_year)

# ask this step details
# @BEGIN filtering_FMID_date_without_year @desc filtering FMID fields which does not have complex date format
# @IN date_complex 
# @IN date_complex @As date_complex_without_year
# @OUT date_complex @AS date_complex_with_year
# @END filtering_FMID_date_without_year
 # we need cleaning over these
date_complex_with_year = date_complex.loc[date_complex[FMID].isin(date_complex_without_year[FMID]) == False]
display(date_complex_with_year)


# In[ ]:

# @BEGIN parse_complex_date @desc  Given a complex dates like '12 June 2012 to 13 July 2012' parse them and return the list of dates
# @IN date_complex @AS date_complex_with_year
# @OUT date_complex @As parsed_date_complex_with_year
# @END parse_complex_date
if date_complex_with_year.shape[0] > 0:
    date_complex_with_year[S_DATE_LIST] = date_complex_with_year.apply(parse_complex_date, axis=1, args=(S_DATE,))

display(date_complex_with_year)


# In[ ]:


# @BEGIN filtering_complex_date @desc filtering
# @IN date_complex @AS parsed_date_complex_with_year
# @OUT date_complex @As filtered_date_complex_with_year
# @END filtering_complex_date
if date_complex_with_year.shape[0] > 0:
    date_complex_with_year = date_complex_with_year.loc[date_complex_with_year[S_DATE_LIST].apply(len) == 2]
else:
    date_complex_with_year = date_complex_with_year
    

# @BEGIN flatten_date_complex @desc flattening date_simple df
# @IN date_complex @As filtered_date_complex_with_year
# @OUT date_complex @As flattened_parsed_date_complex_with_year1
# @END flatten_date_complex
    
# flattening
date_complex_with_year["start"] = [""]*date_complex_with_year.shape[0]
date_complex_with_year["end"] = [""]*date_complex_with_year.shape[0]
def flatten(r: pd.Series):
    r["start"] = r[S_DATE_LIST][0]
    r["end"] = r[S_DATE_LIST][1]
    return r
date_complex_with_year = date_complex_with_year.apply(flatten, axis=1)


# In[ ]:

# @BEGIN saving_complex_date_df @desc saving simple date df 
# @IN date_complex @As flattened_parsed_date_complex_with_year1
# @OUT cleaned_complex_date
# @END saving_complex_date_df
df_to_save2 = date_complex_with_year[[FMID, "start", "end", ZIP]]
df_to_save2 = df_to_save2.reset_index(drop=True)


# In[ ]:


display(df_to_save1)
# @END cleaning_date

# In[ ]:


# pd.concat([df_to_save1, df_to_save2]).to_csv(os.path.join("..", "dataset", "output", FILE_NAME))

