# generate_pawn_ticket_v2_fixed.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from typing import Dict, Optional, List



def generate_pawn_ticket_from_data(contract_data: Dict, customer_data: Dict, product_data: Dict, 
                                  shop_data: Optional[Dict] = None, output_file: Optional[str] = None,
                                  renewal_data: Optional[List[Dict]] = None) -> str:
    """
    สร้าง PDF ใบฝากขายจากข้อมูลจริงในระบบ พร้อม layout ที่ปรับปรุงแล้ว
    
    Args:
        contract_data (Dict): ข้อมูลสัญญา
        customer_data (Dict): ข้อมูลลูกค้า
        product_data (Dict): ข้อมูลสินค้า
        shop_data (Dict, optional): ข้อมูลร้านค้า ถ้าไม่ระบุจะใช้ข้อมูลเริ่มต้น
        output_file (str, optional): ชื่อไฟล์ PDF ที่จะสร้าง ถ้าไม่ระบุจะสร้างชื่ออัตโนมัติ
        renewal_data (List[Dict], optional): ข้อมูลการต่อดอก
    
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
    c.drawCentredString(width / 2.0, y_pos, "ใบขายฝาก")
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

    # --- Contract Info Section ---
    c.setFont("THSarabun", 14)
    contract_number = contract_data.get('contract_number', 'N/A')
    start_date = contract_data.get('start_date', 'N/A')
    end_date = contract_data.get('end_date', 'N/A')
    days_count = contract_data.get('days_count', 0)
    
    thai_start_date = convert_to_thai_date(start_date)
    thai_end_date = convert_to_thai_date(end_date)

    # แสดงข้อมูลสัญญาในบรรทัดเดียว
    c.drawString(LEFT_MARGIN, y_pos, f"สัญญาเลขที่: {contract_number}")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"วันที่: {thai_start_date}")
    y_pos -= LINE_HEIGHT
    
    c.drawString(LEFT_MARGIN, y_pos, f"ระยะเวลาฝาก: {days_count} วัน")
    c.drawRightString(RIGHT_MARGIN, y_pos, f"ครบกำหนด: {thai_end_date}")
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 6)

    # --- Customer Info Section ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "ข้อมูลผู้ขายฝาก:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    customer_code = customer_data.get('customer_code', '')
    phone = customer_data.get('phone', 'N/A')
    id_card = customer_data.get('id_card', 'N/A')
    
    # แสดงข้อมูลลูกค้าแบบ 2 คอลัมน์
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
    c.drawString(LEFT_MARGIN, y_pos, "รายการทรัพย์สินที่ขายฝาก:")
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
    
    estimated_value = contract_data.get('estimated_value', 0)
    if estimated_value > 0:
        c.drawString(LEFT_MARGIN + 20, y_pos, f"มูลค่าประเมิน: {estimated_value:,.2f} บาท")
        y_pos -= LINE_HEIGHT
    
    y_pos -= 10

    # ตรวจสอบหน้าใหม่
    y_pos = check_page_break(y_pos, 8)

    # --- Financial Info Section ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN, y_pos, "ข้อมูลการเงิน:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 12)
    pawn_amount = contract_data.get('pawn_amount', 0)
    interest_rate = contract_data.get('interest_rate', 0)
    fee_amount = contract_data.get('fee_amount', 0)
    total_redemption = contract_data.get('total_redemption', pawn_amount)
    
    # แสดงข้อมูลการเงินแบบ 2 คอลัมน์
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ยอดฝาก: {pawn_amount:,.2f} บาท")
    c.drawString(LEFT_MARGIN + 280, y_pos, f"ระยะเวลา: {days_count} วัน")
    y_pos -= LINE_HEIGHT
    
    if interest_rate > 0:
        interest_amount = (pawn_amount * interest_rate * days_count) / 36500
        c.drawString(LEFT_MARGIN + 20, y_pos, f"อัตราดอกเบี้ย: {interest_rate:.2f}% ต่อปี")
        c.drawString(LEFT_MARGIN + 280, y_pos, f"ดอกเบี้ย: {interest_amount:,.2f} บาท")
        y_pos -= LINE_HEIGHT
    
    if fee_amount > 0:
        c.drawString(LEFT_MARGIN + 20, y_pos, f"ค่าธรรมเนียม: {fee_amount:,.2f} บาท")
        y_pos -= LINE_HEIGHT
  
    
    # หัก ณ ที่จ่าย
    withholding_tax_rate = contract_data.get('withholding_tax_rate', 0)
    withholding_tax_amount = contract_data.get('withholding_tax_amount', 0)
    if withholding_tax_rate > 0 and withholding_tax_amount > 0:
        c.drawString(LEFT_MARGIN + 20, y_pos, f"หัก ณ ที่จ่าย ({withholding_tax_rate:.2f}%): {withholding_tax_amount:,.2f} บาท")
        y_pos -= LINE_HEIGHT
    
    # ยอดจ่าย
    total_paid = contract_data.get('total_paid', pawn_amount)
    if total_paid != pawn_amount:
        c.drawString(LEFT_MARGIN + 20, y_pos, f"ยอดจ่าย: {total_paid:,.2f} บาท")
        y_pos -= LINE_HEIGHT
    
    # ไฮไลท์ยอดไถ่ถอน
    c.setFont("THSarabun-Bold", 14)
    c.drawString(LEFT_MARGIN + 20, y_pos, f"ยอดไถ่ถอนรวม: {total_redemption:,.2f} บาท")
    y_pos -= SECTION_SPACING

    # ตรวจสอบหน้าใหม่สำหรับเงื่อนไข
    y_pos = check_page_break(y_pos, 10)

    # --- Terms and Conditions (แบบย่อ) ---
    c.line(LEFT_MARGIN, y_pos + 5, RIGHT_MARGIN, y_pos + 5)
    y_pos -= 15
    
    c.setFont("THSarabun-Bold", 12)
    c.drawString(LEFT_MARGIN, y_pos, "เงื่อนไขสำคัญ:")
    y_pos -= LINE_HEIGHT
    
    c.setFont("THSarabun", 10)
    important_terms = [
        f"• สินค้าต้องไถ่ถอนภายในวันที่ {thai_end_date} หากเกินกำหนดจะตกเป็นของทางร้าน",
        f"• ยอดไถ่ถอนรวม {total_redemption:,.2f} บาท (รวมดอกเบี้ย {interest_rate:.2f}% ต่อปี)"
    ]
    
    # เพิ่มเงื่อนไขการต่อดอก
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
    
    important_terms.extend([
        "• ผู้ขายฝากรับรองว่าสินค้าเป็นกรรมสิทธิ์ของตนและไม่เกี่ยวข้องกับการกระทำผิดกฎหมาย",
        "• หากมีบุคคลใดมาก่อกวนสิทธิ์ ผู้ขายฝากต้องรับผิดชดใช้ความเสียหาย",
        "• กรณีสินค้าสูญหายจากภัยธรรมชาติหรือโจรกรรม ทางร้านไม่รับผิดชอบ"
    ])
    
    for term in important_terms:
        y_pos = check_page_break(y_pos, 1)
        c.drawString(LEFT_MARGIN + 15, y_pos, term)
        y_pos -= 14
    
    y_pos -= 10

    # ตรวจสอบหน้าใหม่สำหรับลายเซ็น
    y_pos = check_page_break(y_pos, 8)

    # --- Summary Box ---
    c.setFont("THSarabun-Bold", 14)
    
    # คำนวณขนาดของ Summary Box ตามข้อมูลการต่อดอก
    box_height = 35
    if renewal_data:
        box_height = 60  # เพิ่มความสูงถ้ามีข้อมูลการต่อดอก
    
    summary_box_y = y_pos - 20
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
    
    # ลายเซ็นผู้ขายฝาก
    c.drawString(width - 280, signature_y, "ลงชื่อ _________________________ ผู้ขายฝาก")
    c.drawString(width - 280, signature_y - 20, f"( {customer_name} )")
    c.drawString(width - 280, signature_y - 35, f"วันที่: {thai_start_date}")
    
    # Footer info
    signature_y -= 60
    c.setFont("THSarabun", 10)
    c.drawString(LEFT_MARGIN, signature_y, f"เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Save the PDF file
    c.save()
    print(f"Successfully created '{output_file}' with improved layout")
    return output_file

# --- Main execution ---
if __name__ == "__main__":
    # This will create the PDF file in the same directory where you run the script.
    generate_pawn_ticket("pawn_ticket_fixed.pdf")