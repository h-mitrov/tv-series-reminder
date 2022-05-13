import datetime
import tmdbsimple as tmdb
from api_key import API_KEY

tmdb.API_KEY = API_KEY
tmdb.REQUESTS_TIMEOUT = 5

info = tmdb.TV(615).credits()

print(info)
#
# season_info = tmdb.TV_Seasons(615, 1)
# air_dates = []
#
#
# for episode in season_info['episodes']:
#     air_dates.append(datetime.datetime.strptime(episode['air_date'], '%Y-%m-%d'))
#
# print(air_dates)
#
#
#
# #
# print(datetime.datetime.strptime('2020-02-02', '%Y-%m-%d'))
#
