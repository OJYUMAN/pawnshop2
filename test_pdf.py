#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify PDF generation is working properly
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_pdf_generation():
    """Test PDF generation with sample data"""
    try:
        from pdf import generate_pawn_ticket_pdf_data
        
        # Sample contract data
        contract = {
            "contract_number": "TEST-001",
            "copy_number": 1,
            "start_date": "2025-01-15",
            "start_time": "14:30",
            "end_date": "2025-02-14",
            "days_count": 30,
            "pawn_amount": 5000,
            "total_redemption": 5500,
        }
        
        customer = {
            "first_name": "ทดสอบ",
            "last_name": "ระบบ",
            "age": 25,
            "phone": "08-1234-5678",
            "id_card": "1-2345-67890-12-3",
            "house_number": "123",
            "street": "ถนนทดสอบ",
            "subdistrict": "แขวงทดสอบ",
            "district": "เขตทดสอบ",
            "province": "กรุงเทพมหานคร",
            "postcode": "10000",
        }
        
        product = {
            "brand": "Samsung",
            "name": "Galaxy S24",
            "color": "ดำ",
            "imei1": "123456789012345",
            "serial_number": "SN123456789",
            "condition": "ดีมาก",
            "accessories": "สายชาร์จและกล่องเดิม",
        }
        
        shop = {
            "name": "ร้านทดสอบ",
            "branch": "สาขาทดสอบ",
            "address": "123 ถ.ทดสอบ ต.ทดสอบ อ.ทดสอบ จ.ทดสอบ 10000",
            "witness_name": "พยานทดสอบ",
        }
        
        # Generate PDF
        output_file = "test_contract.pdf"
        result = generate_pawn_ticket_pdf_data(contract, customer, product, shop, output_file)
        
        if os.path.exists(result):
            print(f"✅ PDF generation successful!")
            print(f"📄 Output file: {result}")
            print(f"📏 File size: {os.path.getsize(result)} bytes")
            return True
        else:
            print("❌ PDF generation failed - output file not found")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing PDF generation...")
    print("=" * 50)
    
    success = test_pdf_generation()
    
    if success:
        print("=" * 50)
        print("🎉 All tests passed! PDF generation is working correctly.")
    else:
        print("=" * 50)
        print("💥 Tests failed! Please check the error messages above.")
        sys.exit(1)
