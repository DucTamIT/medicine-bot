import json
import os
from datetime import datetime
import pytz
from config import TIMEZONE

TZ = pytz.timezone(TIMEZONE)
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "doses.json")


def _load() -> dict:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _today_key() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d")


def mark_taken(med_id: str, time_slot: str) -> bool:
    """Mark a dose as taken. Returns True if newly marked, False if already marked."""
    data = _load()
    day_key = _today_key()
    dose_key = f"{day_key}|{med_id}|{time_slot}"
    if dose_key in data:
        return False
    data[dose_key] = datetime.now(TZ).isoformat()
    _save(data)
    return True


def is_taken(med_id: str, time_slot: str) -> bool:
    data = _load()
    day_key = _today_key()
    dose_key = f"{day_key}|{med_id}|{time_slot}"
    return dose_key in data


def get_today_status() -> dict:
    """Returns dict of {dose_key: taken_time} for today."""
    data = _load()
    day_key = _today_key()
    return {k: v for k, v in data.items() if k.startswith(day_key)}


def get_all_data() -> dict:
    return _load()
