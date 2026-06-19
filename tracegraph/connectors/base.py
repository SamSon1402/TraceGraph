"""Connector base. One subclass per source; each flattens a native export schema
into a list of normalized ``Event`` objects.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

from ..models import Event


class BaseConnector(ABC):
    source: str

    @abstractmethod
    def to_events(self, raw: dict) -> list[Event]:  # pragma: no cover - interface
        ...

    def load(self, path: str | Path) -> list[Event]:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return self.to_events(raw)

    @staticmethod
    def parse_ts(value: str) -> datetime:
        """Parse an ISO-8601 timestamp, normalizing to UTC."""
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
