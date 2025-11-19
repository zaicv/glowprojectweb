import os
import requests
from typing import Dict, Any
import re

# Try to import aiohttp, but we'll use requests as fallback
try:
    import aiohttp
    ASYNC_HTTP_AVAILABLE = True
except ImportError:
    ASYNC_HTTP_AVAILABLE = False

class Superpower:
    def __init__(self):
        self.name = "Wolfram Alpha"
        # Get APP ID from environment variable for security
        self.app_id = os.getenv("WOLFRAM_APP_ID", "QHVWLG8J63")
        
        # Define what this superpower can handle
        self.intent_map = {
            "compute": "Perform math/science/factual computation",
            "calculate": "Solve mathematical equations and calculations",
            "solve": "Solve complex problems in math, science, or engineering",
            "convert": "Convert between units, currencies, or formats",
            "lookup": "Look up factual information, data, or statistics",
            "analyze": "Analyze data, equations, or scientific concepts",
            "compare": "Compare different entities, values, or concepts",
            "explain": "Get detailed explanations of concepts or processes",
        }

    async def run(self, intent: str, **kwargs):
        """Route intents to their handler"""
        try:
            print(f"🔍 Wolfram Alpha: Processing intent '{intent}' with kwargs: {kwargs}")
            
            query = kwargs.get("query", "")
            if not query:
                return "❌ Please provide a query to process"
                
            if intent in self.intent_map:
                print(f"🔍 Wolfram Alpha: Calling query_wolfram with query: '{query}'")
                result = await self.query_wolfram(query, intent)
                print(f" Wolfram Alpha: Got result: {result}")
                return result
            else:
                return f"❌ Unknown Wolfram Alpha intent: {intent}"
        except Exception as e:
            print(f"❌ Wolfram Alpha run() error: {type(e).__name__}: {str(e)}")
            return f"❌ Error in Wolfram Alpha superpower: {str(e)}"

    async def query_wolfram(self, query: str, intent: str = "compute"):
        """Call Wolfram Alpha LLM API"""
        try:
            print(f"🔍 Wolfram Alpha: Starting API call for query: '{query}'")
            
            # For now, let's use the synchronous fallback to avoid aiohttp issues
            print(f"🔍 Wolfram Alpha: Using sync fallback to avoid aiohttp issues")
            return await self._query_wolfram_sync(query, intent)
            
        except Exception as e:
            print(f"❌ Wolfram Alpha query_wolfram() error: {type(e).__name__}: {str(e)}")
            return f"❌ Unexpected error: {str(e)}"

    def clean_and_format_response(self, text_response: str, intent: str, query: str) -> str:
        """Clean and format the response to be human-friendly and concise"""
        try:
            # Clean up the response
            cleaned_text = text_response.strip()
            
            # Extract key information based on intent type
            if intent in ["lookup", "weather"]:
                return self._format_weather_lookup(cleaned_text, query)
            elif intent in ["compute", "calculate", "solve"]:
                return self._format_math_computation(cleaned_text, query)
            elif intent in ["convert"]:
                return self._format_conversion(cleaned_text, query)
            else:
                return self._format_general_response(cleaned_text, query)
                
        except Exception as e:
            print(f"🔍 Wolfram Alpha: Formatting error: {e}")
            # Fallback to simple formatting
            return f"**{query}**\n\n{text_response[:500]}..."

    def _format_weather_lookup(self, text: str, query: str) -> str:
        """Format weather lookup responses cleanly"""
        lines = text.split('\n')
        formatted_parts = []
        
        # Extract current weather
        current_temp = None
        conditions = None
        humidity = None
        wind = None
        
        # Extract forecast
        tonight_forecast = None
        tomorrow_forecast = None
        
        # Extract images
        images = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract current weather
            if "temperature |" in line and "°F" in line:
                current_temp = line.split("|")[1].strip()
            elif "conditions |" in line:
                conditions = line.split("|")[1].strip()
            elif "relative humidity |" in line:
                humidity = line.split("|")[1].strip()
            elif "wind speed |" in line:
                wind = line.split("|")[1].strip()
                
            # Extract forecast
            elif "Tonight:" in line:
                tonight_forecast = line.replace("Tonight:", "").strip()
            elif "Tomorrow:" in line:
                tomorrow_forecast = line.replace("Tomorrow:", "").strip()
                
            # Extract images - look for lines that contain image URLs
            elif "https://public" in line and ".png" in line:
                # Clean up the URL - remove any prefix text
                url_match = re.search(r'https://public[^\s]+\.png', line)
                if url_match:
                    clean_url = url_match.group(0)
                    images.append(clean_url)
        
        # Build clean response
        formatted_parts.append(f"# 🌤️ Weather in {query.split('weather in ')[-1].title()}")
        
        if current_temp or conditions:
            formatted_parts.append("## Current Conditions")
            if current_temp:
                formatted_parts.append(f"**Temperature:** {current_temp}")
            if conditions:
                formatted_parts.append(f"**Conditions:** {conditions}")
            if humidity:
                formatted_parts.append(f"**Humidity:** {humidity}")
            if wind:
                formatted_parts.append(f"**Wind:** {wind}")
        
        if tonight_forecast:
            formatted_parts.append("\n## Tonight")
            formatted_parts.append(tonight_forecast)
            
        if tomorrow_forecast:
            formatted_parts.append("\n## Tomorrow")
            formatted_parts.append(tomorrow_forecast)
        
        # Add images if available - with proper markdown syntax
        if images:
            formatted_parts.append("\n## 📊 Weather Charts")
            for i, img_url in enumerate(images[:3]):  # Limit to 3 images
                formatted_parts.append(f"![Weather Chart {i+1}]({img_url})")
        
        return '\n'.join(formatted_parts)

    def _format_math_computation(self, text: str, query: str) -> str:
        """Format mathematical computation responses cleanly"""
        lines = text.split('\n')
        formatted_parts = []
        
        # Extract the main result
        main_result = None
        plot_image = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for the main mathematical result
            if "=" in line and any(op in line for op in ["+", "-", "*", "/", "d/dx", "∫"]):
                main_result = line
            elif "https://public" in line and ".png" in line:
                plot_image = line.strip()
        
        # Build clean response
        formatted_parts.append(f"# 🧮 {query.title()}")
        
        if main_result:
            formatted_parts.append("\n## Result")
            formatted_parts.append(f"```\n{main_result}\n```")
        
        if plot_image:
            formatted_parts.append("\n## 📊 Visual Representation")
            formatted_parts.append(f"![Mathematical Plot]({plot_image})")
        
        return '\n'.join(formatted_parts)

    def _format_conversion(self, text: str, query: str) -> str:
        """Format conversion responses cleanly"""
        lines = text.split('\n')
        formatted_parts = []
        
        # Extract the conversion result
        conversion_result = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for conversion result
            if "=" in line and any(unit in line.lower() for unit in ["°f", "°c", "km", "mi", "kg", "lb", "usd", "eur"]):
                conversion_result = line
                break
        
        # Build clean response
        formatted_parts.append(f"# 🧮 {query.title()}")
        
        if conversion_result:
            formatted_parts.append("\n## Conversion")
            formatted_parts.append(f"**{conversion_result}**")
        
        return '\n'.join(formatted_parts)

    def _format_general_response(self, text: str, query: str) -> str:
        """Format general responses cleanly"""
        lines = text.split('\n')
        formatted_parts = []
        
        # Extract key information (first few meaningful lines)
        key_info = []
        images = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip technical headers
            if any(skip in line.lower() for skip in ["query:", "assumption:", "input interpretation:", "wolfram|alpha website result"]):
                continue
                
            # Collect meaningful information
            if line and not line.startswith("http"):
                key_info.append(line)
                
            # Collect images
            elif "https://public" in line and ".png" in line:
                images.append(line.strip())
        
        # Build clean response
        formatted_parts.append(f"# 🧮 {query.title()}")
        
        if key_info:
            formatted_parts.append("\n## Information")
            # Take first 3-5 meaningful lines
            for info in key_info[:5]:
                if info and len(info) > 10:  # Only meaningful lines
                    formatted_parts.append(f"• {info}")
        
        # Add images if available
        if images:
            formatted_parts.append("\n## 📊 Visual Data")
            for i, img_url in enumerate(images[:2]):  # Limit to 2 images
                formatted_parts.append(f"![Data Visualization {i+1}]({img_url})")
        
        return '\n'.join(formatted_parts)

    async def _query_wolfram_sync(self, query: str, intent: str):
        """Synchronous version using requests"""
        try:
            print(f"🔍 Wolfram Alpha: Using sync requests for query: '{query}'")
            
            url = "https://www.wolframalpha.com/api/v1/llm-api"
            params = {
                "appid": self.app_id,
                "input": query
            }

            print(f"🔍 Wolfram Alpha: Making sync request to {url}")
            response = requests.get(url, params=params, timeout=30)
            print(f"🔍 Wolfram Alpha: Sync response status: {response.status_code}")
            
            if response.status_code != 200:
                return f"❌ Wolfram API Error: HTTP {response.status_code}"
            
            print(f"🔍 Wolfram Alpha: About to parse response...")
            
            # First try to parse as JSON
            try:
                data = response.json()
                print(f"🔍 Wolfram Alpha: Successfully parsed JSON response")
                
                # Handle JSON response
                if isinstance(data, dict):
                    if "result" in data:
                        result = self.clean_and_format_response(data['result'], intent, query)
                        return result
                    elif "answer" in data:
                        result = self.clean_and_format_response(data['answer'], intent, query)
                        return result
                    elif "text" in data:
                        result = self.clean_and_format_response(data['text'], intent, query)
                        return result
                    else:
                        result = self.clean_and_format_response(str(data), intent, query)
                        return result
                        
            except Exception as json_error:
                print(f"🔍 Wolfram Alpha: JSON parse failed, trying text response: {json_error}")
                
                # If JSON fails, treat as text response
                text_response = response.text
                print(f" Wolfram Alpha: Raw response text: {text_response[:200]}...")
                
                # Format the text response beautifully
                if text_response:
                    result = self.clean_and_format_response(text_response, intent, query)
                    return result
                else:
                    return f"❌ Wolfram API returned empty response"
                
        except requests.Timeout:
            return "⏰ Request timed out. Try a simpler query."
        except requests.RequestException as e:
            return f"❌ Network error: {str(e)}"
        except Exception as e:
            print(f"❌ Wolfram Alpha sync error: {type(e).__name__}: {str(e)}")
            return f"❌ Unexpected error: {str(e)}"

    def get_help(self):
        """Return help information for this superpower"""
        return f"""
🧮 **Wolfram Alpha Superpower**

**Available Intents:**
{chr(10).join(f"• {intent}: {desc}" for intent, desc in self.intent_map.items())}

**Examples:**
• "compute the derivative of x^2 + 3x + 1"
• "solve 2x + 5 = 13"
• "convert 100 USD to EUR"
• "lookup population of Tokyo"
• "analyze y = mx + b"
• "compare GDP of USA vs China"
• "explain photosynthesis"

**Note:** This superpower uses the Wolfram Alpha LLM API for computational knowledge and problem-solving.
"""