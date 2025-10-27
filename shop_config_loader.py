# -*- coding: utf-8 -*-
"""
Utility module for loading shop configuration from JSON file
"""
import json
import os


def load_shop_config(config_file="shop_config.json"):
    """
    Load shop configuration from JSON file
    
    Args:
        config_file: Path to the JSON configuration file
        
    Returns:
        Dictionary containing shop information with keys:
        - name: Shop name
        - branch: Shop branch
        - address: Shop address
    """
    try:
        # Try to find the config file in the current directory
        if not os.path.isabs(config_file):
            config_path = os.path.join(os.path.dirname(__file__), config_file)
        else:
            config_path = config_file
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                return {
                    'name': config.get('shop_name', 'ร้าน ไอโปรโมบาย'),
                    'branch': config.get('shop_branch', 'สาขาหล่มสัก'),
                    'address': config.get('shop_address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'),
                    'tax_id': config.get('tax_id', '0-1234-56789-01-2'),
                    'phone': config.get('phone', '02-345-6789'),
                    'authorized_signer': config.get('authorized_signer', 'นายประเสริฐ ใจดี'),
                    'buyer_signer_name': config.get('buyer_signer_name', 'นายประเสริฐ ใจดี'),
                    'witness_name': config.get('witness_name', 'นางสาวมั่นใจ ถูกต้อง'),
                    'interest_rate': config.get('interest_rate', 10.0),
                    'auto_calculate_interest': config.get('auto_calculate_interest', True),
                    'default_paper_mode': config.get('default_paper_mode', 1)
                }
        else:
            print("Warning: Shop config file not found at {}, using defaults".format(config_path))
            return get_default_shop_config()
    except Exception as e:
        print("Error loading shop config: {}, using defaults".format(e))
        return get_default_shop_config()


def get_default_shop_config():
    """
    Get default shop configuration
    
    Returns:
        Dictionary with default shop information
    """
    return {
        'name': 'ร้าน ไอโปรโมบาย',
        'branch': 'สาขาหล่มสัก',
        'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110',
        'tax_id': '0-1234-56789-01-2',
        'phone': '02-345-6789',
        'authorized_signer': 'นายประเสริฐ ใจดี',
        'buyer_signer_name': 'นายประเสริฐ ใจดี',
        'witness_name': 'นางสาวมั่นใจ ถูกต้อง',
        'interest_rate': 10.0,
        'auto_calculate_interest': True,
        'default_paper_mode': 1  # 0=A4, 1=Half-A4 continuous
    }


def save_shop_config(shop_data, config_file="shop_config.json"):
    """
    Save shop configuration to JSON file
    
    Args:
        shop_data: Dictionary containing shop information
        config_file: Path to the JSON configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.isabs(config_file):
            config_path = os.path.join(os.path.dirname(__file__), config_file)
        else:
            config_path = config_file
            
        config = {
            'shop_name': shop_data.get('name', 'ร้าน ไอโปรโมบาย'),
            'shop_branch': shop_data.get('branch', 'สาขาหล่มสัก'),
            'shop_address': shop_data.get('address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'),
            'tax_id': shop_data.get('tax_id', '0-1234-56789-01-2'),
            'phone': shop_data.get('phone', '02-345-6789'),
            'authorized_signer': shop_data.get('authorized_signer', 'นายประเสริฐ ใจดี'),
            'buyer_signer_name': shop_data.get('buyer_signer_name', 'นายประเสริฐ ใจดี'),
            'witness_name': shop_data.get('witness_name', 'นางสาวมั่นใจ ถูกต้อง'),
            'interest_rate': shop_data.get('interest_rate', 10.0),
            'auto_calculate_interest': shop_data.get('auto_calculate_interest', True)
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Error saving shop config: {}".format(e))
        return False


if __name__ == "__main__":
    # Test the configuration loader
    config = load_shop_config()
    print("Loaded shop config:")
    for key, value in config.items():
        print("  {}: {}".format(key, value))
