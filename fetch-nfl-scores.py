import datetime
import time
import json
import os

import jsonpickle

import constants
import requests
from classes import Game, Week, Team, Record


def get_api_response(url: str):
    get_api_response.counter += 1
    api_response = requests.get(url)
    return api_response.json()


def find_wins(stats_list: list):
    for item in stats_list:
        if item["name"] == "Wins":
            return int(item["displayValue"])
    return 0


def find_losses(stats_list: list):
    for item in stats_list:
        if item["name"] == "Losses":
            return int(item["displayValue"])
    return 0


def find_ties(stats_list: list):
    for item in stats_list:
        if item["name"] == "Ties":
            return int(item["displayValue"])
    return 0


def find_caesars(odds_items: list):
    for item in odds_items:
        if item["provider"]["name"] == "Caesars Sportsbook":
            return item
    if len(odds_items) > 0:
        return odds_items[0]
    return None


def get_record_info(url: str):
    record_response = get_api_response(url)
    if len(record_response["items"]) > 0:
        wins = find_wins(record_response["items"][0]["stats"])
        losses = find_losses(record_response["items"][0]["stats"])
        ties = find_ties(record_response["items"][0]["stats"])
        return Record(wins, losses, ties)
    return Record(0, 0, 0)


def get_team_info(team_dict: dict, odds_dict: dict):
    score_response = get_api_response(team_dict["score"]["$ref"])
    team_response = get_api_response(team_dict["team"]["$ref"])
    team_is_home = team_dict["homeAway"] == "home"

    caesars_odds = find_caesars(odds_dict["items"])

    if caesars_odds is not None:
        home_team_odds = caesars_odds["homeTeamOdds"]
        away_team_odds = caesars_odds["awayTeamOdds"]

        try:
            money_line = home_team_odds["moneyLine"] if team_is_home else away_team_odds["moneyLine"]
        except KeyError:
            money_line = ""
    else:
        money_line = ""

    return Team(
        name=team_response["displayName"],
        abbrev=team_response["abbreviation"],
        score=score_response["displayValue"],
        logo=team_response["logos"][0]["href"],
        record=get_record_info(team_response["record"]["$ref"]),
        money_line=money_line
    )


def get_teams_info(team1_dict: dict, team2_dict: dict, odds_dict: dict):
    team1 = get_team_info(team1_dict, odds_dict)
    team2 = get_team_info(team2_dict, odds_dict)

    return [
        team1 if team1_dict["homeAway"] == "home" else team2,
        team2 if team1_dict["homeAway"] == "home" else team1
    ]


def get_week_info(season: int, season_type: int, week_num: int):
    week_info_start_time = time.perf_counter()
    week_info_response = get_api_response(constants.WEEK_EVENTS.format(
        season=str(season),
        season_type=str(season_type),
        week_num=str(week_num)
    ))
    week_games = []
    for item in week_info_response["items"]:
        try:
            game_info_response = get_api_response(item["$ref"])
            competition = game_info_response.get("competitions")[0]
            competitors = competition.get("competitors")
            odds_response = get_api_response(competition["odds"]["$ref"])
            teams_info = get_teams_info(competitors[0], competitors[1], odds_response)
            game_start = datetime.datetime.strptime(game_info_response["date"], "%Y-%m-%dT%H:%MZ")
            caesars = find_caesars(odds_response["items"])
            if caesars is not None:
                spread = find_caesars(odds_response["items"]).get("details", "")
            else:
                spread = ""
            broadcast_response = get_api_response(competition["broadcasts"]["$ref"])
            channels = [station["station"] for station in broadcast_response["items"]]
            week_games.append(Game(
                game_id=game_info_response["id"],
                home_team=teams_info[0],
                away_team=teams_info[1],
                start_time=game_start,
                spread=spread,
                channels=channels,
                is_finished=competition["recapAvailable"]
            ))
        except KeyError as e:
            print(item["$ref"])
            print(e)
            exit(1)
    week = Week(
        season=season,
        season_type=season_type,
        week_num=week_num,
        games=week_games
    )
    weeks_directory = f'api/seasons/{season}/weeks'
    if not os.path.exists(weeks_directory):
        os.makedirs(f'api/seasons/{season}/weeks')
    with open(f'api/seasons/{season}/weeks/{str(week_num).zfill(2)}.json', 'w') as f:
        json.dump(json.loads(jsonpickle.encode(week)), f, indent=2)
    week_info_end_time = time.perf_counter()
    print(f"Gathered week #{week_num} info in {week_info_end_time - week_info_start_time} seconds")


if __name__ == '__main__':
    get_api_response.counter = 0
    start_time = time.perf_counter()
    for x in range(1, 19):
        get_week_info(2022, 2, x)
    end_time = time.perf_counter()
    print(f"Gathered season data in {end_time - start_time} seconds")
    print(f"{get_api_response.counter} API calls were made")
