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

    # --- Load model ---
    try:
        model = joblib.load("no2_rf_pipeline.pkl")
        st.success("Model loaded successfully!")
    except Exception as e:
        st.error(f"Model could not be loaded: {e}")
        st.stop()

    # --- Load feature dataset ---
    try:
        df_feat = pd.read_csv("no2_with_features.csv", parse_dates=["month"])
    except Exception as e:
        st.error(f"Could not load no2_with_features.csv — {e}")
        st.stop()

    # --- Basic validation ---
    if "City" not in df_feat.columns or "month" not in df_feat.columns or "NO2" not in df_feat.columns:
        st.error("no2_with_features.csv is missing required columns (City, month, NO2).")
        st.stop()

    # --- UI ---
    city = st.selectbox("Select a city for prediction:", sorted(df_feat["City"].dropna().unique()))
    horizon = st.slider("Forecast horizon (months):", 1, 12, 6)

    st.subheader(f"Forecasting next {horizon} months for **{city}**")

    city_df = df_feat[df_feat["City"] == city].sort_values("month").copy()
    if city_df.empty:
        st.error("No data found for this city in no2_with_features.csv.")
        st.stop()

    last_row = city_df.iloc[-1]

    # --- Starting state from last observed row ---
    current_year = int(last_row.get("year", last_row["month"].year))
    current_month_num = int(last_row.get("month_num", last_row["month"].month))

    last_NO2 = float(last_row["NO2"])
    last_prev = float(last_row.get("NO2_prev_month", last_NO2))
    last_roll3 = float(last_row.get("NO2_roll3", last_NO2))

    # --- IMPORTANT: Use exact feature columns order expected by the model ---
    if hasattr(model, "feature_names_in_"):
        REQUIRED = list(model.feature_names_in_)
    else:
        # fallback if feature_names_in_ is not available
        REQUIRED = ["City", "season", "year", "month_num", "dayofyear", "NO2_prev_month", "NO2_roll3"]

    preds = []
    future_months = []

    def month_to_season(m: int) -> int:
        # 1=winter, 2=spring, 3=summer, 4=autumn (same as Project 5)
        return (m % 12) // 3 + 1

    for i in range(1, horizon + 1):
        # compute future year + month
        future_month_num = ((current_month_num - 1 + i) % 12) + 1
        extra_years = (current_month_num - 1 + i) // 12
        future_year = current_year + extra_years

        # dayofyear (use mid-month to be consistent)
        day_of_year = int(pd.Timestamp(int(future_year), int(future_month_num), 15).day_of_year)
        season_value = int(month_to_season(int(future_month_num)))

        # build one-row input with correct types
        row = {
            "City": str(city),
            "season": int(season_value),
            "year": int(future_year),
            "month_num": int(future_month_num),
            "dayofyear": int(day_of_year),
            "NO2_prev_month": float(last_NO2),
            "NO2_roll3": float(last_roll3),
        }

        # ensure correct column order + only required columns
        X = pd.DataFrame([[row.get(c, None) for c in REQUIRED]], columns=REQUIRED)

        # force numeric types (critical for sklearn imputers/scalers)
        for col in ["season", "year", "month_num", "dayofyear"]:
            if col in X.columns:
                X[col] = pd.to_numeric(X[col], errors="coerce").astype("Int64")
        for col in ["NO2_prev_month", "NO2_roll3"]:
            if col in X.columns:
                X[col] = pd.to_numeric(X[col], errors="coerce").astype(float)
        if "City" in X.columns:
            X["City"] = X["City"].astype(str)

        # predict
        try:
            y_pred = float(model.predict(X)[0])
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            st.write("Debug input row sent to model:")
            st.dataframe(X)
            st.stop()

        preds.append(y_pred)
        future_months.append(pd.Timestamp(int(future_year), int(future_month_num), 1).strftime("%b %Y"))

        # update rolling state for next step
        last_roll3 = (last_roll3 * 3 - last_prev + y_pred) / 3.0
        last_prev = last_NO2
        last_NO2 = y_pred

    forecast_df = pd.DataFrame({"Month": future_months, "Predicted NO2": preds})

# 1) Chart FIRST
fig5 = px.line(
    forecast_df,
    x="Month",
    y="Predicted NO2",
    markers=True,
    title=f"Forecasted NO₂ for {city}"
)
st.plotly_chart(fig5, use_container_width=True)

# 2) Table AFTER
st.write("### 📅 Forecast Table")
st.dataframe(forecast_df, use_container_width=True)
