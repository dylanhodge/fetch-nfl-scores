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


def get_teams_info(team1_dict: dict, team2_dict: dict, odds_dict: dict):
    team1_score_response = get_api_response(team1_dict["score"]["$ref"])
    team2_score_response = get_api_response(team2_dict["score"]["$ref"])
    team1_is_home = team1_dict["homeAway"] == "home"
    team2_is_home = team2_dict["homeAway"] == "home"
    team1_team_response = get_api_response(team1_dict["team"]["$ref"])
    team2_team_response = get_api_response(team2_dict["team"]["$ref"])

    caesars_odds = find_caesars(odds_dict["items"])

    if caesars_odds is not None:
        home_team_odds = caesars_odds["homeTeamOdds"]
        away_team_odds = caesars_odds["awayTeamOdds"]

        try:
            team1_money_line = home_team_odds["moneyLine"] if team1_is_home else away_team_odds["moneyLine"]
            team2_money_line = home_team_odds["moneyLine"] if team2_is_home else away_team_odds["moneyLine"]
        except KeyError:
            team1_money_line = ""
            team2_money_line = ""
    else:
        team1_money_line = ""
        team2_money_line = ""

    team1 = Team(
        team1_team_response["displayName"],
        team1_team_response["abbreviation"],
        team1_score_response["displayValue"],
        team1_team_response["logos"][0]["href"],
        get_record_info(team1_team_response["record"]["$ref"]),
        team1_money_line
    )

    team2 = Team(
        team2_team_response["displayName"],
        team2_team_response["abbreviation"],
        team2_score_response["displayValue"],
        team2_team_response["logos"][0]["href"],
        get_record_info(team2_team_response["record"]["$ref"]),
        team2_money_line
    )

    return [
        team1 if team1_is_home else team2,
        team2 if team1_is_home else team1
    ]


def get_week_info(season: int, season_type: int, week_num: int):
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
            try:
                caesars = find_caesars(odds_response["items"])
                if caesars is not None:
                    spread = find_caesars(odds_response["items"])["details"]
                else:
                    spread = ""
            except KeyError:
                spread = ""
            broadcast_response = get_api_response(competition["broadcasts"]["$ref"])
            channels = [station["station"] for station in broadcast_response["items"]]
            week_games.append(Game(teams_info[0], teams_info[1], game_start, spread, channels))
        except KeyError as e:
            print(item["$ref"])
            print(e)
            exit(1)
    week = Week(season, season_type, week_num, week_games)
    weeks_directory = f'api/seasons/{season}/weeks'
    if not os.path.exists(weeks_directory):
        os.makedirs(f'api/seasons/{season}/weeks')
    with open(f'api/seasons/{season}/weeks/{str(week_num).zfill(2)}.json', 'w') as f:
        json.dump(json.loads(jsonpickle.encode(week)), f)


if __name__ == '__main__':
    get_api_response.counter = 0
    start_time = time.perf_counter()
    for x in range(1, 19):
        get_week_info(2022, 2, x)
    end_time = time.perf_counter()
    print(f"Gathered season data in {end_time - start_time} seconds")
    print(f"{get_api_response.counter} API calls were made")
