import datetime
import re
from dateutil.parser import parse


def set_range_with_today():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    day_before_yesterday = yesterday - datetime.timedelta(days=1)
    return yesterday, day_before_yesterday


def set_range(start, till, with_range=False):
    start, till = parse(start), parse(till)
    return start, till
