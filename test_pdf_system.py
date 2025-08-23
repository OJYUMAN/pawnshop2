# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบระบบสร้างใบขายฝาก PDF
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from contract_pdf_generator import ContractPDFGenerator
from database import PawnShopDatabase

def test_pdf_generator():
    """ทดสอบการสร้าง PDF Generator"""
    try:
        print("🧪 ทดสอบการสร้าง PDF Generator...")
        generator = ContractPDFGenerator()
        print("✅ สร้าง PDF Generator สำเร็จ")
        return generator
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

def test_database_connection():
    """ทดสอบการเชื่อมต่อฐานข้อมูล"""
    try:
        print("🧪 ทดสอบการเชื่อมต่อฐานข้อมูล...")
        db = PawnShopDatabase()
        print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ")
        return db
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

def test_get_contracts(db):
    """ทดสอบการดึงข้อมูลสัญญา"""
    try:
        print("🧪 ทดสอบการดึงข้อมูลสัญญา...")
        contracts = db.get_all_contracts()
        print(f"✅ พบสัญญา {len(contracts)} รายการ")
        
        if contracts:
            print("📋 สัญญาล่าสุด:")
            for i, contract in enumerate(contracts[:3]):  # แสดง 3 รายการแรก
                print(f"  {i+1}. {contract.get('contract_number', 'N/A')} - {contract.get('first_name', '')} {contract.get('last_name', '')}")
        
        return contracts
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return []

def test_generate_pdf_from_contract(generator, contract):
    """ทดสอบการสร้าง PDF จากสัญญา"""
    try:
        print(f"🧪 ทดสอบการสร้าง PDF จากสัญญา {contract.get('contract_number', 'N/A')}...")
        
        # ดึงข้อมูลลูกค้าและสินค้า
        db = PawnShopDatabase()
        customer_data = db.get_customer_by_id(contract['customer_id'])
        product_data = db.get_product_by_id(contract['product_id'])
        
        if not customer_data or not product_data:
            print("❌ ไม่พบข้อมูลลูกค้าหรือสินค้า")
            return False
        
        # สร้าง PDF
        output_path = f"test_contract_{contract['contract_number']}.pdf"
        result_path = generator.generate_pdf_from_data(
            contract, customer_data, product_data, output_path
        )
        
        if result_path and os.path.exists(result_path):
            print(f"✅ สร้าง PDF สำเร็จ: {result_path}")
            print(f"📁 ขนาดไฟล์: {os.path.getsize(result_path)} bytes")
            return True
        else:
            print("❌ ไม่สามารถสร้าง PDF ได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_generate_pdf_with_temp_data(generator):
    """ทดสอบการสร้าง PDF จากข้อมูลชั่วคราว"""
    try:
        print("🧪 ทดสอบการสร้าง PDF จากข้อมูลชั่วคราว...")
        
        # สร้างข้อมูลทดสอบ
        temp_contract = {
            'contract_number': 'TEST-001',
            'pawn_amount': 5000.0,
            'interest_rate': 3.0,
            'fee_amount': 100.0,
            'withholding_tax_rate': 3.0,
            'withholding_tax_amount': 15.0,
            'total_paid': 5000.0,
            'total_redemption': 5115.0,
            'start_date': '2024-01-01',
            'end_date': '2024-02-01',
            'days_count': 31
        }
        
        temp_customer = {
            'first_name': 'ทดสอบ',
            'last_name': 'ระบบ',
            'phone': '0812345678',
            'id_card': '1234567890123',
            'house_number': '123',
            'street': 'ถนนทดสอบ',
            'subdistrict': 'ตำบลทดสอบ',
            'district': 'อำเภอทดสอบ',
            'province': 'จังหวัดทดสอบ'
        }
        
        temp_product = {
            'name': 'โทรศัพท์มือถือ',
            'brand': 'Samsung',
            'size': '6.1 นิ้ว',
            'weight': 150,
            'serial_number': 'SN123456789'
        }
        
        # สร้าง PDF
        output_path = "test_temp_contract.pdf"
        result_path = generator.generate_pdf_from_data(
            temp_contract, temp_customer, temp_product, output_path
        )
        
        if result_path and os.path.exists(result_path):
            print(f"✅ สร้าง PDF จากข้อมูลชั่วคราวสำเร็จ: {result_path}")
            print(f"📁 ขนาดไฟล์: {os.path.getsize(result_path)} bytes")
            return True
        else:
            print("❌ ไม่สามารถสร้าง PDF จากข้อมูลชั่วคราวได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับการทดสอบ"""
    print("🚀 เริ่มต้นการทดสอบระบบสร้างใบขายฝาก PDF")
    print("=" * 50)
    
    # ทดสอบการสร้าง PDF Generator
    generator = test_pdf_generator()
    if not generator:
        print("❌ ไม่สามารถทดสอบต่อได้")
        return
    
    # ทดสอบการเชื่อมต่อฐานข้อมูล
    db = test_database_connection()
    if not db:
        print("❌ ไม่สามารถทดสอบต่อได้")
        return
    
    # ทดสอบการดึงข้อมูลสัญญา
    contracts = test_get_contracts(db)
    
    # ทดสอบการสร้าง PDF จากสัญญาที่มีอยู่
    if contracts:
        print("\n📋 ทดสอบการสร้าง PDF จากสัญญาที่มีอยู่...")
        success = test_generate_pdf_from_contract(generator, contracts[0])
        if success:
            print("✅ การทดสอบจากสัญญาจริงสำเร็จ")
        else:
            print("❌ การทดสอบจากสัญญาจริงล้มเหลว")
    
    # ทดสอบการสร้าง PDF จากข้อมูลชั่วคราว
    print("\n📋 ทดสอบการสร้าง PDF จากข้อมูลชั่วคราว...")
    success = test_generate_pdf_with_temp_data(generator)
    if success:
        print("✅ การทดสอบจากข้อมูลชั่วคราวสำเร็จ")
    else:
        print("❌ การทดสอบจากข้อมูลชั่วคราวล้มเหลว")
    
    print("\n" + "=" * 50)
    print("🏁 การทดสอบเสร็จสิ้น")
    
    # แสดงผลลัพธ์
    if success:
        print("✅ ระบบสร้าง PDF ทำงานได้ปกติ")
        print("💡 คุณสามารถใช้งานระบบได้แล้ว")
    else:
        print("❌ ระบบสร้าง PDF มีปัญหา")
        print("🔧 กรุณาตรวจสอบข้อผิดพลาดและแก้ไข")

if __name__ == "__main__":
    # ตรวจสอบว่ามีไฟล์ฟอนต์หรือไม่
    font_files = ['THSarabun.ttf', 'THSarabun Bold.ttf']
    missing_fonts = [f for f in font_files if not os.path.exists(f)]
    
    if missing_fonts:
        print(f"⚠️  ไม่พบไฟล์ฟอนต์: {', '.join(missing_fonts)}")
        print("📁 กรุณาวางไฟล์ฟอนต์ในโฟลเดอร์โปรเจค")
        print("🔗 ดาวน์โหลดได้จาก: https://fonts.google.com/specimen/Sarabun")
        sys.exit(1)
    
    # รันการทดสอบ
    main()

