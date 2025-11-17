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

st.title("🌍 European NO₂ Dashboard (2018–2025)")

# --------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------
st.sidebar.header("Filters")

cities = sorted(df["City"].unique())
selected_cities = st.sidebar.multiselect("Select Cities:", cities, default=cities[:5])

years = sorted(df["year"].unique())
selected_years = st.sidebar.slider("Select Year Range:", min_value=min(years), max_value=max(years),
                                   value=(min(years), max(years)))

df_filtered = df[
    (df["City"].isin(selected_cities)) &
    (df["year"] >= selected_years[0]) &
    (df["year"] <= selected_years[1])
]

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
# 2) NO₂ LEVELS FOR SEPTEMBER 2025 ONLY
# --------------------------------------------------------
st.subheader("🍂 NO₂ Levels by City in September 2025")

df_sep25 = df[(df["year"] == 2025) & (df["month_num"] == 9)]

sep_chart = (
    alt.Chart(df_sep25)
    .mark_bar()
    .encode(
        x=alt.X("City:N", sort="-y"),
        y="NO2:Q",
        color="City:N",
        tooltip=["City", "NO2"]
    )
)

st.altair_chart(sep_chart, use_container_width=True)

# --------------------------------------------------------
# 3) CORRELATION BETWEEN TIME AND NO₂
# --------------------------------------------------------
st.subheader("📈 Correlation Between Time and NO₂ Concentration")

trend_chart = (
    alt.Chart(df_filtered)
    .mark_line(point=True)
    .encode(
        x="month:T",
        y="NO2:Q",
        color="City:N",
        tooltip=["City", "month", "NO2"]
    )
)

st.altair_chart(trend_chart, use_container_width=True)

st.success("Dashboard loaded successfully! 🚀")
