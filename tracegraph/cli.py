"""Command-line interface.

    python -m tracegraph.cli                  # ingest sample data, print trajectory
    python -m tracegraph.cli --json
    python -m tracegraph.cli --dot > graph.dot && dot -Tpng graph.dot -o graph.png
    python -m tracegraph.cli --data ./data

Exit code is non-zero when temporal anomalies are found, so the command can gate CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .graph import to_dot
from .pipeline import IngestResult, TraceGraph

_DATA = Path(__file__).resolve().parent.parent / "data"

_DIM = "\033[2m"; _BOLD = "\033[1m"; _GREEN = "\033[32m"; _RED = "\033[31m"
_ACC = "\033[38;5;111m"; _RESET = "\033[0m"

_VERB = {
    "document.edited": "edited",
    "ticket.opened": "opened",
    "ticket.status": "moved",
    "message.sent": "posted",
}


def _print_human(result: IngestResult) -> None:
    g = result.trajectory
    print(f"\n{_BOLD}TraceGraph{_RESET}  {_DIM}3 sources \u2192 1 trajectory{_RESET}")
    print(f"{_DIM}{'-'*64}{_RESET}")

    print(f"\n{_BOLD}Unified events{_RESET}  "
          f"{_DIM}{len(result.events)} events · {len(result.graph.edges)} references{_RESET}")
    for ev in sorted(result.events, key=lambda e: e.ts):
        refs = ", ".join(ev.refs) if ev.refs else "\u2014"
        print(f"  {ev.ts.strftime('%m-%d %H:%M')}  {ev.source:7} {str(ev.type):16} "
              f"{ev.actor:14} {_DIM}refs: {refs}{_RESET}")

    print(f"\n{_BOLD}Reconstructed trajectory{_RESET}")
    for s in g.steps:
        marker = f"{_ACC}\u25c6{_RESET}" if s.on_spine else f"{_DIM}\u25c7{_RESET}"
        dep = ""
        if s.depends_on:
            dep = f"  {_DIM}\u2192 {', '.join(s.depends_on)}{_RESET}"
        title = s.event.title if len(s.event.title) <= 54 else s.event.title[:53] + "\u2026"
        print(f"  {marker} {s.n}. {_BOLD}{s.event.actor}{_RESET} "
              f"{_VERB.get(str(s.event.type), '')} \u2014 {title}{dep}")

    spine = " \u2192 ".join(g.spine)
    print(f"\n  {_ACC}\u25c6 spine{_RESET} {_DIM}(longest causal chain){_RESET}: {spine}")

    if result.anomalies:
        print(f"\n  {_RED}anomalies:{_RESET}")
        for a in result.anomalies:
            print(f"    {_RED}\u2717{_RESET} {a}")
    else:
        print(f"\n  {_GREEN}\u2713 temporal consistency OK{_RESET} "
              f"{_DIM}(every reference points backwards in time){_RESET}")
    print()


def _to_json(result: IngestResult) -> dict:
    return {
        "events": [
            {"id": e.id, "source": e.source, "type": str(e.type), "actor": e.actor,
             "ts": e.ts.isoformat(), "title": e.title, "refs": e.refs}
            for e in result.events
        ],
        "edges": [{"src": e.src, "dst": e.dst, "kind": e.kind} for e in result.graph.edges],
        "trajectory": [
            {"n": s.n, "event": s.event.id, "depends_on": list(s.depends_on),
             "on_spine": s.on_spine}
            for s in result.trajectory.steps
        ],
        "spine": result.trajectory.spine,
        "anomalies": result.anomalies,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tracegraph", description=__doc__)
    p.add_argument("--data", type=Path, default=_DATA)
    p.add_argument("--json", action="store_true")
    p.add_argument("--dot", action="store_true", help="emit Graphviz DOT")
    args = p.parse_args(argv)

    result = TraceGraph().run(args.data)

    if args.dot:
        print(to_dot(result.graph))
    elif args.json:
        print(json.dumps(_to_json(result), indent=2, ensure_ascii=False))
    else:
        _print_human(result)

    return 0 if not result.anomalies else 1


if __name__ == "__main__":
    sys.exit(main())
