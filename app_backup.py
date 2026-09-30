import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.calculator import build_budget, budget_summary, daily_breakdown
from src.exporter import make_csv, make_json

st.set_page_config(
    page_title="Trip Budget Calculator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main-title {font-size: 2.5rem;font-weight:800;margin-bottom:0.2rem}
.subtitle {color:#64748b;margin-bottom:1.5rem}
.metric-card {padding:18px;border-radius:16px;background:#f8fafc;border:1px solid #e2e8f0}
.section {font-size:1.25rem;font-weight:700;margin-top:1rem}
</style>
""", unsafe_allow_html=True)

if "budget_rows" not in st.session_state:
    st.session_state.budget_rows = []

st.markdown('<div class="main-title">✈️ Trip Budget Calculator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Plan, analyze, and export a realistic travel budget in minutes.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Trip Setup")
    trip_name = st.text_input("Trip name", "My Dream Trip")
    destination = st.text_input("Destination", "Hyderabad")
    travelers = st.number_input("Travelers", 1, 50, 2)
    start_date = st.date_input("Start date", date.today())
    end_date = st.date_input("End date", start_date + timedelta(days=4))
    currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP", "AED", "SGD", "JPY"])
    contingency = st.slider("Emergency / contingency (%)", 0, 30, 10)

    if end_date < start_date:
        st.error("End date must be on or after start date.")
    else:
        st.success(f"{(end_date - start_date).days + 1} calendar days")

tabs = st.tabs(["📊 Budget Planner", "📅 Daily Plan", "📈 Analytics", "💾 Export"])

with tabs[0]:
    st.subheader("Budget Planner")
    st.caption("Enter total category costs for the whole trip. Per-person figures are calculated automatically.")

    defaults = {
        "Transportation": 5000.0,
        "Accommodation": 8000.0,
        "Food & Dining": 5000.0,
        "Activities & Tickets": 3000.0,
        "Shopping": 2000.0,
        "Travel Insurance": 1000.0,
        "Other": 1500.0,
    }

    categories = list(defaults.keys())
    cols = st.columns(2)
    inputs = {}
    for i, category in enumerate(categories):
        with cols[i % 2]:
            inputs[category] = st.number_input(
                category,
                min_value=0.0,
                value=defaults[category],
                step=500.0,
                key=f"cost_{category}",
            )

    budget = build_budget(inputs, travelers, contingency)
    summary = budget_summary(budget)

    st.markdown("### 💰 Trip Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Base Cost", f"{currency} {summary['base_total']:,.2f}")
    m2.metric("Contingency", f"{currency} {summary['contingency']:,.2f}")
    m3.metric("Grand Total", f"{currency} {summary['grand_total']:,.2f}")
    m4.metric("Per Traveler", f"{currency} {summary['per_person']:,.2f}")

    st.divider()
    df = pd.DataFrame(budget)
    df["Share"] = (df["Amount"] / max(summary["base_total"], 1) * 100).round(1)
    st.dataframe(
        df.rename(columns={"Category": "Category", "Amount": "Total", "PerPerson": "Per Traveler"}),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        f"Your estimated daily spend is {currency} "
        f"{summary['grand_total'] / max((end_date - start_date).days + 1, 1):,.2f} "
        f"for the entire group."
    )

with tabs[1]:
    st.subheader("📅 Daily Budget Plan")
    days = max((end_date - start_date).days + 1, 1)
    total = budget_summary(build_budget(inputs, travelers, contingency))["grand_total"]
    daily = daily_breakdown(inputs, days, contingency)

    daily_df = pd.DataFrame(daily)
    daily_df["Date"] = [
        start_date + timedelta(days=i) for i in range(days)
    ]
    daily_df["Date"] = daily_df["Date"].astype(str)
    st.dataframe(daily_df, use_container_width=True, hide_index=True)

    st.markdown("### Day-by-day allocation")
    fig = px.bar(
        daily_df,
        x="Date",
        y="Total",
        color="Category",
        title="Estimated Daily Spending",
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("📈 Budget Analytics")
    budget = build_budget(inputs, travelers, contingency)
    analytics_df = pd.DataFrame(budget)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(
            analytics_df,
            names="Category",
            values="Amount",
            hole=0.45,
            title="Base Budget Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(
            analytics_df.sort_values("Amount", ascending=True),
            x="Amount",
            y="Category",
            orientation="h",
            title="Cost by Category",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Budget Insights")
    top = analytics_df.sort_values("Amount", ascending=False).iloc[0]
    st.write(
        f"**Largest expense:** {top['Category']} at {currency} {top['Amount']:,.2f} "
        f"({top['Amount'] / max(analytics_df['Amount'].sum(), 1) * 100:.1f}% of base budget)."
    )
    st.write(
        f"**Group size:** {travelers} traveler(s). "
        f"**Contingency:** {contingency}%."
    )

with tabs[3]:
    st.subheader("💾 Export Your Trip Plan")
    budget = build_budget(inputs, travelers, contingency)
    summary = budget_summary(budget)

    export_data = {
        "trip": {
            "name": trip_name,
            "destination": destination,
            "travelers": travelers,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "currency": currency,
            "contingency_percent": contingency,
        },
        "summary": summary,
        "categories": budget,
    }

    csv_bytes = make_csv(budget)
    json_bytes = make_json(export_data)

    st.download_button(
        "⬇️ Download Budget CSV",
        data=csv_bytes,
        file_name=f"{trip_name.replace(' ', '_')}_budget.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "⬇️ Download Trip Plan JSON",
        data=json_bytes,
        file_name=f"{trip_name.replace(' ', '_')}_trip.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown("### Preview")
    st.json(export_data)
