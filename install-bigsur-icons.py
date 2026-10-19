#!/usr/bin/env python3
"""Install the upstream Big Sur ICNS artwork into a user XDG icon theme."""

from __future__ import annotations

import re
import shutil
import struct
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ARCHIVE_URL = "https://codeload.github.com/nunosans/big-sur-icons/zip/refs/heads/main"
THEME_NAME = "SonomaGlass-dark"
ALIASES = {
    "Android Studio": ["android-studio", "androidstudio", "com.google.AndroidStudio"],
    "Dropbox": ["dropbox", "com.dropbox.Dropbox"],
    "Figma": ["figma", "figma-linux"],
    "Firefox": ["firefox", "org.mozilla.firefox"],
    "Slack": ["slack", "com.slack.Slack"],
    "Spotify": ["spotify", "com.spotify.Client"],
    "Sublime Text": ["sublime-text", "sublime_text"],
    "WhatsApp": ["whatsapp", "com.whatsapp.WhatsApp"],
    "Zoom": ["zoom", "Zoom.us", "us.zoom.Zoom"],
}


def icon_png(data: bytes) -> bytes:
    if len(data) < 8 or data[:4] != b"icns":
        raise ValueError("not an ICNS file")
    chunks: list[tuple[int, bytes]] = []
    offset = 8
    while offset + 8 <= len(data):
        length = struct.unpack_from(">I", data, offset + 4)[0]
        if length < 8 or offset + length > len(data):
            raise ValueError("invalid ICNS chunk")
        payload = data[offset + 8 : offset + length]
        if payload.startswith(b"\x89PNG\r\n\x1a\n") and len(payload) >= 24:
            width, height = struct.unpack_from(">II", payload, 16)
            chunks.append((width * height, payload))
        offset += length
    if not chunks:
        raise ValueError("ICNS file contains no PNG icon")
    return max(chunks, key=lambda item: item[0])[1]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def main() -> int:
    force = "--force" in sys.argv[1:]
    archive_arg = next((Path(arg).expanduser() for arg in sys.argv[1:] if arg != "--force"), None)
    data_home = Path.home() / ".local/share/icons"
    cache_home = Path.home() / ".cache/sonoma-glass/icons"
    cached_archive = cache_home / "big-sur-icons.zip"
    target = data_home / THEME_NAME
    apps = target / "apps/scalable"
    marker = target / ".sonoma-glass-bigsur-overlay"

    if not apps.is_dir():
        print(f"Install the Sonoma Glass icon base first: {target}", file=sys.stderr)
        return 1
    if marker.exists() and not force:
        print(f"Big Sur icons already installed: {target}")
        return 0

    data_home.mkdir(parents=True, exist_ok=True)
    cache_home.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sonoma-glass-icons-", dir=data_home) as temp_dir:
        archive = archive_arg
        if archive is None:
            if force or not cached_archive.is_file():
                partial = cached_archive.with_suffix(".zip.part")
                request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "Sonoma-Glass-Theme"})
                print("Downloading Big Sur icons from nunosans/big-sur-icons…", flush=True)
                with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as output:
                    shutil.copyfileobj(response, output)
                partial.replace(cached_archive)
            else:
                print("Using the cached Big Sur app icons.", flush=True)
            archive = cached_archive
        elif not archive.is_file():
            print(f"Icon archive not found: {archive}", file=sys.stderr)
            return 2

        staging = Path(temp_dir) / "BigSur-overlay"
        app_dir = staging / "apps/scalable"
        app_dir.mkdir(parents=True)
        with zipfile.ZipFile(archive) as bundle:
            for name in bundle.namelist():
                if not name.startswith("big-sur-icons-main/Icons/") or not name.endswith(".icns"):
                    continue
                source_name = Path(name).stem
                try:
                    image = icon_png(bundle.read(name))
                except (ValueError, zipfile.BadZipFile) as error:
                    print(f"Skipping {source_name}: {error}", file=sys.stderr)
                    continue
                names = [slug(source_name), *ALIASES.get(source_name, [])]
                for icon_name in set(names):
                    (app_dir / f"{icon_name}.png").write_bytes(image)

        (staging / "BigSur-ATTRIBUTION.txt").write_text(
            "Big Sur application icon artwork is by Nuno Coelho Santos.\n"
            "Source: https://github.com/nunosans/big-sur-icons\n"
            "License: Creative Commons Attribution-NonCommercial 4.0 International.\n"
            "The source artwork is downloaded from the original repository during installation.\n"
        )
        for icon in app_dir.glob("*.png"):
            destination = apps / icon.name
            if not destination.exists():
                shutil.copy2(icon, destination)
        shutil.copy2(staging / "BigSur-ATTRIBUTION.txt", target / "BigSur-ATTRIBUTION.txt")
        marker.write_text("Supplemental artwork from nunosans/big-sur-icons.\n")
    print(f"Added matching Big Sur application icons to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
