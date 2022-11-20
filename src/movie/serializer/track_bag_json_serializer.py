import datetime
from typing import Dict, Any


from movie.entity.track import TrackBag, Track
from movie.serializer.time_conversion import time_to_minutes


class TrackBagJsonSerializer:
    @classmethod
    def serialize(cls, track_bag: TrackBag) -> Dict[Any, Any]:
        data = [cls.serialize_track(i, v) for i, v in track_bag.track_by_id.items()]
        return {"data": data}

    @classmethod
    def serialize_track(cls, track_id: int, track: Track) -> Any:
        return [track_id, [[time_to_minutes(p.track_time),
                            round(p.canvas_coords[0]),
                            round(p.canvas_coords[1])] for p in track.points]]
