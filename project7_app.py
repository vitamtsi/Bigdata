import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="NO₂ Dashboard", page_icon="🌍", layout="wide")


# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("clean_no2_long.csv", parse_dates=["month"])

df = load_data()


# --------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------
st.sidebar.header("Filters")

# Multi-city selector
all_cities = sorted(df["City"].unique())
selected_cities = st.sidebar.multiselect(
    "Select cities:",
    all_cities,
    default=[all_cities[0]]
)

# Fix: convert Timestamp → date for Streamlit slider
min_date = df["month"].min().date()
max_date = df["month"].max().date()

date_range = st.sidebar.slider(
    "Select date range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter (convert month to date)
filtered = df[
    (df["City"].isin(selected_cities)) &
    (df["month"].dt.date >= date_range[0]) &
    (df["month"].dt.date <= date_range[1])
]


# --------------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------------
st.title("🌍 European NO₂ Concentration Dashboard")
st.write("Compare NO₂ pollution levels across multiple European capital cities.")


# --------------------------------------------------------
# LINE CHART
# --------------------------------------------------------
st.subheader("NO₂ Over Time")

line_chart = (
    alt.Chart(filtered)
    .mark_line()
    .encode(
        x="month:T",
        y="NO2:Q",
        color="City:N",
        tooltip=["City", "month", "NO2"]
    )
    .properties(height=400)
)

st.altair_chart(line_chart, use_container_width=True)


# --------------------------------------------------------
# AVERAGE TABLE
# --------------------------------------------------------
st.subheader("Average NO₂ Levels by City (Selected Range)")

avg_table = (
    filtered.groupby("City")["NO2"]
    .mean()
    .round(2)
    .reset_index()
    .sort_values("NO2", ascending=False)
)

st.dataframe(avg_table, use_container_width=True)


# --------------------------------------------------------
# HCI/UX NOTES — Project 7 Requirement
# --------------------------------------------------------
with st.expander("ℹ Usability Notes"):
    st.write("""
    ### HCI & UX Improvements
    - **Interactive filtering**: cities and date range
    - **User control & freedom**: easy to reset or expand selections
    - **Clear feedback**: charts update instantly
    - **Consistency**: colors match per city
    - **Minimal cognitive load**: simple, clean layout
    """)
