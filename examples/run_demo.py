"""Ingest the sample corpus and print the reconstructed trajectory.

    python examples/run_demo.py
"""

from __future__ import annotations

from pathlib import Path

from tracegraph import TraceGraph

DATA = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    result = TraceGraph().run(DATA)

    print(f"ingested {len(result.events)} events, "
          f"{len(result.graph.edges)} references\n")

    print("trajectory:")
    for s in result.trajectory.steps:
        mark = "*" if s.on_spine else " "
        deps = f"  -> {', '.join(s.depends_on)}" if s.depends_on else ""
        print(f"  {mark} {s.n}. [{s.event.source}] {s.event.actor}: "
              f"{s.event.title}{deps}")

    print("\nspine:", " -> ".join(result.trajectory.spine))
    print("anomalies:", result.anomalies or "none")


if __name__ == "__main__":
    main()
