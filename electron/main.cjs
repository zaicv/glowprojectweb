const { app, BrowserWindow, Menu, shell, Tray, globalShortcut, nativeImage, screen, ipcMain } = require("electron");
const path = require("path");

// Only load electron-reload in development (when app is not packaged)
if (!app.isPackaged) {
  try {
    require("electron-reload")(__dirname, {
      electron: path.join(__dirname, "..", "node_modules", ".bin", "electron"),
      hardResetMethod: "exit"
    });
  } catch (err) {
    // electron-reload may not be available (shouldn't happen in dev, but safe to ignore)
    console.log("electron-reload not available:", err.message);
  }
}

// Enable hardware acceleration before app ready
app.commandLine.appendSwitch("enable-gpu-rasterization");
app.commandLine.appendSwitch("enable-zero-copy");
app.commandLine.appendSwitch("ignore-gpu-blacklist");

// Ignore SSL certificate errors in development
if (process.env.NODE_ENV !== "production" || process.env.VITE_DEV_SERVER_URL) {
  app.commandLine.appendSwitch("ignore-certificate-errors");
}

let overlayWindow = null;
let tray = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 600,
    minHeight: 400,
    show: false,
    frame: false,
    titleBarStyle: "hiddenInset",
    trafficLightPosition: { x: 12, y: 12 },
    // Temporarily disable vibrancy to test performance
    // vibrancy: "sidebar",
    // visualEffectState: "active",
    backgroundColor: "#000000", // Set a solid background instead
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      // Performance optimizations
      backgroundThrottling: false, // Prevent throttling when window is in background
      offscreen: false,
      // Enable hardware acceleration
      enableBlinkFeatures: "CSSColorSchemeUARendering",
      // Optimize rendering
      disableDialogs: false,
      sandbox: false, // Needed for some web APIs
      preload: path.join(__dirname, "preload.cjs"),
    },
  });

  // Performance: Prevent navigation throttling
  win.webContents.setFrameRate(60);

  // Handle errors in loading
  win.webContents.on("did-fail-load", (event, errorCode, errorDescription) => {
    console.error("Failed to load:", errorCode, errorDescription);
  });

  // Optimize for performance
  win.webContents.once("dom-ready", () => {
    // Enable hardware acceleration in renderer
    win.webContents.executeJavaScript(`
      // Force hardware acceleration
      document.body.style.transform = 'translateZ(0)';
      // Optimize animations
      const style = document.createElement('style');
      style.textContent = \`
        * {
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
\`;
      document.head.appendChild(style);
    `);
  });

  win.webContents.session.setCertificateVerifyProc((request, callback) => {
    if (process.env.VITE_DEV_SERVER_URL) {
      callback(0); // Allow certificate in dev
    } else {
      callback(-2); // Use default verification in production
    }
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    win
      .loadFile(path.join(app.getAppPath(), "dist/index.html"))
      .catch((err) => {
        console.error("Error loading file:", err);
        const altPath = path.join(__dirname, "../dist/index.html");
        win.loadFile(altPath).catch((err2) => {
          console.error("Alternative path also failed:", err2);
        });
      });
  }

  win.once("ready-to-show", () => win.show());

  return win;
}

function createOverlayWindow() {
  if (overlayWindow) return overlayWindow;

  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  overlayWindow = new BrowserWindow({
    width,
    height,
    x: 0,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    movable: false,
    fullscreenable: false,
    show: false,
    backgroundColor: "#00000000",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      backgroundThrottling: false,
      preload: path.join(__dirname, "preload.cjs"),
    },
  });

  const overlayURL = process.env.VITE_DEV_SERVER_URL 
    ? `${process.env.VITE_DEV_SERVER_URL}/overlay`
    : `file://${path.join(app.getAppPath(), "dist/index.html")}#/overlay`;
  
  overlayWindow.webContents.session.setCertificateVerifyProc((request, callback) => {
    if (process.env.VITE_DEV_SERVER_URL) {
      callback(0); // Allow certificate in dev
    } else {
      callback(-2); // Use default verification in production
    }
  });
  
  overlayWindow.loadURL(overlayURL).catch((err) => {
    console.error("Overlay load error:", err);
    const altPath = path.join(__dirname, "../dist/index.html");
    overlayWindow.loadFile(altPath).then(() => {
      overlayWindow.webContents.executeJavaScript(`window.location.hash = '#/overlay'`);
    });
  });

  overlayWindow.on("closed", () => { overlayWindow = null; });
  return overlayWindow;
}

function toggleOverlay() {
  console.log("🔄 Toggling overlay...");
  if (!overlayWindow) {
    console.log("📦 Creating overlay window...");
    createOverlayWindow();
    overlayWindow.once("ready-to-show", () => {
      console.log("✨ Showing overlay window");
      overlayWindow.show();
      overlayWindow.focus();
      overlayWindow.webContents.send("overlay-show");
    });
  } else if (overlayWindow.isVisible()) {
    console.log("👋 Hiding overlay window");
    overlayWindow.webContents.send("overlay-hide");
    setTimeout(() => overlayWindow.hide(), 300);
  } else {
    console.log("👀 Showing overlay window");
    overlayWindow.show();
    overlayWindow.focus();
    overlayWindow.webContents.send("overlay-show");
  }
}

function createTray() {
  let iconPath = path.join(app.getAppPath(), "public/Phoebe.jpg");
  if (!require("fs").existsSync(iconPath)) {
    iconPath = path.join(__dirname, "../public/Phoebe.jpg");
  }
  if (!require("fs").existsSync(iconPath)) {
    iconPath = path.join(process.cwd(), "public/Phoebe.jpg");
  }
  
  const icon = nativeImage.createFromPath(iconPath);
  if (icon.isEmpty()) {
    console.error("Tray icon not found at:", iconPath);
    return;
  }
  
  const resizedIcon = icon.resize({ width: 22, height: 22 });
  tray = new Tray(resizedIcon);
  
  tray.setToolTip("Phoebe - Cmd+Shift+G");
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: "Show Phoebe", click: toggleOverlay },
    { type: "separator" },
    { label: "Quit", click: () => { app.isQuitting = true; app.quit(); } },
  ]));
  
  tray.on("click", toggleOverlay);
  console.log("✅ Tray icon created successfully");
}

// 🔹 Create New Window Function
function createNewWindow() {
  const newWin = createWindow();
  newWin.focus();
}

// 🔹 Menu Template
const isMac = process.platform === "darwin";
const template = [
  ...(isMac
    ? [
        {
          label: app.name,
          submenu: [
            { role: "about", label: "About GlowGPT" },
            { type: "separator" },
            { role: "services" },
            { type: "separator" },
            { role: "hide" },
            { role: "hideothers" },
            { role: "unhide" },
            { type: "separator" },
            { role: "quit" },
          ],
        },
      ]
    : []),
  {
    label: "File",
    submenu: [
      {
        label: "New Window",
        accelerator: "CmdOrCtrl+N",
        click: () => createNewWindow(),
      },
      {
        label: "New Chat",
        accelerator: "CmdOrCtrl+T",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("new-chat");
        },
      },
      { type: "separator" },
      {
        label: "Save Chat as PDF",
        accelerator: "CmdOrCtrl+S",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("save-chat-pdf");
        },
      },
      {
        label: "Sync with Supabase",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("sync-supabase");
        },
      },
      { type: "separator" },
      isMac ? { role: "close" } : { role: "quit" },
    ],
  },
  {
    label: "Edit",
    submenu: [
      { role: "undo" },
      { role: "redo" },
      { type: "separator" },
      { role: "cut" },
      { role: "copy" },
      { role: "paste" },
      { role: "selectAll" },
    ],
  },
  {
    label: "View",
    submenu: [
      {
        label: "Toggle Orb",
        accelerator: "CmdOrCtrl+O",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("toggle-orb");
        },
      },
      {
        label: "Show Memory Tree",
        accelerator: "CmdOrCtrl+M",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("show-memory-tree");
        },
      },
      {
        label: "Toggle Superpowers",
        accelerator: "CmdOrCtrl+P",
        click: (menuItem, browserWindow) => {
          if (browserWindow)
            browserWindow.webContents.send("toggle-superpowers");
        },
      },
      {
        label: "Glow Mode",
        accelerator: "CmdOrCtrl+G",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("glow-mode");
        },
      },
      { type: "separator" },
      { role: "reload" },
      { role: "toggleDevTools" },
      { type: "separator" },
      { role: "resetZoom" },
      { role: "zoomIn" },
      { role: "zoomOut" },
      { type: "separator" },
      { role: "togglefullscreen" },
    ],
  },
  {
    label: "Window",
    submenu: [
      { role: "minimize" },
      { role: "zoom" },
      { type: "separator" },
      { role: "front" },
    ],
  },
  {
    role: "help",
    submenu: [
      {
        label: "The Glow Philosophy",
        click: (menuItem, browserWindow) => {
          if (browserWindow) browserWindow.webContents.send("show-philosophy");
        },
      },
      {
        label: "Visit Website",
        click: async () => {
          await shell.openExternal("https://theglowproject.com");
        },
      },
      {
        label: "Report a Bug",
        click: async () => {
          await shell.openExternal(
            "https://github.com/IsaiahBriggs/GlowGPT/issues"
          );
        },
      },
    ],
  },
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);

// Set About Panel info
app.setAboutPanelOptions({
  applicationName: "GlowGPT",
  applicationVersion: "1.0.0",
  credits: "Developed by The Glow Project",
  website: "https://theglowproject.com",
  copyright: "© 2025 Isaiah Briggs",
});

// Handle uncaught errors
process.on("uncaughtException", (error) => {
  console.error("Uncaught Exception:", error);
});

app.whenReady().then(() => {
  app.commandLine.appendSwitch("enable-features", "VaapiVideoDecoder");
  createWindow();
  
  try {
    createTray();
  } catch (err) {
    console.error("❌ Failed to create tray:", err);
  }
  
  createOverlayWindow();
  
  const registered = globalShortcut.register("CommandOrControl+Shift+G", () => {
    console.log("⌨️  Global shortcut triggered");
    toggleOverlay();
  });
  
  if (!registered) {
    console.error("❌ Failed to register global shortcut");
  } else {
    console.log("✅ Global shortcut registered: Cmd+Shift+G");
  }
  
  ipcMain.on("overlay-hide-request", () => {
    if (overlayWindow && overlayWindow.isVisible()) {
      overlayWindow.webContents.send("overlay-hide");
      setTimeout(() => overlayWindow.hide(), 300);
    }
  });
  
  console.log("🚀 GlowGPT ready! Press Cmd+Shift+G or click tray icon to show Phoebe");
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});
