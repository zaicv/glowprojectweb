# 🌐 Web Search Superpower Setup Guide

You now have a beautiful web search capability integrated into your AI assistant, powered by the Brave Search API!

## ✨ What's New

### Backend

- **New Superpower**: `WebSearch` with 4 intents:
  - `search`: General web search
  - `news`: Recent news articles
  - `research`: Deep research mode
  - `fact_check`: Verify facts from reliable sources

### Frontend

- **SearchResultCard**: Beautiful animated cards for each search result
- **Auto-parsing**: Automatically detects and renders search results in chat
- **Smooth animations**: Staggered entrance animations and hover effects
- **Theme-aware**: Adapts to light/dark theme seamlessly

## 🚀 Setup Instructions

### 1. Get Your Brave Search API Key (Free!)

1. Go to: https://brave.com/search/api/
2. Sign up for a free account
3. You'll get **2,000 free queries per month** 🎉
4. Copy your API key

### 2. Add API Key to Environment

Add this line to your `.env` file in `The Core/GlowGPT/`:

```bash
BRAVE_SEARCH_API_KEY=your_api_key_here
```

### 3. Restart GlowGPT

```bash
cd "The Core/GlowGPT"
# Stop your server if running
# Then start it again
python main.py  # or however you normally run it
```

The superpower will auto-load! You should see:

```
✅ Loaded superpower: Web Search
```

## 📖 Usage Examples

Once set up, your AI can now:

### Search the Web

```
User: "Search for the latest news about SpaceX Starship"
AI: [Returns beautiful search result cards with links and previews]
```

### Get Recent News

```
User: "News about AI breakthroughs"
AI: [Returns recent news articles with timestamps]
```

### Deep Research

```
User: "Research quantum computing applications"
AI: [Returns comprehensive search results]
```

### Fact Check

```
User: "Fact check: Does drinking water help with headaches?"
AI: [Searches reliable sources like .edu, .gov, news sites]
```

## 🎨 Features

### Beautiful UI Elements

- ✨ **Staggered animations** - Each result card animates in sequence
- 🎭 **Hover effects** - Cards lift and glow on hover
- 🖼️ **Favicons** - Shows website icons for easy recognition
- 🔗 **External link indicators** - Clear visual cues for external links
- ⏱️ **Timestamps** - For news results, shows "2 hours ago", etc.
- 🌈 **Gradient backgrounds** - Subtle animated gradients on hover
- 🎯 **Domain previews** - Shows the source domain at bottom of each card

### Smart Parsing

- Automatically detects search results in markdown
- Separates search results from regular content
- Preserves markdown formatting for non-search content

## 🔧 Technical Details

### Files Created/Modified

**Backend:**

- `The Core/GlowGPT/superpowers/WebSearch/main.py` - Main superpower
- `The Core/GlowGPT/superpowers/WebSearch/__init__.py` - Package init

**Frontend:**

- `src/components/Chat/SearchResultCard.tsx` - Result card component
- `src/utils/parseSearchResults.ts` - Parser utility
- `src/components/Chat/ChatMessages.tsx` - Modified to render results

### Architecture

```
User Query → GlowGPT Backend → WebSearch Superpower → Brave API
                                         ↓
                                 Formatted Response
                                         ↓
Frontend Parser → Extract Search Results → Render Cards
```

### API Response Format

The backend formats results with embedded metadata:

```markdown
# 🔍 Search Results: your query

<!-- SEARCH_RESULTS_START -->
<div class="search-result-data" data-title="..." data-url="..." ...></div>
...
<!-- SEARCH_RESULTS_END -->
```

The frontend parser extracts this metadata and renders beautiful cards.

## 🎯 Next Steps

### Optional Enhancements

1. **Add caching** to reduce API calls:

   ```python
   # In WebSearch/main.py, add Redis or simple dict caching
   ```

2. **Add image search**:

   ```python
   async def search_images(self, query: str):
       # Use Brave Image Search API
   ```

3. **Add search filters**:

   - Time range (past hour, day, week, month, year)
   - Safe search
   - Country/language

4. **Add related searches**:
   - Already supported in backend, can enhance UI

## 🐛 Troubleshooting

### "API key not configured" error

- Make sure `BRAVE_SEARCH_API_KEY` is in your `.env` file
- Restart the GlowGPT server

### Search results not showing

- Check browser console for errors
- Verify the superpower is loaded (check server logs)
- Make sure you're testing with an AI intent that triggers search

### Cards not animating

- Ensure `framer-motion` is installed: `npm install framer-motion`
- Check for CSS conflicts

## 📊 Rate Limits

**Free Tier:** 2,000 queries/month

- ~66 searches per day
- ~2.2 searches per hour on average
- More than enough for personal use!

**If you need more:**

- Upgrade to Brave Search Pro
- Or implement caching to reuse results

## 💡 Pro Tips

1. **Use specific queries** for better results
2. **Fact-check mode** is great for verifying claims
3. **News mode** filters for recent content
4. **Research mode** provides comprehensive results
5. The AI will automatically decide which intent to use based on your request

## 🎉 Enjoy!

You now have ChatGPT-like web browsing with beautiful animations and previews!

---

**Questions?** Check the code comments in:

- `The Core/GlowGPT/superpowers/WebSearch/main.py`
- `src/components/Chat/SearchResultCard.tsx`
