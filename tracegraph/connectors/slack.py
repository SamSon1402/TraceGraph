"""Slack connector.

Native shape:
    {"channel": str, "messages": [{"id","ts","user","text","refs":[...]}]}
"""

from __future__ import annotations

from ..models import Event, EventType
from .base import BaseConnector


class SlackConnector(BaseConnector):
    source = "slack"

    def to_events(self, raw: dict) -> list[Event]:
        channel = raw["channel"]
        events: list[Event] = []
        for m in raw["messages"]:
            events.append(Event(
                id=f"slack:{channel}#{m['id']}",
                source=self.source,
                type=EventType.MESSAGE_SENT,
                actor=m["user"],
                ts=self.parse_ts(m["ts"]),
                title=m["text"],
                text=m["text"],
                raw_refs=tuple(m.get("refs", [])),
            ))
        return events
