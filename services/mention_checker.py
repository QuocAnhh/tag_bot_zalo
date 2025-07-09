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
                        if isinstance(mention, dict) and mention.get("user_id") == self.bot_id:
                            return True
            
            message = raw_data.get("message", "")
            if f"@{self.bot_id}" in message or "@BotBiva" in message:
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking mentions: {e}")
            return False
    
    def extract_command_text(self, webhook_data: SMaxWebhook) -> str:
        """abtract text command sau khi loại bỏ mention"""
        try:
            message = webhook_data.raw.get("message", "")
            
            # Loại bỏ mention khỏi message
            cleaned_message = message.replace(f"@{self.bot_id}", "").replace("@BotBiva", "")
            
            return cleaned_message.strip()
            
        except Exception as e:
            print(f"Error extracting command: {e}")
            return ""