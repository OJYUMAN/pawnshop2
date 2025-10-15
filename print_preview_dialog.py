# -*- coding: utf-8 -*-
"""
ระบบพรีวิวและเลือกเครื่องปริ้นสำหรับสัญญาฝากขายและสัญญาไถ่คืน
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QGroupBox, QRadioButton, QButtonGroup, QMessageBox,
    QFileDialog, QSpacerItem, QSizePolicy, QFrame, QScrollArea, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
import tempfile
import os
import subprocess
import platform

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
    QT_PDF_AVAILABLE = True
except ImportError:
    QPdfDocument = None
    QPdfView = None
    QT_PDF_AVAILABLE = False

# เปิดใช้งาน Qt PDF สำหรับการพรีวิวภายในแอป
QT_PDF_AVAILABLE = True


class PrintPreviewDialog(QDialog):
    """หน้าตาพรีวิวและเลือกเครื่องปริ้น"""
    
    def __init__(self, parent=None, contract_type="pawn", 
                 pdf_generator_func=None,
                 contract_data=None,
                 customer_data=None,
                 product_data=None,
                 shop_data=None):
        super().__init__(parent)
        
        self.contract_type = contract_type  # "pawn" หรือ "redemption"
        self.pdf_generator_func = pdf_generator_func
        self.contract_data = contract_data or {}
        self.customer_data = customer_data or {}
        self.product_data = product_data or {}
        self.shop_data = shop_data or {}
        
        self.temp_pdf_path = None
        self.printers = []
        
        title = "พรีวิวและเลือกการปริ้น - " + ("สัญญาฝากขาย" if contract_type == 'pawn' else "สัญญาไถ่คืน")
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(1000, 700)
        
        self.setup_ui()
        self.load_printers()
        self.generate_preview()
    
    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout(self)
        
        # หัวเรื่อง
        title_text = "พรีวิวเอกสาร" + ("สัญญาฝากขาย" if self.contract_type == 'pawn' else "สัญญาไถ่คืน")
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # พื้นที่พรีวิว
        preview_group = QGroupBox("ตัวอย่างเอกสาร")
        preview_layout = QVBoxLayout(preview_group)
        
        # พื้นที่แสดงพรีวิว
        self.preview_area = QScrollArea()
        self.preview_area.setWidgetResizable(True)
        self.preview_area.setMinimumHeight(400)
        self.preview_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background: #ffffff;
            }
        """)
        
        self.preview_label = QLabel("กำลังสร้างตัวอย่างเอกสาร...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 20px;
            }
        """)
        
        self.preview_area.setWidget(self.preview_label)
        preview_layout.addWidget(self.preview_area)
        layout.addWidget(preview_group)
        
        # ตัวเลือกการปริ้น
        print_group = QGroupBox("ตัวเลือกการปริ้น")
        print_layout = QVBoxLayout(print_group)
        
        # กลุ่มตัวเลือก
        self.print_option_group = QButtonGroup()
        
        # ปริ้นกับเครื่องปริ้น
        self.print_radio = QRadioButton("ปริ้นกับเครื่องปริ้น")
        self.print_radio.setChecked(True)
        self.print_option_group.addButton(self.print_radio, 0)
        print_layout.addWidget(self.print_radio)
        
        # เลือกเครื่องปริ้น
        printer_layout = QHBoxLayout()
        printer_layout.addWidget(QLabel("เลือกเครื่องปริ้น:"))
        self.printer_combo = QComboBox()
        self.printer_combo.setMinimumWidth(200)
        printer_layout.addWidget(self.printer_combo)
        printer_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        print_layout.addLayout(printer_layout)
        
        # บันทึกเป็น PDF
        self.pdf_radio = QRadioButton("บันทึกเป็นไฟล์ PDF")
        self.print_option_group.addButton(self.pdf_radio, 1)
        print_layout.addWidget(self.pdf_radio)
        
        # เลือกตำแหน่งไฟล์ PDF
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(QLabel("ตำแหน่งไฟล์:"))
        self.pdf_path_edit = QLineEdit()
        self.pdf_path_edit.setPlaceholderText("เลือกตำแหน่งบันทึกไฟล์ PDF...")
        pdf_layout.addWidget(self.pdf_path_edit)
        self.browse_btn = QPushButton("เลือก...")
        self.browse_btn.clicked.connect(self.browse_pdf_location)
        pdf_layout.addWidget(self.browse_btn)
        print_layout.addLayout(pdf_layout)
        
        layout.addWidget(print_group)
        
        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.refresh_btn = QPushButton("รีเฟรชตัวอย่าง")
        self.refresh_btn.clicked.connect(self.generate_preview)
        button_layout.addWidget(self.refresh_btn)
        
        self.print_btn = QPushButton("ปริ้น/บันทึก")
        self.print_btn.clicked.connect(self.execute_print)
        self.print_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        button_layout.addWidget(self.print_btn)
        
        self.cancel_btn = QPushButton("ยกเลิก")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_printers(self):
        """โหลดรายการเครื่องปริ้น"""
        try:
            if platform.system() == "Windows":
                # ใช้ wmic เพื่อดึงรายการเครื่องปริ้น
                result = subprocess.run(['wmic', 'printer', 'get', 'name'], 
                                      capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # ข้าม header
                        printer_name = line.strip()
                        if printer_name:
                            self.printers.append(printer_name)
                            self.printer_combo.addItem(printer_name)
            elif platform.system() == "Darwin":  # macOS
                # ใช้ lpstat เพื่อดึงรายการเครื่องปริ้น
                result = subprocess.run(['lpstat', '-p'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.startswith('printer '):
                            printer_name = line.split()[1]
                            self.printers.append(printer_name)
                            self.printer_combo.addItem(printer_name)
            else:  # Linux
                result = subprocess.run(['lpstat', '-p'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.startswith('printer '):
                            printer_name = line.split()[1]
                            self.printers.append(printer_name)
                            self.printer_combo.addItem(printer_name)
            
            if not self.printers:
                self.printer_combo.addItem("ไม่พบเครื่องปริ้น")
                self.print_radio.setEnabled(False)
                
        except Exception as e:
            print("ไม่สามารถโหลดรายการเครื่องปริ้น: " + str(e))
            self.printer_combo.addItem("ไม่สามารถโหลดรายการเครื่องปริ้น")
            self.print_radio.setEnabled(False)
    
    def generate_preview(self):
        """สร้างตัวอย่างเอกสาร"""
        try:
            self.preview_label.setText("กำลังสร้างตัวอย่างเอกสาร...")
            self.print_btn.setEnabled(False)
            
            # สร้างไฟล์ PDF ชั่วคราว
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            self.temp_pdf_path = temp_file.name
            temp_file.close()
            
            # เรียกใช้ฟังก์ชันสร้าง PDF
            result = None
            if self.pdf_generator_func:
                # ใช้ฟังก์ชันที่ส่งมาจากแอปหลัก
                if self.contract_type == "pawn":
                    result = self.pdf_generator_func(
                        contract_data=self.contract_data,
                        customer_data=self.customer_data,
                        product_data=self.product_data,
                        shop_data=self.shop_data,
                        output_file=self.temp_pdf_path
                    )
                else:
                    result = self.pdf_generator_func(
                        redemption_data=self.contract_data,
                        customer_data=self.customer_data,
                        product_data=self.product_data,
                        original_contract_data=self.contract_data,
                        shop_data=self.shop_data,
                        output_file=self.temp_pdf_path
                    )
            else:
                # ใช้ฟังก์ชันเริ่มต้นถ้าไม่มี pdf_generator_func
                if self.contract_type == "pawn":
                    # สร้างสัญญาฝากขาย
                    from pdf import generate_pawn_ticket_from_data as generate_pawn_contract_pdf
                    result = generate_pawn_contract_pdf(
                        contract_data=self.contract_data,
                        customer_data=self.customer_data,
                        product_data=self.product_data,
                        shop_data=self.shop_data,
                        output_file=self.temp_pdf_path
                    )
                else:
                    # สร้างสัญญาไถ่คืน
                    from pdf3 import generate_redemption_contract_pdf
                    result = generate_redemption_contract_pdf(
                        redemption_data=self.contract_data,
                        customer_data=self.customer_data,
                        product_data=self.product_data,
                        original_contract_data=self.contract_data,
                        shop_data=self.shop_data,
                        output_file=self.temp_pdf_path
                    )
                
                # ตรวจสอบว่าการสร้าง PDF สำเร็จหรือไม่
                if not result or result == "":
                    raise Exception("การสร้างไฟล์ PDF ล้มเหลว - ไม่สามารถสร้างไฟล์ได้")
                
                # ตรวจสอบว่าไฟล์มีเนื้อหาหรือไม่
                if not os.path.exists(self.temp_pdf_path) or os.path.getsize(self.temp_pdf_path) == 0:
                    raise Exception("ไฟล์ PDF ที่สร้างขึ้นว่างเปล่า - ตรวจสอบข้อมูลและลองใหม่")
            
            # แสดงตัวอย่าง
            self.show_preview()
            
        except Exception as e:
            self.preview_label.setText("เกิดข้อผิดพลาดในการสร้างตัวอย่าง: " + str(e))
            print("Error generating preview: " + str(e))
        finally:
            self.print_btn.setEnabled(True)
    
    def show_preview(self):
        """แสดงตัวอย่างเอกสาร"""
        if not self.temp_pdf_path or not os.path.exists(self.temp_pdf_path):
            self.preview_label.setText("ไม่สามารถสร้างตัวอย่างเอกสารได้")
            return
        
        try:
            if QT_PDF_AVAILABLE and QPdfDocument and QPdfView:
                # ใช้ Qt PDF Viewer ภายในแอป
                self.setup_pdf_viewer()
            else:
                # เปิดไฟล์ PDF ด้วยโปรแกรมภายนอก
                if platform.system() == "Windows":
                    os.startfile(self.temp_pdf_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", self.temp_pdf_path])
                else:
                    subprocess.Popen(["xdg-open", self.temp_pdf_path])
                
                self.preview_label.setText("ตัวอย่างเอกสารถูกเปิดในโปรแกรมอ่าน PDF แล้ว\nกรุณาตรวจสอบเอกสารก่อนดำเนินการต่อ")
            
        except Exception as e:
            self.preview_label.setText("ไม่สามารถเปิดตัวอย่างเอกสารได้: " + str(e))
    
    def setup_pdf_viewer(self):
        """ตั้งค่า PDF Viewer ภายในแอป"""
        try:
            # สร้าง PDF Document
            self.pdf_document = QPdfDocument()
            
            # โหลดไฟล์ PDF
            if not self.pdf_document.load(self.temp_pdf_path):
                self.preview_label.setText("ไม่สามารถโหลดไฟล์ PDF ได้")
                return
            
            # สร้าง PDF View
            self.pdf_view = QPdfView()
            self.pdf_view.setDocument(self.pdf_document)
            
            # ลบ label เดิมและเพิ่ม PDF view
            self.preview_area.takeWidget()
            self.preview_area.setWidget(self.pdf_view)
            
            # ตั้งค่าการแสดงผล
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
            
            print("PDF viewer setup successfully")
            
        except Exception as e:
            print(f"Error setting up PDF viewer: {e}")
            self.preview_label.setText("ไม่สามารถแสดงพรีวิว PDF ได้: " + str(e))
    
    def browse_pdf_location(self):
        """เลือกตำแหน่งบันทึกไฟล์ PDF"""
        contract_type_name = "pawn_contract" if self.contract_type == 'pawn' else "redemption_contract"
        contract_number = self.contract_data.get('contract_number', 'unknown')
        default_filename = contract_type_name + "_" + contract_number + ".pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "เลือกตำแหน่งบันทึกไฟล์ PDF",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            self.pdf_path_edit.setText(file_path)
    
    def execute_print(self):
        """ดำเนินการปริ้นหรือบันทึก PDF"""
        try:
            if not self.temp_pdf_path or not os.path.exists(self.temp_pdf_path):
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบไฟล์เอกสารที่จะปริ้น")
                return
            
            if self.print_radio.isChecked():
                # ปริ้นกับเครื่องปริ้น
                printer_name = self.printer_combo.currentText()
                if not printer_name or printer_name == "ไม่พบเครื่องปริ้น":
                    QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกเครื่องปริ้น")
                    return
                
                self.print_to_printer(printer_name)
                
            else:
                # บันทึกเป็น PDF
                pdf_path = self.pdf_path_edit.text().strip()
                if not pdf_path:
                    QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกตำแหน่งบันทึกไฟล์ PDF")
                    return
                
                self.save_as_pdf(pdf_path)
            
            QMessageBox.information(self, "สำเร็จ", "ดำเนินการเสร็จสิ้น")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: " + str(e))
    
    def print_to_printer(self, printer_name):
        """ปริ้นกับเครื่องปริ้น"""
        try:
            if platform.system() == "Windows":
                # ใช้ lpr หรือ copy command
                subprocess.run(['copy', '/B', self.temp_pdf_path, '\\\\' + printer_name], check=True)
            else:
                # ใช้ lpr command
                subprocess.run(['lpr', '-P', printer_name, self.temp_pdf_path], check=True)
                
        except subprocess.CalledProcessError as e:
            raise Exception("ไม่สามารถปริ้นได้: " + str(e))
    
    def save_as_pdf(self, output_path):
        """บันทึกเป็นไฟล์ PDF"""
        try:
            import shutil
            shutil.copy2(self.temp_pdf_path, output_path)
        except Exception as e:
            raise Exception("ไม่สามารถบันทึกไฟล์ได้: " + str(e))
    
    def cleanup(self):
        """ลบไฟล์ชั่วคราว"""
        # ปิด PDF document
        if hasattr(self, 'pdf_document') and self.pdf_document:
            self.pdf_document.close()
        
        # ลบไฟล์ชั่วคราว
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try:
                os.unlink(self.temp_pdf_path)
            except:
                pass
    
    def closeEvent(self, event):
        """เมื่อปิดหน้าต่าง"""
        self.cleanup()
        event.accept()


# ฟังก์ชันช่วยสำหรับการเรียกใช้
def show_print_preview(parent, contract_type, pdf_generator_func,
                      contract_data, customer_data, 
                      product_data, shop_data=None):
    """
    แสดงหน้าตาพรีวิวและเลือกการปริ้น
    
    Args:
        parent: parent widget
        contract_type: "pawn" หรือ "redemption"
        pdf_generator_func: ฟังก์ชันสร้าง PDF
        contract_data: ข้อมูลสัญญา
        customer_data: ข้อมูลลูกค้า
        product_data: ข้อมูลสินค้า
        shop_data: ข้อมูลร้าน (optional)
    
    Returns:
        bool: True ถ้าผู้ใช้เลือกปริ้น/บันทึก, False ถ้ายกเลิก
    """
    dialog = PrintPreviewDialog(
        parent=parent,
        contract_type=contract_type,
        pdf_generator_func=pdf_generator_func,
        contract_data=contract_data,
        customer_data=customer_data,
        product_data=product_data,
        shop_data=shop_data
    )
    
    result = dialog.exec_()
    dialog.cleanup()
    return result == QDialog.Accepted
