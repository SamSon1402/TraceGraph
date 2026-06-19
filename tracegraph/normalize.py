"""Reference resolution.

A normalized event references others in two ways:

* **Explicit** — a native link field (Jira ``links.to``, a Slack ``refs`` array).
* **Mention** — a raw key or an alias that appears in the event's free text
  ("context is in the Atlas Launch Spec" mentions the doc by title).

The ``Resolver`` indexes every event by its native key and aliases, then resolves both
kinds into the normalized id of the target event. Mention resolution prefers the
longest alias so "Atlas Launch Spec" wins over any shorter fragment.
"""

from __future__ import annotations

from .models import Event


class Resolver:
    def __init__(self, events: list[Event]) -> None:
        # native key / alias  ->  normalized id
        self._index: dict[str, str] = {}
        self._aliases: list[tuple[str, str]] = []  # (alias, normalized_id), longest first
        for ev in events:
            if ev.raw_key:
                self._index[ev.raw_key] = ev.id
                self._aliases.append((ev.raw_key, ev.id))
            for alias in ev.aliases:
                self._index[alias] = ev.id
                self._aliases.append((alias, ev.id))
        self._aliases.sort(key=lambda p: len(p[0]), reverse=True)

    def resolve_key(self, key: str) -> str | None:
        return self._index.get(key)

    def mentions_in(self, text: str) -> list[str]:
        """Return normalized ids whose key/alias is mentioned in ``text``."""
        found: list[str] = []
        for alias, norm_id in self._aliases:
            if alias and alias in text and norm_id not in found:
                found.append(norm_id)
        return found


def resolve_references(events: list[Event]) -> list[Event]:
    """Populate each event's ``refs`` from explicit links and in-text mentions."""
    resolver = Resolver(events)
    for ev in events:
        refs: list[str] = []
        for raw in ev.raw_refs:                       # explicit
            target = resolver.resolve_key(raw)
            if target and target != ev.id and target not in refs:
                refs.append(target)
        for target in resolver.mentions_in(ev.text):  # mentions
            if target != ev.id and target not in refs:
                refs.append(target)
        ev.refs = refs
    return events
