#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการรวมข้อมูลการต่อดอกในระบบ
"""

import sys
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QDate

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from contract_form import NewContractDialog
from database import PawnShopDatabase
from pdf import generate_pawn_ticket_from_data

def test_renewal_integration():
    """ทดสอบการรวมข้อมูลการต่อดอก"""
    print("=== ทดสอบการรวมข้อมูลการต่อดอก ===")
    
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
    
    test_renewal_data = [
        {
            'renewal_date': '2024-02-01',
            'renewal_days': 30,
            'renewal_rate': 2.5
        },
        {
            'renewal_date': '2024-03-01',
            'renewal_days': 30,
            'renewal_rate': 2.5
        }
    ]
    
    test_shop_data = {
        'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    }
    
    try:
        # ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอก
        print("1. ทดสอบการสร้าง PDF พร้อมข้อมูลการต่อดอก...")
        
        output_file = "test_pawn_ticket_with_renewal.pdf"
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
            else:
                print("   ✗ ไม่พบไฟล์ PDF ที่สร้างขึ้น")
        else:
            print("   ✗ ไม่สามารถสร้าง PDF ได้")
        
        # ทดสอบการสร้าง PDF โดยไม่มีข้อมูลการต่อดอก
        print("\n2. ทดสอบการสร้าง PDF โดยไม่มีข้อมูลการต่อดอก...")
        
        output_file_no_renewal = "test_pawn_ticket_no_renewal.pdf"
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

def test_database_renewal():
    """ทดสอบฐานข้อมูลการต่อดอก"""
    print("\n=== ทดสอบฐานข้อมูลการต่อดอก ===")
    
    try:
        db = PawnShopDatabase()
        
        # ทดสอบการสร้างสัญญา
        print("1. ทดสอบการสร้างสัญญา...")
        contract_data = {
            'contract_number': 'TEST001',
            'customer_id': 1,
            'product_id': 1,
            'pawn_amount': 5000.0,
            'interest_rate': 2.0,
            'fee_amount': 50.0,
            'withholding_tax_rate': 3.0,
            'withholding_tax_amount': 3.0,
            'total_paid': 4997.0,
            'total_redemption': 5053.0,
            'start_date': '2024-01-01',
            'end_date': '01/02/2024',
            'days_count': 30
        }
        
        # ตรวจสอบว่ามีลูกค้าและสินค้าในฐานข้อมูลหรือไม่
        customers = db.search_customers("")
        products = db.search_products("")
        
        if customers and products:
            contract_data['customer_id'] = customers[0]['id']
            contract_data['product_id'] = products[0]['id']
            
            contract_id = db.create_contract(contract_data)
            print(f"   ✓ สร้างสัญญาสำเร็จ ID: {contract_id}")
            
            # ทดสอบการเพิ่มข้อมูลการต่อดอก
            print("2. ทดสอบการเพิ่มข้อมูลการต่อดอก...")
            renewal_data = {
                'contract_id': contract_id,
                'contract_number': contract_data['contract_number'],
                'renewal_count': 1,
                'fee_amount': 25.0,
                'penalty_amount': 0.0,
                'discount_amount': 0.0,
                'total_amount': 25.0,
                'renewal_date': '2024-02-01',
                'current_due_date': '2024-02-01',
                'new_due_date': '2024-03-01',
                'extension_days': 30
            }
            
            renewal_id = db.add_renewal(renewal_data)
            print(f"   ✓ เพิ่มข้อมูลการต่อดอกสำเร็จ ID: {renewal_id}")
            
            # ทดสอบการดึงข้อมูลการต่อดอก
            print("3. ทดสอบการดึงข้อมูลการต่อดอก...")
            renewals = db.get_renewals_by_contract(contract_id)
            print(f"   ✓ พบข้อมูลการต่อดอก {len(renewals)} รายการ")
            
            for renewal in renewals:
                print(f"      - ครั้งที่ {renewal['renewal_count']}: {renewal['total_amount']:.2f} บาท")
            
            # ลบข้อมูลทดสอบ
            print("4. ลบข้อมูลทดสอบ...")
            db.delete_contract(contract_id)
            print("   ✓ ลบข้อมูลทดสอบเรียบร้อย")
            
        else:
            print("   ⚠ ไม่มีข้อมูลลูกค้าหรือสินค้าในฐานข้อมูล")
            print("   กรุณาเพิ่มข้อมูลลูกค้าและสินค้าก่อนทดสอบ")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทดสอบฐานข้อมูล: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("เริ่มต้นการทดสอบการรวมข้อมูลการต่อดอก...")
    
    # ทดสอบการสร้าง PDF
    test_renewal_integration()
    
    # ทดสอบฐานข้อมูล
    test_database_renewal()
    
    print("\nการทดสอบเสร็จสิ้น")
