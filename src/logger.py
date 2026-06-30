"""
BioBridge AI V1 - Local Logging Utility
---------------------------------------
Provides a single helper function to log feature usage locally.

Design goals:
- Standard library only
- JSON Lines (.jsonl) format
- Auto-create logs directory/file
- Best-effort logging (never crashes the app)
"""

import json
import os
from datetime import datetime, timezone

from src.constants import (
    LOG_DIRECTORY,
    LOG_FILENAME,
    MAX_LOG_INPUT_LENGTH,
)


def log_event(
    feature,
    status,
    user_input,
    latency_ms=None,
    error_message=None,
    rejection_reason=None,
):
    """
    Logs a single event to the local JSONL log file.

    Parameters
    ----------
    feature : str
        Feature name.
    status : str
        success / error / rejected
    user_input : str
        Original user input.
    latency_ms : int | float | None
        Execution time in milliseconds.
    error_message : str | None
        Error details if an exception occurred.
    rejection_reason : str | None
        Reason for rejection (harmful, medical, homework, offtopic).

    Returns
    -------
    None
    """

    try:
        os.makedirs(LOG_DIRECTORY, exist_ok=True)

        log_path = os.path.join(LOG_DIRECTORY, LOG_FILENAME)

        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feature": feature,
            "status": status,
            "user_input": (user_input or "")[:MAX_LOG_INPUT_LENGTH],
            "latency_ms": latency_ms,
            "error_message": error_message,
            "rejection_reason": rejection_reason,
        }

        with open(log_path, "a", encoding="utf-8") as file:
            json.dump(log_record, file)
            file.write("\n")

    except Exception as e:
        print(f"[LOGGER ERROR] {e}")

    return None
