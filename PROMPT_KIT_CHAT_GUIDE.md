# Prompt-Kit Chat Pages Guide

I've created two new chat pages for your GlowOS application using [prompt-kit](https://www.prompt-kit.com/blocks) UI components. These pages provide modern, polished chat interfaces with different features.

## 📁 New Files Created

1. **`ChatPromptKit.tsx`** - Simple, clean chat interface
2. **`ChatWithSidebar.tsx`** - Full-featured chat with sidebar and thread management

## 🎨 Features

### ChatPromptKit.tsx (Simple Version)

- ✨ Clean, minimal chat interface
- 💬 Message history with avatars
- ⌨️ Smooth auto-resizing input
- 🎯 Suggestion pills for quick starts
- 🌙 Light/Dark theme support
- ✍️ Typing indicators
- 📱 Fully responsive design

### ChatWithSidebar.tsx (Full Version)

- 📂 Collapsible sidebar with chat history
- 🔄 Thread switching and management
- ✏️ Rename and delete threads
- 👤 User profile in sidebar
- 🎴 Interactive suggestion cards
- ⚙️ Settings access
- 📱 Mobile-responsive sidebar toggle
- All features from the simple version

## 🚀 How to Use

### Option 1: Add to Your Router

Update your route configuration in `App.tsx` or your routing file:

```typescript
import ChatPromptKit from "@/pages/ChatPromptKit";
import ChatWithSidebar from "@/pages/ChatWithSidebar";

// Add these routes:
<Route path="/chat-pk" element={<ChatPromptKit />} />
<Route path="/chat-sidebar" element={<ChatWithSidebar />} />
<Route path="/chat-sidebar/:threadId" element={<ChatWithSidebar />} />
```

### Option 2: Replace Existing Chat

If you want to replace your current chat page:

```typescript
// In App.tsx
import ChatPromptKit from "@/pages/ChatPromptKit";

// Replace your existing chat route:
<Route path="/chat" element={<ChatPromptKit />} />;
```

## 🎯 Customization

### Theming

Both components use your existing theme system from `useUIState()`:

```typescript
const { theme, toggleTheme } = useUIState();
```

Themes automatically adapt between light and dark modes.

### Persona Integration

The chat pages integrate with your `PersonaContext`:

```typescript
const { getCurrentPersona, currentPersona } = usePersona();
```

The current persona's name and description appear in the header.

### Styling

All components use Tailwind CSS and can be customized:

- **Colors**: Modify gradient colors in the avatar and headers
- **Spacing**: Adjust padding/margins in the container classes
- **Border radius**: Change `rounded-*` classes for different looks

### Suggestion Cards

Customize the empty state suggestions in either file:

```typescript
// In ChatPromptKit.tsx
const suggestions = [
  "Tell me a joke",
  "Help me brainstorm",
  "Explain quantum physics",
  "Write a poem",
];

// In ChatWithSidebar.tsx
const suggestionCards = [
  {
    icon: "💡",
    title: "Brainstorm ideas",
    description: "Generate creative solutions",
  },
  // Add more...
];
```

## 🔧 Technical Details

### Dependencies Used

All dependencies are already in your `package.json`:

- `framer-motion` - Smooth animations
- `lucide-react` - Modern icons
- `@radix-ui/*` - Accessible UI primitives
- `tailwind-merge` - Smart class merging

### Prompt-Kit Components Used

From `/src/components/ui/`:

- **PromptInput** - Auto-resizing input with smooth transitions
- **PromptInputTextarea** - Smart textarea that grows with content
- **SendButton** - Animated send button with disabled states
- **ChatContainer** - Scrollable container with auto-scroll
- **Avatar** - User and AI avatars with fallbacks

## 📱 Responsive Design

Both pages are fully responsive:

- **Desktop**: Full sidebar + chat area
- **Tablet**: Toggleable sidebar with overlay
- **Mobile**: Mobile-optimized with hamburger menu

## 🎨 Theme Examples

### Dark Mode

- Background: `#0a0a0a`
- Text: `white`
- Borders: `white/10`
- Hover: `white/10`

### Light Mode

- Background: `white`
- Text: `gray-900`
- Borders: `black/10`
- Hover: `black/5`

## 🔄 Migration from Existing Chat

If migrating from your current `Chat.tsx`:

1. **Keep your hooks**: Both new pages use your existing custom hooks:

   - `useChatLoader`
   - `useChatState`
   - `useUIState`
   - `usePersona`

2. **Update imports**: Make sure all imports point to the correct paths

3. **Test features**: Verify that all your existing features work:
   - Message sending
   - Thread loading
   - Persona switching
   - Theme toggling

## 🎯 Next Steps

1. **Try it out**: Navigate to `/chat-pk` or `/chat-sidebar`
2. **Customize**: Adjust colors, spacing, and suggestions
3. **Integrate**: Connect with your backend for thread management
4. **Extend**: Add more features like file uploads, voice input, etc.

## 📚 Resources

- [Prompt-Kit Blocks](https://www.prompt-kit.com/blocks) - More examples
- [Prompt-Kit Components](https://www.prompt-kit.com/) - Component documentation
- [Framer Motion](https://www.framer.com/motion/) - Animation docs
- [Radix UI](https://www.radix-ui.com/) - Accessible components

## 💡 Tips

1. **Performance**: The auto-scroll uses `useEffect` for smooth scrolling
2. **Accessibility**: All components use Radix UI for WCAG compliance
3. **Animations**: Framer Motion provides 60fps animations
4. **Type Safety**: Full TypeScript support with proper types

## 🐛 Troubleshooting

### Styles not working?

Make sure Tailwind is properly configured in `tailwind.config.js`

### Components not found?

Verify all UI components exist in `/src/components/ui/`

### Hooks throwing errors?

Check that all custom hooks are properly initialized

---

Enjoy your new chat interface! 🎉

For more inspiration, check out the [prompt-kit showcase](https://www.prompt-kit.com/blocks).
