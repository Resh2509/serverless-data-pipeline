import os
from datetime import datetime

import pandas as pd

from config import PROCESSED_DATA_DIR
from monitoring.logger import get_logger

logger = get_logger(__name__)

def transform_data(raw_data):
    """
    Clean and transform raw API data into a structured DataFrame.

    Returns:
        tuple:
            df (pd.DataFrame)
            processed_file_path (str | None)
            quality_metrics (dict)
    """
    try:
        logger.info("Starting transformation step")

        if not raw_data:
            logger.warning("No raw data received for transformation")
            return pd.DataFrame(), None, {}

        df = pd.DataFrame(raw_data)

        required_columns = ["userId", "id", "title", "body"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return pd.DataFrame(), None, {}

        input_record_count = len(df)
        duplicate_count = int(df.duplicated(subset=["id"]).sum())
        null_title_count = int(df["title"].isna().sum())
        null_body_count = int(df["body"].isna().sum())

        df = df.drop_duplicates(subset=["id"]).copy()

        df["title"] = df["title"].astype(str).str.strip().str.lower()
        df["body"] = df["body"].astype(str).str.strip()

        empty_title_count = int((df["title"] == "").sum())
        empty_body_count = int((df["body"] == "").sum())

        df["title_length"] = df["title"].apply(len)
        df["body_length"] = df["body"].apply(len)
        df["word_count"] = df["body"].apply(lambda x: len(x.split()))
        df["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_file = os.path.join(
            PROCESSED_DATA_DIR, f"processed_posts_{timestamp}.csv"
        )
        df.to_csv(processed_file, index=False)

        quality_metrics = {
            "input_record_count": int(input_record_count),
            "output_record_count": int(len(df)),
            "duplicate_count": duplicate_count,
            "null_title_count": null_title_count,
            "null_body_count": null_body_count,
            "empty_title_count": empty_title_count,
            "empty_body_count": empty_body_count,
        }

        logger.info(f"Transformation complete. Processed {len(df)} records")
        logger.info(f"Processed data saved to {processed_file}")
        logger.info(f"Data quality metrics: {quality_metrics}")

        return df, processed_file, quality_metrics

    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        return pd.DataFrame(), None, {}