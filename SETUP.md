# คู่มือการติดตั้งและใช้งาน โปรแกรมรับจำนำ อัญชัน

## การติดตั้ง

### 1. ความต้องการระบบ
- Python 3.8 หรือใหม่กว่า
- PySide6 (GUI Framework)
- SQLite3 (ฐานข้อมูล)

### 2. การติดตั้ง Dependencies
```bash
# ติดตั้ง PySide6
pip3 install PySide6

# หรือติดตั้งจาก requirements.txt
pip3 install -r requirements.txt
```

### 3. การรันโปรแกรม
```bash
# รันโปรแกรมหลัก
python3 main.py

# เพิ่มข้อมูลตัวอย่าง (เลือกใช้)
python3 test_data.py
```

## โครงสร้างโปรเจค

```
pownshop/
├── main.py              # โปรแกรมหลัก (GUI)
├── database.py          # ระบบฐานข้อมูล
├── utils.py             # ฟังก์ชันช่วยเหลือ
├── dialogs.py           # หน้าต่างต่างๆ
├── test_data.py         # สคริปต์เพิ่มข้อมูลตัวอย่าง
├── requirements.txt     # Dependencies
├── README.md           # คู่มือการใช้งาน
├── SETUP.md            # คู่มือการติดตั้ง
├── .gitignore          # ไฟล์ที่ไม่ต้องการ commit
└── pawnshop.db         # ฐานข้อมูล SQLite (สร้างอัตโนมัติ)
```

## การใช้งานครั้งแรก

### 1. รันโปรแกรม
```bash
python3 main.py
```

### 2. เพิ่มข้อมูลตัวอย่าง (แนะนำ)
```bash
python3 test_data.py
```

### 3. เริ่มใช้งาน
1. คลิก "สัญญาใหม่" เพื่อสร้างสัญญาใหม่
2. คลิก "ลูกค้า" > "เพิ่มลูกค้า" เพื่อเพิ่มลูกค้า
3. กรอกข้อมูลลูกค้าและสินค้า
4. บันทึกสัญญา

## ฟีเจอร์หลัก

### ระบบจัดการลูกค้า
- เพิ่ม/แก้ไขข้อมูลลูกค้า
- ค้นหาลูกค้าตามชื่อ, เลขบัตร, รหัส
- ตรวจสอบความถูกต้องของข้อมูล

### ระบบจัดการสินค้า
- เพิ่ม/แก้ไขข้อมูลสินค้า
- รองรับรูปภาพสินค้า
- จัดการคลังสินค้า

### ระบบสัญญา
- สร้างสัญญาขายฝากใหม่
- คำนวณดอกเบี้ยอัตโนมัติ
- ติดตามสถานะสัญญา

### ระบบการชำระ
- ชำระดอกเบี้ยรายเดือน
- ต่อดอกเบี้ย
- ไถ่ถอนสัญญา

### ระบบรายงาน
- รายงานประจำวัน
- รายงานประจำเดือน
- สัญญาที่ครบกำหนด

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. ไม่สามารถรันโปรแกรมได้
```bash
# ตรวจสอบ Python version
python3 --version

# ตรวจสอบ PySide6
pip3 list | grep PySide6

# ติดตั้งใหม่
pip3 install PySide6
```

#### 2. ฐานข้อมูลเสียหาย
```bash
# ลบฐานข้อมูลเก่า
rm pawnshop.db

# รันโปรแกรมใหม่ (จะสร้างฐานข้อมูลใหม่)
python3 main.py
```

#### 3. ไม่สามารถติดตั้ง PySide6
```bash
# อัปเดต pip
pip3 install --upgrade pip

# ติดตั้ง PySide6
pip3 install PySide6

# หรือใช้ conda
conda install -c conda-forge pyside6
```

### การ Debug
```bash
# รันด้วย verbose mode
python3 -v main.py

# ตรวจสอบ error logs
python3 main.py 2>&1 | tee error.log
```

## การพัฒนา

### การเพิ่มฟีเจอร์ใหม่
1. แก้ไขไฟล์ที่เกี่ยวข้อง
2. อัปเดตฐานข้อมูล (ถ้าจำเป็น)
3. ทดสอบฟีเจอร์ใหม่
4. อัปเดตเอกสาร

### การปรับแต่ง UI
- แก้ไขไฟล์ `main.py`
- ปรับแต่ง stylesheet
- เพิ่ม/ลบ widgets

### การเพิ่มรายงานใหม่
1. เพิ่มฟังก์ชันใน `database.py`
2. เพิ่ม UI ใน `main.py`
3. ทดสอบรายงาน

## การสำรองข้อมูล

### สำรองฐานข้อมูล
```bash
# สำรองฐานข้อมูล
cp pawnshop.db pawnshop_backup_$(date +%Y%m%d).db
```

### กู้คืนฐานข้อมูล
```bash
# กู้คืนฐานข้อมูล
cp pawnshop_backup_YYYYMMDD.db pawnshop.db
```

## การตั้งค่า

### การตั้งค่าพื้นฐาน
- อัตราดอกเบี้ยเริ่มต้น: 3.0%
- จำนวนวันเริ่มต้น: 30 วัน
- รูปแบบเลขที่สัญญา: 53-10-4-XXXX

### การตั้งค่าบริษัท
- ชื่อบริษัท: ร้านรับจำนำ อัญชัน
- ที่อยู่: (แก้ไขในฐานข้อมูล)
- เบอร์โทรศัพท์: (แก้ไขในฐานข้อมูล)

## การติดตั้งบนระบบต่างๆ

### macOS
```bash
# ใช้ Homebrew
brew install python3
pip3 install PySide6

# หรือใช้ conda
conda install -c conda-forge pyside6
```

### Ubuntu/Debian
```bash
# ติดตั้ง dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง PySide6
pip install PySide6
```

### Windows
```bash
# ดาวน์โหลด Python จาก python.org
# ติดตั้ง PySide6
pip install PySide6

# หรือใช้ conda
conda install -c conda-forge pyside6
```

## การสร้าง Executable

### ใช้ PyInstaller
```bash
# ติดตั้ง PyInstaller
pip3 install pyinstaller

# สร้าง executable
pyinstaller --onefile --windowed main.py

# ไฟล์ executable จะอยู่ใน dist/
```

### ใช้ cx_Freeze
```bash
# ติดตั้ง cx_Freeze
pip3 install cx_Freeze

# สร้าง setup.py
python3 setup.py build
```

## การทดสอบ

### รันข้อมูลตัวอย่าง
```bash
python3 test_data.py
```

### ทดสอบฟีเจอร์
1. สร้างสัญญาใหม่
2. เพิ่มลูกค้า
3. เพิ่มสินค้า
4. ชำระดอกเบี้ย
5. ไถ่ถอนสัญญา
6. ดูรายงาน

## การสนับสนุน

หากพบปัญหาในการติดตั้งหรือใช้งาน กรุณาติดต่อทีมพัฒนา

## ลิขสิทธิ์

โปรแกรมนี้พัฒนาเพื่อใช้งานภายในองค์กร กรุณาไม่แจกจ่ายหรือขายต่อโดยไม่ได้รับอนุญาต
