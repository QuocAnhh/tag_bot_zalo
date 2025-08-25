from datetime import datetime, timedelta
from typing import Dict, Any

class FakeDataService:
    def __init__(self):
        self.call_data = self._generate_call_data()
        self.system_status = self._generate_system_status()
        self.phone_configs = self._generate_phone_configs()

    def _generate_call_data(self) -> Dict[str, Any]:
        today = datetime.now()
        return {
            "today": {"total_calls": 42, "successful_calls": 35, "failed_calls": 7, "avg_duration": "120 giây"},
            "week": {
                "total_calls": 210,
                "successful_calls": 180,
                "failed_calls": 30,
                "daily_breakdown": [{"date": (today - timedelta(days=i)).strftime("%d/%m"), "calls": 30 - i} for i in range(7)],
            },
            "month": {"total_calls": 900, "growth_rate": "+15%", "busiest_hour": "10:00"},
        }

    def _generate_system_status(self) -> Dict[str, Any]:
        return {"overall_status": "Hoạt động tốt", "uptime": "98.7%", "last_restart": "2 ngày trước", "active_lines": 8, "queue_length": 2}

    def _generate_phone_configs(self) -> Dict[str, Any]:
        return {"configured_numbers": ["+84901234567", "+84912345678", "+84923456789"], "total_lines": 10, "active_lines": 8, "last_config_change": "1 giờ trước"}

    def get_call_report(self, period: str = "today") -> Dict[str, Any]:
        return self.call_data.get(period, self.call_data["today"])

    def get_system_status(self) -> Dict[str, Any]:
        return self.system_status

    def get_phone_config(self) -> Dict[str, Any]:
        return self.phone_configs

    def configure_phone(self, phone_number: str) -> Dict[str, Any]:
        return {
            "success": True,
            "message": f"Đã cấu hình thành công số {phone_number}",
            "new_config": {"phone": phone_number, "status": "active", "configured_at": datetime.now().strftime("%H:%M %d/%m/%Y")},
        }
