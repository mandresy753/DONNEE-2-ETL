import logging

logger = logging.getLogger(__name__)

POLLUTANT_COLUMNS = ["co", "no", "no2", "o3", "so2", "nh3", "pm25", "pm10"]


def validate(df):
    """Filtre les lignes invalides plutôt que de faire échouer tout le batch
    pour une seule mauvaise valeur (une lecture AQI hors plage ou un polluant
    négatif ne doit pas bloquer les milliers d'autres lignes valides)."""
    if df.empty:
        raise Exception("Empty dataframe")

    before = len(df)

    df = df[df["aqi"].between(1, 5)]

    for column in POLLUTANT_COLUMNS:
        df = df[~(df[column] < 0)]

    dropped = before - len(df)
    if dropped:
        logger.warning(f"{dropped} invalid row(s) dropped during validation")

    if df.empty:
        raise Exception("All rows invalid after validation")

    return df
