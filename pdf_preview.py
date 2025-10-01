#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับเรียกใช้ pdf.py จาก main.py
ใช้ Python 3 เพื่อรองรับ PyMuPDF และ Pillow
"""
import sys
import json
import tempfile
import os
from pdf import generate_pawn_ticket_from_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_preview.py <json_data>")
        sys.exit(1)
    
    try:
        # อ่านข้อมูลจาก command line argument
        data = json.loads(sys.argv[1])
        
        # เรียกใช้ฟังก์ชันสร้าง PDF และเปิด preview
        result = generate_pawn_ticket_from_data(
            contract_data=data['contract_data'],
            customer_data=data['customer_data'],
            product_data=data['product_data'],
            shop_data=data.get('shop_data'),
            show_preview=True
        )
        
        if result:
            print(f"PDF created successfully: {result}")
        else:
            print("Failed to create PDF")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

