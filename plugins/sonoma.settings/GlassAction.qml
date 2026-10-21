import QtQuick
import qs.Commons
import "../../glass" as Glass

Rectangle {
  id: root
  property string text: ""
  property bool selected: false
  property bool quiet: false
  property int textSize: 12
  property color foreground: "#eef4fa"
  signal clicked()
  implicitWidth: label.implicitWidth + 22
  implicitHeight: 32
  radius: 9
  color: selected ? Qt.alpha(Color.accent, .35) : pointer.containsMouse ? "#19ffffff" : quiet ? "transparent" : "#0dffffff"
  border.width: selected || activeFocus ? 1 : 0
  border.color: activeFocus ? "#9acbf1" : Qt.alpha(Color.accent, .65)
  opacity: enabled ? 1 : .4
  activeFocusOnTab: true
  Keys.onReturnPressed: clicked()
  Keys.onSpacePressed: clicked()
  Glass.LiquidChrome { anchors.fill: parent; cornerRadius: root.radius; engaged: pointer.containsMouse; selected: root.selected }
  Text {
    id: label
    anchors.centerIn: parent
    width: Math.max(0, root.width - 16)
    text: root.text
    color: root.foreground
    font.family: "sans-serif"
    font.pixelSize: root.textSize
    horizontalAlignment: Text.AlignHCenter
    elide: Text.ElideRight
  }
  MouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onPressed: root.forceActiveFocus(); onClicked: root.clicked() }
}
