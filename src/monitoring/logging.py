from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.utils.paths import LOG_DIR


class PredictionLogger:
    def __init__(self, log_path: Path | None = None) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_path = log_path or LOG_DIR / "predictions.jsonl"

    def write(self, record: dict[str, Any]) -> None:
        event = {"logged_at": datetime.now(UTC).isoformat(), **record}
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")
