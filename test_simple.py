#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบพรีวิวแบบง่ายๆ (ไม่ใช้ GUI)
"""

import sys
import os
import tempfile

# เพิ่ม path ของโปรเจค
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pdf_generation():
    """ทดสอบการสร้าง PDF"""
    try:
        print("ทดสอบการสร้าง PDF...")
        
        # ข้อมูลตัวอย่าง
        contract_data = {
            'contract_number': 'TEST-001',
            'start_date': '2024-01-15',
            'end_date': '2024-02-15',
            'pawn_amount': 5000.0,
            'total_redemption': 5500.0,
            'interest_rate': 10.0,
            'days_count': 30
        }
        
        customer_data = {
            'first_name': 'สมชาย',
            'last_name': 'ใจดี',
            'id_card': '1234567890123',
            'phone': '0812345678',
            'house_number': '123',
            'street': 'ถนนสุขุมวิท',
            'subdistrict': 'คลองตัน',
            'district': 'วัฒนา',
            'province': 'กรุงเทพฯ',
            'postcode': '10110'
        }
        
        product_data = {
            'name': 'iPhone 15 Pro',
            'brand': 'Apple',
            'model': 'iPhone 15 Pro',
            'color': 'Titanium Blue',
            'serial_number': 'ABC123456789',
            'condition': 'สภาพดี',
            'accessories': 'สายชาร์จและกล่องเดิม'
        }
        
        shop_data = {
            'name': 'ร้านจำนำมือถือ',
            'branch': 'สาขาสุขุมวิท',
            'address': '123 ถนนสุขุมวิท กรุงเทพฯ 10110',
            'phone': '02-123-4567',
            'tax_id': '1234567890123'
        }
        
        # สร้างไฟล์ PDF ชั่วคราว
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        
        print("สร้างไฟล์ PDF ชั่วคราวที่: " + temp_pdf_path)
        
        # ทดสอบการสร้างสัญญาฝากขาย
        try:
            from pdf import generate_pawn_contract_html
            result = generate_pawn_contract_html(
                contract_data=contract_data,
                customer_data=customer_data,
                product_data=product_data,
                shop_data=shop_data,
                output_file=temp_pdf_path
            )
            
            if result and os.path.exists(result):
                print("✓ สร้างสัญญาฝากขายสำเร็จ: " + result)
            else:
                print("✗ สร้างสัญญาฝากขายไม่สำเร็จ")
                
        except Exception as e:
            print("✗ เกิดข้อผิดพลาดในการสร้างสัญญาฝากขาย: " + str(e))
        
        # ทดสอบการสร้างสัญญาไถ่คืน
        try:
            from pdf3 import generate_redemption_contract_pdf
            
            redemption_data = {
                'redemption_date': '2024-01-20',
                'deposit_date': '2024-01-15',
                'due_date': '2024-02-15',
                'total_days': 5,
                'principal_amount': 5000.0,
                'penalty_amount': 0.0,
                'discount_amount': 0.0,
                'redemption_amount': 5000.0
            }
            
            result = generate_redemption_contract_pdf(
                redemption_data=redemption_data,
                customer_data=customer_data,
                product_data=product_data,
                original_contract_data=contract_data,
                shop_data=shop_data,
                output_file=temp_pdf_path
            )
            
            if result and os.path.exists(result):
                print("✓ สร้างสัญญาไถ่คืนสำเร็จ: " + result)
            else:
                print("✗ สร้างสัญญาไถ่คืนไม่สำเร็จ")
                
        except Exception as e:
            print("✗ เกิดข้อผิดพลาดในการสร้างสัญญาไถ่คืน: " + str(e))
        
        # ลบไฟล์ชั่วคราว
        try:
            os.unlink(temp_pdf_path)
            print("ลบไฟล์ชั่วคราวแล้ว")
        except:
            pass
            
    except Exception as e:
        print("เกิดข้อผิดพลาดในการทดสอบ: " + str(e))

if __name__ == "__main__":
    test_pdf_generation()
