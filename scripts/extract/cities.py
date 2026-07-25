import json

from scripts.extract.config import CITIES_FILE


def load_cities() -> list[dict]:
    if not CITIES_FILE.exists():
        raise FileNotFoundError(f"Missing file: {CITIES_FILE}")

    with open(CITIES_FILE, encoding="utf-8") as file:
        cities = json.load(file)

    if not isinstance(cities, list):
        raise ValueError("cities.json must contain a list")

    if not cities:
        raise ValueError("cities.json is empty")

    required_keys = {"name", "country", "latitude", "longitude"}
    for city in cities:
        missing = required_keys - city.keys()
        if missing:
            raise ValueError(f"City entry {city} is missing keys: {missing}")

    return cities
