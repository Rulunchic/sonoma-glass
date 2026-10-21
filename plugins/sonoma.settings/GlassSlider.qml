import QtQuick
import qs.Commons
import "../../glass" as Glass

Item {
  id: root
  property real from: 0
  property real to: 1
  property real stepSize: .01
  property real value: 0
  property real dragValue: value
  property Gradient trackGradient: null
  property real trackHeight: 4
  readonly property bool pressed: pointer.pressed
  readonly property real shownValue: pressed ? dragValue : value
  readonly property real fraction: Math.max(0, Math.min(1, (shownValue - from) / Math.max(.000001, to - from)))
  signal edited(real value)
  implicitWidth: 180
  implicitHeight: 32
  activeFocusOnTab: true
  function snap(v) {
    return Math.max(from, Math.min(to, Math.round((v - from) / stepSize) * stepSize + from))
  }
  function at(px) { return snap(from + Math.max(0, Math.min(1, (px - 9) / Math.max(1, width - 18))) * (to - from)) }
  Keys.onLeftPressed: edited(snap(value - stepSize))
  Keys.onRightPressed: edited(snap(value + stepSize))
  Rectangle {
    x: 9; width: Math.max(0, parent.width - 18)
    height: root.trackHeight; radius: height / 2; anchors.verticalCenter: parent.verticalCenter
    color: "#25ffffff"
    gradient: root.trackGradient
    Rectangle { visible: root.trackGradient === null; width: parent.width * root.fraction; height: parent.height; radius: 2; color: Color.accent }
  }
  Rectangle {
    x: root.fraction * Math.max(0, parent.width - 18)
    anchors.verticalCenter: parent.verticalCenter
    width: 18; height: 18; radius: 9
    color: "#f5f8fc"
    border.width: root.activeFocus ? 2 : 1; border.color: root.activeFocus ? "#9acbf1" : "#55ffffff"
    scale: pointer.pressed ? 1.12 : 1
    Behavior on scale { NumberAnimation { duration: 90 } }
    Glass.LiquidChrome { anchors.fill: parent; cornerRadius: 9; engaged: pointer.containsMouse || pointer.pressed; resting: true }
  }
  MouseArea {
    id: pointer
    anchors.fill: parent
    hoverEnabled: true
    preventStealing: true
    cursorShape: Qt.PointingHandCursor
    onPressed: function(mouse) { root.forceActiveFocus(); root.dragValue = root.at(mouse.x) }
    onPositionChanged: function(mouse) { if (pressed) root.dragValue = root.at(mouse.x) }
    onReleased: function(mouse) { root.edited(root.at(mouse.x)) }
  }
}
