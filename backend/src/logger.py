"""
Decision Logger — saves every agent decision to logs/session.jsonl.
Each line is a self-contained JSON record of one full recommendation session.
This is the audit trail that makes the system trustworthy and debuggable.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOGS_DIR, "session.jsonl")

logger = logging.getLogger(__name__)


def log_session(
    user_input: str,
    mood_vector: Dict,
    rag_context: List[Dict],
    agent_log: Dict,
    recommendations: List[Dict],
) -> str:
    """
    Write a full session record to logs/session.jsonl.
    Returns the session_id for reference.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")

    record = {
        "session_id":      session_id,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "user_input":      user_input,
        "mood_vector":     mood_vector,
        "rag_retrieved": [
            {"source": c["source"], "score": round(c["score"], 3), "text_preview": c["text"][:120]}
            for c in rag_context
        ],
        "agent": {
            "retries":      agent_log.get("retries", 0),
            "final_passed": agent_log.get("final_passed", True),
            "critiques":    agent_log.get("critiques", []),
        },
        "recommendations": [
            {
                "title":            r["title"],
                "artist":           r["artist"],
                "genre":            r["genre"],
                "score":            r["score"],
                "confidence_score": r.get("confidence_score"),
                "confidence_level": r.get("confidence_level"),
                "explanation":      r["explanation"],
            }
            for r in recommendations
        ],
    }

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        logger.info(f"Session logged: {session_id}")
    except Exception as e:
        logger.error(f"Failed to write log: {e}")

    return session_id


def get_recent_sessions(n: int = 5) -> List[Dict]:
    """Read the last n sessions from the log file."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(line) for line in lines[-n:]]
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return []
