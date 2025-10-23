# -*- coding: utf-8 -*-
"""
สัญญาไถ่คืน/ใบเสร็จ PDF
- หน้า A4 เต็ม ระยะขอบ 16mm
- สัญญาไถ่คืน ใช้เลย์เอาต์ตาม HTML ตัวอย่าง (หัวเรื่อง, meta 2 คอลัมน์, ย่อหน้า, ลายเซ็น 3 ช่อง)
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.units import mm
from datetime import datetime
from typing import Dict, Optional
import os
from shop_config_loader import load_shop_config


# ---------- Font & Date ----------
def ensure_fonts(font_path='NotoSansThai-Regular.ttf', bold_font_path='NotoSansThai-Bold.ttf'):
    """Setup Thai fonts for PDF generation with improved rendering"""
    from resource_path import get_font_path
    font_path = get_font_path(font_path)
    bold_font_path = get_font_path(bold_font_path)
    if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
        raise FileNotFoundError(f"ไม่พบไฟล์ฟอนต์: {font_path} หรือ {bold_font_path}")
    if 'NotoSansThai' not in pdfmetrics.getRegisteredFontNames():
        # ใช้ subfontIndex=0 เพื่อให้รองรับตัวอักษรไทยได้ดีขึ้น
        pdfmetrics.registerFont(TTFont('NotoSansThai', font_path, subfontIndex=0))
    if 'NotoSansThai-Bold' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('NotoSansThai-Bold', bold_font_path, subfontIndex=0))

def thai_date(date_val: Optional[str]) -> str:
    month_map = {
        'January': 'มกราคม', 'February': 'กุมภาพันธ์', 'March': 'มีนาคม',
        'April': 'เมษายน', 'May': 'พฤษภาคม', 'June': 'มิถุนายน',
        'July': 'กรกฎาคม', 'August': 'สิงหาคม', 'September': 'กันยายน',
        'October': 'ตุลาคม', 'November': 'พฤศจิกายน', 'December': 'ธันวาคม'
    }
    try:
        if not date_val or date_val == 'N/A':
            return 'N/A'
        if isinstance(date_val, datetime):
            dt = date_val
        else:
            s = str(date_val)
            dt = datetime.strptime(s, '%Y-%m-%d') if '-' in s else datetime.strptime(s, '%d/%m/%Y')
        out = dt.strftime('%d %B %Y')
        for e, t in month_map.items():
            out = out.replace(e, t)
        return out
    except Exception:
        return str(date_val) if date_val else 'N/A'


# ---------- A4 Doc (margin 16mm) ----------
class A4Doc(BaseDocTemplate):
    """
    หน้า A4 เต็ม ระยะขอบ 16mm ตาม @page { margin: 16mm }
    """
    def __init__(self, filename, pagesize=A4, **kwargs):
        super().__init__(filename, pagesize=pagesize, **kwargs)
        width, height = pagesize
        margin = 16 * mm
        frame = Frame(
            margin, margin,
            width - 2 * margin,
            height - 2 * margin,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
            showBoundary=0
        )
        self.addPageTemplates(PageTemplate(id='A4Full', frames=[frame]))


# ---------- Styles (ชิดซ้าย + CJK wrap เพื่อตัดปัญหาช่องไฟ + ปรับปรุงการแสดงผลภาษาไทย) ----------
def make_styles():
    styles = getSampleStyleSheet()

    # เพิ่ม leading และขนาดตัวอักษรเพื่อแก้ปัญหาวรรณยุกต์ซ้อนกับสระ
    common = dict(leading=18, alignment=TA_LEFT, wordWrap='CJK', spaceBefore=0, spaceAfter=2)

    styles.add(ParagraphStyle(name="TH", fontName="NotoSansThai", fontSize=15, **common))  # เพิ่มจาก 13.5 เป็น 15
    styles.add(ParagraphStyle(name="TH-bold", fontName="NotoSansThai-Bold", fontSize=15, **common))  # เพิ่มจาก 13.5 เป็น 15

    styles.add(ParagraphStyle(
        name="TH-h1", fontName="NotoSansThai-Bold", fontSize=22, leading=26,  # เพิ่มจาก 20 เป็น 22, leading จาก 22.5 เป็น 26
        alignment=TA_CENTER, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="TH-meta", fontName="NotoSansThai", fontSize=13, leading=16,  # เพิ่มจาก 12 เป็น 13, leading จาก 13.4 เป็น 16
        alignment=TA_LEFT, wordWrap='CJK', spaceBefore=0, spaceAfter=1
    ))
    styles.add(ParagraphStyle(
        name="TH-section", fontName="NotoSansThai-Bold", fontSize=15, leading=18,  # เพิ่มจาก 13.5 เป็น 15, leading จาก 15.2 เป็น 18
        alignment=TA_LEFT, wordWrap='CJK', spaceBefore=4, spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name="TH-indent", fontName="NotoSansThai", fontSize=15,  # เพิ่มจาก 13.5 เป็น 15
        leftIndent=12*mm, **common
    ))
    styles.add(ParagraphStyle(
        name="TH-mini", fontName="NotoSansThai", fontSize=12, leading=15, textColor=colors.black  # เพิ่มจาก 10.5 เป็น 12, leading จาก 11.6 เป็น 15
    ))
    styles.add(ParagraphStyle(
        name="TH-right", fontName="NotoSansThai", fontSize=15, leading=18, alignment=TA_RIGHT  # เพิ่มจาก 13.5 เป็น 15, leading จาก 15.2 เป็น 18
    ))
    return styles


# ---------- Helpers ----------
def _shop(shop_data: Optional[Dict]):
    cfg = load_shop_config()
    return (
        (shop_data or {}).get('name', cfg['name']),
        (shop_data or {}).get('branch', cfg['branch']),
        (shop_data or {}).get('address', cfg['address']),
        (shop_data or {}).get('tax_id', cfg.get('tax_id', '')),
        (shop_data or {}).get('phone', cfg.get('phone', '')),
        (shop_data or {}).get('authorized_signer', cfg.get('authorized_signer', '')),
        (shop_data or {}).get('buyer_signer_name', cfg.get('buyer_signer_name', '')),
        (shop_data or {}).get('witness_name', cfg.get('witness_name', ''))
    )

def _meta_row(left_text: str, right_text: str, styles, col_gap_mm=10):
    """
    แถว meta: 2 คอลัมน์ ชิดซ้าย-ขวา
    """
    page_w = A4[0]
    margin = 16*mm
    usable = page_w - 2*margin
    gap = col_gap_mm * mm
    col_w = (usable - gap) / 2.0
    t = Table(
        [[Paragraph(left_text, styles["TH-meta"]), Paragraph(right_text, styles["TH-meta"])]],
        colWidths=[col_w, col_w]
    )
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    return t

def _signatures_block(names: Dict[str, str], styles):
    """
    บล็อกลายเซ็น 3 ช่อง: ผู้ไถ่คืน / ผู้รับไถ่คืน / พยาน
    """
    labels = [("ผู้ไถ่คืน", names.get("redeemer", "")),
              ("ผู้รับไถ่คืน", names.get("receiver", "")),
              ("พยาน", names.get("witness", ""))]
    cells = []
    for label, name in labels:
        cell = [
            Paragraph("ลงชื่อ ______________________________", styles["TH"]),
            Paragraph(f"( {name or '_________________'} )", styles["TH"]),
            Paragraph(label, styles["TH"])
        ]
        cells.append(cell)

    page_w = A4[0]
    margin = 16*mm
    usable = page_w - 2*margin
    col_w = usable / 3.0
    t = Table([cells], colWidths=[col_w, col_w, col_w])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t


# ================= CONTRACT (HTML layout) =================
def generate_redemption_contract_pdf(redemption_data: Dict, customer_data: Dict,
                                    product_data: Dict, original_contract_data: Dict,
                                    shop_data: Optional[Dict] = None,
                                    output_file: Optional[str] = None, output_folder: Optional[str] = None) -> str:
    """
    เรนเดอร์สัญญาไถ่คืน ด้วยรูปแบบเอกสารตาม HTML ตัวอย่าง
    """
    try:
        ensure_fonts()
    except Exception as e:
        error_msg = f"Font loading error: {str(e)}"
        print(error_msg)
        return ""

    if not output_file:
        contract_number = original_contract_data.get('contract_number', 'unknown')
        redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"redemption_contract_{contract_number}_{redemption_date}.pdf"

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, output_file)

    styles = make_styles()
    doc = A4Doc(output_file, pagesize=A4)

    # ---------- Extract & normalize data ----------
    shop_name, shop_branch, shop_address, shop_tax_id, shop_phone, authorized_signer, buyer_signer_name, witness_name = _shop(shop_data)

    original_contract_number = original_contract_data.get('contract_number', 'N/A')
    original_contract_date = thai_date(original_contract_data.get('start_date', 'N/A'))

    redemption_count = redemption_data.get('redemption_count', 1)
    thai_redemption_date_full = thai_date(redemption_data.get('redemption_date', datetime.now().strftime('%Y-%m-%d')))
    redemption_time = redemption_data.get('redemption_time', '15:00 น.')
    total_days = int(redemption_data.get('total_days', 0) or 0)

    principal_amount = float(redemption_data.get('principal_amount', 0) or 0)
    fee_amount = float(redemption_data.get('fee_amount', 0) or 0)
    penalty_amount = float(redemption_data.get('penalty_amount', 0) or 0)
    discount_amount = float(redemption_data.get('discount_amount', 0) or 0)
    total_redemption = float(redemption_data.get('redemption_amount', 0) or 0)

    first_name = customer_data.get('first_name', '') or ''
    last_name = customer_data.get('last_name', '') or ''
    customer_name = f"{first_name} {last_name}".strip() or "_________________"
    id_card = customer_data.get('id_card', '_________________') or '_________________'
    age = customer_data.get('age', '') or ''
    age_str = f"อายุ {age} ปี " if age else ""
    phone = customer_data.get('phone', '_________________') or '_________________'

    addr_parts = []
    if customer_data.get('house_number'): addr_parts.append(str(customer_data['house_number'] or ''))
    if customer_data.get('street'): addr_parts.append(str(customer_data['street'] or ''))
    if customer_data.get('subdistrict'): addr_parts.append(f"แขวง/ตำบล{customer_data['subdistrict'] or ''}")
    if customer_data.get('district'): addr_parts.append(f"เขต/อำเภอ{customer_data['district'] or ''}")
    if customer_data.get('province'): addr_parts.append(f"จ.{customer_data['province'] or ''}")
    if customer_data.get('zipcode'): addr_parts.append(str(customer_data['zipcode'] or ''))
    address = " ".join(addr_parts) if addr_parts else "_________________"

    authorized_person = authorized_signer

    brand = product_data.get('brand', '') or ''
    name = product_data.get('model', '') or product_data.get('name', 'ทรัพย์สิน') or 'ทรัพย์สิน'
    color = product_data.get('color', '') or ''
    imei1 = product_data.get('imei1', '') or ''
    imei2 = product_data.get('imei2', '') or ''
    serial = product_data.get('serial_number', '') or ''
    accessories = product_data.get('accessories', '') or ''
    orig_ref_date = thai_date(original_contract_data.get('start_date', 'N/A'))

    # ---------- Build story ----------
    story = []

    # Title
    story.append(Paragraph("สัญญาไถ่คืนทรัพย์สิน (โทรศัพท์มือถือ)", styles["TH-h1"]))
    story.append(Spacer(1, 4))

    # Meta rows (2 แถว)
    story.append(_meta_row(
        f"อ้างอิงสัญญาขายฝากเดิม: {original_contract_number}",
        f"ฉบับไถ่คืน: {redemption_count}", styles
    ))
    story.append(_meta_row(
        f"ทำที่: {shop_name} สาขา{shop_branch}",
        f"วันที่ไถ่คืน: {thai_redemption_date_full} เวลา {redemption_time}", styles
    ))
    story.append(Spacer(1, 4))

    # Section: คู่สัญญา
    story.append(Paragraph("คู่สัญญา", styles["TH-section"]))
    p1 = (
        f"ระหว่าง {customer_name} {age_str}เลขบัตรประจำตัวประชาชน {id_card} "
        f"ที่อยู่ {address} โทร {phone} ซึ่งต่อไปนี้เรียกว่า "
        f"“<b>ผู้ไถ่คืน</b>” ฝ่ายหนึ่ง กับ {shop_name} สาขา{shop_branch} "
        f"เลขประจำตัวผู้เสียภาษี {shop_tax_id} ที่ตั้ง {shop_address} โทร {shop_phone} "
        f"โดย{authorized_person} เป็นผู้มีอำนาจลงนาม ซึ่งต่อไปนี้เรียกว่า "
        f"“<b>ผู้รับไถ่คืน</b>” อีกฝ่ายหนึ่ง"
    )
    story.append(Paragraph(p1, styles["TH-indent"]))

    # Section: รายการทรัพย์สินที่ไถ่คืน
    story.append(Paragraph("รายการทรัพย์สินที่ไถ่คืน", styles["TH-section"]))
    prod_line = f"โทรศัพท์มือถือยี่ห้อ {brand} รุ่น {name}"
    if color: prod_line += f" สี{color}"
    detail_line = []
    if imei1: detail_line.append(f"หมายเลข IMEI 1: {imei1}")
    if imei2: detail_line.append(f"IMEI 2: {imei2}")
    if serial: detail_line.append(f"Serial Number: {serial}")
    detail_join = ", ".join(detail_line) if detail_line else ""
    acc_line = f"อุปกรณ์ที่รับคืนพร้อมกัน: {accessories}" if accessories else ""
    ref_line = f"ตามที่เคยระบุไว้ในสัญญาขายฝากเดิมเลขที่ {original_contract_number} ลงวันที่ {orig_ref_date}"
    p2 = f"{prod_line} {detail_join} {acc_line} {ref_line}".strip()
    story.append(Paragraph(p2, styles["TH-indent"]))

    # Section: ข้อความไถ่คืน
    story.append(Paragraph("ข้อความไถ่คืน", styles["TH-section"]))
    p3 = (
        f"ผู้ไถ่คืนได้ชำระเงินจำนวน <b>{total_redemption:,.0f} บาทถ้วน</b> ให้แก่ผู้รับไถ่คืน "
        f"ครบถ้วนถูกต้องตามที่กำหนด ภายในกำหนดไถ่ถอน {total_days} วันนับแต่วันที่ทำสัญญาขายฝากเดิม "
        f"ทั้งนี้ ผู้รับไถ่คืนได้รับเงินไว้แล้วและยินยอมคืนทรัพย์สินพร้อมอุปกรณ์ตามรายการข้างต้น "
        f"ให้แก่ผู้ไถ่คืนโดยเรียบร้อย"
    )
    p4 = (
        "นับแต่เวลาที่ระบุในสัญญานี้ กรรมสิทธิ์ในทรัพย์สินดังกล่าวกลับเป็นของผู้ไถ่คืนโดยสมบูรณ์ "
        "ผู้รับไถ่คืนไม่มีสิทธิครอบครองหรือเรียกร้องสิทธิใด ๆ อันเกี่ยวกับทรัพย์สินดังกล่าวอีกต่อไป "
        "และตกลงว่าการขายฝากตามสัญญาเดิมเป็นอันสิ้นผลโดยสมบูรณ์"
    )
    story.append(Paragraph(p3, styles["TH-indent"]))
    story.append(Paragraph(p4, styles["TH-indent"]))

    # Section: การตรวจสอบและรับคืน
    story.append(Paragraph("การตรวจสอบและรับคืน", styles["TH-section"]))
    p5 = (
        "คู่สัญญาได้ทำการตรวจรับทรัพย์สินร่วมกันแล้ว พบว่าสภาพทรัพย์สินเป็นไปตามที่ระบุในสัญญาขายฝากเดิม "
        "ผู้ไถ่คืนยืนยันว่ารับทรัพย์สินและอุปกรณ์ครบถ้วนถูกต้อง และผู้รับไถ่คืนยืนยันการส่งมอบเรียบร้อย"
    )
    story.append(Paragraph(p5, styles["TH-indent"]))

    # Section: การยืนยันคู่สัญญา
    story.append(Paragraph("การยืนยันคู่สัญญา", styles["TH-section"]))
    p6 = (
        f"คู่สัญญาได้อ่านและเข้าใจข้อความในสัญญาฉบับนี้โดยตลอดดีแล้ว จึงได้ตกลงลงนามและยอมรับผูกพันตามสัญญานี้ทุกประการ "
        f"ทำขึ้น ณ {shop_name} สาขา{shop_branch} เมื่อวันที่ {thai_redemption_date_full}"
    )
    story.append(Paragraph(p6, styles["TH-indent"]))
    story.append(Spacer(1, 6))

    # Signatures (3 columns)
    sig_names = {
        "redeemer": customer_name,
        "receiver": authorized_person,
        "witness": (redemption_data.get('witness_name') or witness_name or "_________________")
    }
    story.append(_signatures_block(sig_names, styles))
    story.append(Spacer(1, 6))

    # Footer mini
    footer = Paragraph(
        f"เอกสารสร้างโดยระบบ | อ้างอิงสัญญาเดิม: {original_contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles["TH-mini"]
    )
    story.append(footer)

    # Build
    try:
        doc.build(story)
        print(f"Successfully created redemption contract '{output_file}'")
        return output_file
    except Exception as e:
        error_msg = f"PDF building error: {str(e)}"
        print(error_msg)
        return ""


# ================= RECEIPT (กระชับ) =================
def generate_redemption_receipt_pdf(redemption_data: Dict, customer_data: Dict,
                                    product_data: Dict, original_contract_data: Dict,
                                    shop_data: Optional[Dict] = None,
                                    output_file: Optional[str] = None) -> str:
    try:
        ensure_fonts()
    except Exception as e:
        error_msg = f"Font loading error: {str(e)}"
        print(error_msg)
        return ""

    if not output_file:
        contract_number = original_contract_data.get('contract_number', 'unknown')
        redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"redemption_receipt_{contract_number}_{redemption_date}.pdf"

    styles = make_styles()
    PAGE_W = A4[0]
    shop_name, shop_branch, shop_address, shop_tax_id, shop_phone, authorized_signer, buyer_signer_name, witness_name = _shop(shop_data)

    contract_number = original_contract_data.get('contract_number', 'N/A')
    total_days = int(redemption_data.get('total_days', 0) or 0)
    thai_redemption_date = thai_date(redemption_data.get('redemption_date', datetime.now().strftime('%Y-%m-%d')))

    principal_amount = float(redemption_data.get('principal_amount', 0) or 0)
    fee_amount = float(redemption_data.get('fee_amount', 0) or 0)
    penalty_amount = float(redemption_data.get('penalty_amount', 0) or 0)
    discount_amount = float(redemption_data.get('discount_amount', 0) or 0)
    total_redemption = float(redemption_data.get('redemption_amount', 0) or 0)

    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    phone = customer_data.get('phone', 'N/A')

    # ใช้หน้า A4 เต็ม (margin 16mm)
    doc = A4Doc(output_file, pagesize=A4)
    story = [
        Paragraph("ใบเสร็จการไถ่คืน", styles["TH-h1"]),
        Paragraph(f"{shop_name} ({shop_branch})", styles["TH"]),
        Paragraph(shop_address, styles["TH"]),
        Spacer(1, 6),
    ]

    # กล่องข้อมูล & ชำระ
    def _boxed(tbl, colWidths, header_rows=1, font_size=13.5):
        t = Table(tbl, colWidths=colWidths)
        t.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'NotoSansThai', font_size),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
            ('INNERGRID', (0,header_rows), (-1,-1), 0.25, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('LEFTPADDING',(0,0),(-1,-1),3),
            ('RIGHTPADDING',(0,0),(-1,-1),3),
            ('TOPPADDING',(0,0),(-1,-1),2),
            ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ]))
        return t

    info = _boxed([
        [Paragraph("<b>รายละเอียดการไถ่คืน</b>", styles["TH-bold"]), ""],
        [Paragraph("เลขที่สัญญา", styles["TH"]), Paragraph(contract_number, styles["TH-right"])],
        [Paragraph("วันที่ไถ่คืน", styles["TH"]), Paragraph(thai_redemption_date, styles["TH-right"])],
        [Paragraph("จำนวนวันที่ฝาก", styles["TH"]), Paragraph(f"{total_days} วัน", styles["TH-right"])],
    ], [60*mm, (PAGE_W-32*mm)-60*mm], header_rows=1)
    story += [info, Spacer(1,6)]

    pay = _boxed([
        [Paragraph("<b>รายละเอียดการชำระ</b>", styles["TH-bold"]), ""],
        [Paragraph("เงินต้น", styles["TH"]), Paragraph(f"{principal_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ค่าธรรมเนียม", styles["TH"]), Paragraph(f"{fee_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ค่าปรับ", styles["TH"]), Paragraph(f"{penalty_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ส่วนลด", styles["TH"]), Paragraph(f"{discount_amount:,.2f}", styles["TH-right"])],
        [Paragraph("<b>ยอดรวม</b>", styles["TH-bold"]), Paragraph(f"<b>{total_redemption:,.2f}</b>", styles["TH-right"])],
    ], [60*mm, (PAGE_W-32*mm)-60*mm], header_rows=1)
    story += [pay, Spacer(1,6)]

    col_w = (PAGE_W - 32*mm)/2
    cp = _boxed([
        [Paragraph("<b>ลูกค้า</b>", styles["TH-bold"]), Paragraph("<b>สินค้า</b>", styles["TH-bold"])],
        [Paragraph(f"ชื่อ: {customer_name}<br/>โทร: {phone}", styles["TH"]),
         Paragraph(f"{product_data.get('brand', '') or ''} {product_data.get('model', '') or product_data.get('name', 'N/A') or 'N/A'}".strip(), styles["TH"])],
    ], [col_w, col_w], header_rows=1)
    story += [cp, Spacer(1,6)]

    story += [Paragraph(
        f"เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles["TH-mini"]
    )]

    try:
        doc.build(story)
        print(f"Successfully created redemption receipt '{output_file}'")
        return output_file
    except Exception as e:
        error_msg = f"PDF building error: {str(e)}"
        print(error_msg)
        return ""


# --- Main ---
if __name__ == "__main__":
    print("Ready: A4 full-page layouts (contract = HTML style, receipt = compact).")