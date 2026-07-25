import logging
import time

from datetime import datetime, timedelta, timezone

from scripts.extract.cities import load_cities
from scripts.extract.client import fetch_aqi_history
from scripts.extract.storage import save_raw_json
from scripts.extract.config import (
    BACKFILL_MONTHS,
    BACKFILL_CHUNK_DAYS,
    BACKFILL_REQUEST_DELAY,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_window(months: int) -> tuple[datetime, datetime]:
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=months * 30)
    return start, end


def build_chunks(start: datetime, end: datetime, chunk_days: int) -> list[tuple[datetime, datetime]]:
    """Découpe [start, end] en tranches de `chunk_days` jours maximum,
    pour éviter des requêtes trop volumineuses côté API."""
    chunks = []
    current = start
    step = timedelta(days=chunk_days)

    while current < end:
        chunk_end = min(current + step, end)
        chunks.append((current, chunk_end))
        current = chunk_end

    return chunks


def save_history_payload(city: dict, payload: dict) -> int:
    """Éclate la réponse `history` (une entrée par heure) en fichiers bruts
    individuels, au même format que ceux produits par extract.py, pour que
    la suite du pipeline (transform.py) n'ait rien à savoir du backfill."""
    entries = payload.get("list") or []
    saved = 0

    for entry in entries:
        if "dt" not in entry:
            continue
        measurement_time = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
        save_raw_json(city, {"list": [entry]}, measurement_time)
        saved += 1

    return saved


def backfill_city(city: dict, start: datetime, end: datetime) -> int:
    total_saved = 0

    for chunk_start, chunk_end in build_chunks(start, end, BACKFILL_CHUNK_DAYS):
        logger.info(
            f"{city['name']}: fetching {chunk_start.isoformat()} -> {chunk_end.isoformat()}"
        )
        try:
            payload = fetch_aqi_history(city, chunk_start, chunk_end)
        except Exception:
            logger.exception(
                f"{city['name']}: chunk failed ({chunk_start} -> {chunk_end}), skipped"
            )
            continue

        saved = save_history_payload(city, payload)
        total_saved += saved
        logger.info(f"{city['name']}: {saved} hourly readings saved for this chunk")

        time.sleep(BACKFILL_REQUEST_DELAY)

    return total_saved


def run_backfill():
    cities = load_cities()
    start, end = get_window(BACKFILL_MONTHS)

    logger.info(
        f"Backfill window: {start.isoformat()} -> {end.isoformat()} "
        f"({BACKFILL_MONTHS} months, {len(cities)} cities)"
    )

    grand_total = 0
    failed_cities = []

    for city in cities:
        try:
            saved = backfill_city(city, start, end)
            grand_total += saved
            logger.info(f"{city['name']}: {saved} readings saved in total")
        except Exception:
            logger.exception(f"Backfill failed entirely for {city['name']}")
            failed_cities.append(city["name"])

    logger.info(f"Backfill completed: {grand_total} readings saved")

    if failed_cities:
        logger.error(f"Backfill failed for: {', '.join(failed_cities)}")
        raise SystemExit(1)


if __name__ == "__main__":
    run_backfill()
