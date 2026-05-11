#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Chutzrit Git Task Push
# @raycast.mode fullOutput
# @raycast.packageName Chutzrit AI Office
# @raycast.icon 🚀

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

exec "$PYTHON" scripts/git_task_push.py
