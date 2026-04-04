import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from data.milb_api import get_stats, LEVEL_ORDER
from data.msstate_players import MSU_PLAYERS

st.set_page_config(page_title="Diamond Dawg Tracker", layout="wide")

st.title("Diamond Dawg Tracker")
st.markdown(
    "2026 game logs and season stats YTD for Mississippi State University "
    "alumni currently active in professional baseball. MLB players appear "
    "first, followed by MiLB levels. Within each level, players are sorted "
    "alphabetically by last name."
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

# Fetch stats for all players, collect results for sorting
results = []

progress = st.progress(0, text="Loading Diamond Dawgs...")
total = len(MSU_PLAYERS)

for i, (player_name, player_id) in enumerate(MSU_PLAYERS):
    progress.progress((i + 1) / total, text=f"Checking {player_name}...")
    stats_df, current_level = get_stats(player_id)
    if stats_df is not None and not stats_df.empty:
        last_name = player_name.split()[-1]
        results.append((player_name, last_name, current_level, stats_df))

progress.empty()

if not results:
    st.info("No active stats found for any MSU alumni at this time.")
else:
    # Sort: MLB first, then by level, then alphabetically by last name within each level
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
