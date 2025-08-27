#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบสำหรับ pdf2.py
แสดงการใช้งานฟังก์ชันสร้างใบฝากต่อและใบเสร็จการต่อดอก
"""

from pdf2 import generate_renewal_contract_pdf, generate_renewal_receipt_pdf
from datetime import datetime, timedelta


def test_renewal_contract():
    """ทดสอบการสร้างใบฝากต่อ"""
    print("=== ทดสอบการสร้างใบฝากต่อ ===")
    
    # ข้อมูลสัญญาเดิม
    original_contract_data = {
        'contract_number': 'C001-2024',
        'start_date': '2024-01-01',
        'end_date': '2024-04-01',
        'days_count': 90,
        'pawn_amount': 50000.00,
        'interest_rate': 15.00,
        'estimated_value': 75000.00
    }
    
    # ข้อมูลลูกค้า
    customer_data = {
        'customer_code': 'C001',
        'first_name': 'สมชาย',
        'last_name': 'ใจดี',
        'phone': '081-234-5678',
        'id_card': '1234567890123',
        'house_number': '123',
        'street': 'ถนนสุขุมวิท',
        'subdistrict': 'คลองเตย',
        'district': 'คลองเตย',
        'province': 'กรุงเทพมหานคร'
    }
    
    # ข้อมูลสินค้า
    product_data = {
        'name': 'โทรศัพท์มือถือ',
        'brand': 'iPhone',
        'size': '6.1 นิ้ว',
        'weight': '174',
        'weight_unit': 'กรัม',
        'serial_number': 'SN123456789',
        'other_details': 'สีดำ, 128GB'
    }
    
    # ข้อมูลการต่อดอก
    renewal_data = {
        'renewal_date': '2024-03-25',
        'extension_days': 30,
        'interest_amount': 616.44,  # (50000 * 15% * 30) / 365
        'fee_amount': 100.00,
        'total_amount': 716.44
    }
    
    # ข้อมูลร้านค้า
    shop_data = {
        'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    }
    
    try:
        # สร้างใบฝากต่อ
        output_file = generate_renewal_contract_pdf(
            original_contract_data=original_contract_data,
            customer_data=customer_data,
            product_data=product_data,
            renewal_data=renewal_data,
            shop_data=shop_data,
            output_file='test_renewal_contract.pdf'
        )
        
        if output_file:
            print(f"✅ สร้างใบฝากต่อสำเร็จ: {output_file}")
        else:
            print("❌ สร้างใบฝากต่อไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")


def test_renewal_receipt():
    """ทดสอบการสร้างใบเสร็จการต่อดอก"""
    print("\n=== ทดสอบการสร้างใบเสร็จการต่อดอก ===")
    
    # ข้อมูลการต่อดอก
    renewal_data = {
        'renewal_date': '2024-03-25',
        'extension_days': 30,
        'interest_amount': 616.44,
        'fee_amount': 100.00,
        'total_amount': 716.44
    }
    
    # ข้อมูลลูกค้า
    customer_data = {
        'customer_code': 'C001',
        'first_name': 'สมชาย',
        'last_name': 'ใจดี',
        'phone': '081-234-5678',
        'id_card': '1234567890123'
    }
    
    # ข้อมูลสัญญาเดิม
    original_contract_data = {
        'contract_number': 'C001-2024',
        'start_date': '2024-01-01',
        'end_date': '2024-04-01',
        'days_count': 90,
        'pawn_amount': 50000.00
    }
    
    # ข้อมูลร้านค้า
    shop_data = {
        'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    }
    
    try:
        # สร้างใบเสร็จการต่อดอก
        output_file = generate_renewal_receipt_pdf(
            renewal_data=renewal_data,
            customer_data=customer_data,
            original_contract_data=original_contract_data,
            shop_data=shop_data,
            output_file='test_renewal_receipt.pdf'
        )
        
        if output_file:
            print(f"✅ สร้างใบเสร็จการต่อดอกสำเร็จ: {output_file}")
        else:
            print("❌ สร้างใบเสร็จการต่อดอกไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")


def test_with_real_data():
    """ทดสอบกับข้อมูลจริง (ถ้ามี)"""
    print("\n=== ทดสอบกับข้อมูลจริง ===")
    
    # ข้อมูลตัวอย่างที่ใกล้เคียงกับข้อมูลจริง
    original_contract_data = {
        'contract_number': 'PWN-2024-001',
        'start_date': '2024-01-15',
        'end_date': '2024-04-15',
        'days_count': 90,
        'pawn_amount': 25000.00,
        'interest_rate': 18.00,
        'estimated_value': 35000.00
    }
    
    customer_data = {
        'customer_code': 'CUST-001',
        'first_name': 'นางสาว',
        'last_name': 'สมหญิง รักดี',
        'phone': '089-876-5432',
        'id_card': '9876543210987',
        'house_number': '456',
        'street': 'ถนนเพชรบุรี',
        'subdistrict': 'บางกะปิ',
        'district': 'ห้วยขวาง',
        'province': 'กรุงเทพมหานคร'
    }
    
    product_data = {
        'name': 'เครื่องประดับทองคำ',
        'brand': 'ทองคำแท้',
        'size': 'ขนาด 1 บาท',
        'weight': '15.16',
        'weight_unit': 'กรัม',
        'serial_number': 'GOLD-001',
        'other_details': 'ทองคำ 96.5%'
    }
    
    renewal_data = {
        'renewal_date': datetime.now().strftime('%Y-%m-%d'),
        'extension_days': 45,
        'interest_amount': 555.21,  # (25000 * 18% * 45) / 365
        'fee_amount': 150.00,
        'total_amount': 705.21
    }
    
    shop_data = {
        'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    }
    
    try:
        # สร้างใบฝากต่อ
        contract_file = generate_renewal_contract_pdf(
            original_contract_data=original_contract_data,
            customer_data=customer_data,
            product_data=product_data,
            renewal_data=renewal_data,
            shop_data=shop_data,
            output_file='real_renewal_contract.pdf'
        )
        
        # สร้างใบเสร็จการต่อดอก
        receipt_file = generate_renewal_receipt_pdf(
            renewal_data=renewal_data,
            customer_data=customer_data,
            original_contract_data=original_contract_data,
            shop_data=shop_data,
            output_file='real_renewal_receipt.pdf'
        )
        
        if contract_file and receipt_file:
            print(f"✅ สร้างเอกสารสำเร็จ:")
            print(f"   - ใบฝากต่อ: {contract_file}")
            print(f"   - ใบเสร็จ: {receipt_file}")
        else:
            print("❌ สร้างเอกสารไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
    print("🚀 เริ่มทดสอบ PDF2.py")
    print("=" * 50)
    
    # ทดสอบการสร้างใบฝากต่อ
    test_renewal_contract()
    
    # ทดสอบการสร้างใบเสร็จการต่อดอก
    test_renewal_receipt()
    
    # ทดสอบกับข้อมูลจริง
    test_with_real_data()
    
    print("\n" + "=" * 50)
    print("✅ การทดสอบเสร็จสิ้น")
    print("\n📋 สรุปฟังก์ชันที่ใช้งานได้:")
    print("1. generate_renewal_contract_pdf() - สร้างใบฝากต่อ")
    print("2. generate_renewal_receipt_pdf() - สร้างใบเสร็จการต่อดอก")
    print("\n💡 วิธีการใช้งาน:")
    print("- เรียกใช้ฟังก์ชันพร้อมส่งข้อมูลที่จำเป็น")
    print("- ระบบจะสร้างไฟล์ PDF อัตโนมัติ")
    print("- สามารถระบุชื่อไฟล์ output ได้ หรือให้ระบบสร้างชื่ออัตโนมัติ")
