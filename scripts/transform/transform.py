import json
import logging
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FOLDER = BASE_DIR / "data" / "raw"
CLEAN_FOLDER = BASE_DIR / "data" / "clean"
OUTPUT_FILE = CLEAN_FOLDER / "aqi_clean.csv"
REPORT_FILE = CLEAN_FOLDER / "validation_report.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

REQUIRED_COLUMNS = [
    "city",
    "country",
    "latitude",
    "longitude",
    "timestamp_utc",
    "aqi",
    "co",
    "no",
    "no2",
    "o3",
    "so2",
    "pm25",
    "pm10",
    "nh3",
]

def extract_row(data):

    entry = (
        data.get("list") or [{}]
    )[0]
    main = entry.get(
        "main",
        {}
    )
    components = entry.get(
        "components",
        {}
    )
    coords = data.get(
        "coord",
        {}
    )

    if "coordinates" in data:

        coords = data["coordinates"]
        latitude = coords.get("latitude")
        longitude = coords.get("longitude")
    else:

        latitude = coords.get("lat")
        longitude = coords.get("lon")

    timestamp = entry.get("dt")

    if data.get("timestamp"):
        timestamp = data["timestamp"]

    return {
        "city": data.get("city"),
        "country": data.get("country"),
        "latitude": latitude,
        "longitude": longitude,
        "timestamp_utc": timestamp,
        "aqi": main.get("aqi"),
        "co": components.get("co"),
        "no": components.get("no"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),
        "nh3": components.get("nh3"),
        "pm25": components.get("pm2_5"),
        "pm10": components.get("pm10"),
    }

def read_raw_files():

    rows = []
    files = list(
        RAW_FOLDER.rglob("*.json")
    )

    logging.info(
        f"{len(files)} raw files found"
    )

    for file in files:
        try:
            with open(
                file,
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            row = extract_row(data)

            row["raw_file_time"] = (
                file.stat().st_mtime
            )
            rows.append(row)
        except Exception as e:

            logging.error(
                f"{file}: {e}"
            )

    return rows


def clean_dataframe(df):


    # Timestamp Unix
    unix_mask = pd.to_numeric(
        df["timestamp_utc"],
        errors="coerce"
    ).notna()


    df.loc[
        unix_mask,
        "timestamp_utc"
    ] = pd.to_datetime(
        df.loc[
            unix_mask,
            "timestamp_utc"
        ],
        unit="s",
        utc=True
    )


    # Timestamp ISO

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        errors="coerce",
        utc=True
    )


    # Suppression données inutiles

    df = df.dropna(
        subset=[
            "city",
            "timestamp_utc"
        ]
    )


    # Conversion numérique

    numeric_columns = [
        "latitude",
        "longitude",
        "aqi",
        "co",
        "no",
        "no2",
        "o3",
        "so2",
        "nh3",
        "pm25",
        "pm10"
    ]


    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )



    # Heure pour analyse

    df["hour"] = (
        df["timestamp_utc"]
        .dt.floor("h")
    )



    # Garder dernière valeur

    df = df.sort_values(
        [
            "city",
            "hour",
            "raw_file_time"
        ]
    )


    df = df.drop_duplicates(
        [
            "city",
            "hour"
        ],
        keep="last"
    )


    return df



# ==========================
# BUSINESS QUALITY CHECKS
# ==========================

def quality_checks(df):

    errors = []


    # AQI OpenWeather = 1 à 5

    invalid_aqi = df[
        ~df["aqi"].between(
            1,
            5
        )
    ]


    if len(invalid_aqi):

        errors.append(
            f"{len(invalid_aqi)} invalid AQI"
        )



    # Pollution négative impossible

    pollutants = [
        "co",
        "no",
        "no2",
        "o3",
        "so2",
        "nh3",
        "pm25",
        "pm10"
    ]


    for col in pollutants:

        count = (
            df[col] < 0
        ).sum()


        if count:

            errors.append(
                f"{count} negative values in {col}"
            )



    # Coordonnées

    invalid_coordinates = df[
        ~df["latitude"].between(
            -90,
            90
        )
        |
        ~df["longitude"].between(
            -180,
            180
        )
    ]


    if len(invalid_coordinates):

        errors.append(
            f"{len(invalid_coordinates)} invalid coordinates"
        )


    return errors



# ==========================
# BUILD CLEAN CSV
# ==========================

def build_clean():

    rows = read_raw_files()


    if not rows:

        raise Exception(
            "No raw data"
        )


    df = pd.DataFrame(rows)


    df = clean_dataframe(df)


    quality_checks(df)

    logging.info(
        f"Clean CSV created : {OUTPUT_FILE}"
    )
    return df

def main():

    build_clean()



if __name__ == "__main__":

    main()