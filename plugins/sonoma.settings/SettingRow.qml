import QtQuick
import "../../glass" as Glass

Item {
  id: row
  required property var definition
  required property var currentValue
  property string label: definition.label
  property bool detailed: false
  property bool transparency: false
  signal edited(var value)
  signal colorRequested(var definition, string value)
  signal choiceRequested(var definition, var value)
  readonly property bool numeric: definition.type === "number" || definition.type === "integer"
  height: numeric ? 68 : definition.type === "text" ? 76 : 44
  implicitHeight: height

  function colorValue(v) {
    var text = String(v)
    return text.length === 9 ? "#" + text.slice(7, 9) + text.slice(1, 7) : text
  }
  function decimals() { return definition.step < .01 ? 3 : definition.step < 1 ? 2 : 0 }

  Text {
    anchors.left: parent.left
    anchors.right: editor.left
    anchors.rightMargin: 12
    anchors.top: parent.top
    height: 32
    text: row.label
    verticalAlignment: Text.AlignVCenter
    elide: Text.ElideRight
    wrapMode: Text.WordWrap
    maximumLineCount: 2
    color: "#eef4fa"
    font.family: "sans-serif"
    font.pixelSize: 12
  }
  Loader {
    id: editor
    anchors.top: parent.top
    anchors.right: reset.visible ? reset.left : parent.right
    anchors.rightMargin: reset.visible ? 6 : 0
    width: row.numeric ? 76 : row.definition.type === "boolean" ? 44 : Math.min(210, row.width * .5)
    height: 32
    sourceComponent: row.numeric ? numberValue : row.definition.type === "boolean" ? switchValue
      : row.definition.type === "color" ? colorValueEditor : row.definition.type === "choice" ? choiceValue : emptyValue
  }
  GlassAction {
    id: reset
    anchors.right: parent.right
    anchors.top: parent.top
    width: 26; height: 32
    text: "↺"
    quiet: true
    visible: row.detailed && row.currentValue !== row.definition.default
    onClicked: row.edited(row.definition.default)
  }
  GlassSlider {
    id: slider
    visible: row.numeric
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    anchors.topMargin: 33
    height: 32
    from: row.numeric ? row.transparency ? 1-row.definition.max : row.definition.min : 0
    to: row.numeric ? row.transparency ? 1-row.definition.min : row.definition.max : 1
    stepSize: row.numeric ? row.definition.step : .01
    value: row.numeric ? row.transparency ? 1-Number(row.currentValue) : Number(row.currentValue) : 0
    onEdited: function(value) { row.edited(Math.round((row.transparency ? 1-value : value) * 10000) / 10000) }
  }
  GlassField {
    visible: row.definition.type === "text"
    anchors.top: parent.top
    anchors.topMargin: 35
    width: parent.width
    height: 32
    text: String(row.currentValue)
    onEditingFinished: if (text !== String(row.currentValue)) row.edited(text)
  }
  Component {
    id: emptyValue
    Item {}
  }
  Component {
    id: numberValue
    GlassField {
      text: Number(row.transparency ? (slider.pressed ? slider.shownValue : 1-Number(row.currentValue))*100 : slider.pressed ? slider.shownValue : row.currentValue).toFixed(row.transparency ? 0 : row.decimals())
      suffix: row.transparency ? "%" : ""
      horizontalAlignment: TextInput.AlignRight
      validator: DoubleValidator { bottom: row.transparency ? (1-row.definition.max)*100 : row.definition.min; top: row.transparency ? (1-row.definition.min)*100 : row.definition.max; locale: "C" }
      onEditingFinished: {
        var next = row.transparency ? 1-Number(text)/100 : Number(text.replace(",", "."))
        if (acceptableInput && Math.abs(next - Number(row.currentValue)) > .000001) row.edited(next)
      }
    }
  }
  Component {
    id: switchValue
    Item {
      Rectangle {
        anchors.centerIn: parent
        width: 40; height: 23; radius: 12
        color: row.currentValue ? "#709bd1" : "#33ffffff"
        Rectangle {
          y: 3; x: row.currentValue ? 20 : 3
          width: 17; height: 17; radius: 9; color: "#f5f8fc"
          Behavior on x { NumberAnimation { duration: 100 } }
        }
        Glass.LiquidChrome { anchors.fill: parent; cornerRadius: 12; resting: true; engaged: switchPointer.containsMouse }
      }
      MouseArea { id: switchPointer; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: row.edited(!row.currentValue) }
    }
  }
  Component {
    id: choiceValue
    GlassAction { text: String(row.currentValue) + "  ›"; onClicked: row.choiceRequested(row.definition, row.currentValue) }
  }
  Component {
    id: colorValueEditor
    GlassAction {
      text: ""
      onClicked: row.colorRequested(row.definition, String(row.currentValue))
      Row {
        anchors.centerIn: parent
        spacing: 9
        Rectangle {
          width: 22; height: 22; radius: 6
          color: row.colorValue(row.currentValue)
          border.color: "#66ffffff"
        }
        Text { text: String(row.currentValue).toUpperCase(); color: "#dae8f5"; font.family: "sans-serif"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
      }
    }
  }
}
