from datetime import datetime, timedelta
import random
from typing import Dict, Any

class FakeDataService:
    def __init__(self):
        self.call_data = self._generate_call_data()
        self.system_status = self._generate_system_status()
        self.phone_configs = self._generate_phone_configs()
    
    def _generate_call_data(self) -> Dict[str, Any]:
        """Tạo fake data cho các cuộc gọi"""
        today = datetime.now()
        return {
            "today": {
                "total_calls": random.randint(10, 50),
                "successful_calls": random.randint(8, 45),
                "failed_calls": random.randint(1, 5),
                "avg_duration": f"{random.randint(30, 180)} giây"
            },
            "week": {
                "total_calls": random.randint(100, 300),
                "successful_calls": random.randint(80, 250),
                "failed_calls": random.randint(5, 20),
                "daily_breakdown": [
                    {"date": (today - timedelta(days=i)).strftime("%d/%m"), 
                     "calls": random.randint(5, 25)} 
                    for i in range(7)
                ]
            },
            "month": {
                "total_calls": random.randint(500, 1500),
                "growth_rate": f"+{random.randint(5, 25)}%",
                "busiest_hour": f"{random.randint(9, 17)}:00"
            }
        }
    
    def _generate_system_status(self) -> Dict[str, Any]:
        """Fake system status"""
        statuses = ["Hoạt động tốt", "Cảnh báo", "Bảo trì"]
        return {
            "overall_status": random.choice(statuses),
            "uptime": f"{random.randint(90, 99)}.{random.randint(0, 9)}%",
            "last_restart": "2 ngày trước",
            "active_lines": random.randint(5, 12),
            "queue_length": random.randint(0, 5)
        }
    
    def _generate_phone_configs(self) -> Dict[str, Any]:
        """Fake phone configurations"""
        return {
            "configured_numbers": [
                "+84901234567", "+84912345678", "+84923456789"
            ],
            "total_lines": 10,
            "active_lines": 8,
            "last_config_change": "1 giờ trước"
        }
    
    def get_call_report(self, period: str = "today") -> Dict[str, Any]:
        """Lấy báo cáo cuộc gọi theo thời gian"""
        return self.call_data.get(period, self.call_data["today"])
    
    def get_system_status(self) -> Dict[str, Any]:
        """Lấy trạng thái hệ thống"""
        return self.system_status
    
    def get_phone_config(self) -> Dict[str, Any]:
        """Lấy cấu hình số điện thoại"""
        return self.phone_configs
    
    def configure_phone(self, phone_number: str) -> Dict[str, Any]:
        """Fake cấu hình số điện thoại mới"""
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            return {
                "success": True,
                "message": f"Đã cấu hình thành công số {phone_number}",
                "new_config": {
                    "phone": phone_number,
                    "status": "active",
                    "configured_at": datetime.now().strftime("%H:%M %d/%m/%Y")
                }
            }
        else:
            return {
                "success": False,
                "message": f"Không thể cấu hình số {phone_number}. Vui lòng thử lại!",
                "error": "CONNECTION_TIMEOUT"
            }