# generate_pawn_ticket_pdf.py
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, Optional, List
import os
import html

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    KeepInFrame, SimpleDocTemplate
)
from reportlab.lib.units import mm

# (ยังคงรองรับ shop_config_loader ถ้ามี)
try:
    from shop_config_loader import load_shop_config
except Exception:
    def load_shop_config():
        return {
            "name": "ร้านตัวอย่าง",
            "branch": "สาขาตัวอย่าง",
            "address": "123/45 ถ.ตัวอย่าง ต.ตัวอย่าง อ.ตัวอย่าง จ.ตัวอย่าง 10000"
        }

# ---------- Utils ----------
TH_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def buddhist_year(dt: datetime) -> int:
    return dt.year + 543

def thai_date(date_str: str, include_time: bool=False) -> str:
    """
    รองรับ 'YYYY-MM-DD' หรือ 'DD/MM/YYYY' หรือ 'YYYY-MM-DD HH:MM'
    คืนค่าเป็นวันที่ไทย (พ.ศ.) เช่น '14 ตุลาคม 2568' หรือ '14 ตุลาคม 2568 เวลา 10:30 น.'
    """
    if not date_str or date_str == "N/A":
        return "N/A"
    ds = date_str.strip()
    dt = None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(ds, fmt)
            break
        except Exception:
            continue
    if not dt:
        return ds

    day = dt.day
    month_name = TH_MONTHS[dt.month - 1]
    year_th = buddhist_year(dt)
    if include_time or ("%H" in ds and "%M" in ds):
        return f"{day} {month_name} {year_th} เวลา {dt.strftime('%H:%M')} น."
    return f"{day} {month_name} {year_th}"

def money(n) -> str:
    try:
        return f"{float(n):,.0f}" if abs(float(n) - int(float(n))) < 1e-9 else f"{float(n):,.2f}"
    except Exception:
        return str(n)

def esc(s: Optional[str]) -> str:
    return html.escape(s or "")

# ---------- Font Setup ----------
def ensure_fonts(font_path='THSarabun.ttf', bold_font_path='THSarabun Bold.ttf'):
    """Setup Thai fonts for PDF generation"""
    try:
        from resource_path import get_font_path
        font_path = get_font_path(font_path)
        bold_font_path = get_font_path(bold_font_path)
        
        if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
            raise FileNotFoundError(f"ไม่พบไฟล์ฟอนต์: {font_path} หรือ {bold_font_path}")
        
        if 'THSarabun' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('THSarabun', font_path))
        if 'THSarabun-Bold' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการโหลดฟอนต์: {e}")
        raise

# ---------- PDF Styles ----------
def make_pdf_styles():
    """Create paragraph styles for PDF generation"""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TH", fontName="THSarabun", fontSize=12, leading=14))
    styles.add(ParagraphStyle(name="TH-bold", fontName="THSarabun-Bold", fontSize=12, leading=14))
    styles.add(ParagraphStyle(name="TH-h", fontName="THSarabun-Bold", fontSize=18, leading=20, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-sub", fontName="THSarabun-Bold", fontSize=14, leading=16, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-right", fontName="THSarabun", fontSize=12, leading=14, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TH-small", fontName="THSarabun", fontSize=10, leading=12))
    return styles

# ---------- Main PDF generator ----------
def generate_pawn_ticket_from_data(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    output_file: Optional[str] = None,
    renewal_data: Optional[List[Dict]] = None
) -> str:
    """
    สร้างไฟล์ PDF รูปแบบ 'สัญญาขายฝาก (โทรศัพท์มือถือ)' 
    - ใช้ ReportLab แทน HTML
    - สร้าง PDF เต็มหน้า A4
    - รองรับข้อมูลต่อดอก (renewal_data)
    """
    try:
        ensure_fonts()
    except Exception as e:
        print(f"Error setting up fonts: {e}")
        return ""
    
    if not output_file:
        contract_number = contract_data.get("contract_number", "unknown")
        output_file = f"pawn_contract_{contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    styles = make_pdf_styles()
    
    # โหลดค่าร้านจาก config
    default_shop = load_shop_config() or {}
    shop_name = (shop_data or {}).get("name", default_shop.get("name", ""))
    shop_branch = (shop_data or {}).get("branch", default_shop.get("branch", ""))
    shop_address = (shop_data or {}).get("address", default_shop.get("address", ""))
    
    # ข้อมูลสัญญา
    contract_number = contract_data.get("contract_number", "N/A")
    copy_number = contract_data.get("copy_number", 1)
    start_date_th = thai_date(contract_data.get("start_date", ""))
    end_date_th = thai_date(contract_data.get("end_date", ""))
    days_count = contract_data.get("days_count", 0)
    pawn_amount = contract_data.get("pawn_amount", 0)
    redemption_amount = contract_data.get("total_redemption", pawn_amount)
    
    # ข้อมูลลูกค้า
    full_name = (customer_data.get("full_name") or 
                f"{customer_data.get('first_name','')} {customer_data.get('last_name','')}".strip()) or "-"
    id_card = customer_data.get("id_card", "-")
    age = customer_data.get("age")
    phone = customer_data.get("phone", "-")
    
    # ที่อยู่ลูกค้า
    addr_parts = [p for p in [
        customer_data.get('house_number',''),
        customer_data.get('street',''),
        customer_data.get('subdistrict',''),
        customer_data.get('district',''),
        customer_data.get('province',''),
        customer_data.get('postcode','')
    ] if p]
    addr_text = " ".join(addr_parts) if addr_parts else "-"
    
    # ข้อมูลสินค้า
    brand = product_data.get("brand", "")
    model = product_data.get("model", "") or product_data.get("name", "")
    color = product_data.get("color", "")
    imei1 = product_data.get("imei1") or product_data.get("IMEI1") or ""
    imei2 = product_data.get("imei2") or product_data.get("IMEI2") or ""
    serial = product_data.get("serial_number") or product_data.get("serial") or ""
    condition = product_data.get("condition", "สภาพโดยรวมดี")
    accessories = product_data.get("accessories", "สายชาร์จและกล่องเดิม")
    
    # สร้าง PDF
    doc = SimpleDocTemplate(output_file, pagesize=A4, 
                          rightMargin=20*mm, leftMargin=20*mm, 
                          topMargin=20*mm, bottomMargin=20*mm)
    
    story = []
    
    # หัวเรื่อง
    story.append(Paragraph("สัญญาขายฝาก (โทรศัพท์มือถือ)", styles["TH-h"]))
    story.append(Spacer(1, 6*mm))
    
    # ข้อมูลสัญญา
    contract_info = [
        [Paragraph("สัญญาเลขที่:", styles["TH-bold"]), Paragraph(contract_number, styles["TH"]),
         Paragraph("ฉบับที่:", styles["TH-bold"]), Paragraph(str(copy_number), styles["TH"])],
        [Paragraph("ทำที่:", styles["TH-bold"]), Paragraph(f"{shop_name} {shop_branch}", styles["TH"]),
         Paragraph("วันที่:", styles["TH-bold"]), Paragraph(start_date_th, styles["TH"])]
    ]
    
    contract_table = Table(contract_info, colWidths=[30*mm, 50*mm, 30*mm, 50*mm])
    contract_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'THSarabun', 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(contract_table)
    story.append(Spacer(1, 6*mm))
    
    # คู่สัญญา
    story.append(Paragraph("คู่สัญญา", styles["TH-bold"]))
    story.append(Spacer(1, 2*mm))
    
    customer_info = f"""
    ระหว่าง {full_name}{f" อายุ {int(age)} ปี" if isinstance(age, (int, float)) else ""} 
    เลขบัตรประจำตัวประชาชน {id_card}<br/>
    ที่อยู่ {addr_text} โทร {phone}<br/>
    ซึ่งต่อไปนี้เรียกว่า "ผู้ขายฝาก" ฝ่ายหนึ่ง
    """
    
    shop_info = f"""
    กับ {shop_name} {shop_branch} เลขประจำตัวผู้เสียภาษี {contract_data.get('tax_id','')}<br/>
    ที่ตั้ง {shop_address}  {contract_data.get('shop_phone','')}<br/>
    โดย{contract_data.get('authorized_signer','ผู้มีอำนาจลงนาม')} เป็นผู้มีอำนาจลงนาม 
    ซึ่งต่อไปนี้เรียกว่า "ผู้ซื้อฝาก" อีกฝ่ายหนึ่ง
    """
    
    story.append(Paragraph(customer_info, styles["TH"]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(shop_info, styles["TH"]))
    story.append(Spacer(1, 6*mm))
    
    # รายละเอียดทรัพย์สิน
    story.append(Paragraph("รายละเอียดทรัพย์สินที่ขายฝาก", styles["TH-bold"]))
    story.append(Spacer(1, 2*mm))
    
    product_details = f"""
    โทรศัพท์มือถือยี่ห้อ {brand or 'ไม่ระบุ'} รุ่น {model or 'ไม่ระบุ'}{(" สี " + color) if color else ""}
    {"," if (imei1 or imei2 or serial) else ""} 
    {" IMEI 1: " + imei1 if imei1 else ""}{("," if imei1 and (imei2 or serial) else "")}
    {" IMEI 2: " + imei2 if imei2 else ""}{("," if imei2 and serial else "")}
    {" Serial Number: " + serial if serial else ""} สภาพโดยรวม{condition}<br/>
    อุปกรณ์ที่มากับเครื่อง: {accessories}
    """
    
    story.append(Paragraph(product_details, styles["TH"]))
    story.append(Spacer(1, 6*mm))
    
    # ข้อตกลงและเงื่อนไข
    story.append(Paragraph("ข้อตกลงและเงื่อนไข", styles["TH-bold"]))
    story.append(Spacer(1, 2*mm))
    
    terms = [
        f"ข้อ 1. ผู้ซื้อฝากตกลงรับซื้อฝากทรัพย์สินดังกล่าวในราคา {money(pawn_amount)} บาทถ้วน และผู้ขายฝากตกลงขายฝากในราคาดังกล่าว โดยผู้ขายฝากได้รับเงินครบถ้วนแล้วในวันทำสัญญา",
        f"ข้อ 2. ผู้ขายฝากมีสิทธิไถ่ถอนทรัพย์สินภายในกำหนด {days_count if days_count else '-'} วัน นับแต่วันที่ทำสัญญา โดยต้องชำระเงินจำนวน {money(redemption_amount)} บาทถ้วน ภายในวันที่ {end_date_th} เวลาไม่เกิน 18.00 น.",
        "ข้อ 3. หากผู้ขายฝากไม่ชำระเงินไถ่ถอนภายในกำหนดตามข้อ 2 ให้ถือว่าผู้ขายฝากสละสิทธิในการไถ่ถอน และผู้ซื้อฝากมีสิทธิจัดการทรัพย์สินดังกล่าวได้โดยชอบ",
        "ข้อ 4. ผู้ขายฝากรับรองว่าทรัพย์สินเป็นกรรมสิทธิ์ของตน มิได้มีภาระผูกพัน จำนำ จำนอง หรือคดีพิพาทใด ๆ และยินยอมให้ผู้ซื้อฝากตรวจสอบความถูกต้องของหมายเลข IMEI/Serial ได้",
        "ข้อ 5. ในกรณีสูญหาย/ถูกโจรกรรม ผู้ขายฝากต้องแจ้งความและแจ้งผู้ซื้อฝากทันที ผู้ซื้อฝากไม่รับผิดชอบต่อความเสียหายที่เกิดขึ้นก่อนการไถ่ถอน",
        "ข้อ 6. คู่สัญญาตกลงให้ศาลในเขตที่ตั้งของผู้ซื้อฝากมีเขตอำนาจพิจารณาข้อพิพาทที่อาจเกิดขึ้นจากสัญญานี้"
    ]
    
    for term in terms:
        story.append(Paragraph(term, styles["TH"]))
        story.append(Spacer(1, 2*mm))
    
    # การรับเงินและเอกสารแนบ
    story.append(Paragraph("การรับเงินและเอกสารแนบ", styles["TH-bold"]))
    story.append(Spacer(1, 2*mm))
    
    receipt_text = f"""
    ผู้ขายฝากได้รับเงินจำนวน {money(pawn_amount)} บาทถ้วนแล้วเรียบร้อยในวันทำสัญญา
    พร้อมส่งมอบทรัพย์สินและอุปกรณ์ตามรายการข้างต้นให้แก่ผู้ซื้อฝากครบถ้วน
    โดยมีสำเนาบัตรประชาชนผู้ขายฝาก 1 ฉบับ และรูปถ่ายทรัพย์สินแนบเป็นหลักฐาน
    """
    
    story.append(Paragraph(receipt_text, styles["TH"]))
    story.append(Spacer(1, 6*mm))
    
    # การยืนยันคู่สัญญา
    story.append(Paragraph("การยืนยันคู่สัญญา", styles["TH-bold"]))
    story.append(Spacer(1, 2*mm))
    
    confirmation_text = f"""
    คู่สัญญาได้อ่านและเข้าใจข้อความในสัญญาฉบับนี้โดยตลอดดีแล้ว จึงได้ตกลงลงนามและยอมรับผูกพันตามสัญญานี้ทุกประการ
    ทำขึ้น ณ {shop_name} {shop_branch} เมื่อวันที่ {thai_date(contract_data.get('signed_date') or contract_data.get('start_date', ''))}
    """
    
    story.append(Paragraph(confirmation_text, styles["TH"]))
    story.append(Spacer(1, 8*mm))
    
    # ลายเซ็น
    signatures = [
        [Paragraph("ลงชื่อ ______________________________", styles["TH"]),
         Paragraph("ลงชื่อ ______________________________", styles["TH"]),
         Paragraph("ลงชื่อ ______________________________", styles["TH"])],
        [Paragraph(f"( {full_name} )", styles["TH"]),
         Paragraph(f"( {contract_data.get('buyer_signer_name','______________________________')} )", styles["TH"]),
         Paragraph(f"( {contract_data.get('witness_name','______________________________')} )", styles["TH"])],
        [Paragraph("ผู้ขายฝาก", styles["TH"]),
         Paragraph("ผู้ซื้อฝาก", styles["TH"]),
         Paragraph("พยาน", styles["TH"])]
    ]
    
    sig_table = Table(signatures, colWidths=[60*mm, 60*mm, 60*mm])
    sig_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'THSarabun', 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 6*mm))
    
    # ข้อมูลต่อดอก (ถ้ามี)
    if renewal_data:
        story.append(Paragraph("ประวัติการต่อดอก", styles["TH-bold"]))
        story.append(Spacer(1, 2*mm))
        
        renewal_table_data = [["วันที่ต่อดอก", "ต่อเพิ่ม (วัน)", "รวม"]]
        for renewal in renewal_data:
            renewal_table_data.append([
                thai_date(renewal.get('renewal_date', '')),
                str(renewal.get('extension_days', 0)),
                money(renewal.get('total_amount', 0))
            ])
        
        renewal_table = Table(renewal_table_data, colWidths=[60*mm, 40*mm, 60*mm])
        renewal_table.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'THSarabun', 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(renewal_table)
        story.append(Spacer(1, 6*mm))
    
    # Footer
    footer_text = f"""
    เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    story.append(Paragraph(footer_text, styles["TH-small"]))
    
    # สร้าง PDF
    doc.build(story)
    print(f"Successfully created pawn contract PDF: {output_file}")
    return output_file

# ---------- Main HTML generator ----------
def generate_pawn_contract_html(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    output_file: Optional[str] = None,
    witness_name: Optional[str] = None,
) -> str:
    """
    สร้างไฟล์ HTML รูปแบบ 'สัญญาขายฝาก (โทรศัพท์มือถือ)' ตามเทมเพลตที่ผู้ใช้ให้มา
    - แปลงวันที่เป็นรูปแบบไทย (พ.ศ.)
    - เติมข้อมูลจาก dict ต่าง ๆ
    """
    # โหลดค่าร้านจาก config เป็นค่าเริ่มต้น
    default_shop = load_shop_config() or {}
    shop_name = (shop_data or {}).get("name", default_shop.get("name", ""))
    shop_branch = (shop_data or {}).get("branch", default_shop.get("branch", ""))
    shop_address = (shop_data or {}).get("address", default_shop.get("address", ""))

    contract_number = contract_data.get("contract_number", "N/A")
    copy_number = contract_data.get("copy_number", 1)
    place_full = f"{shop_name} {('สาข' in shop_branch and shop_branch) or f'({shop_branch})' if shop_branch else ''}".replace("()", "").strip()
    place_full = place_full if place_full else shop_name
    place_line = place_full if place_full else "สถานที่ทำสัญญา"

    start_date_raw = contract_data.get("start_date", "")
    end_date_raw = contract_data.get("end_date", "")
    # ถ้าใส่เวลาแยกมาใน contract_data
    start_time = contract_data.get("start_time")  # "HH:MM"
    # รวมเวลาให้ thai_date ตรวจจับเอง
    start_dt_for_display = f"{start_date_raw} {start_time}" if (start_time and start_date_raw) else start_date_raw

    start_date_th = thai_date(start_dt_for_display, include_time=bool(start_time))
    end_date_th = thai_date(end_date_raw)

    days_count = contract_data.get("days_count")
    pawn_amount = contract_data.get("pawn_amount", 0)
    redemption_amount = contract_data.get("total_redemption", pawn_amount)

    # ลูกค้า
    full_name = (customer_data.get("full_name") or f"{customer_data.get('first_name','')} {customer_data.get('last_name','')}".strip()) or "-"
    id_card = customer_data.get("id_card", "-")
    age = customer_data.get("age")
    phone = customer_data.get("phone", "-")
    # สร้างที่อยู่ย่อ
    addr_parts = [p for p in [
        customer_data.get('house_number',''),
        customer_data.get('street',''),
        customer_data.get('subdistrict',''),
        customer_data.get('district',''),
        customer_data.get('province',''),
        customer_data.get('postcode','')
    ] if p]
    addr_text = " ".join(addr_parts) if addr_parts else "-"

    # ทรัพย์สิน
    brand = product_data.get("brand", "")
    model = product_data.get("model", "") or product_data.get("name", "")
    color = product_data.get("color", "")
    imei1 = product_data.get("imei1") or product_data.get("IMEI1") or ""
    imei2 = product_data.get("imei2") or product_data.get("IMEI2") or ""
    serial = product_data.get("serial_number") or product_data.get("serial") or ""
    condition = product_data.get("condition", "สภาพโดยรวมดี")
    accessories = product_data.get("accessories", "สายชาร์จและกล่องเดิม")

    # ชื่อพยาน
    witness = witness_name or contract_data.get("witness_name") or "นางสาวมั่นใจ ถูกต้อง"

    # ฉบับที่
    copy_txt = f"{int(copy_number)}" if isinstance(copy_number, (int, float)) else esc(str(copy_number))

    # เตรียม HTML
    html_doc = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <title>สัญญาขายฝาก (โทรศัพท์มือถือ) – {esc(full_name)} – {esc(contract_number)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    @page {{
      size: A4;
      margin: 16mm;
    }}
    * {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Noto Sans Thai", "TH Sarabun New", "Sarabun", system-ui, -apple-system, "Segoe UI", Tahoma, sans-serif;
      color: #000;
      background: #fff;
      line-height: 1.5;
      font-size: 13.5pt;
    }}
    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto;
      padding: 16mm;
    }}
    h1 {{
      text-align: center;
      font-size: 20pt;
      margin: 0 0 6mm 0;
    }}
    .meta {{
      font-size: 12pt;
      margin-bottom: 6mm;
    }}
    .meta .row {{
      display: flex;
      justify-content: space-between;
      gap: 10mm;
    }}
    .meta .row span {{
      display: inline-block;
    }}
    .section-title {{
      font-weight: 700;
      margin: 3mm 0 1mm 0;
    }}
    p {{
      margin: 2mm 0;
      text-align: justify;
    }}
    .indent {{
      text-indent: 12mm;
    }}
    .number {{
      font-weight: 700;
    }}
    .signatures {{
      margin-top: 8mm;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8mm;
      font-size: 12pt;
    }}
    .sig {{
      text-align: center;
    }}
    .foot {{
      font-size: 10.5pt;
      color: #000;
      margin-top: 6mm;
    }}
    @media print {{
      .page {{ padding: 14mm; }}
      p {{ margin: 1.6mm 0; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>สัญญาขายฝาก (โทรศัพท์มือถือ)</h1>

    <div class="meta">
      <div class="row"><span>สัญญาเลขที่: {esc(contract_number)}</span><span>ฉบับที่: {copy_txt}</span></div>
      <div class="row"><span>ทำที่: {esc(place_line)}</span><span>วันที่: {esc(start_date_th)}</span></div>
    </div>

    <div class="section-title">คู่สัญญา</div>
    <p class="indent">
      ระหว่าง {esc(full_name)}{f" อายุ {int(age)} ปี" if isinstance(age, (int, float)) else ""} เลขบัตรประจำตัวประชาชน {esc(id_card)}
      ที่อยู่ {esc(addr_text)} โทร {esc(phone)}
      ซึ่งต่อไปนี้เรียกว่า “<strong>ผู้ขายฝาก</strong>”
      ฝ่ายหนึ่ง กับ {esc(shop_name)} {esc(shop_branch)} เลขประจำตัวผู้เสียภาษี {esc(contract_data.get('tax_id',''))}
      ที่ตั้ง {esc(shop_address)}  {esc(contract_data.get('shop_phone',''))}
      โดย{esc(contract_data.get('authorized_signer','ผู้มีอำนาจลงนาม'))} เป็นผู้มีอำนาจลงนาม ซึ่งต่อไปนี้เรียกว่า “<strong>ผู้ซื้อฝาก</strong>” อีกฝ่ายหนึ่ง
    </p>

    <div class="section-title">รายละเอียดทรัพย์สินที่ขายฝาก</div>
    <p class="indent">
      โทรศัพท์มือถือยี่ห้อ {esc(brand or 'ไม่ระบุ')} รุ่น {esc(model or 'ไม่ระบุ')}{(" สี " + esc(color)) if color else ""}{"," if (imei1 or imei2 or serial) else ""} 
      {" IMEI 1: " + esc(imei1) if imei1 else ""}{("," if imei1 and (imei2 or serial) else "")}
      {" IMEI 2: " + esc(imei2) if imei2 else ""}{("," if imei2 and serial else "")}
      {" Serial Number: " + esc(serial) if serial else ""} สภาพโดยรวม{esc(condition)}
      อุปกรณ์ที่มากับเครื่อง: {esc(accessories)}
    </p>

    <div class="section-title">ข้อตกลงและเงื่อนไข</div>
    <p class="indent"><span class="number">ข้อ 1.</span>
      ผู้ซื้อฝากตกลงรับซื้อฝากทรัพย์สินดังกล่าวในราคา <strong>{money(pawn_amount)} บาทถ้วน</strong>
      และผู้ขายฝากตกลงขายฝากในราคาดังกล่าว โดยผู้ขายฝากได้รับเงินครบถ้วนแล้วในวันทำสัญญา
    </p>
    <p class="indent"><span class="number">ข้อ 2.</span>
      ผู้ขายฝากมีสิทธิไถ่ถอนทรัพย์สินภายในกำหนด <strong>{esc(str(days_count)) if days_count else '-' } วัน</strong>
      นับแต่วันที่ทำสัญญา โดยต้องชำระเงินจำนวน <strong>{money(redemption_amount)} บาทถ้วน</strong>
      ภายในวันที่ <strong>{esc(end_date_th)}</strong> เวลาไม่เกิน 18.00 น.
    </p>
    <p class="indent"><span class="number">ข้อ 3.</span>
      หากผู้ขายฝากไม่ชำระเงินไถ่ถอนภายในกำหนดตามข้อ 2 ให้ถือว่าผู้ขายฝาก
      สละสิทธิในการไถ่ถอน และผู้ซื้อฝากมีสิทธิจัดการทรัพย์สินดังกล่าวได้โดยชอบ
    </p>
    <p class="indent"><span class="number">ข้อ 4.</span>
      ผู้ขายฝากรับรองว่าทรัพย์สินเป็นกรรมสิทธิ์ของตน มิได้มีภาระผูกพัน จำนำ จำนอง หรือคดีพิพาทใด ๆ
      และยินยอมให้ผู้ซื้อฝากตรวจสอบความถูกต้องของหมายเลข IMEI/Serial ได้
    </p>
    <p class="indent"><span class="number">ข้อ 5.</span>
      ในกรณีสูญหาย/ถูกโจรกรรม ผู้ขายฝากต้องแจ้งความและแจ้งผู้ซื้อฝากทันที
      ผู้ซื้อฝากไม่รับผิดชอบต่อความเสียหายที่เกิดขึ้นก่อนการไถ่ถอน
    </p>
    <p class="indent"><span class="number">ข้อ 6.</span>
      คู่สัญญาตกลงให้ศาลในเขตที่ตั้งของผู้ซื้อฝากมีเขตอำนาจพิจารณาข้อพิพาทที่อาจเกิดขึ้นจากสัญญานี้
    </p>

    <div class="section-title">การรับเงินและเอกสารแนบ</div>
    <p class="indent">
      ผู้ขายฝากได้รับเงินจำนวน {money(pawn_amount)} บาทถ้วนแล้วเรียบร้อยในวันทำสัญญา
      พร้อมส่งมอบทรัพย์สินและอุปกรณ์ตามรายการข้างต้นให้แก่ผู้ซื้อฝากครบถ้วน
      โดยมีสำเนาบัตรประชาชนผู้ขายฝาก 1 ฉบับ และรูปถ่ายทรัพย์สินแนบเป็นหลักฐาน
    </p>

    <div class="section-title">การยืนยันคู่สัญญา</div>
    <p class="indent">
      คู่สัญญาได้อ่านและเข้าใจข้อความในสัญญาฉบับนี้โดยตลอดดีแล้ว จึงได้ตกลงลงนามและยอมรับผูกพันตามสัญญานี้ทุกประการ
      ทำขึ้น ณ {esc(place_line)} เมื่อวันที่ {esc(thai_date(contract_data.get('signed_date') or start_date_raw))}
    </p>

    <div class="signatures">
      <div class="sig">
        <div>ลงชื่อ ______________________________</div>
        <div>( {esc(full_name)} )</div>
        <div>ผู้ขายฝาก</div>
      </div>
      <div class="sig">
        <div>ลงชื่อ ______________________________</div>
        <div>( {esc(contract_data.get('buyer_signer_name','                  '))} )</div>
        <div>ผู้ซื้อฝาก</div>
      </div>
      <div class="sig">
        <div>ลงชื่อ ______________________________</div>
        <div>(               )</div>
        <div>พยาน</div>
      </div>
    </div>

    <div class="foot">
      เอกสารสร้างโดยระบบ | เลขที่สัญญา: {esc(contract_number)} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
  </div>
</body>
</html>"""

    if not output_file:
        output_file = f"pawn_contract_{contract_number or 'unknown'}.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return output_file


# ----- quick demo -----
if __name__ == "__main__":
    contract = {
        "contract_number": "CF-20259192",
        "copy_number": 1,
        "start_date": "2025-10-14",
        "start_time": "10:30",
        "end_date": "2025-11-13",
        "days_count": 30,
        "pawn_amount": 10000,
        "total_redemption": 11000,
        "tax_id": "0-1234-56789-01-2",
        "shop_phone": "02-345-6789",
        "authorized_signer": "นายประเสริฐ ใจดี",
        "buyer_signer_name": "นายประเสริฐ ใจดี",
        "signed_date": "2025-10-14",
    }
    customer = {
        "first_name": "สมชาย",
        "last_name": "ใจดี",
        "age": 32,
        "phone": "08-1234-5678",
        "id_card": "1-2345-67890-12-3",
        "house_number": "99/9",
        "street": "ถ.ตัวอย่าง",
        "subdistrict": "แขวงตัวอย่าง",
        "district": "เขตตัวอย่าง",
        "province": "กรุงเทพมหานคร",
        "postcode": "10000",
    }
    product = {
        "brand": "Apple",
        "name": "iPhone 17",
        "color": "ดำ",
        "imei1": "3567 8901 2345 678",
        "imei2": "3567 8901 2345 679",
        "serial_number": "SN1234567890",
        "condition": "ดี มีรอยขนแมวเล็กน้อย",
        "accessories": "สายชาร์จแท้และกล่องเดิม",
    }
    shop = {
        "name": "ร้านไอโปรโปรโมบาย",
        "branch": "สาขาหล่มสัก",
        "address": "14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110",
    }

    out = generate_pawn_contract_html(contract, customer, product, shop, output_file="pawn_contract_demo.html")
    print("Created:", out)