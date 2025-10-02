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

echo
echo "Building Windows executable..."
pyinstaller PawnShopApp.spec --clean --noconfirm

echo
if [ -f "dist/PawnShopApp/PawnShopApp.exe" ]; then
    echo "Build completed successfully!"
    echo "Executable location: dist/PawnShopApp/PawnShopApp.exe"
    echo
    echo "You can now distribute the entire 'dist/PawnShopApp' folder."
else
    echo "Build failed! Check the output above for errors."
fi
