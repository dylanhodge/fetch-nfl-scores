import datetime


class Record(object):
    def __init__(self, wins: int, losses: int, ties: int):
        self.wins = wins
        self.losses = losses
        self.ties = ties


class Team(object):
    def __init__(self, name: str, abbrev: str, score: str, logo: str, record: Record, moneyline: str):
        self.name = name
        self.abbrev = abbrev
        self.score = score
        self.logo = logo
        self.record = record
        self.moneyline = moneyline


class Game(object):
    def __init__(self, home_team: Team, away_team: Team, start_time: datetime.datetime, spread: str, channels: list):
        self.homeTeam = home_team
        self.awayTeam = away_team
        self.start_time = start_time.strftime("%Y-%m-%d %H:%M")
        self.spread = spread
        self.channels = channels


class Week(object):
    def __init__(self, season: int, season_type: int, week_num: int, games=None):
        if games is None:
            games = []
        self.season = season
        self.season_type = season_type
        self.week_num = week_num
        self.games = games
