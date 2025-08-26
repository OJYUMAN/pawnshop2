#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการโหลดข้อมูลสัญญาและข้อมูลลูกค้า/สินค้า
"""

import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import PawnShopDatabase

def test_contract_loading():
    """ทดสอบการโหลดข้อมูลสัญญา"""
    print("=== ทดสอบการโหลดข้อมูลสัญญา ===")
    
    try:
        db = PawnShopDatabase()
        
        # ทดสอบการค้นหาสัญญา
        print("1. ทดสอบการค้นหาสัญญา...")
        contracts = db.search_contracts_by_number("")
        
        if contracts:
            print(f"   ✓ พบสัญญา {len(contracts)} รายการ")
            
            # เลือกสัญญาแรกมาทดสอบ
            test_contract = contracts[0]
            contract_id = test_contract['id']
            contract_number = test_contract['contract_number']
            
            print(f"   ✓ เลือกสัญญา: {contract_number} (ID: {contract_id})")
            
            # ทดสอบการดึงข้อมูลสัญญาตาม ID
            print("2. ทดสอบการดึงข้อมูลสัญญาตาม ID...")
            contract = db.get_contract_by_id(contract_id)
            
            if contract:
                print(f"   ✓ ดึงข้อมูลสัญญาสำเร็จ")
                print(f"      - เลขที่สัญญา: {contract.get('contract_number', 'N/A')}")
                print(f"      - ยอดฝาก: {contract.get('pawn_amount', 0):,.2f} บาท")
                print(f"      - อัตราดอกเบี้ย: {contract.get('interest_rate', 0):.2f}%")
                print(f"      - วันที่เริ่มต้น: {contract.get('start_date', 'N/A')}")
                print(f"      - วันที่สิ้นสุด: {contract.get('end_date', 'N/A')}")
                
                # ทดสอบการดึงข้อมูลลูกค้า
                print("3. ทดสอบการดึงข้อมูลลูกค้า...")
                customer_id = contract.get('customer_id')
                if customer_id:
                    customer = db.get_customer_by_id(customer_id)
                    if customer:
                        print(f"   ✓ ดึงข้อมูลลูกค้าสำเร็จ")
                        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
                        print(f"      - ชื่อ: {customer_name}")
                        print(f"      - รหัส: {customer.get('customer_code', 'N/A')}")
                        print(f"      - เบอร์โทร: {customer.get('phone', 'N/A')}")
                        print(f"      - บัตรประชาชน: {customer.get('id_card', 'N/A')}")
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
                        print(f"      - ยี่ห้อ: {product.get('brand', 'N/A')}")
                        print(f"      - ขนาด: {product.get('size', 'N/A')}")
                        print(f"      - น้ำหนัก: {product.get('weight', 'N/A')} กรัม")
                        print(f"      - หมายเลขซีเรียล: {product.get('serial_number', 'N/A')}")
                    else:
                        print("   ✗ ไม่สามารถดึงข้อมูลสินค้าได้")
                else:
                    print("   ⚠ ไม่มี product_id ในสัญญา")
                
                # ทดสอบการดึงข้อมูลการต่อดอก
                print("5. ทดสอบการดึงข้อมูลการต่อดอก...")
                renewals = db.get_renewals_by_contract(contract_id)
                if renewals:
                    print(f"   ✓ พบข้อมูลการต่อดอก {len(renewals)} รายการ")
                    for renewal in renewals:
                        print(f"      - ครั้งที่ {renewal['renewal_count']}: {renewal['total_amount']:.2f} บาท")
                else:
                    print("   ⚠ ไม่มีข้อมูลการต่อดอก")
                
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

def test_database_structure():
    """ทดสอบโครงสร้างฐานข้อมูล"""
    print("\n=== ทดสอบโครงสร้างฐานข้อมูล ===")
    
    try:
        db = PawnShopDatabase()
        
        # ทดสอบการดึงข้อมูลจากตารางต่างๆ
        print("1. ทดสอบตาราง contracts...")
        contracts = db.get_all_contracts()
        print(f"   ✓ พบสัญญา {len(contracts)} รายการ")
        
        print("2. ทดสอบตาราง customers...")
        customers = db.get_all_customers()
        print(f"   ✓ พบลูกค้า {len(customers)} รายการ")
        
        print("3. ทดสอบตาราง products...")
        products = db.get_all_products()
        print(f"   ✓ พบสินค้า {len(products)} รายการ")
        
        print("4. ทดสอบตาราง renewals...")
        renewals = db.get_all_renewals()
        print(f"   ✓ พบข้อมูลการต่อดอก {len(renewals)} รายการ")
        
        # ตรวจสอบความสัมพันธ์ระหว่างตาราง
        print("5. ตรวจสอบความสัมพันธ์ระหว่างตาราง...")
        if contracts and customers and products:
            contract = contracts[0]
            customer_id = contract.get('customer_id')
            product_id = contract.get('product_id')
            
            if customer_id and product_id:
                customer = db.get_customer_by_id(customer_id)
                product = db.get_product_by_id(product_id)
                
                if customer and product:
                    print("   ✓ ความสัมพันธ์ระหว่างตารางถูกต้อง")
                    print(f"      - สัญญา {contract['contract_number']} เกี่ยวข้องกับ:")
                    print(f"        * ลูกค้า: {customer['customer_code']}")
                    print(f"        * สินค้า: {product['name']}")
                else:
                    print("   ⚠ ความสัมพันธ์ระหว่างตารางไม่ถูกต้อง")
            else:
                print("   ⚠ สัญญาไม่มี customer_id หรือ product_id")
        else:
            print("   ⚠ ไม่มีข้อมูลเพียงพอในการตรวจสอบ")
        
        print("\n=== การทดสอบเสร็จสิ้น ===")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("เริ่มต้นการทดสอบการโหลดข้อมูลสัญญา...")
    
    # ทดสอบการโหลดข้อมูลสัญญา
    test_contract_loading()
    
    # ทดสอบโครงสร้างฐานข้อมูล
    test_database_structure()
    
    print("\nการทดสอบเสร็จสิ้น")
