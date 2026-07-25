import logging
import sys

from datetime import datetime, timezone

from scripts.extract.cities import load_cities
from scripts.extract.client import fetch_aqi
from scripts.extract.storage import save_raw_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def extract_city(city: dict, extraction_time: datetime):
    logger.info(f"Extracting {city['name']}")

    data = fetch_aqi(city)

    filepath = save_raw_json(city, data, extraction_time)
    logger.info(f"Saved {filepath}")


def extract_all():
    cities = load_cities()
    extraction_time = datetime.now(timezone.utc)

    logger.info(f"{len(cities)} cities loaded")

    failures = []
    for city in cities:
        try:
            extract_city(city, extraction_time)
        except Exception:
            logger.exception(f"Extraction failed for {city['name']}")
            failures.append(city["name"])

    if failures:
        logger.error(f"Extraction failed for: {', '.join(failures)}")
        raise SystemExit(1)

    logger.info("Extraction completed successfully")


if __name__ == "__main__":
    extract_all()
