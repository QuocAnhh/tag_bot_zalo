import re
from typing import Dict, Any

class SimpleIntentAnalyzer:
    """Phân tích intent dựa trên danh sách regex đơn giản."""
    def __init__(self):
        raw_patterns = {
            "call_report_today": [
                r"báo cáo.*hôm nay", r"số cuộc gọi.*ngày", r"thống kê.*hôm nay", r"cuộc gọi.*today"
            ],
            "call_report_week": [
                r"báo cáo.*tuần", r"thống kê.*tuần", r"cuộc gọi.*tuần", r"weekly.*report"
            ],
            "call_report_month": [
                r"báo cáo.*tháng", r"thống kê.*tháng", r"cuộc gọi.*tháng", r"monthly.*report"
            ],
            "system_status": [
                r"trạng thái.*hệ thống", r"kiểm tra.*hệ thống", r"hệ thống.*thế nào", r"system.*status", r"health.*check"
            ],
            "phone_config": [
                r"cấu hình.*số", r"config.*phone", r"thiết lập.*điện thoại", r"setup.*number"
            ],
            "phone_list": [
                r"danh sách.*số", r"số điện thoại.*nào", r"list.*phone", r"show.*numbers", r"phone.*list", r"list phone", r"phone.*config.*list"
            ],
        }
        self.intent_patterns = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in raw_patterns.items()
        }
        self.phone_regex = re.compile(r'(\+?84|0)[0-9]{8,10}')

    def analyze(self, command_text: str) -> Dict[str, Any]:
        text = command_text.strip()
        intent = self._detect_intent(text)
        params = self._extract_parameters(text, intent)
        return {
            "intent": intent,
            "parameters": params,
            "confidence": 0.95 if intent != "unknown" else 0.1,
            "original_text": command_text,
        }

    def _detect_intent(self, text: str) -> str:
        for intent, patterns in self.intent_patterns.items():
            if any(p.search(text) for p in patterns):
                return intent
        return "unknown"

    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        phone_match = self.phone_regex.search(text)
        if phone_match:
            params["phone_number"] = phone_match.group()
        if "hôm qua" in text:
            params["period"] = "yesterday"
        elif "tuần trước" in text:
            params["period"] = "last_week"
        elif "tháng trước" in text:
            params["period"] = "last_month"
        return params