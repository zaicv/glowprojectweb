# Phoebe Overlay Setup

## Quick Start

### Development Mode (Recommended for Testing)
```bash
npm run electron:dev
```

This will:
- Start the Vite dev server
- Launch Electron with the overlay ready
- Show console logs for debugging

### Production Build
```bash
npm run electron:build
```

Then launch the built app.

## How to Use

1. **Keyboard Shortcut**: Press `Cmd+Shift+G` (or `Ctrl+Shift+G` on Windows/Linux)
2. **Tray Icon**: Click the Phoebe icon in your menu bar (next to Spotlight/Volume)
3. **Close**: Click the backdrop or press `Cmd+Shift+G` again

## Troubleshooting

### Tray Icon Not Showing
- Check console logs when app starts
- Icon should appear in menu bar automatically
- If missing, check that `public/Phoebe.jpg` exists

### Overlay Not Appearing
- Check Electron console for errors
- Make sure Vite dev server is running (for dev mode)
- Try the keyboard shortcut: `Cmd+Shift+G`

### Debug Mode
All console logs are enabled - check the Electron console window for:
- ✅ Tray icon created successfully
- ✅ Global shortcut registered: Cmd+Shift+G
- 🚀 GlowGPT ready!
- 🔄 Toggling overlay... (when shortcut pressed)

