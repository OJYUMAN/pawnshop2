# generate_renewal_contract_pdf.py  (fit one half A4 page; auto-shrink)
# -*- coding: utf-8 -*-
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
from PySide6.QtWidgets import QFileDialog, QApplication
import sys, os
from shop_config_loader import load_shop_config


# ----------------- UI helper -----------------
def select_output_folder(title="เลือกโฟลเดอร์สำหรับจัดเก็บไฟล์ PDF") -> Optional[str]:
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        folder = QFileDialog.getExistingDirectory(None, title, "", QFileDialog.Option.ShowDirsOnly)
        return folder or None
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเลือกโฟลเดอร์: {e}")
        return None


# ----------------- Fonts & Date -----------------
def ensure_fonts(font_path='THSarabun.ttf', bold_font_path='THSarabun Bold.ttf'):
    from resource_path import get_font_path
    font_path = get_font_path(font_path)
    bold_font_path = get_font_path(bold_font_path)
    if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
        raise FileNotFoundError(f"ไม่พบไฟล์ฟอนต์: {font_path} หรือ {bold_font_path}")
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
            if '-' in s:
                dt = datetime.strptime(s, '%Y-%m-%d')
            else:
                dt = datetime.strptime(s, '%d/%m/%Y')
        out = dt.strftime('%d %B %Y')
        for eng, th in month_map.items():
            out = out.replace(eng, th)
        return out
    except Exception:
        return str(date_str) if date_str else 'N/A'


# ----------------- Half-page Doc -----------------
class TopHalfDoc(BaseDocTemplate):
    def __init__(self, filename, pagesize=A4, **kwargs):
        super().__init__(filename, pagesize=pagesize, **kwargs)
        width, height = pagesize
        margin_lr = 8 * mm
        margin_top = 6 * mm
        frame_h = height / 2 - margin_top  # ครึ่งแผ่น
        frame_y = height / 2
        self.frame = Frame(
            margin_lr, frame_y, width - 2 * margin_lr, frame_h,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0
        )
        self.addPageTemplates(PageTemplate(id='TopHalf', frames=[self.frame]))


# ----------------- Styles (compact) -----------------
def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TH", fontName="THSarabun", fontSize=9.6, leading=11))
    styles.add(ParagraphStyle(name="TH-bold", fontName="THSarabun-Bold", fontSize=9.6, leading=11))
    styles.add(ParagraphStyle(name="TH-h", fontName="THSarabun-Bold", fontSize=16, leading=18, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-sub", fontName="THSarabun-Bold", fontSize=11, leading=12.5, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-right", fontName="THSarabun", fontSize=9.6, leading=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TH-mini", fontName="THSarabun", fontSize=8.6, leading=10))
    return styles


# ----------------- CONTRACT -----------------
def generate_renewal_contract_pdf(original_contract_data: Dict, customer_data: Dict, product_data: Dict,
                                  renewal_data: Dict, shop_data: Optional[Dict] = None,
                                  output_file: Optional[str] = None, output_folder: Optional[str] = None,
                                  ask_folder: bool = False) -> str:

    try:
        ensure_fonts()
    except Exception as e:
        print(e); return ""

    if not output_file:
        contract_number = original_contract_data.get('contract_number', 'unknown')
        renewal_date = renewal_data.get('renewal_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"renewal_contract_{contract_number}_{renewal_date}.pdf"

    if ask_folder and not output_folder:
        output_folder = select_output_folder()
        if not output_folder:
            print("ยกเลิกการสร้าง PDF"); return ""
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, output_file)

    styles = make_styles()
    width, height = A4

    # --- shop ---
    # Load shop configuration from JSON file
    default_shop_config = load_shop_config()
    shop_name = (shop_data or {}).get('name', default_shop_config['name'])
    shop_branch = (shop_data or {}).get('branch', default_shop_config['branch'])
    shop_address = (shop_data or {}).get('address', default_shop_config['address'])

    # --- original ---
    original_contract_number = original_contract_data.get('contract_number', 'N/A')
    original_start_date = thai_date(original_contract_data.get('start_date', 'N/A'))
    original_end_date = thai_date(original_contract_data.get('end_date', 'N/A'))
    original_days_count = original_contract_data.get('days_count', 0)

    # --- renewal ---
    extension_days = int(renewal_data.get('extension_days', 0) or 0)
    total_amount = float(renewal_data.get('total_amount', 0) or 0)
    renewal_date_disp = thai_date(renewal_data.get('renewal_date', datetime.now().strftime('%Y-%m-%d')))

    # new end date
    thai_new_end_date = 'N/A'
    try:
        end_src = original_contract_data.get('end_date')
        if end_src and end_src != 'N/A':
            if '-' in str(end_src):
                end_date_obj = datetime.strptime(str(end_src), '%Y-%m-%d')
            else:
                end_date_obj = datetime.strptime(str(end_src), '%d/%m/%Y')
            new_end_date = end_date_obj + timedelta(days=extension_days)
            thai_new_end_date = thai_date(new_end_date.strftime('%Y-%m-%d'))
    except Exception:
        pass

    original_pawn_amount = float(original_contract_data.get('pawn_amount', 0) or 0)
    total_redemption = original_pawn_amount + total_amount

    # --- product & customer ---
    product_name = product_data.get('model', '') or product_data.get('name', 'N/A')
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

    # -------- story (compact) --------
    def cell_para(text, style="TH"):
        return Paragraph(text, styles[style])

    # Header (กระชับ)
    header = [
        cell_para("ใบฝากต่อ", "TH-h"),
        cell_para(f"{shop_name} ({shop_branch})", "TH-sub"),
        cell_para(shop_address, "TH")
    ]

    # 2 คอลัมน์หลัก
    left = [
        [cell_para("<b>สัญญาเดิม</b>", "TH-bold"), ""],
        [cell_para("เลขที่", "TH"), cell_para(original_contract_number, "TH-right")],
        [cell_para("เริ่ม", "TH"), cell_para(original_start_date, "TH-right")],
        [cell_para("ระยะเวลา", "TH"), cell_para(f"{original_days_count} วัน", "TH-right")],
        [cell_para("ครบเดิม", "TH"), cell_para(original_end_date, "TH-right")],
    ]
    right = [
        [cell_para("<b>ต่อดอก</b>", "TH-bold"), ""],
        [cell_para("วันที่", "TH"), cell_para(renewal_date_disp, "TH-right")],
        [cell_para("ต่อเพิ่ม", "TH"), cell_para(f"{extension_days} วัน", "TH-right")],
        [cell_para("<b>รวมต่อดอก</b>", "TH-bold"), cell_para(f"<b>{total_amount:,.2f}</b>", "TH-right")],
        [cell_para("ครบใหม่", "TH"), cell_para(thai_new_end_date, "TH-right")],
    ]

    def boxed(tbl, col1=28*mm, col2=54*mm):
        t = Table(tbl, colWidths=[col1, col2])
        t.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'THSarabun', 9.6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('INNERGRID', (0,1), (-1,-1), 0.25, colors.grey),
            ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (1,0), colors.whitesmoke),
            ('LEFTPADDING',(0,0),(-1,-1),2),
            ('RIGHTPADDING',(0,0),(-1,-1),2),
            ('TOPPADDING',(0,0),(-1,-1),1),
            ('BOTTOMPADDING',(0,0),(-1,-1),1),
        ]))
        return t

    left_t = boxed(left)
    right_t = boxed(right)
    two_col = Table([[left_t, right_t]], colWidths=[(width-16*mm)/2, (width-16*mm)/2])
    two_col.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),1),
        ('RIGHTPADDING',(0,0),(-1,-1),1),
        ('TOPPADDING',(0,0),(-1,-1),0),
        ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ]))

    # Customer + Product (รวมกระชับ)
    cust_prod = [
        [cell_para("<b>ผู้ขายฝาก</b>", "TH-bold"), cell_para("<b>ทรัพย์สิน</b>", "TH-bold")],
        [cell_para(f"รหัส: {customer_code} | โทร: {phone}<br/>ชื่อ: {customer_name}<br/>บัตร: {id_card}<br/>ที่อยู่: {address}", "TH"),
         cell_para(f"{product_display}<br/>{' | '.join(details_bits)}"
                   + (f"<br/>รายละเอียด: {other_details}" if other_details else "")
                   + (f"<br/>ประเมิน: {estimated_value:,.2f} บาท" if estimated_value>0 else ""), "TH")]
    ]
    cust_prod_t = Table(cust_prod, colWidths=[(width-16*mm)/2, (width-16*mm)/2])
    cust_prod_t.setStyle(TableStyle([
        ('FONT',(0,0),(-1,-1),'THSarabun',9.6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOX',(0,0),(-1,-1),0.25,colors.grey),
        ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.whitesmoke),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))

    # Money summary (เน้นบรรทัดสุดท้าย)
    money = [
        [cell_para("ยอดฝากเดิม", "TH"), cell_para(f"{original_pawn_amount:,.2f}", "TH-right"),
         cell_para("", "TH"), cell_para("", "TH-right")],
        [cell_para("<b>รวมต่อดอก</b>", "TH-bold"), cell_para(f"<b>{total_amount:,.2f}</b>", "TH-right"),
         cell_para("<b>ยอดไถ่คืนรวม</b>", "TH-bold"), cell_para(f"<b>{total_redemption:,.2f}</b>", "TH-right")],
    ]
    money_t = Table(money, colWidths=[28*mm, 28*mm, 28*mm, (width-16*mm) - 84*mm])
    money_t.setStyle(TableStyle([
        ('FONT',(0,0),(-1,-1),'THSarabun',9.6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOX',(0,0),(-1,-1),0.25,colors.grey),
        ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
        ('BACKGROUND',(0,2),(-1,2),colors.whitesmoke),
    ]))

    # Terms (ย่อเป็นย่อหน้าเดียว)
    terms_text = (
        f"• ต่อเพิ่ม {extension_days} วัน | ครบใหม่ {thai_new_end_date} | ไถ่คืนรวม {total_redemption:,.2f} บาท "
        "• หากไม่ไถ่คืนตามกำหนด ทรัพย์สินตกเป็นของร้าน • ต่อได้อีกโดยชำระดอก/ค่าธรรมเนียม • มูลค่าประเมินเดิมไม่เปลี่ยน"
    )
    terms = Table([[cell_para(terms_text, "TH-mini")]], colWidths=[width-16*mm])
    terms.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.25,colors.grey),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))

    # Signatures (ตารางบาง ๆ)
    sig = Table([
        [cell_para("ลงชื่อ ____________________ ผู้รับฝาก", "TH"),
         cell_para("ลงชื่อ ____________________ ผู้ขายฝาก", "TH")],
        [cell_para("( นาย/นาง/นางสาว _________________ )", "TH"),
         cell_para(f"( {customer_name} )", "TH")],
        [cell_para("วันที่: _________________", "TH"),
         cell_para(f"วันที่: {renewal_date_disp}", "TH")],
    ], colWidths=[(width-16*mm)/2, (width-16*mm)/2])
    sig.setStyle(TableStyle([
        ('FONT',(0,0),(-1,-1),'THSarabun',9.6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))

    footer = cell_para(
        f"เอกสารต่อดอกสร้างโดยระบบ | เลขที่สัญญา: {original_contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "TH-mini"
    )

    content = [
        *header,
        Spacer(1, 2),
        two_col,
        Spacer(1, 2),
        cust_prod_t,
        Spacer(1, 2),
        money_t,
        Spacer(1, 1),
        terms,
        Spacer(1, 1),
        sig,
        Spacer(1, 1),
        footer
    ]

    # ----- Build with KeepInFrame (บีบอัตโนมัติให้พอดีครึ่งหน้า) -----
    doc = TopHalfDoc(output_file, pagesize=A4)
    maxW = doc.frame._width
    maxH = doc.frame._height
    story = [KeepInFrame(maxW, maxH, content, mode='shrink')]  # <<< จุดสำคัญ
    doc.build(story)
    print(f"Successfully created renewal contract '{output_file}'")
    return output_file


# ----------------- RECEIPT (ใช้แนวคิดเดียวกัน) -----------------
def generate_renewal_receipt_pdf(renewal_data: Dict, customer_data: Dict,
                                 original_contract_data: Dict, shop_data: Optional[Dict] = None,
                                 output_file: Optional[str] = None, output_folder: Optional[str] = None,
                                 ask_folder: bool = False) -> str:
    try:
        ensure_fonts()
    except Exception as e:
        print(e); return ""

    if not output_file:
        contract_number = original_contract_data.get('contract_number', 'unknown')
        renewal_date = renewal_data.get('renewal_date', datetime.now().strftime('%Y%m%d'))
        output_file = f"renewal_receipt_{contract_number}_{renewal_date}.pdf"

    if ask_folder and not output_folder:
        output_folder = select_output_folder("เลือกโฟลเดอร์สำหรับจัดเก็บใบเสร็จการต่อดอก")
        if not output_folder:
            print("ยกเลิกการสร้าง PDF"); return ""
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, output_file)

    styles = make_styles()
    width, height = A4

    # Load shop configuration from JSON file
    default_shop_config = load_shop_config()
    shop_name = (shop_data or {}).get('name', default_shop_config['name'])
    shop_branch = (shop_data or {}).get('branch', default_shop_config['branch'])
    shop_address = (shop_data or {}).get('address', default_shop_config['address'])

    contract_number = original_contract_data.get('contract_number', 'N/A')
    extension_days = int(renewal_data.get('extension_days', 0) or 0)
    total_amount = float(renewal_data.get('total_amount', 0) or 0)
    renewal_date_disp = thai_date(renewal_data.get('renewal_date', datetime.now().strftime('%Y-%m-%d')))

    first_name = customer_data.get('first_name', '')
    last_name = customer_data.get('last_name', '')
    customer_name = f"{first_name} {last_name}".strip()
    phone = customer_data.get('phone', 'N/A')

    header = [
        Paragraph("ใบเสร็จการต่อดอก", styles["TH-h"]),
        Paragraph(f"{shop_name} ({shop_branch})", styles["TH-sub"]),
        Paragraph(shop_address, styles["TH"]),
    ]

    info = Table([
        [Paragraph("<b>รายละเอียดการต่อดอก</b>", styles["TH-bold"]), ""],
        [Paragraph("เลขที่สัญญา", styles["TH"]), Paragraph(contract_number, styles["TH-right"])],
        [Paragraph("วันที่ต่อดอก", styles["TH"]), Paragraph(renewal_date_disp, styles["TH-right"])],
        [Paragraph("ต่อเพิ่ม", styles["TH"]), Paragraph(f"{extension_days} วัน", styles["TH-right"])],
        [Paragraph("ดอกเบี้ย", styles["TH"]), Paragraph(f"{interest_amount:,.2f}", styles["TH-right"])],
        [Paragraph("ค่าธรรมเนียม", styles["TH"]), Paragraph(f"{fee_amount:,.2f}", styles["TH-right"])],
        [Paragraph("<b>ยอดรวม</b>", styles["TH-bold"]), Paragraph(f"<b>{total_amount:,.2f}</b>", styles["TH-right"])],
    ], colWidths=[60*mm, (width-16*mm)-60*mm])
    info.setStyle(TableStyle([
        ('FONT',(0,0),(-1,-1),'THSarabun',9.6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOX',(0,0),(-1,-1),0.25,colors.grey),
        ('INNERGRID',(0,1),(-1,-1),0.25,colors.grey),
        ('SPAN',(0,0),(1,0)),
        ('BACKGROUND',(0,0),(1,0),colors.whitesmoke),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))

    cust = Table([
        [Paragraph("<b>ลูกค้า</b>", styles["TH-bold"]), Paragraph("<b>การชำระเงิน</b>", styles["TH-bold"])],
        [Paragraph(f"ชื่อ: {customer_name}<br/>โทร: {phone}", styles["TH"]),
         Paragraph(f"สถานะ: ชำระแล้ว<br/>วันที่: {renewal_date_disp}<br/>จำนวน: {total_amount:,.2f} บาท", styles["TH"])],
    ], colWidths=[(width-16*mm)/2, (width-16*mm)/2])
    cust.setStyle(TableStyle([
        ('FONT',(0,0),(-1,-1),'THSarabun',9.6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOX',(0,0),(-1,-1),0.25,colors.grey),
        ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.whitesmoke),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))

    footer = Paragraph(
        f"เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles["TH-mini"]
    )

    content = [*header, Spacer(1,2), info, Spacer(1,2), cust, Spacer(1,1), footer]

    # build in half page with auto-shrink
    doc = TopHalfDoc(output_file, pagesize=A4)
    maxW, maxH = doc.frame._width, doc.frame._height
    story = [KeepInFrame(maxW, maxH, content, mode='shrink')]
    doc.build(story)
    print(f"Successfully created renewal receipt '{output_file}'")
    return output_file


if __name__ == "__main__":
    print("Half-page PDFs ready. ใช้ KeepInFrame เพื่ออัดทุกอย่างให้อยู่ครึ่งแผ่นเดียว.")
