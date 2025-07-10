import requests
from typing import Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class SmaxService:
    def __init__(self):
        self.base_url = "https://api.smax.ai/public/bizs/hotline-biva"
        self.trigger_id = "686e1c9e78179ca2b4cca02e"
        self.token = os.getenv("SMAX_TOKEN", "eyJhbGciOiJIUzI1NiJ9...")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str = "GET", data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Gửi request đến SMAX API - DISABLED for testing"""
        print(f"🚀 Would send {method} to SMAX API: {self.base_url}")
        if data:
            print(f"📤 Payload: {data}")
        
        # DISABLED - return mock response for testing
        print("⚠️ SMAX API call disabled for testing")
        return {
            "status": "success",
            "message": "Mock SMAX response",
            "disabled": True
        }
    
    def get_call_report(self, period: str = "today") -> Dict[str, Any]:
        """Lấy báo cáo cuộc gọi từ SMAX - gọi API thật nhưng trả fake data"""
        data = {
            "customer": {
                "id": "",
                "page_id": ""
            },
            "attrs": [
                {
                    "name": "report_type",
                    "value": "call_report"
                },
                {
                    "name": "period", 
                    "value": period
                },
                {
                    "name": "timestamp",
                    "value": datetime.now().isoformat()
                }
            ]
        }
        
        # Mock SMAX API call (disabled for testing)
        result = self._make_request("POST", data)
        print(f"SMAX API Response for call_report: {result}")
        
        # Luôn trả về fake data
        from .fake_data import FakeDataService
        fake_service = FakeDataService()
        return fake_service.get_call_report(period)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Lấy trạng thái hệ thống từ SMAX - gọi API thật nhưng trả fake data"""
        data = {
            "customer": {
                "id": "",
                "page_id": ""
            },
            "attrs": [
                {
                    "name": "report_type",
                    "value": "system_status"
                },
                {
                    "name": "timestamp",
                    "value": datetime.now().isoformat()
                }
            ]
        }
        
        # Mock SMAX API call (disabled for testing)
        result = self._make_request("POST", data)
        print(f"SMAX API Response for system_status: {result}")
        
        # Luôn trả về fake data
        from .fake_data import FakeDataService
        fake_service = FakeDataService()
        return fake_service.get_system_status()
    
    def get_phone_config(self) -> Dict[str, Any]:
        """Lấy cấu hình số điện thoại từ SMAX - gọi API thật nhưng trả fake data"""
        data = {
            "customer": {
                "id": "",
                "page_id": ""
            },
            "attrs": [
                {
                    "name": "report_type",
                    "value": "phone_config"
                }
            ]
        }
        
        # Gọi API SMAX thật (để test integration)
        result = self._make_request("POST", data)
        print(f"SMAX API Response for phone_config: {result}")
        
        # Luôn trả về fake data
        from .fake_data import FakeDataService
        fake_service = FakeDataService()
        return fake_service.get_phone_config()
    
    def configure_phone(self, phone_number: str) -> Dict[str, Any]:
        """Cấu hình số điện thoại mới qua SMAX - gọi API thật nhưng trả fake data"""
        data = {
            "customer": {
                "id": "",
                "page_id": ""
            },
            "attrs": [
                {
                    "name": "action_type",
                    "value": "configure_phone"
                },
                {
                    "name": "phone_number",
                    "value": phone_number
                },
                {
                    "name": "timestamp",
                    "value": datetime.now().isoformat()
                }
            ]
        }
        
        # Gọi API SMAX thật (để test integration)
        result = self._make_request("POST", data)
        print(f"SMAX API Response for configure_phone: {result}")
        
        # Luôn trả về fake data
        from .fake_data import FakeDataService
        fake_service = FakeDataService()
        return fake_service.configure_phone(phone_number)
    
    def _process_call_report(self, data: Dict, period: str) -> Dict[str, Any]:
        """Xử lý dữ liệu báo cáo cuộc gọi từ SMAX"""
        # Xử lý response từ SMAX API thành format mong muốn
        # Tùy thuộc vào structure response thực tế từ SMAX
        
        # Ví dụ structure (cần điều chỉnh theo response thực tế):
        if period == "today":
            return {
                "total_calls": data.get("total_calls", 0),
                "successful_calls": data.get("successful_calls", 0), 
                "failed_calls": data.get("failed_calls", 0),
                "avg_duration": data.get("avg_duration", "0 giây")
            }
        elif period == "week":
            return {
                "total_calls": data.get("total_calls", 0),
                "successful_calls": data.get("successful_calls", 0),
                "failed_calls": data.get("failed_calls", 0),
                "daily_breakdown": data.get("daily_breakdown", [])
            }
        elif period == "month":
            return {
                "total_calls": data.get("total_calls", 0),
                "growth_rate": data.get("growth_rate", "0%"),
                "busiest_hour": data.get("busiest_hour", "Unknown")
            }
    
    def _process_system_status(self, data: Dict) -> Dict[str, Any]:
        """Xử lý dữ liệu trạng thái hệ thống"""
        return {
            "overall_status": data.get("status", "Unknown"),
            "uptime": data.get("uptime", "0%"),
            "last_restart": data.get("last_restart", "Unknown"),
            "active_lines": data.get("active_lines", 0),
            "queue_length": data.get("queue_length", 0)
        }
    
    def _process_phone_config(self, data: Dict) -> Dict[str, Any]:
        """Xử lý dữ liệu cấu hình phone"""
        return {
            "configured_numbers": data.get("configured_numbers", []),
            "total_lines": data.get("total_lines", 0),
            "active_lines": data.get("active_lines", 0),
            "last_config_change": data.get("last_config_change", "Unknown")
        }
    
    def _process_config_result(self, data: Dict, phone_number: str) -> Dict[str, Any]:
        """Xử lý kết quả cấu hình phone"""
        success = data.get("success", False)
        
        if success:
            return {
                "success": True,
                "message": f"Đã cấu hình thành công số {phone_number}",
                "new_config": {
                    "phone": phone_number,
                    "status": data.get("status", "active"),
                    "configured_at": datetime.now().strftime("%H:%M %d/%m/%Y")
                }
            }
        else:
            return {
                "success": False,
                "message": data.get("message", f"Không thể cấu hình số {phone_number}"),
                "error": data.get("error_code", "UNKNOWN_ERROR")
            }
