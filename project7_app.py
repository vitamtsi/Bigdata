import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

st.set_page_config(
    page_title="Spatio-temporal Analysis of Urban NO₂ in European Capitals (2018–2025)",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("clean_no2_long.csv", parse_dates=["month"])
    df["year"] = df["month"].dt.year
    df["month_num"] = df["month"].dt.month
    df["dayofyear"] = df["month"].dt.dayofyear
    df["month_short"] = df["month"].dt.strftime("%b")
    df["month_label"] = df["month"].dt.strftime("%b %Y")
    return df

df = load_data()

# Optional: load model lazily only when Tab 5 is used
@st.cache_resource
def load_no2_model():
    model = joblib.load("no2_rf_pipeline.pkl")
    features = getattr(model, "feature_names_in_", None)
    if features is None:
        raise RuntimeError("Model has no feature_names_in_. Check Project 5 training.")
    return model, list(features)


st.title("🌍 Spatio-temporal Analysis of Urban NO₂ in European Capitals (2018–2025)")

# ========================================================
#  TABS
# ========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Temporal Dynamics",
    "🏙️ City-level Monthly Profiles",
    "📉 Temporal Correlation Structure",
    "🍁 Seasonal Concentration Patterns",
    "🔮 Predictive Forecasting"
])

# ========================================================
# TAB 1 — NO₂ OVER TIME
# ========================================================
with tab1:
    st.header("📈 Temporal Dynamics of NO₂")

    # Default cities: Riga, Vilnius, Tallinn, EU27
    default_cities = [
        "Riga (Latvia)",
        "Vilnius (Lithuania)",
        "Tallinn (Estonia)",
        "EU27 (aggregate)",
    ]
    all_cities = sorted(df["City"].unique())
    default_selection = [c for c in default_cities if c in all_cities]

    cities = st.multiselect(
        "Select cities to display:",
        all_cities,
        default=default_selection
    )

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    # start from 2023 by default if available
    default_start = 2023 if 2023 >= min_year else min_year

    years = st.slider(
        "Select year range:",
        min_value=min_year,
        max_value=max_year,
        value=(default_start, max_year),
    )

    df_t = df[
        (df["City"].isin(cities)) &
        (df["year"].between(years[0], years[1]))
    ].copy()

    # Ensure EU27 is always in selection & red if present
    color_map = {"EU27 (aggregate)": "red"}
    # Other cities get default Plotly palette

    # Use custom_data for nice hover labels
    df_t["year_int"] = df_t["year"]
    fig1 = px.line(
        df_t,
        x="month",
        y="NO2",
        color="City",
        color_discrete_map=color_map,
        markers=True,
        title="NO₂ Concentration Over Time"
    )

    fig1.update_traces(
        customdata=np.stack(
            [df_t["City"], df_t["NO2"], df_t["month_short"], df_t["year_int"]],
            axis=-1
        ),
        hovertemplate=(
            "City = %{customdata[0]}<br>"
            "NO₂ = %{customdata[1]:.1f} µg/m³<br>"
            "month = %{customdata[2]}<br>"
            "year = %{customdata[3]}<extra></extra>"
        )
    )

    fig1.update_layout(
        xaxis=dict(
            dtick="M1",
            tickformat="%b\n%Y",
            showgrid=True
        ),
        yaxis=dict(showgrid=True)
    )

    st.plotly_chart(fig1, use_container_width=True)

# ========================================================
# TAB 2 — CITY MONTHLY LEVELS
# ========================================================
with tab2:
    st.header("🏙️ City-level Monthly NO₂ Profiles")

    # Month names for dropdown
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    selected_year = st.selectbox(
        "Select Year:",
        sorted(df["year"].unique()),
        index=sorted(df["year"].unique()).index(2025)
        if 2025 in df["year"].unique() else 0
    )

    # display month names but map to number
    month_label = st.selectbox(
        "Select Month:",
        list(month_names.values()),
        index=8  # September by default (0-based index)
    )
    # reverse map
    inv_month = {v: k for k, v in month_names.items()}
    selected_month = inv_month[month_label]

    df_m = df[
        (df["year"] == selected_year) &
        (df["month_num"] == selected_month)
    ].copy()

    if df_m.empty:
        st.warning("No data available for this year/month combination.")
    else:
        eu_value = df_m[df_m["City"] == "EU27 (aggregate)"]["NO2"].mean()

        # classify relative to EU27 average
        df_m["relative"] = df_m["NO2"].apply(
            lambda x: "Above EU average" if x > eu_value
            else ("At EU average" if np.isclose(x, eu_value, atol=1e-6)
                  else "Below EU average")
        )

        # same colour logic as correlation-style (high = red, low = green)
        color_map_rel = {
            "Above EU average": "#d73027",   # red
            "At EU average": "#fee08b",      # yellow
            "Below EU average": "#1a9850"    # green
        }

        # sort by NO2 descending (highest at top in bar chart)
        df_m = df_m.sort_values("NO2", ascending=False)

        month_name_long = f"{month_label} {selected_year}"

        fig2 = px.bar(
            df_m,
            x="City",
            y="NO2",
            color="relative",
            color_discrete_map=color_map_rel,
            title=f"NO₂ Levels by City — {month_name_long}",
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
        color_continuous_scale="RdYlGn_r",  # negative (improvement) → green, positive (worsening) → red
        title="Pearson Correlation Between Time and NO₂ Concentration"
    )

    fig3.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig3, use_container_width=True)

# ========================================================
# TAB 4 — SEASONAL VARIATION
# ========================================================
with tab4:
    st.header("🍁 Seasonal Patterns of NO₂ Concentration")

    def assign_season(m):
        if m in [12, 1, 2]:
            return "Winter"
        elif m in [3, 4, 5]:
            return "Spring"
        elif m in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"

    df_season = df.copy()
    df_season["season"] = df_season["month_num"].apply(assign_season)

    season_colors = {
        "Winter": "purple",
        "Spring": "gold",
        "Summer": "green",
        "Autumn": "orange"
    }

    fig4 = px.box(
        df_season,
        x="season",
        y="NO2",
        color="season",
        color_discrete_map=season_colors,
        category_orders={"season": ["Winter", "Spring", "Summer", "Autumn"]},
        title="Seasonal Distribution of NO₂ Concentrations in European Capitals"
    )

    # add city info to tooltip
    fig4.update_traces(
        customdata=np.stack(
            [df_season["City"], df_season["season"], df_season["NO2"]],
            axis=-1
        ),
        hovertemplate=(
            "City = %{customdata[0]}<br>"
            "Season = %{customdata[1]}<br>"
            "NO₂ = %{customdata[2]:.1f} µg/m³<extra></extra>"
        )
    )

    st.plotly_chart(fig4, use_container_width=True)

# ========================================================
# TAB 5 — PREDICTIVE FORECASTING (OPTION A)
# ========================================================
with tab5:
    st.header("🔮 Forecasting Future NO₂ with the Trained Model")

    st.markdown(
        "This tab uses the **Random Forest regression pipeline** trained in Project 5 "
        "(`no2_rf_pipeline.pkl`) to generate **multi-step monthly forecasts** for a "
        "selected capital city."
    )

    try:
        model, REQUIRED = load_no2_model()
    except Exception as e:
        st.error(f"Model could not be loaded: {e}")
        st.stop()

    cities_for_forecast = sorted(df["City"].unique())
    # default to Riga if present
    default_city_index = cities_for_forecast.index("Riga (Latvia)") if "Riga (Latvia)" in cities_for_forecast else 0

    city = st.selectbox(
        "Select city for forecasting:",
        cities_for_forecast,
        index=default_city_index
    )

    horizon = st.slider(
        "Forecast horizon (months ahead):",
        min_value=3,
        max_value=24,
        value=12
    )

    df_city = df[df["City"] == city].sort_values("month").copy()

    if df_city.shape[0] < 3:
        st.warning("Not enough historical data for this city to build a rolling forecast.")
    else:
        # prepare history
        last_known_month = df_city["month"].max()
        history_no2 = df_city["NO2"].tolist()
        last_three = history_no2[-3:]
        last_no2 = history_no2[-1]

        forecasts = []
        current_date = last_known_month

        for step in range(1, horizon + 1):
            next_date = current_date + pd.DateOffset(months=1)

            year = next_date.year
            month_num = next_date.month
            dayofyear = next_date.dayofyear
            season_num = (month_num % 12) // 3 + 1  # same logic as Project 5 (1..4)

            NO2_prev_month = last_no2
            NO2_roll3 = float(np.mean(last_three))

            row = {
                "City": city,
                "season": season_num,
                "year": year,
                "month_num": month_num,
                "dayofyear": dayofyear,
                "NO2_prev_month": NO2_prev_month,
                "NO2_roll3": NO2_roll3,
            }

            # align exactly with training feature order
            X_row = pd.DataFrame([row], columns=REQUIRED)
            pred_val = float(model.predict(X_row)[0])

            forecasts.append({
                "City": city,
                "month": next_date,
                "NO2_pred": pred_val
            })

            # update for next loop
            current_date = next_date
            last_no2 = pred_val
            last_three = (last_three + [pred_val])[-3:]

        df_forecast = pd.DataFrame(forecasts)
        df_forecast["type"] = "Forecast"
        df_forecast["month_label"] = df_forecast["month"].dt.strftime("%b %Y")

        # recent history (last 24 months for context)
        df_hist = df_city.copy()
        df_hist = df_hist.sort_values("month").tail(24)
        df_hist["type"] = "History"
        df_hist = df_hist.rename(columns={"NO2": "NO2_pred"})
        df_hist["month_label"] = df_hist["month"].dt.strftime("%b %Y")

        df_plot = pd.concat([df_hist, df_forecast], ignore_index=True)

        fig5 = px.line(
            df_plot,
            x="month",
            y="NO2_pred",
            color="type",
            color_discrete_map={"History": "blue", "Forecast": "red"},
            line_dash="type",
            markers=True,
            title=f"Historical and Forecasted NO₂ for {city}"
        )

        fig5.update_traces(
            hovertemplate=(
                "Type = %{legendgroup}<br>"
                "NO₂ = %{y:.1f} µg/m³<br>"
                "month = %{x|%b %Y}<extra></extra>"
            )
        )

        fig5.update_layout(
            xaxis=dict(
                dtick="M1",
                tickformat="%b\n%Y",
                showgrid=True
            ),
            yaxis=dict(showgrid=True)
        )

        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("Forecasted Values")
        st.dataframe(
            df_forecast[["month", "NO2_pred"]]
            .assign(month=lambda d: d["month"].dt.strftime("%b %Y"))
            .rename(columns={"month": "Month", "NO2_pred": "Predicted NO₂ (µg/m³)"})
        )

        st.markdown(
            f"- Last observed NO₂ for **{city}**: "
            f"**{history_no2[-1]:.1f} µg/m³** in {last_known_month.strftime('%b %Y')}  \n"
            f"- Mean forecast over next {horizon} months: "
            f"**{df_forecast['NO2_pred'].mean():.1f} µg/m³**  \n"
            f"- Min / Max forecast: "
            f"**{df_forecast['NO2_pred'].min():.1f} / {df_forecast['NO2_pred'].max():.1f} µg/m³**"
        )
