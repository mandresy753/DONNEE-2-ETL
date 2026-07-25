import json
import logging

def read_raw_files(folder):
    rows = []
    files = list(
        folder.rglob("*.json")
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
            rows.append(
                {
                    "data": data,
                    "file_time": file.stat().st_mtime
                }
            )

        except Exception as e:
            logging.error(
                f"{file}: {e}"
            )
    return rows