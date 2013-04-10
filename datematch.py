import re
from datetime import datetime, timedelta

def hunt_for_day (now, dow, forward, match_today = False):
    direction = -1
    start = 1
    if forward:
        direction = 1
    if match_today:
        start = 0
    for days in range (start, 8):
        next_date = now + timedelta(days=days*direction)
        next_dow = next_date.strftime ('%A').lower()
        if next_dow.startswith (dow):
            return next_date
    return None

def find_first_of_month (now):
    year = now.year
    month = now.month
    return datetime.strptime(str(year) + '-' + str(month) + '-01', '%Y-%m-%d')

def find_next_month (now):
    in_next_month = find_first_of_month (now) + timedelta(days=33)
    return find_first_of_month (in_next_month)

def find_prev_month (now):
    in_last_month = find_first_of_month (now) + timedelta(days=-1)
    return find_first_of_month (in_last_month)

def find_end_of_month (now):
    first_of_this_month = find_first_of_month (now)
    first_of_next_month = find_next_month (first_of_this_month)
    return first_of_next_month - timedelta (days=1)
    
def hunt_for_month (now, month_to_find, forward, match_this_month = False):
    month = None
    if not match_this_month:
        if forward:
            month = find_next_month (now)
        else:
            month = find_prev_month (now)
    else:
        month = find_first_of_month (now)
        
    for i in range (0, 12):
        i = i # stop warning
        month_name = month.strftime ('%B').lower()
        if month_name.startswith (month_to_find):
            return month
        if forward:
            month = find_next_month (month)
        else:
            month = find_prev_month (month)
    return None

def find_monday_this_week (now):
    return hunt_for_day (now, 'mo', False, match_today=True)

def find_monday_next_week (now):
    return hunt_for_day (now, 'mo', True, match_today=False)

def find_january_this_year (now):
    year = now.year
    return datetime.strptime(str(year) + '-01-01', '%Y-%m-%d')

def date_from_string (now, date_str):
    if date_str == "today":
        return now
    elif date_str == 'yesterday':
        return now + timedelta(days=-1)
    elif date_str == 'tomorrow':
        return now + timedelta(days=1)
    elif re.match ('^next (mo|tu|we|th|fr|sa|su)', date_str) != None:
        dow = date_str[4:].strip ()
        next_monday = find_monday_next_week (now)
        return hunt_for_day (next_monday, dow, True, match_today=True)
    elif re.match ('^last (mo|tu|we|th|fr|sa|su)', date_str) != None:
        dow = date_str[4:].strip ()
        this_monday = find_monday_this_week (now)
        return hunt_for_day (this_monday, dow, False)
    elif re.match ('^(mo|tu|we|th|fr|sa|su)', date_str) != None:
        dow = date_str.strip ()
        monday = find_monday_this_week (now)
        return hunt_for_day (monday, dow, True, match_today=True)
    elif re.match ('^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', date_str) != None:
        month = date_str.strip ()
        jan = find_january_this_year (now)
        return hunt_for_month (jan, month, True, match_this_month=True)
    elif re.match ('^next (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', date_str) != None:
        month_str = date_str[4:].strip ()
        jan = find_january_this_year (now)
        month = hunt_for_month (jan, month_str, True, match_this_month=True).month
        year = now.year
        return datetime.strptime(str(year + 1) + '-' + str(month) + '-01', '%Y-%m-%d')
    elif re.match ('^last (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', date_str) != None:
        month_str = date_str[4:].strip ()
        jan = find_january_this_year (now)
        return hunt_for_month (jan, month_str, False, match_this_month=False)
    elif re.match ('^[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9]$', date_str) != None:
        return datetime.strptime(date_str, '%Y-%m-%d')
    else:
        return None

def process_date_specifier (now, date_spec):
    date_spec = date_spec.lower().strip()
    
    if date_spec == '' or date_spec == 'none':
        return (None, None)
    if date_spec == '' or date_spec == 'any':
        # This is a bit of a hack
        return (datetime.strptime ('1900-01-01', '%Y-%m-%d'), datetime.strptime ('9000-01-01', '%Y-%m-%d'))
    
    match_date = date_from_string (now, date_spec)
    if match_date != None:
        # We've found a single stand alone date, not a range.
        # But if it's a month we want to convert it into a range
        
        if re.match ('(next |last )?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', date_spec) != None:
            return (match_date, find_end_of_month (match_date))
        else:    
            return (match_date, match_date)
    
    if date_spec == 'this week':
        mon = find_monday_this_week (now)
        sun = hunt_for_day (now, 'sun', True, match_today=True)
        return (mon, sun)
    elif date_spec == 'next week':
        mon = find_monday_this_week (now) + timedelta(days=7)
        sun = hunt_for_day (now, 'sun', True, match_today=True) + timedelta(days=7)
        return (mon, sun)
    elif date_spec == 'last week':
        mon = find_monday_this_week (now) - timedelta(days=7)
        sun = hunt_for_day (now, 'sun', True, match_today=True) - timedelta(days=7)
        return (mon, sun)
    elif date_spec.startswith ('from '):
        date_str = date_spec[4:].strip()
        start =  date_from_string (now, date_str)
        return (start, None)
    elif date_spec.startswith ('to '):
        date_str = date_spec[2:].strip()
        end =  date_from_string (now, date_str)
        if re.match ('.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', date_str) != None:
            end = find_end_of_month (end)
        return (None, end)
    elif re.search (' to ', date_spec) != None:
        elements = str.split (date_spec, ' to ')
        elements = [x.strip() for x in elements if len (x) > 0]
        start = date_from_string(now, elements[0])
        end = date_from_string(now, elements[1])
        if re.match ('.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', elements[1]) != None:
            end = find_end_of_month (end)
        return (start, end)
    else:
        raise Exception ('I don\'t think "' + date_spec + '" is any kind of date specification I recognise')