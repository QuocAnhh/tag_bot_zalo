import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv("BOT_ID", "default_bot_id")

SMAX_SECRET = os.getenv("SMAX_SECRET", "your_default_smax_secret_here")
SMAX_TOKEN = os.getenv("SMAX_TOKEN", "your_default_smax_token_here")
SMAX_API_KEY = os.getenv("SMAX_API_KEY", "your_default_smax_api_key_here")
SMAX_RESPONSE_WEBHOOK_URL = os.getenv("SMAX_RESPONSE_WEBHOOK_URL")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

if not all([SMAX_API_KEY, SMAX_TOKEN, SMAX_RESPONSE_WEBHOOK_URL]):
    print("CRITICAL ERROR: One or more required environment variables are missing.")
    print("Please check your .env file and ensure the following are set:")
    print("- SMAX_API_KEY")
    print("- SMAX_TOKEN")
    print("- SMAX_RESPONSE_WEBHOOK_URL")
    # exit(1)

print("--- Environment Variables Loaded ---")
print(f"BOT_ID: {BOT_ID}")
print("SMAX_API_KEY: Loaded" if SMAX_API_KEY else "SMAX_API_KEY: ❌ NOT SET")
print("SMAX_TOKEN: Loaded" if SMAX_TOKEN else "SMAX_TOKEN: ❌ NOT SET")
print("SMAX_RESPONSE_WEBHOOK_URL: Loaded" if SMAX_RESPONSE_WEBHOOK_URL else "SMAX_RESPONSE_WEBHOOK_URL: ❌ NOT SET")
print("------------------------------------")
