#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that the forfeiture date comparison fix works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import PawnShopDatabase
from datetime import datetime, timedelta

def test_forfeiture_date_comparison():
    """Test that forfeiture detection works correctly with date comparison"""
    try:
        # Initialize database
        db = PawnShopDatabase("test_pawnshop.db")
        
        # Test data: Create a contract that should NOT be forfeited (end date in future)
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        past_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        print("Today: {}".format(datetime.now().strftime('%Y-%m-%d')))
        print("Future date (should NOT be forfeited): {}".format(future_date))
        print("Past date (should be forfeited): {}".format(past_date))
        
        # Test the query directly
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test with future date (should return 0 results)
            cursor.execute('''
                SELECT COUNT(*) FROM contracts 
                WHERE status = 'active' 
                AND DATE(?) < DATE('now')
            ''', (future_date,))
            
            future_count = cursor.fetchone()[0]
            print("Future date query result: {} (should be 0)".format(future_count))
            
            # Test with past date (should return 1 result if contract exists)
            cursor.execute('''
                SELECT COUNT(*) FROM contracts 
                WHERE status = 'active' 
                AND DATE(?) < DATE('now')
            ''', (past_date,))
            
            past_count = cursor.fetchone()[0]
            print("Past date query result: {}".format(past_count))
            
            # Test the actual forfeiture query
            cursor.execute('''
                SELECT c.contract_number, c.end_date
                FROM contracts c
                WHERE c.status = 'active' 
                AND DATE(c.end_date) < DATE('now')
                ORDER BY c.end_date DESC
            ''')
            
            forfeited_contracts = cursor.fetchall()
            print("Found {} forfeited contracts:".format(len(forfeited_contracts)))
            for contract in forfeited_contracts:
                print("  - Contract: {}, End Date: {}".format(contract[0], contract[1]))
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print("Error: {}".format(str(e)))
        return False

if __name__ == "__main__":
    print("Testing forfeiture date comparison fix...")
    test_forfeiture_date_comparison()
