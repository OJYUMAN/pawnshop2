#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการอัพเดทสัญญาและการแก้ไขปัญหา UNIQUE constraint
"""

import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import PawnShopDatabase

def test_contract_update():
    """ทดสอบการอัพเดทสัญญา"""
    print("=== ทดสอบการอัพเดทสัญญา ===")
    
    try:
        db = PawnShopDatabase()
        
        # ทดสอบการสร้างสัญญาใหม่
        print("1. ทดสอบการสร้างสัญญาใหม่...")
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
            
            # ทดสอบการอัพเดทสัญญา
            print("2. ทดสอบการอัพเดทสัญญา...")
            updated_contract_data = contract_data.copy()
            updated_contract_data['id'] = contract_id
            updated_contract_data['pawn_amount'] = 6000.0  # เปลี่ยนยอดฝาก
            updated_contract_data['interest_rate'] = 2.5    # เปลี่ยนอัตราดอกเบี้ย
            
            updated_id = db.update_contract(updated_contract_data)
            print(f"   ✓ อัพเดทสัญญาสำเร็จ ID: {updated_id}")
            
            # ตรวจสอบข้อมูลที่อัพเดท
            print("3. ตรวจสอบข้อมูลที่อัพเดท...")
            updated_contract = db.get_contract_by_id(contract_id)
            if updated_contract:
                print(f"   ✓ ยอดฝากที่อัพเดท: {updated_contract['pawn_amount']:,.2f} บาท")
                print(f"   ✓ อัตราดอกเบี้ยที่อัพเดท: {updated_contract['interest_rate']:.2f}%")
                
                # ตรวจสอบว่าข้อมูลถูกอัพเดทจริงหรือไม่
                if updated_contract['pawn_amount'] == 6000.0 and updated_contract['interest_rate'] == 2.5:
                    print("   ✓ ข้อมูลถูกอัพเดทถูกต้อง")
                else:
                    print("   ✗ ข้อมูลไม่ถูกอัพเดท")
            else:
                print("   ✗ ไม่สามารถดึงข้อมูลสัญญาที่อัพเดทได้")
            
            # ทดสอบการสร้างสัญญาใหม่ด้วยเลขที่สัญญาเดิม (ควรจะล้มเหลว)
            print("4. ทดสอบการสร้างสัญญาใหม่ด้วยเลขที่สัญญาเดิม...")
            try:
                duplicate_contract_data = contract_data.copy()
                duplicate_contract_data['pawn_amount'] = 7000.0  # เปลี่ยนยอดฝาก
                
                duplicate_id = db.create_contract(duplicate_contract_data)
                print("   ✗ ควรจะเกิดข้อผิดพลาด UNIQUE constraint")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print("   ✓ เกิดข้อผิดพลาด UNIQUE constraint ตามที่คาดหวัง")
                else:
                    print(f"   ⚠ เกิดข้อผิดพลาดอื่น: {str(e)}")
            
            # ลบข้อมูลทดสอบ
            print("5. ลบข้อมูลทดสอบ...")
            # ตรวจสอบว่ามีฟังก์ชัน delete_contract หรือไม่
            if hasattr(db, 'delete_contract'):
                db.delete_contract(contract_id)
                print("   ✓ ลบข้อมูลทดสอบเรียบร้อย")
            else:
                print("   ⚠ ไม่มีฟังก์ชัน delete_contract")
            
        else:
            print("   ⚠ ไม่มีข้อมูลลูกค้าหรือสินค้าในฐานข้อมูล")
            print("   กรุณาเพิ่มข้อมูลลูกค้าและสินค้าก่อนทดสอบ")
        
        print("\n=== การทดสอบเสร็จสิ้น ===")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}")
        import traceback
        traceback.print_exc()

def test_contract_loading():
    """ทดสอบการโหลดสัญญาเดิม"""
    print("\n=== ทดสอบการโหลดสัญญาเดิม ===")
    
    try:
        db = PawnShopDatabase()
        
        # ทดสอบการค้นหาสัญญา
        print("1. ทดสอบการค้นหาสัญญา...")
        contracts = db.search_contracts_by_number("")
        
        if contracts:
            print(f"   ✓ พบสัญญา {len(contracts)} รายการ")
            
            # เลือกสัญญาแรกมาทดสอบ
            test_contract = contracts[0]
            contract_number = test_contract['contract_number']
            
            print(f"   ✓ เลือกสัญญา: {contract_number}")
            
            # ทดสอบการดึงข้อมูลสัญญาตามเลขที่สัญญา
            print("2. ทดสอบการดึงข้อมูลสัญญาตามเลขที่สัญญา...")
            contract = db.get_contract_by_number(contract_number)
            
            if contract:
                print(f"   ✓ ดึงข้อมูลสัญญาสำเร็จ")
                print(f"      - เลขที่สัญญา: {contract.get('contract_number', 'N/A')}")
                print(f"      - ยอดฝาก: {contract.get('pawn_amount', 0):,.2f} บาท")
                print(f"      - อัตราดอกเบี้ย: {contract.get('interest_rate', 0):.2f}%")
                
                # ทดสอบการดึงข้อมูลลูกค้า
                print("3. ทดสอบการดึงข้อมูลลูกค้า...")
                customer_id = contract.get('customer_id')
                if customer_id:
                    customer = db.get_customer_by_id(customer_id)
                    if customer:
                        print(f"   ✓ ดึงข้อมูลลูกค้าสำเร็จ")
                        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
                        print(f"      - ชื่อ: {customer_name}")
                    else:
                        print("   ✗ ไม่สามารถดึงข้อมูลลูกค้าได้")
                else:
                    print("   ⚠ ไม่มี customer_id ในสัญญา")
                
                # ทดสอบการดึงข้อมูลสินค้า
                print("4. ทดสอบการดึงข้อมูลสินค้า...")
                product_id = contract.get('product_id')
                if product_id:
                    product = db.get_product_by_id(product_id)
                    if product:
                        print(f"   ✓ ดึงข้อมูลสินค้าสำเร็จ")
                        print(f"      - ชื่อ: {product.get('name', 'N/A')}")
                    else:
                        print("   ✗ ไม่สามารถดึงข้อมูลสินค้าได้")
                else:
                    print("   ⚠ ไม่มี product_id ในสัญญา")
                
            else:
                print("   ✗ ไม่สามารถดึงข้อมูลสัญญาได้")
            
        else:
            print("   ⚠ ไม่พบสัญญาในฐานข้อมูล")
            print("   กรุณาเพิ่มสัญญาก่อนทดสอบ")
        
        print("\n=== การทดสอบเสร็จสิ้น ===")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("เริ่มต้นการทดสอบการอัพเดทสัญญา...")
    
    # ทดสอบการอัพเดทสัญญา
    test_contract_update()
    
    # ทดสอบการโหลดสัญญาเดิม
    test_contract_loading()
    
    print("\nการทดสอบเสร็จสิ้น")
