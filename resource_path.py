# -*- coding: utf-8 -*-
"""
Resource path utilities for PyInstaller bundled applications
"""
import sys
import os

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for both dev and PyInstaller bundle
    
    Args:
        relative_path (str): Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in development mode
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_font_path(font_name):
    """
    Get the correct path for font files
    
    Args:
        font_name (str): Name of the font file
        
    Returns:
        str: Absolute path to the font file
    """
    return resource_path(font_name)

def get_icon_path(icon_name):
    """
    Get the correct path for icon files
    
    Args:
        icon_name (str): Name/path of the icon file
        
    Returns:
        str: Absolute path to the icon file
    """
    if icon_name.startswith('icons/'):
        return resource_path(icon_name)
    else:
        return resource_path(f'icons/{icon_name}')

def get_database_path(db_name='pawnshop.db'):
    """
    Get the correct path for database file
    
    Args:
        db_name (str): Name of the database file
        
    Returns:
        str: Absolute path to the database file
    """
    return resource_path(db_name)

def get_config_path(config_name='config.json'):
    """
    Get the correct path for config file
    
    Args:
        config_name (str): Name of the config file
        
    Returns:
        str: Absolute path to the config file
    """
    return resource_path(config_name)

def ensure_output_directory(output_path):
    """
    Ensure the output directory exists
    
    Args:
        output_path (str): Path to create directory for
        
    Returns:
        str: The directory path
    """
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory
