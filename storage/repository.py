from storage.db import get_connection
from monitoring.logger import get_logger

logger = get_logger(__name__)

def create_tables():
    """
    Create all required tables.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_posts (
            id INTEGER PRIMARY KEY,
            userId INTEGER,
            title TEXT,
            body TEXT,
            title_length INTEGER,
            body_length INTEGER,
            word_count INTEGER,
            processed_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT,
            status TEXT,
            records_fetched INTEGER,
            records_inserted INTEGER,
            raw_file_path TEXT,
            processed_file_path TEXT,
            input_record_count INTEGER,
            output_record_count INTEGER,
            duplicate_count INTEGER,
            null_title_count INTEGER,
            null_body_count INTEGER,
            empty_title_count INTEGER,
            empty_body_count INTEGER,
            error_message TEXT
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database tables ensured: processed_posts, pipeline_runs")

def insert_data(df):
    """
    Insert transformed DataFrame rows into SQLite.
    Returns number of inserted rows.
    """
    if df.empty:
        logger.warning("No transformed data to insert into database")
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    rows = [
        (
            int(row["id"]),
            int(row["userId"]),
            row["title"],
            row["body"],
            int(row["title_length"]),
            int(row["body_length"]),
            int(row["word_count"]),
            row["processed_at"],
        )
        for _, row in df.iterrows()
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO processed_posts
        (id, userId, title, body, title_length, body_length, word_count, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()

    logger.info(f"Inserted/updated {len(rows)} records into processed_posts")
    return len(rows)

def insert_pipeline_run(
    status,
    records_fetched=0,
    records_inserted=0,
    raw_file_path=None,
    processed_file_path=None,
    quality_metrics=None,
    error_message=None,
    run_timestamp=None,
):
    """
    Insert one pipeline run record into pipeline_runs.
    """
    if quality_metrics is None:
        quality_metrics = {}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pipeline_runs (
            run_timestamp,
            status,
            records_fetched,
            records_inserted,
            raw_file_path,
            processed_file_path,
            input_record_count,
            output_record_count,
            duplicate_count,
            null_title_count,
            null_body_count,
            empty_title_count,
            empty_body_count,
            error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_timestamp,
        status,
        records_fetched,
        records_inserted,
        raw_file_path,
        processed_file_path,
        quality_metrics.get("input_record_count", 0),
        quality_metrics.get("output_record_count", 0),
        quality_metrics.get("duplicate_count", 0),
        quality_metrics.get("null_title_count", 0),
        quality_metrics.get("null_body_count", 0),
        quality_metrics.get("empty_title_count", 0),
        quality_metrics.get("empty_body_count", 0),
        error_message,
    ))

    conn.commit()
    conn.close()

    logger.info(f"Pipeline run logged with status={status}")

def fetch_recent_pipeline_runs(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            run_id,
            run_timestamp,
            status,
            records_fetched,
            records_inserted,
            raw_file_path,
            processed_file_path,
            input_record_count,
            output_record_count,
            duplicate_count,
            null_title_count,
            null_body_count,
            empty_title_count,
            empty_body_count,
            error_message
        FROM pipeline_runs
        ORDER BY run_id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    columns = [
        "run_id",
        "run_timestamp",
        "status",
        "records_fetched",
        "records_inserted",
        "raw_file_path",
        "processed_file_path",
        "input_record_count",
        "output_record_count",
        "duplicate_count",
        "null_title_count",
        "null_body_count",
        "empty_title_count",
        "empty_body_count",
        "error_message",
    ]

    return [dict(zip(columns, row)) for row in rows]