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
      className={`relative h-screen w-full flex flex-col overflow-hidden ${
        theme === "dark"
          ? "bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white"
          : "bg-gradient-to-br from-gray-50 via-white to-gray-100 text-gray-900"
      }`}
      style={{ margin: 0, padding: 0 }}
    >
      {/* Always render UI; fade in with opacity */}
      <div
        className={`transition-opacity duration-1000 ${
          chatVisible ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
      >
        {/* ░░░ SETTINGS ░░░ */}
        <Settings
          showSettings={showSettings}
          setShowSettings={setShowSettings}
          theme={theme}
          setTheme={setTheme}
          sidebarOffset={sidebarOffset}
        />

        {/* ░░░ HEADER ░░░ */}
        <Header
          theme={theme}
          sidebarOffset={sidebarOffset}
          personaName={currentPersona?.name}
          personaDescription={currentPersona?.description}
        />

        {/* Remove the bottom right persona indicator since it's now in the header */}

        {/* ░░░ SIDEBAR ░░░ */}
        <Sidebar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          sidebarControls={sidebarControls}
          sidebarRef={sidebarRef}
          sidebarOffset={sidebarOffset}
          theme={theme}
        />
      </div>

      {/* ░░░ HOME ORB ░░░ */}
      <div
        onClick={() => {
          if (!chatVisible) {
            setOrbColors(orb?.colors ?? ["#93c5fd", "#3b82f6"]);
            setChatVisible(true);
            setTimeout(() => setOrbActivated(true), 500);
          }
        }}
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-0 cursor-pointer"
        style={{
          pointerEvents: chatVisible ? "none" : "auto",
          width: 300,
          height: 300,
        }}
      >
        <div
          className={`transition-all duration-1000 ${
            orbActivated ? "prismGlow" : ""
          }`}
          style={{
            width: "100%",
            height: "100%",
            borderRadius: "9999px",
            overflow: "hidden",
          }}
        >
          <Scene /> {/* replaces <HomeOrb /> */}
        </div>
      </div>

      {/* MAIN SCROLL AREA */}
      <div
        className={`flex-1 flex flex-col overflow-y-auto transition-opacity duration-1000 will-change-opacity ${
          chatVisible
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }`}
        style={{ position: "relative", zIndex: 10 }}
      >
        {/* ░░░ CHAT MESSAGES ░░░ */}
        <ChatMessages messages={messages} theme={theme} isTyping={isTyping} />

        {/* ░░░ INPUT SECTION ░░░ */}
        <div
          className="relative z-50 mb-24 px-4 sm:px-6 md:px-8"
          style={{ marginTop: "20px" }}
        >
          {/* Input Box */}
          {showCarousel && (
            <div className="absolute bottom-28 w-full z-50">
              <GPTCarousel
                theme={theme}
                onSelect={() => setShowCarousel(false)}
              />
            </div>
          )}

          <InputBox
            sidebarOffset={sidebarOffset}
            theme={theme}
            textareaRef={textareaRef}
            input={input}
            setInput={setInput}
            handleKeyDown={handleKeyDown}
            setModel={setModel}
            model={model}
            dropdownOpen={dropdownOpen}
            setDropdownOpen={setDropdownOpen}
            models={models}
            sendMessage={handleSendClick}
            useMistral={useMistral}
            setUseMistral={setUseMistral}
            toggleCarousel={toggleCarousel}
            useVoice={useVoice}
            setUseVoice={setUseVoice}
            onAddDownloadTask={function (url: string): void {
              throw new Error("Function not implemented.");
            }}
            onToggleMemoryTree={toggleMemoryTree}
            memoryTreeVisible={memoryTreeVisible}
            onMemoryTest={handleMemoryTest}
          />
        </div>
      </div>

      {/* ░░░ ORB-BASED DICTATION INPUT ░░░ */}
      <AnimatePresence>
        {chatVisible && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.8 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50"
          >
            <div className="relative">
              {/* Dictation Orb with TheGlowOrb visual style */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onMouseDown={handleOrbMouseDown}
                onMouseUp={handleOrbMouseUp}
                onMouseLeave={handleOrbMouseUp}
              >
                <motion.div
                  className={`z-0 cursor-pointer bg-[#f9f9f9] border border-[#ddd] rounded-full shadow-sm transition-all duration-200 ${
                    isOrbHolding ? "scale-110 shadow-lg" : ""
                  }`}
                  style={{ width: 64, height: 64 }}
                >
                  <motion.div
                    style={{
                      width: "100%",
                      height: "100%",
                      borderRadius: "9999px",
                      overflow: "hidden",
                    }}
                  >
                    <Scene />
                  </motion.div>
                </motion.div>

                {/* Animated rings like TheGlowOrb */}
                <motion.div
                  className="absolute inset-0 rounded-full border-2 border-[#bbb]"
                  animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.8, 0.5] }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />

                <motion.div
                  className="absolute inset-0 rounded-full border border-[#bbb]"
                  animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0, 0.3] }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />

                {/* Listening state ring */}
                {isListening && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-red-400"
                    initial={{ scale: 1, opacity: 0.5 }}
                    animate={{ scale: 1.2, opacity: 1 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                  />
                )}

                {/* Hold state ring */}
                {isOrbHolding && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-blue-400"
                    initial={{ scale: 1, opacity: 0.5 }}
                    animate={{ scale: 1.2, opacity: 1 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                  />
                )}
              </motion.div>

              {/* Status indicator */}
              <AnimatePresence>
                {isListening && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-black/80 text-white text-xs px-3 py-1 rounded-full backdrop-blur-sm"
                  >
                    Listening...
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Memory Tree */}
      <MemoryTree
        isVisible={memoryTreeVisible}
        memories={retrievedMemories}
        theme={theme}
        onToggle={toggleMemoryTree}
      />
    </div>
  );
}
// #endregion
