# config.py
import os
import sys
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("🚨 FATAL CONFIG ERROR: OPENROUTER_API_KEY environment variable is missing.")
    sys.exit(1)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("🚨 FATAL CONFIG ERROR: GEMINI_API_KEY environment variable is missing.")
    sys.exit(1)

# 100% OpenRouter Architecture
EMBEDDING_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
FAST_MODEL = "gemini-3.1-flash-lite"
ACTING_MODEL = "openai/gpt-oss-20b:free"    
REASONING_MODEL = "openai/gpt-oss-120b:free"