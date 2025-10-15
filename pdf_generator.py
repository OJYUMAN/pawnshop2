# -*- coding: utf-8 -*-
"""
PDF Generator for Pawn Shop Contracts (Python 2.7 compatible)
สร้างไฟล์ PDF จริงๆ แทน HTML
"""

import os
import html
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# Thai month names
TH_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def buddhist_year(dt):
    return dt.year + 543

def thai_date(date_str, include_time=False):
    """
    Convert date string to Thai format
    """
    if not date_str or date_str == "N/A":
        return "N/A"
    
    try:
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M']:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    break
                except ValueError:
                    continue
            else:
                return str(date_str)
        
        day = dt.day
        month_name = TH_MONTHS[dt.month - 1]
        year_th = buddhist_year(dt)
        
        if include_time or ("%H" in str(date_str) and "%M" in str(date_str)):
            return str(day) + " " + month_name + " " + str(year_th) + " เวลา " + dt.strftime('%H:%M') + " น."
        return str(day) + " " + month_name + " " + str(year_th)
        
    except Exception:
        return str(date_str)

def money(n):
    try:
        if abs(float(n) - int(float(n))) < 1e-9:
            return "{:,.0f}".format(float(n))
        else:
            return "{:,.2f}".format(float(n))
    except Exception:
        return str(n)

def esc(s):
    return html.escape(s or "")

def ensure_fonts(font_path='THSarabun.ttf', bold_font_path='THSarabun Bold.ttf'):
    """Setup Thai fonts for PDF generation"""
    try:
        from resource_path import get_font_path
        font_path = get_font_path(font_path)
        bold_font_path = get_font_path(bold_font_path)
        
        if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
            raise FileNotFoundError("ไม่พบไฟล์ฟอนต์: " + str(font_path) + " หรือ " + str(bold_font_path))
        
        if 'THSarabun' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('THSarabun', font_path))
        if 'THSarabun-Bold' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))
    except Exception as e:
        print("เกิดข้อผิดพลาดในการโหลดฟอนต์: " + str(e))
        raise

def make_pdf_styles():
    """Create paragraph styles for PDF generation"""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TH", fontName="THSarabun", fontSize=12, leading=14))
    styles.add(ParagraphStyle(name="TH-bold", fontName="THSarabun-Bold", fontSize=12, leading=14))
    styles.add(ParagraphStyle(name="TH-center", fontName="THSarabun", fontSize=12, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-right", fontName="THSarabun", fontSize=12, leading=14, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TH-small", fontName="THSarabun", fontSize=10, leading=12))
    styles.add(ParagraphStyle(name="TH-title", fontName="THSarabun-Bold", fontSize=16, leading=18, alignment=TA_CENTER))
    return styles

def generate_pawn_contract_pdf(contract_data, customer_data, product_data, shop_data=None, output_file=None, witness_name=None):
    """
    Generate pawn contract PDF using ReportLab
    """
    try:
        ensure_fonts()
    except Exception as e:
        print("Error setting up fonts: " + str(e))
        return ""
    
    if not output_file:
        contract_number = contract_data.get("contract_number", "unknown")
        output_file = "pawn_contract_" + str(contract_number) + "_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".pdf"
    
    # Load shop config
    try:
        from shop_config_loader import load_shop_config
        default_shop = load_shop_config() or {}
    except:
        default_shop = {}
    
    shop_name = (shop_data or {}).get("name", default_shop.get("name", ""))
    shop_branch = (shop_data or {}).get("branch", default_shop.get("branch", ""))
    shop_address = (shop_data or {}).get("address", default_shop.get("address", ""))
    shop_tax_id = (shop_data or {}).get("tax_id", default_shop.get("tax_id", ""))
    shop_phone = (shop_data or {}).get("phone", default_shop.get("phone", ""))
    authorized_signer = (shop_data or {}).get("authorized_signer", default_shop.get("authorized_signer", ""))
    buyer_signer_name = (shop_data or {}).get("buyer_signer_name", default_shop.get("buyer_signer_name", ""))
    witness_name = (shop_data or {}).get("witness_name", default_shop.get("witness_name", ""))
    
    contract_number = contract_data.get("contract_number", "N/A")
    copy_number = contract_data.get("copy_number", 1)
    place_full = shop_name + " " + (shop_branch if shop_branch else "")
    place_full = place_full if place_full else shop_name
    
    start_date_raw = contract_data.get("start_date", "")
    end_date_raw = contract_data.get("end_date", "")
    start_time = contract_data.get("start_time")
    start_dt_for_display = start_date_raw + " " + start_time if (start_time and start_date_raw) else start_date_raw
    
    start_date_th = thai_date(start_dt_for_display, include_time=bool(start_time)) or "N/A"
    end_date_th = thai_date(end_date_raw) or "N/A"
    
    days_count = contract_data.get("days_count")
    pawn_amount = contract_data.get("pawn_amount", 0)
    redemption_amount = contract_data.get("total_redemption", pawn_amount)
    
    # Customer data
    full_name = (customer_data.get("full_name") or 
                (customer_data.get('first_name','') + " " + customer_data.get('last_name','')).strip()) or "-"
    id_card = customer_data.get("id_card", "-")
    age = customer_data.get("age")
    phone = customer_data.get("phone", "-")
    
    # Address
    addr_parts = [p for p in [
        customer_data.get('house_number',''),
        customer_data.get('street',''),
        customer_data.get('subdistrict',''),
        customer_data.get('district',''),
        customer_data.get('province',''),
        customer_data.get('postcode','')
    ] if p]
    addr_text = " ".join(addr_parts) if addr_parts else "-"
    
    # Product data
    brand = product_data.get("brand", "")
    model = product_data.get("model", "") or product_data.get("name", "")
    color = product_data.get("color", "")
    imei1 = product_data.get("imei1") or product_data.get("IMEI1") or ""
    imei2 = product_data.get("imei2") or product_data.get("IMEI2") or ""
    serial = product_data.get("serial_number") or product_data.get("serial") or ""
    condition = product_data.get("condition", "สภาพโดยรวมดี")
    accessories = product_data.get("accessories", "สายชาร์จและกล่องเดิม")
    
    # Witness
    witness = witness_name or contract_data.get("witness_name") or "นางสาวมั่นใจ ถูกต้อง"
    
    # Copy number
    copy_txt = str(int(copy_number)) if isinstance(copy_number, (int, float)) else esc(str(copy_number))
    
    # Create PDF
    doc = SimpleDocTemplate(output_file, pagesize=A4, 
                           rightMargin=16*mm, leftMargin=16*mm, 
                           topMargin=16*mm, bottomMargin=16*mm)
    story = []
    styles = make_pdf_styles()
    
    # Title
    story.append(Paragraph("สัญญาขายฝาก (โทรศัพท์มือถือ)", styles["TH-title"]))
    story.append(Spacer(1, 12))
    
    # Contract info table
    contract_info_data = [
        ["เลขที่สัญญา:", contract_number, "ฉบับที่:", copy_txt],
        ["ทำที่:", place_full, "วันที่:", start_date_th]
    ]
    
    contract_table = Table(contract_info_data, colWidths=[3*cm, 6*cm, 2*cm, 5*cm])
    contract_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'THSarabun'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'THSarabun-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'THSarabun-Bold'),
    ]))
    
    story.append(contract_table)
    story.append(Spacer(1, 12))
    
    # Customer info
    customer_info = "ระหว่าง " + full_name
    if isinstance(age, (int, float)):
        customer_info += " อายุ " + str(int(age)) + " ปี"
    customer_info += " เลขบัตรประจำตัวประชาชน " + id_card + "<br/>"
    customer_info += "ที่อยู่ " + addr_text + " โทร " + phone
    
    story.append(Paragraph(customer_info, styles["TH"]))
    story.append(Spacer(1, 6))
    
    # Shop info
    shop_info = "กับ " + shop_name + " " + shop_branch + " เลขประจำตัวผู้เสียภาษี " + shop_tax_id + "<br/>"
    shop_info += "ที่อยู่ " + shop_address + " โทร " + shop_phone
    
    story.append(Paragraph(shop_info, styles["TH"]))
    story.append(Spacer(1, 6))
    
    # Product details
    product_details = "โทรศัพท์มือถือยี่ห้อ " + (brand or 'ไม่ระบุ') + " รุ่น " + (model or 'ไม่ระบุ')
    if color:
        product_details += " สี " + color
    product_details += "<br/>"
    product_details += "เลข IMEI 1: " + imei1 + " เลข IMEI 2: " + imei2 + "<br/>"
    product_details += "เลข Serial: " + serial + "<br/>"
    product_details += "สภาพ: " + condition + "<br/>"
    product_details += "อุปกรณ์ประกอบ: " + accessories
    
    story.append(Paragraph(product_details, styles["TH"]))
    story.append(Spacer(1, 12))
    
    # Terms
    terms = [
        "ข้อ 1. ผู้ซื้อฝากตกลงรับซื้อฝากทรัพย์สินดังกล่าวในราคา " + money(pawn_amount) + " บาทถ้วน และผู้ขายฝากตกลงขายฝากในราคาดังกล่าว โดยผู้ขายฝากได้รับเงินครบถ้วนแล้วในวันทำสัญญา",
        "ข้อ 2. ผู้ขายฝากมีสิทธิไถ่ถอนทรัพย์สินภายในกำหนด " + (str(days_count) if days_count else '-') + " วัน นับแต่วันที่ทำสัญญา โดยต้องชำระเงินจำนวน " + money(redemption_amount) + " บาทถ้วน ภายในวันที่ " + end_date_th + " เวลาไม่เกิน 18.00 น.",
        "ข้อ 3. หากผู้ขายฝากไม่ชำระเงินไถ่ถอนภายในกำหนดตามข้อ 2 ให้ถือว่าผู้ขายฝากสละสิทธิในการไถ่ถอน และผู้ซื้อฝากมีสิทธิจัดการทรัพย์สินดังกล่าวได้โดยชอบ",
        "ข้อ 4. สัญญาฉบับนี้มีผลผูกพันคู่สัญญาทั้งสองฝ่าย และมีพยานเป็นผู้ลงนามรับรอง"
    ]
    
    for term in terms:
        story.append(Paragraph(term, styles["TH"]))
        story.append(Spacer(1, 6))
    
    # Receipt
    receipt_text = "ผู้ขายฝากได้รับเงินจำนวน " + money(pawn_amount) + " บาทถ้วนแล้วเรียบร้อยในวันทำสัญญา"
    story.append(Paragraph(receipt_text, styles["TH"]))
    story.append(Spacer(1, 6))
    
    # Confirmation
    confirmation_text = "คู่สัญญาได้อ่านและเข้าใจข้อความในสัญญาฉบับนี้โดยตลอดดีแล้ว จึงได้ตกลงลงนามและยอมรับผูกพันตามสัญญานี้ทุกประการ"
    story.append(Paragraph(confirmation_text, styles["TH"]))
    story.append(Spacer(1, 12))
    
    # Signatures
    signature_data = [
        ["ลงชื่อ ______________________________", "ลงชื่อ ______________________________", "ลงชื่อ ______________________________"],
        ["( " + full_name + " )", "( " + buyer_signer_name + " )", "( " + witness + " )"],
        ["ผู้ขายฝาก", "ผู้ซื้อฝาก", "พยาน"]
    ]
    
    signature_table = Table(signature_data, colWidths=[6*cm, 6*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'THSarabun'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, 1), 'THSarabun-Bold'),
    ]))
    
    story.append(signature_table)
    story.append(Spacer(1, 12))
    
    # Footer
    footer_text = "เอกสารสร้างโดยระบบ | เลขที่สัญญา: " + contract_number + " | สร้างเมื่อ: " + datetime.now().strftime('%d/%m/%Y %H:%M')
    story.append(Paragraph(footer_text, styles["TH-small"]))
    
    # Build PDF
    doc.build(story)
    print("Successfully created pawn contract PDF: " + str(output_file))
    return output_file
