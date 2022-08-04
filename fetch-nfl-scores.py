import datetime
import json
import os

import jsonpickle

import constants
import requests
from classes import Game, Week


def get_api_response(url: str):
    api_response = requests.get(url)
    return api_response.json()


def get_week_info(season: int, season_type: int, week_num: int):
    week_info_response = get_api_response(constants.WEEK_EVENTS.format(
        season=str(season),
        season_type=str(season_type),
        week_num=str(week_num)
    ))
    week_games = []
    for item in week_info_response["items"]:
        game_info_response = get_api_response(item["$ref"])
        competition_name = game_info_response["name"]
        competitors = competition_name.split(" at ")
        week_games.append(Game(competitors[1], competitors[0], datetime.datetime.strptime(game_info_response["date"], "%Y-%m-%dT%H:%MZ")))
    week = Week(season, season_type, week_num, week_games)
    weeks_directory = f'api/seasons/{season}/weeks'
    if not os.path.exists(weeks_directory):
        os.makedirs(f'api/seasons/{season}/weeks')
    with open(f'api/seasons/{season}/weeks/{str(week_num).zfill(2)}.json', 'w') as f:
        json.dump(json.loads(jsonpickle.encode(week)), f)


if __name__ == '__main__':
    for x in range(1, 19):
        get_week_info(2022, 2, x)
