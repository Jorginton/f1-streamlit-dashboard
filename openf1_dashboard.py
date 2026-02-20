"""
OpenF1 Dashboard — Streamlit app
Run with: streamlit run openf1_dashboard.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenF1 Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }
  h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
    color: #ffffff !important;
  }

  /* Main background */
  .stApp { background-color: #0d0d0d; color: #e8e8e8; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #161616;
    border-right: 2px solid #e10600;
  }
  section[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
  }
  section[data-testid="stSidebar"] label {
    color: #cccccc !important;
    font-weight: 500;
  }

  /* General text contrast improvements */
  p, span, div, li {
    color: #e0e0e0;
  }
  .stCaption, [data-testid="stCaptionContainer"] {
    color: #aaaaaa !important;
  }

  /* Selectbox / dropdowns */
  .stSelectbox label {
    color: #cccccc !important;
    font-weight: 500;
    font-size: 14px;
  }
  /* The closed select box */
  .stSelectbox [data-baseweb="select"] > div {
    background-color: #2a2a2a !important;
    border-color: #555 !important;
    color: #f0f0f0 !important;
  }
  .stSelectbox [data-baseweb="select"] * {
    color: #f0f0f0 !important;
    background-color: #2a2a2a !important;
  }
  /* The open dropdown list — force dark background + light text */
  [data-baseweb="popover"],
  [data-baseweb="popover"] *,
  [data-baseweb="menu"],
  [data-baseweb="menu"] *,
  ul[role="listbox"],
  ul[role="listbox"] * {
    background-color: #2a2a2a !important;
    color: #f0f0f0 !important;
  }
  li[role="option"],
  [data-baseweb="option"] {
    background-color: #2a2a2a !important;
    color: #f0f0f0 !important;
  }
  li[role="option"]:hover,
  [data-baseweb="option"]:hover,
  li[aria-selected="true"],
  [aria-selected="true"] {
    background-color: #e10600 !important;
    color: #ffffff !important;
  }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #1e1e1e;
    border: 1px solid #333;
    border-left: 3px solid #e10600;
    border-radius: 6px;
    padding: 12px 18px;
  }
  [data-testid="metric-container"] label {
    color: #aaaaaa !important;
    font-size: 13px !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 26px !important;
    font-weight: 600;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #1a1a1a;
    border-radius: 6px;
    padding: 4px;
    border: 1px solid #2a2a2a;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.5px;
    font-size: 16px;
    background: transparent;
    color: #aaaaaa !important;
    border-radius: 4px;
    padding: 6px 16px;
  }
  .stTabs [aria-selected="true"] {
    background: #e10600 !important;
    color: #ffffff !important;
  }
  .stTabs [data-baseweb="tab"]:hover {
    color: #ffffff !important;
    background: #2a2a2a !important;
  }

  /* Dataframe */
  .stDataFrame {
    border: 1px solid #2a2a2a;
    border-radius: 6px;
  }
  .stDataFrame th {
    background: #1e1e1e !important;
    color: #cccccc !important;
  }
  .stDataFrame td {
    color: #e0e0e0 !important;
  }

  /* Info/warning boxes */
  .stInfo {
    background: #1a2a1a;
    border-left-color: #39b54a;
    color: #cccccc !important;
  }
  .stWarning {
    background: #2a2010;
    color: #cccccc !important;
  }

  /* Spinner text */
  .stSpinner > div {
    color: #cccccc !important;
  }

  /* Divider */
  hr { border-color: #e10600; opacity: 0.25; }

  /* Section headers */
  .section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px;
    letter-spacing: 2px;
    color: #ffffff;
    border-bottom: 1px solid #333;
    padding-bottom: 6px;
    margin: 20px 0 12px 0;
  }

  /* Championship table rows */
  .champ-table {
    width: 100%;
    border-collapse: collapse;
  }
  .champ-table th {
    background: #1e1e1e;
    color: #aaaaaa;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid #333;
  }
  .champ-table td {
    padding: 10px 14px;
    color: #e0e0e0;
    border-bottom: 1px solid #222;
    font-size: 15px;
  }
  .champ-table tr:hover td { background: #1e1e1e; }
  .pos-badge {
    display: inline-block;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-weight: 600;
    font-size: 13px;
    background: #2a2a2a;
    color: #ffffff;
  }
  .pos-1 { background: #ffd700; color: #000; }
  .pos-2 { background: #c0c0c0; color: #000; }
  .pos-3 { background: #cd7f32; color: #000; }
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://api.openf1.org/v1"

# ─── API helpers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch(endpoint: str, params: dict = None) -> list:
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error ({endpoint}): {e}")
        return []

def df(data: list) -> pd.DataFrame:
    return pd.DataFrame(data) if data else pd.DataFrame()

TEAM_COLORS = {
    "Red Bull Racing": "#3671C6",
    "Ferrari": "#E8002D",
    "Mercedes": "#27F4D2",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine": "#FF87BC",
    "Williams": "#64C4FF",
    "RB": "#6692FF",
    "Kick Sauber": "#52E252",
    "Haas F1 Team": "#B6BABD",
    "Cadillac": "#C41E3A",
}

PLOTLY_THEME = dict(
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#161616",
    font_color="#e0e0e0",
    font_family="DM Sans",
    xaxis=dict(gridcolor="#2a2a2a", linecolor="#444", tickfont=dict(color="#cccccc")),
    yaxis=dict(gridcolor="#2a2a2a", linecolor="#444", tickfont=dict(color="#cccccc")),
    title_font=dict(color="#ffffff", family="Bebas Neue", size=20),
    legend=dict(font=dict(color="#cccccc")),
)

# ─── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏎️ OpenF1\n### Dashboard")
    st.markdown("---")

    year = st.selectbox("Season", list(range(2026, 2022, -1)), index=0)

    # Meetings
    with st.spinner("Loading meetings…"):
        meetings_raw = fetch("meetings", {"year": year})
    meetings_df = df(meetings_raw)

    meeting_options = {}
    if not meetings_df.empty and "meeting_name" in meetings_df.columns:
        for _, row in meetings_df.iterrows():
            meeting_options[row["meeting_name"]] = row["meeting_key"]

    # Auto-select latest meeting (last in list = most recent)
    meeting_names = list(meeting_options.keys())
    default_meeting_idx = len(meeting_names) if meeting_names else 0  # "All" is index 0, latest is last

    selected_meeting_name = st.selectbox(
        "Race / Grand Prix",
        ["All"] + meeting_names,
        index=default_meeting_idx,
    )
    selected_meeting_key = meeting_options.get(selected_meeting_name)

    # Sessions — auto-select the Race session if available
    session_options = {}
    session_types = {}
    if selected_meeting_key:
        sessions_raw = fetch("sessions", {"meeting_key": selected_meeting_key})
        sessions_df = df(sessions_raw)
        if not sessions_df.empty and "session_name" in sessions_df.columns:
            for _, row in sessions_df.iterrows():
                label = f"{row['session_name']}"
                session_options[label] = row["session_key"]
                session_types[label] = row.get("session_type", "")

    # Auto-select Race session, fallback to latest
    session_names = list(session_options.keys())
    default_session_idx = 0
    for i, name in enumerate(session_names):
        if "race" in name.lower():
            default_session_idx = i + 1  # +1 because "All" is index 0
            break
    else:
        if session_names:
            default_session_idx = len(session_names)  # latest = last

    selected_session_name = st.selectbox(
        "Session",
        ["All"] + session_names,
        index=default_session_idx,
        disabled=(not session_options),
    )
    selected_session_key = session_options.get(selected_session_name)

    # Drivers
    driver_params = {}
    if selected_session_key:
        driver_params["session_key"] = selected_session_key
    elif selected_meeting_key:
        driver_params["meeting_key"] = selected_meeting_key

    drivers_raw = fetch("drivers", driver_params) if driver_params else []
    drivers_df = df(drivers_raw)

    driver_options = {"All": None}
    if not drivers_df.empty and "full_name" in drivers_df.columns:
        for _, row in drivers_df.drop_duplicates("driver_number").iterrows():
            label = f"#{row['driver_number']} {row['full_name']}"
            driver_options[label] = row["driver_number"]

    team_options = {"All": None}
    if not drivers_df.empty and "team_name" in drivers_df.columns:
        for t in sorted(drivers_df["team_name"].dropna().unique()):
            team_options[t] = t

    st.markdown("---")
    selected_driver_label = st.selectbox("Driver", list(driver_options.keys()))
    selected_driver_number = driver_options[selected_driver_label]

    selected_team_label = st.selectbox("Team", list(team_options.keys()))
    selected_team = team_options[selected_team_label]

    st.markdown("---")
    st.caption("Data: [openf1.org](https://openf1.org) · Free historical data from 2023+")
    st.markdown("""
<div style="margin-top:12px;font-size:13px;color:#aaaaaa;line-height:1.8">
  Created by <span style="color:#ffffff;font-weight:600">Jorg van de Ven</span><br>
  <a href="https://jorgvandeven.nl/?utm_source=streamlit&utm_medium=referral&utm_campaign=f1_dashboard"
     target="_blank" style="color:#e10600;text-decoration:none;">🌐 jorgvandeven.nl</a><br>
  <a href="https://www.linkedin.com/in/jorgvandeven/"
     target="_blank" style="color:#e10600;text-decoration:none;">💼 LinkedIn</a>
</div>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"## {year} Formula 1 Season")
    subtitle = selected_meeting_name if selected_meeting_name != "All" else "Full Season Overview"
    if selected_session_name != "All":
        subtitle += f" · {selected_session_name}"
    st.caption(subtitle)

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_standings, tab_overview, tab_laps, tab_stints, tab_pit, tab_positions, tab_weather = st.tabs([
    "🏆 Championship", "📊 Race Results", "⏱ Lap Times", "🛞 Stints", "🔧 Pit Stops", "🏁 Positions", "🌦 Weather"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 0 — Championship Standings (NEW — main view)
# ══════════════════════════════════════════════════════════════════════
with tab_standings:
    st.markdown('<div class="section-header">Driver Championship</div>', unsafe_allow_html=True)

    # Collect all race sessions for the year to compute standings
    with st.spinner("Building championship standings…"):
        all_sessions_raw = fetch("sessions", {"year": year, "session_name": "Race"})
    all_sessions_df = df(all_sessions_raw)

    # Points system
    POINTS_MAP = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

    driver_points: dict = {}
    team_points: dict = {}
    driver_team_map: dict = {}
    race_by_race: list = []

    if not all_sessions_df.empty and "session_key" in all_sessions_df.columns:
        race_sessions = all_sessions_df.to_dict("records")

        for session in race_sessions:
            sk = session["session_key"]
            race_name = session.get("meeting_key", sk)

            # Try session_result endpoint first
            res_raw = fetch("session_result", {"session_key": sk})
            res_df = df(res_raw)

            if res_df.empty or "position" not in res_df.columns:
                continue

            # Get driver names for this session
            drv_raw = fetch("drivers", {"session_key": sk})
            drv_df = df(drv_raw)

            if not drv_df.empty and "driver_number" in res_df.columns:
                merge_cols = [c for c in ["driver_number", "full_name", "team_name"] if c in drv_df.columns]
                res_df = res_df.merge(
                    drv_df[merge_cols].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )

            meeting_name = session.get("session_key", "")
            # Try to get meeting name
            mtg_raw = fetch("meetings", {"meeting_key": session.get("meeting_key", "")})
            mtg_df = df(mtg_raw)
            if not mtg_df.empty and "meeting_name" in mtg_df.columns:
                meeting_name = mtg_df.iloc[0]["meeting_name"]

            for _, row in res_df.iterrows():
                pos = row.get("position")
                pts = row.get("points")

                # Use API points if available, otherwise calculate
                if pts is None or pd.isna(pts):
                    try:
                        pts = POINTS_MAP.get(int(pos), 0)
                    except (ValueError, TypeError):
                        pts = 0
                else:
                    try:
                        pts = float(pts)
                    except (ValueError, TypeError):
                        pts = 0

                driver = row.get("full_name", f"#{row.get('driver_number','?')}")
                team = row.get("team_name", "Unknown")

                driver_points[driver] = driver_points.get(driver, 0) + pts
                team_points[team] = team_points.get(team, 0) + pts
                driver_team_map[driver] = team

                race_by_race.append({
                    "race": meeting_name,
                    "driver": driver,
                    "team": team,
                    "position": pos,
                    "points": pts,
                })

    # ── Driver standings table ──────────────────────────────────────
    if driver_points:
        sorted_drivers = sorted(driver_points.items(), key=lambda x: x[1], reverse=True)

        col_drv, col_team = st.columns(2)

        with col_drv:
            st.markdown('<div class="section-header">Drivers</div>', unsafe_allow_html=True)
            rows_html = ""
            for rank, (driver, pts) in enumerate(sorted_drivers, 1):
                team = driver_team_map.get(driver, "")
                color = TEAM_COLORS.get(team, "#e10600")
                badge_class = f"pos-{rank}" if rank <= 3 else ""
                rows_html += f"""
                <tr>
                  <td><span class="pos-badge {badge_class}">{rank}</span></td>
                  <td style="border-left: 3px solid {color}; padding-left: 10px;">
                    <strong style="color:#ffffff">{driver}</strong><br>
                    <span style="color:#888;font-size:12px">{team}</span>
                  </td>
                  <td style="font-weight:600;color:#ffffff;font-size:18px">{int(pts)}</td>
                </tr>"""
            st.markdown(f"""
            <table class="champ-table">
              <thead><tr>
                <th style="width:50px">#</th>
                <th>Driver</th>
                <th>PTS</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)

        # ── Constructor standings ──────────────────────────────────
        with col_team:
            st.markdown('<div class="section-header">Constructors</div>', unsafe_allow_html=True)
            sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)
            rows_html = ""
            for rank, (team, pts) in enumerate(sorted_teams, 1):
                color = TEAM_COLORS.get(team, "#e10600")
                badge_class = f"pos-{rank}" if rank <= 3 else ""
                rows_html += f"""
                <tr>
                  <td><span class="pos-badge {badge_class}">{rank}</span></td>
                  <td>
                    <span style="display:inline-block;width:4px;height:32px;background:{color};
                      border-radius:2px;vertical-align:middle;margin-right:10px;"></span>
                    <strong style="color:#ffffff">{team}</strong>
                  </td>
                  <td style="font-weight:600;color:#ffffff;font-size:18px">{int(pts)}</td>
                </tr>"""
            st.markdown(f"""
            <table class="champ-table">
              <thead><tr>
                <th style="width:50px">#</th>
                <th>Constructor</th>
                <th>PTS</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)

        # ── Points progression chart ────────────────────────────────
        if race_by_race:
            st.markdown('<div class="section-header">Points Progression</div>', unsafe_allow_html=True)
            prog_df = pd.DataFrame(race_by_race)

            # Filter by driver/team if selected
            if selected_driver_number and not drivers_df.empty:
                drv_name_row = drivers_df[drivers_df["driver_number"] == selected_driver_number]
                if not drv_name_row.empty:
                    drv_name = drv_name_row.iloc[0].get("full_name","")
                    prog_df = prog_df[prog_df["driver"] == drv_name]
            if selected_team:
                prog_df = prog_df[prog_df["team"] == selected_team]

            if not prog_df.empty:
                prog_df = prog_df.sort_values("race")
                cumul = prog_df.groupby(["driver","race"])["points"].sum().groupby(level=0).cumsum().reset_index()
                cumul.columns = ["driver","race","cumulative_points"]

                fig = px.line(
                    cumul,
                    x="race", y="cumulative_points",
                    color="driver",
                    markers=True,
                    labels={"race": "Race", "cumulative_points": "Points", "driver": "Driver"},
                    title="Cumulative Points — Season Progression",
                )
                fig.update_layout(**PLOTLY_THEME, height=420)
                fig.update_traces(line_width=2.5)
                st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No race results available yet for this season. Check back once the season begins, or select a past season.")

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — Race Results (was Overview)
# ══════════════════════════════════════════════════════════════════════
with tab_overview:
    result_params = {}
    if selected_session_key:
        result_params["session_key"] = selected_session_key
    elif selected_meeting_key:
        result_params["meeting_key"] = selected_meeting_key

    if result_params:
        with st.spinner("Loading session results…"):
            results_raw = fetch("session_result", result_params)
        results_df = df(results_raw)

        if not results_df.empty:
            if not drivers_df.empty and "driver_number" in results_df.columns:
                merge_cols = [c for c in ["driver_number", "full_name", "team_name", "team_colour"] if c in drivers_df.columns]
                results_df = results_df.merge(
                    drivers_df[merge_cols].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )

            st.markdown('<div class="section-header">Session Results</div>', unsafe_allow_html=True)

            display_df = results_df.copy()
            if selected_driver_number:
                display_df = display_df[display_df["driver_number"] == selected_driver_number]
            if selected_team:
                display_df = display_df[display_df["team_name"] == selected_team]

            display_cols = [c for c in ["position", "full_name", "team_name", "driver_number"] if c in display_df.columns]
            if "gap_to_leader" in display_df.columns:
                display_cols.append("gap_to_leader")
            if "points" in display_df.columns:
                display_cols.append("points")

            if not display_df.empty:
                st.dataframe(display_df[display_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No results match the current filters.")

    # Driver grid cards
    if not drivers_df.empty:
        st.markdown('<div class="section-header">Driver Grid</div>', unsafe_allow_html=True)
        filter_d = drivers_df.copy()
        if selected_driver_number:
            filter_d = filter_d[filter_d["driver_number"] == selected_driver_number]
        if selected_team:
            filter_d = filter_d[filter_d["team_name"] == selected_team]

        filter_d = filter_d.drop_duplicates("driver_number")
        cols = st.columns(min(4, max(1, len(filter_d))))

        for i, (_, row) in enumerate(filter_d.iterrows()):
            with cols[i % len(cols)]:
                color = row.get("team_colour") or TEAM_COLORS.get(row.get("team_name", ""), "#e10600")
                if not str(color).startswith("#"):
                    color = "#" + str(color)
                st.markdown(f"""
                <div style="background:#1a1a1a;border-left:4px solid {color};
                     border-radius:6px;padding:12px 14px;margin-bottom:10px;">
                  <div style="font-size:28px;font-family:'Bebas Neue',sans-serif;
                       letter-spacing:2px;color:{color}"># {row.get('driver_number','')}</div>
                  <div style="font-size:15px;font-weight:600;color:#ffffff">{row.get('full_name','')}</div>
                  <div style="font-size:12px;color:#aaaaaa;margin-top:2px">{row.get('team_name','')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Select a race and session from the sidebar to see results.")

# ══════════════════════════════════════════════════════════════════════
# TAB 2 — Lap Times
# ══════════════════════════════════════════════════════════════════════
with tab_laps:
    if not selected_session_key:
        st.info("Please select a specific session to view lap times.")
    else:
        lap_params = {"session_key": selected_session_key}
        if selected_driver_number:
            lap_params["driver_number"] = selected_driver_number

        with st.spinner("Loading lap data…"):
            laps_raw = fetch("laps", lap_params)
        laps_df = df(laps_raw)

        if laps_df.empty:
            st.warning("No lap data available for this session.")
        else:
            if not drivers_df.empty and "driver_number" in laps_df.columns:
                laps_df = laps_df.merge(
                    drivers_df[["driver_number","full_name","team_name","team_colour"]].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )
            if selected_team and "team_name" in laps_df.columns:
                laps_df = laps_df[laps_df["team_name"] == selected_team]

            if "lap_duration" in laps_df.columns and "lap_number" in laps_df.columns:
                laps_plot = laps_df.dropna(subset=["lap_duration"])

                c1, c2, c3 = st.columns(3)
                c1.metric("Total Laps", int(laps_plot["lap_number"].max()) if not laps_plot.empty else "—")
                c2.metric("Fastest Lap", f"{laps_plot['lap_duration'].min():.3f}s" if not laps_plot.empty else "—")
                if "full_name" in laps_plot.columns and not laps_plot.empty:
                    fastest_driver = laps_plot.loc[laps_plot["lap_duration"].idxmin(), "full_name"]
                    c3.metric("Fastest Driver", fastest_driver)

                st.markdown('<div class="section-header">Lap Time Chart</div>', unsafe_allow_html=True)
                color_col = "full_name" if "full_name" in laps_plot.columns else None
                fig = px.line(
                    laps_plot.sort_values("lap_number"),
                    x="lap_number", y="lap_duration",
                    color=color_col,
                    labels={"lap_number": "Lap", "lap_duration": "Time (s)", "full_name": "Driver"},
                )
                fig.update_layout(**PLOTLY_THEME, title="Lap Times by Lap")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown('<div class="section-header">Lap Time Distribution</div>', unsafe_allow_html=True)
                fig2 = px.box(
                    laps_plot,
                    x=color_col if color_col else None,
                    y="lap_duration",
                    color=color_col,
                    labels={"lap_duration": "Lap Time (s)"},
                )
                fig2.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="section-header">Raw Lap Data</div>', unsafe_allow_html=True)
            st.dataframe(laps_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 3 — Stints
# ══════════════════════════════════════════════════════════════════════
with tab_stints:
    if not selected_session_key:
        st.info("Please select a specific session to view stints.")
    else:
        stint_params = {"session_key": selected_session_key}
        if selected_driver_number:
            stint_params["driver_number"] = selected_driver_number

        with st.spinner("Loading stint data…"):
            stints_raw = fetch("stints", stint_params)
        stints_df = df(stints_raw)

        if stints_df.empty:
            st.warning("No stint data available.")
        else:
            if not drivers_df.empty and "driver_number" in stints_df.columns:
                stints_df = stints_df.merge(
                    drivers_df[["driver_number","full_name","team_name","team_colour"]].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )
            if selected_team and "team_name" in stints_df.columns:
                stints_df = stints_df[stints_df["team_name"] == selected_team]

            st.markdown('<div class="section-header">Tyre Strategy</div>', unsafe_allow_html=True)
            if {"lap_start","lap_end","full_name","compound"}.issubset(stints_df.columns):
                compound_colors = {
                    "SOFT": "#e8002d", "MEDIUM": "#ffd900", "HARD": "#f0f0f0",
                    "INTERMEDIATE": "#39b54a", "WET": "#0067ff",
                }
                fig = go.Figure()
                for _, row in stints_df.iterrows():
                    color = compound_colors.get(str(row.get("compound","")).upper(), "#888")
                    fig.add_trace(go.Bar(
                        x=[row["lap_end"] - row["lap_start"]],
                        base=[row["lap_start"]],
                        y=[row["full_name"]],
                        orientation="h",
                        marker_color=color,
                        name=str(row.get("compound","")),
                        hovertemplate=(
                            f"<b>{row['full_name']}</b><br>"
                            f"Compound: {row.get('compound','')}<br>"
                            f"Laps: {row['lap_start']}–{row['lap_end']}<extra></extra>"
                        ),
                        showlegend=False,
                    ))
                fig.update_layout(
                    barmode="overlay",
                    title="Tyre Strategy (Gantt)",
                    xaxis_title="Lap Number",
                    yaxis_title="Driver",
                    **PLOTLY_THEME,
                )
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(stints_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 4 — Pit Stops
# ══════════════════════════════════════════════════════════════════════
with tab_pit:
    if not selected_session_key:
        st.info("Please select a specific session to view pit stop data.")
    else:
        pit_params = {"session_key": selected_session_key}
        if selected_driver_number:
            pit_params["driver_number"] = selected_driver_number

        with st.spinner("Loading pit data…"):
            pit_raw = fetch("pit", pit_params)
        pit_df = df(pit_raw)

        if pit_df.empty:
            st.warning("No pit stop data available.")
        else:
            if not drivers_df.empty and "driver_number" in pit_df.columns:
                pit_df = pit_df.merge(
                    drivers_df[["driver_number","full_name","team_name"]].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )
            if selected_team and "team_name" in pit_df.columns:
                pit_df = pit_df[pit_df["team_name"] == selected_team]

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pit Stops", len(pit_df))
            if "pit_duration" in pit_df.columns:
                c2.metric("Fastest Stop", f"{pit_df['pit_duration'].min():.2f}s")
                c3.metric("Average Stop", f"{pit_df['pit_duration'].mean():.2f}s")

            if "pit_duration" in pit_df.columns and "full_name" in pit_df.columns:
                st.markdown('<div class="section-header">Pit Stop Duration by Driver</div>', unsafe_allow_html=True)
                fig = px.bar(
                    pit_df.sort_values("pit_duration"),
                    x="full_name", y="pit_duration", color="full_name",
                    labels={"full_name": "Driver", "pit_duration": "Duration (s)"},
                )
                fig.update_layout(**PLOTLY_THEME, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(pit_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 5 — Positions
# ══════════════════════════════════════════════════════════════════════
with tab_positions:
    if not selected_session_key:
        st.info("Please select a specific session to view position data.")
    else:
        pos_params = {"session_key": selected_session_key}
        if selected_driver_number:
            pos_params["driver_number"] = selected_driver_number

        with st.spinner("Loading position data…"):
            pos_raw = fetch("position", pos_params)
        pos_df = df(pos_raw)

        if pos_df.empty:
            st.warning("No position data available.")
        else:
            if not drivers_df.empty and "driver_number" in pos_df.columns:
                pos_df = pos_df.merge(
                    drivers_df[["driver_number","full_name","team_name","team_colour"]].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )
            if selected_team and "team_name" in pos_df.columns:
                pos_df = pos_df[pos_df["team_name"] == selected_team]

            if "date" in pos_df.columns:
                pos_df["date"] = pd.to_datetime(pos_df["date"], errors="coerce")
                pos_df = pos_df.dropna(subset=["date"]).sort_values("date")

            if "position" in pos_df.columns and "date" in pos_df.columns:
                st.markdown('<div class="section-header">Position Over Time</div>', unsafe_allow_html=True)
                color_col = "full_name" if "full_name" in pos_df.columns else None
                fig = px.line(
                    pos_df, x="date", y="position",
                    color=color_col,
                    labels={"date": "Time", "position": "Position", "full_name": "Driver"},
                )
                fig.update_yaxes(autorange="reversed", dtick=1)
                fig.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 6 — Weather
# ══════════════════════════════════════════════════════════════════════
with tab_weather:
    if not selected_session_key:
        st.info("Please select a specific session to view weather data.")
    else:
        with st.spinner("Loading weather data…"):
            weather_raw = fetch("weather", {"session_key": selected_session_key})
        weather_df = df(weather_raw)

        if weather_df.empty:
            st.warning("No weather data available.")
        else:
            if "date" in weather_df.columns:
                weather_df["date"] = pd.to_datetime(weather_df["date"], errors="coerce")
                weather_df = weather_df.dropna(subset=["date"]).sort_values("date")

            numeric_cols = ["air_temperature", "track_temperature", "humidity",
                            "wind_speed", "rainfall", "pressure"]
            available = [c for c in numeric_cols if c in weather_df.columns]

            if available:
                c1, c2, c3 = st.columns(3)
                if "air_temperature" in weather_df.columns:
                    c1.metric("Avg Air Temp", f"{weather_df['air_temperature'].mean():.1f}°C")
                if "track_temperature" in weather_df.columns:
                    c2.metric("Avg Track Temp", f"{weather_df['track_temperature'].mean():.1f}°C")
                if "humidity" in weather_df.columns:
                    c3.metric("Avg Humidity", f"{weather_df['humidity'].mean():.1f}%")

                st.markdown('<div class="section-header">Temperature Over Session</div>', unsafe_allow_html=True)
                temp_cols = [c for c in ["air_temperature","track_temperature"] if c in weather_df.columns]
                if temp_cols and "date" in weather_df.columns:
                    fig = px.line(
                        weather_df.melt(id_vars="date", value_vars=temp_cols),
                        x="date", y="value", color="variable",
                        labels={"date":"Time","value":"Temperature (°C)","variable":"Sensor"},
                    )
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

                if "wind_speed" in weather_df.columns and "date" in weather_df.columns:
                    st.markdown('<div class="section-header">Wind Speed</div>', unsafe_allow_html=True)
                    fig2 = px.area(weather_df, x="date", y="wind_speed",
                                   labels={"date":"Time","wind_speed":"Wind Speed (m/s)"})
                    fig2.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig2, use_container_width=True)

            st.dataframe(weather_df, use_container_width=True, hide_index=True)
