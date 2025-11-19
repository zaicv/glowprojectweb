# 🧩 Prompt-Kit Components Reference

A visual guide to the prompt-kit components used in your chat pages.

---

## 📦 Component Library

All components are located in `/src/components/ui/`

### Core Chat Components

#### 1. **PromptInput**

The main container for the chat input area.

```typescript
<PromptInput
  value={input}
  onValueChange={setInput}
  onSubmit={handleSendClick}
  className="shadow-lg"
>
  {/* Children go here */}
</PromptInput>
```

**Features:**

- Auto-resizing container
- Smooth focus animations
- Click-to-focus anywhere in the container
- Context provider for child components

**Props:**

- `value` - Current input text
- `onValueChange` - Callback when text changes
- `onSubmit` - Callback when Enter is pressed
- `maxHeight` - Maximum height before scrolling (default: 240px)
- `isLoading` - Disable input during loading

---

#### 2. **PromptInputTextarea**

Auto-growing textarea that expands with content.

```typescript
<PromptInputTextarea
  ref={textareaRef}
  placeholder="Message..."
  className="text-white"
/>
```

**Features:**

- Auto-resize as user types
- Smooth height transitions
- IME composition support (for Asian languages)
- Submit on Enter, new line on Shift+Enter

**Props:**

- All standard textarea props
- `disableAutosize` - Disable auto-resizing
- `ref` - Forward ref for focus control

---

#### 3. **PromptInputActions**

Container for action buttons (attach, send, etc.)

```typescript
<PromptInputActions>
  <button>Action 1</button>
  <button>Action 2</button>
</PromptInputActions>
```

**Features:**

- Flex layout with gap
- Fade-in animation
- Responsive spacing

---

#### 4. **PromptInputAction**

Individual action button with tooltip.

```typescript
<PromptInputAction tooltip="Attach file" side="top">
  <button>
    <Paperclip className="w-5 h-5" />
  </button>
</PromptInputAction>
```

**Features:**

- Animated tooltip on hover
- Hover/tap scale animations
- Automatic disabled state
- Customizable tooltip position

**Props:**

- `tooltip` - Tooltip content
- `side` - Tooltip position: top/bottom/left/right

---

#### 5. **SendButton**

Animated send button with loading states.

```typescript
<SendButton
  onClick={handleSendClick}
  disabled={!input.trim() || isTyping}
  theme="dark"
  size="lg"
/>
```

**Features:**

- Hover/tap animations
- Theme-aware styling
- Disabled state styling
- ArrowUp icon built-in

**Props:**

- `onClick` - Send callback
- `disabled` - Disable button
- `theme` - "light" | "dark" | "system"
- `size` - "sm" | "md" | "lg"

---

#### 6. **ChatContainerRoot**

Scrollable container with auto-scroll to bottom.

```typescript
<ChatContainerRoot className="flex-1">
  <ChatContainerContent>{/* Messages go here */}</ChatContainerContent>
</ChatContainerRoot>
```

**Features:**

- Auto-scroll to bottom on new messages
- Smooth resize handling
- Instant initial scroll
- Accessible scroll area (role="log")

**Uses:** `use-stick-to-bottom` library for smart scrolling

---

#### 7. **ChatContainerContent**

Content wrapper for messages.

```typescript
<ChatContainerContent>
  <div className="space-y-6">
    {messages.map((msg) => (
      <Message key={msg.id} />
    ))}
  </div>
</ChatContainerContent>
```

**Features:**

- Flex column layout
- Full width
- Works with stick-to-bottom

---

### Supporting Components

#### 8. **Avatar & AvatarFallback**

User/AI avatars with fallback content.

```typescript
<Avatar className="h-8 w-8">
  <AvatarImage src="/user.jpg" />
  <AvatarFallback className="bg-purple-500 text-white">
    <User className="w-4 h-4" />
  </AvatarFallback>
</Avatar>
```

**Features:**

- Automatic fallback when no image
- Radix UI Avatar (accessible)
- Circular by default
- Customizable size and colors

---

#### 9. **ScrollArea**

Custom scrollbar with smooth scrolling.

```typescript
<ScrollArea className="h-full">{/* Scrollable content */}</ScrollArea>
```

**Features:**

- Custom styled scrollbar
- Smooth scroll behavior
- Cross-browser consistent
- Radix UI ScrollArea

---

#### 10. **Button**

Styled button with variants.

```typescript
<Button variant="outline" className="w-full gap-2">
  <Plus className="w-5 h-5" />
  New Chat
</Button>
```

**Variants:**

- `default` - Solid background
- `outline` - Border only
- `ghost` - Transparent
- `link` - Text link style

**Sizes:**

- `sm` - Small button
- `md` - Medium (default)
- `lg` - Large button

---

## 🎨 Layout Patterns

### Pattern 1: Full Chat Layout

```typescript
<div className="h-screen flex flex-col">
  {/* Header */}
  <header className="flex-shrink-0">{/* Fixed header content */}</header>

  {/* Messages (scrollable) */}
  <div className="flex-1 overflow-hidden">
    <ScrollArea className="h-full">{/* Messages */}</ScrollArea>
  </div>

  {/* Input (fixed bottom) */}
  <div className="flex-shrink-0">
    <PromptInput>{/* Input components */}</PromptInput>
  </div>
</div>
```

**Key points:**

- `flex-1` on messages area for growth
- `flex-shrink-0` on header/input to prevent squishing
- `overflow-hidden` on messages container
- `h-full` on ScrollArea

---

### Pattern 2: Sidebar + Chat Layout

```typescript
<div className="h-screen flex">
  {/* Sidebar */}
  <aside className="w-80 flex-shrink-0">{/* Sidebar content */}</aside>

  {/* Main chat */}
  <div className="flex-1 flex flex-col min-w-0">{/* Use Pattern 1 here */}</div>
</div>
```

**Key points:**

- `min-w-0` on main area for proper flex behavior
- Fixed width sidebar with `flex-shrink-0`
- `flex-1` on chat area for remaining space

---

### Pattern 3: Message Item

```typescript
<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  className="flex gap-4"
>
  {/* Avatar */}
  <Avatar className="h-8 w-8 flex-shrink-0">{/* Avatar content */}</Avatar>

  {/* Message */}
  <div className="flex-1 space-y-2">
    <div className="flex items-center gap-2">
      <span className="font-semibold text-sm">Username</span>
      <span className="text-xs opacity-40">Timestamp</span>
    </div>
    <div className="prose">
      <p>{message.content}</p>
    </div>
  </div>
</motion.div>
```

**Key points:**

- `flex-shrink-0` on avatar to prevent squishing
- `flex-1` on message content for growth
- `space-y-2` for vertical spacing
- Framer Motion for entrance animation

---

### Pattern 4: Typing Indicator

```typescript
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  className="flex gap-4"
>
  <Avatar className="h-8 w-8">{/* Bot avatar */}</Avatar>
  <div className="flex items-center gap-1 pt-2">
    {[0, 150, 300].map((delay) => (
      <div
        key={delay}
        className="w-2 h-2 rounded-full bg-white/60 animate-bounce"
        style={{ animationDelay: `${delay}ms` }}
      />
    ))}
  </div>
</motion.div>
```

**Key points:**

- Staggered animation delays for wave effect
- Same layout as message for consistency
- Fade in/out with AnimatePresence

---

## 🎯 Common Recipes

### Recipe 1: Theme-Aware Styling

```typescript
const baseClass = "p-4 rounded-lg";
const themedClass = cn(
  baseClass,
  theme === "dark" ? "bg-white/10 text-white" : "bg-black/10 text-black"
);

return <div className={themedClass}>Content</div>;
```

---

### Recipe 2: Responsive Sidebar Toggle

```typescript
const [sidebarOpen, setSidebarOpen] = useState(true);

// Mobile: always toggle
// Desktop: always visible
return (
  <>
    <AnimatePresence>
      {sidebarOpen && (
        <motion.aside
          initial={{ x: -320, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -320, opacity: 0 }}
        >
          {/* Sidebar content */}
        </motion.aside>
      )}
    </AnimatePresence>

    <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden">
      <Menu />
    </button>
  </>
);
```

---

### Recipe 3: Auto-Scroll on New Messages

```typescript
const scrollAreaRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (scrollAreaRef.current) {
    const scrollContainer = scrollAreaRef.current.querySelector(
      "[data-radix-scroll-area-viewport]"
    );
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }
}, [messages, isTyping]);

return <ScrollArea ref={scrollAreaRef}>{/* Content */}</ScrollArea>;
```

---

### Recipe 4: Suggestion Pills

```typescript
const suggestions = [
  "Tell me a joke",
  "Help me brainstorm",
  "Explain quantum physics",
];

return (
  <div className="flex flex-wrap gap-2">
    {suggestions.map((text) => (
      <button
        key={text}
        onClick={() => setInput(text)}
        className={cn(
          "px-4 py-2 rounded-full text-sm transition-all",
          "hover:scale-105",
          theme === "dark"
            ? "bg-white/10 hover:bg-white/20"
            : "bg-black/5 hover:bg-black/10"
        )}
      >
        {text}
      </button>
    ))}
  </div>
);
```

---

### Recipe 5: Message Timestamp

```typescript
const formatTime = (timestamp: Date) => {
  const now = new Date();
  const diff = now.getTime() - timestamp.getTime();

  if (diff < 60000) return "Just now";
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return timestamp.toLocaleTimeString();
  return timestamp.toLocaleDateString();
};

return (
  <span className="text-xs opacity-40">{formatTime(message.timestamp)}</span>
);
```

---

## 🎨 Animation Presets

### Fade In

```typescript
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>
  {content}
</motion.div>
```

### Slide Up

```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  {content}
</motion.div>
```

### Scale

```typescript
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ duration: 0.15 }}
>
  {content}
</motion.button>
```

### Slide In (Sidebar)

```typescript
<motion.aside
  initial={{ x: -320, opacity: 0 }}
  animate={{ x: 0, opacity: 1 }}
  exit={{ x: -320, opacity: 0 }}
  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
>
  {content}
</motion.aside>
```

---

## 📚 Further Reading

- **Prompt-Kit Docs**: https://www.prompt-kit.com/
- **Radix UI**: https://www.radix-ui.com/
- **Framer Motion**: https://www.framer.com/motion/
- **Tailwind CSS**: https://tailwindcss.com/
- **cn() utility**: Uses `tailwind-merge` + `clsx`

---

## 💡 Tips & Best Practices

### Performance

- Use `transform` and `opacity` for animations (GPU accelerated)
- Memoize expensive components with `React.memo`
- Virtualize long message lists if needed

### Accessibility

- All Radix components are WCAG 2.1 compliant
- Use semantic HTML elements
- Include proper ARIA labels
- Test with keyboard navigation

### TypeScript

- All components are fully typed
- Use `React.FC` or explicit prop types
- Import types from component libraries

### Styling

- Use `cn()` utility for conditional classes
- Keep theme logic consistent
- Use Tailwind's opacity utilities for variants

---

**Need more examples?** Check the files:

- `ChatPromptKit.tsx` - Simple implementation
- `ChatWithSidebar.tsx` - Advanced implementation
- `PROMPT_KIT_CHAT_GUIDE.md` - Full documentation

---

_Built with [prompt-kit](https://www.prompt-kit.com/blocks) - UI blocks for AI applications_
