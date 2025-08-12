# generate_pawn_ticket_v2_fixed.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_pawn_ticket(output_file="pawn_ticket.pdf"):
    """
    Generates a formal pawn ticket PDF document with a centered header.
    Fixed version with no text overlapping issues.

    Args:
        output_file (str): The name of the output PDF file.
    """
    try:
        # Load the Thai Sarabun font.
        # Ensure the 'THSarabun.ttf' file is in the same directory as this script.
        font_path = 'THSarabun.ttf'
        bold_font_path = 'THSarabun Bold.ttf'

        if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
            print(f"Error: Font file not found.")
            print("Please make sure 'THSarabun.ttf' and 'THSarabun Bold.ttf' are in the same folder as the script.")
            return

        pdfmetrics.registerFont(TTFont('THSarabun', font_path))
        pdfmetrics.registerFont(TTFont('THSarabun-Bold', bold_font_path))

    except Exception as e:
        print(f"An error occurred while loading the font: {e}")
        return

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # --- Centered Header ---
    # The title "ใบขายฝาก" is now centered with a larger font size for emphasis.
    c.setFont("THSarabun-Bold", 24)
    c.drawCentredString(width / 2.0, height - 60, "ใบขายฝาก")

    c.setFont("THSarabun-Bold", 16)
    c.drawCentredString(width / 2.0, height - 90, "ร้าน ไอโปรโมบายเซอร์วิส (สาขาหล่มสัก)")

    c.setFont("THSarabun", 12)
    c.drawCentredString(width / 2.0, height - 110, "14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110")

    # --- Document Body ---
    # We use a y_pos variable to easily manage vertical spacing.
    y_pos = height - 150
    left_margin = 50
    right_margin = width - 50

    # --- Contract Info ---
    # Placed contract number on the left and date on the right for a formal look.
    c.setFont("THSarabun", 14)
    c.drawString(left_margin, y_pos, "สัญญาเลขที่: 68-07-4-100650")
    c.drawRightString(right_margin, y_pos, "วันที่: 21 กรกฎาคม 2568")
    y_pos -= 30

    # --- Customer Info ---
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "ข้อมูลผู้ขายฝาก:")
    y_pos -= 20
    
    # Fixed: Put name and phone on separate lines to avoid overlap
    c.setFont("THSarabun", 14)
    c.drawString(left_margin + 15, y_pos, "ชื่อ: นายโสภี ยันหล้า")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "โทรศัพท์: 0918512767")
    y_pos -= 20
    
    # Fixed: Put address and ID on separate lines to avoid overlap
    c.drawString(left_margin + 15, y_pos, "ที่อยู่: 13/1 ซอยเพียรเหรียญรักษา ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "บัตรประชาชนเลขที่: 3679800089763")
    y_pos -= 25

    # --- Item Info ---
    c.line(left_margin, y_pos, right_margin, y_pos) # Separator line
    y_pos -= 20
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "รายการทรัพย์สินที่ขายฝาก:")
    y_pos -= 20
    c.setFont("THSarabun", 14)
    c.drawString(left_margin + 15, y_pos, "ทรัพย์สิน: realme c51")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "ขายฝากไว้เป็นจำนวนเงิน: 1,000.00 บาท (หนึ่งพันบาทถ้วน)")
    y_pos -= 20
    
    # Fixed: Put processing fee and service fee on separate lines
    c.drawString(left_margin + 15, y_pos, "ค่าดำเนินการ: 0.00 บาท")
    y_pos -= 20
    c.drawString(left_margin + 15, y_pos, "ค่าธรรมเนียม: 100.00 บาท")
    y_pos -= 25

    # --- Terms and Conditions ---
    c.line(left_margin, y_pos, right_margin, y_pos) # Separator line
    y_pos -= 20
    c.setFont("THSarabun-Bold", 14)
    c.drawString(left_margin, y_pos, "เงื่อนไขและข้อตกลง:")
    y_pos -= 15
    c.setFont("THSarabun", 12)
    
    # Fixed: Adjusted line spacing and text wrapping for better readability
    text_terms = [
        "1. ข้าพเจ้าขอรับรองว่าสินค้าที่นำมาขายฝากเป็นกรรมสิทธิ์ของผู้ขายฝากอย่างแท้จริง ไม่มีการติดค้างชำระ",
        "    หรืออยู่ระหว่างผ่อนชำระ และไม่เกี่ยวกับการกระทำผิดกฏหมายใดๆ และมิได้ได้มาโดยการลักทรัพย์",
        "    ฉ้อโกง วิ่งราว กรรโชกทรัพย์ รีดทรัพย์ หรือโกงเจ้าหนี้แต่ประการใด",
        "",
        "2. หากมีบุคคลใดมาก่อกวนขัดสิทธิ์ผู้ซื้อในอันจะครองทรัพย์สินโดยปกติ เพราะบุคคลนั้นมีสิทธิ์",
        "    เหนือทรัพย์สินที่ได้ขายฝาก เพราะความผิดของผู้ขายฝาก ผู้ขายฝากจำต้องรับผิดชดใช้ค่าสินค้า",
        "    และความเสียหายอื่นๆ (ถ้ามี) แก่ผู้ซื้อ",
        "",
        "3. ข้าพเจ้าผู้ขายฝากได้อ่านเงื่อนไขที่กำหนดไว้ ได้รับทราบและเข้าใจถี่ถ้วน และตกลงทำตาม",
        "    เงื่อนไขในเอกสารนี้ทุกประการ พร้อมได้รับเงินถูกต้องตามจำนวนแล้ว จึงลงลายมือชื่อไว้เป็นหลักฐาน"
    ]
    
    for line in text_terms:
        if line.strip():  # Only draw non-empty lines
            c.drawString(left_margin + 15, y_pos, line)
        y_pos -= 16  # Consistent line spacing
    
    y_pos -= 15

    # --- Note ---
    c.setFont("THSarabun-Bold", 12)
    c.drawString(left_margin, y_pos, "หมายเหตุ:")
    y_pos -= 15
    c.setFont("THSarabun", 12)
    
    # Fixed: Split long note text into multiple lines
    note_lines = [
        "กรณีสินค้าหายหรือสูญหายซึ่งพิสูจน์ได้ว่าถูกโจรกรรม หรือเนื่องจากภัยธรรมชาติ",
        "ทางร้านไม่ต้องชดใช้หรือรับผิดชอบใดๆทั้งสิ้น",
        "",
        "หากเกินกำหนดเวลาไถ่ถอน ถือว่าท่านสละสิทธิ์ในทรัพย์สินนี้ให้ตกเป็นของทางร้านโดยสมบูรณ์"
    ]
    
    for note_line in note_lines:
        if note_line.strip():
            c.drawString(left_margin + 30, y_pos, note_line)
        y_pos -= 16
    
    y_pos -= 15

    # --- Redeem Info ---
    c.setFont("THSarabun-Bold", 16)
    c.drawString(left_margin, y_pos, "ยอดไถ่ถอน: 1,100.00 บาท (หนึ่งพันหนึ่งร้อยบาทถ้วน)")
    y_pos -= 25
    c.drawString(left_margin, y_pos, "กำหนดไถ่ทรัพย์สินภายในวันที่: 20 สิงหาคม 2568")
    y_pos -= 60

    # --- Signatures ---
    c.setFont("THSarabun", 14)
    # Fixed: Proper spacing for signatures
    signature_y = y_pos
    c.drawString(left_margin + 30, signature_y, "ลงชื่อ _________________________ ผู้รับฝาก")
    c.drawString(width - 280, signature_y, "ลงชื่อ _________________________ ผู้ขายฝาก")
    
    signature_y -= 25
    c.drawString(width - 230, signature_y, "( นายโสภี ยันหล้า )")

    # Save the PDF file
    c.save()
    print(f"Successfully created '{output_file}'")

# --- Main execution ---
if __name__ == "__main__":
    # This will create the PDF file in the same directory where you run the script.
    generate_pawn_ticket("pawn_ticket_fixed.pdf")