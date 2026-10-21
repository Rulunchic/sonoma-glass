#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SUPPORT="${HOME:?HOME is not set}/.local/share/sonoma-glass"
THEME="$HOME/.config/omarchy/themes/sonoma-glass"

# Omarchy removes executable theme configs from a cloned theme. Keep an
# independent checkout before turning that folder into a trusted local theme.
if [[ "$ROOT" == "$THEME" ]]; then
  SOURCE="$SUPPORT/source"
  if [[ ! -d "$SOURCE/.git" ]]; then
    mkdir -p "$SUPPORT"
    if [[ -d "$ROOT/.git" ]]; then
      git clone "$ROOT" "$SOURCE"
      git -C "$SOURCE" remote set-url origin https://github.com/Rulunchic/sonoma-glass.git
    else
      git clone https://github.com/Rulunchic/sonoma-glass.git "$SOURCE"
    fi
  elif [[ -d "$ROOT/.git" ]]; then
    git -C "$SOURCE" pull --ff-only
  fi
  exec "$SOURCE/install.sh" "$@"
fi
if ! command -v python3 >/dev/null; then
  echo 'Python 3.11+ is required.' >&2
  exit 1
fi
exec python3 "$ROOT/runtime/cli.py" install --source "$ROOT" "$@"
