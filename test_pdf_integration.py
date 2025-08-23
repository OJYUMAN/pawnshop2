#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการทำงานของระบบ PDF ที่เชื่อมต่อกับระบบหลัก
"""

import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_generation():
    """ทดสอบการสร้าง PDF จากข้อมูลจริง"""
    try:
        from pdf import generate_pawn_ticket_from_data
        
        print("=== ทดสอบการสร้าง PDF จากข้อมูลจริง ===")
        
        # สร้างข้อมูลทดสอบ
        contract_data = {
            'contract_number': 'CN-2024-001',
            'start_date': '2024-01-15',
            'end_date': '2024-02-15',
            'days_count': 30,
            'pawn_amount': 5000.00,
            'interest_rate': 15.0,
            'fee_amount': 100.00,
            'withholding_tax_rate': 3.0,
            'withholding_tax_amount': 75.00,
            'total_paid': 4925.00,
            'total_redemption': 5175.00
        }
        
        customer_data = {
            'first_name': 'สมชาย',
            'last_name': 'ใจดี',
            'id_card': '1234567890123',
            'phone': '0812345678',
            'house_number': '123',
            'street': 'ถนนสุขุมวิท',
            'subdistrict': 'คลองเตย',
            'district': 'คลองเตย',
            'province': 'กรุงเทพมหานคร'
        }
        
        product_data = {
            'name': 'iPhone 14',
            'brand': 'Apple',
            'size': '6.1 inch',
            'weight': 172.0,
            'weight_unit': 'g',
            'serial_number': 'ABC123456789',
            'other_details': 'สีน้ำเงิน 128GB'
        }
        
        print("ข้อมูลสัญญา:", contract_data)
        print("ข้อมูลลูกค้า:", customer_data)
        print("ข้อมูลสินค้า:", product_data)
        
        # สร้าง PDF
        output_file = "test_pawn_ticket_real.pdf"
        result = generate_pawn_ticket_from_data(
            contract_data=contract_data,
            customer_data=customer_data,
            product_data=product_data,
            output_file=output_file
        )
        
        if result:
            print(f"[SUCCESS] สร้าง PDF สำเร็จ: {result}")
            
            # ตรวจสอบว่าไฟล์ถูกสร้างขึ้นหรือไม่
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"[FILE] ไฟล์ถูกสร้างขึ้น: {result}")
                print(f"[SIZE] ขนาดไฟล์: {file_size:,} bytes")
            else:
                print("[ERROR] ไฟล์ไม่ถูกสร้างขึ้น")
        else:
            print("[ERROR] ไม่สามารถสร้าง PDF ได้")
            
    except ImportError as e:
        print(f"[ERROR] ไม่สามารถ import pdf.py ได้: {e}")
    except Exception as e:
        print(f"[ERROR] เกิดข้อผิดพลาด: {e}")

def test_pdf_generation_with_current_date():
    """ทดสอบการสร้าง PDF ด้วยวันที่ปัจจุบัน"""
    try:
        from pdf import generate_pawn_ticket_from_data
        
        print("\n=== ทดสอบการสร้าง PDF ด้วยวันที่ปัจจุบัน ===")
        
        today = datetime.now()
        end_date = today + timedelta(days=30)
        
        contract_data = {
            'contract_number': f'CN-{today.strftime("%Y%m%d")}-001',
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days_count': 30,
            'pawn_amount': 10000.00,
            'interest_rate': 12.0,
            'fee_amount': 200.00,
            'withholding_tax_rate': 3.0,
            'withholding_tax_amount': 150.00,
            'total_paid': 9850.00,
            'total_redemption': 10350.00
        }
        
        customer_data = {
            'first_name': 'สมหญิง',
            'last_name': 'รักดี',
            'id_card': '9876543210987',
            'phone': '0898765432',
            'house_number': '456',
            'street': 'ถนนรัชดาภิเษก',
            'subdistrict': 'ดินแดง',
            'district': 'ดินแดง',
            'province': 'กรุงเทพมหานคร'
        }
        
        product_data = {
            'name': 'Samsung Galaxy S23',
            'brand': 'Samsung',
            'size': '6.1 inch',
            'weight': 168.0,
            'weight_unit': 'g',
            'serial_number': 'XYZ987654321',
            'other_details': 'สีดำ 256GB'
        }
        
        print("ข้อมูลสัญญา:", contract_data)
        print("ข้อมูลลูกค้า:", customer_data)
        print("ข้อมูลสินค้า:", product_data)
        
        # สร้าง PDF
        output_file = f"test_pawn_ticket_{today.strftime('%Y%m%d_%H%M%S')}.pdf"
        result = generate_pawn_ticket_from_data(
            contract_data=contract_data,
            customer_data=customer_data,
            product_data=product_data,
            output_file=output_file
        )
        
        if result:
            print(f"[SUCCESS] สร้าง PDF สำเร็จ: {result}")
            
            # ตรวจสอบว่าไฟล์ถูกสร้างขึ้นหรือไม่
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"[FILE] ไฟล์ถูกสร้างขึ้น: {result}")
                print(f"[SIZE] ขนาดไฟล์: {file_size:,} bytes")
            else:
                print("[ERROR] ไฟล์ไม่ถูกสร้างขึ้น")
        else:
            print("[ERROR] ไม่สามารถสร้าง PDF ได้")
            
    except ImportError as e:
        print(f"[ERROR] ไม่สามารถ import pdf.py ได้: {e}")
    except Exception as e:
        print(f"[ERROR] เกิดข้อผิดพลาด: {e}")

def test_font_files():
    """ทดสอบการตรวจสอบไฟล์ฟอนต์"""
    print("\n=== ทดสอบการตรวจสอบไฟล์ฟอนต์ ===")
    
    font_files = ['THSarabun.ttf', 'THSarabun Bold.ttf']
    
    for font_file in font_files:
        if os.path.exists(font_file):
            file_size = os.path.getsize(font_file)
            print(f"[OK] {font_file}: พบ (ขนาด: {file_size:,} bytes)")
        else:
            print(f"[MISSING] {font_file}: ไม่พบ")

def main():
    """ฟังก์ชันหลักสำหรับการทดสอบ"""
    print("[START] เริ่มทดสอบระบบ PDF ที่เชื่อมต่อกับระบบหลัก")
    print("=" * 60)
    
    # ทดสอบไฟล์ฟอนต์
    test_font_files()
    
    # ทดสอบการสร้าง PDF
    test_pdf_generation()
    test_pdf_generation_with_current_date()
    
    print("\n" + "=" * 60)
    print("[END] เสร็จสิ้นการทดสอบ")

if __name__ == "__main__":
    main()
