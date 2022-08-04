import datetime


class Game(object):
    def __init__(self, home_team: str, away_team: str, start_time: datetime.datetime, home_score: str = 0, away_score: str = 0):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.start_time = start_time.strftime("%Y-%m-%d %H:%M")


class Week(object):
    def __init__(self, season: int, season_type: int, week_num: int, games=None):
        if games is None:
            games = []
        self.season = season
        self.season_type = season_type
        self.week_num = week_num
        self.games = games
