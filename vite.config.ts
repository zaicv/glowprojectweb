import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import fs from "fs";

export default defineConfig({
  plugins: [react()],
  base: "./", // ✅ keep this if you want relative asset paths
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    historyApiFallback: true, // ✅ for React Router
    host: "0.0.0.0", // ✅ so Tailscale can reach it
    port: 5174,
    strictPort: true,
  },
  build: {
    outDir: "dist",
    // Use esbuild instead of terser (faster and already included)
    minify: "esbuild",
    rollupOptions: {
      output: {
        manualChunks: {
          // Split large dependencies into separate chunks
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
          three: ["three", "@react-three/fiber", "@react-three/drei"],
          ui: [
            "@radix-ui/react-dialog",
            "@radix-ui/react-dropdown-menu",
            "@radix-ui/react-popover",
          ],
        },
      },
    },
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000,
    // Enable source maps only in dev
    sourcemap: false,
  },
});
