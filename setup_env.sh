#!/bin/bash
# Environment setup script for PawnShop app on macOS
# This script sets up the necessary environment variables for WeasyPrint to work

# Set up library paths for WeasyPrint dependencies
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"

# Activate Python 3 virtual environment
source venv3/bin/activate

echo "Environment set up successfully!"
echo "DYLD_LIBRARY_PATH: $DYLD_LIBRARY_PATH"
echo "PKG_CONFIG_PATH: $PKG_CONFIG_PATH"
echo "Python version: $(python --version)"
echo ""
echo "You can now run your application with:"
echo "  python main.py"
echo "  or"
echo "  python pdf.py"
