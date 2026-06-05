import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pages_src.data import get_orders, TODAY

AGING_COLORS = {
    "0–3 days": "#68d391",
    "4–7 days": "#f6e05e",
    "8–14 days": "#f6ad55",
    "15+ days": "#fc8181",
}

def age_bucket(days):
    if days <= 3: return "0–3 days"
    elif days <= 7: return "4–7 days"
    elif days <= 14: return "8–14 days"
    else: return "15+ days"

def render():
    st.markdown("# ⏱️ Aging Report & SLA Tracking")
    st.info("🔧 **Brian (Supply Chain):** This is your daily ops view. Watch the 15+ bucket and late SLA orders closely. Backordered items will always show in the 15+ aging tier.")

    orders = get_orders()
    orders = orders.copy()
    orders["age_bucket"] = orders["age_days"].apply(age_bucket)
    BUCKET_ORDER = ["0–3 days", "4–7 days", "8–14 days", "15+ days"]

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        regions = ["All"] + sorted(orders["region"].unique().tolist())
        region_filter = st.selectbox("Region", regions)
    with col2:
        stage_filter = st.selectbox("Stage", ["All"] + list(orders["stage"].unique()))

    df = orders.copy()
    if region_filter != "All":
        df = df[df["region"] == region_filter]
    if stage_filter != "All":
        df = df[df["stage"] == stage_filter]

    # ── AGING SECTION ──────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Order Aging Buckets</div>', unsafe_allow_html=True)

    aging = df.groupby("age_bucket").agg(
        Orders=("order_id", "count"),
        Units=("units", "sum"),
        Value=("order_value", "sum")
    ).reindex(BUCKET_ORDER).reset_index()

    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    bucket_colors = ["#38a169", "#d69e2e", "#dd6b20", "#e53e3e"]
    for i, row in aging.iterrows():
        with cols[i]:
            st.markdown(f"""
            <div style="background:{bucket_colors[i]}15; border:1px solid {bucket_colors[i]}40;
                        border-radius:10px; padding:16px 20px; text-align:center;">
                <div style="font-size:11px;font-weight:700;color:{bucket_colors[i]};text-transform:uppercase;letter-spacing:0.05em">{row['age_bucket']}</div>
                <div style="font-size:32px;font-weight:800;color:{bucket_colors[i]};margin:6px 0">{int(row['Orders']) if not pd.isna(row['Orders']) else 0}</div>
                <div style="font-size:12px;color:#718096;">orders</div>
                <div style="font-size:14px;font-weight:600;color:#4a5568;margin-top:4px">${int(row['Value'])/1e3:.0f}K</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        fig = px.bar(
            aging, x="age_bucket", y="Orders",
            color="age_bucket",
            color_discrete_map=AGING_COLORS,
            text="Orders",
            labels={"age_bucket": "Aging Bucket", "Orders": "# Orders"},
            category_orders={"age_bucket": BUCKET_ORDER}
        )
        fig.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=10),
            showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"), xaxis=dict(showgrid=False)
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        fig2 = px.pie(
            aging, values="Value", names="age_bucket",
            color="age_bucket",
            color_discrete_map=AGING_COLORS,
            hole=0.5,
            category_orders={"age_bucket": BUCKET_ORDER},
            title="Value at Risk by Bucket"
        )
        fig2.update_layout(height=280, margin=dict(l=0, r=0, t=30, b=10))
        fig2.update_traces(textinfo="percent", textposition="inside")
        st.plotly_chart(fig2, use_container_width=True)

    # Detailed aging table
    with st.expander("📋 Aging Detail by Stage"):
        pivot = df.groupby(["stage", "age_bucket"])["order_id"].count().unstack(fill_value=0)
        pivot = pivot.reindex(columns=[c for c in BUCKET_ORDER if c in pivot.columns])
        st.dataframe(pivot, use_container_width=True)

    # ── SLA SECTION ──────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">SLA / Promise Tracking</div>', unsafe_allow_html=True)

    total = len(df)
    at_risk = df[df["sla_at_risk"] == True]
    late = df[df["late"] == True]
    on_track = df[(df["sla_at_risk"] == False) & (df["late"] == False)]
    pct_at_risk = len(at_risk) / total * 100 if total else 0
    pct_late = len(late) / total * 100 if total else 0
    pct_on_track = len(on_track) / total * 100 if total else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("On Track", f"{len(on_track):,}", f"{pct_on_track:.0f}% of orders")
    with col2:
        st.metric("At Risk (< 3 days to SLA)", f"{len(at_risk):,}", f"{pct_at_risk:.0f}% at risk", delta_color="inverse")
    with col3:
        st.metric("Late Orders", f"{len(late):,}", f"${late['order_value'].sum()/1e3:.0f}K", delta_color="inverse")
    with col4:
        st.metric("Late Order Value", f"${late['order_value'].sum()/1e3:.0f}K",
                  f"{pct_late:.0f}% of pipeline", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # SLA gauge
    col_gauge, col_bar = st.columns([1, 1.5])
    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(pct_on_track, 1),
            title={"text": "% Orders On Track", "font": {"size": 14}},
            number={"suffix": "%", "font": {"size": 36}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#38a169"},
                "steps": [
                    {"range": [0, 60], "color": "#fed7d7"},
                    {"range": [60, 80], "color": "#fefcbf"},
                    {"range": [80, 100], "color": "#c6f6d5"},
                ],
                "threshold": {"line": {"color": "#8B0A1E", "width": 3}, "thickness": 0.75, "value": 85}
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor="white")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_bar:
        sla_region = df.groupby("region").apply(lambda x: pd.Series({
            "On Track": len(x[(x["sla_at_risk"]==False) & (x["late"]==False)]),
            "At Risk": len(x[x["sla_at_risk"]==True]),
            "Late": len(x[x["late"]==True]),
        })).reset_index()
        sla_melt = sla_region.melt(id_vars="region", var_name="Status", value_name="Orders")
        fig_r = px.bar(
            sla_melt, x="region", y="Orders", color="Status",
            color_discrete_map={"On Track": "#68d391", "At Risk": "#f6ad55", "Late": "#fc8181"},
            barmode="stack",
            labels={"region": "Region"}
        )
        fig_r.update_layout(
            height=260, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"), xaxis=dict(showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_r, use_container_width=True)

    # Late orders table
    st.markdown('<div class="section-header">Late Orders — Full Detail</div>', unsafe_allow_html=True)
    if len(late) > 0:
        late_show = late[["order_id", "store_id", "rep", "region", "model", "units",
                           "order_value", "stage", "received_date", "promised_ship_date", "age_days"]].copy()
        late_show["order_value"] = late_show["order_value"].apply(lambda x: f"${x:,.0f}")
        late_show["received_date"] = late_show["received_date"].dt.strftime("%b %d")
        late_show["promised_ship_date"] = late_show["promised_ship_date"].dt.strftime("%b %d")
        late_show = late_show.sort_values("age_days", ascending=False)
        late_show.columns = ["Order ID", "Store", "Rep", "Region", "Model", "Units",
                              "Value", "Stage", "Received", "Promised Ship", "Age (days)"]
        st.dataframe(late_show, use_container_width=True, hide_index=True)
    else:
        st.success("No late orders! All orders are on track.")
