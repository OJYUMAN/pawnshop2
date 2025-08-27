# -*- coding: utf-8 -*-
"""
ระบบสร้างสัญญาไถ่ถอน PDF
สำหรับการไถ่ถอนสินค้าที่ขายฝาก
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List


def generate_redemption_contract_pdf(redemption_data: Dict, customer_data: Dict, 
                                    product_data: Dict, original_contract_data: Dict,
                                    shop_data: Optional[Dict] = None, 
                                    output_file: Optional[str] = None, output_folder: Optional[str] = None) -> str:
    """
    สร้าง PDF สัญญาไถ่ถอน
    
    Args:
        redemption_data (Dict): ข้อมูลการไถ่ถอน
        customer_data (Dict): ข้อมูลลูกค้า
        product_data (Dict): ข้อมูลสินค้า
        original_contract_data (Dict): ข้อมูลสัญญาเดิม
        shop_data (Dict, optional): ข้อมูลร้านค้า
        output_file (str, optional): ชื่อไฟล์ PDF ที่จะสร้าง
    
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
        contract_number = original_contract_data.get('contract_number', 'unknown')
        redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"redemption_contract_{contract_number}_{redemption_date}.pdf"
    
    # กำหนดโฟลเดอร์ปลายทาง
    if output_folder:
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        os.makedirs(output_folder, exist_ok=True)
        # รวมเส้นทางโฟลเดอร์กับชื่อไฟล์
        output_file = os.path.join(output_folder, output_file)

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    # กำหนดค่าคงที่สำหรับ layout
    LEFT_MARGIN = 50
    RIGHT_MARGIN = width - 50
    TOP_MARGIN = height - 40
    BOTTOM_MARGIN = 80
    LINE_HEIGHT = 18
    SECTION_SPACING = 25
    
    # ฟังก์ชันช่วยในการตรวจสอบและเพิ่มหน้าใหม่
    def check_page_break(current_y, required_lines=3):
        if current_y - (required_lines * LINE_HEIGHT) < BOTTOM_MARGIN:
            c.showPage()
            return TOP_MARGIN
        return current_y
    
    # ฟังก์ชันแปลงวันที่เป็นภาษาไทย
    def convert_to_thai_date(date_str):
        month_map = {
            'January': 'มกราคม', 'February': 'กุมภาพันธ์', 'March': 'มีนาคม',
            'April': 'เมษายน', 'May': 'พฤษภาคม', 'June': 'มิถุนายน',
            'July': 'กรกฎาคม', 'August': 'สิงหาคม', 'September': 'กันยายน',
            'October': 'ตุลาคม', 'November': 'พฤศจิกายน', 'December': 'ธันวาคม'
        }
        
        try:
            if date_str and date_str != 'N/A':
                if isinstance(date_str, str):
                    if '-' in date_str:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    thai_date = date_obj.strftime('%d %B %Y')
                    for eng, thai in month_map.items():
                        thai_date = thai_date.replace(eng, thai)
                    return thai_date
                else:
                    return str(date_str)
            else:
                return 'N/A'
        except:
            return date_str if date_str else 'N/A'
    
    # เริ่มต้น y_position
    y_pos = TOP_MARGIN

    # --- Header ---
    c.setFont("THSarabun-Bold", 24)
    c.drawCentredString(width / 2.0, y_pos, "สัญญาไถ่ถอน")
    y_pos -= 35

    c.setFont("THSarabun-Bold", 16)
    shop_name = shop_data.get('name', 'ร้าน ไอโปรโมบายเซอร์วิส') if shop_data else 'ร้าน ไอโปรโมบายเซอร์วิส'
    shop_branch = shop_data.get('branch', 'สาขาหล่มสัก') if shop_data else 'สาขาหล่มสัก'
    shop_full_name = f"{shop_name} ({shop_branch})"
    c.drawCentredString(width / 2.0, y_pos, shop_full_name)
    y_pos -= 25

    c.setFont("THSarabun", 12)
    shop_address = shop_data.get('address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110') if shop_data else '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    c.drawCentredString(width / 2.0, y_pos, shop_address)
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 5)

    # --- Original Contract Info Section ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "ข้อมูลสัญญาเดิม:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    original_contract_number = original_contract_data.get('contract_number', 'N/A')
    original_start_date = original_contract_data.get('start_date', 'N/A')
    original_end_date = original_contract_data.get('end_date', 'N/A')
    original_pawn_amount = original_contract_data.get('pawn_amount', 0)
    
    thai_original_start_date = convert_to_thai_date(original_start_date)
    thai_original_end_date = convert_to_thai_date(original_end_date)

    c.drawString(LEFT_MARGIN + 20, y_pos, f"เลขที่สัญญาเดิม: {original_contract_number}")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"วันที่เริ่มต้น: {thai_original_start_date}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ยอดฝากเดิม: {original_pawn_amount:,.2f} บาท")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"ครบกำหนดเดิม: {thai_original_end_date}")
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 6)

    # --- Redemption Info Section ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "ข้อมูลการไถ่ถอน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y-%m-%d'))
    deposit_date = redemption_data.get('deposit_date', 'N/A')
    due_date = redemption_data.get('due_date', 'N/A')
    total_days = redemption_data.get('total_days', 0)
    
    thai_redemption_date = convert_to_thai_date(redemption_date)
    thai_deposit_date = convert_to_thai_date(deposit_date)
    thai_due_date = convert_to_thai_date(due_date)

    c.drawString(LEFT_MARGIN + 20, y_pos, f"วันที่ไถ่ถอน: {thai_redemption_date}")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"วันที่รับฝาก: {thai_deposit_date}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"จำนวนวันที่ฝาก: {total_days} วัน")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"วันที่ครบกำหนด: {thai_due_date}")
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 6)

    # --- Customer Info Section ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "ข้อมูลผู้ไถ่ถอน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    customer_code = customer_data.get('customer_code', '')
    phone = customer_data.get('phone', 'N/A')
    id_card = customer_data.get('id_card', 'N/A')
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"รหัสลูกค้า: {customer_code}")
    c.drawString(LEFT_MARGIN + 280, y_pos, f"โทรศัพท์: {phone}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ชื่อ-นามสกุล: {customer_name}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"บัตรประชาชน: {id_card}")
    y_pos -= LINE_HEIGHT
    
    # สร้างที่อยู่แบบย่อ
    house_number = customer_data.get('house_number', '')
    street = customer_data.get('street', '')
    subdistrict = customer_data.get('subdistrict', '')
    district = customer_data.get('district', '')
    province = customer_data.get('province', '')
    
    address_parts = []
    if house_number: address_parts.append(house_number)
    if street: address_parts.append(street)
    if subdistrict: address_parts.append(f"ต.{subdistrict}")
    if district: address_parts.append(f"อ.{district}")
    if province: address_parts.append(f"จ.{province}")
    
    address = " ".join(address_parts) if address_parts else "N/A"
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ที่อยู่: {address}")
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 6)

    # --- Product Info Section ---
    c.line(LEFT_MARGIN, y_pos + 5, RIGHT_MARGIN, y_pos + 5)
    y_pos -= 15
    
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "รายการทรัพย์สินที่ไถ่ถอน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    product_name = product_data.get('name', 'N/A')
    brand = product_data.get('brand', '')
    product_display = f"{brand} {product_name}" if brand else product_name
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ทรัพย์สิน: {product_display}")
    y_pos -= LINE_HEIGHT
    
    # แสดงรายละเอียดสินค้าแบบ compact
    details = []
    size = product_data.get('size', '')
    weight = product_data.get('weight', '')
    weight_unit = product_data.get('weight_unit', '')
    serial_number = product_data.get('serial_number', '')
    
    if size: details.append(f"ขนาด: {size}")
    if weight: 
        weight_text = f"{weight} {weight_unit}" if weight_unit else str(weight)
        details.append(f"น้ำหนัก: {weight_text}")
    if serial_number: details.append(f"S/N: {serial_number}")
    
    if details:
        details_text = " | ".join(details)
        c.drawString(LEFT_MARGIN + 20, y_pos, details_text)
        y_pos -= LINE_HEIGHT
    
    other_details = product_data.get('other_details', '')
    if other_details:
        c.drawString(LEFT_MARGIN + 20, y_pos, f"รายละเอียดอื่นๆ: {other_details}")
        y_pos -= LINE_HEIGHT
    
    estimated_value = original_contract_data.get('estimated_value', 0)
    if estimated_value > 0:
        c.drawString(LEFT_MARGIN + 20, y_pos, f"มูลค่าประเมิน: {estimated_value:,.2f} บาท")
        y_pos -= LINE_HEIGHT
    
    y_pos -= 10

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 8)

    # --- Financial Summary Section ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "สรุปการเงิน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    principal_amount = redemption_data.get('principal_amount', 0)
    fee_amount = redemption_data.get('fee_amount', 0)
    penalty_amount = redemption_data.get('penalty_amount', 0)
    discount_amount = redemption_data.get('discount_amount', 0)
    total_redemption = redemption_data.get('redemption_amount', 0)
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"เงินต้น: {principal_amount:,.2f} บาท")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"ค่าธรรมเนียม: {fee_amount:,.2f} บาท")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ค่าปรับ: {penalty_amount:,.2f} บาท")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"ส่วนลด: {discount_amount:,.2f} บาท")
    y_pos -= LINE_HEIGHT
    
    # ไฮไลท์ยอดไถ่ถอนรวม
    c.setFont("THSarabun-Bold", 16)
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ยอดไถ่ถอนรวม: {total_redemption:,.2f} บาท")
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่สำหรับเงื่อนไข
    y_pos = check_page_break(y_pos, 10)

    # --- Terms and Conditions for Redemption ---
    c.line(LEFT_MARGIN, y_pos + 5, RIGHT_MARGIN, y_pos + 5)
    y_pos -= 15
    
    c.setFont("THSarabun-Bold", 12)
    c.drawString(LEFT_MARGIN, y_pos, "เงื่อนไขการไถ่ถอน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 10)
    redemption_terms = [
        f"• การไถ่ถอนครั้งนี้ทำในวันที่: {thai_redemption_date}",
        f"• จำนวนวันที่ฝากไว้: {total_days} วัน",
        f"• ยอดไถ่ถอนรวม: {total_redemption:,.2f} บาท",
        "• หลังจากไถ่ถอนแล้ว สินค้าจะถูกส่งมอบให้กับผู้ไถ่ถอน",
        "• การไถ่ถอนถือเป็นการสิ้นสุดสัญญาการขายฝาก",
        "• ผู้ไถ่ถอนต้องตรวจสอบสินค้าก่อนรับมอบ",
        "• หากสินค้ามีความเสียหาย ต้องแจ้งให้ทราบทันที",
        "• หลังจากรับมอบสินค้าแล้ว ทางร้านไม่รับผิดชอบความเสียหายใดๆ"
    ]
    
    for term in redemption_terms:
        y_pos = check_page_break(y_pos, 1)
        c.drawString(LEFT_MARGIN + 15, y_pos, term)
        y_pos -= 14
    
    y_pos -= 10

    # ตรวจสอบหน้าใหม่สำหรับ Summary Box
    y_pos = check_page_break(y_pos, 8)

    # --- Redemption Summary Box ---
    c.setFont("THSarabun-Bold", 14)
    
    summary_box_y = y_pos - 20
    box_height = 80
    c.rect(LEFT_MARGIN, summary_box_y - box_height, RIGHT_MARGIN - LEFT_MARGIN, box_height, stroke=1, fill=0)
    
    # ข้อมูลการไถ่ถอน
    c.drawCentredString(width / 2.0, summary_box_y - 15, f"การไถ่ถอน: {thai_redemption_date}")
    c.drawCentredString(width / 2.0, summary_box_y - 30, f"ยอดไถ่ถอนรวม: {total_redemption:,.2f} บาท")
    c.drawCentredString(width / 2.0, summary_box_y - 45, f"จำนวนวันที่ฝาก: {total_days} วัน")
    c.drawCentredString(width / 2.0, summary_box_y - 60, f"สถานะ: ไถ่ถอนเรียบร้อย")
    
    y_pos = summary_box_y - (box_height + 20)

    # ตรวจสอบหน้าใหม่สำหรับลายเซ็น
    y_pos = check_page_break(y_pos, 6)

    # --- Signatures ---
    c.setFont("THSarabun", 12)
    signature_y = y_pos - 20
    
    # ลายเซ็นผู้รับฝาก
    c.drawString(LEFT_MARGIN + 30, signature_y, "ลงชื่อ _________________________ ผู้รับฝาก")
    c.drawString(LEFT_MARGIN + 30, signature_y - 20, "( นาย/นาง/นางสาว _________________ )")
    c.drawString(LEFT_MARGIN + 30, signature_y - 35, "วันที่: _________________")
    
    # ลายเซ็นผู้ไถ่ถอน
    c.drawString(width - 280, signature_y, "ลงชื่อ _________________________ ผู้ไถ่ถอน")
    c.drawString(width - 280, signature_y - 20, f"( {customer_name} )")
    c.drawString(width - 280, signature_y - 35, f"วันที่: {thai_redemption_date}")
    
    # Footer info
    signature_y -= 60
    c.setFont("THSarabun", 10)
    c.drawString(LEFT_MARGIN, signature_y, f"เอกสารไถ่ถอนสร้างโดยระบบ | เลขที่สัญญา: {original_contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Save the PDF file
    c.save()
    print(f"Successfully created redemption contract '{output_file}'")
    return output_file


def generate_redemption_receipt_pdf(redemption_data: Dict, customer_data: Dict, 
                                   product_data: Dict, original_contract_data: Dict,
                                   shop_data: Optional[Dict] = None,
                                   output_file: Optional[str] = None) -> str:
    """
    สร้าง PDF ใบเสร็จการไถ่ถอน
    
    Args:
        redemption_data (Dict): ข้อมูลการไถ่ถอน
        customer_data (Dict): ข้อมูลลูกค้า
        product_data (Dict): ข้อมูลสินค้า
        original_contract_data (Dict): ข้อมูลสัญญาเดิม
        shop_data (Dict, optional): ข้อมูลร้านค้า
        output_file (str, optional): ชื่อไฟล์ PDF ที่จะสร้าง
    
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
        contract_number = original_contract_data.get('contract_number', 'unknown')
        redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"redemption_receipt_{contract_number}_{redemption_date}.pdf"

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    # กำหนดค่าคงที่สำหรับ layout
    LEFT_MARGIN = 50
    RIGHT_MARGIN = width - 50
    TOP_MARGIN = height - 40
    BOTTOM_MARGIN = 80
    LINE_HEIGHT = 18
    SECTION_SPACING = 25
    
    # ฟังก์ชันแปลงวันที่เป็นภาษาไทย
    def convert_to_thai_date(date_str):
        month_map = {
            'January': 'มกราคม', 'February': 'กุมภาพันธ์', 'March': 'มีนาคม',
            'April': 'เมษายน', 'May': 'พฤษภาคม', 'June': 'มิถุนายน',
            'July': 'กรกฎาคม', 'August': 'สิงหาคม', 'September': 'กันยายน',
            'October': 'ตุลาคม', 'November': 'พฤศจิกายน', 'December': 'ธันวาคม'
        }
        
        try:
            if date_str and date_str != 'N/A':
                if isinstance(date_str, str):
                    if '-' in date_str:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    thai_date = date_obj.strftime('%d %B %Y')
                    for eng, thai in month_map.items():
                        thai_date = thai_date.replace(eng, thai)
                    return thai_date
                else:
                    return str(date_str)
            else:
                return 'N/A'
        except:
            return date_str if date_str else 'N/A'
    
    # เริ่มต้น y_position
    y_pos = TOP_MARGIN

    # --- Header ---
    c.setFont("THSarabun-Bold", 24)
    c.drawCentredString(width / 2.0, y_pos, "ใบเสร็จการไถ่ถอน")
    y_pos -= 35

    c.setFont("THSarabun-Bold", 16)
    shop_name = shop_data.get('name', 'ร้าน ไอโปรโมบายเซอร์วิส') if shop_data else 'ร้าน ไอโปรโมบายเซอร์วิส'
    shop_branch = shop_data.get('branch', 'สาขาหล่มสัก') if shop_data else 'สาขาหล่มสัก'
    shop_full_name = f"{shop_name} ({shop_branch})"
    c.drawCentredString(width / 2.0, y_pos, shop_full_name)
    y_pos -= 25

    c.setFont("THSarabun", 12)
    shop_address = shop_data.get('address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110') if shop_data else '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
    c.drawCentredString(width / 2.0, y_pos, shop_address)
    y_pos -= SECTION_SPACING

    # --- Receipt Details ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "รายละเอียดการไถ่ถอน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    contract_number = original_contract_data.get('contract_number', 'N/A')
    redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y-%m-%d'))
    total_days = redemption_data.get('total_days', 0)
    
    thai_redemption_date = convert_to_thai_date(redemption_date)
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"เลขที่สัญญา: {contract_number}")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"วันที่ไถ่ถอน: {thai_redemption_date}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"จำนวนวันที่ฝาก: {total_days} วัน")
    y_pos -= SECTION_SPACING

    # --- Payment Details ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "รายละเอียดการชำระ:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    principal_amount = redemption_data.get('principal_amount', 0)
    fee_amount = redemption_data.get('fee_amount', 0)
    penalty_amount = redemption_data.get('penalty_amount', 0)
    discount_amount = redemption_data.get('discount_amount', 0)
    total_redemption = redemption_data.get('redemption_amount', 0)
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"เงินต้น: {principal_amount:,.2f} บาท")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"ค่าธรรมเนียม: {fee_amount:,.2f} บาท")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ค่าปรับ: {penalty_amount:,.2f} บาท")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"ส่วนลด: {discount_amount:,.2f} บาท")
    y_pos -= LINE_HEIGHT
    
    # ไฮไลท์ยอดรวม
    c.setFont("THSarabun-Bold", 16)
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ยอดรวม: {total_redemption:,.2f} บาท")
    y_pos -= SECTION_SPACING

    # --- Customer Info ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "ข้อมูลลูกค้า:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ชื่อ-นามสกุล: {customer_name}")
    y_pos -= LINE_HEIGHT
    
    phone = customer_data.get('phone', 'N/A')
    c.drawString(LEFT_MARGIN + 20, y_pos, f"โทรศัพท์: {phone}")
    y_pos -= SECTION_SPACING

    # --- Product Info ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "สินค้าที่ไถ่ถอน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    product_name = product_data.get('name', 'N/A')
    brand = product_data.get('brand', '')
    product_display = f"{brand} {product_name}" if brand else product_name
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ทรัพย์สิน: {product_display}")
    y_pos -= SECTION_SPACING

    # --- Payment Confirmation ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "การชำระเงิน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    c.drawString(LEFT_MARGIN + 20, y_pos, f"สถานะ: ชำระแล้ว")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"วันที่ชำระ: {thai_redemption_date}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN + 20, y_pos, f"จำนวนเงิน: {total_redemption:,.2f} บาท")
    y_pos -= SECTION_SPACING

    # --- Footer ---
    y_pos -= 20
    c.setFont("THSarabun", 10)
    c.drawString(LEFT_MARGIN, y_pos, f"เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Save the PDF file
    c.save()
    print(f"Successfully created redemption receipt '{output_file}'")
    return output_file


# --- Main execution ---
if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print("PDF3.py - ระบบสร้างสัญญาไถ่ถอน")
    print("ฟังก์ชันที่ใช้งานได้:")
    print("1. generate_redemption_contract_pdf() - สร้างสัญญาไถ่ถอน")
    print("2. generate_redemption_receipt_pdf() - สร้างใบเสร็จการไถ่ถอน")
