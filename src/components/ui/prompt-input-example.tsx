"use client";

import React, { useState } from "react";
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputActions,
  PromptInputSend,
} from "./prompt-input";

export function PromptInputExample() {
  const [value, setValue] = useState("");
  const [theme, setTheme] = useState<"light" | "dark" | "system">("light");

  const handleSubmit = () => {
    console.log("Submitted:", value);
    setValue("");
  };

  return (
    <div className={`p-8 ${theme === "dark" ? "bg-gray-900" : "bg-white"}`}>
      <div className="max-w-2xl mx-auto space-y-4">
        <div className="flex gap-2">
          <button
            onClick={() => setTheme("light")}
            className="px-3 py-1 rounded bg-gray-200 text-black"
          >
            Light
          </button>
          <button
            onClick={() => setTheme("dark")}
            className="px-3 py-1 rounded bg-gray-800 text-white"
          >
            Dark
          </button>
        </div>

        <PromptInput
          value={value}
          onValueChange={setValue}
          onSubmit={handleSubmit}
          theme={theme}
        >
          <PromptInputTextarea
            placeholder="Type your message..."
            className={theme === "dark" ? "text-white" : "text-black"}
          />
          <PromptInputActions>
            <PromptInputSend theme={theme} size="md" />
          </PromptInputActions>
        </PromptInput>
      </div>
    </div>
  );
}
