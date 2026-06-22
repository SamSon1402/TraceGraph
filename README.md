# TraceGraph

**Multimodal ingestion & trajectory reconstruction.**

Agent training data isn't documents — it's *trajectories*: the ordered chain of who did
what, across which tools, referencing what. TraceGraph ingests raw exports from Slack,
Jira and Notion (each with its own native schema), normalizes them into one event
model, resolves the cross-references between them, builds a reference graph, and
reconstructs the multi-step workflow an RL environment would replay.

> Built as a worked example for the **Ooak Data — Data Engineer (Infrastructure)** role:
> *"…work across multimodal data (documents, communications, and tool integrations)."*
> This is the ingestion stage that turns those integrations into structured trajectories.

---

## Pipeline

```
  slack_export.json   jira_export.json   notion_export.json   (heterogeneous schemas)
        │  connectors
        ▼
  Event[]                                   (one unified model)
        │  resolve references  (explicit links + in-text mentions)
        ▼
  reference graph  ──►  temporal validation  (refs must point backwards in time)
        │  reconstruct
        ▼
  Trajectory  (temporally ordered steps + the longest causal "spine")
```

The whole run is repeatable: same exports → same trajectory.

## What it does, concretely

Three different native shapes come in:

| Source | Native fields (excerpt) |
|---|---|
| Slack | `messages[].{ts, user, text, refs}` |
| Jira | `key, created, reporter, fields.{summary,status}, status_changed, links[].to` |
| Notion | `id, title, last_edited, author` |

…and one unified model comes out:

```
03-10 16:20  notion  document.edited  Jane Okafor    refs: —
03-12 09:02  jira    ticket.opened    Diego Ramirez  refs: notion:doc_atlas
03-12 09:14  slack   message.sent     Jane Okafor    refs: —
03-12 09:16  slack   message.sent     Diego Ramirez  refs: jira:ATLAS-482
03-12 09:21  slack   message.sent     Priya Nair     refs: notion:doc_atlas
03-12 09:30  jira    ticket.status    system         refs: jira:ATLAS-482

Reconstructed trajectory
  ◆ 1. Jane Okafor edited — Atlas Launch Spec
  ◆ 2. Diego Ramirez opened — ATLAS-482            → notion:doc_atlas
  ◇ 3. Jane Okafor posted — board approved Project Atlas …
  ◆ 4. Diego Ramirez posted — pushed auth under ATLAS-482 …  → jira:ATLAS-482
  ◇ 5. Priya Nair posted — context is in the Atlas Launch Spec → notion:doc_atlas
  ◇ 6. system moved — ATLAS-482 → In Review        → jira:ATLAS-482

  ◆ spine: notion:doc_atlas → jira:ATLAS-482 → slack:atlas-launch#2
  ✓ temporal consistency OK
```

### The two things worth a close look

- **Reference resolution handles both explicit and implicit links.** Jira's
  `links.to` is an explicit reference; a Slack message that just says *"context is in
  the Atlas Launch Spec"* references the doc only by its **title** — TraceGraph resolves
  that mention back to the right node by indexing every event's keys and aliases.
- **The spine is a real graph algorithm.** It's the longest path in the reference DAG
  (computed with a memoized DFS), i.e. the backbone causal chain
  `doc → ticket → message` — the structure that matters most when replaying the
  workflow as an environment.

Plus a **data-quality gate**: every reference must point backwards in time (you can't
cite a ticket that doesn't exist yet). Violations are reported as anomalies, and the
CLI exits non-zero so it can gate a pipeline.

## Quickstart

```bash
# standard library only — no third-party runtime dependencies
python -m tracegraph.cli                       # ingest + reconstruct (human-readable)
python -m tracegraph.cli --json                # machine-readable
python -m tracegraph.cli --dot > graph.dot     # Graphviz; dot -Tpng graph.dot -o graph.png
python examples/run_demo.py
```

### Library use

```python
from tracegraph import TraceGraph

result = TraceGraph().run("data")
for step in result.trajectory.steps:
    print(step.n, step.event.source, step.event.title, "->", step.depends_on)

print("spine:", result.trajectory.spine)
print("anomalies:", result.anomalies)
```

### Composes with the rest of the pipeline

```
TraceGraph  →  CoherentTwin  →  FidelityGauge
 (structure)    (anonymize)      (QA gate)
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q     # 16 tests: connectors, resolution, graph, temporal validation, trajectory
```

## Layout

```
tracegraph/
├── tracegraph/
│   ├── models.py        # Event, Edge, Graph, Step, Trajectory
│   ├── connectors/      # slack / jira / notion schema adapters
│   ├── normalize.py     # explicit-link + in-text mention resolution
│   ├── graph.py         # graph build · temporal validation · DOT export
│   ├── trajectory.py    # temporal ordering + longest-path spine
│   ├── pipeline.py      # orchestration -> IngestResult
│   └── cli.py
├── data/                # three native exports
├── examples/run_demo.py
└── tests/
```

---
