# Standard library imports
import asyncio

# Third party imports
import aiohttp

# Local application imports
from config import API_KEY
from .models import User, Title, Saved
from . import db


async def discover_title_info(tmdb_id: int) -> dict:
    """
    Async function, that calls the TMDB API for full info about a specific title.
    Returns a dictionary with main title's characteristics: name, year, air dates for the last season, etc.
    """
    title_data = dict()

    # here we're getting the full TV Series info using its id
    async with aiohttp.ClientSession() as session:
        url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={API_KEY}&language=en-US'

        async with session.get(url) as response:
            full_response = await response.json()

    # getting the year and production status
    first_aired = full_response.get('first_air_date')
    title_data['year'] = '({})'.format(first_aired[:4]) if first_aired is not None else ''
    title_data['in_production'] = full_response.get('in_production')

    # if title is in production, it fetches the data about the last season
    # and gets the relevant air dates for every episode
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

    return title_data


async def search_titles(query: str) -> list:
    """
    Async function. Gets a string as an argument, then makes a request to the TMDB API,
    creates a list of unique title ids, then performs a separate request for each of the titles
    in order to get the full info.
    Finally, fetches the search result as a list of titles.
    """
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
    """
    This function gets a specific url to TMDB API, performs a request and fetches the result as a list of titles.
    It is called only from other functions, such as fetch_popular_series(), fetch_top_series(), etc.
    These functions specify the url type.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            full_response = await response.json()

    title_ids = [title.get('id') for title in full_response.get('results')]
    tasks = [asyncio.create_task(discover_title_info(title_id)) for title_id in title_ids]
    all_titles = []
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    for task in tasks:
        # start_time = time.time()
        await task
        all_titles.append(task.result())
        # print(time.time() - start_time)
    return all_titles


def fetch_trending_series(period: str) -> list:
    """
    Fetches trending series. Period could be only 'day' or 'week'.
    """
    query_link = f'https://api.themoviedb.org/3/trending/tv/{period}?api_key={API_KEY}'
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_popular_series() -> list:
    """
        Fetches popular series. Takes no arguments.
    """
    query_link = f'https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&language=en-US&page=1'
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_top_series() -> list:
    """
        Fetches top-rated series. Takes no arguments.
    """
    query_link = f'https://api.themoviedb.org/3/tv/top_rated?api_key={API_KEY}'
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_airing_today() -> list:
    """
        Fetches series airing today. Takes no arguments.
    """
    query_link = f'https://api.themoviedb.org/3/tv/airing_today?api_key={API_KEY}&language=en-US&page=1'
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results


def fetch_airing_this_week() -> list:
    """
        Fetches series airing this week. Takes no arguments.
    """
    query_link = f'https://api.themoviedb.org/3/tv/on_the_air?api_key={API_KEY}&language=en-US&page=1'
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(fetch_series(query_link))
    return results
