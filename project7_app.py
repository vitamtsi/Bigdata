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
df["year"] = df["month"].dt.year
df["month_num"] = df["month"].dt.month
df["month_name"] = df["month"].dt.strftime("%B")

st.title("🌍 European NO₂ Dashboard (2018–2025)")

# --------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------
st.sidebar.header("Filters")

# Select Cities
cities = sorted(df["City"].unique())
selected_cities = st.sidebar.multiselect(
    "Select Cities:",
    cities,
    default=cities[:5]
)

# Year range (for first graph)
years = sorted(df["year"].unique())
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years))
)

# NEW: Filters for Month-by-Month graph 🌙
st.sidebar.markdown("---")
st.sidebar.subheader("Monthly Comparison Chart Filters")

selected_year_for_month = st.sidebar.selectbox(
    "Select Year for Monthly Chart:",
    years,
    index=years.index(2025)
)

months_map = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

selected_month = st.sidebar.selectbox(
    "Select Month:",
    list(months_map.values()),
    index=8  # default September
)

selected_month_num = list(months_map.keys())[list(months_map.values()).index(selected_month)]

# Filter final dataset
df_filtered = df[
    (df["City"].isin(selected_cities)) &
    (df["year"] >= selected_years[0]) &
    (df["year"] <= selected_years[1])
]

# --------------------------------------------------------
# ORIGINAL BEAUTIFUL TIME SERIES GRAPH
# --------------------------------------------------------
st.subheader("📈 NO₂ over Time (with Year Range Filter)")

time_chart = (
    alt.Chart(df_filtered)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:T", title="Date"),
        y=alt.Y("NO2:Q", title="NO₂ (µg/m³)"),
        color="City:N",
        tooltip=["City", "month:T", "NO2"]
    )
)

st.altair_chart(time_chart, use_container_width=True)

# --------------------------------------------------------
# 1) AVERAGE NO₂ 2018–2025
# --------------------------------------------------------
st.subheader("📊 Average NO₂ Concentration by European Capital (2018–2025)")

avg_chart = (
    alt.Chart(df_filtered)
    .mark_bar()
    .encode(
        x=alt.X("City:N", sort="-y"),
        y=alt.Y("mean(NO2):Q", title="Average NO₂ (µg/m³)"),
        color="City:N",
        tooltip=["City", "mean(NO2)"]
    )
)

st.altair_chart(avg_chart, use_container_width=True)

# --------------------------------------------------------
# 2) MONTH-BY-MONTH FILTERING GRAPH (dynamic)
# --------------------------------------------------------
st.subheader(f"📅 NO₂ Levels by City — {selected_month} {selected_year_for_month}")

df_month = df[
    (df["year"] == selected_year_for_month) &
    (df["month_num"] == selected_month_num)
]

month_chart = (
    alt.Chart(df_month)
    .mark_bar()
    .encode(
        x=alt.X("City:N", sort="-y"),
        y="NO2:Q",
        color="City:N",
        tooltip=["City", "NO2"]
    )
)

st.altair_chart(month_chart, use_container_width=True)

# --------------------------------------------------------
# 3) TREND / CORRELATION GRAPH
# --------------------------------------------------------
st.subheader("📉 Correlation Between Time and NO₂ Concentration")

trend_chart = (
    alt.Chart(df_filtered)
    .mark_line(point=True)
    .encode(
        x="month:T",
        y="NO2:Q",
        color="City:N",
        tooltip=["City", "month:T", "NO2"]
    )
)

st.altair_chart(trend_chart, use_container_width=True)

st.success("Dashboard loaded successfully! 🚀")
