import datetime

import pytz
from shapely import wkb
from shapely.geometry import Point
from sqlalchemy import select

from maps.map_descriptor import MapDescriptor
from movie.entity.geolocation import GeoLocation
from movie.entity.track import TrackBag, TrackPoint


class TrackRepository:
    def __init__(self, engine):
        """
        engine could be obtained as
        engine = sqlalchemy.create_engine(settings.db_uri)
        """
        self.engine = engine

    def load_tracks(
            self,
            map: MapDescriptor,
            start: datetime.datetime,
            end: datetime.datetime) -> TrackBag:
        tracks = TrackBag()

        step, steps_total = 1, round((end - start).total_seconds() / 60 / 60)

        while start < end:
            print(f"Downloading part {step} of {steps_total}")
            step += 1
            query_end = start + datetime.timedelta(hours=1)
            query_end = min(end, query_end)
            query = (
                select(GeoLocation)
                    .where(GeoLocation.time >= start)
                    .where(GeoLocation.time < query_end)
                    .order_by(GeoLocation.time)
            )
            result = self.engine.execute(query)

            row: GeoLocation
            for row in result.fetchall():
                coords, track_time, tracker_id = row.coordinates, row.time, row.tracker_id
                world_point: Point = wkb.loads(bytes(coords.data))
                canvas_point = map.geo_to_canvas(
                    (world_point.y, world_point.x))
                tracks.add_point(TrackPoint(
                    canvas_coords=canvas_point,
                    track_time=track_time.astimezone(pytz.utc)
                ), tracker_id)
            start = query_end
        # for track in tracks.track_by_id.values():
        #     track.points.sort(key=lambda p: p.track_time)

        return tracks
