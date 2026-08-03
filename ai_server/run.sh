#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; . ./.env; set +a; fi
export ZARA_DATA_DIR="${ZARA_DATA_DIR:-data}"
. .venv/bin/activate
python main.py
