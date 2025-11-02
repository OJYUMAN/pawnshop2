# pdf3.py
# -*- coding: utf-8 -*-
"""
Generate Thai redemption-contract PDF using WeasyPrint only.

- ใช้ WeasyPrint เรนเดอร์ HTML → PDF (ไม่มี ReportLab)
- HA4 แนวนอน (210mm × 148.5mm), margin = 5mm รอบด้าน
- ฟอนต์ไทย: พยายามใช้ "TH Sarabun New" ถ้ามีในระบบ, สำรองเป็น "Sarabun", "Noto Sans Thai"
- รองรับฟังก์ชันชื่อเดิม: generate_redemption_ticket_pdf_data(), generate_redemption_contract_html(), generate_redemption_ticket_from_data()
- ใช้พารามิเตอร์ข้อมูลแบบเดิม (contract_data, customer_data, product_data, shop_data)

ติดตั้งระบบเสริม (Linux) ตามเอกสาร WeasyPrint ถ้าจำเป็น: cairo, pango, gdk-pixbuf, libffi
"""

import sys
import os

# Set up environment for WeasyPrint on macOS
if sys.platform == "darwin":  # macOS
    os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib:" + os.environ.get("DYLD_LIBRARY_PATH", "")
    os.environ["PKG_CONFIG_PATH"] = "/opt/homebrew/lib/pkgconfig:" + os.environ.get("PKG_CONFIG_PATH", "")

from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
import html

from weasyprint import HTML, CSS

# ---------- Utils ----------
TH_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def buddhist_year(dt: datetime) -> int:
    return dt.year + 543

def thai_date(date_str: str, include_time: bool = False) -> str:
    """
    รองรับ 'YYYY-MM-DD' หรือ 'DD/MM/YYYY' หรือ 'YYYY-MM-DD HH:MM' หรือ 'DD/MM/YYYY HH:MM'
    คืนค่าเป็นวันที่ไทย (พ.ศ.) เช่น '14 ตุลาคม 2568' หรือ '14 ตุลาคม 2568 เวลา 10:30 น.'
    """
    if not date_str or date_str == "N/A":
        return "N/A"
    ds = date_str.strip()
    dt: Optional[datetime] = None
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
    # ถ้าสตริงมีเวลา หรือบังคับ include_time
    if include_time or ("%H:%M" in ds):
        return f"{day} {month_name} {year_th} เวลา {dt.strftime('%H:%M')} น."
    return f"{day} {month_name} {year_th}"

def money(n) -> str:
    try:
        f = float(n)
        if abs(f - int(f)) < 1e-9:
            return "{:,.0f}".format(f)
        else:
            return "{:,.2f}".format(f)
    except Exception:
        return str(n)

def esc(s) -> str:
    return html.escape("" if s is None else str(s))

# ---------- Optional font discovery ----------
def _font_face_block() -> str:
    """
    พยายามใช้ฟอนต์จากระบบก่อน: 'TH Sarabun New', 'Sarabun', 'Noto Sans Thai'
    ถ้ามีโมดูล resource_path.get_font_path() จะลองดึงไฟล์ฟอนต์จากโปรเจ็กต์
    """
    font_sources = []

    # 1) system-local (no file path needed)
    font_sources.append("""
    @font-face {
      font-family: 'THSarabunLocal';
      src: local('TH Sarabun New'), local('Sarabun');
      font-weight: 400;
      font-style: normal;
    }
    @font-face {
      font-family: 'THSarabunLocal';
      src: local('TH Sarabun New Bold'), local('Sarabun Bold');
      font-weight: 700;
      font-style: normal;
    }
    """)

    # 2) optional project font path (if available)
    try:
        from resource_path import get_font_path  # optional utility in your project
        # ลองชื่อทั่วไป
        for name, weight in [("THSarabunNew.ttf", 400), ("THSarabunNew Bold.ttf", 700), ("Sarabun-Regular.ttf", 400), ("Sarabun-Bold.ttf", 700)]:
            try:
                p = get_font_path(name)
                if p and os.path.exists(p):
                    url = Path(p).absolute().as_uri()
                    font_sources.append(f"""
                    @font-face {{
                      font-family: 'THSarabunLocal';
                      src: url('{url}');
                      font-weight: {weight};
                      font-style: normal;
                    }}
                    """)
            except Exception:
                pass
    except Exception:
        # ไม่มี resource_path ก็ข้าม
        pass

    # 3) fallback to generic (Noto Sans Thai / system-ui)
    font_sources.append("""
    @font-face {
      font-family: 'NotoThaiLocal';
      src: local('Noto Sans Thai'), local('Noto Sans');
      font-weight: 400;
      font-style: normal;
    }
    """)

    return "\n".join(font_sources)

# ---------- HTML Builder ----------
def _build_redemption_contract_html(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    font_size_multiplier: float = 1.0,
) -> str:
    # ร้าน
    default_shop = {}
    try:
        from shop_config_loader import load_shop_config  # optional
        default_shop = load_shop_config() or {}
    except Exception:
        default_shop = {
            "name": "ร้านตัวอย่าง",
            "branch": "สาขาตัวอย่าง",
            "address": "123/45 ถ.ตัวอย่าง ต.ตัวอย่าง อ.ตัวอย่าง จ.ตัวอย่าง 10000",
        }

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

    # เงื่อนไข: ข้อ 1-5 ติดกันและเป็นตัวหนาทั้งหมด - สำหรับการไถ่คืน
    terms_text = f"""
    <div class="term-bold-continuous">ข้อ 1. ผู้ขายฝากได้ชำระเงินไถ่ถอนครบถ้วนจำนวน <span class="amount-underline">{money(redemption_amount)}</span> บาท ตามกำหนดเวลา ข้อ 2. ผู้ซื้อฝากได้ส่งมอบทรัพย์สินและอุปกรณ์ครบถ้วนให้ผู้ขายฝากแล้ว ข้อ 3. สัญญาขายฝากเดิมเลขที่ {esc(contract_data.get('original_contract_number', contract_number))} สิ้นสุดลง ข้อ 4. ผู้ขายฝากรับรองว่าได้รับทรัพย์สินและอุปกรณ์ครบถ้วนในสภาพเดิม ข้อ 5. คู่สัญญาไม่มีข้อพิพาทใดๆ ต่อกัน</div>
    """

    # ฟุตเตอร์เวลา
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M')

    # คำนวณขนาดตัวอักษรตาม multiplier
    def scale_font(base_size):
        return base_size * font_size_multiplier
    
    body_font = scale_font(13)
    h1_font = scale_font(19)
    meta_font = scale_font(11)
    contract_number_font = scale_font(16)
    section_title_font = scale_font(15)
    term_large_font = scale_font(11)
    term_small_font = scale_font(11)
    signature_font = scale_font(11)
    foot_font = scale_font(6)
    # คำนวณระยะห่างลายเซ็นตามขนาดตัวอักษร
    # ตั้งค่าให้ช่องลงชื่อชิดกับแถวสุดท้ายของข้อมูล
    signature_margin_top = -25

    # HTML + CSS (inline) — ครึ่งหน้า A4, 0 margin, ตัวอักษรใหญ่
    html_doc = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <title>สัญญาไถ่คืน – {esc(full_name)} – {esc(contract_number)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    {_font_face_block()}

    @page {{
      size: 210mm 148.5mm;        /* HA4 แนวนอน: กว้าง 210mm × สูง 148.5mm */
      margin: 5mm;                /* margin 5mm รอบด้าน */
    }}
    html, body {{
      margin: 0; padding: 0;
    }}
    * {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      box-sizing: border-box;
    }}

    body {{
      font-family: 'THSarabunLocal', 'NotoThaiLocal', 'Noto Sans Thai', system-ui, sans-serif;
      color: #000;
      background: white;
      font-size: {body_font}pt;
      font-weight: 700;
      line-height: 1.3;
    }}

    .page {{
      width: 200mm;               /* กว้าง 210mm - margin 5mm × 2 = 200mm */
      height: 138.5mm;            /* สูง 148.5mm - margin 5mm × 2 = 138.5mm */
      margin: 0 auto;
      padding: 0;
      display: grid;
      grid-template-rows: auto 1fr auto; /* header / content / signatures */
      row-gap: 0mm;               /* ลบระยะห่างระหว่าง grid rows */
      max-height: 138.5mm;        /* จำกัดความสูงให้พอดีหน้า */
      overflow: hidden;            /* ป้องกันเนื้อหาล้น */
    }}
    
    .page > div:nth-child(2) {{
      overflow: hidden;            /* ป้องกันเนื้อหาล้นในส่วน content */
      min-height: 0;               /* อนุญาตให้ย่อได้ */
      margin-bottom: -10mm;        /* ลดระยะห่างด้านล่างเพื่อให้ชิดกับลายเซ็น */
    }}

    h1 {{
      text-align: center;
      font-weight: 700;
      font-size: {h1_font}pt;
      margin: 0;
      line-height: 1.1;
      padding: 0.3mm 1mm 0 1mm;
    }}

    .meta {{
      padding: 0 1mm;
      margin: 0;
    }}
    .meta .row {{
      display: flex;
      justify-content: space-between;
      gap: 2mm;
      margin: 0.2mm 0;
      font-size: {meta_font}pt;
      font-weight: 700;
      line-height: 1.2;
    }}
    .contract-number {{
      font-size: {contract_number_font}pt;
      font-weight: 700;
      color: #000;
    }}

    .section-title {{
      font-weight: 700;
      margin: 0.2mm 0 0.1mm 0;
      padding: 0 1mm;
      line-height: 1.2;
      font-size: {section_title_font}pt;
      display: block;
    }}
    span.section-title {{
      display: inline;
      margin: 0;
      padding: 0;
    }}

    p {{
      margin: 0.2mm 0;
      padding: 0 1mm;
      text-align: justify;
      font-weight: 700;
      line-height: 1.25;
    }}
    .indent {{ text-indent: 5mm; }}

    .terms {{
      margin-top: 0.1mm;
      padding: 0 1mm;
    }}
    
    .term-large {{
      font-size: {term_large_font}pt;
      font-weight: 700;
      line-height: 1.6;
      margin: 1mm 0;
      text-align: justify;
    }}
    
    .term-small {{
      font-size: {term_small_font}pt;
      font-weight: 700;
      line-height: 1.5;
      margin: 1mm 0;
      text-align: justify;
    }}
    
    .term-bold-continuous {{
      font-size: {term_large_font}pt;
      font-weight: 700;
      line-height: 1.4;
      margin: 0.5mm 0;
      text-align: justify;
    }}

    .signatures {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1mm;
      text-align: center;
      padding: 0 1mm;
      margin: {signature_margin_top}mm 0 0 0;
      font-size: {signature_font}pt;
      font-weight: 700;
      align-self: start;           /* จัดให้อยู่ด้านบนของ grid row เพื่อให้ margin-top ทำงาน */
    }}
    .sig-line {{ 
      white-space: nowrap;
      line-height: 1.2;
    }}

    .foot {{
      font-size: {foot_font}pt;
      font-weight: 700;
      text-align: right;
      padding: 0 1mm;
      margin: 0;
      line-height: 1.3;
    }}

    .amount-underline {{
      border-bottom: 2px solid #000;
      padding: 0 50px;
      display: inline-block;
      min-width: 30px;
    }}
    
    .product-content {{
      font-size: {term_large_font}pt;
      font-weight: 700;
      line-height: 1.25;
      margin: 0.2mm 0;
      padding: 0 1mm;
      text-align: justify;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div>
      <h1>สัญญาไถ่คืน</h1>
      <div class="meta">
        <div class="row"><span class="contract-number">สัญญาเลขที่: {esc(contract_number)}</span></div>
        <div class="row"><span>ทำที่: {esc(place_line)}</span><span>วันที่: {esc(start_date_th)}</span></div>
      </div>
    </div>

    <div>
      <div class="section-title">คู่สัญญา</div>
      <p class="indent">
        ระหว่าง {esc(full_name)}{f" อายุ {int(age)} ปี" if isinstance(age,(int,float)) else ""} เลขบัตรประชาชน {esc(id_card)} ที่อยู่ {esc(addr_text)} โทร {esc(phone)} ซึ่งเรียกว่า "<strong>ผู้ขายฝาก</strong>" กับ {esc(shop_name)} {esc(shop_branch)} เลขประจำตัวผู้เสียภาษี {esc(shop_tax_id)} ที่ตั้ง {esc(shop_address)} โทร {esc(shop_phone)} โดย{esc(authorized_signer)} เป็นผู้มีอำนาจลงนาม ซึ่งเรียกว่า "<strong>ผู้ซื้อฝาก</strong>"
      </p>

      <div class="section-title">รายละเอียดทรัพย์สิน</div>
      <p class="product-content indent">
        โทรศัพท์มือถือยี่ห้อ {esc(brand or 'ไม่ระบุ')} รุ่น {esc(model or 'ไม่ระบุ')}{(" สี " + esc(color)) if color else ""}{" IMEI1: " + esc(imei1) if imei1 else ""}{" IMEI2: " + esc(imei2) if imei2 else ""}{" Serial: " + esc(serial) if serial else ""} สภาพ{esc(condition)} อุปกรณ์: {esc(accessories)}
      </p>

      <div class="section-title">ข้อตกลงและเงื่อนไข</div>
      <div class="terms">{terms_text}</div>

      <div class="section-title">การชำระเงินและยืนยัน</div>
      <p class="indent">
        ผู้ขายฝากได้ชำระเงินไถ่ถอน <span class="amount-underline">{money(redemption_amount)}</span> บาท พร้อมรับทรัพย์สินและอุปกรณ์ครบถ้วน คู่สัญญาได้อ่านและเข้าใจข้อความโดยตลอดแล้ว จึงลงนามและยอมรับผูกพันตามสัญญา ทำ ณ {esc(place_line)} วันที่ {esc(thai_date(contract_data.get('signed_date') or start_date_raw))}
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
        <div>( {esc(buyer_signer_name or authorized_signer or 'ผู้มีอำนาจลงนาม')} )</div>
        <div>ผู้ซื้อฝาก</div>
      </div>
    </div>

  
  </div>
</body>
</html>"""
    return html_doc

# ---------- Public API ----------
def generate_redemption_contract_html(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    output_file: Optional[str] = None,
    witness_name: Optional[str] = None,  # kept for API compatibility (handled in shop_data/witness)
    font_size_multiplier: float = 1.0,
) -> str:
    """
    เขียนไฟล์ HTML ของสัญญาไถ่คืน (HA4 แนวนอน, margin 5mm, ตัวอักษรใหญ่)
    """
    # allow overriding witness by arg
    if witness_name:
        shop_data = dict(shop_data or {})
        shop_data["witness_name"] = witness_name

    html_doc = _build_redemption_contract_html(contract_data, customer_data, product_data, shop_data, font_size_multiplier)

    if not output_file:
        contract_number = contract_data.get("contract_number", "unknown")
        output_file = f"redemption_contract_{contract_number}.html"

    Path(output_file).write_text(html_doc, encoding="utf-8")
    return output_file

def generate_redemption_ticket_pdf_data(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    output_file: Optional[str] = None,
    font_size_multiplier: float = 1.0,
) -> str:
    """
    สร้าง PDF สัญญาไถ่คืนแบบ HA4 แนวนอน (210mm × 148.5mm) ด้วย WeasyPrint เท่านั้น
    """
    html_doc = _build_redemption_contract_html(contract_data, customer_data, product_data, shop_data, font_size_multiplier)

    if not output_file:
        contract_number = contract_data.get("contract_number", "unknown")
        output_file = f"redemption_contract_{contract_number}.pdf"

    # Stylesheet เสริม (ถ้าต้องการเพิ่มสำหรับสภาพแวดล้อมเฉพาะ)
    stylesheet = CSS(string="""
      /* ที่ว่างสำหรับ override เพิ่มเติมถ้าจำเป็น */
    """)

    HTML(string=html_doc, base_url=str(Path(".").absolute())).write_pdf(
        target=output_file,
        stylesheets=[stylesheet]
    )
    return output_file

def generate_redemption_ticket_from_data(
    contract_data: Dict,
    customer_data: Dict,
    product_data: Dict,
    shop_data: Optional[Dict] = None,
    show_preview: bool = False,  # kept for API compatibility (unused)
    output_file: Optional[str] = None,
    font_size_multiplier: float = 1.0,
) -> str:
    """
    Alias (เพื่อความเข้ากันได้กับโค้ดเดิม)
    """
    return generate_redemption_ticket_pdf_data(
        contract_data=contract_data,
        customer_data=customer_data,
        product_data=product_data,
        shop_data=shop_data,
        output_file=output_file,
        font_size_multiplier=font_size_multiplier
    )

# ---------- Quick demo ----------
if __name__ == "__main__":
    contract = {
        "contract_number": "RD-20259192",
        "copy_number": 1,
        "start_date": "2025-10-14",
        "start_time": "10:30",
        "end_date": "2025-11-13",
        "days_count": 30,
        "pawn_amount": 10000,
        "total_redemption": 11000,
        "original_contract_number": "CF-20259192",
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
        "witness_name": "นางสาวมั่นใจ ถูกต้อง",
    }

    html_out = generate_redemption_contract_html(contract, customer, product, shop, output_file="redemption_contract_demo.html")
    print("Created HTML:", html_out)

    pdf_out = generate_redemption_ticket_pdf_data(contract, customer, product, shop, output_file="redemption_contract_demo.pdf")
    print("Created PDF:", pdf_out)