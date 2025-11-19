import { NotificationDrawer } from "@/components/NotificationDrawer";
import { PinchToHomeHandler } from "@/components/PinchToHomeHandler";
import { AppSidebar } from "@/components/Sidebar/app-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/sonner";
import { PersonaProvider } from "@/context/PersonaContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { WebSocketProvider } from "@/context/WebSocketContext";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  Route,
  BrowserRouter as Router,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { AuthProvider } from "./components/auth/AuthContext";
import AuthBox from "./pages/Authentification/LoginPage";
import Profile from "./pages/Authentification/Profile";
import Chat from "./pages/Chat/Chat";
import GlowDev from "./pages/GlowDev";
import GlowDashboard from "./pages/Home/GlowDashboard";
import KnowledgeBase from "./pages/KnowledgeBase/KnowledgeBase";
import ChatCopy from "./pages/lateron/Chat copy";
import FolderDashboard from "./pages/lateron/FolderDashboard";
import GlowFieldPage from "./pages/lateron/GlowField";
import GPTs from "./pages/lateron/GPTsSelection";
import MoneyCopilot from "./pages/lateron/miney";
import TheGlowProject from "./pages/TheGlowProject.com/About";
import GlowGPT from "./pages/TheGlowProject.com/GlowGPT";
import Memories from "./pages/Memory/Memories";
import PersonaDesigner from "./pages/Personas/PersonaDesigner";
import Personas from "./pages/Personas/Personas";
import { default as AlauraLog, default as Phoebe } from "./pages/Superpowers/AlauraLog";
import GlowCloud from "./pages/Superpowers/GlowCloud";
import Plex from "./pages/Superpowers/Plex";
import RipDisc from "./pages/Superpowers/RipDisc";
import Superpowers from "./pages/Superpowers/Superpowers";
import YouTube from "./pages/Superpowers/YouTube";

// Prompt-Kit Chat Pages

import { useElectronMenu } from "@/hooks/useElectronMenu";
import { FullChatApp } from "./pages/Chat/FullChatApp";
import ARSAFoundation from "./pages/TheGlowProject.com/ARSAFoundation";
import GlowProcess from "./pages/TheGlowProject.com/GlowProcess";
import TheGlowFoundation from "./pages/TheGlowProject.com/TheGlowFoundation";
import MindGarden from "./pages/MindGarden/MIndGarden";
import GlowOnboarding from "./pages/Onboarding/GlowOnboarding";
import Overlay from "./pages/Overlay/Overlay";

const NAV_LINKS = [
  { label: "Foundation", path: "/the-glow-foundation" },
  { label: "Glow Process", path: "/glow-process" },
  { label: "GlowGPT", path: "/glowgpt" },
  { label: "ARSA Foundation", path: "/arsafoundation" },
  { label: "About", path: "/the-glow-project" },
];

function GlobalNavBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const navRef = useRef<HTMLDivElement>(null);
  const indicatorRef = useRef<HTMLSpanElement>(null);
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const [indicatorStyle, setIndicatorStyle] = useState<{
    width: number;
    left: number;
  }>({ width: 0, left: 0 });
  const [isNavVisible, setIsNavVisible] = useState(true);

  const handleNavigate = (path: string) => {
    if (location.pathname !== path) {
      navigate(path);
    }
  };

  const isActive = (path: string) => {
    if (path === "/chat") {
      return location.pathname === "/" || location.pathname.startsWith("/chat");
    }
    return location.pathname.startsWith(path);
  };

  // Update indicator position when route changes
  useEffect(() => {
    const updateIndicator = () => {
      const activeIndex = NAV_LINKS.findIndex((link) => {
        if (link.path === "/chat") {
          return location.pathname === "/" || location.pathname.startsWith("/chat");
        }
        return location.pathname.startsWith(link.path);
      });
      
      if (activeIndex === -1 || !buttonRefs.current[activeIndex] || !navRef.current) return;

      const activeButton = buttonRefs.current[activeIndex];
      const navRect = navRef.current.getBoundingClientRect();
      const buttonRect = activeButton.getBoundingClientRect();

      setIndicatorStyle({
        width: buttonRect.width,
        left: buttonRect.left - navRect.left,
      });
    };



    
    // Small delay to ensure DOM is ready
    const timeoutId = setTimeout(updateIndicator, 0);

    // Update on resize
    const handleResize = () => {
      requestAnimationFrame(updateIndicator);
    };

    window.addEventListener("resize", handleResize);
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener("resize", handleResize);
    };
  }, [location.pathname]);

  return (
    <div className="pointer-events-none fixed inset-x-0 top-4 z-50 flex justify-center px-4">
      <div className="pointer-events-auto flex items-center gap-3">
        <nav
          ref={navRef}
          className={`relative flex items-center gap-1 rounded-full border border-white/10 bg-zinc-900/70 px-2 py-1 shadow-[0_8px_30px_rgba(0,0,0,0.4)] backdrop-blur-2xl transition-all duration-500 ease-in-out ${
            isNavVisible ? 'translate-y-0 opacity-100' : '-translate-y-20 opacity-0 pointer-events-none'
          }`}
        >
          {/* Sliding indicator */}
          <span
            ref={indicatorRef}
            className="absolute top-1.5 h-[calc(100%-0.75rem)] rounded-full bg-black/80 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] transition-all duration-300 ease-out"
            style={{
              width: `${indicatorStyle.width}px`,
              left: `${indicatorStyle.left}px`,
            }}
          />
          
          {NAV_LINKS.map((link, index) => {
            const active = isActive(link.path);

            return (
              <button
                type="button"
                key={link.path}
                ref={(el) => {
                  buttonRefs.current[index] = el;
                }}
                onClick={() => handleNavigate(link.path)}
                className={`relative z-10 rounded-full px-4 py-2 text-sm font-medium transition-all duration-300 ${
                  active
                    ? "text-white"
                    : "text-zinc-300 hover:text-white hover:bg-white/5"
                }`}
              >
                <span className="relative whitespace-nowrap">{link.label}</span>
              </button>
            );
          })}
        </nav>
        
        {/* Toggle Button (Dot) */}
        <button
          type="button"
          onClick={() => setIsNavVisible(!isNavVisible)}
          className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-zinc-900/70 shadow-[0_8px_30px_rgba(0,0,0,0.4)] backdrop-blur-2xl transition-all duration-300 hover:bg-zinc-800/70 hover:scale-110"
          aria-label={isNavVisible ? "Hide navigation" : "Show navigation"}
        >
          <div className={`h-2 w-2 rounded-full bg-white transition-all duration-300 ${
            isNavVisible ? 'opacity-100' : 'opacity-50'
          }`} />
        </button>
      </div>
    </div>
  );
}
function ElectronMenuBridge() {
  const navigate = useNavigate();

  const handleNewChat = useCallback(() => {
    navigate("/chat");
  }, [navigate]);

  const handleShowPhilosophy = useCallback(() => {
    navigate("/the-glow-foundation");
  }, [navigate]);

  useElectronMenu({
    "new-chat": handleNewChat,
    "show-philosophy": handleShowPhilosophy,
  });

  return null;
}
function App() {
  return (
    <Router>
      <ElectronMenuBridge />
      <ThemeProvider>
        <AuthProvider>
          <PersonaProvider>
            <WebSocketProvider>
              <Routes>
                <Route path="/overlay" element={<Overlay />} />
                <Route
                  path="/*"
                  element={
                    <SidebarProvider>
                      <AppSidebar />
                      <SidebarInset>
                        <PinchToHomeHandler />
                        <GlobalNavBar />
                        <div className="fixed top-20 right-4 z-50">
                          <NotificationDrawer />
                        </div>
                        <div>
                          <Routes>
                            <Route path="/" element={<Chat />} />
                            <Route path="/glowcloud" element={<GlowCloud />} />
                            <Route path="/youtube" element={<YouTube />} />
                            <Route path="/alauralog" element={<AlauraLog />} />
                            <Route path="/ripdisc" element={<RipDisc />} />
                            <Route path="/glow-dev" element={<GlowDev />} />
                            <Route path="/chat/:threadId?" element={<Chat />} />
                            <Route path="/gpts" element={<GPTs />} />
                            <Route path="/miney" element={<MoneyCopilot />} />
                            <Route path="/personas" element={<Personas />} />
                            <Route path="/personas/create" element={<PersonaDesigner />} />
                            <Route path="/chatcopy" element={<ChatCopy />} />
                            <Route path="/fullchat" element={<FullChatApp />} />
                            <Route path="/superpowers" element={<Superpowers />} />
                            <Route path="/plex" element={<Plex />} />
                            <Route path="/phoebe" element={<Phoebe />} />
                            <Route path="/authbox" element={<AuthBox />} />
                            <Route path="/profile" element={<Profile />} />
                            <Route path="/memories" element={<Memories />} />
                            <Route path="/knowledge-base" element={<KnowledgeBase />} />
                            <Route path="/folders" element={<FolderDashboard />} />
                            <Route path="/glow-onboarding" element={<GlowOnboarding />} />
                            <Route path="/glow-field" element={<GlowFieldPage />} />
                            <Route path="/glow-dashboard" element={<GlowDashboard />} />
                            <Route path="/the-glow-foundation" element={<TheGlowFoundation />} />
                            <Route path="/glowgpt" element={<GlowGPT />} />
                            <Route path="/arsafoundation" element={<ARSAFoundation />} />
                            <Route path="/glow-process" element={<GlowProcess />} />
                            <Route path="/about" element={<TheGlowProject />} />
                            <Route path="/the-glow-project" element={<TheGlowProject />} />
                            <Route path="/mind-garden" element={<MindGarden />} />
                          </Routes>
                        </div>
                      </SidebarInset>
                    </SidebarProvider>
                  }
                />
              </Routes>
            </WebSocketProvider>
          </PersonaProvider>
        </AuthProvider>
      </ThemeProvider>
      <Toaster />
    </Router>
  );
}

export default App;
