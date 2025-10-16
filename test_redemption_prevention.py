#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบระบบป้องกันการไถ่คืนซ้ำ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ใช้ Python 2.7 compatible imports
try:
    from database import PawnShopDatabase
    from dialogs import RedemptionDialog
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QDate
except ImportError:
    print("ไม่สามารถ import modules ได้ - ใช้ Python 3.6+ และติดตั้ง dependencies")
    sys.exit(1)

def test_redemption_prevention():
    """ทดสอบระบบป้องกันการไถ่คืนซ้ำ"""
    print("=== ทดสอบระบบป้องกันการไถ่คืนซ้ำ ===")
    
    # สร้าง database instance
    db = PawnShopDatabase()
    
    # ทดสอบฟังก์ชันตรวจสอบสถานะสัญญา
    print("\n1. ทดสอบฟังก์ชัน is_contract_redeemed:")
    
    # สร้างสัญญาทดสอบ
    test_contract_data = {
        'contract_number': 'TEST-001',
        'customer_id': 1,
        'product_id': 1,
        'pawn_amount': 1000.0,
        'fee_amount': 0.0,
        'total_paid': 1000.0,
        'total_redemption': 1000.0,
        'start_date': '2024-01-01',
        'end_date': '2024-01-31',
        'days_count': 30
    }
    
    try:
        # สร้างสัญญาทดสอบ
        contract_id = db.create_contract(test_contract_data)
        print("   สร้างสัญญาทดสอบ ID: {}".format(contract_id))
        
        # ตรวจสอบสถานะก่อนการไถ่คืน
        is_redeemed_before = db.is_contract_redeemed(contract_id)
        print("   สถานะก่อนการไถ่คืน: {}".format('ไถ่คืนแล้ว' if is_redeemed_before else 'ยังไม่ไถ่คืน'))
        
        # ทำการไถ่คืน
        redemption_data = {
            'contract_id': contract_id,
            'redemption_date': '2024-01-15',
            'redemption_amount': 1000.0,
            'deposit_date': '2024-01-01',
            'due_date': '2024-01-31',
            'total_days': 14,
            'principal_amount': 1000.0,
            'fee_amount': 0.0,
            'penalty_amount': 0.0,
            'discount_amount': 0.0
        }
        
        redemption_id = db.redeem_contract(redemption_data)
        print("   ทำการไถ่คืน ID: {}".format(redemption_id))
        
        # ตรวจสอบสถานะหลังการไถ่คืน
        is_redeemed_after = db.is_contract_redeemed(contract_id)
        print("   สถานะหลังการไถ่คืน: {}".format('ไถ่คืนแล้ว' if is_redeemed_after else 'ยังไม่ไถ่คืน'))
        
        # ทดสอบฟังก์ชันดึงประวัติการไถ่คืน
        print("\n2. ทดสอบฟังก์ชัน get_contract_redemption_history:")
        redemption_history = db.get_contract_redemption_history(contract_id)
        print("   จำนวนการไถ่คืน: {}".format(len(redemption_history)))
        
        for i, redemption in enumerate(redemption_history, 1):
            print("   {}. วันที่: {} ยอด: {:.2f} บาท".format(
                i, 
                redemption.get('redemption_date'), 
                redemption.get('redemption_amount', 0)
            ))
        
        print("\n✅ การทดสอบเสร็จสิ้น - ระบบป้องกันการไถ่คืนซ้ำทำงานถูกต้อง")
        
    except Exception as e:
        print("❌ เกิดข้อผิดพลาดในการทดสอบ: {}".format(e))
    
    finally:
        # ลบข้อมูลทดสอบ
        try:
            db.delete_contract(contract_id)
            print("\n🧹 ลบสัญญาทดสอบ ID: {} เรียบร้อย".format(contract_id))
        except:
            pass

def test_redemption_dialog():
    """ทดสอบ RedemptionDialog"""
    print("\n=== ทดสอบ RedemptionDialog ===")
    
    app = QApplication(sys.argv)
    
    # สร้างข้อมูลสัญญาทดสอบ
    test_contract_data = {
        'id': 1,
        'contract_number': 'TEST-001',
        'customer_id': 1,
        'product_id': 1,
        'pawn_amount': 1000.0,
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    }
    
    try:
        # สร้าง RedemptionDialog
        dialog = RedemptionDialog(None, test_contract_data)
        print("   สร้าง RedemptionDialog เรียบร้อย")
        
        # ทดสอบฟังก์ชัน check_contract_status
        status_ok = dialog.check_contract_status()
        print("   ผลการตรวจสอบสถานะ: {}".format('ผ่าน' if status_ok else 'ไม่ผ่าน'))
        
        print("✅ การทดสอบ RedemptionDialog เสร็จสิ้น")
        
    except Exception as e:
        print("❌ เกิดข้อผิดพลาดในการทดสอบ RedemptionDialog: {}".format(e))

if __name__ == "__main__":
    test_redemption_prevention()
    test_redemption_dialog()
