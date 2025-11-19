# superpowers/Notion/main.py
import os
from typing import Dict, Any
from dotenv import load_dotenv

class Superpower:
    def __init__(self):
        self.name = "Notion Deep Memory"
        
        # Load environment variables
        load_dotenv(dotenv_path="/Users/zai/The GlowOS/glow/The Core/GlowGPT/.env")
        
        # Notion API credentials
        self.notion_token = os.getenv("NOTION_API_TOKEN")
        if not self.notion_token:
            raise ValueError("❌ NOTION_API_TOKEN not found in environment variables")
        
        self.base_url = "https://api.notion.com/v1"
        
        # Define what this superpower can handle
        self.intent_map = {
            "search_notion": "Search and retrieve content from Notion workspace",
            "get_page": "Get specific Notion page content",
            "search_blocks": "Search blocks within a page",
            "summarize_page": "Summarize content from a specific Notion page"
        }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        try:
            print(f"📚 Notion: Processing intent '{intent}' with kwargs: {kwargs}")
            
            query = kwargs.get("query", "")
            
            if intent == "search_notion":
                return await self.search_notion(query)
            elif intent == "get_page":
                page_id = kwargs.get("page_id", "")
                return await self.get_page(page_id)
            elif intent == "search_blocks":
                page_id = kwargs.get("page_id", "")
                return await self.search_blocks(page_id, query)
            elif intent == "summarize_page":
                page_id = kwargs.get("page_id", "")
                raw_query = kwargs.get("search_query") or kwargs.get("query", "")
                details = kwargs.get("details", "")
                
                # Extract search query - prefer details field, just get the filename
                if details:
                    # Extract filename from details like "SoulDoc.pdf in the Knowledge/Documents database"
                    if "pdf" in details.lower():
                        # Find the PDF filename
                        import re
                        match = re.search(r'(\w+\.pdf)', details, re.IGNORECASE)
                        search_query = match.group(1) if match else details.split()[0]
                    else:
                        search_query = details.split()[0]  # Get first word as filename
                elif raw_query:
                    # Remove common summarize phrases
                    search_query = raw_query.replace("Summarize the page of ", "").replace("summarize ", "").strip()
                else:
                    search_query = ""
                
                return await self.summarize_page(page_id if page_id else "", search_query if not page_id else "")
            else:
                return f"❌ Unknown Notion intent: {intent}"
                
        except Exception as e:
            print(f"❌ Notion run() error: {type(e).__name__}: {str(e)}")
            return f"❌ Error in Notion superpower: {str(e)}"

    async def search_notion(self, query: str):
        """Search all databases and pages in Notion"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28"
            }
            
            # Search endpoint
            search_url = f"{self.base_url}/search"
            payload = {"query": query, "page_size": 10}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"📚 Notion search returned {len(data.get('results', []))} results")
                        # Debug: print first result structure
                        if data.get("results"):
                            print(f"🔍 First result structure: {data['results'][0].keys()}")
                        return self._format_search_results(data)
                    else:
                        error_text = await resp.text()
                        print(f"❌ Notion API error: {resp.status} - {error_text}")
                        return f"❌ Notion search failed: {resp.status}"
                        
        except Exception as e:
            import traceback
            print(f"❌ Error searching Notion: {str(e)}")
            traceback.print_exc()
            return f"❌ Error searching Notion: {str(e)}"

    async def get_page(self, page_id: str):
        """Get content from a specific Notion page"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28"
            }
            
            page_url = f"{self.base_url}/pages/{page_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(page_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._format_page_content(data)
                    else:
                        return f"❌ Notion page fetch failed: {resp.status}"
                        
        except Exception as e:
            return f"❌ Error getting Notion page: {str(e)}"

    async def search_blocks(self, page_id: str, query: str):
        """Search blocks within a specific page"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28"
            }
            
            blocks_url = f"{self.base_url}/blocks/{page_id}/children"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(blocks_url, headers=headers) as resp:
                    if resp.status == 200:
                        blocks = await resp.json()
                        return self._extract_matching_blocks(blocks, query)
                    else:
                        return f"❌ Failed to fetch blocks: {resp.status}"
                        
        except Exception as e:
            return f"❌ Error searching blocks: {str(e)}"

    def _format_search_results(self, data: dict) -> str:
        """Format search results for display"""
        results = data.get("results", [])
        if not results:
            return "📚 No matching Notion content found"
        
        formatted = ["# 📚 Notion Search Results\n"]
        for item in results[:5]:
            # Extract title safely - Notion objects have different structures
            title = self._extract_title(item)
            url = item.get("url", "No URL")
            object_type = item.get("object", "unknown")
            formatted.append(f"## {title}")
            formatted.append(f"📄 Type: {object_type}")
            formatted.append(f"🔗 [View in Notion]({url})\n")
        
        return "\n".join(formatted)
    
    def _extract_title(self, item: dict) -> str:
        """Safely extract title from various Notion object types"""
        try:
            # Method 1: Check if it's a page with properties
            properties = item.get("properties", {})
            if properties:
                # Try to get title from various possible property names
                for prop_name in ["title", "Name", "name"]:
                    if prop_name in properties:
                        prop = properties[prop_name]
                        # Handle title property structure
                        if isinstance(prop, dict):
                            title_array = prop.get("title", [])
                            if isinstance(title_array, list) and len(title_array) > 0:
                                return title_array[0].get("plain_text", "Untitled")
                
                # Try to get any rich text or text property
                for prop_name, prop_data in properties.items():
                    if isinstance(prop_data, dict):
                        rich_text = prop_data.get("rich_text", [])
                        if rich_text and isinstance(rich_text, list) and len(rich_text) > 0:
                            return rich_text[0].get("plain_text", "Untitled")
            
            # Method 2: Try to get from object type specific fields
            if item.get("object") == "database":
                db_title = item.get("title", [])
                if isinstance(db_title, list) and len(db_title) > 0:
                    return db_title[0].get("plain_text", "Untitled")
            
            # Method 3: Fallback
            return item.get("id", "Unknown")[:8] + "..."
            
        except Exception as e:
            print(f"⚠️ Error extracting title: {e}")
            return "Untitled"

    def _format_page_content(self, data: dict) -> str:
        """Format page content for display"""
        title = self._extract_title(data)
        return f"# 📄 {title}\n\n(Page content extraction can be implemented here)"

    def _extract_matching_blocks(self, blocks: dict, query: str) -> str:
        """Extract blocks that match the query"""
        matching = []
        for block in blocks.get("results", []):
            block_type = block.get("type", "")
            content = block.get(block_type, {})
            text = content.get("rich_text", [])
            # Add logic to search within blocks
        return f"Found {len(matching)} matching blocks"

    async def summarize_page(self, page_id: str = "", search_query: str = ""):
        """Get and summarize content from a Notion page by ID or search by title"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28"
            }
            
            async with aiohttp.ClientSession() as session:
                # If we have a search query, search for the page first
                if search_query:
                    print(f"🔍 Searching for page: {search_query}")
                    search_url = f"{self.base_url}/search"
                    search_payload = {"query": search_query, "page_size": 10}
                    
                    async with session.post(search_url, json=search_payload, headers=headers) as resp:
                        if resp.status != 200:
                            return f"❌ Failed to search for page: {resp.status}"
                        data = await resp.json()
                        results = data.get("results", [])
                        
                        # Find pages (not databases)
                        pages = [r for r in results if r.get("object") == "page"]
                        if not pages:
                            return f"❌ No pages found matching '{search_query}'"
                        
                        # Try to find exact match first
                        page = None
                        search_lower = search_query.lower()
                        for p in pages:
                            title = self._extract_title(p).lower()
                            if search_lower in title or title in search_lower:
                                page = p
                                break
                        
                        # If no exact match, use first page
                        if not page:
                            page = pages[0]
                        
                        page_id = page.get("id")
                        page_title = self._extract_title(page)
                        print(f"✅ Found page: {page_title} (ID: {page_id})")
                
                # Get all blocks from the page
                blocks_url = f"{self.base_url}/blocks/{page_id}/children"
                page_text = []
                async with session.get(blocks_url, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"❌ Failed to fetch page blocks: {resp.status} - {error_text}")
                        return f"❌ Failed to fetch page blocks: {resp.status}"
                    
                    blocks = await resp.json()
                    
                    # Extract text from all blocks
                    for block in blocks.get("results", []):
                        block_type = block.get("type")
                        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
                            content = block.get(block_type, {})
                            rich_text = content.get("rich_text", [])
                            if rich_text:
                                text = "".join([t.get("plain_text", "") for t in rich_text])
                                if text.strip():
                                    page_text.append(text)
                    
                    if not page_text:
                        return "📄 Page has no readable content"
                    
                    full_text = "\n".join(page_text)
                    
                    # Use Groq to summarize
                    from config import client as groq_client
                    summary_prompt = f"Summarize this Notion page content in 2-3 paragraphs:\n\n{full_text[:2000]}"
                    
                    response = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "user", "content": summary_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    summary_text = response.choices[0].message.content
                    if summary_text:
                        summary_text = summary_text.strip()
                    return f"# 📝 Page Summary\n\n{summary_text}"
                    
        except Exception as e:
            import traceback
            print(f"❌ Error summarizing page: {str(e)}")
            traceback.print_exc()
            return f"❌ Error summarizing page: {str(e)}"

    def get_help(self):
        return """
📚 **Notion Deep Memory**

Available Intents:
• search_notion: Search your entire Notion workspace
• get_page: Retrieve specific page content
• search_blocks: Search within a specific page
• summarize_page: Summarize content from a specific Notion page

Examples:
• "Search Notion for my meeting notes about Q4 planning"
• "Get the content from my Notion project page"
• "Summarize the Notion page with ID [page_id]"
"""