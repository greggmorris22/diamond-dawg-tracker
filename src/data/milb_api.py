"""
MLB Stats API helpers for fetching game logs and season stats.
Covers both MiLB and MLB levels so Diamond Dawg Tracker can show
active players at every level.
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


def format_hitting_stats(splits: list, season_stat: dict) -> pd.DataFrame:
    """Format the 7 most recent game logs + a season total row for a hitter."""
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]
    recent_7.reverse()  # chronological order

    rows = []
    for game in recent_7:
        s = game.get('stat', {})
        t = game.get('team', {}).get('name', 'UNK')
        o = game.get('opponent', {}).get('name', 'UNK')
        lvl = game.get('sport', {}).get('abbreviation', 'UNK')
        date_short = game.get('date', '')[5:]
        game_pk = game.get('game', {}).get('gamePk')

        if "River Cats" in t: t = "SAC"
        elif "Chihuahuas" in o: o = "ELP"
        elif "Chihuahuas" in t: t = "ELP"
        elif "River Cats" in o: o = "SAC"

        date_value = _savant_url(game_pk, date_short) if game_pk else date_short

        rows.append({
            "Date": date_value,
            "Lvl": lvl,
            "Team": t,
            "OPP": f"vs {o}" if game.get('isHome') else f"@ {o}",
            "AB":  s.get('atBats', 0),
            "R":   s.get('runs', 0),
            "H":   s.get('hits', 0),
            "TB":  s.get('totalBases', 0),
            "2B":  s.get('doubles', 0),
            "3B":  s.get('triples', 0),
            "HR":  s.get('homeRuns', 0),
            "RBI": s.get('rbi', 0),
            "BB":  s.get('baseOnBalls', 0),
            "IBB": s.get('intentionalWalks', 0),
            "SO":  s.get('strikeOuts', 0),
            "SB":  s.get('stolenBases', 0),
            "CS":  s.get('caughtStealing', 0),
            "AVG": s.get('avg', '.000'),
            "OBP": s.get('obp', '.000'),
            "SLG": s.get('slg', '.000'),
            "HBP": s.get('hitByPitch', 0),
            "SAC": s.get('sacBunts', 0),
            "SF":  s.get('sacFlies', 0),
        })

    s = season_stat if season_stat else {}
    rows.append({
        "Date": "", "Lvl": "-", "Team": "-", "OPP": "-",
        "AB": s.get('atBats', 0), "R": s.get('runs', 0), "H": s.get('hits', 0),
        "TB": s.get('totalBases', 0), "2B": s.get('doubles', 0), "3B": s.get('triples', 0),
        "HR": s.get('homeRuns', 0), "RBI": s.get('rbi', 0), "BB": s.get('baseOnBalls', 0),
        "IBB": s.get('intentionalWalks', 0), "SO": s.get('strikeOuts', 0),
        "SB": s.get('stolenBases', 0), "CS": s.get('caughtStealing', 0),
        "AVG": s.get('avg', '.000'), "OBP": s.get('obp', '.000'), "SLG": s.get('slg', '.000'),
        "HBP": s.get('hitByPitch', 0), "SAC": s.get('sacBunts', 0), "SF": s.get('sacFlies', 0),
    })
    return pd.DataFrame(rows)


def format_pitching_stats(splits: list, season_stat: dict) -> pd.DataFrame:
    """Format the 7 most recent game logs + a season total row for a pitcher."""
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]
    recent_7.reverse()

    rows = []
    for game in recent_7:
        s = game.get('stat', {})
        t = game.get('team', {}).get('name', 'UNK')
        o = game.get('opponent', {}).get('name', 'UNK')
        lvl = game.get('sport', {}).get('abbreviation', 'UNK')
        date_short = game.get('date', '')[5:]
        game_pk = game.get('game', {}).get('gamePk')

        date_value = _savant_url(game_pk, date_short) if game_pk else date_short

        rows.append({
            "Date": date_value,
            "Lvl": lvl,
            "Team": t,
            "OPP": f"vs {o}" if game.get('isHome') else f"@ {o}",
            "W":    s.get('wins', 0),
            "L":    s.get('losses', 0),
            "ERA":  s.get('era', '0.00'),
            "G":    s.get('gamesPlayed', 0),
            "GS":   s.get('gamesStarted', 0),
            "CG":   s.get('completeGames', 0),
            "SHO":  s.get('shutouts', 0),
            "SV":   s.get('saves', 0),
            "SVO":  s.get('saveOpportunities', 0),
            "IP":   s.get('inningsPitched', '0.0'),
            "H":    s.get('hits', 0),
            "R":    s.get('runs', 0),
            "ER":   s.get('earnedRuns', 0),
            "HR":   s.get('homeRuns', 0),
            "HB":   s.get('hitBatsmen', 0),
            "BB":   s.get('baseOnBalls', 0),
            "IBB":  s.get('intentionalWalks', 0),
            "SO":   s.get('strikeOuts', 0),
            "NP-S": f"{s.get('numberOfPitches', 0)}-{s.get('strikes', 0)}",
            "AVG":  s.get('avg', '.000'),
            "WHIP": s.get('whip', '0.00'),
        })

    s = season_stat if season_stat else {}
    rows.append({
        "Date": "", "Lvl": "-", "Team": "-", "OPP": "-",
        "W": s.get('wins', 0), "L": s.get('losses', 0), "ERA": s.get('era', '0.00'),
        "G": s.get('gamesPlayed', 0), "GS": s.get('gamesStarted', 0),
        "CG": s.get('completeGames', 0), "SHO": s.get('shutouts', 0),
        "SV": s.get('saves', 0), "SVO": s.get('saveOpportunities', 0),
        "IP": s.get('inningsPitched', '0.0'), "H": s.get('hits', 0),
        "R": s.get('runs', 0), "ER": s.get('earnedRuns', 0), "HR": s.get('homeRuns', 0),
        "HB": s.get('hitBatsmen', 0), "BB": s.get('baseOnBalls', 0),
        "IBB": s.get('intentionalWalks', 0), "SO": s.get('strikeOuts', 0),
        "NP-S": f"{s.get('numberOfPitches', 0)}-{s.get('strikes', 0)}",
        "AVG": s.get('avg', '.000'), "WHIP": s.get('whip', '0.00'),
    })
    return pd.DataFrame(rows)


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

    Returns (df, current_level) where current_level is the sport abbreviation
    of the player's most recent game (used for sorting in the app).
    Returns (None, None) if the player has no 2026 regular-season stats.

    sport_ids:
        1  = MLB
        11 = AAA, 12 = AA, 13 = A+, 14 = A,
        15 = Rookie Complex, 16 = DSL, 17 = VSL
    """
    profile_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
    profile = fetch_stats(profile_url)
    if not profile or not profile.get('people'):
        return None, None

    pos_code = profile['people'][0].get('primaryPosition', {}).get('code', '')
    is_pitcher = (pos_code == '1')
    group = "pitching" if is_pitcher else "hitting"
    year = 2026
    sport_ids = [1, 11, 12, 13, 14, 15, 16, 17]

    def fetch_level(sid):
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
                        ab = new_stat.get('atBats', 0)
                        ip = new_stat.get('inningsPitched', '0.0')
                        if ab > best_season_stat.get('atBats', 0) or ip > best_season_stat.get('inningsPitched', '0.0'):
                            best_season_stat = new_stat

    if not all_splits:
        return None, None

    # Determine current level from the most recent game
    all_splits.sort(key=lambda x: x['date'], reverse=True)
    current_level = all_splits[0].get('sport', {}).get('abbreviation', 'UNK')

    if is_pitcher:
        return format_pitching_stats(all_splits, best_season_stat), current_level
    else:
        return format_hitting_stats(all_splits, best_season_stat), current_level
