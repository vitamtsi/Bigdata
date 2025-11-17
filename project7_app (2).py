import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="NO₂ Prediction Dashboard", page_icon="🌍")

@st.cache_resource
def load_model():
    return joblib.load("no2_rf_pipeline.pkl")

model = load_model()
FEATURES = model.feature_names_in_

st.title("🌍 NO₂ Prediction Dashboard")

st.sidebar.header("Input")

city = st.sidebar.text_input("City", "Vienna (Austria)")
season = st.sidebar.selectbox("Season", [1,2,3,4])
year = st.sidebar.number_input("Year", 2000, 2030, 2024)
month_num = st.sidebar.slider("Month", 1, 12, 4)
dayofyear = st.sidebar.slider("Day of year", 1, 366, 92)
prev_no2 = st.sidebar.number_input("Previous month NO₂", 0.0, 200.0, 20.0)
roll3 = st.sidebar.number_input("3-month rolling NO₂", 0.0, 200.0, 21.0)

row = {
    "City": city,
    "season": season,
    "year": year,
    "month_num": month_num,
    "dayofyear": dayofyear,
    "NO2_prev_month": prev_no2,
    "NO2_roll3": roll3
}

df = pd.DataFrame([row])[list(FEATURES)]

if st.button("Predict"):
    prediction = model.predict(df)[0]
    st.success(f"Predicted NO₂: **{prediction:.2f} µg/m³**")
