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
    user_search = ''
    search = None

    if request.method == 'POST':
        if not user_search:
            user_search = request.form.get('user_search')
        search = tmdb.Search()
        response = search.tv(query=user_search)

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
            title['tmdb_id'] = title.get('id')
            title['year'] = title.get('first_air_date')
            title['last_season_id'] = last_season_id
            title['air_dates'] = air_dates

    return render_template('home.html',
                           user_search=user_search,
                           search=search,
                           user=user,
                           flash=flash,
                           enumerate=enumerate)


@main_app.route('/profile')
@login_required
def profile():
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()

    saved_titles = db.session.query(Title).join(Saved).filter(Saved.user_id == current_user.user_id).filter(Title.tmdb_id == Saved.tmdb_id).all()
    titles_list = []
    for title in saved_titles:
        info_dict = dict()
        info_dict['tmdb_id'] = title.tmdb_id
        info_dict['poster_path'] = title.poster_path
        info_dict['name'] = title.name
        info_dict['year'] = title.year
        info_dict['overview'] = title.overview
        info_dict['in_production'] = title.in_production
        info_dict['air_dates'] = title.air_dates
        titles_list.append(info_dict)

    return render_template('profile.html', name=current_user.name, titles_list=titles_list, user=user)


@main_app.route('/data_operation', methods=['GET', 'PUT'])
@login_required
def save_action():
    if request.method == 'GET':
        return '', 200

    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title = db.session.query(Title).filter_by(tmdb_id=request.form.get('tmdb_id')).first()
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

    return '', 200


@main_app.route('/render_card/', methods=['GET'])
@login_required
def render_card():
    tmdb_id = request.args.get('tmdb_id')
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title = db.session.query(Title).filter_by(tmdb_id=tmdb_id).first()
    title_dict = dict()
    title_dict['tmdb_id'] = title.tmdb_id
    title_dict['poster_path'] = title.poster_path
    title_dict['name'] = title.name
    title_dict['year'] = title.year
    title_dict['overview'] = title.overview
    title_dict['in_production'] = title.in_production
    title_dict['air_dates'] = title.air_dates
    return render_template('title_card.html', user=user, title=title_dict)
