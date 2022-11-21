from flask import current_app as app, make_response, request
from flask import render_template

from maps.map_descriptor import square_map
from movie.page_data_cache import PageDataCache
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
    start_date = PageDataCache.parse_date_short_str(request.args.get('start_date'))
    end_date = PageDataCache.parse_date_short_str(request.args.get('end_date'))

    data_source = PageDataSource(
        square_map,
    )
    data = data_source.get_track(
        start_date,
        end_date
    )
    response = make_response(data, 200)
    response.mimetype = "text/plain"
    return response


@app.route('/cached_periods/')
def cached_periods():
    return PageDataCache.get_cached_intervals()
