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
    st.header("📈 Dynamics of NO₂concentrations across European capital cities")

    # ---- reorder city list so EU27 is always first ----
    all_cities = sorted(df["City"].unique())
    reordered_cities = ["EU27 (aggregate)"] + [c for c in all_cities if c != "EU27 (aggregate)"]

    cities = st.multiselect(
        "Select cities:",
        reordered_cities,
        default=["EU27 (aggregate)", "Riga (Latvia)", "Tallinn (Estonia)"]
    )

    # ---- year range ----
    years = st.slider("Select year range:", 2018, 2025, (2018, 2025))

    # ---- filter data ----
    df_t = df[
        (df["City"].isin(cities)) &
        (df["year"].between(years[0], years[1]))
    ].copy()

    # ---- add formatted month labels ----
    df_t["month_short"] = df_t["month"].dt.strftime("%b")
    df_t["year_only"] = df_t["month"].dt.year

    # ---- color rules ----
    color_map = {
        "EU27 (aggregate)": "red"
    }

    fig = px.line(
        df_t,
        x="month",
        y="NO2",
        color="City",
        markers=True,
        title="NO₂ Concentrations Over Time",
        color_discrete_map=color_map  # EU27 red, others auto
    )

    # ---- tooltip formatting ----
    fig.update_traces(
        hovertemplate="<b>City</b>=%{text}<br>" +
                      "NO₂=%{y}<br>" +
                      "month=%{customdata[0]}<br>" +
                      "year=%{customdata[1]}",
        text=df_t["City"],
        customdata=df_t[["month_short", "year_only"]]
    )

    # ---- x-axis formatting ----
    fig.update_layout(
        xaxis=dict(dtick="M12", tickformat="%Y"),
        legend_title_text="City"
    )

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
