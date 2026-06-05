import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

TODAY = datetime(2026, 6, 5)

REGIONS = ["Midwest", "Northeast", "Southeast", "West", "Southwest"]
REPS = ["Marcus Johnson", "Sarah Chen", "Derek Williams", "Priya Patel",
        "Tom Kowalski", "Lisa Nguyen", "Aaron Brooks", "Kelly Martinez"]
STAGES = ["Received", "In Production", "In Decoration", "Ready to Ship", "Backordered"]
STAGE_WEIGHTS = [0.15, 0.30, 0.25, 0.20, 0.10]
HELMET_MODELS = ["SpeedFlex", "Axiom", "Precision Diamond", "F7", "Revo Speed"]
DECORATION_TYPES = ["Custom Paint", "Decal Kit", "Team Logo", "Standard"]

def make_orders(n=320):
    orders = []
    for i in range(n):
        received = TODAY - timedelta(days=random.randint(0, 28))
        stage = random.choices(STAGES, weights=STAGE_WEIGHTS)[0]
        units = random.randint(10, 250)
        price_per = random.choice([189, 219, 249, 289, 319])
        promised_days = random.randint(7, 21)
        promised_ship = received + timedelta(days=promised_days)
        sla_at_risk = promised_ship < TODAY + timedelta(days=3) and stage not in ["Ready to Ship"]
        late = promised_ship < TODAY and stage not in ["Ready to Ship"]
        age_days = (TODAY - received).days
        region = random.choice(REGIONS)
        rep = random.choice(REPS)
        store_id = f"STR-{random.randint(1000, 1999)}"
        model = random.choice(HELMET_MODELS)
        orders.append({
            "order_id": f"ORD-{10000+i}",
            "store_id": store_id,
            "rep": rep,
            "region": region,
            "model": model,
            "decoration": random.choice(DECORATION_TYPES),
            "units": units,
            "unit_price": price_per,
            "order_value": units * price_per,
            "stage": stage,
            "received_date": received,
            "promised_ship_date": promised_ship,
            "age_days": age_days,
            "sla_at_risk": sla_at_risk,
            "late": late,
        })
    return pd.DataFrame(orders)

def make_stores(orders_df):
    store_ids = orders_df["store_id"].unique()
    stores = []
    for sid in store_ids:
        sub = orders_df[orders_df["store_id"] == sid]
        rep = sub["rep"].iloc[0]
        region = sub["region"].iloc[0]
        open_date = TODAY - timedelta(days=random.randint(30, 365))
        stores.append({
            "store_id": sid,
            "store_name": f"Gameday Store {sid}",
            "rep": rep,
            "region": region,
            "open_date": open_date,
            "total_orders": len(sub),
            "total_units": sub["units"].sum(),
            "total_revenue": sub["order_value"].sum(),
            "active": random.random() > 0.1,
        })
    return pd.DataFrame(stores)

def make_monthly_shipped():
    months = pd.date_range(end=TODAY, periods=13, freq="MS")
    rows = []
    base_rev = 1_800_000
    for i, m in enumerate(months):
        ly_month = m - pd.DateOffset(years=1)
        rev = base_rev * (1 + 0.08 * (i / 12)) * random.uniform(0.88, 1.12)
        units = int(rev / 230)
        orders = int(units / 45)
        stores = random.randint(18, 34)
        rows.append({
            "month": m,
            "month_label": m.strftime("%b %Y"),
            "revenue": rev,
            "units": units,
            "orders": orders,
            "stores_active": stores,
            "avg_order_value": rev / max(orders, 1),
            "is_current_year": m.year == TODAY.year,
        })
    df = pd.DataFrame(rows)
    # Add LY comparison (shift by 12 months)
    df["revenue_ly"] = df["revenue"].shift(12) * random.uniform(0.88, 0.95)
    return df

def make_rep_performance(orders_df):
    grouped = orders_df.groupby("rep").agg(
        total_revenue=("order_value", "sum"),
        total_units=("units", "sum"),
        total_orders=("order_id", "count"),
        stores_created=("store_id", "nunique"),
        regions=("region", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()
    grouped["avg_order_value"] = grouped["total_revenue"] / grouped["total_orders"]
    grouped = grouped.sort_values("total_revenue", ascending=False).reset_index(drop=True)
    grouped["rank"] = grouped.index + 1
    return grouped

# Cached loaders
_orders = None
_stores = None
_monthly = None
_reps = None

def get_orders():
    global _orders
    if _orders is None:
        _orders = make_orders(320)
    return _orders

def get_stores():
    global _stores
    if _stores is None:
        _stores = make_stores(get_orders())
    return _stores

def get_monthly():
    global _monthly
    if _monthly is None:
        _monthly = make_monthly_shipped()
    return _monthly

def get_rep_performance():
    global _reps
    if _reps is None:
        _reps = make_rep_performance(get_orders())
    return _reps
