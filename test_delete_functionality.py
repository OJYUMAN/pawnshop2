#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบฟังก์ชันการลบข้อมูล
"""

import sqlite3
import os
from database import PawnShopDatabase

def test_delete_functions():
    """ทดสอบฟังก์ชันการลบข้อมูล"""
    print("ทดสอบฟังก์ชันการลบข้อมูล...")
    
    # สร้างฐานข้อมูลทดสอบ
    db = PawnShopDatabase("test_delete.db")
    
    try:
        # ทดสอบการเพิ่มข้อมูลลูกค้า
        customer_data = {
            'customer_code': 'TEST001',
            'first_name': 'ทดสอบ',
            'last_name': 'ลูกค้า',
            'id_card': '1234567890123',
            'phone': '0812345678',
            'house_number': '123',
            'street': 'ถนนทดสอบ',
            'subdistrict': 'แขวงทดสอบ',
            'district': 'เขตทดสอบ',
            'province': 'กรุงเทพฯ'
        }
        
        customer_id = db.add_customer(customer_data)
        print(f"เพิ่มลูกค้าสำเร็จ ID: {customer_id}")
        
        # ทดสอบการเพิ่มข้อมูลสินค้า
        product_data = {
            'name': 'สินค้าทดสอบ',
            'brand': 'ยี่ห้อทดสอบ',
            'size': 'ขนาดทดสอบ',
            'weight': 100.0,
            'serial_number': 'SERIAL001'
        }
        
        product_id = db.add_product(product_data)
        print(f"เพิ่มสินค้าสำเร็จ ID: {product_id}")
        
        # ทดสอบการลบข้อมูลสินค้า (ควรลบได้เพราะไม่มีสัญญาเกี่ยวข้อง)
        if db.delete_product(product_id):
            print("ลบสินค้าสำเร็จ")
        else:
            print("ลบสินค้าไม่สำเร็จ")
        
        # ทดสอบการลบข้อมูลลูกค้า (ควรลบได้เพราะไม่มีสัญญาเกี่ยวข้อง)
        if db.delete_customer(customer_id):
            print("ลบลูกค้าสำเร็จ")
        else:
            print("ลบลูกค้าไม่สำเร็จ")
        
        # ทดสอบการลบข้อมูลที่ไม่มีอยู่
        if db.delete_customer(999):
            print("ลบลูกค้าที่ไม่มีอยู่สำเร็จ (ไม่ควรเป็นเช่นนี้)")
        else:
            print("ลบลูกค้าที่ไม่มีอยู่ไม่สำเร็จ (ถูกต้อง)")
        
        print("การทดสอบเสร็จสิ้น")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
    
    finally:
        # ลบไฟล์ฐานข้อมูลทดสอบ
        if os.path.exists("test_delete.db"):
            os.remove("test_delete.db")
            print("ลบไฟล์ฐานข้อมูลทดสอบแล้ว")

if __name__ == "__main__":
    test_delete_functions()
