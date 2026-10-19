#!/usr/bin/env python3
"""Install a pinned upstream WhiteSur icon theme in the user's icon directory."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REVISION = "73d8040da51a9ed74e47c7366e7e9ff437601a5c"
ARCHIVE_URL = f"https://codeload.github.com/vinceliuice/WhiteSur-icon-theme/zip/{REVISION}"
THEME_BASE = "SonomaGlass"


def main() -> int:
    data_home = Path.home() / ".local/share/icons"
    cache_home = Path.home() / ".cache/sonoma-glass/icons"
    archive = cache_home / f"whitesur-{REVISION}.zip"
    theme = data_home / f"{THEME_BASE}-dark"
    attribution = theme / "ATTRIBUTION.txt"
    if theme.exists() and not attribution.exists():
        raise SystemExit(f"Refusing to replace an unrelated icon theme: {theme}")
    data_home.mkdir(parents=True, exist_ok=True)
    cache_home.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="sonoma-glass-whitesur-") as temp_dir:
        if not archive.is_file():
            partial = archive.with_suffix(".zip.part")
            request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "Sonoma-Glass-Theme"})
            print("Downloading the pinned WhiteSur icon theme…", flush=True)
            with urllib.request.urlopen(request, timeout=180) as response, partial.open("wb") as output:
                shutil.copyfileobj(response, output)
            partial.replace(archive)
        else:
            print("Using the cached pinned WhiteSur icon theme.", flush=True)

        with zipfile.ZipFile(archive) as bundle:
            root = next(
                (name.split("/", 1)[0] for name in bundle.namelist() if name.endswith("/install.sh")),
                None,
            )
            if root is None:
                raise RuntimeError("WhiteSur archive does not contain install.sh")
            source = Path(temp_dir) / root
            for member in bundle.infolist():
                path = Path(member.filename)
                if path.is_absolute() or ".." in path.parts:
                    raise RuntimeError("WhiteSur archive contains an unsafe path")
                bundle.extract(member, temp_dir)

        subprocess.run(
            [
                "bash",
                str(source / "install.sh"),
                "--dest",
                str(data_home),
                "--name",
                THEME_BASE,
                "--theme",
                "default",
            ],
            check=True,
        )

        for variant in ("SonomaGlass", "SonomaGlass-light", "SonomaGlass-dark"):
            variant_dir = data_home / variant
            license_file = source / "COPYING"
            if license_file.is_file():
                shutil.copy2(license_file, variant_dir / "COPYING")
            (variant_dir / "ATTRIBUTION.txt").write_text(
                "WhiteSur icon theme by vinceliuice and contributors.\n"
                "Source: https://github.com/vinceliuice/WhiteSur-icon-theme\n"
                f"Pinned revision: {REVISION}\n"
                "License: GNU General Public License v3.0.\n"
            )

        apps = theme / "apps/scalable"
        for alias, source_name in {
            "vesktop.svg": "Vesktop.svg",
            "org.telegram.desktop.svg": "telegram.svg",
            "com.ayugram.desktop.svg": "telegram.svg",
            "omarchy-discord.svg": "discord.svg",
        }.items():
            original = apps / source_name
            if original.is_file():
                alias_path = apps / alias
                if alias_path.exists() or alias_path.is_symlink():
                    alias_path.unlink()
                alias_path.symlink_to(source_name)

    print(f"Installed complete WhiteSur app and folder icons in {theme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
