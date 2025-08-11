#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบการคำนวณยอดไถ่ถอน
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import PawnShopUtils

def test_redemption_calculations():
    """ทดสอบการคำนวณยอดไถ่ถอน"""
    print("=== ทดสอบการคำนวณยอดไถ่ถอน ===\n")
    
    # ข้อมูลทดสอบ
    pawn_amount = 10000  # ยอดฝาก 10,000 บาท
    interest_rate = 1.5   # อัตราดอกเบี้ย 1.5% ต่อเดือน
    days = 30            # ระยะเวลา 30 วัน
    withholding_tax_rate = 15  # อัตราหัก ณ ที่จ่าย 15%
    fee_amount = 100     # ค่าธรรมเนียม 100 บาท
    
    print(f"ข้อมูลทดสอบ:")
    print(f"  ยอดฝาก: {pawn_amount:,.2f} บาท")
    print(f"  อัตราดอกเบี้ย: {interest_rate}% ต่อเดือน")
    print(f"  ระยะเวลา: {days} วัน")
    print(f"  อัตราหัก ณ ที่จ่าย: {withholding_tax_rate}%")
    print(f"  ค่าธรรมเนียม: {fee_amount:,.2f} บาท\n")
    
    # คำนวณดอกเบี้ย
    interest_amount = PawnShopUtils.calculate_interest(pawn_amount, interest_rate, days)
    print(f"ดอกเบี้ย: {interest_amount:,.2f} บาท")
    
    # คำนวณหัก ณ ที่จ่าย
    withholding_tax_amount = PawnShopUtils.calculate_withholding_tax(interest_amount, withholding_tax_rate)
    print(f"หัก ณ ที่จ่าย: {withholding_tax_amount:,.2f} บาท")
    
    # คำนวณยอดไถ่ถอนแบบต่างๆ
    redemption_without_tax = PawnShopUtils.calculate_redemption_without_tax(
        pawn_amount, interest_amount, fee_amount
    )
    redemption_with_tax = PawnShopUtils.calculate_redemption_with_tax(
        pawn_amount, interest_amount, fee_amount, withholding_tax_amount
    )
    
    print(f"\nผลการคำนวณ:")
    print(f"  ยอดไถ่ถอน (ไม่รวมหัก ณ ที่จ่าย): {redemption_without_tax:,.2f} บาท")
    print(f"  ยอดไถ่ถอน (รวมหัก ณ ที่จ่าย): {redemption_with_tax:,.2f} บาท")
    
    # ตรวจสอบความถูกต้อง
    expected_without_tax = pawn_amount + interest_amount + fee_amount
    expected_with_tax = pawn_amount + interest_amount + fee_amount - withholding_tax_amount
    
    print(f"\nการตรวจสอบ:")
    print(f"  ยอดไถ่ถอน (ไม่รวมหัก ณ ที่จ่าย) ถูกต้อง: {abs(redemption_without_tax - expected_without_tax) < 0.01}")
    print(f"  ยอดไถ่ถอน (รวมหัก ณ ที่จ่าย) ถูกต้อง: {abs(redemption_with_tax - expected_with_tax) < 0.01}")
    
    # แสดงรายละเอียดการคำนวณ
    print(f"\nรายละเอียดการคำนวณ:")
    print(f"  ยอดฝาก: {pawn_amount:,.2f} บาท")
    print(f"  + ดอกเบี้ย: {interest_amount:,.2f} บาท")
    print(f"  + ค่าธรรมเนียม: {fee_amount:,.2f} บาท")
    print(f"  = ยอดรวม: {pawn_amount + interest_amount + fee_amount:,.2f} บาท")
    print(f"  - หัก ณ ที่จ่าย: {withholding_tax_amount:,.2f} บาท")
    print(f"  = ยอดไถ่ถอน: {redemption_with_tax:,.2f} บาท")

if __name__ == "__main__":
    test_redemption_calculations()
