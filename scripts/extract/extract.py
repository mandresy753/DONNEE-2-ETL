import json
import logging
import os
import time

from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()


# ==========================
# PATHS
# ==========================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


CITIES_FILE = (
    PROJECT_ROOT /
    "data" /
    "cities.json"
)


RAW_DIR = (
    PROJECT_ROOT /
    "data" /
    "raw"
)


# ==========================
# API CONFIG
# ==========================

CURRENT_API_URL = (
    "https://api.openweathermap.org/data/2.5/air_pollution"
)


HISTORY_API_URL = (
    "https://api.openweathermap.org/data/2.5/air_pollution/history"
)


AQI_API_KEY = os.getenv(
    "AQI_API_KEY"
)


REQUEST_TIMEOUT = 30

MAX_RETRY = 3



# ==========================
# LOGGING
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "- %(levelname)s "
        "- %(message)s"
    )
)



# ==========================
# LOAD CITIES
# ==========================

def load_cities() -> list[dict]:

    if not CITIES_FILE.exists():

        raise FileNotFoundError(
            f"Missing file : {CITIES_FILE}"
        )


    with open(
        CITIES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        cities = json.load(file)


    if not isinstance(cities, list):

        raise ValueError(
            "cities.json must contain a list"
        )


    return cities



# ==========================
# FETCH OPENWEATHER API
# ==========================

def fetch_aqi(
    city: dict,
    target_datetime: datetime | None = None
):

    if not AQI_API_KEY:

        raise ValueError(
            "AQI_API_KEY missing"
        )


    params = {
        "lat": city["latitude"],
        "lon": city["longitude"],
        "appid": AQI_API_KEY
    }


    if target_datetime:

        timestamp = int(
            target_datetime.timestamp()
        )


        params.update(
            {
                "start": timestamp,
                "end": timestamp + 3600
            }
        )


        url = HISTORY_API_URL


    else:

        url = CURRENT_API_URL



    for attempt in range(
        1,
        MAX_RETRY + 1
    ):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT
            )


            response.raise_for_status()


            return response.json()



        except requests.exceptions.RequestException as error:


            logging.warning(
                f"Attempt {attempt}/{MAX_RETRY} "
                f"failed for {city['name']} : {error}"
            )


            if attempt < MAX_RETRY:

                time.sleep(
                    attempt * 5
                )

            else:

                raise



# ==========================
# RAW FILE PATH
# ==========================

def build_file_path(
    city: dict,
    extraction_time: datetime
):

    date_folder = extraction_time.strftime(
        "%Y-%m-%d"
    )


    filename = (
        f"{city['name'].lower().replace(' ', '_')}_"
        f"{extraction_time.strftime('%H-%M-%S')}.json"
    )


    folder = (
        RAW_DIR /
        date_folder
    )


    return folder / filename



# ==========================
# CHECK EXISTENCE
# ==========================

def raw_file_exists(
    city: dict,
    extraction_time: datetime
):

    filepath = build_file_path(
        city,
        extraction_time
    )

    return filepath.exists()



# ==========================
# SAVE RAW JSON
# ==========================

def save_raw_json(
    city: dict,
    data: dict,
    extraction_time: datetime
):

    filepath = build_file_path(
        city,
        extraction_time
    )


    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    data.update(
        {
            "city": city["name"],

            "country": city.get(
                "country",
                "Unknown"
            ),

            "coordinates": {
                "latitude": city["latitude"],
                "longitude": city["longitude"]
            },

            "timestamp": (
                extraction_time
                .astimezone(timezone.utc)
                .isoformat()
            )
        }
    )


    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


    return filepath



# ==========================
# EXTRACT ONE CITY
# ==========================

def extract_aqi(
    city: dict,
    extraction_time: datetime
):

    if raw_file_exists(
        city,
        extraction_time
    ):

        logging.info(
            f"Already exists : "
            f"{city['name']} {extraction_time}"
        )

        return



    logging.info(
        f"Extracting {city['name']}"
    )


    data = fetch_aqi(
        city,
        extraction_time
    )


    filepath = save_raw_json(
        city,
        data,
        extraction_time
    )


    logging.info(
        f"Saved : {filepath}"
    )



# ==========================
# MAIN
# ==========================

def main():

    cities = load_cities()


    extraction_time = datetime.now(
        timezone.utc
    )


    logging.info(
        f"{len(cities)} cities loaded"
    )


    logging.info(
        f"Extraction batch time : {extraction_time}"
    )


    for city in cities:

        extract_aqi(
            city,
            extraction_time
        )



if __name__ == "__main__":

    main()