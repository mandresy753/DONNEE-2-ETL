from pathlib import Path
import pandas as pd

from extractor import extract_row
from reader import read_raw_files
from cleaner import clean_dataframe
from validator import validate
from writer import write_clean


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FOLDER = BASE_DIR / "data" / "raw"
OUTPUT_FILE = (
    BASE_DIR /
    "data" /
    "clean" /
    "aqi_clean.csv"
)

def main():

    raw_files = read_raw_files(RAW_FOLDER)
    rows = []

    for item in raw_files:
        row = extract_row(item["data"])
        row["file_time"] = (item["file_time"])
        rows.append(row)

    df = pd.DataFrame(rows)
    df = clean_dataframe(df)
    validate(df)
    write_clean(df, OUTPUT_FILE)

if __name__ == "__main__":
    main()