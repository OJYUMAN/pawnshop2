# -*- coding: utf-8 -*-
"""
Test script to verify shop configuration integration with PDF generation
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from shop_config_loader import load_shop_config

def test_shop_config():
    """Test shop configuration loading"""
    print("Testing shop configuration loader...")
    
    # Load shop config
    config = load_shop_config()
    
    print("Shop configuration loaded successfully:")
    print("  Name: {}".format(config['name']))
    print("  Branch: {}".format(config['branch']))
    print("  Address: {}".format(config['address']))
    
    # Test that all required keys are present
    required_keys = ['name', 'branch', 'address']
    for key in required_keys:
        if key not in config:
            print("ERROR: Missing required key: {}".format(key))
            return False
        if not config[key]:
            print("ERROR: Empty value for key: {}".format(key))
            return False
    
    print("All required keys present and have values")
    return True

if __name__ == "__main__":
    success = test_shop_config()
    if success:
        print("\n✓ Shop configuration test passed!")
    else:
        print("\n✗ Shop configuration test failed!")
        sys.exit(1)
