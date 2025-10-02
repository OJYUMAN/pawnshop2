# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Add the current directory to the path
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
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
