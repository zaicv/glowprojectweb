import { lazy, Suspense } from "react";
import {
  BrowserRouter as Router,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import TheGlowFoundation from "./pages/lateron/TheGlowProject.com/TheGlowFoundation";
import GlowProcess from "./pages/lateron/TheGlowProject.com/GlowProcess";
import GlowGPT from "./pages/lateron/TheGlowProject.com/GlowGPT";
import ARSAFoundation from "./pages/lateron/TheGlowProject.com/ARSAFoundation";
import TheGlowProject from "./pages/lateron/TheGlowProject.com/About";

const ENABLE_FULL_APP =
  import.meta.env.VITE_ENABLE_FULL_APP === "true";

const LegacyApp = ENABLE_FULL_APP
  ? lazy(() => import("./AppLegacy"))
  : null;

function MarketingSite() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TheGlowFoundation />} />
        <Route path="/the-glow-foundation" element={<TheGlowFoundation />} />
        <Route path="/glow-process" element={<GlowProcess />} />
        <Route path="/glowgpt" element={<GlowGPT />} />
        <Route path="/arsafoundation" element={<ARSAFoundation />} />
        <Route path="/about" element={<TheGlowProject />} />
        <Route path="/the-glow-project" element={<TheGlowProject />} />
        <Route path="*" element={<Navigate to="/the-glow-foundation" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  if (ENABLE_FULL_APP && LegacyApp) {
    return (
      <Suspense
        fallback={
          <div className="flex min-h-screen items-center justify-center bg-black text-white">
            Loading experience...
          </div>
        }
      >
        <LegacyApp />
      </Suspense>
    );
  }

  return <MarketingSite />;
}

export default App;
