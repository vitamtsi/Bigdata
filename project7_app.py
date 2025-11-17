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

# Multiple cities instead of one
all_cities = sorted(df["City"].unique())
selected_cities = st.sidebar.multiselect(
    "Select cities:",
    all_cities,
    default=["Vienna (Austria)", "Paris (France)"]
)

# Date range filter
min_date = df["month"].min()
max_date = df["month"].max()

date_range = st.sidebar.slider(
    "Select date range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter the dataset
filtered = df[
    (df["City"].isin(selected_cities)) &
    (df["month"].between(date_range[0], date_range[1]))
]

# --------------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------------
st.title("🌍 European NO₂ Concentration Dashboard")
st.write("Compare NO₂ pollution levels across multiple European capital cities.")

# --------------------------------------------------------
# LINE CHART (multi-city)
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
# CITY COMPARISON TABLE
# --------------------------------------------------------
st.subheader("Average NO₂ Levels by City")

avg_table = (
    filtered.groupby("City")["NO2"]
    .mean()
    .round(2)
    .reset_index()
    .sort_values("NO2", ascending=False)
)

st.dataframe(avg_table, use_container_width=True)

# --------------------------------------------------------
# UX / HEURISTIC NOTES
# --------------------------------------------------------
with st.expander("ℹ Usability Notes (for Project 7 Requirements)"):
    st.write("""
    **This dashboard was designed with the following HCI/UX principles:**

    -  *Visibility & User Control*: Users can interactively filter cities and date ranges.
    -  *Consistency*: The same color is applied to each city across graphs.
    -  *Feedback*: Filters update charts instantly.
    -  *Minimal Cognitive Load*: Simple visual representation of pollution trends.
    -  *Heuristic Evaluation*: Tested with basic user interactions (filters, sliders).
    """)
