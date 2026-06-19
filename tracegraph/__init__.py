"""TraceGraph — multimodal ingestion & trajectory reconstruction.

Agent training data isn't documents, it's *trajectories*: the ordered chain of who did
what, across which tools, referencing what. TraceGraph ingests raw exports from Slack,
Jira and Notion (each with its own native schema), normalizes them into one event
model, resolves the cross-references between them (explicit links *and* in-text
mentions), builds a reference graph, and reconstructs the multi-step workflow an RL
environment would replay.

    >>> from tracegraph import TraceGraph
    >>> result = TraceGraph().run("data")
    >>> [step.event.title for step in result.trajectory.steps][:2]
    ['Atlas Launch Spec', 'ATLAS-482']
    >>> result.anomalies
    []
"""

from .models import Edge, Event, EventType, Graph, Step, Trajectory
from .pipeline import IngestResult, TraceGraph

__all__ = [
    "TraceGraph",
    "IngestResult",
    "Event",
    "EventType",
    "Graph",
    "Edge",
    "Trajectory",
    "Step",
]

__version__ = "0.1.0"
