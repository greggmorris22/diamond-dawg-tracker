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


# ── League-average constants for wRC+ calculation ───────────────────────────
# Approximate 2025 MLB values (FanGraphs). They shift slightly each season;
# update these constants here if precision matters for future years.
_LG_WOBA        = 0.312   # league-average wOBA
_WOBA_SCALE     = 1.157   # wOBA scale factor (converts wOBA to runs above average)
_LG_R_PA        = 0.120   # league runs per plate appearance

# Linear weights for wOBA (2025 FanGraphs values)
_W_UBB  = 0.690   # unintentional walk
_W_HBP  = 0.722   # hit by pitch
_W_1B   = 0.888   # single
_W_2B   = 1.271   # double
_W_3B   = 1.616   # triple
_W_HR   = 2.101   # home run

# FIP constant — shifts slightly each year; 3.10 is a good 2026 approximation.
# True value = lgERA - (13*lgHR + 3*(lgBB+lgHBP) - 2*lgK) / lgIP
_FIP_CONSTANT = 3.10
# ─────────────────────────────────────────────────────────────────────────────


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


def _ip_to_decimal(ip_str) -> float:
    """
    Convert innings pitched string (e.g. '5.1') to decimal innings.
    The MLB Stats API uses the tenths digit to represent outs recorded (not
    actual tenths): .1 = 1 out = 1/3 inning, .2 = 2 outs = 2/3 inning.
    """
    try:
        parts = str(ip_str).split('.')
        innings = int(parts[0])
        outs = int(parts[1]) if len(parts) > 1 else 0
        return innings + outs / 3.0
    except Exception:
        return 0.0


def fetch_game_scores(game_pks: list) -> dict:
    """
    Fetch final scores for a batch of gamePks in a single MLB Schedule API call.

    Returns a dict keyed by gamePk:
        {gamePk: {'home_score': int, 'away_score': int, 'home_winner': bool}}

    The caller resolves team vs. opponent score using isHome from the split.
    """
    if not game_pks:
        return {}
    pks_str = ",".join(str(pk) for pk in game_pks)
    url = f"https://statsapi.mlb.com/api/v1/schedule?gamePks={pks_str}&hydrate=linescore"
    data = fetch_stats(url)
    if not data:
        return {}

    scores = {}
    for date_entry in data.get('dates', []):
        for game in date_entry.get('games', []):
            pk = game.get('gamePk')
            if pk:
                teams      = game.get('teams', {})
                home       = teams.get('home', {})
                away       = teams.get('away', {})
                home_score = home.get('score')
                away_score = away.get('score')
                if home_score is not None and away_score is not None:
                    scores[pk] = {
                        'home_score':  home_score,
                        'away_score':  away_score,
                        'home_winner': home.get('isWinner', False),
                    }
    return scores


def _score_str(game_pk: int, is_home: bool, scores: dict) -> str:
    """
    Format the final score for one game as 'W 5-3' or 'L 2-4'.
    The player's team score is always shown first.
    Returns '-' if score data is unavailable (e.g. game still in progress).
    """
    data = scores.get(game_pk)
    if not data:
        return "-"
    if is_home:
        team_score = data['home_score']
        opp_score  = data['away_score']
        won        = data['home_winner']
    else:
        team_score = data['away_score']
        opp_score  = data['home_score']
        won        = not data['home_winner']
    result = "W" if won else "L"
    return f"{result} {team_score}-{opp_score}"


def format_hitting_stats(splits: list, scores: dict) -> pd.DataFrame:
    """
    Format the 7 most recent game logs for a hitter. Most recent game first.

    Columns: Date, Lvl, Team, Opp, Score, AB, R, H, 2B, 3B, HR, RBI,
             BB, SO, SB, CS, AVG, OBP, SLG
    """
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]  # most recent first

    rows = []
    for game in recent_7:
        s       = game.get('stat', {})
        t       = game.get('team', {}).get('name', 'UNK')
        o       = game.get('opponent', {}).get('name', 'UNK')
        lvl     = game.get('sport', {}).get('abbreviation', 'UNK')
        date_short = game.get('date', '')[5:]
        game_pk    = game.get('game', {}).get('gamePk')
        is_home    = game.get('isHome', False)

        if "River Cats" in t: t = "SAC"
        elif "Chihuahuas" in o: o = "ELP"
        elif "Chihuahuas" in t: t = "ELP"
        elif "River Cats" in o: o = "SAC"

        date_value = _savant_url(game_pk, date_short) if game_pk else date_short
        opp_label  = f"vs {o}" if is_home else f"@ {o}"
        score      = _score_str(game_pk, is_home, scores) if game_pk else "-"

        rows.append({
            "Date":  date_value,
            "Lvl":   lvl,
            "Team":  t,
            "Opp":   opp_label,
            "Score": score,
            "AB":    s.get('atBats', 0),
            "R":     s.get('runs', 0),
            "H":     s.get('hits', 0),
            "2B":    s.get('doubles', 0),
            "3B":    s.get('triples', 0),
            "HR":    s.get('homeRuns', 0),
            "RBI":   s.get('rbi', 0),
            "BB":    s.get('baseOnBalls', 0),
            "SO":    s.get('strikeOuts', 0),
            "SB":    s.get('stolenBases', 0),
            "CS":    s.get('caughtStealing', 0),
            "AVG":   s.get('avg', '.000'),
            "OBP":   s.get('obp', '.000'),
            "SLG":   s.get('slg', '.000'),
        })

    return pd.DataFrame(rows)


def format_hitting_season(season_stat: dict) -> pd.DataFrame:
    """
    Format season totals for a hitter into a single-row DataFrame.

    All stats are derived from raw counting stats in the MLB Stats API:

      BB%   = BB / PA * 100
      K%    = SO / PA * 100
      ISO   = SLG - AVG
      BABIP = (H - HR) / (AB - SO - HR + SF)
      wRC+  = ((wOBA - lgwOBA) / wOBA_scale + lgR/PA) / lgR/PA * 100
              wOBA itself is computed from linear weights applied to
              counting stats (uBB, HBP, 1B, 2B, 3B, HR).

    wRC+ uses 2025 MLB league-average constants defined at the top of this
    module (_LG_WOBA, _WOBA_SCALE, _LG_R_PA). Update those constants if
    precise 2026 values become available.

    Columns: PA, H, 2B, 3B, HR, R, RBI, SB, CS, BB%, K%, ISO, BABIP,
             AVG, OBP, SLG, OPS, wRC+
    """
    s = season_stat if season_stat else {}

    pa      = s.get('plateAppearances', 0)
    ab      = s.get('atBats', 0)
    h       = s.get('hits', 0)
    hr      = s.get('homeRuns', 0)
    doubles = s.get('doubles', 0)
    triples = s.get('triples', 0)
    so      = s.get('strikeOuts', 0)
    bb      = s.get('baseOnBalls', 0)
    ibb     = s.get('intentionalWalks', 0)
    hbp     = s.get('hitByPitch', 0)
    sf      = s.get('sacFlies', 0)
    slg_str = s.get('slg', '.000')
    avg_str = s.get('avg', '.000')

    bb_pct = f"{bb / pa * 100:.1f}%" if pa > 0 else "-.-%"
    k_pct  = f"{so / pa * 100:.1f}%" if pa > 0 else "-.-%"

    try:
        iso = f"{float(slg_str) - float(avg_str):.3f}"
    except (ValueError, TypeError):
        iso = ".000"

    babip_denom = ab - so - hr + sf
    babip = f"{(h - hr) / babip_denom:.3f}" if babip_denom > 0 else ".000"

    # wOBA = (w_uBB*uBB + w_HBP*HBP + w_1B*1B + w_2B*2B + w_3B*3B + w_HR*HR)
    #        / (AB + BB - IBB + SF + HBP)
    singles  = h - doubles - triples - hr
    ubb      = bb - ibb
    woba_num = (_W_UBB*ubb + _W_HBP*hbp + _W_1B*singles
                + _W_2B*doubles + _W_3B*triples + _W_HR*hr)
    woba_den = ab + bb - ibb + sf + hbp
    if woba_den > 0:
        woba     = woba_num / woba_den
        wrc_plus = round(
            ((woba - _LG_WOBA) / _WOBA_SCALE + _LG_R_PA) / _LG_R_PA * 100
        )
        wrc_plus_str = str(wrc_plus)
    else:
        wrc_plus_str = "-"

    row = {
        "PA":    pa,
        "H":     h,
        "2B":    doubles,
        "3B":    triples,
        "HR":    hr,
        "R":     s.get('runs', 0),
        "RBI":   s.get('rbi', 0),
        "SB":    s.get('stolenBases', 0),
        "CS":    s.get('caughtStealing', 0),
        "BB%":   bb_pct,
        "K%":    k_pct,
        "ISO":   iso,
        "BABIP": babip,
        "AVG":   avg_str,
        "OBP":   s.get('obp', '.000'),
        "SLG":   slg_str,
        "OPS":   s.get('ops', '.000'),
        "wRC+":  wrc_plus_str,
    }
    return pd.DataFrame([row])


def format_pitching_stats(splits: list, scores: dict) -> pd.DataFrame:
    """
    Format the 7 most recent game logs for a pitcher. Most recent game first.

    Columns: Date, Lvl, Team, Opp, Score, GS, W, L, SV, BS, HLD,
             IP, H, R, ER, HR, BB, K, NP-S, BAA, ERA
    """
    splits.sort(key=lambda x: x['date'], reverse=True)
    recent_7 = splits[:7]  # most recent first

    rows = []
    for game in recent_7:
        s       = game.get('stat', {})
        t       = game.get('team', {}).get('name', 'UNK')
        o       = game.get('opponent', {}).get('name', 'UNK')
        lvl     = game.get('sport', {}).get('abbreviation', 'UNK')
        date_short = game.get('date', '')[5:]
        game_pk    = game.get('game', {}).get('gamePk')
        is_home    = game.get('isHome', False)

        date_value = _savant_url(game_pk, date_short) if game_pk else date_short
        opp_label  = f"vs {o}" if is_home else f"@ {o}"
        score      = _score_str(game_pk, is_home, scores) if game_pk else "-"

        rows.append({
            "Date":  date_value,
            "Lvl":   lvl,
            "Team":  t,
            "Opp":   opp_label,
            "Score": score,
            "GS":    s.get('gamesStarted', 0),
            "W":     s.get('wins', 0),
            "L":     s.get('losses', 0),
            "SV":    s.get('saves', 0),
            "BS":    s.get('blownSaves', 0),
            "HLD":   s.get('holds', 0),
            "IP":    s.get('inningsPitched', '0.0'),
            "H":     s.get('hits', 0),
            "R":     s.get('runs', 0),
            "ER":    s.get('earnedRuns', 0),
            "HR":    s.get('homeRuns', 0),
            "BB":    s.get('baseOnBalls', 0),
            "K":     s.get('strikeOuts', 0),
            "NP-S":  f"{s.get('numberOfPitches', 0)}-{s.get('strikes', 0)}",
            "BAA":   s.get('avg', '.000'),
            "ERA":   s.get('era', '0.00'),
        })

    return pd.DataFrame(rows)


def format_pitching_season(season_stat: dict) -> pd.DataFrame:
    """
    Format season totals for a pitcher into a single-row DataFrame.

    All stats are derived from raw counting stats in the MLB Stats API:

      K/9     = (SO / IP) * 9
      BB/9    = (BB / IP) * 9
      HR/9    = (HR / IP) * 9
      K%-BB%  = (K/BF - BB/BF) * 100
      BABIP   = (H - HR) / (BF - BB - SO - HR - HBP)
      LOB%    = (H + BB + HBP - R) / (H + BB + HBP - 1.4 * HR) * 100
      GB%     = groundOuts / (groundOuts + airOuts) * 100
                [Note: the API returns 'groundOuts' and 'airOuts' as outs
                recorded, not total batted-ball events. This lumps line-drive
                outs into airOuts, so GB% will differ slightly from
                Statcast-based values.]
      HR/FB   = HR / (airOuts + HR) * 100
                [Same approximation as GB% — airOuts includes line drives.]
      FIP     = (13*HR + 3*(BB+HBP) - 2*K) / IP + FIP_constant

    FIP constant is 3.10 (_FIP_CONSTANT at top of module). Update annually.

    Columns: GP-GS, W-L, SV-BS, IP, QS, R, ER, BAA, K/9, BB/9, HR/9,
             K%-BB%, BABIP, LOB%, GB%, HR/FB, ERA, FIP
    """
    s = season_stat if season_stat else {}

    ip_str      = s.get('inningsPitched', '0.0')
    ip          = _ip_to_decimal(ip_str)
    gp          = s.get('gamesPlayed', 0)
    gs          = s.get('gamesStarted', 0)
    w           = s.get('wins', 0)
    l           = s.get('losses', 0)
    sv          = s.get('saves', 0)
    bs          = s.get('blownSaves', 0)
    qs          = s.get('qualityStarts', 0)
    k           = s.get('strikeOuts', 0)
    bb          = s.get('baseOnBalls', 0)
    hr          = s.get('homeRuns', 0)
    hbp         = s.get('hitBatsmen', 0)
    h           = s.get('hits', 0)
    r           = s.get('runs', 0)
    bf          = s.get('battersFaced', 0)
    ground_outs = s.get('groundOuts', 0)
    air_outs    = s.get('airOuts', 0)

    k9  = f"{k  / ip * 9:.2f}" if ip > 0 else "-.--"
    bb9 = f"{bb / ip * 9:.2f}" if ip > 0 else "-.--"
    hr9 = f"{hr / ip * 9:.2f}" if ip > 0 else "-.--"

    # K%-BB%: strikeout rate minus walk rate, per batter faced
    k_minus_bb = f"{(k / bf - bb / bf) * 100:.1f}%" if bf > 0 else "-.-%"

    # BABIP (pitcher): (H - HR) / (BF - BB - K - HR - HBP)
    babip_denom = bf - bb - k - hr - hbp
    babip = f"{(h - hr) / babip_denom:.3f}" if babip_denom > 0 else ".000"

    # LOB% = (H + BB + HBP - R) / (H + BB + HBP - 1.4 * HR)
    lob_num = h + bb + hbp - r
    lob_den = h + bb + hbp - 1.4 * hr
    lob_pct = f"{lob_num / lob_den * 100:.1f}%" if lob_den > 0 else "-.-%"

    # GB% = groundOuts / (groundOuts + airOuts)  [see docstring for caveat]
    contact_outs = ground_outs + air_outs
    gb_pct = f"{ground_outs / contact_outs * 100:.1f}%" if contact_outs > 0 else "-.-%"

    # HR/FB = HR / (airOuts + HR)  [see docstring for caveat]
    hr_fb_den = air_outs + hr
    hr_fb = f"{hr / hr_fb_den * 100:.1f}%" if hr_fb_den > 0 else "-.-%"

    # FIP = (13*HR + 3*(BB+HBP) - 2*K) / IP + constant
    fip = f"{(13 * hr + 3 * (bb + hbp) - 2 * k) / ip + _FIP_CONSTANT:.2f}" if ip > 0 else "-.--"

    row = {
        "GP-GS":  f"{gp}-{gs}",
        "W-L":    f"{w}-{l}",
        "SV-BS":  f"{sv}-{bs}",
        "IP":     ip_str,
        "QS":     qs,
        "R":      r,
        "ER":     s.get('earnedRuns', 0),
        "BAA":    s.get('avg', '.000'),
        "K/9":    k9,
        "BB/9":   bb9,
        "HR/9":   hr9,
        "K%-BB%": k_minus_bb,
        "BABIP":  babip,
        "LOB%":   lob_pct,
        "GB%":    gb_pct,
        "HR/FB":  hr_fb,
        "ERA":    s.get('era', '0.00'),
        "FIP":    fip,
    }
    return pd.DataFrame([row])


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


@st.cache_data(ttl=3600)
def get_stats(player_id: int) -> tuple:
    """
    Fetch 2026 regular-season game logs and season stats for the given player.
    Covers MLB (sportId=1) and all MiLB levels (11-17).

    Returns (game_log_df, season_df, current_level, is_pitcher) where:
      - game_log_df:   up to 7 most recent games, most recent first, with Score
      - season_df:     single-row season totals with advanced rate stats
      - current_level: sport abbreviation of the player's most recent game
                       (used for sorting in the app)
      - is_pitcher:    True if the player's primary position is pitcher (code '1')

    Returns (None, None, None, None) if the player has no 2026 regular-season stats.

    sport_ids: 1=MLB, 11=AAA, 12=AA, 13=A+, 14=A, 15=Rookie, 16=DSL, 17=VSL
    """
    profile_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
    profile = fetch_stats(profile_url)
    if not profile or not profile.get('people'):
        return None, None, None, None

    pos_code   = profile['people'][0].get('primaryPosition', {}).get('code', '')
    is_pitcher = (pos_code == '1')
    group      = "pitching" if is_pitcher else "hitting"
    year       = 2026
    sport_ids  = [1, 11, 12, 13, 14, 15, 16, 17]

    def fetch_level(sid):
        url = (
            f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
            f"?stats=gameLog,season&group={group}&season={year}"
            f"&gameType=R&sportId={sid}"
        )
        return fetch_stats(url)

    all_splits       = []
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
        return None, None, None, None

    # Determine current level from the most recent game
    all_splits.sort(key=lambda x: x['date'], reverse=True)
    current_level = all_splits[0].get('sport', {}).get('abbreviation', 'UNK')

    # Fetch final scores for the 7 most recent games — one batched API call
    recent_pks = [s.get('game', {}).get('gamePk') for s in all_splits[:7]]
    recent_pks = [pk for pk in recent_pks if pk]
    scores = fetch_game_scores(recent_pks)

    if is_pitcher:
        game_log_df = format_pitching_stats(all_splits, scores)
        season_df   = format_pitching_season(best_season_stat)
    else:
        game_log_df = format_hitting_stats(all_splits, scores)
        season_df   = format_hitting_season(best_season_stat)

    return game_log_df, season_df, current_level, is_pitcher
