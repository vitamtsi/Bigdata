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

    # ---- reorder so EU27 always first ----
    all_cities = sorted(df["City"].unique())
    reordered_cities = ["EU27 (aggregate)"] + [c for c in all_cities if c != "EU27 (aggregate)"]

    cities = st.multiselect(
        "Select cities:",
        reordered_cities,
        default=["EU27 (aggregate)", "Riga (Latvia)", "Tallinn (Estonia)"]
    )

    years = st.slider("Select year range:", 2018, 2025, (2018, 2025))

    df_t = df[
        (df["City"].isin(cities)) &
        (df["year"].between(years[0], years[1]))
    ].copy()

    # Short month labels (Jan, Feb, …)
    df_t["month_label"] = df_t["month"].dt.strftime("%b %Y")

    # ---- Color mapping (EU27 fixed red) ----
    non_red_palette = px.colors.qualitative.Dark24
    non_red_palette = [c for c in non_red_palette if "FF0000" not in c]  # remove red

    color_map = {"EU27 (aggregate)": "red"}
    other_cities = [c for c in cities if c != "EU27 (aggregate)"]

    for i, city in enumerate(other_cities):
        color_map[city] = non_red_palette[i % len(non_red_palette)]

    # ---- Plot ----
    fig = px.line(
        df_t,
        x="month_label",
        y="NO2",
        color="City",
        markers=True,
        title="NO₂ Concentrations Across Time",
        color_discrete_map=color_map
    )

    # ---- Hover info ----
    fig.update_traces(
        hovertemplate="<b>City</b>=%{text}<br>" +
                      "NO₂=%{y}<br>" +
                      "Month=%{x}",
        text=df_t["City"]
    )

    # ---- Improve grid: horizontal + vertical ----
    fig.update_layout(
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray"
        ),
        plot_bgcolor="white",
        legend_title_text="City"
    )

    st.plotly_chart(fig, use_container_width=True)

# ========================================================
# TAB 2 — CITY MONTHLY LEVELS
# ========================================================
with tab2:
    st.header("🏙️ Monthly NO₂ Levels by European Capitals")

    selected_year = st.selectbox("Select Year:", sorted(df["year"].unique()), index=7)
    selected_month = st.selectbox("Select Month:", list(range(1, 13)), index=9)

    df_m = df[(df["year"] == selected_year) & (df["month_num"] == selected_month)].copy()

    # EU27 mean value
    eu_value = df_m[df_m["City"] == "EU27 (aggregate)"]["NO2"].mean()

    # Assign correct colors
    def color_rule(x):
        if x > eu_value:
            return "red"         # above EU average
        elif x < eu_value:
            return "green"       # below EU average
        else:
            return "yellow"      # exactly EU average

    df_m["color"] = df_m["NO2"].apply(color_rule)

    # Sort bars by descending NO2 level
    df_m = df_m.sort_values("NO2", ascending=False)

    # Month label
    month_name = pd.to_datetime(f"{selected_year}-{selected_month}-01").strftime("%B %Y")

    fig2 = px.bar(
        df_m,
        x="City",
        y="NO2",
        color="color",
        color_discrete_map={
            "red": "red",
            "green": "green",
            "yellow": "gold"
        },
        title=f"NO₂ Levels by City — {month_name}"
    )

    fig2.update_layout(
        xaxis_tickangle=-60,
        showlegend=False
    )

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
