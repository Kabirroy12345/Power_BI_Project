"""
Manufacturing Analytics — Statistical Analysis & Insights
==========================================================
Performs advanced analytics on the processed manufacturing data:
- OEE trend analysis
- Pareto analysis (downtime causes)
- Correlation analysis (sensor data vs. defects)
- Shift performance comparison (ANOVA)
- Machine reliability (MTBF)

Author: Kabir Roy
Project: Manufacturing Operations & OEE Analytics Dashboard
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")
CHARTS_DIR = os.path.join(BASE_DIR, "dashboard", "screenshots")

# ============================================================
# STYLE CONFIG
# ============================================================
# Honeywell-inspired color palette
COLORS = {
    "primary": "#E4002B",     # Honeywell Red
    "secondary": "#1B365D",   # Dark Navy
    "accent": "#00A3E0",      # Bright Blue
    "success": "#00B140",     # Green
    "warning": "#FFC72C",     # Yellow/Amber
    "dark": "#1a1a2e",        # Dashboard dark bg
    "text": "#FFFFFF",
    "grid": "#333355",
}

PALETTE = ["#E4002B", "#00A3E0", "#00B140", "#FFC72C", "#9B59B6", "#E67E22", "#1ABC9C", "#34495E"]

plt.rcParams.update({
    'figure.facecolor': COLORS["dark"],
    'axes.facecolor': '#16213e',
    'axes.edgecolor': COLORS["grid"],
    'axes.labelcolor': COLORS["text"],
    'text.color': COLORS["text"],
    'xtick.color': COLORS["text"],
    'ytick.color': COLORS["text"],
    'grid.color': COLORS["grid"],
    'grid.alpha': 0.3,
    'font.family': 'sans-serif',
    'font.size': 11,
    'figure.dpi': 150,
})


def load_data():
    """Load processed fact and dimension tables."""
    print("📥 Loading processed data...")
    fact = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_production.csv"), parse_dates=["timestamp"])
    dim_machine = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_machine.csv"))
    dim_product = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_product.csv"))
    
    # Merge for enriched analysis
    df = fact.merge(dim_machine[["machine_key", "machine_type", "manufacturer"]],
                    left_on="machine_id", right_on="machine_key", how="left", suffixes=("", "_dim"))
    df = df.merge(dim_product[["product_key", "product_name", "product_category", "unit_cost_usd"]],
                  left_on="product_id", right_on="product_key", how="left", suffixes=("", "_dim"))
    
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    df["month_label"] = pd.to_datetime(df["date"]).dt.strftime("%b %Y")
    df["week"] = pd.to_datetime(df["date"]).dt.isocalendar().week
    
    print(f"   ✅ Loaded {len(df):,} records")
    return df


def analyze_oee_trends(df):
    """Monthly OEE trend analysis by production line."""
    print("\n📈 Analyzing OEE Trends...")
    
    monthly = df.groupby(["month", "production_line"]).agg(
        avg_oee=("oee", "mean"),
        avg_availability=("availability", "mean"),
        avg_performance=("performance", "mean"),
        avg_quality=("quality", "mean"),
        total_units=("total_units_produced", "sum"),
        total_good=("good_units", "sum"),
    ).reset_index()
    
    monthly["month_str"] = monthly["month"].astype(str)
    
    # --- Chart 1: OEE Trend by Line ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("OEE Components — Monthly Trend by Production Line", fontsize=16, fontweight="bold", y=0.98)
    
    metrics = [
        ("avg_oee", "Overall OEE", "OEE %"),
        ("avg_availability", "Availability", "Availability %"),
        ("avg_performance", "Performance", "Performance %"),
        ("avg_quality", "Quality", "Quality %"),
    ]
    
    targets = [0.85, 0.90, 0.95, 0.99]
    
    for idx, (col, title, ylabel) in enumerate(metrics):
        ax = axes[idx // 2][idx % 2]
        
        for i, line in enumerate(sorted(monthly["production_line"].unique())):
            line_data = monthly[monthly["production_line"] == line]
            ax.plot(line_data["month_str"], line_data[col] * 100,
                    marker="o", markersize=4, linewidth=2,
                    color=PALETTE[i], label=line, alpha=0.9)
        
        # Target line
        ax.axhline(y=targets[idx] * 100, color=COLORS["warning"], linestyle="--",
                   linewidth=1.5, alpha=0.7, label=f"Target ({targets[idx]:.0%})")
        
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8, loc="lower right")
        ax.grid(True, alpha=0.2)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "oee_trends.png"), bbox_inches="tight", dpi=150)
    plt.close()
    
    # Summary stats
    overall_oee = df["oee"].mean()
    best_line = df.groupby("production_line")["oee"].mean().idxmax()
    worst_line = df.groupby("production_line")["oee"].mean().idxmin()
    
    print(f"   Overall Average OEE: {overall_oee:.2%}")
    print(f"   Best Performing Line: {best_line} ({df[df['production_line']==best_line]['oee'].mean():.2%})")
    print(f"   Worst Performing Line: {worst_line} ({df[df['production_line']==worst_line]['oee'].mean():.2%})")
    
    return {
        "overall_oee": overall_oee,
        "best_line": best_line,
        "worst_line": worst_line,
    }


def analyze_downtime_pareto(df):
    """Pareto analysis of downtime causes."""
    print("\n📊 Performing Downtime Pareto Analysis...")
    
    downtime_df = df[df["downtime_min"] > 0].copy()
    
    pareto = downtime_df.groupby("downtime_reason").agg(
        total_downtime_hrs=("downtime_min", lambda x: x.sum() / 60),
        incident_count=("downtime_min", "count"),
        avg_duration_min=("downtime_min", "mean"),
    ).sort_values("total_downtime_hrs", ascending=False).reset_index()
    
    pareto["cumulative_pct"] = (pareto["total_downtime_hrs"].cumsum() / pareto["total_downtime_hrs"].sum()) * 100
    pareto["pct_of_total"] = (pareto["total_downtime_hrs"] / pareto["total_downtime_hrs"].sum()) * 100
    
    # --- Chart: Pareto ---
    fig, ax1 = plt.subplots(figsize=(14, 7))
    fig.suptitle("Downtime Pareto Analysis — Top Causes of Lost Production Time",
                 fontsize=15, fontweight="bold", y=0.98)
    
    bars = ax1.bar(range(len(pareto)), pareto["total_downtime_hrs"],
                   color=PALETTE[:len(pareto)], alpha=0.85, edgecolor="white", linewidth=0.5)
    
    ax1.set_xlabel("Downtime Reason", fontsize=12)
    ax1.set_ylabel("Total Downtime (Hours)", fontsize=12, color=COLORS["accent"])
    ax1.set_xticks(range(len(pareto)))
    ax1.set_xticklabels(pareto["downtime_reason"], rotation=35, ha="right", fontsize=9)
    
    # Cumulative line
    ax2 = ax1.twinx()
    ax2.plot(range(len(pareto)), pareto["cumulative_pct"],
             color=COLORS["warning"], marker="D", markersize=6, linewidth=2.5, label="Cumulative %")
    ax2.axhline(y=80, color=COLORS["primary"], linestyle="--", linewidth=1.5, alpha=0.7, label="80% Threshold")
    ax2.set_ylabel("Cumulative %", fontsize=12, color=COLORS["warning"])
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.legend(loc="center right", fontsize=9)
    
    # Add value labels on bars
    for bar, val in zip(bars, pareto["total_downtime_hrs"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                 f"{val:,.0f}h", ha="center", va="bottom", fontsize=8, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "downtime_pareto.png"), bbox_inches="tight", dpi=150)
    plt.close()
    
    # Find the 80% threshold
    causes_80 = pareto[pareto["cumulative_pct"] <= 80]["downtime_reason"].tolist()
    if len(causes_80) == 0:
        causes_80 = [pareto.iloc[0]["downtime_reason"]]
    
    print(f"   Top causes (80% of downtime): {', '.join(causes_80)}")
    print(f"   Total downtime hours: {pareto['total_downtime_hrs'].sum():,.0f}")
    
    return {"pareto": pareto, "top_causes_80": causes_80}


def analyze_correlations(df):
    """Correlation analysis: sensor readings vs. defect rate."""
    print("\n🔬 Analyzing Sensor Correlations...")
    
    analysis_df = df[df["total_units_produced"] > 0].copy()
    
    # Temperature vs Scrap Rate
    temp_corr, temp_p = stats.pearsonr(analysis_df["temperature_c"], analysis_df["scrap_rate"])
    
    # Vibration vs Scrap Rate
    vib_corr, vib_p = stats.pearsonr(analysis_df["vibration_mm_s"], analysis_df["scrap_rate"])
    
    # --- Chart: Scatter plots ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Sensor Data Correlation with Defect Rate — Predictive Maintenance Potential",
                 fontsize=14, fontweight="bold", y=1.02)
    
    # Temperature scatter
    sample = analysis_df.sample(n=min(3000, len(analysis_df)), random_state=42)
    ax1.scatter(sample["temperature_c"], sample["scrap_rate"] * 100,
                alpha=0.3, s=8, color=COLORS["primary"], edgecolor="none")
    
    # Trend line
    z = np.polyfit(sample["temperature_c"], sample["scrap_rate"] * 100, 1)
    p = np.poly1d(z)
    x_line = np.linspace(sample["temperature_c"].min(), sample["temperature_c"].max(), 100)
    ax1.plot(x_line, p(x_line), color=COLORS["warning"], linewidth=2.5, linestyle="--")
    
    ax1.set_xlabel("Temperature (°C)")
    ax1.set_ylabel("Scrap Rate (%)")
    ax1.set_title(f"Temperature vs. Scrap Rate\nr = {temp_corr:.3f} (p = {temp_p:.2e})", fontsize=12)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.grid(True, alpha=0.2)
    
    # Vibration scatter
    ax2.scatter(sample["vibration_mm_s"], sample["scrap_rate"] * 100,
                alpha=0.3, s=8, color=COLORS["accent"], edgecolor="none")
    
    z2 = np.polyfit(sample["vibration_mm_s"], sample["scrap_rate"] * 100, 1)
    p2 = np.poly1d(z2)
    x_line2 = np.linspace(sample["vibration_mm_s"].min(), min(sample["vibration_mm_s"].max(), 20), 100)
    ax2.plot(x_line2, p2(x_line2), color=COLORS["warning"], linewidth=2.5, linestyle="--")
    
    ax2.set_xlabel("Vibration (mm/s)")
    ax2.set_ylabel("Scrap Rate (%)")
    ax2.set_title(f"Vibration vs. Scrap Rate\nr = {vib_corr:.3f} (p = {vib_p:.2e})", fontsize=12)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "sensor_correlation.png"), bbox_inches="tight", dpi=150)
    plt.close()
    
    print(f"   Temperature-Scrap Correlation: r={temp_corr:.3f} (p={temp_p:.2e})")
    print(f"   Vibration-Scrap Correlation: r={vib_corr:.3f} (p={vib_p:.2e})")
    
    return {
        "temp_corr": temp_corr, "temp_p": temp_p,
        "vib_corr": vib_corr, "vib_p": vib_p,
    }


def analyze_shift_performance(df):
    """ANOVA test comparing shift performance."""
    print("\n⏰ Analyzing Shift Performance...")
    
    shift_data = df[df["total_units_produced"] > 0]
    
    morning = shift_data[shift_data["shift_id"] == "SHIFT-1"]["oee"]
    afternoon = shift_data[shift_data["shift_id"] == "SHIFT-2"]["oee"]
    night = shift_data[shift_data["shift_id"] == "SHIFT-3"]["oee"]
    
    # One-way ANOVA
    f_stat, p_value = stats.f_oneway(morning, afternoon, night)
    
    # --- Chart: Box plot ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Shift Performance Comparison — Statistical Analysis",
                 fontsize=14, fontweight="bold", y=1.02)
    
    shift_labels = ["Morning\n(06:00-14:00)", "Afternoon\n(14:00-22:00)", "Night\n(22:00-06:00)"]
    data_groups = [morning * 100, afternoon * 100, night * 100]
    
    bp = ax1.boxplot(data_groups, labels=shift_labels, patch_artist=True,
                     medianprops=dict(color=COLORS["warning"], linewidth=2),
                     whiskerprops=dict(color=COLORS["text"]),
                     capprops=dict(color=COLORS["text"]),
                     flierprops=dict(markerfacecolor=COLORS["primary"], markersize=3, alpha=0.3))
    
    box_colors = [COLORS["accent"], COLORS["success"], COLORS["primary"]]
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_ylabel("OEE (%)")
    ax1.set_title("OEE Distribution by Shift", fontsize=12)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.grid(True, alpha=0.2, axis="y")
    
    # Add ANOVA result annotation
    sig_text = f"ANOVA F={f_stat:.2f}, p={p_value:.2e}\n"
    sig_text += "✅ Significant difference" if p_value < 0.05 else "❌ No significant difference"
    ax1.text(0.02, 0.02, sig_text, transform=ax1.transAxes, fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["dark"], edgecolor=COLORS["grid"]))
    
    # Bar chart of means
    means = [morning.mean() * 100, afternoon.mean() * 100, night.mean() * 100]
    bars = ax2.bar(shift_labels, means, color=box_colors, alpha=0.8, edgecolor="white", linewidth=0.5)
    
    for bar, val in zip(bars, means):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 f"{val:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
    
    ax2.set_ylabel("Average OEE (%)")
    ax2.set_title("Average OEE by Shift", fontsize=12)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.grid(True, alpha=0.2, axis="y")
    ax2.axhline(y=85, color=COLORS["warning"], linestyle="--", linewidth=1.5, alpha=0.6, label="World-Class (85%)")
    ax2.legend(fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "shift_performance.png"), bbox_inches="tight", dpi=150)
    plt.close()
    
    print(f"   Morning Avg OEE: {morning.mean():.2%}")
    print(f"   Afternoon Avg OEE: {afternoon.mean():.2%}")
    print(f"   Night Avg OEE: {night.mean():.2%}")
    print(f"   ANOVA F-statistic: {f_stat:.2f}, p-value: {p_value:.2e}")
    print(f"   Significant difference: {'Yes' if p_value < 0.05 else 'No'}")
    
    return {
        "morning_oee": morning.mean(),
        "afternoon_oee": afternoon.mean(),
        "night_oee": night.mean(),
        "f_stat": f_stat,
        "p_value": p_value,
    }


def analyze_machine_reliability(df):
    """Machine reliability analysis — MTBF."""
    print("\n🔧 Analyzing Machine Reliability (MTBF)...")
    
    failures = df[df["downtime_reason"] == "Equipment Failure"].copy()
    
    # Count failures per machine
    failure_counts = failures.groupby("machine_id").size().reset_index(name="failure_count")
    
    # Total operating hours per machine
    operating = df.groupby("machine_id").agg(
        total_run_hrs=("actual_run_time_min", lambda x: x.sum() / 60),
        total_records=("record_id", "count"),
    ).reset_index()
    
    reliability = operating.merge(failure_counts, on="machine_id", how="left")
    reliability["failure_count"] = reliability["failure_count"].fillna(0).astype(int)
    reliability["mtbf_hrs"] = np.where(
        reliability["failure_count"] > 0,
        reliability["total_run_hrs"] / reliability["failure_count"],
        reliability["total_run_hrs"]  # No failures = MTBF is total run time
    )
    
    reliability = reliability.sort_values("mtbf_hrs", ascending=True)
    
    # --- Chart: MTBF ---
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.suptitle("Machine Reliability — Mean Time Between Failures (MTBF)",
                 fontsize=15, fontweight="bold", y=0.98)
    
    colors = [COLORS["primary"] if mtbf < reliability["mtbf_hrs"].median() else COLORS["success"]
              for mtbf in reliability["mtbf_hrs"]]
    
    bars = ax.barh(range(len(reliability)), reliability["mtbf_hrs"],
                   color=colors, alpha=0.85, edgecolor="white", linewidth=0.5)
    
    ax.set_yticks(range(len(reliability)))
    ax.set_yticklabels(reliability["machine_id"], fontsize=9)
    ax.set_xlabel("MTBF (Hours)", fontsize=12)
    
    # Add value labels
    for bar, val, fc in zip(bars, reliability["mtbf_hrs"], reliability["failure_count"]):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f} hrs ({fc} failures)", va="center", fontsize=8)
    
    # Median line
    median_mtbf = reliability["mtbf_hrs"].median()
    ax.axvline(x=median_mtbf, color=COLORS["warning"], linestyle="--", linewidth=2,
               label=f"Median: {median_mtbf:,.0f} hrs")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2, axis="x")
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "machine_reliability.png"), bbox_inches="tight", dpi=150)
    plt.close()
    
    least_reliable = reliability.iloc[0]["machine_id"]
    most_reliable = reliability.iloc[-1]["machine_id"]
    
    print(f"   Least Reliable: {least_reliable} (MTBF: {reliability.iloc[0]['mtbf_hrs']:,.0f} hrs)")
    print(f"   Most Reliable: {most_reliable} (MTBF: {reliability.iloc[-1]['mtbf_hrs']:,.0f} hrs)")
    
    return {
        "reliability": reliability,
        "least_reliable": least_reliable,
        "most_reliable": most_reliable,
    }


def generate_executive_summary(df, oee_results, pareto_results, corr_results, shift_results, mtbf_results):
    """Generate the insights summary markdown."""
    print("\n📝 Generating Executive Summary...")
    
    total_units = df["total_units_produced"].sum()
    total_good = df["good_units"].sum()
    total_defects = df["defect_units"].sum()
    total_downtime_hrs = df["downtime_min"].sum() / 60
    total_energy = df["energy_kwh"].sum()
    
    # Production value estimate
    df_with_cost = df.copy()
    unit_costs = {"PRD-001": 245, "PRD-002": 89.5, "PRD-003": 62, "PRD-004": 155,
                  "PRD-005": 78, "PRD-006": 320, "PRD-007": 195, "PRD-008": 45}
    df_with_cost["revenue"] = df_with_cost["good_units"] * df_with_cost["product_id"].map(unit_costs).fillna(100)
    total_revenue = df_with_cost["revenue"].sum()
    
    summary = f"""# 📊 Manufacturing Operations Analytics — Key Insights

## Executive Summary

This analysis covers **12 months** (Jan–Dec 2024) of manufacturing operations data across **5 production lines** 
and **20 machines**, totaling **{len(df):,} hourly records**.

---

## 🏭 Production Overview

| Metric | Value |
|--------|-------|
| **Total Units Produced** | {total_units:,.0f} |
| **Good Units (Passed QC)** | {total_good:,.0f} |
| **Defective Units** | {total_defects:,.0f} |
| **Overall Scrap Rate** | {(total_defects/total_units)*100:.2f}% |
| **Total Downtime** | {total_downtime_hrs:,.0f} hours |
| **Energy Consumed** | {total_energy:,.0f} kWh |
| **Est. Production Value** | ${total_revenue:,.0f} |

---

## 📈 Key Finding #1: OEE Below World-Class Target

- **Overall OEE: {oee_results['overall_oee']:.1%}** (Target: ≥ 85%)
- Best line: **{oee_results['best_line']}** ({df[df['production_line']==oee_results['best_line']]['oee'].mean():.1%})
- Worst line: **{oee_results['worst_line']}** ({df[df['production_line']==oee_results['worst_line']]['oee'].mean():.1%})
- **Recommendation**: Focus improvement efforts on {oee_results['worst_line']} — potential to recover 
  {abs(df[df['production_line']==oee_results['best_line']]['oee'].mean() - df[df['production_line']==oee_results['worst_line']]['oee'].mean()):.1%} OEE gap.

## 📊 Key Finding #2: Downtime Pareto (80/20 Rule)

The top downtime causes responsible for **80% of lost production time** are:
{chr(10).join(f'- **{cause}**' for cause in pareto_results['top_causes_80'])}

- **Recommendation**: Prioritize reducing **Equipment Failure** and **Material Shortage** — 
  these two causes alone account for a major share of avoidable downtime.

## 🔬 Key Finding #3: Sensor-Defect Correlation (Predictive Maintenance Opportunity)

- **Temperature–Scrap Rate**: r = {corr_results['temp_corr']:.3f} {'(Significant ✅)' if corr_results['temp_p'] < 0.05 else '(Not Significant)'}
- **Vibration–Scrap Rate**: r = {corr_results['vib_corr']:.3f} {'(Significant ✅)' if corr_results['vib_p'] < 0.05 else '(Not Significant)'}
- **Recommendation**: Implement threshold-based alerts — when vibration exceeds **8 mm/s** or temperature 
  deviates **>10°C** from baseline, trigger preventive inspection. This is a strong candidate for a 
  **predictive maintenance model**.

## ⏰ Key Finding #4: Night Shift Underperforms

- Morning: **{shift_results['morning_oee']:.1%}** | Afternoon: **{shift_results['afternoon_oee']:.1%}** | Night: **{shift_results['night_oee']:.1%}**
- ANOVA p-value: {shift_results['p_value']:.2e} — {'Statistically significant difference ✅' if shift_results['p_value'] < 0.05 else 'No significant difference'}
- **Recommendation**: Investigate root causes of night shift underperformance — 
  potential factors include fatigue, reduced supervision, or environmental conditions.

## 🔧 Key Finding #5: Machine Reliability Varies Significantly

- **Least Reliable**: {mtbf_results['least_reliable']} — prioritize for maintenance overhaul
- **Most Reliable**: {mtbf_results['most_reliable']}
- **Recommendation**: Machines with MTBF below the fleet median should be scheduled for 
  preventive maintenance or parts replacement.

---

## 💡 Business Impact Summary

> If OEE is improved from **{oee_results['overall_oee']:.1%}** to the world-class target of **85%**, 
> the estimated annual production increase would be **~{int(total_good * (0.85 / oee_results['overall_oee'] - 1)):,} additional good units**, 
> translating to approximately **${int(total_revenue * (0.85 / oee_results['overall_oee'] - 1)):,}** in additional revenue.

---

*Analysis generated using Python (Pandas, SciPy, Matplotlib) — {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    with open(os.path.join(ANALYSIS_DIR, "insights_summary.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("   ✅ Saved insights_summary.md")
    return summary


def run_analytics():
    """Run the complete analytics pipeline."""
    print("=" * 60)
    print("🔬 MANUFACTURING ANALYTICS PIPELINE")
    print("=" * 60)
    
    os.makedirs(CHARTS_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    df = load_data()
    
    oee_results = analyze_oee_trends(df)
    pareto_results = analyze_downtime_pareto(df)
    corr_results = analyze_correlations(df)
    shift_results = analyze_shift_performance(df)
    mtbf_results = analyze_machine_reliability(df)
    
    generate_executive_summary(df, oee_results, pareto_results, corr_results, shift_results, mtbf_results)
    
    print("\n" + "=" * 60)
    print("✅ ANALYTICS PIPELINE COMPLETE")
    print(f"   Charts saved to: {CHARTS_DIR}")
    print(f"   Insights saved to: {ANALYSIS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    run_analytics()
