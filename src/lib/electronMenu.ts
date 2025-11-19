export const MENU_CHANNELS = [
  "new-chat",
  "save-chat-pdf",
  "sync-supabase",
  "toggle-orb",
  "show-memory-tree",
  "toggle-superpowers",
  "glow-mode",
  "show-philosophy",
] as const;

export type MenuChannel = (typeof MENU_CHANNELS)[number];

export const isMenuChannel = (value: string): value is MenuChannel =>
  (MENU_CHANNELS as readonly string[]).includes(value);
