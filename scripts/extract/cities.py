import json

from config import CITIES_FILE

def load_cities() -> list[dict]:

    if not CITIES_FILE.exists():

        raise FileNotFoundError(
            f"Missing file: {CITIES_FILE}"
        )

    with open(
        CITIES_FILE,
        encoding="utf-8"
    ) as file:

        cities = json.load(file)

    if not isinstance(cities, list):
        raise ValueError(
            "cities.json must contain a list"
        )

    return cities