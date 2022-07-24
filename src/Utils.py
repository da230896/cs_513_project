from collections import defaultdict
import re 
import calendar
import datetime
import pandas as pd
from pyzipcode import ZipCodeDatabase

simple_date_pattern = r"[0-9]+\/[0-9]+\/[0-9]+" # .../.../...
simple_date_pattern_2 = r"(\d{1,2}\/\d{1,2}\/\d{4})|(\d{1,2}\/\d{1,2}\/\d{2})" # ../../1996 or ../../96
year_pattern = r"\b\d{4}\b" # 1996 explicit boundaries
explicit_1or2digits = r"\b\d{1,2}\b" # only 1 or 12...
month_pattern = r"jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?"
weekday_pattern = r"[a-zA-Z]+\s*:"
time_extract_pattern = r"(\d+:*\d*)\s*(am|pm)" # for 09:00 am

# date time consumable patterns
input_format_group1 = "%m/%d/%Y" # 02/13/1996
input_format_group2 = "%m/%d/%y" # 02/13/96
output_format = "%Y-%m-%d"

FMID = "FMID"
ZIP = "zip"
zip_code_db = ZipCodeDatabase()

def parse_date(r: pd.Series, *args):
    """
        Given a simple string ../../.... to ../../.... parse and give the list
    """
    # three crazy data cleaning issue came up:
    # 1. Date is out of month range
    # 2. few have years in terms of 2 digits => this can be handled here in except --> Done
    # 3. Some have Extra supporting string like "Start Date" and "End Date" str, Need to remove them --> Done
    # 4. Done: need to add IC where if year match,if  months match then dates diff
    column_key = args[0]
    lo_mo = re.finditer(simple_date_pattern_2, r[column_key]) # ["1/2/1996", "2/2/1996"]
    datetime_list = []
    for mo in lo_mo:
        try:
            s = mo.group(2) if mo.group(1) is None else mo.group(1) # --> mo.group(2) present only if mo.group(1) is not there
            format_ = input_format_group2 if mo.group(1) is None else input_format_group1
            datetime_list.append(datetime.datetime.strptime(s, format_))
        except Exception as e:
            print(r[FMID], "Has some issues", e)
    if len(datetime_list) != 2:
        print(r[FMID], "Has only 1 parsable date")
        return []

    d1 = datetime_list[0]
    d2 = datetime_list[1]
    if d1.year == d2.year and d1.month == d2.month and d1.day == d2.day:
        # this is a violation of IC
        print("Dates are same for ", r[FMID])
        return []

    return [str(d1.date()), str(d2.date())]

def find_month_index(mo: str):
    ls1 = [s.lower() for s in list(calendar.month_abbr)]
    ls2 = [s.lower() for s in list(calendar.month_name)]
    if mo in ls1:
        return ls1.index(mo)
    elif mo in ls2:
        return ls2.index(mo)
    raise Exception("Month not correct", mo)

def get_year(text: str, id: str):
    lo_mo_year = list(re.finditer(year_pattern, text)) # matching exact 4-digit numbers
    if len(lo_mo_year) > 2 or len(lo_mo_year) < 1:
        print("non cleanable data since More than 2/less than 1 year str", id)
        return None
    year = lo_mo_year[0].group()
    if len(lo_mo_year) == 2:
        if year != lo_mo_year[1].group():
            print("non cleanable data since different years", id)
            return None
    return int(year)

def get_months(text:str, id:str):
    lo_mo_month = list(re.finditer(month_pattern, text.lower()))
    if len(lo_mo_month) > 2 or len(lo_mo_month) <= 1:
        print("non cleanable data since More than/less than 2 months str", id)
        return None
    try:
        m1 = find_month_index(lo_mo_month[0].group())
        m2 = find_month_index(lo_mo_month[1].group())
    except Exception as e:
        print("non cleanable data some exception at getting month index", id, e)
        return None
    return m1, m2

def get_dates(text: str, id: str):
    dates_lo_mo = list(re.finditer(explicit_1or2digits, text))
    if len(dates_lo_mo) > 2 or len(dates_lo_mo) <= 1:
        print("non cleanable data since More than/less than 2 date str", id)
        return None
    d1 = int(dates_lo_mo[0].group())
    d2 = int(dates_lo_mo[1].group())
    return d1, d2

def parse_complex_date(r: pd.Series, *args):
    """
        Given a complex dates like "12 June 2012 to 13 July 2012" parse them and return the list of dates
    """
    id = r[FMID]
    text = r[args[0]]

    # cleaning
    # 1. years can be 1 but if 2 then they should be same --> Done
    # 2. Months need to be 2. If same then dates need to be different
    # 3. Dates need to be 2.
    # 4. convert to ISO format
    year = get_year(text, id)
    if year is None:
        return []

    months = get_months(text, id)
    if months is None:
        return []
    else:
        m1, m2 = months

    dates = get_dates(text, id)
    if dates is None:
        return []
    else:
        d1, d2 = dates

    if m1 == m2:
        # check dates are diff
        if d1 == d2:
            print("non cleanable data since need 2 diff dates str", id)
            return []

    from_date = datetime.datetime(year, m1, d1)
    to_date = datetime.datetime(year, m2, d2)
    return [str(from_date.date()), str(to_date.date())]

def validate_zip_code(z: str):
    return z.isnumeric() and zip_code_db.get(z) is not None

def get_timezone(zip: str):
    offset = zip_code_db[int(zip)].timezone
    return datetime.timezone(offset=datetime.timedelta(hours=offset))

def get_iso_date_from_pair(t_str: str, am_or_pm: str, tz): # ("09:00", "am") ==> iso
    # for case ("3", "pm") need to allow 0 min
    t_h = int(t_str.split(":")[0])
    if am_or_pm == "pm" and t_h != 12:
        t_h += 12 # 12 pm is as is, rest +12
    if am_or_pm == "am" and t_h == 12:
        t_h = 0 # 12 am is 00 rest as is
    t_m = int(t_str.split(":")[1]) if len(t_str.split(":")) > 1 else 0
    return datetime.time(hour=t_h, minute=t_m, tzinfo=tz)

def parse_time(s: pd.Series, *args):
    col_key = args[0]
    timings_dict = {} # day: tuple of start and end time
    for data in s[col_key]: # [Wed: 9:00 AM-1:00 PM,]
        if data == "":
            continue
        weekdays = list(re.finditer(weekday_pattern, data))
        if len(weekdays) > 1 or len(weekdays) == 0:
            print("one weekday entry should not have multiple weekdays in it", s[FMID])
            continue

        day = (weekdays[0].group()[:-1]).lower().strip()
        raw_time_data = data[weekdays[0].end():].strip()
        timings = re.findall(time_extract_pattern, raw_time_data.lower()) # [("09:00", "am"), ("9", "pm")]
        if len(timings) != 2:
            print("there should be open and close time", s[FMID])
            continue
        try:
            tz = get_timezone(s[ZIP])
            t0 = get_iso_date_from_pair(timings[0][0], timings[0][1], tz)
            t1 = get_iso_date_from_pair(timings[1][0], timings[1][1], tz)
        except Exception as e:
            print("Some issue in converting to iso ", s[FMID], e)
            continue

        if timings_dict.get(day) is not None:
            print("check multiple days reported for", s[FMID])
            print("prev data", timings_dict.get(day), "current data:", raw_time_data)
            continue
        timings_dict[day] = [t0.isoformat(), t1.isoformat()]
    return timings_dict