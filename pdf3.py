# -*- coding: utf-8 -*-
"""
ระบบสร้างสัญญาไถ่ถอน/ใบเสร็จ PDF
กระดาษ = A4 เต็ม แต่เนื้อหาขนาดเดิมเท่าครึ่งแผ่น (วางบนครึ่งบนของหน้า)
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    KeepInFrame
)
from reportlab.lib.units import mm
from datetime import datetime, timedelta
from typing import Dict, Optional
import os


# ---------- Font & Date ----------
def ensure_fonts(font_path='THSarabun.ttf', bold_font_path='THSarabun Bold.ttf'):
    if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
        raise FileNotFoundError("กรุณาวาง THSarabun.ttf และ THSarabun Bold.ttf ไว้โฟลเดอร์เดียวกับสคริปต์")
    if 'THSarabun' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('THSarabun', font_path))
    if 'THSarabun-Bold' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))

def thai_date(date_str: Optional[str]) -> str:
    month_map = {
        'January': 'มกราคม', 'February': 'กุมภาพันธ์', 'March': 'มีนาคม',
        'April': 'เมษายน', 'May': 'พฤษภาคม', 'June': 'มิถุนายน',
        'July': 'กรกฎาคม', 'August': 'สิงหาคม', 'September': 'กันยายน',
        'October': 'ตุลาคม', 'November': 'พฤศจิกายน', 'December': 'ธันวาคม'
    }
    try:
        if not date_str or date_str == 'N/A':
            return 'N/A'
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            s = str(date_str)
            dt = datetime.strptime(s, '%Y-%m-%d') if '-' in s else datetime.strptime(s, '%d/%m/%Y')
        out = dt.strftime('%d %B %Y')
        for eng, th in month_map.items():
            out = out.replace(eng, th)
        return out
    except Exception:
        return str(date_str) if date_str else 'N/A'


# ---------- A4 (Top Half) Doc ----------
class A4TopHalfDoc(BaseDocTemplate):
    """
    กำหนดหน้า A4 เต็ม แต่สร้าง Frame เท่ากับ 'พื้นที่ครึ่งแผ่น' ที่ครึ่งบนของหน้า
    เพื่อให้เนื้อหาขนาดเท่าเดิม (แบบครึ่งแผ่น) ไม่ถูกขยาย
    """
    def __init__(self, filename, pagesize=A4, **kwargs):
        super().__init__(filename, pagesize=pagesize, **kwargs)
        width, height = pagesize
        margin_lr = 8 * mm
        margin_tb = 6 * mm
        # วางกรอบบนครึ่งบน: เริ่มที่ y = height/2 + margin_tb
        # ความสูงกรอบ = (height/2) - 2*margin_tb  (เท่ากับตอนใช้หน้า Half-A4)
        self.frame = Frame(
            margin_lr,
            (height / 2.0) + margin_tb,
            width - 2 * margin_lr,
            (height / 2.0) - 2 * margin_tb,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
            showBoundary=0
        )
        self.addPageTemplates(PageTemplate(id='A4TopHalf', frames=[self.frame]))


# ---------- Styles (compact) ----------
def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TH", fontName="THSarabun", fontSize=9.6, leading=11))
    styles.add(ParagraphStyle(name="TH-bold", fontName="THSarabun-Bold", fontSize=9.6, leading=11))
    styles.add(ParagraphStyle(name="TH-h", fontName="THSarabun-Bold", fontSize=16, leading=18, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-sub", fontName="THSarabun-Bold", fontSize=11, leading=12.5, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-right", fontName="THSarabun", fontSize=9.6, leading=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TH-mini", fontName="THSarabun", fontSize=8.6, leading=10))
    return styles


# ---------- Helpers ----------
def _shop(shop_data: Optional[Dict]):
    return (
        (shop_data or {}).get('name', 'ร้าน ไอโปรโมบายเซอร์วิส'),
        (shop_data or {}).get('branch', 'สาขาหล่มสัก'),
        (shop_data or {}).get('address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'),
    )

def _boxed(tbl, colWidths, header_rows=1, font_size=9.6):
    t = Table(tbl, colWidths=colWidths)
    t.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'THSarabun', font_size),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
        ('INNERGRID', (0,header_rows), (-1,-1), 0.25, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))
    return t


# ================= CONTRACT =================
def generate_redemption_contract_pdf(redemption_data: Dict, customer_data: Dict,
                                    product_data: Dict, original_contract_data: Dict,
                                    shop_data: Optional[Dict] = None,
                                    output_file: Optional[str] = None, output_folder: Optional[str] = None) -> str:
    try:
        ensure_fonts()
    except Exception as e:
        print(e); return ""

    if not output_file:
        contract_number = original_contract_data.get('contract_number', 'unknown')
        redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"redemption_contract_{contract_number}_{redemption_date}.pdf"

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, output_file)

    styles = make_styles()
    PAGE_W = A4[0]  # กว้างเท่าเดิมกับ Half-A4 (210mm)

    shop_name, shop_branch, shop_address = _shop(shop_data)

    # original
    original_contract_number = original_contract_data.get('contract_number', 'N/A')
    original_start_date = thai_date(original_contract_data.get('start_date', 'N/A'))
    original_end_date = thai_date(original_contract_data.get('end_date', 'N/A'))
    original_pawn_amount = float(original_contract_data.get('pawn_amount', 0) or 0)

    # redemption
    thai_redemption_date = thai_date(redemption_data.get('redemption_date', datetime.now().strftime('%Y-%m-%d')))
    deposit_date = thai_date(redemption_data.get('deposit_date', 'N/A'))
    due_date = thai_date(redemption_data.get('due_date', 'N/A'))
    total_days = int(redemption_data.get('total_days', 0) or 0)

    principal_amount = float(redemption_data.get('principal_amount', 0) or 0)
    fee_amount = float(redemption_data.get('fee_amount', 0) or 0)
    penalty_amount = float(redemption_data.get('penalty_amount', 0) or 0)
    discount_amount = float(redemption_data.get('discount_amount', 0) or 0)
    total_redemption = float(redemption_data.get('redemption_amount', 0) or 0)

    # customer
    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    customer_code = customer_data.get('customer_code', '')
    phone = customer_data.get('phone', 'N/A')
    id_card = customer_data.get('id_card', 'N/A')
    addr_parts = []
    if customer_data.get('house_number'): addr_parts.append(customer_data['house_number'])
    if customer_data.get('street'): addr_parts.append(customer_data['street'])
    if customer_data.get('subdistrict'): addr_parts.append(f"ต.{customer_data['subdistrict']}")
    if customer_data.get('district'): addr_parts.append(f"อ.{customer_data['district']}")
    if customer_data.get('province'): addr_parts.append(f"จ.{customer_data['province']}")
    address = " ".join(addr_parts) if addr_parts else "N/A"

    # product
    product_name = product_data.get('name', 'N/A')
    brand = product_data.get('brand', '')
    product_display = f"{brand} {product_name}".strip()
    details_bits = []
    if product_data.get('size'): details_bits.append(f"ขนาด {product_data.get('size')}")
    if product_data.get('weight'):
        w = str(product_data.get('weight')); wu = product_data.get('weight_unit') or ''
        details_bits.append(f"น้ำหนัก {w}{(' '+wu) if wu else ''}")
    if product_data.get('serial_number'): details_bits.append(f"S/N {product_data.get('serial_number')}")
    other_details = product_data.get('other_details', '')
    estimated_value = float(original_contract_data.get('estimated_value', 0) or 0)

    # ---------- story ----------
    story = [
        Paragraph("สัญญาไถ่ถอน", styles["TH-h"]),
        Paragraph(f"{shop_name} ({shop_branch})", styles["TH-sub"]),
        Paragraph(shop_address, styles["TH"]),
        Spacer(1, 2),
    ]

    # top two columns (ขนาดเท่าเดิม)
    col_w = (PAGE_W - 16*mm) / 2.0
    left = [
        [Paragraph("<b>สัญญาเดิม</b>", styles["TH-bold"]), ""],
        [Paragraph("เลขที่", styles["TH"]), Paragraph(original_contract_number, styles["TH-right"])],
        [Paragraph("เริ่ม", styles["TH"]), Paragraph(original_start_date, styles["TH-right"])],
        [Paragraph("ครบเดิม", styles["TH"]), Paragraph(original_end_date, styles["TH-right"])],
        [Paragraph("ยอดฝากเดิม", styles["TH"]), Paragraph(f"{original_pawn_amount:,.2f} บาท", styles["TH-right"])],
    ]
    right = [
        [Paragraph("<b>การไถ่ถอน</b>", styles["TH-bold"]), ""],
        [Paragraph("วันที่ไถ่ถอน", styles["TH"]), Paragraph(thai_redemption_date, styles["TH-right"])],
        [Paragraph("วันที่รับฝาก", styles["TH"]), Paragraph(deposit_date, styles["TH-right"])],
        [Paragraph("ครบกำหนด", styles["TH"]), Paragraph(due_date, styles["TH-right"])],
        [Paragraph("จำนวนวันที่ฝาก", styles["TH"]), Paragraph(f"{total_days} วัน", styles["TH-right"])],
    ]
    left_t  = _boxed(left,  [30*mm, col_w-30*mm])
    right_t = _boxed(right, [30*mm, col_w-30*mm])
    two_col = Table([[left_t, right_t]], colWidths=[col_w, col_w])
    two_col.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),1),
        ('RIGHTPADDING',(0,0),(-1,-1),1),
        ('TOPPADDING',(0,0),(-1,-1),0),
        ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ]))
    story += [two_col, Spacer(1,2)]

    # customer + product
    cust_prod = [
        [Paragraph("<b>ผู้ไถ่ถอน</b>", styles["TH-bold"]), Paragraph("<b>ทรัพย์สิน</b>", styles["TH-bold"])],
        [Paragraph(f"รหัส: {customer_code} | โทร: {phone}<br/>ชื่อ: {customer_name}<br/>บัตร: {id_card}<br/>ที่อยู่: {address}", styles["TH"]),
         Paragraph(f"{product_display}"
                   + (f"<br/>{' | '.join(details_bits)}" if details_bits else "")
                   + (f"<br/>รายละเอียด: {other_details}" if other_details else "")
                   + (f"<br/>ประเมิน: {estimated_value:,.2f} บาท" if estimated_value>0 else ""), styles["TH"])],
    ]
    cust_prod_t = _boxed(cust_prod, [col_w, col_w], header_rows=1)
    story += [cust_prod_t, Spacer(1,2)]

    # money summary
    money = [
        [Paragraph("เงินต้น", styles["TH"]), Paragraph(f"{principal_amount:,.2f}", styles["TH-right"]),
         Paragraph("ค่าธรรมเนียม", styles["TH"]), Paragraph(f"{fee_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ค่าปรับ", styles["TH"]), Paragraph(f"{penalty_amount:,.2f}", styles["TH-right"]),
         Paragraph("ส่วนลด", styles["TH"]), Paragraph(f"{discount_amount:,.2f}", styles["TH-right"])],
        [Paragraph("<b>ยอดไถ่ถอนรวม</b>", styles["TH-bold"]), Paragraph(f"<b>{total_redemption:,.2f}</b>", styles["TH-right"]),
         Paragraph("", styles["TH"]), Paragraph("", styles["TH"])],
    ]
    money_t = _boxed(money, [28*mm, 28*mm, 28*mm, (PAGE_W-16*mm)-84*mm], header_rows=0)
    story += [money_t, Spacer(1,2)]

    # terms
    terms_text = (
        f"• ไถ่ถอนวันที่ {thai_redemption_date} • ฝาก {total_days} วัน • ยอดไถ่ถอน {total_redemption:,.2f} บาท "
        "• หลังไถ่ถอนถือว่าสัญญาขายฝากสิ้นสุด • ตรวจสอบสินค้าให้เรียบร้อยก่อนรับมอบ"
    )
    terms_t = _boxed([[Paragraph(terms_text, styles["TH-mini"])]], [PAGE_W-16*mm], header_rows=0)
    story += [terms_t, Spacer(1,2)]

    # signatures
    sig = Table([
        [Paragraph("ลงชื่อ ____________________ ผู้รับฝาก", styles["TH"]),
         Paragraph("ลงชื่อ ____________________ ผู้ไถ่ถอน", styles["TH"])],
        [Paragraph("( นาย/นาง/นางสาว _________________ )", styles["TH"]),
         Paragraph(f"( {customer_name} )", styles["TH"])],
        [Paragraph("วันที่: _________________", styles["TH"]),
         Paragraph(f"วันที่: {thai_redemption_date}", styles["TH"])],
    ], colWidths=[col_w, col_w])
    sig.setStyle(TableStyle([
        ('FONT',(0,0),(-1,-1),'THSarabun',9.6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))
    story += [sig, Spacer(1,1)]
    story += [Paragraph(
        f"เอกสารไถ่ถอนสร้างโดยระบบ | เลขที่สัญญา: {original_contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles["TH-mini"]
    )]

    # build (A4 เต็ม / ใช้เฉพาะกรอบครึ่งบน)
    doc = A4TopHalfDoc(output_file, pagesize=A4)
    _frame = getattr(doc, "frame", doc.pageTemplates[0].frames[0])
    story = [KeepInFrame(_frame._width, _frame._height, story, mode='shrink')]
    doc.build(story)
    print(f"Successfully created redemption contract '{output_file}'")
    return output_file


# ================= RECEIPT =================
def generate_redemption_receipt_pdf(redemption_data: Dict, customer_data: Dict,
                                    product_data: Dict, original_contract_data: Dict,
                                    shop_data: Optional[Dict] = None,
                                    output_file: Optional[str] = None) -> str:
    try:
        ensure_fonts()
    except Exception as e:
        print(e); return ""

    if not output_file:
        contract_number = original_contract_data.get('contract_number', 'unknown')
        redemption_date = redemption_data.get('redemption_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"redemption_receipt_{contract_number}_{redemption_date}.pdf"

    styles = make_styles()
    PAGE_W = A4[0]
    shop_name, shop_branch, shop_address = _shop(shop_data)

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

    story = [
        Paragraph("ใบเสร็จการไถ่ถอน", styles["TH-h"]),
        Paragraph(f"{shop_name} ({shop_branch})", styles["TH-sub"]),
        Paragraph(shop_address, styles["TH"]),
        Spacer(1, 2),
    ]

    info = _boxed([
        [Paragraph("<b>รายละเอียดการไถ่ถอน</b>", styles["TH-bold"]), ""],
        [Paragraph("เลขที่สัญญา", styles["TH"]), Paragraph(contract_number, styles["TH-right"])],
        [Paragraph("วันที่ไถ่ถอน", styles["TH"]), Paragraph(thai_redemption_date, styles["TH-right"])],
        [Paragraph("จำนวนวันที่ฝาก", styles["TH"]), Paragraph(f"{total_days} วัน", styles["TH-right"])],
    ], [60*mm, (PAGE_W-16*mm)-60*mm], header_rows=1)
    story += [info, Spacer(1,2)]

    pay = _boxed([
        [Paragraph("<b>รายละเอียดการชำระ</b>", styles["TH-bold"]), ""],
        [Paragraph("เงินต้น", styles["TH"]), Paragraph(f"{principal_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ค่าธรรมเนียม", styles["TH"]), Paragraph(f"{fee_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ค่าปรับ", styles["TH"]), Paragraph(f"{penalty_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ส่วนลด", styles["TH"]), Paragraph(f"{discount_amount:,.2f}", styles["TH-right"])],
        [Paragraph("<b>ยอดรวม</b>", styles["TH-bold"]), Paragraph(f"<b>{total_redemption:,.2f}</b>", styles["TH-right"])],
    ], [60*mm, (PAGE_W-16*mm)-60*mm], header_rows=1)
    story += [pay, Spacer(1,2)]

    col_w = (PAGE_W - 16*mm)/2
    cp = _boxed([
        [Paragraph("<b>ลูกค้า</b>", styles["TH-bold"]), Paragraph("<b>สินค้า</b>", styles["TH-bold"])],
        [Paragraph(f"ชื่อ: {customer_name}<br/>โทร: {phone}", styles["TH"]),
         Paragraph((product_data.get('brand','') + ' ' if product_data.get('brand') else '') + product_data.get('name','N/A'), styles["TH"])],
    ], [col_w, col_w], header_rows=1)
    story += [cp, Spacer(1,1)]

    story += [Paragraph(
        f"เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles["TH-mini"]
    )]

    doc = A4TopHalfDoc(output_file, pagesize=A4)
    _frame = getattr(doc, "frame", doc.pageTemplates[0].frames[0])
    story = [KeepInFrame(_frame._width, _frame._height, story, mode='shrink')]
    doc.build(story)
    print(f"Successfully created redemption receipt '{output_file}'")
    return output_file


# --- Main ---
if __name__ == "__main__":
    print("A4 full page; content sized like half-page (top half).")
