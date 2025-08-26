#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกที่ละเอียดมากขึ้น
"""

import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf import generate_pawn_ticket_from_data

def test_enhanced_pdf_with_renewal():
    """ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกที่ละเอียดมากขึ้น"""
    print("=== ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกที่ละเอียดมากขึ้น ===")
    
    # สร้างข้อมูลทดสอบ
    test_contract_data = {
        'contract_number': 'CN0001',
        'start_date': '2024-01-01',
        'end_date': '01/02/2024',
        'days_count': 30,
        'pawn_amount': 10000.0,
        'interest_rate': 2.5,
        'fee_amount': 100.0,
        'withholding_tax_rate': 3.0,
        'withholding_tax_amount': 7.5,
        'total_paid': 9992.5,
        'total_redemption': 10107.5
    }
    
    test_customer_data = {
        'customer_code': 'C0001',
        'first_name': 'ทดสอบ',
        'last_name': 'ระบบ',
        'id_card': '1234567890123',
        'phone': '0812345678',
        'house_number': '123',
        'street': 'ถนนทดสอบ',
        'subdistrict': 'ตำบลทดสอบ',
        'district': 'อำเภอทดสอบ',
        'province': 'จังหวัดทดสอบ'
    }
    
    test_product_data = {
        'name': 'ทองคำ',
        'brand': 'ทองคำแท้',
        'size': '1 บาท',
        'weight': 15.16,
        'weight_unit': 'กรัม',
        'serial_number': 'SN001'
    }
    
    # ข้อมูลการต่อดอกที่ละเอียดมากขึ้น
    test_renewal_data = [
        {
            'renewal_count': 1,
            'renewal_date': '2024-02-01',
            'extension_days': 30,
            'fee_amount': 50.0,
            'penalty_amount': 0.0,
            'discount_amount': 0.0,
            'total_amount': 50.0,
            'current_due_date': '2024-02-01',
            'new_due_date': '2024-03-01'
        },
        {
            'renewal_count': 2,
            'renewal_date': '2024-03-01',
            'extension_days': 30,
            'fee_amount': 50.0,
            'penalty_amount': 25.0,  # ค่าปรับ
            'discount_amount': 10.0,  # ส่วนลด
            'total_amount': 65.0,
            'current_due_date': '2024-03-01',
            'new_due_date': '2024-04-01'
        },
        {
            'renewal_count': 3,
            'renewal_date': '2024-04-01',
            'extension_days': 45,  # ต่อดอกนานขึ้น
            'fee_amount': 75.0,  # ค่าธรรมเนียมมากขึ้น
            'penalty_amount': 0.0,
            'discount_amount': 0.0,
            'total_amount': 75.0,
            'current_due_date': '2024-04-01',
            'new_due_date': '2024-05-16'
        }
    ]
    
    test_shop_data = {
        'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    }
    
    try:
        # ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกที่ละเอียด
        print("1. ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกที่ละเอียด...")
        
        output_file = "test_enhanced_pawn_ticket_with_renewal.pdf"
        result = generate_pawn_ticket_from_data(
            contract_data=test_contract_data,
            customer_data=test_customer_data,
            product_data=test_product_data,
            shop_data=test_shop_data,
            output_file=output_file,
            renewal_data=test_renewal_data
        )
        
        if result:
            print(f"   ✓ สร้าง PDF สำเร็จ: {result}")
            
            # ตรวจสอบว่าไฟล์ถูกสร้างขึ้น
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   ✓ ไฟล์ PDF มีขนาด: {file_size:,} bytes")
                
                # แสดงสรุปข้อมูลการต่อดอก
                total_fees = sum(renewal['total_amount'] for renewal in test_renewal_data)
                total_days = sum(renewal['extension_days'] for renewal in test_renewal_data)
                print(f"   ✓ สรุปข้อมูลการต่อดอก:")
                print(f"      - จำนวนครั้ง: {len(test_renewal_data)} ครั้ง")
                print(f"      - จำนวนวันรวม: {total_days} วัน")
                print(f"      - ค่าธรรมเนียมรวม: {total_fees:,.2f} บาท")
                
                # แสดงรายละเอียดแต่ละครั้ง
                for i, renewal in enumerate(test_renewal_data, 1):
                    print(f"      - ครั้งที่ {i}: {renewal['extension_days']} วัน, {renewal['total_amount']:,.2f} บาท")
            else:
                print("   ✗ ไม่พบไฟล์ PDF ที่สร้างขึ้น")
        else:
            print("   ✗ ไม่สามารถสร้าง PDF ได้")
        
        # ทดสอบการสร้าง PDF โดยไม่มีข้อมูลการต่อดอก
        print("\n2. ทดสอบการสร้าง PDF โดยไม่มีข้อมูลการต่อดอก...")
        
        output_file_no_renewal = "test_enhanced_pawn_ticket_no_renewal.pdf"
        result_no_renewal = generate_pawn_ticket_from_data(
            contract_data=test_contract_data,
            customer_data=test_customer_data,
            product_data=test_product_data,
            shop_data=test_shop_data,
            output_file=output_file_no_renewal
        )
        
        if result_no_renewal:
            print(f"   ✓ สร้าง PDF สำเร็จ: {result_no_renewal}")
        else:
            print("   ✗ ไม่สามารถสร้าง PDF ได้")
        
        print("\n=== การทดสอบเสร็จสิ้น ===")
        
        # ลบไฟล์ทดสอบ
        for test_file in [output_file, output_file_no_renewal]:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"ลบไฟล์ทดสอบ: {test_file}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}")
        import traceback
        traceback.print_exc()

def test_pdf_with_single_renewal():
    """ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกครั้งเดียว"""
    print("\n=== ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกครั้งเดียว ===")
    
    # สร้างข้อมูลทดสอบ
    test_contract_data = {
        'contract_number': 'CN0002',
        'start_date': '2024-01-01',
        'end_date': '01/02/2024',
        'days_count': 30,
        'pawn_amount': 5000.0,
        'interest_rate': 2.0,
        'fee_amount': 50.0,
        'withholding_tax_rate': 3.0,
        'withholding_tax_amount': 3.0,
        'total_paid': 4997.0,
        'total_redemption': 5053.0
    }
    
    test_customer_data = {
        'customer_code': 'C0002',
        'first_name': 'ทดสอบ',
        'last_name': 'ครั้งเดียว',
        'id_card': '9876543210987',
        'phone': '0898765432',
        'house_number': '456',
        'street': 'ถนนทดสอบครั้งเดียว',
        'subdistrict': 'ตำบลทดสอบครั้งเดียว',
        'district': 'อำเภอทดสอบครั้งเดียว',
        'province': 'จังหวัดทดสอบครั้งเดียว'
    }
    
    test_product_data = {
        'name': 'เครื่องประดับ',
        'brand': 'ทองคำแท้',
        'size': 'ขนาดกลาง',
        'weight': 8.5,
        'weight_unit': 'กรัม',
        'serial_number': 'SN002'
    }
    
    # ข้อมูลการต่อดอกครั้งเดียว
    test_renewal_data = [
        {
            'renewal_count': 1,
            'renewal_date': '2024-02-01',
            'extension_days': 60,  # ต่อดอกนานขึ้น
            'fee_amount': 100.0,
            'penalty_amount': 0.0,
            'discount_amount': 0.0,
            'total_amount': 100.0,
            'current_due_date': '2024-02-01',
            'new_due_date': '2024-04-01'
        }
    ]
    
    test_shop_data = {
        'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    }
    
    try:
        output_file = "test_single_renewal_pawn_ticket.pdf"
        result = generate_pawn_ticket_from_data(
            contract_data=test_contract_data,
            customer_data=test_customer_data,
            product_data=test_product_data,
            shop_data=test_shop_data,
            output_file=output_file,
            renewal_data=test_renewal_data
        )
        
        if result:
            print(f"   ✓ สร้าง PDF สำเร็จ: {result}")
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   ✓ ไฟล์ PDF มีขนาด: {file_size:,} bytes")
                
                # แสดงสรุปข้อมูลการต่อดอก
                renewal = test_renewal_data[0]
                print(f"   ✓ สรุปข้อมูลการต่อดอก:")
                print(f"      - จำนวนครั้ง: 1 ครั้ง")
                print(f"      - จำนวนวัน: {renewal['extension_days']} วัน")
                print(f"      - ค่าธรรมเนียม: {renewal['total_amount']:,.2f} บาท")
                print(f"      - วันครบกำหนดใหม่: {renewal['new_due_date']}")
            else:
                print("   ✗ ไม่พบไฟล์ PDF ที่สร้างขึ้น")
        else:
            print("   ✗ ไม่สามารถสร้าง PDF ได้")
        
        # ลบไฟล์ทดสอบ
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"ลบไฟล์ทดสอบ: {output_file}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("เริ่มต้นการทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกที่ละเอียดมากขึ้น...")
    
    # ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกหลายครั้ง
    test_enhanced_pdf_with_renewal()
    
    # ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอกครั้งเดียว
    test_pdf_with_single_renewal()
    
    print("\nการทดสอบเสร็จสิ้น")
