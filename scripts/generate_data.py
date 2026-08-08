"""
Manufacturing Operations Data Generator
========================================
Generates realistic synthetic manufacturing/factory floor data for OEE analysis.
Simulates 5 production lines, 20 machines, 12 months of hourly records.

Author: Kabir Roy
Project: Manufacturing Operations & OEE Analytics Dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================================
# CONFIGURATION
# ============================================================

# Date range: 12 months
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31, 23, 0, 0)

# Machines (5 lines × 4 machines each = 20 machines)
PRODUCTION_LINES = {
    "Line_A": {"machines": ["CNC_Mill_A1", "Injection_Molder_A2", "Assembly_Robot_A3", "Quality_Scanner_A4"],
               "base_oee": 0.78},
    "Line_B": {"machines": ["CNC_Mill_B1", "Injection_Molder_B2", "Assembly_Robot_B3", "Quality_Scanner_B4"],
               "base_oee": 0.82},
    "Line_C": {"machines": ["CNC_Mill_C1", "Injection_Molder_C2", "Assembly_Robot_C3", "Quality_Scanner_C4"],
               "base_oee": 0.75},
    "Line_D": {"machines": ["CNC_Mill_D1", "Laser_Cutter_D2", "Welding_Robot_D3", "Quality_Scanner_D4"],
               "base_oee": 0.80},
    "Line_E": {"machines": ["CNC_Mill_E1", "Laser_Cutter_E2", "Assembly_Robot_E3", "Packaging_Unit_E4"],
               "base_oee": 0.73},
}

MACHINE_TYPES = {
    "CNC_Mill": {"ideal_cycle_time_sec": 45, "energy_base_kwh": 12.5, "temp_base_c": 65},
    "Injection_Molder": {"ideal_cycle_time_sec": 30, "energy_base_kwh": 18.0, "temp_base_c": 180},
    "Assembly_Robot": {"ideal_cycle_time_sec": 20, "energy_base_kwh": 5.0, "temp_base_c": 35},
    "Quality_Scanner": {"ideal_cycle_time_sec": 10, "energy_base_kwh": 2.5, "temp_base_c": 28},
    "Laser_Cutter": {"ideal_cycle_time_sec": 35, "energy_base_kwh": 15.0, "temp_base_c": 95},
    "Welding_Robot": {"ideal_cycle_time_sec": 40, "energy_base_kwh": 20.0, "temp_base_c": 120},
    "Packaging_Unit": {"ideal_cycle_time_sec": 15, "energy_base_kwh": 3.0, "temp_base_c": 25},
}

PRODUCTS = [
    {"id": "PRD-001", "name": "Turbo Actuator Valve", "category": "Aerospace", "target_cycle_sec": 45},
    {"id": "PRD-002", "name": "HVAC Control Module", "category": "Building Tech", "target_cycle_sec": 30},
    {"id": "PRD-003", "name": "Pressure Sensor Unit", "category": "Industrial", "target_cycle_sec": 20},
    {"id": "PRD-004", "name": "Gas Detection Sensor", "category": "Safety", "target_cycle_sec": 25},
    {"id": "PRD-005", "name": "Thermostat Controller", "category": "Building Tech", "target_cycle_sec": 35},
    {"id": "PRD-006", "name": "Fuel Nozzle Assembly", "category": "Aerospace", "target_cycle_sec": 50},
    {"id": "PRD-007", "name": "Industrial PLC Board", "category": "Industrial", "target_cycle_sec": 40},
    {"id": "PRD-008", "name": "Fire Alarm Module", "category": "Safety", "target_cycle_sec": 15},
]

OPERATORS = [
    {"id": "OP-001", "name": "Rajesh Kumar", "experience": "Senior", "certified": True},
    {"id": "OP-002", "name": "Priya Sharma", "experience": "Senior", "certified": True},
    {"id": "OP-003", "name": "Amit Patel", "experience": "Mid", "certified": True},
    {"id": "OP-004", "name": "Neha Gupta", "experience": "Mid", "certified": True},
    {"id": "OP-005", "name": "Vikram Singh", "experience": "Junior", "certified": False},
    {"id": "OP-006", "name": "Ananya Das", "experience": "Junior", "certified": False},
    {"id": "OP-007", "name": "Rahul Verma", "experience": "Senior", "certified": True},
    {"id": "OP-008", "name": "Sneha Reddy", "experience": "Mid", "certified": True},
    {"id": "OP-009", "name": "Arjun Nair", "experience": "Junior", "certified": False},
    {"id": "OP-010", "name": "Kavita Joshi", "experience": "Mid", "certified": True},
]

SHIFTS = [
    {"id": "SHIFT-1", "name": "Morning", "hours": "06:00-14:00"},
    {"id": "SHIFT-2", "name": "Afternoon", "hours": "14:00-22:00"},
    {"id": "SHIFT-3", "name": "Night", "hours": "22:00-06:00"},
]

DOWNTIME_REASONS = [
    ("Planned Maintenance", 0.25),
    ("Equipment Failure", 0.20),
    ("Material Shortage", 0.15),
    ("Changeover/Setup", 0.15),
    ("Quality Issue", 0.10),
    ("Operator Break", 0.05),
    ("Power Outage", 0.05),
    ("Calibration", 0.03),
    ("Software Error", 0.02),
]

# ============================================================
# DATA GENERATION
# ============================================================

def get_machine_type(machine_id):
    """Extract machine type from machine ID."""
    for mtype in MACHINE_TYPES:
        if mtype.replace("_", "").lower() in machine_id.replace("_", "").lower():
            return mtype
    return "Assembly_Robot"  # fallback

def get_shift(hour):
    """Determine shift from hour of day."""
    if 6 <= hour < 14:
        return SHIFTS[0]
    elif 14 <= hour < 22:
        return SHIFTS[1]
    else:
        return SHIFTS[2]

def generate_data():
    """Generate the complete manufacturing dataset."""
    print("🏭 Generating Manufacturing Operations Data...")
    print(f"   Date Range: {START_DATE.date()} to {END_DATE.date()}")
    
    records = []
    current = START_DATE
    record_id = 1
    
    while current <= END_DATE:
        hour = current.hour
        day_of_week = current.weekday()  # 0=Mon, 6=Sun
        month = current.month
        
        # Weekend: reduced operations (only Line_A and Line_B)
        is_weekend = day_of_week >= 5
        
        shift = get_shift(hour)
        
        # Seasonal demand factor (higher in Q2 and Q4)
        seasonal_factor = 1.0
        if month in [4, 5, 6]:
            seasonal_factor = 1.15
        elif month in [10, 11, 12]:
            seasonal_factor = 1.20
        elif month in [1, 2]:
            seasonal_factor = 0.85
        
        # Night shift performance penalty
        shift_factor = 1.0
        if shift["id"] == "SHIFT-3":
            shift_factor = 0.92
        elif shift["id"] == "SHIFT-1":
            shift_factor = 1.05
        
        for line_name, line_info in PRODUCTION_LINES.items():
            # Skip most lines on weekends
            if is_weekend and line_name not in ["Line_A", "Line_B"]:
                continue
            
            for machine_id in line_info["machines"]:
                mtype = get_machine_type(machine_id)
                mtype_info = MACHINE_TYPES[mtype]
                
                # Select product (weighted by category relevance)
                product = random.choice(PRODUCTS)
                
                # Select operator (shift-based assignment)
                operator = random.choice(OPERATORS)
                
                # --- PLANNED PRODUCTION TIME ---
                planned_time_min = 60  # 1 hour per record
                
                # --- DOWNTIME ---
                # Base downtime probability
                downtime_prob = 0.15  # 15% chance of downtime per hour
                if is_weekend:
                    downtime_prob = 0.10  # Less downtime on weekends (maintenance crews)
                
                has_downtime = np.random.random() < downtime_prob
                downtime_min = 0
                downtime_reason = "No Downtime"
                
                if has_downtime:
                    # Weighted random downtime reason
                    reasons, weights = zip(*DOWNTIME_REASONS)
                    downtime_reason = np.random.choice(reasons, p=weights)
                    
                    # Downtime duration varies by reason
                    if downtime_reason == "Planned Maintenance":
                        downtime_min = np.random.choice([30, 45, 60])
                    elif downtime_reason == "Equipment Failure":
                        downtime_min = np.random.exponential(25)
                    elif downtime_reason == "Power Outage":
                        downtime_min = np.random.choice([15, 30, 60])
                    else:
                        downtime_min = np.random.exponential(12)
                    
                    downtime_min = min(round(downtime_min, 1), 60)
                
                # --- ACTUAL RUN TIME ---
                actual_run_time = max(planned_time_min - downtime_min, 0)
                
                # --- PRODUCTION ---
                ideal_cycle_sec = mtype_info["ideal_cycle_time_sec"]
                
                # Max possible units in actual run time
                max_units = int((actual_run_time * 60) / ideal_cycle_sec) if actual_run_time > 0 else 0
                
                # Performance factor (speed losses)
                perf_factor = np.clip(
                    np.random.normal(0.90 * shift_factor * line_info["base_oee"] / 0.78, 0.05),
                    0.60, 1.0
                )
                
                total_units = max(int(max_units * perf_factor * seasonal_factor), 0)
                total_units = min(total_units, max_units)  # Can't exceed theoretical max
                
                # Actual cycle time (inverse of performance)
                actual_cycle_sec = round(ideal_cycle_sec / perf_factor, 2) if perf_factor > 0 else 0
                
                # --- QUALITY ---
                base_defect_rate = 0.03  # 3% base
                if operator["experience"] == "Junior":
                    base_defect_rate += 0.02
                if shift["id"] == "SHIFT-3":
                    base_defect_rate += 0.01
                
                defect_rate = np.clip(np.random.normal(base_defect_rate, 0.01), 0.005, 0.15)
                defect_units = max(int(total_units * defect_rate), 0)
                good_units = total_units - defect_units
                
                # --- SENSOR DATA ---
                temperature = round(np.random.normal(mtype_info["temp_base_c"], 5), 1)
                # Higher temperature correlates slightly with more defects
                if temperature > mtype_info["temp_base_c"] + 10:
                    defect_units += int(np.random.poisson(2))
                    good_units = max(total_units - defect_units, 0)
                
                vibration = round(np.random.exponential(2.5) + 0.5, 2)
                # Higher vibration = more issues
                if vibration > 8:
                    defect_units += int(np.random.poisson(3))
                    good_units = max(total_units - defect_units, 0)
                
                energy_kwh = round(
                    mtype_info["energy_base_kwh"] * (actual_run_time / 60) * np.random.normal(1.0, 0.05),
                    2
                )
                energy_kwh = max(energy_kwh, 0)
                
                # --- RECORD ---
                records.append({
                    "record_id": record_id,
                    "timestamp": current.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": current.strftime("%Y-%m-%d"),
                    "hour": hour,
                    "production_line": line_name,
                    "machine_id": machine_id,
                    "machine_type": mtype,
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "product_category": product["category"],
                    "operator_id": operator["id"],
                    "operator_name": operator["name"],
                    "operator_experience": operator["experience"],
                    "shift_id": shift["id"],
                    "shift_name": shift["name"],
                    "planned_production_time_min": planned_time_min,
                    "actual_run_time_min": round(actual_run_time, 1),
                    "downtime_min": round(downtime_min, 1),
                    "downtime_reason": downtime_reason,
                    "ideal_cycle_time_sec": ideal_cycle_sec,
                    "actual_cycle_time_sec": actual_cycle_sec,
                    "total_units_produced": total_units,
                    "good_units": good_units,
                    "defect_units": defect_units,
                    "temperature_c": temperature,
                    "vibration_mm_s": vibration,
                    "energy_kwh": energy_kwh,
                })
                record_id += 1
        
        current += timedelta(hours=1)
    
    df = pd.DataFrame(records)
    
    # Save raw data
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "manufacturing_data.csv")
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {len(df):,} records")
    print(f"📁 Saved to: {output_path}")
    print(f"\n📊 Data Summary:")
    print(f"   Date Range:    {df['date'].min()} to {df['date'].max()}")
    print(f"   Machines:      {df['machine_id'].nunique()}")
    print(f"   Products:      {df['product_id'].nunique()}")
    print(f"   Operators:     {df['operator_id'].nunique()}")
    print(f"   Total Units:   {df['total_units_produced'].sum():,.0f}")
    print(f"   Good Units:    {df['good_units'].sum():,.0f}")
    print(f"   Defect Units:  {df['defect_units'].sum():,.0f}")
    print(f"   Avg Downtime:  {df['downtime_min'].mean():.1f} min/hr")
    
    return df


if __name__ == "__main__":
    df = generate_data()
