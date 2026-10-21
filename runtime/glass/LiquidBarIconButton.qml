import QtQuick
import qs.Ui as Ui
import qs.Commons

Ui.BarIconButton {
  id: root
  LiquidChrome {
    z: -1
    anchors.fill: parent
    anchors.margins: Style.space(2)
    enabled: root.interactive
    engaged: root.tooltipHovered
    selected: root.active
    cornerRadius: Math.min(height / 2, Style.cornerRadius)
  }
}
