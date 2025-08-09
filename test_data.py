#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับเพิ่มข้อมูลตัวอย่างเพื่อทดสอบโปรแกรมรับจำนำ อัญชัน
"""

from database import PawnShopDatabase
from utils import PawnShopUtils
from datetime import datetime, timedelta

def add_sample_data():
    """เพิ่มข้อมูลตัวอย่าง"""
    db = PawnShopDatabase()
    
    print("กำลังเพิ่มข้อมูลตัวอย่าง...")
    
    # เพิ่มลูกค้าตัวอย่าง
    customers = [
        {
            'customer_code': 'C0001',
            'first_name': 'สมชาย',
            'last_name': 'ใจดี',
            'id_card': '1234567890123',
            'phone': '0812345678',
            'house_number': '123/45',
            'street': 'ถนนสุขุมวิท',
            'subdistrict': 'คลองเตย',
            'district': 'คลองเตย',
            'province': 'กรุงเทพมหานคร',
            'other_details': 'ลูกค้าประจำ'
        },
        {
            'customer_code': 'C0002',
            'first_name': 'สมหญิง',
            'last_name': 'รักดี',
            'id_card': '9876543210987',
            'phone': '0898765432',
            'house_number': '456/78',
            'street': 'ถนนรัชดาภิเษก',
            'subdistrict': 'ดินแดง',
            'district': 'ดินแดง',
            'province': 'กรุงเทพมหานคร',
            'other_details': 'ลูกค้าใหม่'
        },
        {
            'customer_code': 'C0003',
            'first_name': 'จีรวัฒน์',
            'last_name': 'ทองแสวง',
            'id_card': '3100601887771',
            'phone': '0816616931',
            'house_number': '248/27',
            'street': 'ซอยเสรีไทย 32 ถนนเสรีไทย',
            'subdistrict': 'แขวงคันนายาว',
            'district': 'เขตคันนายาว',
            'province': 'กรุงเทพมหานคร',
            'other_details': 'ลูกค้าประจำ'
        }
    ]
    
    customer_ids = []
    for customer in customers:
        try:
            customer_id = db.add_customer(customer)
            customer_ids.append(customer_id)
            print(f"เพิ่มลูกค้า: {customer['first_name']} {customer['last_name']}")
        except Exception as e:
            print(f"ไม่สามารถเพิ่มลูกค้า {customer['first_name']}: {e}")
    
    # เพิ่มสินค้าตัวอย่าง
    products = [
        {
            'name': 'สร้อยคอทอง',
            'brand': 'ทองคำแท้',
            'size': '18 นิ้ว',
            'weight': 15.5,
            'serial_number': 'GOLD001',
            'other_details': 'ทองคำ 96.5%'
        },
        {
            'name': 'แหวนเพชร',
            'brand': 'Diamond Plus',
            'size': '6.5',
            'weight': 3.2,
            'serial_number': 'DIAMOND001',
            'other_details': 'เพชร 1 กะรัต'
        },
        {
            'name': 'นาฬิกาโรเล็กซ์',
            'brand': 'Rolex',
            'size': '40mm',
            'weight': 150.0,
            'serial_number': 'ROLEX001',
            'other_details': 'Submariner Date'
        },
        {
            'name': 'โทรศัพท์มือถือ',
            'brand': 'iPhone',
            'size': '6.1 นิ้ว',
            'weight': 194.0,
            'serial_number': 'IPHONE001',
            'other_details': 'iPhone 13 Pro'
        }
    ]
    
    product_ids = []
    for product in products:
        try:
            product_id = db.add_product(product)
            product_ids.append(product_id)
            print(f"เพิ่มสินค้า: {product['name']}")
        except Exception as e:
            print(f"ไม่สามารถเพิ่มสินค้า {product['name']}: {e}")
    
    # เพิ่มสัญญาตัวอย่าง
    contracts = [
        {
            'contract_number': '53-10-4-1078',
            'customer_id': customer_ids[0] if customer_ids else 1,
            'product_id': product_ids[0] if product_ids else 1,
            'pawn_amount': 10000.0,
            'interest_rate': 3.0,
            'fee_amount': 300.0,
            'total_paid': 10000.0,
            'total_redemption': 10300.0,
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'days_count': 30
        },
        {
            'contract_number': '53-10-4-1079',
            'customer_id': customer_ids[1] if len(customer_ids) > 1 else 1,
            'product_id': product_ids[1] if len(product_ids) > 1 else 1,
            'pawn_amount': 25000.0,
            'interest_rate': 3.5,
            'fee_amount': 875.0,
            'total_paid': 25000.0,
            'total_redemption': 25875.0,
            'start_date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            'days_count': 30
        },
        {
            'contract_number': '53-10-4-1080',
            'customer_id': customer_ids[2] if len(customer_ids) > 2 else 1,
            'product_id': product_ids[2] if len(product_ids) > 2 else 1,
            'pawn_amount': 50000.0,
            'interest_rate': 4.0,
            'fee_amount': 2000.0,
            'total_paid': 50000.0,
            'total_redemption': 52000.0,
            'start_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'days_count': 30
        }
    ]
    
    contract_ids = []
    for contract in contracts:
        try:
            contract_id = db.create_contract(contract)
            contract_ids.append(contract_id)
            print(f"เพิ่มสัญญา: {contract['contract_number']}")
        except Exception as e:
            print(f"ไม่สามารถเพิ่มสัญญา {contract['contract_number']}: {e}")
    
    # เพิ่มการชำระดอกเบี้ยตัวอย่าง
    if contract_ids:
        payment_data = {
            'contract_id': contract_ids[0],
            'payment_date': datetime.now().strftime('%Y-%m-%d'),
            'interest_amount': 300.0,
            'penalty_amount': 0.0,
            'discount_amount': 0.0,
            'total_amount': 300.0
        }
        
        try:
            payment_id = db.add_interest_payment(payment_data)
            print(f"เพิ่มการชำระดอกเบี้ย: สัญญา {contracts[0]['contract_number']}")
        except Exception as e:
            print(f"ไม่สามารถเพิ่มการชำระดอกเบี้ย: {e}")
    
    # เพิ่มการไถ่ถอนตัวอย่าง
    if len(contract_ids) > 2:
        redemption_data = {
            'contract_id': contract_ids[2],
            'redemption_date': datetime.now().strftime('%Y-%m-%d'),
            'redemption_amount': 52000.0
        }
        
        try:
            redemption_id = db.redeem_contract(redemption_data)
            print(f"เพิ่มการไถ่ถอน: สัญญา {contracts[2]['contract_number']}")
        except Exception as e:
            print(f"ไม่สามารถเพิ่มการไถ่ถอน: {e}")
    
    print("\nเพิ่มข้อมูลตัวอย่างเสร็จสิ้น!")
    print(f"ลูกค้า: {len(customer_ids)} ราย")
    print(f"สินค้า: {len(product_ids)} รายการ")
    print(f"สัญญา: {len(contract_ids)} สัญญา")

def show_sample_reports():
    """แสดงรายงานตัวอย่าง"""
    db = PawnShopDatabase()
    
    print("\n=== รายงานตัวอย่าง ===")
    
    # รายงานประจำวัน
    today = datetime.now().strftime('%Y-%m-%d')
    daily_summary = db.get_daily_summary(today)
    
    print(f"\nรายงานประจำวัน: {today}")
    print(f"สัญญาใหม่: {daily_summary['new_contracts_count']} สัญญา")
    print(f"การไถ่ถอน: {daily_summary['redemptions_count']} สัญญา")
    print(f"การชำระดอกเบี้ย: {daily_summary['interest_payments_count']} ครั้ง")
    
    # สัญญาที่ใกล้ครบกำหนด
    expiring_contracts = db.get_expiring_contracts(7)
    
    print(f"\nสัญญาที่ใกล้ครบกำหนด (7 วัน): {len(expiring_contracts)} สัญญา")
    for contract in expiring_contracts[:3]:  # แสดง 3 สัญญาแรก
        print(f"- {contract['contract_number']}: {contract['first_name']} {contract['last_name']}")

if __name__ == '__main__':
    print("โปรแกรมรับจำนำ อัญชัน - ข้อมูลตัวอย่าง")
    print("=" * 50)
    
    try:
        add_sample_data()
        show_sample_reports()
        
        print("\nคุณสามารถรันโปรแกรมหลักได้แล้ว:")
        print("python main.py")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        print("กรุณาตรวจสอบการติดตั้งและลองใหม่อีกครั้ง")
