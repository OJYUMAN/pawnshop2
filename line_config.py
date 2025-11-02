# -*- coding: utf-8 -*-
"""
การตั้งค่าสำหรับส่งข้อความเข้า Line
"""
import json
import os
import sys

def get_line_config_file_path(config_file="line_config.json"):
    """
    Get the correct path for the LINE config file based on execution mode
    
    Args:
        config_file: Name of the config file
        
    Returns:
        Absolute path to where the config file should be read/written
    """
    # Check if running from PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # Get the directory where the exe is located
        exe_dir = os.path.dirname(sys.executable)
        config_path = os.path.join(exe_dir, config_file)
    else:
        # Running in development mode
        config_path = os.path.join(os.path.dirname(__file__), config_file)
    
    return config_path

def load_line_config():
    """
    Load LINE configuration from JSON file
    
    Returns:
        Dictionary containing LINE configuration with keys:
        - channel_access_token: LINE Channel Access Token
        - user_id: LINE User ID
    """
    config_path = get_line_config_file_path()
    
    # Default values (fallback)
    default_token = "s4BtggEmX4IbMkVKOhk8PSlDyGoOxMA5m4eLpgYDOGIL1zqnVLjT92GaXk/S+7/DAxSlmRWNQDO7KT0+VvbOQDb1P/xGPxHLHFYcDsDFbaykVpLAAWTKPcaaLfAcTvEXXEGGaMAclwVBbkxM6OdyWQdB04t89/1O/w1cDnyilFU="
    default_user_id = "e386dc4a629cc6ccb7d13d58d55cbf8c"
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {
                    'channel_access_token': config.get('channel_access_token', default_token),
                    'user_id': config.get('user_id', default_user_id)
                }
        else:
            # Create default config file if it doesn't exist
            default_config = {
                'channel_access_token': default_token,
                'user_id': default_user_id
            }
            # Ensure the directory exists
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            print("Created default line_config.json at: {}".format(config_path))
            return default_config
    except Exception as e:
        print("Error loading LINE config: {}, using defaults".format(e))
        return {
            'channel_access_token': default_token,
            'user_id': default_user_id
        }

# Load LINE configuration from JSON file
_line_config = load_line_config()

# Line Bot Configuration (loaded from JSON file)
LINE_CHANNEL_ACCESS_TOKEN = _line_config['channel_access_token']
LINE_USER_ID = _line_config['user_id']

# การตั้งค่าการส่งข้อความ
ENABLE_LINE_NOTIFICATION = True  # เปิด/ปิดการส่งข้อความเข้า Line
SEND_CONTRACT_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อบันทึกสัญญา
SEND_RENEWAL_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อต่อดอก
SEND_REDEMPTION_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อไถ่คืน
SEND_DAILY_INCOME_NOTIFICATION = True  # ส่งการแจ้งเตือนสรุปรายได้รายวัน
SEND_FORFEITURE_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อสินค้าหลุดจำนำ

# รูปแบบข้อความ
MESSAGE_TEMPLATE = {
    'contract_new': """
📋 สัญญาใหม่: {contract_number}

👤 ลูกค้า: {customer_name}
📱 เบอร์โทร: {customer_phone}
🆔 บัตรประชาชน: {customer_id_card}

💍 สินค้า: {product_name}
🏷️ ยี่ห้อ: {product_brand}

💰 ราคาฝากขาย: {pawn_amount:,.2f} บาท
📅 วันเริ่มต้น: {start_date}
📅 วันสิ้นสุด: {end_date}
⏰ จำนวนวัน: {days_count} วัน
💵 จำนวนเงินรวมที่ต้องจ่าย: {total_paid:,.2f} บาท
💎 ยอดซื้อเครื่องคืน: {total_redemption:,.2f} บาท

⏰ เวลาที่บันทึก: {timestamp}
    """.strip(),
    
    'renewal': """
🔄 การต่อดอก: {contract_number}

👤 ลูกค้า: {customer_name}
💰 จำนวนเงินเดิม: {original_amount:,.2f} บาท
💸 ค่าธรรมเนียมการต่อดอก: {renewal_fee:,.2f} บาท
📅 วันต่อดอก: {renewal_date}
⏰ เวลาที่ต่อดอก: {timestamp}
    """.strip(),
    
    'redemption': """
💎 ซื้อเครื่องคืน: {contract_number}

👤 ลูกค้า: {customer_name}
📱 เบอร์โทร: {customer_phone}
🆔 บัตรประชาชน: {customer_id_card}

💍 สินค้า: {product_name}
🏷️ ยี่ห้อ: {product_brand}

💰 จำนวนฝากขาย: {pawn_amount:,.2f} บาท
💵 จำนวนเงินรวมที่ต้องจ่าย: {total_paid:,.2f} บาท
💎 จำนวนเงินซื้อเครื่องคืน: {redemption_amount:,.2f} บาท
📅 วันเริ่มต้น: {start_date}
📅 วันสิ้นสุด: {end_date}
📅 วันซื้อเครื่องคืน: {redemption_date}
⏰ จำนวนวัน: {days_count} วัน

⏰ เวลาที่ซื้อเครื่องคืน: {timestamp}
    """.strip(),
    
    'forfeiture': """
    ⏰ สัญญาหมดอายุ: {contract_number}

    👤 ลูกค้า: {customer_name}
    💍 สินค้า: {product_name}
    💰 วงเงินกู้: {pawn_amount:,.2f} บาท
    📅 วันสิ้นสุดสัญญา: {end_date}
    ⏰ วันที่หมดอายุ: {timestamp}
    """.strip(),
    
    'daily_income': """
📊 สรุปรายได้รายวัน - {date}

📋 สัญญาใหม่: {new_contracts} สัญญา
💎 การซื้อเครื่องคืน: {redemptions} ครั้ง

💎 จำนวนเงินซื้อเครื่องคืน: {total_redemption_amount:,.2f} บาท

⏰ เวลาที่สรุป: {timestamp}
    """.strip()
}
