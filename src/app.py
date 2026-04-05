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
    "Recent game logs and season stats YTD for all Diamond Dawg alumni who "
    "have played in 2026. Sorted by level and alphabetically by last name."
)

# Column config shared by all stat tables. Renders the Date column as a
# clickable link to the Baseball Savant gamefeed. The URL has the short date
# embedded as &d=MM-DD so the regex can extract it for display. The Season
# aggregate row has an empty URL and renders as a blank cell.
STAT_COLUMN_CONFIG = {
    "Date": st.column_config.LinkColumn(
        "Date",
        display_text=r"d=(\d{2}-\d{2})"
    )
}


def fetch_player(player_name: str, player_id: int):
    """Fetch stats for one player. Returns (name, last_name, level, df) or None."""
    stats_df, current_level = get_stats(player_id)
    if stats_df is not None and not stats_df.empty:
        last_name = player_name.split()[-1]
        return (player_name, last_name, current_level, stats_df)
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

    for player_name, _, current_level, stats_df in results:
        st.subheader(f"{player_name}  —  {current_level}")
        st.dataframe(
            stats_df,
            use_container_width=True,
            hide_index=True,
            column_config=STAT_COLUMN_CONFIG
        )
