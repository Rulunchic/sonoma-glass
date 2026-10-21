import QtQuick

Rectangle {
  id: root
  property alias text: input.text
  property alias validator: input.validator
  property alias horizontalAlignment: input.horizontalAlignment
  property string placeholderText: ""
  property string suffix: ""
  readonly property bool acceptableInput: input.acceptableInput
  readonly property bool editing: input.activeFocus
  signal accepted()
  signal editingFinished()
  implicitHeight: 32
  implicitWidth: 160
  radius: 8
  color: "#0dffffff"
  border.width: 1
  border.color: input.activeFocus ? "#88c7e5ff" : "#1affffff"
  function focusField() { input.forceActiveFocus() }
  TextInput {
    id: input
    anchors.fill: parent
    anchors.leftMargin: 10
    anchors.rightMargin: root.suffix.length ? 25 : 10
    verticalAlignment: TextInput.AlignVCenter
    selectByMouse: true
    activeFocusOnTab: true
    clip: true
    color: "#eef4fa"
    selectedTextColor: "white"
    selectionColor: "#507faa"
    font.family: "sans-serif"
    font.pixelSize: 12
    onAccepted: root.accepted()
    onEditingFinished: root.editingFinished()
  }
  Text {
    anchors.right: parent.right
    anchors.rightMargin: 8
    height: parent.height
    verticalAlignment: Text.AlignVCenter
    text: root.suffix
    color: "#90eef4fa"
    font.pixelSize: 11
  }
  Text {
    anchors.fill: input
    verticalAlignment: Text.AlignVCenter
    visible: input.text.length === 0
    text: root.placeholderText
    color: "#70eef4fa"
    font.family: "sans-serif"
    font.pixelSize: 12
    elide: Text.ElideRight
  }
}
