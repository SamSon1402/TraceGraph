from __future__ import annotations

from tracegraph import TraceGraph


def test_trajectory_is_temporally_ordered(result):
    ts = [s.event.ts for s in result.trajectory.steps]
    assert ts == sorted(ts)


def test_trajectory_starts_with_the_document(result):
    first = result.trajectory.steps[0]
    assert first.event.id == "notion:doc_atlas"   # earliest event = the doc edit


def test_spine_is_the_longest_causal_chain(result):
    spine = result.trajectory.spine
    # doc -> ticket -> (message or status): a 3-node chain
    assert len(spine) >= 3
    assert spine[0] == "notion:doc_atlas"
    assert "jira:ATLAS-482" in spine


def test_steps_carry_their_dependencies(result):
    step_by_id = {s.event.id: s for s in result.trajectory.steps}
    assert "notion:doc_atlas" in step_by_id["jira:ATLAS-482"].depends_on
    assert "jira:ATLAS-482" in step_by_id["slack:atlas-launch#2"].depends_on


def test_pipeline_counts(result):
    assert len(result.events) == 6
    assert len(result.graph.edges) == 4
    assert len(result.trajectory) == 6


def test_run_is_repeatable():
    a = TraceGraph().run("data")
    b = TraceGraph().run("data")
    assert [s.event.id for s in a.trajectory.steps] == [s.event.id for s in b.trajectory.steps]
    assert a.trajectory.spine == b.trajectory.spine
