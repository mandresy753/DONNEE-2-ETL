import logging

import pandas as pd

from scripts.extract.config import RAW_DIR, ARCHIVE_DIR, CLEAN_DIR
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


def archive_processed(paths):
    """Déplace les fichiers bruts traités avec succès vers data/processed/,
    pour que le prochain run ne retraite pas indéfiniment tout l'historique
    (sans ça, chaque exécution horaire relit et recharge TOUT ce qui a été
    accumulé depuis le début, y compris après un backfill de plusieurs mois)."""
    for path in paths:
        try:
            relative = path.relative_to(RAW_DIR)
            target = ARCHIVE_DIR / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(target)
        except Exception:
            logger.exception(f"Could not archive {path}")


def main():
    raw_items = read_raw_files(RAW_DIR)

    if not raw_items:
        logger.info("No new raw files to process")
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

    archive_processed([item["path"] for item in raw_items])

    logger.info(f"{len(df)} clean rows written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
