#!/usr/bin/env python3
"""Remove Sonoma Glass icon files and restore desktop entries it changed."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


HOME = Path.home()
SUPPORT = HOME / ".local/share/sonoma-glass"
STATE = SUPPORT / "desktop-icon-overrides.json"
ICONS = HOME / ".local/share/icons"


def main() -> int:
    if STATE.is_file():
        for item in json.loads(STATE.read_text()):
            target = Path(item["target"])
            backup = Path(item["backup"])
            if item["created"]:
                target.unlink(missing_ok=True)
            elif backup.is_file():
                shutil.copy2(backup, target)
        STATE.unlink()
    for name in ("SonomaGlass", "SonomaGlass-light", "SonomaGlass-dark"):
        theme = ICONS / name
        if (theme / "ATTRIBUTION.txt").is_file():
            shutil.rmtree(theme)
    print("Restored desktop entries and removed the Sonoma Glass icon themes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
