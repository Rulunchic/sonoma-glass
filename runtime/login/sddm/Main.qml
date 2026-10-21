import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Effects

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#173650"
    property date now: new Date()
    property string currentUser: userModel.lastUser || "__SONOMA_USER__"
    property bool loginPending: false
    property bool loginFailed: false
    property int sessionIndex: sessionModel.lastIndex

    function login() {
        if (loginPending || password.text.length === 0)
            return;
        loginPending = true;
        sddm.login(currentUser, password.text, sessionIndex);
    }
    Connections {
        target: sddm
        function onLoginFailed() {
            root.loginPending = false;
            root.loginFailed = true;
            password.text = "";
            password.forceActiveFocus();
        }
        function onLoginSucceeded() {
            password.text = "";
        }
    }
    Timer {
        interval: 1000
        repeat: true
        running: true
        onTriggered: root.now = new Date()
    }
    Image {
        id: wallpaper
        anchors.fill: parent
        source: "background.jpg"
        fillMode: Image.PreserveAspectCrop
        sourceSize.width: width
        sourceSize.height: height
    }
    MultiEffect {
        anchors.fill: wallpaper
        source: wallpaper
        autoPaddingEnabled: false
        blurEnabled: wallpaper.status === Image.Ready
        blur: 0.25
        blurMax: 48
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop {
                position: 0
                color: "#18000000"
            }
            GradientStop {
                position: 0.5
                color: "#0a000000"
            }
            GradientStop {
                position: 1
                color: "#38000000"
            }
        }
        MouseArea {
            anchors.fill: parent
            onClicked: password.forceActiveFocus()
        }
    }
    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: Math.max(36, root.height * 0.09)
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
            font.pixelSize: Math.max(64, Math.min(144, root.height * 0.16))
            font.weight: Font.DemiBold
            font.letterSpacing: -4
        }
    }
    Column {
        id: userBlock
        anchors.horizontalCenter: parent.horizontalCenter
        y: Math.max(root.height * 0.55, root.height - implicitHeight - Math.max(70, root.height * 0.14))
        spacing: 12
        Rectangle {
            width: 76
            height: 76
            radius: 38
            anchors.horizontalCenter: parent.horizontalCenter
            border.width: 1
            border.color: "#70ffffff"
            gradient: Gradient {
                GradientStop {
                    position: 0
                    color: "#81bffd"
                }
                GradientStop {
                    position: 1
                    color: "#4d67be"
                }
            }
            LiquidChrome {
                anchors.fill: parent
                cornerRadius: 38
                resting: true
            }
            Text {
                anchors.centerIn: parent
                text: root.currentUser.charAt(0).toUpperCase()
                color: "white"
                font.family: "sans-serif"
                font.pixelSize: 36
                font.weight: Font.Medium
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.currentUser
            color: "white"
            font.family: "sans-serif"
            font.pixelSize: 20
            font.weight: Font.Medium
        }
        Controls.ComboBox {
            anchors.horizontalCenter: parent.horizontalCenter
            visible: userModel.count > 1
            model: userModel
            textRole: "name"
            currentIndex: userModel.lastIndex
            onActivated: {
                root.currentUser = currentText;
                password.text = "";
                root.loginFailed = false;
            }
        }
        Rectangle {
            id: inputField
            anchors.horizontalCenter: parent.horizontalCenter
            width: 246
            height: 40
            radius: 20
            color: Qt.rgba(1, 1, 1, 0.16)
            border.width: 1
            border.color: root.loginFailed ? "#ff9ba6" : "#55ffffff"
            LiquidChrome {
                anchors.fill: parent
                cornerRadius: 20
                resting: true
                engaged: password.activeFocus
            }
            TextInput {
                id: password
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 40
                verticalAlignment: TextInput.AlignVCenter
                horizontalAlignment: TextInput.AlignHCenter
                echoMode: TextInput.Password
                passwordCharacter: "\u25cf"
                passwordMaskDelay: 0
                font.family: "sans-serif"
                font.pixelSize: 15
                color: "white"
                selectionColor: "#527baee5"
                selectedTextColor: "white"
                enabled: !root.loginPending
                focus: true
                clip: true
                onAccepted: root.login()
                onTextChanged: root.loginFailed = false
                Keys.onEscapePressed: text = ""
            }
            Text {
                anchors.fill: password
                visible: password.text.length === 0
                text: root.loginPending ? "Вход…" : "Введите пароль"
                color: "#dfffffff"
                font.family: "sans-serif"
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            GlassButton {
                width: 28
                height: 28
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.verticalCenter: parent.verticalCenter
                text: root.loginPending ? "…" : "→"
                enabled: !root.loginPending
                onClicked: root.login()
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.loginFailed ? "Неверный пароль. Попробуйте ещё раз." : "Введите пароль для входа"
            color: root.loginFailed ? "#ffd1d6" : "#cfffffff"
            font.family: "sans-serif"
            font.pixelSize: 12
        }
    }
    Controls.ComboBox {
        id: sessionPicker
        anchors.left: parent.left
        anchors.leftMargin: 24
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        model: sessionModel
        textRole: "name"
        currentIndex: root.sessionIndex
        onActivated: root.sessionIndex = currentIndex
        opacity: hovered || activeFocus ? 1 : 0.65
    }
    Row {
        anchors.right: parent.right
        anchors.rightMargin: 24
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        spacing: 12
        GlassButton {
            text: "Перезагрузка"
            visible: sddm.canReboot
            onClicked: sddm.reboot()
        }
        GlassButton {
            text: "Выключить"
            visible: sddm.canPowerOff
            onClicked: sddm.powerOff()
        }
    }
    component GlassButton: Controls.Button {
        id: button
        implicitWidth: label.implicitWidth + 26
        implicitHeight: 34
        activeFocusOnTab: true
        contentItem: Text {
            id: label
            text: button.text
            color: "white"
            font.family: "sans-serif"
            font.pixelSize: 13
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            radius: height / 2
            color: Qt.rgba(1, 1, 1, button.hovered ? 0.15 : 0.07)
            border.width: 1
            border.color: "#40ffffff"
            LiquidChrome {
                anchors.fill: parent
                cornerRadius: parent.radius
                resting: true
                engaged: button.hovered || button.activeFocus
            }
        }
    }
    Component.onCompleted: password.forceActiveFocus()
}
