# สรุปการแก้ไขปัญหา UNIQUE constraint failed: contracts.contract_number

## ภาพรวมปัญหา

ข้อผิดพลาด `UNIQUE constraint failed: contracts.contract_number` เกิดขึ้นเมื่อระบบพยายามสร้างสัญญาใหม่ด้วยเลขที่สัญญาที่ซ้ำกับที่มีอยู่ในฐานข้อมูลแล้ว

## สาเหตุของปัญหา

1. **การแก้ไขข้อมูลสัญญาเดิม**: เมื่อผู้ใช้แก้ไขข้อมูลสัญญาแล้วพยายามบันทึก ระบบเรียกใช้ `create_contract()` แทนที่จะเป็น `update_contract()`
2. **การโหลดสัญญาเดิม**: ไม่มีฟังก์ชันสำหรับโหลดสัญญาเดิมมาแก้ไข
3. **การตรวจสอบสถานะ**: ไม่มีการตรวจสอบว่าสัญญานั้นเป็นสัญญาใหม่หรือสัญญาเดิม

## การแก้ไขที่ทำ

### 1. เพิ่มฟังก์ชัน `update_contract` ใน `database.py`

```python
def update_contract(self, contract_data: Dict) -> int:
    """อัพเดทสัญญา"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE contracts SET
                customer_id = ?, product_id = ?, pawn_amount = ?,
                interest_rate = ?, fee_amount = ?, withholding_tax_rate = ?, 
                withholding_tax_amount = ?, total_paid = ?, total_redemption = ?, 
                start_date = ?, end_date = ?, days_count = ?
            WHERE id = ?
        ''', (
            contract_data['customer_id'],
            contract_data['product_id'],
            contract_data['pawn_amount'],
            contract_data['interest_rate'],
            contract_data['fee_amount'],
            contract_data.get('withholding_tax_rate', 0.0),
            contract_data.get('withholding_tax_amount', 0.0),
            contract_data['total_paid'],
            contract_data['total_redemption'],
            contract_data['start_date'],
            contract_data['end_date'],
            contract_data['days_count'],
            contract_data['id']
        ))
        
        conn.commit()
        return contract_data['id']
```

### 2. ปรับปรุงฟังก์ชัน `save_contract` ใน `contract_form.py`

```python
def save_contract(self):
    """บันทึกสัญญา"""
    # ... ตรวจสอบข้อมูลที่จำเป็น ...
    
    try:
        # ตรวจสอบว่ามีสัญญาอยู่แล้วหรือไม่
        if hasattr(self, 'current_contract') and self.current_contract:
            # อัพเดทสัญญาเดิม
            contract_data['id'] = self.current_contract['id']
            contract_id = self.db.update_contract(contract_data)
            action_message = "อัพเดทสัญญาเรียบร้อย"
        else:
            # สร้างสัญญาใหม่
            contract_id = self.db.create_contract(contract_data)
            action_message = "บันทึกสัญญาเรียบร้อย"
        
        # ... บันทึกข้อมูลการต่อดอก ...
        
        QMessageBox.information(self, "สำเร็จ", action_message)
        self.accept()
        
    except Exception as e:
        QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
```

### 3. เพิ่มฟังก์ชัน `load_existing_contract` สำหรับโหลดสัญญาเดิม

```python
def load_existing_contract(self):
    """โหลดสัญญาเดิมมาแก้ไข"""
    try:
        # สร้าง dialog สำหรับค้นหาสัญญา
        from PySide6.QtWidgets import QInputDialog
        
        contract_number, ok = QInputDialog.getText(
            self, 
            "โหลดสัญญาเดิม", 
            "กรุณากรอกเลขที่สัญญาที่ต้องการแก้ไข:"
        )
        
        if ok and contract_number.strip():
            # ค้นหาสัญญาในฐานข้อมูล
            contract = self.db.get_contract_by_number(contract_number.strip())
            
            if contract:
                # ตั้งค่า current_contract
                self.current_contract = contract
                
                # โหลดข้อมูลสัญญา
                self.load_contract_data(contract)
                
                # โหลดข้อมูลลูกค้าและสินค้า
                # ... โหลดข้อมูลเพิ่มเติม ...
                
                QMessageBox.information(self, "สำเร็จ", f"โหลดสัญญา {contract_number} เรียบร้อยแล้ว")
            else:
                QMessageBox.warning(self, "ไม่พบข้อมูล", f"ไม่พบสัญญาเลขที่ {contract_number}")
                
    except Exception as e:
        QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
```

### 4. เพิ่มฟังก์ชัน `load_contract_data` สำหรับโหลดข้อมูลสัญญา

```python
def load_contract_data(self, contract_data):
    """โหลดข้อมูลสัญญา"""
    if contract_data:
        # โหลดข้อมูลสัญญา
        self.contract_number_edit.setText(contract_data.get('contract_number', ''))
        self.pawn_amount_spin.setValue(contract_data.get('pawn_amount', 0))
        self.interest_rate_spin.setValue(contract_data.get('interest_rate', 0))
        
        # โหลดวันที่และจำนวนวัน
        # ... โหลดข้อมูลเพิ่มเติม ...
        
        # คำนวณวันที่สิ้นสุดและยอดต่างๆ
        self.calculate_end_date()
        self.calculate_amounts()
```

### 5. เพิ่มฟังก์ชัน `clear_form` สำหรับล้างฟอร์ม

```python
def clear_form(self):
    """ล้างฟอร์ม"""
    self.current_customer = None
    self.current_product = None
    self.current_contract = None
    
    # ล้างข้อมูลสัญญา
    self.contract_number_edit.clear()
    self.pawn_amount_spin.setValue(0)
    # ... ล้างข้อมูลอื่นๆ ...
    
    # สร้างเลขที่สัญญาใหม่
    self.generate_new_contract_number()
    
    # คำนวณวันที่สิ้นสุดและยอดต่างๆ
    self.calculate_end_date()
    self.calculate_amounts()
```

### 6. เพิ่มปุ่มในส่วน UI

```python
# ปุ่มโหลดสัญญาเดิม
self.load_existing_contract_btn = QPushButton("โหลดสัญญาเดิม")
self.load_existing_contract_btn.clicked.connect(self.load_existing_contract)

# ปุ่มล้างฟอร์ม
self.clear_form_btn = QPushButton("ล้างฟอร์ม")
self.clear_form_btn.clicked.connect(self.clear_form)
```

## วิธีการใช้งาน

### การแก้ไขสัญญาเดิม

1. **คลิกปุ่ม "โหลดสัญญาเดิม"**
2. **กรอกเลขที่สัญญาที่ต้องการแก้ไข**
3. **ระบบจะโหลดข้อมูลสัญญา, ลูกค้า, และสินค้า**
4. **แก้ไขข้อมูลที่ต้องการ**
5. **คลิกปุ่ม "บันทึกสัญญา"** - ระบบจะอัพเดทข้อมูลเดิม

### การสร้างสัญญาใหม่

1. **คลิกปุ่ม "ล้างฟอร์ม"** เพื่อล้างข้อมูลทั้งหมด
2. **กรอกข้อมูลสัญญาใหม่**
3. **คลิกปุ่ม "บันทึกสัญญา"** - ระบบจะสร้างสัญญาใหม่

## การป้องกันปัญหา

1. **ตรวจสอบสถานะ**: ระบบตรวจสอบว่ามี `current_contract` หรือไม่
2. **เลือกฟังก์ชันที่เหมาะสม**: ใช้ `update_contract()` สำหรับสัญญาเดิม, `create_contract()` สำหรับสัญญาใหม่
3. **ข้อความแจ้งเตือน**: แสดงข้อความที่เหมาะสมสำหรับการอัพเดทหรือสร้างใหม่

## การทดสอบ

สร้างไฟล์ `test_contract_update.py` เพื่อทดสอบ:

1. **การสร้างสัญญาใหม่**
2. **การอัพเดทสัญญาเดิม**
3. **การป้องกันการสร้างสัญญาซ้ำ**
4. **การโหลดสัญญาเดิม**

## ประโยชน์ที่ได้

1. **แก้ไขปัญหา UNIQUE constraint**: ไม่เกิดข้อผิดพลาดเมื่อแก้ไขสัญญาเดิม
2. **ความยืดหยุ่น**: สามารถแก้ไขสัญญาเดิมหรือสร้างใหม่ได้
3. **การจัดการข้อมูล**: โหลดและแก้ไขข้อมูลได้อย่างถูกต้อง
4. **ประสบการณ์ผู้ใช้**: UI ที่ใช้งานง่ายและเข้าใจง่าย

## สรุป

การแก้ไขนี้ทำให้ระบบสามารถจัดการสัญญาได้อย่างครบถ้วน ทั้งการสร้างใหม่และการแก้ไขข้อมูลเดิม โดยไม่เกิดปัญหา UNIQUE constraint และให้ประสบการณ์ผู้ใช้ที่ดีขึ้น
