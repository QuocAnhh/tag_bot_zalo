from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import sys
import os
import json
import logging
from typing import Dict, Any, Callable, Awaitable
import httpx
from contextlib import asynccontextmanager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.intent_analyzer import SimpleIntentAnalyzer
from services.smax_service import SmaxService
from services.webhook_service import WebhookService
from utils.response_formatter import ResponseFormatter
from config import SMAX_API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# reusable http client that will be initialized on startup
http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan events.
    Initializes the HTTP client on startup and closes it on shutdown.
    """
    global http_client
    logging.info("🚀 Starting up application...")
    http_client = httpx.AsyncClient(timeout=10.0)
    
    # Pass the client to services that need it
    webhook_service.set_http_client(http_client)
    
    yield
    
    logging.info("👋 Shutting down application...")
    if http_client:
        await http_client.aclose()

app = FastAPI(title="Zalo Bot", version="1.0.0", lifespan=lifespan)

# Add middleware to log ALL incoming requests for debugging
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    start_time = datetime.now()
    logging.info(f"🌍 INCOMING: {request.method} {request.url}")
    logging.info(f"🌍 Headers: {dict(request.headers)}")
    
    # For POST requests, also log the body
    if request.method == "POST":
        body = await request.body()
        if body:
            logging.info(f"🌍 Body: {body.decode('utf-8', errors='replace')}")
        
        # Recreate request for next handler
        async def receive():
            return {"type": "http.request", "body": body}
        
        request = Request(request.scope, receive)
    
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    logging.info(f"🌍 Response: {response.status_code} ({duration:.3f}s)")
    return response

intent_analyzer = SimpleIntentAnalyzer()
smax_service = SmaxService()
webhook_service = WebhookService()
response_formatter = ResponseFormatter()

INTENT_HANDLERS: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {
    "call_report_today": lambda params: smax_service.get_call_report("today"),
    "call_report_week": lambda params: smax_service.get_call_report("week"),
    "call_report_month": lambda params: smax_service.get_call_report("month"),
    "system_status": lambda params: smax_service.get_system_status(),
    "phone_list": lambda params: smax_service.get_phone_config(),
    "phone_config": lambda params: smax_service.configure_phone(params.get("phone_number")),
}

FORMATTER_MAPPING: Dict[str, Callable[..., str]] = {
    "call_report_today": lambda data: response_formatter.format_call_report(data, "today"),
    "call_report_week": lambda data: response_formatter.format_call_report(data, "week"),
    "call_report_month": lambda data: response_formatter.format_call_report(data, "month"),
    "system_status": response_formatter.format_system_status,
    "phone_list": response_formatter.format_phone_config,
    "phone_config": response_formatter.format_config_result,
}

async def handle_intent(intent_result: dict) -> str:
    """
    Handles business logic based on the analyzed intent.
    Uses mappings to call the correct service method and format the response.
    """ 
    intent = intent_result.get("intent")
    params = intent_result.get("parameters", {})
    logging.info(f"Handling intent: {intent} with params: {params}")

    if intent == "phone_config" and not params.get("phone_number"):
        return "❌ Vui lòng cung cấp số điện thoại cần cấu hình!\nVí dụ: `cấu hình số 0901234567`"

    handler = INTENT_HANDLERS.get(intent)
    if not handler:
        logging.warning(f"No handler found for intent: {intent}")
        return response_formatter.format_unknown_command()

    data = await handler(params)
    
    formatter = FORMATTER_MAPPING.get(intent)
    if not formatter:
        logging.error(f"No formatter found for intent: {intent}")
        return response_formatter.format_unknown_command()

    return formatter(data)

async def parse_request_body(request: Request) -> Dict[str, Any]:
    """Parses and logs the request body, handling potential errors."""
    try:
        body_bytes = await request.body()
        if not body_bytes:
            logging.warning("Empty body received. This could be a health check.")
            return {}
        body_str = body_bytes.decode('utf-8')
        logging.info(f"Request body: {body_str}")
        return json.loads(body_str)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e} - Raw body: {body_bytes.decode(errors='replace')}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")
    except UnicodeDecodeError as e:
        logging.error(f"Unicode decode error: {e}") 
        raise HTTPException(status_code=400, detail="Invalid request encoding.")

def get_message_text(body: Dict[str, Any], headers: Dict[str, str] = None) -> str:
    """Extracts the message text from various possible fields in the payload or headers."""
    if headers:
        message_from_header = headers.get("last_content_by_user")
        if message_from_header and "{{" not in message_from_header:
            logging.info(f"Extracted message from header 'last_content_by_user': '{message_from_header}'")
            return message_from_header.strip()
    
    message_text = (
        body.get("message_text")  
        or body.get("last_content_by_user")  #smax sent
        or body.get("message")
        or body.get("text")
        or (body.get("raw", {}).get("message") if isinstance(body.get("raw"), dict) else None)
    )
    
    result = message_text.strip() if message_text else ""
    return result

def is_smax_test_payload(body: Dict[str, Any]) -> bool:
    """Checks if the payload is a test request from SMAX."""
    smax_template_patterns = ["{{$.user id}}", "{{$.group id}}", "{{$."]
    user_id = str(body.get("user_id", ""))
    group_id = str(body.get("group_id", ""))
    return any(p in user_id for p in smax_template_patterns) or \
           any(p in group_id for p in smax_template_patterns)

# api endpoints
@app.get("/")
async def root():
    return {"message": "Zalo Bot is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/webhook/zalo-biva", status_code=200)
async def verify_smax_webhook():
    """
    Handles the GET request from SMAX for webhook verification.
    This is a standard procedure for many webhook providers before they
    start forwarding actual data via POST requests.
    """
    logging.info("Received GET request for Zalo-Biva webhook verification. Responding with success to confirm endpoint validity.")
    return {"status": "verification_successful"}

@app.post("/webhook/zalo-biva")
async def handle_smax_webhook(request: Request, x_api_key: str = Header(None)):
    """Main endpoint to receive and process messages from Zalo via SMAX."""
    logging.info("========== ZALO-BIVA WEBHOOK REQUEST RECEIVED ==========")
    logging.info(f"Request headers: {dict(request.headers)}")
    logging.info(f"Request method: {request.method}")
    logging.info(f"Request URL: {request.url}")
    
    # IMPORTANT: API Key validation is currently disabled for debugging.
    # In a production environment, this check MUST be enabled to prevent
    # unauthorized access.
    if x_api_key != SMAX_API_KEY:
        logging.warning(f"CRITICAL: SMAX API Key validation is DISABLED. Request would have been blocked.")
        # pass # Uncomment and raise HTTPException in production.
        # raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    try:
        body = await parse_request_body(request)
        if not body:
            return JSONResponse(status_code=200, content={"message": "Webhook received, empty body."})

        message_text = get_message_text(body, dict(request.headers))
        
        if not message_text and is_smax_test_payload(body):
            logging.info("Test payload from SMAX received. Responding with success.")
            return JSONResponse(status_code=200, content={"success": True, "message": "Bot test successful."})

        if not message_text:
            logging.error("No valid message text found in payload.")
            logging.error(f"Full payload received: {json.dumps(body, ensure_ascii=False, indent=2)}")
            return JSONResponse(status_code=400, content={"error": "Missing message text."})

        original_message = message_text # Store original message for logging
        logging.info(f"Original message received: '{original_message}'")

        # Clean the message text by removing the initial mention/tag if it exists
        cleaned_message = message_text.strip()
        if cleaned_message.startswith("@"):
            # Find the end of the mention (first space after '@') and trim it
            parts = cleaned_message.split(maxsplit=1)
            if len(parts) > 1:
                message_text = parts[1]
            else:
                # This case handles if the message is ONLY a mention, e.g., "@Bot"
                logging.warning(f"Message contains only a mention, resulting in empty command: '{original_message}'")
                message_text = ""
        else:
            message_text = cleaned_message

        logging.info(f"Cleaned command for analysis: '{message_text}'")

        if not message_text:
            logging.error("Command is empty after cleaning.")
            return JSONResponse(status_code=400, content={"error": "Empty command after cleaning."})

        intent_result = intent_analyzer.analyze(message_text)
        logging.info(f"Intent analysis result: {intent_result}")

        response_text = await handle_intent(intent_result)

        logging.info("Sending response back to SMAX...")
        smax_send_result = await webhook_service.send_response_to_smax(response_text, body, dict(request.headers))
        logging.info(f"SMAX send result: {'Success' if smax_send_result else 'Failure'}")
        
        response_payload = {
            "success": True,
            "message": response_text,
            "smax_forward_status": "sent" if smax_send_result else "failed",
            "metadata": {
                "intent": intent_result.get("intent"),
                "confidence": intent_result.get("confidence"),
                # "bot_id": BOT_ID
                "processed_at": datetime.now().isoformat()
            }
        }
        return JSONResponse(status_code=200, content=response_payload)

    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing the webhook: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "An internal server error occurred."}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)