import { ChatModal } from "@/components/ChatModal";
import GlowLogo from "@/components/logos/glow-logo";
import NavbarNew from "@/components/navbarnew";
import { NotificationDrawer } from "@/components/NotificationDrawer";
import { PinchToHomeHandler } from "@/components/PinchToHomeHandler";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/context/ThemeContext";
import { WebSocketProvider } from "@/context/WebSocketContext";
import {
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AuthProvider } from "./components/auth/AuthContext";
import AuthBox from "./pages/Authentification/LoginPage";
import Profile from "./pages/Authentification/Profile";
import TheGlowProject from "./pages/TheGlowProject.com/About";
import ARSAFoundation from "./pages/TheGlowProject.com/ARSAFoundation";
import GlowGPT from "./pages/TheGlowProject.com/GlowGPT";
import GlowProcess from "./pages/TheGlowProject.com/GlowProcess";
import TheGlowFoundation from "./pages/TheGlowProject.com/TheGlowFoundation";

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <WebSocketProvider>
            <PinchToHomeHandler />
            <NavbarNew 
              logo={<GlowLogo />}
              name="The Glow Project"
              homeUrl="/"
              mobileLinks={[
                { text: "Foundation", href: "/the-glow-foundation" },
                { text: "Glow Process", href: "/glow-process" },
                { text: "GlowGPT", href: "/glowgpt" },
                { text: "ARSA Foundation", href: "/arsafoundation" },
                { text: "About", href: "/about" },
              ]}
              actions={[
                { text: "Sign in", href: "/login", isButton: false },
                {
                  text: "Get Started",
                  href: "/the-glow-foundation",
                  isButton: true,
                  variant: "default",
                },
              ]}
              showNavigation={true}
            />
            <div className="fixed top-20 right-4 z-50">
              <NotificationDrawer />
            </div>
            <ChatModal />
            <Routes>
              <Route path="/" element={<TheGlowFoundation />} />
              <Route path="/the-glow-foundation" element={<TheGlowFoundation />} />
              <Route path="/glow-process" element={<GlowProcess />} />
              <Route path="/glowgpt" element={<GlowGPT />} />
              <Route path="/arsafoundation" element={<ARSAFoundation />} />
              <Route path="/about" element={<TheGlowProject />} />
              <Route path="/login" element={<AuthBox />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </WebSocketProvider>
        </AuthProvider>
      </ThemeProvider>
      <Toaster />
    </Router>
  );
}

export default App;
