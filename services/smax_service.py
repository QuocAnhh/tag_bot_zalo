from typing import Dict, Any

from .fake_data import FakeDataService

class SmaxService:
    """Tương tác dữ liệu (hiện chỉ dùng FakeDataService)."""
    def __init__(self):
        self.fake_service = FakeDataService()

    async def get_call_report(self, period: str = "today") -> Dict[str, Any]:
        return self.fake_service.get_call_report(period)

    async def get_system_status(self) -> Dict[str, Any]:
        return self.fake_service.get_system_status()

    async def get_phone_config(self) -> Dict[str, Any]:
        return self.fake_service.get_phone_config()

    async def configure_phone(self, phone_number: str) -> Dict[str, Any]:
        return self.fake_service.configure_phone(phone_number)
