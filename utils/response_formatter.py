from typing import Dict, Any
from datetime import datetime

class ResponseFormatter:
    @staticmethod
    def _now_str() -> str:
        return datetime.now().strftime('%H:%M %d/%m/%Y')

    @staticmethod
    def format_call_report(data: Dict[str, Any], period: str = "today") -> str:
        """Format báo cáo cuộc gọi"""
        if period == "today":
            return f"""📞 **BÁO CÁO CUỘC GỌI HÔM NAY**
            
🔢 Tổng cuộc gọi: {data['total_calls']}
✅ Thành công: {data['successful_calls']}
❌ Thất bại: {data['failed_calls']}
⏱️ Thời lượng TB: {data['avg_duration']}

_Cập nhật lúc: {ResponseFormatter._now_str()}_"""
        
        elif period == "week":
            daily_str = "\n".join([f"  • {day['date']}: {day['calls']} cuộc gọi" 
                                  for day in data['daily_breakdown']])
            return f"""📊 **BÁO CÁO TUẦN**
            
🔢 Tổng cuộc gọi: {data['total_calls']}
✅ Thành công: {data['successful_calls']}
❌ Thất bại: {data['failed_calls']}

📈 **Chi tiết theo ngày:**
{daily_str}

_Cập nhật lúc: {ResponseFormatter._now_str()}_"""
        
        elif period == "month":
            return f"""📈 **BÁO CÁO THÁNG**
            
🔢 Tổng cuộc gọi: {data['total_calls']}
📊 Tăng trưởng: {data['growth_rate']}
🕒 Giờ cao điểm: {data['busiest_hour']}

_Cập nhật lúc: {ResponseFormatter._now_str()}_"""
    
    @staticmethod
    def format_system_status(data: Dict[str, Any]) -> str:
        """Format trạng thái hệ thống"""
        status_emoji = {
            "Hoạt động tốt": "🟢",
            "Cảnh báo": "🟡", 
            "Bảo trì": "🔴"
        }
        
        emoji = status_emoji.get(data['overall_status'], "⚪")
        
        return f"""🖥️ **TRẠNG THÁI HỆ THỐNG**

{emoji} Tình trạng: {data['overall_status']}
⏳ Uptime: {data['uptime']}
🔄 Khởi động lần cuối: {data['last_restart']}
📞 Đường dây hoạt động: {data['active_lines']}/10
⏰ Hàng đợi: {data['queue_length']} cuộc gọi

_Kiểm tra lúc: {ResponseFormatter._now_str()}_"""
    
    @staticmethod
    def format_phone_config(data: Dict[str, Any]) -> str:
        """Format cấu hình số điện thoại"""
        numbers_str = "\n".join([f"  • {num}" for num in data['configured_numbers']])
        
        return f"""📱 **CẤU HÌNH SỐ ĐIỆN THOẠI**

📋 **Số đã cấu hình:**
{numbers_str}

📊 Tổng đường dây: {data['total_lines']}
🟢 Đang hoạt động: {data['active_lines']}
🕒 Thay đổi cuối: {data['last_config_change']}

_Cập nhật lúc: {ResponseFormatter._now_str()}_"""
    
    @staticmethod
    def format_config_result(result: Dict[str, Any]) -> str:
        """Format kết quả cấu hình"""
        if result['success']:
            c = result['new_config']
            return f"""✅ **CẤU HÌNH THÀNH CÔNG**

📱 Số điện thoại: {c['phone']}
🔄 Trạng thái: {c['status']}
🕒 Thời gian: {c['configured_at']}

Số điện thoại đã sẵn sàng sử dụng! 🎉"""
        return f"""❌ **CẤU HÌNH THẤT BẠI**

📱 Số: {result.get('phone', 'N/A')}
💬 Lỗi: {result['message']}
🔧 Mã lỗi: {result.get('error', 'UNKNOWN')}

Vui lòng thử lại sau! 🔄"""
    
    @staticmethod
    def format_unknown_command() -> str:
        """Format cho lệnh không hiểu"""
        return """🤖 **ZALO-BIVA-BOT RESPONSE**

❓ Xin lỗi, tôi không hiểu lệnh này.

📋 **Các lệnh có sẵn:**
• `báo cáo hôm nay` - Báo cáo cuộc gọi hôm nay
• `báo cáo tuần` - Báo cáo tuần
• `báo cáo tháng` - Báo cáo tháng  
• `trạng thái hệ thống` - Kiểm tra hệ thống
• `show numbers` - Danh sách số điện thoại
• `cấu hình số [SDT]` - Cấu hình số mới

💡 Hãy thử lại với một trong các lệnh trên!"""