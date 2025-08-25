import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv("BOT_ID", "default_bot_id")

SMAX_SECRET = os.getenv("SMAX_SECRET", "your_default_smax_secret_here")
SMAX_TOKEN = os.getenv("SMAX_TOKEN", "your_default_smax_token_here")
SMAX_API_KEY = os.getenv("SMAX_API_KEY", "your_default_smax_api_key_here")
SMAX_RESPONSE_WEBHOOK_URL = os.getenv("SMAX_RESPONSE_WEBHOOK_URL", "")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
