# Ponder — common tasks
# Uses a local virtualenv at .venv. Run `make install` first.

PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help install ingest run eval eval-hard eval-retrieval test clean

help:
	@echo "Ponder — available commands:"
	@echo "  make install         Create .venv and install dependencies"
	@echo "  make ingest          Build the vector index from data/corpus"
	@echo "  make run             Launch the Streamlit chat UI"
	@echo "  make eval            Full evaluation (needs an LLM key)"
	@echo "  make eval-hard       Hard set: paraphrase, multi-source, unanswerable (needs an LLM key)"
	@echo "  make eval-retrieval  Retrieval-only evaluation (no key needed)"
	@echo "  make test            Run the test suite"
	@echo "  make clean           Remove the local index and caches"

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Done. Now: cp .env.example .env  (and add your key), then 'make ingest'."

ingest:
	$(PY) -m ponder.ingest

run:
	.venv/bin/streamlit run app.py

eval:
	$(PY) eval.py

eval-hard:
	$(PY) eval.py --set hard

eval-retrieval:
	$(PY) eval.py --retrieval-only

test:
	$(PY) -m pytest -q

clean:
	rm -rf .chroma .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
