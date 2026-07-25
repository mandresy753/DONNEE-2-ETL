import logging

from datetime import datetime, timezone
from cities import load_cities
from client import fetch_aqi
from storage import save_raw_json

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "- %(levelname)s "
        "- %(message)s"
    )
)

logger = logging.getLogger(__name__)

def extract_city(
    city: dict,
    extraction_time: datetime
):

    logger.info(
        f"Extracting {city['name']}"
    )

    data = fetch_aqi(
        city
    )

    filepath = save_raw_json(
        city,
        data,
        extraction_time
    )
    logger.info(
        f"Saved {filepath}"
    )

def extract_all():
    cities = load_cities()

    extraction_time = datetime.now(
        timezone.utc
    )

    logger.info(
        f"{len(cities)} cities loaded"
    )

    for city in cities:

        extract_city(
            city,
            extraction_time
        )

if __name__ == "__main__":
    extract_all()
