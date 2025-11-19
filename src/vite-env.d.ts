/// <reference types="vite/client" />

import type { MenuChannel } from "./lib/electronMenu";

declare global {
  interface ElectronAPI {
    onMenuEvent: (
      channel: MenuChannel,
      callback: (...args: unknown[]) => void
    ) => () => void;
  }

  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
