# ─────────────────────────────────────────────────────────────────────────────
# app.py  —  Aadhaar Enrolment Intelligence Dashboard  (All Phases)
# Run locally : streamlit run app.py
# Deploy      : push to GitHub → share.streamlit.io
#
# FILE NOTES:
#   - enrolment_clean, biometric_clean, demographic_clean are Excel (.xlsx)
#     or CSV — we auto-detect based on what exists in /data/
#   - The 3 raw ZIPs (api_data_*) are NOT needed here — we use cleaned files
#   - demographic_clean is ~119 MB → use Git LFS for GitHub (instructions below)
#   - All HTML charts and PNGs are in /data/ — loaded via components.html / st.image
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aadhaar Enrolment Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #2d3561 100%);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stMetric"] {
        background: white;
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    h2 { color: #1e293b; font-weight: 700; margin-top: 1.5rem; }
    h3 { color: #334155; font-weight: 600; }
    .phase-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data/"

# ── Helper: smart file loader (handles .xlsx and .csv both) ──────────────────
def smart_load(basename, parse_dates=None):
    """
    Try loading basename as .csv first, then .xlsx.
    pandas read_csv can also handle .zip if there's one CSV inside.
    """
    for ext in [".csv", ".xlsx", ".csv.zip"]:
        path = DATA_DIR + basename + ext
        if os.path.exists(path):
            if ext == ".xlsx":
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path, parse_dates=parse_dates or [])
            return df, path
    return None, None

# ── Helper: load HTML chart ───────────────────────────────────────────────────
def show_html_chart(filename, height=520):
    path = DATA_DIR + filename
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=height, scrolling=False)
    else:
        st.warning(f"⚠️ Chart not found: `{filename}` — make sure it's in your `/data/` folder.")

# ── Helper: show PNG ─────────────────────────────────────────────────────────
def show_png(filename, caption=""):
    path = DATA_DIR + filename
    if os.path.exists(path):
        st.image(path, caption=caption, use_column_width=True)
    else:
        st.warning(f"⚠️ Image not found: `{filename}` — make sure it's in your `/data/` folder.")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    enrolment, ep = smart_load("enrolment_clean", parse_dates=["date"])
    biometric, bp = smart_load("biometric_clean")
    demographic, dp = smart_load("demographic_clean")

    if enrolment is None:
        st.error("❌ enrolment_clean not found in /data/ — check your folder.")
        st.stop()

    # Ensure date column is datetime
    if "date" in enrolment.columns:
        enrolment["date"] = pd.to_datetime(enrolment["date"], errors="coerce")

    enrolment["year_month"]   = enrolment["date"].dt.strftime("%Y-%m")
    enrolment["month_name"]   = enrolment["date"].dt.strftime("%b %Y")
    enrolment["day_of_month"] = enrolment["date"].dt.day

    return enrolment, biometric, demographic, ep, bp, dp

with st.spinner("Loading data..."):
    enrolment, biometric, demographic, ep, bp, dp = load_all_data()

ALL_MONTHS = ["2025-03","2025-04","2025-05","2025-06",
              "2025-07","2025-08","2025-09","2025-10"]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🇮🇳 Aadhaar Dashboard")
st.sidebar.markdown("---")

all_states = sorted(enrolment["state"].unique())
selected_states = st.sidebar.multiselect(
    "📍 Select States",
    options=all_states,
    default=all_states[:10],
    help="Filters all live charts"
)
if not selected_states:
    selected_states = all_states

available_months = sorted(enrolment["year_month"].dropna().unique())
month_range = st.sidebar.select_slider(
    "📅 Month Range",
    options=available_months,
    value=(available_months[0], available_months[-1]),
)

st.sidebar.markdown("---")
st.sidebar.markdown("**👶 Age Groups (Tab 3)**")
show_0_5  = st.sidebar.checkbox("0–5 years",  value=True)
show_5_17 = st.sidebar.checkbox("5–17 years", value=True)
show_18   = st.sidebar.checkbox("18+ years",  value=True)

st.sidebar.markdown("---")
st.sidebar.caption(f"📁 Enrolment: `{ep}`")
st.sidebar.caption(f"📁 Biometric: `{bp}`")
st.sidebar.caption(f"📁 Demographic: `{dp}`")

# ── Apply filters ─────────────────────────────────────────────────────────────
df = enrolment[
    (enrolment["state"].isin(selected_states)) &
    (enrolment["year_month"] >= month_range[0]) &
    (enrolment["year_month"] <= month_range[1])
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🇮🇳 Aadhaar Enrolment Intelligence Dashboard")
st.caption(
    f"Showing **{len(selected_states)} states** | "
    f"**{month_range[0]}** → **{month_range[1]}** | "
    f"**{len(df):,} records** | Data: UIDAI Mar–Oct 2025"
)
st.markdown("---")

# ── KPI ROW ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Enrolments",  f"{int(df['total_enrolments'].sum()):,}")
c2.metric("States",            f"{df['state'].nunique()}")
c3.metric("Age 0–5",           f"{int(df['age_0_5'].sum()):,}")
c4.metric("Age 5–17",          f"{int(df['age_5_17'].sum()):,}")
c5.metric("Age 18+",           f"{int(df['age_18_greater'].sum()):,}")
st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trends",
    "🗺️  Maps",
    "👥  EDA",
    "👶 Age Groups",
    "🔬 Data Quality",
    "📊 Summary Table",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PHASE 4 TIME-SERIES TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📈 Time-Series Trend Analysis")
    st.info("All charts below are the **saved Phase 4 outputs** from Colab. "
            "The live charts below them react to your sidebar filters.")

    # ── Saved Phase 4 HTML charts ────────────────────────────────
    st.markdown("#### Saved Charts from Phase 4")
    phase4_charts = {
        "National Monthly Trend (Annotated)": "trend_national_monthly.html",
        "Top 5 States Comparison":            "trend_top5_states.html",
        "Age Group Stacked Area":             "trend_age_groups.html",
        "MoM Growth Rate":                   "trend_mom_growth.html",
    }
    selected_p4 = st.selectbox("Select Phase 4 chart", list(phase4_charts.keys()))
    show_html_chart(phase4_charts[selected_p4], height=520)

    st.markdown("#### Phase 4 PNGs")
    col_p4a, col_p4b = st.columns(2)
    with col_p4a:
        show_png("heatmap_state_month.png", "State × Month Heatmap")
    with col_p4b:
        show_png("chart_day_of_month.png",  "Day-of-Month Batch Dump Pattern")

    st.markdown("---")

    # ── LIVE: National monthly trend (filtered) ──────────────────
    st.markdown("#### 🔴 Live — National Monthly Trend (filtered by sidebar)")
    monthly = (
        df.groupby("year_month")
        .agg(total_enrolments=("total_enrolments","sum"))
        .reset_index().sort_values("year_month")
    )
    monthly = (
        monthly.set_index("year_month")
        .reindex(ALL_MONTHS, fill_value=0)
        .reset_index().rename(columns={"index":"year_month"})
    )
    monthly["year_month"] = monthly["year_month"].astype(str)
    y_vals = monthly["total_enrolments"].replace(0, None).tolist()

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["year_month"], y=y_vals,
        mode="lines+markers", name="Enrolments",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=8), connectgaps=False,
        hovertemplate="<b>%{x}</b><br>Enrolments: %{y:,.0f}<extra></extra>",
    ))
    fig_trend.add_vrect(
        x0="2025-07", x1="2025-09",
        fillcolor="#fee2e2", opacity=0.4, layer="below", line_width=0,
    )
    fig_trend.add_annotation(
        x="2025-08", y=max([v for v in y_vals if v] or [1]) * 0.5,
        text="⚠️ Aug 2025<br>No Data", showarrow=False,
        font=dict(color="#dc2626", size=11),
        bgcolor="#fff1f2", bordercolor="#dc2626", borderwidth=1,
    )
    fig_trend.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(title="Month", tickangle=-30,
                   showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="Total Enrolments", tickformat=",.0f",
                   showgrid=True, gridcolor="#f1f5f9"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── LIVE: Top 5 states multi-line ───────────────────────────
    st.markdown("#### 🔴 Live — Top 5 States Comparison (filtered)")
    top5 = (
        df.groupby("state")["total_enrolments"]
        .sum().sort_values(ascending=False).head(5).index.tolist()
    )
    df_top5 = (
        df[df["state"].isin(top5)]
        .groupby(["year_month","state"])["total_enrolments"]
        .sum().reset_index().sort_values("year_month")
    )
    fig_top5 = px.line(
        df_top5, x="year_month", y="total_enrolments", color="state",
        markers=True,
        labels={"total_enrolments":"Enrolments","year_month":"Month","state":"State"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_top5.update_layout(
        height=400, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=-30, showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#f1f5f9"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_top5, use_container_width=True)

    # ── LIVE: MoM Growth ────────────────────────────────────────
    st.markdown("#### 🔴 Live — Month-on-Month Growth Rate (filtered)")
    growth = (
        df.groupby(["year_month","state"])["total_enrolments"]
        .sum().reset_index().sort_values(["state","year_month"])
    )
    growth["mom_growth"] = (
        growth.groupby("state")["total_enrolments"].pct_change() * 100
    )
    growth = growth[~growth["year_month"].isin(["2025-03","2025-08"])]
    growth = growth[~growth["mom_growth"].isin([np.inf,-np.inf])].dropna(subset=["mom_growth"])
    top10_g = (
        df.groupby("state")["total_enrolments"]
        .sum().sort_values(ascending=False).head(10).index.tolist()
    )
    fig_growth = px.bar(
        growth[growth["state"].isin(top10_g)],
        x="year_month", y="mom_growth", color="state", barmode="group",
        labels={"mom_growth":"MoM Growth (%)","year_month":"Month","state":"State"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_growth.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
    fig_growth.update_layout(
        height=400, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=-30, showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(ticksuffix="%", showgrid=True, gridcolor="#f1f5f9"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_growth, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PHASE 3 CHOROPLETH MAPS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🗺️  India Choropleth Maps")
    st.info("These are the saved Phase 3 HTML outputs from Colab.")

    map_options = {
        "Plotly Choropleth":  "choropleth_plotly.html",
        "Folium Map":         "choropleth_folium.html",
        "State Ranking Chart":"state_ranking_chart.html",
    }
    selected_map = st.selectbox("Select map", list(map_options.keys()))
    show_html_chart(map_options[selected_map], height=620)

    st.markdown("---")
    st.markdown("#### 🔴 Live — State Enrolment Bar Chart (filtered)")
    state_totals = (
        df.groupby("state")["total_enrolments"]
        .sum().sort_values(ascending=True).reset_index()
    )
    fig_bar = px.bar(
        state_totals, x="total_enrolments", y="state", orientation="h",
        labels={"total_enrolments":"Total Enrolments","state":""},
        color="total_enrolments", color_continuous_scale="Blues",
    )
    fig_bar.update_layout(
        height=max(400, len(state_totals)*22),
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        xaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 🔴 Live — State × Month Heatmap (filtered, top 10)")
    top10 = (
        df.groupby("state")["total_enrolments"]
        .sum().sort_values(ascending=False).head(10).index.tolist()
    )
    pivot = (
        df[df["state"].isin(top10)]
        .groupby(["state","year_month"])["total_enrolments"]
        .sum().unstack("year_month").fillna(0)
    )
    fig_heat = px.imshow(
        pivot / 1000,
        color_continuous_scale="YlOrRd",
        labels=dict(color="Enrolments (K)"),
        aspect="auto",
    )
    fig_heat.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(title="Month"), yaxis=dict(title=""),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PHASE 2 EDA
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊  Exploratory Data Analysis")
    st.info("Saved charts from Phase 2 Colab notebook.")

    phase2_pngs = [
        ("chart_heatmap.png",          "Correlation Heatmap"),
        ("chart_monthly_trend.png",    "Monthly Trend (Phase 2)"),
    ]
    for fname, caption in phase2_pngs:
        show_png(fname, caption)
        st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AGE GROUPS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 👶 Age Group Analysis")

    age_monthly = (
        df.groupby("year_month")
        .agg(
            age_0_5=("age_0_5","sum"),
            age_5_17=("age_5_17","sum"),
            age_18_greater=("age_18_greater","sum"),
        )
        .reset_index().sort_values("year_month")
    )
    age_monthly = (
        age_monthly.set_index("year_month")
        .reindex(ALL_MONTHS, fill_value=0)
        .reset_index().rename(columns={"index":"year_month"})
    )

    fig_age = go.Figure()
    cfg = [
        ("age_0_5",        "Age 0–5",  "#4ecdc4", show_0_5),
        ("age_5_17",       "Age 5–17", "#45b7d1", show_5_17),
        ("age_18_greater", "Age 18+",  "#2c7bb6", show_18),
    ]
    for col, label, color, show in cfg:
        if show:
            fig_age.add_trace(go.Scatter(
                x=age_monthly["year_month"],
                y=age_monthly[col].replace(0, None),
                name=label, stackgroup="one",
                line=dict(width=0.5, color=color), fillcolor=color,
                connectgaps=False,
                hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<extra></extra>",
            ))

    # Fixed version ✅ — annotation added separately
    fig_age.add_vrect(
    x0="2025-07", x1="2025-09",
    fillcolor="#fee2e2", opacity=0.3, layer="below", line_width=0,
)
    fig_age.add_annotation(
    x="2025-08", yref="paper", y=0.95,
    text="No data Aug 2025", showarrow=False,
    font=dict(size=10, color="#dc2626"),
)
    fig_age.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=-30, showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="Total Enrolments", tickformat=",.0f",
                   showgrid=True, gridcolor="#f1f5f9"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05),
        title="Age Group Stacked Area (filtered)",
    )
    st.plotly_chart(fig_age, use_container_width=True)

    col_pie, col_bar = st.columns(2)
    with col_pie:
        st.markdown("#### Overall Age Distribution")
        fig_pie = px.pie(
            values=[df["age_0_5"].sum(), df["age_5_17"].sum(), df["age_18_greater"].sum()],
            names=["Age 0–5","Age 5–17","Age 18+"],
            color_discrete_sequence=["#4ecdc4","#45b7d1","#2c7bb6"],
            hole=0.4,
        )
        fig_pie.update_layout(height=360, paper_bgcolor="white")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        st.markdown("#### Age Group by Top 10 States")
        age_state = (
            df.groupby("state")
            .agg(age_0_5=("age_0_5","sum"),
                 age_5_17=("age_5_17","sum"),
                 age_18_greater=("age_18_greater","sum"))
            .sort_values("age_18_greater", ascending=False)
            .head(10).reset_index()
        )
        age_melt = age_state.melt(
            id_vars="state",
            value_vars=["age_0_5","age_5_17","age_18_greater"],
            var_name="age_group", value_name="enrolments"
        )
        age_melt["age_group"] = age_melt["age_group"].map({
            "age_0_5":"Age 0–5","age_5_17":"Age 5–17","age_18_greater":"Age 18+"
        })
        fig_age_state = px.bar(
            age_melt, x="state", y="enrolments", color="age_group",
            barmode="stack",
            color_discrete_map={"Age 0–5":"#4ecdc4","Age 5–17":"#45b7d1","Age 18+":"#2c7bb6"},
            labels={"enrolments":"Enrolments","state":"","age_group":"Age Group"},
        )
        fig_age_state.update_layout(
            height=360, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickangle=-45, showgrid=False),
            yaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#f1f5f9"),
            legend=dict(orientation="h", y=1.05),
        )
        st.plotly_chart(fig_age_state, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA QUALITY
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🔬 Data Quality Findings")
    st.info("These findings are what make this project interview-worthy. "
            "Finding data issues and documenting them is the mark of a real analyst.")

    col_q1, col_q2 = st.columns(2)

    with col_q1:
        st.markdown("""
        #### 🔴 Finding 1 — Batch Upload Pattern
        Day 1 of every month has **massively higher enrolments** than any other day:
        - **Jul 1 = 616,868** (7× daily average)
        - Apr 1 = 257K | Jun 1 = 215K | May 1 = 183K

        The source system **batches the previous month's data** and uploads on the 1st.
        ➡️ **Daily analysis is misleading. Monthly aggregation is correct.**

        ---
        #### 🔴 Finding 2 — August 2025 Missing
        Zero records exist for August 2025 — this is a **data gap**, not zero enrolments.
        All charts show this as a visible break, not a zero bar.

        ---
        #### 🟡 Finding 3 — State Name Standardisation (Phase 1)
        | Raw name | Fixed to |
        |---|---|
        | West Bangal, W.Bengal, WEST BENGAL | **West Bengal** |
        | Orissa | **Odisha** |
        | Pondicherry | **Puducherry** |
        | 5 Dadra/Daman variants | **Merged UT name** |
        | Rows with value "100000" | **Dropped** |
        """)

    with col_q2:
        st.markdown("#### Day-of-Month Distribution (All Data)")
        day_dist = (
            enrolment.groupby("day_of_month")["total_enrolments"]
            .sum().reset_index()
        )
        fig_day = go.Figure(go.Bar(
            x=day_dist["day_of_month"],
            y=day_dist["total_enrolments"] / 1000,
            marker_color=["#dc2626" if d==1 else "#3b82f6"
                          for d in day_dist["day_of_month"]],
            hovertemplate="Day %{x}<br>%{y:,.0f}K enrolments<extra></extra>",
        ))
        fig_day.update_layout(
            height=380, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Day of Month", dtick=5,
                       showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(title="Enrolments (K)",
                       showgrid=True, gridcolor="#f1f5f9"),
        )
        st.plotly_chart(fig_day, use_container_width=True)
        st.caption("🔴 Red bar = Day 1 (batch dump). Blue = real daily activity.")

    # Dataset info
    st.markdown("---")
    st.markdown("#### Dataset Overview")
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.metric("Enrolment rows",   f"{len(enrolment):,}")
    col_d2.metric("Biometric rows",   f"{len(biometric):,}" if biometric is not None else "N/A")
    col_d3.metric("Demographic rows", f"{len(demographic):,}" if demographic is not None else "N/A")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("### 📊 Filtered Summary Table")

    summary = (
        df.groupby("state")
        .agg(
            total_enrolments=("total_enrolments","sum"),
            age_0_5=("age_0_5","sum"),
            age_5_17=("age_5_17","sum"),
            age_18_greater=("age_18_greater","sum"),
            months_active=("year_month","nunique"),
        )
        .sort_values("total_enrolments", ascending=False)
        .reset_index()
    )
    summary["age_18_share%"] = (
        summary["age_18_greater"] / summary["total_enrolments"] * 100
    ).round(1)

    summary_display = summary.copy()
    summary_display["total_enrolments"] = summary_display["total_enrolments"].apply(lambda x: f"{x:,.0f}")
    summary_display["age_0_5"]          = summary_display["age_0_5"].apply(lambda x: f"{x:,.0f}")
    summary_display["age_5_17"]         = summary_display["age_5_17"].apply(lambda x: f"{x:,.0f}")
    summary_display["age_18_greater"]   = summary_display["age_18_greater"].apply(lambda x: f"{x:,.0f}")
    summary_display["age_18_share%"]    = summary_display["age_18_share%"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(summary_display, use_container_width=True, height=520)

    st.download_button(
        label="⬇️ Download filtered summary as CSV",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="aadhaar_filtered_summary.csv",
        mime="text/csv",
    )