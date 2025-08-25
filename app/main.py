from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import json
from typing import Dict, Any, Callable, Awaitable
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.intent_analyzer import SimpleIntentAnalyzer
from services.smax_service import SmaxService
from utils.response_formatter import ResponseFormatter
from config import SMAX_API_KEY

app = FastAPI(title="Zalo Bot", version="1.0.0")

intent_analyzer = SimpleIntentAnalyzer()
smax_service = SmaxService()

INTENT_HANDLERS: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {
    "call_report_today": lambda params: smax_service.get_call_report("today"),
    "call_report_week": lambda params: smax_service.get_call_report("week"),
    "call_report_month": lambda params: smax_service.get_call_report("month"),
    "system_status": lambda params: smax_service.get_system_status(),
    "phone_list": lambda params: smax_service.get_phone_config(),
    "phone_config": lambda params: smax_service.configure_phone(params.get("phone_number")),
}

FORMATTER_MAPPING: Dict[str, Callable[..., str]] = {
    "call_report_today": lambda data: ResponseFormatter.format_call_report(data, "today"),
    "call_report_week": lambda data: ResponseFormatter.format_call_report(data, "week"),
    "call_report_month": lambda data: ResponseFormatter.format_call_report(data, "month"),
    "system_status": ResponseFormatter.format_system_status,
    "phone_list": ResponseFormatter.format_phone_config,
    "phone_config": ResponseFormatter.format_config_result,
}

def get_message_text(body: Dict[str, Any], headers: Dict[str, str] = None) -> str:
    if headers:
        header_val = headers.get("last_content_by_user")
        if header_val and "{{" not in header_val:
            return header_val.strip()
    message_text = (
        body.get("message_text")
        or body.get("message-text")
        or body.get("last_content_by_user")
        or body.get("message")
        or body.get("text")
        or (body.get("raw", {}).get("message") if isinstance(body.get("raw"), dict) else None)
    )
    return message_text.strip() if message_text else ""

def clean_command(text: str) -> str:
    text = text.strip()
    if text.startswith("@"):  # bỏ mention đầu câu
        parts = text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""
    return text

async def handle_intent(intent_result: dict) -> str:
    intent = intent_result.get("intent")
    params = intent_result.get("parameters", {})
    if intent == "phone_config" and not params.get("phone_number"):
        return "❌ Vui lòng cung cấp số điện thoại cần cấu hình!\nVí dụ: `cấu hình số 0901234567`"
    handler = INTENT_HANDLERS.get(intent)
    if not handler:
        return ResponseFormatter.format_unknown_command()
    data = await handler(params)
    formatter = FORMATTER_MAPPING.get(intent)
    if not formatter:
        return ResponseFormatter.format_unknown_command()
    return formatter(data)

async def parse_request_body(request: Request) -> Dict[str, Any]:
    try:
        body_bytes = await request.body()
        if not body_bytes:
            return {}
        return json.loads(body_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid request encoding.")

@app.get("/")
async def root():
    return {"message": "Zalo Bot is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/webhook/zalo-biva", status_code=200)
async def verify_smax_webhook():
    return {"status": "verification_successful"}

@app.post("/webhook/zalo-biva")
async def handle_smax_webhook(request: Request, x_api_key: str = Header(None)):
    if x_api_key != SMAX_API_KEY:
        pass
    try:
        body = await parse_request_body(request)
        message_text = get_message_text(body, dict(request.headers))
        if not message_text:
            return JSONResponse(status_code=200, content={"message": ResponseFormatter.format_unknown_command()})
        cleaned = clean_command(message_text)
        if not cleaned:
            return JSONResponse(status_code=200, content={"message": ResponseFormatter.format_unknown_command()})
        intent_result = intent_analyzer.analyze(cleaned)
        response_text = await handle_intent(intent_result)
        return JSONResponse(status_code=200, content={"message": response_text})
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        return JSONResponse(status_code=500, content={"success": False, "error": "An internal server error occurred."})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8888, reload=True)
