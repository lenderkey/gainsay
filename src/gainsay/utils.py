OBJ_TABLE_ID_LENGTH = 40
OBJ_POINTER_LENGTH = 40
SUBCRIBER_ID_LENGTH = 40

#
#   datetime.py
#
#   Datetime helper functions
#

from typing import Generator, Tuple

import datetime
import zoneinfo
import dateutil.parser

import re
from typing import Union

REFERENCE_TZ_STR = 'America/Toronto'
REFERENCE_TZ = zoneinfo.ZoneInfo(REFERENCE_TZ_STR)
UTC = datetime.timezone.utc

def reminder_times() -> Generator[Tuple[str, str], None, None]:
    """
    This is used for the reminder time dropdowns in the annotation
    """
    for hour in range(0, 23): 
        for minute in (0, 15, 30, 45): 
            period = "AM" if hour < 12 else "PM"
            display_hour = hour % 12 or 12 
            value = f"{hour:02}:{minute:02}"
            label = f"{display_hour}:{minute:02} {period}"
            yield (value, label)

def now(**ad)-> str|datetime.datetime:
    """
    Return the current time in our standard format
    """
    return formatter_isodatetime(None, **ad)

def formatter_isodatetime(
    value:Union[datetime.datetime,datetime.date,str,None,datetime.timedelta],
    tz:Union[datetime.tzinfo,str]=None,
    as_datetime:bool=False) -> str|datetime.datetime:
    """
    Convert the value into our standard ISO datetime format
    (which is exactly the same as the Node.JS format), e.g.
    '2023-03-12T18:37:16.610Z'
    Note that ISO dates strings have a much wider format, and python
    uses something slightly differently natively.
    If value does not have a timezone, we will use tz as the timezone. 
    If in this case tz is None, it is a ValueError.
    If value is a date, assume it is noon.
    If value is a string, it must be an ISO value of some sort, otherwise ValueError.
    Note:
    - if as_datetime is True, we return a datetime.datetime object instead of a string
    """

    if value == None:
        value = datetime.datetime.utcnow().replace(tzinfo=UTC)
    elif isinstance(value, datetime.timedelta):
        value = datetime.datetime.utcnow().replace(tzinfo=UTC) + value

    if isinstance(tz, str):
        try:
            tz = zoneinfo.ZoneInfo(tz)
        except:
            raise ValueError("timezone string must be valid")

    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            if tz is None:
                raise ValueError("datetime value must have a timezone, or a timezone must be provided")
            result = value.replace(tzinfo=tz)
        else:
            result = value

    elif isinstance(value, datetime.date):
        # value.tzinfo == None
        if tz is None:
            raise ValueError("timezone must be provided for date value")
        result = datetime.datetime(value.year, value.month, value.day, 12, 0, 0, 0, tzinfo=tz)

    elif isinstance(value, str):
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            # value.tzinfo == None
            if tz is None:
                raise ValueError("timezone must be provided for date string value")
            result = datetime.datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]), 12, 0, 0, 0, tzinfo=tz)
        else:
            result = dateutil.parser.isoparse(value)
            if result.tzinfo is None:
                if tz is None:
                    raise ValueError(f"string value '{value}' must have a timezone, or a timezone must be provided")
                result = result.replace(tzinfo=tz)

    else:
        raise ValueError("value must be datetime, date, string, None or timedelta")

    result = result.astimezone(UTC)
    if as_datetime:
        return result

    return result.isoformat(timespec='milliseconds')[:-6] + 'Z'


def formatter_isodate(
    value:Union[datetime.datetime,datetime.date,str,None,datetime.timedelta],
    tz:Union[datetime.tzinfo,str]=None,
    reference_tz:Union[datetime.tzinfo,str]=REFERENCE_TZ_STR,
    *,
    as_date:bool=False,
) -> str|datetime.date:
    """
    Convert the value into our standard ISO date format YYYY-MM-DD.
    """

    for _ in range(1):
        if value == None:
            value = datetime.datetime.utcnow().replace(tzinfo=UTC)
        elif isinstance(value, datetime.timedelta):
            value = datetime.datetime.utcnow().replace(tzinfo=UTC) + value

        if isinstance(reference_tz, str):
            try:
                reference_tz = zoneinfo.ZoneInfo(reference_tz)
            except:
                raise ValueError("reference timezone string must be valid")

        if isinstance(value, datetime.datetime):
            result = dateutil.parser.isoparse(formatter_isodatetime(value, tz)).astimezone(reference_tz)
            result = result.isoformat()[:10]
            break

        elif isinstance(value, datetime.date):
            result = value.isoformat()
            break

        elif isinstance(value, str):
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                result = dateutil.parser.isoparse(value)
            elif value == "today":
                result = datetime.datetime.now().astimezone(reference_tz)
            elif value == "tomorrow":
                result = (datetime.datetime.now() + datetime.timedelta(days=1)).astimezone(reference_tz)
            elif value == "yesterday":
                result = (datetime.datetime.now() - datetime.timedelta(days=1)).astimezone(reference_tz)
            else:
                result = dateutil.parser.isoparse(formatter_isodatetime(value, tz)).astimezone(reference_tz)

            result = result.isoformat()[:10]
            break

        else:
            raise ValueError("value must be datetime, date, string, None or timedelta")
        
    if as_date:
        return datetime.date.fromisoformat(result)
        
    return result

def advance_isodatetime(dt:str):
    """
    This moves the date one millisecond into the future. This
    is because if the mismatch of our datetime concept which 
    is at the Millisecond level, vs Django's which is much more
    fine grained. Gumshoe is getting confused and returing events
    we have processed.

    The longterm solution is to implement 'list' or 'obj_list' for
    returning the objects to process, and just using Gumshoe for filtering.
    However, we are somewhat time limited at the moment!

    DPJ 2023-04-24
    """
    
    dt = formatter_isodatetime(dt, as_datetime=True)
    dt = dt + datetime.timedelta(milliseconds=1)
    return formatter_isodatetime(dt)

