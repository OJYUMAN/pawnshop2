@echo off
echo Building PawnShop App for Windows...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Create build directory if it doesn't exist
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist\PawnShopApp" rmdir /s /q "dist\PawnShopApp"
if exist "build\PawnShopApp" rmdir /s /q "build\PawnShopApp"

REM Check required files
echo Checking required files...
if not exist "THSarabun.ttf" (
    echo ERROR: THSarabun.ttf not found!
    pause
    exit /b 1
)
if not exist "THSarabun Bold.ttf" (
    echo ERROR: THSarabun Bold.ttf not found!
    pause
    exit /b 1
)
if not exist "icons" (
    echo ERROR: icons folder not found!
    pause
    exit /b 1
)

echo.
echo Building Windows executable...
pyinstaller PawnShopApp.spec --clean --noconfirm

echo.
if exist "dist\PawnShopApp\PawnShopApp.exe" (
    echo Build completed successfully!
    echo Executable location: dist\PawnShopApp\PawnShopApp.exe
    echo.
    echo Verifying build contents...
    if exist "dist\PawnShopApp\THSarabun.ttf" (
        echo ✓ Font files included
    ) else (
        echo ✗ Font files missing
    )
    if exist "dist\PawnShopApp\icons" (
        echo ✓ Icon files included
    ) else (
        echo ✗ Icon files missing
    )
    echo.
    echo You can now distribute the entire 'dist\PawnShopApp' folder.
) else (
    echo Build failed! Check the output above for errors.
)

pause
