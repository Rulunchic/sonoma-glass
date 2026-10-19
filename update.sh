#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED="${HOME:?HOME is not set}/.local/share/sonoma-glass"

if [[ "$ROOT" != "$EXPECTED" || ! -d "$ROOT/.git" ]]; then
  echo "Run this from the git clone at $EXPECTED." >&2
  exit 1
fi

git -C "$ROOT" pull --ff-only
"$ROOT/install.sh"
