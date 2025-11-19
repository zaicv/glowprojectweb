import os
import aiohttp
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import re

class Superpower:
    def __init__(self):
        self.name = "Web Search"
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
        
        # Define what this superpower can handle
        self.intent_map = {
            "search": "Search the web for information",
            "news": "Search for recent news articles",
            "research": "Deep research on a topic with multiple sources",
            "fact_check": "Verify facts and find reliable sources",
        }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        try:
            query = kwargs.get("query", "")
            if not query:
                return "❌ Please provide a search query"
            
            if not self.api_key:
                return "❌ Brave Search API key not configured. Please set BRAVE_SEARCH_API_KEY environment variable."
                
            if intent == "search":
                return await self.search_web(query)
            elif intent == "news":
                return await self.search_news(query)
            elif intent == "research":
                return await self.deep_research(query)
            elif intent == "fact_check":
                return await self.fact_check(query)
            else:
                return f"❌ Unknown intent: {intent}"
        except Exception as e:
            print(f"❌ WebSearch error: {e}")
            return f"❌ Error: {str(e)}"

    async def search_web(self, query: str) -> str:
        """Search the web using Brave Search API"""
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            params = {
                "q": query,
                "count": 8,
                "text_decorations": "false",
                "search_lang": "en",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"❌ Search API Error: HTTP {response.status}\n{error_text}"
                    
                    data = await response.json()
                    return self._format_chatgpt_style(data, query)
                    
        except asyncio.TimeoutError:
            return "⏰ Search timed out. Please try again."
        except Exception as e:
            print(f"❌ Search error: {e}")
            return f"❌ Search error: {str(e)}"

    def _format_chatgpt_style(self, data: Dict, query: str) -> str:
        """Format search results in ChatGPT style with inline citations and source cards"""
        web_results = data.get("web", {}).get("results", [])
        
        if not web_results:
            return "I couldn't find any results for that query."
        
        # Build a natural response with inline citations
        response_parts = []
        sources = []
        
        # Create source metadata
        for i, result in enumerate(web_results[:6], 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            description = result.get("description", "")
            
            # Try to extract image if available
            thumbnail = ""
            if "thumbnail" in result and result["thumbnail"]:
                if isinstance(result["thumbnail"], dict):
                    thumbnail = result["thumbnail"].get("src", "")
                elif isinstance(result["thumbnail"], str):
                    thumbnail = result["thumbnail"]
            
            sources.append({
                "index": i,
                "title": title,
                "url": url,
                "description": description,
                "thumbnail": thumbnail
            })
        
        # Build natural language response with proper formatting
        response_parts.append("## Search Results\n")
        
        # Create a synthesized answer from top results with inline citations
        for i, source in enumerate(sources[:5], 1):
            desc = source["description"]
            if desc and len(desc) > 50:  # Only include substantial descriptions
                # Clean and format the description
                clean_desc = desc.strip()
                
                # Add as a paragraph with citation
                response_parts.append(f"{clean_desc} [^{i}]\n")
        
        # Add visual break
        response_parts.append("\n---\n")
        
        # Add sources metadata for frontend parsing
        response_parts.append("\n<!-- SOURCES_START -->")
        for source in sources:
            thumb_attr = f' data-thumbnail="{source["thumbnail"]}"' if source["thumbnail"] else ''
            response_parts.append(
                f'<source data-index="{source["index"]}" '
                f'data-url="{source["url"]}" '
                f'data-title="{self._escape_html(source["title"])}" '
                f'data-description="{self._escape_html(source["description"])}"{thumb_attr}></source>'
            )
        response_parts.append("<!-- SOURCES_END -->")
        
        return "\n".join(response_parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return text.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', ' ')

    async def search_news(self, query: str) -> str:
        """Search for recent news"""
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            params = {
                "q": query,
                "count": 8,
                "freshness": "pd",  # Past day
                "text_decorations": "false",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        return f"❌ News search error: HTTP {response.status}"
                    
                    data = await response.json()
                    result = self._format_chatgpt_style(data, query)
                    # Replace header for news
                    return result.replace("## Search Results", "## Latest News")
                    
        except Exception as e:
            return f"❌ News search error: {str(e)}"

    async def deep_research(self, query: str) -> str:
        """Perform deep research with multiple perspectives"""
        result = await self.search_web(query)
        return result.replace("## Search Results", "## Research Summary")

    async def fact_check(self, query: str) -> str:
        """Fact check by searching reliable sources"""
        # Add site restrictions for reliable sources
        modified_query = f"{query} (site:.edu OR site:.gov OR site:reuters.com OR site:apnews.com OR site:bbc.com)"
        result = await self.search_web(modified_query)
        return result.replace("## Search Results", "## Fact Check Results")

    def get_help(self):
        """Return help information"""
        return """
🌐 **Web Search Superpower**

**Available Intents:**
• search: Search the web for current information
• news: Get recent news articles
• research: Deep dive into a topic
• fact_check: Verify facts from reliable sources

**Examples:**
• "search latest AI developments"
• "news about space exploration"
• "research quantum computing"
• "fact check vaccine effectiveness"

**Powered by:** Brave Search API
"""
