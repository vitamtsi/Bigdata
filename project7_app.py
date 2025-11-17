import streamlit as st
import pandas as pd
import plotly.express as px

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
    "🤖 Machine Learning Prediction"
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

    # --- BUILD INITIAL FIG ---
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

    # --- SORT HOVER ORDER ---
    # Sort traces at each x (month) by descending NO2 value
    # EU27 gets absolute top priority
    sorted_traces = sorted(
        fig.data,
        key=lambda t: (
            0 if t.name == "EU27 (aggregate)" else 1,
            -max(t.y)  # descending by NO2
        )
    )
    fig.data = tuple(sorted_traces)

    # AXIS FORMATTING
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

    # Month name list
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    # Select year
    selected_year = st.selectbox("Select Year:", sorted(df["year"].unique()), index=7)

    # Select month by name
    selected_month_name = st.selectbox(
        "Select Month:",
        list(month_names.values()),
        index=1  # February (just default)
    )

    # Convert back to month number
    selected_month = [num for num, name in month_names.items() if name == selected_month_name][0]

    # Filter data
    df_m = df[(df["year"] == selected_year) & (df["month_num"] == selected_month)].copy()

    # EU27 mean value
    eu_value = df_m[df_m["City"] == "EU27 (aggregate)"]["NO2"].mean()

    # Sort cities by NO2 descending
    df_m = df_m.sort_values("NO2", ascending=False)

    # Chart title month
    month_title = selected_month_name + " " + str(selected_year)

    # Plot
    fig2 = px.bar(
        df_m,
        x="City",
        y="NO2",
        color="NO2",
        color_continuous_scale="RdYlGn_r",  # same palette as correlation
        title=f"NO₂ Levels by City — {month_title}"
    )

    # EU average line
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
        # ŠEIT GALVENĀ IZMAIŅA:
        color_continuous_scale="RdYlGn_r",
        title="Correlation Between Time and NO₂ Concentration"
    )

    fig3.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig3, use_container_width=True)

# ========================================================

# ========================================================
# TAB 4 — SEASONAL VARIATION (with custom season colors)
# ========================================================
with tab4:
    st.header("🍁 Seasonal Variation of NO₂ Concentration")

    # Assign seasons manually
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

    # Custom season colors
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
                          color_continuous_scale="RdYlGn_r",
                          title="Prediction vs EU27 Long-Term Average")

        st.plotly_chart(fig_pred, use_container_width=True)
