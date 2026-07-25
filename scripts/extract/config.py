import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CITIES_FILE = (
    PROJECT_ROOT /
    "data" /
    "cities.json"
)
RAW_DIR = (
    PROJECT_ROOT /
    "data" /
    "raw"
)
API_URL = (
    "https://api.openweathermap.org/data/2.5/air_pollution"
)
API_KEY = os.getenv("API_KEY")
REQUEST_TIMEOUT = 30
MAX_RETRY = 3