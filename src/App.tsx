import { ChatModal } from "@/components/ChatModal";
import GlowLogo from "@/components/logos/glow-logo";
import { NotificationDrawer } from "@/components/NotificationDrawer";
import { PinchToHomeHandler } from "@/components/PinchToHomeHandler";
import { Button } from "@/components/ui/button";
import Navigation from "@/components/ui/navigation";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/context/ThemeContext";
import { WebSocketProvider } from "@/context/WebSocketContext";
import { Menu } from "lucide-react";
import {
  Route,
  BrowserRouter as Router,
  Routes,
  useNavigate,
} from "react-router-dom";
import { AuthProvider } from "./components/auth/AuthContext";
import AuthBox from "./pages/Authentification/LoginPage";
import Profile from "./pages/Authentification/Profile";
import TheGlowProject from "./pages/TheGlowProject.com/About";
import ARSAFoundation from "./pages/TheGlowProject.com/ARSAFoundation";
import GlowGPT from "./pages/TheGlowProject.com/GlowGPT";
import GlowProcess from "./pages/TheGlowProject.com/GlowProcess";
import TheGlowFoundation from "./pages/TheGlowProject.com/TheGlowFoundation";

function GlobalNavbar() {
  const navigate = useNavigate();

  return (
    <header className="fixed top-0 inset-x-0 z-50 flex justify-center px-4 pt-4">
      <div className="w-full max-w-7xl mx-auto relative">
        <div className="rounded-full px-6 py-3 border border-white/10 bg-zinc-900/70 shadow-[0_8px_30px_rgba(0,0,0,0.4)] backdrop-blur-2xl">
          <nav className="flex items-center justify-between">
            {/* Left Side: Logo + Navigation */}
            <div className="flex items-center gap-6">
              <a
                href="/"
                onClick={(e) => {
                  e.preventDefault();
                  navigate("/");
                }}
                className="flex items-center gap-2 text-lg font-bold text-white hover:text-[#e1e65c] transition-colors"
              >
                <GlowLogo />
                <span className="hidden sm:inline">The Glow Project</span>
              </a>
              <Navigation />
            </div>

            {/* Right Side: Actions */}
            <div className="flex items-center gap-3">
              <a
                href="/login"
                onClick={(e) => {
                  e.preventDefault();
                  navigate("/login");
                }}
                className="hidden md:block text-sm text-zinc-300 hover:text-white transition-colors"
              >
                Sign in
              </a>
              <Button
                asChild
                className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-full shadow-sm hidden sm:flex"
              >
                <a
                  href="/the-glow-foundation"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/the-glow-foundation");
                  }}
                >
                  Get Started
                </a>
              </Button>

              {/* Mobile Menu */}
              <Sheet>
                <SheetTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0 md:hidden text-white hover:bg-white/10 rounded-full"
                  >
                    <Menu className="size-5" />
                    <span className="sr-only">Toggle navigation menu</span>
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="bg-zinc-900 border-zinc-800">
                  <nav className="grid gap-6 text-lg font-medium">
                    <a
                      href="/"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/");
                      }}
                      className="flex items-center gap-2 text-xl font-bold text-white"
                    >
                      <GlowLogo />
                      <span>The Glow Project</span>
                    </a>
                    <a
                      href="/the-glow-foundation"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/the-glow-foundation");
                      }}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      Foundation
                    </a>
                    <a
                      href="/glow-process"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/glow-process");
                      }}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      Glow Process
                    </a>
                    <a
                      href="/glowgpt"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/glowgpt");
                      }}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      GlowGPT
                    </a>
                    <a
                      href="/arsafoundation"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/arsafoundation");
                      }}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      ARSA Foundation
                    </a>
                    <a
                      href="/about"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/about");
                      }}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      About
                    </a>
                    <a
                      href="/login"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate("/login");
                      }}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      Sign in
                    </a>
                  </nav>
                </SheetContent>
              </Sheet>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <WebSocketProvider>
            <PinchToHomeHandler />
            <GlobalNavbar />
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
