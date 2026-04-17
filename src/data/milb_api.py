"""
MLB Stats API helpers for fetching game logs and season stats.
Covers both MiLB and MLB levels so Diamond Dawg Tracker can show
active players at every level.
"""

import urllib.request
import json
import pandas as pd
import concurrent.futures
import streamlit as st


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


def format_hitting_game_logs(splits: list) -> pd.DataFrame:
    """Format the 7 most recent game logs for a hitter."""
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]

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
    return pd.DataFrame(rows)


def format_pitching_game_logs(splits: list) -> pd.DataFrame:
    """Format the 7 most recent game logs for a pitcher."""
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]

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
    return pd.DataFrame(rows)


def format_hitting_season_stats(s: dict) -> pd.DataFrame:
    """Format the advanced season stats for a hitter."""
    # Hitters: PA, BB%, K%, AVG, OBP, SLG, ISO, BABIP, HR, R, RBI, SB
    pa = s.get('plateAppearances', 0)
    bb = s.get('baseOnBalls', 0)
    so = s.get('strikeOuts', 0)
    h = s.get('hits', 0)
    hr = s.get('homeRuns', 0)
    ab = s.get('atBats', 0)
    sf = s.get('sacFlies', 0)
    
    if pa == 0:
        pa = ab + bb + s.get('hitByPitch', 0) + sf + s.get('sacBunts', 0)

    bb_pct = f"{(bb / pa * 100):.1f}%" if pa > 0 else "0.0%"
    k_pct = f"{(so / pa * 100):.1f}%" if pa > 0 else "0.0%"
    
    avg = s.get('avg', '.000')
    obp = s.get('obp', '.000')
    slg = s.get('slg', '.000')
    
    try:
        iso_val = float(slg) - float(avg)
        iso = f"{iso_val:.3f}".lstrip('0')
        if iso.startswith('-'):
            iso = '.000'
    except ValueError:
        iso = ".000"
        
    babip = s.get('babip', '.000')
    if babip == '.000' and (ab - so - hr + sf) > 0:
        babip_val = (h - hr) / (ab - so - hr + sf)
        babip = f"{babip_val:.3f}".lstrip('0')

    row = {
        "PA": pa,
        "BB%": bb_pct,
        "K%": k_pct,
        "AVG": avg,
        "OBP": obp,
        "SLG": slg,
        "ISO": iso,
        "BABIP": babip,
        "HR": hr,
        "R": s.get('runs', 0),
        "RBI": s.get('rbi', 0),
        "SB": s.get('stolenBases', 0)
    }
    return pd.DataFrame([row])


def format_pitching_season_stats(s: dict) -> pd.DataFrame:
    """Format the advanced season stats for a pitcher."""
    # Pitchers: IP, K, K%, BB%, K-BB%, WHIP, ERA, FIP, AVG, BABIP, LOB%
    ip = s.get('inningsPitched', '0.0')
    bfp = s.get('battersFaced', 0)
    so = s.get('strikeOuts', 0)
    bb = s.get('baseOnBalls', 0)
    hr = s.get('homeRuns', 0)
    hbp = s.get('hitBatsmen', 0)
    h = s.get('hits', 0)
    r = s.get('runs', 0)
    ab = s.get('atBats', 0)
    sf = s.get('sacFlies', 0)

    # Calculate IP float (e.g. 1.1 -> 1.333)
    try:
        ip_parts = str(ip).split('.')
        ip_float = int(ip_parts[0]) + (int(ip_parts[1]) / 3.0 if len(ip_parts)>1 else 0)
    except ValueError:
        ip_float = 0.0

    k_pct_val = (so / bfp * 100) if bfp > 0 else 0
    bb_pct_val = (bb / bfp * 100) if bfp > 0 else 0
    k_minus_bb_val = k_pct_val - bb_pct_val

    k_pct = f"{k_pct_val:.1f}%"
    bb_pct = f"{bb_pct_val:.1f}%"
    k_minus_bb = f"{k_minus_bb_val:.1f}%"
    
    # FIP
    fip = "0.00"
    if ip_float > 0:
        fip_val = ((13 * hr + 3 * (bb + hbp) - 2 * so) / ip_float) + 3.20
        fip = f"{fip_val:.2f}"
        
    # BABIP
    babip = ".000"
    babip_denom = ab - so - hr + sf
    if babip_denom > 0:
        babip_val = (h - hr) / babip_denom
        babip = f"{babip_val:.3f}".lstrip('0')
        
    # LOB%
    lob = "0.0%"
    lob_denom = h + bb + hbp - 1.4 * hr
    if lob_denom > 0:
        lob_val = (h + bb + hbp - r) / lob_denom
        lob = f"{(lob_val * 100):.1f}%"

    row = {
        "IP": ip,
        "K": so,
        "K%": k_pct,
        "BB%": bb_pct,
        "K-BB%": k_minus_bb,
        "WHIP": s.get('whip', '0.00'),
        "ERA": s.get('era', '0.00'),
        "FIP": fip,
        "AVG": s.get('avg', '.000'),
        "BABIP": babip,
        "LOB%": lob
    }
    return pd.DataFrame([row])


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


@st.cache_data(ttl=3600)
def get_stats(player_id: int) -> tuple:
    """
    Fetch 2026 regular-season game logs and season stats for the given player.
    Returns (game_log_df, season_stats_df, current_level, is_pitcher).
    """
    profile_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
    profile = fetch_stats(profile_url)
    if not profile or not profile.get('people'):
        return None, None, None, None

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
                        # Find the stat block with the most PA/IP
                        ab = new_stat.get('atBats', 0)
                        ip = new_stat.get('inningsPitched', '0.0')
                        
                        try:
                            ip_parts = str(ip).split('.')
                            ip_float = int(ip_parts[0]) + (int(ip_parts[1]) / 3.0 if len(ip_parts)>1 else 0)
                        except: ip_float = 0
                        
                        try:
                            best_ip_parts = str(best_season_stat.get('inningsPitched', '0.0')).split('.')
                            best_ip_float = int(best_ip_parts[0]) + (int(best_ip_parts[1]) / 3.0 if len(best_ip_parts)>1 else 0)
                        except: best_ip_float = 0

                        if ab > best_season_stat.get('atBats', 0) or ip_float > best_ip_float:
                            best_season_stat = new_stat

    if not all_splits:
        return None, None, None, None

    all_splits.sort(key=lambda x: x['date'], reverse=True)
    current_level = all_splits[0].get('sport', {}).get('abbreviation', 'UNK')

    s_stat = best_season_stat if best_season_stat else {}

    if is_pitcher:
        gl_df = format_pitching_game_logs(all_splits)
        ss_df = format_pitching_season_stats(s_stat)
    else:
        gl_df = format_hitting_game_logs(all_splits)
        ss_df = format_hitting_season_stats(s_stat)

    return gl_df, ss_df, current_level, is_pitcher
