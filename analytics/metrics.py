import os
import pandas as pd

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from storage.db import get_connection
from storage.repository import fetch_recent_pipeline_runs

def generate_metrics():
    conn = get_connection()

    try:
        df = pd.read_sql_query("SELECT * FROM processed_posts", conn)

        if df.empty:
            return {
                "total_posts": 0,
                "unique_users": 0,
                "avg_title_length": 0,
                "avg_body_length": 0,
                "avg_word_count": 0,
                "longest_title_length": 0,
            }

        metrics = {
            "total_posts": int(len(df)),
            "unique_users": int(df["userId"].nunique()),
            "avg_title_length": round(float(df["title_length"].mean()), 2),
            "avg_body_length": round(float(df["body_length"].mean()), 2),
            "avg_word_count": round(float(df["word_count"].mean()), 2),
            "longest_title_length": int(df["title_length"].max()),
        }

        return metrics

    finally:
        conn.close()

def posts_per_user():
    conn = get_connection()

    try:
        query = """
            SELECT userId, COUNT(*) AS post_count
            FROM processed_posts
            GROUP BY userId
            ORDER BY post_count DESC, userId ASC
        """
        df = pd.read_sql_query(query, conn)
        return df

    finally:
        conn.close()

def pipeline_health_summary():
    recent_runs = fetch_recent_pipeline_runs(limit=1)
    latest_run = recent_runs[0] if recent_runs else None

    raw_snapshot_count = (
        len([f for f in os.listdir(RAW_DATA_DIR)]) if os.path.exists(RAW_DATA_DIR) else 0
    )
    processed_snapshot_count = (
        len([f for f in os.listdir(PROCESSED_DATA_DIR)]) if os.path.exists(PROCESSED_DATA_DIR) else 0
    )

    if latest_run:
        return {
            "last_run_time": latest_run["run_timestamp"],
            "last_run_status": latest_run["status"],
            "last_records_fetched": latest_run["records_fetched"],
            "last_records_inserted": latest_run["records_inserted"],
            "raw_snapshot_count": raw_snapshot_count,
            "processed_snapshot_count": processed_snapshot_count,
            "last_duplicate_count": latest_run["duplicate_count"],
            "last_null_title_count": latest_run["null_title_count"],
            "last_null_body_count": latest_run["null_body_count"],
            "last_empty_title_count": latest_run["empty_title_count"],
            "last_empty_body_count": latest_run["empty_body_count"],
        }

    return {
        "last_run_time": None,
        "last_run_status": "NO_RUNS",
        "last_records_fetched": 0,
        "last_records_inserted": 0,
        "raw_snapshot_count": raw_snapshot_count,
        "processed_snapshot_count": processed_snapshot_count,
        "last_duplicate_count": 0,
        "last_null_title_count": 0,
        "last_null_body_count": 0,
        "last_empty_title_count": 0,
        "last_empty_body_count": 0,
    }

def recent_pipeline_runs(limit=10):
    return fetch_recent_pipeline_runs(limit=limit)