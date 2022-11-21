import datetime

import sqlalchemy

from maps.map_descriptor import MapDescriptor
from movie.entity.track import TrackBag
from movie.page_data_cache import PageDataCache
from movie.repository.track_repository import TrackRepository
from movie.serializer.time_conversion import time_to_minutes, time_to_timespan
from movie.serializer.track_bag_json_serializer import TrackBagJsonSerializer
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
        data = PageDataCache.get_cached_data(start_time_utc, end_time_utc)
        if not data:
            data = self._read_data_from_server(start_time_utc, end_time_utc)
        data = self._set_data_timings(data, start_time_utc, end_time_utc)
        return data

    def _read_data_from_server(
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
        data = TrackBagJsonSerializer.serialize(self.geo_map, track_bag)
        PageDataCache.cache_data(start_time_utc, end_time_utc, data)
        return data

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
