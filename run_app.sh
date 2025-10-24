#!/bin/bash
# Startup script for PawnShop application with proper environment setup

# Navigate to the application directory
cd "$(dirname "$0")"

# Activate Python 3 virtual environment
source venv3/bin/activate

# Set library path for WeasyPrint on macOS
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"

# Run the main application
python main.py
