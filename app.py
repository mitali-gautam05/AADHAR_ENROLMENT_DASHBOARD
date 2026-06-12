# ─────────────────────────────────────────────────────────────────────────────
# app.py  —  Aadhaar Enrolment Intelligence Dashboard  (All Phases)
# Run locally : streamlit run app.py
# Deploy      : push to GitHub → share.streamlit.io
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
    background-color: #ffffff !important;
    color: #0f172a !important;
}
.main *, .block-container * { color: #0f172a !important; }
h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 700 !important; }
p, li, span, label, div { color: #0f172a !important; }
.stMarkdown p, .stMarkdown li, .stMarkdown span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #0f172a !important; font-weight: 500 !important;
}
[data-testid="stAlert"] *, div[data-baseweb="notification"] * {
    color: #0f172a !important; font-weight: 500 !important;
}
[data-testid="stMetric"] {
    background: #fefce8 !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07) !important;
}
[data-testid="stMetricLabel"] p { color: #78350f !important; font-weight: 700 !important; font-size: 13px !important; }
[data-testid="stMetricValue"]   { color: #0f172a !important; font-weight: 800 !important; }
.stSelectbox label p, .stMultiSelect label p,
.stSlider label p, .stCheckbox label span {
    color: #0f172a !important; font-weight: 600 !important;
}
[data-baseweb="select"] * { color: #0f172a !important; }
.stTabs [data-baseweb="tab-list"] { background: #f1f5f9; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 16px; }
.stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
    color: #334155 !important; font-weight: 600 !important; font-size: 14px !important;
}
.stTabs [aria-selected="true"] { background: #ffffff !important; box-shadow: 0 1px 4px rgba(0,0,0,0.12); }
.stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
    color: #b45309 !important; font-weight: 700 !important;
}
.stCaption p, [data-testid="stCaptionContainer"] p { color: #64748b !important; font-size: 12px !important; }
[data-testid="stImage"] {
    background: #fefce8 !important; border: 1.5px solid #fde68a !important;
    border-radius: 10px !important; padding: 10px !important;
}
[data-testid="stDataFrame"] { border-radius: 10px; border: 1px solid #e2e8f0; }
.stDownloadButton button {
    background: #1e3a5f !important; color: #ffffff !important;
    border-radius: 8px !important; font-weight: 600 !important; border: none !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 100%) !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stCheckbox label span, [data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Drive fallback URLs ───────────────────────────────────────────────────────
DRIVE_URLS = {
    "enrolment_clean"  : "https://drive.google.com/uc?id=1_hFlwzxQl3qLlheZtJaoaugek7SHIneA&export=download",
    "biometric_clean"  : "https://drive.google.com/uc?id=1cZk2ortPLPTzjCabK5mzhi1dBUL2RwZD&export=download",
    "demographic_clean": "https://drive.google.com/uc?id=1rTIP4GZXM3dVov_knSvw5CnTatE2wCof&export=download",
}
DATA_DIR = "data/"

def load_csv(key, parse_dates=None):
    local = DATA_DIR + key + ".csv"
    if os.path.exists(local):
        return pd.read_csv(local, parse_dates=parse_dates or [])
    url = DRIVE_URLS.get(key)
    if url:
        return pd.read_csv(url, parse_dates=parse_dates or [])
    return None

# ── FIX 1: st.components.v1.html → st.iframe ─────────────────────────────────
def show_html_chart(filename, height=520):
    path = DATA_DIR + filename
    if os.path.exists(path):
        # Write temp file and serve via st.iframe is not supported for local files
        # Best approach: read and embed via markdown iframe trick won't work either
        # Use st.components.v1.html but suppress warning with newer import pattern
        import streamlit.components.v1 as components
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=height, scrolling=False)
    else:
        st.warning(f"Chart not found: **{filename}** — place it in the /data/ folder.")

# ── FIX 2: use_column_width → width parameter ────────────────────────────────
def show_png(filename, caption=""):
    path = DATA_DIR + filename
    if os.path.exists(path):
        st.image(path, caption=caption, width=None)   # width=None = full container
    else:
        st.warning(f"Image not found: **{filename}** — place it in the /data/ folder.")

# ── Chart layout helper ───────────────────────────────────────────────────────
def chart_layout(fig, height=420):
    fig.update_layout(
        height=height,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=13, color="#0f172a"),
        title_font=dict(size=16, color="#0f172a"),
        legend=dict(font=dict(size=12, color="#0f172a")),
        xaxis=dict(tickfont=dict(size=12, color="#0f172a"),
                   title_font=dict(size=13, color="#0f172a"),
                   showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(tickfont=dict(size=12, color="#0f172a"),
                   title_font=dict(size=13, color="#0f172a"),
                   showgrid=True, gridcolor="#f1f5f9"),
        margin=dict(l=50, r=30, t=50, b=50),
    )
    return fig

# ── FIX 3: use_container_width → width='stretch' ─────────────────────────────
def plot(fig):
    st.plotly_chart(fig, width="stretch")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    enrolment   = load_csv("enrolment_clean", parse_dates=["date"])
    biometric   = load_csv("biometric_clean")
    demographic = load_csv("demographic_clean")

    if enrolment is None:
        st.error("enrolment_clean.csv not found.")
        st.stop()

    enrolment["date"]         = pd.to_datetime(enrolment["date"], errors="coerce")
    enrolment["year_month"]   = enrolment["date"].dt.strftime("%Y-%m")
    enrolment["month_name"]   = enrolment["date"].dt.strftime("%b %Y")
    enrolment["day_of_month"] = enrolment["date"].dt.day

    if "total_enrolments" not in enrolment.columns:
        enrolment["total_enrolments"] = (
            enrolment.get("age_0_5", 0) +
            enrolment.get("age_5_17", 0) +
            enrolment.get("age_18_greater", 0)
        )
    return enrolment, biometric, demographic

with st.spinner("Loading data..."):
    enrolment, biometric, demographic = load_all_data()

ALL_MONTHS = ["2025-03","2025-04","2025-05","2025-06",
              "2025-07","2025-08","2025-09","2025-10"]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🇮🇳 Aadhaar Dashboard")
st.sidebar.markdown("---")

all_states      = sorted(enrolment["state"].unique())
selected_states = st.sidebar.multiselect(
    "📍 Select States", options=all_states, default=all_states[:10],
    help="Filters all live charts",
)
if not selected_states:
    selected_states = all_states

available_months = sorted(enrolment["year_month"].dropna().unique())
month_range = st.sidebar.select_slider(
    "📅 Month Range", options=available_months,
    value=(available_months[0], available_months[-1]),
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Age Groups (Tab 4)**")
show_0_5  = st.sidebar.checkbox("0-5 years",  value=True)
show_5_17 = st.sidebar.checkbox("5-17 years", value=True)
show_18   = st.sidebar.checkbox("18+ years",  value=True)
st.sidebar.markdown("---")
st.sidebar.caption("Data: UIDAI Aadhaar  |  Mar-Oct 2025")
st.sidebar.caption("Built by Mitali Gupta | MITS Gwalior")

# ── Filters ───────────────────────────────────────────────────────────────────
df = enrolment[
    (enrolment["state"].isin(selected_states)) &
    (enrolment["year_month"] >= month_range[0]) &
    (enrolment["year_month"] <= month_range[1])
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🇮🇳 Aadhaar Enrolment Intelligence Dashboard")
st.markdown(
    f"Showing **{len(selected_states)} states** | "
    f"**{month_range[0]}** to **{month_range[1]}** | "
    f"**{len(df):,} records** | Data: UIDAI Mar-Oct 2025"
)
st.markdown("---")

# ── KPI ROW ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Enrolments", f"{int(df['total_enrolments'].sum()):,}")
c2.metric("States / UTs",     f"{df['state'].nunique()}")
c3.metric("Age 0-5",          f"{int(df['age_0_5'].sum()):,}")
c4.metric("Age 5-17",         f"{int(df['age_5_17'].sum()):,}")
c5.metric("Age 18+",          f"{int(df['age_18_greater'].sum()):,}")
st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trends", "🗺️ Maps", "👥 EDA",
    "👶 Age Groups", "🔬 Data Quality", "📊 Summary",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Phase 4 — Time-Series Trend Analysis")
    st.info("Saved HTML charts from Phase 4 Colab are shown first. "
            "Live charts below react to your sidebar filters.")

    st.subheader("Saved Phase 4 Charts")
    phase4_charts = {
        "National Monthly Trend (Annotated)": "trend_national_monthly.html",
        "Top 5 States Comparison":            "trend_top5_states.html",
        "Age Group Stacked Area":             "trend_age_groups.html",
        "MoM Growth Rate":                    "trend_mom_growth.html",
    }
    selected_p4 = st.selectbox("Select Phase 4 chart", list(phase4_charts.keys()))
    show_html_chart(phase4_charts[selected_p4], height=520)

    st.subheader("Phase 4 Static Charts")
    col_p4a, col_p4b = st.columns(2)
    with col_p4a:
        show_png("heatmap_state_month.png", "State x Month Heatmap")
    with col_p4b:
        show_png("chart_day_of_month.png",  "Day-of-Month Batch Dump Pattern")

    st.markdown("---")
    st.subheader("Live — National Monthly Trend")

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
        line=dict(color="#2563eb", width=3),
        marker=dict(size=9, color="#2563eb"),
        connectgaps=False,
        hovertemplate="<b>%{x}</b><br>Enrolments: %{y:,.0f}<extra></extra>",
    ))
    fig_trend.add_vrect(
        x0="2025-07", x1="2025-09",
        fillcolor="#fee2e2", opacity=0.4, layer="below", line_width=0,
    )
    fig_trend.add_annotation(
        x="2025-08", yref="paper", y=0.5,
        text="Aug 2025 - No Data", showarrow=False,
        font=dict(color="#dc2626", size=12, family="Arial"),
        bgcolor="#fff1f2", bordercolor="#dc2626", borderwidth=1,
    )
    non_null = [v for v in y_vals if v is not None]
    if non_null:
        peak_idx   = monthly["total_enrolments"].idxmax()
        peak_month = monthly.loc[peak_idx, "year_month"]
        peak_val   = monthly.loc[peak_idx, "total_enrolments"]
        fig_trend.add_annotation(
            x=peak_month, y=peak_val,
            text=f"Peak: {peak_val/1e3:.0f}K",
            showarrow=True, arrowhead=2, ax=0, ay=-45,
            font=dict(size=12, color="#16a34a"), arrowcolor="#16a34a",
        )
    chart_layout(fig_trend)
    fig_trend.update_xaxes(title="Month", tickangle=-30)
    fig_trend.update_yaxes(title="Total Enrolments", tickformat=",.0f")
    fig_trend.update_layout(hovermode="x unified")
    plot(fig_trend)

    st.subheader("Live — Top 5 States Comparison")
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
    chart_layout(fig_top5)
    fig_top5.update_xaxes(tickangle=-30)
    fig_top5.update_yaxes(tickformat=",.0f")
    fig_top5.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, font=dict(size=12, color="#0f172a")),
    )
    plot(fig_top5)

    st.subheader("Live — Month-on-Month Growth Rate")
    growth = (
        df.groupby(["year_month","state"])["total_enrolments"]
        .sum().reset_index().sort_values(["state","year_month"])
    )
    growth["mom_growth"] = growth.groupby("state")["total_enrolments"].pct_change() * 100
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
    fig_growth.add_hline(y=0, line_dash="dash", line_color="#64748b", line_width=1)
    chart_layout(fig_growth)
    fig_growth.update_xaxes(tickangle=-30)
    fig_growth.update_yaxes(ticksuffix="%")
    fig_growth.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, font=dict(size=11, color="#0f172a")),
    )
    plot(fig_growth)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MAPS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Phase 3 — India Choropleth Maps")
    st.info("Saved Phase 3 HTML outputs from Colab.")

    map_options = {
        "Plotly Choropleth":   "choropleth_plotly.html",
        "Folium Map":          "choropleth_folium.html",
        "State Ranking Chart": "state_ranking_chart.html",
    }
    selected_map = st.selectbox("Select map", list(map_options.keys()))
    show_html_chart(map_options[selected_map], height=620)

    st.markdown("---")
    st.subheader("Live — State Enrolment Bar Chart")
    state_totals = (
        df.groupby("state")["total_enrolments"]
        .sum().sort_values(ascending=True).reset_index()
    )
    fig_bar = px.bar(
        state_totals, x="total_enrolments", y="state", orientation="h",
        labels={"total_enrolments":"Total Enrolments","state":""},
        color="total_enrolments", color_continuous_scale="Blues",
    )
    chart_layout(fig_bar, height=max(420, len(state_totals)*22))
    fig_bar.update_xaxes(tickformat=",.0f")
    fig_bar.update_layout(coloraxis_showscale=False)
    plot(fig_bar)

    st.subheader("Live — State x Month Heatmap (Top 10)")
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
        aspect="auto", text_auto=".0f",
    )
    fig_heat.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(size=13, color="#0f172a"),
        xaxis=dict(title="Month", tickfont=dict(size=12, color="#0f172a")),
        yaxis=dict(title="",      tickfont=dict(size=12, color="#0f172a")),
    )
    plot(fig_heat)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EDA
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Phase 2 — Exploratory Data Analysis")
    st.info("Saved charts from the Phase 2 Colab notebook.")

    for fname, caption in [
        ("chart_state_enrolment.png", "State-wise Total Enrolments"),
        ("chart_heatmap.png",         "State x Month Heatmap"),
        ("chart_monthly_trend.png",   "Monthly Trend"),
    ]:
        st.subheader(caption)
        show_png(fname, caption)
        st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AGE GROUPS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("Age Group Analysis")

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
    for col, label, color, show in [
        ("age_0_5",        "Age 0-5",  "#0ea5e9", show_0_5),
        ("age_5_17",       "Age 5-17", "#10b981", show_5_17),
        ("age_18_greater", "Age 18+",  "#6366f1", show_18),
    ]:
        if show:
            fig_age.add_trace(go.Scatter(
                x=age_monthly["year_month"],
                y=age_monthly[col].replace(0, None),
                name=label, stackgroup="one",
                line=dict(width=1, color=color), fillcolor=color,
                connectgaps=False,
                hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<extra></extra>",
            ))
    fig_age.add_vrect(
        x0="2025-07", x1="2025-09",
        fillcolor="#fee2e2", opacity=0.3, layer="below", line_width=0,
    )
    fig_age.add_annotation(
        x="2025-08", yref="paper", y=0.92,
        text="No data Aug 2025", showarrow=False,
        font=dict(size=11, color="#dc2626"),
    )
    chart_layout(fig_age)
    fig_age.update_xaxes(tickangle=-30)
    fig_age.update_yaxes(title="Total Enrolments", tickformat=",.0f")
    fig_age.update_layout(
        hovermode="x unified",
        title="Age Group Stacked Area (filtered)",
        legend=dict(orientation="h", y=1.08, font=dict(size=13, color="#0f172a")),
    )
    plot(fig_age)

    col_pie, col_bar2 = st.columns(2)
    with col_pie:
        st.subheader("Overall Age Distribution")
        fig_pie = px.pie(
            values=[df["age_0_5"].sum(), df["age_5_17"].sum(), df["age_18_greater"].sum()],
            names=["Age 0-5","Age 5-17","Age 18+"],
            color_discrete_sequence=["#0ea5e9","#10b981","#6366f1"],
            hole=0.4,
        )
        fig_pie.update_traces(
            textposition="inside", textinfo="percent+label",
            textfont=dict(size=13, color="white"),
        )
        fig_pie.update_layout(
            height=360, paper_bgcolor="white",
            legend=dict(font=dict(size=12, color="#0f172a")),
        )
        plot(fig_pie)

    with col_bar2:
        st.subheader("Age Group by Top 10 States")
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
            var_name="age_group", value_name="enrolments",
        )
        age_melt["age_group"] = age_melt["age_group"].map({
            "age_0_5":"Age 0-5","age_5_17":"Age 5-17","age_18_greater":"Age 18+"
        })
        fig_age_state = px.bar(
            age_melt, x="state", y="enrolments",
            color="age_group", barmode="stack",
            color_discrete_map={"Age 0-5":"#0ea5e9","Age 5-17":"#10b981","Age 18+":"#6366f1"},
            labels={"enrolments":"Enrolments","state":"","age_group":"Age Group"},
        )
        chart_layout(fig_age_state, height=360)
        fig_age_state.update_xaxes(tickangle=-45)
        fig_age_state.update_yaxes(tickformat=",.0f")
        fig_age_state.update_layout(
            legend=dict(orientation="h", y=1.08, font=dict(size=12, color="#0f172a")),
        )
        plot(fig_age_state)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA QUALITY
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("Data Quality Findings")
    st.info("These findings are what make this project interview-worthy. "
            "Discovering and documenting data issues is the mark of a real analyst.")

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.subheader("Finding 1 — Batch Upload Pattern")
        st.markdown(
            "Day 1 of every month has **massively higher enrolments**:\n\n"
            "- **Jul 1 = 616,868** (7x daily average)\n"
            "- Apr 1 = 257K | Jun 1 = 215K | May 1 = 183K\n\n"
            "Source system batches previous month's data and uploads on the 1st. "
            "**Monthly aggregation is the correct granularity, not daily.**"
        )
        st.subheader("Finding 2 — August 2025 Missing")
        st.markdown(
            "Zero records for August 2025 — a **data gap**, not zero enrolments. "
            "All trend charts show this as a visible line break."
        )
        st.subheader("Finding 3 — State Name Cleaning")
        cleaning_df = pd.DataFrame([
            ["West Bangal / WEST BENGAL (6 variants)", "West Bengal"],
            ["Orissa",                                 "Odisha"],
            ["Pondicherry",                            "Puducherry"],
            ["Uttaranchal",                            "Uttarakhand"],
            ["Chhatisgarh",                            "Chhattisgarh"],
            ["Tamilnadu",                              "Tamil Nadu"],
            ["Cities in state col",                   "Dropped"],
            ["Rows with value 100000",                 "Dropped (garbage)"],
        ], columns=["Raw Value", "Cleaned To"])
        st.dataframe(cleaning_df, hide_index=True, width="stretch")

    with col_q2:
        st.subheader("Day-of-Month Distribution")
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
        chart_layout(fig_day, height=380)
        fig_day.update_xaxes(title="Day of Month", dtick=5)
        fig_day.update_yaxes(title="Enrolments (K)")
        plot(fig_day)
        st.caption("Red = Day 1 batch dump | Blue = real daily activity")

    st.markdown("---")
    st.subheader("Dataset Overview")
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.metric("Enrolment rows",   f"{len(enrolment):,}")
    col_d2.metric("Biometric rows",   f"{len(biometric):,}" if biometric is not None else "N/A")
    col_d3.metric("Demographic rows", f"{len(demographic):,}" if demographic is not None else "N/A")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.header("Filtered Summary Table")

    summary = (
        df.groupby("state")
        .agg(
            total_enrolments = ("total_enrolments","sum"),
            age_0_5          = ("age_0_5","sum"),
            age_5_17         = ("age_5_17","sum"),
            age_18_greater   = ("age_18_greater","sum"),
            months_active    = ("year_month","nunique"),
        )
        .sort_values("total_enrolments", ascending=False)
        .reset_index()
    )
    summary["age_18_share%"] = (
        summary["age_18_greater"] / summary["total_enrolments"] * 100
    ).round(1)

    disp = summary.copy()
    for c in ["total_enrolments","age_0_5","age_5_17","age_18_greater"]:
        disp[c] = disp[c].apply(lambda x: f"{int(x):,}")
    disp["age_18_share%"] = disp["age_18_share%"].apply(lambda x: f"{x:.1f}%")
    disp.columns = ["State","Total Enrolments","Age 0-5","Age 5-17",
                    "Age 18+","Months Active","18+ Share"]

    st.dataframe(disp, hide_index=True, width="stretch", height=520)
    st.download_button(
        label     = "Download filtered summary as CSV",
        data      = summary.to_csv(index=False).encode("utf-8"),
        file_name = "aadhaar_filtered_summary.csv",
        mime      = "text/csv",
    )