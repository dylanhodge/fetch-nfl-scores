BASE = 'https://sports.core.api.espn.com'

FOOTBALL = BASE + '/v2/sports/football'
NFL = FOOTBALL + '/leagues/nfl'

SEASONS = NFL + '/seasons/{season}'
SEASON_TYPE = SEASONS + '/types/{season_type}'
EVENTS = NFL + '/events/{event_id}'

WEEKS = SEASON_TYPE + '/weeks'
WEEK_NUM = WEEKS + '/{week_num}'
WEEK_EVENTS = WEEK_NUM + '/events'

COMPETITION = EVENTS + '/competitions/{event_id}'
