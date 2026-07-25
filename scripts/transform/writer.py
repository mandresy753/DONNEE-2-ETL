FINAL_COLUMNS = [
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


def write_clean(df, output):
    output.parent.mkdir(parents=True, exist_ok=True)

    df[FINAL_COLUMNS].to_csv(output, index=False)
