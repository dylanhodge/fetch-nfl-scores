import datetime


class Record(object):
    def __init__(self, wins: int, losses: int, ties: int):
        self.wins = wins
        self.losses = losses
        self.ties = ties


class Team(object):
    def __init__(self, name: str, abbrev: str, score: int, logo: str, record: Record, money_line: str):
        self.name = name
        self.abbrev = abbrev
        self.score = score
        self.logo = logo
        self.record = record
        self.moneyLine = money_line


class Game(object):
    def __init__(self, game_id: str, home_team: Team, away_team: Team, start_time: datetime.datetime, spread: str, is_finished: bool):
        self.id = game_id
        self.homeTeam = home_team
        self.awayTeam = away_team
        self.startTime = int(start_time.timestamp())
        self.spread = spread
        self.finished = is_finished


class Week(object):
    def __init__(self, season: int, season_type: int, week_num: int, games=None):
        if games is None:
            games = []
        self.id = f"season-{season}_week-{week_num}"
        self.season = season
        self.seasonType = season_type
        self.weekNum = week_num
        self.games = games
        games.sort(key=lambda game: game.startTime)
        self.startTime = games[0].startTime
