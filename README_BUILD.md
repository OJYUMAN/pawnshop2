# การสร้าง Windows Executable สำหรับ PawnShop App

## ข้อกำหนดเบื้องต้น (Prerequisites)

1. **Python 3.8+** ติดตั้งบนระบบ
2. **Virtual Environment** (แนะนำ)
3. **Dependencies** ทั้งหมดติดตั้งแล้ว

## วิธีการติดตั้ง Dependencies

```bash
# สร้าง virtual environment (ถ้ายังไม่มี)
python -m venv venv

# เปิดใช้งาน virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

## วิธีการ Build Windows App

### วิธีที่ 1: ใช้ Build Script (แนะนำ)

**สำหรับ Windows:**
```cmd
build_windows.bat
```

**สำหรับ macOS/Linux:**
```bash
chmod +x build_windows.sh
./build_windows.sh
```

### วิธีที่ 2: ใช้คำสั่ง PyInstaller โดยตรง

```bash
# ติดตั้ง PyInstaller (ถ้ายังไม่มี)
pip install pyinstaller

# ลบ build เก่า
rm -rf dist/PawnShopApp build/PawnShopApp

# Build แบบ directory (หลายไฟล์)
pyinstaller PawnShopApp.spec --clean --noconfirm

# หรือ Build แบบ one-file (ไฟล์เดียว) - แก้ไข spec ก่อน
# ต้อง uncomment ส่วน one-file ใน PawnShopApp.spec
```

## ผลลัพธ์หลัง Build

หลังจาก build เสร็จ คุณจะได้:

- **Directory Build**: `dist/PawnShopApp/` - โฟลเดอร์ที่มีไฟล์ทั้งหมด
- **Executable**: `dist/PawnShopApp/PawnShopApp.exe` - ไฟล์หลัก

## การแจกจ่าย (Distribution)

1. **แบบ Directory**: แจกจ่ายทั้งโฟลเดอร์ `dist/PawnShopApp/`
2. **แบบ ZIP**: บีบอัดโฟลเดอร์ `dist/PawnShopApp/` เป็นไฟล์ ZIP

## การแก้ไขปัญหา (Troubleshooting)

### ปัญหาที่พบบ่อย:

1. **Missing modules**: เพิ่ม module ใน `hiddenimports` ใน PawnShopApp.spec
2. **Missing files**: เพิ่มไฟล์ใน `datas` ใน PawnShopApp.spec
3. **Font issues**: ตรวจสอบว่าไฟล์ฟอนต์ถูก copy ไปด้วย
4. **Icon ไม่แสดง**: ตรวจสอบว่าโฟลเดอร์ `icons/` ถูก copy ไปด้วย
5. **PDF สร้างไม่ได้**: ตรวจสอบว่าไฟล์ฟอนต์และ PDF modules ถูก include

### การแก้ไขปัญหาเฉพาะ:

**ปัญหา Icons ไม่แสดง:**
- ตรวจสอบว่าไฟล์ `resource_path.py` ถูก include
- ตรวจสอบว่าโฟลเดอร์ `icons/` อยู่ใน `datas` ของ spec file
- ใช้ฟังก์ชัน `get_icon_path()` แทนการใช้ path โดยตรง

**ปัญหา PDF สร้างไม่ได้:**
- ตรวจสอบว่าไฟล์ฟอนต์ `THSarabun.ttf` และ `THSarabun Bold.ttf` ถูก include
- ตรวจสอบว่า modules `pdf.py`, `pdf2.py`, `pdf3.py` ถูก include
- ใช้ฟังก์ชัน `get_font_path()` แทนการใช้ path โดยตรง

### คำสั่งเพิ่มเติม:

```bash
# ดู dependencies ที่ PyInstaller ตรวจพบ
pyi-makespec --onefile main.py

# วิเคราะห์ imports
pyi-archive_viewer dist/PawnShopApp/PawnShopApp.exe

# Debug mode
pyinstaller PawnShopApp.spec --debug=all
```

## ข้อมูลสำคัญ

- **ขนาดไฟล์**: ประมาณ 200-300 MB (รวม PySide6)
- **เวลา Build**: 2-5 นาที (ขึ้นกับความเร็วเครื่อง)
- **Platform**: Windows 10/11 (64-bit)

## การปรับแต่งเพิ่มเติม

### เพิ่ม Icon:
```python
# ใน PawnShopApp.spec
icon='path/to/icon.ico'
```

### เพิ่ม Version Info:
```python
# ใน PawnShopApp.spec
version='version_info.txt'
```

### Build แบบ One-File:
- Uncomment ส่วน one-file EXE ใน PawnShopApp.spec
- Comment ส่วน COLLECT
