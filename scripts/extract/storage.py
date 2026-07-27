import json

from datetime import datetime, timezone
from scripts.extract.config import RAW_DIR


def build_file_path(city: dict, moment: datetime):
    date_folder = moment.strftime("%Y-%m-%d")

    filename = (
        f"{city['name'].lower().replace(' ', '_')}_"
        f"{moment.strftime('%H-%M-%S')}.json"
    )
    return RAW_DIR / date_folder / filename


def save_raw_json(city: dict, data: dict, moment: datetime):
    """Sauvegarde une lecture brute pour une ville.

    `moment` est l'horodatage associé à la lecture : l'heure d'extraction pour
    une lecture "live" (extract.py), ou l'heure de mesure réelle pour une
    lecture historique (backfill.py). Il sert à la fois à nommer le fichier
    et à renseigner le champ `timestamp` utilisé en aval par la transformation.
    """
    filepath = build_file_path(city, moment)

    filepath.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(data)
    payload.update(
        {
            "city": city["name"],
            "country": city.get("country", "Unknown"),
            "coordinates": {
                "latitude": city["latitude"],
                "longitude": city["longitude"],
            },
            "timestamp": moment.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
            ),
        }
    )

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)

    return filepath
