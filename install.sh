#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME:?HOME is not set}"
SUPPORT="$HOME_DIR/.local/share/sonoma-glass"
THEME="$HOME_DIR/.config/omarchy/themes/sonoma-glass"
HYPRGLASS="$SUPPORT/deps/hyprglass"
COMMIT="$(<"$ROOT/HYPRGLASS-COMMIT")"
REBUILD=0

if [[ "${1:-}" == "--rebuild" ]]; then
  REBUILD=1
elif [[ $# -gt 0 ]]; then
  echo "Usage: ./install.sh [--rebuild]" >&2
  exit 2
fi

if [[ "$ROOT" != "$SUPPORT" ]]; then
  echo "Clone this repository to $SUPPORT, then run ./install.sh from there." >&2
  exit 1
fi

for command in git make c++ pkg-config wayland-scanner hyprctl omarchy; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Missing command: $command" >&2
    echo "On Arch, install base-devel, git, pkgconf, wayland-protocols and Hyprland development files." >&2
    exit 1
  fi
done

if ! pkg-config --exists hyprland pixman-1 libdrm wayland-server; then
  echo "Hyprland development pkg-config files are missing; install the matching Hyprland package." >&2
  exit 1
fi

version="$(hyprctl version | sed -nE 's/^Hyprland ([0-9]+\.[0-9]+)\..*/\1/p' | head -n1)"
if [[ "$version" != "0.56" ]]; then
  echo "This theme's HyprGlass build is pinned for Hyprland 0.56; detected ${version:-unknown}." >&2
  echo "A matching HyprGlass branch/commit must be selected before installing on this version." >&2
  exit 1
fi

if [[ ! -d "$HYPRGLASS/.git" ]]; then
  mkdir -p "$(dirname -- "$HYPRGLASS")"
  git clone --depth 1 --branch hyprland-0.56 https://github.com/hyprnux/hyprglass.git "$HYPRGLASS"
fi

if [[ "$(git -C "$HYPRGLASS" remote get-url origin)" != "https://github.com/hyprnux/hyprglass.git" ]]; then
  echo "Unexpected repository at $HYPRGLASS; refusing to overwrite it." >&2
  exit 1
fi

if [[ "$(git -C "$HYPRGLASS" rev-parse HEAD)" != "$COMMIT" ]]; then
  git -C "$HYPRGLASS" fetch --depth 1 origin "$COMMIT"
  git -C "$HYPRGLASS" checkout --detach "$COMMIT"
fi

if [[ ! -s "$HYPRGLASS/hyprglass.so" || $REBUILD == 1 ]]; then
  make -C "$HYPRGLASS" clean
  make -C "$HYPRGLASS" -j"$(nproc)"
fi

mkdir -p "$THEME"
cp -a "$ROOT/theme/." "$THEME/"
omarchy theme set sonoma-glass

echo "Sonoma Glass installed. The six included wallpapers are available in the Omarchy background picker."
echo "To update later, run: $SUPPORT/update.sh"
