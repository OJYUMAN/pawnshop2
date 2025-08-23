#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบฟีเจอร์สแกนบัตรประชาชน
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dialogs import CustomerDialog

class TestIDCardScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ทดสอบฟีเจอร์สแกนบัตรประชาชน")
        self.setGeometry(100, 100, 400, 200)
        
        # สร้าง central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # สร้าง layout
        layout = QVBoxLayout(central_widget)
        
        # หัวข้อ
        title_label = QLabel("ทดสอบฟีเจอร์สแกนบัตรประชาชน")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # คำอธิบาย
        desc_label = QLabel("คลิกปุ่มด้านล่างเพื่อเปิดหน้าจอเพิ่มข้อมูลลูกค้า\nและทดสอบฟีเจอร์สแกนบัตรประชาชน")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("margin: 20px; color: #666;")
        layout.addWidget(desc_label)
        
        # ปุ่มทดสอบ
        test_button = QPushButton("เปิดหน้าจอเพิ่มข้อมูลลูกค้า")
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        test_button.clicked.connect(self.open_customer_dialog)
        layout.addWidget(test_button)
        
        # หมายเหตุ
        note_label = QLabel("หมายเหตุ: ต้องมี card reader และบัตรประชาชนเพื่อทดสอบ")
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setStyleSheet("margin: 20px; color: #999; font-size: 12px;")
        layout.addWidget(note_label)
    
    def open_customer_dialog(self):
        """เปิดหน้าจอเพิ่มข้อมูลลูกค้า"""
        try:
            dialog = CustomerDialog(self)
            dialog.exec()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "ผิดพลาด", f"ไม่สามารถเปิดหน้าจอได้: {str(e)}")

def test_smartcard_import():
    """ทดสอบการ import โมดูล smartcard"""
    try:
        from smartcard.System import readers
        from smartcard.util import toHexString
        from smartcard.Exceptions import NoCardException, CardConnectionException
        
        print("✅ โมดูล smartcard สามารถ import ได้")
        
        # ตรวจสอบ card reader
        reader_list = readers()
        if reader_list:
            print(f"✅ พบ card reader: {len(reader_list)} ตัว")
            for i, reader in enumerate(reader_list):
                print(f"  {i}: {reader}")
        else:
            print("⚠️  ไม่พบ card reader")
            print("   กรุณาตรวจสอบ:")
            print("   1. การเชื่อมต่อ USB")
            print("   2. การติดตั้ง driver")
            print("   3. PC/SC service ทำงานอยู่")
        
        return True
        
    except ImportError as e:
        print(f"❌ ไม่สามารถ import โมดูล smartcard ได้: {e}")
        print("   กรุณาติดตั้งด้วยคำสั่ง: pip install pyscard")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=== ทดสอบฟีเจอร์สแกนบัตรประชาชน ===\n")
    
    # ทดสอบการ import โมดูล
    if not test_smartcard_import():
        print("\n❌ ไม่สามารถใช้งานฟีเจอร์สแกนบัตรประชาชนได้")
        print("กรุณาติดตั้ง dependencies ที่จำเป็นก่อน")
        return
    
    print("\n✅ ระบบพร้อมใช้งาน")
    print("เริ่มต้น GUI...")
    
    # สร้าง GUI
    app = QApplication(sys.argv)
    window = TestIDCardScanner()
    window.show()
    
    # รัน event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
