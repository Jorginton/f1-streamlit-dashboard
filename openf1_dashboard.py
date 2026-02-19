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
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }
  h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
  }
  .stApp { background-color: #0d0d0d; color: #f0f0f0; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #141414;
    border-right: 1px solid #e10600;
  }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #e10600;
    border-radius: 4px;
    padding: 10px 16px;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #141414;
    border-radius: 4px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.5px;
    font-size: 16px;
    background: transparent;
    color: #888;
    border-radius: 3px;
  }
  .stTabs [aria-selected="true"] {
    background: #e10600 !important;
    color: #fff !important;
  }

  /* Dataframe */
  .stDataFrame { border: 1px solid #2a2a2a; border-radius: 4px; }

  /* Divider accent */
  hr { border-color: #e10600; opacity: 0.3; }
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
}

PLOTLY_THEME = dict(
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#141414",
    font_color="#f0f0f0",
    font_family="DM Sans",
    xaxis=dict(gridcolor="#2a2a2a", linecolor="#333"),
    yaxis=dict(gridcolor="#2a2a2a", linecolor="#333"),
)

# ─── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏎️ OpenF1\n### Dashboard")
    st.markdown("---")

    year = st.selectbox("Season", list(range(2025, 2022, -1)), index=0)

    # Meetings
    with st.spinner("Loading meetings…"):
        meetings_raw = fetch("meetings", {"year": year})
    meetings_df = df(meetings_raw)

    meeting_options = {}
    if not meetings_df.empty and "meeting_name" in meetings_df.columns:
        for _, row in meetings_df.iterrows():
            meeting_options[row["meeting_name"]] = row["meeting_key"]

    selected_meeting_name = st.selectbox(
        "Race / Grand Prix",
        ["All"] + list(meeting_options.keys()),
        index=0,
    )
    selected_meeting_key = meeting_options.get(selected_meeting_name)

    # Sessions
    session_options = {}
    if selected_meeting_key:
        sessions_raw = fetch("sessions", {"meeting_key": selected_meeting_key})
        sessions_df = df(sessions_raw)
        if not sessions_df.empty and "session_name" in sessions_df.columns:
            for _, row in sessions_df.iterrows():
                label = f"{row['session_name']}"
                session_options[label] = row["session_key"]

    selected_session_name = st.selectbox(
        "Session",
        ["All"] + list(session_options.keys()),
        index=0,
        disabled=(not session_options),
    )
    selected_session_key = session_options.get(selected_session_name)

    # Drivers from selected session / meeting
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

# ─── Header ───────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"## {year} Formula 1 Season")
    subtitle = selected_meeting_name if selected_meeting_name != "All" else "Full Season Overview"
    if selected_session_name != "All":
        subtitle += f" · {selected_session_name}"
    st.caption(subtitle)
with col_h2:
    st.markdown("")  # spacer

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_laps, tab_stints, tab_pit, tab_positions, tab_weather = st.tabs([
    "📊 Overview", "⏱ Lap Times", "🛞 Stints", "🔧 Pit Stops", "🏁 Positions", "🌦 Weather"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ══════════════════════════════════════════════════════════════════════
with tab_overview:
    # Session results
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
            # Merge driver names
            if not drivers_df.empty and "driver_number" in results_df.columns:
                merge_cols = [c for c in ["driver_number", "full_name", "team_name", "team_colour"] if c in drivers_df.columns]
                results_df = results_df.merge(
                    drivers_df[merge_cols].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )

            st.markdown("### Session Results")

            # Filter by driver / team
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
        st.markdown("### Driver Grid")
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
                if not color.startswith("#"):
                    color = "#" + color
                st.markdown(f"""
                <div style="background:#1a1a1a;border-left:4px solid {color};
                     border-radius:6px;padding:12px 14px;margin-bottom:10px;">
                  <div style="font-size:28px;font-family:'Bebas Neue',sans-serif;
                       letter-spacing:2px;color:{color}">#{row.get('driver_number','')}</div>
                  <div style="font-size:15px;font-weight:500">{row.get('full_name','')}</div>
                  <div style="font-size:12px;color:#888;margin-top:2px">{row.get('team_name','')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Select a season and race/session to see driver and result data.")

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
            # Merge names
            if not drivers_df.empty and "driver_number" in laps_df.columns:
                laps_df = laps_df.merge(
                    drivers_df[["driver_number","full_name","team_name","team_colour"]].drop_duplicates("driver_number"),
                    on="driver_number", how="left"
                )

            if selected_team and "team_name" in laps_df.columns:
                laps_df = laps_df[laps_df["team_name"] == selected_team]

            if "lap_duration" in laps_df.columns and "lap_number" in laps_df.columns:
                laps_plot = laps_df.dropna(subset=["lap_duration"])

                # Metrics row
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Laps", int(laps_plot["lap_number"].max()) if not laps_plot.empty else "—")
                c2.metric("Fastest Lap", f"{laps_plot['lap_duration'].min():.3f}s" if not laps_plot.empty else "—")
                if "full_name" in laps_plot.columns:
                    fastest_driver = laps_plot.loc[laps_plot["lap_duration"].idxmin(), "full_name"] if not laps_plot.empty else "—"
                    c3.metric("Fastest Driver", fastest_driver)

                st.markdown("### Lap Time Chart")
                color_col = "full_name" if "full_name" in laps_plot.columns else None
                fig = px.line(
                    laps_plot.sort_values("lap_number"),
                    x="lap_number", y="lap_duration",
                    color=color_col,
                    labels={"lap_number": "Lap", "lap_duration": "Time (s)", "full_name": "Driver"},
                    title="Lap Times by Lap",
                )
                fig.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### Lap Time Distribution")
                fig2 = px.box(
                    laps_plot,
                    x=color_col if color_col else None,
                    y="lap_duration",
                    color=color_col,
                    labels={"lap_duration": "Lap Time (s)"},
                )
                fig2.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### Raw Lap Data")
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

            st.markdown("### Tyre Strategy")
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
                st.markdown("### Pit Stop Duration by Driver")
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
                pos_df["date"] = pd.to_datetime(pos_df["date"])
                pos_df = pos_df.sort_values("date")

            if "position" in pos_df.columns and "date" in pos_df.columns:
                st.markdown("### Position Over Time")
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
                weather_df["date"] = pd.to_datetime(weather_df["date"])
                weather_df = weather_df.sort_values("date")

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

                st.markdown("### Temperature Over Session")
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
                    st.markdown("### Wind Speed")
                    fig2 = px.area(weather_df, x="date", y="wind_speed",
                                   labels={"date":"Time","wind_speed":"Wind Speed (m/s)"})
                    fig2.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig2, use_container_width=True)

            st.dataframe(weather_df, use_container_width=True, hide_index=True)
