#!/bin/sh
set -eu
cd "$(dirname "$0")/example"
export PYTHONPATH="$(dirname "$PWD")/.local_runtime${PYTHONPATH:+:$PYTHONPATH}"
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
