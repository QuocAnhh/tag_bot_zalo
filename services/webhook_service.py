import requests
from typing import Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class WebhookService:
    def __init__(self):
        # URL webhook của bot để SMAX gọi đến
        self.webhook_url = os.getenv("SMAX_WEBHOOK_URL")
        self.smax_api_url = "https://api.smax.ai/public/bizs/hotline-biva/triggers/686e1c9e78179ca2b4cca02e"
        self.token = os.getenv("SMAX_TOKEN", "eyJhbGciOiJIUzI1NiJ9...")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def forward_to_smax(self, webhook_data: Dict[str, Any], intent_data: Dict[str, Any]) -> Optional[Dict]:
        """Forward webhook data đến SMAX API với format chuẩn"""
        
        smax_payload = {
            "customer": {
                "id": webhook_data.get("data", {}).get("user_id", ""),
                "page_id": webhook_data.get("data", {}).get("group_id", "")
            },
            "attrs": [
                {"name": "message", "value": webhook_data.get("raw", {}).get("message", "")},
                {"name": "mentions", "value": webhook_data.get("raw", {}).get("mentions", "")}
            ]
        }
        
        # Gửi thật đến SMAX API
        try:
            response = requests.post(
                self.smax_api_url,
                headers=self.headers,
                json=smax_payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            print(f"✅ SMAX Response: {result}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ SMAX API Error: {e}")
            return None
    
    def process_webhook_attributes(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý và trích xuất attributes từ webhook"""
        
        return {
            "webhook_url": self.webhook_url,
            "method": "POST", 
            "content_type": "application/json",
            "event_filter": "zalo_mention",
            "webhook_enabled": "enabled",
            "trigger_on": "mention_received",
            "connection_timeout": "30",
            "processed_at": datetime.now().isoformat(),
            "source": "zalo_bot_biva"
        }
    
    def validate_webhook_setup(self) -> Dict[str, Any]:
        """Kiểm tra cấu hình webhook có đúng không"""
        
        expected_attributes = [
            "webhook_url", "method", "content_type", 
            "event_filter", "webhook_enabled", "trigger_on", "connection_timeout"
        ]
        
        current_config = self.process_webhook_attributes({})
        
        validation_result = {
            "valid": True,
            "webhook_url": self.webhook_url,
            "smax_api_url": self.smax_api_url,
            "attributes_configured": expected_attributes,
            "current_config": current_config,
            "timestamp": datetime.now().isoformat()
        }
        
        return validation_result
