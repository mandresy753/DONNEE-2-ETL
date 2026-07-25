import logging
import time

import requests

from config import (
    API_KEY,
    API_URL,
    REQUEST_TIMEOUT,
    MAX_RETRY,
)

logger = logging.getLogger(__name__)

def fetch_aqi(city: dict):

    if not API_KEY:
        raise ValueError("API_KEY missing")

    params = {
        "lat": city["latitude"],
        "lon": city["longitude"],
        "appid": API_KEY
    }

    for attempt in range(
        1,
        MAX_RETRY + 1
    ):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as error:

            logger.warning(
                f"Attempt {attempt}/{MAX_RETRY} "
                f"failed for {city['name']}: {error}"
            )

            if attempt < MAX_RETRY:
                time.sleep(
                    attempt * 5
                )
            else:
                raise