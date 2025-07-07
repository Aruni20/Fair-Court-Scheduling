# dashboard/streamlit_app.py
"""
Streamlit dashboard for court scheduling analytics.
Displays 4 KPIs and 4 EDA/statistical plots for system performance monitoring.
"""

import streamlit as st
import pandas as pd
from clickhouse_driver import Client
from config.config import CLICKHOUSE_HOST, CLICKHOUSE_DB
import plotly.express as px
from datetime import datetime, timedelta

st.title("Court Scheduling Analytics Dashboard")

def fetch_kpis():
    """Fetch latest KPIs from ClickHouse."""
    try:
        client = Client(host=CLICKHOUSE_HOST, database=CLICKHOUSE_DB)
        result = client.execute("SELECT * FROM kpi_metrics ORDER BY date DESC LIMIT 1")
        return result[0] if result else []
    except Exception as e:
        st.error(f"Error fetching KPIs: {e}")
        return []

def fetch_court_distribution():
    """Fetch case count per court."""
    try:
        client = Client(host=CLICKHOUSE_HOST, database=CLICKHOUSE_DB)
        result = client.execute("SELECT court_id, COUNT(*) as case_count FROM schedules GROUP BY court_id")
        return pd.DataFrame(result, columns=['court_id', 'case_count'])
    except Exception as e:
        st.error(f"Error fetching court distribution: {e}")
        return pd.DataFrame()

def fetch_judge_workload_trend():
    """Fetch judge workload over time."""
    try:
        client = Client(host=CLICKHOUSE_HOST, database=CLICKHOUSE_DB)
        result = client.execute(
            "SELECT scheduled_date, judge_id, COUNT(*) as case_count "
            "FROM schedules "
            "WHERE scheduled_date >= %s "
            "GROUP BY scheduled_date, judge_id "
            "ORDER BY scheduled_date",
            [(datetime.now() - timedelta(days=30)).date()]
        )
        return pd.DataFrame(result, columns=['scheduled_date', 'judge_id', 'case_count'])
    except Exception as e:
        st.error(f"Error fetching judge workload: {e}")
        return pd.DataFrame()

def fetch_delay_by_case_type():
    """Fetch delay by case type."""
    try:
        client = Client(host=CLICKHOUSE_HOST, database=CLICKHOUSE_DB)
        result = client.execute(
            "SELECT c.case_type_id, DATEDIFF('day', c.filing_date, s.scheduled_date) as delay_days "
            "FROM cases c JOIN schedules s ON c.case_id = s.case_id "
            "WHERE s.scheduled_date IS NOT NULL"
        )
        return pd.DataFrame(result, columns=['case_type_id', 'delay_days'])
    except Exception as e:
        st.error(f"Error fetching delay data: {e}")
        return pd.DataFrame()

def fetch_hearing_outcomes():
    """Fetch hearing outcomes distribution."""
    try:
        client = Client(host=CLICKHOUSE_HOST, database=CLICKHOUSE_DB)
        result = client.execute(
            "SELECT outcome, COUNT(*) as count "
            "FROM schedules "
            "WHERE outcome IS NOT NULL "
            "GROUP BY outcome"
        )
        return pd.DataFrame(result, columns=['outcome', 'count'])
    except Exception as e:
        st.error(f"Error fetching hearing outcomes: {e}")
        return pd.DataFrame()

# Display KPIs
st.header("Key Performance Indicators")
kpis = fetch_kpis()

if kpis:
    st.subheader(f"Latest KPIs ({kpis[0]})")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fairness Index", f"{kpis[1]:.2f}")
    col2.metric("Undertrial % (7 days)", f"{kpis[2]:.2f}%")
    col3.metric("Avg Delay (days)", f"{kpis[3]:.2f}")
    col4.metric("Adjournment Rate", f"{kpis[4]:.2f}%")
else:
    st.warning("No KPI data available.")

# EDA and Statistical Plots
st.header("System Performance Analytics")

# Plot 1: Case Distribution by Court
st.subheader("Case Distribution by Court")
court_dist = fetch_court_distribution()
if not court_dist.empty:
    fig1 = px.bar(court_dist, x='court_id', y='case_count', 
                  title="Number of Cases per Court",
                  labels={'court_id': 'Court ID', 'case_count': 'Number of Cases'})
    st.plotly_chart(fig1)
else:
    st.warning("No court distribution data available.")

# Plot 2: Judge Workload Trend
st.subheader("Judge Workload Trend (Last 30 Days)")
workload = fetch_judge_workload_trend()
if not workload.empty:
    fig2 = px.line(workload, x='scheduled_date', y='case_count', color='judge_id',
                   title="Judge Workload Over Time",
                   labels={'scheduled_date': 'Date', 'case_count': 'Number of Cases', 'judge_id': 'Judge ID'})
    st.plotly_chart(fig2)
else:
    st.warning("No workload trend data available.")

# Plot 3: Delay by Case Type
st.subheader("Delay by Case Type")
delay_data = fetch_delay_by_case_type()
if not delay_data.empty:
    fig3 = px.box(delay_data, x='case_type_id', y='delay_days',
                  title="Delay Distribution by Case Type",
                  labels={'case_type_id': 'Case Type ID', 'delay_days': 'Delay (Days)'})
    st.plotly_chart(fig3)
else:
    st.warning("No delay data available.")

# Plot 4: Hearing Outcomes
st.subheader("Hearing Outcomes Distribution")
outcomes = fetch_hearing_outcomes()
if not outcomes.empty:
    fig4 = px.pie(outcomes, names='outcome', values='count',
                  title="Hearing Outcomes")
    st.plotly_chart(fig4)
else:
    st.warning("No hearing outcomes data available.")