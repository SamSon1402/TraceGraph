"""Jira connector.

Native shape:
    {"key","created","reporter","assignee","fields":{"summary","status"},
     "status_changed","links":[{"type","to"}]}

Emits two events: the ticket creation and (if present) a later status change. Modeling
the status change as its own event is what lets the trajectory capture "the ticket
moved to In Review" as a distinct step in the workflow.
"""

from __future__ import annotations

from ..models import Event, EventType
from .base import BaseConnector


class JiraConnector(BaseConnector):
    source = "jira"

    def to_events(self, raw: dict) -> list[Event]:
        key = raw["key"]
        fields = raw["fields"]
        ticket_id = f"jira:{key}"
        link_refs = tuple(link["to"] for link in raw.get("links", []))

        events = [Event(
            id=ticket_id,
            source=self.source,
            type=EventType.TICKET_OPENED,
            actor=raw["reporter"],
            ts=self.parse_ts(raw["created"]),
            title=key,
            text=fields["summary"],
            raw_key=key,
            raw_refs=link_refs,
        )]

        if raw.get("status_changed"):
            events.append(Event(
                id=f"{ticket_id}#status",
                source=self.source,
                type=EventType.TICKET_STATUS,
                actor="system",
                ts=self.parse_ts(raw["status_changed"]),
                title=f"{key} \u2192 {fields['status']}",
                text="",
                raw_refs=(key,),
            ))
        return events
