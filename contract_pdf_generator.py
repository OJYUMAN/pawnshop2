# -*- coding: utf-8 -*-
"""
ระบบสร้างใบขายฝาก PDF จากข้อมูลสัญญา
ปรับเนื้อหาให้ตรงตามสัญญาและใช้ format เหมือน pdf.py
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from typing import Dict, Optional
from database import PawnShopDatabase
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QObject, Signal

class ContractPDFGenerator(QObject):
    """คลาสสำหรับสร้างใบขายฝาก PDF จากข้อมูลสัญญา"""
    
    pdf_generated = Signal(str)  # ส่งสัญญาณเมื่อสร้าง PDF สำเร็จ
    
    def __init__(self):
        super().__init__()
        self.db = PawnShopDatabase()
        self.setup_fonts()
    
    def setup_fonts(self):
        """ตั้งค่าฟอนต์ภาษาไทยด้วยการปรับปรุงการแสดงผล"""
        try:
            from resource_path import get_font_path
            font_path = get_font_path('NotoSansThai-Regular.ttf')
            bold_font_path = get_font_path('NotoSansThai-Bold.ttf')
            
            if not os.path.exists(font_path) or not os.path.exists(bold_font_path):
                raise FileNotFoundError(f"ไม่พบไฟล์ฟอนต์: {font_path} หรือ {bold_font_path}")
            
            # ใช้ subfontIndex=0 เพื่อให้รองรับตัวอักษรไทยได้ดีขึ้น
            pdfmetrics.registerFont(TTFont('NotoSansThai', font_path, subfontIndex=0))
            pdfmetrics.registerFont(TTFont('NotoSansThai-Bold', bold_font_path, subfontIndex=0))
            
            print("ฟอนต์ภาษาไทยโหลดสำเร็จ - NotoSansThai และ NotoSansThai-Bold")
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดฟอนต์: {e}")
            raise
    
    def generate_contract_pdf(self, contract_id: int, output_path: str = None, ask_folder: bool = False) -> Optional[str]:
        """
        สร้างใบขายฝาก PDF จากข้อมูลสัญญา
        
        Args:
            contract_id: ID ของสัญญา
            output_path: เส้นทางไฟล์ที่จะบันทึก (ถ้าไม่ระบุจะให้เลือกเอง)
            ask_folder: ถ้าเป็น True จะแสดง dialog เลือกโฟลเดอร์
        
        Returns:
            เส้นทางไฟล์ที่บันทึก หรือ None ถ้าเกิดข้อผิดพลาด
        """
        try:
            # ดึงข้อมูลสัญญา
            contract_data = self.db.get_contract_by_id(contract_id)
            if not contract_data:
                raise ValueError("ไม่พบข้อมูลสัญญา")
            
            # ดึงข้อมูลลูกค้าและสินค้า
            customer_data = self.db.get_customer_by_id(contract_data['customer_id'])
            product_data = self.db.get_product_by_id(contract_data['product_id'])
            
            if not customer_data or not product_data:
                raise ValueError("ไม่พบข้อมูลลูกค้าหรือสินค้า")
            
            # กำหนดชื่อไฟล์
            if not output_path:
                filename = f"ใบขายฝาก_{contract_data['contract_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                if ask_folder:
                    # ให้ผู้ใช้เลือกโฟลเดอร์
                    selected_folder = self.select_save_folder("เลือกโฟลเดอร์สำหรับจัดเก็บใบขายฝาก")
                    if not selected_folder:
                        print("ยกเลิกการสร้าง PDF")
                        return None
                    output_path = os.path.join(selected_folder, filename)
                else:
                    output_path = os.path.join(os.getcwd(), filename)
            
            # สร้าง PDF
            self._create_pdf(contract_data, customer_data, product_data, output_path)
            
            # ส่งสัญญาณ
            self.pdf_generated.emit(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการสร้าง PDF: {e}")
            return None
    
    def generate_pdf_from_data(self, contract_data: Dict, customer_data: Dict, product_data: Dict, output_path: str = None) -> Optional[str]:
        """
        สร้างใบขายฝาก PDF จากข้อมูลที่ส่งมาโดยตรง
        
        Args:
            contract_data: ข้อมูลสัญญา
            customer_data: ข้อมูลลูกค้า
            product_data: ข้อมูลสินค้า
            output_path: เส้นทางไฟล์ที่จะบันทึก (ถ้าไม่ระบุจะให้เลือกเอง)
        
        Returns:
            เส้นทางไฟล์ที่บันทึก หรือ None ถ้าเกิดข้อผิดพลาด
        """
        try:
            # ตรวจสอบข้อมูลที่จำเป็น
            if not contract_data or not customer_data or not product_data:
                raise ValueError("ข้อมูลไม่ครบถ้วน")
            
            # กำหนดชื่อไฟล์
            if not output_path:
                filename = f"ใบขายฝาก_{contract_data.get('contract_number', 'temp')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                output_path = os.path.join(os.getcwd(), filename)
            
            # สร้าง PDF
            self._create_pdf(contract_data, customer_data, product_data, output_path)
            
            # ส่งสัญญาณ
            self.pdf_generated.emit(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการสร้าง PDF: {e}")
            return None
    
    def _create_pdf(self, contract_data: Dict, customer_data: Dict, product_data: Dict, output_path: str):
        """สร้างไฟล์ PDF"""
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # เริ่มต้นที่ตำแหน่งบนสุด (เพิ่ม margin)
        y_pos = height - 80
        
        # --- ส่วนหัว ---
        self._draw_header(c, width, height, y_pos)
        y_pos -= 150
        
        # --- ข้อมูลสัญญา ---
        y_pos = self._draw_contract_info(c, contract_data, width, y_pos)
        y_pos -= 30
        
        # --- ข้อมูลลูกค้า ---
        y_pos = self._draw_customer_info(c, customer_data, width, y_pos)
        y_pos -= 25
        
        # --- ข้อมูลสินค้า ---
        y_pos = self._draw_product_info(c, product_data, contract_data, width, y_pos)
        y_pos -= 25
        
        # --- เงื่อนไขและข้อตกลง ---
        y_pos = self._draw_terms_and_conditions(c, width, y_pos)
        y_pos -= 15
        
        # --- หมายเหตุ ---
        y_pos = self._draw_notes(c, width, y_pos)
        y_pos -= 15
        
        # --- ข้อมูลการไถ่คืน ---
        y_pos = self._draw_redemption_info(c, contract_data, width, y_pos)
        y_pos -= 60
        
        # --- ลายเซ็น ---
        self._draw_signatures(c, customer_data, width, y_pos)
        
        # บันทึกไฟล์
        c.save()
    
    def _draw_header(self, c: canvas.Canvas, width: float, height: float, y_pos: float):
        """วาดส่วนหัวเอกสาร"""
        # หัวข้อหลัก
        c.setFont("NotoSansThai-Bold", 26)  # ลดจาก 28pt
        c.drawCentredString(width / 2.0, y_pos, "ใบขายฝาก")
        
        # ชื่อร้าน - โหลดจาก shop_config.json
        from shop_config_loader import load_shop_config
        shop_config = load_shop_config()
        
        c.setFont("NotoSansThai-Bold", 16)  # ลดจาก 18pt
        c.drawCentredString(width / 2.0, y_pos - 35, f"{shop_config['name']} ({shop_config['branch']})")
        
        # ที่อยู่ร้าน
        c.setFont("NotoSansThai", 14)  # ลดจาก 16pt
        c.drawCentredString(width / 2.0, y_pos - 55, shop_config['address'])
    
    def _draw_contract_info(self, c: canvas.Canvas, contract_data: Dict, width: float, y_pos: float) -> float:
        """วาดข้อมูลสัญญา"""
        left_margin = 60
        right_margin = width - 60
        
        c.setFont("NotoSansThai", 14)  # ลดจาก 16pt
        c.drawString(left_margin, y_pos, f"สัญญาเลขที่: {contract_data['contract_number']}")
        
        # แปลงวันที่
        start_date = datetime.strptime(contract_data['start_date'], '%Y-%m-%d')
        formatted_start_date = start_date.strftime('%d %B %Y')
        c.drawRightString(right_margin, y_pos, f"วันที่: {formatted_start_date}")
        
        return y_pos - 35
    
    def _draw_customer_info(self, c: canvas.Canvas, customer_data: Dict, width: float, y_pos: float) -> float:
        """วาดข้อมูลลูกค้า"""
        left_margin = 60
        
        c.setFont("NotoSansThai-Bold", 14)  # ลดจาก 16pt
        c.drawString(left_margin, y_pos, "ข้อมูลผู้ขายฝาก:")
        y_pos -= 20
        
        c.setFont("NotoSansThai", 14)  # ลดจาก 16pt
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}"
        c.drawString(left_margin + 15, y_pos, f"ชื่อ: {customer_name}")
        y_pos -= 20
        
        if customer_data.get('phone'):
            c.drawString(left_margin + 15, y_pos, f"โทรศัพท์: {customer_data['phone']}")
            y_pos -= 20
        
        # ที่อยู่
        address_parts = [
            customer_data.get('house_number', ''),
            customer_data.get('street', ''),
            customer_data.get('subdistrict', ''),
            customer_data.get('district', ''),
            customer_data.get('province', '')
        ]
        address = ' '.join(filter(None, address_parts))
        if address:
            c.drawString(left_margin + 15, y_pos, f"ที่อยู่: {address}")
            y_pos -= 20
        
        if customer_data.get('id_card'):
            c.drawString(left_margin + 15, y_pos, f"บัตรประชาชนเลขที่: {customer_data['id_card']}")
            y_pos -= 20
        
        return y_pos
    
    def _draw_product_info(self, c: canvas.Canvas, product_data: Dict, contract_data: Dict, width: float, y_pos: float) -> float:
        """วาดข้อมูลสินค้า"""
        left_margin = 60
        right_margin = width - 60
        
        # เส้นคั่น
        c.line(left_margin, y_pos, right_margin, y_pos)
        y_pos -= 20
        
        c.setFont("NotoSansThai-Bold", 14)  # ลดจาก 16pt
        c.drawString(left_margin, y_pos, "รายการทรัพย์สินที่ขายฝาก:")
        y_pos -= 20
        
        c.setFont("NotoSansThai", 14)  # ลดจาก 16pt
        
        # ชื่อสินค้า
        product_name = product_data.get('model', '') or product_data.get('name', '')
        if product_data.get('brand'):
            product_name += f" {product_data['brand']}"
        c.drawString(left_margin + 15, y_pos, f"ทรัพย์สิน: {product_name}")
        y_pos -= 20
        
        # ยอดฝาก
        pawn_amount = contract_data['pawn_amount']
        c.drawString(left_margin + 15, y_pos, f"ขายฝากไว้เป็นจำนวนเงิน: {pawn_amount:,.2f} บาท")
        y_pos -= 20
        
        
        return y_pos
    
    def _draw_terms_and_conditions(self, c: canvas.Canvas, width: float, y_pos: float) -> float:
        """วาดเงื่อนไขและข้อตกลง"""
        left_margin = 60  # เพิ่มขอบซ้าย
        right_margin = width - 60  # เพิ่มขอบขวา
        
        # เส้นคั่น
        c.line(left_margin, y_pos, right_margin, y_pos)
        y_pos -= 20
        
        c.setFont("NotoSansThai-Bold", 16)
        c.drawString(left_margin, y_pos, "เงื่อนไขและข้อตกลง:")
        y_pos -= 15
        
        # ข้อ 1 - ตัวใหญ่ขึ้นและตัวหนา
        c.setFont("NotoSansThai-Bold", 16)  # ลดจาก 18pt
        term1 = "1. ข้าพเจ้าขอรับรองว่าสินค้าที่นำมาขายฝากเป็นกรรมสิทธิ์ของผู้ขายฝากอย่างแท้จริง ไม่มีการติดค้างชำระ"
        c.drawString(left_margin + 15, y_pos, term1)
        y_pos -= 18
        
        term1a = "    หรืออยู่ระหว่างผ่อนชำระ และไม่เกี่ยวกับการกระทำผิดกฏหมายใดๆ และมิได้ได้มาโดยการลักทรัพย์"
        c.drawString(left_margin + 15, y_pos, term1a)
        y_pos -= 18
        
        term1b = "    ฉ้อโกง วิ่งราว กรรโชกทรัพย์ รีดทรัพย์ หรือโกงเจ้าหนี้แต่ประการใด"
        c.drawString(left_margin + 15, y_pos, term1b)
        y_pos -= 20
        
        # ข้อ 2 - ตัวใหญ่ขึ้นและตัวหนา
        c.setFont("NotoSansThai-Bold", 16)  # ลดจาก 18pt
        c.drawString(left_margin + 15, y_pos, term2)
        y_pos -= 18
        
        term2a = "    เหนือทรัพย์สินที่ได้ขายฝาก เพราะความผิดของผู้ขายฝาก ผู้ขายฝากจำต้องรับผิดชดใช้ค่าสินค้า"
        c.drawString(left_margin + 15, y_pos, term2a)
        y_pos -= 18
        
        term2b = "    และความเสียหายอื่นๆ (ถ้ามี) แก่ผู้ซื้อ"
        c.drawString(left_margin + 15, y_pos, term2b)
        y_pos -= 20
        
        # ข้อ 3 - ตัวเล็กเท่าเดิม
        c.setFont("NotoSansThai", 14)  # ลดจาก 16pt
        term3 = "3. ข้าพเจ้าผู้ขายฝากได้อ่านเงื่อนไขที่กำหนดไว้ ได้รับทราบและเข้าใจถี่ถ้วน และตกลงทำตาม"
        c.drawString(left_margin + 15, y_pos, term3)
        y_pos -= 18
        
        term3a = "    เงื่อนไขในเอกสารนี้ทุกประการ พร้อมได้รับเงินถูกต้องตามจำนวนแล้ว จึงลงลายมือชื่อไว้เป็นหลักฐาน"
        c.drawString(left_margin + 15, y_pos, term3a)
        y_pos -= 20
        
        return y_pos
    
    def _draw_notes(self, c: canvas.Canvas, width: float, y_pos: float) -> float:
        """วาดหมายเหตุ"""
        left_margin = 60
        
        c.setFont("NotoSansThai-Bold", 12)
        c.drawString(left_margin, y_pos, "หมายเหตุ:")
        y_pos -= 15
        
        c.setFont("NotoSansThai", 16)
        
        notes = [
            "กรณีสินค้าหายหรือสูญหายซึ่งพิสูจน์ได้ว่าถูกโจรกรรม หรือเนื่องจากภัยธรรมชาติ",
            "ทางร้านไม่ต้องชดใช้หรือรับผิดชอบใดๆทั้งสิ้น",
            "",
            "หากเกินกำหนดเวลาไถ่คืน ถือว่าท่านสละสิทธิ์ในทรัพย์สินนี้ให้ตกเป็นของทางร้านโดยสมบูรณ์"
        ]
        
        for note in notes:
            if note.strip():
                c.drawString(left_margin + 30, y_pos, note)
            y_pos -= 16
        
        return y_pos
    
    def _draw_redemption_info(self, c: canvas.Canvas, contract_data: Dict, width: float, y_pos: float) -> float:
        """วาดข้อมูลการไถ่คืน"""
        left_margin = 60
        
        c.setFont("NotoSansThai-Bold", 16)  # ลดจาก 18pt
        total_redemption = contract_data['total_redemption']
        c.drawString(left_margin, y_pos, f"ยอดไถ่คืน: {total_redemption:,.2f} บาท")
        y_pos -= 25
        
        # แปลงวันที่สิ้นสุด
        end_date = datetime.strptime(contract_data['end_date'], '%Y-%m-%d')
        formatted_end_date = end_date.strftime('%d %B %Y')
        c.drawString(left_margin, y_pos, f"กำหนดไถ่ทรัพย์สินภายในวันที่: {formatted_end_date}")
        
        return y_pos
    
    def _draw_signatures(self, c: canvas.Canvas, customer_data: Dict, width: float, y_pos: float):
        """วาดส่วนลายเซ็น"""
        left_margin = 60
        
        c.setFont("NotoSansThai", 14)  # ลดจาก 16pt
        
        # ลายเซ็นผู้รับฝาก
        c.drawString(left_margin + 30, y_pos, "ลงชื่อ _________________________ ผู้รับฝาก")
        
        # ลายเซ็นผู้ขายฝาก
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}"
        c.drawString(width - 280, y_pos, "ลงชื่อ _________________________ ผู้ขายฝาก")
        
        # ชื่อผู้ขายฝาก
        y_pos -= 25
        c.drawString(width - 230, y_pos, f"( {customer_name} )")
        
        # Note: ReportLab doesn't easily support underline text, 
        # so prices in terms are already bold to emphasize them
    
    def select_save_location(self, contract_number: str) -> Optional[str]:
        """ให้ผู้ใช้เลือกตำแหน่งที่จะบันทึกไฟล์"""
        filename = f"ใบขายฝาก_{contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "บันทึกใบขายฝาก",
            filename,
            "PDF Files (*.pdf)"
        )
        
        return file_path if file_path else None

    def select_save_folder(self, title: str) -> Optional[str]:
        """ให้ผู้ใช้เลือกโฟลเดอร์"""
        folder_path = QFileDialog.getExistingDirectory(
            None,
            title,
            os.path.expanduser("~") # เริ่มจากโฟลเดอร์ที่ผู้ใช้ตั้งไว้
        )
        return folder_path if folder_path else None


# ฟังก์ชันสำหรับใช้งานจากภายนอก
def generate_contract_pdf(contract_id: int, output_path: str = None, ask_folder: bool = False) -> Optional[str]:
    """
    ฟังก์ชันสำหรับสร้างใบขายฝาก PDF
    
    Args:
        contract_id: ID ของสัญญา
        output_path: เส้นทางไฟล์ที่จะบันทึก (ถ้าไม่ระบุจะให้เลือกเอง)
        ask_folder: ถ้าเป็น True จะแสดง dialog เลือกโฟลเดอร์
    
    Returns:
        เส้นทางไฟล์ที่บันทึก หรือ None ถ้าเกิดข้อผิดพลาด
    """
    try:
        generator = ContractPDFGenerator()
        return generator.generate_contract_pdf(contract_id, output_path, ask_folder)
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None


if __name__ == "__main__":
    # ทดสอบการสร้าง PDF
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # ตัวอย่างการใช้งาน
    contract_id = 1  # เปลี่ยนเป็น ID สัญญาที่ต้องการ
    result = generate_contract_pdf(contract_id)
    
    if result:
        print(f"สร้าง PDF สำเร็จ: {result}")
    else:
        print("เกิดข้อผิดพลาดในการสร้าง PDF")
    
    sys.exit(app.exec())
