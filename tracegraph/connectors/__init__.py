"""Connectors package."""

from __future__ import annotations

from pathlib import Path

from ..models import Event
from .base import BaseConnector
from .jira import JiraConnector
from .notion import NotionConnector
from .slack import SlackConnector

__all__ = [
    "BaseConnector",
    "SlackConnector",
    "JiraConnector",
    "NotionConnector",
    "load_corpus",
]


def load_corpus(data_dir: str | Path) -> list[Event]:
    """Ingest the bundled Slack + Jira + Notion exports into normalized events."""
    data_dir = Path(data_dir)
    events: list[Event] = []
    events += SlackConnector().load(data_dir / "slack_export.json")
    events += JiraConnector().load(data_dir / "jira_export.json")
    events += NotionConnector().load(data_dir / "notion_export.json")
    return events
