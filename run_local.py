"""
Run the AI Pronunciation Trainer locally with .env support
"""

import os
import sys


# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded environment from .env file")
except ImportError:
    print("[WARN] python-dotenv not installed")
    print("       Install with: pip install python-dotenv")
    print("       Continuing with system environment variables...\n")

# Check for API key
api_key = os.getenv('WHISPER_API_KEY') or os.getenv('OPENAI_API_KEY')
if not api_key:
    print("[ERROR] WHISPER_API_KEY not found in .env file!")
    print("\nMake sure your .env file contains:")
    print("WHISPER_API_KEY=sk-proj-xxxxxxxxxxxxxxxx")
    sys.exit(1)

print(f"[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")
print("")

# Import and run the web app
import webApp

# The webApp.py will run automatically when imported

