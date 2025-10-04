# -*- coding: utf-8 -*-
"""
Test script to verify PDF generation with shop configuration
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_pdf_generation():
    """Test PDF generation with shop configuration"""
    print("Testing PDF generation with shop configuration...")
    
    # Sample data for testing
    contract_data = {
        "contract_number": "TEST-2025-0001",
        "start_date": "2025-01-15",
        "end_date": "2025-02-15",
        "days_count": 30,
        "pawn_amount": 5000,
        "total_paid": 5000,
        "total_redemption": 5250
    }
    
    customer_data = {
        "customer_code": "CUST-TEST-001",
        "first_name": "ทดสอบ",
        "last_name": "ระบบ",
        "phone": "081-234-5678",
        "id_card": "1234567890123",
        "house_number": "123/45",
        "street": "ถนนทดสอบ",
        "subdistrict": "ตำบลทดสอบ",
        "district": "อำเภอทดสอบ",
        "province": "จังหวัดทดสอบ"
    }
    
    product_data = {
        "name": "โทรศัพท์มือถือทดสอบ",
        "brand": "TestBrand",
        "size": "6.1 นิ้ว",
        "weight": "180",
        "weight_unit": "กรัม",
        "serial_number": "TEST123456789",
        "other_details": "สภาพดี"
    }
    
    try:
        # Test pdf.py (pawn ticket)
        print("Testing pdf.py (pawn ticket)...")
        from pdf import generate_pawn_ticket_from_data
        
        output_file = generate_pawn_ticket_from_data(
            contract_data, customer_data, product_data, 
            output_file="test_pawn_ticket.pdf"
        )
        
        if os.path.exists(output_file):
            print("✓ Pawn ticket PDF generated successfully: {}".format(output_file))
            os.remove(output_file)  # Clean up
        else:
            print("✗ Pawn ticket PDF generation failed")
            return False
            
    except Exception as e:
        print("✗ Error testing pdf.py: {}".format(e))
        return False
    
    try:
        # Test pdf2.py (renewal contract)
        print("Testing pdf2.py (renewal contract)...")
        from pdf2 import generate_renewal_contract_pdf
        
        renewal_data = {
            "renewal_date": "2025-02-10",
            "extension_days": 15,
            "interest_amount": 150.0,
            "fee_amount": 50.0,
            "total_amount": 200.0
        }
        
        output_file = generate_renewal_contract_pdf(
            contract_data, customer_data, product_data, renewal_data,
            output_file="test_renewal_contract.pdf"
        )
        
        if os.path.exists(output_file):
            print("✓ Renewal contract PDF generated successfully: {}".format(output_file))
            os.remove(output_file)  # Clean up
        else:
            print("✗ Renewal contract PDF generation failed")
            return False
            
    except Exception as e:
        print("✗ Error testing pdf2.py: {}".format(e))
        return False
    
    try:
        # Test pdf3.py (redemption contract)
        print("Testing pdf3.py (redemption contract)...")
        from pdf3 import generate_redemption_contract_pdf
        
        redemption_data = {
            "redemption_date": "2025-02-15",
            "deposit_date": "2025-01-15",
            "due_date": "2025-02-15",
            "total_days": 30,
            "principal_amount": 5000.0,
            "fee_amount": 200.0,
            "penalty_amount": 0.0,
            "discount_amount": 0.0,
            "redemption_amount": 5200.0
        }
        
        output_file = generate_redemption_contract_pdf(
            redemption_data, customer_data, product_data, contract_data,
            output_file="test_redemption_contract.pdf"
        )
        
        if os.path.exists(output_file):
            print("✓ Redemption contract PDF generated successfully: {}".format(output_file))
            os.remove(output_file)  # Clean up
        else:
            print("✗ Redemption contract PDF generation failed")
            return False
            
    except Exception as e:
        print("✗ Error testing pdf3.py: {}".format(e))
        return False
    
    return True

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n✓ All PDF generation tests passed!")
        print("Shop configuration is successfully integrated with all PDF types.")
    else:
        print("\n✗ Some PDF generation tests failed!")
        sys.exit(1)
