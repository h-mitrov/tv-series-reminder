from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
from flask_login import login_required, current_user
import tmdbsimple as tmdb
from .models import User, Title, Saved
from . import db
import datetime

from api_key import API_KEY

main_app = Blueprint('reminder', __name__)
tmdb.API_KEY = API_KEY
tmdb.REQUESTS_TIMEOUT = 5


@main_app.route('/', methods=['GET', 'POST'])
def home():
    try:
        user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    except AttributeError:
        user = None

    field_value = ''
    search = None

    if request.method == 'POST':
        search = tmdb.Search()
        response = search.tv(query=request.form.get('user_search'))

        for title in search.results:
            if not title.get('poster_path'):
                title['poster_path'] = 'https://i.ibb.co/7QtVShm/no-image.jpg'
            else:
                title['poster_path'] = 'https://image.tmdb.org/t/p/w300/' + title.get('poster_path')

            # here we're getting the full TV Series info using its id
            full_info = tmdb.TV(title.get('id'))
            full_response = full_info.info()
            title['in_production'] = full_response.get('in_production')

            if not title['in_production']:
                last_season_id = None
                air_dates = None
            else:
                last_season_id = max([season['season_number'] for season in full_response.get('seasons')])
                season_info = tmdb.TV_Seasons(title.get('id'), last_season_id).info()
                air_dates = []

                for episode in season_info.get('episodes'):
                    air_dates.append(datetime.datetime.strptime(episode.get('air_date'), '%Y-%m-%d'))
            title['last_season_id'] = last_season_id
            title['air_dates'] = air_dates

    return render_template('home.html',
                           field_value=field_value,
                           search=search,
                           user=user,
                           flash=flash,
                           enumerate=enumerate)


@main_app.route('/profile')
@login_required
def profile():
    # saved_titles = db.session.query(Saved).filter_by(user_id=current_user.user_id)
    # titles_info = []
    # for title in saved_titles:
    #     full_info = tmdb.TV(title.tmdb_id)
    #     full_response = full_info.info()
    # , saved_titles = saved_titles
    return render_template('profile.html', name=current_user.name)


@main_app.route('/save', methods=['POST'])
@login_required
def save_action():
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title = db.session.query(Title).filter_by(tmdb_id=request.form.get('tmdb_id')).first()
    # print(request.data.get('tmdb_id'))
    if not title:
        title = Title(tmdb_id=request.form.get('tmdb_id'),
                      poster_path=request.form.get('poster_path'),
                      name=request.form.get('name'),
                      year=request.form.get('year'),
                      overview=request.form.get('overview'),
                      in_production=0 if request.form.get('in_production') is False else 1,
                      air_dates=request.form.get('air_dates')
                      )
        db.session.add(title)

    action = request.form.get('action')

    if action.lower() == 'save':
        user.save_title(title.tmdb_id)
        db.session.commit()
    if action.lower() == 'delete':
        user.delete_title(title.tmdb_id)
        db.session.commit()
    else:
        return abort(404)

