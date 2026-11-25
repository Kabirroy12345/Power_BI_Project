# Manufacturing OEE Dashboard — Key Insights Summary

## 1. Headline KPIs (2024 Full-Year — 145,728 Hourly Records)

| Metric | DAX Result | Target / Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Overall OEE** | **`82.5%`** | `85.0%` (World Class) | `-2.5%` gap to target |
| **Availability Rate** | **`94.4%`** | `90.0%` | Exceeds target (`+4.4%`) |
| **Performance Rate** | **`90.8%`** | `95.0%` | Primary OEE bottleneck (`-4.2%`) |
| **Quality Rate** | **`96.3%`** | `99.0%` | Solid first-pass yield |
| **Total Units Produced** | **`21,839,423`** | — | Across 8 products & 20 machines |
| **Good Units (First Pass)** | **`21,027,873`** | — | `96.28%` yield |
| **Defect / Scrap Units** | **`811,550`** | — | **`3.72%` Scrap Rate** |
| **Total Downtime** | **`8,197.9 hrs`** | — | **`5.63%`** of Planned Time |
| **Unplanned Downtime** | **`4,258.7 hrs`** | — | `51.9%` of total downtime (`3,939.2 hrs` is Planned Maintenance) |

---

## 2. Production Line Breakdown

| Production Line | OEE | Availability | Performance Rate | Quality Rate | Unplanned Downtime (Hrs) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Line_B` (Best)** | **`85.3%`** | `94.6%` | `93.7%` | `96.3%` | `1,017.0 hrs` (24/7 schedule) |
| **`Line_D`** | **`83.8%`** | `94.4%` | `92.2%` | `96.3%` | `744.4 hrs` |
| **`Line_A`** | **`83.1%`** | `94.2%` | `91.6%` | `96.3%` | `959.2 hrs` (24/7 schedule) |
| **`Line_C`** | **`80.3%`** | `94.3%` | `88.4%` | `96.3%` | `780.3 hrs` |
| **`Line_E` (Lowest)** | **`78.9%`** | `94.3%` | `86.8%` | `96.3%` | `757.8 hrs` |

- **Takeaway:** `Line_B` already operates above the `85.0%` World-Class benchmark (`85.3%`). `Line_E` (`78.9%`) and `Line_C` (`80.3%`) lag primarily due to slower running speed (**Performance Rate** of `86.8%` and `88.4%`).

---

## 3. Shift Comparison

| Shift | Hours | OEE | Availability | Performance Rate | Quality Rate | Scrap Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Morning (`SHIFT-1`)** | `06:00–14:00` | **`85.7%`** | `94.5%` | `93.9%` | `96.6%` | **`3.40%`** |
| **Afternoon (`SHIFT-2`)** | `14:00–22:00` | **`83.8%`** | `94.3%` | `92.0%` | `96.6%` | **`3.42%`** |
| **Night (`SHIFT-3`)** | `22:00–06:00` | **`78.1%`** | `94.3%` | `86.6%` | `95.6%` | **`4.44%`** |

- **Takeaway:** The **Night Shift** drops to **`78.1%` OEE** (a `7.6` percentage point drop below Morning) and sees scrap rise to **`4.44%`** (vs. `~3.4%` during daytime shifts).

---

## 4. Unplanned Downtime Root Causes (`4,258.7 Hours`)

| Rank | Unplanned Downtime Reason | Hours Lost | Share of Unplanned Downtime | Cumulative Share |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Equipment Failure** | **`1,612.8 hrs`** | `37.9%` | `37.9%` |
| **2** | **Material Shortage** | **`612.1 hrs`** | `14.4%` | `52.2%` |
| **3** | **Changeover/Setup** | **`606.6 hrs`** | `14.2%` | `66.5%` |
| **4** | **Power Outage** | **`588.8 hrs`** | `13.8%` | `80.3%` |
| **5** | **Quality Issue** | **`415.5 hrs`** | `9.8%` | `90.1%` |
| **6** | **Operator Break** | **`201.5 hrs`** | `4.7%` | `94.8%` |
| **7** | **Calibration** | **`143.0 hrs`** | `3.4%` | `98.2%` |
| **8** | **Software Error** | **`78.3 hrs`** | `1.8%` | `100.0%` |

---

## 5. Actionable Recommendations

1. **Speed Optimization on `Line_E` & `Line_C`:** Investigate minor stops and cycle slowdowns on `Line_E` (`Laser_Cutter_E2` at `78.3%` OEE) and `Line_C` using `Line_B` operating settings as a benchmark.
2. **Night Shift Support & Handover Checks:** Add maintenance/supervisory support during the `22:00–06:00` Night Shift to close the speed (`86.6%`) and scrap (`4.44%`) gap.
3. **Preventive Maintenance for Equipment Failures:** Target the `#1` unplanned downtime driver (`Equipment Failure`, `1,612.8 hrs`, `37.9%` of unplanned stops) with scheduled preventive inspections before peak summer/autumn runs.
4. **Line-Side Material Buffer Planning:** Address `Material Shortage` (`612.1 hrs`) and standardize `Changeover/Setup` (`606.6 hrs`) procedures across shifts.
