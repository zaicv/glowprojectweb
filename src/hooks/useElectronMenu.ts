import { useEffect, useRef } from "react";
import { MENU_CHANNELS, type MenuChannel } from "@/lib/electronMenu";

type MenuHandlerMap = Partial<Record<MenuChannel, () => void | Promise<void>>>;

/**
 * Subscribes to native Electron menu events that are bridged through preload.
 * Handlers remain up-to-date without resubscribing.
 */
export function useElectronMenu(handlers: MenuHandlerMap) {
  const handlersRef = useRef<MenuHandlerMap>(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  useEffect(() => {
    const api = (window as any)?.electronAPI;
    if (!api?.onMenuEvent) {
      return;
    }

    const cleanups = MENU_CHANNELS.map((channel) =>
      api.onMenuEvent(channel, () => {
        const handler = handlersRef.current[channel];
        handler?.();
      })
    );

    return () => {
      cleanups.forEach((cleanup: (() => void) | undefined) => cleanup?.());
    };
  }, []);
}
