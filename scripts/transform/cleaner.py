import pandas as pd


NUMERIC_COLUMNS = [
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

def clean_dataframe(df):

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        errors="coerce",
        utc=True
    )

    df = df.dropna(
        subset=[
            "city",
            "timestamp_utc"
        ]
    )


    df[NUMERIC_COLUMNS] = (
        df[NUMERIC_COLUMNS]
        .apply(
            pd.to_numeric,
            errors="coerce"
        )
    )

    df["hour"] = (
        df["timestamp_utc"]
        .dt.floor("h")
    )

    df = df.sort_values(
        [
            "city",
            "hour",
            "file_time"
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