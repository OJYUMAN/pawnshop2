#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบพรีวิวและเลือกเครื่องปริ้น
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

# เพิ่ม path ของโปรเจค
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from print_preview_dialog import show_print_preview

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ทดสอบระบบพรีวิวและเลือกเครื่องปริ้น")
        self.setGeometry(100, 100, 400, 300)
        
        # สร้าง UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # ปุ่มทดสอบสัญญาฝากขาย
        self.test_pawn_btn = QPushButton("ทดสอบสัญญาฝากขาย")
        self.test_pawn_btn.clicked.connect(self.test_pawn_contract)
        layout.addWidget(self.test_pawn_btn)
        
        # ปุ่มทดสอบสัญญาไถ่คืน
        self.test_redemption_btn = QPushButton("ทดสอบสัญญาไถ่คืน")
        self.test_redemption_btn.clicked.connect(self.test_redemption_contract)
        layout.addWidget(self.test_redemption_btn)
    
    def test_pawn_contract(self):
        """ทดสอบสัญญาฝากขาย"""
        try:
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
            
            # เรียกใช้ระบบพรีวิว
            from pdf import generate_pawn_contract_html as pdf_generator
            
            success = show_print_preview(
                parent=self,
                contract_type="pawn",
                pdf_generator_func=pdf_generator,
                contract_data=contract_data,
                customer_data=customer_data,
                product_data=product_data,
                shop_data=shop_data
            )
            
            if success:
                print("ทดสอบสัญญาฝากขายสำเร็จ")
            else:
                print("ทดสอบสัญญาฝากขายถูกยกเลิก")
                
        except Exception as e:
            print("เกิดข้อผิดพลาดในการทดสอบสัญญาฝากขาย: " + str(e))
    
    def test_redemption_contract(self):
        """ทดสอบสัญญาไถ่คืน"""
        try:
            # ข้อมูลตัวอย่าง
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
            
            # เรียกใช้ระบบพรีวิว
            from pdf3 import generate_redemption_contract_pdf as pdf_generator
            
            success = show_print_preview(
                parent=self,
                contract_type="redemption",
                pdf_generator_func=pdf_generator,
                contract_data=redemption_data,
                customer_data=customer_data,
                product_data=product_data,
                shop_data=shop_data
            )
            
            if success:
                print("ทดสอบสัญญาไถ่คืนสำเร็จ")
            else:
                print("ทดสอบสัญญาไถ่คืนถูกยกเลิก")
                
        except Exception as e:
            print("เกิดข้อผิดพลาดในการทดสอบสัญญาไถ่คืน: " + str(e))

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
