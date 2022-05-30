import asyncio
import time
from flask import render_template, request, redirect, url_for, flash, abort, session, Blueprint
from flask_login import login_required, current_user

import aiohttp

from .models import User, Title, Saved
from . import db
from config import API_KEY


main_app = Blueprint('reminder', __name__)


async def discover_title_info(tmdb_id):
    # here we're getting the full TV Series info using its id
    title_data = dict()
    # start_time = time.time()
    async with aiohttp.ClientSession() as session:
        url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={API_KEY}&language=en-US'

        async with session.get(url) as response:
            full_response = await response.json()

    first_aired = full_response.get('first_air_date')
    title_data['year'] = '({})'.format(first_aired[:4]) if first_aired is not None else ''
    title_data['in_production'] = full_response.get('in_production')

    if not title_data['in_production']:
        last_season_id = None
        title_data['air_dates'] = None
    else:
        last_season_id = max([season['season_number'] for season in full_response.get('seasons')])

        async with aiohttp.ClientSession() as session:
            url = f'https://api.themoviedb.org/3/tv/{tmdb_id}/season/{last_season_id}?api_key={API_KEY}&language=en-US'

            async with session.get(url) as response:
                season_info = await response.json()

        air_dates = []
        episodes = season_info.get('episodes')
        if episodes is not None:
            for episode in season_info.get('episodes'):
                air_date = episode.get('air_date')
                if air_date is not None:
                    air_dates.append(air_date)
            title_data['air_dates'] = '|'.join(air_dates)

    if full_response.get('poster_path') is None:
        title_data['poster_path'] = 'https://i.ibb.co/5c4VKL3/no-image-1.jpg'
    else:
        title_data['poster_path'] = 'https://image.tmdb.org/t/p/w300_and_h450_bestv2' + full_response.get('poster_path')

    title_data['tmdb_id'] = tmdb_id
    title_data['last_season_id'] = last_season_id
    title_data['name'] = full_response.get('name')
    title_data['overview'] = full_response.get('overview')
    # print(time.time() - start_time)
    return title_data


def unpack_title(title: Title) -> dict:
    title_dict = dict()
    title_dict['tmdb_id'] = title.tmdb_id
    title_dict['poster_path'] = title.poster_path
    title_dict['name'] = title.name
    title_dict['year'] = title.year
    title_dict['overview'] = title.overview
    title_dict['in_production'] = title.in_production
    title_dict['air_dates'] = title.air_dates
    return title_dict


async def search_titles(query: str):
    async with aiohttp.ClientSession() as session:
        url = f'https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&language=en-US&page=1&query={query}' \
              f'&include_adult=false'

        async with session.get(url) as response:
            full_response = await response.json()

    title_ids = [title.get('id') for title in full_response.get('results')]
    tasks = [asyncio.create_task(discover_title_info(title_id)) for title_id in title_ids]
    all_titles = []

    for task in tasks:
        await task
        all_titles.append(task.result())

    return all_titles


async def fetch_series(url: str) -> list:
    """Period could be only 'day' or 'week'"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            full_response = await response.json()

    title_ids = [title.get('id') for title in full_response.get('results')]
    tasks = [asyncio.create_task(discover_title_info(title_id)) for title_id in title_ids]
    all_titles = []
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    for task in tasks:
        # start_time = time.time()
        await task
        all_titles.append(task.result())
        # print(time.time() - start_time)
    return all_titles


def fetch_trending_series(period: str) -> list:
    query_link = f'https://api.themoviedb.org/3/trending/tv/{period}?api_key={API_KEY}'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_popular_series() -> list:
    query_link = f'https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&language=en-US&page=1'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_top_series() -> list:
    query_link = f'https://api.themoviedb.org/3/tv/top_rated?api_key={API_KEY}'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_airing_today() -> list:
    query_link = f'https://api.themoviedb.org/3/tv/airing_today?api_key={API_KEY}&language=en-US&page=1'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_airing_this_week() -> list:
    query_link = f'https://api.themoviedb.org/3/tv/on_the_air?api_key={API_KEY}&language=en-US&page=1'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


@main_app.route('/', methods=['GET', 'POST'])
def home():
    try:
        user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    except AttributeError:
        user = None
    user_search = ''
    results = []
    greeting = ''

    if request.method == 'POST':
        user_search = request.form.get('user_search')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        results = asyncio.run(search_titles(user_search))
        greeting = f"Here are the search results for '{user_search}':"

    if request.method == 'GET':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        results = fetch_trending_series('day')
        greeting = "Trending today:"

    return render_template('home.html',
                           user_search=user_search,
                           results=results,
                           user=user,
                           greeting=greeting,
                           flash=flash)


@main_app.route('/fetch/<string:tv_type>')
def get_results(tv_type):
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
def profile():
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()

    saved_titles = db.session.query(Title).join(Saved).filter(Saved.user_id == current_user.user_id).filter(Title.tmdb_id == Saved.tmdb_id).all()
    titles_list = []
    for title in saved_titles:
        title_dict = unpack_title(title)
        titles_list.append(title_dict)

    return render_template('profile.html', name=current_user.name, titles_list=titles_list, user=user)


@main_app.route('/data_operation', methods=['GET', 'PUT'])
@login_required
def save_action():
    if request.method == 'GET':
        return '', 200

    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()

    action = request.form.get('action')

    if action.lower() == 'save':
        user.save_title(request.form.get('tmdb_id'), full_title_data=request.form)
    if action.lower() == 'delete':
        user.delete_title(request.form.get('tmdb_id'))

    return '', 200


@main_app.route('/render_card/', methods=['GET'])
@login_required
def render_card():
    tmdb_id = request.args.get('tmdb_id')
    user = db.session.query(User).filter_by(user_id=current_user.user_id).first()
    title = db.session.query(Title).filter_by(tmdb_id=tmdb_id).first()
    title_dict = unpack_title(title)
    return render_template('title_card.html', user=user, title=title_dict)
