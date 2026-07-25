import logging
import time
from datetime import datetime

import requests

from scripts.extract.config import (
    API_KEY,
    API_URL,
    HISTORY_API_URL,
    REQUEST_TIMEOUT,
    MAX_RETRY,
)

logger = logging.getLogger(__name__)


def _get_with_retry(url: str, params: dict, label: str) -> dict:
    if not API_KEY:
        raise ValueError("API_KEY missing")

    last_error = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as error:
            last_error = error
            logger.warning(
                f"Attempt {attempt}/{MAX_RETRY} failed for {label}: {error}"
            )
            if attempt < MAX_RETRY:
                time.sleep(attempt * 5)

    raise last_error


def fetch_aqi(city: dict) -> dict:
    """Récupère la qualité de l'air actuelle pour une ville."""
    params = {
        "lat": city["latitude"],
        "lon": city["longitude"],
        "appid": API_KEY,
    }
    return _get_with_retry(API_URL, params, city["name"])


def fetch_aqi_history(city: dict, start: datetime, end: datetime) -> dict:
    """Récupère l'historique de qualité de l'air pour une ville entre start et end (UTC)."""
    params = {
        "lat": city["latitude"],
        "lon": city["longitude"],
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "appid": API_KEY,
    }
    return _get_with_retry(HISTORY_API_URL, params, f"{city['name']} (history)")
