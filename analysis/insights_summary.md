# 📊 Manufacturing Operations Analytics — Key Insights & Statistical Summary

## Executive Summary

This analysis covers **12 months** (Jan–Dec 2024) of manufacturing operations telemetry across **5 production lines**, **20 industrial machines**, **8 products**, **3 shifts**, and **10 operators**, totaling **145,728 hourly records**.

---

## 🏭 Production & Financial Overview

| Metric | Value | DAX Measure / Benchmark |
|--------|-------|-------------------------|
| **Total Units Produced** | **21,839,423** | `[Total Units]` |
| **Good Units (Passed QC)** | **21,027,873** | `[Good Units]` (First-Pass Yield: **96.28%**) |
| **Defective Units** | **811,550** | `[Defect Units]` |
| **Overall Scrap Rate** | **3.72%** | `[Scrap Rate]` (Cost of Poor Quality: **$120.2M**) |
| **Overall OEE (DAX / Row Mean)** | **82.54% / 82.60%** | `[OEE]` (World-Class Target: **≥ 85.0%**) |
| **Availability / Performance / Quality** | **94.37% / 90.84% / 96.28%** | `[Availability]` × `[Performance Rate]` × `[Quality Rate]` |
| **Total / Unplanned Downtime** | **8,198 hrs / 4,259 hrs** | `[Downtime Hours]` / `[Unplanned Downtime]` |
| **Fleet Reliability (MTBF)** | **33.0 hours** | `[MTBF Hours]` across **4,169** Equipment Failures |
| **Energy Consumed** | **1,362,755 kWh** | `[Total Energy kWh]` (`0.065 kWh` per good unit) |
| **Total Production Value** | **$3,107,610,212 ($3.11B)** | `[Production Value]` (`SUMX` × `RELATED(unit_cost_usd)`) |

---

## 📈 Key Finding #1: OEE Below World-Class Target (Speed & Quality Losses)

- **Overall OEE: 82.54% DAX / 82.60% Mean** (Target: ≥ 85.0%)
- **Availability (`94.37%`)** exceeds the 90% benchmark, proving machines are scheduled effectively.
- **Performance (`90.84%` vs 95% target)** and **Quality (`96.28%` vs 99% target)** are the primary drags on OEE.
- **Best Line:** `Line_B` (**85.39%** — World Class ✅) | **Bottleneck Line:** `Line_E` (**78.92%** — `-6.47%` OEE gap ⚠️).

## 📊 Key Finding #2: Downtime Pareto (80/20 Rule)

- Across **8,198 total downtime hours**, the top causes are **Planned Maintenance (`3,939.2h`)**, **Equipment Failure (`1,612.8h`)**, **Material Shortage (`612.1h`)**, and **Changeover/Setup (`606.6h`)**.
- Isolating **4,258.7 hours of Unplanned Downtime** (`[Unplanned Downtime]` DAX measure):
  - **Equipment Failure (37.9%)**, **Material Shortage (14.4%)**, **Changeover/Setup (14.2%)**, and **Power Outage (13.8%)** drive **80.3%** of all avoidable lost production time.

## 🔬 Key Finding #3: IoT Sensor Telemetry & Simpson's Paradox

- **Vibration–Scrap Correlation:** `r = +0.237` (`p < 0.0001` ✅). When vibration exceeds **8.0 mm/s**, average scrap rate surges from **3.50% to 6.36%** (+82% relative jump).
- **Temperature–Scrap Correlation (Simpson's Paradox Resolved):** Pooling raw temperature across different machine types yields `r = -0.029` because Injection Molders run at `180°C` while Quality Scanners run at `28°C`. Normalizing by machine baseline (`Δ°C = temperature_c - baseline_c`) reveals a highly significant positive correlation (`r = +0.049, p = 6.99e-78` ✅): when `ΔT > +10°C`, scrap jumps from **3.60% to 5.45%**.

## ⏰ Key Finding #4: Night Shift & Uncertified Operator Quality Gap

- **Shift One-Way ANOVA:** Morning (**87.36%**) vs. Afternoon (**85.28%**) vs. Night (**79.60%**) — `F = 3,433.49, p < 0.0001` (Statistically significant ✅).
- **Operator Certification Impact:** The 3 uncertified Junior operators (`OP-005`, `OP-006`, `OP-009`) average a **5.12% scrap rate** compared to **3.12%** across the 7 quality-certified Senior/Mid operators (+64% more defects).

## 🔧 Key Finding #5: Machine Reliability (MTBF) Varies Across Fleet

- **Least Reliable Asset:** `Assembly_Robot_E3` (**29.75 hrs MTBF**, 199 failures) and `Injection_Molder_C2` (**30.19 hrs MTBF**).
- **Most Reliable Asset:** `Assembly_Robot_B3` (**37.56 hrs MTBF**) and `CNC_Mill_A1` (**37.33 hrs MTBF**).

---

## 💡 Quantified Business Impact Summary

> Raising plant OEE from **82.6% to the 85.0% World-Class target** yields **+610,832 additional good units/year**, generating **+$90,272,099 ($90.27M) in incremental annual production value**. Certifying the 3 Junior operators and deploying `8 mm/s` vibration alerts recovers an additional **~$39.25M** in avoided scrap (COPQ).
