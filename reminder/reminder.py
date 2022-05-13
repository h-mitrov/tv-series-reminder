from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
from flask_login import login_required, current_user
import tmdbsimple as tmdb
from .models import User, Title
from . import db

main_app = Blueprint('reminder', __name__)
tmdb.API_KEY = '6597f21906b21190e71439495f57b0d2'
tmdb.REQUESTS_TIMEOUT = 5


@main_app.route('/', methods=['GET', 'POST'])
def home():
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
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
            full_info = tmdb.TV(title.get('id'))
            full_response = full_info.info()
            title['in_production'] = full_response.get('in_production')



    return render_template('home.html', field_value=field_value, search=search, user=user)


@main_app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main_app.route('/save/<int:tmdb_id>/<action>')
@login_required
def save_action(tmdb_id=None, action=None):

    # if not request.args:
    #     return abort(404)
    #
    # tmdb_id = request.args.get('tmdb_id')
    # action = request.args.get('action')
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title = db.session.query(Title).filter_by(tmdb_id=tmdb_id).first()

    # return '{}, {}'.format(user, title)

    if not title:
        title = Title(tmdb_id=tmdb_id)
        db.session.add(title)

    if action == 'save':
        user.save_title(title.tmdb_id)
        db.session.commit()
    if action == 'delete':
        user.delete_title(title.tmdb_id)
        db.session.commit()

    return '', 204


