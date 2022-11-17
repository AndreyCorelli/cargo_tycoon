import datetime
from dataclasses import dataclass
from typing import Tuple, List, Dict

from movie.entity.visual_settings import TrackColorMap


@dataclass
class TrackPoint:
    canvas_coords: Tuple[float, float]
    track_time: datetime.datetime

    @property
    def integer_xy_coords(self) -> Tuple[int, int]:
        return round(self.canvas_coords[0]), round(self.canvas_coords[1])


@dataclass
class Track:
    points: List[TrackPoint]
    color: Tuple[int, int, int] = (20, 20, 60)


class TrackBag:
    def __init__(self):
        self.track_by_id: Dict[int, Track] = {}

    def add_point(self, point: TrackPoint, track_id: int):
        track = self.track_by_id.get(track_id)
        if track:
            track.points.append(point)
            return
        track = Track([point])
        self.track_by_id[track_id] = track

    def colorize(self, color_map: TrackColorMap):
        for id, track in self.track_by_id.items():
            track.color = color_map.get_color(id)
