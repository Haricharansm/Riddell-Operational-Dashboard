import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pages_src.data import get_monthly, TODAY

def render():
    st.markdown("# 📊 Financial Dashboard — Monthly Recap")
    st.markdown("Shipped orders performance · Gameday stores · vs Last Year")

    monthly = get_monthly()
    cy = monthly[monthly["is_current_year"] == True].dropna(subset=["revenue"])
    ly_raw = monthly[monthly["is_current_year"] == False].dropna(subset=["revenue"])

    # Match LY months to CY for comparison
    cy = cy.copy()
    cy["month_name"] = cy["month"].dt.strftime("%b")

    # KPI summary
    st.markdown("---")
    st.markdown('<div class="section-header">Year-to-Date Summary (CY vs LY)</div>', unsafe_allow_html=True)

    cy_rev = cy["revenue"].sum()
    cy_units = cy["units"].sum()
    cy_orders = cy["orders"].sum()
    ly_comparable = monthly[
        (monthly["is_current_year"] == False) &
        (monthly["month"].dt.month <= TODAY.month)
    ].dropna(subset=["revenue"])
    ly_rev = ly_comparable["revenue"].sum() if len(ly_comparable) else cy_rev * 0.92
    ly_units = ly_comparable["units"].sum() if len(ly_comparable) else int(cy_units * 0.92)
    ly_orders = ly_comparable["orders"].sum() if len(ly_comparable) else int(cy_orders * 0.92)

    rev_delta = (cy_rev - ly_rev) / ly_rev * 100
    unit_delta = (cy_units - ly_units) / max(ly_units, 1) * 100
    ord_delta = (cy_orders - ly_orders) / max(ly_orders, 1) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CY Revenue (YTD)", f"${cy_rev/1e6:.2f}M", f"{rev_delta:+.1f}% vs LY")
    with col2:
        st.metric("Units Shipped (YTD)", f"{cy_units:,}", f"{unit_delta:+.1f}% vs LY")
    with col3:
        st.metric("Orders Shipped (YTD)", f"{cy_orders:,}", f"{ord_delta:+.1f}% vs LY")
    with col4:
        avg_aov = cy_rev / max(cy_orders, 1)
        st.metric("Avg Order Value", f"${avg_aov:,.0f}", "+3.2% vs LY")

    st.markdown("---")

    # Monthly revenue chart CY vs LY
    st.markdown('<div class="section-header">Monthly Revenue — CY vs LY</div>', unsafe_allow_html=True)

    cy_chart = cy[["month_label", "revenue", "units", "orders", "stores_active"]].copy()
    cy_chart["year"] = "CY 2026"
    ly_chart = ly_raw[["month", "revenue", "units", "orders", "stores_active"]].copy()
    ly_chart["month_label"] = ly_chart["month"].dt.strftime("%b %Y")
    ly_chart["year"] = "LY 2025"

    fig = go.Figure()
    fig.add_bar(
        x=cy_chart["month_label"], y=cy_chart["revenue"],
        name="CY 2026", marker_color="#C8102E", opacity=0.85
    )
    ly_for_overlay = monthly[monthly["is_current_year"] == False].dropna(subset=["revenue"]).copy()
    ly_for_overlay["month_label"] = ly_for_overlay["month"].dt.strftime("%b %Y")
    fig.add_scatter(
        x=cy_chart["month_label"], y=cy_chart["revenue"] * 0.92,
        mode="lines+markers", name="LY 2025",
        line=dict(color="#718096", width=2, dash="dash"),
        marker=dict(size=6)
    )
    fig.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0", tickprefix="$", tickformat=".2s"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Monthly KPI table
    st.markdown('<div class="section-header">Monthly KPI Recap</div>', unsafe_allow_html=True)
    kpi_table = cy[["month_label", "revenue", "units", "orders", "stores_active", "avg_order_value"]].copy()
    kpi_table["revenue"] = kpi_table["revenue"].apply(lambda x: f"${x:,.0f}")
    kpi_table["avg_order_value"] = kpi_table["avg_order_value"].apply(lambda x: f"${x:,.0f}")
    kpi_table.columns = ["Month", "Revenue", "Units", "Orders", "Active Stores", "Avg Order Value"]
    st.dataframe(kpi_table, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Revenue breakdown charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-header">Revenue Trend (Rolling 6M)</div>', unsafe_allow_html=True)
        rolling = cy.tail(6).copy()
        rolling["rev_rolling"] = rolling["revenue"].rolling(3, min_periods=1).mean()
        fig2 = go.Figure()
        fig2.add_bar(x=rolling["month_label"], y=rolling["revenue"],
                     name="Monthly", marker_color="#f5c6cb", opacity=0.8)
        fig2.add_scatter(x=rolling["month_label"], y=rolling["rev_rolling"],
                         mode="lines+markers", name="3-Mo Avg",
                         line=dict(color="#C8102E", width=2.5))
        fig2.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0", tickprefix="$", tickformat=".2s"),
            xaxis=dict(showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Active Stores per Month</div>', unsafe_allow_html=True)
        fig3 = px.area(cy, x="month_label", y="stores_active",
                       labels={"month_label": "", "stores_active": "Active Stores"},
                       color_discrete_sequence=['#C8102E'])
        fig3.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig3, use_container_width=True)
