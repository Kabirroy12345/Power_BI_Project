# 🚀 Manufacturing OEE Dashboard: 2-Hour Interview Crash Course

*Read this to quickly understand exactly what you built, why it matters, and how to talk about it in the interview.*

---

## 1. The 30-Second Elevator Pitch (Memorize This)
"I built an end-to-end **Manufacturing Operations & OEE Analytics Dashboard**. Factory managers struggle to know exactly *why* they are losing money on the production line—is it machine downtime, slow cycle times, or high defect rates? 

I solved this by building a complete data pipeline: I wrote a Python ETL script to clean raw machine logs and structure them into a **Star Schema**, then imported that into **Power BI**. I wrote custom **DAX measures** to calculate OEE (Overall Equipment Effectiveness) in real-time, allowing managers to instantly identify equipment failures, track scrap rates, and optimize production across different shifts and product lines."

---

## 2. The Core Architecture (How it Works)
If they ask about the tech stack or how data flows:

1. **The Raw Data:** Simulated/raw manufacturing data logging hourly machine performance, cycle times, defects, and downtime reasons.
2. **The Python ETL Pipeline (`etl_pipeline.py`):** I used **Pandas** to clean the data (removing duplicates, clipping negative values, ensuring data integrity where good + defect = total units). 
3. **The Data Model (Star Schema):** The ETL script outputs clean CSVs structured into a Star Schema:
   - **1 Fact Table:** `fact_production` (contains the measurable metrics like actual run time, defect units, and pre-calculated availability/performance).
   - **5 Dimension Tables:** `dim_date`, `dim_machine`, `dim_product`, `dim_shift`, and `dim_operator`.
4. **The Power BI Layer (DAX):** I created a dedicated Measures table containing complex DAX formulas for Time Intelligence (Month-over-Month, YTD), OEE components, and Machine Reliability (MTBF - Mean Time Between Failures).
5. **The Visuals:** A dark-themed, industrial-style dashboard featuring KPI cards with conditional formatting (Green/Yellow/Red for OEE status), Pareto charts for downtime analysis, and trend lines.

---

## 3. Top 5 Interview Questions & How to Answer Them

### Q1: "What exactly is OEE and how did you calculate it?"
**Your Answer:** "OEE stands for Overall Equipment Effectiveness. It's the gold standard for measuring manufacturing productivity. It is calculated by multiplying three factors: **Availability** (uptime vs planned time), **Performance** (actual speed vs ideal speed), and **Quality** (good units vs total units). In my project, I computed these base metrics in the Python ETL for row-level accuracy, and then aggregated them using DAX in Power BI for dynamic filtering."

### Q2: "Why did you use a Star Schema instead of just loading a single flat table?"
**Your Answer:** "A flat table would be massive, redundant, and slow to query. By using a Star Schema, I normalized the descriptive attributes into Dimension tables (like Machines and Operators) and kept only the foreign keys and numeric metrics in the Fact table. This is the best practice for Power BI data modeling because it drastically reduces file size and makes DAX filter context work perfectly across relationships."

### Q3: "What was the most challenging DAX measure you wrote?"
**Your Answer:** "Handling Time Intelligence and Machine Reliability. For example, calculating **MTBF (Mean Time Between Failures)** required dividing the total actual run time (in hours) by the count of rows where the downtime reason specifically equaled 'Equipment Failure'. Also, creating the **OEE MoM % (Month-over-Month)** required using `CALCULATE` and `DATEADD` to safely compare the current context to the previous month without breaking if data was missing."

### Q4: "How did you handle dirty data in your Python ETL?"
**Your Answer:** "I built several data quality checks using Pandas. I dropped duplicate `record_id`s, clipped negative values to zero (since you can't have negative downtime or units), and enforced mathematical consistency (ensuring `good_units` exactly equaled `total_units_produced` minus `defect_units`). I also handled missing values by filling NaNs so Power BI wouldn't throw errors during import."

### Q5: "If a manager looks at your dashboard and sees a low OEE, what do they do next?"
**Your Answer:** "They follow the 'drill-down' path I designed. The main KPI card shows the low OEE. They look at the Gauge charts to see which of the 3 components is failing (Availability, Performance, or Quality). If Availability is low, they check the **Downtime Pareto chart** to see the top reasons (e.g., 'Equipment Failure'). If Quality is low, they can filter by the **Operator Dimension** or **Machine Dimension** to see if a specific person or machine is causing the defects."

---

## 4. Buzzwords to Drop Naturally
* **"Star Schema" & "Fact/Dimension Tables"**: Proves you understand proper data warehouse modeling, not just making pretty charts.
* **"Filter Context"**: Use this when talking about DAX. "I set up the relationships so the filter context flows down from the dimensions to the fact table."
* **"ETL (Extract, Transform, Load)"**: Emphasizes that you handle the data engineering part, not just the front-end design.
* **"Actionable Insights"**: Mention that the dashboard isn't just for looking at numbers; it's for finding root causes (like downtime reasons) to take action.

---

## 5. Your 5-Minute Pre-Interview Checklist
- [ ] Open Power BI Desktop with your `.pbix` file loaded and ready to present.
- [ ] Be ready to open `etl_pipeline.py` to show you can write actual Python code for data cleaning.
- [ ] Have this cheat sheet on a second monitor or split screen.
- [ ] Remember: You built a *Data Engineering Pipeline + Business Intelligence Solution*, not just a spreadsheet chart!
