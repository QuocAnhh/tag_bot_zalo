import re
from typing import Dict, Any, Optional

class SimpleIntentAnalyzer:
    """parse intent"""
    
    def __init__(self):
        self.intent_patterns = {
            "call_report_today": [
                r"báo cáo.*hôm nay",
                r"số cuộc gọi.*ngày",
                r"thống kê.*hôm nay",
                r"cuộc gọi.*today"
            ],
            "call_report_week": [
                r"báo cáo.*tuần",
                r"thống kê.*tuần",
                r"cuộc gọi.*tuần",
                r"weekly.*report"
            ],
            "call_report_month": [
                r"báo cáo.*tháng",
                r"thống kê.*tháng", 
                r"cuộc gọi.*tháng",
                r"monthly.*report"
            ],
            "system_status": [
                r"trạng thái.*hệ thống",
                r"kiểm tra.*hệ thống",
                r"hệ thống.*thế nào",
                r"system.*status",
                r"health.*check"
            ],
            "phone_config": [
                r"cấu hình.*số",
                r"config.*phone",
                r"thiết lập.*điện thoại",
                r"setup.*number"
            ],
            "phone_list": [
                r"danh sách.*số",
                r"số điện thoại.*nào",
                r"list.*phone",
                r"show.*numbers",
                r"phone.*list",
                r"list phone",  # Exact match for "list phone"
                r"phone.*config.*list"
            ]
        }
    
    def analyze(self, command_text: str) -> Dict[str, Any]:
        """Phân tích intent từ command text"""
        command_lower = command_text.lower()
        
        # tìm intent
        detected_intent = self._detect_intent(command_lower)
        
        # lấy paramêtrs
        parameters = self._extract_parameters(command_lower, detected_intent)
        
        return {
            "intent": detected_intent,
            "parameters": parameters,
            "confidence": 0.95 if detected_intent != "unknown" else 0.1,
            "original_text": command_text
        }
    
    def _detect_intent(self, text: str) -> str:
        """Detect intent từ text"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return "unknown"
    
    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """trích xuất parameters từ text"""
        params = {}
        
        # bóc tách số điện thoại
        phone_pattern = r'(\+?84|0)[0-9]{8,10}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            params["phone_number"] = phone_match.group()
        
        # bóc tách thời gian
        if "hôm qua" in text:
            params["period"] = "yesterday"
        elif "tuần trước" in text:
            params["period"] = "last_week"
        elif "tháng trước" in text:
            params["period"] = "last_month"
        
        return params