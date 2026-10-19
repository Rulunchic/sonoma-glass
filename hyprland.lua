-- This local theme uses only options supported by installed Hyprland 0.56.2.
-- Returning to another theme restores Omarchy's defaults on config reload.
local active = { colors = { "rgba(64b5ffff)", "rgba(ffffffff)" }, angle = 135 }

hl.config({
  general = {
    gaps_in = 4,
    gaps_out = 7,
    border_size = 2,
    col = { active_border = active, inactive_border = "rgba(ffffff24)" },
  },
  decoration = {
    rounding = 16,
    rounding_power = 3.8,
    shadow = { enabled = true, range = 24, render_power = 3, color = "rgba(00000055)" },
    blur = {
      enabled = true,
      size = 30,
      passes = 4,
      new_optimizations = true,
      ignore_opacity = true,
      popups = true,
      xray = false,
      noise = 0.012,
      contrast = 1.08,
      brightness = 1.06,
      vibrancy = 0.32,
    },
  },
  group = { col = { border_active = active, border_inactive = "rgba(ffffff24)" } },
})

-- Let the compositor blend window surfaces with the blurred desktop beneath.
-- Keep Foot crisp and give its own background alpha in foot.ini instead.
hl.window_rule({ match = { class = ".*" }, opacity = "0.90 0.84" })
hl.window_rule({ match = { class = "foot" }, opacity = "1 1" })

-- Exclude the wallpaper, click-catcher and image-selector layers.
hl.layer_rule({
  match = { namespace = "^(omarchy-bar|omarchy-menu|omarchy-emojis|omarchy-clipboard|omarchy-keyboard-panel|omarchy-osd|omarchy-notifications|omarchy-polkit|omarchy-network-qr)$" },
  blur = true,
  ignore_alpha = 0.22,
})

-- install.sh builds HyprGlass for this machine and puts it here.
hl.plugin.load(os.getenv("HOME") .. "/.local/share/sonoma-glass/deps/hyprglass/hyprglass.so")

local function configure_hyprglass()
  if not hl.plugin.hyprglass then return end
  local hg = hl.plugin.hyprglass
  hg.config({
    default_theme = "dark",
    default_preset = "pomme",
    tint_color = 0x78aef020,
    skip_opaque_windows = false,
    layers = { enabled = true },
  })

  hg.preset("sonoma-terminal", {
    inherits = "pomme",
    blur_strength = 1.25,
    blur_iterations = 3,
  })
  hg.preset("sonoma-menu", {
    inherits = "pomme",
    glass_opacity = 0.88,
  })
  hl.window_rule({ match = { class = "foot" }, tag = "+hyprglass_preset_sonoma-terminal" })

  -- Raise the mask cutoff for the scrolling app menu so clipped row shadows
  -- do not trigger patches of glass at the top and bottom of its viewport.
  hg.layer("omarchy-menu", {
    preset = "sonoma-menu",
    mask_threshold = 0.32,
    mask_feather = 0.12,
  })

  for _, namespace in ipairs({
    "omarchy-bar", "omarchy-emojis", "omarchy-clipboard",
    "omarchy-keyboard-panel", "omarchy-osd", "omarchy-notifications",
    "omarchy-polkit", "omarchy-network-qr",
  }) do
    hg.layer(namespace, { preset = "pomme", mask_threshold = 0.12, mask_feather = 0.25 })
  end
end

-- The plugin becomes available after config parsing on first startup; reapply
-- its theme after startup and after each Omarchy/Hyprland config reload.
configure_hyprglass()
hl.on("hyprland.start", configure_hyprglass)
hl.on("config.reloaded", configure_hyprglass)
