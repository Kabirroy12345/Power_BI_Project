# DAX Measures — Power BI Implementation Guide

## Overview

This document contains all DAX measures needed to recreate the Manufacturing Operations & OEE Dashboard in Power BI Desktop. Import the processed CSV files from `data/processed/` and set up relationships as described in the Data Dictionary.

---

## Step 1: Import Data & Set Up Relationships

1. Open Power BI Desktop → **Get Data** → **Text/CSV**
2. Import all 6 files from `data/processed/`:
   - `fact_production.csv` (Fact table)
   - `dim_date.csv`, `dim_machine.csv`, `dim_product.csv`, `dim_shift.csv`, `dim_operator.csv`
3. Go to **Model View** and create the following relationships:

| From (Fact) | To (Dimension) | Key |
|-------------|-----------------|-----|
| `fact_production[date_key]` | `dim_date[date_key]` | Many-to-One |
| `fact_production[machine_id]` | `dim_machine[machine_key]` | Many-to-One |
| `fact_production[product_id]` | `dim_product[product_key]` | Many-to-One |
| `fact_production[shift_id]` | `dim_shift[shift_key]` | Many-to-One |
| `fact_production[operator_id]` | `dim_operator[operator_key]` | Many-to-One |

---

## Step 2: Create a Measures Table

In Power BI, create a dedicated **Measures** table:
- **Home** → **Enter Data** → Name the table `_Measures` → Click **Load**

---

## Step 3: DAX Measures

### Core OEE Measures

```dax
// Overall Equipment Effectiveness
OEE = 
VAR _Availability = [Availability]
VAR _Performance = [Performance Rate]
VAR _Quality = [Quality Rate]
RETURN
    _Availability * _Performance * _Quality

// Availability: Actual Run Time / Planned Production Time
Availability = 
DIVIDE(
    SUM(fact_production[actual_run_time_min]),
    SUM(fact_production[planned_production_time_min]),
    0
)

// Performance: (Ideal Cycle Time × Total Units) / Actual Run Time (in seconds)
Performance Rate = 
DIVIDE(
    SUMX(
        fact_production,
        fact_production[ideal_cycle_time_sec] * fact_production[total_units_produced]
    ),
    SUM(fact_production[actual_run_time_min]) * 60,
    0
)

// Quality: Good Units / Total Units
Quality Rate = 
DIVIDE(
    SUM(fact_production[good_units]),
    SUM(fact_production[total_units_produced]),
    0
)
```

### Production Measures

```dax
// Total Units Produced
Total Units = SUM(fact_production[total_units_produced])

// Total Good Units
Good Units = SUM(fact_production[good_units])

// Total Defect Units
Defect Units = SUM(fact_production[defect_units])

// Scrap Rate
Scrap Rate = 
DIVIDE(
    [Defect Units],
    [Total Units],
    0
)

// Production Value (USD)
Production Value = 
SUMX(
    fact_production,
    fact_production[good_units] * RELATED(dim_product[unit_cost_usd])
)
```

### Downtime Measures

```dax
// Total Downtime (Hours)
Downtime Hours = 
DIVIDE(
    SUM(fact_production[downtime_min]),
    60,
    0
)

// Downtime Percentage
Downtime % = 
DIVIDE(
    SUM(fact_production[downtime_min]),
    SUM(fact_production[planned_production_time_min]),
    0
)

// Unplanned Downtime Hours
Unplanned Downtime = 
DIVIDE(
    CALCULATE(
        SUM(fact_production[downtime_min]),
        NOT(fact_production[downtime_reason] IN {"Planned Maintenance", "No Downtime"})
    ),
    60,
    0
)
```

### Time Intelligence Measures

```dax
// OEE Previous Month
OEE PM = 
CALCULATE(
    [OEE],
    DATEADD(dim_date[date], -1, MONTH)
)

// OEE Month-over-Month Change
OEE MoM Change = 
VAR _Current = [OEE]
VAR _Previous = [OEE PM]
RETURN
    IF(
        NOT(ISBLANK(_Previous)),
        _Current - _Previous,
        BLANK()
    )

// OEE MoM % Change
OEE MoM % = 
DIVIDE(
    [OEE MoM Change],
    [OEE PM],
    BLANK()
)

// YTD Good Units
Good Units YTD = 
CALCULATE(
    [Good Units],
    DATESYTD(dim_date[date])
)

// Running Total Production
Running Total Units = 
CALCULATE(
    [Good Units],
    FILTER(
        ALL(dim_date),
        dim_date[date] <= MAX(dim_date[date])
    )
)
```

### Energy Measures

```dax
// Total Energy (kWh)
Total Energy kWh = SUM(fact_production[energy_kwh])

// Energy per Good Unit
Energy per Unit = 
DIVIDE(
    [Total Energy kWh],
    [Good Units],
    0
)

// Energy Efficiency (Units per kWh)
Energy Efficiency = 
DIVIDE(
    [Good Units],
    [Total Energy kWh],
    0
)
```

### Machine Reliability Measures

```dax
// Equipment Failure Count
Failure Count = 
CALCULATE(
    COUNTROWS(fact_production),
    fact_production[downtime_reason] = "Equipment Failure"
)

// MTBF (Mean Time Between Failures)
MTBF Hours = 
DIVIDE(
    SUM(fact_production[actual_run_time_min]) / 60,
    [Failure Count],
    SUM(fact_production[actual_run_time_min]) / 60
)
```

### KPI Formatting Measures

```dax
// OEE Status (for conditional formatting)
OEE Status = 
SWITCH(
    TRUE(),
    [OEE] >= 0.85, "World Class",
    [OEE] >= 0.75, "Good",
    [OEE] >= 0.65, "Needs Improvement",
    "Critical"
)

// OEE Status Color
OEE Color = 
SWITCH(
    TRUE(),
    [OEE] >= 0.85, "#00B140",
    [OEE] >= 0.75, "#FFC72C",
    [OEE] >= 0.65, "#F97316",
    "#E4002B"
)

// Trend Arrow
OEE Trend Arrow = 
IF(
    [OEE MoM Change] > 0,
    "▲ " & FORMAT(ABS([OEE MoM Change]) * 100, "0.0") & "%",
    "▼ " & FORMAT(ABS([OEE MoM Change]) * 100, "0.0") & "%"
)
```

---

## Step 4: Recommended Visuals

| Visual | Purpose | Measures Used |
|--------|---------|---------------|
| **KPI Card** | Overall OEE | `[OEE]`, `[OEE MoM Change]` |
| **Gauge** | Availability / Performance / Quality | Individual rates |
| **Line Chart** | OEE Trend by Month | `[OEE]` by `dim_date[month_name]` with `production_line` legend |
| **Stacked Bar** | Downtime Pareto | `[Downtime Hours]` by `downtime_reason` |
| **Donut Chart** | Production by Category | `[Good Units]` by `dim_product[product_category]` |
| **Matrix** | Line Performance | Lines × OEE metrics with conditional formatting |
| **Scatter Plot** | Sensor Correlation | `temperature_c` vs `scrap_rate`, `vibration_mm_s` vs `scrap_rate` |
| **Bar Chart** | MTBF Ranking | `[MTBF Hours]` by `machine_id` |
| **Clustered Bar** | Shift Comparison | `[OEE]` by `dim_shift[shift_name]` |

---

## Step 5: Dashboard Design Tips

1. **Color Palette**: Use Honeywell-inspired colors (#E4002B red, #1B365D navy, #00A3E0 blue)
2. **Background**: Set page background to dark (#1a1a2e) for a modern look
3. **Fonts**: Use Segoe UI or DIN for a clean industrial feel
4. **Conditional Formatting**: Apply to OEE values (Green ≥85%, Yellow ≥75%, Red <75%)
5. **Slicers**: Add date range, production line, machine type, and shift slicers
