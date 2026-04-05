"""
MLB Stats API helpers for fetching game logs and season stats.
Covers both MiLB and MLB levels so Diamond Dawg Tracker can show
active players at every level.

Each public function returns separate season-totals and recent-games
DataFrames so the app can display them in distinct labeled sections,
along with player profile info (team, age, position).
"""

import urllib.request
import json
import pandas as pd
import concurrent.futures


def fetch_stats(url: str):
    """Fetch JSON from a URL, returning None on any error."""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except Exception:
        return None


def _savant_url(game_pk: int, date_short: str) -> str:
    """
    Build a Baseball Savant gamefeed URL with the short date (MM-DD) embedded
    as a query param so Streamlit's LinkColumn regex can extract it for display.
    """
    return f"https://baseballsavant.mlb.com/gamefeed?gamePk={game_pk}&d={date_short}"


def _team_abbrev(team_obj: dict) -> str:
    """
    Extract a short team label from a team object in a game log split.
    Tries the abbreviation field first; falls back to the full name.
    Applies manual overrides for long MiLB team names that have no abbreviation.
    """
    abbrev = team_obj.get('abbreviation') or team_obj.get('name', 'UNK')
    # Manual overrides for teams where the API returns the full name
    overrides = {
        'Sacramento River Cats': 'SAC',
        'El Paso Chihuahuas': 'ELP',
    }
    return overrides.get(abbrev, abbrev)


def format_hitting_stats(splits: list, season_stat: dict) -> tuple:
    """
    Format hitting data into two separate DataFrames.

    Returns:
        season_df  -- one-row DataFrame of 2026 season totals
                      (GP, AB, R, H, 2B, 3B, HR, RBI, BB, SO, SB, CS,
                       AVG, OBP, SLG, OPS)
        games_df   -- DataFrame of the 7 most recent games in chronological
                      order (Date linked to Savant, Team, Opp, Result, and
                      per-game slash-line stats)
    """
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]
    recent_7.reverse()  # chronological order for display

    rows = []
    for game in recent_7:
        s = game.get('stat', {})
        t = _team_abbrev(game.get('team', {}))
        o = _team_abbrev(game.get('opponent', {}))
        date_short = game.get('date', '')[5:]   # "YYYY-MM-DD" -> "MM-DD"
        game_pk = game.get('game', {}).get('gamePk')

        # isWin reflects whether the player's team won the game
        is_win = game.get('isWin')
        result = "W" if is_win is True else ("L" if is_win is False else "")

        home_away = "vs" if game.get('isHome') else "@"
        date_value = _savant_url(game_pk, date_short) if game_pk else date_short

        rows.append({
            "Date":   date_value,
            "Team":   t,
            "Opp":    f"{home_away} {o}",
            "Result": result,
            "AB":     s.get('atBats', 0),
            "R":      s.get('runs', 0),
            "H":      s.get('hits', 0),
            "2B":     s.get('doubles', 0),
            "3B":     s.get('triples', 0),
            "HR":     s.get('homeRuns', 0),
            "RBI":    s.get('rbi', 0),
            "BB":     s.get('baseOnBalls', 0),
            "SO":     s.get('strikeOuts', 0),
            "SB":     s.get('stolenBases', 0),
            "CS":     s.get('caughtStealing', 0),
            "AVG":    s.get('avg', '.000'),
            "OBP":    s.get('obp', '.000'),
            "SLG":    s.get('slg', '.000'),
        })

    games_df = pd.DataFrame(rows)

    # Season totals — compute OPS from API field if available, otherwise
    # derive it from OBP + SLG to avoid a separate endpoint call.
    s = season_stat if season_stat else {}
    obp_str = s.get('obp', '.000')
    slg_str = s.get('slg', '.000')
    ops_val = s.get('ops')
    if ops_val is None:
        try:
            ops_val = f"{float(obp_str) + float(slg_str):.3f}"
        except (ValueError, TypeError):
            ops_val = '.000'

    season_df = pd.DataFrame([{
        "GP":  s.get('gamesPlayed', 0),
        "AB":  s.get('atBats', 0),
        "R":   s.get('runs', 0),
        "H":   s.get('hits', 0),
        "2B":  s.get('doubles', 0),
        "3B":  s.get('triples', 0),
        "HR":  s.get('homeRuns', 0),
        "RBI": s.get('rbi', 0),
        "BB":  s.get('baseOnBalls', 0),
        "SO":  s.get('strikeOuts', 0),
        "SB":  s.get('stolenBases', 0),
        "CS":  s.get('caughtStealing', 0),
        "AVG": s.get('avg', '.000'),
        "OBP": obp_str,
        "SLG": slg_str,
        "OPS": ops_val,
    }])

    return season_df, games_df


def format_pitching_stats(splits: list, season_stat: dict) -> tuple:
    """
    Format pitching data into two separate DataFrames.

    Returns:
        season_df  -- one-row DataFrame of 2026 season totals
                      (G, GS, W, L, ERA, IP, H, R, ER, HR, BB, SO, WHIP)
        games_df   -- DataFrame of the 7 most recent appearances in
                      chronological order
    """
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]
    recent_7.reverse()

    rows = []
    for game in recent_7:
        s = game.get('stat', {})
        t = _team_abbrev(game.get('team', {}))
        o = _team_abbrev(game.get('opponent', {}))
        date_short = game.get('date', '')[5:]
        game_pk = game.get('game', {}).get('gamePk')

        is_win = game.get('isWin')
        result = "W" if is_win is True else ("L" if is_win is False else "")

        home_away = "vs" if game.get('isHome') else "@"
        date_value = _savant_url(game_pk, date_short) if game_pk else date_short

        rows.append({
            "Date":   date_value,
            "Team":   t,
            "Opp":    f"{home_away} {o}",
            "Result": result,
            "W":      s.get('wins', 0),
            "L":      s.get('losses', 0),
            "IP":     s.get('inningsPitched', '0.0'),
            "H":      s.get('hits', 0),
            "R":      s.get('runs', 0),
            "ER":     s.get('earnedRuns', 0),
            "HR":     s.get('homeRuns', 0),
            "BB":     s.get('baseOnBalls', 0),
            "SO":     s.get('strikeOuts', 0),
            "NP-S":   f"{s.get('numberOfPitches', 0)}-{s.get('strikes', 0)}",
            "ERA":    s.get('era', '0.00'),
            "WHIP":   s.get('whip', '0.00'),
        })

    games_df = pd.DataFrame(rows)

    s = season_stat if season_stat else {}
    season_df = pd.DataFrame([{
        "G":    s.get('gamesPlayed', 0),
        "GS":   s.get('gamesStarted', 0),
        "W":    s.get('wins', 0),
        "L":    s.get('losses', 0),
        "SV":   s.get('saves', 0),
        "ERA":  s.get('era', '0.00'),
        "IP":   s.get('inningsPitched', '0.0'),
        "H":    s.get('hits', 0),
        "R":    s.get('runs', 0),
        "ER":   s.get('earnedRuns', 0),
        "HR":   s.get('homeRuns', 0),
        "BB":   s.get('baseOnBalls', 0),
        "SO":   s.get('strikeOuts', 0),
        "WHIP": s.get('whip', '0.00'),
    }])

    return season_df, games_df


# Priority order for display: MLB first, then down through the minors.
# The Lvl abbreviations come from sport.abbreviation in the API response.
LEVEL_ORDER = {
    "MLB": 0,
    "AAA": 1,
    "AA":  2,
    "A+":  3,
    "A":   4,
    "Rk":  5,
    "DSL": 6,
    "VSL": 7,
}


def get_stats(player_id: int) -> tuple:
    """
    Fetch 2026 regular-season game logs and season stats for the given player.
    Covers MLB (sportId=1) and all MiLB levels (11-17).

    Returns a 6-tuple:
        (season_df, games_df, current_level, team_abbrev, age, position)

    Where:
        season_df     -- one-row season-totals DataFrame (or None)
        games_df      -- recent-games DataFrame (or None)
        current_level -- sport abbreviation of the most recent game
        team_abbrev   -- player's current team abbreviation from their profile
        age           -- player's current age
        position      -- player's primary position abbreviation (C, SS, P, etc.)

    Returns (None, None, None, None, None, None) if the player has no 2026
    regular-season stats.

    sport_ids:
        1  = MLB
        11 = AAA, 12 = AA, 13 = A+, 14 = A,
        15 = Rookie Complex, 16 = DSL, 17 = VSL
    """
    profile_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
    profile = fetch_stats(profile_url)
    if not profile or not profile.get('people'):
        return None, None, None, None, None, None

    person = profile['people'][0]
    pos_code   = person.get('primaryPosition', {}).get('code', '')
    position   = person.get('primaryPosition', {}).get('abbreviation', 'UNK')
    age        = person.get('currentAge', 'UNK')
    team_abbrev = person.get('currentTeam', {}).get('abbreviation', 'UNK')

    is_pitcher = (pos_code == '1')
    group = "pitching" if is_pitcher else "hitting"
    year = 2026
    sport_ids = [1, 11, 12, 13, 14, 15, 16, 17]

    def fetch_level(sid):
        """Fetch game log and season stats for one sport level."""
        url = (
            f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
            f"?stats=gameLog,season&group={group}&season={year}"
            f"&gameType=R&sportId={sid}"
        )
        return fetch_stats(url)

    all_splits = []
    best_season_stat = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_level, sid): sid for sid in sport_ids}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res and res.get('stats'):
                for block in res['stats']:
                    if block['type']['displayName'] == 'gameLog' and block.get('splits'):
                        all_splits.extend(block['splits'])
                    elif block['type']['displayName'] == 'season' and block.get('splits'):
                        new_stat = block['splits'][0].get('stat', {})
                        ab  = new_stat.get('atBats', 0)
                        ip  = new_stat.get('inningsPitched', '0.0')
                        if (ab > best_season_stat.get('atBats', 0)
                                or ip > best_season_stat.get('inningsPitched', '0.0')):
                            best_season_stat = new_stat

    if not all_splits:
        return None, None, None, None, None, None

    # Determine the player's current level from their most recent game
    all_splits.sort(key=lambda x: x['date'], reverse=True)
    current_level = all_splits[0].get('sport', {}).get('abbreviation', 'UNK')

    if is_pitcher:
        season_df, games_df = format_pitching_stats(all_splits, best_season_stat)
    else:
        season_df, games_df = format_hitting_stats(all_splits, best_season_stat)

    return season_df, games_df, current_level, team_abbrev, age, position
