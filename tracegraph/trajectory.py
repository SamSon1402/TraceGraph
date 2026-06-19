"""Trajectory reconstruction.

A trajectory is the events in temporal order, each annotated with what it builds on.
On top of that ordering we extract the **spine**: the longest causal chain in the
reference DAG (doc -> ticket -> message -> ...), which is the backbone of the workflow
an RL environment would replay. The spine is computed as a longest path in the DAG via
memoized depth-first search.
"""

from __future__ import annotations

from functools import lru_cache

from .models import Event, Graph, Step, Trajectory


def reconstruct(events: list[Event], graph: Graph) -> Trajectory:
    ordered = sorted(events, key=lambda e: (e.ts, e.source, e.id))
    spine = set(_longest_chain(graph))
    steps = [
        Step(
            n=i + 1,
            event=ev,
            depends_on=tuple(ev.refs),
            on_spine=ev.id in spine,
        )
        for i, ev in enumerate(ordered)
    ]
    spine_chrono = sorted(spine, key=lambda nid: graph.nodes[nid].ts)
    return Trajectory(steps=steps, spine=spine_chrono)


def _longest_chain(graph: Graph) -> list[str]:
    """Longest path in the reference DAG (edges point from newer to older events)."""

    @lru_cache(maxsize=None)
    def best_from(node_id: str) -> tuple[int, tuple[str, ...]]:
        best_len, best_path = 1, (node_id,)
        for e in graph.out_edges(node_id):
            length, path = best_from(e.dst)
            if length + 1 > best_len:
                best_len, best_path = length + 1, (node_id, *path)
        return best_len, best_path

    if not graph.nodes:
        return []
    best = max((best_from(nid) for nid in graph.nodes), key=lambda t: t[0])
    # reverse so the chain reads chronologically (root -> leaf)
    return list(reversed(best[1]))
