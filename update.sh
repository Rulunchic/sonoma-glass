#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -d "$ROOT/.git" ]]; then
  echo 'Run update.sh from the source git checkout.' >&2
  exit 1
fi
git -C "$ROOT" pull --ff-only
exec "$ROOT/install.sh" --yes "$@"
