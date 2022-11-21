import datetime
import os
from typing import Optional, List, Tuple
import re

import pytz

from paths import CACHE_PATH


class PageDataCache:
    @classmethod
    def parse_date_short_str(cls, date_str: str) -> datetime.datetime:
        year_month_date = [int(s) for s in date_str.split('-')]
        return datetime.datetime(year_month_date[0], year_month_date[1], year_month_date[2], 0, 0, 0, 0, pytz.UTC)

    @classmethod
    def get_cached_intervals(cls) -> List[Tuple[str, str]]:

        file_names = [o for o in os.listdir(CACHE_PATH)
                      if os.path.isfile(os.path.join(CACHE_PATH, o))]

        date_strings = []
        for file_name in file_names:
            dates = cls._parse_file_name(file_name)
            if not dates:
                continue

            name_dates = [f"{d[0]}-{d[1]}-{d[2]}" for d in dates]
            date_strings.append((name_dates[0], name_dates[1]))
        return date_strings

    @classmethod
    def _parse_file_name(cls, file_name: str) -> Optional[List[Tuple[int, int, int]]]:
        pattern = re.compile(r"^\d{2,2}_\d{2,2}_\d{2,2}\-\d{2,2}_\d{2,2}_\d{2,2}$")
        name, _ = os.path.splitext(file_name)
        if not pattern.match(name):
            return None

        name_dates = name.split("-")
        result = []
        for date_str in name_dates:
            parts = date_str.split("_")
            result.append((int(parts[0]), int(parts[1]), int(parts[2])))

        return result

    @classmethod
    def cache_data(cls,
                   start_time_utc: datetime.datetime,
                   end_time_utc: datetime.datetime,
                   data: str) -> None:
        file_path = cls._get_cache_file_path(start_time_utc, end_time_utc, False)
        with open(file_path, 'w') as f:
            f.write(data)

    @classmethod
    def get_cached_data(cls, start_time_utc: datetime.datetime,
                        end_time_utc: datetime.datetime) -> Optional[str]:
        file_path = cls._get_cache_file_path(start_time_utc, end_time_utc, True)
        if not file_path:
            return None
        # read file and deserialize
        with open(file_path) as f:
            return f.read()

    @classmethod
    def _get_cache_file_path(cls,
                             start_time_utc: datetime.datetime,
                             end_time_utc: datetime.datetime,
                             check_file_exists: bool) -> str:
        key = cls._get_cache_key(start_time_utc, end_time_utc)
        file_path = os.path.join(CACHE_PATH, key)
        if check_file_exists and not os.path.isfile(file_path):
            return ""
        return file_path

    @classmethod
    def _get_cache_key(cls, start_time_utc: datetime.datetime,
                       end_time_utc: datetime.datetime) -> str:
        return f"{start_time_utc:%y_%m_%d}-{end_time_utc:%y_%m_%d}.txt"
