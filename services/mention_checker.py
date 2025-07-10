import os
from typing import List
from app.models.webhook import SMaxWebhook, Mention

class MentionChecker:
    def __init__(self):
        self.bot_id = os.getenv("BOT_ID", "default_bot_id")
    
    def is_bot_mentioned(self, webhook_data: SMaxWebhook) -> bool:
        """check xem bot có được tag không"""
        try:
            # Kiểm tra trong raw data
            raw_data = webhook_data.raw
            
            # Tìm mentions trong raw data
            if "mentions" in raw_data:
                mentions = raw_data["mentions"]
                if isinstance(mentions, list):
                    for mention in mentions:
                        if isinstance(mention, dict):
                            user_id = mention.get("user_id")
                            display_name = mention.get("display_name", "")
                            # Check bot ID hoặc display name
                            if user_id == self.bot_id or "BotBiva" in display_name or "botbiva" in display_name.lower():
                                return True
            
            # Kiểm tra message text để tìm mention
            message = raw_data.get("message", "")
            mention_patterns = [
                f"@{self.bot_id}",
                "@BotBiva", 
                "@botbiva",
                "@Quốc Anh",
                "@quốc anh", 
                "bot biva",
                "Bot Biva",
                "BOT BIVA",
                "Quốc Anh",
                "quốc anh"
            ]
            
            for pattern in mention_patterns:
                if pattern.lower() in message.lower():
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking mentions: {e}")
            return False
    
    def extract_command_text(self, webhook_data: SMaxWebhook) -> str:
        """abstract text command sau khi loại bỏ mention"""
        try:
            message = webhook_data.raw.get("message", "")
            
            # Loại bỏ tất cả các dạng mention khỏi message
            mention_patterns = [
                f"@{self.bot_id}",
                "@BotBiva", 
                "@botbiva",
                "@Quốc Anh",
                "@quốc anh",
                "bot biva",
                "Bot Biva", 
                "BOT BIVA",
                "Quốc Anh",
                "quốc anh"
            ]
            
            cleaned_message = message
            for pattern in mention_patterns:
                cleaned_message = cleaned_message.replace(pattern, "")
            
            # Loại bỏ extra spaces
            cleaned_message = " ".join(cleaned_message.split())
            
            return cleaned_message.strip()
            
        except Exception as e:
            print(f"Error extracting command: {e}")
            return ""