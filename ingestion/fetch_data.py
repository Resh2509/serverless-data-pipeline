import json
import os
from datetime import datetime

import requests

from config import API_URL, RAW_DATA_DIR
from monitoring.logger import get_logger

logger = get_logger(__name__)

def fetch_data():
    """
    Fetch data from public API and save raw JSON snapshot locally.

    Returns:
        tuple:
            raw_data (list[dict])
            raw_file_path (str | None)
            records_fetched (int)
    """
    try:
        logger.info("Starting data ingestion from public API")

        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()

        data = response.json()

        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_file = os.path.join(RAW_DATA_DIR, f"raw_posts_{timestamp}.json")

        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Fetched {len(data)} records from API")
        logger.info(f"Raw data saved to {raw_file}")

        return data, raw_file, len(data)

    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        return [], None, 0