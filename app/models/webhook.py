from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Mention(BaseModel):
    user_id: str
    display_name: str
    start: int
    end: int

class ZaloMessage(BaseModel):
    message_id: str
    user_id: str
    display_name: str
    message: str
    timestamp: int
    mentions: Optional[List[Mention]] = []

class SMaxWebhook(BaseModel):
    event_type: str
    data: Dict[str, Any]
    raw: Dict[str, Any]
    
class BotResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None