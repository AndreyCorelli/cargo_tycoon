import datetime
import json
import os
import time
from typing import Optional, Dict, Any

import sqlalchemy

from maps.map_descriptor import MapDescriptor
from movie.entity.track import TrackBag
from movie.repository.track_repository import TrackRepository
from movie.serializer.time_conversion import START_DATE, time_to_minutes, time_to_timespan
from movie.serializer.track_bag_json_serializer import TrackBagJsonSerializer
from paths import CACHE_PATH
from settings import settings


class PageDataSource:
    def __init__(
            self,
            geo_map: MapDescriptor):
        self.geo_map = geo_map
        self.track_bag = TrackBag()

    def get_track(
            self,
            start_time_utc: datetime.datetime,
            end_time_utc: datetime.datetime) -> str:
        data = self.get_cached_data(start_time_utc, end_time_utc)
        if not data:
            data = self.read_data_from_server(start_time_utc, end_time_utc)
        data = self._set_data_timings(data, start_time_utc, end_time_utc)
        return data

    def read_data_from_server(
            self,
            start_time_utc: datetime.datetime,
            end_time_utc: datetime.datetime) -> str:
        engine = sqlalchemy.create_engine(settings.db_uri)
        repo = TrackRepository(engine)
        track_bag = repo.load_tracks(
            self.geo_map,
            start_time_utc,
            end_time_utc
        )
        data = TrackBagJsonSerializer.serialize(track_bag)
        self.cache_data(start_time_utc, end_time_utc, data)
        return data

    def cache_data(self,
                   start_time_utc: datetime.datetime,
                   end_time_utc: datetime.datetime,
                   data: str) -> None:
        file_path = self._get_cache_file_path(start_time_utc, end_time_utc, False)
        with open(file_path, 'w') as f:
            f.write(data)

    def get_cached_data(self, start_time_utc: datetime.datetime,
                        end_time_utc: datetime.datetime) -> Optional[str]:
        file_path = self._get_cache_file_path(start_time_utc, end_time_utc, True)
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
        return f"{start_time_utc:%y_%m_%d_%H_%M}-{end_time_utc:%y_%m_%d_%H_%M}.txt"

    @classmethod
    def _set_data_timings(
            cls,
            data: str,
            start_time_utc: datetime.datetime,
            end_time_utc: datetime.datetime):
        prefix = f"{time_to_timespan(start_time_utc)}," + \
                 f"{time_to_timespan(end_time_utc)}," + \
                 f"{time_to_minutes(start_time_utc)}," + \
                 f"{time_to_minutes(end_time_utc)},"
        return prefix + data
