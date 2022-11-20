import math
import os
from typing import Tuple, List

import cv2

from paths import IMAGES_PATH


class GeoPivot:
    """
    being used solely in MapDescriptor
    """
    def __init__(self, lat: float, lon: float, canvas_x: int, canvas_y: int):
        self.lat = lat
        self.lon = lon
        self.canvas_x = canvas_x
        self.canvas_y = canvas_y


class MapDescriptor:
    """
    Translate geo coords to the coordinates of the map
    for which we define:
    - size in pixels (canvas_w, canvas_h)
    - 2 pivot points
    - where for each pivot points we define:
    - - geo coords (lat, lon)
    - - map coords (canvas_x, canvas_y) in pixels
    For formulas check
    https://stackoverflow.com/questions/14329691/convert-latitude-longitude-point-to-a-pixels-x-y-on-mercator-projection
    """
    def __init__(
            self,
            map_file_path: str,
            canvas_w: int,
            canvas_h: int,
            pivots: List[GeoPivot]):
        self.map_file_path = map_file_path
        self.map_pic = cv2.imread(map_file_path)
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.pivots = pivots

        pivot_a = self._get_rel_canvas_coords((self.pivots[0].lat, self.pivots[0].lon))
        pivot_b = self._get_rel_canvas_coords((self.pivots[1].lat, self.pivots[1].lon))
        self.kx = (self.pivots[1].canvas_x - self.pivots[0].canvas_x) / (pivot_b[0] - pivot_a[0])
        self.ky = (self.pivots[1].canvas_y - self.pivots[0].canvas_y) / (pivot_b[1] - pivot_a[1])
        self.left = self.pivots[0].canvas_x - pivot_a[0] * self.kx
        self.top = self.pivots[0].canvas_y - pivot_a[1] * self.ky
        min_dim = min(canvas_w, canvas_h)
        self.leap_dist_px_square = (min_dim / 30) ** 2

    def geo_to_canvas(self, coords: Tuple[float, float]) -> Tuple[float, float]:
        rel_x, rel_y = self._get_rel_canvas_coords(coords)
        x = rel_x * self.kx + self.left
        y = rel_y * self.ky + self.top
        return x, y

    def is_leap(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        # We calculate the squared distance in pixels. Two points that are separated further
        # then this value are considered belonging to different segments
        dx, dy = a[0] - b[0], a[1] - b[1]
        distance = dx * dx + dy * dy
        return distance > self.leap_dist_px_square

    @classmethod
    def _get_rel_canvas_coords(cls, coords: Tuple[float, float]) -> Tuple[float, float]:
        """
        convert (lat, long) to (x, y)
        x, y are relative canvas coordinates
        """
        w, h = 1.0, 1.0
        latitude, longitude = coords
        x = (longitude + 180) * (w / 360)
        lat_rad = latitude * math.pi / 180
        merc_n = math.log(math.tan((math.pi / 4) + (lat_rad / 2)))
        y = (h / 2) - (w * merc_n / (2 * math.pi))
        return x, y


def make_default_map_descriptor() -> MapDescriptor:
    london_pivot = GeoPivot(51.57733, -0.13942, 518, 386)
    tbilisi_pivot = GeoPivot(41.70609, 44.79598, 1733, 772)

    return MapDescriptor(os.path.join(IMAGES_PATH, "map.png"),
                         1841, 974, [london_pivot, tbilisi_pivot])


def make_square_map_descriptor() -> MapDescriptor:
    dublin_pivot = GeoPivot(53.3244431, -6.385786, 182, 353)
    istanbul_pivot = GeoPivot(41.0055005, 28.7319977, 1065, 812)

    return MapDescriptor(os.path.join(IMAGES_PATH, "map_square.png"),
                         1122, 976, [dublin_pivot, istanbul_pivot])


# mapping for /src/img/map.png
default_map = make_default_map_descriptor()

# mapping for /src/img/map_square.png
square_map = make_square_map_descriptor()
