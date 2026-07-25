import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CITIES_FILE = PROJECT_ROOT / "data" / "cities.json"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ARCHIVE_DIR = PROJECT_ROOT / "data" / "processed"
CLEAN_DIR = PROJECT_ROOT / "data" / "clean"

# Endpoint "current" (utilisé par extract.py, extraction horaire en direct)
API_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

# Endpoint "history" (utilisé par backfill.py, lecture de données passées)
HISTORY_API_URL = "https://api.openweathermap.org/data/2.5/air_pollution/history"

API_KEY = os.getenv("API_KEY")

REQUEST_TIMEOUT = 30
MAX_RETRY = 3

# --- Paramètres du backfill ---
# Nombre de mois d'historique à récupérer
BACKFILL_MONTHS = int(os.getenv("BACKFILL_MONTHS", "3"))
# Taille des tranches de requêtes (en jours) envoyées à l'API history.
# On découpe pour éviter des réponses trop volumineuses / timeouts.
BACKFILL_CHUNK_DAYS = int(os.getenv("BACKFILL_CHUNK_DAYS", "15"))
# Pause (secondes) entre deux appels API pour rester correct avec le rate limit
BACKFILL_REQUEST_DELAY = float(os.getenv("BACKFILL_REQUEST_DELAY", "1"))
