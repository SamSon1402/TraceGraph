.PHONY: install run json dot demo test

install:
	pip install -e ".[dev]"

run:        ## ingest sample data, print the reconstructed trajectory
	python -m tracegraph.cli

json:
	python -m tracegraph.cli --json

dot:        ## emit Graphviz DOT (pipe to: dot -Tpng > graph.png)
	python -m tracegraph.cli --dot

demo:
	python examples/run_demo.py

test:
	pytest -q
