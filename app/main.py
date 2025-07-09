from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.models.webhook import SMaxWebhook, BotResponse
from app.services.mention_checker import MentionChecker
from app.services.intent_analyzer import SimpleIntentAnalyzer
from app.services.fake_data import FakeDataService
from app.utils.response_formatter import ResponseFormatter

load_dotenv()

app = FastAPI(title="Zalo Bot", version="1.0.0")

mention_checker = MentionChecker()
intent_analyzer = SimpleIntentAnalyzer()
fake_data_service = FakeDataService()
response_formatter = ResponseFormatter()

@app.get("/")
async def root():
    return {"message": "Zalo Bot Demo is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-07-09 07:13:01"}

@app.post("/webhook/smax")
async def handle_smax_webhook(request: Request):
    """Xử lý webhook từ Smax"""
    try:
        body = await request.json()
        print(f"Received webhook: {body}")
        
        webhook_data = SMaxWebhook(**body)
        
        if not mention_checker.is_bot_mentioned(webhook_data):
            return JSONResponse(
                status_code=200,
                content={"message": "Bot not mentioned, ignored"}
            )
        
        command_text = mention_checker.extract_command_text(webhook_data)
        print(f"Command extracted: {command_text}")
        
        intent_result = intent_analyzer.analyze(command_text)
        print(f"Intent analyzed: {intent_result}")
        
        response_text = await process_intent(intent_result)
        
        # Trả về response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": response_text,
                "intent": intent_result["intent"],
                "confidence": intent_result["confidence"]
            }
        )
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

async def process_intent(intent_result: dict) -> str:
    """Xử lý intent và trả về response text"""
    intent = intent_result["intent"]
    parameters = intent_result["parameters"]
    
    if intent == "call_report_today":
        data = fake_data_service.get_call_report("today")
        return response_formatter.format_call_report(data, "today")
    
    elif intent == "call_report_week":
        data = fake_data_service.get_call_report("week")
        return response_formatter.format_call_report(data, "week")
    
    elif intent == "call_report_month":
        data = fake_data_service.get_call_report("month")
        return response_formatter.format_call_report(data, "month")
    
    elif intent == "system_status":
        data = fake_data_service.get_system_status()
        return response_formatter.format_system_status(data)
    
    elif intent == "phone_list":
        data = fake_data_service.get_phone_config()
        return response_formatter.format_phone_config(data)
    
    elif intent == "phone_config":
        phone_number = parameters.get("phone_number")
        if phone_number:
            result = fake_data_service.configure_phone(phone_number)
            return response_formatter.format_config_result(result)
        else:
            return "❌ Vui lòng cung cấp số điện thoại cần cấu hình!\nVí dụ: `cấu hình số 0901234567`"
    
    else:
        return response_formatter.format_unknown_command()

@app.post("/test/webhook")
async def test_webhook():
    """Test endpoint với fake webhook data"""
    fake_webhook = {
        "event_type": "message_received",
        "data": {
            "message_id": "test_123",
            "user_id": "user_456", 
            "display_name": "Test User"
        },
        "raw": {
            "message": "@BotBiva báo cáo cuộc gọi hôm nay",
            "mentions": [
                {
                    "user_id": os.getenv("BOT_ID", "default_bot_id"),
                    "display_name": "BotBiva",
                    "start": 0,
                    "end": 8
                }
            ]
        }
    }
    
    request_mock = type('Request', (), {
        'json': lambda: fake_webhook
    })()
    
    return await handle_smax_webhook(request_mock)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )