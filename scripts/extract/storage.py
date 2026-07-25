import json

from datetime import datetime, timezone
from config import RAW_DIR

def build_file_path(
    city: dict,
    extraction_time: datetime
):
    date_folder = extraction_time.strftime("%Y-%m-%d")

    filename = (
        f"{city['name'].lower().replace(' ', '_')}_"
        f"{extraction_time.strftime('%H-%M-%S')}.json"
    )
    return (
        RAW_DIR /
        date_folder /
        filename
    )

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