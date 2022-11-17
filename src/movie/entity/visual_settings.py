import datetime
from dataclasses import dataclass
from typing import Tuple, List, Optional, Callable

import cv2


@dataclass
class DrawingSettings:
    path_transparency: float = 0.6
    path_thickness: float = 2
    path_tail_thickness: float = 1

    head_radius: float = 3
    head_thickness: float = 1


def format_time_minutes(tm: datetime.datetime) -> str:
    return f"{tm:%Y/%m/%d/} {tm:%H:%M}"


def format_time_hours(tm: datetime.datetime) -> str:
    return f"{tm:%Y/%m/%d} {tm:%H}:00"


@dataclass
class TimerDrawingSettings:
    format_time_string: Callable[[datetime.datetime], str] = format_time_minutes

    relative_coords: Optional[Tuple[float, float]] = (2, 94)
    abs_coords: Optional[Tuple[int, int]] = None

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.66
    color = (222, 222, 222)
    thickness: float = 2

    background_color = (22, 22, 22)
    background_size = (220, 34)


@dataclass
class TrackColorMap:
    colors: List[Tuple[int, int, int]]

    def get_color(self, hashing_number: int) -> Tuple[int, int, int]:
        i = hashing_number % len(self.colors)
        return self.colors[i]


DEFAULT_COLOR_MAP = TrackColorMap(
    [
        (180, 20, 20),
        (120, 60, 20),
        (80, 100, 20),
        (40, 140, 20),
        (20, 180, 20),
        (20, 140, 60),
        (20, 100, 100),
        (20, 60, 140),
        (20, 20, 180)
    ]
)
