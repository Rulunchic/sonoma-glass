#!/usr/bin/env python3
"""Fill WhiteSur gaps for installed desktop entries and theme absolute-path icons."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


THEME = Path.home() / ".local/share/icons/SonomaGlass-dark"
APPS = THEME / "apps/scalable"
APP_DIRS = [Path("/usr/share/applications"), Path.home() / ".local/share/applications"]
SUPPORT = Path.home() / ".local/share/sonoma-glass"
BACKUPS = SUPPORT / "desktop-icon-backups"
STATE = SUPPORT / "desktop-icon-overrides.json"

EXACT = {
    "Albion Online": "applications-games",
    "Arctic Drive Playtest": "applications-games",
    "Deadlock": "applications-games",
    "Geometry Dash": "applications-games",
    "Disk Usage": "org.gnome.baobab",
    "ArtCraft Launcher": "applications-graphics",
    "DeckCraft": "applications-games",
    "EffectCraft": "applications-graphics",
    "FilmCraft": "multimedia-video-player",
    "SoundCraft": "audio-player",
    "WordCraft": "accessories-text-editor",
    "Antigravity IDE": "code",
    "Concat": "audio-player",
    "Dota 2 Mod Manager": "applications-games",
    "Image Viewer": "accessories-image-viewer",
    "INCY": "accessories-notes",
    "Sober": "applications-games",
    "PureRef": "applications-interfacedesign",
    "XMCL": "applications-games",
    "AmneziaVPN": "airvpn",
    "Aether": "browser",
    "AudioRelay": "audio-player",
    "ChatGPT": "openai",
    "cliamp": "audio-player",
    "Moonlight": "multimedia-video-player",
    "Tensaku": "accessories-text-editor",
    "Limine-snapper-restore": "yast-snapper",
    "Micro": "terminal",
    "Run Software": "gnome-software",
    "Omacalc": "accessories-calculator",
    "Omacut": "applications-graphics",
    "Omawrite": "accessories-text-editor",
    "KNewStuff Dialog": "system-software-install",
    "scrcpy": "accessories-camera",
    "Voxtype Configuration": "audio-recorder",
    "Portal": "applications-system",
    "Vesktop": "discord",
    "Telegram": "telegram",
    "AyuGram Desktop": "telegram",
}


def icon_exists(name: str) -> bool:
    return any((APPS / f"{name}.{suffix}").exists() for suffix in ("svg", "png", "xpm"))


def choose(name: str, icon: str) -> str:
    if name in EXACT:
        return EXACT[name]
    key = f"{name} {icon}".casefold()
    rules = [
        (("discord", "vesktop"), "discord"),
        (("telegram", "ayugram"), "telegram"),
        (("steam_icon", "game", "dota", "counter-strike", "albion"), "applications-games"),
        (("vpn",), "airvpn"),
        (("disk", "baobab", "usage"), "org.gnome.baobab"),
        (("chatgpt", "openai"), "openai"),
        (("audio", "music", "sound", "microphone"), "audio-player"),
        (("video", "film", "movie"), "multimedia-video-player"),
        (("image", "photo", "picture", "paint", "design", "art"), "applications-graphics"),
        (("text", "write", "editor", "note", "micro"), "accessories-text-editor"),
        (("calculator", "calc", "math"), "accessories-calculator"),
        (("browser", "web", "aether"), "browser"),
        (("java",), "applications-java"),
        (("terminal", "console", "shell"), "terminal"),
        (("software", "store", "install", "package"), "gnome-software"),
        (("phone", "scrcpy", "mobile"), "accessories-camera"),
    ]
    for needles, destination in rules:
        if any(needle in key for needle in needles):
            return destination
    return "applications-system"


def entry_values(path: Path) -> tuple[str, str] | None:
    section = ""
    name = ""
    icon = ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
        elif section == "Desktop Entry":
            if line.startswith("Name="):
                name = line.split("=", 1)[1]
            elif line.startswith("Icon="):
                icon = line.split("=", 1)[1]
    return (name, icon) if name and icon else None


def rewrite_icon(path: Path, alias: str) -> None:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    section = ""
    rewritten = False
    for index, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
        elif section == "Desktop Entry" and stripped.startswith("Icon="):
            ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            lines[index] = f"Icon={alias}{ending}"
            rewritten = True
            break
    if rewritten:
        path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    if not APPS.is_dir():
        raise SystemExit(f"Install the Sonoma Glass icon theme first: {THEME}")
    SUPPORT.mkdir(parents=True, exist_ok=True)
    backups = json.loads(STATE.read_text()) if STATE.exists() else []
    known_backups = {item["target"] for item in backups}

    entries: dict[str, Path] = {}
    for directory in APP_DIRS:
        if directory.is_dir():
            entries.update({path.name: path for path in directory.glob("*.desktop")})

    aliases = 0
    overrides = 0
    for path in entries.values():
        values = entry_values(path)
        if not values:
            continue
        name, icon = values
        source_name = choose(name, icon)
        if icon.startswith("/"):
            alias = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
            source = APPS / f"{source_name}.svg"
            if not source.is_file():
                continue
            user_apps = Path.home() / ".local/share/applications"
            target = path if path.parent == user_apps else user_apps / path.name
            key = str(target)
            if key not in known_backups:
                BACKUPS.mkdir(parents=True, exist_ok=True)
                backup = BACKUPS / path.name
                created = target != path and not target.exists()
                backup.unlink(missing_ok=True)
                shutil.copy2(path if created else target, backup)
                backups.append({"target": key, "backup": str(backup), "created": created})
                known_backups.add(key)
            if target != path and not target.exists():
                shutil.copy2(path, target)
            target.chmod(target.stat().st_mode | 0o200)
            rewrite_icon(target, alias)
            alias_path = APPS / f"{alias}.svg"
            if not alias_path.exists():
                alias_path.symlink_to(source.name)
            overrides += 1
            continue

        if icon_exists(icon):
            continue
        source = APPS / f"{source_name}.svg"
        if source.is_file():
            destination = APPS / f"{icon}.svg"
            if not destination.exists():
                destination.symlink_to(source.name)
                aliases += 1

    STATE.write_text(json.dumps(backups, indent=2) + "\n")
    print(f"Mapped {aliases} missing app icons to matching WhiteSur designs; added {overrides} path-icon overrides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
