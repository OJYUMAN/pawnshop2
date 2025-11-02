# -*- coding: utf-8 -*-
"""
สคริปต์สร้าง Mock Database สำหรับทดสอบระบบ
สร้างข้อมูลตัวอย่าง: ลูกค้า, สินค้า, และสัญญา
"""

import sqlite3
from datetime import datetime, timedelta
from database import PawnShopDatabase

def create_mock_data(db_path="pawnshop.db"):
    """สร้างข้อมูลตัวอย่างสำหรับทดสอบ"""
    
    db = PawnShopDatabase(db_path)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # ลบข้อมูลเดิม (ถ้ามี)
        print("กำลังลบข้อมูลเดิม...")
        cursor.execute("DELETE FROM redemptions")
        cursor.execute("DELETE FROM interest_payments")
        cursor.execute("DELETE FROM renewals")
        cursor.execute("DELETE FROM contracts")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM customers")
        
        # Reset auto increment
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('customers', 'products', 'contracts')")
        
        print("กำลังสร้างข้อมูลตัวอย่าง...\n")
        
        # สร้างข้อมูลลูกค้า
        customers_data = [
            {
                'customer_code': 'C0001',
                'first_name': 'สมชาย',
                'last_name': 'ใจดี',
                'id_card': '1234567890123',
                'house_number': '123',
                'street': 'ถนนสุขุมวิท',
                'subdistrict': 'คลองตัน',
                'district': 'วัฒนา',
                'province': 'กรุงเทพมหานคร',
                'phone': '0812345678',
                'other_details': ''
            },
            {
                'customer_code': 'C0002',
                'first_name': 'สมหญิง',
                'last_name': 'รักดี',
                'id_card': '2345678901234',
                'house_number': '456',
                'street': 'ถนนพหลโยธิน',
                'subdistrict': 'บางเขน',
                'district': 'บางเขน',
                'province': 'กรุงเทพมหานคร',
                'phone': '0823456789',
                'other_details': ''
            },
            {
                'customer_code': 'C0003',
                'first_name': 'ประยุทธ์',
                'last_name': 'ศรีสุข',
                'id_card': '3456789012345',
                'house_number': '789',
                'street': 'ถนนรัชดาภิเษก',
                'subdistrict': 'ห้วยขวาง',
                'district': 'ห้วยขวาง',
                'province': 'กรุงเทพมหานคร',
                'phone': '0834567890',
                'other_details': ''
            },
            {
                'customer_code': 'C0004',
                'first_name': 'สุรชัย',
                'last_name': 'บุญมี',
                'id_card': '4567890123456',
                'house_number': '321',
                'street': 'ถนนสีลม',
                'subdistrict': 'สีลม',
                'district': 'บางรัก',
                'province': 'กรุงเทพมหานคร',
                'phone': '0845678901',
                'other_details': ''
            },
            {
                'customer_code': 'C0005',
                'first_name': 'สุดา',
                'last_name': 'ใจงาม',
                'id_card': '5678901234567',
                'house_number': '654',
                'street': 'ถนนลาดพร้าว',
                'subdistrict': 'จตุจักร',
                'district': 'จตุจักร',
                'province': 'กรุงเทพมหานคร',
                'phone': '0856789012',
                'other_details': ''
            },
            {
                'customer_code': 'C0006',
                'first_name': 'วิชัย',
                'last_name': 'มั่นคง',
                'id_card': '6789012345678',
                'house_number': '987',
                'street': 'ถนนวิภาวดี',
                'subdistrict': 'พญาไท',
                'district': 'พญาไท',
                'province': 'กรุงเทพมหานคร',
                'phone': '0867890123',
                'other_details': ''
            }
        ]
        
        customer_ids = []
        for customer in customers_data:
            cursor.execute('''
                INSERT INTO customers (
                    customer_code, first_name, last_name, id_card,
                    house_number, street, subdistrict, district, province,
                    phone, other_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer['customer_code'],
                customer['first_name'],
                customer['last_name'],
                customer['id_card'],
                customer['house_number'],
                customer['street'],
                customer['subdistrict'],
                customer['district'],
                customer['province'],
                customer['phone'],
                customer['other_details']
            ))
            customer_ids.append(cursor.lastrowid)
        
        print(f"✓ สร้างข้อมูลลูกค้า {len(customers_data)} รายการ")
        
        # สร้างข้อมูลสินค้า
        products_data = [
            {
                'name': 'iPhone 15 Pro Max',
                'brand': 'Apple',
                'model': 'A3101',
                'serial_number': 'SN001234567',
                'imei1': '123456789012345',
                'imei2': '',
                'condition': 'ดีมาก',
                'accessories': 'กล่อง, สายชาร์จ, หูฟัง',
                'other_details': ''
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'brand': 'Samsung',
                'model': 'SM-S928',
                'serial_number': 'SN002345678',
                'imei1': '234567890123456',
                'imei2': '234567890123457',
                'condition': 'ดี',
                'accessories': 'กล่อง, สายชาร์จ',
                'other_details': ''
            },
            {
                'name': 'MacBook Pro 16"',
                'brand': 'Apple',
                'model': 'M3 Pro',
                'serial_number': 'SN003456789',
                'imei1': '',
                'imei2': '',
                'condition': 'ดีมาก',
                'accessories': 'กล่อง, สายชาร์จ, คู่มือ',
                'other_details': ''
            },
            {
                'name': 'iPad Pro 12.9"',
                'brand': 'Apple',
                'model': 'M2',
                'serial_number': 'SN004567890',
                'imei1': '',
                'imei2': '',
                'condition': 'ดี',
                'accessories': 'กล่อง, Apple Pencil',
                'other_details': ''
            },
            {
                'name': 'Rolex Submariner',
                'brand': 'Rolex',
                'model': '126610LN',
                'serial_number': 'SN005678901',
                'imei1': '',
                'imei2': '',
                'condition': 'ดีมาก',
                'accessories': 'กล่อง, คู่มือ',
                'other_details': ''
            },
            {
                'name': 'Nintendo Switch OLED',
                'brand': 'Nintendo',
                'model': 'HEG-001',
                'serial_number': 'SN006789012',
                'imei1': '',
                'imei2': '',
                'condition': 'ดี',
                'accessories': 'กล่อง, Joy-Con, สายชาร์จ',
                'other_details': ''
            },
            {
                'name': 'AirPods Pro 2',
                'brand': 'Apple',
                'model': 'A2931',
                'serial_number': 'SN007890123',
                'imei1': '',
                'imei2': '',
                'condition': 'ดีมาก',
                'accessories': 'กล่อง, หูฟัง',
                'other_details': ''
            },
            {
                'name': 'Sony WH-1000XM5',
                'brand': 'Sony',
                'model': 'WH-1000XM5',
                'serial_number': 'SN008901234',
                'imei1': '',
                'imei2': '',
                'condition': 'ดี',
                'accessories': 'กล่อง, สายชาร์จ',
                'other_details': ''
            }
        ]
        
        product_ids = []
        for product in products_data:
            cursor.execute('''
                INSERT INTO products (
                    name, brand, model, serial_number,
                    imei1, imei2, condition, accessories, other_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product['name'],
                product['brand'],
                product['model'],
                product['serial_number'],
                product['imei1'],
                product['imei2'],
                product['condition'],
                product['accessories'],
                product['other_details']
            ))
            product_ids.append(cursor.lastrowid)
        
        print(f"✓ สร้างข้อมูลสินค้า {len(products_data)} รายการ")
        
        # วันปัจจุบัน
        today = datetime.now().date()
        
        # สร้างข้อมูลสัญญา (มีวันที่ครบกำหนดหลากหลาย)
        contracts_data = [
            # สัญญาที่ครบกำหนดแล้ว (สำหรับทดสอบรายการครบกำหนด)
            {
                'contract_number': 'CN0001',
                'customer_id': customer_ids[0],
                'product_id': product_ids[0],
                'pawn_amount': 50000.00,
                'fee_amount': 3000.00,
                'total_paid': 53000.00,
                'total_redemption': 53000.00,
                'start_date': (today - timedelta(days=60)).strftime('%Y-%m-%d'),
                'end_date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),  # ครบกำหนด 5 วันแล้ว
                'days_count': 30,
                'status': 'active'
            },
            {
                'contract_number': 'CN0002',
                'customer_id': customer_ids[1],
                'product_id': product_ids[1],
                'pawn_amount': 45000.00,
                'fee_amount': 2700.00,
                'total_paid': 47700.00,
                'total_redemption': 47700.00,
                'start_date': (today - timedelta(days=35)).strftime('%Y-%m-%d'),
                'end_date': (today - timedelta(days=2)).strftime('%Y-%m-%d'),  # ครบกำหนด 2 วันแล้ว
                'days_count': 30,
                'status': 'active'
            },
            {
                'contract_number': 'CN0003',
                'customer_id': customer_ids[2],
                'product_id': product_ids[2],
                'pawn_amount': 120000.00,
                'fee_amount': 7200.00,
                'total_paid': 127200.00,
                'total_redemption': 127200.00,
                'start_date': (today - timedelta(days=33)).strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),  # ครบกำหนดวันนี้
                'days_count': 30,
                'status': 'active'
            },
            {
                'contract_number': 'CN0004',
                'customer_id': customer_ids[3],
                'product_id': product_ids[3],
                'pawn_amount': 35000.00,
                'fee_amount': 2100.00,
                'total_paid': 37100.00,
                'total_redemption': 37100.00,
                'start_date': (today - timedelta(days=10)).strftime('%Y-%m-%d'),
                'end_date': (today - timedelta(days=1)).strftime('%Y-%m-%d'),  # ครบกำหนดเมื่อวาน
                'days_count': 7,
                'status': 'active'
            },
            # สัญญาที่ใกล้ครบกำหนด
            {
                'contract_number': 'CN0005',
                'customer_id': customer_ids[4],
                'product_id': product_ids[4],
                'pawn_amount': 250000.00,
                'fee_amount': 15000.00,
                'total_paid': 265000.00,
                'total_redemption': 265000.00,
                'start_date': (today - timedelta(days=28)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),  # ใกล้ครบกำหนด (2 วัน)
                'days_count': 30,
                'status': 'active'
            },
            {
                'contract_number': 'CN0006',
                'customer_id': customer_ids[5],
                'product_id': product_ids[5],
                'pawn_amount': 15000.00,
                'fee_amount': 900.00,
                'total_paid': 15900.00,
                'total_redemption': 15900.00,
                'start_date': (today - timedelta(days=25)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),  # ใกล้ครบกำหนด (5 วัน)
                'days_count': 30,
                'status': 'active'
            },
            # สัญญาที่ยังไม่ครบกำหนด
            {
                'contract_number': 'CN0007',
                'customer_id': customer_ids[0],
                'product_id': product_ids[6],
                'pawn_amount': 8000.00,
                'fee_amount': 480.00,
                'total_paid': 8480.00,
                'total_redemption': 8480.00,
                'start_date': (today - timedelta(days=20)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(days=10)).strftime('%Y-%m-%d'),  # ยังไม่ครบกำหนด (10 วัน)
                'days_count': 30,
                'status': 'active'
            },
            {
                'contract_number': 'CN0008',
                'customer_id': customer_ids[1],
                'product_id': product_ids[7],
                'pawn_amount': 12000.00,
                'fee_amount': 720.00,
                'total_paid': 12720.00,
                'total_redemption': 12720.00,
                'start_date': (today - timedelta(days=15)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),  # ยังไม่ครบกำหนด (15 วัน)
                'days_count': 30,
                'status': 'active'
            },
            # สัญญาที่ไถ่คืนแล้ว (เพื่อแสดงตัวอย่าง)
            {
                'contract_number': 'CN0009',
                'customer_id': customer_ids[2],
                'product_id': product_ids[0],
                'pawn_amount': 40000.00,
                'fee_amount': 2400.00,
                'total_paid': 42400.00,
                'total_redemption': 42400.00,
                'start_date': (today - timedelta(days=90)).strftime('%Y-%m-%d'),
                'end_date': (today - timedelta(days=60)).strftime('%Y-%m-%d'),
                'days_count': 30,
                'status': 'redeemed'
            },
            # สัญญาที่หลุดจำนำแล้ว
            {
                'contract_number': 'CN0010',
                'customer_id': customer_ids[3],
                'product_id': product_ids[1],
                'pawn_amount': 30000.00,
                'fee_amount': 1800.00,
                'total_paid': 31800.00,
                'total_redemption': 31800.00,
                'start_date': (today - timedelta(days=120)).strftime('%Y-%m-%d'),
                'end_date': (today - timedelta(days=90)).strftime('%Y-%m-%d'),
                'days_count': 30,
                'status': 'lost'
            }
        ]
        
        for contract in contracts_data:
            cursor.execute('''
                INSERT INTO contracts (
                    contract_number, customer_id, product_id,
                    pawn_amount, fee_amount, total_paid, total_redemption,
                    start_date, end_date, days_count, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract['contract_number'],
                contract['customer_id'],
                contract['product_id'],
                contract['pawn_amount'],
                contract['fee_amount'],
                contract['total_paid'],
                contract['total_redemption'],
                contract['start_date'],
                contract['end_date'],
                contract['days_count'],
                contract['status']
            ))
        
        print(f"✓ สร้างข้อมูลสัญญา {len(contracts_data)} รายการ")
        
        conn.commit()
        
        print("\n" + "="*50)
        print("สรุปข้อมูลที่สร้าง:")
        print("="*50)
        print(f"✓ ลูกค้า: {len(customers_data)} รายการ")
        print(f"✓ สินค้า: {len(products_data)} รายการ")
        print(f"✓ สัญญา: {len(contracts_data)} รายการ")
        print("\nสัญญาที่ครบกำหนดแล้ว (แสดงในรายการครบกำหนด):")
        
        due_contracts = [c for c in contracts_data if c['status'] == 'active' and 
                        datetime.strptime(c['end_date'], '%Y-%m-%d').date() <= today]
        for contract in due_contracts:
            end_date = datetime.strptime(contract['end_date'], '%Y-%m-%d').date()
            days_overdue = (today - end_date).days
            print(f"  - {contract['contract_number']}: ครบกำหนด {days_overdue} วัน")
        
        print(f"\nรวม {len(due_contracts)} สัญญาที่ครบกำหนด")
        print("\n" + "="*50)
        print("✓ สร้าง Mock Database เสร็จสมบูรณ์!")
        print("="*50)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("สร้าง Mock Database สำหรับทดสอบระบบ")
    print("="*50 + "\n")
    
    try:
        create_mock_data()
        print("\n✓ พร้อมทดสอบระบบแล้ว!")
        print("\nหมายเหตุ: ข้อมูลที่สร้างจะรวมสัญญาที่ครบกำหนดแล้ว")
        print("          เพื่อทดสอบฟีเจอร์ 'รายการครบกำหนด'")
        
    except Exception as e:
        print(f"\n✗ เกิดข้อผิดพลาด: {str(e)}")
        import traceback
        traceback.print_exc()

