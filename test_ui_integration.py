#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบการใช้งานปุ่มสแกนบัตรใน UI หลัก
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_card_reader_detection():
    """ทดสอบการตรวจจับ card reader"""
    print("=== ทดสอบการตรวจจับ Card Reader ===")
    
    try:
        from smartcard.System import readers
        
        reader_list = readers()
        if not reader_list:
            print("❌ ไม่พบ card reader")
            return False
        
        print(f"✅ พบ card reader: {len(reader_list)} ตัว")
        for i, reader in enumerate(reader_list):
            print(f"  {i}: {reader}")
        
        return True
        
    except ImportError:
        print("❌ ไม่พบโมดูล smartcard")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_ui_integration():
    """ทดสอบการรวมฟีเจอร์สแกนบัตรใน UI"""
    print("\n=== ทดสอบการรวมฟีเจอร์สแกนบัตรใน UI ===")
    
    try:
        # ทดสอบการ import คลาสที่จำเป็น
        from main import PawnShopUI
        print("✅ สามารถ import PawnShopUI ได้")
        
        # ทดสอบการสร้าง instance
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # สร้าง UI (ไม่แสดง)
        ui = PawnShopUI()
        print("✅ สามารถสร้าง PawnShopUI ได้")
        
        # ทดสอบการเรียกใช้ฟังก์ชันสแกนบัตร
        if hasattr(ui, 'scan_id_card'):
            print("✅ มีฟังก์ชัน scan_id_card")
        else:
            print("❌ ไม่มีฟังก์ชัน scan_id_card")
            return False
        
        if hasattr(ui, 'check_card_reader_status'):
            print("✅ มีฟังก์ชัน check_card_reader_status")
        else:
            print("❌ ไม่มีฟังก์ชัน check_card_reader_status")
            return False
        
        if hasattr(ui, 'on_card_data_ready'):
            print("✅ มีฟังก์ชัน on_card_data_ready")
        else:
            print("❌ ไม่มีฟังก์ชัน on_card_data_ready")
            return False
        
        if hasattr(ui, 'on_scan_error'):
            print("✅ มีฟังก์ชัน on_scan_error")
        else:
            print("❌ ไม่มีฟังก์ชัน on_scan_error")
            return False
        
        if hasattr(ui, 'open_customer_dialog_with_card_data'):
            print("✅ มีฟังก์ชัน open_customer_dialog_with_card_data")
        else:
            print("❌ ไม่มีฟังก์ชัน open_customer_dialog_with_card_data")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ UI: {e}")
        return False

def test_dialog_integration():
    """ทดสอบการรวมกับ dialogs"""
    print("\n=== ทดสอบการรวมกับ Dialogs ===")
    
    try:
        from dialogs import ThaiIDCardScanner, CustomerDialog
        print("✅ สามารถ import ThaiIDCardScanner และ CustomerDialog ได้")
        
        # ทดสอบการสร้าง instance
        scanner = ThaiIDCardScanner()
        print("✅ สามารถสร้าง ThaiIDCardScanner ได้")
        
        # ทดสอบการสร้าง CustomerDialog
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = CustomerDialog()
        print("✅ สามารถสร้าง CustomerDialog ได้")
        
        # ทดสอบการเรียกใช้ฟังก์ชันที่จำเป็น
        if hasattr(dialog, 'fill_form_with_card_data'):
            print("✅ มีฟังก์ชัน fill_form_with_card_data")
        else:
            print("❌ ไม่มีฟังก์ชัน fill_form_with_card_data")
            return False
        
        if hasattr(dialog, 'save_card_photo'):
            print("✅ มีฟังก์ชัน save_card_photo")
        else:
            print("❌ ไม่มีฟังก์ชัน save_card_photo")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ Dialogs: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=== ทดสอบการรวมฟีเจอร์สแกนบัตรใน UI หลัก ===\n")
    
    # ทดสอบการตรวจจับ card reader
    card_reader_ok = test_card_reader_detection()
    
    # ทดสอบการรวมใน UI
    ui_ok = test_ui_integration()
    
    # ทดสอบการรวมกับ dialogs
    dialog_ok = test_dialog_integration()
    
    # สรุปผลการทดสอบ
    print("\n=== สรุปผลการทดสอบ ===")
    print(f"Card Reader Detection: {'✅' if card_reader_ok else '❌'}")
    print(f"UI Integration: {'✅' if ui_ok else '❌'}")
    print(f"Dialog Integration: {'✅' if dialog_ok else '❌'}")
    
    if card_reader_ok and ui_ok and dialog_ok:
        print("\n🎉 การทดสอบสำเร็จ! ฟีเจอร์สแกนบัตรพร้อมใช้งานใน UI หลัก")
        print("\nวิธีการใช้งาน:")
        print("1. เปิดโปรแกรมหลัก (python3 main.py)")
        print("2. ไปที่เมนู 'ลูกค้า' → 'สแกนบัตรประชาชน'")
        print("3. หรือคลิกปุ่ม 'สแกนบัตรประชาชน' ใน toolbar ด้านล่าง")
        print("4. ใส่บัตรประชาชนใน card reader")
        print("5. รอการอ่านข้อมูลและยืนยันการใช้งาน")
    else:
        print("\n❌ การทดสอบล้มเหลว กรุณาตรวจสอบและแก้ไขปัญหา")
    
    print("\n=== การทดสอบเสร็จสิ้น ===")

if __name__ == "__main__":
    main()
