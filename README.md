# 🏎️ OpenF1 Dashboard

For years I've been playing around with APIs — most notably the F1 APIs — but going further than calling just a couple of endpoints never really happened. When Streamlit was shown to me during a webinar, I decided to finally change that and build a proper dashboard using Python, Streamlit, and with some help from my buddy Claude. 😄

Live demo: [f1-app-dashboard.streamlit.app](https://f1-app-dashboard.streamlit.app)

---

## What it does

A Formula 1 dashboard powered by the [OpenF1 API](https://openf1.org), covering seasons from 2023 onwards. The main view shows the Driver and Constructor Championship standings for the selected season, with a cumulative points progression chart across all races. From there you can drill down into any individual race and session to explore the data further.

**Tabs:**
- 🏆 **Championship** - Driver and Constructor standings with points progression across the season
- 📊 **Race Results** - Session results and driver grid for the selected race
- ⏱ **Lap Times** - Lap time chart and distribution per session
- 🛞 **Stints** - Tyre strategy visualised as a Gantt chart
- 🔧 **Pit Stops** - Pit stop durations per driver
- 🏁 **Positions** - Position changes throughout a session
- 🌦 **Weather** - Air/track temperature, wind speed and humidity over a session

---

## Tech stack

- [Python](https://python.org)
- [Streamlit](https://streamlit.io)
- [OpenF1 API](https://openf1.org) — free, open-source F1 data from 2023+
- [Plotly](https://plotly.com/python/) — interactive charts
- [Pandas](https://pandas.pydata.org/)

---

## Run it locally

```bash
git clone https://github.com/Jorginton/f1-streamlit-dashboard
cd f1-streamlit-dashboard
pip install -r requirements.txt
streamlit run openf1_dashboard.py
```

Opens at `http://localhost:8501`. No API key needed — OpenF1 is fully open.

---

## About

Created by **Jorg van de Ven**

🌐 [jorgvandeven.nl](https://jorgvandeven.nl/?utm_source=github&utm_medium=referral&utm_campaign=f1_dashboard)  
💼 [linkedin.com/in/jorgvandeven](https://www.linkedin.com/in/jorgvandeven/)
