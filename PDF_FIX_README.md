# PDF Generation Fix for macOS

## ปัญหาที่แก้ไข
ข้อผิดพลาด: `cannot load library 'libgobject-2.0-0'` เมื่อพยายามสร้างหรือพรีวิว PDF

## สาเหตุ
- WeasyPrint ต้องการไลบรารีระบบ GTK (libgobject-2.0-0) ที่ไม่สามารถหาได้ใน macOS
- ไลบรารีที่จำเป็นไม่ได้อยู่ใน PATH ที่ระบบสามารถหาได้

## การแก้ไขที่ทำ

### 1. ใช้ Python 3 Environment
- เปลี่ยนจาก `venv` (Python 2.7) เป็น `venv3` (Python 3.13)
- WeasyPrint ต้องการ Python 3 ขึ้นไป

### 2. ติดตั้ง Dependencies
```bash
# ติดตั้งไลบรารีระบบ
brew install cairo pango gdk-pixbuf libffi gtk+3 glib

# ติดตั้ง WeasyPrint ใน Python 3 environment
source venv3/bin/activate
pip install weasyprint
```

### 3. ตั้งค่า Environment Variables
เพิ่ม environment variables ในไฟล์ `main.py` และ `pdf.py`:
```python
# Set up environment for WeasyPrint on macOS
if sys.platform == "darwin":  # macOS
    os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib:" + os.environ.get("DYLD_LIBRARY_PATH", "")
    os.environ["PKG_CONFIG_PATH"] = "/opt/homebrew/lib/pkgconfig:" + os.environ.get("PKG_CONFIG_PATH", "")
```

### 4. Scripts ที่สร้างขึ้น
- `setup_env.sh` - สำหรับตั้งค่า environment
- `run_app.sh` - สำหรับรันแอปพลิเคชัน (มี environment setup อยู่แล้ว)
- `test_pdf.py` - สำหรับทดสอบการสร้าง PDF

## วิธีใช้งาน

### รันแอปพลิเคชัน
```bash
./run_app.sh
```

### ทดสอบ PDF Generation
```bash
source venv3/bin/activate
python test_pdf.py
```

### รันโดยตรง
```bash
source venv3/bin/activate
python main.py
```

## การตรวจสอบ
- ✅ WeasyPrint import สำเร็จ
- ✅ PDF generation ทำงานได้
- ✅ ไฟล์ PDF ถูกสร้างขึ้นและมีขนาดที่เหมาะสม
- ✅ แอปพลิเคชันหลักสามารถ import ได้โดยไม่มีข้อผิดพลาด

## หมายเหตุ
- การแก้ไขนี้จะทำงานเฉพาะบน macOS เท่านั้น
- ระบบจะตรวจสอบ platform และตั้งค่า environment variables อัตโนมัติ
- ไม่จำเป็นต้องตั้งค่า environment variables ด้วยตนเองอีกต่อไป
