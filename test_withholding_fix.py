#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that withholding_tax_rate_spin attribute exists
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from main import PawnShopUI

def test_withholding_tax_spin():
    """Test that withholding_tax_rate_spin attribute exists"""
    app = QApplication(sys.argv)
    
    try:
        # Create the UI
        ui = PawnShopUI()
        
        # Check if the attribute exists
        if hasattr(ui, 'withholding_tax_rate_spin'):
            print("✅ SUCCESS: withholding_tax_rate_spin attribute exists")
            print("   Type: " + str(type(ui.withholding_tax_rate_spin)))
            print("   Value: " + str(ui.withholding_tax_rate_spin.value()))
            return True
        else:
            print("❌ ERROR: withholding_tax_rate_spin attribute does not exist")
            return False
            
    except Exception as e:
        print("❌ ERROR: Exception occurred: " + str(e))
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    success = test_withholding_tax_spin()
    sys.exit(0 if success else 1)
