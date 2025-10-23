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
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
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

def buddhist_year(dt):
    return dt.year + 543

def thai_date(date_str, include_time=False):
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
        return str(day) + " " + month_name + " " + str(year_th) + " เวลา " + dt.strftime('%H:%M') + " น."
    return str(day) + " " + month_name + " " + str(year_th)

def money(n):
    try:
        if abs(float(n) - int(float(n))) < 1e-9:
            return "{:,.0f}".format(float(n))
        else:
            return "{:,.2f}".format(float(n))
    except Exception:
        return str(n)

def esc(s):
    return html.escape(str(s) if s is not None else "")

# ---------- Font Setup ----------
def ensure_fonts(font_path='angsa.ttf', bold_font_path='angsa.ttf'):
    """Setup Thai fonts for PDF generation with improved rendering"""
    try:
        from resource_path import get_font_path
        font_path = get_font_path(font_path)
        bold_font_path = get_font_path(bold_font_path)
        
        if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
            raise FileNotFoundError("ไม่พบไฟล์ฟอนต์: " + str(font_path) + " หรือ " + str(bold_font_path))
        
        # ลงทะเบียนฟอนต์ด้วยการตั้งค่าที่ดีขึ้นสำหรับภาษาไทย
        if 'Angsa' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Angsa', font_path, subfontIndex=0))
        if 'Angsa-Bold' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Angsa-Bold', bold_font_path, subfontIndex=0))
            
        print("ฟอนต์ภาษาไทยโหลดสำเร็จ - Angsa และ Angsa-Bold")
    except Exception as e:
        print("เกิดข้อผิดพลาดในการโหลดฟอนต์: " + str(e))
        raise

# ---------- PDF Styles ----------
def make_pdf_styles():
    """Create paragraph styles for PDF generation - compact layout"""
    styles = getSampleStyleSheet()
    
    # หัวข้อหลัก - ลดขนาดลง
    styles.add(ParagraphStyle(
        name="TH-h", 
        fontName="Angsa-Bold", 
        fontSize=18,
        leading=27,  # เพิ่ม leading มากขึ้นเพื่อป้องกันวรรณยุกต์ทับสระ (1.5x)
        alignment=TA_CENTER,
        wordWrap='CJK',
        spaceBefore=0,
        spaceAfter=2
    ))
    
    # หัวข้อย่อย
    styles.add(ParagraphStyle(
        name="TH-bold", 
        fontName="Angsa-Bold", 
        fontSize=12,
        leading=18,  # เพิ่ม leading (1.5x)
        alignment=TA_LEFT,
        wordWrap='CJK',
        spaceBefore=1,
        spaceAfter=1
    ))
    
    # ข้อความทั่วไป
    styles.add(ParagraphStyle(
        name="TH", 
        fontName="Angsa", 
        fontSize=11,
        leading=17,  # เพิ่ม leading เพื่อให้วรรณยุกต์ไม่ทับสระ (1.55x)
        alignment=TA_LEFT,
        wordWrap='CJK',
        spaceBefore=0.5,
        spaceAfter=0.5
    ))
    
    # ข้อตกลง - เล็กมาก
    styles.add(ParagraphStyle(
        name="TH-tiny", 
        fontName="Angsa", 
        fontSize=9,
        leading=14,  # เพิ่ม leading (1.55x)
        alignment=TA_LEFT,
        wordWrap='CJK',
        spaceBefore=0.5,
        spaceAfter=0.5
    ))
    
    # ข้อความเล็ก
    styles.add(ParagraphStyle(
        name="TH-small", 
        fontName="Angsa", 
        fontSize=9,
        leading=14,  # เพิ่ม leading (1.55x)
        alignment=TA_LEFT,
        wordWrap='CJK'
    ))
    
    # ข้อความขวา
    styles.add(ParagraphStyle(
        name="TH-right", 
        fontName="Angsa", 
        fontSize=11,
        leading=17,  # เพิ่ม leading (1.55x)
        alignment=TA_RIGHT,
        wordWrap='CJK'
    ))
    
    return styles

# ---------- Main PDF generator ----------
def generate_pawn_ticket_pdf_data(
    contract_data,
    customer_data,
    product_data,
    shop_data=None,
    output_file=None,
):
    """
    PDF: ครึ่งหน้า A4, margin = 0, ฟอนต์หลักใหญ่, ส่วน 'ข้อตกลงและเงื่อนไข' = ย่อหน้าเดียว 12pt
    """
    # 1) ฟอนต์ไทย (Angsa/Angsa-Bold) จาก ensure_fonts()
    try:
        ensure_fonts()
    except Exception as e:
        print(f"Error setting up fonts: {e}")
        return ""

    # 2) เตรียมข้อมูล
    if not output_file:
        contract_number = contract_data.get("contract_number", "unknown")
        output_file = f"pawn_contract_max_{contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    default_shop = load_shop_config() or {}
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
    start_date_th = thai_date(contract_data.get("start_date", ""))
    end_date_th = thai_date(contract_data.get("end_date", ""))
    start_signed = thai_date(contract_data.get('signed_date') or contract_data.get('start_date', ''))
    days_count = contract_data.get("days_count")
    pawn_amount = contract_data.get("pawn_amount", 0)
    redemption_amount = contract_data.get("total_redemption", pawn_amount)

    full_name = (customer_data.get("full_name") or f"{customer_data.get('first_name','')} {customer_data.get('last_name','')}".strip()) or "-"
    id_card = customer_data.get("id_card", "-")
    age = customer_data.get("age")
    phone = customer_data.get("phone", "-")
    addr_parts = [p for p in [
        customer_data.get('house_number',''),
        customer_data.get('street',''),
        customer_data.get('subdistrict',''),
        customer_data.get('district',''),
        customer_data.get('province',''),
        customer_data.get('postcode','')
    ] if p]
    addr_text = " ".join(addr_parts) if addr_parts else "-"

    brand = product_data.get("brand", "")
    model = product_data.get("model", "") or product_data.get("name", "")
    color = product_data.get("color", "")
    imei1 = product_data.get("imei1") or product_data.get("IMEI1") or ""
    imei2 = product_data.get("imei2") or product_data.get("IMEI2") or ""
    serial = product_data.get("serial_number") or product_data.get("serial") or ""
    condition = product_data.get("condition", "สภาพโดยรวมดี")
    accessories = product_data.get("accessories", "สายชาร์จและกล่องเดิม")

    place_line = f"{shop_name} {shop_branch}".strip()

    # 3) หน้า A4 เต็ม + margin 0.5mm
    PAGE_W, PAGE_H = A4[0], A4[1]  # 210 x 297 mm
    margin = 0.5*mm
    doc = BaseDocTemplate(
        output_file,
        pagesize=(PAGE_W, PAGE_H),
        leftMargin=margin, rightMargin=margin, topMargin=margin, bottomMargin=margin
    )
    frame = Frame(margin, margin, PAGE_W-2*margin, PAGE_H-2*margin, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    doc.addPageTemplates([PageTemplate(id="A4-small-margin", frames=[frame])])

    # 4) สไตล์: ตัวหนังสือใหญ่ + line spacing น้อยที่สุด
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TH-Title",
        fontName="Angsa-Bold",
        fontSize=31,           # หัวเรื่องใหญ่ (ลด 1)
        leading=35,            # line spacing น้อยที่สุด
        alignment=TA_CENTER,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="TH-Big",
        fontName="Angsa",
        fontSize=19,           # เนื้อหาหลัก (ลด 1)
        leading=21,            # line spacing น้อยที่สุด
        alignment=TA_LEFT,
        spaceBefore=1,
        spaceAfter=1,
        wordWrap="CJK"
    ))
    styles.add(ParagraphStyle(
        name="TH-BigBold",
        fontName="Angsa-Bold",
        fontSize=19,           # (ลด 1)
        leading=21,
        alignment=TA_LEFT,
        spaceBefore=1,
        spaceAfter=1,
        wordWrap="CJK"
    ))
    styles.add(ParagraphStyle(
        name="TH-Terms",
        fontName="Angsa",
        fontSize=15,           # เงื่อนไข (ลด 1)
        leading=17,            # line spacing น้อยที่สุด
        alignment=TA_JUSTIFY,
        spaceBefore=1,
        spaceAfter=1,
        wordWrap="CJK"
    ))
    styles.add(ParagraphStyle(
        name="TH-Foot",
        fontName="Angsa",
        fontSize=13,           # (ลด 1)
        leading=15,
        alignment=TA_RIGHT,
        spaceBefore=0,
        spaceAfter=0
    ))

    # 5) สร้างเนื้อหาให้เหมาะกับหน้า A4 เต็ม
    story = []
    # หัวเรื่อง
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("สัญญาขายฝาก (โทรศัพท์มือถือ)", styles["TH-Title"]))

    # บรรทัดสัญญาเลขที่ / ฉบับที่ / ทำที่ / วันที่
    meta_tbl = Table(
        [
            [Paragraph("สัญญาเลขที่:", styles["TH-BigBold"]), Paragraph(esc(contract_number), styles["TH-Big"]),
             Paragraph("ฉบับที่:", styles["TH-BigBold"]), Paragraph(str(copy_number), styles["TH-Big"])],
            [Paragraph("ทำที่:", styles["TH-BigBold"]), Paragraph(esc(place_line), styles["TH-Big"]),
             Paragraph("วันที่:", styles["TH-BigBold"]), Paragraph(esc(start_date_th), styles["TH-Big"])],
        ],
        colWidths=[50*mm, 70*mm, 40*mm, 50*mm],  # จัดให้พอดีกว้างหน้า (ปรับตาม margin)
        hAlign='LEFT'
    )
    meta_tbl.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Angsa', 14),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 2*mm))

    # คู่สัญญา
    party_text = (
        f"ระหว่าง {esc(full_name)}{(' อายุ ' + str(int(age)) + ' ปี') if isinstance(age,(int,float)) else ''} "
        f"เลขบัตรประชาชน {esc(id_card)} ที่อยู่ {esc(addr_text)} โทร {esc(phone)} "
        f"ซึ่งเรียกว่า \"ผู้ขายฝาก\" กับ {esc(shop_name)} {esc(shop_branch)} "
        f"เลขประจำตัวผู้เสียภาษี {esc(shop_tax_id)} ที่ตั้ง {esc(shop_address)} โทร {esc(shop_phone)} "
        f"โดย{esc(authorized_signer)} เป็นผู้มีอำนาจลงนาม ซึ่งเรียกว่า \"ผู้ซื้อฝาก\""
    )
    story.append(Paragraph(party_text, styles["TH-Big"]))
    story.append(Spacer(1, 2*mm))

    # รายละเอียดทรัพย์สิน
    prod_text = (
        f"โทรศัพท์มือถือยี่ห้อ {esc(brand or 'ไม่ระบุ')} รุ่น {esc(model or 'ไม่ระบุ')}"
        f"{(' สี ' + esc(color)) if color else ''}"
        f"{(' IMEI1: ' + esc(imei1)) if imei1 else ''}"
        f"{(' IMEI2: ' + esc(imei2)) if imei2 else ''}"
        f"{(' Serial: ' + esc(serial)) if serial else ''} "
        f"สภาพ{esc(condition)} อุปกรณ์: {esc(accessories)}"
    )
    story.append(Paragraph(prod_text, styles["TH-Big"]))
    story.append(Spacer(1, 2*mm))

    # ข้อตกลงและเงื่อนไข
    terms_text = (
        f"ข้อ 1. ผู้ซื้อฝากตกลงรับซื้อฝากทรัพย์สินในราคา {money(pawn_amount)} บาท ผู้ขายฝากได้รับเงินครบแล้ว "
        f"ข้อ 2. ผู้ขายฝากมีสิทธิไถ่ถอนภายใน {esc(str(days_count)) if days_count else '-'} วัน โดยชำระเงิน {money(redemption_amount)} บาท "
        f"ภายในวันที่ {esc(end_date_th)} เวลา 18.00 น. "
        "ข้อ 3. หากไม่ชำระภายในกำหนด ถือว่าสละสิทธิ และผู้ซื้อฝากมีสิทธิจัดการทรัพย์สิน "
        "ข้อ 4. ผู้ขายฝากรับรองว่าทรัพย์สินเป็นกรรมสิทธิ์ของตน ไม่มีภาระผูกพัน และยินยอมให้ตรวจสอบ IMEI/Serial "
        "ข้อ 5. กรณีสูญหาย/โจรกรรม ผู้ขายฝากต้องแจ้งความและแจ้งผู้ซื้อฝากทันที "
        "ข้อ 6. ศาลในเขตที่ตั้งผู้ซื้อฝากมีอำนาจพิจารณาข้อพิพาท"
    )
    story.append(Paragraph(terms_text, styles["TH-Terms"]))
    story.append(Spacer(1, 2*mm))

    # การรับเงินและยืนยัน
    confirm_text = (
        f"ผู้ขายฝากได้รับเงิน {money(pawn_amount)} บาท พร้อมส่งมอบทรัพย์สินและอุปกรณ์ครบถ้วน "
        f"คู่สัญญาได้อ่านและเข้าใจข้อความโดยตลอดแล้ว จึงลงนามและยอมรับผูกพันตามสัญญา "
        f"ทำ ณ {esc(place_line)} วันที่ {esc(start_signed)}"
    )
    story.append(Paragraph(confirm_text, styles["TH-Big"]))
    story.append(Spacer(1, 5*mm))

    # ลายเซ็น (3 ช่อง)
    sig_tbl = Table(
        [
            [Paragraph("ลงชื่อ ____________________", styles["TH-Big"]),
             Paragraph("ลงชื่อ ____________________", styles["TH-Big"]),
             Paragraph("ลงชื่อ ____________________", styles["TH-Big"])],
            [Paragraph(f"( {esc(full_name)} )", styles["TH-Big"]),
             Paragraph(f"( {esc(buyer_signer_name or authorized_signer or 'ผู้มีอำนาจลงนาม')} )", styles["TH-Big"]),
             Paragraph(f"( {esc(witness_name or 'พยาน')} )", styles["TH-Big"])],
            [Paragraph("ผู้ขายฝาก", styles["TH-Big"]),
             Paragraph("ผู้ซื้อฝาก", styles["TH-Big"]),
             Paragraph("พยาน", styles["TH-Big"])],
        ],
        colWidths=[(PAGE_W-2*margin)/3.0, (PAGE_W-2*margin)/3.0, (PAGE_W-2*margin)/3.0],
        hAlign='CENTER'
    )
    sig_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sig_tbl)

    # Footer
    story.append(Spacer(1, 5*mm))
    foot_text = f"เอกสารสร้างโดยระบบ | เลขที่: {contract_number} | {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    story.append(Paragraph(foot_text, styles["TH-Foot"]))

    # 6) สร้างไฟล์
    doc.build(story)
    print(f"Successfully created pawn contract PDF: {output_file}")
    return output_file


# ---------- Main HTML generator ----------
def generate_pawn_contract_html(
    contract_data,
    customer_data,
    product_data,
    shop_data=None,
    output_file=None,
    witness_name=None,
):
    """
    สัญญาขายฝาก (โทรศัพท์มือถือ)
    - ครึ่งหน้า A4 (สูง 148.5mm)
    - ไม่มีขอบพิมพ์เลย (0mm)
    - ตัวอักษรหลัก "ใหญ่ที่สุดเท่าที่เหมาะสม" (ตั้งฐานที่ 22pt)
    - เงื่อนไขรวมเป็นย่อหน้าเดียว 12pt
    """
    # โหลดข้อมูลร้าน
    default_shop = load_shop_config() or {}
    shop_name = (shop_data or {}).get("name", default_shop.get("name", ""))
    shop_branch = (shop_data or {}).get("branch", default_shop.get("branch", ""))
    shop_address = (shop_data or {}).get("address", default_shop.get("address", ""))
    shop_tax_id = (shop_data or {}).get("tax_id", default_shop.get("tax_id", ""))
    shop_phone = (shop_data or {}).get("phone", default_shop.get("phone", ""))
    authorized_signer = (shop_data or {}).get("authorized_signer", default_shop.get("authorized_signer", ""))
    buyer_signer_name = (shop_data or {}).get("buyer_signer_name", default_shop.get("buyer_signer_name", ""))
    witness_name = (shop_data or {}).get("witness_name", default_shop.get("witness_name", ""))

    # สัญญา
    contract_number = contract_data.get("contract_number", "N/A")
    copy_number = contract_data.get("copy_number", 1)
    place_line = f"{shop_name} {shop_branch}".strip()

    start_date_raw = contract_data.get("start_date", "")
    end_date_raw = contract_data.get("end_date", "")
    start_time = contract_data.get("start_time")
    start_dt_for_display = f"{start_date_raw} {start_time}" if start_time else start_date_raw
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

    witness = witness_name or contract_data.get("witness_name") or "นางสาวมั่นใจ ถูกต้อง"

    # เงื่อนไข: ย่อหน้าเดียว 12pt
    terms_text = (
        f"ข้อ 1. ผู้ซื้อฝากตกลงรับซื้อฝากทรัพย์สินในราคา {money(pawn_amount)} บาท ผู้ขายฝากได้รับเงินครบแล้ว "
        f"ข้อ 2. ผู้ขายฝากมีสิทธิไถ่ถอนภายใน {esc(str(days_count)) if days_count else '-'} วัน โดยชำระเงิน {money(redemption_amount)} บาท "
        f"ภายในวันที่ {esc(end_date_th)} เวลา 18.00 น. "
        "ข้อ 3. หากไม่ชำระภายในกำหนด ถือว่าสละสิทธิ และผู้ซื้อฝากมีสิทธิจัดการทรัพย์สิน "
        "ข้อ 4. ผู้ขายฝากรับรองว่าทรัพย์สินเป็นกรรมสิทธิ์ของตน ไม่มีภาระผูกพัน และยินยอมให้ตรวจสอบ IMEI/Serial "
        "ข้อ 5. กรณีสูญหาย/โจรกรรม ผู้ขายฝากต้องแจ้งความและแจ้งผู้ซื้อฝากทันที "
        "ข้อ 6. ศาลในเขตที่ตั้งผู้ซื้อฝากมีอำนาจพิจารณาข้อพิพาท"
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <title>สัญญาขายฝาก – {esc(full_name)} – {esc(contract_number)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    /* ไม่มีขอบพิมพ์เลย */
    @page {{
      size: A4;
      margin: 0;
    }}
    html, body {{
      margin: 0;
      padding: 0;
    }}
    * {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      box-sizing: border-box;
    }}

    /* ตั้งฐาน font ใหญ่ + line-height น้อยที่สุด */
    body {{
      font-family: "TH Sarabun New", "Noto Sans Thai", system-ui, sans-serif;
      color: #000;
      background: #fff;
      font-size: 27pt;            /* ใหญ่ (ลด 1) */
      line-height: 1.15;          /* น้อยที่สุดเพื่อประหยัดพื้นที่ */
    }}

    /* ครึ่งหน้า A4 สูง 148.5mm — ไม่เว้น padding */
    .page {{
      width: 210mm;
      height: 148.5mm;
      margin: 0 auto;
      padding: 0;
      display: grid;
      grid-template-rows: auto 1fr auto auto; /* หัวเรื่อง / เนื้อหา / ลายเซ็น / ฟุตเตอร์ */
      row-gap: 2mm;   /* ระยะห่างบล็อกเล็กน้อยพอ */
    }}

    h1 {{
      text-align: center;
      font-size: 35pt;   /* ใหญ่ (ลด 1) */
      margin: 0;
      line-height: 1.1;
      padding: 1mm 2mm 0 2mm;
    }}

    .meta {{
      padding: 0 2mm;
      margin: 0;
    }}
    .meta .row {{
      display: flex;
      justify-content: space-between;
      gap: 3mm;
      margin: 0.5mm 0;
    }}

    .section-title {{
      font-weight: 700;
      margin: 1mm 0 0.5mm 0;
      padding: 0 2mm;
      line-height: 1.2;
    }}

    p {{
      margin: 0.5mm 0;
      padding: 0 2mm;
      text-align: justify;
    }}
    .indent {{ text-indent: 7mm; }}

    /* เงื่อนไขเป็นย่อหน้าเดียวและตัวใหญ่ */
    .terms {{
      font-size: 19pt;  /* (ลด 1) */
      line-height: 1.15;
      margin-top: 0.5mm;
      text-align: justify;
      padding: 0 2mm;
    }}

    .signatures {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 1.5mm;
      text-align: center;
      padding: 0 2mm;
      margin: 0;
    }}
    .sig-line {{ white-space: nowrap; }}

    .foot {{
      font-size: 15pt;  /* (ลด 1) */
      text-align: right;
      padding: 0 2mm;
      margin: 0;
      line-height: 1.1;
    }}

    @media print {{
      p {{ orphans: 2; widows: 2; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div>
      <h1>สัญญาขายฝาก (โทรศัพท์มือถือ)</h1>
      <div class="meta">
        <div class="row"><span>สัญญาเลขที่: {esc(contract_number)}</span><span>ฉบับที่: {esc(copy_number)}</span></div>
        <div class="row"><span>ทำที่: {esc(place_line)}</span><span>วันที่: {esc(start_date_th)}</span></div>
      </div>
    </div>

    <div>
      <div class="section-title">คู่สัญญา</div>
      <p class="indent">
        ระหว่าง {esc(full_name)}{f" อายุ {int(age)} ปี" if isinstance(age,(int,float)) else ""} เลขบัตรประจำตัวประชาชน {esc(id_card)}
        ที่อยู่ {esc(addr_text)} โทร {esc(phone)} ซึ่งเรียกว่า "<strong>ผู้ขายฝาก</strong>"
        กับ {esc(shop_name)} {esc(shop_branch)} เลขประจำตัวผู้เสียภาษี {esc(shop_tax_id)} ที่ตั้ง {esc(shop_address)} โทร {esc(shop_phone)}
        โดย{esc(authorized_signer)} เป็นผู้มีอำนาจลงนาม ซึ่งเรียกว่า "<strong>ผู้ซื้อฝาก</strong>"
      </p>

      <div class="section-title">รายละเอียดทรัพย์สิน</div>
      <p class="indent">
        โทรศัพท์มือถือยี่ห้อ {esc(brand or 'ไม่ระบุ')} รุ่น {esc(model or 'ไม่ระบุ')}{(" สี " + esc(color)) if color else ""}{" IMEI1: " + esc(imei1) if imei1 else ""}{" IMEI2: " + esc(imei2) if imei2 else ""}{" Serial: " + esc(serial) if serial else ""} สภาพ{esc(condition)} อุปกรณ์: {esc(accessories)}
      </p>

      <div class="section-title">ข้อตกลงและเงื่อนไข</div>
      <p class="terms">{terms_text}</p>

      <div class="section-title">การรับเงินและยืนยัน</div>
      <p class="indent">
        ผู้ขายฝากได้รับเงิน {money(pawn_amount)} บาท พร้อมส่งมอบทรัพย์สินและอุปกรณ์ครบถ้วน
        คู่สัญญาได้อ่านและเข้าใจข้อความโดยตลอดแล้ว จึงลงนามและยอมรับผูกพันตามสัญญา
        ทำ ณ {esc(place_line)} วันที่ {esc(thai_date(contract_data.get('signed_date') or start_date_raw))}
      </p>
    </div>

    <div class="signatures">
      <div>
        <div class="sig-line">ลงชื่อ ____________________</div>
        <div>( {esc(full_name)} )</div>
        <div>ผู้ขายฝาก</div>
      </div>
      <div>
        <div class="sig-line">ลงชื่อ ____________________</div>
        <div>( {esc(buyer_signer_name)} )</div>
        <div>ผู้ซื้อฝาก</div>
      </div>
      <div>
        <div class="sig-line">ลงชื่อ ____________________</div>
        <div>( {esc(witness)} )</div>
        <div>พยาน</div>
      </div>
    </div>

    <div class="foot">
      เอกสารสร้างโดยระบบ | เลขที่: {esc(contract_number)} | {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
  </div>
</body>
</html>"""

    if not output_file:
        output_file = f"pawn_contract_{contract_number or 'unknown'}.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return output_file

# ---------- Alias function for compatibility ----------
def generate_pawn_ticket_from_data(
    contract_data,
    customer_data,
    product_data,
    shop_data=None,
    show_preview=False,
    output_file=None
):
    """
    Alias function for generate_pawn_ticket_pdf_data to maintain compatibility
    with existing code that imports this function name.
    """
    return generate_pawn_ticket_pdf_data(
        contract_data=contract_data,
        customer_data=customer_data,
        product_data=product_data,
        shop_data=shop_data,
        output_file=output_file
    )

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







