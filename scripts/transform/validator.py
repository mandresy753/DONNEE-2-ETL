def validate(df):

    if df.empty:
        raise Exception(
            "Empty dataframe"
        )

    if not df["aqi"].between(
        1,
        5
    ).all():
        raise Exception(
            "Invalid AQI"
        )

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

    for column in pollutants:

        if (df[column] < 0).any():

            raise Exception(
                f"Negative value in {column}"
            )