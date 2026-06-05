import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pages_src.data import get_rep_performance, get_orders, get_stores

MEDAL = ["🥇", "🥈", "🥉"]

def render():
    st.markdown("# 🏆 Scoreboard & Rep Performance")

    reps = get_rep_performance()
    orders = get_orders()
    stores = get_stores()

    # ── TOP REPS ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Top Reps — Revenue</div>', unsafe_allow_html=True)

    top3 = reps.head(3)
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    podium_colors = ["#C8102E", "#C0C0C0", "#CD7F32"]
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style="border:2px solid {podium_colors[i]}; border-radius:12px;
                        padding:20px; text-align:center; background:{podium_colors[i]}10;">
                <div style="font-size:32px">{MEDAL[i]}</div>
                <div style="font-size:16px;font-weight:700;color:#1a202c;margin:6px 0">{row['rep']}</div>
                <div style="font-size:22px;font-weight:800;color:{podium_colors[i]}">${row['total_revenue']/1e3:.0f}K</div>
                <div style="font-size:12px;color:#718096;margin-top:4px">{int(row['stores_created'])} stores · {int(row['total_orders'])} orders</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Full rep leaderboard
    fig = go.Figure(go.Bar(
        y=reps["rep"][::-1],
        x=reps["total_revenue"][::-1],
        orientation="h",
        marker=dict(
            color=reps["total_revenue"][::-1],
            colorscale=[[0,'#f5c6cb'],[1,'#8B0A1E']],
        ),
        text=reps["total_revenue"][::-1].apply(lambda x: f"${x/1e3:.0f}K"),
        textposition="outside"
    ))
    fig.update_layout(
        height=340, margin=dict(l=0, r=80, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── TOP REGIONS ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Top Regions</div>', unsafe_allow_html=True)

    region_perf = orders.groupby("region").agg(
        Revenue=("order_value", "sum"),
        Units=("units", "sum"),
        Orders=("order_id", "count"),
        Stores=("store_id", "nunique"),
    ).reset_index().sort_values("Revenue", ascending=False)

    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        fig_reg = px.bar(
            region_perf, x="region", y="Revenue",
            color="Revenue", color_continuous_scale=[[0,'#f5c6cb'],[1,'#8B0A1E']],
            text=region_perf["Revenue"].apply(lambda x: f"${x/1e3:.0f}K"),
            labels={"region": "Region", "Revenue": "Revenue ($)"}
        )
        fig_reg.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#f0f0f0", tickprefix="$", tickformat=".2s"),
            coloraxis_showscale=False
        )
        fig_reg.update_traces(textposition="outside")
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_right:
        st.dataframe(
            region_perf.assign(
                Revenue=region_perf["Revenue"].apply(lambda x: f"${x:,.0f}")
            ).rename(columns={"region": "Region"}),
            use_container_width=True, hide_index=True
        )

    # ── TOP STORES ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Top 10 Stores by Revenue</div>', unsafe_allow_html=True)

    top_stores = stores.sort_values("total_revenue", ascending=False).head(10).copy()
    top_stores["rank"] = range(1, 11)

    col_chart, col_table = st.columns([1.3, 1])
    with col_chart:
        fig_s = px.bar(
            top_stores, x="total_revenue", y="store_name",
            orientation="h",
            color="total_revenue", color_continuous_scale=[[0,'#f5c6cb'],[1,'#8B0A1E']],
            text=top_stores["total_revenue"].apply(lambda x: f"${x/1e3:.0f}K"),
            labels={"store_name": "", "total_revenue": "Revenue ($)"}
        )
        fig_s.update_layout(
            height=360, margin=dict(l=0, r=80, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False),
            coloraxis_showscale=False
        )
        fig_s.update_traces(textposition="outside")
        st.plotly_chart(fig_s, use_container_width=True)

    with col_table:
        show = top_stores[["rank", "store_name", "rep", "region", "total_orders", "total_revenue"]].copy()
        show["total_revenue"] = show["total_revenue"].apply(lambda x: f"${x:,.0f}")
        show.columns = ["#", "Store", "Rep", "Region", "Orders", "Revenue"]
        st.dataframe(show, use_container_width=True, hide_index=True)

    # ── STORES CREATED BY REP ──────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Stores Created by Rep</div>', unsafe_allow_html=True)

    rep_stores = stores.groupby("rep").agg(
        Stores_Created=("store_id", "count"),
        Active=("active", "sum"),
        Total_Revenue=("total_revenue", "sum"),
    ).reset_index().sort_values("Stores_Created", ascending=False)
    rep_stores["Inactive"] = rep_stores["Stores_Created"] - rep_stores["Active"]

    fig_rs = go.Figure()
    fig_rs.add_bar(y=rep_stores["rep"], x=rep_stores["Active"],
                   orientation="h", name="Active", marker_color="#68d391")
    fig_rs.add_bar(y=rep_stores["rep"], x=rep_stores["Inactive"],
                   orientation="h", name="Inactive", marker_color="#fc8181")
    fig_rs.update_layout(
        barmode="stack", height=320,
        margin=dict(l=0, r=0, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_rs, use_container_width=True)

    # Full rep detail table
    st.markdown('<div class="section-header">Full Rep Performance Table</div>', unsafe_allow_html=True)
    rep_table = reps.copy()
    rep_table["total_revenue"] = rep_table["total_revenue"].apply(lambda x: f"${x:,.0f}")
    rep_table["avg_order_value"] = rep_table["avg_order_value"].apply(lambda x: f"${x:,.0f}")
    rep_table.columns = ["Rep", "Revenue", "Units", "Orders", "Stores Created", "Regions", "Avg Order Value", "Rank"]
    rep_table = rep_table[["Rank", "Rep", "Revenue", "Units", "Orders", "Stores Created", "Avg Order Value", "Regions"]]
    st.dataframe(rep_table, use_container_width=True, hide_index=True)
