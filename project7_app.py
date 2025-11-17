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
    df_t["month"] = df_t["month"].dt.strftime("%b %Y")

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
