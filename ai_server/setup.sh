#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
mkdir -p data database storage sample_data models/piper certs
python scripts/download_models.py
python scripts/init_database.py
if [ ! -f certs/server.key ] || [ ! -f certs/server.crt ]; then
  openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/server.key -out certs/server.crt -days 365 -subj "/CN=zara-ai.local"
fi
cp -n .env.example .env
