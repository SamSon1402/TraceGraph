"""Pipeline: ingest -> normalize -> resolve -> graph -> validate -> trajectory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .connectors import load_corpus
from .graph import build_graph, validate_temporal
from .models import Event, Graph, Trajectory
from .normalize import resolve_references
from .trajectory import reconstruct


@dataclass
class IngestResult:
    events: list[Event]
    graph: Graph
    trajectory: Trajectory
    anomalies: list[str]


class TraceGraph:
    """Turn a directory of raw tool exports into a reconstructed trajectory."""

    def run(self, data_dir: str | Path) -> IngestResult:
        events = load_corpus(data_dir)          # ingest (heterogeneous schemas)
        resolve_references(events)              # resolve explicit + mention refs
        graph = build_graph(events)             # reference graph
        anomalies = validate_temporal(graph)    # data-quality: refs must point back
        trajectory = reconstruct(events, graph)  # ordered workflow + spine
        return IngestResult(
            events=events,
            graph=graph,
            trajectory=trajectory,
            anomalies=anomalies,
        )
