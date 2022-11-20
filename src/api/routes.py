import datetime

import pytz
from flask import current_app as app
from flask import render_template

from maps.map_descriptor import square_map
from movie.page_data_source import PageDataSource


@app.route('/')
def index():
    """Landing page."""
    return render_template(
        'index.html',
        title="Sennder Keeps Tracking",
        description="Sennder Keeps Tracking"
    )


@app.route('/track_data/')
def track_data():
    # year = request.args.get('year', datetime.date.today().year)
    # week = request.args.get('week', 0)

    data_source = PageDataSource(
        square_map,
    )
    track_data = data_source.get_track(
        datetime.datetime(2022, 10, 13, 7, 0, 0, 0, pytz.UTC),
        datetime.datetime(2022, 10, 26, 7, 0, 0, 0, pytz.UTC)
    )
    return track_data
