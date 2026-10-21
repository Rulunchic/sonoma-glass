import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.Ui as Ui
import "../../glass" as Glass

Ui.Panel {
  id: root
  moduleName: "sonoma.settings"
  ipcTarget: "sonoma.settings"
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight
  property var catalogue: ({groups: [], options: []})
  property var values: ({})
  property var pending: ({})
  property var inFlight: ({})
  property var actions: []
  property string operation: ""
  property string mode: "quick"
  property string selectedGroup: "glass.terminal"
  property string scope: "terminal"
  property string query: ""
  property string message: ""
  property bool failed: false
  property string errors: ""
  property var profileNames: []
  property var colorDefinition: null
  property string choiceKey: ""
  property string choiceTitle: ""
  property var choices: []
  property var appliedSystem: ({})
  readonly property string cli: Quickshell.env("HOME") + "/.local/bin/sonoma-glass"
  readonly property string directory: Quickshell.env("HOME") + "/.config/omarchy/sonoma-glass/"
  readonly property var areas: [
    {id:"windows", label:"Окна", opacity:"desktop.active_opacity"},
    {id:"terminal", label:"Терминал", opacity:"terminal.alpha"},
    {id:"bar", label:"Бар", opacity:"shell.bar.background-alpha"},
    {id:"menu", label:"Меню", opacity:"shell.menu.background-alpha"},
    {id:"widgets", label:"Виджеты", opacity:"shell.popups.background-alpha"}]
  readonly property var area: areas.filter(function(a) { return a.id === scope })[0]
  readonly property var index: {
    var entries = ({})
    catalogue.options.forEach(function(item) { entries[item.key] = item })
    return entries
  }
  readonly property var visibleOptions: {
    if (mode === "quick") {
      return [area.opacity, "glass."+scope+".refraction_strength", "glass."+scope+".blur_strength",
        scope === "terminal" ? "terminal.rim_width" : "glass."+scope+".bevel_strength",
        "glass."+scope+".tint_color", "components.bubbles"]
        .map(function(key) { return index[key] }).filter(function(item) { return !!item })
    }
    return catalogue.options.filter(function(item) {
      if (!query.length) return item.group === selectedGroup
      return (item.label + " " + item.key + " " + item.hint).toLowerCase().indexOf(query.toLowerCase()) >= 0
    })
  }
  readonly property string groupLabel: {
    var found = catalogue.groups.filter(function(g) { return g.id === selectedGroup })[0]
    return found ? found.label : "Выбрать раздел"
  }
  readonly property bool overlayVisible: colorDefinition !== null || choiceKey !== ""
  readonly property bool showSystem: mode === "all" && !query.length && (selectedGroup === "system" || selectedGroup === "components")

  function quickLabel(item) {
    if (mode !== "quick") return item.label
    if (item.key === area.opacity) return "Прозрачность фона"
    if (item.key.endsWith("refraction_strength")) return "Преломление"
    if (item.key.endsWith("blur_strength")) return "Размытие"
    if (item.key.endsWith("tint_color")) return "Оттенок стекла"
    if (item.key.endsWith("bevel_strength")) return "Свет по краям"
    if (item.key === "terminal.rim_width") return "Ширина края"
    if (item.key === "components.bubbles") return "Волны на кнопках"
    return item.label
  }
  function valueOf(item) { return values[item.key] === undefined ? item.default : values[item.key] }
  function change(key, value) {
    var next = Object.assign({}, values); next[key] = value; values = next
    var update = Object.assign({}, pending); update[key] = value; pending = update
    failed = false; message = "Сохраняю…"; debounce.restart()
  }
  function enqueue(args) { actions = actions.concat([args]); flush() }
  function flush() {
    if (worker.running) return
    if (Object.keys(pending).length) {
      inFlight = Object.assign({}, pending)
      worker.command = [cli, "set-json", JSON.stringify(inFlight)]
      pending = ({})
      operation = "set-json"
    } else if (actions.length) {
      var rest = actions.slice(), action = rest.shift()
      worker.command = [cli].concat(action); actions = rest; operation = action[0]
    } else return
    errors = ""; failed = false; worker.running = true
  }
  function pickColor(definition, value) {
    colorDefinition = definition
    colors.title = definition.label
    colors.alphaAllowed = !!definition.alpha
    colors.originalValue = value
    colors.load(value)
  }
  function pickChoice(definition, current) {
    choiceKey = definition.key
    choiceTitle = definition.label
    choices = definition.choices.map(function(v) { return {id:v, label:v} })
  }
  function closeOverlay() { colorDefinition = null; choiceKey = "" }
  function choose(id) {
    var key = choiceKey; choiceKey = ""
    if (key === "$group") selectedGroup = id
    else if (key === "$profile") { profileName.text = id; enqueue(["profile", "load", id]) }
    else change(key, id)
  }
  onOpenedChanged: if (opened) { schema.reload(); data.reload(); applied.reload(); profileReader.running = true }
  onModeChanged: { query = ""; if (search) search.text = "" }

  FileView {
    id: schema
    path: root.directory + "schema.json"
    watchChanges: true
    onFileChanged: reload()
    onLoaded: { try { root.catalogue = JSON.parse(text()) } catch(e) { root.message = String(e); root.failed = true } }
  }
  FileView {
    id: data
    path: root.directory + "settings.json"
    watchChanges: true
    onFileChanged: reload()
    onLoaded: {
      try { root.values = Object.assign({}, JSON.parse(text()).values, root.inFlight, root.pending) }
      catch(e) { root.message = String(e); root.failed = true }
    }
  }
  FileView {
    id: applied
    path: root.directory + "system-applied.json"
    watchChanges: true
    printErrors: false
    onFileChanged: reload()
    onLoaded: { try { root.appliedSystem = JSON.parse(text()) } catch(e) {} }
  }
  Timer { id: debounce; interval: 180; onTriggered: root.flush() }
  Process {
    id: worker
    stdout: StdioCollector {}
    stderr: StdioCollector { onStreamFinished: root.errors = text }
    onExited: function(code, status) {
      root.failed = code !== 0
      root.message = code === 0 ? "Сохранено" : (root.errors.trim() || "Не удалось применить настройку")
      root.inFlight = ({})
      data.reload(); applied.reload()
      if (root.operation === "profile") profileReader.running = true
      Qt.callLater(root.flush)
    }
  }
  Process {
    id: profileReader
    command: [root.cli, "profile", "list"]
    stdout: StdioCollector { onStreamFinished: root.profileNames = text.trim().length ? text.trim().split("\n") : [] }
  }

  Glass.LiquidBarIconButton {
    id: button
    bar: root.bar
    text: "󰒓"
    tooltipText: "Sonoma Glass"
    active: root.opened
    useActiveColor: false
    onPressed: root.toggle()
  }

  Glass.LiquidPanel {
    id: panel
    anchorItem: button
    bar: root.bar
    owner: root
    open: root.opened
    contentWidth: panel.fittedContentWidth(560)
    contentHeight: panel.fittedContentHeight(620, 620)
    focusTarget: content

    Rectangle {
      anchors.fill: parent
      anchors.margins: -10
      radius: 14
      color: "#d9263746"
    }
    Item {
      id: content
      anchors.fill: parent
      focus: true
      Keys.onEscapePressed: { if (root.overlayVisible) root.closeOverlay(); else root.close() }
      ColumnLayout {
        anchors.fill: parent
        spacing: 10
        enabled: !root.overlayVisible
        RowLayout {
          Layout.fillWidth: true
          Text { Layout.fillWidth: true; text: "Sonoma Glass"; color: "#eef4fa"; font.family: "sans-serif"; font.pixelSize: 18; font.weight: Font.DemiBold }
          GlassAction { text: "Стекло"; selected: !!root.values["components.glass"]; onClicked: root.change("components.glass", !root.values["components.glass"]) }
          GlassAction { text: "↶"; width: 32; onClicked: root.enqueue(["undo"]) }
          GlassAction { text: "✕"; width: 32; quiet: true; onClicked: root.close() }
        }
        RowLayout {
          Layout.fillWidth: true
          spacing: 6
          Repeater {
            model: [{id:"balanced", label:"Баланс"}, {id:"clear", label:"Прозрачный"}, {id:"frosted", label:"Матовый"}, {id:"quiet", label:"Спокойный"}]
            GlassAction { required property var modelData; Layout.fillWidth: true; text: modelData.label; onClicked: root.enqueue(["preset", modelData.id]) }
          }
        }
        RowLayout {
          Layout.fillWidth: true
          spacing: 4
          Repeater {
            model: [{id:"quick", label:"Основное"}, {id:"all", label:"Все параметры"}, {id:"profiles", label:"Профили"}]
            GlassAction { required property var modelData; Layout.fillWidth: true; quiet: true; selected: root.mode === modelData.id; text: modelData.label; onClicked: root.mode = modelData.id }
          }
        }
        Rectangle { Layout.fillWidth: true; height: 1; color: "#1affffff" }
        RowLayout {
          visible: root.mode === "quick"
          Layout.fillWidth: true
          spacing: 3
          Repeater {
            model: root.areas
            GlassAction { required property var modelData; Layout.fillWidth: true; quiet: true; selected: root.scope === modelData.id; text: modelData.label; onClicked: root.scope = modelData.id }
          }
        }
        GlassField {
          id: search
          visible: root.mode === "all"
          Layout.fillWidth: true
          Layout.preferredHeight: 32
          placeholderText: "Поиск по всем настройкам"
          onTextChanged: root.query = text
        }
        GlassAction {
          visible: root.mode === "all" && !root.query.length
          Layout.fillWidth: true
          text: root.groupLabel + "  ▾"
          onClicked: {
            root.choiceKey = "$group"; root.choiceTitle = "Раздел"
            root.choices = root.catalogue.groups.map(function(g) { return {id:g.id, label:g.label} })
          }
        }
        ListView {
          id: options
          visible: root.mode !== "profiles"
          Layout.fillWidth: true
          Layout.fillHeight: true
          model: root.visibleOptions
          clip: true
          boundsBehavior: Flickable.StopAtBounds
          spacing: 6
          C.ScrollBar.vertical: C.ScrollBar {
            width: 5
            policy: C.ScrollBar.AsNeeded
            contentItem: Rectangle { implicitWidth: 4; radius: 2; color: "#55d7e5f2" }
            background: Item {}
          }
          delegate: SettingRow {
            required property var modelData
            width: options.width - 12
            definition: modelData
            currentValue: root.valueOf(modelData)
            label: root.quickLabel(modelData)
            detailed: root.mode === "all"
            transparency: root.mode === "quick" && modelData.key === root.area.opacity
            onEdited: function(value) { root.change(modelData.key, value) }
            onColorRequested: function(definition, value) { root.pickColor(definition, value) }
            onChoiceRequested: function(definition, value) { root.pickChoice(definition, value) }
          }
          Text { anchors.centerIn: parent; visible: options.count === 0; text: "Ничего не найдено"; color: "#a6c1d5"; font.pixelSize: 12 }
        }
        ColumnLayout {
          visible: root.mode === "profiles"
          Layout.fillWidth: true
          Layout.fillHeight: true
          spacing: 12
          Text { text: "Мои профили"; color: "#eef4fa"; font.pixelSize: 14 }
          GlassField { id: profileName; Layout.fillWidth: true; Layout.preferredHeight: 32; placeholderText: "Название профиля" }
          RowLayout {
            Layout.fillWidth: true
            GlassAction { Layout.fillWidth: true; text: "Сохранить текущий"; onClicked: if (profileName.text.trim()) root.enqueue(["profile", "save", profileName.text.trim()]) }
            GlassAction {
              Layout.fillWidth: true; text: "Загрузить…"; enabled: root.profileNames.length > 0
              onClicked: { root.choiceKey = "$profile"; root.choiceTitle = "Загрузить профиль"; root.choices = root.profileNames.map(function(p) { return {id:p, label:p} }) }
            }
          }
          Item { Layout.preferredHeight: 16 }
          Text { text: "Перенести настройки"; color: "#eef4fa"; font.pixelSize: 14 }
          GlassField { id: jsonPath; Layout.fillWidth: true; Layout.preferredHeight: 32; text: "~/sonoma-settings.json" }
          RowLayout {
            Layout.fillWidth: true
            GlassAction { Layout.fillWidth: true; text: "Импорт"; onClicked: if (jsonPath.text.trim()) root.enqueue(["import", jsonPath.text.trim()]) }
            GlassAction { Layout.fillWidth: true; text: "Экспорт"; onClicked: if (jsonPath.text.trim()) root.enqueue(["export", jsonPath.text.trim()]) }
          }
          Item { Layout.fillHeight: true }
        }
        GlassAction {
          visible: root.showSystem
          Layout.fillWidth: true
          text: "Применить вход и загрузку…"
          onClicked: root.enqueue(["system-apply", "--gui"])
        }
        Text {
          Layout.fillWidth: true
          Layout.preferredHeight: 24
          text: root.message || (root.mode === "quick" && root.scope === "terminal" ? "Фон Foot изменится в новых окнах" : "Параметры сохраняются после изменения")
          color: root.failed ? "#ffa9b3" : "#8cafc8"
          font.family: "sans-serif"
          font.pixelSize: 10
          maximumLineCount: 2
          elide: Text.ElideRight
          wrapMode: Text.WordWrap
        }
      }
      ColorEditor {
        id: colors
        visible: root.colorDefinition !== null
        anchors.fill: parent
        onAccepted: function(value) { var key = root.colorDefinition.key; root.colorDefinition = null; root.change(key, value) }
        onCanceled: root.closeOverlay()
      }
      Rectangle {
        visible: root.choiceKey !== ""
        anchors.fill: parent
        color: "#fa263746"
        radius: 12
        MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }
        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 14
          spacing: 12
          RowLayout {
            Layout.fillWidth: true
            Text { Layout.fillWidth: true; text: root.choiceTitle; color: "#eef4fa"; font.family: "sans-serif"; font.pixelSize: 16; elide: Text.ElideRight }
            GlassAction { text: "✕"; width: 32; quiet: true; onClicked: root.closeOverlay() }
          }
          ListView {
            id: choiceList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            boundsBehavior: Flickable.StopAtBounds
            model: root.choices
            C.ScrollBar.vertical: C.ScrollBar { width: 5; contentItem: Rectangle { implicitWidth: 4; radius: 2; color: "#55d7e5f2" } background: Item {} }
            delegate: GlassAction { required property var modelData; width: choiceList.width-8; height: 34; text: modelData.label; quiet: true; onClicked: root.choose(modelData.id) }
          }
        }
      }
    }
  }
}
