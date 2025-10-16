

import requests
import json

def send_line_message(channel_access_token, user_id, message):
    """
    ส่งข้อความผ่าน LINE Messaging API
    
    Args:
        channel_access_token (str): Channel Access Token
        user_id (str): User ID ของผู้รับ
        message (str): ข้อความที่ต้องการส่ง
    
    Returns:
        bool: True ถ้าส่งสำเร็จ, False ถ้าส่งไม่สำเร็จ
    """
    url = "https://api.line.me/v2/bot/message/broadcast"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {channel_access_token}'
    }
    
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("ส่งข้อความสำเร็จ")
        return True
    else:
        print(f"ส่งข้อความไม่สำเร็จ: {response.status_code}")
        print(response.text)
        return False

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    CHANNEL_ACCESS_TOKEN = "s4BtggEmX4IbMkVKOhk8PSlDyGoOxMA5m4eLpgYDOGIL1zqnVLjT92GaXk/S+7/DAxSlmRWNQDO7KT0+VvbOQDb1P/xGPxHLHFYcDsDFbaykVpLAAWTKPcaaLfAcTvEXXEGGaMAclwVBbkxM6OdyWQdB04t89/1O/w1cDnyilFU="
    USER_ID = "U2b2ca0d3bbe61e7dadc5a393ec8d5e9c"
    MESSAGE = "สวัสดีครับ! ทดสอบส่งข้อความจาก Python"
    
    send_line_message(CHANNEL_ACCESS_TOKEN, USER_ID, MESSAGE)