import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from data.milb_api import get_milb_stats
from data.msstate_players import MSU_PLAYERS

st.set_page_config(page_title="MSU MiLB Tracker", layout="wide")

st.title("MSU MiLB Tracker")
st.markdown(
    "Last 7 minor league game logs and 2026 season stats YTD for "
    "Mississippi State University alumni currently active in MiLB. "
    "Players who have reached MLB or are no longer active are automatically excluded."
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

found_any = False

for player_name, player_id in MSU_PLAYERS:
    with st.spinner(f"Checking {player_name}..."):
        stats_df = get_milb_stats(player_id)

    if stats_df is not None and not stats_df.empty:
        found_any = True
        st.subheader(player_name)
        st.dataframe(
            stats_df,
            use_container_width=True,
            hide_index=True,
            column_config=STAT_COLUMN_CONFIG
        )

if not found_any:
    st.info("No active MiLB stats found for any MSU alumni at this time.")
