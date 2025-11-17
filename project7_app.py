import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="NO₂ Dashboard", page_icon="🌍", layout="wide")

# --------------------------------------------------------
# 1) LOAD DATA
# --------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("clean_no2_long.csv", parse_dates=["month"])

df = load_data()

# --------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------
st.sidebar.header("Filters")

# MULTI-SELECT CITIES
cities = st.sidebar.multiselect(
    "Select cities:",
    options=sorted(df["City"].unique()),
    default=["Riga (Latvia)", "Tallinn (Estonia)", "EU27 (aggregate)"]
)

# ----- FIX: USE A SLIDER INSTEAD OF CALENDAR -----
min_date = df["month"].min()
max_date = df["month"].max()

date_range = st.sidebar.slider(
    "Select date range (years):",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime())
)

# --------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------
filtered = df.copy()

if cities:
    filtered = filtered[filtered["City"].isin(cities)]

start, end = date_range
filtered = filtered[(filtered["month"] >= start) &
                    (filtered["month"] <= end)]

# --------------------------------------------------------
# TITLE
# --------------------------------------------------------
st.title("🌍 NO₂ Data Explorer")
st.write("Interactive dashboard to explore European NO₂ trends over time.")

# --------------------------------------------------------
# LINE CHART WITH YEAR TICKS
# --------------------------------------------------------
if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    chart = (
        alt.Chart(filtered)
        .mark_line()
        .encode(
            x=alt.X(
                "month:T",
                axis=alt.Axis(
                    format="%Y",         # show only YEAR
                    tickCount="year",     # yearly ticks
                    labelAngle=0
                )
            ),
            y="NO2:Q",
            color="City:N",
            tooltip=["City", "month", "NO2"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

# --------------------------------------------------------
# SHOW RAW DATA
# --------------------------------------------------------
with st.expander("Show filtered data table"):
    st.dataframe(filtered)
