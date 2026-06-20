#!/usr/bin/env bash
# MaxiManage — one-command launcher.
# Builds the React frontend and starts the FastAPI server, which serves both
# the API (/api/*) and the built single-page app on http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"

echo "▶ Building frontend…"
( cd frontend && npm install --no-audit --no-fund && npm run build )

echo "▶ Setting up backend…"
cd backend
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

echo "▶ Starting MaxiManage on http://localhost:8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
