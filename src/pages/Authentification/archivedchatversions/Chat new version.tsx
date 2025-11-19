// =======================================================
// 🎭 IMPORTS - THEATER ANALOGY: TOOLS FROM THE BACKSTAGE SHED
// =======================================================
// #region
// Before the play starts, the crew grabs all the props, costumes, lights, and sound gear.
// → In code: import InputBox, Sidebar, ChatMessages…

// React & Hooks
import { useState, useRef, useEffect } from "react";
import { useAnimation, motion, AnimatePresence } from "framer-motion";
import { useLocation, useParams, useNavigate } from "react-router-dom";

// Components
import InputBox from "../../../components/Chat/InputBox";
import Sidebar from "../../../components/Sidebar1";
import Settings from "../../../components/Settings";
import ChatMessages from "../../../components/Chat/ChatMessages";
import Header from "../../../components/Global/Header";
import GPTCarousel from "../../../components/Orb/GPTCarousel";
import Scene from "../../../components/Orb/Scene";
import Toolbar from "../../../components/Chat/Toolbar";
import MemoryTree from "../../../components/Chat/MemoryTree";
import ActionAnimation from "@/components/Chat/ActionAnimation";

// External Libraries
import { Button } from "@/components/ui/button";
import SonnerPositionDemo from "@/components/Toaster";
import { Toaster } from "@/components/ui/sonner";
import { Mic, MicOff, Volume2 } from "lucide-react";
import { usePersona } from "@/context/PersonaContext";

// Custom Hooks
import { useThemeEffect } from "@/hooks/Chat/useThemeEffect";
import { useSupabaseInit } from "@/hooks/Chat/useSupabaseInit";
import { useSidebarOffset } from "@/hooks/Chat/useSidebarOffset";
import { useChatLoader } from "@/hooks/Chat/useChatLoader";
import { useOrbHandlers } from "@/hooks/Chat/useOrbHandlers";
import { useUIState } from "@/hooks/Chat/useUIState";
import { useChatState } from "@/hooks/Chat/useChatState";
// #endregion

// =======================================================
// 🎭 CONSTANTS & TYPES - THEATER ANALOGY: SCRIPT & CAST LIST
// =======================================================
// #region
// The director writes down which characters exist, what lines they can say,
// and what acts are in the play.
// → In code: constants & types.

import { models } from "../../../lib/constants";
import type { Message } from "../../../lib/types";
// #endregion

// =======================================================
// 🎭 HELPERS - THEATER ANALOGY: STAGEHANDS' LITTLE GADGETS
// =======================================================
// #region
// Rope pulleys, flashlights, tape for marking floor spots.
// Small but essential helpers to keep things moving.

import {
  getHealthData,
  getPersonaColor,
  getOrCreateThread,
  supabase,
} from "../../../services/helpers";

import { speakPhoebe } from "../../../services/voice";

import {
  extractMemoriesFromResponse,
  addMemory,
  retrieveMemories,
} from "../../../services/memory";

import { sendMessage } from "../../../services/chat";
// #endregion

// =======================================================
// 🎭 THEATER ANALOGY: MAIN PERFORMANCE COMPONENT
// =======================================================
// #region
// The whole play is directed from here.
// The director keeps sticky notes:
// • "Lights: dark theme"
// • "Actor is speaking"
// • "Mic is recording"
// • "Sidebar is open"
// These notes tell the crew what the current situation on stage is.
// Inside: state (director's notebook), effects (stage cues),
// voice dictation (stenographer), sendMessage (stage manager),
// and render (stage with props and actors).

export default function Home() {
  // =======================================================
  // 🎭 STATE - THEATER ANALOGY: DIRECTOR'S NOTEBOOK
  // =======================================================
  // #region
  // The director keeps sticky notes telling the crew what the current situation on stage is.

  // -----------------------------
  // Director's Notebook: Router & Navigation - Theater Location & Scene Changes
  // -----------------------------
  const location = useLocation();
  const navigate = useNavigate();
  const { threadId } = useParams();

  const passedThreadId = location.state?.threadId;
  const orb = location.state?.orb;

  // -----------------------------
  // Director's Notebook: Persona Context - Actor's Role & Personality
  // -----------------------------
  const { getCurrentPersona, currentPersona, switchPersona } = usePersona();

  // -----------------------------
  // Director's Notebook: UI State - Stage Lighting & Set Design
  // -----------------------------
  const {
    theme,
    setTheme,
    orbColors,
    setOrbColors,
    showSettings,
    setShowSettings,
    showCarousel,
    setShowCarousel,
    sidebarOpen,
    setSidebarOpen,
    sidebarOffset,
    setSidebarOffset,
    chatVisible,
    setChatVisible,
    orbActivated,
    setOrbActivated,
    memoryTreeVisible,
    setMemoryTreeVisible,
    dropdownOpen,
    setDropdownOpen,
    toggleCarousel,
    toggleMemoryTree,
  } = useUIState();

  // -----------------------------
  // Director's Notebook: Chat State - Actor's Lines & Dialogue
  // -----------------------------
  const {
    messages,
    setMessages,
    currentThread,
    setCurrentThread,
    healthData,
    retrievedMemories,
    setRetrievedMemories,
  } = useChatLoader(threadId);

  const {
    input,
    setInput,
    handleKeyDown,
    setModel,
    model,
    isTyping,
    useMistral,
    setUseMistral,
    useVoice,
    setUseVoice,
    handleMemoryTest,
    handleSendClick,
  } = useChatState({
    currentThread,
    setMessages,
    setCurrentThread,
    setRetrievedMemories,
    healthData,
    getCurrentPersona,
    currentPersona,
  });

  // -----------------------------
  // Director's Notebook: Stage Equipment & Special Effects
  // -----------------------------
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const sidebarControls = useAnimation();

  // -----------------------------
  // Director's Notebook: Orb Hold Handlers - Stage Manager's Controls
  // -----------------------------
  const { handleOrbMouseDown, handleOrbMouseUp, isOrbHolding, isListening } =
    useOrbHandlers({ setShowCarousel, setInput });
  // #endregion

  // =======================================================
  // 🎭 EFFECTS - THEATER ANALOGY: AUTOMATIC STAGE CUES
  // =======================================================
  // #region
  // Some things just happen when the play reaches a certain point:
  // • Lights dim at Act 2
  // • Spotlight turns on when main actor enters
  // • Curtains close at the end
  // → In code: useEffect automatically runs: connect Supabase, apply theme, animate orb, load chat history.

  // Initialization & Theme Effects
  useSupabaseInit();
  useThemeEffect(theme);
  useSidebarOffset(sidebarOpen, sidebarRef);

  useEffect(() => {
    // Orb activation delay
    const timer = setTimeout(() => {
      setOrbColors(orb?.colors ?? ["#93c5fd", "#3b82f6"]);
      setChatVisible(true);
      setTimeout(() => setOrbActivated(true), 500);
    }, 800);
    return () => clearTimeout(timer);
  }, []);
  // #endregion

  // =======================================================
  // 🎭 VOICE DICTATION - THEATER ANALOGY: THE COURT STENOGRAPHER IN THE WINGS
  // =======================================================
  // #region
  // Actors speak, and a stenographer instantly writes down their words for the script.
  // → In code: startDictation() → mic records → Whisper transcribes → text gets dropped into input.
  // #endregion

  // =======================================================
  // 🎭 SEND MESSAGE - THEATER ANALOGY: THE STAGE MANAGER'S COMMUNICATION BOOTH
  // =======================================================
  // #region
  // When an actor delivers a new line (user types a message):
  // 1. Stage manager pins the line on the script board (update messages).
  // 2. Files a copy in the theater's archive (insert into Supabase).
  // 3. If it's a special type of note (todo, memory, health check) → it goes to the right department backstage (local logic).
  // 4. Otherwise, the line is radioed to HQ (backend /chat) where a writer (LLM) prepares the assistant's reply.
  // 5. The assistant's reply is pinned on the board and archived too.
  // 6. If it's a special line (actor speaks, mic is recording), it goes to the stenographer (local dictation).

  // Update the sendMessage function to use PersonaContext

  // Add this helper function to parse memory blocks from your backend

  // Add this function to manually retrieve memories for testing

  // Add this to your InputBox props to test memory retrieval
  // #endregion

  // =======================================================
  // 🎭 RENDER - THEATER ANALOGY: THE STAGE ITSELF
  // =======================================================
  // #region
  // Finally, everything shows up on stage for the audience:
  // • Actors (ChatMessages) speak lines.
  // • Props (Sidebar, Header, Settings) decorate the stage.
  // • Special effects (Orb glowing, animations) add drama.
  // • InputBox is the actor's microphone, where new lines get delivered.
  // The stage is what the user sees. Everything else (imports, helpers, state, effects) is backstage crew making sure the show runs smoothly.
  return (
    <div
      className={`h-screen w-full flex ${
        theme === "dark"
          ? "bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white"
          : "bg-gradient-to-br from-gray-50 via-white to-gray-100 text-gray-900"
      }`}
    >
      {/* Simplified Sidebar */}
      <Sidebar
        theme={theme}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      {/* Main Chat Area - No layout shift */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Header with hamburger menu */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <div className="w-6 h-6 flex flex-col gap-1">
              <div className="w-5 h-0.5 bg-current rounded-full" />
              <div className="w-4 h-0.5 bg-current rounded-full" />
              <div className="w-5 h-0.5 bg-current rounded-full" />
            </div>
          </button>
          <h1 className="text-lg font-semibold">ChatGPT</h1>
          <div className="w-10" /> {/* Spacer */}
        </div>

        {/* Welcome Orb - Only show when no messages */}
        {!chatVisible && messages.length === 0 && (
          <div
            onClick={() => {
              setOrbColors(orb?.colors ?? ["#93c5fd", "#3b82f6"]);
              setChatVisible(true);
              setTimeout(() => setOrbActivated(true), 500);
            }}
            className="flex-1 flex items-center justify-center cursor-pointer"
          >
            <div
              className={`transition-all duration-1000 ${
                orbActivated ? "prismGlow" : ""
              } w-72 h-72 rounded-full overflow-hidden`}
            >
              <Scene />
            </div>
          </div>
        )}
        {/* ░░░ HEADER ░░░ */}
        <Header
          theme={theme}
          sidebarOffset={sidebarOffset}
          personaName={currentPersona?.name}
          personaDescription={currentPersona?.description}
        />
        {/* Chat Messages - Takes remaining space */}
        <div className="flex-1 min-h-0">
          <ChatMessages messages={messages} theme={theme} isTyping={isTyping} />
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="flex-shrink-0 p-4">
          {/* Carousel overlay */}
          {showCarousel && (
            <div className="absolute bottom-20 left-0 right-0 z-50">
              <GPTCarousel
                theme={theme}
                onSelect={() => setShowCarousel(false)}
              />
            </div>
          )}

          <InputBox
            theme={theme}
            textareaRef={textareaRef}
            input={input}
            setInput={setInput}
            handleKeyDown={handleKeyDown}
            setModel={setModel}
            model={model}
            dropdownOpen={dropdownOpen}
            setDropdownOpen={setDropdownOpen}
            sendMessage={handleSendClick}
            useMistral={useMistral}
            setUseMistral={setUseMistral}
            useVoice={useVoice}
            setUseVoice={setUseVoice}
            onToggleMemoryTree={toggleMemoryTree}
            memoryTreeVisible={memoryTreeVisible}
            onMemoryTest={handleMemoryTest}
          />
        </div>
      </div>

      {/* Memory Tree Overlay */}
      {memoryTreeVisible && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <MemoryTree
            isVisible={memoryTreeVisible}
            memories={retrievedMemories}
            theme={theme}
            onToggle={toggleMemoryTree}
          />
        </div>
      )}
    </div>
  );
}

// #endregion
