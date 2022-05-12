from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
from flask_login import login_required, current_user
import tmdbsimple as tmdb
# from .models import User, Title
from . import db

main_app = Blueprint('reminder', __name__)
tmdb.API_KEY = '6597f21906b21190e71439495f57b0d2'
tmdb.REQUESTS_TIMEOUT = 5


@main_app.route('/', methods=['GET', 'POST'])
def home():
    field_value = ''
    search = None

    @login_required
    def render_save_url(cur_title):
        return url_for("like_action")

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
            # print(type(current_user))
            # print()
            # print()
            # print()
            # print()
            # print()
            # # title['link'] = render_save_url(title)
            # # title['saved_status'] = current_user.has_saved_title(title)

    return render_template('home.html', field_value=field_value, search=search)


@main_app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


# @main_app.route('/add/<int:title_id>/<action>')
# @login_required
# def like_action(title_id, action):
#     title = Title.query.filter_by(id=title_id).first_or_404()
#     if action == 'save':
#         current_user.save_title(title)
#         db.session.commit()
#     if action == 'delete':
#         current_user.delete_title(title)
#         db.session.commit()
#     return redirect(request.referrer)


