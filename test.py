import requests

def test_line_token(channel_access_token):
    """
    ทดสอบว่า Channel Access Token ใช้งานได้หรือไม่
    """
    url = "https://api.line.me/v2/bot/info"
    
    headers = {
        'Authorization': f'Bearer {channel_access_token}'
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Token ใช้งานได้!")
        print(f"Bot Name: {data.get('displayName', 'N/A')}")
        print(f"User ID: {data.get('userId', 'N/A')}")
        print(f"Chat Mode: {data.get('chatMode', 'N/A')}")
        return True
    else:
        print("❌ Token ไม่ถูกต้อง!")
        print(f"Error: {response.text}")
        return False

# ทดสอบ Token
if __name__ == "__main__":
    # ใส่ Channel Access Token ของคุณที่นี่
    CHANNEL_ACCESS_TOKEN = "s4BtggEmX4IbMkVKOhk8PSlDyGoOxMA5m4eLpgYDOGIL1zqnVLjT92GaXk/S+7/DAxSlmRWNQDO7KT0+VvbOQDb1P/xGPxHLHFYcDsDFbaykVpLAAWTKPcaaLfAcTvEXXEGGaMAclwVBbkxM6OdyWQdB04t89/1O/w1cDnyilFU="
    
    test_line_token(CHANNEL_ACCESS_TOKEN)