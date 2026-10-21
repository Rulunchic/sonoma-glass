import QtQuick
import Quickshell
import QtQuick.Effects
import qs.Commons
import qs.Ui
import "../../glass" as Glass

Item {
  id: root

  property string backgroundPath: ""
  property int backgroundVersion: 0
  property bool fingerprintConfigured: false
  property bool authenticatingPassword: false
  property string failureMessage: ""
  property int failedAttempts: 0
  property bool inputEnabled: true
  property bool loadBackground: true
  property string passwordText: ""
  property bool syncingPasswordText: false

  readonly property string placeholderText: "Введите пароль"
  readonly property int fieldWidth: 246
  readonly property int fieldHeight: 40
  readonly property int outlineThickness: 1
  readonly property int fieldFontSize: 14
  readonly property int passwordDotFontSize: 15
  readonly property int passwordDotLetterSpacing: 3
  // Space to keep clear on each side of the field for the fingerprint icon
  // (icon width plus a gap) so the centered dots never run under it.
  readonly property real fingerprintReserve: fingerprintConfigured ? Math.round(fingerprintIcon.implicitWidth + 12) : 0
  // Shrink the dots to fit once the password outgrows the field, so every
  // keystroke stays visible — otherwise long passwords clip with no feedback.
  readonly property real passwordDotScale: dotMetrics.advanceWidth > 0
    ? Math.min(1, (passwordInput.width - 4) / dotMetrics.advanceWidth)
    : 1
  readonly property bool showPasswordCursor: inputEnabled && !authenticatingPassword && failureMessage.length === 0
  readonly property bool errorState: failureMessage.length > 0
  readonly property var inputBorderSpec: Border.flat(errorState ? "#ff9ba6" : Qt.rgba(1, 1, 1, 0.32), 1)
  readonly property string displayName: Quickshell.env("USER") || "User"
  property date now: new Date()
  onLoadBackgroundChanged: if (loadBackground) now = new Date()
  function submitCurrentPassword() {
    if (!root.inputEnabled || root.authenticatingPassword) return
    var submitted = root.passwordText
    root.passwordTextEdited("")
    if (submitted.length > 0) root.submitPassword(submitted)
  }

  signal submitPassword(string password)
  signal passwordTextEdited(string password)
  signal clearFailureRequested()
  signal wakeRequested()

  // Cache-busts the lock background by appending `?v=`. Adding a query
  // string keeps Image's loader happy while forcing it to reload when the
  // user picks a new background mid-session.
  function fileUrl(path) {
    if (!path) return ""
    var encoded = String(path).split("/").map(encodeURIComponent).join("/")
    return "file://" + encoded + "?v=" + backgroundVersion
  }

  function forcePasswordFocus() {
    passwordInput.forceActiveFocus()
  }

  function clearPassword() {
    passwordTextEdited("")
  }

  function syncPasswordText() {
    if (passwordInput.text === passwordText) return
    syncingPasswordText = true
    passwordInput.text = passwordText
    syncingPasswordText = false
  }

  onPasswordTextChanged: syncPasswordText()
  onInputEnabledChanged: {
    if (inputEnabled) Qt.callLater(forcePasswordFocus)
  }
  Component.onCompleted: {
    syncPasswordText()
    if (inputEnabled) Qt.callLater(forcePasswordFocus)
  }

  // Measures the masked password at full size; passwordDotScale compares this
  // against the field width to decide how far the dots must shrink to fit.
  TextMetrics {
    id: dotMetrics
    font.family: Style.font.family
    font.pixelSize: root.passwordDotFontSize
    font.letterSpacing: root.passwordDotLetterSpacing
    text: "●".repeat(passwordInput.text.length)
  }


  Timer { interval: 1000; repeat: true; running: root.loadBackground && root.visible; onTriggered: root.now = new Date() }
  Rectangle {
    anchors.fill: parent
    color: "#173650"
    Image {
      id: wallpaper
      anchors.fill: parent
      source: root.loadBackground ? root.fileUrl(root.backgroundPath) : ""
      fillMode: Image.PreserveAspectCrop
      asynchronous: true
      cache: false
      sourceSize.width: width
      sourceSize.height: height
    }
    MultiEffect {
      anchors.fill: wallpaper
      source: wallpaper
      autoPaddingEnabled: false
      blurEnabled: root.loadBackground && wallpaper.status === Image.Ready
      blur: Glass.GlassSettings.value("system.lock_blur", 0.25)
      blurMax: 48
    }
    Rectangle {
      anchors.fill: parent
      gradient: Gradient {
        GradientStop { position: 0; color: "#18000000" }
        GradientStop { position: 0.5; color: "#0a000000" }
        GradientStop { position: 1; color: "#38000000" }
      }
    }
    MouseArea {
      anchors.fill: parent
      hoverEnabled: true
      onClicked: { root.wakeRequested(); root.forcePasswordFocus() }
      onPositionChanged: root.wakeRequested()
    }
    Column {
      anchors.horizontalCenter: parent.horizontalCenter
      y: Math.max(36, parent.height * 0.09)
      spacing: 0
      Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: Qt.formatDateTime(root.now, "dddd, d MMMM")
        color: "white"
        font.family: "sans-serif"
        font.pixelSize: Math.max(18, Math.min(25, root.height * 0.03))
        font.weight: Font.Medium
      }
      Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: Qt.formatDateTime(root.now, "HH:mm")
        color: "white"
        font.family: "sans-serif"
        font.pixelSize: Math.max(64, Math.min(Glass.GlassSettings.value("system.clock_size", 144), root.height * 0.20))
        font.weight: Font.DemiBold
        font.letterSpacing: -4
      }
    }
    Column {
      id: userBlock
      anchors.horizontalCenter: parent.horizontalCenter
      y: Math.max(parent.height * 0.55, parent.height - implicitHeight - Math.max(70, parent.height * 0.14))
      spacing: 12
      Rectangle {
        width: 76; height: 76; radius: 38
        anchors.horizontalCenter: parent.horizontalCenter
        border.width: 1
        border.color: "#70ffffff"
        gradient: Gradient {
          GradientStop { position: 0; color: "#81bffd" }
          GradientStop { position: 1; color: "#4d67be" }
        }
        Glass.LiquidChrome { anchors.fill: parent; cornerRadius: 38; resting: true }
        Text {
          anchors.centerIn: parent
          text: root.displayName.charAt(0).toUpperCase()
          color: "white"
          font.family: "sans-serif"
          font.pixelSize: 36
          font.weight: Font.Medium
        }
      }
      Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.displayName
        color: "white"
        font.family: "sans-serif"
        font.pixelSize: 20
        font.weight: Font.Medium
      }
      BorderSurface {
        id: inputField
        anchors.horizontalCenter: parent.horizontalCenter
        width: root.fieldWidth
        height: root.fieldHeight
        color: Qt.rgba(1, 1, 1, 0.16)
        borderSpec: root.inputBorderSpec
        radius: height / 2
        clip: true
        Glass.LiquidChrome {
          anchors.fill: parent
          cornerRadius: inputField.radius
          resting: true
          engaged: passwordInput.activeFocus
        }
      TextInput {
        id: passwordInput
        anchors.fill: parent
        anchors.topMargin: inputField.borderTop
        // Reserve the fingerprint icon's width on both sides so the centered
        // dots stay symmetric and never slide under the icon as they grow.
        anchors.rightMargin: inputField.borderRight + 40 + root.fingerprintReserve
        anchors.bottomMargin: inputField.borderBottom
        anchors.leftMargin: inputField.borderLeft + 16
        verticalAlignment: TextInput.AlignVCenter
        horizontalAlignment: TextInput.AlignHCenter
        activeFocusOnPress: true
        clip: true
        enabled: root.inputEnabled && !root.authenticatingPassword
        readOnly: root.authenticatingPassword
        echoMode: TextInput.Password
        passwordCharacter: "\u25CF"
        passwordMaskDelay: 0
        color: Color.lock.text
        selectionColor: Color.lock.selection
        selectedTextColor: Color.lock.text
        font.family: "sans-serif"
        font.pixelSize: text.length > 0 ? Math.max(1, Math.floor(root.passwordDotFontSize * root.passwordDotScale)) : root.fieldFontSize
        font.letterSpacing: text.length > 0 ? root.passwordDotLetterSpacing * root.passwordDotScale : 0
        cursorVisible: activeFocus && root.showPasswordCursor && text.length > 0
        cursorDelegate: Rectangle {
          width: 2
          color: Color.lock.text
          visible: passwordInput.cursorVisible
        }

        onTextChanged: {
          if (!root.syncingPasswordText) root.passwordTextEdited(text)
          if (text.length > 0) {
            root.wakeRequested()
          }
          if (text.length > 0 && root.failureMessage.length > 0) root.clearFailureRequested()
        }

        onAccepted: {
          var submitted = root.passwordText
          root.passwordTextEdited("")
          if (submitted.length > 0) root.submitPassword(submitted)
        }

        Keys.onPressed: function(event) {
          root.wakeRequested()
          if (event.key === Qt.Key_Escape || (event.modifiers & Qt.ControlModifier && event.key === Qt.Key_U)) {
            root.passwordTextEdited("")
            event.accepted = true
          }
        }
      }
        Text {
          anchors.fill: passwordInput
          visible: passwordInput.text.length === 0
          text: root.authenticatingPassword ? "Проверка…" : root.placeholderText
          color: "#dfffffff"
          font.family: "sans-serif"
          font.pixelSize: root.fieldFontSize
          horizontalAlignment: Text.AlignHCenter
          verticalAlignment: Text.AlignVCenter
          elide: Text.ElideRight
        }
        Text {
          id: fingerprintIcon
          visible: root.fingerprintConfigured
          text: "󰈷"
          font.family: Style.font.family
          color: "white"
          font.pixelSize: 18
          anchors.right: unlockButton.left
          anchors.rightMargin: 4
          anchors.verticalCenter: parent.verticalCenter
        }
        Glass.LiquidActionButton {
          id: unlockButton
          anchors.right: parent.right
          anchors.rightMargin: 5
          anchors.verticalCenter: parent.verticalCenter
          size: 28
          radius: 14
          iconText: root.authenticatingPassword ? "…" : "→"
          fontFamily: "sans-serif"
          foreground: "white"
          fontSize: 20
          enabled: root.inputEnabled && !root.authenticatingPassword
          onClicked: root.submitCurrentPassword()
        }
      }
      Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.errorState ? "Неверный пароль. Попробуйте ещё раз." : "Введите пароль для разблокировки"
        color: root.errorState ? "#ffd1d6" : "#cfffffff"
        font.family: "sans-serif"
        font.pixelSize: 12
      }
    }
    Text {
      anchors.bottom: parent.bottom
      anchors.bottomMargin: 28
      anchors.horizontalCenter: parent.horizontalCenter
      text: root.fingerprintConfigured ? "Можно использовать отпечаток пальца" : "Экран заблокирован"
      color: "#aaffffff"
      font.family: "sans-serif"
      font.pixelSize: 12
    }
  }
}
