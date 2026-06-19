"""Notion connector.

Native shape:
    {"id","title","last_edited","author","block_count"}

The page title is registered as an alias so that an in-text mention like
"context is in the Atlas Launch Spec" elsewhere can be resolved back to this event.
"""

from __future__ import annotations

from ..models import Event, EventType
from .base import BaseConnector


class NotionConnector(BaseConnector):
    source = "notion"

    def to_events(self, raw: dict) -> list[Event]:
        return [Event(
            id=f"notion:{raw['id']}",
            source=self.source,
            type=EventType.DOCUMENT_EDITED,
            actor=raw["author"],
            ts=self.parse_ts(raw["last_edited"]),
            title=raw["title"],
            text=raw["title"],
            raw_key=raw["id"],
            aliases=(raw["title"],),
        )]
