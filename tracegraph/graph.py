"""Reference graph construction, validation and Graphviz export."""

from __future__ import annotations

from .models import Edge, Event, Graph


def build_graph(events: list[Event]) -> Graph:
    nodes = {ev.id: ev for ev in events}
    edges: list[Edge] = []
    for ev in events:
        explicit = {
            t for raw in ev.raw_refs
            for t in [nodes_key_to_id(raw, nodes)] if t
        }
        for target in ev.refs:
            kind = "explicit" if target in explicit else "mention"
            edges.append(Edge(ev.id, target, kind))
    return Graph(nodes=nodes, edges=edges)


def nodes_key_to_id(raw: str, nodes: dict[str, Event]) -> str | None:
    for ev in nodes.values():
        if ev.raw_key == raw:
            return ev.id
    return None


def validate_temporal(graph: Graph) -> list[str]:
    """A reference must point backwards in time.

    If event A references event B, B must have happened no later than A — you cannot
    cite a ticket that does not yet exist. Violations are reported as data anomalies
    rather than silently graphed.
    """
    anomalies: list[str] = []
    for e in graph.edges:
        src, dst = graph.nodes[e.src], graph.nodes[e.dst]
        if dst.ts > src.ts:
            anomalies.append(
                f"{src.id} references {dst.id}, but the target is newer "
                f"({dst.ts.isoformat()} > {src.ts.isoformat()})"
            )
    return anomalies


def to_dot(graph: Graph) -> str:
    """Export the graph in Graphviz DOT for visual inspection (`dot -Tpng`)."""
    color = {"slack": "#c98bff", "jira": "#8b95ff", "notion": "#46e0c0"}
    lines = ["digraph trajectory {", "  rankdir=LR;",
             '  node [shape=box style="rounded,filled" fontname="Helvetica" '
             'fillcolor="#1a1c24" color="#334155" fontcolor="#f4f5f7"];',
             '  edge [color="#8b95ff" fontcolor="#9ea3ad" fontsize=9];']
    for ev in graph.nodes.values():
        label = ev.title.replace('"', "'")
        lines.append(f'  "{ev.id}" [label="{label}\\n{ev.source}" '
                     f'color="{color.get(ev.source, "#334155")}"];')
    for e in graph.edges:
        style = "solid" if e.kind == "explicit" else "dashed"
        lines.append(f'  "{e.src}" -> "{e.dst}" [style={style} label="{e.kind}"];')
    lines.append("}")
    return "\n".join(lines)
