# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import glob
from PyInstaller.utils.hooks import collect_dynamic_libs

# Add the current directory to the path
block_cipher = None

# Collect MSYS2 DLLs for WeasyPrint
msys2_dlls = []
msys2_path = r"C:\msys64\ucrt64\bin"
if os.path.exists(msys2_path):
    # Common DLLs needed for WeasyPrint on Windows
    dll_patterns = [
        "libcairo*.dll",
        "libpango*.dll", 
        "libgdk_pixbuf*.dll",
        "libffi*.dll",
        "libgobject*.dll",
        "libglib*.dll",
        "libpixman*.dll",
        "libpng*.dll",
        "libfreetype*.dll",
        "libfontconfig*.dll",
        "libexpat*.dll",
        "libharfbuzz*.dll",
        "libfribidi*.dll",
        "libthai*.dll",
        "libintl*.dll",
        "libiconv*.dll",
        "libbz2*.dll",
        "libz*.dll",
        "liblzma*.dll",
        "libxml2*.dll",
        "libxslt*.dll",
        "libexslt*.dll",
        "libgcrypt*.dll",
        "libgpg-error*.dll",
        "libnettle*.dll",
        "libhogweed*.dll",
        "libgmp*.dll",
        "libwinpthread*.dll",
        "libgcc_s_seh*.dll",
        "libstdc++*.dll"
    ]
    
    for pattern in dll_patterns:
        dll_files = glob.glob(os.path.join(msys2_path, pattern))
        for dll_file in dll_files:
            msys2_dlls.append((dll_file, "bin"))

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=msys2_dlls,
    datas=[
        ('icons', 'icons'),
        ('THSarabun.ttf', '.'),
        ('THSarabun Bold.ttf', '.'),
        ('config.json', '.'),
        ('pawnshop.db', '.'),
        ('product_images', 'product_images'),
        ('pdf.py', '.'),
        ('pdf2.py', '.'),
        ('pdf3.py', '.'),
        ('resource_path.py', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'reportlab.pdfbase.ttfonts',
        'reportlab.pdfbase.pdfmetrics',
        'reportlab.platypus',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'reportlab.pdfgen.canvas',
        'reportlab.lib.enums',
        'requests',
        'json',
        'sqlite3',
        'datetime',
        'tempfile',
        'shutil',
        'PIL',
        'PIL.Image',
        'pyscard',
        'resource_path',
        'pdf',
        'pdf2', 
        'pdf3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PawnShopApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=None,  # You can add an .ico file here for Windows
    version=None,  # You can add version info here
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PawnShopApp',
)

# Optional: Create a one-file executable (uncomment if needed)
# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     [],
#     name='PawnShopApp',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=False,
#     disable_windowed_traceback=False,
#     icon=None,
#     version=None,
# )
