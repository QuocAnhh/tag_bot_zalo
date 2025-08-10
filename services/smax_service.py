from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

from .fake_data import FakeDataService

load_dotenv()

class SmaxService:
    """tương tác với smax api"""
    def __init__(self):
        self.token = os.getenv("SMAX_TOKEN", "your_smax_token_here")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.fake_service = FakeDataService()

    async def get_call_report(self, period: str = "today") -> Dict[str, Any]:
        """lấy báo cáo cuộc gọi"""
        print(f"Service: Getting call report for period '{period}'...")
        # In a real implementation, you would make an async HTTP request here
        # await http_client.post(...)
        return self.fake_service.get_call_report(period)

    async def get_system_status(self) -> Dict[str, Any]:
        """lấy báo cáo trạng thái hệ thống"""
        print("Service: Getting system status...")
        return self.fake_service.get_system_status()

    async def get_phone_config(self) -> Dict[str, Any]:
        """lấy cấu hình điện thoại"""
        print("Service: Getting phone config...")
        return self.fake_service.get_phone_config()

    async def configure_phone(self, phone_number: str) -> Dict[str, Any]:
        """cấu hình điện thoại"""
        print(f"Service: Configuring phone number '{phone_number}'...")
        return self.fake_service.configure_phone(phone_number)
