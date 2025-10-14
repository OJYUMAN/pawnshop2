#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that the fee_amount field fix works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import PawnShopDatabase

def test_contract_creation():
    """Test creating a contract with fee_amount field"""
    try:
        # Initialize database
        db = PawnShopDatabase("test_pawnshop.db")
        
        # Test contract data with fee_amount
        contract_data = {
            'contract_number': 'TEST001',
            'customer_id': 1,
            'product_id': 1,
            'pawn_amount': 1000.0,
            'fee_amount': 0.0,  # This should now work
            'total_paid': 1000.0,
            'total_redemption': 1000.0,
            'start_date': '2024-01-01',
            'end_date': '2024-02-01',
            'days_count': 30
        }
        
        # Try to create contract
        contract_id = db.create_contract(contract_data)
        print("Contract created successfully with ID: {}".format(contract_id))
        
        # Clean up test database
        os.remove("test_pawnshop.db")
        print("Test completed successfully - fee_amount error is fixed!")
        return True
        
    except Exception as e:
        print("Error: {}".format(str(e)))
        return False

if __name__ == "__main__":
    print("Testing fee_amount field fix...")
    success = test_contract_creation()
    sys.exit(0 if success else 1)
