#!/bin/bash

echo "Building PawnShop App for Windows..."
echo

# Check if PyInstaller is installed
if ! python -m pip show pyinstaller > /dev/null 2>&1; then
    echo "Installing PyInstaller..."
    python -m pip install pyinstaller
fi

# Create build directories if they don't exist
mkdir -p dist
mkdir -p build

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/PawnShopApp
rm -rf build/PawnShopApp

# Check required files
echo "Checking required files..."
if [ ! -f "THSarabun.ttf" ]; then
    echo "ERROR: THSarabun.ttf not found!"
    exit 1
fi
if [ ! -f "THSarabun Bold.ttf" ]; then
    echo "ERROR: THSarabun Bold.ttf not found!"
    exit 1
fi
if [ ! -d "icons" ]; then
    echo "ERROR: icons folder not found!"
    exit 1
fi

echo
echo "Building Windows executable..."
pyinstaller PawnShopApp.spec --clean --noconfirm

echo
if [ -f "dist/PawnShopApp/PawnShopApp.exe" ]; then
    echo "Build completed successfully!"
    echo "Executable location: dist/PawnShopApp/PawnShopApp.exe"
    echo
    echo "Verifying build contents..."
    if [ -f "dist/PawnShopApp/THSarabun.ttf" ]; then
        echo "✓ Font files included"
    else
        echo "✗ Font files missing"
    fi
    if [ -d "dist/PawnShopApp/icons" ]; then
        echo "✓ Icon files included"
    else
        echo "✗ Icon files missing"
    fi
    echo
    echo "You can now distribute the entire 'dist/PawnShopApp' folder."
else
    echo "Build failed! Check the output above for errors."
fi
