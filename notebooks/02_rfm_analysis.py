"""
=============================================================================
PROJECT 2: E-Commerce RFM Segmentation & Revenue Analysis
RFM Scoring Model + Full EDA
=============================================================================
Business Question:
  Who are our most valuable customers and where is revenue being lost?

RFM Framework:
  R (Recency)   — How recently did the customer purchase?
  F (Frequency) — How often do they purchase?
  M (Monetary)  — How much do they spend in total?

Segments produced:
  Champions        → Recent, frequent, high spend
  Loyal Customers  → Frequent, high spend, slightly less recent
  Potential Loyal  → Recent, moderate frequency
  At Risk          → Previously good, haven't bought lately
  Can't Lose Them  → High value, now inactive
  Lost             → Long inactive, low engagement
  New Customers    → Bought once recently
  Price Sensitive  → Low monetary despite frequency
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi": 150, "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa", "axes.grid": True,
    "grid.color": "white", "grid.linewidth": 1.0,
    "font.family": "DejaVu Sans", "axes.titlesize": 13,
    "axes.titleweight": "bold", "axes.labelsize": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})

C = {"primary": "#1565C0", "secondary": "#E53935", "success": "#2E7D32",
     "warning": "#F57F17", "neutral": "#546E7A", "purple": "#6A1B9A",
     "teal": "#00695C", "orange": "#E65100"}

DATA  = "/sessions/dazzling-sweet-pascal/day2_rfm/data"
CHART = "/sessions/dazzling-sweet-pascal/day2_rfm/charts"

# ── Load & Clean ──────────────────────────────────────────────────────────
df = pd.read_csv(f"{DATA}/online_retail_raw.csv", parse_dates=["InvoiceDate"])

print("=" * 60)
print("DATA CLEANING SUMMARY")
print("=" * 60)
print(f"Raw records:          {len(df):,}")

# Remove cancellations for RFM (keep for revenue loss analysis)
df_cancel = df[df["InvoiceNo"].astype(str).str.startswith("C")].copy()
df_clean  = df[~df["InvoiceNo"].astype(str).str.startswith("C")].copy()
df_clean  = df_clean[df_clean["Quantity"] > 0]
df_clean  = df_clean[df_clean["UnitPrice"] > 0]
df_clean  = df_clean.dropna(subset=["CustomerID"])

print(f"After removing cancellations: {len(df_clean):,}")
print(f"Cancellation lines: {len(df_cancel):,}")
print(f"Unique customers: {df_clean['CustomerID'].nunique():,}")
print(f"Date range: {df_clean['InvoiceDate'].min().date()} → {df_clean['InvoiceDate'].max().date()}")

# ── RFM Calculation ───────────────────────────────────────────────────────
snapshot_date = df_clean["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df_clean.groupby("CustomerID").agg(
    Recency   = ("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
    Frequency = ("InvoiceNo",   "nunique"),
    Monetary  = ("Revenue",     "sum")
).reset_index()

rfm["Monetary"] = rfm["Monetary"].round(2)

# ── RFM Scoring (1–5 quintiles) ───────────────────────────────────────────
rfm["R_Score"] = pd.qcut(rfm["Recency"],   5, labels=[5,4,3,2,1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"],  5, labels=[1,2,3,4,5]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

# ── Customer Segmentation ─────────────────────────────────────────────────
def segment_customer(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 4:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New Customers"
    elif r >= 3 and f >= 2 and m >= 3:
        return "Potential Loyal"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f >= 4 and m >= 4:
        return "Can't Lose Them"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    elif f >= 3 and m <= 2:
        return "Price Sensitive"
    else:
        return "Needs Attention"

rfm["Segment"] = rfm.apply(segment_customer, axis=1)

# ── Print Summary ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("RFM SEGMENTATION RESULTS")
print("=" * 60)
seg_summary = rfm.groupby("Segment").agg(
    Customers = ("CustomerID", "count"),
    Avg_Recency   = ("Recency",   "mean"),
    Avg_Frequency = ("Frequency", "mean"),
    Avg_Monetary  = ("Monetary",  "mean"),
    Total_Revenue = ("Monetary",  "sum"),
).round(1).sort_values("Total_Revenue", ascending=False)
print(seg_summary.to_string())

total_rev = rfm["Monetary"].sum()
champions = rfm[rfm["Segment"] == "Champions"]
at_risk   = rfm[rfm["Segment"] == "At Risk"]
lost      = rfm[rfm["Segment"] == "Lost"]

print(f"\nTotal Revenue:             £{total_rev:,.2f}")
print(f"Champions Revenue:         £{champions['Monetary'].sum():,.2f} ({champions['Monetary'].sum()/total_rev*100:.1f}%)")
print(f"At Risk Revenue (at stake):£{at_risk['Monetary'].sum():,.2f}")
print(f"Lost Revenue:              £{lost['Monetary'].sum():,.2f}")
print(f"Cancellation Revenue Lost: £{abs(df_cancel['Revenue'].sum()):,.2f}")

# ============================================================
# CHART 1: Customer Segment Distribution (Treemap-style bar)
# ============================================================
seg_counts = rfm["Segment"].value_counts()
seg_colors = {
    "Champions": "#1565C0", "Loyal Customers": "#1976D2",
    "Potential Loyal": "#42A5F5", "New Customers": "#90CAF9",
    "At Risk": "#E53935", "Can't Lose Them": "#B71C1C",
    "Lost": "#EF9A9A", "Price Sensitive": "#F57F17",
    "Needs Attention": "#546E7A"
}

fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(seg_counts.index, seg_counts.values,
              color=[seg_colors.get(s, "#999") for s in seg_counts.index],
              edgecolor="white", linewidth=0.8)

for bar, val in zip(bars, seg_counts.values):
    pct = val / len(rfm) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
            f"{val:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=8, fontweight="bold")

ax.set_title("Customer Segmentation by RFM Score\nDistribution across 9 behavioural segments")
ax.set_xlabel("Customer Segment")
ax.set_ylabel("Number of Customers")
plt.xticks(rotation=20, ha="right")
fig.tight_layout()
fig.savefig(f"{CHART}/01_segment_distribution.png", bbox_inches="tight")
plt.close()
print("\n✅ Chart 1 saved")

# ============================================================
# CHART 2: Revenue by Segment (Pareto principle)
# ============================================================
seg_rev = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)
cumulative_pct = (seg_rev.cumsum() / seg_rev.sum() * 100)

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()

colors = [seg_colors.get(s, "#999") for s in seg_rev.index]
ax1.bar(seg_rev.index, seg_rev.values / 1000, color=colors, edgecolor="white", alpha=0.9)
ax2.plot(range(len(seg_rev)), cumulative_pct.values, "ko-", linewidth=2, markersize=6)
ax2.axhline(80, color="red", linestyle="--", alpha=0.6, linewidth=1.2)
ax2.text(len(seg_rev)-0.5, 81, "80% Revenue", ha="right", fontsize=8, color="red")

ax1.set_ylabel("Revenue (£ thousands)")
ax2.set_ylabel("Cumulative Revenue %")
ax1.set_xticks(range(len(seg_rev)))
ax1.set_xticklabels(seg_rev.index, rotation=20, ha="right")
ax1.set_title("Revenue by Customer Segment — Pareto Analysis\nWhich segments drive 80% of revenue?")
fig.tight_layout()
fig.savefig(f"{CHART}/02_revenue_by_segment.png", bbox_inches="tight")
plt.close()
print("✅ Chart 2 saved")

# ============================================================
# CHART 3: RFM Scatter — Recency vs Monetary (colored by segment)
# ============================================================
fig, ax = plt.subplots(figsize=(11, 7))
for seg, color in seg_colors.items():
    subset = rfm[rfm["Segment"] == seg]
    if len(subset) == 0: continue
    ax.scatter(subset["Recency"], subset["Monetary"],
               c=color, label=seg, alpha=0.6, s=20, edgecolors="none")

ax.set_xlabel("Recency (days since last purchase)")
ax.set_ylabel("Monetary Value (£ total spend)")
ax.set_title("RFM Scatter — Recency vs. Monetary Value by Segment\nIdeal customers: bottom-right (recent + high spend)")
ax.legend(loc="upper right", fontsize=8, markerscale=2)
ax.set_yscale("log")
fig.tight_layout()
fig.savefig(f"{CHART}/03_rfm_scatter.png", bbox_inches="tight")
plt.close()
print("✅ Chart 3 saved")

# ============================================================
# CHART 4: Monthly Revenue Trend with annotations
# ============================================================
df_clean["YearMonth"] = df_clean["InvoiceDate"].dt.to_period("M")
monthly = df_clean.groupby("YearMonth")["Revenue"].sum().reset_index()
monthly["YearMonth_dt"] = monthly["YearMonth"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(monthly["YearMonth_dt"], monthly["Revenue"]/1000,
                alpha=0.3, color=C["primary"])
ax.plot(monthly["YearMonth_dt"], monthly["Revenue"]/1000,
        color=C["primary"], linewidth=2)

# Annotate peak
peak = monthly.loc[monthly["Revenue"].idxmax()]
ax.annotate(f'Peak: £{peak["Revenue"]/1000:.0f}K',
            xy=(peak["YearMonth_dt"], peak["Revenue"]/1000),
            xytext=(peak["YearMonth_dt"], peak["Revenue"]/1000 + 50),
            fontsize=9, color="red", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="red"))

ax.set_title("Monthly Revenue Trend (Dec 2009 – Dec 2011)\nSeasonal peaks in Q4 confirm Christmas-driven demand")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (£ thousands)")
fig.tight_layout()
fig.savefig(f"{CHART}/04_monthly_revenue.png", bbox_inches="tight")
plt.close()
print("✅ Chart 4 saved")

# ============================================================
# CHART 5: Revenue by Country (Top 10)
# ============================================================
country_rev = df_clean.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 6))
colors_c = [C["primary"] if c == "United Kingdom" else C["neutral"] for c in country_rev.index]
bars = ax.barh(country_rev.index[::-1], country_rev.values[::-1]/1000, color=colors_c[::-1])

for bar in bars:
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            f"£{bar.get_width():.0f}K", va="center", fontsize=8)

ax.set_xlabel("Revenue (£ thousands)")
ax.set_title("Revenue by Country — Top 10 Markets\nUK dominates; Germany & France are key international markets")
fig.tight_layout()
fig.savefig(f"{CHART}/05_revenue_by_country.png", bbox_inches="tight")
plt.close()
print("✅ Chart 5 saved")

# ============================================================
# CHART 6: Revenue by Product Category
# ============================================================
cat_rev = df_clean.groupby("Category")["Revenue"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(cat_rev.index, cat_rev.values/1000,
              color=plt.cm.Blues(np.linspace(0.4, 0.9, len(cat_rev)))[::-1])
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f"£{bar.get_height():.0f}K", ha="center", va="bottom", fontsize=8)
ax.set_ylabel("Revenue (£ thousands)")
ax.set_title("Revenue by Product Category\nHome Decor and Kitchenware lead revenue contribution")
plt.xticks(rotation=15, ha="right")
fig.tight_layout()
fig.savefig(f"{CHART}/06_revenue_by_category.png", bbox_inches="tight")
plt.close()
print("✅ Chart 6 saved")

# ============================================================
# CHART 7: RFM Heatmap — Average Monetary by R×F Score
# ============================================================
rfm_heat = rfm.groupby(["R_Score","F_Score"])["Monetary"].mean().unstack()

fig, ax = plt.subplots(figsize=(9, 6))
sns.heatmap(rfm_heat, annot=True, fmt=".0f", cmap="YlOrRd",
            ax=ax, linewidths=0.5, linecolor="white",
            cbar_kws={"label": "Avg Monetary Value (£)"},
            annot_kws={"size": 9})
ax.set_title("Average Customer Value by Recency × Frequency Score\nHigh R + High F = Champions (top-right cell)")
ax.set_xlabel("Frequency Score (1=Low, 5=High)")
ax.set_ylabel("Recency Score (1=Old, 5=Recent)")
fig.tight_layout()
fig.savefig(f"{CHART}/07_rfm_heatmap.png", bbox_inches="tight")
plt.close()
print("✅ Chart 7 saved")

# ============================================================
# CHART 8: Revenue at Risk — At Risk + Can't Lose + Lost
# ============================================================
risk_segs = ["Champions", "Loyal Customers", "At Risk", "Can't Lose Them", "Lost"]
risk_data = rfm[rfm["Segment"].isin(risk_segs)].groupby("Segment").agg(
    Customers=("CustomerID","count"),
    Revenue=("Monetary","sum")
).reindex(risk_segs)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].bar(risk_data.index, risk_data["Customers"],
            color=[seg_colors.get(s, "#999") for s in risk_data.index])
axes[0].set_title("Customer Count by Value Segment")
axes[0].set_ylabel("Customers")
plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=15, ha="right")

axes[1].bar(risk_data.index, risk_data["Revenue"]/1000,
            color=[seg_colors.get(s, "#999") for s in risk_data.index])
axes[1].set_title("Revenue at Risk by Segment\n(At Risk + Can't Lose = Re-engagement targets)")
axes[1].set_ylabel("Revenue (£ thousands)")
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=15, ha="right")

# Annotate at-risk revenue
for ax_i in axes:
    for bar in ax_i.patches:
        ax_i.text(bar.get_x() + bar.get_width()/2,
                  bar.get_height() + 0.5,
                  f"{bar.get_height():,.0f}",
                  ha="center", va="bottom", fontsize=8)

fig.suptitle("Revenue at Risk Analysis — Where is money being lost?", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{CHART}/08_revenue_at_risk.png", bbox_inches="tight")
plt.close()
print("✅ Chart 8 saved")

# ── Save RFM table ─────────────────────────────────────────────────────────
rfm.to_csv(f"{DATA}/rfm_scores.csv", index=False)
print("\n✅ RFM scores saved")
print(f"\nTotal customers scored: {len(rfm):,}")
print(f"Segments: {rfm['Segment'].value_counts().to_dict()}")
