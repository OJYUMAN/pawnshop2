# PDF3.py - ระบบสร้างสัญญาไถ่ถอน

## คำอธิบาย
`pdf3.py` เป็นระบบสำหรับสร้างเอกสาร PDF เกี่ยวกับการไถ่ถอนสินค้าที่ขายฝาก โดยมีฟังก์ชันหลัก 2 ฟังก์ชัน:

1. **`generate_redemption_contract_pdf()`** - สร้างสัญญาไถ่ถอน
2. **`generate_redemption_receipt_pdf()`** - สร้างใบเสร็จการไถ่ถอน

## ความต้องการของระบบ
- Python 3.6+
- ReportLab library
- ฟอนต์ภาษาไทย: `THSarabun.ttf` และ `THSarabun Bold.ttf`

## การติดตั้ง
```bash
pip install reportlab
```

## การใช้งาน

### 1. สร้างสัญญาไถ่ถอน
```python
from pdf3 import generate_redemption_contract_pdf

# ข้อมูลการไถ่ถอน
redemption_data = {
    'redemption_date': '2025-01-15',
    'deposit_date': '2024-10-15',
    'due_date': '2025-01-15',
    'total_days': 92,
    'principal_amount': 10000.00,
    'fee_amount': 500.00,
    'penalty_amount': 0.00,
    'discount_amount': 0.00,
    'redemption_amount': 10500.00
}

# ข้อมูลลูกค้า
customer_data = {
    'customer_code': 'C001',
    'first_name': 'สมชาย',
    'last_name': 'ใจดี',
    'phone': '0812345678',
    'id_card': '1234567890123',
    'house_number': '123',
    'street': 'ถนนสุขุมวิท',
    'subdistrict': 'คลองเตย',
    'district': 'เขตคลองเตย',
    'province': 'กรุงเทพมหานคร'
}

# ข้อมูลสินค้า
product_data = {
    'name': 'โทรศัพท์มือถือ',
    'brand': 'iPhone',
    'size': '6.1 นิ้ว',
    'weight': '174',
    'weight_unit': 'กรัม',
    'serial_number': 'SN123456789',
    'other_details': 'สีดำ 128GB'
}

# ข้อมูลสัญญาเดิม
original_contract_data = {
    'contract_number': 'C2024001',
    'start_date': '2024-10-15',
    'end_date': '2025-01-15',
    'days_count': 92,
    'pawn_amount': 10000.00,
    'interest_rate': 2.5,
    'estimated_value': 15000.00
}

# ข้อมูลร้านค้า
shop_data = {
    'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
    'branch': 'สาขาหล่มสัก',
    'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
}

# สร้างสัญญาไถ่ถอน
result = generate_redemption_contract_pdf(
    redemption_data=redemption_data,
    customer_data=customer_data,
    product_data=product_data,
    original_contract_data=original_contract_data,
    shop_data=shop_data,
    output_file='redemption_contract.pdf'
)

if result:
    print(f"สร้างสัญญาไถ่ถอนสำเร็จ: {result}")
else:
    print("เกิดข้อผิดพลาดในการสร้างสัญญาไถ่ถอน")
```

### 2. สร้างใบเสร็จการไถ่ถอน
```python
from pdf3 import generate_redemption_receipt_pdf

# สร้างใบเสร็จการไถ่ถอน
result = generate_redemption_receipt_pdf(
    redemption_data=redemption_data,
    customer_data=customer_data,
    product_data=product_data,
    original_contract_data=original_contract_data,
    shop_data=shop_data,
    output_file='redemption_receipt.pdf'
)

if result:
    print(f"สร้างใบเสร็จการไถ่ถอนสำเร็จ: {result}")
else:
    print("เกิดข้อผิดพลาดในการสร้างใบเสร็จการไถ่ถอน")
```

## โครงสร้างเอกสาร

### สัญญาไถ่ถอน
1. **ส่วนหัว** - ชื่อเอกสารและข้อมูลร้านค้า
2. **ข้อมูลสัญญาเดิม** - เลขที่สัญญา วันที่ จำนวนเงิน
3. **ข้อมูลการไถ่ถอน** - วันที่ไถ่ถอน จำนวนวันที่ฝาก
4. **ข้อมูลผู้ไถ่ถอน** - ข้อมูลลูกค้าและที่อยู่
5. **รายการทรัพย์สิน** - ข้อมูลสินค้าที่ไถ่ถอน
6. **สรุปการเงิน** - รายละเอียดการชำระเงิน
7. **เงื่อนไขการไถ่ถอน** - ข้อกำหนดและเงื่อนไข
8. **ลายเซ็น** - ลายเซ็นผู้เกี่ยวข้อง

### ใบเสร็จการไถ่ถอน
1. **ส่วนหัว** - ชื่อเอกสารและข้อมูลร้านค้า
2. **รายละเอียดการไถ่ถอน** - ข้อมูลสัญญาและวันที่
3. **รายละเอียดการชำระ** - จำนวนเงินต่างๆ
4. **ข้อมูลลูกค้า** - ชื่อและข้อมูลติดต่อ
5. **สินค้าที่ไถ่ถอน** - รายการสินค้า
6. **การชำระเงิน** - สถานะการชำระ
7. **ส่วนท้าย** - ข้อมูลระบบและเวลา

## การปรับแต่ง

### เปลี่ยนข้อมูลร้านค้า
แก้ไขในส่วน `shop_data` หรือส่งค่าใหม่ผ่านพารามิเตอร์

### เปลี่ยนฟอนต์
วางไฟล์ฟอนต์ `.ttf` ในโฟลเดอร์เดียวกับ `pdf3.py` และแก้ไขชื่อไฟล์ในโค้ด

### ปรับแต่ง Layout
แก้ไขค่าคงที่ในส่วนต้นของฟังก์ชัน:
- `LEFT_MARGIN` - ระยะขอบซ้าย
- `RIGHT_MARGIN` - ระยะขอบขวา
- `TOP_MARGIN` - ระยะขอบบน
- `BOTTOM_MARGIN` - ระยะขอบล่าง
- `LINE_HEIGHT` - ความสูงของบรรทัด
- `SECTION_SPACING` - ระยะห่างระหว่างส่วน

## การแก้ไขปัญหา

### ฟอนต์ไม่แสดงผล
- ตรวจสอบว่าไฟล์ฟอนต์อยู่ในโฟลเดอร์เดียวกัน
- ตรวจสอบชื่อไฟล์ฟอนต์ให้ถูกต้อง
- ตรวจสอบสิทธิ์การเข้าถึงไฟล์

### PDF ไม่สร้าง
- ตรวจสอบสิทธิ์การเขียนไฟล์ในโฟลเดอร์
- ตรวจสอบพื้นที่ว่างในดิสก์
- ตรวจสอบข้อมูลที่ส่งเข้าไปว่าครบถ้วนหรือไม่

### ข้อความภาษาไทยแสดงผิด
- ตรวจสอบการเข้ารหัสไฟล์ (UTF-8)
- ตรวจสอบฟอนต์ภาษาไทย
- ตรวจสอบ ReportLab version

## การใช้งานในระบบหลัก

### ใน RedemptionDialog
```python
# สร้างเฉพาะสัญญาไถ่ถอน
self.generate_redemption_contract_only()

# สร้างสัญญาไถ่ถอนและบันทึกการไถ่ถอน
self.confirm_redemption()
```

### การพิมพ์อัตโนมัติ
ระบบจะพิมพ์สัญญาไถ่ถอนอัตโนมัติเมื่อมีการไถ่ถอนจริง หรือผู้ใช้สามารถเลือกสร้างเฉพาะสัญญาได้

## หมายเหตุ
- ไฟล์ PDF จะถูกสร้างในโฟลเดอร์ปัจจุบันหากไม่ระบุ `output_file`
- ชื่อไฟล์จะถูกสร้างอัตโนมัติตามรูปแบบ: `redemption_contract_{contract_number}_{date}.pdf`
- ระบบรองรับการพิมพ์อัตโนมัติผ่าน `lpr` (macOS/Linux) และ `start /print` (Windows)
