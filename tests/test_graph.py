from __future__ import annotations

from datetime import timedelta

from tracegraph.graph import build_graph, to_dot, validate_temporal
from tracegraph.normalize import resolve_references


def test_graph_has_expected_edges(result):
    edges = {(e.src, e.dst) for e in result.graph.edges}
    assert ("jira:ATLAS-482", "notion:doc_atlas") in edges
    assert ("jira:ATLAS-482#status", "jira:ATLAS-482") in edges
    assert ("slack:atlas-launch#2", "jira:ATLAS-482") in edges
    assert ("slack:atlas-launch#3", "notion:doc_atlas") in edges


def test_edge_kinds_classified(result):
    by_pair = {(e.src, e.dst): e.kind for e in result.graph.edges}
    assert by_pair[("jira:ATLAS-482", "notion:doc_atlas")] == "explicit"
    assert by_pair[("slack:atlas-launch#3", "notion:doc_atlas")] == "mention"


def test_sample_corpus_is_temporally_consistent(result):
    assert result.anomalies == []


def test_future_reference_is_flagged(events):
    resolve_references(events)
    graph = build_graph(events)
    # make the doc newer than everything that references it -> anomaly
    doc = graph.nodes["notion:doc_atlas"]
    doc.ts = doc.ts + timedelta(days=365)
    anomalies = validate_temporal(graph)
    assert anomalies
    assert any("notion:doc_atlas" in a for a in anomalies)


def test_dot_export_is_wellformed(result):
    dot = to_dot(result.graph)
    assert dot.startswith("digraph trajectory {")
    assert dot.rstrip().endswith("}")
    assert "->" in dot
