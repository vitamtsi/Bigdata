import streamlit as st
import pandas as pd
import plotly.express as px
import sklearn
import joblib
import numpy as np

st.sidebar.write("⚙️ Streamlit sklearn version:", sklearn.__version__)

st.set_page_config(page_title="NO₂concentrations across European capital cities", page_icon="🌍", layout="wide")

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("clean_no2_long.csv", parse_dates=["month"])
    df["year"] = df["month"].dt.year
    df["month_num"] = df["month"].dt.month
    return df

df = load_data()

st.title("🌍 European NO₂ Dashboard (2018–2025)")

# ========================================================
#  TABS
# ========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 NO₂ Over Time",
    "🏙️ NO₂ Levels by City",
    "📉 Correlation (Time vs NO₂)",
    "🍁 Seasonal Variation",
    "🔮 Forecasting Model"
])

# ========================================================
# TAB 1 — TIME SERIES
# ========================================================
with tab1:
    st.header("📈 Dynamics of NO₂concentrations across European capital cities")

    # Priority cities shown first
    priority_cities = [
        "EU27 (aggregate)",
        "Riga (Latvia)",
        "Bucharest (Romania)",
        "Tallinn (Estonia)"
    ]

    other_cities = sorted([c for c in df["City"].unique() if c not in priority_cities])
    ordered_cities = priority_cities + other_cities

    cities = st.multiselect(
        "Select cities:",
        ordered_cities,
        default=priority_cities
    )

    years = st.slider("Select year range:", 2018, 2025, (2023, 2025))

    df_t = df[
        (df["City"].isin(cities)) &
        (df["year"].between(years[0], years[1]))
    ].copy()

    df_t["month_short"] = df_t["month"].dt.strftime("%b")
    df_t["year"] = df_t["month"].dt.year

    # COLOR MAP — EU27 ALWAYS RED
    base_colors = px.colors.qualitative.Set2
    color_map = {city: base_colors[i % len(base_colors)] for i, city in enumerate(ordered_cities)}
    color_map["EU27 (aggregate)"] = "red"

    fig = px.line(
        df_t,
        x="month",
        y="NO2",
        color="City",
        color_discrete_map=color_map,
        markers=True,
        hover_data={
            "City": True,
            "NO2": True,
            "month_short": True,
            "year": True,
            "month": False
        },
        title="NO₂ Over Time (Selected Cities)"
    )

    # SORT hover order
    sorted_traces = sorted(
        fig.data,
        key=lambda t: (
            0 if t.name == "EU27 (aggregate)" else 1,
            -max(t.y)
        )
    )
    fig.data = tuple(sorted_traces)

    fig.update_xaxes(tickformat="%b\n%Y", showgrid=True)
    fig.update_yaxes(showgrid=True)

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# ========================================================
# TAB 2 — CITY MONTHLY LEVELS
# ========================================================
with tab2:
    st.header("🏙️ Monthly NO₂ Levels by European Capitals")

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    selected_year = st.selectbox("Select Year:", sorted(df["year"].unique()), index=7)

    selected_month_name = st.selectbox(
        "Select Month:",
        list(month_names.values()),
        index=1
    )

    selected_month = [num for num, name in month_names.items() if name == selected_month_name][0]

    df_m = df[(df["year"] == selected_year) & (df["month_num"] == selected_month)].copy()

    eu_value = df_m[df_m["City"] == "EU27 (aggregate)"]["NO2"].mean()

    df_m = df_m.sort_values("NO2", ascending=False)

    month_title = selected_month_name + " " + str(selected_year)

    fig2 = px.bar(
        df_m,
        x="City",
        y="NO2",
        color="NO2",
        color_continuous_scale="RdYlGn_r",
        title=f"NO₂ Levels by City — {month_title}"
    )

    fig2.add_hline(
        y=eu_value,
        line_dash="dash",
        line_color="black",
        annotation_text="EU27 average",
        annotation_position="top left"
    )

    fig2.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig2, use_container_width=True)

# ========================================================
# TAB 3 — CORRELATION
# ========================================================
with tab3:
    st.header("📉 Correlation Between Time and NO₂ (2018–2025)")

    df_corr = df.copy()
    df_corr["time_index"] = (df_corr["month"] - df_corr["month"].min()).dt.days

    correlations = (
        df_corr.groupby("City")[["time_index", "NO2"]]
        .corr()
        .iloc[0::2]["NO2"]
        .reset_index()
        .rename(columns={"NO2": "correlation"})
    )

    fig3 = px.bar(
        correlations.sort_values("correlation"),
        x="City",
        y="correlation",
        color="correlation",
        color_continuous_scale="RdYlGn_r",
        title="Correlation Between Time and NO₂ Concentration"
    )

    fig3.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig3, use_container_width=True)

# ========================================================
# TAB 4 — SEASONAL VARIATION
# ========================================================
with tab4:
    st.header("🍁 Seasonal Variation of NO₂ Concentration")

    def assign_season(m):
        if m in [12, 1, 2]:
            return "Winter"
        elif m in [3, 4, 5]:
            return "Spring"
        elif m in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"

    df["season"] = df["month_num"].apply(assign_season)

    season_colors = {
        "Winter": "purple",
        "Spring": "gold",
        "Summer": "green",
        "Autumn": "orange"
    }

    fig4 = px.box(
        df,
        x="season",
        y="NO2",
        color="season",
        color_discrete_map=season_colors,
        category_orders={"season": ["Winter", "Spring", "Summer", "Autumn"]},
        hover_data={"City": True, "NO2": ":.2f", "season": True, "month_num": False},
        title="Seasonal Variation of NO₂ Concentration in European Capitals"
    )

    st.plotly_chart(fig4, use_container_width=True)


# ========================================================
# TAB 5 — FORECASTING MODEL
# ========================================================
with tab5:
    st.header("🔮 Forecasting Future NO₂ Concentrations")

    st.write("This tab uses the trained Random Forest pipeline to forecast future monthly NO₂ values.")

    # Try loading the model
    try:
        model = joblib.load("no2_rf_pipeline.pkl")
        st.success("Model loaded successfully!")
    except Exception as e:
        st.error(f"Model could not be loaded: {e}")
        st.stop()

    # Load feature engineered dataset
    try:
        df_feat = pd.read_csv("no2_with_features.csv", parse_dates=["month"])
    except:
        st.error("Could not load no2_with_features.csv — upload it to the Streamlit app folder.")
        st.stop()

    # UI
    city = st.selectbox("Select a city for prediction:", sorted(df_feat["City"].unique()))

    horizon = st.slider("Forecast horizon (months):", 1, 12, 6)

    st.subheader(f"Forecasting next {horizon} months for **{city}**")

    # Filter last known values
    city_df = df_feat[df_feat["City"] == city].sort_values("month")

    last_row = city_df.iloc[-1]

    preds = []
    future_months = []

    current_year = last_row["year"]
    current_month_num = last_row["month_num"]
    last_NO2 = last_row["NO2"]
    last_prev = last_row["NO2_prev_month"]
    last_roll3 = last_row["NO2_roll3"]
    last_dayofyear = last_row["dayofyear"]

    for i in range(1, horizon + 1):
        future_month_num = ((current_month_num - 1 + i) % 12) + 1
        extra_years = (current_month_num - 1 + i) // 12
        future_year = current_year + extra_years

        day_of_year = pd.Timestamp(future_year, future_month_num, 15).day_of_year

        season_value = (
            1 if future_month_num in [12, 1, 2] else
            2 if future_month_num in [3, 4, 5] else
            3 if future_month_num in [6, 7, 8] else
            4
        )

        X = pd.DataFrame([{
            "City": city,
            "season": season_value,
            "year": future_year,
            "month_num": future_month_num,
            "dayofyear": day_of_year,
            "NO2_prev_month": last_NO2,
            "NO2_roll3": last_roll3
        }])

        y_pred = model.predict(X)[0]

        preds.append(y_pred)
        future_months.append(f"{pd.Timestamp(future_year, future_month_num, 1).strftime('%b %Y')}")

        last_roll3 = (last_roll3 * 3 - last_prev + y_pred) / 3
        last_prev = last_NO2
        last_NO2 = y_pred

    # Table
    forecast_df = pd.DataFrame({
        "Month": future_months,
        "Predicted NO2": preds
    })

    st.write("### 📅 Forecast Table")
    st.dataframe(forecast_df)

    # Chart
    fig5 = px.line(
        forecast_df,
        x="Month",
        y="Predicted NO2",
        markers=True,
        title=f"Forecasted NO₂ for {city}"
    )

    st.plotly_chart(fig5, use_container_width=True)
