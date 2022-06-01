# Standard library imports
import asyncio
import time
from collections.abc import Callable

# Third party imports
from flask import render_template, request, redirect, url_for, flash, abort, session, Blueprint
from flask_login import login_required, current_user

# Local application imports
from .models import User, Title, Saved
from . import db
from .functions import *


main_app = Blueprint('reminder', __name__)


@main_app.route('/', methods=['GET', 'POST'])
def home() -> Callable:
    """ 
    The main function. Calls other functions to render the home page or other specific
    content pages (popular, trending, etc.).
    """
    try:
        user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    except AttributeError:
        user = None
    user_search = ''
    results = []
    greeting = ''

    if request.method == 'POST':
        user_search = request.form.get('user_search')
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        results = asyncio.run(search_titles(user_search))
        greeting = f"Here are the search results for '{user_search}':"

    if request.method == 'GET':
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        results = fetch_trending_series('day')
        greeting = "Trending today:"

    return render_template('home.html',
                           user_search=user_search,
                           results=results,
                           user=user,
                           greeting=greeting,
                           flash=flash)


@main_app.route('/fetch/<string:tv_type>')
def get_results(tv_type: str) -> Callable:
    """ 
    Fetches a list of TV Series and calls a render_template function.
    The contents of the list depend on the argument. 
    """
    
    try:
        user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    except AttributeError:
        user = None
    user_search = ''
    
    if tv_type == 'trending_this_week':
        greeting = "Trending this week:"
        results = fetch_trending_series('week')
        
    elif tv_type == 'trending_today':
        greeting = "Trending today:"
        results = fetch_trending_series('day')
        
    elif tv_type == 'popular':
        greeting = "Popular TV series:"
        results = fetch_popular_series()
        
    elif tv_type == 'on_air':
        greeting = "Airing today:"
        results = fetch_airing_today()
        
    elif tv_type == 'airing_this_week':
        greeting = "Airing this week:"
        results = fetch_airing_this_week()
        
    elif tv_type == 'top_rated':
        greeting = "Top rated TV series:"
        results = fetch_top_series()
        
    else:
        return abort(404)
    
    return render_template('home.html',
                           user_search=user_search,
                           results=results,
                           user=user,
                           greeting=greeting,
                           flash=flash)


@main_app.route('/profile')
@login_required
def profile() -> Callable:
    """ 
    Fetches from database all the saved titles for current user.
    Returns a call to 'render_template' function, which renders the 'Profile' page template.
    """
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title_ids = db.session.query(Saved.tmdb_id).filter_by(user_id=current_user.user_id).all()
    titles_list = [title['tmdb_id'] for title in title_ids]
    saved_titles = db.session.query(Title).filter(Title.tmdb_id.in_(titles_list)).all()

    titles_list = []
    for title in saved_titles:
        title_dict = title.convert_to_dict()
        titles_list.append(title_dict)

    return render_template('profile.html',
                           name=current_user.name,
                           titles_list=titles_list,
                           user=user)


@main_app.route('/data_operation', methods=['GET', 'PUT'])
@login_required
def save_action() -> str:
    """ 
    Saves or deletes a title from 'Saved' table in the database.
    Each save is unique, depending on the current user id.
    """
    if request.method == 'GET':
        return '', 200

    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()

    action = request.form.get('action')

    if action.lower() == 'save':
        user.save_title(request.form.get('tmdb_id'),
                        full_title_data=request.form)
    if action.lower() == 'delete':
        user.delete_title(request.form.get('tmdb_id'))

    return '', 200


@main_app.route('/render_card/', methods=['GET'])
@login_required
def render_card() -> Callable:
    """ 
    Renders a single title card. All needed data is fetched from the database.
    This function is called from the frontend to update the title card every time
    the title was saved or deleted from the database.
    """

    tmdb_id = request.args.get('tmdb_id')
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title = db.session.query(Title).filter_by(tmdb_id=tmdb_id).first()
    title_dict = title.convert_to_dict()
    return render_template('title_card.html',
                           user=user,
                           title=title_dict)
