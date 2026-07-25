import csv
import logging
import os
import sys
import uuid

from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
CLEAN_FILE = "data/clean/aqi_clean.csv"
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


def get_connection():
    load_dotenv()
    db_url = os.getenv(
        "NEON_DB_URL"
    )

    if not db_url:
        raise Exception(
            "NEON_DB_URL missing"
        )
    return psycopg2.connect(db_url)

def read_clean_csv():

    if not os.path.exists(CLEAN_FILE):

        raise FileNotFoundError(
            CLEAN_FILE
        )

    with open(
        CLEAN_FILE,
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        missing = [
            col
            for col in REQUIRED_COLUMNS
            if col not in reader.fieldnames
        ]

        if missing:
            raise Exception(
                f"Missing columns : {missing}"
            )


        return list(reader)



def to_float(value):

    if value in (
        "",
        None
    ):
        return None

    return float(value)



def parse_timestamp(value):

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00"
        )
    )



def build_date(row):

    dt = parse_timestamp(
        row["timestamp_utc"]
    )


    return (
        int(dt.strftime("%Y%m%d")),
        dt.date(),
        dt.year,
        (dt.month - 1) // 3 + 1,
        dt.month,
        dt.strftime("%B"),
        dt.day,
        dt.weekday(),
        dt.strftime("%A"),
        dt.weekday() >= 5
    )



def load_dim_date(
    conn,
    rows
):

    dates = {}

    for row in rows:

        data = build_date(row)

        dates[data[0]] = data


    values = list(
        dates.values()
    )


    with conn.cursor() as cursor:

        execute_values(
            cursor,
            """
            INSERT INTO dim_date
            (
                date_id,
                full_date,
                year,
                quarter,
                month,
                month_name,
                day,
                day_of_week,
                day_name,
                is_weekend
            )
            VALUES %s
            ON CONFLICT (date_id)
            DO NOTHING
            """,
            values
        )


    conn.commit()

    return dates



def load_dim_location(
    conn,
    rows
):

    locations = {}

    for row in rows:

        key = (
            row["city"],
            row["country"]
        )

        locations[key] = (
            row["city"],
            row["country"],
            to_float(row["latitude"]),
            to_float(row["longitude"])
        )


    with conn.cursor() as cursor:

        execute_values(
            cursor,
            """
            INSERT INTO dim_location
            (
                city,
                country,
                latitude,
                longitude
            )
            VALUES %s
            ON CONFLICT(city,country)
            DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude
            RETURNING
                location_id,
                city,
                country
            """,
            list(locations.values()),
            fetch=True
        )

        result = cursor.fetchall()


    conn.commit()


    location_ids = {}

    for location_id, city, country in result:

        location_ids[
            (city, country)
        ] = location_id


    return location_ids



def load_fact_air_quality(
    conn,
    rows,
    location_ids
):

    extraction_id = uuid.uuid4()

    extraction_timestamp = datetime.now(
        timezone.utc
    )


    values = []


    for row in rows:

        timestamp = parse_timestamp(
            row["timestamp_utc"]
        )


        date_id = int(
            timestamp.strftime(
                "%Y%m%d"
            )
        )


        location_id = location_ids[
            (
                row["city"],
                row["country"]
            )
        ]


        values.append(
            (
                str(extraction_id),
                extraction_timestamp,
                date_id,
                timestamp.hour,
                location_id,
                timestamp,
                to_float(row["aqi"]),
                to_float(row["co"]),
                to_float(row["no"]),
                to_float(row["no2"]),
                to_float(row["o3"]),
                to_float(row["so2"]),
                to_float(row["pm25"]),
                to_float(row["pm10"]),
                to_float(row["nh3"]),
            )
        )


    with conn.cursor() as cursor:

        execute_values(
            cursor,
            """
            INSERT INTO fact_air_quality_hourly
            (
                extraction_id,
                extraction_timestamp,
                date_id,
                hour,
                location_id,
                measurement_timestamp,
                aqi,
                co,
                no,
                no2,
                o3,
                so2,
                pm2_5,
                pm10,
                nh3
            )
            VALUES %s
            ON CONFLICT
            (
                location_id,
                measurement_timestamp
            )
            DO UPDATE SET

                extraction_id = EXCLUDED.extraction_id,
                extraction_timestamp = EXCLUDED.extraction_timestamp,
                aqi = EXCLUDED.aqi,
                co = EXCLUDED.co,
                no = EXCLUDED.no,
                no2 = EXCLUDED.no2,
                o3 = EXCLUDED.o3,
                so2 = EXCLUDED.so2,
                pm2_5 = EXCLUDED.pm2_5,
                pm10 = EXCLUDED.pm10,
                nh3 = EXCLUDED.nh3
            """,
            values
        )


    conn.commit()

def main():
    rows = read_clean_csv()
    if not rows:

        logger.warning(
            "No data"
        )

        return

    conn = get_connection()

    try:
        load_dim_date(
            conn,
            rows
        )

        location_ids = load_dim_location(
            conn,
            rows
        )

        load_fact_air_quality(
            conn,
            rows,
            location_ids
        )

    except Exception:
        conn.rollback()
        logger.exception(
            "Load failed"
        )
        sys.exit(1)

    finally:
        conn.close()

    logger.info(
        "Warehouse load completed"
    )

if __name__ == "__main__":
    main()