from maps.map_descriptor import MapDescriptor
from movie.entity.track import TrackBag, Track
from movie.serializer.time_conversion import time_to_minutes


class TrackBagJsonSerializer:
    @classmethod
    def serialize(cls, map: MapDescriptor, track_bag: TrackBag) -> str:
        data = ""
        for i, track in track_bag.track_by_id.items():
            data += cls.serialize_track(map, i, track)
        return data

    @classmethod
    def serialize_track(cls, map: MapDescriptor, track_id: int, track: Track) -> str:
        if not track.points:
            return ""
        str_data = f"{track_id},"
        prev_minute = 0
        last_coords = None

        for p in track.points:
            minute = time_to_minutes(p.track_time)
            time_delta = minute - prev_minute

            prev_minute = minute

            xy = round(p.canvas_coords[0]), round(p.canvas_coords[1])
            if last_coords and map.is_leap(xy, last_coords):
                # there's a sudden leap from one geo point to another
                # we'll insert an empty point as an indication of this anomaly
                str_data += f"{time_delta},0,0,"
            last_coords = xy

            str_data += f"{time_delta},{xy[0]},{xy[1]},"
        str_data += "#"
        return str_data
