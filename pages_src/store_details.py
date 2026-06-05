import streamlit as st
import plotly.express as px
import pandas as pd
from pages_src.data import get_stores, get_orders, TODAY
from datetime import timedelta

def render():
    st.markdown("# 🏪 Store Details")

    stores = get_stores()
    orders = get_orders()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        regions = ["All"] + sorted(stores["region"].unique().tolist())
        region_filter = st.selectbox("Region", regions)
    with col2:
        reps = ["All"] + sorted(stores["rep"].unique().tolist())
        rep_filter = st.selectbox("Rep", reps)
    with col3:
        status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])

    df = stores.copy()
    if region_filter != "All":
        df = df[df["region"] == region_filter]
    if rep_filter != "All":
        df = df[df["rep"] == rep_filter]
    if status_filter == "Active":
        df = df[df["active"] == True]
    elif status_filter == "Inactive":
        df = df[df["active"] == False]

    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stores Created", f"{len(df):,}")
    with col2:
        st.metric("Active Stores", f"{df['active'].sum():,}", f"{df['active'].mean()*100:.0f}% active")
    with col3:
        st.metric("Total Revenue", f"${df['total_revenue'].sum()/1e6:.2f}M")
    with col4:
        avg_rev = df['total_revenue'].mean()
        st.metric("Avg Revenue / Store", f"${avg_rev:,.0f}")

    st.markdown("---")

    # Stores opened over time
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown('<div class="section-header">Stores Opened Over Time</div>', unsafe_allow_html=True)
        df_time = df.copy()
        df_time["open_month"] = df_time["open_date"].dt.to_period("M").dt.to_timestamp()
        monthly_opens = df_time.groupby("open_month")["store_id"].count().reset_index()
        monthly_opens.columns = ["Month", "New Stores"]
        monthly_opens["Cumulative"] = monthly_opens["New Stores"].cumsum()

        fig = px.bar(monthly_opens, x="Month", y="New Stores",
                     labels={"Month": "", "New Stores": "Stores Opened"},
                     color_discrete_sequence=['#C8102E'])
        fig.add_scatter(x=monthly_opens["Month"], y=monthly_opens["Cumulative"],
                        mode="lines+markers", name="Cumulative",
                        line=dict(color="#8B0A1E", width=2), yaxis="y2")
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"),
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Stores by Region</div>', unsafe_allow_html=True)
        region_counts = df.groupby("region").agg(
            Stores=("store_id", "count"),
            Revenue=("total_revenue", "sum")
        ).reset_index()
        fig2 = px.bar(region_counts, x="Stores", y="region", orientation="h",
                      color="Revenue", color_continuous_scale=[[0,'#f5c6cb'],[1,'#8B0A1E']],
                      labels={"region": "", "Stores": "# Stores"})
        fig2.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Stores created by rep
    st.markdown('<div class="section-header">Stores Created by Rep</div>', unsafe_allow_html=True)
    rep_stores = df.groupby("rep").agg(
        Stores=("store_id", "count"),
        Active=("active", "sum"),
        Revenue=("total_revenue", "sum"),
        Avg_Rev=("total_revenue", "mean"),
    ).reset_index().sort_values("Stores", ascending=False)

    fig3 = px.bar(rep_stores, x="rep", y="Stores",
                  color="Revenue", color_continuous_scale=[[0,'#f5c6cb'],[1,'#8B0A1E']],
                  text="Stores",
                  labels={"rep": "Sales Rep", "Stores": "Stores Created"})
    fig3.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, tickangle=-20),
        yaxis=dict(gridcolor="#f0f0f0"),
        coloraxis_showscale=False
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    # Store detail table
    st.markdown('<div class="section-header">Store Performance Table</div>', unsafe_allow_html=True)
    show = df[["store_id", "store_name", "rep", "region", "open_date",
               "total_orders", "total_units", "total_revenue", "active"]].copy()
    show["total_revenue"] = show["total_revenue"].apply(lambda x: f"${x:,.0f}")
    show["open_date"] = show["open_date"].dt.strftime("%b %d, %Y")
    show["active"] = show["active"].apply(lambda x: "✅ Active" if x else "⛔ Inactive")
    show.columns = ["Store ID", "Store Name", "Rep", "Region", "Opened",
                    "Orders", "Units", "Revenue", "Status"]
    show = show.sort_values("Revenue", ascending=False)

    st.dataframe(show, use_container_width=True, hide_index=True)
