# -*- coding: utf-8 -*-
"""
การตั้งค่าสำหรับส่งข้อความเข้า Line
"""

# Line Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN = "s4BtggEmX4IbMkVKOhk8PSlDyGoOxMA5m4eLpgYDOGIL1zqnVLjT92GaXk/S+7/DAxSlmRWNQDO7KT0+VvbOQDb1P/xGPxHLHFYcDsDFbaykVpLAAWTKPcaaLfAcTvEXXEGGaMAclwVBbkxM6OdyWQdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "U2b2ca0d3bbe61e7dadc5a393ec8d5e9c"

# การตั้งค่าการส่งข้อความ
ENABLE_LINE_NOTIFICATION = True  # เปิด/ปิดการส่งข้อความเข้า Line
SEND_CONTRACT_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อบันทึกสัญญา
SEND_RENEWAL_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อต่อดอก
SEND_REDEMPTION_NOTIFICATION = True  # ส่งการแจ้งเตือนเมื่อไถ่ถอน
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
🏷️ แบรนด์: {product_brand}
📏 ขนาด: {product_size}
🔢 เลขประจำตัว: {product_serial}

💰 จำนวนเงินกู้: {pawn_amount:,.2f} บาท
📅 วันเริ่มต้น: {start_date}
📅 วันสิ้นสุด: {end_date}
⏰ จำนวนวัน: {days_count} วัน
📊 อัตราดอกเบี้ย: {interest_rate}% ต่อเดือน
💸 ค่าธรรมเนียม: {fee_amount:,.2f} บาท
🏦 ภาษีหัก ณ ที่จ่าย: {withholding_tax_amount:,.2f} บาท
💵 จำนวนเงินรวมที่ต้องจ่าย: {total_paid:,.2f} บาท
💎 จำนวนเงินไถ่ถอน: {total_redemption:,.2f} บาท

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
💎 การไถ่ถอน: {contract_number}

👤 ลูกค้า: {customer_name}
💰 จำนวนเงินไถ่ถอน: {redemption_amount:,.2f} บาท
📅 วันไถ่ถอน: {redemption_date}
⏰ เวลาที่ไถ่ถอน: {timestamp}
    """.strip(),
    
    'forfeiture': """
    ❗ หลุดจำนำ: {contract_number}

    👤 ลูกค้า: {customer_name}
    💍 สินค้า: {product_name}
    💰 วงเงินกู้: {pawn_amount:,.2f} บาท
    📅 วันสิ้นสุดสัญญา: {end_date}
    ⏰ วันที่หลุด: {timestamp}
    """.strip(),
    
    'daily_income': """
📊 สรุปรายได้รายวัน - {date}

📋 สัญญาใหม่: {new_contracts} สัญญา
🔄 การต่อดอก: {renewals} ครั้ง
💎 การไถ่ถอน: {redemptions} ครั้ง

💰 ดอกเบี้ยรวม: {total_interest:,.2f} บาท
💸 ค่าธรรมเนียมการต่อดอก: {total_renewal_fees:,.2f} บาท
💵 ค่าธรรมเนียมรวม: {total_fees:,.2f} บาท
💎 จำนวนเงินไถ่ถอน: {total_redemption_amount:,.2f} บาท

📈 รายได้สุทธิ: {net_income:,.2f} บาท

⏰ เวลาที่สรุป: {timestamp}
    """.strip()
}
