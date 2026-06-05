import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pages_src.data import get_orders, STAGES

STAGE_COLORS = {
    "Received": "#f5c6cb",
    "In Production": "#f6ad55",
    "In Decoration": "#b794f4",
    "Ready to Ship": "#68d391",
    "Backordered": "#fc8181",
}

def render():
    st.markdown("# 📦 Order Pipeline View")
    orders = get_orders()

    # Filters
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            regions = ["All"] + sorted(orders["region"].unique().tolist())
            region_filter = st.selectbox("Region", regions)
        with col2:
            reps = ["All"] + sorted(orders["rep"].unique().tolist())
            rep_filter = st.selectbox("Rep", reps)
        with col3:
            models = ["All"] + sorted(orders["model"].unique().tolist())
            model_filter = st.selectbox("Model", models)

    df = orders.copy()
    if region_filter != "All":
        df = df[df["region"] == region_filter]
    if rep_filter != "All":
        df = df[df["rep"] == rep_filter]
    if model_filter != "All":
        df = df[df["model"] == model_filter]

    # Summary metrics
    st.markdown('<div class="section-header">Pipeline Summary</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Open Orders", f"{len(df):,}", f"${df['order_value'].sum()/1e6:.2f}M")
    with col2:
        backorder = df[df["stage"] == "Backordered"]
        st.metric("Backordered", f"{len(backorder):,}", f"${backorder['order_value'].sum()/1e3:.0f}K", delta_color="inverse")
    with col3:
        rts = df[df["stage"] == "Ready to Ship"]
        st.metric("Ready to Ship", f"{len(rts):,}", f"${rts['order_value'].sum()/1e3:.0f}K")
    with col4:
        in_prod = df[df["stage"].isin(["In Production", "In Decoration"])]
        st.metric("In Production / Decoration", f"{len(in_prod):,}", f"${in_prod['order_value'].sum()/1e6:.2f}M")

    st.markdown("---")

    # Stage breakdown
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="section-header">Orders by Stage</div>', unsafe_allow_html=True)
        stage_df = df.groupby("stage").agg(
            Orders=("order_id", "count"),
            Units=("units", "sum"),
            Value=("order_value", "sum")
        ).reindex(STAGES).reset_index()
        stage_df.columns = ["Stage", "Orders", "Units", "Value ($)"]
        stage_df["Value ($)"] = stage_df["Value ($)"].apply(lambda x: f"${x:,.0f}")

        fig = go.Figure(go.Bar(
            x=stage_df["Orders"],
            y=stage_df["Stage"],
            orientation="h",
            marker_color=[STAGE_COLORS.get(s, "#cbd5e0") for s in stage_df["Stage"]],
            text=stage_df["Orders"],
            textposition="outside",
        ))
        fig.update_layout(
            height=280, margin=dict(l=0, r=40, t=10, b=10),
            xaxis_title="", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Value by Stage ($)</div>', unsafe_allow_html=True)
        stage_val = df.groupby("stage")["order_value"].sum().reindex(STAGES).reset_index()
        fig2 = px.pie(
            stage_val, values="order_value", names="stage",
            color="stage",
            color_discrete_map=STAGE_COLORS,
            hole=0.45
        )
        fig2.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="v", x=1, y=0.5)
        )
        fig2.update_traces(textinfo="percent+label", textposition="inside")
        st.plotly_chart(fig2, use_container_width=True)

    # Stage table
    st.markdown('<div class="section-header">Stage Detail Table</div>', unsafe_allow_html=True)
    stage_summary = df.groupby("stage").agg(
        Orders=("order_id", "count"),
        Units=("units", "sum"),
        Total_Value=("order_value", "sum"),
        Avg_Order_Value=("order_value", "mean"),
    ).reindex(STAGES).reset_index()
    stage_summary["Total_Value"] = stage_summary["Total_Value"].apply(lambda x: f"${x:,.0f}")
    stage_summary["Avg_Order_Value"] = stage_summary["Avg_Order_Value"].apply(lambda x: f"${x:,.0f}")
    stage_summary.columns = ["Stage", "Orders", "Units", "Total Value", "Avg Order Value"]
    st.dataframe(stage_summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Orders by Region & Stage</div>', unsafe_allow_html=True)
    region_stage = df.groupby(["region", "stage"])["order_value"].sum().reset_index()
    fig3 = px.bar(
        region_stage, x="region", y="order_value", color="stage",
        color_discrete_map=STAGE_COLORS,
        labels={"order_value": "Order Value ($)", "region": "Region", "stage": "Stage"},
        barmode="stack"
    )
    fig3.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"), xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Raw order table (collapsed)
    with st.expander("📋 View all orders"):
        show = df[["order_id", "store_id", "rep", "region", "model", "units", "order_value", "stage", "received_date", "promised_ship_date", "late", "sla_at_risk"]].copy()
        show["order_value"] = show["order_value"].apply(lambda x: f"${x:,.0f}")
        show["received_date"] = show["received_date"].dt.strftime("%b %d, %Y")
        show["promised_ship_date"] = show["promised_ship_date"].dt.strftime("%b %d, %Y")
        st.dataframe(show, use_container_width=True, hide_index=True)
