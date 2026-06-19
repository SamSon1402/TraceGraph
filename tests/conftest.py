from __future__ import annotations

from pathlib import Path

import pytest

from tracegraph import TraceGraph
from tracegraph.connectors import load_corpus

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def events():
    return load_corpus(DATA)


@pytest.fixture
def result():
    return TraceGraph().run(DATA)
