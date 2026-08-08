# Data Dictionary — Manufacturing Operations Dataset

## Overview

This document describes all columns in the raw and processed datasets used in the Manufacturing Operations & OEE Analytics Dashboard.

---

## Raw Data: `manufacturing_data.csv`

| # | Column | Data Type | Description | Example |
|---|--------|-----------|-------------|---------|
| 1 | `record_id` | Integer | Unique identifier for each hourly record | 1, 2, 3... |
| 2 | `timestamp` | Datetime | Full timestamp of the record (hourly granularity) | 2024-01-01 06:00:00 |
| 3 | `date` | Date | Date portion of the timestamp | 2024-01-01 |
| 4 | `hour` | Integer | Hour of day (0–23) | 6, 14, 22 |
| 5 | `production_line` | String | Production line identifier | Line_A, Line_B |
| 6 | `machine_id` | String | Unique machine identifier | CNC_Mill_A1 |
| 7 | `machine_type` | String | Type/class of machine | CNC_Mill, Injection_Molder |
| 8 | `product_id` | String | Product being manufactured | PRD-001 |
| 9 | `product_name` | String | Human-readable product name | Turbo Actuator Valve |
| 10 | `product_category` | String | Business segment category | Aerospace, Building Tech |
| 11 | `operator_id` | String | Operator on duty | OP-001 |
| 12 | `operator_name` | String | Operator's name | Rajesh Kumar |
| 13 | `operator_experience` | String | Experience level | Senior, Mid, Junior |
| 14 | `shift_id` | String | Shift identifier | SHIFT-1, SHIFT-2, SHIFT-3 |
| 15 | `shift_name` | String | Shift name | Morning, Afternoon, Night |
| 16 | `planned_production_time_min` | Float | Planned production time (minutes) | 60 |
| 17 | `actual_run_time_min` | Float | Actual machine run time (minutes) | 48.5 |
| 18 | `downtime_min` | Float | Unplanned/planned downtime (minutes) | 11.5 |
| 19 | `downtime_reason` | String | Reason for downtime | Equipment Failure |
| 20 | `ideal_cycle_time_sec` | Float | Theoretical best cycle time (seconds/unit) | 45 |
| 21 | `actual_cycle_time_sec` | Float | Measured cycle time (seconds/unit) | 52.3 |
| 22 | `total_units_produced` | Integer | Total units produced (good + defect) | 85 |
| 23 | `good_units` | Integer | Units passing quality inspection | 82 |
| 24 | `defect_units` | Integer | Units failing quality inspection | 3 |
| 25 | `temperature_c` | Float | Machine operating temperature (°C) | 67.3 |
| 26 | `vibration_mm_s` | Float | Machine vibration reading (mm/s) | 3.45 |
| 27 | `energy_kwh` | Float | Energy consumed during the hour (kWh) | 11.2 |

---

## Processed Data: Star Schema

### Fact Table: `fact_production.csv`

All columns from raw data plus the following computed KPI columns:

| Column | Formula | Description |
|--------|---------|-------------|
| `date_key` | YYYYMMDD format | Foreign key to dim_date |
| `availability` | `actual_run_time_min / planned_production_time_min` | Equipment availability ratio (0–1) |
| `performance` | `(ideal_cycle_time_sec × total_units) / (actual_run_time_min × 60)` | Speed efficiency ratio (0–1) |
| `quality` | `good_units / total_units_produced` | First-pass quality ratio (0–1) |
| `oee` | `availability × performance × quality` | Overall Equipment Effectiveness (0–1) |
| `scrap_rate` | `defect_units / total_units_produced` | Defect ratio (0–1) |
| `energy_per_unit_kwh` | `energy_kwh / good_units` | Energy efficiency metric |

### Dimension Tables

#### `dim_date.csv`
| Column | Description |
|--------|-------------|
| `date_key` | Primary key (YYYYMMDD integer) |
| `date` | ISO date string |
| `year`, `quarter`, `month` | Calendar hierarchy |
| `month_name`, `day_name` | Human-readable labels |
| `week_of_year`, `day_of_month`, `day_of_week` | Numeric identifiers |
| `is_weekend`, `is_weekday` | Boolean flags (0/1) |
| `fiscal_year`, `fiscal_quarter` | April–March fiscal calendar |

#### `dim_machine.csv`
| Column | Description |
|--------|-------------|
| `machine_key` | Primary key |
| `machine_id` | Machine identifier |
| `machine_type` | Equipment type |
| `production_line` | Assigned line |
| `manufacturer` | OEM manufacturer |
| `install_year` | Year installed |
| `maintenance_interval_hrs` | Scheduled maintenance frequency |
| `status` | Current operational status |

#### `dim_product.csv`
| Column | Description |
|--------|-------------|
| `product_key` | Primary key |
| `product_id` | Product code |
| `product_name` | Full product name |
| `product_category` | Business segment |
| `target_cycle_time_sec` | Ideal cycle time |
| `unit_cost_usd` | Manufacturing cost per unit |

#### `dim_shift.csv`
| Column | Description |
|--------|-------------|
| `shift_key` | Primary key |
| `shift_id` | Shift identifier |
| `shift_name` | Morning / Afternoon / Night |
| `start_hour`, `end_hour` | Shift boundaries |
| `hours_range` | Display label |
| `is_day_shift` | Boolean (0/1) |

#### `dim_operator.csv`
| Column | Description |
|--------|-------------|
| `operator_key` | Primary key |
| `operator_id` | Employee ID |
| `operator_name` | Full name |
| `experience_level` | Senior / Mid / Junior |
| `is_certified` | Quality certification flag |
| `hire_year` | Year of hire |

---

## Star Schema Relationships

```
                    ┌──────────────┐
                    │  dim_date    │
                    │  (date_key)  │
                    └──────┬───────┘
                           │
┌──────────────┐  ┌────────┴────────┐  ┌──────────────┐
│ dim_machine  │──│ fact_production │──│  dim_product  │
│ (machine_key)│  │                 │  │ (product_key) │
└──────────────┘  └────────┬────────┘  └──────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────┴─────┐ ┌─────┴──────┐
              │ dim_shift  │ │dim_operator│
              │(shift_key) │ │(oper._key) │
              └────────────┘ └────────────┘
```
