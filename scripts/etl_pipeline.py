"""
ETL Pipeline — Transform Raw Data into Star Schema
====================================================
Reads the raw manufacturing CSV and outputs dimension + fact tables
optimized for Power BI data modeling.

Author: Kabir Roy
Project: Manufacturing Operations & OEE Analytics Dashboard
"""

import pandas as pd
import numpy as np
import os

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "manufacturing_data.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def load_raw_data():
    """Load and do initial cleaning of raw data."""
    print("📥 Loading raw data...")
    df = pd.read_csv(RAW_PATH, parse_dates=["timestamp"])
    print(f"   Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # --- Data Cleaning ---
    # 1. Remove any duplicate record_ids
    dupes = df.duplicated(subset=["record_id"]).sum()
    if dupes > 0:
        print(f"   ⚠️  Removed {dupes} duplicate records")
        df = df.drop_duplicates(subset=["record_id"])
    
    # 2. Handle negative values
    numeric_cols = ["planned_production_time_min", "actual_run_time_min", "downtime_min",
                    "total_units_produced", "good_units", "defect_units", "energy_kwh"]
    for col in numeric_cols:
        negatives = (df[col] < 0).sum()
        if negatives > 0:
            print(f"   ⚠️  Fixed {negatives} negative values in {col}")
            df[col] = df[col].clip(lower=0)
    
    # 3. Ensure good_units + defect_units = total_units
    df["defect_units"] = df["defect_units"].clip(upper=df["total_units_produced"])
    df["good_units"] = df["total_units_produced"] - df["defect_units"]
    
    # 4. Fill any NaN values
    df = df.fillna(0)
    
    print("   ✅ Data cleaning complete")
    return df


def create_dim_date(df):
    """Create the Date dimension table."""
    print("📅 Creating dim_date...")
    dates = pd.to_datetime(df["date"]).drop_duplicates().sort_values()
    
    dim_date = pd.DataFrame({
        "date_key": dates.dt.strftime("%Y%m%d").astype(int),
        "date": dates.dt.strftime("%Y-%m-%d"),
        "year": dates.dt.year,
        "quarter": dates.dt.quarter,
        "quarter_name": "Q" + dates.dt.quarter.astype(str),
        "month": dates.dt.month,
        "month_name": dates.dt.strftime("%B"),
        "month_short": dates.dt.strftime("%b"),
        "week_of_year": dates.dt.isocalendar().week.values,
        "day_of_month": dates.dt.day,
        "day_of_week": dates.dt.dayofweek,
        "day_name": dates.dt.strftime("%A"),
        "is_weekend": (dates.dt.dayofweek >= 5).astype(int),
        "is_weekday": (dates.dt.dayofweek < 5).astype(int),
        "fiscal_year": np.where(dates.dt.month >= 4, dates.dt.year, dates.dt.year - 1),
        "fiscal_quarter": np.where(dates.dt.month >= 4,
                                   ((dates.dt.month - 4) // 3) + 1,
                                   ((dates.dt.month + 8) // 3) + 1),
    })
    
    print(f"   ✅ {len(dim_date)} date records")
    return dim_date


def create_dim_machine(df):
    """Create the Machine dimension table."""
    print("🔧 Creating dim_machine...")
    
    machine_metadata = {
        "CNC_Mill": {"manufacturer": "DMG MORI", "install_year": 2020, "maintenance_interval_hrs": 500},
        "Injection_Molder": {"manufacturer": "ARBURG", "install_year": 2019, "maintenance_interval_hrs": 400},
        "Assembly_Robot": {"manufacturer": "FANUC", "install_year": 2021, "maintenance_interval_hrs": 1000},
        "Quality_Scanner": {"manufacturer": "Keyence", "install_year": 2022, "maintenance_interval_hrs": 2000},
        "Laser_Cutter": {"manufacturer": "TRUMPF", "install_year": 2021, "maintenance_interval_hrs": 600},
        "Welding_Robot": {"manufacturer": "ABB", "install_year": 2020, "maintenance_interval_hrs": 800},
        "Packaging_Unit": {"manufacturer": "Bosch Rexroth", "install_year": 2022, "maintenance_interval_hrs": 1500},
    }
    
    machines = df[["machine_id", "machine_type", "production_line"]].drop_duplicates()
    
    records = []
    for _, row in machines.iterrows():
        meta = machine_metadata.get(row["machine_type"], {})
        records.append({
            "machine_key": row["machine_id"],
            "machine_id": row["machine_id"],
            "machine_type": row["machine_type"].replace("_", " "),
            "production_line": row["production_line"],
            "manufacturer": meta.get("manufacturer", "Unknown"),
            "install_year": meta.get("install_year", 2020),
            "maintenance_interval_hrs": meta.get("maintenance_interval_hrs", 500),
            "status": "Active",
        })
    
    dim_machine = pd.DataFrame(records)
    print(f"   ✅ {len(dim_machine)} machines")
    return dim_machine


def create_dim_product(df):
    """Create the Product dimension table."""
    print("📦 Creating dim_product...")
    
    products = df[["product_id", "product_name", "product_category"]].drop_duplicates()
    
    target_cycles = {
        "PRD-001": 45, "PRD-002": 30, "PRD-003": 20, "PRD-004": 25,
        "PRD-005": 35, "PRD-006": 50, "PRD-007": 40, "PRD-008": 15,
    }
    
    unit_costs = {
        "PRD-001": 245.00, "PRD-002": 89.50, "PRD-003": 62.00, "PRD-004": 155.00,
        "PRD-005": 78.00, "PRD-006": 320.00, "PRD-007": 195.00, "PRD-008": 45.00,
    }
    
    dim_product = pd.DataFrame({
        "product_key": products["product_id"],
        "product_id": products["product_id"],
        "product_name": products["product_name"],
        "product_category": products["product_category"],
        "target_cycle_time_sec": products["product_id"].map(target_cycles),
        "unit_cost_usd": products["product_id"].map(unit_costs),
    })
    
    print(f"   ✅ {len(dim_product)} products")
    return dim_product


def create_dim_shift():
    """Create the Shift dimension table."""
    print("⏰ Creating dim_shift...")
    
    dim_shift = pd.DataFrame([
        {"shift_key": "SHIFT-1", "shift_id": "SHIFT-1", "shift_name": "Morning",
         "start_hour": 6, "end_hour": 14, "hours_range": "06:00-14:00", "is_day_shift": 1},
        {"shift_key": "SHIFT-2", "shift_id": "SHIFT-2", "shift_name": "Afternoon",
         "start_hour": 14, "end_hour": 22, "hours_range": "14:00-22:00", "is_day_shift": 1},
        {"shift_key": "SHIFT-3", "shift_id": "SHIFT-3", "shift_name": "Night",
         "start_hour": 22, "end_hour": 6, "hours_range": "22:00-06:00", "is_day_shift": 0},
    ])
    
    print(f"   ✅ {len(dim_shift)} shifts")
    return dim_shift


def create_dim_operator(df):
    """Create the Operator dimension table."""
    print("👷 Creating dim_operator...")
    
    operators = df[["operator_id", "operator_name", "operator_experience"]].drop_duplicates()
    
    certifications = {
        "OP-001": True, "OP-002": True, "OP-003": True, "OP-004": True,
        "OP-005": False, "OP-006": False, "OP-007": True, "OP-008": True,
        "OP-009": False, "OP-010": True,
    }
    
    hire_years = {
        "OP-001": 2018, "OP-002": 2017, "OP-003": 2020, "OP-004": 2019,
        "OP-005": 2023, "OP-006": 2023, "OP-007": 2016, "OP-008": 2020,
        "OP-009": 2024, "OP-010": 2019,
    }
    
    dim_operator = pd.DataFrame({
        "operator_key": operators["operator_id"],
        "operator_id": operators["operator_id"],
        "operator_name": operators["operator_name"],
        "experience_level": operators["operator_experience"],
        "is_certified": operators["operator_id"].map(certifications).astype(int),
        "hire_year": operators["operator_id"].map(hire_years),
    })
    
    print(f"   ✅ {len(dim_operator)} operators")
    return dim_operator


def create_fact_production(df):
    """Create the Fact Production table with computed OEE metrics."""
    print("📊 Creating fact_production...")
    
    fact = df.copy()
    
    # --- Compute OEE Components ---
    # Availability = Actual Run Time / Planned Production Time
    fact["availability"] = np.where(
        fact["planned_production_time_min"] > 0,
        fact["actual_run_time_min"] / fact["planned_production_time_min"],
        0
    )
    fact["availability"] = fact["availability"].clip(0, 1)
    
    # Performance = (Ideal Cycle Time × Total Units) / (Actual Run Time in seconds)
    actual_run_sec = fact["actual_run_time_min"] * 60
    fact["performance"] = np.where(
        actual_run_sec > 0,
        (fact["ideal_cycle_time_sec"] * fact["total_units_produced"]) / actual_run_sec,
        0
    )
    fact["performance"] = fact["performance"].clip(0, 1)
    
    # Quality = Good Units / Total Units
    fact["quality"] = np.where(
        fact["total_units_produced"] > 0,
        fact["good_units"] / fact["total_units_produced"],
        0
    )
    fact["quality"] = fact["quality"].clip(0, 1)
    
    # OEE = Availability × Performance × Quality
    fact["oee"] = fact["availability"] * fact["performance"] * fact["quality"]
    fact["oee"] = fact["oee"].clip(0, 1)
    
    # Scrap Rate
    fact["scrap_rate"] = np.where(
        fact["total_units_produced"] > 0,
        fact["defect_units"] / fact["total_units_produced"],
        0
    )
    
    # Energy per unit
    fact["energy_per_unit_kwh"] = np.where(
        fact["good_units"] > 0,
        fact["energy_kwh"] / fact["good_units"],
        0
    )
    
    # Date key for joining
    fact["date_key"] = pd.to_datetime(fact["date"]).dt.strftime("%Y%m%d").astype(int)
    
    # Select and rename columns for the fact table
    fact_production = fact[[
        "record_id", "date_key", "timestamp", "date", "hour",
        "machine_id", "product_id", "operator_id", "shift_id",
        "production_line",
        "planned_production_time_min", "actual_run_time_min", "downtime_min", "downtime_reason",
        "ideal_cycle_time_sec", "actual_cycle_time_sec",
        "total_units_produced", "good_units", "defect_units",
        "availability", "performance", "quality", "oee", "scrap_rate",
        "temperature_c", "vibration_mm_s", "energy_kwh", "energy_per_unit_kwh",
    ]].copy()
    
    # Round metrics
    for col in ["availability", "performance", "quality", "oee", "scrap_rate", "energy_per_unit_kwh"]:
        fact_production[col] = fact_production[col].round(4)
    
    print(f"   ✅ {len(fact_production):,} fact records")
    print(f"   📈 Average OEE: {fact_production['oee'].mean():.2%}")
    print(f"   📈 Average Availability: {fact_production['availability'].mean():.2%}")
    print(f"   📈 Average Performance: {fact_production['performance'].mean():.2%}")
    print(f"   📈 Average Quality: {fact_production['quality'].mean():.2%}")
    
    return fact_production


def run_etl():
    """Run the complete ETL pipeline."""
    print("=" * 60)
    print("🔄 ETL PIPELINE — Manufacturing Operations Data")
    print("=" * 60)
    
    # Load & clean
    df = load_raw_data()
    
    # Create dimensions
    dim_date = create_dim_date(df)
    dim_machine = create_dim_machine(df)
    dim_product = create_dim_product(df)
    dim_shift = create_dim_shift()
    dim_operator = create_dim_operator(df)
    
    # Create fact table
    fact_production = create_fact_production(df)
    
    # Save all tables
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    tables = {
        "dim_date.csv": dim_date,
        "dim_machine.csv": dim_machine,
        "dim_product.csv": dim_product,
        "dim_shift.csv": dim_shift,
        "dim_operator.csv": dim_operator,
        "fact_production.csv": fact_production,
    }
    
    print("\n💾 Saving processed tables...")
    for filename, table in tables.items():
        path = os.path.join(PROCESSED_DIR, filename)
        table.to_csv(path, index=False)
        print(f"   📁 {filename}: {len(table):,} rows × {len(table.columns)} cols")
    
    print("\n" + "=" * 60)
    print("✅ ETL PIPELINE COMPLETE")
    print(f"   Output directory: {PROCESSED_DIR}")
    print("=" * 60)
    
    return tables


if __name__ == "__main__":
    run_etl()
