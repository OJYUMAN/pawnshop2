#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการทำงานของระบบ PDF ที่ปรับปรุงแล้วให้ดึงข้อมูลทั้งหมดจากสัญญา
"""

import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_pdf_generation():
    """ทดสอบการสร้าง PDF ที่ปรับปรุงแล้ว"""
    try:
        from pdf import generate_pawn_ticket_from_data
        
        print("=== ทดสอบการสร้าง PDF ที่ปรับปรุงแล้ว ===")
        
        # สร้างข้อมูลทดสอบที่ครบถ้วน
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
            'total_redemption': 5175.00,
            'status': 'active',
            'estimated_value': 6000.00
        }
        
        customer_data = {
            'customer_code': 'C001',
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
        
        shop_data = {
            'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
            'branch': 'สาขาหล่มสัก',
            'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
        }
        
        print("ข้อมูลสัญญา:", contract_data)
        print("ข้อมูลลูกค้า:", customer_data)
        print("ข้อมูลสินค้า:", product_data)
        print("ข้อมูลร้านค้า:", shop_data)
        
        # สร้าง PDF
        output_file = "test_enhanced_pawn_ticket.pdf"
        result = generate_pawn_ticket_from_data(
            contract_data=contract_data,
            customer_data=customer_data,
            product_data=product_data,
            shop_data=shop_data,
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

def test_enhanced_pdf_with_current_date():
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
            'total_redemption': 10350.00,
            'status': 'active',
            'estimated_value': 12000.00
        }
        
        customer_data = {
            'customer_code': 'C002',
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
        
        shop_data = {
            'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
            'branch': 'สาขาหล่มสัก',
            'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
        }
        
        print("ข้อมูลสัญญา:", contract_data)
        print("ข้อมูลลูกค้า:", customer_data)
        print("ข้อมูลสินค้า:", product_data)
        print("ข้อมูลร้านค้า:", shop_data)
        
        # สร้าง PDF
        output_file = f"test_enhanced_pawn_ticket_{today.strftime('%Y%m%d_%H%M%S')}.pdf"
        result = generate_pawn_ticket_from_data(
            contract_data=contract_data,
            customer_data=customer_data,
            product_data=product_data,
            shop_data=shop_data,
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

def test_pdf_without_shop_data():
    """ทดสอบการสร้าง PDF โดยไม่ระบุข้อมูลร้านค้า"""
    try:
        from pdf import generate_pawn_ticket_from_data
        
        print("\n=== ทดสอบการสร้าง PDF โดยไม่ระบุข้อมูลร้านค้า ===")
        
        contract_data = {
            'contract_number': 'CN-2024-002',
            'start_date': '2024-01-20',
            'end_date': '2024-02-20',
            'days_count': 30,
            'pawn_amount': 3000.00,
            'interest_rate': 10.0,
            'fee_amount': 50.00,
            'withholding_tax_rate': 0.0,
            'withholding_tax_amount': 0.00,
            'total_paid': 3000.00,
            'total_redemption': 3050.00,
            'status': 'active',
            'estimated_value': 3500.00
        }
        
        customer_data = {
            'customer_code': 'C003',
            'first_name': 'สมศักดิ์',
            'last_name': 'มั่งมี',
            'id_card': '1112223334445',
            'phone': '0876543210',
            'house_number': '789',
            'street': 'ถนนลาดพร้าว',
            'subdistrict': 'ลาดพร้าว',
            'district': 'วังทองหลาง',
            'province': 'กรุงเทพมหานคร'
        }
        
        product_data = {
            'name': 'MacBook Air',
            'brand': 'Apple',
            'size': '13.6 inch',
            'weight': 1.24,
            'weight_unit': 'kg',
            'serial_number': 'MAC123456789',
            'other_details': 'สีเงิน M2 Chip 8GB RAM 256GB SSD'
        }
        
        print("ข้อมูลสัญญา:", contract_data)
        print("ข้อมูลลูกค้า:", customer_data)
        print("ข้อมูลสินค้า:", product_data)
        print("ข้อมูลร้านค้า: ไม่ระบุ (ใช้ข้อมูลเริ่มต้น)")
        
        # สร้าง PDF โดยไม่ระบุ shop_data
        output_file = "test_pawn_ticket_default_shop.pdf"
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

def main():
    """ฟังก์ชันหลักสำหรับการทดสอบ"""
    print("[START] เริ่มทดสอบระบบ PDF ที่ปรับปรุงแล้ว")
    print("=" * 60)
    
    # ทดสอบการสร้าง PDF ที่ปรับปรุงแล้ว
    test_enhanced_pdf_generation()
    test_enhanced_pdf_with_current_date()
    test_pdf_without_shop_data()
    
    print("\n" + "=" * 60)
    print("[END] เสร็จสิ้นการทดสอบ")

if __name__ == "__main__":
    main()
