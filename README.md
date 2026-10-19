# Sonoma Glass for Omarchy

macOS-inspired Omarchy theme with Apple-blue accents, compact spacing, translucent Foot, Hyprland blur, and the HyprGlass Pomme preset. The repository includes the six Macintosh wallpapers selected for this theme. It does not include Apple aerial videos or other wallpaper collections.

## Requirements

- Omarchy with Hyprland **0.56.x**
- Arch build tools and Hyprland development files: `base-devel`, `git`, `pkgconf`, `wayland-protocols`, and `hyprland`
- A normal graphical Omarchy session for applying the theme

The installer builds the pinned HyprGlass revision locally against the installed Hyprland headers. It does not install packages with `sudo`.

## Install

```bash
git clone https://github.com/Rulunchic/sonoma-glass.git ~/.local/share/sonoma-glass
cd ~/.local/share/sonoma-glass
./install.sh
```

This installs the theme files under `~/.config/omarchy/themes/sonoma-glass`, builds HyprGlass under `~/.local/share/sonoma-glass/deps/hyprglass`, and applies the theme. The six bundled JPEGs are placed in the theme's `backgrounds/` folder, so the normal Omarchy wallpaper picker can select them. `Blue_Computer.jpg` is the default wallpaper.

## Update

```bash
~/.local/share/sonoma-glass/update.sh
```

The updater fast-forwards the Git checkout, refreshes the installed theme files and reapplies Sonoma Glass. To rebuild HyprGlass after a compatible Hyprland update, run `~/.local/share/sonoma-glass/install.sh --rebuild`.

## Remove

Select another theme with `omarchy theme set <name>`, then remove the theme and checkout:

```bash
rm -rf ~/.config/omarchy/themes/sonoma-glass
rm -rf ~/.local/share/sonoma-glass
```

## Wallpaper credits

The six Macintosh wallpaper images are by [Basic Apple Guy](https://basicappleguy.com/haberdashery/macintoshwallpapers). They are included here at the repository owner's request; please use them for personal desktop wallpaper use and consult the original page for the creator's terms. This project is unofficial and is not affiliated with Apple or Basic Apple Guy.

## Licenses

The theme configuration and installer scripts in this repository are provided under the MIT License. HyprGlass is a separate project; its MIT license is included as `HYPRGLASS-LICENSE`. Wallpaper artwork is not covered by either code license.
