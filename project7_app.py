import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="NO₂ Dashboard", page_icon="🌍", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("clean_no2_long.csv", parse_dates=["month"])

df = load_data()

st.sidebar.header("Filters")
cities = sorted(df["City"].unique())
selected_city = st.sidebar.selectbox("Choose a city:", cities)

year_min = int(df["month"].dt.year.min())
year_max = int(df["month"].dt.year.max())
selected_year = st.sidebar.slider("Select year:", year_min, year_max, year_max)

filtered = df[
    (df["City"] == selected_city) &
    (df["month"].dt.year == selected_year)
]

st.subheader(f"NO₂ Levels in {selected_city} ({selected_year})")

if filtered.empty:
    st.warning("No data available.")
else:
    chart = (
        alt.Chart(filtered)
        .mark_line(point=True)
        .encode(x="month:T", y="NO2:Q")
    )
    st.altair_chart(chart, use_container_width=True)

st.subheader("Raw Data")
st.dataframe(filtered)
