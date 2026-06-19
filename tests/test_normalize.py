from __future__ import annotations

from datetime import timezone

from tracegraph.connectors import load_corpus
from tracegraph.models import EventType
from tracegraph.normalize import resolve_references


def test_three_schemas_normalize_to_one_model(events):
    # 3 slack messages + 1 ticket + 1 status + 1 doc = 6 events
    assert len(events) == 6
    sources = {e.source for e in events}
    assert sources == {"slack", "jira", "notion"}
    # every event has the same shape regardless of origin
    for e in events:
        assert e.id and e.actor and isinstance(e.type, EventType)
        assert e.ts.tzinfo == timezone.utc


def test_jira_emits_ticket_and_status(events):
    types = [e.type for e in events if e.source == "jira"]
    assert EventType.TICKET_OPENED in types
    assert EventType.TICKET_STATUS in types


def test_explicit_link_resolves(events):
    resolve_references(events)
    ticket = next(e for e in events if e.id == "jira:ATLAS-482")
    assert "notion:doc_atlas" in ticket.refs       # links.to -> doc


def test_in_text_mention_resolves(events):
    resolve_references(events)
    # message 3 mentions the doc only by its title, not by key
    msg3 = next(e for e in events if e.id.endswith("#3"))
    assert "notion:doc_atlas" in msg3.refs


def test_message_keyword_mention_resolves(events):
    resolve_references(events)
    msg2 = next(e for e in events if e.id.endswith("#2"))
    assert "jira:ATLAS-482" in msg2.refs
