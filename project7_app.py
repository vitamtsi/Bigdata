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
    default=sorted(df["City"].unique())[:3]  # first 3 cities as default
)

# DATE RANGE FILTER
min_date = df["month"].min().to_pydatetime()
max_date = df["month"].max().to_pydatetime()

date_range = st.sidebar.date_input(
    "Select date range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# --------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------
filtered = df.copy()

if cities:
    filtered = filtered[filtered["City"].isin(cities)]

start, end = date_range
filtered = filtered[(filtered["month"] >= pd.to_datetime(start)) &
                    (filtered["month"] <= pd.to_datetime(end))]

# --------------------------------------------------------
# TITLE
# --------------------------------------------------------
st.title("🌍 NO₂ Data Explorer")
st.write("Filter cities and timeframe to explore NO₂ levels across Europe.")

# --------------------------------------------------------
# LINE CHART (WITH YEAR TICKS)
# --------------------------------------------------------
if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    line_chart = (
        alt.Chart(filtered)
        .mark_line()
        .encode(
            x=alt.X(
                "month:T",
                axis=alt.Axis(
                    format="%Y",        # Only show YEAR
                    tickCount="year",   # Tick every year
                    labelAngle=0
                )
            ),
            y="NO2:Q",
            color="City:N",
            tooltip=["City", "month", "NO2"]
        )
        .properties(height=400)
    )

    st.altair_chart(line_chart, use_container_width=True)

# --------------------------------------------------------
# SHOW RAW DATA
# --------------------------------------------------------
with st.expander("Show filtered data table"):
    st.dataframe(filtered)
