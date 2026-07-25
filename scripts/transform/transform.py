import logging

import pandas as pd

from scripts.extract.config import RAW_DIR, CLEAN_DIR
from scripts.transform.extractor import extract_row
from scripts.transform.reader import read_raw_files
from scripts.transform.cleaner import clean_dataframe
from scripts.transform.validator import validate
from scripts.transform.writer import write_clean

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_FILE = CLEAN_DIR / "aqi_clean.csv"


def main():
    raw_items = read_raw_files(RAW_DIR)

    if not raw_items:
        logger.info("No raw files found in the data lake")
        return

    rows = []
    for item in raw_items:
        row = extract_row(item["data"])
        row["file_time"] = item["file_time"]
        rows.append(row)

    df = pd.DataFrame(rows)
    df = clean_dataframe(df)
    df = validate(df)
    write_clean(df, OUTPUT_FILE)

    logger.info(f"{len(df)} clean rows written to {OUTPUT_FILE} (full history)")


if __name__ == "__main__":
    main()
