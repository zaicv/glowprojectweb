const { contextBridge, ipcRenderer } = require("electron");

const MENU_CHANNELS = [
  "new-chat",
  "save-chat-pdf",
  "sync-supabase",
  "toggle-orb",
  "show-memory-tree",
  "toggle-superpowers",
  "glow-mode",
  "show-philosophy",
];

contextBridge.exposeInMainWorld("electronAPI", {
  onMenuEvent(channel, callback) {
    if (!MENU_CHANNELS.includes(channel) || typeof callback !== "function") {
      return () => {};
    }
    const subscription = (_event, ...args) => callback(...args);
    ipcRenderer.on(channel, subscription);
    return () => ipcRenderer.removeListener(channel, subscription);
  },
  onOverlayEvent(channel, callback) {
    if (typeof callback !== "function") return () => {};
    const subscription = () => callback();
    ipcRenderer.on(`overlay-${channel}`, subscription);
    return () => ipcRenderer.removeListener(`overlay-${channel}`, subscription);
  },
  hideOverlay() {
    ipcRenderer.send("overlay-hide-request");
  },
});
