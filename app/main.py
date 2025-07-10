from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.webhook import SMaxWebhook, BotResponse
from services.mention_checker import MentionChecker
from services.intent_analyzer import SimpleIntentAnalyzer
from services.smax_service import SmaxService
from services.webhook_service import WebhookService
from utils.response_formatter import ResponseFormatter

import logging
import requests
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

load_dotenv()

app = FastAPI(title="Zalo Bot", version="1.0.0")

mention_checker = MentionChecker()
intent_analyzer = SimpleIntentAnalyzer()
smax_service = SmaxService()
webhook_service = WebhookService()
response_formatter = ResponseFormatter()

SMAX_API_KEY = os.getenv("SMAX_API_KEY", "your_smax_api_key")
SMAX_RESPONSE_WEBHOOK_URL = os.getenv("SMAX_RESPONSE_WEBHOOK_URL", "https://api.smax.ai/public/bizs/hotline-biva/triggers/686f2dcbe2c4b0887fffb708")
SMAX_TOKEN = os.getenv("SMAX_TOKEN", "your_smax_token")

def parse_intent(message: str) -> dict:
    """Parse intent từ message, trả về dict response phù hợp cho block Zalo"""
    msg = message.lower()
    if "báo cáo hôm nay" in msg:
        return {"messages": [{"type": "text", "text": "Tổng số cuộc gọi hôm nay là 12 cuộc."}]}
    # Có thể mở rộng thêm các intent khác ở đây
    return {"messages": [{"type": "text", "text": "Xin lỗi, tôi chưa hiểu yêu cầu của bạn."}]}

@app.get("/")
async def root():
    return {"message": "Zalo Bot Demo is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-07-09 07:13:01"}

@app.get("/webhook/config")
async def get_webhook_config():
    """Kiểm tra cấu hình webhook"""
    try:
        config = webhook_service.validate_webhook_setup()
        return JSONResponse(
            status_code=200,
            content=config
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/webhook/zalo")
async def handle_zalo_webhook(request: Request):
    """Xử lý webhook trực tiếp từ Zalo"""
    try:
        body = await request.json()
        print(f"📥 Received Zalo webhook: {body}")
        
        # Convert Zalo webhook format thành SMaxWebhook format
        zalo_webhook = {
            "event_type": body.get("event_name", "message_received"),
            "data": {
                "message_id": body.get("message", {}).get("msg_id", ""),
                "user_id": body.get("sender", {}).get("id", ""),
                "display_name": body.get("sender", {}).get("name", "")
            },
            "raw": {
                "message": body.get("message", {}).get("text", ""),
                "mentions": body.get("message", {}).get("mentions", [])
            }
        }
        
        webhook_data = SMaxWebhook(**zalo_webhook)
        
        if not mention_checker.is_bot_mentioned(webhook_data):
            return JSONResponse(
                status_code=200,
                content={"message": "Bot not mentioned, ignored"}
            )
        
        command_text = mention_checker.extract_command_text(webhook_data)
        print(f"💬 Zalo Command: {command_text}")
        
        intent_result = intent_analyzer.analyze(command_text)
        print(f"🧠 Zalo Intent: {intent_result}")
        
        response_text = await process_intent(intent_result)
        
        # Format response cho Zalo
        zalo_response = {
            "recipient": {
                "user_id": body.get("sender", {}).get("id", "")
            },
            "message": {
                "text": response_text
            }
        }
        
        # Log SMAX nếu cần
        if os.getenv("DEBUG") == "True":
            smax_response = webhook_service.forward_to_smax(zalo_webhook, intent_result)
            print(f"🚀 SMAX logged: {smax_response is not None}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "response": zalo_response,
                "intent": intent_result["intent"],
                "confidence": intent_result["confidence"]
            }
        )
        
    except Exception as e:
        print(f"❌ Error processing Zalo webhook: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/webhook/smax")
async def handle_smax_webhook(request: Request):
    """Xử lý webhook từ SMAX (nhận data từ Zalo qua SMAX)"""
    try:
        body = await request.json()
        print("=== PAYLOAD RECEIVED ===")
        print(body)
        print("========================")
        print(f"📥 Received SMAX webhook: {body}")

        # Lấy thông tin mention
        mentions = body.get("raw", {}).get("mentions", [])
        if isinstance(mentions, str):
            import json
            try:
                mentions = json.loads(mentions)
            except Exception as e:
                print(f"Error parsing mentions: {e}")
                mentions = []
        bot_id = os.getenv("BOT_ID")  # Đảm bảo BOT_ID là user_id của bot bạn

        # Chỉ xử lý nếu bot bị tag (mention)
        is_mentioned = any(m.get("user_id") == bot_id for m in mentions)
        if not is_mentioned:
            print("Bot not mentioned, ignore message.")
            return JSONResponse(status_code=200, content={"message": "Bot not mentioned, ignored"})
        
        webhook_data = SMaxWebhook(**body)
        command_text = mention_checker.extract_command_text(webhook_data)
        print(f"💬 Command extracted: {command_text}")
        
        # Nếu phát hiện intent đặc biệt cho block Zalo thì trả về đúng format
        if "báo cáo hôm nay" in command_text.lower():
            response_for_zalo = parse_intent(command_text)
            return JSONResponse(status_code=200, content=response_for_zalo)
        
        intent_result = intent_analyzer.analyze(command_text)
        print(f"🧠 Intent analyzed: {intent_result}")
        
        # Log đến SMAX API (để tracking/analytics)
        smax_response = webhook_service.forward_to_smax(body, intent_result)
        
        response_text = await process_intent(intent_result)
        
        # Format response cho SMAX (sẽ forward về Zalo)
        smax_formatted_response = {
            "success": True,
            "response_type": "text",
            "content": {
                "text": response_text,
                "format": "markdown"
            },
            "metadata": {
                "intent": intent_result["intent"],
                "confidence": intent_result["confidence"],
                "bot_id": os.getenv("BOT_ID"),
                "processed_at": datetime.now().isoformat(),
                "source": "bot_biva"
            },
            "webhook_attributes": webhook_service.process_webhook_attributes(body)
        }
        
        print(f"📤 Sending response to SMAX: {smax_formatted_response}")
        
        return JSONResponse(
            status_code=200,
            content=smax_formatted_response
        )
        
    except Exception as e:
        print(f"❌ Error processing SMAX webhook: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/webhook/smax_v2")
async def smax_webhook_v2(request: Request, x_api_key: str = Header(None)):
    # Bảo mật: kiểm tra API Key
    if x_api_key != SMAX_API_KEY:
        logging.warning("Unauthorized Smax request")
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    logging.info(f"=== PAYLOAD RECEIVED (v2) ===\n{body}\n========================")

    # Log message_text để debug
    message_text = body.get("message_text", "")
    logging.info(f"Received message_text: '{message_text}'")

    # Validate payload
    required_fields = ["user_id", "message_text"]
    if not all(field in body for field in required_fields):
        logging.error("Missing required fields in Smax payload")
        return JSONResponse(status_code=400, content={"error": "Missing required fields"})

    # Lấy pid và page_pid nếu có
    pid = body.get("pid")
    page_pid = body.get("page_pid")

    # Phân tích intent
    intent, params = analyze_intent_v2(body["message_text"])

    # Gọi module nghiệp vụ
    try:
        response_message = handle_business_logic_v2(intent, params, body)
    except Exception as e:
        logging.error(f"Business logic error: {e}")
        response_message = "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau."

    # Chỉ trả về message nếu intent khác 'unknown'
    return JSONResponse(status_code=200, content={
        "message": response_message if intent != "unknown" else "Xin lỗi, tôi chưa hiểu yêu cầu của bạn.",
        "pid": pid,
        "page_pid": page_pid
    })


def analyze_intent_v2(message_text):
    print(f"[DEBUG] analyze_intent_v2 input: {message_text}")
    message = message_text.lower()
    # call_report_today
    if re.search(r"báo cáo.*hôm nay|số cuộc gọi.*ngày|thống kê.*hôm nay|cuộc gọi.*today", message):
        print(f"[DEBUG] analyze_intent_v2 output: call_report_today, {{}}")
        return "call_report_today", {}
    # call_report_week
    if re.search(r"báo cáo.*tuần|thống kê.*tuần|cuộc gọi.*tuần|weekly.*report", message):
        print(f"[DEBUG] analyze_intent_v2 output: call_report_week, {{}}")
        return "call_report_week", {}
    # call_report_month
    if re.search(r"báo cáo.*tháng|thống kê.*tháng|cuộc gọi.*tháng|monthly.*report", message):
        print(f"[DEBUG] analyze_intent_v2 output: call_report_month, {{}}")
        return "call_report_month", {}
    # system_status
    if re.search(r"trạng thái.*hệ thống|kiểm tra.*hệ thống|hệ thống.*thế nào|system.*status|health.*check", message):
        print(f"[DEBUG] analyze_intent_v2 output: system_status, {{}}")
        return "system_status", {}
    # phone_config
    if re.search(r"cấu hình.*số|config.*phone|thiết lập.*điện thoại|setup.*number", message):
        phone_pattern = r'(\+?84|0)[0-9]{8,10}'
        phone_match = re.search(phone_pattern, message)
        params = {"phone_number": phone_match.group()} if phone_match else {}
        print(f"[DEBUG] analyze_intent_v2 output: phone_config, {params}")
        return "phone_config", params
    # phone_list
    if re.search(r"danh sách.*số|số điện thoại.*nào|list.*phone|show.*numbers", message):
        print(f"[DEBUG] analyze_intent_v2 output: phone_list, {{}}")
        return "phone_list", {}
    # check_order
    if "kiểm tra trạng thái đơn hàng" in message:
        order_id = re.findall(r"đơn hàng (\w+)", message)
        params = {"order_id": order_id[0]} if order_id else {}
        print(f"[DEBUG] analyze_intent_v2 output: check_order, {params}")
        return "check_order", params
    # Trích xuất thời gian
    params = {}
    if "hôm qua" in message:
        params["period"] = "yesterday"
    elif "tuần trước" in message:
        params["period"] = "last_week"
    elif "tháng trước" in message:
        params["period"] = "last_month"
    print(f"[DEBUG] analyze_intent_v2 output: unknown, {params}")
    return "unknown", params


def handle_business_logic_v2(intent, params, body):
    print(f"[DEBUG] intent: {intent}, params: {params}")
    if intent == "call_report_today":
        data = smax_service.get_call_report("today")
        print(f"[DEBUG] call_report_today data: {data}")
        result = response_formatter.format_call_report(data, "today")
        print(f"[DEBUG] formatted result: {result}")
        return result
    if intent == "call_report_week":
        data = smax_service.get_call_report("week")
        print(f"[DEBUG] call_report_week data: {data}")
        result = response_formatter.format_call_report(data, "week")
        print(f"[DEBUG] formatted result: {result}")
        return result
    if intent == "call_report_month":
        data = smax_service.get_call_report("month")
        print(f"[DEBUG] call_report_month data: {data}")
        result = response_formatter.format_call_report(data, "month")
        print(f"[DEBUG] formatted result: {result}")
        return result
    if intent == "system_status":
        data = smax_service.get_system_status()
        print(f"[DEBUG] system_status data: {data}")
        result = response_formatter.format_system_status(data)
        print(f"[DEBUG] formatted result: {result}")
        return result
    if intent == "phone_list":
        data = smax_service.get_phone_config()
        print(f"[DEBUG] phone_list data: {data}")
        result = response_formatter.format_phone_config(data)
        print(f"[DEBUG] formatted result: {result}")
        return result
    if intent == "phone_config":
        phone_number = params.get("phone_number")
        print(f"[DEBUG] phone_config phone_number: {phone_number}")
        if phone_number:
            result = smax_service.configure_phone(phone_number)
            print(f"[DEBUG] configure_phone result: {result}")
            formatted = response_formatter.format_config_result(result)
            print(f"[DEBUG] formatted result: {formatted}")
            return formatted
        else:
            formatted = response_formatter.format_config_result("❌ Vui lòng cung cấp số điện thoại cần cấu hình!\nVí dụ: `cấu hình số 0901234567`")
            print(f"[DEBUG] formatted result: {formatted}")
            return formatted
    if intent == "check_order":
        order_id = params.get("order_id")
        print(f"[DEBUG] check_order order_id: {order_id}")
        result = check_order_status_v2(order_id)
        print(f"[DEBUG] check_order result: {result}")
        return result  # Trả về chuỗi đơn giản, không dùng format_config_result
    formatted = response_formatter.format_unknown_command()
    print(f"[DEBUG] formatted result: {formatted}")
    return formatted

def check_order_status_v2(order_id):
    if not order_id:
        return "Bạn vui lòng cung cấp mã đơn hàng."
    return f"Đơn hàng {order_id} đang được giao."

# Hàm gửi phản hồi về Smax

def send_response_to_smax_v2(response_body):
    headers = {
        "Authorization": f"Bearer {SMAX_TOKEN}",
        "Content-Type": "application/json"
    }
    customer_pairs = [
        {"pid": "zlw7130418348219046314", "page_pid": "zlw142009811400881830"},
        {"pid": "zlw4653585428410358730", "page_pid": "zlw142009811400881830"},
        {"pid": "zlw3103011479636620366", "page_pid": "zlw142009811400881830"}
    ]
    for customer in customer_pairs:
        payload = {
            "customer": customer,
            "attrs": [
                {"name": "message", "value": response_body.get("response_message", "")},
                {"name": "mentions", "value": response_body.get("mentions", "")}
            ]
        }
        try:
            resp = requests.post(SMAX_RESPONSE_WEBHOOK_URL, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            logging.info(f"Sent response to Smax for customer {customer}: {resp.status_code}")
        except Exception as e:
            logging.error(f"Error sending response to Smax for customer {customer}: {e}")

async def process_intent(intent_result: dict) -> str:
    """Xử lý intent và trả về response text"""
    intent = intent_result["intent"]
    parameters = intent_result["parameters"]
    
    if intent == "call_report_today":
        data = smax_service.get_call_report("today")
        return response_formatter.format_call_report(data, "today")
    
    elif intent == "call_report_week":
        data = smax_service.get_call_report("week")
        return response_formatter.format_call_report(data, "week")
    
    elif intent == "call_report_month":
        data = smax_service.get_call_report("month")
        return response_formatter.format_call_report(data, "month")
    
    elif intent == "system_status":
        data = smax_service.get_system_status()
        return response_formatter.format_system_status(data)
    
    elif intent == "phone_list":
        data = smax_service.get_phone_config()
        return response_formatter.format_phone_config(data)
    
    elif intent == "phone_config":
        phone_number = parameters.get("phone_number")
        if phone_number:
            result = smax_service.configure_phone(phone_number)
            return response_formatter.format_config_result(result)
        else:
            return response_formatter.format_config_result("❌ Vui lòng cung cấp số điện thoại cần cấu hình!\nVí dụ: `cấu hình số 0901234567`")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)