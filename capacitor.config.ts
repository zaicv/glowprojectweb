import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.glow.app",
  appName: "glow",
  webDir: "dist",
  server: {
    url: "https://100.83.147.76:5173", // 👈 Replace with YOUR Mac's local IP
    cleartext: true,
  },
};

export default config;
