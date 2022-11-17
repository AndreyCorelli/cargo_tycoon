import datetime
import os
from dataclasses import dataclass
from typing import Optional, Tuple, List

import cv2
import sqlalchemy
import numpy as np
from numpy import ndarray

from maps.map_descriptor import MapDescriptor
from movie.entity.track import TrackBag, Track
from movie.entity.visual_settings import TrackColorMap, DEFAULT_COLOR_MAP, \
    DrawingSettings, TimerDrawingSettings
from movie.repository.track_repository import TrackRepository
from paths import OUTPUT_PATH
from settings import settings


@dataclass
class MovieTiming:
    start_time: datetime.datetime
    end_time: datetime.datetime
    seconds_per_frame: int
    track_fading_seconds: int
    track_cutting_seconds: int
    video_framerate: float = 20

    @property
    def frames_count(self) -> int:
        fc = (self.end_time - self.start_time).total_seconds() / self.seconds_per_frame
        return int(round(fc))


class MovieOperator:
    def __init__(
            self,
            frames_folder: str,
            geo_map: MapDescriptor,
            movie_timing: MovieTiming,
            color_map: Optional[TrackColorMap] = None,
            drawing_settings: Optional[DrawingSettings] = None,
            timer_drawing_settings: Optional[TimerDrawingSettings] = None):
        self.frames_folder = frames_folder
        self.geo_map = geo_map
        self.movie_timing = movie_timing
        self.color_map = color_map or DEFAULT_COLOR_MAP
        self.drawing_settings = drawing_settings or DrawingSettings()
        self.timer_drawing_settings = timer_drawing_settings
        self.track_bag = TrackBag()

    def shot(self):
        engine = sqlalchemy.create_engine(settings.db_uri)
        repo = TrackRepository(engine)
        self.track_bag = repo.load_tracks(
            self.geo_map,
            self.movie_timing.start_time,
            self.movie_timing.end_time
        )
        self.track_bag.colorize(self.color_map)
        self._shot_all_frames()
        print("Rendering video...")
        self._render_video()
        print(f"Video's ready in the {self.frames_folder} folder")

    def _shot_all_frames(self):
        frame_num, frames_total = 1, self.movie_timing.frames_count
        start, end = self.movie_timing.start_time, self.movie_timing.end_time

        while start < end:
            print(f"Filming frame {frame_num} of {frames_total}")
            query_end = start + datetime.timedelta(
                seconds=self.movie_timing.seconds_per_frame)
            query_end = min(end, query_end)

            frame_path = os.path.join(
                self.frames_folder, f"frame_{frame_num:04}.png")
            self._shot_frame(query_end, frame_path)

            start = query_end
            frame_num += 1
            # break

    def _render_video(self):
        image_folder = self.frames_folder
        video_path = os.path.join(self.frames_folder, 'video.avi')

        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        images.sort()
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(
            video_path, 0, self.movie_timing.video_framerate, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()

    def _shot_frame(
            self,
            frame_time: datetime.datetime,
            frame_file_name: str):
        alpha = self.drawing_settings.path_transparency
        background = self.geo_map.map_pic.copy()
        overlay = background.copy()

        tail_start = frame_time - datetime.timedelta(seconds=self.movie_timing.track_cutting_seconds)
        body_start = frame_time - datetime.timedelta(seconds=self.movie_timing.track_fading_seconds)

        for _, track in self.track_bag.track_by_id.items():
            overlay = self._draw_track(
                overlay, track, frame_time, tail_start, body_start)
        merged_image = cv2.addWeighted(overlay, alpha, background, 1 - alpha, 0)
        merged_image = self._draw_time_stamp(merged_image, frame_time)
        cv2.imwrite(frame_file_name, merged_image)

    def _draw_track(
            self,
            overlay: ndarray,
            track: Track,
            frame_time: datetime.datetime,
            tail_start: datetime.datetime,
            body_start: datetime.datetime) -> ndarray:
        if tail_start > track.points[-1].track_time:
            return overlay
        if frame_time < track.points[0].track_time:
            return overlay
        points_body, points_tail = [], []

        for pt in track.points:
            if pt.track_time > frame_time:
                break
            if pt.track_time >= body_start:
                points_body.append(pt.integer_xy_coords)
                continue
            if pt.track_time >= tail_start:
                points_tail.append(pt.integer_xy_coords)

        # draw the tail and the body
        for points, thickness in [
            (points_tail, self.drawing_settings.path_tail_thickness),
            (points_body, self.drawing_settings.path_thickness)]:
            if not points:
                continue
            overlay = self._draw_track_polyline(overlay, points, thickness, track.color)
        # draw the head
        if len(points_body) > 1:
            # if the track is being updated
            if points_body[0] != points_body[-1]:
                overlay = cv2.circle(
                    overlay, points_body[-1],
                    self.drawing_settings.head_radius,
                    track.color,
                    self.drawing_settings.head_thickness)
        return overlay

    def _draw_track_polyline(
            self, overlay: ndarray, points: List[Tuple[int, int]],
            thickness: float, color: Tuple[int, int, int]):
        # split the line to a number of lines if there are
        # leaps (huge distances between 2 adjacent points)
        prev_pt = points[0]
        segments = [[]]
        for point in points:
            if self.geo_map.is_leap(point, prev_pt):
                segments.append([point])
            else:
                segments[-1].append(point)
            prev_pt = point

        for segment in segments:
            pts = np.array(segment, np.int32)
            pts = pts.reshape((-1, 1, 2))
            overlay = cv2.polylines(
                overlay,
                [pts],
                False,
                color,
                thickness=thickness)
        return overlay

    def _draw_time_stamp(self, image: ndarray, frame_time: datetime.datetime) -> ndarray:
        sets = self.timer_drawing_settings
        if not sets:
            return image
        time_str = sets.format_time_string(frame_time)
        coords = sets.abs_coords
        if not coords:
            rel_x, rel_y = sets.relative_coords
            coords = round(self.geo_map.canvas_w * rel_x / 100), \
                     round(self.geo_map.canvas_h * rel_y / 100)

        PADDING = 5
        if sets.background_size[0]:
            coords_top = coords[0] - PADDING, coords[1] + PADDING
            coords_btm = coords[0] + sets.background_size[0], coords[1] - sets.background_size[1]
            image = cv2.rectangle(image, coords_top, coords_btm, sets.background_color, -1)

        image = cv2.putText(image, time_str, (coords[0], coords[1] - PADDING * 2),
                            sets.font, sets.font_scale, sets.color, sets.thickness)
        return image

    @classmethod
    def create_default_frames_folder(cls) -> str:
        out_path = os.path.join(OUTPUT_PATH, f"{datetime.date.today()}")
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        return out_path
