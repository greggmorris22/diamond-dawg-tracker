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

STAT_COLUMN_CONFIG = {
    "Date": st.column_config.LinkColumn(
        "Date",
        display_text=r"d=(\d{2}-\d{2})"
    )
}

def fetch_player(player_name: str, player_id: int, draft_class: int):
    """Fetch stats for one player. Returns a dict with all necessary state."""
    gl_df, ss_df, current_level, is_pitcher = get_stats(player_id)
    has_stats = gl_df is not None and not gl_df.empty
    
    parts = player_name.split()
    last_name = parts[-1]
    first_name = " ".join(parts[:-1])
    
    if has_stats:
        dropdown_name = f"{first_name} {last_name}"
    else:
        # User requested to see them but visually greyed out / unselectable
        # Best approximation in purely native Streamlit selectbox:
        dropdown_name = f"{first_name} {last_name} (No 2026 Stats)"

    return {
        "name": player_name,
        "last_name": last_name,
        "dropdown_name": dropdown_name,
        "draft_class": draft_class,
        "has_stats": has_stats,
        "gl_df": gl_df,
        "ss_df": ss_df,
        "level": current_level,
        "is_pitcher": is_pitcher
    }

with st.spinner("Loading Diamond Dawgs..."):
    # Fetch all players in parallel rather than sequentially
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(fetch_player, row[0], row[1], row[2])
            for row in MSU_PLAYERS
        ]
        all_results = [f.result() for f in concurrent.futures.as_completed(futures)]

# Sort alphabetically by last name for dropdown purposes
all_results.sort(key=lambda r: r["last_name"])

# --- FILTERS ---
st.divider()
col1, col2 = st.columns(2)

# Draft Class Filter
draft_years = sorted(list(set(p[2] for p in MSU_PLAYERS)), reverse=True)
draft_options = ["All"] + draft_years

with col1:
    selected_draft_class = st.selectbox("Filter by Draft Class", options=draft_options)

# Filter the list by Draft Class first
if selected_draft_class == "All":
    filtered_results = all_results
else:
    filtered_results = [r for r in all_results if r["draft_class"] == selected_draft_class]

active_count = sum(1 for r in filtered_results if r["has_stats"])
player_options = [f"All ({active_count})"] + [r["dropdown_name"] for r in filtered_results]

# Player Filter
with col2:
    selected_player = st.selectbox("Filter by Player", options=player_options)

st.divider()

# --- DISPLAY MATCHING PLAYERS ---
# Filter by selected player
if selected_player.startswith("All"):
    # Show only active players if 'All' is selected
    display_results = [r for r in filtered_results if r["has_stats"]]
else:
    # Find the specific player selected
    display_results = [r for r in filtered_results if r["dropdown_name"] == selected_player]

if not display_results:
    if selected_player.startswith("All"):
        st.info("No active stats found for this filter combination at this time.")
    else:
        st.info("This player has not recorded any stats yet for the 2026 season.")
else:
    # Sort active players: MLB first, then by level, then alphabetically by last name within level
    display_results.sort(key=lambda r: (LEVEL_ORDER.get(r["level"], 99), r["last_name"]))

    if selected_player.startswith("All"):
        st.success(f"Found {len(display_results)} active Diamond Dawgs.")

    for r in display_results:
        # If user explicitly selected an inactive player, it gets caught above in `if not display_results`.
        # Just a safety check here:
        if not r["has_stats"]:
            st.info(f"{r['name']} has not recorded any stats yet for the 2026 season.")
            continue
            
        st.subheader(f"{r['name']}  —  {r['level']}")
        
        # 1. Season Stats Section (Above Game Logs)
        st.markdown("**2026 Season Stats**")
        st.dataframe(
            r["ss_df"],
            use_container_width=True,
            hide_index=True
        )
        
        # 2. Recent Game Logs
        st.markdown("**Recent Game Logs**")
        st.dataframe(
            r["gl_df"],
            use_container_width=True,
            hide_index=True,
            column_config=STAT_COLUMN_CONFIG
        )
        st.write("") # small spacer
