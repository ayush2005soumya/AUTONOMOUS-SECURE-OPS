# config.py
import os
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# 100% OpenRouter Architecture
EMBEDDING_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
FAST_MODEL = "meta-llama/llama-3.2-3b-instruct:free"
ACTING_MODEL = "openai/gpt-oss-20b:free"    
REASONING_MODEL = "openai/gpt-oss-120b:free"