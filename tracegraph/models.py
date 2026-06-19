"""Core data models. Plain, serializable dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    DOCUMENT_EDITED = "document.edited"
    TICKET_OPENED = "ticket.opened"
    TICKET_STATUS = "ticket.status"
    MESSAGE_SENT = "message.sent"

    def __str__(self) -> str:
        return self.value


@dataclass
class Event:
    """One normalized event in the unified model.

    Connectors emit these with ``raw_refs`` (native reference strings) and ``aliases``
    (strings by which this event can be mentioned elsewhere). The pipeline's resolution
    step turns those into ``refs`` — normalized ids of other events.
    """

    id: str                      # normalized id, e.g. "jira:ATLAS-482"
    source: str                  # slack | jira | notion
    type: EventType
    actor: str
    ts: datetime
    title: str
    text: str = ""               # searched for in-text mentions
    raw_key: str | None = None   # native id others may reference (e.g. "ATLAS-482")
    aliases: tuple[str, ...] = ()  # extra strings that resolve to this event
    raw_refs: tuple[str, ...] = ()  # native reference strings to resolve
    refs: list[str] = field(default_factory=list)  # resolved normalized ids


@dataclass(frozen=True)
class Edge:
    src: str   # event that makes the reference
    dst: str   # event/artifact it points at
    kind: str  # "explicit" (link field) | "mention" (found in text)


@dataclass
class Graph:
    nodes: dict[str, Event]
    edges: list[Edge] = field(default_factory=list)

    def out_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.src == node_id]

    def in_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.dst == node_id]


@dataclass(frozen=True)
class Step:
    """One step of a reconstructed trajectory."""

    n: int
    event: Event
    depends_on: tuple[str, ...]   # normalized ids this step builds on
    on_spine: bool                # part of the longest causal chain


@dataclass
class Trajectory:
    steps: list[Step]
    spine: list[str]              # normalized ids of the critical (longest) path

    def __len__(self) -> int:
        return len(self.steps)
