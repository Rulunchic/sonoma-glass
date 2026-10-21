import QtQuick

// Decorative only: pointer handlers observe passively. Existing buttons keep
// their clicks, wheel input, keyboard navigation, focus and accessibility.
Item {
  id: root
  property bool engaged: false
  property bool selected: false
  property bool resting: false
  property real cornerRadius: 18
  property color accent: "#64b5ff"
  readonly property bool hovered: pointer.hovered
  readonly property real pressedAmount: pressAmount
  property real hoverAmount: root.enabled && engaged ? 1 : 0
  property real pressAmount: root.enabled && press.active ? 1 : 0
  property real lightX: pointer.hovered ? pointer.point.position.x : width * 0.32
  property real lightY: pointer.hovered ? pointer.point.position.y : height * 0.15
  property real selectionAmount: selected ? 1 : 0
  property real bubbleAmount: root.enabled ? (press.active ? -1.0 : (engaged ? 1.0 : 0.0)) : 0.0
  property real waveProgress: 1.0
  property real waveAmplitude: 0.0
  property vector2d waveOrigin: Qt.vector2d(width * 0.5, height * 0.5)

  property double lastBubbleMoveAt: 0
  property point lastBubblePoint: Qt.point(-10000, -10000)
  function moveBubble(px, py) {
    if (!root.engaged) return
    var now = Date.now()
    var dx = px - lastBubblePoint.x, dy = py - lastBubblePoint.y
    if (now - lastBubbleMoveAt < 180 || dx * dx + dy * dy < 100) return
    lastBubbleMoveAt = now
    lastBubblePoint = Qt.point(px, py)
    root.bubble(0.38)
  }
  function bubble(strength) {
    if (!root.enabled) return
    // Use the actual local pointer position, not the smoothed light position.
    var px = press.active ? press.point.position.x : (pointer.hovered ? pointer.point.position.x : width * 0.5)
    var py = press.active ? press.point.position.y : (pointer.hovered ? pointer.point.position.y : height * 0.5)
    waveOrigin = Qt.vector2d(Math.max(0, Math.min(width, px)), Math.max(0, Math.min(height, py)))
    waveAmplitude = strength
    wave.restart()
  }
  onEngagedChanged: if (engaged) bubble(0.55)

  NumberAnimation {
    id: wave
    target: root
    property: "waveProgress"
    from: 0.0
    to: 1.0
    duration: 620
    easing.type: Easing.OutQuad
  }
  Behavior on bubbleAmount {
    SpringAnimation { spring: 4.2; damping: 0.24; mass: 0.8; epsilon: 0.004 }
  }

  visible: width > 0 && height > 0
    && (resting || selectionAmount > 0.001 || hoverAmount > 0.001 || pressAmount > 0.001 || wave.running)
  // Animate only the decoration; control contents and hit rectangles stay put.
  // Squash/stretch happens in the material, inside a stable hit rectangle.
  Behavior on hoverAmount { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
  Behavior on pressAmount { NumberAnimation { duration: 90; easing.type: Easing.OutCubic } }
  Behavior on selectionAmount { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
  Behavior on lightX { NumberAnimation { duration: 65; easing.type: Easing.OutCubic } }
  Behavior on lightY { NumberAnimation { duration: 65; easing.type: Easing.OutCubic } }

  HoverHandler {
    id: pointer
    target: null
    onPointChanged: if (hovered) root.moveBubble(point.position.x, point.position.y)
  }
  PointHandler {
    id: press
    target: null
    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
    enabled: root.engaged && root.enabled
    onActiveChanged: root.bubble(active ? 1.0 : 0.75)
  }

  ShaderEffect {
    anchors.fill: parent
    property vector2d surfaceSize: Qt.vector2d(width, height)
    property vector2d lightPosition: Qt.vector2d(root.lightX, root.lightY)
    property color accentColor: root.accent
    property real cornerRadius: root.cornerRadius
    property real hoverAmount: root.hoverAmount
    property real pressAmount: root.pressAmount
    property real selectedAmount: root.selectionAmount
    property real restAmount: root.resting ? 1 : 0
    property real bubbleAmount: root.bubbleAmount
    property real waveProgress: root.waveProgress
    property real waveAmplitude: root.waveAmplitude
    property vector2d waveOrigin: root.waveOrigin
    fragmentShader: Qt.resolvedUrl("liquid-control.frag.qsb")
  }
}
