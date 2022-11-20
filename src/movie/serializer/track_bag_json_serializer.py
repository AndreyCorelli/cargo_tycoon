from movie.entity.track import TrackBag, Track
from movie.serializer.time_conversion import time_to_minutes


class TrackBagJsonSerializer:
    @classmethod
    def serialize(cls, track_bag: TrackBag) -> str:
        data = ""
        for i, track in track_bag.track_by_id.items():
            data += cls.serialize_track(i, track)
        return data

    @classmethod
    def serialize_track(cls, track_id: int, track: Track) -> str:
        if not track.points:
            return ""
        str_data = f"{track_id},"
        prev_minute = 0
        for p in track.points:
            minute = time_to_minutes(p.track_time)
            str_data += f"{minute - prev_minute},"
            prev_minute = minute
            str_data += f"{round(p.canvas_coords[0])},{round(p.canvas_coords[1])},"
        str_data += "#"
        return str_data
