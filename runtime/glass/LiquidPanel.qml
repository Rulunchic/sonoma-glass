import QtQuick
import Quickshell
import Quickshell.Wayland
import qs.Commons
import qs.Ui

// Keep Omarchy's panel controls, focus and dismissal handling. Only advertise
// the actual glass card to ext-background-effect-v1 instead of the full screen.
KeyboardPanel {
  id: root
  BackgroundEffect.blurRegion: Region {
    x: Math.round(root.cardOrigin.x)
    y: Math.round(root.cardOrigin.y)
    width: root.contentWidth
    height: root.contentHeight
    radius: Style.cornerRadius
  }
}
