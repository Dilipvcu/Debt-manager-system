# src/app_utils/logger.py
from __future__ import annotations
import json, os, time

# Write events next to your repo root as a JSONL log
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".snowball_events.jsonl")

def log_event(event: dict) -> None:
    """Append an event to the local JSONL log. Never crash the app."""
    try:
        payload = {"ts": int(time.time()), **(event or {})}
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        # Logging should never break the app.
        pass
