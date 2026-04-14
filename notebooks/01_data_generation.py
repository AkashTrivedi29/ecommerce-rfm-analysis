"""
=============================================================================
PROJECT 2: E-Commerce RFM Segmentation & Revenue Analysis
Dataset Generator — Modelled after UCI Online Retail Dataset
=============================================================================
Original Dataset: UCI Online Retail II (Chen et al., 2019)
  - 500K+ real transactions from a UK-based online retailer
  - Dec 2009 – Dec 2011
  - Available at: archive.ics.uci.edu/dataset/502/online+retail+ii

This script generates a realistic synthetic replica preserving:
  - Transaction volume and seasonality patterns
  - Return/cancellation rates (~2%)
  - Customer concentration (top 20% = 80% revenue — Pareto principle)
  - Product mix and pricing distributions
  - Geographic distribution (UK + international)
=============================================================================
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# ---------------------------------------------------------------------------
# 1. Product Catalogue (200 SKUs modelled after UCI dataset)
# ---------------------------------------------------------------------------
product_categories = {
    "Home Decor":        {"skus": 40, "price_range": (2.50, 25.00),  "weight": 0.28},
    "Kitchenware":       {"skus": 35, "price_range": (1.25, 18.50),  "weight": 0.22},
    "Seasonal/Gifts":    {"skus": 30, "price_range": (0.85, 35.00),  "weight": 0.18},
    "Stationery":        {"skus": 25, "price_range": (0.42, 8.75),   "weight": 0.12},
    "Garden & Outdoor":  {"skus": 20, "price_range": (3.50, 22.00),  "weight": 0.10},
    "Children's Items":  {"skus": 15, "price_range": (1.50, 15.00),  "weight": 0.06},
    "Candles & Fragrance":{"skus":15, "price_range": (2.25, 28.00),  "weight": 0.04},
}

products = []
stock_id = 20000
for cat, params in product_categories.items():
    for i in range(params["skus"]):
        price = round(np.random.uniform(*params["price_range"]), 2)
        products.append({
            "StockCode":   str(stock_id),
            "Description": f"{cat} Item {i+1:02d}",
            "Category":    cat,
            "UnitPrice":   price,
        })
        stock_id += 1

df_products = pd.DataFrame(products)

# ---------------------------------------------------------------------------
# 2. Customer Base (4,500 customers)
# ---------------------------------------------------------------------------
countries = {
    "United Kingdom":  0.82,
    "Germany":         0.04,
    "France":          0.03,
    "EIRE":            0.03,
    "Netherlands":     0.02,
    "Spain":           0.01,
    "Belgium":         0.01,
    "Australia":       0.01,
    "Switzerland":     0.01,
    "Other":           0.02,
}

n_customers = 4500
customer_ids = list(range(12000, 12000 + n_customers))
country_list = np.random.choice(
    list(countries.keys()),
    size=n_customers,
    p=list(countries.values())
)

# Customer value tiers (Pareto distribution)
# Top 5%   → Very High value (Champions)
# Next 15% → High value
# Next 30% → Medium value
# Next 30% → Low value
# Bottom 20% → Churned/dormant
customer_tiers = np.random.choice(
    ["very_high", "high", "medium", "low", "dormant"],
    size=n_customers,
    p=[0.05, 0.15, 0.30, 0.30, 0.20]
)

tier_orders = {
    "very_high": (20, 50),
    "high":      (8, 20),
    "medium":    (3, 8),
    "low":       (1, 3),
    "dormant":   (0, 1),
}

tier_qty = {
    "very_high": (10, 30),
    "high":      (4, 12),
    "medium":    (2, 6),
    "low":       (1, 3),
    "dormant":   (1, 2),
}

# ---------------------------------------------------------------------------
# 3. Generate Transactions (Dec 2009 – Dec 2011)
# ---------------------------------------------------------------------------
start_date = datetime(2009, 12, 1)
end_date   = datetime(2011, 12, 9)
date_range = (end_date - start_date).days

def seasonal_weight(date):
    """Heavier Nov-Dec (Christmas), lighter Jan-Feb"""
    month = date.month
    weights = {1:0.6, 2:0.6, 3:0.8, 4:0.85, 5:0.9, 6:0.9,
               7:0.85, 8:0.85, 9:1.0, 10:1.1, 11:1.4, 12:1.5}
    return weights.get(month, 1.0)

transactions = []
invoice_id = 536365

for i, (cust_id, tier, country) in enumerate(zip(customer_ids, customer_tiers, country_list)):
    n_orders_range = tier_orders[tier]
    n_orders = np.random.randint(*n_orders_range) if n_orders_range[1] > n_orders_range[0] else n_orders_range[0]

    if n_orders == 0:
        continue

    # Spread orders across date range
    order_dates = sorted([
        start_date + timedelta(days=np.random.randint(0, date_range))
        for _ in range(n_orders)
    ])

    for order_date in order_dates:
        # Seasonal boost
        if np.random.random() > seasonal_weight(order_date) * 0.5:
            continue

        # Number of line items per invoice
        n_lines = np.random.randint(*tier_qty[tier])

        # Select products for this invoice
        selected = df_products.sample(n=min(n_lines, len(df_products))).copy()

        for _, prod in selected.iterrows():
            qty = np.random.randint(1, 25)
            # Cancellation (~2% of transactions)
            is_cancel = np.random.random() < 0.02
            inv_no = f"C{invoice_id}" if is_cancel else str(invoice_id)
            if is_cancel:
                qty = -qty

            transactions.append({
                "InvoiceNo":   inv_no,
                "StockCode":   prod["StockCode"],
                "Description": prod["Description"],
                "Category":    prod["Category"],
                "Quantity":    qty,
                "InvoiceDate": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "UnitPrice":   prod["UnitPrice"],
                "CustomerID":  cust_id,
                "Country":     country,
            })
        invoice_id += 1

df_raw = pd.DataFrame(transactions)
df_raw["Revenue"] = df_raw["Quantity"] * df_raw["UnitPrice"]

print(f"✅ Raw transactions generated: {len(df_raw):,} rows")
print(f"   Customers: {df_raw['CustomerID'].nunique():,}")
print(f"   Invoices:  {df_raw['InvoiceNo'].nunique():,}")
print(f"   Date range: {df_raw['InvoiceDate'].min()} → {df_raw['InvoiceDate'].max()}")
print(f"   Total Revenue: £{df_raw[df_raw['Quantity']>0]['Revenue'].sum():,.2f}")
print(f"   Cancellations: {(df_raw['InvoiceNo'].str.startswith('C')).sum():,} lines")

# Save
df_raw.to_csv("/sessions/dazzling-sweet-pascal/day2_rfm/data/online_retail_raw.csv", index=False)
df_products.to_csv("/sessions/dazzling-sweet-pascal/day2_rfm/data/products.csv", index=False)
print("\n✅ Raw data saved")
