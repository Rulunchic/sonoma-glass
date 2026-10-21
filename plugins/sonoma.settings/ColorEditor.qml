import QtQuick

Rectangle {
  id: picker
  property string title: "Цвет"
  property string originalValue: "#ffffff"
  property bool alphaAllowed: false
  property real hue: 0
  property real saturation: 0
  property real brightness: 1
  property real alpha: 1
  readonly property color rgb: Qt.hsva(hue, saturation, brightness, 1)
  readonly property color preview: Qt.rgba(rgb.r, rgb.g, rgb.b, alphaAllowed ? alpha : 1)
  readonly property string hex: "#" + byte(rgb.r) + byte(rgb.g) + byte(rgb.b) + (alphaAllowed ? byte(alpha) : "")
  signal accepted(string value)
  signal canceled()
  color: "#fa263746"
  radius: 12
  border.color: "#35ffffff"

  function byte(v) { return Math.round(v * 255).toString(16).padStart(2, "0") }
  function load(text) {
    if (!/^#[0-9a-f]{6}([0-9a-f]{2})?$/i.test(text)) return
    var r = parseInt(text.slice(1,3),16)/255, g = parseInt(text.slice(3,5),16)/255, b = parseInt(text.slice(5,7),16)/255
    var mx = Math.max(r,g,b), mn = Math.min(r,g,b), delta = mx-mn
    var h = delta === 0 ? 0 : mx === r ? ((g-b)/delta)%6 : mx === g ? (b-r)/delta+2 : (r-g)/delta+4
    hue = ((h/6)%1+1)%1
    saturation = mx === 0 ? 0 : delta/mx
    brightness = mx
    alpha = alphaAllowed && text.length===9 ? parseInt(text.slice(7,9),16)/255 : 1
  }
  MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }
  Column {
    anchors.fill: parent
    anchors.margins: 18
    spacing: 12
    Row {
      width: parent.width
      Text { width: parent.width - 36; height: 30; verticalAlignment: Text.AlignVCenter; text: picker.title; color: "#eef4fa"; font.family: "sans-serif"; font.pixelSize: 16; elide: Text.ElideRight }
      GlassAction { text: "✕"; width: 36; quiet: true; onClicked: picker.canceled() }
    }
    Rectangle {
      id: square
      width: parent.width
      height: Math.max(100, Math.min(185, picker.height - (picker.alphaAllowed ? 300 : 255)))
      radius: 8
      clip: true
      color: Qt.hsva(picker.hue, 1, 1, 1)
      Rectangle { anchors.fill: parent; gradient: Gradient { orientation: Gradient.Horizontal; GradientStop { position: 0; color: "white" } GradientStop { position: 1; color: "#00ffffff" } } }
      Rectangle { anchors.fill: parent; gradient: Gradient { GradientStop { position: 0; color: "#00000000" } GradientStop { position: 1; color: "black" } } }
      Rectangle {
        x: picker.saturation * (parent.width-2) - 6
        y: (1-picker.brightness) * (parent.height-2) - 6
        width: 14; height: 14; radius: 7
        color: "transparent"; border.width: 2; border.color: "white"
      }
      MouseArea {
        anchors.fill: parent
        preventStealing: true
        function update(mouse) { picker.saturation = Math.max(0,Math.min(1,mouse.x/width)); picker.brightness = 1-Math.max(0,Math.min(1,mouse.y/height)) }
        onPressed: function(mouse) { square.forceActiveFocus(); update(mouse) }
        onPositionChanged: function(mouse) { if (pressed) update(mouse) }
      }
    }
    GlassSlider {
      width: parent.width; height: 30
      value: picker.hue; stepSize: .001; trackHeight: 12
      trackGradient: Gradient {
        orientation: Gradient.Horizontal
        GradientStop { position: 0; color: "#ff0000" }
        GradientStop { position: .1667; color: "#ffff00" }
        GradientStop { position: .3333; color: "#00ff00" }
        GradientStop { position: .5; color: "#00ffff" }
        GradientStop { position: .6667; color: "#0000ff" }
        GradientStop { position: .8333; color: "#ff00ff" }
        GradientStop { position: 1; color: "#ff0000" }
      }
      onShownValueChanged: if (pressed) picker.hue = shownValue
      onEdited: function(value) { picker.hue = value }
    }
    Row {
      visible: picker.alphaAllowed
      width: parent.width
      Text { width: parent.width - 50; text: "Плотность цвета"; color: "#9bb3c8"; font.family: "sans-serif"; font.pixelSize: 11 }
      Text { width: 50; horizontalAlignment: Text.AlignRight; text: Math.round(picker.alpha*100)+"%"; color: "#dce8f3"; font.pixelSize: 11 }
    }
    Item {
      width: parent.width; height: 30
      visible: picker.alphaAllowed
      Item {
        anchors.fill: parent; anchors.leftMargin: 9; anchors.rightMargin: 9
        anchors.topMargin: 9; anchors.bottomMargin: 9
        clip: true
        Repeater {
          model: Math.max(0, Math.ceil(parent.width/6))*2
          Rectangle {
            required property int index
            property int columns: Math.max(1, Math.ceil(parent.width/6))
            x: index%columns*6; y: Math.floor(index/columns)*6
            width: 6; height: 6
            color: (index%columns + Math.floor(index/columns))%2 ? "#77909e" : "#d7e0e8"
          }
        }
      }
      GlassSlider {
        anchors.fill: parent
        value: picker.alpha; stepSize: .01; trackHeight: 12
        trackGradient: Gradient {
          orientation: Gradient.Horizontal
          GradientStop { position: 0; color: Qt.rgba(picker.rgb.r,picker.rgb.g,picker.rgb.b,0) }
          GradientStop { position: 1; color: picker.rgb }
        }
        onShownValueChanged: if (pressed) picker.alpha = shownValue
        onEdited: function(value) { picker.alpha = value }
      }
    }
    Row {
      spacing: 10
      Repeater {
        model: ["#f5f5f7", "#929aa3", "#1c1c1e", "#0a84ff", "#64b5ff", "#bf5af2", "#ff375f", "#ff9f0a", "#ffd60a", "#30d158"]
        Rectangle {
          required property string modelData
          width: 24; height: 24; radius: 12
          color: modelData; border.color: "#55ffffff"
          MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
              parent.forceActiveFocus()
              if (picker.alphaAllowed && picker.alpha < .01) picker.alpha = .2
              picker.load(parent.modelData + (picker.alphaAllowed ? picker.byte(picker.alpha) : ""))
            }
          }
        }
      }
    }
    Row {
      width: parent.width
      spacing: 10
      Rectangle { width: 48; height: 32; radius: 8; color: picker.preview; border.color: "#55ffffff" }
      GlassField {
        id: hexField
        width: parent.width - 58; height: 32
        text: picker.hex.toUpperCase()
        validator: RegularExpressionValidator { regularExpression: picker.alphaAllowed ? /#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?/ : /#[0-9a-fA-F]{6}/ }
        onEditingFinished: if (acceptableInput) picker.load(text)
      }
    }
    Row {
      width: parent.width
      spacing: 10
      GlassAction { text: "Отмена"; width: (parent.width-10)/2; onClicked: picker.canceled() }
      GlassAction {
        text: "Готово"; selected: true; width: (parent.width-10)/2
        enabled: !hexField.editing || hexField.acceptableInput
        onClicked: { if (hexField.editing && hexField.acceptableInput) picker.load(hexField.text); picker.accepted(picker.hex) }
      }
    }
  }
}
