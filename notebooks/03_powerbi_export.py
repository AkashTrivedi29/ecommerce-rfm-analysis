"""
=============================================================================
Power BI Export — RFM Segmentation & Revenue Analysis
=============================================================================
Creates optimised tables for Power BI data model.
Power BI works best with a Star Schema:
  - Fact table: transactions
  - Dimension tables: customers (with RFM), products, dates

Dashboard Pages planned:
  Page 1: Executive KPI Summary (revenue, customers, avg order value)
  Page 2: Customer Segmentation (RFM treemap + scatter)
  Page 3: Revenue Analysis (trend + by country + by category)
  Page 4: Revenue at Risk (at-risk + lost segments)
=============================================================================
"""
import pandas as pd
import numpy as np

DATA = "/sessions/dazzling-sweet-pascal/day2_rfm/data"

df_raw = pd.read_csv(f"{DATA}/online_retail_raw.csv", parse_dates=["InvoiceDate"])
rfm    = pd.read_csv(f"{DATA}/rfm_scores.csv")

# Remove cancellations
df_clean = df_raw[~df_raw["InvoiceNo"].astype(str).str.startswith("C")].copy()
df_clean = df_clean[df_clean["Quantity"] > 0]
df_clean = df_clean[df_clean["UnitPrice"] > 0]
df_clean = df_clean.dropna(subset=["CustomerID"])

# ── FACT TABLE: Transactions ───────────────────────────────────────────────
fact = df_clean[["InvoiceNo","InvoiceDate","StockCode","CustomerID",
                 "Quantity","UnitPrice","Revenue","Country","Category"]].copy()
fact["InvoiceDate"] = pd.to_datetime(fact["InvoiceDate"])
fact["Year"]        = fact["InvoiceDate"].dt.year
fact["Month"]       = fact["InvoiceDate"].dt.month
fact["MonthName"]   = fact["InvoiceDate"].dt.strftime("%b")
fact["YearMonth"]   = fact["InvoiceDate"].dt.to_period("M").astype(str)
fact["Quarter"]     = "Q" + fact["InvoiceDate"].dt.quarter.astype(str)
fact["DayOfWeek"]   = fact["InvoiceDate"].dt.day_name()

# ── DIM TABLE: Customers with RFM ─────────────────────────────────────────
dim_customer = rfm[["CustomerID","Recency","Frequency","Monetary",
                     "R_Score","F_Score","M_Score","RFM_Total","Segment"]].copy()
dim_customer["Value_Tier"] = pd.cut(
    dim_customer["RFM_Total"],
    bins=[0, 5, 8, 11, 15],
    labels=["Low Value", "Medium Value", "High Value", "Champions"]
)
dim_customer["Is_At_Risk"]    = dim_customer["Segment"].isin(["At Risk","Can't Lose Them"]).astype(int)
dim_customer["Is_Champion"]   = (dim_customer["Segment"] == "Champions").astype(int)
dim_customer["Is_Lost"]       = (dim_customer["Segment"] == "Lost").astype(int)
dim_customer["Monetary_Band"] = pd.cut(
    dim_customer["Monetary"],
    bins=[0, 500, 2000, 5000, 10000, 999999],
    labels=["<£500", "£500-2K", "£2K-5K", "£5K-10K", "£10K+"]
)

# ── DIM TABLE: Date ────────────────────────────────────────────────────────
date_range = pd.date_range(start="2009-12-01", end="2011-12-31", freq="D")
dim_date = pd.DataFrame({
    "Date":       date_range,
    "Year":       date_range.year,
    "Month":      date_range.month,
    "MonthName":  date_range.strftime("%b"),
    "Quarter":    "Q" + date_range.quarter.astype(str),
    "YearMonth":  date_range.to_period("M").astype(str),
    "DayOfWeek":  date_range.day_name(),
    "IsWeekend":  (date_range.dayofweek >= 5).astype(int),
})

# ── SUMMARY TABLE: Segment KPIs (for Power BI cards) ─────────────────────
seg_kpi = rfm.groupby("Segment").agg(
    Customers      = ("CustomerID",  "count"),
    Total_Revenue  = ("Monetary",    "sum"),
    Avg_Revenue    = ("Monetary",    "mean"),
    Avg_Recency    = ("Recency",     "mean"),
    Avg_Frequency  = ("Frequency",   "mean"),
).round(2).reset_index()

seg_kpi["Revenue_Share_Pct"] = (seg_kpi["Total_Revenue"] / seg_kpi["Total_Revenue"].sum() * 100).round(2)
seg_kpi["Customer_Share_Pct"] = (seg_kpi["Customers"] / seg_kpi["Customers"].sum() * 100).round(2)
seg_kpi["Priority"] = seg_kpi["Segment"].map({
    "Champions": 1, "Loyal Customers": 2, "Potential Loyal": 3,
    "New Customers": 4, "At Risk": 5, "Can't Lose Them": 6,
    "Needs Attention": 7, "Price Sensitive": 8, "Lost": 9
})
seg_kpi = seg_kpi.sort_values("Priority")

# ── MONTHLY REVENUE TABLE ─────────────────────────────────────────────────
monthly = df_clean.groupby(["YearMonth" if "YearMonth" in df_clean.columns else
    df_clean["InvoiceDate"].dt.to_period("M").astype(str)]).agg(
    Revenue       = ("Revenue",    "sum"),
    Orders        = ("InvoiceNo",  "nunique"),
    Customers     = ("CustomerID", "nunique"),
).reset_index()

if "InvoiceDate" in monthly.columns:
    monthly = monthly.rename(columns={"InvoiceDate":"YearMonth"})

monthly_agg = fact.groupby("YearMonth").agg(
    Revenue   = ("Revenue",    "sum"),
    Orders    = ("InvoiceNo",  "nunique"),
    Customers = ("CustomerID", "nunique"),
    Avg_Order_Value = ("Revenue", "mean"),
).round(2).reset_index()

# ── Save all Power BI tables ───────────────────────────────────────────────
fact.to_csv(f"{DATA}/powerbi_fact_transactions.csv", index=False)
dim_customer.to_csv(f"{DATA}/powerbi_dim_customers.csv", index=False)
dim_date.to_csv(f"{DATA}/powerbi_dim_date.csv", index=False)
seg_kpi.to_csv(f"{DATA}/powerbi_segment_kpi.csv", index=False)
monthly_agg.to_csv(f"{DATA}/powerbi_monthly_revenue.csv", index=False)

print("✅ Power BI export complete")
print(f"   powerbi_fact_transactions.csv  — {len(fact):,} rows")
print(f"   powerbi_dim_customers.csv      — {len(dim_customer):,} rows")
print(f"   powerbi_dim_date.csv           — {len(dim_date):,} rows")
print(f"   powerbi_segment_kpi.csv        — {len(seg_kpi):,} rows")
print(f"   powerbi_monthly_revenue.csv    — {len(monthly_agg):,} rows")

# ── KPI Summary for README ─────────────────────────────────────────────────
print("""
╔══════════════════════════════════════════════════════════════╗
║         KEY BUSINESS METRICS                                 ║
╠══════════════════════════════════════════════════════════════╣""")
print(f"║  Total Revenue:        £{fact['Revenue'].sum():>12,.2f}              ║")
print(f"║  Total Orders:         {fact['InvoiceNo'].nunique():>12,}              ║")
print(f"║  Unique Customers:     {fact['CustomerID'].nunique():>12,}              ║")
print(f"║  Avg Order Value:      £{fact.groupby('InvoiceNo')['Revenue'].sum().mean():>11,.2f}              ║")
print(f"║  Champions (% of rev): {rfm[rfm['Segment']=='Champions']['Monetary'].sum()/rfm['Monetary'].sum()*100:>11.1f}%              ║")
print(f"║  At-Risk Revenue:      £{rfm[rfm['Segment']=='At Risk']['Monetary'].sum():>11,.2f}              ║")
print("""╚══════════════════════════════════════════════════════════════╝

POWER BI DASHBOARD BLUEPRINT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAGE 1 — Executive Summary
  • Card visuals: Total Revenue, Orders, Customers, AOV
  • Line chart: Monthly Revenue (powerbi_monthly_revenue.csv)
  • Slicer: Year, Country

PAGE 2 — Customer Segmentation
  • Treemap: Customers by Segment (powerbi_segment_kpi.csv)
  • Bar chart: Revenue by Segment
  • Scatter: Recency vs Monetary (powerbi_dim_customers.csv)
  • KPI cards: Champions %, At-Risk Revenue

PAGE 3 — Revenue Analysis
  • Bar: Revenue by Country (powerbi_fact_transactions.csv)
  • Bar: Revenue by Category
  • Matrix: RFM Score heatmap

PAGE 4 — Revenue at Risk
  • Gauge: At-Risk Revenue vs Total
  • Table: Top at-risk customers (filter Segment = At Risk)
  • Action plan text boxes
""")
