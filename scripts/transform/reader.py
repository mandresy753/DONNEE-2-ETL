import json
import logging

logger = logging.getLogger(__name__)


def read_raw_files(folder):
    """Lit tous les fichiers JSON bruts d'un dossier.

    Retourne une liste de dicts {"data", "file_time", "path"}. `path` permet
    à l'appelant d'archiver ensuite les fichiers effectivement traités.
    """
    rows = []
    files = list(folder.rglob("*.json"))
    logger.info(f"{len(files)} raw files found")

    for file in files:
        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)
            rows.append(
                {
                    "data": data,
                    "file_time": file.stat().st_mtime,
                    "path": file,
                }
            )
        except Exception as e:
            logger.error(f"{file}: {e}")

    return rows
