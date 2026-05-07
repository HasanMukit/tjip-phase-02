#!/usr/bin/env bash
# Build the search index and serve the site locally for preview.
# search-index.json is gitignored; CI rebuilds it on deploy.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_index.py
PORT="${PORT:-8000}"
echo "Serving on http://localhost:${PORT}/  (Ctrl-C to stop)"
exec python3 -m http.server "$PORT"
