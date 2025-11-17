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
# TAB 5 — ML-BASED NO₂ PREDICTION
# ========================================================
with tab5:
    st.header("🤖 Machine Learning Prediction of NO₂ Concentration")

    st.write(
        "This tool uses the Random Forest model trained in Project 5 to predict future NO₂ "
        "concentrations based on seasonal patterns, temporal features, and lagged pollution values."
    )

    # ----------------------------
    # Load trained model
    # ----------------------------
    import joblib
    model = joblib.load("no2_rf_pipeline.pkl")

    # Required features:
    required_features = [
        "City", "season", "year", "month_num",
        "dayofyear", "NO2_prev_month", "NO2_roll3"
    ]

    st.subheader("Input Parameters")

    # --- user inputs ---
    city = st.selectbox("Select City:", sorted(df["City"].unique()))
    year = st.number_input("Prediction Year:", min_value=2018, max_value=2035, value=2024)
    month_name = st.selectbox("Select Month:", 
                              ["January","February","March","April","May","June",
                               "July","August","September","October","November","December"])
    
    # convert month → number
    month_map = {
        "January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
        "July":7,"August":8,"September":9,"October":10,"November":11,"December":12
    }
    month_num = month_map[month_name]

    # derive seasonal category
    def get_season(m):
        if m in [12,1,2]:
            return 1  # winter
        elif m in [3,4,5]:
            return 2  # spring
        elif m in [6,7,8]:
            return 3  # summer
        else:
            return 4  # autumn

    season = get_season(month_num)

    # calculate day of year
    import datetime
    dayofyear = datetime.datetime(year, month_num, 1).timetuple().tm_yday

    # estimate previous month NO2 automatically from dataset
    df_city = df[df["City"] == city].sort_values("month")

    # previous month date
    if month_num == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month_num - 1

    # find NO2_prev_month
    prev_value = df_city[
        (df_city["month"].dt.year == prev_year) &
        (df_city["month"].dt.month == prev_month)
    ]["NO2"]

    if len(prev_value) > 0:
        NO2_prev_month = prev_value.iloc[0]
    else:
        NO2_prev_month = float(df_city["NO2"].mean())  # fallback if no data

    # rolling mean (3 months)
    df_city["prev3"] = df_city["NO2"].rolling(3).mean()
    roll_value = df_city[
        (df_city["month"].dt.year == prev_year) &
        (df_city["month"].dt.month == prev_month)
    ]["prev3"]

    if len(roll_value) > 0:
        NO2_roll3 = roll_value.iloc[0]
    else:
        NO2_roll3 = float(df_city["NO2"].rolling(3).mean().iloc[-1])

    st.write("Automatically derived features:")
    st.write(f"• Previous month NO₂: **{NO2_prev_month:.1f}** µg/m³")  
    st.write(f"• 3-month rolling mean: **{NO2_roll3:.1f}** µg/m³")  
    st.write(f"• Season (1–4): **{season}**")  
    st.write(f"• Day of year: **{dayofyear}**")

    # build dataframe for prediction
    input_data = {
        "City": city,
        "season": season,
        "year": year,
        "month_num": month_num,
        "dayofyear": dayofyear,
        "NO2_prev_month": NO2_prev_month,
        "NO2_roll3": NO2_roll3
    }

    input_df = pd.DataFrame([input_data], columns=required_features)

    # ----------- prediction button -----------
    if st.button("Predict NO₂ Level"):
        pred = model.predict(input_df)[0]

        st.subheader("Predicted NO₂ Concentration")
        st.metric(label="NO₂ (µg/m³)", value=f"{pred:.2f}")

        # compare to EU27 mean
        eu_mean = df[df["City"]=="EU27 (aggregate)"]["NO2"].mean()

        if pred > eu_mean + 5:
            color = "red"
            msg = "Above EU27 average — higher pollution expected"
        elif pred < eu_mean - 5:
            color = "green"
            msg = "Below EU27 average — lower pollution expected"
        else:
            color = "gold"
            msg = "Close to EU27 average"

        st.markdown(f"### <span style='color:{color}'>{msg}</span>", unsafe_allow_html=True)

        # show comparison bar
        compare_df = pd.DataFrame({
            "Category": ["Prediction", "EU27 Average"],
            "NO2": [pred, eu_mean]
        })

        fig_pred = px.bar(compare_df, x="Category", y="NO2",
                          color="NO2",
                          color_continuous_scale="RdYlGn_r",
                          title="Prediction vs EU27 Long-Term Average")

        st.plotly_chart(fig_pred, use_container_width=True)
