# 🚀 Manufacturing OEE Dashboard: Complete Interview Playbook & Cheat Sheet

*Read this before your interview tomorrow. Every single number below matches your `data/processed/*.csv` Star Schema dataset, your `scripts/analytics.py` output, and your interactive Power BI Studio Dashboard (`dashboard/dashboard_preview.html`).*

---

## 1. The 30-Second Elevator Pitch (Memorize This)
> "I built an end-to-end **Manufacturing Operations & OEE Analytics Dashboard** covering **145,728 hourly machine logs** across **5 production lines** and **20 industrial machines** for full-year 2024. Factory managers struggle to know *why* they are losing money on the floor—is it unplanned breakdowns, slow cycle times, or quality defects?
>
> I solved this in two stages: First, I built a **Python Pandas ETL pipeline** (`etl_pipeline.py`) that cleans raw machine telemetry—deduplicating IDs, clipping negative values, enforcing `good_units + defect_units = total_units_produced`, and normalizing flat logs into a **Kimball Star Schema** (1 Fact table + 5 Dimension tables). Second, I modeled the Star Schema in **Power BI** with a dedicated `_Measures` table containing **26 custom DAX measures**—including `SUMX` + `RELATED` for weighted performance and `$3.11B` production value, `DATEADD` for Month-over-Month Time Intelligence, and `MTBF Hours` for machine reliability. Using the dashboard, I identified a **$90.27M annual revenue recovery opportunity** by bringing OEE from **82.5% to the 85% World-Class target**."

---

## 2. Exact Dataset Numbers to Know Cold (100% Consistent Across Code & Dashboard)

| Metric | Exact Value | Interview Context / Insight |
|--------|-------------|-----------------------------|
| **Total Hourly Records (`fact_production`)** | **145,728 rows** | 12 months (Jan–Dec 2024), 5 lines, 20 machines (Lines A & B run 24/7; C, D, E run weekdays) |
| **Overall OEE (`[OEE]` DAX / Row Mean)** | **82.54% DAX** (82.60% Mean) | Below 85.0% World-Class target (-2.46% gap) |
| **Availability (`[Availability]`)** | **94.37%** | **Exceeds** ≥ 90.0% target (137,530 run hrs / 145,728 planned hrs) |
| **Performance Rate (`[Performance Rate]`)** | **90.84% DAX** (89.20% Mean) | **Primary speed bottleneck** vs ≥ 95.0% target (-4.16% gap) |
| **Quality Rate (`[Quality Rate]`)** | **96.28% DAX** | **Quality gap** vs ≥ 99.0% target (First-Pass Yield) |
| **Total Units / Good Units / Defects** | **21,839,423** / **21,027,873** / **811,550** | **Scrap Rate = 3.72%** (`$120.2M` Cost of Poor Quality) |
| **Total Production Value (`[Production Value]`)** | **$3,107,610,212 ($3.11B)** | Calculated via `SUMX(fact_production, good_units * RELATED(dim_product[unit_cost_usd]))` |
| **Best vs. Worst Production Line** | **Line_B (85.4%)** vs **Line_E (78.9%)** | Line_B is World-Class; Line_E has a 6.5% OEE gap |
| **Total vs. Unplanned Downtime** | **8,198 hrs** Total / **4,259 hrs** Unplanned | Top causes: Planned Maint. (3,939h), **Equipment Failure (1,613h)**, **Material Shortage (612h)**, **Changeover (607h)** |
| **Fleet Reliability (`[MTBF Hours]`)** | **33.0 hrs** (4,169 Failures) | Worst: `Assembly_Robot_E3` (**29.8h MTBF**); Best: `Assembly_Robot_B3` (**37.6h MTBF**) |
| **Shift Performance (One-Way ANOVA)** | Morning **87.4%**, Afternoon **85.3%**, Night **79.6%** | **ANOVA F = 3,433.49, p < 0.0001** (Statistically significant Night Shift drop) |
| **Workforce Certification Gap (`dim_operator`)** | **3.12% Scrap** (Certified) vs **5.12% Scrap** (Uncertified) | The 3 uncertified Junior operators (`OP-005`, `OP-006`, `OP-009`) have a **+64% higher defect rate** |
| **IoT Sensor Correlations (Predictive Maint.)** | Vibration `r = +0.237` (`p < 0.0001`) | When Vibration **> 8 mm/s**, scrap jumps **3.50% → 6.36%**; when Temp Δ **> +10°C**, scrap jumps **3.60% → 5.45%** |

---

## 3. How to Demo the Dashboard Live in 3 Minutes (`dashboard/dashboard_preview.html`)

1. **Open `dashboard/dashboard_preview.html` in Chrome/Edge** (Click `⛶ Fullscreen` in the top-right corner).
2. **Start on Page 1 (Executive OEE Overview)**:
   - Point out the **6 KPI Cards** and **3 Radial Gauges**: show how Availability (`94.4%`) beats target, while Performance (`90.8%`) and Quality (`96.3%`) pull Overall OEE down to `82.5%`.
   - Click **`Unplanned Only`** on the **Downtime Pareto Chart** to show how your DAX `[Unplanned Downtime]` measure strips out Planned Maintenance (`3,939h`) to expose **Equipment Failure (`1,613h`)** and **Material Shortage (`612h`)**.
   - Click **`Line_E`** directly in the **Production Line Matrix** to cross-filter the entire dashboard in real time!
3. **Click Page 2 Tab (Downtime & MTBF Reliability)**:
   - Show the **20-Machine MTBF Ranking** with the `33.0h` fleet median line, highlighting `Assembly_Robot_E3` (`29.8h`) and the Line × Reason Downtime Heatmap.
4. **Click Page 3 Tab (Quality & IoT Sensor Predictive Maintenance)**:
   - Show the **Vibration vs. Scrap Scatter Plot** (`> 8 mm/s` alert threshold) and toggle **Normalized Δ°C vs. Raw Temp °C** to explain how you solved **Simpson's Paradox** across heterogeneous machine classes (Injection Molders at 180°C vs Quality Scanners at 28°C).
5. **Click Page 4 Tab (Shift ANOVA, Workforce & Energy)**:
   - Point to the **Shift ANOVA chart** (`F = 3,433.49, p < 0.0001`) and the **Operator Scorecard** showing that the 3 uncertified Junior operators (`OP-005`, `OP-006`, `OP-009`) average `5.12%` scrap vs `3.12%` for Certified operators.
6. **Click the Left Rail Icons (`🔗 Model`, `🗃️ Data`, `📐 DAX / ETL`)**:
   - Show the **Kimball Star Schema diagram** (`🔗 Model`) with `1 ───► *` single-direction filter propagation.
   - Show the **26 Live DAX Measures** (`📐 DAX / ETL`) recalculating live as you change slicers!

---

## 4. Top 6 Interview Questions & Winning Answers

### Q1: "What is OEE and why did you compute it both in Python ETL and in DAX?"
**Answer:** "OEE is `Availability × Performance × Quality`. I pre-computed row-level OEE in `etl_pipeline.py` so data scientists can run row-level statistical tests (like One-Way ANOVA across shifts in `analytics.py`), and I wrote dynamic **DAX measures** in Power BI using ratio-of-sums (`DIVIDE(SUM(...), SUM(...))` and `SUMX`) because in BI reporting you cannot simply average percentages across unequal production volumes. In my dashboard, you can even toggle between `DAX Aggregate (82.54%)` and `Row-Level Mean (82.60%)`."

### Q2: "Why did you design a Kimball Star Schema instead of loading the raw CSV directly?"
**Answer:** "Loading a flat denormalized table duplicates text strings (machine manufacturers, product names, operator names) across 145,728 rows, bloating VertiPaq dictionary size and causing ambiguous auto-exist filtering in DAX. By normalizing into `fact_production` (numeric measures + foreign keys) and 5 dimensions (`dim_date`, `dim_machine`, `dim_product`, `dim_shift`, `dim_operator`) joined via `Many-to-One (*:1)` single-direction relationships, filter context propagates cleanly from dimensions to the fact table."

### Q3: "What was the most complex DAX measure you wrote?"
**Answer:** "Three stand out:
1. **`[Performance Rate]` & `[Production Value]`**: Required row-context iteration via `SUMX` combined with `RELATED(dim_product[unit_cost_usd])` to weight each hourly run by its product's specific cycle time and unit cost across the relationship.
2. **`[Unplanned Downtime]`**: Used `CALCULATE` with `NOT(fact_production[downtime_reason] IN {"Planned Maintenance", "No Downtime"})` to separate actionable breakdowns (`4,259 hrs`) from scheduled maintenance (`3,939 hrs`).
3. **`[OEE MoM Change]`**: Used `VAR` variables, `CALCULATE([OEE], DATEADD(dim_date[date], -1, MONTH))`, and `IF(NOT(ISBLANK(_Previous)), ...)` to prevent blank-month edge cases."

### Q4: "How did you handle data quality issues in your Python ETL?"
**Answer:** "In `scripts/etl_pipeline.py`, I implemented 4 automated quality gates:
1. Deduplicated primary keys (`drop_duplicates(subset=['record_id'])`).
2. Clipped physical impossibilities (`clip(lower=0)` on run time, downtime, units, and energy).
3. Enforced accounting identity (`defect_units = defect_units.clip(upper=total_units)` and `good_units = total_units - defect_units`).
4. Standardized surrogate `date_key` integers (`YYYYMMDD`) for fast integer-join relationships in Power BI."

### Q5: "Did you find any interesting statistical nuance in the IoT sensor data?"
**Answer:** "Yes—**Simpson's Paradox** in temperature telemetry! When pooling raw `temperature_c` across all 20 machines, correlation with scrap looks slightly negative (`r = -0.029`) because Injection Molders naturally operate at `180°C` while Quality Scanners run at `28°C`. When I normalized temperature against each machine type's baseline (`Δ°C = temperature_c - temp_baseline_c`), the true positive correlation emerged (`r = +0.049, p < 10⁻⁷⁷`), proving that overheating `> +10°C` above baseline spikes scrap from `3.60%` to `5.45%`."

### Q6: "If a plant manager looks at your dashboard and sees 82.5% OEE, what concrete actions do you recommend?"
**Answer:** "Four quantified actions from Page 5 of my dashboard:
1. **Prioritize Line_E (`78.9% OEE`) & `Assembly_Robot_E3` (`29.8h MTBF`)** for preventive maintenance overhaul.
2. **Deploy real-time IoT alerts** when vibration exceeds `8.0 mm/s` (where scrap jumps from `3.50%` to `6.36%`) or temperature exceeds `+10°C` above baseline.
3. **Certify the 3 Junior Operators (`OP-005`, `OP-006`, `OP-009`)**, whose scrap rate is `5.12%` vs `3.12%` for certified staff.
4. **Add Night Shift supervision/tooling support** (`79.6%` OEE vs `87.4%` Morning).
Closing the 2.46% OEE gap to 85% yields **+610,832 good units** and **+$90.27M in annual production value**."
