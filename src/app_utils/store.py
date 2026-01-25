# src/app_utils/store.py
from __future__ import annotations
import json, os
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".mentor_state.json")

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict) -> None:
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
