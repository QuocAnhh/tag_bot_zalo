import httpx
import json
import logging
from typing import Dict, Any, Optional

from config import SMAX_RESPONSE_WEBHOOK_URL, SMAX_TOKEN

logger = logging.getLogger(__name__)

class WebhookService:
    """gửi tin nhắn trả lời về webhook smax"""
    def __init__(self):
        self.smax_api_url = SMAX_RESPONSE_WEBHOOK_URL
        self.token = SMAX_TOKEN
        self.http_client: Optional[httpx.AsyncClient] = None
        
        if not self.smax_api_url or not self.token:
            logger.error("SMAX_RESPONSE_WEBHOOK_URL or SMAX_TOKEN is not configured.")
            raise ValueError("SMAX webhook configuration is missing.")
            
        logger.info(f"WebhookService initialized for URL: {self.smax_api_url}")

    def set_http_client(self, client: httpx.AsyncClient):
        """cấu hình httpx.AsyncClient"""
        logger.info("HTTP client has been set for WebhookService.")
        self.http_client = client

    def _validate_identifier(self, value: str, name: str) -> Optional[str]:
        """kiểm tra xem identifier có phải là placeholder hay không"""
        if not value or "{{" in value:
            logger.warning(f"Invalid or placeholder value for '{name}': '{value}'. Skipping.")
            return None
        return value

    def _create_payload(self, response_text: str, original_payload: Dict[str, Any], headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """tạo payload json cho webhook smax, trả về None nếu identifier không hợp lệ"""
        
        raw_pid = (headers or {}).get("pid") or original_payload.get("pid", "")
        raw_page_pid = (headers or {}).get("page_pid") or original_payload.get("page_pid", "")
        raw_user_id = (headers or {}).get("user_id") or original_payload.get("user_id", "")
        raw_group_id = (headers or {}).get("group_id") or original_payload.get("group_id", "")

        pid = self._validate_identifier(str(raw_pid), "pid")
        page_pid = self._validate_identifier(str(raw_page_pid), "page_pid")
        user_id = self._validate_identifier(str(raw_user_id), "user_id")

        if not pid or not user_id or not page_pid:
            logger.error("Cannot create a valid payload due to missing or invalid identifiers (pid, page_pid, user_id).")
            return None
        
        # group_id can be optional
        group_id = str(raw_group_id or "").strip()

        return {
            "customer": {
                "pid": pid,
                "page_pid": page_pid
            },
            "attrs": [
                {"name": "message", "value": response_text},
                {"name": "user_id", "value": user_id},
                {"name": "group_id", "value": group_id},
            ]
        }

    async def send_response_to_smax(self, response_text: str, original_payload: Dict[str, Any], headers: Dict[str, str] = None) -> bool:
        """gửi tin nhắn trả lời về smax"""
        if not response_text or not isinstance(response_text, str):
            logger.error("Invalid response_text provided.")
            return False
            
        if not original_payload or not isinstance(original_payload, dict):
            logger.error("Invalid original_payload provided.")
            return False

        payload = self._create_payload(response_text, original_payload, headers)
        
        if not payload:
            logger.error("Payload creation failed due to invalid identifiers. Aborting send to SMAX.")
            return False
            
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": "Zalo-Biva-Bot/1.0"
        }
        
        if not self.http_client:
            logger.critical("HTTP client is not available in WebhookService. Cannot send request to SMAX.")
            return False

        logger.info(f"Sending POST request to SMAX at {self.smax_api_url}")
        logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        try:
            response = await self.http_client.post(
                self.smax_api_url,
                headers=headers,
                json=payload
            )
            
            # raise an exception for 4xx/5xx responses
            response.raise_for_status() 
            
            logger.info(f"Successfully sent response to SMAX. Status: {response.status_code}")
            logger.debug(f"SMAX Response Body: {response.text}")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred when calling SMAX: {e.response.status_code} - {e.response.text}")
            logger.error(f"Request payload that failed: {json.dumps(payload, ensure_ascii=False)}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request to SMAX failed: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred in send_response_to_smax: {e}", exc_info=True)
            return False
    
    def test_payload_format(self, response_text: str = "Test message", original_payload: Dict[str, Any] = None) -> Dict:
        """phương thức kiểm tra format payload"""
        
        if original_payload is None:
            original_payload = {
                "pid": "test_pid_123",
                "page_pid": "test_page_456", 
                "user_id": "test_user_789",
                "group_id": "test_group_012"
            }
        
        # clean and validate values
        pid = str(original_payload.get("pid", "")).strip()
        page_pid = str(original_payload.get("page_pid", "")).strip()
        user_id = str(original_payload.get("user_id", "")).strip()
        group_id = str(original_payload.get("group_id", "")).strip()
        
        test_payload = {
            "customer": {
                "pid": pid,
                "page_pid": page_pid
            },
            "attrs": [
                {
                    "name": "message",
                    "value": response_text
                },
                {
                    "name": "user_id", 
                    "value": user_id
                },
                {
                    "name": "group_id",
                    "value": group_id
                }
            ]
        }
        
        print("🧪 Test payload format:")
        print(json.dumps(test_payload, indent=2, ensure_ascii=False))
        return test_payload
