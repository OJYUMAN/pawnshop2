# generate_pawn_ticket_v6_2_halfA4_compact_clean.py
# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.units import mm
from datetime import datetime
import os
from typing import Dict, Optional, List


# -------- utils --------
def ensure_fonts():
    from resource_path import get_font_path
    font_path = get_font_path('THSarabun.ttf')
    bold_font_path = get_font_path('THSarabun Bold.ttf')
    if not (os.path.exists(font_path) and os.path.exists(bold_font_path)):
        raise FileNotFoundError(f"ไม่พบไฟล์ฟอนต์: {font_path} หรือ {bold_font_path}")
    pdfmetrics.registerFont(TTFont('THSarabun', font_path))
    pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))


def thai_date(date_str: str) -> str:
    month_map = {
        'January': 'มกราคม', 'February': 'กุมภาพันธ์', 'March': 'มีนาคม',
        'April': 'เมษายน', 'May': 'พฤษภาคม', 'June': 'มิถุนายน',
        'July': 'กรกฎาคม', 'August': 'สิงหาคม', 'September': 'กันยายน',
        'October': 'ตุลาคม', 'November': 'พฤศจิกายน', 'December': 'ธันวาคม'
    }
    from datetime import datetime
    try:
        if date_str and date_str != 'N/A':
            if '-' in date_str:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                dt = datetime.strptime(date_str, '%d/%m/%Y')
            s = dt.strftime('%d %B %Y')
            for eng, th in month_map.items():
                s = s.replace(eng, th)
            return s
        return 'N/A'
    except Exception:
        return date_str or 'N/A'


# -------- main --------
def generate_pawn_ticket_from_data(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    output_file: Optional[str] = None,
    renewal_data: Optional[List[Dict]] = None,
) -> str:
    """
    คอมแพ็กต์ครึ่งบน A4 หน้าเดียว (2 คอลัมน์) – เวอร์ชันตัด อัตราดอกเบี้ย/ค่าธรรมเนียม/หัก ณ ที่จ่าย ออก
    """
    ensure_fonts()

    width, height = A4
    margin_lr = 8 * mm
    margin_top = 6 * mm
    frame_y = height / 2
    frame_h = height / 2 - margin_top

    if not output_file:
        output_file = f"pawn_ticket_{contract_data.get('contract_number','unknown')}.pdf"

    # ---- styles ----
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TH-base", fontName="THSarabun", fontSize=11.2, leading=13))
    styles.add(ParagraphStyle(name="TH-bold", fontName="THSarabun-Bold", fontSize=11.2, leading=13))
    styles.add(ParagraphStyle(name="TH-small", fontName="THSarabun", fontSize=10.5, leading=12))
    styles.add(ParagraphStyle(name="TH-header", fontName="THSarabun-Bold", fontSize=20, leading=24, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-sub", fontName="THSarabun-Bold", fontSize=13, leading=16, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TH-right", fontName="THSarabun", fontSize=11.2, leading=13, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TH-right-bold", fontName="THSarabun-Bold", fontSize=11.2, leading=13, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TH-term", fontName="THSarabun", fontSize=10.2, leading=12))

    # ---- data ----
    shop_name = (shop_data or {}).get('name', 'ร้าน ไอโปรโมบายเซอร์วิส')
    shop_branch = (shop_data or {}).get('branch', 'สาขาหล่มสัก')
    shop_address = (shop_data or {}).get('address', '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110')

    contract_number = contract_data.get('contract_number', 'N/A')
    start_date = thai_date(contract_data.get('start_date', 'N/A'))
    end_date = thai_date(contract_data.get('end_date', 'N/A'))
    days_count = contract_data.get('days_count', 0)

    pawn_amount = float(contract_data.get('pawn_amount', 0))
    total_redemption = float(contract_data.get('total_redemption', pawn_amount))
    total_paid = float(contract_data.get('total_paid', pawn_amount))

    full_name = f"{customer_data.get('first_name','')} {customer_data.get('last_name','')}".strip() or "-"
    customer_code = customer_data.get('customer_code', '-') or '-'
    phone = customer_data.get('phone', '-') or '-'
    id_card = customer_data.get('id_card', '-') or '-'
    addr_parts = [p for p in [
        customer_data.get('house_number',''),
        customer_data.get('street',''),
        f"ต.{customer_data.get('subdistrict','')}" if customer_data.get('subdistrict') else "",
        f"อ.{customer_data.get('district','')}" if customer_data.get('district') else "",
        f"จ.{customer_data.get('province','')}" if customer_data.get('province') else "",
    ] if p]
    address = " ".join(addr_parts) if addr_parts else "-"

    prod_name = product_data.get('name','-') or '-'
    brand = product_data.get('brand','')
    prod_display = f"{brand} {prod_name}".strip() if brand else prod_name
    size = product_data.get('size','-') or '-'
    weight = product_data.get('weight','')
    weight_unit = product_data.get('weight_unit','')
    weight_txt = f"{weight} {weight_unit}".strip() if weight else "-"
    sn = product_data.get('serial_number','-') or '-'
    other = product_data.get('other_details','-') or '-'

    renewal_lines = []
    if renewal_data:
        total_renewal_fees = sum(r.get('total_amount', 0) for r in renewal_data)
        total_renewal_days = sum(r.get('extension_days', 0) for r in renewal_data)
        renewal_lines = [
            f"ต่อดอกแล้ว {len(renewal_data)} ครั้ง รวม {int(total_renewal_days)} วัน",
            f"ค่าธรรมเนียมต่อดอกรวม: {total_renewal_fees:,.2f} บาท",
        ]

    # ---------- story ----------
    story = []
    story.append(Paragraph("ใบขายฝาก", styles["TH-header"]))
    story.append(Paragraph(f"{shop_name} ({shop_branch})", styles["TH-sub"]))
    story.append(Paragraph(shop_address, styles["TH-base"]))
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.grey))
    story.append(Spacer(1, 2))

    # สรุปสัญญา
    summary = Table([
        [
            Paragraph(f"สัญญาเลขที่: <b>{contract_number}</b>", styles["TH-base"]),
            Paragraph(f"วันที่ทำสัญญา: <b>{start_date}</b>", styles["TH-right"])
        ],
        [
            Paragraph(f"ระยะเวลาฝาก: <b>{days_count} วัน</b>", styles["TH-base"]),
            Paragraph(f"ครบกำหนด: <b>{end_date}</b>", styles["TH-right"])
        ],
    ], colWidths=[(width-2*margin_lr)/2, (width-2*margin_lr)/2])
    summary.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(summary)
    story.append(Spacer(1, 3))

    # --- 2 คอลัมน์ ---
    col_w = (width - 2*margin_lr)
    left_w = col_w * 0.53
    right_w = col_w * 0.47

    # Left column
    cust_tbl_inner = Table([
        [Paragraph(f"รหัสลูกค้า: <b>{customer_code}</b>", styles["TH-base"]),
         Paragraph(f"โทรศัพท์: <b>{phone}</b>", styles["TH-base"])],
        [Paragraph(f"ชื่อ-นามสกุล: <b>{full_name}</b>", styles["TH-base"]), ""],
        [Paragraph(f"บัตรประชาชน: <b>{id_card}</b>", styles["TH-base"]), ""],
        [Paragraph(f"ที่อยู่: <b>{address}</b>", styles["TH-base"]), ""],
    ], colWidths=[left_w*0.62, left_w*0.38])
    cust_tbl_inner.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.7,colors.black),
        ("INNERGRID",(0,0),(-1,-1),0.25,colors.Color(0.85,0.85,0.85)),
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    prod_tbl_inner = Table([
        [Paragraph(f"ทรัพย์สิน: <b>{prod_display}</b>", styles["TH-base"])],
        [Paragraph(f"ขนาด: <b>{size}</b>   |   น้ำหนัก: <b>{weight_txt}</b>   |   S/N: <b>{sn}</b>", styles["TH-base"])],
        [Paragraph(f"รายละเอียดอื่นๆ: <b>{other}</b>", styles["TH-base"])],
    ], colWidths=[left_w-2])
    prod_tbl_inner.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.7,colors.black),
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    left_stack = Table([
        [Paragraph("<b>ข้อมูลผู้ขายฝาก</b>", styles["TH-bold"])],
        [cust_tbl_inner],
        [Spacer(1, 3)],
        [Paragraph("<b>รายการทรัพย์สินที่ขายฝาก</b>", styles["TH-bold"])],
        [prod_tbl_inner],
    ], colWidths=[left_w])
    left_stack.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))

    # Right column: finance (ตัดอัตราดอก/ค่าธรรมเนียม/หัก ณ ที่จ่าย)
    finance_rows = [
        [Paragraph(f"ยอดฝาก: <b>{pawn_amount:,.2f} บาท</b>", styles["TH-base"]),
         Paragraph(f"ระยะเวลา: <b>{days_count} วัน</b>", styles["TH-base"])],
    ]
    # แสดง "ยอดจ่าย" เฉพาะเมื่อไม่เท่ากับยอดฝาก
    if abs(total_paid - pawn_amount) > 1e-6:
        finance_rows.append([Paragraph(f"ยอดจ่าย: <b>{total_paid:,.2f} บาท</b>", styles["TH-base"]), ""])

    finance_tbl_inner = Table(finance_rows, colWidths=[right_w*0.58, right_w*0.42])
    finance_tbl_inner.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.7,colors.black),
        ("INNERGRID",(0,0),(-1,-1),0.25,colors.Color(0.85,0.85,0.85)),
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    highlight = Table([[Paragraph(
        f"<b>ยอดไถ่ถอนรวม: {total_redemption:,.2f} บาท</b>  |  <b>กำหนดไถ่ถอน: {end_date}</b>",
        styles["TH-bold"]
    )]], colWidths=[right_w])
    highlight.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.Color(0.96,0.96,0.96)),
        ("BOX",(0,0),(-1,-1),0.7,colors.black),
        ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    # เงื่อนไขสำคัญ (ตัดข้อความเกี่ยวกับดอกเบี้ย/ค่าธรรมเนียม/หัก ณ ที่จ่าย ออก)
    terms = [
        f"• ไถ่ถอนภายใน <b>{end_date}</b> มิฉะนั้นทรัพย์จะตกเป็นของร้าน",
        f"• ยอดไถ่ถอนรวม <b>{total_redemption:,.2f} บาท</b>",
    ]
    if renewal_data:
        terms += renewal_lines
    else:
        terms += ["• ต่อดอกได้เมื่อครบกำหนด ตามเงื่อนไขของร้าน"]

    terms += [
        "• ผู้ขายฝากยืนยันกรรมสิทธิ์ถูกต้องและไม่เกี่ยวข้องกับการกระทำผิดกฎหมาย",
        "• กรณีมีผู้ก่อกวนสิทธิ์ ผู้ขายฝากต้องชดใช้ความเสียหาย",
        "• ความเสียหายจากภัยธรรมชาติ/โจรกรรม ร้านไม่รับผิดชอบ",
    ]

    right_stack = Table([
        [Paragraph("<b>ข้อมูลการเงิน</b>", styles["TH-bold"])],
        [finance_tbl_inner],
        [Spacer(1, 3)],
        [highlight],
        [Spacer(1, 3)],
        [Paragraph("<b>เงื่อนไขสำคัญ (ย่อ)</b>", styles["TH-bold"])],
        [Paragraph("<br/>".join(terms), styles["TH-term"])],
    ], colWidths=[right_w])
    right_stack.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))

    # Two-column wrapper
    two_col = Table([[left_stack, right_stack]], colWidths=[left_w, right_w])
    two_col.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    two_col.hAlign = "LEFT"
    story.append(two_col)
    story.append(Spacer(1, 3))

    # signatures
    sig = Table([
        [
            Paragraph("ลงชื่อ ________________________ ผู้รับฝาก", styles["TH-base"]),
            Paragraph("ลงชื่อ ________________________ ผู้ขายฝาก", styles["TH-right-bold"])
        ],
        [
            Paragraph("( นาย/นาง/นางสาว __________________ )", styles["TH-base"]),
            Paragraph(f"( {full_name} )", styles["TH-right-bold"])
        ],
        [
            Paragraph("วันที่: ____________", styles["TH-base"]),
            Paragraph(f"วันที่: {start_date}", styles["TH-right-bold"])
        ]
    ], colWidths=[(width-2*margin_lr)/2, (width-2*margin_lr)/2])
    sig.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),
        ("BOTTOMPADDING",(0,0),(-1,-1),1),
    ]))
    story.append(sig)

    # footer
    story.append(Paragraph(
        f"<font name='THSarabun' size='9.8'>เอกสารสร้างโดยระบบ | เลขที่สัญญา: {contract_number} | "
        f"สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</font>",
        styles["TH-base"]
    ))

    # ------- DocTemplate with top-half frame -------
    class TopHalfDoc(BaseDocTemplate):
        def __init__(self, filename, **kw):
            kw.setdefault("allowSplitting", 1)
            super().__init__(filename, **kw)
            self.allowSplitting = 1
            self.splitLongTables = 1
            frame = Frame(
                margin_lr, frame_y, width-2*margin_lr, frame_h,
                leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                showBoundary=0
            )
            self.addPageTemplates(PageTemplate(id='TopHalf', frames=[frame]))

    doc = TopHalfDoc(output_file, pagesize=A4,
                     leftMargin=margin_lr, rightMargin=margin_lr, topMargin=margin_top, bottomMargin=0)

    doc.build(story)
    return output_file


# ----- quick demo -----
if __name__ == "__main__":
    contract = {
        "contract_number": "LS-2025-0001",
        "start_date": "2025-09-10",
        "end_date": "2025-10-10",
        "days_count": 30,
        "estimated_value": 15000,
        "pawn_amount": 10000,
        # *** ตัด fields ดอก/ค่าธรรมเนียม/หัก ณ ที่จ่าย ออก — เก็บไว้ก็ได้แต่ไม่ถูกใช้งาน ***
        "total_paid": 10000,
        "total_redemption": 10350
    }
    customer = {
        "customer_code": "CUST-001",
        "first_name": "สมชาย",
        "last_name": "ใจดี",
        "phone": "081-234-5678",
        "id_card": "1234567890123",
        "house_number": "99/9",
        "street": "ถ.พินิจ",
        "subdistrict": "หล่มสัก",
        "district": "หล่มสัก",
        "province": "เพชรบูรณ์"
    }
    product = {
        "name": "iPhone 13 Pro Max",
        "brand": "Apple",
        "size": "6.7 นิ้ว",
        "weight": "240",
        "weight_unit": "กรัม",
        "serial_number": "SN1234567890",
        "other_details": "สภาพดี มีเคสและฟิล์ม"
    }
    shop = {
        "name": "ร้าน ไอโปรโมบายเซอร์วิส",
        "branch": "สาขาหล่มสัก",
        "address": "14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110"
    }
    renewals = [
        {"extension_days": 15, "total_amount": 150.0},
        {"extension_days": 10, "total_amount": 120.0},
    ]
    out = generate_pawn_ticket_from_data(
        contract, customer, product, shop, "pawn_ticket_halfA4_compact_clean.pdf", renewals
    )
    print("Created:", out)
