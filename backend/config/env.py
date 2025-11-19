"""
🔧 Environment & Client Setup - Utility Room & Control Panels
Loads environment variables and initializes API clients
"""
import os
from dotenv import load_dotenv
from groq import Groq
from anthropic import Anthropic
from supabase import create_client, Client
import openai
import whisper
import requests

# Load .env file
load_dotenv()

# =========================
# 🔑 API Keys
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# =========================
# 🤖 API Clients
# =========================
client = Groq(api_key=GROQ_API_KEY)
claude = Anthropic(api_key=CLAUDE_API_KEY)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Whisper model for transcription
whisper_model = whisper.load_model("base")  # or "small" / "medium" / "large"

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# ✅ Connection Tests
# =========================
def test_supabase_connection():
    """Test Supabase connection at startup"""
    try:
        test_resp = supabase.table("persona").select("*").limit(1).execute()
        print("✅ Supabase connected and accessible.")
        print(f"🔧 Supabase URL loaded: {SUPABASE_URL}")
    except Exception as e:
        print("❌ Supabase connection failed:", e)

def test_ollama_embedding():
    """Test Ollama embedding service"""
    try:
        print("🚀 Testing Ollama embedding...")
        response = requests.post(
            "http://127.0.0.1:11434/api/embed",
            json={
                "model": "nomic-embed-text",
                "input": ["search_document: A dog is running through the park."]
            }
        )
        data = response.json()
        if "embeddings" in data and data["embeddings"]:
            print("✅ Ollama embedding returned!")
            print(f"Embedding length: {len(data['embeddings'][0])}")
        else:
            print(f"❌ No embeddings found in response: {data}")
    except Exception as e:
        print(f"💥 Ollama exception: {e}")

# Run connection tests on import
test_supabase_connection()
test_ollama_embedding()

# Export all clients and constants
__all__ = [
    "client",           # Groq client
    "claude",           # Claude client
    "supabase",         # Supabase client
    "whisper_model",    # Whisper model
    "GROQ_API_KEY",
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "openai_client",
]