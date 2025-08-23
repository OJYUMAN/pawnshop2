# generate_pawn_ticket_v2_fixed.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from typing import Dict, Optional

def generate_pawn_ticket(output_file="pawn_ticket.pdf"):
    """
    Generates a formal pawn ticket PDF document with a centered header.
    Fixed version with no text overlapping issues.

    Args:
        output_file (str): The name of the output PDF file.
    """
    try:
        # Load the Thai Sarabun font.
        # Ensure the 'THSarabun.ttf' file is in the same directory as this script.
        font_path = 'THSarabun.ttf'
        bold_font_path = 'THSarabun Bold.ttf'

        if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
            print(f"Error: Font file not found.")
            print("Please make sure 'THSarabun.ttf' and 'THSarabun Bold.ttf' are in the same folder as the script.")
            return

        pdfmetrics.registerFont(TTFont('THSarabun', font_path))
        pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))

    except Exception as e:
        print(f"An error occurred while loading the font: {e}")
        return

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # --- Centered Header ---
    # The title "ใบขายฝาก" is now centered with a larger font size for emphasis.
    c.setFont("THSarabun-Bold", 24)
    c.drawCentredString(width / 2.0, height - 60, "ใบขายฝาก")

    c.setFont("THSarabun-Bold", 16)
    c.drawCentredString(width / 2.0, height - 90, "ร้าน ไอโปรโมบายเซอร์วิส (สาขาหล่มสัก)")

    c.setFont("THSarabun", 12)
    c.drawCentredString(width / 2.0, height - 110, "14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110")

    # --- Document Body ---
    # We use a y_pos variable to easily manage vertical spacing.
    y_pos = height - 150
    left_margin = 50
    right_margin = width - 50

    # --- Contract Info ---
    # Placed contract number on the left and date on the right for a formal look.
    c.setFont("THSarabun", 14)
    c.drawString(left_margin, y_pos, "สัญญาเลขที่: 68-07-4-100650")
    c.drawRightString(right_margin, y_pos, "วันที่: 21 กรกฎาคม 2568")
    y_pos -= 30

    # --- Customer Info ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "ข้อมูลผู้ขายฝาก:")
    y_pos -= 20
    
    # Fixed: Put name and phone on separate lines to avoid overlap
    c.setFont("THSarabun", 14)
    c.drawString(left_margin + 15, y_pos, "ชื่อ: นายโสภี ยันหล้า")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "โทรศัพท์: 0918512767")
    y_pos -= 20
    
    # Fixed: Put address and ID on separate lines to avoid overlap
    c.drawString(left_margin + 15, y_pos, "ที่อยู่: 13/1 ซอยเพียรเหรียญรักษา ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "บัตรประชาชนเลขที่: 3679800089763")
    y_pos -= 25

    # --- Item Info ---
    c.line(left_margin, y_pos, right_margin, y_pos) # Separator line
    y_pos -= 20
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "รายการทรัพย์สินที่ขายฝาก:")
    y_pos -= 20
    c.setFont("THSarabun", 14)
    c.drawString(left_margin + 15, y_pos, "ทรัพย์สิน: realme c51")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "ขายฝากไว้เป็นจำนวนเงิน: 1,000.00 บาท (หนึ่งพันบาทถ้วน)")
    y_pos -= 20
    
    # Fixed: Put processing fee and service fee on separate lines
    c.drawString(left_margin + 15, y_pos, "ค่าดำเนินการ: 0.00 บาท")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "ค่าธรรมเนียม: 100.00 บาท")
    y_pos -= 25

    # --- Terms and Conditions ---
    c.line(left_margin, y_pos, right_margin, y_pos) # Separator line
    y_pos -= 20
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "เงื่อนไขและข้อตกลง:")
    y_pos -= 15
    c.setFont("THSarabun", 12)
    
    # Fixed: Adjusted line spacing and text wrapping for better readability
    text_terms = [
        "1. ข้าพเจ้าขอรับรองว่าสินค้าที่นำมาขายฝากเป็นกรรมสิทธิ์ของผู้ขายฝากอย่างแท้จริง ไม่มีการติดค้างชำระ",
        "    หรืออยู่ระหว่างผ่อนชำระ และไม่เกี่ยวกับการกระทำผิดกฏหมายใดๆ และมิได้ได้มาโดยการลักทรัพย์",
        "    ฉ้อโกง วิ่งราว กรรโชกทรัพย์ รีดทรัพย์ หรือโกงเจ้าหนี้แต่ประการใด",
        "",
        "2. หากมีบุคคลใดมาก่อกวนขัดสิทธิ์ผู้ซื้อในอันจะครองทรัพย์สินโดยปกติ เพราะบุคคลนั้นมีสิทธิ์",
        "    เหนือทรัพย์สินที่ได้ขายฝาก เพราะความผิดของผู้ขายฝาก ผู้ขายฝากจำต้องรับผิดชดใช้ค่าสินค้า",
        "    และความเสียหายอื่นๆ (ถ้ามี) แก่ผู้ซื้อ",
        "",
        "3. ข้าพเจ้าผู้ขายฝากได้อ่านเงื่อนไขที่กำหนดไว้ ได้รับทราบและเข้าใจถี่ถ้วน และตกลงทำตาม",
        "    เงื่อนไขในเอกสารนี้ทุกประการ พร้อมได้รับเงินถูกต้องตามจำนวนแล้ว จึงลงลายมือชื่อไว้เป็นหลักฐาน"
    ]
    
    for line in text_terms:
        if line.strip():  # Only draw non-empty lines
            c.drawString(left_margin + 15, y_pos, line)
        y_pos -= 16  # Consistent line spacing
    
    y_pos -= 15

    # --- Note ---
    c.setFont("THSarabun-Bold", 12)
    c.drawString(left_margin, y_pos, "หมายเหตุ:")
    y_pos -= 15
    c.setFont("THSarabun", 12)
    
    # Fixed: Split long note text into multiple lines
    note_lines = [
        "กรณีสินค้าหายหรือสูญหายซึ่งพิสูจน์ได้ว่าถูกโจรกรรม หรือเนื่องจากภัยธรรมชาติ",
        "ทางร้านไม่ต้องชดใช้หรือรับผิดชอบใดๆทั้งสิ้น",
        "",
        "หากเกินกำหนดเวลาไถ่ถอน ถือว่าท่านสละสิทธิ์ในทรัพย์สินนี้ให้ตกเป็นของทางร้านโดยสมบูรณ์"
    ]
    
    for note_line in note_lines:
        if note_line.strip():
            c.drawString(left_margin + 30, y_pos, note_line)
        y_pos -= 16
    
    y_pos -= 15

    # --- Redeem Info ---
    c.setFont("THSarabun-Bold", 16)
    c.drawString(left_margin, y_pos, "ยอดไถ่ถอน: 1,100.00 บาท (หนึ่งพันหนึ่งร้อยบาทถ้วน)")
    y_pos -= 25
    c.drawString(left_margin, y_pos, "กำหนดไถ่ทรัพย์สินภายในวันที่: 20 สิงหาคม 2568")
    y_pos -= 60

    # --- Signatures ---
    c.setFont("THSarabun", 14)
    # Fixed: Proper spacing for signatures
    signature_y = y_pos
    c.drawString(left_margin + 30, signature_y, "ลงชื่อ _________________________ ผู้รับฝาก")
    c.drawString(width - 280, signature_y, "ลงชื่อ _________________________ ผู้ขายฝาก")
    
    signature_y -= 25
    c.drawString(width - 230, signature_y, "( นายโสภี ยันหล้า )")

    # Save the PDF file
    c.save()
    print(f"Successfully created '{output_file}'")

def generate_pawn_ticket_from_data(contract_data: Dict, customer_data: Dict, product_data: Dict, 
                                  shop_data: Optional[Dict] = None, output_file: Optional[str] = None) -> str:
    """
    สร้าง PDF ใบฝากขายจากข้อมูลจริงในระบบ
    
    Args:
        contract_data (Dict): ข้อมูลสัญญา
        customer_data (Dict): ข้อมูลลูกค้า
        product_data (Dict): ข้อมูลสินค้า
        shop_data (Dict, optional): ข้อมูลร้านค้า ถ้าไม่ระบุจะใช้ข้อมูลเริ่มต้น
        output_file (str, optional): ชื่อไฟล์ PDF ที่จะสร้าง ถ้าไม่ระบุจะสร้างชื่ออัตโนมัติ
    
    Returns:
        str: ชื่อไฟล์ PDF ที่สร้าง
    """
    try:
        # ตรวจสอบฟอนต์
        font_path = 'THSarabun.ttf'
        bold_font_path = 'THSarabun Bold.ttf'

        if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
            print(f"Error: Font file not found.")
            print("Please make sure 'THSarabun.ttf' and 'THSarabun Bold.ttf' are in the same folder as the script.")
            return ""

        pdfmetrics.registerFont(TTFont('THSarabun', font_path))
        pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))

    except Exception as e:
        print(f"An error occurred while loading the font: {e}")
        return ""

    # สร้างชื่อไฟล์อัตโนมัติถ้าไม่ระบุ
    if not output_file:
        contract_number = contract_data.get('contract_number', 'unknown')
        output_file = f"pawn_ticket_{contract_number}.pdf"

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # --- Header ---
    c.setFont("THSarabun-Bold", 24)
    c.drawCentredString(width / 2.0, height - 60, "ใบขายฝาก")

    c.setFont("THSarabun-Bold", 16)
    # ดึงข้อมูลร้านค้าจาก shop_data หรือใช้ข้อมูลเริ่มต้น
    shop_name = shop_data.get('name', 'ร้าน ไอโปรโมบายเซอร์วิส') if shop_data else 'ร้าน ไอโปรโมบายเซอร์วิส'
    shop_branch = shop_data.get('branch', 'สาขาหล่มสัก') if shop_data else 'สาขาหล่มสัก'
    shop_full_name = f"{shop_name} ({shop_branch})"
    c.drawCentredString(width / 2.0, height - 90, shop_full_name)

    c.setFont("THSarabun", 12)
    # ดึงที่อยู่ร้านค้าจาก shop_data หรือใช้ข้อมูลเริ่มต้น
    shop_address = shop_data.get('address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110') if shop_data else '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    c.drawCentredString(width / 2.0, height - 110, shop_address)

    # --- Document Body ---
    y_pos = height - 150
    left_margin = 50
    right_margin = width - 50

    # --- Contract Info ---
    c.setFont("THSarabun", 14)
    contract_number = contract_data.get('contract_number', 'N/A')
    start_date = contract_data.get('start_date', 'N/A')
    end_date = contract_data.get('end_date', 'N/A')
    days_count = contract_data.get('days_count', 0)
    
    # แปลงวันที่ให้เป็นรูปแบบไทย
    month_map = {
        'January': 'มกราคม', 'February': 'กุมภาพันธ์', 'March': 'มีนาคม',
        'April': 'เมษายน', 'May': 'พฤษภาคม', 'June': 'มิถุนายน',
        'July': 'กรกฎาคม', 'August': 'สิงหาคม', 'September': 'กันยายน',
        'October': 'ตุลาคม', 'November': 'พฤศจิกายน', 'December': 'ธันวาคม'
    }
    
    try:
        if start_date != 'N/A':
            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            thai_date = date_obj.strftime('%d %B %Y')
            for eng, thai in month_map.items():
                thai_date = thai_date.replace(eng, thai)
        else:
            thai_date = 'N/A'
    except:
        thai_date = start_date
    
    try:
        if end_date != 'N/A':
            if isinstance(end_date, str):
                if '-' in end_date:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
                thai_end_date = end_date_obj.strftime('%d %B %Y')
                for eng, thai in month_map.items():
                    thai_end_date = thai_end_date.replace(eng, thai)
            else:
                thai_end_date = str(end_date)
        else:
            thai_end_date = 'N/A'
    except:
        thai_end_date = 'N/A'

    # ข้อมูลสัญญา
    c.drawString(left_margin, y_pos, f"สัญญาเลขที่: {contract_number}")
    c.drawRightString(right_margin, y_pos, f"วันที่: {thai_date}")
    y_pos -= 25
    
    # ข้อมูลเพิ่มเติมของสัญญา
    c.drawString(left_margin, y_pos, f"ระยะเวลาฝาก: {days_count} วัน")
    c.drawRightString(right_margin, y_pos, f"ครบกำหนด: {thai_end_date}")
    y_pos -= 30

    # --- Customer Info ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "ข้อมูลผู้ขายฝาก:")
    y_pos -= 20
    
    c.setFont("THSarabun", 14)
    # ข้อมูลลูกค้า
    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    customer_code = customer_data.get('customer_code', '')
    
    c.drawString(left_margin + 15, y_pos, f"รหัสลูกค้า: {customer_code}")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, f"ชื่อ-นามสกุล: {customer_name}")
    y_pos -= 20
    
    phone = customer_data.get('phone', 'N/A')
    c.drawString(left_margin + 15, y_pos, f"โทรศัพท์: {phone}")
    y_pos -= 20
    
    id_card = customer_data.get('id_card', 'N/A')
    c.drawString(left_margin + 15, y_pos, f"บัตรประชาชนเลขที่: {id_card}")
    y_pos -= 20
    
    # สร้างที่อยู่จากข้อมูลในฐานข้อมูล
    house_number = customer_data.get('house_number', '')
    street = customer_data.get('street', '')
    subdistrict = customer_data.get('subdistrict', '')
    district = customer_data.get('district', '')
    province = customer_data.get('province', '')
    
    address_parts = []
    if house_number:
        address_parts.append(house_number)
    if street:
        address_parts.append(street)
    if subdistrict:
        address_parts.append(f"ต.{subdistrict}")
    if district:
        address_parts.append(f"อ.{district}")
    if province:
        address_parts.append(f"จ.{province}")
    
    address = " ".join(address_parts) if address_parts else "N/A"
    c.drawString(left_margin + 15, y_pos, f"ที่อยู่: {address}")
    y_pos -= 25

    # --- Item Info ---
    c.line(left_margin, y_pos, right_margin, y_pos)
    y_pos -= 20
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "รายการทรัพย์สินที่ขายฝาก:")
    y_pos -= 20
    c.setFont("THSarabun", 14)
    
    # ข้อมูลสินค้า
    product_name = product_data.get('name', 'N/A')
    brand = product_data.get('brand', '')
    if brand:
        product_display = f"{brand} {product_name}"
    else:
        product_display = product_name
    
    c.drawString(left_margin + 15, y_pos, f"ทรัพย์สิน: {product_display}")
    y_pos -= 20
    
    # รายละเอียดสินค้าเพิ่มเติม
    size = product_data.get('size', '')
    if size:
        c.drawString(left_margin + 15, y_pos, f"ขนาด: {size}")
        y_pos -= 20
    
    weight = product_data.get('weight', '')
    weight_unit = product_data.get('weight_unit', '')
    if weight:
        weight_text = f"{weight} {weight_unit}" if weight_unit else str(weight)
        c.drawString(left_margin + 15, y_pos, f"น้ำหนัก: {weight_text}")
        y_pos -= 20
    
    serial_number = product_data.get('serial_number', '')
    if serial_number:
        c.drawString(left_margin + 15, y_pos, f"เลขประจำเครื่อง: {serial_number}")
        y_pos -= 20
    
    other_details = product_data.get('other_details', '')
    if other_details:
        c.drawString(left_margin + 15, y_pos, f"รายละเอียดอื่นๆ: {other_details}")
        y_pos -= 20
    
    # ข้อมูลการประเมินมูลค่า
    estimated_value = contract_data.get('estimated_value', 0)
    if estimated_value > 0:
        c.drawString(left_margin + 15, y_pos, f"มูลค่าประเมิน: {estimated_value:,.2f} บาท")
        y_pos -= 20
    
    y_pos -= 10
    
    # ข้อมูลการเงิน
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "ข้อมูลการเงิน:")
    y_pos -= 20
    c.setFont("THSarabun", 14)
    
    # ข้อมูลหลัก
    pawn_amount = contract_data.get('pawn_amount', 0)
    c.drawString(left_margin + 15, y_pos, f"ขายฝากไว้เป็นจำนวนเงิน: {pawn_amount:,.2f} บาท")
    y_pos -= 20
    
    # แสดงจำนวนวัน
    days_count = contract_data.get('days_count', 0)
    if days_count > 0:
        c.drawString(left_margin + 15, y_pos, f"ระยะเวลาฝาก: {days_count} วัน")
        y_pos -= 20
    
    # แสดงอัตราดอกเบี้ย
    interest_rate = contract_data.get('interest_rate', 0)
    if interest_rate > 0:
        c.drawString(left_margin + 15, y_pos, f"อัตราดอกเบี้ย: {interest_rate:.2f}% ต่อปี")
        y_pos -= 20
    
    # คำนวณดอกเบี้ย
    if interest_rate > 0 and days_count > 0:
        interest_amount = (pawn_amount * interest_rate * days_count) / 36500
        c.drawString(left_margin + 15, y_pos, f"ดอกเบี้ย: {interest_amount:,.2f} บาท")
        y_pos -= 20
    
    # ค่าธรรมเนียม
    fee_amount = contract_data.get('fee_amount', 0)
    if fee_amount > 0:
        c.drawString(left_margin + 15, y_pos, f"ค่าธรรมเนียม: {fee_amount:,.2f} บาท")
        y_pos -= 20
    
    # หัก ณ ที่จ่าย
    withholding_tax_rate = contract_data.get('withholding_tax_rate', 0)
    withholding_tax_amount = contract_data.get('withholding_tax_amount', 0)
    if withholding_tax_rate > 0 and withholding_tax_amount > 0:
        c.drawString(left_margin + 15, y_pos, f"หัก ณ ที่จ่าย ({withholding_tax_rate:.2f}%): {withholding_tax_amount:,.2f} บาท")
        y_pos -= 20
    
    # ยอดจ่าย
    total_paid = contract_data.get('total_paid', pawn_amount)
    if total_paid != pawn_amount:
        c.drawString(left_margin + 15, y_pos, f"ยอดจ่าย: {total_paid:,.2f} บาท")
        y_pos -= 20
    
    # ยอดไถ่ถอน
    total_redemption = contract_data.get('total_redemption', 0)
    if total_redemption > 0:
        c.drawString(left_margin + 15, y_pos, f"ยอดไถ่ถอนรวม: {total_redemption:,.2f} บาท")
        y_pos -= 20
    
    y_pos -= 15

    # --- Terms and Conditions ---
    c.line(left_margin, y_pos, right_margin, y_pos)
    y_pos -= 20
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "เงื่อนไขและข้อตกลง:")
    y_pos -= 15
    c.setFont("THSarabun", 12)
    
    # เงื่อนไขที่ปรับตามข้อมูลสัญญาจริง
    text_terms = [
        f"1. ข้าพเจ้าขอรับรองว่าสินค้า {product_display} ที่นำมาขายฝากเป็นกรรมสิทธิ์ของผู้ขายฝากอย่างแท้จริง",
        "    ไม่มีการติดค้างชำระ หรืออยู่ระหว่างผ่อนชำระ และไม่เกี่ยวกับการกระทำผิดกฏหมายใดๆ",
        "    และมิได้ได้มาโดยการลักทรัพย์ ฉ้อโกง วิ่งราว กรรโชกทรัพย์ รีดทรัพย์ หรือโกงเจ้าหนี้แต่ประการใด",
        "",
        f"2. สัญญานี้มีผลบังคับใช้เป็นระยะเวลา {days_count} วัน นับจากวันที่ {thai_date}",
        f"    หากเกินกำหนดเวลาไถ่ถอน (วันที่ {thai_end_date}) สินค้าจะตกเป็นของทางร้านโดยสมบูรณ์",
        "",
        f"3. อัตราดอกเบี้ยที่ใช้คำนวณคือ {interest_rate:.2f}% ต่อปี",
        f"    ยอดไถ่ถอนรวมดอกเบี้ยและค่าธรรมเนียมเป็นจำนวน {total_redemption:,.2f} บาท",
        "",
        f"4. ข้อมูลสัญญา: เลขที่ {contract_number} วันที่เริ่มต้น {thai_date} วันที่ครบกำหนด {thai_end_date}",
        f"    ยอดฝาก {pawn_amount:,.2f} บาท ยอดไถ่ถอน {total_redemption:,.2f} บาท",
        "",
        "5. หากมีบุคคลใดมาก่อกวนขัดสิทธิ์ผู้ซื้อในอันจะครองทรัพย์สินโดยปกติ เพราะบุคคลนั้นมีสิทธิ์",
        "    เหนือทรัพย์สินที่ได้ขายฝาก เพราะความผิดของผู้ขายฝาก ผู้ขายฝากจำต้องรับผิดชดใช้ค่าสินค้า",
        "    และความเสียหายอื่นๆ (ถ้ามี) แก่ผู้ซื้อ",
        "",
        "6. ข้าพเจ้าผู้ขายฝากได้อ่านเงื่อนไขที่กำหนดไว้ ได้รับทราบและเข้าใจถี่ถ้วน และตกลงทำตาม",
        "    เงื่อนไขในเอกสารนี้ทุกประการ พร้อมได้รับเงินถูกต้องตามจำนวนแล้ว จึงลงลายมือชื่อไว้เป็นหลักฐาน"
    ]
    
    for line in text_terms:
        if line.strip():
            c.drawString(left_margin + 15, y_pos, line)
        y_pos -= 16
    
    y_pos -= 15

    # --- Note ---
    c.setFont("THSarabun-Bold", 12)
    c.drawString(left_margin, y_pos, "หมายเหตุ:")
    y_pos -= 15
    c.setFont("THSarabun", 12)
    
    # หมายเหตุที่ปรับตามข้อมูลสัญญาจริง
    note_lines = [
        f"• สัญญานี้มีผลบังคับใช้จนถึงวันที่ {thai_end_date}",
        f"• ยอดไถ่ถอนรวมดอกเบี้ยและค่าธรรมเนียม: {total_redemption:,.2f} บาท",
        f"• ระยะเวลาฝาก: {days_count} วัน (จาก {thai_date} ถึง {thai_end_date})",
        "",
        "• กรณีสินค้าหายหรือสูญหายซึ่งพิสูจน์ได้ว่าถูกโจรกรรม หรือเนื่องจากภัยธรรมชาติ",
        "  ทางร้านไม่ต้องชดใช้หรือรับผิดชอบใดๆทั้งสิ้น",
        "",
        f"• หากเกินกำหนดเวลาไถ่ถอน (วันที่ {thai_end_date})",
        "  ถือว่าท่านสละสิทธิ์ในทรัพย์สินนี้ให้ตกเป็นของทางร้านโดยสมบูรณ์",
        "",
        "• ลูกค้าสามารถไถ่ถอนสินค้าได้ตลอดเวลาก่อนครบกำหนด โดยชำระยอดไถ่ถอนตามที่ระบุข้างต้น",
        "",
        f"• ข้อมูลสินค้า: {product_display}",
        f"• ข้อมูลลูกค้า: {customer_name} (รหัส: {customer_code})"
    ]
    
    for note_line in note_lines:
        if note_line.strip():
            c.drawString(left_margin + 30, y_pos, note_line)
        y_pos -= 16
    
    y_pos -= 15

    # --- Redeem Info ---
    c.setFont("THSarabun-Bold", 16)
    total_redemption = contract_data.get('total_redemption', pawn_amount)
    c.drawString(left_margin, y_pos, f"ยอดไถ่ถอน: {total_redemption:,.2f} บาท")
    y_pos -= 25
    
    # คำนวณวันที่ไถ่ถอน
    try:
        if start_date != 'N/A':
            end_date = contract_data.get('end_date', start_date)
            if isinstance(end_date, str):
                if '-' in end_date:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
                thai_end_date = end_date_obj.strftime('%d %B %Y')
                for eng, thai in month_map.items():
                    thai_end_date = thai_end_date.replace(eng, thai)
            else:
                thai_end_date = str(end_date)
        else:
            thai_end_date = 'N/A'
    except:
        thai_end_date = 'N/A'
    
    c.drawString(left_margin, y_pos, f"กำหนดไถ่ทรัพย์สินภายในวันที่: {thai_end_date}")
    y_pos -= 60

    # --- Signatures ---
    c.setFont("THSarabun", 14)
    signature_y = y_pos
    
    # ลายเซ็นผู้รับฝาก
    c.drawString(left_margin + 30, signature_y, "ลงชื่อ _________________________ ผู้รับฝาก")
    c.drawString(left_margin + 30, signature_y - 25, "( นาย/นาง/นางสาว _________________ )")
    c.drawString(left_margin + 30, signature_y - 45, "วันที่: _________________")
    
    # ลายเซ็นผู้ขายฝาก
    c.drawString(width - 280, signature_y, "ลงชื่อ _________________________ ผู้ขายฝาก")
    c.drawString(width - 280, signature_y - 25, f"( {customer_name} )")
    c.drawString(width - 280, signature_y - 45, f"วันที่: {thai_date}")
    
    # ข้อมูลเพิ่มเติม
    signature_y -= 80
    c.setFont("THSarabun", 12)
    c.drawString(left_margin, signature_y, "หมายเหตุ:")
    c.drawString(left_margin + 15, signature_y - 20, "• เอกสารนี้พิมพ์จากระบบคอมพิวเตอร์")
    c.drawString(left_margin + 15, signature_y - 35, f"• สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawString(left_margin + 15, signature_y - 50, f"• เลขที่สัญญา: {contract_number}")
    c.drawString(left_margin + 15, signature_y - 65, f"• ร้าน: {shop_full_name}")
    c.drawString(left_margin + 15, signature_y - 80, f"• สถานะสัญญา: {contract_data.get('status', 'active')}")

    # Save the PDF file
    c.save()
    print(f"Successfully created '{output_file}'")
    return output_file

# --- Main execution ---
if __name__ == "__main__":
    # This will create the PDF file in the same directory where you run the script.
    generate_pawn_ticket("pawn_ticket_fixed.pdf")