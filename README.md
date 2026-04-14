# E-Commerce RFM Segmentation & Revenue Analysis

> **Tools:** Python · Pandas · Matplotlib · Seaborn · Power BI
> **Data:** Modelled after UCI Online Retail II Dataset (Chen et al., 2019) — 115K+ transactions
> **Author:** Akash Trivedi · [LinkedIn](https://www.linkedin.com/in/at2924/) · [Tableau Public](https://public.tableau.com/app/profile/akash.trivedi4762)

---

## Business Question

**Who are our most valuable customers and where is revenue being lost?**

This project applies RFM (Recency, Frequency, Monetary) scoring to segment 3,039 customers into 8 behavioural groups, quantify revenue at risk, and identify re-engagement targets for the marketing team.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total Revenue Analysed | **£15.9M** |
| Total Transactions | **113,203** |
| Unique Customers Scored | **3,039** |
| Average Order Value | **£1,289** |
| Champions (23.7% of customers) | **74.5% of revenue** |
| At-Risk Revenue (re-engagement target) | **£834,356** |
| Lost Revenue (churned customers) | **£190,891** |
| Cancellation Revenue Lost | **£316,064** |

---

## RFM Framework

| Score | Dimension | Definition |
|-------|-----------|-----------|
| **R** | Recency | Days since last purchase (lower = better) |
| **F** | Frequency | Number of unique invoices |
| **M** | Monetary | Total spend in £ |

Each dimension scored 1–5 via quintile ranking. Combined into RFM Total Score (3–15).

---

## Customer Segments

| Segment | Customers | Revenue | Avg Recency | Action |
|---------|-----------|---------|-------------|--------|
| **Champions** | 719 | £11.87M | 32 days | Reward & retain |
| **Loyal Customers** | 326 | £2.27M | 120 days | Upsell |
| **Potential Loyal** | 290 | £375K | 86 days | Build frequency |
| **At Risk** | 329 | £834K | 345 days | Win-back campaign |
| **Can't Lose Them** | — | — | — | Urgent re-engagement |
| **New Customers** | 248 | £133K | 38 days | Onboard well |
| **Price Sensitive** | 192 | £95K | 242 days | Value offers |
| **Lost** | 689 | £191K | 471 days | Low priority |

---

## Visualizations

| # | Chart | Insight |
|---|-------|---------|
| 1 | Segment Distribution Bar | 689 Lost customers — largest segment by count |
| 2 | Revenue by Segment (Pareto) | Champions alone = 74.5% of revenue |
| 3 | RFM Scatter — Recency vs Monetary | Visual cluster separation by segment |
| 4 | Monthly Revenue Trend | Clear Q4 seasonality; Christmas peaks |
| 5 | Revenue by Country | UK = 82%; Germany/France = key growth markets |
| 6 | Revenue by Product Category | Home Decor leads; Seasonal/Gifts highest margin |
| 7 | RFM Heatmap (R×F → Monetary) | High R + High F = exponentially higher spend |
| 8 | Revenue at Risk | £834K at-risk, £191K lost — £1M+ re-engagement opportunity |

---

## Project Structure

```
ecommerce-rfm-analysis/
├── data/
│   ├── online_retail_raw.csv           # 115K raw transactions
│   ├── rfm_scores.csv                  # 3,039 customers with RFM scores + segments
│   ├── powerbi_fact_transactions.csv   # Fact table (star schema)
│   ├── powerbi_dim_customers.csv       # Customer dimension with RFM
│   ├── powerbi_dim_date.csv            # Date dimension
│   ├── powerbi_segment_kpi.csv         # Segment-level KPIs
│   └── powerbi_monthly_revenue.csv     # Monthly aggregates
├── notebooks/
│   ├── 01_data_generation.py           # Transaction data simulation
│   ├── 02_rfm_analysis.py              # RFM scoring + 8 visualizations
│   └── 03_powerbi_export.py            # Star schema export + blueprint
├── charts/
│   ├── 01_segment_distribution.png
│   ├── 02_revenue_by_segment.png
│   ├── 03_rfm_scatter.png
│   ├── 04_monthly_revenue.png
│   ├── 05_revenue_by_country.png
│   ├── 06_revenue_by_category.png
│   ├── 07_rfm_heatmap.png
│   └── 08_revenue_at_risk.png
└── README.md
```

---

## How to Run

```bash
git clone https://github.com/AkashTrivedi29/ecommerce-rfm-analysis
cd ecommerce-rfm-analysis
pip install pandas numpy matplotlib seaborn

python notebooks/01_data_generation.py
python notebooks/02_rfm_analysis.py
python notebooks/03_powerbi_export.py
```

---

## Power BI Dashboard

**Dashboard file:** Open `Akash_Trivedi_RFM_Analysis.pbix` in Power BI Desktop to explore the full 4-page interactive report.

**4-page dashboard:**
1. **Executive Summary** — KPI cards, monthly revenue trend, slicers
2. **Customer Segmentation** — Treemap, revenue by segment, RFM scatter
3. **Revenue Analysis** — Country/category breakdown, seasonality
4. **Revenue at Risk** — Gauge, at-risk customer table, action recommendations

---

## Business Recommendations

**Immediate (0–30 days):**
- Launch win-back email campaign targeting 329 **At Risk** customers — £834K revenue opportunity
- Offer exclusive loyalty rewards to 719 **Champions** — protect £11.87M revenue base

**Short-term (30–90 days):**
- Convert 290 **Potential Loyal** customers with frequency incentives (2nd/3rd purchase discounts)
- Investigate £316K in cancellation revenue — identify top return reasons by product category

**Strategic (90+ days):**
- Expand Germany & France markets — currently 7% of revenue with strong growth indicators
- Build seasonal inventory model around Q4 peaks — Nov/Dec = 2.5× average monthly revenue

---

## Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.10 | Data pipeline, RFM scoring |
| Pandas | Data cleaning, aggregation, quintile scoring |
| Matplotlib / Seaborn | 8 analytical visualizations |
| Power BI | 4-page interactive business dashboard |
| GitHub | Version control + portfolio |

---

*Data modelled after UCI Online Retail II Dataset. Original dataset: Chen et al. (2019), UCI ML Repository.*
