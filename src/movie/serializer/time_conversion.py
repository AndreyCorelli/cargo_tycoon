import datetime
import time

import pytz

START_DATE = datetime.datetime(2016, 1, 1, 0, 0, 0, 0, pytz.UTC)


def time_to_minutes(t: datetime.datetime) -> int:
    return int((t - START_DATE).total_seconds() / 60)


def time_to_timespan(t: datetime.datetime) -> int:
    return int(time.mktime(t.timetuple()))
