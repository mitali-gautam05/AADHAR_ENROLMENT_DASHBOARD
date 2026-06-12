# 🇮🇳 Aadhaar Enrolment Intelligence Dashboard

An end-to-end data analytics project built on ~1M UIDAI Aadhaar enrolment records (March–October 2025). Covers data cleaning, exploratory analysis, geospatial mapping, time-series trend analysis, and a live interactive Streamlit dashboard.


## 📸 Dashboard Preview

> *(Add a screenshot after deployment — drag an image here on GitHub)*

---

## 📌 Project Highlights

- Cleaned **~1M raw records** across 36 states/UTs — resolved 55 dirty state name variants
- Built an **India choropleth map** using Plotly and Folium with correct GeoJSON alignment
- Discovered a **batch upload pattern** (Day 1 of every month = 5–7× normal volume) — documented as a data quality finding
- Identified **August 2025 data gap** — full month missing from source, shown as explicit break in all trend charts
- Deployed as a **live filterable dashboard** with state selector, date range slider, and age group toggle

---

## 🗂️ Project Structure

```
UIDAI_APP/
├── app.py                          # Streamlit dashboard (6 tabs)
├── requirements.txt                # Pinned package versions
├── README.md                       # This file
└── data/
    ├── enrolment_clean.csv         # 1,006,007 rows — main dataset
    ├── biometric_clean.csv         # 1,861,108 rows
    ├── demographic_clean.csv       # 2,071,698 rows
    ├── state_enrolment.csv         # 36-row aggregation (Phase 3 input)
    ├── monthly_trend.csv           # Monthly totals (Phase 4 input)
    ├── choropleth_plotly.html      # Interactive India map (Plotly)
    ├── choropleth_folium.html      # Interactive India map (Folium/Leaflet)
    ├── state_ranking_chart.html    # State enrolment ranked bar chart
    ├── trend_national_monthly.html # Annotated national trend line
    ├── trend_top5_states.html      # Top 5 states comparison
    ├── trend_age_groups.html       # Age group stacked area chart
    ├── trend_mom_growth.html       # Month-on-month growth rate
    ├── heatmap_state_month.png     # State × month heatmap
    └── chart_day_of_month.png      # Batch upload pattern chart
```

---

## 🧱 Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| Data wrangling | Pandas 2.2.2, NumPy 1.26.4 |
| Visualisation | Plotly 5.22, Matplotlib 3.9, Seaborn 0.13 |
| Geo mapping | Plotly Choropleth, Folium, India GeoJSON |
| Dashboard | Streamlit 1.35 |
| Notebooks | Google Colab (Phases 1–4) |
| IDE | VS Code (Phase 5) |

---

## 🔬 Build Phases

### Phase 1 — Data Cleaning
- Loaded 3 datasets from zip files (enrolment, biometric, demographic)
- Resolved **55 dirty state name variants** to canonical 36 (28 states + 8 UTs)
- Key fixes: `West Bangal` → West Bengal, `Orissa` → Odisha, `Pondicherry` → Puducherry, `Uttaranchal` → Uttarakhand, 5 Dadra/Daman variants → merged UT name
- Dropped cities incorrectly entered in state column (Darbhanga, Jaipur, Nagpur, Puttenahalli, BALANAGAR, Raja Annamalai Puram)
- Parsed dates from `DD-MM-YYYY` strings to `datetime64`
- Result: zero nulls, zero negatives, exactly 36 canonical states across all 3 datasets

### Phase 2 — Exploratory Data Analysis
- State-wise aggregation and ranking
- Age group breakdown (national pie + state-wise stacked bar)
- Monthly trend with `resample('ME')` — correct time-series pandas idiom
- State × month heatmap
- District-level drill-down for top 5 states
- Biometric vs demographic update rate diverging bar chart

### Phase 3 — India Choropleth Map
- Fetched India GeoJSON from `geohacker/india` (property key: `NAME_1`)
- Resolved GeoJSON mismatches: old names (Orissa, Uttaranchal), missing states (Telangana pre-2014, Ladakh pre-2019), Dadra/Daman split 50/50 across two old polygons
- Built interactive Plotly choropleth (hover tooltips, colour scale)
- Built standalone Folium/Leaflet map (self-contained HTML)

### Phase 4 — Time-Series Analysis
- National monthly trend with event annotations
- **Key finding:** August 2025 has zero records — full data gap, not zero enrolments
- **Key finding:** Day 1 of every month = batch upload from previous month (Jul 1 = 616,868 enrolments, 7× daily average) — daily analysis is misleading, monthly is correct
- State × month heatmap showing August as explicit grey column
- Month-on-month growth rate by state

### Phase 5 — Streamlit Dashboard
- 6-tab interactive app: Trends, Maps, EDA, Age Groups, Data Quality, Summary Table
- `@st.cache_data` on all data loaders — 62MB CSV read once, cached in memory
- Sidebar filters: state multiselect, date range slider, age group toggles
- All Phase 2–4 charts embedded + live filtered versions reacting to sidebar
- `add_vrect` annotation crash fixed: annotations always via separate `add_annotation`

---

## 📊 Dataset

| Dataset | Rows | Columns |
|---|---|---|
| Enrolment (cleaned) | 1,006,007 | date, state, district, pincode, age_0_5, age_5_17, age_18_greater, total_enrolments |
| Biometric (cleaned) | 1,861,108 | date, state, district, pincode, bio_age_5_17, bio_age_17_ |
| Demographic (cleaned) | 2,071,698 | date, state, district, pincode, demo_age_5_17, demo_age_17_ |

**Source:** UIDAI public enrolment data | **Date range:** March–October 2025  
**Note:** August 2025 is absent from the source dataset entirely.

---

## ⚠️ Key Data Quality Findings

| Finding | Detail |
|---|---|
| Batch upload pattern | Day 1 of each month contains the entire previous month's data uploaded at once |
| August 2025 gap | No records exist for August 2025 in the source data |
| 55 dirty state variants | Inconsistent casing, old names, typos, cities in state column |
| GeoJSON pre-2014 | Telangana and Ladakh don't exist in the boundary file — mapped to parent state polygons |

---

## 🚀 Run Locally

```bash
git clone https://github.com/your-username/UIDAI_APP.git
cd UIDAI_APP

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

# Copy cleaned CSVs and HTML charts into data/ subfolder
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub (exclude `data/` — files too large)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Connect your GitHub repo, set main file: `app.py`
4. For data files: share CSVs via Google Drive public link and update `load_all_data()` to read from URL:
```python
url = f"https://drive.google.com/uc?id=YOUR_FILE_ID&export=download"
df = pd.read_csv(url, parse_dates=["date"])
```
---
