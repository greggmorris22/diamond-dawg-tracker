import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import concurrent.futures
from data.milb_api import get_stats, LEVEL_ORDER
from data.msstate_players import MSU_PLAYERS

st.set_page_config(page_title="Diamond Dawg Tracker", layout="wide")

st.title("Diamond Dawg Tracker")
st.markdown(
    "Recent game logs and 2026 season stats YTD for all Diamond Dawg alumni "
    "who have played this season. Sorted by level, then alphabetically by last name."
)

# Column config applied only to the Recent Games table.
# Renders the Date column as a clickable link to the Baseball Savant gamefeed.
# The URL has the short date embedded as &d=MM-DD so the regex can extract it
# for display. Only the game-log table needs this; the season table has no URLs.
GAMES_COLUMN_CONFIG = {
    "Date": st.column_config.LinkColumn(
        "Date",
        display_text=r"d=(\d{2}-\d{2})"
    )
}


def fetch_player(player_name: str, player_id: int):
    """
    Fetch stats and profile info for one player in a background thread.

    Returns a tuple of (name, last_name, level, team, age, position,
    season_df, games_df), or None if the player has no 2026 stats.
    """
    season_df, games_df, current_level, team, age, position = get_stats(player_id)
    if season_df is not None and not season_df.empty:
        last_name = player_name.split()[-1]
        return (player_name, last_name, current_level, team, age, position,
                season_df, games_df)
    return None


with st.spinner("Loading Diamond Dawgs..."):
    # Fetch all players in parallel rather than sequentially
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(fetch_player, name, pid)
            for name, pid in MSU_PLAYERS
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

# Filter out players with no stats
results = [r for r in results if r is not None]

if not results:
    st.info("No active stats found for any Diamond Dawg at this time.")
else:
    # Sort: MLB first, then by level, then alphabetically by last name within level
    results.sort(key=lambda r: (LEVEL_ORDER.get(r[2], 99), r[1]))

    st.success(f"Found {len(results)} active Diamond Dawgs.")

    for player_name, _, current_level, team, age, position, season_df, games_df in results:
        # --- Player header ---
        st.subheader(player_name)
        st.caption(f"{position}  |  {team}  |  Age {age}  |  {current_level}")

        # --- 2026 season totals ---
        st.markdown("**2026 Stats**")
        st.dataframe(
            season_df,
            use_container_width=True,
            hide_index=True,
        )

        # --- Recent game logs ---
        if games_df is not None and not games_df.empty:
            st.markdown("**Recent Games**")
            st.dataframe(
                games_df,
                use_container_width=True,
                hide_index=True,
                column_config=GAMES_COLUMN_CONFIG,
            )

        st.divider()
