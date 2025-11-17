import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NO₂ Dashboard", page_icon="🌍", layout="wide")

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
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 NO₂ Over Time",
    "🏙️ NO₂ Levels by City",
    "📉 Correlation (Time vs NO₂)",
    "🍁 Seasonal Variation"
])

# ========================================================
# TAB 1 — TIME SERIES
# ========================================================
with tab1:
    st.header("📈 NO₂ Over Time")

    cities = st.multiselect(
        "Select cities:",
        sorted(df["City"].unique()),
        default=["Riga (Latvia)", "Tallinn (Estonia)", "EU27 (aggregate)"]
    )

    years = st.slider("Select year range:", 2018, 2025, (2018, 2025))

    df_t = df[
        (df["City"].isin(cities)) &
        (df["year"].between(years[0], years[1]))
    ]

    fig = px.line(
        df_t,
        x="month",
        y="NO2",
        color="City",
        markers=True,
        title="NO₂ Over Time (Selected Cities)"
    )
    fig.update_layout(xaxis=dict(dtick="M12", tickformat="%Y"))

    st.plotly_chart(fig, use_container_width=True)

# ========================================================
# TAB 2 — CITY MONTHLY LEVELS
# ========================================================
with tab2:
    st.header("🏙️ NO₂ Levels by City")

    selected_year = st.selectbox("Select Year:", sorted(df["year"].unique()), index=7)
    selected_month = st.selectbox("Select Month:", list(range(1, 13)), index=9)

    df_m = df[(df["year"] == selected_year) & (df["month_num"] == selected_month)]

    eu_value = df_m[df_m["City"] == "EU27 (aggregate)"]["NO2"].mean()

    df_m["color"] = df_m["NO2"].apply(
        lambda x: "yellow" if x == eu_value else ("red" if x > eu_value else "green")
    )

    month_name = pd.to_datetime(f"{selected_year}-{selected_month}-01").strftime("%B %Y")

    fig2 = px.bar(
        df_m,
        x="City",
        y="NO2",
        color="color",
        color_discrete_map={"red": "red", "green": "green", "yellow": "gold"},
        title=f"NO₂ Levels by City — {month_name}"
    )

    fig2.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig2, use_container_width=True)

# ========================================================
# TAB 3 — CORRELATION (AR APGRIEZTU KRĀSU SKALU)
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
# TAB 4 — SEASONAL VARIATION (with City tooltip)
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
        hover_data=["City", "month", "year", "NO2"],
        color_discrete_map=season_colors,
        category_orders={"season": ["Winter", "Spring", "Summer", "Autumn"]},
        title="Seasonal Variation of NO₂ Concentration in European Capitals"
    )

    fig4.update_traces(boxpoints="all", jitter=0.3)  # <- shows points too

    st.plotly_chart(fig4, use_container_width=True)
