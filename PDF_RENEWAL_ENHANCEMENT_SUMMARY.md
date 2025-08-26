# สรุปการปรับปรุงข้อมูลการต่อดอกใน PDF

## ภาพรวม

ได้ปรับปรุงไฟล์ `pdf.py` เพื่อแสดงข้อมูลการต่อดอกที่ละเอียดและครบถ้วนมากขึ้น เมื่อลูกค้าได้ต่อดอกแล้ว ข้อมูลจะถูกแสดงใน PDF อย่างชัดเจน

## การปรับปรุงที่ทำ

### 1. ส่วนประวัติการต่อดอก

**เดิม**: แสดงข้อมูลการต่อดอกแบบพื้นฐาน
```python
# ต่อดอกเมื่อครบกำหนด
if renewal_data:
    c.drawString(LEFT_MARGIN + 20, y_pos, "ต่อดอกเมื่อครบกำหนด:")
    # แสดงข้อมูลพื้นฐาน
```

**ใหม่**: แสดงข้อมูลการต่อดอกแบบละเอียด
```python
# ประวัติการต่อดอก
if renewal_data:
    c.drawString(LEFT_MARGIN + 20, y_pos, "ประวัติการต่อดอก:")
    
    # สรุปข้อมูลการต่อดอก
    total_renewal_fees = sum(renewal.get('total_amount', 0) for renewal in renewal_data)
    total_renewal_days = sum(renewal.get('extension_days', 0) for renewal in renewal_data)
    renewal_count = len(renewal_data)
    
    # แสดงสรุป
    c.drawString(LEFT_MARGIN + 20, y_pos, f"จำนวนครั้งที่ต่อดอก: {renewal_count} ครั้ง")
    c.drawString(LEFT_MARGIN + 280, y_pos, f"รวมค่าธรรมเนียม: {total_renewal_fees:,.2f} บาท")
    c.drawString(LEFT_MARGIN + 20, y_pos, f"จำนวนวันรวมที่ต่อดอก: {total_renewal_days} วัน")
    
    # แสดงรายละเอียดแต่ละครั้ง
    for i, renewal in enumerate(renewal_data, 1):
        # ข้อมูลการต่อดอกแต่ละครั้ง
        renewal_date = convert_to_thai_date(renewal.get('renewal_date', 'N/A'))
        extension_days = renewal.get('extension_days', 0)
        fee_amount = renewal.get('fee_amount', 0)
        penalty_amount = renewal.get('penalty_amount', 0)
        discount_amount = renewal.get('discount_amount', 0)
        total_amount = renewal.get('total_amount', 0)
        current_due_date = convert_to_thai_date(renewal.get('current_due_date', 'N/A'))
        new_due_date = convert_to_thai_date(renewal.get('new_due_date', 'N/A'))
        
        # แสดงรายละเอียด
        c.drawString(LEFT_MARGIN + 40, y_pos, f"วันที่ต่อดอก: {renewal_date}")
        c.drawString(LEFT_MARGIN + 280, y_pos, f"ต่อดอก: {extension_days} วัน")
        c.drawString(LEFT_MARGIN + 40, y_pos, f"วันครบกำหนดเดิม: {current_due_date}")
        c.drawString(LEFT_MARGIN + 280, y_pos, f"วันครบกำหนดใหม่: {new_due_date}")
        
        # แสดงค่าใช้จ่าย
        if fee_amount > 0 or penalty_amount > 0 or discount_amount > 0:
            c.drawString(LEFT_MARGIN + 40, y_pos, f"ค่าธรรมเนียม: {fee_amount:,.2f} บาท")
            c.drawString(LEFT_MARGIN + 280, y_pos, f"ค่าปรับ: {penalty_amount:,.2f} บาท")
            if discount_amount > 0:
                c.drawString(LEFT_MARGIN + 40, y_pos, f"ส่วนลด: {discount_amount:,.2f} บาท")
            c.drawString(LEFT_MARGIN + 40, y_pos, f"รวม: {total_amount:,.2f} บาท")
```

### 2. ส่วนเงื่อนไขสำคัญ

**เดิม**: แสดงเงื่อนไขการต่อดอกแบบทั่วไป
```python
if renewal_data:
    important_terms.append("• สามารถต่อดอกได้เมื่อครบกำหนด โดยชำระดอกเบี้ยและค่าธรรมเนียมตามที่กำหนด")
    important_terms.append("• การต่อดอกจะขยายระยะเวลาการฝากตามจำนวนวันที่ต่อดอก")
```

**ใหม่**: แสดงเงื่อนไขการต่อดอกแบบเฉพาะเจาะจง
```python
if renewal_data:
    total_renewal_fees = sum(renewal.get('total_amount', 0) for renewal in renewal_data)
    total_renewal_days = sum(renewal.get('extension_days', 0) for renewal in renewal_data)
    
    important_terms.append(f"• ได้ทำการต่อดอกแล้ว {len(renewal_data)} ครั้ง รวม {total_renewal_days} วัน")
    important_terms.append(f"• ค่าธรรมเนียมการต่อดอกรวม: {total_renewal_fees:,.2f} บาท")
    important_terms.append("• การต่อดอกจะขยายระยะเวลาการฝากตามจำนวนวันที่ต่อดอก")
    important_terms.append("• ยอดไถ่ถอนรวมจะรวมค่าธรรมเนียมการต่อดอกทั้งหมด")
else:
    important_terms.append("• สามารถต่อดอกได้เมื่อครบกำหนด โดยชำระดอกเบี้ยและค่าธรรมเนียมตามที่กำหนด")
    important_terms.append("• การต่อดอกจะขยายระยะเวลาการฝากตามจำนวนวันที่ต่อดอก")
```

### 3. ส่วน Summary Box

**เดิม**: แสดงข้อมูลพื้นฐานแบบคงที่
```python
c.rect(LEFT_MARGIN, summary_box_y - 40, RIGHT_MARGIN - LEFT_MARGIN, 35, stroke=1, fill=0)
c.drawCentredString(width / 2.0, summary_box_y - 15, f"ยอดไถ่ถอน: {total_redemption:,.2f} บาท")
c.drawCentredString(width / 2.0, summary_box_y - 30, f"กำหนดไถ่ถอนภายในวันที่: {thai_end_date}")
```

**ใหม่**: แสดงข้อมูลแบบปรับขนาดตามข้อมูลการต่อดอก
```python
# คำนวณขนาดของ Summary Box ตามข้อมูลการต่อดอก
box_height = 35
if renewal_data:
    box_height = 60  # เพิ่มความสูงถ้ามีข้อมูลการต่อดอก

c.rect(LEFT_MARGIN, summary_box_y - box_height, RIGHT_MARGIN - LEFT_MARGIN, box_height, stroke=1, fill=0)

# ข้อมูลพื้นฐาน
c.drawCentredString(width / 2.0, summary_box_y - 15, f"ยอดไถ่ถอน: {total_redemption:,.2f} บาท")
c.drawCentredString(width / 2.0, summary_box_y - 30, f"กำหนดไถ่ถอนภายในวันที่: {thai_end_date}")

# ข้อมูลการต่อดอก (ถ้ามี)
if renewal_data:
    total_renewal_fees = sum(renewal.get('total_amount', 0) for renewal in renewal_data)
    total_renewal_days = sum(renewal.get('extension_days', 0) for renewal in renewal_data)
    
    c.setFont("THSarabun", 12)
    c.drawCentredString(width / 2.0, summary_box_y - 45, f"ต่อดอกแล้ว {len(renewal_data)} ครั้ง รวม {total_renewal_days} วัน")
    c.drawCentredString(width / 2.0, summary_box_y - 55, f"ค่าธรรมเนียมการต่อดอก: {total_renewal_fees:,.2f} บาท")
```

## ข้อมูลที่แสดงใน PDF

### เมื่อไม่มีข้อมูลการต่อดอก
- แสดงเงื่อนไขการต่อดอกแบบทั่วไป
- Summary Box ขนาดปกติ (35 pixels)

### เมื่อมีข้อมูลการต่อดอก
- **สรุปข้อมูลการต่อดอก**:
  - จำนวนครั้งที่ต่อดอก
  - รวมค่าธรรมเนียม
  - จำนวนวันรวมที่ต่อดอก

- **รายละเอียดการต่อดอกแต่ละครั้ง**:
  - ครั้งที่ (ลำดับการต่อดอก)
  - วันที่ต่อดอก
  - จำนวนวันที่ต่อดอก
  - วันครบกำหนดเดิม
  - วันครบกำหนดใหม่
  - ค่าธรรมเนียม
  - ค่าปรับ (ถ้ามี)
  - ส่วนลด (ถ้ามี)
  - ยอดรวม

- **เงื่อนไขสำคัญ**:
  - จำนวนครั้งและวันรวมที่ต่อดอก
  - ค่าธรรมเนียมการต่อดอกรวม
  - ข้อกำหนดการต่อดอก

- **Summary Box ขยาย**:
  - ขนาดเพิ่มเป็น 60 pixels
  - แสดงข้อมูลการต่อดอกเพิ่มเติม

## การทดสอบ

สร้างไฟล์ทดสอบ `test_enhanced_pdf_renewal.py` เพื่อทดสอบ:

1. **การต่อดอกหลายครั้ง**: ทดสอบการแสดงข้อมูลการต่อดอก 3 ครั้ง
2. **การต่อดอกครั้งเดียว**: ทดสอบการแสดงข้อมูลการต่อดอก 1 ครั้ง
3. **ไม่มีข้อมูลการต่อดอก**: ทดสอบการแสดงเงื่อนไขแบบทั่วไป

## ประโยชน์ที่ได้

1. **ความชัดเจน**: แสดงข้อมูลการต่อดอกอย่างละเอียดและเข้าใจง่าย
2. **ความครบถ้วน**: รวมข้อมูลทุกครั้งที่ต่อดอก
3. **การคำนวณ**: แสดงสรุปยอดรวมค่าธรรมเนียมและจำนวนวัน
4. **การปรับขนาด**: Summary Box ปรับขนาดตามข้อมูลที่มี
5. **เงื่อนไขที่ชัดเจน**: แสดงเงื่อนไขการต่อดอกที่เฉพาะเจาะจง

## การใช้งาน

ข้อมูลการต่อดอกจะถูกแสดงใน PDF อัตโนมัติเมื่อ:

1. มีการส่งพารามิเตอร์ `renewal_data` ไปยังฟังก์ชัน `generate_pawn_ticket_from_data`
2. ข้อมูลใน `renewal_data` มีโครงสร้างที่ถูกต้อง
3. มีฟิลด์ที่จำเป็นครบถ้วน เช่น `renewal_count`, `extension_days`, `total_amount` เป็นต้น

## สรุป

การปรับปรุงนี้ทำให้ PDF แสดงข้อมูลการต่อดอกได้อย่างละเอียดและครบถ้วน ช่วยให้ผู้ใช้เข้าใจประวัติการต่อดอกของลูกค้าได้ชัดเจน และสามารถติดตามค่าใช้จ่ายการต่อดอกได้อย่างแม่นยำ
