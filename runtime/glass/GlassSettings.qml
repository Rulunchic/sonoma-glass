pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

QtObject {
  id: root
  property var values: ({})
  function value(key, fallback) {
    var v = values[key]
    return v === undefined ? fallback : v
  }
  property FileView source: FileView {
    path: Quickshell.env("HOME") + "/.config/omarchy/sonoma-glass/applied.json"
    watchChanges: true
    printErrors: false
    onFileChanged: reload()
    onLoaded: {
      try { root.values = JSON.parse(text()).values || ({}) }
      catch (e) { console.warn("Sonoma settings:", e) }
    }
  }
}
