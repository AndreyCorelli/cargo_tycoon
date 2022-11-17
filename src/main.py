import datetime

import pytz

from maps.map_descriptor import default_map
from movie.entity.visual_settings import TimerDrawingSettings
from movie.movie_operator import MovieOperator, MovieTiming

if __name__ == '__main__':
    frames_folder = MovieOperator.create_default_frames_folder()

    operator = MovieOperator(
        frames_folder,
        default_map,
        MovieTiming(
            start_time=datetime.datetime(2022, 10, 13, 7, 0, 0, 0, pytz.UTC),
            #end_time=datetime.datetime(2022, 11, 2, 18, 0, 0, 0, pytz.UTC),
            end_time=datetime.datetime(2022, 10, 13, 11, 0, 0, 0, pytz.UTC),
            seconds_per_frame=270,
            track_fading_seconds=60*60*4,
            track_cutting_seconds=60*60*10,
            video_framerate=24
        ),
        timer_drawing_settings=TimerDrawingSettings()
    )
    operator.shot()
