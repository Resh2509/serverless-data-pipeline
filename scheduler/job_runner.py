from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from config import SCHEDULE_INTERVAL_MINUTES
from ingestion.fetch_data import fetch_data
from transformation.clean_data import transform_data
from storage.repository import create_tables, insert_data, insert_pipeline_run
from monitoring.logger import get_logger

logger = get_logger(__name__)

def pipeline_job():
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Pipeline job started at {run_timestamp}")

    try:
        raw_data, raw_file_path, records_fetched = fetch_data()

        if not raw_data:
            message = "Pipeline stopped because no raw data was fetched"
            logger.warning(message)

            insert_pipeline_run(
                status="FAILED",
                records_fetched=0,
                records_inserted=0,
                raw_file_path=raw_file_path,
                processed_file_path=None,
                quality_metrics={},
                error_message=message,
                run_timestamp=run_timestamp,
            )
            return

        transformed_df, processed_file_path, quality_metrics = transform_data(raw_data)

        if transformed_df.empty:
            message = "Pipeline stopped because transformed dataframe is empty"
            logger.warning(message)

            insert_pipeline_run(
                status="FAILED",
                records_fetched=records_fetched,
                records_inserted=0,
                raw_file_path=raw_file_path,
                processed_file_path=processed_file_path,
                quality_metrics=quality_metrics,
                error_message=message,
                run_timestamp=run_timestamp,
            )
            return

        records_inserted = insert_data(transformed_df)

        insert_pipeline_run(
            status="SUCCESS",
            records_fetched=records_fetched,
            records_inserted=records_inserted,
            raw_file_path=raw_file_path,
            processed_file_path=processed_file_path,
            quality_metrics=quality_metrics,
            error_message=None,
            run_timestamp=run_timestamp,
        )

        logger.info("Pipeline job completed successfully")

    except Exception as e:
        logger.exception(f"Unexpected pipeline failure: {e}")

        insert_pipeline_run(
            status="FAILED",
            records_fetched=0,
            records_inserted=0,
            raw_file_path=None,
            processed_file_path=None,
            quality_metrics={},
            error_message=str(e),
            run_timestamp=run_timestamp,
        )

if __name__ == "__main__":
    create_tables()

    scheduler = BlockingScheduler()

    # Run immediately once
    pipeline_job()

    # Then schedule repeatedly
    scheduler.add_job(pipeline_job, "interval", minutes=SCHEDULE_INTERVAL_MINUTES)

    logger.info(
        f"Scheduler started. Pipeline will run every {SCHEDULE_INTERVAL_MINUTES} minutes."
    )
    scheduler.start()