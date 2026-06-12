# app.py — Aadhaar Enrolment Intelligence Dashboard

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Aadhaar Enrolment Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Hide Streamlit default top bar & footer ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Force white background everywhere ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container { background-color: #ffffff !important; }

/* ── ALL text in main area: force dark ── */
.main h1 { color: #0c1a2e !important; font-size: 2rem !important; font-weight: 800 !important; }
.main h2 { color: #0c1a2e !important; font-weight: 700 !important; }
.main h3 { color: #0c1a2e !important; font-weight: 700 !important; padding-bottom: 6px; border-bottom: 3px solid #f59e0b; margin-bottom: 14px; }
.main h4 { color: #1e3a5f !important; font-weight: 600 !important; }
.main p, .main span, .main li, .main label,
.main div.stMarkdown p, .main div.stMarkdown li { color: #1e293b !important; }

/* ── KPI metric cards ── */
[data-testid="stMetric"] {
    background: #fffbeb !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07) !important;
}
[data-testid="stMetricLabel"] p { color: #92400e !important; font-weight: 700 !important; font-size: 13px !important; }
[data-testid="stMetricValue"]   { color: #0c1a2e !important; font-weight: 800 !important; }

/* ── PNG/image wrapper ── */
[data-testid="stImage"] img { border-radius: 8px; }
[data-testid="stImage"] {
    background: #fffbeb !important;
    border: 1.5px solid #fde68a !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

/* ── Info / warning / alert boxes ── */
[data-testid="stAlert"] p { color: #1e293b !important; font-weight: 500 !important; }
div[data-baseweb="notification"] p { color: #1e293b !important; }

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] { background: #f8fafc; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 16px; }
.stTabs [data-baseweb="tab"] p { color: #334155 !important; font-weight: 600 !important; font-size: 14px !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; box-shadow: 0 1px 4px rgba(0,0,0,0.12); }
.stTabs [aria-selected="true"] p { color: #b45309 !important; font-weight: 700 !important; }

/* ── Caption text ── */
.stCaption p, [data-testid="stCaptionContainer"] p { color: #64748b !important; font-size: 12px !important; }

/* ── Horizontal rule ── */
hr { border-color: #fde68a !important; opacity: 0.7; }

/* ── Selectbox / dropdown labels ── */
.main .stSelectbox label p { color: #1e293b !important; font-weight: 600 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px; border: 1px solid #e2e8f0; }

/* ── SIDEBAR: dark navy — scoped tightly so it never bleeds into main ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 100%) !important;
    display: block !important;
    visibility: visible !important;
}

/* Force sidebar visible even when header { visibility: hidden } bleeds */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarContent"] {
    visibility: visible !important;
    display: block !important;
}

/* Sidebar text — explicitly listed, NOT using wildcard * */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] .stCheckbox label span,
[data-testid="stSidebar"] .stMultiSelect label p,
[data-testid="stSidebar"] .stSelectbox label p,
[data-testid="stSidebar"] .stSlider label p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li { 
    color: #e2e8f0 !important; 
}

/* Sidebar metric values if any */
[data-testid="stSidebar"] [data-testid="stMetricLabel"] p,
[data-testid="stSidebar"] [data-testid="stMetricValue"] { 
    color: #e2e8f0 !important; 
}

/* Sidebar multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #0f172a !important; }

/* Sidebar select slider values */
[data-testid="stSidebar"] [data-testid="stSlider"] p,
[data-testid="stSidebar"] [data-testid="stSlider"] span { color: #e2e8f0 !important; }

/* Sidebar checkbox text */
[data-testid="stSidebar"] [data-testid="stCheckbox"] p,
[data-testid="stSidebar"] [data-testid="stCheckbox"] span { color: #e2e8f0 !important; }

/* Sidebar separator line */
[data-testid="stSidebar"] hr { border-color: #334155 !important; }
</style>
""", unsafe_allow_html=True)

# ── Google Drive URLs ─────────────────────────────────────────────────────────
DRIVE_URLS = {
    "enrolment_clean"  : "https://drive.google.com/uc?id=1_hFlwzxQl3qLlheZtJaoaugek7SHIneA&export=download",
    "biometric_clean"  : "https://drive.google.com/uc?id=1cZk2ortPLPTzjCabK5mzhi1dBUL2RwZD&export=download",
    "demographic_clean": "https://drive.google.com/uc?id=1rTIP4GZXM3dVov_knSvw5CnTatE2wCof&export=download",
    "state_enrolment"  : "https://drive.google.com/uc?id=19KIPM16ntNVkl0hrSJPkTYF2mZChTUBl&export=download",
    "monthly_trend"    : "https://drive.google.com/uc?id=1-Gaz3jrnqDzjwJOGWZSfY-4xrMVmE4tD&export=download",
}
DATA_DIR = "data/"

def load_csv(key, parse_dates=None):
    local = DATA_DIR + key + ".csv"
    if os.path.exists(local):
        return pd.read_csv(local, parse_dates=parse_dates or []), local
    return pd.read_csv(DRIVE_URLS[key], parse_dates=parse_dates or []), DRIVE_URLS[key]

def show_html_chart(filename, height=520):
    path = DATA_DIR + filename
    if os.path.exists(path):
        components.html(open(path, "r", encoding="utf-8").read(), height=height, scrolling=False)
    else:
        st.warning(f"Chart not found: `{filename}`")

def show_png(filename, caption=""):
    path = DATA_DIR + filename
    if os.path.exists(path):
        st.image(path, caption=caption, use_column_width=True)
    else:
        st.warning(f"Image not found: `{filename}`")

def chart_layout(fig, height=420):
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=13, color="#1e293b"),
        title_font=dict(size=16, color="#0c1a2e", family="Inter, Arial, sans-serif"),
        legend=dict(font=dict(size=12, color="#1e293b")),
        xaxis=dict(
            tickfont=dict(size=12, color="#1e293b"),
            title_font=dict(size=13, color="#1e293b"),
            showgrid=True, gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            tickfont=dict(size=12, color="#1e293b"),
            title_font=dict(size=13, color="#1e293b"),
            showgrid=True, gridcolor="#f1f5f9",
        ),
        margin=dict(l=50, r=30, t=50, b=50),
    )
    return fig

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    enrolment,   ep = load_csv("enrolment_clean",   parse_dates=["date"])
    biometric,   bp = load_csv("biometric_clean")
    demographic, dp = load_csv("demographic_clean")
    enrolment["date"]         = pd.to_datetime(enrolment["date"], errors="coerce")
    enrolment["year_month"]   = enrolment["date"].dt.strftime("%Y-%m")
    enrolment["month_name"]   = enrolment["date"].dt.strftime("%b %Y")
    enrolment["day_of_month"] = enrolment["date"].dt.day
    if "total_enrolments" not in enrolment.columns:
        enrolment["total_enrolments"] = (
            enrolment["age_0_5"] + enrolment["age_5_17"] + enrolment["age_18_greater"]
        )
    return enrolment, biometric, demographic, ep, bp, dp

enrolment, biometric, demographic, ep, bp, dp = load_all_data()

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
st.sidebar.markdown("**👶 Age Groups (Tab 4)**")
show_0_5  = st.sidebar.checkbox("0–5 years",  value=True)
show_5_17 = st.sidebar.checkbox("5–17 years", value=True)
show_18   = st.sidebar.checkbox("18+ years",  value=True)
st.sidebar.markdown("---")
st.sidebar.caption("Data: UIDAI Enrolment Mar–Oct 2025")

# ── Filters ───────────────────────────────────────────────────────────────────
df = enrolment[
    (enrolment["state"].isin(selected_states)) &
    (enrolment["year_month"] >= month_range[0]) &
    (enrolment["year_month"] <= month_range[1])
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='color:#0c1a2e;font-weight:800;font-size:2rem;'>🇮🇳 Aadhaar Enrolment Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:#475569;font-size:14px;margin-top:-8px;'>"
    f"Showing <b>{len(selected_states)} states</b> | "
    f"<b>{month_range[0]}</b> → <b>{month_range[1]}</b> | "
    f"<b>{len(df):,} records</b> | Data: UIDAI Mar–Oct 2025</p>",
    unsafe_allow_html=True,
)
st.markdown("<hr style='border-color:#fde68a;margin:8px 0 16px 0;'>", unsafe_allow_html=True)

# ── KPI ROW ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Enrolments", f"{int(df['total_enrolments'].sum()):,}")
c2.metric("States / UTs",     f"{df['state'].nunique()}")
c3.metric("Age 0–5",          f"{int(df['age_0_5'].sum()):,}")
c4.metric("Age 5–17",         f"{int(df['age_5_17'].sum()):,}")
c5.metric("Age 18+",          f"{int(df['age_18_greater'].sum()):,}")
st.markdown("<hr style='border-color:#fde68a;margin:16px 0;'>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trends", "🗺️ Maps", "👥 EDA",
    "👶 Age Groups", "🔬 Data Quality", "📊 Summary",
])

# ═══════ TAB 1 — TRENDS ═══════
with tab1:
    st.markdown("<h3>📈 Phase 4 — Time-Series Trend Analysis</h3>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#1e3a5f;'>Saved Charts from Phase 4 (Colab)</h4>", unsafe_allow_html=True)
    phase4_charts = {
        "National Monthly Trend (Annotated)": "trend_national_monthly.html",
        "Top 5 States Comparison":            "trend_top5_states.html",
        "Age Group Stacked Area":             "trend_age_groups.html",
        "MoM Growth Rate":                    "trend_mom_growth.html",
    }
    selected_p4 = st.selectbox("Select Phase 4 chart", list(phase4_charts.keys()))
    show_html_chart(phase4_charts[selected_p4], height=520)

    st.markdown("<h4 style='color:#1e3a5f;margin-top:20px;'>Phase 4 Static Charts</h4>", unsafe_allow_html=True)
    col_p4a, col_p4b = st.columns(2)
    with col_p4a:
        show_png("heatmap_state_month.png", "State × Month Heatmap")
    with col_p4b:
        show_png("chart_day_of_month.png",  "Day-of-Month Batch Dump Pattern")

    st.markdown("<hr style='border-color:#fde68a;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#1e3a5f;'>🔴 Live — National Monthly Trend (filtered)</h4>", unsafe_allow_html=True)

    monthly = (
        df.groupby("year_month").agg(total_enrolments=("total_enrolments","sum"))
        .reset_index().sort_values("year_month")
    )
    monthly = (
        monthly.set_index("year_month").reindex(ALL_MONTHS, fill_value=0)
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
    fig_trend.add_vrect(x0="2025-07", x1="2025-09",
        fillcolor="#fee2e2", opacity=0.4, layer="below", line_width=0)
    fig_trend.add_annotation(
        x="2025-08", yref="paper", y=0.5,
        text="⚠️ Aug 2025<br>No Data", showarrow=False,
        font=dict(color="#dc2626", size=12, family="Arial"),
        bgcolor="#fff1f2", bordercolor="#dc2626", borderwidth=1,
    )
    non_null = [v for v in y_vals if v is not None]
    if non_null:
        peak_month = monthly.loc[monthly["total_enrolments"].idxmax(), "year_month"]
        peak_val   = monthly["total_enrolments"].max()
        fig_trend.add_annotation(
            x=peak_month, y=peak_val,
            text=f"Peak: {peak_val/1e3:.0f}K",
            showarrow=True, arrowhead=2, ax=0, ay=-45,
            font=dict(size=12, color="#16a34a", family="Arial"),
            arrowcolor="#16a34a",
        )
    chart_layout(fig_trend)
    fig_trend.update_xaxes(title="Month", tickangle=-30)
    fig_trend.update_yaxes(title="Total Enrolments", tickformat=",.0f")
    fig_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("<h4 style='color:#1e3a5f;'>🔴 Live — Top 5 States Comparison</h4>", unsafe_allow_html=True)
    top5 = df.groupby("state")["total_enrolments"].sum().sort_values(ascending=False).head(5).index.tolist()
    df_top5 = (
        df[df["state"].isin(top5)]
        .groupby(["year_month","state"])["total_enrolments"].sum()
        .reset_index().sort_values("year_month")
    )
    fig_top5 = px.line(df_top5, x="year_month", y="total_enrolments", color="state",
        markers=True,
        labels={"total_enrolments":"Enrolments","year_month":"Month","state":"State"},
        color_discrete_sequence=px.colors.qualitative.Set2)
    chart_layout(fig_top5)
    fig_top5.update_xaxes(tickangle=-30)
    fig_top5.update_yaxes(tickformat=",.0f")
    fig_top5.update_layout(hovermode="x unified",
        legend=dict(font=dict(size=12, color="#1e293b"), orientation="h", y=1.08))
    st.plotly_chart(fig_top5, use_container_width=True)

    st.markdown("<h4 style='color:#1e3a5f;'>🔴 Live — Month-on-Month Growth Rate</h4>", unsafe_allow_html=True)
    growth = (
        df.groupby(["year_month","state"])["total_enrolments"].sum()
        .reset_index().sort_values(["state","year_month"])
    )
    growth["mom_growth"] = growth.groupby("state")["total_enrolments"].pct_change() * 100
    growth = growth[~growth["year_month"].isin(["2025-03","2025-08"])]
    growth = growth[~growth["mom_growth"].isin([np.inf,-np.inf])].dropna(subset=["mom_growth"])
    top10_g = df.groupby("state")["total_enrolments"].sum().sort_values(ascending=False).head(10).index.tolist()
    fig_growth = px.bar(growth[growth["state"].isin(top10_g)],
        x="year_month", y="mom_growth", color="state", barmode="group",
        labels={"mom_growth":"MoM Growth (%)","year_month":"Month","state":"State"},
        color_discrete_sequence=px.colors.qualitative.Set2)
    fig_growth.add_hline(y=0, line_dash="dash", line_color="#64748b", line_width=1)
    chart_layout(fig_growth)
    fig_growth.update_xaxes(tickangle=-30)
    fig_growth.update_yaxes(ticksuffix="%")
    fig_growth.update_layout(hovermode="x unified",
        legend=dict(font=dict(size=11, color="#1e293b"), orientation="h", y=1.08))
    st.plotly_chart(fig_growth, use_container_width=True)

# ═══════ TAB 2 — MAPS ═══════
with tab2:
    st.markdown("<h3>🗺️ Phase 3 — India Choropleth Maps</h3>", unsafe_allow_html=True)
    map_options = {
        "Plotly Choropleth":   "choropleth_plotly.html",
        "Folium Map":          "choropleth_folium.html",
        "State Ranking Chart": "state_ranking_chart.html",
    }
    selected_map = st.selectbox("Select map", list(map_options.keys()))
    show_html_chart(map_options[selected_map], height=620)

    st.markdown("<hr style='border-color:#fde68a;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#1e3a5f;'>🔴 Live — State Enrolment Bar Chart</h4>", unsafe_allow_html=True)
    state_totals = df.groupby("state")["total_enrolments"].sum().sort_values(ascending=True).reset_index()
    fig_bar = px.bar(state_totals, x="total_enrolments", y="state", orientation="h",
        labels={"total_enrolments":"Total Enrolments","state":""},
        color="total_enrolments", color_continuous_scale="Blues")
    fig_bar.update_traces(textposition="outside")
    chart_layout(fig_bar, height=max(420, len(state_totals)*22))
    fig_bar.update_xaxes(tickformat=",.0f")
    fig_bar.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<h4 style='color:#1e3a5f;'>🔴 Live — State × Month Heatmap (top 10)</h4>", unsafe_allow_html=True)
    top10 = df.groupby("state")["total_enrolments"].sum().sort_values(ascending=False).head(10).index.tolist()
    pivot = (
        df[df["state"].isin(top10)]
        .groupby(["state","year_month"])["total_enrolments"].sum()
        .unstack("year_month").fillna(0)
    )
    fig_heat = px.imshow(pivot/1000, color_continuous_scale="YlOrRd",
        labels=dict(color="Enrolments (K)"), aspect="auto", text_auto=".0f")
    fig_heat.update_layout(height=420, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(size=13, color="#1e293b"),
        xaxis=dict(title="Month", tickfont=dict(size=12, color="#1e293b")),
        yaxis=dict(title="", tickfont=dict(size=12, color="#1e293b")))
    st.plotly_chart(fig_heat, use_container_width=True)

# ═══════ TAB 3 — EDA ═══════
with tab3:
    st.markdown("<h3>👥 Phase 2 — Exploratory Data Analysis</h3>", unsafe_allow_html=True)
    st.info("Saved charts from the Phase 2 Colab notebook.")
    for fname, caption in [
        ("chart_state_enrolment.png", "State-wise Total Enrolments"),
        ("chart_heatmap.png",         "State × Month Heatmap"),
        ("chart_monthly_trend.png",   "Monthly Trend"),
    ]:
        show_png(fname, caption)
        st.markdown("<hr style='border-color:#fde68a;'>", unsafe_allow_html=True)

# ═══════ TAB 4 — AGE GROUPS ═══════
with tab4:
    st.markdown("<h3>👶 Age Group Analysis</h3>", unsafe_allow_html=True)

    age_monthly = (
        df.groupby("year_month")
        .agg(age_0_5=("age_0_5","sum"), age_5_17=("age_5_17","sum"),
             age_18_greater=("age_18_greater","sum"))
        .reset_index().sort_values("year_month")
    )
    age_monthly = (
        age_monthly.set_index("year_month").reindex(ALL_MONTHS, fill_value=0)
        .reset_index().rename(columns={"index":"year_month"})
    )

    fig_age = go.Figure()
    for col, label, color, show in [
        ("age_0_5","Age 0-5","#0ea5e9",show_0_5),
        ("age_5_17","Age 5-17","#10b981",show_5_17),
        ("age_18_greater","Age 18+","#6366f1",show_18),
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
    fig_age.add_vrect(x0="2025-07", x1="2025-09",
        fillcolor="#fee2e2", opacity=0.3, layer="below", line_width=0)
    fig_age.add_annotation(x="2025-08", yref="paper", y=0.92,
        text="No data Aug 2025", showarrow=False,
        font=dict(size=11, color="#dc2626", family="Arial"))
    chart_layout(fig_age)
    fig_age.update_xaxes(tickangle=-30)
    fig_age.update_yaxes(title="Total Enrolments", tickformat=",.0f")
    fig_age.update_layout(hovermode="x unified", title="Age Group Stacked Area (filtered)",
        legend=dict(font=dict(size=13, color="#1e293b"), orientation="h", y=1.08))
    st.plotly_chart(fig_age, use_container_width=True)

    col_pie, col_bar2 = st.columns(2)
    with col_pie:
        st.markdown("<h4 style='color:#1e3a5f;'>Overall Age Distribution</h4>", unsafe_allow_html=True)
        fig_pie = px.pie(
            values=[df["age_0_5"].sum(), df["age_5_17"].sum(), df["age_18_greater"].sum()],
            names=["Age 0-5","Age 5-17","Age 18+"],
            color_discrete_sequence=["#0ea5e9","#10b981","#6366f1"], hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label",
            textfont=dict(size=13, color="white"))
        fig_pie.update_layout(height=360, paper_bgcolor="white",
            legend=dict(font=dict(size=12, color="#1e293b")))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar2:
        st.markdown("<h4 style='color:#1e3a5f;'>Age Group by Top 10 States</h4>", unsafe_allow_html=True)
        age_state = (
            df.groupby("state")
            .agg(age_0_5=("age_0_5","sum"), age_5_17=("age_5_17","sum"),
                 age_18_greater=("age_18_greater","sum"))
            .sort_values("age_18_greater", ascending=False).head(10).reset_index()
        )
        age_melt = age_state.melt(id_vars="state",
            value_vars=["age_0_5","age_5_17","age_18_greater"],
            var_name="age_group", value_name="enrolments")
        age_melt["age_group"] = age_melt["age_group"].map({
            "age_0_5":"Age 0-5","age_5_17":"Age 5-17","age_18_greater":"Age 18+"})
        fig_age_state = px.bar(age_melt, x="state", y="enrolments",
            color="age_group", barmode="stack",
            color_discrete_map={"Age 0-5":"#0ea5e9","Age 5-17":"#10b981","Age 18+":"#6366f1"},
            labels={"enrolments":"Enrolments","state":"","age_group":"Age Group"})
        chart_layout(fig_age_state, height=360)
        fig_age_state.update_xaxes(tickangle=-45)
        fig_age_state.update_yaxes(tickformat=",.0f")
        fig_age_state.update_layout(
            legend=dict(font=dict(size=12, color="#1e293b"), orientation="h", y=1.08))
        st.plotly_chart(fig_age_state, use_container_width=True)

# ═══════ TAB 5 — DATA QUALITY ═══════
with tab5:
    st.markdown("<h3>🔬 Data Quality Findings</h3>", unsafe_allow_html=True)
    st.info("These findings are what make this project interview-worthy. "
            "Discovering and documenting data issues is the mark of a real analyst.")

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.markdown("""
<h4 style='color:#1e3a5f;'>🔴 Finding 1 — Batch Upload Pattern</h4>
<p style='color:#1e293b;'>Day 1 of every month has <b>massively higher enrolments</b>:</p>
<ul style='color:#1e293b;'>
<li><b>Jul 1 = 616,868</b> (7× daily average)</li>
<li>Apr 1 = 257K | Jun 1 = 215K | May 1 = 183K</li>
</ul>
<p style='color:#1e293b;'>Source system batches previous month's data and uploads on the 1st.<br>
➡️ <b>Monthly aggregation is the correct granularity, not daily.</b></p>
<hr style='border-color:#fde68a;'>
<h4 style='color:#1e3a5f;'>🔴 Finding 2 — August 2025 Missing</h4>
<p style='color:#1e293b;'>Zero records for August 2025 — a <b>data gap</b>, not zero enrolments.<br>
All trend charts show this as a visible line break.</p>
<hr style='border-color:#fde68a;'>
<h4 style='color:#1e3a5f;'>🟡 Finding 3 — State Name Cleaning</h4>
""", unsafe_allow_html=True)
        cleaning_df = pd.DataFrame([
            ["West Bangal, WEST BENGAL (6 variants)", "West Bengal"],
            ["Orissa",                                "Odisha"],
            ["Pondicherry",                           "Puducherry"],
            ["Uttaranchal",                           "Uttarakhand"],
            ["Chhatisgarh",                           "Chhattisgarh"],
            ["Tamilnadu",                             "Tamil Nadu"],
            ["Darbhanga, Jaipur, Nagpur...",          "Dropped (cities in state col)"],
            ["100000",                                "Dropped (garbage)"],
        ], columns=["Raw Value", "Cleaned To"])
        st.dataframe(cleaning_df, hide_index=True, use_container_width=True)

    with col_q2:
        st.markdown("<h4 style='color:#1e3a5f;'>Day-of-Month Distribution</h4>", unsafe_allow_html=True)
        day_dist = enrolment.groupby("day_of_month")["total_enrolments"].sum().reset_index()
        fig_day = go.Figure(go.Bar(
            x=day_dist["day_of_month"],
            y=day_dist["total_enrolments"] / 1000,
            marker_color=["#dc2626" if d==1 else "#3b82f6" for d in day_dist["day_of_month"]],
            hovertemplate="Day %{x}<br>%{y:,.0f}K enrolments<extra></extra>",
        ))
        chart_layout(fig_day, height=380)
        fig_day.update_xaxes(title="Day of Month", dtick=5)
        fig_day.update_yaxes(title="Enrolments (K)")
        st.plotly_chart(fig_day, use_container_width=True)
        st.caption("🔴 Red = Day 1 batch dump | Blue = real daily activity")

    st.markdown("<hr style='border-color:#fde68a;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#1e3a5f;'>Dataset Overview</h4>", unsafe_allow_html=True)
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.metric("Enrolment rows",   f"{len(enrolment):,}")
    col_d2.metric("Biometric rows",   f"{len(biometric):,}" if biometric is not None else "N/A")
    col_d3.metric("Demographic rows", f"{len(demographic):,}" if demographic is not None else "N/A")

# ═══════ TAB 6 — SUMMARY TABLE ═══════
with tab6:
    st.markdown("<h3>📊 Filtered Summary Table</h3>", unsafe_allow_html=True)

    summary = (
        df.groupby("state")
        .agg(total_enrolments=("total_enrolments","sum"),
             age_0_5=("age_0_5","sum"), age_5_17=("age_5_17","sum"),
             age_18_greater=("age_18_greater","sum"),
             months_active=("year_month","nunique"))
        .sort_values("total_enrolments", ascending=False).reset_index()
    )
    summary["age_18_share%"] = (summary["age_18_greater"] / summary["total_enrolments"] * 100).round(1)

    disp = summary.copy()
    for c in ["total_enrolments","age_0_5","age_5_17","age_18_greater"]:
        disp[c] = disp[c].apply(lambda x: f"{x:,.0f}")
    disp["age_18_share%"] = disp["age_18_share%"].apply(lambda x: f"{x:.1f}%")
    disp.columns = ["State","Total Enrolments","Age 0-5","Age 5-17","Age 18+","Months Active","18+ Share"]

    st.dataframe(disp, hide_index=True, use_container_width=True, height=520)
    st.download_button(
        label="⬇️ Download filtered summary as CSV",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="aadhaar_filtered_summary.csv",
        mime="text/csv",
    )