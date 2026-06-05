import streamlit as st
from pages_src.data import get_orders, get_stores, get_monthly, TODAY
import pandas as pd

def render():
    st.markdown("# 🏈 Riddell Operations & Financial Dashboard")
    st.markdown("**Prototype** · Synthetic data · As of June 5, 2026")
    st.markdown("---")

    orders = get_orders()
    stores = get_stores()
    monthly = get_monthly()

    # Top KPIs
    open_orders = orders[orders["stage"] != "Ready to Ship"]
    at_risk = orders[orders["sla_at_risk"] == True]
    late = orders[orders["late"] == True]
    cy_monthly = monthly[monthly["is_current_year"] == True]
    cy_rev = cy_monthly["revenue"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Open Orders", f"{len(open_orders):,}", f"${open_orders['order_value'].sum()/1e6:.1f}M value")
    with col2:
        st.metric("SLA At Risk", f"{len(at_risk):,}", f"-{len(at_risk)/len(orders)*100:.0f}% orders", delta_color="inverse")
    with col3:
        st.metric("Late Orders", f"{len(late):,}", f"${late['order_value'].sum()/1e3:.0f}K at risk", delta_color="inverse")
    with col4:
        st.metric("Active Stores", f"{stores['active'].sum():,}", f"{len(stores):,} total created")
    with col5:
        st.metric("CY Revenue (shipped)", f"${cy_rev/1e6:.1f}M", "+8.2% vs LY")

    st.markdown("---")
    st.markdown("### 📋 What's in this dashboard")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
**📦 Order Pipeline**
- Total open orders by stage
- Live pipeline view ($ and units)
- Backordered flags

**⏱️ Aging & SLA Tracking**
- Order aging buckets (0–3, 4–7, 8–14, 15+ days)
- SLA promise vs. current status
- Late order identification

**🏪 Store Details**
- Stores opened by rep and region
- Per-store performance
- Activity status
""")
    with col_b:
        st.markdown("""
**📊 Financial Dashboard**
- Monthly executive recap — shipped orders
- Revenue vs. last year
- Key KPIs: units, AOV, orders

**🏆 Scoreboard & Reps**
- Top reps by revenue
- Top regions
- Top performing stores
- Stores created by rep
""")

    st.markdown("---")
    st.info("💡 **Brian (Supply Chain):** Use the Order Pipeline and Aging & SLA pages to monitor production flow. Flag aging orders and backlogs early. The Aging report is your daily ops pulse.")
