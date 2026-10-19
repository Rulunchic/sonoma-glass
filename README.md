# Sonoma Glass for Omarchy

macOS-inspired Omarchy theme with Apple-blue accents, compact spacing, translucent Foot, stronger Hyprland blur, the HyprGlass Pomme preset, and a full Big Sur-style icon theme for applications, folders, devices, and file types. The repository includes the six Macintosh wallpapers selected for this theme. It does not include Apple aerial videos or other wallpaper collections.

## Requirements

- Omarchy with Hyprland **0.56.x**
- Arch build tools and Hyprland development files: `base-devel`, `git`, `pkgconf`, `wayland-protocols`, `hyprland`, `python`, and `gtk4` (for `gtk-update-icon-cache`)
- A normal graphical Omarchy session for applying the theme

The installer builds the pinned HyprGlass revision locally against the installed Hyprland headers. It does not install packages with `sudo`.

## Install

Install the theme through Omarchy's built-in theme installer:

```bash
omarchy theme install https://github.com/Rulunchic/sonoma-glass.git
bash ~/.config/omarchy/themes/sonoma-glass/install.sh
```

Omarchy installs the palette, icon theme selection, and six wallpapers directly. It intentionally filters `hyprland.lua` and `foot.ini` from downloaded theme repos, so the second command builds HyprGlass, installs the pinned WhiteSur Big Sur icon theme with folder and file icons, adds the matching artwork from the linked Big Sur app pack, maps missing installed-app names, installs local Hyprland and terminal settings, and reapplies the theme. Telegram Desktop and Vesktop receive explicit icon-name aliases. The installer keeps an updateable checkout in `~/.local/share/sonoma-glass` and removes the git marker from the local theme copy, allowing Omarchy to load the custom settings.

The six JPEGs are placed in the theme's `backgrounds/` folder, so the normal Omarchy wallpaper picker can select them. `Blue_Computer.jpg` is the default wallpaper.

## Update

```bash
~/.local/share/sonoma-glass/update.sh
```

The updater fast-forwards the Git checkout, refreshes the installed theme files and reapplies Sonoma Glass. To rebuild HyprGlass after a compatible Hyprland update, run `~/.local/share/sonoma-glass/install.sh --rebuild`. To refresh the Big Sur icons from upstream, add `--refresh-icons`.

## Remove

Restore the menu entries changed for absolute-path icons, then select another theme and remove the theme and checkout:

```bash
omarchy theme set <name>
python3 ~/.local/share/sonoma-glass/uninstall-icons.py
rm -rf ~/.config/omarchy/themes/sonoma-glass
rm -rf ~/.local/share/sonoma-glass
```

## Wallpaper credits

The six Macintosh wallpaper images are by [Basic Apple Guy](https://basicappleguy.com/haberdashery/macintoshwallpapers). They are included here at the repository owner's request; please use them for personal desktop wallpaper use and consult the original page for the creator's terms. This project is unofficial and is not affiliated with Apple or Basic Apple Guy.

The base app, folder, device, and file icons come from [WhiteSur Icon Theme](https://github.com/vinceliuice/WhiteSur-icon-theme), pinned to revision `73d8040`; the upstream GPL-3.0 license is installed alongside the icon theme. Matching Big Sur app artwork by [Nuno Coelho Santos](https://github.com/nunosans/big-sur-icons) is downloaded during setup rather than bundled here and follows its [CC BY-NC 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/).

## Licenses

The theme configuration and installer scripts in this repository are provided under the MIT License. HyprGlass is a separate project; its MIT license is included as `HYPRGLASS-LICENSE`. Wallpaper artwork is not covered by either code license.
