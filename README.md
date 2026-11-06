<div align="center">

# 🏭 Manufacturing Operations & OEE Analytics Dashboard
### End-to-End Python ETL Pipeline • Kimball Star Schema • Power BI Semantic Model (26 DAX Measures) • Predictive Maintenance Analytics

[![Power BI](https://img.shields.io/badge/Power%20BI-Desktop%20%26%20PBIP-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](Manufacturing_OEE_Dashboard.pbip)
[![DAX](https://img.shields.io/badge/DAX-26%20Dynamic%20Measures-00A3E0?style=for-the-badge&logo=microsoft&logoColor=white)](docs/dax_measures.md)
[![Python](https://img.shields.io/badge/Python-3.8%2B%20ETL%20%26%20SciPy-3776AB?style=for-the-badge&logo=python&logoColor=white)](scripts/etl_pipeline.py)
[![Data Model](https://img.shields.io/badge/Data%20Model-Kimball%20Star%20Schema-00B140?style=for-the-badge)](docs/data_dictionary.md)
[![Dataset](https://img.shields.io/badge/Hourly%20Telemetry-145%2C728%20Records-E4002B?style=for-the-badge)](data/processed/fact_production.csv)

*An enterprise-grade Business Intelligence and Industrial Data Engineering solution designed to monitor **Overall Equipment Effectiveness (OEE)**, isolate unplanned downtime via **Pareto (80/20) analysis**, track **Mean Time Between Failures (MTBF)** across 20 machines, and uncover **IoT predictive maintenance triggers**.*

[**📊 Launch Interactive Power BI Studio (`dashboard_preview.html`)**](dashboard/dashboard_preview.html) • [**📐 DAX Implementation Guide**](docs/dax_measures.md) • [**🗄️ Data Dictionary**](docs/data_dictionary.md) • [**🎤 Interview Playbook**](Interview_Crash_Course.md)

</div>

---

## 🖼️ Executive Dashboard Preview

![Manufacturing Operations & OEE Analytics Dashboard](dashboard/screenshots/main_dashboard.png)

> **Interactive Studio Included:** Open [`dashboard/dashboard_preview.html`](dashboard/dashboard_preview.html) in any browser to explore the full **Power BI Desktop Studio** experience—featuring **7 global slicers**, **5 interactive report pages**, a live **Kimball Star Schema Model View**, a **Data Table Browser**, and a **Live 26-Measure DAX Evaluator** powered directly by the 145,728-row processed dataset.

---

## 🎯 Business Problem & Quantified Executive Impact

Factory floor leadership lacked unified visibility into **why production lines were missing the 85.0% World-Class OEE benchmark**—whether losses stemmed from machine breakdowns (Availability), slow cycle speeds (Performance), or scrap defects (Quality).

By engineering an automated **Python ETL pipeline** and a **Power BI Kimball Star Schema**, this project analyzed **145,728 hourly machine logs** across **5 production lines**, **20 industrial machines**, **8 products**, **3 shifts**, and **10 operators** (Jan–Dec 2024), delivering four high-impact operational findings:

| KPI / Strategic Dimension | Baseline Value (2024) | World-Class Benchmark | Root-Cause Finding & Quantified Business Impact |
| :--- | :---: | :---: | :--- |
| **Overall OEE (`[OEE]`)** | **82.54% DAX** *(82.60% Mean)* | **≥ 85.0%** | Closing the **2.46% OEE gap** (led by bottleneck `Line_E` at **78.92%**) yields **+610,832 good units/yr** and **+$90.27M in incremental annual production value**. |
| **OEE Components (`A × P × Q`)** | **94.37% × 90.84% × 96.28%** | **90% × 95% × 99%** | **Availability (94.37%)** beats target; **Performance (90.84%)** and **Quality (96.28%)** are the primary drags on plant efficiency. |
| **Total Production & Value** | **21,027,873 Good Units** | *21,839,423 Total* | Generates **$3,107,610,212 ($3.11B)** in salable output (`SUMX(good_units × RELATED(unit_cost_usd))`), with **811,550 defect units (3.72% Scrap = $120.2M COPQ)**. |
| **Downtime & Fleet MTBF** | **8,198h Total / 4,259h Unplanned** | **Fleet MTBF: 33.0h** | **Equipment Failure (1,613h)** and **Material Shortage (612h)** drive **52.3%** of all unplanned downtime. `Assembly_Robot_E3` has the lowest reliability (**29.75h MTBF**). |
| **Shift ANOVA & Workforce** | **Morning 87.4% vs. Night 79.6%** | **ANOVA $p < 0.0001$** | One-Way ANOVA ($F = 3,433.49$) confirms a severe Night Shift drop. Uncertified Junior operators (`OP-005`, `OP-006`, `OP-009`) have a **5.12% scrap rate vs. 3.12%** for Certified staff. |
| **IoT Sensor Telemetry** | **Vib $r = +0.237$ / Temp $\Delta r = +0.049$** | **$\le 8\text{ mm/s}$, $\Delta T \le +10^\circ\text{C}$** | When vibration exceeds **8.0 mm/s**, scrap surges **3.50% → 6.36%** (+82%). When temperature exceeds **+10°C above machine baseline**, scrap jumps **3.60% → 5.45%**. |

---

## 🏗️ End-to-End Architecture & Data Engineering Pipeline

```mermaid
flowchart LR
    subgraph S1["1. Raw Factory Telemetry"]
        A["📄 manufacturing_data.csv<br/>145,728 Hourly Machine Logs<br/>27 Raw Attributes"]
    end

    subgraph S2["2. Python Pandas ETL (etl_pipeline.py)"]
        B["🧹 Data Quality Gates<br/>• Deduplicate record_id<br/>• Clip negative metrics to 0<br/>• Enforce Good + Defect = Total<br/>• Compute Row-Level OEE & KPIs"]
    end

    subgraph S3["3. Kimball Star Schema (data/processed/)"]
        F[("📊 fact_production<br/>145,728 Rows × 28 Cols")]
        D1[("📅 dim_date<br/>366 Days • FY Calendar")]
        D2[("🔧 dim_machine<br/>20 Machines • 7 Types")]
        D3[("📦 dim_product<br/>8 SKUs • 4 Segments")]
        D4[("⏰ dim_shift<br/>3 Shifts • Day/Night")]
        D5[("👷 dim_operator<br/>10 Staff • Certification")]
    end

    subgraph S4["4. Power BI & Analytics Layer"]
        M["📐 _Measures Table<br/>26 Dynamic DAX Formulas<br/>Time Intelligence & MTBF"]
        V["🖥️ 5-Page Power BI Dashboard<br/>& SciPy Statistical Suite"]
    end

    A --> B
    B --> F
    B --> D1 & D2 & D3 & D4 & D5
    D1 & D2 & D3 & D4 & D5 -->|1 : * Single-Dir| F
    F --> M --> V
```

### Stage 1: Python ETL & Data Quality Engineering ([`scripts/etl_pipeline.py`](scripts/etl_pipeline.py))
- **Automated Sanitization:** Removes duplicate `record_id` keys, clips negative sensor/time anomalies (`clip(lower=0)`), and enforces the accounting identity `good_units = total_units_produced - defect_units`.
- **Dimensional Normalization:** Splits denormalized strings (OEM manufacturers, product catalog pricing, shift windows, operator certifications) into 5 normalized dimension tables with surrogate keys (`date_key` in `YYYYMMDD` integer format, `machine_key`, `product_key`, `shift_key`, `operator_key`).
- **Row-Level KPI Enrichment:** Computes `availability`, `performance`, `quality`, `oee`, `scrap_rate`, and `energy_per_unit_kwh` for granular statistical hypothesis testing.

### Stage 2: Statistical Hypothesis Testing ([`scripts/analytics.py`](scripts/analytics.py))
- Runs automated **One-Way ANOVA (`scipy.stats.f_oneway`)** across shifts, **Pearson correlation (`scipy.stats.pearsonr`)** on IoT telemetry, **80/20 Pareto cumulative distributions**, and **MTBF fleet benchmarking**, outputting high-DPI visual diagnostics to [`dashboard/screenshots/`](dashboard/screenshots/) and an executive briefing to [`analysis/insights_summary.md`](analysis/insights_summary.md).

---

## 🗄️ Kimball Star Schema Data Model

The Power BI semantic model ([`Manufacturing_OEE_Dashboard.SemanticModel/model.bim`](Manufacturing_OEE_Dashboard.SemanticModel/model.bim)) follows strict **Kimball Star Schema** best practices. All relationships are **Many-to-One (`*:1`)** with **Single-Direction Cross-Filtering** flowing from Dimension (`1`) to Fact (`*`) to maximize VertiPaq columnar compression and eliminate ambiguous filter paths.

```mermaid
erDiagram
    dim_date ||--o{ fact_production : "date_key (1:*)"
    dim_machine ||--o{ fact_production : "machine_key (1:*)"
    dim_product ||--o{ fact_production : "product_key (1:*)"
    dim_shift ||--o{ fact_production : "shift_key (1:*)"
    dim_operator ||--o{ fact_production : "operator_key (1:*)"

    fact_production {
        int64 record_id PK
        int64 date_key FK
        string machine_id FK
        string product_id FK
        string shift_id FK
        string operator_id FK
        string production_line
        double planned_production_time_min
        double actual_run_time_min
        double downtime_min
        string downtime_reason
        double ideal_cycle_time_sec
        double actual_cycle_time_sec
        int64 total_units_produced
        int64 good_units
        int64 defect_units
        double availability
        double performance
        double quality
        double oee
        double scrap_rate
        double temperature_c
        double vibration_mm_s
        double energy_kwh
    }

    dim_date {
        int64 date_key PK "YYYYMMDD"
        date date "2024-01-01..2024-12-31"
        int64 year
        int64 quarter
        string quarter_name "Q1..Q4"
        int64 month
        string month_name "Sorted by month"
        int64 is_weekend "0 or 1"
        int64 fiscal_year "Apr-Mar Calendar"
        int64 fiscal_quarter
    }

    dim_machine {
        string machine_key PK "20 Active Assets"
        string machine_type "7 Equipment Classes"
        string production_line "Line_A..Line_E"
        string manufacturer "DMG MORI, ARBURG, FANUC, etc."
        int64 install_year "2019..2022"
        int64 maintenance_interval_hrs "400..2000 hrs"
    }

    dim_product {
        string product_key PK "PRD-001..PRD-008"
        string product_name "8 Industrial SKUs"
        string product_category "Aerospace, Building Tech, Industrial, Safety"
        double target_cycle_time_sec "15s..50s"
        double unit_cost_usd "$45.00..$320.00"
    }

    dim_shift {
        string shift_key PK "SHIFT-1..SHIFT-3"
        string shift_name "Morning, Afternoon, Night"
        string hours_range "06-14, 14-22, 22-06"
        int64 is_day_shift "1 or 0"
    }

    dim_operator {
        string operator_key PK "OP-001..OP-010"
        string operator_name "10 Plant Operators"
        string experience_level "Senior, Mid, Junior"
        int64 is_certified "1=Certified, 0=Uncertified"
        int64 hire_year "2016..2024"
    }
```

---

## 📊 Deep-Dive Analytical Visuals & Statistical Findings

### 1. Monthly OEE & Component Trends by Production Line
![OEE Trends by Production Line](dashboard/screenshots/oee_trends.png)
- **`Line_B` (85.39% OEE)** consistently exceeds the 85% World-Class threshold, followed by **`Line_D` (83.91%)** and **`Line_A` (83.14%)**.
- **`Line_E` (78.92% OEE)** and **`Line_C` (80.38% OEE)** require targeted cycle-speed optimization, as Performance (`90.84%` vs `95.0%` target) represents the largest component gap.

---

### 2. Downtime Pareto Analysis (80/20 Rule)
![Downtime Pareto Chart](dashboard/screenshots/downtime_pareto.png)
- Across **8,198 total downtime hours**, **Planned Maintenance (`3,939.2h` / 48.1%)**, **Equipment Failure (`1,612.8h` / 19.7%)**, and **Material Shortage (`612.1h` / 7.5%)** account for **75.2%** of all stopped time.
- When filtering to **Unplanned Downtime Only (`4,258.7 hours`)** via the DAX `[Unplanned Downtime]` measure, **Equipment Failure (37.9%)**, **Material Shortage (14.4%)**, **Changeover/Setup (14.2%)**, and **Power Outage (13.8%)** drive **80.3%** of avoidable factory stops.

---

### 3. IoT Sensor Telemetry & Resolving Simpson's Paradox
![Sensor Correlation Analysis](dashboard/screenshots/sensor_correlation.png)
- **Vibration Alert Trigger (`> 8.0 mm/s`):** Vibration shows a strong positive correlation with defect rate ($r = +0.237, p < 0.0001$). Operating hours with vibration $\le 8.0\text{ mm/s}$ average **3.50% scrap**, whereas readings $> 8.0\text{ mm/s}$ surge to **6.36% scrap** (+82% increase).
- **Resolving Simpson's Paradox in Temperature Telemetry:** Pooling raw temperature (`temperature_c`) across all 20 machines creates an artificial negative correlation ($r = -0.029$) because Injection Molders normally operate at `180°C` while Quality Scanners run at `28°C`. Normalizing temperature as **deviation from each machine class's baseline ($\Delta^\circ\text{C} = T - T_{\text{baseline}}$)** uncovers the true positive correlation ($r = +0.049, p = 6.99 \times 10^{-78}$): overheating $> +10^\circ\text{C}$ spikes scrap from **3.60% to 5.45%**.

---

### 4. Shift Performance Comparison (One-Way ANOVA)
![Shift Performance Comparison](dashboard/screenshots/shift_performance.png)
- **Statistical Proof of Night Shift Drop:** One-Way ANOVA across the 3 shifts confirms a highly significant variance ($F = 3,433.49, p < 0.0001$):
  - **Morning Shift (`06:00–14:00`):** **87.36% OEE** (World Class ✅)
  - **Afternoon Shift (`14:00–22:00`):** **85.28% OEE** (World Class ✅)
  - **Night Shift (`22:00–06:00`):** **79.60% OEE** (-7.76% below Morning ⚠️)

---

### 5. Machine Reliability Ranking (Mean Time Between Failures — MTBF)
![Machine Reliability MTBF](dashboard/screenshots/machine_reliability.png)
- Fleet-wide **MTBF is 33.0 hours** across **4,169 Equipment Failure incidents** (`137,530` total run hours).
- **Top Overhaul Priorities:** `Assembly_Robot_E3` (**29.75 hrs MTBF**, 199 failures), `Injection_Molder_C2` (**30.19 hrs MTBF**), and `Assembly_Robot_C3` (**30.47 hrs MTBF**).
- **Benchmark Assets:** `Assembly_Robot_B3` (**37.56 hrs MTBF**) and `CNC_Mill_A1` (**37.33 hrs MTBF**).

---

## 📐 Advanced DAX Measures Architecture ([`docs/dax_measures.md`](docs/dax_measures.md))

All **26 DAX measures** are housed in a dedicated `_Measures` table (exported in [`dashboard/powerbi/All_26_DAX_Measures.dax`](dashboard/powerbi/All_26_DAX_Measures.dax) and embedded in [`Manufacturing_OEE_Dashboard.SemanticModel/model.bim`](Manufacturing_OEE_Dashboard.SemanticModel/model.bim)) and organized into 6 display folders:

```dax
// 1. Dynamic Ratio-of-Sums OEE & Iterator Performance Rate
Performance Rate = 
DIVIDE(
    SUMX(
        fact_production,
        fact_production[ideal_cycle_time_sec] * fact_production[total_units_produced]
    ),
    SUM(fact_production[actual_run_time_min]) * 60,
    0
)

OEE = 
VAR _Availability = [Availability]
VAR _Performance  = [Performance Rate]
VAR _Quality      = [Quality Rate]
RETURN
    _Availability * _Performance * _Quality

// 2. Cross-Table Revenue Calculation via SUMX + RELATED
Production Value = 
SUMX(
    fact_production,
    fact_production[good_units] * RELATED(dim_product[unit_cost_usd])
)

// 3. Filter-Context Manipulation for Unplanned Downtime
Unplanned Downtime = 
DIVIDE(
    CALCULATE(
        SUM(fact_production[downtime_min]),
        NOT(fact_production[downtime_reason] IN {"Planned Maintenance", "No Downtime"})
    ),
    60,
    0
)

// 4. Null-Safe Month-over-Month Time Intelligence
OEE MoM Change = 
VAR _Current  = [OEE]
VAR _Previous = CALCULATE([OEE], DATEADD(dim_date[date], -1, MONTH))
RETURN
    IF(NOT(ISBLANK(_Previous)), _Current - _Previous, BLANK())

// 5. Fleet Reliability (Mean Time Between Failures)
MTBF Hours = 
DIVIDE(
    SUM(fact_production[actual_run_time_min]) / 60,
    CALCULATE(COUNTROWS(fact_production), fact_production[downtime_reason] = "Equipment Failure"),
    SUM(fact_production[actual_run_time_min]) / 60
)
```

---

## 📂 Repository Structure

```text
Power_BI_Project/
├── Manufacturing_OEE_Dashboard.pbip               # Power BI Desktop Project file
├── Manufacturing_OEE_Dashboard.SemanticModel/
│   ├── definition.pbism
│   └── model.bim                                  # Tabular Model (6 Tables, 5 Relationships, 26 DAX Measures)
├── Manufacturing_OEE_Dashboard.Report/
│   └── definition.pbir                            # Power BI Report definition
├── dashboard/
│   ├── dashboard_preview.html                     # ⭐ 5-Page Interactive Power BI Studio (100% Real Data)
│   ├── powerbi/
│   │   ├── All_26_DAX_Measures.dax                # Complete DAX script for Tabular Editor / DAX Studio
│   │   ├── Honeywell_Industrial_Dark_Theme.json   # Custom Power BI JSON Theme
│   │   └── PowerQuery_M_StarSchema.pq             # Power Query M loader script
│   └── screenshots/
│       ├── main_dashboard.png                     # Executive dashboard overview
│       ├── oee_trends.png                         # Monthly OEE & component trends
│       ├── downtime_pareto.png                    # 80/20 Downtime Pareto chart
│       ├── sensor_correlation.png                 # Vibration & Normalized Δ°C scatter plots
│       ├── shift_performance.png                  # Shift ANOVA boxplot & bar comparison
│       └── machine_reliability.png                # 20-Machine MTBF ranking
├── data/
│   ├── raw/
│   │   └── manufacturing_data.csv                 # Raw hourly factory floor telemetry (145,728 rows)
│   └── processed/                                 # Clean Kimball Star Schema CSVs
│       ├── fact_production.csv                    # Fact table (145,728 rows × 28 cols)
│       ├── dim_date.csv                           # Date dimension (366 days, Fiscal + Calendar)
│       ├── dim_machine.csv                        # Machine dimension (20 machines, 7 types, OEMs)
│       ├── dim_product.csv                        # Product dimension (8 SKUs, 4 categories, unit cost)
│       ├── dim_shift.csv                          # Shift dimension (Morning, Afternoon, Night)
│       └── dim_operator.csv                       # Operator dimension (10 staff, Certification, Tenure)
├── scripts/
│   ├── generate_data.py                           # Synthetic IoT & manufacturing telemetry generator
│   ├── etl_pipeline.py                            # Pandas ETL cleaning & Star Schema builder
│   └── analytics.py                               # SciPy ANOVA, Pearson correlation & chart generator
├── analysis/
│   └── insights_summary.md                        # Automated executive summary & ROI calculations
├── docs/
│   ├── data_dictionary.md                         # Full schema & relationship documentation
│   └── dax_measures.md                            # Step-by-step Power BI & DAX implementation guide
├── Interview_Crash_Course.md                      # 🎤 Elevator pitch, exact metrics & Q&A cheat sheet
└── README.md
```

---

## 🚀 Quick Start & Reproduction Guide

### 1. Run the Data Engineering & Statistical Pipeline
```bash
# Install dependencies
pip install pandas numpy scipy matplotlib

# (Optional) Regenerate the 145,728 raw hourly machine records
python scripts/generate_data.py

# Run the ETL pipeline to build the 6 Kimball Star Schema CSVs in data/processed/
python scripts/etl_pipeline.py

# Run the SciPy statistical suite (ANOVA, Pareto, Sensor Correlations, MTBF) & export charts
python scripts/analytics.py
```

### 2. Explore the Interactive Dashboard
1. **Instant Browser Studio (Zero Setup):** Open [`dashboard/dashboard_preview.html`](dashboard/dashboard_preview.html) in Chrome or Edge to interact with all **5 Report Pages**, **7 Slicers**, **Star Schema Model View**, **Table View**, and **26 Live DAX Measures**.
2. **Power BI Desktop:** Open [`Manufacturing_OEE_Dashboard.pbip`](Manufacturing_OEE_Dashboard.pbip) in Power BI Desktop (or import `data/processed/*.csv`, apply [`dashboard/powerbi/Honeywell_Industrial_Dark_Theme.json`](dashboard/powerbi/Honeywell_Industrial_Dark_Theme.json), and load [`dashboard/powerbi/All_26_DAX_Measures.dax`](dashboard/powerbi/All_26_DAX_Measures.dax)).

---

## 🛠️ Tech Stack
- **Business Intelligence:** Power BI Desktop (`.pbip` / Tabular `model.bim`), DAX, Power Query M
- **Data Engineering & Statistics:** Python 3, Pandas, NumPy, SciPy (`f_oneway`, `pearsonr`), Matplotlib
- **Interactive Frontend Studio:** HTML5, CSS3, Chart.js 4, Embedded Multi-Dimensional OLAP Cube

---
<div align="center">
  <i>Designed & Engineered by <b>Kabir Roy</b></i>
</div>
