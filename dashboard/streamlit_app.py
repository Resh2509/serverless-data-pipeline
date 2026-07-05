import os
import sys

import pandas as pd
import requests
import streamlit as st

# Add project root to Python path so `config.py` can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import DASHBOARD_API_BASE

st.set_page_config(page_title="Serverless Data Pipeline Dashboard", layout="wide")
st.title("Serverless Data Pipeline Dashboard")

def fetch_json(endpoint):
    response = requests.get(f"{DASHBOARD_API_BASE}{endpoint}", timeout=30)
    response.raise_for_status()
    return response.json()

try:
    metrics = fetch_json("/metrics")
    pipeline_health = fetch_json("/pipeline-health")
    posts_data = fetch_json("/posts-per-user")
    pipeline_runs = fetch_json("/pipeline-runs?limit=10")
except Exception as e:
    st.error(f"Failed to load API data: {e}")
    st.stop()

# =========================
# Section 1: Analytics Summary
# =========================
st.subheader("Analytics Summary")
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("Total Posts", metrics["total_posts"])
col2.metric("Unique Users", metrics["unique_users"])
col3.metric("Avg Title Length", metrics["avg_title_length"])

col4.metric("Avg Body Length", metrics["avg_body_length"])
col5.metric("Avg Word Count", metrics["avg_word_count"])
col6.metric("Longest Title Length", metrics["longest_title_length"])

# =========================
# Section 2: Pipeline Health
# =========================
st.subheader("Pipeline Health")
h1, h2, h3 = st.columns(3)
h4, h5, h6 = st.columns(3)

h1.metric("Last Run Status", pipeline_health["last_run_status"])
h2.metric("Records Fetched (Last Run)", pipeline_health["last_records_fetched"])
h3.metric("Records Inserted (Last Run)", pipeline_health["last_records_inserted"])

h4.metric("Raw Snapshots", pipeline_health["raw_snapshot_count"])
h5.metric("Processed Snapshots", pipeline_health["processed_snapshot_count"])
h6.metric("Duplicate Records (Last Run)", pipeline_health["last_duplicate_count"])

st.write(f"**Last Run Time:** {pipeline_health['last_run_time']}")
st.write(
    f"**Null Title Count:** {pipeline_health['last_null_title_count']} | "
    f"**Null Body Count:** {pipeline_health['last_null_body_count']} | "
    f"**Empty Title Count:** {pipeline_health['last_empty_title_count']} | "
    f"**Empty Body Count:** {pipeline_health['last_empty_body_count']}"
)

# =========================
# Section 3: Posts Per User
# =========================
st.subheader("Posts Per User")
if posts_data:
    posts_df = pd.DataFrame(posts_data)
    st.dataframe(posts_df, use_container_width=True)
    st.bar_chart(posts_df.set_index("userId")["post_count"])
else:
    st.info("No posts-per-user data available.")

# =========================
# Section 4: Recent Pipeline Runs
# =========================
st.subheader("Recent Pipeline Runs")
if pipeline_runs:
    runs_df = pd.DataFrame(pipeline_runs)
    st.dataframe(runs_df, use_container_width=True)
else:
    st.info("No pipeline run history available yet.")