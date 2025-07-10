import requests
import json
from datetime import datetime
import os

# Ngrok URL 
NGROK_URL = "https://5196589df6c8.ngrok-free.app"
SMAX_WEBHOOK_URL = os.getenv("SMAX_WEBHOOK_URL", "https://5196589df6c8.ngrok-free.app/webhook/smax")

def simulate_zalo_mention(user_name="TestUser", command="báo cáo cuộc gọi hôm nay"):
    """Simulate user tag bot trên Zalo"""
    print(f"🎭 Simulating: {user_name} tags @Quốc Anh with '{command}'")
    
    # Format giống như SMAX sẽ gửi khi có user tag bot trên Zalo
    smax_webhook_data = {
        "event_type": "zalo_mention_received",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "data": {
            "message_id": f"zalo_msg_{datetime.now().timestamp()}",
            "user_id": f"zalo_user_{hash(user_name) % 10000}",
            "display_name": user_name,
            "platform": "zalo"
        },
        "raw": {
            "message": f"@Quốc Anh {command}",
            "mentions": [
                {
                    "user_id": "Quốc Anh",  # Bot ID mới
                    "display_name": "Quốc Anh",
                    "start": 0,
                    "end": 9
                }
            ],
            "source": "zalo_platform",
            "chat_type": "group",  # hoặc "private"
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        print(f"📤 Sending to: {SMAX_WEBHOOK_URL}")
        response = requests.post(SMAX_WEBHOOK_URL, json=smax_webhook_data, timeout=10)
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract info
            success = result.get('success', False)
            content = result.get('content', {})
            metadata = result.get('metadata', {})
            
            print(f"📤 Success: {success}")
            print(f"🧠 Intent: {metadata.get('intent')}")
            print(f"🎯 Confidence: {metadata.get('confidence')}")
            
            # Show response text
            response_text = content.get('text', '')
            print(f"\n💬 Bot Response to {user_name}:")
            print("=" * 50)
            print(response_text)
            print("=" * 50)
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_different_users_and_commands():
    """Test với nhiều user và command khác nhau"""
    print("🎭 Testing different users and commands...")
    
    test_cases = [
        ("Alice", "báo cáo cuộc gọi hôm nay"),
        ("Bob", "thống kê tuần này"),
        ("Charlie", "kiểm tra trạng thái hệ thống"),
        ("Diana", "danh sách số điện thoại"),
        ("Eve", "cấu hình số 0901234567"),
        ("Frank", "báo cáo tháng này")
    ]
    
    success_count = 0
    for user, command in test_cases:
        print(f"\n{'='*60}")
        if simulate_zalo_mention(user, command):
            success_count += 1
        print(f"{'='*60}")
    
    print(f"\n📊 Results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_edge_cases():
    """Test các trường hợp đặc biệt"""
    print("\n🔍 Testing edge cases...")
    
    edge_cases = [
        ("User1", "hey bot"),  # Không match intent
        ("User2", "@BotBiva"),  # Chỉ mention, không có command
        ("User3", "BotBiva báo cáo"),  # Không có @
        ("User4", "@BotBiva help"),  # Unknown command
    ]
    
    for user, message in edge_cases:
        print(f"\n🔍 Edge case: {user} -> '{message}'")
        simulate_zalo_mention(user, message.replace("@BotBiva ", ""))

def main():
    print("🤖 Zalo Bot Simulation Test")
    print("Giả lập user tag @Quốc Anh trên Zalo qua SMAX")
    print(f"🌐 Testing URL: {NGROK_URL}")
    print("="*60)
    
    # Test health first
    try:
        health_response = requests.get(f"{NGROK_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Bot is ready for testing!")
        else:
            print("❌ Bot not responding!")
            return
    except:
        print("❌ Cannot connect to bot!")
        return
    
    print("\n🧪 Testing different users and commands...")
    test_different_users_and_commands()
    
    print("\n🔍 Testing edge cases...")
    test_edge_cases()
    
    print("\n🎉 Simulation completed!")
    print("\n📋 If this works, your bot is ready for real Zalo!")
    print("👥 Ask a friend to tag your bot on Zalo to test for real.")

if __name__ == "__main__":
    main()
