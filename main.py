import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QToolBar,
    QMenuBar, QMessageBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit,
    QScrollArea, QFrame, QFileDialog, QDialog, QProgressDialog, QInputDialog
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PySide6.QtGui import QIcon, QAction, QPixmap, QPalette, QColor
from PySide6.QtCore import Qt, QSize, QDate
from datetime import datetime, timedelta
import requests
import json
from database import PawnShopDatabase
from utils import PawnShopUtils
from dialogs import CustomerDialog, ProductDialog, InterestPaymentDialog, RedemptionDialog, RenewalDialog
from data_viewer import DataViewerDialog
from customer_search import CustomerSearchDialog
from product_search import ProductSearchDialog
from fee_management import FeeManagementDialog
from line_config import LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID, ENABLE_LINE_NOTIFICATION, SEND_CONTRACT_NOTIFICATION, SEND_DAILY_INCOME_NOTIFICATION, MESSAGE_TEMPLATE, SEND_FORFEITURE_NOTIFICATION
import tempfile
import shutil
from app_services import (
    send_line_message as svc_send_line_message,
    open_pdf_external as svc_open_pdf_external,
    copy_product_image as svc_copy_product_image,
)
from language_manager import language_manager

# Icon mapping for toolbar buttons
ICON_MAP = {
    "document-new":        "icons/file-plus.svg",             # แผ่นกระดาษ + +
    "edit-clear":          "icons/eraser.svg",                # ยางลบ / ถังขยะเล็ก
    "document-save":       "icons/content-save-all.svg",      # แฟล๊ปปี้ดิสก์
    "document-export":     "icons/file-pdf-box.svg",          # เอกสาร + โลโก้ PDF/ลูกศรออก
    "view-refresh":        "icons/refresh.svg",               # ปฏิทิน + ลูกศรหมุน/รีเฟรช
    "go-previous":         "icons/cash-refund.svg",           # มือรับเหรียญ/เช็คถูก
    "folder-open":         "icons/folder-open.svg",           # โฟลเดอร์ + แว่นขยาย
    "document-properties": "icons/history.svg",               # เอกสาร + นาฬิกา/ไทม์ไลน์
    "x-office-calendar":   "icons/calendar-today.svg",        # ปฏิทิน + กราฟแท่ง
    "preferences-system":  "icons/cog.svg",                   # เหรียญ + เฟือง
    "smartcard":           "icons/card-account-details.svg",  # บัตรประชาชนมีรูปคน
}

class PawnShopUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = PawnShopDatabase()
        self.current_customer = None
        self.current_product = None
        self.current_contract = None
        
        self.setWindowTitle("Pawnshop Management System")
        self.setGeometry(100, 100, 1600, 900)

        # Apply modern styles for better UI appearance
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                font-size: 11px;
            }
            QMainWindow {
                background-color: #F8F9FA;
            }
            QGroupBox {
                margin-top: 15px;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                font-weight: bold;
                color: #495057;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                margin-left: 15px;
                background-color: #F8F9FA;
                color: #495057;
            }
            #TopLeftGroup {
                background-color: #E8F5E8;
                border-color: #28A745;
            }
            #TopMiddleGroup {
                background-color: #FFF3CD;
                border-color: #FFC107;
            }
            #SearchGroup {
                background-color: #D1ECF1;
                border-color: #17A2B8;
            }
            #TabWidget, #TabWidget > QWidget > QWidget{
                background-color: #F8F9FA;
            }
            QTabBar::tab {
                background: #E9ECEF;
                padding: 8px 16px;
                border: 1px solid #DEE2E6;
                border-bottom: none;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
                color: #495057;
            }
            QTabBar::tab:selected {
                background: #007BFF;
                color: white;
                border-color: #007BFF;
            }
            QTabBar::tab:hover {
                background: #6C757D;
                color: white;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #DEE2E6;
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                alternate-background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #DEE2E6;
                font-weight: bold;
                color: #495057;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                min-height: 32px;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QToolButton {
                background-color: #FFFFFF;
                color: #424242;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin: 2px;
                padding: 6px;
                font-weight: 500;
                min-width: 60px;
                min-height: 40px;
            }
            QToolButton:hover {
                background-color: #F5F5F5;
                border-color: #BDBDBD;
            }
            QToolButton:pressed {
                background-color: #E3F2FD;
                border-color: #2196F3;
            }
            QToolButton:checked {
                background-color: #E8F5E8;
                border-color: #4CAF50;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #DEE2E6;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007BFF;
            }
            QDateEdit {
                padding: 8px;
                border: 2px solid #DEE2E6;
                border-radius: 4px;
                background-color: white;
                background: white;
            }
            QDateEdit:focus {
                border-color: #007BFF;
            }
            QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #DEE2E6;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #007BFF;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #DEE2E6;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #007BFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #495057;
                margin-right: 5px;
            }
            QToolBar {
                background-color: #FAFAFA;
                border-top: 1px solid #E0E0E0;
                spacing: 8px;
                padding: 8px;
            }
            QToolBar::separator {
                background-color: #E0E0E0;
                width: 1px;
                margin: 4px;
            }
        """)


        # --- Main Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างส่วนต่างๆ
        main_layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ

        # --- Main Content Area ---
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างส่วนซ้ายและขวา
        content_layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ
        
        # Left side - Customer and Product info (50% of screen)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Right side - Contract info, Results, Search (50% of screen)
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addWidget(content_widget)

        # --- Bottom Toolbar ---
        self.create_bottom_toolbar()

        # --- Initialize UI ---
        self.initialize_ui()

    def initialize_ui(self):
        """เริ่มต้น UI"""
        # ไม่แสดงข้อมูลใดๆ เมื่อเริ่มต้น
        self.clear_form()
        
        # ตั้งค่าวันที่เริ่มต้น
        self.start_date_edit.setDate(QDate.currentDate())
        
        # โหลดการตั้งค่า
        self.load_settings()

    def load_settings(self):
        """โหลดการตั้งค่า"""
        try:
            default_interest_rate = float(self.db.get_setting('default_interest_rate'))
            default_days = int(self.db.get_setting('default_contract_days'))
            default_withholding_tax_rate = float(self.db.get_setting('default_withholding_tax_rate'))
            
            self.interest_rate_spin.setValue(default_interest_rate)
            self.days_spin.setValue(default_days)
            self.withholding_tax_rate_spin.setValue(default_withholding_tax_rate)
        except:
            # ใช้ค่าเริ่มต้นถ้าไม่มีการตั้งค่า
            self.interest_rate_spin.setValue(3.0)
            self.days_spin.setValue(30)
            self.withholding_tax_rate_spin.setValue(3.0)

    def send_contract_to_line(self, contract_data, customer_data, product_data):
        """ส่งข้อมูลสัญญาเข้า Line"""
        if not ENABLE_LINE_NOTIFICATION or not SEND_CONTRACT_NOTIFICATION:
            return
            
        try:
            # เตรียมข้อมูลสำหรับส่งเข้า Line
            customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
            customer_phone = customer_data.get('phone', 'ไม่ระบุ')
            customer_id_card = customer_data.get('id_card', 'ไม่ระบุ')
            
            product_name = product_data.get('name', 'ไม่ระบุ')
            product_brand = product_data.get('brand', 'ไม่ระบุ')
            product_size = product_data.get('size', 'ไม่ระบุ')
            product_serial = product_data.get('serial_number', 'ไม่ระบุ')
            
            # ใช้ template จาก config
            line_message = MESSAGE_TEMPLATE['contract_new'].format(
                contract_number=contract_data['contract_number'],
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_id_card=customer_id_card,
                product_name=product_name,
                product_brand=product_brand,
                product_size=product_size,
                product_serial=product_serial,
                pawn_amount=contract_data['pawn_amount'],
                start_date=contract_data['start_date'],
                end_date=contract_data['end_date'],
                days_count=contract_data['days_count'],
                interest_rate=contract_data['interest_rate'],
                fee_amount=contract_data['fee_amount'],
                withholding_tax_amount=contract_data['withholding_tax_amount'],
                total_paid=contract_data['total_paid'],
                total_redemption=contract_data['total_redemption'],
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # ส่งข้อความเข้า Line
            success = self.send_line_message(line_message)
            
            if success:
                print("ส่งข้อมูลสัญญาเข้า Line สำเร็จ")
            else:
                print("ส่งข้อมูลสัญญาเข้า Line ไม่สำเร็จ")
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการส่งข้อมูลเข้า Line: {str(e)}")

    def send_line_message(self, message):
        """ส่งข้อความเข้า Line (delegate to app_services)"""
        return svc_send_line_message(message)
    def send_forfeiture_to_line(self, contract_data):
        """ส่งข้อมูลหลุดจำนำเข้า Line"""
        if not ENABLE_LINE_NOTIFICATION or not SEND_FORFEITURE_NOTIFICATION:
            return
        try:
            customer_name = f"{contract_data.get('first_name', '')} {contract_data.get('last_name', '')}".strip() or "-"
            product_name = contract_data.get('product_name', '-') or '-'
            pawn_amount = float(contract_data.get('pawn_amount', 0))
            end_date = contract_data.get('end_date')
            if isinstance(end_date, (datetime,)):
                end_date_txt = end_date.strftime('%d/%m/%Y')
            else:
                end_date_txt = str(end_date)
            line_message = MESSAGE_TEMPLATE.get('forfeiture', "หลุดจำนำ {contract_number}").format(
                contract_number=contract_data.get('contract_number', '-'),
                customer_name=customer_name,
                product_name=product_name,
                pawn_amount=pawn_amount,
                end_date=end_date_txt,
                timestamp=datetime.now().strftime('%d/%m/%Y %H:%M')
            )
            self.send_line_message(line_message)
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการส่งข้อมูลหลุดจำนำเข้า Line: {str(e)}")



    def create_customer_tab(self):
        """สร้างแท็บข้อมูลลูกค้า (รองรับหลายภาษา)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างกลุ่ม
        layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ
        
        # Customer search section
        search_group = QGroupBox()
        self.customer_search_group = search_group
        search_layout = QGridLayout(search_group)
        search_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        search_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        self.lbl_customer_code = QLabel()
        search_layout.addWidget(self.lbl_customer_code, 0, 0)
        self.customer_code_edit = QLineEdit()
        search_layout.addWidget(self.customer_code_edit, 0, 1)
        
        self.customer_search_btn = QPushButton()
        self.customer_search_btn.clicked.connect(self.search_customer)
        self.customer_search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.customer_search_btn.setMinimumHeight(32)
        search_layout.addWidget(self.customer_search_btn, 0, 2)
        
        self.add_customer_btn = QPushButton()
        self.add_customer_btn.clicked.connect(self.toggle_customer_mode)
        self.add_customer_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_customer_btn.setMinimumHeight(32)
        search_layout.addWidget(self.add_customer_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Customer info section
        self.customer_info_group = QGroupBox()
        self.customer_info_layout = QGridLayout(self.customer_info_group)
        self.customer_info_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        self.customer_info_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        # ชื่อลูกค้า
        self.lbl_borrower_name = QLabel()
        self.customer_info_layout.addWidget(self.lbl_borrower_name, 0, 0)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.customer_name_edit, 0, 1)
        
        # ที่อยู่
        self.lbl_address = QLabel()
        self.customer_info_layout.addWidget(self.lbl_address, 1, 0)
        self.customer_address_edit = QLineEdit()
        self.customer_address_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.customer_address_edit, 1, 1)
        
        # เลขบัตรประชาชน
        self.lbl_id_type = QLabel()
        self.customer_info_layout.addWidget(self.lbl_id_type, 2, 0)
        self.id_card_type_combo = QComboBox()
        self.id_card_type_combo.addItems([
            language_manager.get_text("id_card_type_citizen"),
            language_manager.get_text("id_card_type_driver"),
            language_manager.get_text("id_card_type_passport"),
        ])
        self.id_card_type_combo.setEnabled(False)
        self.customer_info_layout.addWidget(self.id_card_type_combo, 2, 1)
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.id_card_edit, 2, 2)
        
        # ที่อยู่บ้าน
        self.lbl_house_no = QLabel()
        self.customer_info_layout.addWidget(self.lbl_house_no, 3, 0)
        self.house_number_edit = QLineEdit()
        self.house_number_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.house_number_edit, 3, 1)
        
        # ซอย/ถนน
        self.lbl_street = QLabel()
        self.customer_info_layout.addWidget(self.lbl_street, 4, 0)
        self.street_edit = QLineEdit()
        self.street_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.street_edit, 4, 1)
        
        # ตำบล
        self.lbl_subdistrict = QLabel()
        self.customer_info_layout.addWidget(self.lbl_subdistrict, 5, 0)
        self.subdistrict_edit = QLineEdit()
        self.subdistrict_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.subdistrict_edit, 5, 1)
        
        # อำเภอ
        self.lbl_district = QLabel()
        self.customer_info_layout.addWidget(self.lbl_district, 6, 0)
        self.district_edit = QLineEdit()
        self.district_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.district_edit, 6, 1)
        
        # จังหวัด
        self.lbl_province = QLabel()
        self.customer_info_layout.addWidget(self.lbl_province, 7, 0)
        self.province_edit = QLineEdit()
        self.province_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.province_edit, 7, 1)
        
        # โทรศัพท์
        self.lbl_phone = QLabel()
        self.customer_info_layout.addWidget(self.lbl_phone, 8, 0)
        self.phone_edit = QLineEdit()
        self.phone_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.phone_edit, 8, 1)
        
        # รายละเอียดอื่นๆ
        self.lbl_other_details = QLabel()
        self.customer_info_layout.addWidget(self.lbl_other_details, 9, 0)
        self.other_details_edit = QLineEdit()
        self.other_details_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.other_details_edit, 9, 1)
        
        layout.addWidget(self.customer_info_group)
        
        # Customer add form section (initially hidden)
        self.customer_add_group = QGroupBox()
        self.customer_add_layout = QGridLayout(self.customer_add_group)
        self.customer_add_layout.setSpacing(10)
        self.customer_add_layout.setContentsMargins(15, 20, 15, 15)
        
        # รหัสลูกค้า (สร้างอัตโนมัติ)
        self.lbl_customer_code2 = QLabel()
        self.customer_add_layout.addWidget(self.lbl_customer_code2, 0, 0)
        self.customer_code_display_edit = QLineEdit()
        self.customer_code_display_edit.setReadOnly(True)
        self.customer_code_display_edit.setStyleSheet("background-color: #F0F0F0; color: #666;")
        self.customer_add_layout.addWidget(self.customer_code_display_edit, 0, 1, 1, 3)
        
        # ชื่อ-นามสกุล
        self.lbl_first_name = QLabel()
        self.customer_add_layout.addWidget(self.lbl_first_name, 1, 0)
        self.customer_first_name_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_first_name_edit, 1, 1)
        
        self.lbl_last_name = QLabel()
        self.customer_add_layout.addWidget(self.lbl_last_name, 1, 2)
        self.customer_last_name_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_last_name_edit, 1, 3)
        
        # เลขบัตรประชาชน
        self.lbl_id_number = QLabel()
        self.customer_add_layout.addWidget(self.lbl_id_number, 2, 0)
        self.customer_id_card_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_id_card_edit, 2, 1, 1, 3)
        
        # ที่อยู่
        self.customer_add_layout.addWidget(QLabel("บ้านเลขที่:"), 3, 0)
        self.customer_house_number_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_house_number_edit, 3, 1)
        
        self.customer_add_layout.addWidget(QLabel("ซอย/ถนน:"), 3, 2)
        self.customer_street_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_street_edit, 3, 3)
        
        self.customer_add_layout.addWidget(QLabel("ตำบล:"), 4, 0)
        self.customer_subdistrict_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_subdistrict_edit, 4, 1)
        
        self.customer_add_layout.addWidget(QLabel("อำเภอ:"), 4, 2)
        self.customer_district_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_district_edit, 4, 3)
        
        self.customer_add_layout.addWidget(QLabel("จังหวัด:"), 5, 0)
        self.customer_province_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_province_edit, 5, 1, 1, 3)
        
        # โทรศัพท์
        self.customer_add_layout.addWidget(QLabel("โทรศัพท์:"), 6, 0)
        self.customer_phone_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_phone_edit, 6, 1, 1, 3)
        
        # รายละเอียดอื่นๆ
        self.customer_add_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 7, 0)
        self.customer_other_details_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_other_details_edit, 7, 1, 1, 3)
        
        # ปุ่มบันทึกและยกเลิก
        button_layout = QHBoxLayout()
        self.customer_save_btn = QPushButton()
        self.customer_save_btn.clicked.connect(self.save_new_customer)
        self.customer_save_btn.setIcon(QIcon.fromTheme("document-save"))
        button_layout.addWidget(self.customer_save_btn)
        
        self.customer_cancel_btn = QPushButton()
        self.customer_cancel_btn.clicked.connect(self.toggle_customer_mode)
        self.customer_cancel_btn.setIcon(QIcon.fromTheme("edit-clear"))
        button_layout.addWidget(self.customer_cancel_btn)
        
        self.customer_add_layout.addLayout(button_layout, 8, 0, 1, 4)
        
        # ซ่อนฟอร์มเพิ่มลูกค้าไว้ก่อน
        self.customer_add_group.hide()
        layout.addWidget(self.customer_add_group)
        
        # เชื่อมต่ออัปเดตภาษา
        language_manager.language_changed.connect(self.apply_customer_tab_language)
        self.apply_customer_tab_language()

        return tab

    def apply_customer_tab_language(self, *_args):
        """อัปเดตข้อความของแท็บลูกค้าตามภาษาปัจจุบัน"""
        # Group titles
        if hasattr(self, "customer_search_group") and self.customer_search_group is not None:
            self.customer_search_group.setTitle(language_manager.get_text("customer_search_group"))
        self.customer_info_group.setTitle(language_manager.get_text("customer_info_group"))
        self.customer_add_group.setTitle(language_manager.get_text("customer_add_group"))

        # Search section
        self.lbl_customer_code.setText(language_manager.get_text("customer_code"))
        self.customer_search_btn.setText(language_manager.get_text("search"))
        self.add_customer_btn.setText(language_manager.get_text("add_new_customer"))

        # Info section
        self.lbl_borrower_name.setText(language_manager.get_text("borrower_name"))
        self.lbl_address.setText(language_manager.get_text("address"))
        self.lbl_id_type.setText(language_manager.get_text("id_card_short"))
        # อัปเดตรายการใน combo ด้วย (แม้จะ disabled)
        self.id_card_type_combo.clear()
        self.id_card_type_combo.addItems([
            language_manager.get_text("id_card_type_citizen"),
            language_manager.get_text("id_card_type_driver"),
            language_manager.get_text("id_card_type_passport"),
        ])
        self.lbl_house_no.setText(language_manager.get_text("house_number"))
        self.lbl_street.setText(language_manager.get_text("street"))
        self.lbl_subdistrict.setText(language_manager.get_text("subdistrict"))
        self.lbl_district.setText(language_manager.get_text("district"))
        self.lbl_province.setText(language_manager.get_text("province"))
        self.lbl_phone.setText(language_manager.get_text("phone"))
        self.lbl_other_details.setText(language_manager.get_text("other_details"))

        # Add section
        self.lbl_customer_code2.setText(language_manager.get_text("customer_code"))
        self.lbl_first_name.setText(language_manager.get_text("first_name"))
        self.lbl_last_name.setText(language_manager.get_text("last_name"))
        self.lbl_id_number.setText(language_manager.get_text("id_card_number"))
        self.customer_save_btn.setText(language_manager.get_text("save"))
        self.customer_cancel_btn.setText(language_manager.get_text("cancel"))

    def create_product_tab(self):
        """สร้างแท็บข้อมูลสินค้า"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างกลุ่ม
        layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ
        
        # Product search section
        search_group = QGroupBox("ค้นหาสินค้า")
        search_layout = QGridLayout(search_group)
        search_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        search_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        search_layout.addWidget(QLabel("ชื่อสินค้า:"), 0, 0)
        self.product_name_edit = QLineEdit()
        search_layout.addWidget(self.product_name_edit, 0, 1)
        
        self.product_search_btn = QPushButton("ค้นหา")
        self.product_search_btn.clicked.connect(self.search_product)
        self.product_search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.product_search_btn.setMinimumHeight(32)
        search_layout.addWidget(self.product_search_btn, 0, 2)
        
        self.add_product_btn = QPushButton("เพิ่มสินค้าใหม่")
        self.add_product_btn.clicked.connect(self.toggle_product_mode)
        self.add_product_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_product_btn.setMinimumHeight(32)
        search_layout.addWidget(self.add_product_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Product info section
        self.product_info_group = QGroupBox("ข้อมูลสินค้า")
        self.product_info_layout = QGridLayout(self.product_info_group)
        self.product_info_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        self.product_info_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        # สินค้าฝากขาย
        self.product_info_layout.addWidget(QLabel("สินค้าฝากขาย:"), 0, 0)
        self.product_name_display_edit = QLineEdit()
        self.product_name_display_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_name_display_edit, 0, 1)
        
        # ยี่ห้อ/รุ่น
        self.product_info_layout.addWidget(QLabel("ยี่ห้อ/รุ่น:"), 1, 0)
        self.product_brand_edit = QLineEdit()
        self.product_brand_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_brand_edit, 1, 1)
        
        # ขนาด
        self.product_info_layout.addWidget(QLabel("ขนาด:"), 2, 0)
        self.product_size_edit = QLineEdit()
        self.product_size_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_size_edit, 2, 1)
        
        # น้ำหนัก
        self.product_info_layout.addWidget(QLabel("น้ำหนัก:"), 3, 0)
        self.product_weight_combo = QComboBox()
        self.product_weight_combo.addItems(["กรัม", "กิโลกรัม", "บาท"])
        self.product_weight_combo.setEnabled(False)
        self.product_info_layout.addWidget(self.product_weight_combo, 3, 1)
        
        # หมายเลขซีเรียล
        self.product_info_layout.addWidget(QLabel("หมายเลขซีเรียล:"), 4, 0)
        self.serial_number_edit = QLineEdit()
        self.serial_number_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.serial_number_edit, 4, 1)
        
        # รายละเอียดอื่นๆ
        self.product_info_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 5, 0)
        self.product_details_edit = QLineEdit()
        self.product_details_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_details_edit, 5, 1)
        
        # รูปภาพสินค้า
        self.product_info_layout.addWidget(QLabel("รูปภาพสินค้า:"), 6, 0)
        self.product_image_display = QLabel()
        self.product_image_display.setMinimumSize(200, 150)
        self.product_image_display.setMaximumSize(300, 200)
        self.product_image_display.setStyleSheet("border: 2px solid #ccc; background-color: #f9f9f9;")
        self.product_image_display.setAlignment(Qt.AlignCenter)
        self.product_image_display.setText("ไม่มีรูปภาพ")
        self.product_info_layout.addWidget(self.product_image_display, 6, 1)
        
        layout.addWidget(self.product_info_group)
        
        # Product add form section (initially hidden)
        self.product_add_group = QGroupBox("เพิ่มสินค้าใหม่")
        self.product_add_layout = QGridLayout(self.product_add_group)
        self.product_add_layout.setSpacing(10)
        self.product_add_layout.setContentsMargins(15, 20, 15, 15)
        
        # ชื่อสินค้า
        self.product_add_layout.addWidget(QLabel("ชื่อสินค้า:"), 0, 0)
        self.product_add_name_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_name_edit, 0, 1, 1, 3)
        
        # ยี่ห้อ/รุ่น
        self.product_add_layout.addWidget(QLabel("ยี่ห้อ/รุ่น:"), 1, 0)
        self.product_add_brand_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_brand_edit, 1, 1, 1, 3)
        
        # ขนาด
        self.product_add_layout.addWidget(QLabel("ขนาด:"), 2, 0)
        self.product_add_size_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_size_edit, 2, 1, 1, 3)
        
        # น้ำหนัก
        self.product_add_layout.addWidget(QLabel("น้ำหนัก:"), 3, 0)
        self.product_add_weight_combo = QComboBox()
        self.product_add_weight_combo.addItems(["กรัม", "กิโลกรัม", "บาท"])
        self.product_add_layout.addWidget(self.product_add_weight_combo, 3, 1, 1, 3)
        
        # หมายเลขซีเรียล
        self.product_add_layout.addWidget(QLabel("หมายเลขซีเรียล:"), 4, 0)
        self.product_add_serial_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_serial_edit, 4, 1, 1, 3)
        
        # รายละเอียดอื่นๆ
        self.product_add_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 5, 0)
        self.product_add_details_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_details_edit, 5, 1, 1, 3)
        
        # รูปภาพสินค้า
        self.product_add_layout.addWidget(QLabel("รูปภาพสินค้า:"), 6, 0)
        self.product_add_image_path_edit = QLineEdit()
        self.product_add_image_path_edit.setPlaceholderText("เลือกไฟล์รูปภาพ...")
        self.product_add_image_path_edit.setReadOnly(True)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.product_add_image_path_edit)
        
        self.product_add_image_browse_btn = QPushButton("เลือกไฟล์")
        self.product_add_image_browse_btn.clicked.connect(self.browse_product_image)
        self.product_add_image_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        image_layout.addWidget(self.product_add_image_browse_btn)
        
        self.product_add_layout.addLayout(image_layout, 6, 1, 1, 3)
        
        # แสดงรูปภาพตัวอย่าง
        self.product_add_layout.addWidget(QLabel("ตัวอย่างรูปภาพ:"), 7, 0)
        self.product_image_preview = QLabel()
        self.product_image_preview.setMinimumSize(200, 150)
        self.product_image_preview.setMaximumSize(300, 200)
        self.product_image_preview.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.product_image_preview.setAlignment(Qt.AlignCenter)
        self.product_image_preview.setText("ไม่มีรูปภาพ")
        self.product_add_layout.addWidget(self.product_image_preview, 7, 1, 1, 3)
        
        # ปุ่มบันทึกและยกเลิก
        button_layout = QHBoxLayout()
        self.product_save_btn = QPushButton("บันทึก")
        self.product_save_btn.clicked.connect(self.save_new_product)
        self.product_save_btn.setIcon(QIcon.fromTheme("document-save"))
        button_layout.addWidget(self.product_save_btn)
        
        self.product_cancel_btn = QPushButton("ยกเลิก")
        self.product_cancel_btn.clicked.connect(self.toggle_product_mode)
        self.product_cancel_btn.setIcon(QIcon.fromTheme("edit-clear"))
        button_layout.addWidget(self.product_cancel_btn)
        
        self.product_add_layout.addLayout(button_layout, 8, 0, 1, 4)
        
        # ซ่อนฟอร์มเพิ่มสินค้าไว้ก่อน
        self.product_add_group.hide()
        layout.addWidget(self.product_add_group)
        
        return tab

    def create_renewal_tab(self):
        """สร้างแท็บข้อมูลต่อดอก"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างกลุ่ม
        layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ
        
      
        
        # Renewal history table
        history_group = QGroupBox("ประวัติการต่อดอก")
        history_layout = QVBoxLayout(history_group)
        history_layout.setContentsMargins(15, 20, 15, 15)
        
        # สร้างตารางประวัติการต่อดอก
        self.renewal_history_table = QTableWidget(0, 8)
        headers = [
            "ลำดับ", "วันที่ต่อดอก", "จำนวนวันต่อ", "ค่าธรรมเนียม", 
            "ค่าปรับ", "ส่วนลด", "ยอดรวม", "วันที่ครบกำหนดใหม่"
        ]
        self.renewal_history_table.setHorizontalHeaderLabels(headers)
        
        # ตั้งค่าความกว้างคอลัมน์
        header = self.renewal_history_table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # ตั้งค่าการแสดงผลตาราง
        self.renewal_history_table.setAlternatingRowColors(True)
        self.renewal_history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.renewal_history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        history_layout.addWidget(self.renewal_history_table)
        
        # ปุ่มดำเนินการ
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.renewal_process_btn = QPushButton("ดำเนินการต่อดอก")
        self.renewal_process_btn.clicked.connect(self.process_renewal)
        self.renewal_process_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.renewal_process_btn.setMinimumHeight(32)
        self.renewal_process_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.renewal_process_btn)
        
        self.renewal_clear_form_btn = QPushButton("ล้างฟอร์ม")
        self.renewal_clear_form_btn.clicked.connect(self.clear_renewal_form)
        self.renewal_clear_form_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.renewal_clear_form_btn.setMinimumHeight(32)
        button_layout.addWidget(self.renewal_clear_form_btn)
        
        history_layout.addLayout(button_layout)
        layout.addWidget(history_group)
        
        return tab


    def create_left_panel(self):
        """สร้างแผงด้านซ้าย - ข้อมูลผู้ขายและสินค้าฝากขาย"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างส่วนต่างๆ
        left_layout.setContentsMargins(0, 0, 0, 0)  # ไม่มี margin ด้านซ้าย
        
        # Customer and Product info tabs
        info_tabs = self.create_info_tabs()
        left_layout.addWidget(info_tabs)
        
        return left_widget

    def create_info_tabs(self):
        """สร้างแท็บข้อมูลผู้ขายและสินค้า"""
        tab_widget = QTabWidget()
        tab_widget.setObjectName("TabWidget")
        
        # Tab 1: Customer Info
        customer_tab = self.create_customer_tab()
        tab_widget.addTab(customer_tab, "ข้อมูลลูกค้า")
        
        # Tab 2: Product Info
        product_tab = self.create_product_tab()
        tab_widget.addTab(product_tab, "ข้อมูลสินค้าขายฝาก")
        
        # Tab 3: Interest Renewal Info
        renewal_tab = self.create_renewal_tab()
        tab_widget.addTab(renewal_tab, "ข้อมูลต่อดอก")
        
        return tab_widget

    def create_right_panel(self):
        """สร้างแผงด้านขวา - ข้อมูลสัญญา ผลจัดทำ ค้นหา"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างส่วนต่างๆ
        right_layout.setContentsMargins(0, 0, 0, 0)  # ไม่มี margin ด้านขวา
        
        # Top row - Contract info and Results in same row
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setSpacing(20)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Contract info section
        contract_info = self.create_contract_info_section()
        top_row_layout.addWidget(contract_info)
        
        # Results section
        results_section = self.create_results_section()
        top_row_layout.addWidget(results_section)
        
        right_layout.addWidget(top_row)
        
        # Search group
        search_group = self.create_search_group()
        right_layout.addWidget(search_group)
        
        # Data table
        data_table = self.create_data_table()
        right_layout.addWidget(data_table)
        
        return right_widget

    def create_contract_info_section(self):
        """สร้างส่วนข้อมูลสัญญา"""
        group_box = QGroupBox("ข้อมูลสัญญา")
        group_box.setObjectName("TopLeftGroup")
        layout = QGridLayout(group_box)
        layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        # เลขที่สัญญา
        layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        self.contract_number_edit = QLineEdit()
        self.contract_number_edit.setReadOnly(True)
        layout.addWidget(self.contract_number_edit, 0, 1)
        
        # วันที่เริ่มต้น
        layout.addWidget(QLabel("วันที่เริ่มต้น:"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.start_date_edit, 1, 1)
        
        # จำนวนวัน
        layout.addWidget(QLabel("จำนวนวัน:"), 2, 0)
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        layout.addWidget(self.days_spin, 2, 1)
        
        # วันที่สิ้นสุด
        layout.addWidget(QLabel("วันที่สิ้นสุด:"), 3, 0)
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setReadOnly(True)
        layout.addWidget(self.end_date_edit, 3, 1)
        
        # เชื่อมต่อสัญญาณ
        self.start_date_edit.dateChanged.connect(self.calculate_end_date)
        self.days_spin.valueChanged.connect(self.calculate_end_date)
        
        # สถานะสัญญา
        layout.addWidget(QLabel("สถานะสัญญา:"), 4, 0)
        status_layout = QHBoxLayout()
        self.active_radio = QRadioButton("สัญญาเปิด")
        self.redeemed_radio = QRadioButton("ไถ่ถอนแล้ว")
        self.lost_radio = QRadioButton("สูญหาย")
        self.active_radio.setChecked(True)
        status_layout.addWidget(self.active_radio)
        status_layout.addWidget(self.redeemed_radio)
        status_layout.addWidget(self.lost_radio)
        layout.addLayout(status_layout, 4, 1)
        
        # ปุ่มอัปเดตสถานะ
        self.update_status_btn = QPushButton("อัปเดตสถานะ")
        self.update_status_btn.clicked.connect(self.update_contract_status)
        self.update_status_btn.setMaximumWidth(120)
        self.update_status_btn.setIcon(QIcon.fromTheme("view-refresh"))
        layout.addWidget(self.update_status_btn, 4, 2)
        
        return group_box

    def create_results_section(self):
        """สร้างส่วนผลจัดทำ"""
        group_box = QGroupBox("ผลจัดทำ")
        group_box.setObjectName("TopMiddleGroup")
        layout = QGridLayout(group_box)
        layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ

        # ยอดฝาก
        layout.addWidget(QLabel("ยอดฝาก"), 0, 0)
        self.pawn_amount_spin = QDoubleSpinBox()
        self.pawn_amount_spin.setRange(0, 999999)
        self.pawn_amount_spin.setSuffix(" บาท")
        layout.addWidget(self.pawn_amount_spin, 0, 1)

        # อัตราดอกเบี้ย
        layout.addWidget(QLabel("อัตราดอกเบี้ย"), 1, 0)
        self.interest_rate_spin = QDoubleSpinBox()
        self.interest_rate_spin.setRange(0, 100)
        self.interest_rate_spin.setSuffix(" %")
        layout.addWidget(self.interest_rate_spin, 1, 1)

        # ค่าธรรมเนียม
        layout.addWidget(QLabel("ค่าธรรมเนียม"), 2, 0)
        self.fee_amount_label = QLabel("0.00 บาท")
        layout.addWidget(self.fee_amount_label, 2, 1)
        
        # อัตราหัก ณ ที่จ่าย
        layout.addWidget(QLabel("อัตราหัก ณ ที่จ่าย"), 3, 0)
        self.withholding_tax_rate_spin = QDoubleSpinBox()
        self.withholding_tax_rate_spin.setRange(0, 100)
        self.withholding_tax_rate_spin.setSuffix(" %")
        self.withholding_tax_rate_spin.setValue(3.0)
        layout.addWidget(self.withholding_tax_rate_spin, 3, 1)
        
        # ปุ่มอัปเดตอัตราหัก ณ ที่จ่าย
        self.update_tax_rate_btn = QPushButton("อัปเดต")
        self.update_tax_rate_btn.clicked.connect(self.update_withholding_tax_rate)
        self.update_tax_rate_btn.setMaximumWidth(80)
        self.update_tax_rate_btn.setIcon(QIcon.fromTheme("view-refresh"))
        layout.addWidget(self.update_tax_rate_btn, 3, 2)
        
        # ยอดหัก ณ ที่จ่าย
        layout.addWidget(QLabel("ยอดหัก ณ ที่จ่าย"), 4, 0)
        self.withholding_tax_amount_label = QLabel("0.00 บาท")
        layout.addWidget(self.withholding_tax_amount_label, 4, 1)
        
        # ยอดจ่าย
        layout.addWidget(QLabel("ยอดจ่าย"), 5, 0)
        self.total_paid_label = QLabel("0.00 บาท")
        layout.addWidget(self.total_paid_label, 5, 1)

        # ยอดไถ่ถอน
        layout.addWidget(QLabel("ยอดไถ่ถอน"), 6, 0)
        self.total_redemption_label = QLabel("0.00 บาท")
        layout.addWidget(self.total_redemption_label, 6, 1)

        # เชื่อมต่อสัญญาณ
        self.pawn_amount_spin.valueChanged.connect(self.calculate_amounts)
        self.interest_rate_spin.valueChanged.connect(self.calculate_amounts)
        self.withholding_tax_rate_spin.valueChanged.connect(self.calculate_amounts)

        return group_box

    def create_search_group(self):
        group_box = QGroupBox("ค้นหาสัญญา")
        group_box.setObjectName("SearchGroup")
        layout = QVBoxLayout(group_box)
        layout.setSpacing(15)  # เพิ่มระยะห่างระหว่างส่วนต่างๆ
        layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        # เลือกประเภทการค้นหา
        search_type_layout = QHBoxLayout()
        search_type_layout.addWidget(QLabel("ค้นหาตาม:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["เลขที่สัญญา", "เลขบัตรประชาชน", "ชื่อนามสกุล"])
        self.search_type_combo.currentTextChanged.connect(self.on_search_type_changed)
        search_type_layout.addWidget(self.search_type_combo)
        layout.addLayout(search_type_layout)
        
        # ฟอร์มค้นหา
        form_layout = QGridLayout()
        form_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างคอลัมน์
        
        # เลขที่สัญญา (เริ่มต้น)
        form_layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        self.search_contract_combo = QComboBox()
        self.search_contract_combo.addItems(["=", ">", "<", ">=", "<="])
        form_layout.addWidget(self.search_contract_combo, 0, 1)
        self.search_contract_edit = QLineEdit()
        self.search_contract_edit.setPlaceholderText("กรอกเลขที่สัญญา...")
        form_layout.addWidget(self.search_contract_edit, 0, 2)
        
        # เลขบัตรประชาชน (ซ่อนไว้)
        form_layout.addWidget(QLabel("เลขบัตรประชาชน:"), 1, 0)
        self.search_id_card_edit = QLineEdit()
        self.search_id_card_edit.setPlaceholderText("กรอกเลขบัตรประชาชน...")
        self.search_id_card_edit.hide()
        form_layout.addWidget(self.search_id_card_edit, 1, 1, 1, 2)
        
        # ชื่อนามสกุล (ซ่อนไว้)
        form_layout.addWidget(QLabel("ชื่อ:"), 2, 0)
        self.search_first_name_edit = QLineEdit()
        self.search_first_name_edit.setPlaceholderText("กรอกชื่อ...")
        self.search_first_name_edit.hide()
        form_layout.addWidget(self.search_first_name_edit, 2, 1)
        
        form_layout.addWidget(QLabel("นามสกุล:"), 2, 2)
        self.search_last_name_edit = QLineEdit()
        self.search_last_name_edit.setPlaceholderText("กรอกนามสกุล...")
        self.search_last_name_edit.hide()
        form_layout.addWidget(self.search_last_name_edit, 2, 3)

        layout.addLayout(form_layout)
        
        # ปุ่มค้นหา
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างปุ่ม
        
        self.search_btn = QPushButton("ค้นหา")
        self.search_btn.clicked.connect(self.search_contracts)
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.setMinimumHeight(32)
        button_layout.addWidget(self.search_btn)
        
        self.clear_search_btn = QPushButton("ล้างการค้นหา")
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_search_btn.setMinimumHeight(32)
        button_layout.addWidget(self.clear_search_btn)
        
        layout.addLayout(button_layout)

        # ตัวเลือกสถานะสัญญา
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(15)  # เพิ่มระยะห่างระหว่าง radio button
        radio_layout.addWidget(QLabel("สถานะสัญญา:"))
        self.search_active_radio = QRadioButton("สัญญาเปิด")
        self.search_closed_radio = QRadioButton("สัญญาปิด")
        self.search_all_radio = QRadioButton("ทั้งหมด")
        self.search_all_radio.setChecked(True)
        radio_layout.addWidget(self.search_active_radio)
        radio_layout.addWidget(self.search_closed_radio)
        radio_layout.addWidget(self.search_all_radio)
        layout.addLayout(radio_layout)
        
        return group_box

    def create_data_table(self):
        self.contract_table = QTableWidget(0, 14)  # เพิ่มคอลัมน์ให้ครบถ้วน
        headers = [
            "ลำดับ", "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", "ยอดจำนำ", 
            "อัตราดอกเบี้ย", "ค่าธรรมเนียม", "วันที่เริ่มต้น", "วันที่สิ้นสุด", 
            "จำนวนวัน", "ดอกเบี้ย", "หัก ณ ที่จ่าย", "ยอดรวม", "สถานะ"
        ]
        self.contract_table.setHorizontalHeaderLabels(headers)
        
        # ไม่แสดงข้อมูลใดๆ เมื่อเริ่มต้น
        self.contract_table.setRowCount(0)
        
        # ตั้งค่าความกว้างคอลัมน์
        header = self.contract_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ลำดับ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # เลขที่สัญญา
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # ชื่อลูกค้า
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # ชื่อสินค้า
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # ยอดจำนำ
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # อัตราดอกเบี้ย
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # ค่าธรรมเนียม
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # วันที่เริ่มต้น
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # วันที่สิ้นสุด
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # จำนวนวัน
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # ดอกเบี้ย
        header.setSectionResizeMode(11, QHeaderView.ResizeToContents)  # หัก ณ ที่จ่าย
        header.setSectionResizeMode(12, QHeaderView.ResizeToContents)  # ยอดรวม
        header.setSectionResizeMode(13, QHeaderView.ResizeToContents)  # สถานะ
        
        # ตั้งค่าการแสดงผลตาราง
        self.contract_table.setAlternatingRowColors(True)  # สลับสีแถว
        self.contract_table.setSelectionBehavior(QTableWidget.SelectRows)  # เลือกทั้งแถว
        self.contract_table.setEditTriggers(QTableWidget.NoEditTriggers)  # ไม่ให้แก้ไขได้
        
        # เชื่อมต่อการคลิกในตารางเพื่อโหลดข้อมูลสัญญา
        self.contract_table.itemClicked.connect(self.on_contract_table_clicked)
        
        return self.contract_table

  

    def create_bottom_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))  # ลดขนาด icon ให้เล็กลง
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setFixedHeight(75)  # ลดความสูงให้ minimal
        toolbar.setMovable(False)
        toolbar.setFloatable(False)  # ไม่ให้ลอยได้
        toolbar.setAllowedAreas(Qt.BottomToolBarArea)  # จำกัดพื้นที่ให้อยู่ด้านล่างเท่านั้น
        
        # ใช้สี minimal และ modern
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #FAFAFA;
                border-top: 1px solid #E0E0E0;
                spacing: 6px;
                padding: 6px;
            }
            QToolButton {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 4px;
                margin: 1px;
                min-width: 80px;
                min-height: 60px;
                max-width: 80px;
                max-height: 60px;
                color: #424242;
                font-size: 9px;
                font-weight: 500;
                text-align: center;
                qproperty-iconSize: 20px;
            }
            QToolButton:hover {
                background-color: #F8F9FA;
                border-color: #BDBDBD;
            }
            QToolButton:pressed {
                background-color: #E3F2FD;
                border-color: #2196F3;
            }
            QToolButton:disabled {
                background-color: #F5F5F5;
                color: #BDBDBD;
                border-color: #E0E0E0;
            }
            QToolButton:checked {
                background-color: #E8F5E8;
                border-color: #4CAF50;
            }
            QToolBar::separator {
                background-color: #E0E0E0;
                width: 2px;
                margin: 4px 8px;
                border-radius: 1px;
            }
        """)
        
        self.addToolBar(Qt.BottomToolBarArea, toolbar)

        # เก็บ toolbar และ action ไว้สำหรับอัปเดตภาษา
        self.bottom_toolbar = toolbar
        self.toolbar_actions = {}

        # ใช้คีย์สำหรับข้อความ เพื่อรองรับหลายภาษา
        action_defs = [
            ("tb_new_contract", "document-new", self.generate_new_contract),
            ("tb_clear_form", "edit-clear", self.clear_form),
            ("tb_save_contract", "document-save", self.save_contract),
            ("tb_generate_pawn_pdf", "document-export", self.generate_pawn_contract_pdf),
            ("tb_extend_interest", "view-refresh", self.extend_interest),
            ("tb_generate_renewal_pdf", "document-export", self.generate_renewal_contract_pdf),
            ("tb_redeem_contract", "go-previous", self.redeem_contract),
            ("tb_view_all", "folder-open", self.view_contracts),
            ("tb_view_redemptions", "document-properties", self.view_redemptions),
            ("tb_daily_income", "x-office-calendar", self.show_daily_income_summary),
            ("tb_fee_management", "preferences-system", self.show_fee_management),
            ("tb_scan_id", "smartcard", self.scan_id_card),
        ]

        for i, (key, icon_name, slot) in enumerate(action_defs):
            text = language_manager.get_text(key)
            # สร้าง icon ที่เหมาะสมสำหรับแต่ละปุ่ม
            icon = self.create_icon_for_action(icon_name, text)
            action = QAction(icon, text, self)
            action.triggered.connect(slot)
            
            # เพิ่ม tooltip เพื่อความชัดเจน
            action.setToolTip(text)
            
            # เพิ่ม status tip สำหรับ status bar
            action.setStatusTip(f"คลิกเพื่อ {text}")

            toolbar.addAction(action)

            # เก็บ action ไว้เพื่ออัปเดตข้อความภายหลัง
            self.toolbar_actions[key] = action
            
            # เพิ่ม separator หลังปุ่มที่ 3 และ 7 เพื่อแบ่งกลุ่ม
            if i == 3 or i == 7 or i == 11:  # เพิ่ม separator หลังปุ่มสแกนบัตร
                toolbar.addSeparator()

        # ปุ่มสลับภาษา
        lang_key = "tb_toggle_language"
        lang_text = language_manager.get_text(lang_key)
        lang_icon = self.create_icon_for_action("preferences-system", lang_text)
        lang_action = QAction(lang_icon, lang_text, self)
        lang_action.setToolTip(lang_text)
        lang_action.setStatusTip(lang_text)
        lang_action.triggered.connect(self.toggle_language)
        toolbar.addAction(lang_action)
        self.toolbar_actions[lang_key] = lang_action

        # อัปเดตข้อความเมื่อภาษาเปลี่ยน
        language_manager.language_changed.connect(self.apply_toolbar_language)

        # ตั้งข้อความตามภาษาปัจจุบันทันที (เผื่อมีการโหลดจาก config)
        self.apply_toolbar_language()

    def create_icon_for_action(self, icon_name, text):
        """สร้าง icon ที่เหมาะสมสำหรับแต่ละปุ่ม"""
        # ใช้ ICON_MAP ที่กำหนดไว้ก่อน
        if icon_name in ICON_MAP:
            icon = QIcon(ICON_MAP[icon_name])
            if not icon.isNull():
                return icon
        
        # ถ้าไม่มีใน ICON_MAP ให้ลองใช้ system theme icons
        icon = QIcon.fromTheme(icon_name)
        
        # ถ้าไม่มี icon ใน system theme ให้ใช้ fallback icons
        if icon.isNull():
            # ใช้ fallback icons ตามประเภทของปุ่ม
            if "สร้าง" in text or "ใหม่" in text:
                icon = QIcon.fromTheme("document-new", QIcon.fromTheme("plus", QIcon.fromTheme("add")))
            elif "ล้าง" in text or "clear" in text:
                icon = QIcon.fromTheme("edit-clear", QIcon.fromTheme("edit-delete", QIcon.fromTheme("trash")))
            elif "บันทึก" in text or "save" in text:
                icon = QIcon.fromTheme("document-save", QIcon.fromTheme("save", QIcon.fromTheme("floppy")))
            elif "ต่อดอก" in text or "ดอก" in text:
                icon = QIcon.fromTheme("view-refresh", QIcon.fromTheme("reload", QIcon.fromTheme("refresh")))
            elif "ไถ่ถอน" in text:
                icon = QIcon.fromTheme("go-previous", QIcon.fromTheme("arrow-left", QIcon.fromTheme("back")))
            elif "หลุดจำนำ" in text:
                icon = QIcon.fromTheme("edit-delete", QIcon.fromTheme("delete", QIcon.fromTheme("remove")))
            elif "ในขายฝาก" in text:
                icon = QIcon.fromTheme("folder-open", QIcon.fromTheme("folder", QIcon.fromTheme("directory")))
            elif "สรุป" in text:
                icon = QIcon.fromTheme("document-properties", QIcon.fromTheme("document", QIcon.fromTheme("file")))
            elif "รับ" in text:
                icon = QIcon.fromTheme("arrow-down", QIcon.fromTheme("download", QIcon.fromTheme("get")))
            elif "หัก ณ ที่จ่าย" in text:
                icon = QIcon.fromTheme("document-edit", QIcon.fromTheme("edit", QIcon.fromTheme("modify")))
            elif "รายงาน" in text:
                icon = QIcon.fromTheme("document-properties", QIcon.fromTheme("report", QIcon.fromTheme("chart")))
            elif "บัญชีรายวัน" in text:
                icon = QIcon.fromTheme("x-office-calendar", QIcon.fromTheme("calendar", QIcon.fromTheme("date")))
            elif "ตารางดอก" in text:
                icon = QIcon.fromTheme("insert-object", QIcon.fromTheme("table", QIcon.fromTheme("grid")))
            elif "ค่าธรรมเนียม" in text:
                icon = QIcon.fromTheme("preferences-system", QIcon.fromTheme("settings", QIcon.fromTheme("configure")))
            elif "สแกนบัตร" in text or "smartcard" in text:
                icon = QIcon.fromTheme("smartcard", QIcon.fromTheme("contact-new", QIcon.fromTheme("user-identity")))
            else:
                # fallback ไปใช้ icon ทั่วไป
                icon = QIcon.fromTheme("applications-other", QIcon.fromTheme("help-about", QIcon.fromTheme("info")))
        
        # ถ้ายังไม่มี icon ให้สร้าง icon ง่ายๆ จาก text
        if icon.isNull():
            icon = self.create_text_icon(text)
        
        return icon
    
    def create_text_icon(self, text):
        """สร้าง icon ง่ายๆ จาก text เมื่อไม่มี system icon"""
        # ใช้ตัวอักษรแรกของ text เป็น icon
        if text:
            first_char = text[0]
            # สร้าง QIcon จาก text (fallback สำหรับกรณีที่ไม่มี icon)
            return QIcon.fromTheme("applications-other", QIcon.fromTheme("help"))
        return QIcon()

    def apply_toolbar_language(self, *_args):
        """อัปเดตข้อความบนปุ่ม toolbar ตามภาษาปัจจุบัน"""
        if not hasattr(self, "toolbar_actions"):
            return
        for key, action in self.toolbar_actions.items():
            text = language_manager.get_text(key)
            action.setText(text)
            action.setToolTip(text)
            # สำหรับปุ่มที่มีสถานะเป็นคำสั่ง เช่น "คลิกเพื่อ ..." เฉพาะปุ่มที่เป็น action หลัก
            if key != "tb_toggle_language":
                action.setStatusTip(f"คลิกเพื่อ {text}")

    def toggle_language(self):
        """เปิด popup ให้เลือกภาษาและเปลี่ยนภาษา"""
        languages = language_manager.get_available_languages()
        # แสดงชื่อภาษาให้ผู้ใช้เห็นสวยงาม
        display_map = {
            "th": "ไทย",
            "en": "English",
            "lo": "ລາວ",
            "my": "မြန်မာ",
        }
        items = [display_map.get(code, code) for code in languages]

        current_code = language_manager.get_current_language()
        current_index = languages.index(current_code) if current_code in languages else 0

        item, ok = QInputDialog.getItem(
            self,
            language_manager.get_text("language"),
            language_manager.get_text("language"),
            items,
            current_index,
            False
        )
        if ok and item:
            # หา code จากชื่อที่เลือก
            reverse_map = {v: k for k, v in display_map.items()}
            selected_code = reverse_map.get(item)
            if selected_code and selected_code != current_code:
                language_manager.set_language(selected_code)

    def generate_new_contract(self):
        """สร้างสัญญาใหม่ - สร้างเลขที่สัญญาและแสดงบน UI"""
        # สร้างเลขที่สัญญาใหม่
        prefix = self.db.get_setting('contract_prefix') if hasattr(self.db, 'get_setting') else "CN"
        # คำนวณลำดับถัดไปจากฐานข้อมูล
        sequence = self.db.get_next_contract_sequence(prefix)
        contract_number = PawnShopUtils.generate_contract_number(prefix, sequence)
        
        # แสดงเลขที่สัญญาบน UI
        self.contract_number_edit.setText(contract_number)
        
        # ล้างฟอร์มเพื่อเตรียมข้อมูลใหม่
        self.clear_form()
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
        
        # ตั้งค่าวันที่เริ่มต้น
        self.start_date_edit.setDate(QDate.currentDate())
        
        # คำนวณวันที่สิ้นสุด
        self.calculate_end_date()
        
        QMessageBox.information(self, "สำเร็จ", "สร้างสัญญาใหม่: {}".format(contract_number))

    def calculate_end_date(self):
        """คำนวณวันที่สิ้นสุด"""
        start_date = self.start_date_edit.date()
        days = self.days_spin.value()
        end_date = start_date.addDays(days)
        self.end_date_edit.setText(end_date.toString("dd/MM/yyyy"))
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def calculate_amounts(self):
        """คำนวณยอดต่างๆ"""
        pawn_amount = self.pawn_amount_spin.value()
        interest_rate = self.interest_rate_spin.value()
        days = self.days_spin.value()
        withholding_tax_rate = self.withholding_tax_rate_spin.value()
        
        # คำนวณดอกเบี้ย
        interest_amount = PawnShopUtils.calculate_interest(pawn_amount, interest_rate, days)
        
        # ค่าธรรมเนียมจากฐานข้อมูล
        fee_amount = self.db.calculate_fee_amount(pawn_amount, days)
        
        # คำนวณหัก ณ ที่จ่าย (หักจากดอกเบี้ย)
        withholding_tax_amount = interest_amount * (withholding_tax_rate / 100)
        
        # ยอดจ่าย (ยอดฝาก - หัก ณ ที่จ่าย)
        total_paid = pawn_amount - withholding_tax_amount
        
        # ยอดไถ่ถอน (รวมหัก ณ ที่จ่าย) - ใช้ฟังก์ชันใหม่
        total_redemption = PawnShopUtils.calculate_redemption_with_tax(
            pawn_amount, interest_amount, fee_amount, withholding_tax_amount
        )
        
        # แสดงผล
        self.fee_amount_label.setText("{:,.2f} บาท".format(fee_amount))
        self.withholding_tax_amount_label.setText("{:,.2f} บาท".format(withholding_tax_amount))
        self.total_paid_label.setText("{:,.2f} บาท".format(total_paid))
        self.total_redemption_label.setText("{:,.2f} บาท".format(total_redemption))
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def add_customer(self):
        """เพิ่มลูกค้า (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.toggle_customer_mode()
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def search_customer(self):
        """ค้นหาลูกค้า"""
        customer_code = self.customer_code_edit.text().strip()
        if not customer_code:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกรหัสลูกค้า")
            return
        
        # ค้นหาลูกค้าในฐานข้อมูล
        customers = self.db.search_customers(customer_code)
        if customers:
            self.current_customer = customers[0]
            self.load_customer_data()
        else:
            QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบลูกค้าที่มีรหัสนี้")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def load_customer_data(self):
        """โหลดข้อมูลลูกค้า"""
        if self.current_customer:
            self.customer_code_edit.setText(self.current_customer.get('customer_code', ''))
            customer_name = "{} {}".format(self.current_customer.get('first_name', ''), self.current_customer.get('last_name', ''))
            self.customer_name_edit.setText(customer_name)
            self.id_card_edit.setText(self.current_customer.get('id_card', ''))
            self.phone_edit.setText(self.current_customer.get('phone', ''))
            
            # ที่อยู่
            address_parts = [
                self.current_customer.get('house_number', ''),
                self.current_customer.get('street', ''),
                self.current_customer.get('subdistrict', ''),
                self.current_customer.get('district', ''),
                self.current_customer.get('province', '')
            ]
            address = ' '.join(filter(None, address_parts))
            self.customer_address_edit.setText(address)
            
            self.house_number_edit.setText(self.current_customer.get('house_number', ''))
            self.street_edit.setText(self.current_customer.get('street', ''))
            self.subdistrict_edit.setText(self.current_customer.get('subdistrict', ''))
            self.district_edit.setText(self.current_customer.get('district', ''))
            self.province_edit.setText(self.current_customer.get('province', ''))
            self.other_details_edit.setText(self.current_customer.get('other_details', ''))
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def add_product(self):
        """เพิ่มสินค้า (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.toggle_product_mode()
        
        # ล้างตารางประวัติการต่อดอก
        if hasattr(self, 'renewal_history_table'):
            self.renewal_history_table.setRowCount(0)

    def search_product(self):
        """ค้นหาสินค้า"""
        product_name = self.product_name_edit.text().strip()
        if not product_name:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อสินค้า")
            return
        
        # ค้นหาสินค้าในฐานข้อมูล
        products = self.db.search_products(product_name)
        if products:
            self.current_product = products[0]
            self.load_product_data()
        else:
            QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสินค้าที่มีชื่อนี้")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def load_product_data(self):
        """โหลดข้อมูลสินค้า"""
        if self.current_product:
            self.product_name_display_edit.setText(self.current_product.get('name', ''))
            self.product_brand_edit.setText(self.current_product.get('brand', ''))
            self.product_size_edit.setText(self.current_product.get('size', ''))
            self.serial_number_edit.setText(self.current_product.get('serial_number', ''))
            self.product_details_edit.setText(self.current_product.get('other_details', ''))
            
            # แสดงรูปภาพสินค้า
            image_path = self.current_product.get('image_path', '')
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # ปรับขนาดรูปภาพให้พอดีกับ display
                    scaled_pixmap = pixmap.scaled(
                        self.product_image_display.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.product_image_display.setPixmap(scaled_pixmap)
                else:
                    self.product_image_display.setText("ไม่สามารถโหลดรูปภาพได้")
            else:
                self.product_image_display.setText("ไม่มีรูปภาพ")
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def extend_interest(self):
        """ต่อดอกเบี้ย"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        dialog = RenewalDialog(self, self.current_contract)
        if dialog.exec() == QDialog.Accepted:
            # รีเฟรชข้อมูลในตาราง
            self.refresh_contract_table()
            # แสดงประวัติการต่อดอกของสัญญานี้ทันที
            try:
                contract_number = self.current_contract.get('contract_number', '')
                if contract_number:
                    renewals = self.db.get_renewals_by_contract(contract_number)
                    if renewals:
                        self.show_renewals_table(renewals)
                    else:
                        QMessageBox.information(self, "ข้อมูลการต่อดอก", "ไม่พบประวัติการต่อดอกของสัญญานี้")
                    # อัปเดตตารางประวัติในแท็บต่อดอก (ถ้ามี)
                    if hasattr(self, 'renewal_history_table'):
                        self.load_renewal_history(contract_number)
                    
                    # อัปเดตข้อมูลสัญญาปัจจุบันในฟอร์มหลัก
                    updated_contract = self.db.get_contract_by_id(self.current_contract['id'])
                    if updated_contract:
                        self.current_contract = updated_contract
                        self.load_contract_data()
            except Exception as e:
                QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดประวัติการต่อดอก: {str(e)}")
    
    def refresh_contract_table(self):
        """รีเฟรชข้อมูลในตาราง"""
        try:
            if self.current_contract:
                # โหลดข้อมูลสัญญาใหม่
                updated_contract = self.db.get_contract_by_id(self.current_contract['id'])
                if updated_contract:
                    self.current_contract = updated_contract
                    # อัปเดตข้อมูลในฟอร์ม
                    self.load_contract_data()
                    
                    # อัปเดตข้อมูลในตาราง
                    if hasattr(self, 'contract_table') and self.contract_table.rowCount() > 0:
                        # ค้นหาสัญญาใหม่และแสดงในตาราง
                        contracts = self.db.search_contracts_by_number(
                            self.current_contract.get('contract_number', ''), 
                            'all'
                        )
                        if contracts:
                            self.display_contract_in_table(contracts)
                    
                    # อัปเดตประวัติการต่อดอก
                    contract_number = self.current_contract.get('contract_number', '')
                    if contract_number:
                        self.load_renewal_history(contract_number)
        except Exception as e:
            print(f"Error refreshing contract table: {e}")

    def redeem_contract(self):
        """ไถ่ถอนสัญญา"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        try:
            # ดึงข้อมูลลูกค้าและสินค้าเพิ่มเติม
            contract_id = self.current_contract['id']
            customer = self.db.get_customer_by_id(self.current_contract.get('customer_id'))
            product = self.db.get_product_by_id(self.current_contract.get('product_id'))
            
            # สร้างข้อมูลสัญญาที่ครบถ้วน
            full_contract_data = {
                **self.current_contract,
                'customer_id': self.current_contract.get('customer_id'),
                'first_name': customer.get('first_name', '') if customer else '',
                'last_name': customer.get('last_name', '') if customer else '',
                'customer_code': customer.get('customer_code', '') if customer else '',
                'id_card': customer.get('id_card', '') if customer else '',
                'phone': customer.get('phone', '') if customer else '',
                'product_name': product.get('name', '') if product else '',
                'brand': product.get('brand', '') if product else '',
                'serial_number': product.get('serial_number', '') if product else ''
            }
            
            dialog = RedemptionDialog(self, full_contract_data)
            if dialog.exec() == QDialog.Accepted:
                # หลังจากไถ่ถอนสำเร็จ ให้แสดงประวัติการไถ่ถอน
                try:
                    # ดึงข้อมูลการไถ่ถอนของสัญญานี้
                    redemptions = self.db.get_redemptions_by_contract(contract_id)
                    
                    if redemptions:
                        # แสดงประวัติการไถ่ถอนเฉพาะสัญญานี้
                        self.show_redemptions_table(redemptions, contract_specific=True)
                    else:
                        QMessageBox.information(self, "ข้อมูลการไถ่ถอน", "ไม่พบข้อมูลการไถ่ถอนของสัญญานี้")
                    
                    # อัปเดตข้อมูลสัญญาปัจจุบันในฟอร์มหลัก
                    updated_contract = self.db.get_contract_by_id(self.current_contract['id'])
                    if updated_contract:
                        self.current_contract = updated_contract
                        self.load_contract_data()
                        
                        # อัปเดตสถานะสัญญาในฟอร์ม
                        if hasattr(self, 'redeemed_radio') and updated_contract.get('status') == 'redeemed':
                            self.redeemed_radio.setChecked(True)
                        
                except Exception as e:
                    QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดประวัติการไถ่ถอน: {str(e)}")
                    
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดข้อมูลสัญญา: {str(e)}")

    def lost_contract(self):
        """หลุดจำนำ"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        try:
            # อัปเดตสถานะสัญญาเป็น 'lost' ในฐานข้อมูล
            contract_id = self.current_contract['id']
            self.db.update_contract_status(contract_id, 'lost')
            
            # อัปเดตข้อมูลสัญญาปัจจุบัน
            updated_contract = self.db.get_contract_by_id(contract_id)
            if updated_contract:
                self.current_contract = updated_contract
                self.load_contract_data()
                
                # อัปเดตสถานะสัญญาในฟอร์ม
                if hasattr(self, 'lost_radio'):
                    self.lost_radio.setChecked(True)

                # ส่งแจ้งเตือนเข้า Line เมื่อหลุดจำนำ
                try:
                    # enrich minimal fields for template
                    customer = self.db.get_customer_by_id(updated_contract.get('customer_id')) if updated_contract else None
                    product = self.db.get_product_by_id(updated_contract.get('product_id')) if updated_contract else None
                    enriched = {
                        **(updated_contract or {}),
                        'first_name': (customer or {}).get('first_name', ''),
                        'last_name': (customer or {}).get('last_name', ''),
                        'product_name': (product or {}).get('name', ''),
                    }
                    self.send_forfeiture_to_line(enriched)
                except Exception as e:
                    print(f"ส่งแจ้งเตือนหลุดจำนำล้มเหลว: {e}")
                
            QMessageBox.information(self, "สำเร็จ", "อัปเดตสถานะสัญญาเป็น 'หลุดจำนำ' เรียบร้อย")
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการอัปเดตสถานะสัญญา: {str(e)}")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def update_contract_status(self):
        """อัปเดตสถานะสัญญาตามที่เลือกในฟอร์ม"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        try:
            # กำหนดสถานะตามที่เลือก
            if hasattr(self, 'redeemed_radio') and self.redeemed_radio.isChecked():
                status = 'redeemed'
            elif hasattr(self, 'lost_radio') and self.lost_radio.isChecked():
                status = 'lost'
            else:
                status = 'active'
            
            # อัปเดตสถานะในฐานข้อมูล
            contract_id = self.current_contract['id']
            if self.db.update_contract_status(contract_id, status):
                # อัปเดตข้อมูลสัญญาปัจจุบัน
                updated_contract = self.db.get_contract_by_id(contract_id)
                if updated_contract:
                    self.current_contract = updated_contract
                    self.load_contract_data()

                    # ถ้าสถานะเป็น lost ให้ส่งแจ้งเตือนเข้า Line
                    if status == 'lost':
                        try:
                            customer = self.db.get_customer_by_id(updated_contract.get('customer_id')) if updated_contract else None
                            product = self.db.get_product_by_id(updated_contract.get('product_id')) if updated_contract else None
                            enriched = {
                                **(updated_contract or {}),
                                'first_name': (customer or {}).get('first_name', ''),
                                'last_name': (customer or {}).get('last_name', ''),
                                'product_name': (product or {}).get('name', ''),
                            }
                            self.send_forfeiture_to_line(enriched)
                        except Exception as e:
                            print(f"ส่งแจ้งเตือนหลุดจำนำล้มเหลว: {e}")
                
                QMessageBox.information(self, "สำเร็จ", f"อัปเดตสถานะสัญญาเป็น '{status}' เรียบร้อย")
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถอัปเดตสถานะสัญญาได้")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการอัปเดตสถานะสัญญา: {str(e)}")

    def save_contract(self):
        """บันทึกสัญญา"""
        if not self.current_customer:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกลูกค้าก่อน")
            return
        
        if not self.current_product:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสินค้าก่อน")
            return
        
        # สร้างข้อมูลสัญญา
        contract_data = {
            'contract_number': self.contract_number_edit.text(),
            'customer_id': self.current_customer['id'],
            'product_id': self.current_product['id'],
            'pawn_amount': self.pawn_amount_spin.value(),
            'interest_rate': self.interest_rate_spin.value(),
            'fee_amount': float(self.fee_amount_label.text().replace(' บาท', '').replace(',', '')),
            'withholding_tax_rate': self.withholding_tax_rate_spin.value(),
            'withholding_tax_amount': float(self.withholding_tax_amount_label.text().replace(' บาท', '').replace(',', '')),
            'total_paid': float(self.total_paid_label.text().replace(' บาท', '').replace(',', '')),
            'total_redemption': float(self.total_redemption_label.text().replace(' บาท', '').replace(',', '')),
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_edit.text(),
            'days_count': self.days_spin.value(),
            'status': 'redeemed' if hasattr(self, 'redeemed_radio') and self.redeemed_radio.isChecked() else 'lost' if hasattr(self, 'lost_radio') and self.lost_radio.isChecked() else 'active'
        }
        
        try:
            contract_id = self.db.create_contract(contract_data)
            
            # เก็บข้อมูลสัญญาไว้ใน current_contract เพื่อใช้สร้าง PDF
            self.current_contract = {
                'id': contract_id,
                'contract_number': contract_data['contract_number'],
                'start_date': contract_data['start_date'],
                'end_date': contract_data['end_date'],
                'days': contract_data['days_count'],
                'pawn_amount': contract_data['pawn_amount'],
                'interest_rate': contract_data['interest_rate'],
                'fee_amount': contract_data['fee_amount'],
                'withholding_tax_rate': contract_data['withholding_tax_rate'],
                'withholding_tax_amount': contract_data['withholding_tax_amount'],
                'total_paid': contract_data['total_paid'],
                'total_redemption': contract_data['total_redemption'],
                'status': contract_data['status']
            }
            
            QMessageBox.information(self, "สำเร็จ", "บันทึกสัญญาเรียบร้อย")
            
            # ส่งข้อมูลสัญญาเข้า Line
            try:
                self.send_contract_to_line(contract_data, self.current_customer, self.current_product)
            except Exception as e:
                print(f"ไม่สามารถส่งข้อมูลเข้า Line ได้: {str(e)}")
            
            # โหลดประวัติการต่อดอก (ถ้ามี)
            contract_number = contract_data['contract_number']
            if contract_number:
                self.load_renewal_history(contract_number)
            
            # แสดงปุ่มสร้าง PDF
            self.show_pdf_generation_dialog(contract_data)
            
            self.generate_new_contract_number()
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))

    def view_contracts(self):
        """ดูข้อมูลทั้งหมด"""
        dialog = DataViewerDialog(self)
        dialog.exec()
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
    
    def view_renewals(self):
        """ดูข้อมูลการต่อดอก"""
        try:
            # ดึงข้อมูลการต่อดอกทั้งหมด
            renewals = self.db.get_all_renewals()
            
            if not renewals:
                QMessageBox.information(self, "ข้อมูลการต่อดอก", "ไม่พบข้อมูลการต่อดอก")
                return
            
            # สร้างหน้าต่างแสดงข้อมูลการต่อดอก
            self.show_renewals_table(renewals)
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
    
    def show_renewals_table(self, renewals: list):
        """แสดงตารางข้อมูลการต่อดอก"""
        dialog = QDialog(self)
        dialog.setWindowTitle("ข้อมูลการต่อดอก")
        dialog.setModal(True)
        dialog.resize(1200, 600)
        
        layout = QVBoxLayout(dialog)
        
        # สร้างตาราง
        table = QTableWidget()
        table.setColumnCount(11)
        headers = [
            "ลำดับ", "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", "ต่อดอกครั้งที่",
            "ค่าธรรมเนียม", "ค่าปรับ", "ส่วนลด", "รวม", "วันต่อดอก", "วันครบกำหนดใหม่"
        ]
        table.setHorizontalHeaderLabels(headers)
        
        # ตั้งค่าความกว้างคอลัมน์
        header = table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # เพิ่มข้อมูล
        table.setRowCount(len(renewals))
        for row, renewal in enumerate(renewals):
            # ลำดับ
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # เลขที่สัญญา
            table.setItem(row, 1, QTableWidgetItem(renewal.get('contract_number', '')))
            
            # ชื่อลูกค้า
            customer_name = "{} {}".format(
                renewal.get('first_name', ''), 
                renewal.get('last_name', '')
            )
            table.setItem(row, 2, QTableWidgetItem(customer_name))
            
            # ชื่อสินค้า
            table.setItem(row, 3, QTableWidgetItem(renewal.get('product_name', '')))
            
            # ต่อดอกครั้งที่
            table.setItem(row, 4, QTableWidgetItem(str(renewal.get('renewal_count', ''))))
            
            # ค่าธรรมเนียม
            table.setItem(row, 5, QTableWidgetItem(f"{renewal.get('fee_amount', 0):,.2f}"))
            
            # ค่าปรับ
            table.setItem(row, 6, QTableWidgetItem(f"{renewal.get('penalty_amount', 0):,.2f}"))
            
            # ส่วนลด
            table.setItem(row, 7, QTableWidgetItem(f"{renewal.get('discount_amount', 0):,.2f}"))
            
            # รวม
            table.setItem(row, 8, QTableWidgetItem(f"{renewal.get('total_amount', 0):,.2f}"))
            
            # วันต่อดอก
            renewal_date = renewal.get('renewal_date', '')
            if renewal_date:
                try:
                    date_obj = datetime.strptime(renewal_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    table.setItem(row, 9, QTableWidgetItem(formatted_date))
                except:
                    table.setItem(row, 9, QTableWidgetItem(renewal_date))
            else:
                table.setItem(row, 9, QTableWidgetItem(""))
            
            # วันครบกำหนดใหม่
            new_due_date = renewal.get('new_due_date', '')
            if new_due_date:
                try:
                    date_obj = datetime.strptime(new_due_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    table.setItem(row, 10, QTableWidgetItem(formatted_date))
                except:
                    table.setItem(row, 10, QTableWidgetItem(new_due_date))
            else:
                table.setItem(row, 10, QTableWidgetItem(""))
        
        # ตั้งค่าการแสดงผลตาราง
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(table)
        
        # ปุ่มปิด
        close_button = QPushButton("ปิด")
        close_button.clicked.connect(dialog.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()

    def view_redemptions(self):
        """ดูข้อมูลการไถ่ถอน"""
        try:
            # ดึงข้อมูลการไถ่ถอนทั้งหมด
            redemptions = self.db.get_all_redemptions()
            
            if not redemptions:
                QMessageBox.information(self, "ข้อมูลการไถ่ถอน", "ไม่พบข้อมูลการไถ่ถอน")
                return
            
            # สร้างหน้าต่างแสดงข้อมูลการไถ่ถอน
            self.show_redemptions_table(redemptions)
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
    
    def show_redemptions_table(self, redemptions: list, contract_specific: bool = False):
        """แสดงตารางข้อมูลการไถ่ถอน"""
        if contract_specific:
            dialog = QDialog(self)
            dialog.setWindowTitle("ประวัติการไถ่ถอน - สัญญาเฉพาะ")
            dialog.setModal(True)
            dialog.resize(1200, 500)
        else:
            dialog = QDialog(self)
            dialog.setWindowTitle("ข้อมูลการไถ่ถอน")
            dialog.setModal(True)
            dialog.resize(1400, 600)
        
        layout = QVBoxLayout(dialog)
        
        # สร้างตาราง
        table = QTableWidget()
        if contract_specific:
            table.setColumnCount(12)
            headers = [
                "ลำดับ", "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", 
                "วันที่รับฝาก", "วันที่ครบกำหนด", "วันที่ไถ่ถอน", "จำนวนวันที่ฝาก",
                "เงินต้น", "ค่าธรรมเนียม", "ค่าปรับ", "ยอดไถ่ถอน"
            ]
        else:
            table.setColumnCount(10)
            headers = [
                "ลำดับ", "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", 
                "วันที่ไถ่ถอน", "จำนวนวันที่ฝาก", "เงินต้น", "ค่าธรรมเนียม", "ค่าปรับ", "ยอดไถ่ถอน"
            ]
        table.setHorizontalHeaderLabels(headers)
        
        # ตั้งค่าความกว้างคอลัมน์
        header = table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # เพิ่มข้อมูล
        table.setRowCount(len(redemptions))
        for row, redemption in enumerate(redemptions):
            # ลำดับ
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # เลขที่สัญญา
            table.setItem(row, 1, QTableWidgetItem(redemption.get('contract_number', '')))
            
            # ชื่อลูกค้า
            customer_name = "{} {}".format(
                redemption.get('first_name', ''), 
                redemption.get('last_name', '')
            )
            table.setItem(row, 2, QTableWidgetItem(customer_name))
            
            # ชื่อสินค้า
            table.setItem(row, 3, QTableWidgetItem(redemption.get('product_name', '')))
            
            if contract_specific:
                # วันที่รับฝาก
                deposit_date = redemption.get('deposit_date', '')
                table.setItem(row, 4, QTableWidgetItem(deposit_date))
                
                # วันที่ครบกำหนด
                due_date = redemption.get('due_date', '')
                table.setItem(row, 5, QTableWidgetItem(due_date))
                
                # วันที่ไถ่ถอน
                redemption_date = redemption.get('redemption_date', '')
                table.setItem(row, 6, QTableWidgetItem(redemption_date))
                
                # จำนวนวันที่ฝาก
                total_days = redemption.get('total_days', 0)
                table.setItem(row, 7, QTableWidgetItem(str(total_days)))
                
                # เงินต้น
                principal_amount = redemption.get('principal_amount', 0)
                table.setItem(row, 8, QTableWidgetItem(f"{principal_amount:,.2f}"))
                
                # ค่าธรรมเนียม
                fee_amount = redemption.get('fee_amount', 0)
                table.setItem(row, 9, QTableWidgetItem(f"{fee_amount:,.2f}"))
                
                # ค่าปรับ
                penalty_amount = redemption.get('penalty_amount', 0)
                table.setItem(row, 10, QTableWidgetItem(f"{penalty_amount:,.2f}"))
                
                # ยอดไถ่ถอน
                redemption_amount = redemption.get('redemption_amount', 0)
                table.setItem(row, 11, QTableWidgetItem(f"{redemption_amount:,.2f}"))
            else:
                # วันที่ไถ่ถอน
                redemption_date = redemption.get('redemption_date', '')
                table.setItem(row, 4, QTableWidgetItem(redemption_date))
                
                # จำนวนวันที่ฝาก
                total_days = redemption.get('total_days', 0)
                table.setItem(row, 5, QTableWidgetItem(str(total_days)))
                
                # เงินต้น
                principal_amount = redemption.get('principal_amount', 0)
                table.setItem(row, 6, QTableWidgetItem(f"{principal_amount:,.2f}"))
                
                # ค่าธรรมเนียม
                fee_amount = redemption.get('fee_amount', 0)
                table.setItem(row, 7, QTableWidgetItem(f"{fee_amount:,.2f}"))
                
                # ค่าปรับ
                penalty_amount = redemption.get('penalty_amount', 0)
                table.setItem(row, 8, QTableWidgetItem(f"{penalty_amount:,.2f}"))
                
                # ยอดไถ่ถอน
                redemption_amount = redemption.get('redemption_amount', 0)
                table.setItem(row, 9, QTableWidgetItem(f"{redemption_amount:,.2f}"))
        
        layout.addWidget(table)
        
        # ปุ่มปิด
        close_button = QPushButton("ปิด")
        close_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()

    def summary_report(self):
        """สรุปขายฝาก"""
        QMessageBox.information(self, "สรุปขายฝาก", "ฟีเจอร์สรุปขายฝาก")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def receive_payment(self):
        """รับเงิน"""
        QMessageBox.information(self, "รับเงิน", "ฟีเจอร์รับเงิน")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def daily_account(self):
        """บัญชีรายวัน"""
        QMessageBox.information(self, "บัญชีรายวัน", "ฟีเจอร์บัญชีรายวัน")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def interest_schedule(self):
        """ตารางดอกเบี้ย"""
        QMessageBox.information(self, "ตารางดอกเบี้ย", "ฟีเจอร์ตารางดอกเบี้ย")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def on_search_type_changed(self):
        """เมื่อเปลี่ยนประเภทการค้นหา"""
        search_type = self.search_type_combo.currentText()
        
        # ซ่อนฟอร์มทั้งหมดก่อน
        self.search_contract_edit.hide()
        self.search_contract_combo.hide()
        self.search_id_card_edit.hide()
        self.search_first_name_edit.hide()
        self.search_last_name_edit.hide()
        
        # แสดงฟอร์มที่เหมาะสม
        if search_type == "เลขที่สัญญา":
            self.search_contract_edit.show()
            self.search_contract_combo.show()
        elif search_type == "เลขบัตรประชาชน":
            self.search_id_card_edit.show()
        elif search_type == "ชื่อนามสกุล":
            self.search_first_name_edit.show()
            self.search_last_name_edit.show()
        
        # ล้างข้อมูลการค้นหา
        self.clear_search_fields()
        
        # ไม่ล้างประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def clear_search_fields(self):
        """ล้างข้อมูลในฟิลด์ค้นหา"""
        self.search_contract_edit.clear()
        self.search_id_card_edit.clear()
        self.search_first_name_edit.clear()
        self.search_last_name_edit.clear()
        
        # ไม่ล้างประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def search_contracts(self):
        """ค้นหาสัญญาตามประเภทที่เลือก"""
        search_type = self.search_type_combo.currentText()
        
        # ตรวจสอบข้อมูลการค้นหา
        if search_type == "เลขที่สัญญา":
            search_term = self.search_contract_edit.text().strip()
            if not search_term:
                QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกเลขที่สัญญา")
                return
        elif search_type == "เลขบัตรประชาชน":
            search_term = self.search_id_card_edit.text().strip()
            if not search_term:
                QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกเลขบัตรประชาชน")
                return
        elif search_type == "ชื่อนามสกุล":
            first_name = self.search_first_name_edit.text().strip()
            last_name = self.search_last_name_edit.text().strip()
            if not first_name and not last_name:
                QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อหรือนามสกุลอย่างน้อยหนึ่งตัว")
                return
            search_term = f"{first_name} {last_name}".strip()
        else:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกประเภทการค้นหา")
            return
        
        # กำหนดสถานะการค้นหา
        status = 'all'
        if self.search_active_radio.isChecked():
            status = 'active'
        elif self.search_closed_radio.isChecked():
            status = 'redeemed'
        
        try:
            # ค้นหาสัญญาตามประเภทที่เลือก
            if search_type == "เลขที่สัญญา":
                contracts = self.db.search_contracts_by_number(search_term, status)
            elif search_type == "เลขบัตรประชาชน":
                contracts = self.db.search_contracts_by_id_card(search_term, status)
            elif search_type == "ชื่อนามสกุล":
                contracts = self.db.search_contracts_by_name(first_name, last_name, status)
            else:
                contracts = []
            
            if contracts:
                # เลือกสัญญาแรกเป็นสัญญาปัจจุบัน
                self.current_contract = contracts[0]
                
                # โหลดข้อมูลสัญญาในฟอร์ม
                self.load_contract_data()
                
                # โหลดข้อมูลลูกค้าและสินค้าเพิ่มเติม
                self.load_additional_contract_data(contracts[0])
                
                # โหลดประวัติการต่อดอก
                contract_number = contracts[0].get('contract_number', '')
                if contract_number:
                    self.load_renewal_history(contract_number)
                
                # แสดงข้อมูลในตาราง
                self.display_contract_in_table(contracts)
                
                QMessageBox.information(self, "ผลการค้นหา", f"พบ {len(contracts)} สัญญา\nข้อมูลสัญญาแรกถูกโหลดในฟอร์มแล้ว")
            else:
                QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสัญญาที่ตรงกับคำค้นหา")
                self.contract_table.setRowCount(0)
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")

    def clear_search(self):
        """ล้างการค้นหา"""
        self.clear_search_fields()
        self.contract_table.setRowCount(0)
        self.current_contract = None
        
        # ไม่ล้างประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
        
        QMessageBox.information(self, "ล้างการค้นหา", "ล้างการค้นหาเรียบร้อยแล้ว")

    def search_next(self):
        """ค้นหาถัดไป (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.search_contracts()
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
    
    def display_contract_in_table(self, contracts: list):
        """แสดงข้อมูลสัญญาในตาราง"""
        self.contract_table.setRowCount(len(contracts))
        
        for row, contract in enumerate(contracts):
            # ลำดับ
            self.contract_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # เลขที่สัญญา
            contract_number = contract.get('contract_number', '')
            self.contract_table.setItem(row, 1, QTableWidgetItem(contract_number))
            
            # ชื่อลูกค้า
            customer_name = "{} {}".format(contract.get('first_name', ''), contract.get('last_name', ''))
            self.contract_table.setItem(row, 2, QTableWidgetItem(customer_name))
            
            # ชื่อสินค้า
            product_name = contract.get('product_name', '')
            self.contract_table.setItem(row, 3, QTableWidgetItem(product_name))
            
            # ยอดจำนำ
            pawn_amount = contract.get('pawn_amount', 0)
            self.contract_table.setItem(row, 4, QTableWidgetItem(f"{pawn_amount:,.2f}"))
            
            # อัตราดอกเบี้ย
            interest_rate = contract.get('interest_rate', 0)
            self.contract_table.setItem(row, 5, QTableWidgetItem(f"{interest_rate:.2f}%"))
            
            # ค่าธรรมเนียม
            fee_amount = contract.get('fee_amount', 0)
            self.contract_table.setItem(row, 6, QTableWidgetItem(f"{fee_amount:,.2f}"))
            
            # วันที่เริ่มต้น
            start_date = contract.get('start_date', '')
            self.contract_table.setItem(row, 7, QTableWidgetItem(start_date))
            
            # วันที่สิ้นสุด
            end_date = contract.get('end_date', '')
            self.contract_table.setItem(row, 8, QTableWidgetItem(end_date))
            
            # จำนวนวัน
            days_count = contract.get('days_count', 0)
            self.contract_table.setItem(row, 9, QTableWidgetItem(str(days_count)))
            
            # ดอกเบี้ย
            interest_amount = (pawn_amount * interest_rate * days_count) / 100
            self.contract_table.setItem(row, 10, QTableWidgetItem(f"{interest_amount:,.2f}"))
            
            # หัก ณ ที่จ่าย
            withholding_tax_amount = contract.get('withholding_tax_amount', 0)
            self.contract_table.setItem(row, 11, QTableWidgetItem(f"{withholding_tax_amount:,.2f}"))
            
            # ยอดรวม
            total_amount = pawn_amount + interest_amount + fee_amount - withholding_tax_amount
            self.contract_table.setItem(row, 12, QTableWidgetItem(f"{total_amount:,.2f}"))
            
            # สถานะ
            status = contract.get('status', 'active')
            status_text = "ใช้งาน" if status == 'active' else "ไถ่ถอนแล้ว" if status == 'redeemed' else "สูญหาย"
            self.contract_table.setItem(row, 13, QTableWidgetItem(status_text))
            
            # เก็บข้อมูล ID ไว้ใน item
            self.contract_table.item(row, 0).setData(Qt.UserRole, contract.get('id'))
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def search_by_name(self):
        """ค้นหาตามชื่อ (legacy - ใช้ฟังก์ชันใหม่แทน)"""
        # เปลี่ยนไปใช้การค้นหาตามชื่อนามสกุล
        self.search_type_combo.setCurrentText("ชื่อนามสกุล")
        self.on_search_type_changed()
        QMessageBox.information(self, "การค้นหา", "กรุณาเลือกประเภทการค้นหาเป็น 'ชื่อนามสกุล' และกรอกข้อมูล")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.current_contract:
            # โหลดข้อมูลสัญญา
            self.contract_number_edit.setText(self.current_contract.get('contract_number', ''))
            
            # โหลดข้อมูลลูกค้า
            customer_name = "{} {}".format(self.current_contract.get('first_name', ''), self.current_contract.get('last_name', ''))
            self.customer_name_edit.setText(customer_name)
            
            # โหลดข้อมูลสินค้า
            self.product_name_display_edit.setText(self.current_contract.get('product_name', ''))
            
            # โหลดข้อมูลสัญญาเพิ่มเติม
            self.pawn_amount_spin.setValue(self.current_contract.get('pawn_amount', 0))
            self.interest_rate_spin.setValue(self.current_contract.get('interest_rate', 3.0))
            
            # อัปเดตค่าธรรมเนียมใน label
            fee_amount = self.current_contract.get('fee_amount', 0)
            self.fee_amount_label.setText(f"{fee_amount:,.2f} บาท")
            
            # อัปเดตยอดจ่ายและยอดไถ่ถอนใน label
            total_paid = self.current_contract.get('total_paid', 0)
            self.total_paid_label.setText(f"{total_paid:,.2f} บาท")
            
            total_redemption = self.current_contract.get('total_redemption', 0)
            self.total_redemption_label.setText(f"{total_redemption:,.2f} บาท")
            
            # โหลดวันที่
            start_date = self.current_contract.get('start_date', '')
            if start_date:
                try:
                    if isinstance(start_date, str):
                        if '-' in start_date:
                            date_obj = QDate.fromString(start_date, "yyyy-MM-dd")
                        else:
                            date_obj = QDate.fromString(start_date, "dd/MM/yyyy")
                        if date_obj.isValid():
                            self.start_date_edit.setDate(date_obj)
                except:
                    pass
            
            end_date = self.current_contract.get('end_date', '')
            if end_date:
                try:
                    if isinstance(end_date, str):
                        if '-' in end_date:
                            date_obj = QDate.fromString(end_date, "yyyy-MM-dd")
                        else:
                            date_obj = QDate.fromString(end_date, "dd/MM/yyyy")
                        if date_obj.isValid():
                            self.end_date_edit.setDate(date_obj)
                except:
                    pass
            
            # โหลดจำนวนวัน
            days_count = self.current_contract.get('days_count', 0)
            if days_count > 0:
                self.days_spin.setValue(days_count)
            
            # โหลดข้อมูลหัก ณ ที่จ่าย
            withholding_tax_rate = self.current_contract.get('withholding_tax_rate', 3.0)
            self.withholding_tax_rate_spin.setValue(withholding_tax_rate)
            
            withholding_tax_amount = self.current_contract.get('withholding_tax_amount', 0)
            if withholding_tax_amount > 0:
                self.withholding_tax_amount_label.setText("{:,.2f} บาท".format(withholding_tax_amount))
            
            # คำนวณยอดต่างๆ ใหม่
            self.calculate_amounts()
            
            # อัปเดตสถานะสัญญา
            status = self.current_contract.get('status', 'active')
            if hasattr(self, 'redeemed_radio') and hasattr(self, 'lost_radio') and hasattr(self, 'active_radio'):
                if status == 'redeemed':
                    self.redeemed_radio.setChecked(True)
                elif status == 'lost':
                    self.lost_radio.setChecked(True)
                else:
                    self.active_radio.setChecked(True)
            
            # โหลดประวัติการต่อดอก
            contract_number = self.current_contract.get('contract_number', '')
            if contract_number:
                self.load_renewal_history(contract_number)

    def clear_form(self):
        """ล้างฟอร์ม"""
        self.current_customer = None
        self.current_product = None
        self.current_contract = None
        
        # ล้างข้อมูลลูกค้า
        self.customer_code_edit.clear()
        self.customer_name_edit.clear()
        self.customer_address_edit.clear()
        self.id_card_edit.clear()
        self.house_number_edit.clear()
        self.street_edit.clear()
        self.subdistrict_edit.clear()
        self.district_edit.clear()
        self.province_edit.clear()
        self.phone_edit.clear()
        self.other_details_edit.clear()
        
        # ล้างข้อมูลสินค้า
        self.product_name_edit.clear()
        self.product_name_display_edit.clear()
        self.product_brand_edit.clear()
        self.product_size_edit.clear()
        self.serial_number_edit.clear()
        self.product_details_edit.clear()
        
        # ล้างข้อมูลฟอร์มเพิ่มลูกค้าใหม่
        self.customer_code_display_edit.clear()
        self.customer_first_name_edit.clear()
        self.customer_last_name_edit.clear()
        self.customer_id_card_edit.clear()
        self.customer_house_number_edit.clear()
        self.customer_street_edit.clear()
        self.customer_subdistrict_edit.clear()
        self.customer_district_edit.clear()
        self.customer_province_edit.clear()
        self.customer_phone_edit.clear()
        self.customer_other_details_edit.clear()
        
        # ล้างข้อมูลฟอร์มเพิ่มสินค้าใหม่
        self.product_add_name_edit.clear()
        self.product_add_brand_edit.clear()
        self.product_add_size_edit.clear()
        self.product_add_serial_edit.clear()
        self.product_add_details_edit.clear()
        self.product_add_weight_combo.setCurrentIndex(0)
        self.product_add_image_path_edit.clear()
        self.product_image_preview.clear()
        self.product_image_preview.setText("ไม่มีรูปภาพ")
        
        # ล้างรูปภาพสินค้าในส่วนแสดงข้อมูล
        self.product_image_display.clear()
        self.product_image_display.setText("ไม่มีรูปภาพ")
        
        # ล้างยอด
        self.pawn_amount_spin.setValue(0)
        self.withholding_tax_rate_spin.setValue(3.0)
        self.calculate_amounts()
        
        # รีเซ็ตสถานะสัญญา
        if hasattr(self, 'active_radio'):
            self.active_radio.setChecked(True)
        
        # กลับไปแสดงฟอร์มข้อมูลปกติ
        if hasattr(self, 'customer_add_group'):
            self.customer_add_group.hide()
            self.customer_info_group.show()
        if hasattr(self, 'product_add_group'):
            self.product_add_group.hide()
            self.product_info_group.show()
        
        # ไม่ล้างประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def generate_new_contract_number(self):
        """สร้างเลขที่สัญญาใหม่"""
        prefix = self.db.get_setting('contract_prefix') if hasattr(self.db, 'get_setting') else "CN"
        # คำนวณลำดับถัดไปจากฐานข้อมูล
        sequence = self.db.get_next_contract_sequence(prefix)
        contract_number = PawnShopUtils.generate_contract_number(prefix, sequence)
        self.contract_number_edit.setText(contract_number)
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def show_daily_report(self):
        """แสดงรายงานประจำวัน"""
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            summary = self.db.get_daily_summary(today)
            
            message = """
รายงานประจำวัน: {}
สัญญาใหม่: {} สัญญา ({:,.2f} บาท)
การไถ่ถอน: {} สัญญา ({:,.2f} บาท)
การชำระดอกเบี้ย: {} ครั้ง ({:,.2f} บาท)
การต่อดอก: {} ครั้ง ({:,.2f} บาท)
            """.format(
                today,
                summary['new_contracts_count'],
                summary['new_contracts_amount'],
                summary['redemptions_count'],
                summary['redemptions_amount'],
                summary['interest_payments_count'],
                summary['interest_payments_amount'],
                summary['renewals_count'],
                summary['renewals_amount']
            )
        except:
            message = "รายงานประจำวัน: {}\nไม่สามารถโหลดข้อมูลได้".format(today)
        
        QMessageBox.information(self, "รายงานประจำวัน", message)
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def show_monthly_report(self):
        """แสดงรายงานประจำเดือน"""
        QMessageBox.information(self, "รายงานประจำเดือน", "ฟีเจอร์รายงานประจำเดือน")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
    
    def show_withholding_tax_report(self):
        """แสดงรายงานหัก ณ ที่จ่าย"""
        try:
            # ดึงข้อมูลหัก ณ ที่จ่ายจากฐานข้อมูล
            contracts = self.db.get_contracts_with_withholding_tax()
            
            if not contracts:
                QMessageBox.information(self, "รายงานหัก ณ ที่จ่าย", "ไม่พบข้อมูลหัก ณ ที่จ่าย")
                return
            
            # สร้างรายงาน
            total_withholding_tax = sum(contract.get('withholding_tax_amount', 0) for contract in contracts)
            total_interest = sum(contract.get('interest_amount', 0) for contract in contracts)
            
            message = f"""
รายงานหัก ณ ที่จ่าย:

จำนวนสัญญา: {len(contracts)} สัญญา
ยอดดอกเบี้ยรวม: {total_interest:,.2f} บาท
ยอดหัก ณ ที่จ่ายรวม: {total_withholding_tax:,.2f} บาท
ยอดจ่ายจริงรวม: {total_interest - total_withholding_tax:,.2f} บาท

หมายเหตุ: หัก ณ ที่จ่ายจะถูกหักจากดอกเบี้ยที่ลูกค้าต้องจ่าย
            """
            
            QMessageBox.information(self, "รายงานหัก ณ ที่จ่าย", message)
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")
    
    def show_renewals_report(self):
        """แสดงรายงานการต่อดอก"""
        try:
            # ดึงข้อมูลการต่อดอกทั้งหมด
            renewals = self.db.get_all_renewals()
            
            if not renewals:
                QMessageBox.information(self, "รายงานการต่อดอก", "ไม่พบข้อมูลการต่อดอก")
                return
            
            # สร้างรายงาน
            total_renewals = len(renewals)
            total_fees = sum(renewal.get('fee_amount', 0) for renewal in renewals)
            total_penalties = sum(renewal.get('penalty_amount', 0) for renewal in renewals)
            total_discounts = sum(renewal.get('discount_amount', 0) for renewal in renewals)
            total_amount = sum(renewal.get('total_amount', 0) for renewal in renewals)
            
            # จัดกลุ่มตามสัญญา
            contracts_renewed = {}
            for renewal in renewals:
                contract_number = renewal.get('contract_number', 'ไม่ทราบ')
                if contract_number not in contracts_renewed:
                    contracts_renewed[contract_number] = 0
                contracts_renewed[contract_number] += 1
            
            message = f"""
รายงานการต่อดอก:

จำนวนการต่อดอกทั้งหมด: {total_renewals} ครั้ง
จำนวนสัญญาที่ต่อดอก: {len(contracts_renewed)} สัญญา

รายละเอียดยอดเงิน:
- ค่าธรรมเนียมรวม: {total_fees:,.2f} บาท
- ค่าปรับรวม: {total_penalties:,.2f} บาท
- ส่วนลดรวม: {total_discounts:,.2f} บาท
- ยอดรวม: {total_amount:,.2f} บาท

หมายเหตุ: การต่อดอกจะช่วยให้ลูกค้าสามารถขยายเวลาการไถ่ถอนสินค้าได้
            """
            
            QMessageBox.information(self, "รายงานการต่อดอก", message)
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")
    
    def calculate_withholding_tax(self):
        """คำนวณหัก ณ ที่จ่าย"""
        if not self.current_contract and not self.pawn_amount_spin.value():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกยอดฝากก่อน")
            return
        
        # คำนวณหัก ณ ที่จ่ายใหม่
        self.calculate_amounts()
        
        # แสดงผลลัพธ์
        withholding_tax_amount = float(self.withholding_tax_amount_label.text().replace(' บาท', '').replace(',', ''))
        total_paid = float(self.total_paid_label.text().replace(' บาท', '').replace(',', ''))
        
        message = f"""
การคำนวณหัก ณ ที่จ่าย:

ยอดฝาก: {self.pawn_amount_spin.value():,.2f} บาท
อัตราหัก ณ ที่จ่าย: {self.withholding_tax_rate_spin.value():.2f}%
ยอดหัก ณ ที่จ่าย: {withholding_tax_amount:,.2f} บาท
ยอดจ่ายจริง: {total_paid:,.2f} บาท

หัก ณ ที่จ่ายจะถูกหักจากดอกเบี้ยที่ลูกค้าต้องจ่าย
        """
        
        QMessageBox.information(self, "ผลการคำนวณหัก ณ ที่จ่าย", message)
        
        # ล้างตารางประวัติการต่อดอก
        if hasattr(self, 'renewal_history_table'):
            self.renewal_history_table.setRowCount(0)
    
    def update_withholding_tax_rate(self):
        """อัปเดตอัตราหัก ณ ที่จ่าย"""
        current_rate = self.withholding_tax_rate_spin.value()
        
        # อัปเดตในฐานข้อมูล
        if self.db.update_withholding_tax_rate(current_rate):
            QMessageBox.information(self, "สำเร็จ", f"อัปเดตอัตราหัก ณ ที่จ่ายเป็น {current_rate:.2f}% เรียบร้อย")
            
            # ล้างตารางประวัติการต่อดอก
            if hasattr(self, 'renewal_history_table'):
                self.renewal_history_table.setRowCount(0)
        else:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถอัปเดตอัตราหัก ณ ที่จ่ายได้")
    
    def show_fee_management(self):
        """แสดงหน้าต่างจัดการค่าธรรมเนียม"""
        dialog = FeeManagementDialog(self)
        dialog.fee_updated.connect(self.on_fee_updated)
        dialog.exec()
    
    def on_fee_updated(self):
        """เมื่อมีการอัปเดตข้อมูลค่าธรรมเนียม"""
        # รีเฟรชการคำนวณค่าธรรมเนียมในฟอร์ม
        self.calculate_amounts()
        
        # ล้างตารางประวัติการต่อดอก
        if hasattr(self, 'renewal_history_table'):
            self.renewal_history_table.setRowCount(0)

    def toggle_customer_mode(self):
        """สลับโหมดการเพิ่มลูกค้า"""
        if self.customer_info_group.isVisible():
            # สลับไปโหมดเพิ่มลูกค้าใหม่
            self.customer_info_group.hide()
            self.customer_add_group.show()
            # สร้างรหัสลูกค้าใหม่
            self.generate_new_customer_code()
            self.customer_add_group.setFocus()
        else:
            # สลับกลับไปโหมดแสดงข้อมูล
            self.customer_add_group.hide()
            self.customer_info_group.show()
            self.customer_info_group.setFocus()
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def save_new_customer(self):
        """บันทึกข้อมูลลูกค้าใหม่"""
        customer_code = self.customer_code_display_edit.text().strip()
        first_name = self.customer_first_name_edit.text().strip()
        last_name = self.customer_last_name_edit.text().strip()
        id_card = self.customer_id_card_edit.text().strip()
        house_number = self.customer_house_number_edit.text().strip()
        street = self.customer_street_edit.text().strip()
        subdistrict = self.customer_subdistrict_edit.text().strip()
        district = self.customer_district_edit.text().strip()
        province = self.customer_province_edit.text().strip()
        phone = self.customer_phone_edit.text().strip()
        other_details = self.customer_other_details_edit.text().strip()

        if not first_name or not last_name or not id_card:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกข้อมูลชื่อ, นามสกุล, และเลขบัตรประชาชน")
            return

        # ตรวจสอบความซ้ำซ้อนของรหัสลูกค้าและเลขบัตรประชาชน
        if self.db.check_customer_exists(customer_code=customer_code):
            QMessageBox.warning(self, "แจ้งเตือน", f"รหัสลูกค้า {customer_code} มีอยู่ในระบบแล้ว กรุณาสร้างรหัสใหม่")
            self.generate_new_customer_code()
            return
        
        if self.db.check_customer_exists(id_card=id_card):
            QMessageBox.warning(self, "แจ้งเตือน", f"เลขบัตรประชาชน {id_card} มีอยู่ในระบบแล้ว")
            return

        try:
            customer_data = {
                'customer_code': customer_code,
                'first_name': first_name,
                'last_name': last_name,
                'id_card': id_card,
                'house_number': house_number,
                'street': street,
                'subdistrict': subdistrict,
                'district': district,
                'province': province,
                'phone': phone,
                'other_details': other_details
            }
            new_customer_id = self.db.add_customer(customer_data)
            self.current_customer = self.db.get_customer_by_id(new_customer_id)
            self.load_customer_data()
            self.toggle_customer_mode()
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            
            QMessageBox.information(self, "สำเร็จ", f"เพิ่มลูกค้าเรียบร้อย\nรหัสลูกค้า: {customer_code}")
        except ValueError as e:
            QMessageBox.warning(self, "ข้อมูลซ้ำซ้อน", str(e))
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการเพิ่มลูกค้า: {str(e)}")

    def toggle_product_mode(self):
        """สลับโหมดการเพิ่มสินค้า"""
        if self.product_info_group.isVisible():
            # สลับไปโหมดเพิ่มสินค้าใหม่
            self.product_info_group.hide()
            self.product_add_group.show()
            # ล้างข้อมูลรูปภาพ
            self.product_add_image_path_edit.clear()
            self.product_image_preview.clear()
            self.product_image_preview.setText("ไม่มีรูปภาพ")
            self.product_add_group.setFocus()
        else:
            # สลับกลับไปโหมดแสดงข้อมูล
            self.product_add_group.hide()
            self.product_info_group.show()
            self.product_info_group.setFocus()
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def save_new_product(self):
        """บันทึกข้อมูลสินค้าใหม่"""
        name = self.product_add_name_edit.text().strip()
        brand = self.product_add_brand_edit.text().strip()
        size = self.product_add_size_edit.text().strip()
        weight_unit = self.product_add_weight_combo.currentText()
        serial_number = self.product_add_serial_edit.text().strip()
        other_details = self.product_add_details_edit.text().strip()
        image_path = self.product_add_image_path_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อสินค้า")
            return

        try:
            # คัดลอกรูปภาพไปยังโฟลเดอร์ของโปรแกรม
            if image_path:
                image_path = self.copy_product_image(image_path)
            
            product_data = {
                'name': name,
                'brand': brand,
                'size': size,
                'weight_unit': weight_unit,
                'serial_number': serial_number,
                'other_details': other_details,
                'image_path': image_path
            }
            new_product_id = self.db.add_product(product_data)
            self.current_product = self.db.get_product_by_id(new_product_id)
            self.load_product_data()
            self.toggle_product_mode()
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            
            QMessageBox.information(self, "สำเร็จ", "เพิ่มสินค้าเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการเพิ่มสินค้า: {str(e)}")

    def generate_new_customer_code(self):
        """สร้างรหัสลูกค้าใหม่"""
        try:
            prefix = self.db.get_setting('customer_prefix')
        except:
            prefix = "C"  # ใช้ค่าเริ่มต้นถ้าไม่มีในฐานข้อมูล
        
        # สร้างรหัสลูกค้าใหม่จากฐานข้อมูล
        customer_code = self.db.get_next_customer_code(prefix)
        self.customer_code_display_edit.setText(customer_code)
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def browse_product_image(self):
        """เลือกไฟล์รูปภาพสินค้า"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "เลือกไฟล์รูปภาพสินค้า", 
            "", 
            "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif);;All Files (*)", 
            options=options
        )
        if file_name:
            self.product_add_image_path_edit.setText(file_name)
            # แสดงรูปภาพตัวอย่าง
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                # ปรับขนาดรูปภาพให้พอดีกับ preview
                scaled_pixmap = pixmap.scaled(
                    self.product_image_preview.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.product_image_preview.setPixmap(scaled_pixmap)
            else:
                self.product_image_preview.setText("ไม่สามารถโหลดรูปภาพได้")
            
            # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def copy_product_image(self, source_path: str) -> str:
        """คัดลอกรูปภาพสินค้าไปยังโฟลเดอร์ของโปรแกรม (delegate to app_services)"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return svc_copy_product_image(source_path, base_dir)

    def generate_pawn_contract_pdf(self):
        """สร้างใบขายฝากเป็น PDF"""
        # ตรวจสอบว่ามีข้อมูลครบหรือไม่
        missing_data = []
        if not self.current_customer:
            missing_data.append("ลูกค้า")
        if not self.current_product:
            missing_data.append("สินค้า")
        
        if missing_data:
            if hasattr(self, 'current_contract') and self.current_contract:
                # ถ้ามีสัญญาแต่ไม่มีข้อมูลลูกค้าหรือสินค้า แสดงข้อความที่ชัดเจนขึ้น
                QMessageBox.warning(self, "แจ้งเตือน", 
                    f"ไม่พบข้อมูล{', '.join(missing_data)}ในสัญญา\n"
                    "กรุณาโหลดข้อมูลสัญญาใหม่อีกครั้ง หรือตรวจสอบฐานข้อมูล")
            else:
                QMessageBox.warning(self, "แจ้งเตือน", f"กรุณาเลือก{', '.join(missing_data)}ก่อนสร้างใบขายฝาก")
            return
        
        # ตรวจสอบว่ามีข้อมูลสัญญาพื้นฐานหรือไม่
        if not self.contract_number_edit.text().strip():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกเลขที่สัญญาก่อนสร้างใบขายฝาก")
            return
        
        try:
            # สร้างไฟล์ชั่วคราวสำหรับพรีวิว
            with tempfile.TemporaryDirectory() as tmpdir:
                contract_number = self.contract_number_edit.text() or "ใหม่"
                temp_file = os.path.join(tmpdir, f"pawn_preview_{contract_number}.pdf")

                # สร้าง PDF ลงไฟล์ชั่วคราว
                self._create_pawn_contract_pdf(temp_file)

                # เปิดด้วยโปรแกรมอ่าน PDF ภายนอกเสมอ และให้ตัวเลือกบันทึก
                self._open_pdf_external(temp_file)

                suggested_name = f"ใบขายฝาก_{contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "บันทึก PDF",
                    suggested_name,
                    "PDF Files (*.pdf)"
                )
                if save_path:
                    shutil.copyfile(temp_file, save_path)
                    QMessageBox.information(self, "สำเร็จ", f"บันทึกใบขายฝากแล้วที่:\n{save_path}")

        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการสร้าง/พรีวิว PDF: {str(e)}")

    def _create_pawn_contract_pdf(self, file_path):
        """สร้างไฟล์ PDF ใบขายฝากโดยใช้ฟังก์ชันจาก pdf.py"""
        try:
            # ตรวจสอบข้อมูลลูกค้าและสินค้าอีกครั้ง
            if not self.current_customer or not self.current_product:
                raise Exception("ข้อมูลลูกค้าหรือสินค้าไม่ครบถ้วน")
            
            # นำเข้าฟังก์ชันจาก pdf.py
            from pdf import generate_pawn_ticket_from_data
            
            # สร้างข้อมูลสัญญาจาก UI
            contract_data = {
                'contract_number': self.contract_number_edit.text(),
                'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
                'end_date': self.end_date_edit.text(),
                'days_count': self.days_spin.value(),
                'pawn_amount': self.pawn_amount_spin.value(),
                'interest_rate': self.interest_rate_spin.value(),
                'fee_amount': float(self.fee_amount_label.text().replace(' บาท', '').replace(',', '')),
                'withholding_tax_rate': self.withholding_tax_rate_spin.value(),
                'withholding_tax_amount': float(self.withholding_tax_amount_label.text().replace(' บาท', '').replace(',', '')),
                'total_paid': float(self.total_paid_label.text().replace(' บาท', '').replace(',', '')),
                'total_redemption': float(self.total_redemption_label.text().replace(' บาท', '').replace(',', ''))
            }
            
            # สร้างข้อมูลร้านค้า
            shop_data = {
                'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
                'branch': 'สาขาหล่มสัก',
                'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
            }
            
            # ดึงข้อมูลการต่อดอกจากฐานข้อมูล
            renewal_data = []
            if hasattr(self, 'current_contract') and self.current_contract:
                contract_id = self.current_contract.get('id')
                if contract_id:
                    renewal_data = self.db.get_renewals_by_contract(contract_id)
            
            # เรียกใช้ฟังก์ชันสร้าง PDF จาก pdf.py
            result = generate_pawn_ticket_from_data(
                contract_data=contract_data,
                customer_data=self.current_customer,
                product_data=self.current_product,
                shop_data=shop_data,
                output_file=file_path,
                renewal_data=renewal_data
            )
            
            if not result:
                raise Exception("ไม่สามารถสร้าง PDF ได้")
                
        except ImportError:
            # Fallback ไปใช้วิธีเดิมถ้าไม่สามารถ import pdf.py ได้
            self._create_pawn_contract_pdf_fallback(file_path)
        except Exception as e:
            # Fallback ไปใช้วิธีเดิมถ้าเกิดข้อผิดพลาด
            print(f"Error using pdf.py: {e}")
            self._create_pawn_contract_pdf_fallback(file_path)
    
    def _open_pdf_external(self, pdf_path: str):
        # delegate to app_services
        svc_open_pdf_external(pdf_path)

    def _create_pawn_contract_pdf_fallback(self, file_path):
        """สร้างไฟล์ PDF ใบขายฝากแบบเดิม (fallback)"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # สร้าง styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # center
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        )
        
        normal_style = styles['Normal']
        
        # หัวเอกสาร
        story.append(Paragraph("ใบขายฝาก", title_style))
        story.append(Spacer(1, 20))
        
        # ข้อมูลสัญญา
        story.append(Paragraph("ข้อมูลสัญญา", heading_style))
        contract_data = [
            ["เลขที่สัญญา:", self.contract_number_edit.text()],
            ["วันที่เริ่มต้น:", self.start_date_edit.date().toString("yyyy-MM-dd")],
            ["วันที่สิ้นสุด:", self.end_date_edit.text()],
            ["จำนวนวัน:", f"{self.days_spin.value()} วัน"]
        ]
        
        contract_table = Table(contract_data, colWidths=[4*cm, 8*cm])
        contract_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(contract_table)
        story.append(Spacer(1, 15))
        
        # ข้อมูลลูกค้า
        story.append(Paragraph("ข้อมูลลูกค้า", heading_style))
        
        # สร้างที่อยู่จากส่วนประกอบต่างๆ
        address_parts = [
            self.current_customer.get('house_number', ''),
            self.current_customer.get('street', ''),
            self.current_customer.get('subdistrict', ''),
            self.current_customer.get('district', ''),
            self.current_customer.get('province', '')
        ]
        address = ' '.join(filter(None, address_parts))
        
        customer_data = [
            ["รหัสลูกค้า:", self.current_customer.get('customer_code', '')],
            ["ชื่อ-นามสกุล:", f"{self.current_customer.get('first_name', '')} {self.current_customer.get('last_name', '')}"],
            ["เลขบัตรประชาชน:", self.current_customer.get('id_card', '')],
            ["ที่อยู่:", address],
            ["เบอร์โทรศัพท์:", self.current_customer.get('phone', '')]
        ]
        
        customer_table = Table(customer_data, colWidths=[4*cm, 8*cm])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 15))
        
        # ข้อมูลสินค้า
        story.append(Paragraph("ข้อมูลสินค้า", heading_style))
        product_data = [
            ["ชื่อสินค้า:", self.current_product['name']],
            ["ยี่ห้อ:", self.current_product['brand']],
            ["ขนาด:", self.current_product['size']],
            ["น้ำหนัก:", f"{self.current_product['weight']} {self.current_product['weight_unit']}"],
            ["เลขประจำเครื่อง:", self.current_product['serial_number']],
            ["รายละเอียดอื่นๆ:", self.current_product['other_details']]
        ]
        
        product_table = Table(product_data, colWidths=[4*cm, 8*cm])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(product_table)
        story.append(Spacer(1, 15))
        
        # ข้อมูลการเงิน
        story.append(Paragraph("ข้อมูลการเงิน", heading_style))
        financial_data = [
            ["ยอดฝาก:", f"{self.pawn_amount_spin.value():,.2f} บาท"],
            ["อัตราดอกเบี้ย:", f"{self.interest_rate_spin.value()}%"],
            ["ค่าธรรมเนียม:", self.fee_amount_label.text()],
            ["อัตราหัก ณ ที่จ่าย:", f"{self.withholding_tax_rate_spin.value()}%"],
            ["ยอดหัก ณ ที่จ่าย:", self.withholding_tax_amount_label.text()],
            ["ยอดจ่าย:", self.total_paid_label.text()],
            ["ยอดไถ่ถอน:", self.total_redemption_label.text()]
        ]
        
        financial_table = Table(financial_data, colWidths=[4*cm, 8*cm])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(financial_table)
        story.append(Spacer(1, 20))
        
        # เงื่อนไขและข้อตกลง
        story.append(Paragraph("เงื่อนไขและข้อตกลง", heading_style))
        terms = [
            "1. ลูกค้าต้องชำระดอกเบี้ยและค่าธรรมเนียมตามกำหนดเวลา",
            "2. หากไม่ชำระภายในกำหนด สินค้าจะตกเป็นของร้าน",
            "3. ลูกค้าสามารถไถ่ถอนสินค้าได้ตลอดเวลาก่อนครบกำหนด",
            "4. ร้านจะเก็บรักษาสินค้าให้อย่างดีและปลอดภัย",
            "5. หากสินค้าเสียหายจากเหตุสุดวิสัย ร้านไม่รับผิดชอบ"
        ]
        
        for term in terms:
            story.append(Paragraph(term, normal_style))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        
        # ลายเซ็น
        signature_data = [
            ["", ""],
            ["ลายเซ็นลูกค้า", "ลายเซ็นผู้รับฝาก"],
            ["", ""],
            ["วันที่:", "วันที่:"]
        ]
        
        signature_table = Table(signature_data, colWidths=[6*cm, 6*cm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(signature_table)
        
        # สร้าง PDF
        doc.build(story)

    def generate_renewal_contract_pdf(self):
        """สร้างใบฝากต่อ PDF"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        try:
            # ดึงข้อมูลลูกค้าและสินค้าเพิ่มเติม
            contract_id = self.current_contract['id']
            customer = self.db.get_customer_by_id(self.current_contract.get('customer_id'))
            product = self.db.get_product_by_id(self.current_contract.get('product_id'))
            
            if not customer or not product:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลลูกค้าหรือสินค้า")
                return
            
            # ดึงข้อมูลการต่อดอกล่าสุด
            renewals = []
            try:
                contract_number = self.current_contract.get('contract_number', '')
                if contract_number:
                    renewals = self.db.get_renewals_by_contract(contract_number)
            except:
                pass
            
            if not renewals:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลการต่อดอกของสัญญานี้\nกรุณาต่อดอกก่อนสร้างใบฝากต่อ")
                return
            
            # ใช้ข้อมูลการต่อดอกล่าสุด
            latest_renewal = renewals[-1]
            
            # สร้างข้อมูลการต่อดอกสำหรับ PDF
            renewal_data = {
                'renewal_date': latest_renewal.get('renewal_date', ''),
                'extension_days': latest_renewal.get('deposit_days', 0),
                'interest_amount': latest_renewal.get('fee_amount', 0),
                'fee_amount': latest_renewal.get('penalty_amount', 0),
                'total_amount': latest_renewal.get('total_amount', 0)
            }
            
            # สร้างข้อมูลสัญญาที่ครบถ้วน
            original_contract_data = {
                'contract_number': self.current_contract.get('contract_number', ''),
                'start_date': self.current_contract.get('start_date', ''),
                'end_date': self.current_contract.get('end_date', ''),
                'days_count': self.current_contract.get('days_count', 0),
                'pawn_amount': self.current_contract.get('pawn_amount', 0),
                'interest_rate': self.current_contract.get('interest_rate', 0),
                'estimated_value': self.current_contract.get('estimated_value', 0)
            }
            
            # สร้างข้อมูลลูกค้าที่ครบถ้วน
            customer_data = {
                'customer_code': customer.get('customer_code', ''),
                'first_name': customer.get('first_name', ''),
                'last_name': customer.get('last_name', ''),
                'phone': customer.get('phone', ''),
                'id_card': customer.get('id_card', ''),
                'house_number': customer.get('house_number', ''),
                'street': customer.get('street', ''),
                'subdistrict': customer.get('subdistrict', ''),
                'district': customer.get('district', ''),
                'province': customer.get('province', '')
            }
            
            # สร้างข้อมูลสินค้าที่ครบถ้วน
            product_data = {
                'name': product.get('name', ''),
                'brand': product.get('brand', ''),
                'size': product.get('size', ''),
                'weight': product.get('weight', ''),
                'weight_unit': product.get('weight_unit', ''),
                'serial_number': product.get('serial_number', ''),
                'other_details': product.get('other_details', '')
            }
            
            # ข้อมูลร้านค้า
            shop_data = {
                'name': 'ร้าน ไอโปรโมบายเซอร์วิส',
                'branch': 'สาขาหล่มสัก',
                'address': '14-15 ถ.พินิจ ต.หล่มสัก อ.หล่มสัก จ.เพชรบูรณ์ 67110'
            }
            
            # นำเข้า pdf2.py
            try:
                from pdf2 import generate_renewal_contract_pdf
                
                # สร้างชื่อไฟล์
                contract_number = self.current_contract.get('contract_number', 'unknown')
                renewal_date = renewal_data['renewal_date'].replace('-', '') if renewal_data['renewal_date'] else datetime.now().strftime('%Y%m%d')
                
                # สร้างไฟล์ชั่วคราวสำหรับพรีวิว และแสดงพรีวิว
                with tempfile.TemporaryDirectory() as tmpdir:
                    temp_file = os.path.join(tmpdir, f"renewal_preview_{contract_number}_{renewal_date}.pdf")
                    result = generate_renewal_contract_pdf(
                        original_contract_data=original_contract_data,
                        customer_data=customer_data,
                        product_data=product_data,
                        renewal_data=renewal_data,
                        shop_data=shop_data,
                        output_file=os.path.basename(temp_file),
                        output_folder=tmpdir
                    )

                    if not result:
                        QMessageBox.warning(self, "แจ้งเตือน", "สร้างใบฝากต่อไม่สำเร็จ")
                        return

                    # เปิดด้วยโปรแกรมอ่าน PDF ภายนอกเสมอ และให้ตัวเลือกบันทึก
                    self._open_pdf_external(temp_file)

                    suggested_name = f"renewal_contract_{contract_number}_{renewal_date}.pdf"
                    save_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "บันทึก PDF ใบฝากต่อ",
                        suggested_name,
                        "PDF Files (*.pdf)"
                    )
                    if save_path:
                        shutil.copyfile(temp_file, save_path)
                        QMessageBox.information(self, "สำเร็จ", f"บันทึกใบฝากต่อแล้วที่:\n{save_path}")
                    
            except ImportError:
                QMessageBox.critical(self, "ผิดพลาด", "ไม่สามารถนำเข้า pdf2.py ได้\nกรุณาตรวจสอบว่าไฟล์ pdf2.py อยู่ในโฟลเดอร์เดียวกัน")
            except Exception as e:
                QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการสร้าง PDF: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def fix_database_duplicates(self):
        """แก้ไขปัญหาข้อมูลซ้ำซ้อนในฐานข้อมูล"""
        try:
            # แก้ไขปัญหารหัสลูกค้าซ้ำซ้อน
            customer_codes_fixed = self.db.fix_duplicate_customer_codes()
            
            # แก้ไขปัญหาเลขบัตรประชาชนซ้ำซ้อน
            id_cards_fixed = self.db.fix_duplicate_id_cards()
            
            if customer_codes_fixed > 0 or id_cards_fixed > 0:
                message = f"แก้ไขข้อมูลซ้ำซ้อนเรียบร้อย:\n"
                if customer_codes_fixed > 0:
                    message += f"- รหัสลูกค้าซ้ำซ้อน: {customer_codes_fixed} รายการ\n"
                if id_cards_fixed > 0:
                    message += f"- เลขบัตรประชาชนซ้ำซ้อน: {id_cards_fixed} รายการ"
                
                QMessageBox.information(self, "สำเร็จ", message)
                
                # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
            else:
                QMessageBox.information(self, "ไม่พบปัญหา", "ไม่พบข้อมูลซ้ำซ้อนในฐานข้อมูล")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการแก้ไขข้อมูลซ้ำซ้อน: {str(e)}")

    # Methods for renewal tab functionality
    def search_renewals(self):
        """ค้นหาการต่อดอกตามเลขที่สัญญา"""
        contract_number = self.renewal_contract_search_edit.text().strip()
        if not contract_number:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกเลขที่สัญญา")
            return
        
        try:
            # ค้นหาสัญญาในฐานข้อมูล
            contracts = self.db.search_contracts_by_number(contract_number, 'active')
            if contracts:
                contract = contracts[0]
                self.load_renewal_contract_data(contract)
                self.load_renewal_history(contract_number)
            else:
                QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสัญญาที่มีเลขที่นี้")
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")

    def load_renewal_contract_data(self, contract: dict):
        """โหลดข้อมูลสัญญาสำหรับการต่อดอก"""
        # ข้อมูลสัญญา
        self.renewal_contract_number_edit.setText(contract.get('contract_number', ''))
        
        # ข้อมูลลูกค้า
        customer_name = "{} {}".format(
            contract.get('first_name', ''), 
            contract.get('last_name', '')
        )
        self.renewal_customer_name_edit.setText(customer_name)
        
        # ข้อมูลสินค้า
        self.renewal_product_name_edit.setText(contract.get('product_name', ''))
        
        # ยอดจำนำ
        pawn_amount = contract.get('pawn_amount', 0)
        self.renewal_pawn_amount_edit.setText(f"{pawn_amount:,.2f}")
        
        # วันที่ครบกำหนดเดิม
        end_date = contract.get('end_date', '')
        if end_date:
            try:
                if isinstance(end_date, str):
                    if '-' in end_date:
                        date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    else:
                        date_obj = datetime.strptime(end_date, "%d/%m/%Y")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    self.renewal_original_due_date_edit.setText(formatted_date)
            except:
                self.renewal_original_due_date_edit.setText(end_date)
        
        # คำนวณวันที่ครบกำหนดใหม่
        self.calculate_renewal_dates()
        
        # โหลดประวัติการต่อดอก
        contract_number = contract.get('contract_number', '')
        if contract_number:
            self.load_renewal_history(contract_number)

    def load_renewal_history(self, contract_number: str):
        """โหลดประวัติการต่อดอก"""
        try:
            renewals = self.db.get_renewals_by_contract(contract_number)
            self.display_renewal_history(renewals)
        except Exception as e:
            print(f"Error loading renewal history: {e}")

    def display_renewal_history(self, renewals: list):
        """แสดงประวัติการต่อดอกในตาราง"""
        self.renewal_history_table.setRowCount(len(renewals))
        
        for row, renewal in enumerate(renewals):
            # ลำดับ
            self.renewal_history_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # วันที่ต่อดอก
            renewal_date = renewal.get('renewal_date', '')
            if renewal_date:
                try:
                    date_obj = datetime.strptime(renewal_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    self.renewal_history_table.setItem(row, 1, QTableWidgetItem(formatted_date))
                except:
                    self.renewal_history_table.setItem(row, 1, QTableWidgetItem(renewal_date))
            else:
                self.renewal_history_table.setItem(row, 1, QTableWidgetItem(""))
            
            # จำนวนวันต่อ
            extension_days = renewal.get('deposit_days', 0)
            self.renewal_history_table.setItem(row, 2, QTableWidgetItem(str(extension_days)))
            
            # ค่าธรรมเนียม
            fee_amount = renewal.get('fee_amount', 0)
            self.renewal_history_table.setItem(row, 3, QTableWidgetItem(f"{fee_amount:,.2f}"))
            
            # ค่าปรับ
            penalty_amount = renewal.get('penalty_amount', 0)
            self.renewal_history_table.setItem(row, 4, QTableWidgetItem(f"{penalty_amount:,.2f}"))
            
            # ส่วนลด
            discount_amount = renewal.get('discount_amount', 0)
            self.renewal_history_table.setItem(row, 5, QTableWidgetItem(f"{discount_amount:,.2f}"))
            
            # ยอดรวม
            total_amount = renewal.get('total_amount', 0)
            self.renewal_history_table.setItem(row, 6, QTableWidgetItem(f"{total_amount:,.2f}"))
            
            # วันที่ครบกำหนดใหม่
            new_due_date = renewal.get('new_due_date', '')
            if new_due_date:
                try:
                    date_obj = datetime.strptime(new_due_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    self.renewal_history_table.setItem(row, 7, QTableWidgetItem(formatted_date))
                except:
                    self.renewal_history_table.setItem(row, 7, QTableWidgetItem(new_due_date))
            else:
                self.renewal_history_table.setItem(row, 7, QTableWidgetItem(""))
        
        # แสดงข้อมูลประวัติการต่อดอกเรียบร้อยแล้ว

    def calculate_renewal_dates(self):
        """คำนวณวันที่ครบกำหนดใหม่"""
        try:
            original_due_date = self.renewal_original_due_date_edit.text()
            if original_due_date:
                # แปลงวันที่จาก dd/mm/yyyy เป็น datetime object
                date_obj = datetime.strptime(original_due_date, "%d/%m/%Y")
                extension_days = self.renewal_extension_days_spin.value()
                
                # คำนวณวันที่ใหม่
                new_date = date_obj + timedelta(days=extension_days)
                new_date_str = new_date.strftime("%d/%m/%Y")
                
                self.renewal_new_due_date_edit.setText(new_date_str)
        except Exception as e:
            print(f"Error calculating renewal dates: {e}")

    def calculate_renewal_total(self):
        """คำนวณยอดรวมการต่อดอก"""
        fee_amount = self.renewal_fee_amount_spin.value()
        penalty_amount = self.renewal_penalty_amount_spin.value()
        discount_amount = self.renewal_discount_amount_spin.value()
        
        total = fee_amount + penalty_amount - discount_amount
        self.renewal_total_amount_label.setText(f"{total:,.2f} บาท")

    def process_renewal(self):
        """ดำเนินการต่อดอก"""
        contract_number = self.renewal_contract_number_edit.text().strip()
        if not contract_number:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาค้นหาสัญญาก่อนดำเนินการต่อดอก")
            return
        
        # ตรวจสอบข้อมูลที่จำเป็น
        extension_days = self.renewal_extension_days_spin.value()
        fee_amount = self.renewal_fee_amount_spin.value()
        
        if extension_days <= 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาระบุจำนวนวันต่อดอก")
            return
        
        if fee_amount <= 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาระบุค่าธรรมเนียมต่อดอก")
            return
        
        try:
            # สร้างข้อมูลการต่อดอก
            renewal_data = {
                'contract_number': contract_number,
                'extension_days': extension_days,
                'fee_amount': fee_amount,
                'penalty_amount': self.renewal_penalty_amount_spin.value(),
                'discount_amount': self.renewal_discount_amount_spin.value(),
                'total_amount': float(self.renewal_total_amount_label.text().replace(' บาท', '').replace(',', '')),
                'renewal_date': datetime.now().strftime("%Y-%m-%d"),
                'new_due_date': datetime.strptime(self.renewal_new_due_date_edit.text(), "%d/%m/%Y").strftime("%Y-%m-%d")
            }
            
            # บันทึกการต่อดอกในฐานข้อมูล
            renewal_id = self.db.add_renewal(renewal_data)
            
            if renewal_id:
                # อัปเดตวันที่ครบกำหนดใหม่ในสัญญา
                self.db.update_contract_end_date(contract_number, renewal_data['new_due_date'])
                
                QMessageBox.information(self, "สำเร็จ", "ดำเนินการต่อดอกเรียบร้อยแล้ว")
                
                # รีเฟรชข้อมูล
                self.load_renewal_history(contract_number)
                
                # อัปเดตข้อมูลสัญญาปัจจุบันในฟอร์มหลัก
                if self.current_contract and self.current_contract.get('contract_number') == contract_number:
                    # โหลดข้อมูลสัญญาใหม่
                    updated_contract = self.db.get_contract_by_id(self.current_contract['id'])
                    if updated_contract:
                        self.current_contract = updated_contract
                        self.load_contract_data()
                
                self.clear_renewal_form()
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถดำเนินการต่อดอกได้")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการดำเนินการต่อดอก: {str(e)}")

    def clear_renewal_search(self):
        """ล้างการค้นหาการต่อดอก"""
        self.renewal_contract_search_edit.clear()
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ
        
        # ล้างฟอร์มการต่อดอก
        self.clear_renewal_form()

    def clear_renewal_form(self):
        """ล้างฟอร์มการต่อดอก"""
        self.renewal_contract_number_edit.clear()
        self.renewal_customer_name_edit.clear()
        self.renewal_product_name_edit.clear()
        self.renewal_pawn_amount_edit.clear()
        self.renewal_original_due_date_edit.clear()
        self.renewal_extension_days_spin.setValue(30)
        self.renewal_new_due_date_edit.clear()
        self.renewal_fee_amount_spin.setValue(0)
        self.renewal_penalty_amount_spin.setValue(0)
        self.renewal_discount_amount_spin.setValue(0)
        self.renewal_total_amount_label.setText("0.00 บาท")
        
        # ไม่ล้างตารางประวัติการต่อดอก เพื่อให้แสดงข้อมูลประวัติ

    def load_additional_contract_data(self, contract: dict):
        """โหลดข้อมูลลูกค้าและสินค้าเพิ่มเติม"""
        try:
            # โหลดข้อมูลลูกค้าเพิ่มเติม
            customer_id = contract.get('customer_id')
            if customer_id:
                customer = self.db.get_customer_by_id(customer_id)
                if customer:
                    # ตั้งค่า current_customer เพื่อใช้ในการสร้าง PDF
                    self.current_customer = customer
                    
                    # โหลดข้อมูลที่อยู่
                    self.customer_code_edit.setText(customer.get('customer_code', ''))
                    self.customer_address_edit.setText(customer.get('address', ''))
                    self.id_card_edit.setText(customer.get('id_card', ''))
                    self.house_number_edit.setText(customer.get('house_number', ''))
                    self.street_edit.setText(customer.get('street', ''))
                    self.subdistrict_edit.setText(customer.get('subdistrict', ''))
                    self.district_edit.setText(customer.get('district', ''))
                    self.province_edit.setText(customer.get('province', ''))
                    self.phone_edit.setText(customer.get('phone', ''))
                    self.other_details_edit.setText(customer.get('other_details', ''))
            
            # โหลดข้อมูลสินค้าเพิ่มเติม
            product_id = contract.get('product_id')
            if product_id:
                product = self.db.get_product_by_id(product_id)
                if product:
                    # ตั้งค่า current_product เพื่อใช้ในการสร้าง PDF
                    self.current_product = product
                    
                    self.product_name_edit.setText(product.get('name', ''))
                    self.product_brand_edit.setText(product.get('brand', ''))
                    self.product_size_edit.setText(product.get('size', ''))
                    self.serial_number_edit.setText(product.get('serial_number', ''))
                    self.product_details_edit.setText(product.get('other_details', ''))
                    
                    # แสดงรูปภาพสินค้า
                    image_path = product.get('image_path', '')
                    if image_path and os.path.exists(image_path):
                        pixmap = QPixmap(image_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(
                                self.product_image_display.size(), 
                                Qt.KeepAspectRatio, 
                                Qt.SmoothTransformation
                            )
                            self.product_image_display.setPixmap(scaled_pixmap)
                        else:
                            self.product_image_display.setText("ไม่สามารถโหลดรูปภาพได้")
                    else:
                        self.product_image_display.setText("ไม่มีรูปภาพ")
                        
        except Exception as e:
            print(f"Error loading additional contract data: {e}")

    def on_contract_table_clicked(self, item):
        """เมื่อมีการคลิกในตาราง"""
        try:
            # หาแถวที่คลิก
            row = item.row()
            contract_id = self.contract_table.item(row, 0).data(Qt.UserRole)
            
            if contract_id:
                # ค้นหาสัญญาตาม ID
                contract = self.db.get_contract_by_id(contract_id)
                if contract:
                    # อัปเดตสัญญาปัจจุบัน
                    self.current_contract = contract
                    
                    # โหลดข้อมูลในฟอร์ม
                    self.load_contract_data()
                    
                    # โหลดข้อมูลลูกค้าและสินค้าเพิ่มเติม
                    self.load_additional_contract_data(contract)
                    
                    # โหลดประวัติการต่อดอก
                    contract_number = contract.get('contract_number', '')
                    if contract_number:
                        self.load_renewal_history(contract_number)
                    
                    # แสดงข้อความแจ้งเตือน
                    customer_name = f"{self.current_customer.get('first_name', '')} {self.current_customer.get('last_name', '')}" if self.current_customer else "ไม่พบข้อมูล"
                    product_name = self.current_product.get('name', 'ไม่พบข้อมูล') if self.current_product else "ไม่พบข้อมูล"
                    
                    QMessageBox.information(self, "โหลดข้อมูล", 
                        f"โหลดข้อมูลสัญญา {contract.get('contract_number', '')} เรียบร้อยแล้ว\n"
                        f"ลูกค้า: {customer_name}\n"
                        f"สินค้า: {product_name}")
                    
        except Exception as e:
            print(f"Error handling table click: {e}")

    def show_daily_income_summary(self):
        """แสดงสรุปรายได้รายวันและส่งเข้า Line"""
        try:
            # รับวันที่ปัจจุบัน
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # คำนวณรายได้รายวัน
            daily_income = self.calculate_daily_income(current_date)
            
            # แสดง dialog สรุปรายได้รายวัน
            self.show_daily_income_dialog(daily_income, current_date)
            
            # ส่งสรุปรายได้รายวันเข้า Line
            if ENABLE_LINE_NOTIFICATION:
                self.send_daily_income_to_line(daily_income, current_date)
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการคำนวณรายได้รายวัน: {str(e)}")

    def calculate_daily_income(self, date):
        """คำนวณรายได้รายวัน"""
        try:
            daily_income = {
                'date': date,
                'new_contracts': 0,
                'renewals': 0,
                'redemptions': 0,
                'total_interest': 0.0,
                'total_fees': 0.0,
                'total_renewal_fees': 0.0,
                'total_redemption_amount': 0.0,
                'net_income': 0.0
            }
            
            # นับสัญญาใหม่
            new_contracts = self.db.get_contracts_by_date(date)
            daily_income['new_contracts'] = len(new_contracts)
            
            # คำนวณดอกเบี้ยจากสัญญาใหม่
            for contract in new_contracts:
                daily_income['total_interest'] += contract.get('fee_amount', 0)
                daily_income['total_fees'] += contract.get('fee_amount', 0)
            
            # นับการต่อดอก
            renewals = self.db.get_renewals_by_date(date)
            daily_income['renewals'] = len(renewals)
            
            # คำนวณค่าธรรมเนียมการต่อดอก
            for renewal in renewals:
                daily_income['total_renewal_fees'] += renewal.get('fee_amount', 0)
                daily_income['total_fees'] += renewal.get('fee_amount', 0)
            
            # นับการไถ่ถอน
            redemptions = self.db.get_redemptions_by_date(date)
            daily_income['redemptions'] = len(redemptions)
            
            # คำนวณจำนวนเงินไถ่ถอน
            for redemption in redemptions:
                daily_income['total_redemption_amount'] += redemption.get('amount', 0)
            
            # คำนวณรายได้สุทธิ
            daily_income['net_income'] = daily_income['total_fees'] - daily_income['total_redemption_amount']
            
            return daily_income
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการคำนวณรายได้รายวัน: {str(e)}")
            return None

    def show_daily_income_dialog(self, daily_income, date):
        """แสดง dialog สรุปรายได้รายวัน"""
        if not daily_income:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถคำนวณรายได้รายวันได้")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"สรุปรายได้รายวัน - {date}")
        dialog.setModal(True)
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # หัวข้อ
        title_label = QLabel(f"📊 สรุปรายได้รายวัน - {date}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # ตารางสรุป
        summary_table = QTableWidget()
        summary_table.setColumnCount(2)
        summary_table.setRowCount(8)
        summary_table.setHorizontalHeaderLabels(["รายการ", "จำนวน/จำนวนเงิน"])
        
        # ข้อมูลในตาราง
        summary_data = [
            ("📋 สัญญาใหม่", f"{daily_income['new_contracts']} สัญญา"),
            ("🔄 การต่อดอก", f"{daily_income['renewals']} ครั้ง"),
            ("💎 การไถ่ถอน", f"{daily_income['redemptions']} ครั้ง"),
            ("💰 ดอกเบี้ยรวม", f"{daily_income['total_interest']:,.2f} บาท"),
            ("💸 ค่าธรรมเนียมการต่อดอก", f"{daily_income['total_renewal_fees']:,.2f} บาท"),
            ("💵 ค่าธรรมเนียมรวม", f"{daily_income['total_fees']:,.2f} บาท"),
            ("💎 จำนวนเงินไถ่ถอน", f"{daily_income['total_redemption_amount']:,.2f} บาท"),
            ("📈 รายได้สุทธิ", f"{daily_income['net_income']:,.2f} บาท")
        ]
        
        for row, (label, value) in enumerate(summary_data):
            summary_table.setItem(row, 0, QTableWidgetItem(label))
            summary_table.setItem(row, 1, QTableWidgetItem(value))
            
            # ตั้งค่าสีสำหรับรายได้สุทธิ
            if row == 7:  # รายได้สุทธิ
                if daily_income['net_income'] > 0:
                    summary_table.item(row, 1).setBackground(Qt.green)
                    summary_table.item(row, 1).setForeground(Qt.white)
                elif daily_income['net_income'] < 0:
                    summary_table.item(row, 1).setBackground(Qt.red)
                    summary_table.item(row, 1).setForeground(Qt.white)
        
        summary_table.resizeColumnsToContents()
        summary_table.setAlternatingRowColors(True)
        layout.addWidget(summary_table)
        
        # ปุ่มปิด
        close_button = QPushButton("ปิด")
        close_button.clicked.connect(dialog.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        layout.addWidget(close_button)
        
        dialog.exec()

    def send_daily_income_to_line(self, daily_income, date):
        """ส่งสรุปรายได้รายวันเข้า Line"""
        if not ENABLE_LINE_NOTIFICATION or not SEND_DAILY_INCOME_NOTIFICATION:
            return
            
        try:
            # ใช้ template จาก config
            line_message = MESSAGE_TEMPLATE['daily_income'].format(
                date=date,
                new_contracts=daily_income['new_contracts'],
                renewals=daily_income['renewals'],
                redemptions=daily_income['redemptions'],
                total_interest=daily_income['total_interest'],
                total_renewal_fees=daily_income['total_renewal_fees'],
                total_fees=daily_income['total_fees'],
                total_redemption_amount=daily_income['total_redemption_amount'],
                net_income=daily_income['net_income'],
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # ส่งข้อความเข้า Line
            success = self.send_line_message(line_message)
            
            if success:
                print("ส่งสรุปรายได้รายวันเข้า Line สำเร็จ")
                QMessageBox.information(self, "สำเร็จ", "ส่งสรุปรายได้รายวันเข้า Line เรียบร้อยแล้ว")
            else:
                print("ส่งสรุปรายได้รายวันเข้า Line ไม่สำเร็จ")
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถส่งสรุปรายได้รายวันเข้า Line ได้")
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการส่งสรุปรายได้รายวันเข้า Line: {str(e)}")
            QMessageBox.warning(self, "แจ้งเตือน", f"เกิดข้อผิดพลาดในการส่งข้อมูลเข้า Line: {str(e)}")

    def scan_id_card(self):
        """สแกนบัตรประชาชนและเพิ่มข้อมูลลูกค้า"""
        try:
            # ตรวจสอบสถานะ card reader ก่อน
            if not self.check_card_reader_status():
                return
            
            # แสดงข้อความแนะนำ
            QMessageBox.information(self, "คำแนะนำ", 
                "กรุณาใส่บัตรประชาชนใน card reader ก่อนคลิกตกลง\n\n"
                "หากยังไม่ใส่บัตร ระบบจะแสดงข้อความแจ้งเตือน")
            
            # สร้างและเริ่มการสแกนในเธรดแยก
            from dialogs import ThaiIDCardScanner
            self.card_scanner = ThaiIDCardScanner()
            self.card_scanner.card_data_ready.connect(self.on_card_data_ready)
            self.card_scanner.error_occurred.connect(self.on_scan_error)
            
            # แสดง progress dialog
            from PySide6.QtWidgets import QProgressDialog
            self.progress_dialog = QProgressDialog("กำลังสแกนบัตรประชาชน...", "ยกเลิก", 0, 100, self)
            self.progress_dialog.setWindowTitle("สแกนบัตรประชาชน")
            self.progress_dialog.setModal(True)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setAutoReset(False)
            
            # เชื่อมต่อ progress
            self.card_scanner.progress_updated.connect(self.progress_dialog.setValue)
            self.card_scanner.progress_updated.connect(lambda: self.progress_dialog.setLabelText("กำลังสแกนบัตรประชาชน..."))
            
            # เริ่มการสแกน
            self.card_scanner.start()
            self.progress_dialog.show()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"ไม่สามารถเริ่มการสแกนได้: {str(e)}")
    
    def check_card_reader_status(self):
        """ตรวจสอบสถานะ card reader"""
        try:
            from smartcard.System import readers
            
            reader_list = readers()
            if not reader_list:
                QMessageBox.warning(self, "แจ้งเตือน", 
                    "ไม่พบ card reader\n\nกรุณาตรวจสอบ:\n"
                    "1. Card reader เชื่อมต่อ USB หรือไม่\n"
                    "2. Driver ติดตั้งแล้วหรือไม่\n"
                    "3. PC/SC service ทำงานอยู่หรือไม่")
                return False
            
            # แสดงข้อมูล card reader ที่พบ
            reader_info = f"พบ card reader: {len(reader_list)} ตัว\n"
            for i, reader in enumerate(reader_list):
                reader_info += f"  {i}: {reader}\n"
            
            # ตรวจสอบการเชื่อมต่อแบบเบา (ไม่ต้องมีบัตร)
            try:
                reader = reader_list[0]
                # ไม่ต้องเชื่อมต่อกับบัตร เพียงแค่ตรวจสอบว่า reader พร้อมใช้งาน
                print(f"Card reader พร้อมใช้งาน: {reader}")
                return True
                
            except Exception as e:
                print(f"ข้อผิดพลาดในการตรวจสอบ card reader: {e}")
                # แม้จะตรวจสอบไม่สำเร็จ แต่ให้ลองสแกนต่อไป
                return True
                
        except ImportError:
            QMessageBox.critical(self, "ผิดพลาด", 
                "ไม่พบโมดูล smartcard\n\nกรุณาติดตั้งด้วยคำสั่ง:\npip install pyscard")
            return False
        except Exception as e:
            print(f"ข้อผิดพลาดในการตรวจสอบ card reader: {e}")
            # แม้จะตรวจสอบไม่สำเร็จ แต่ให้ลองสแกนต่อไป
            return True
    
    def on_card_data_ready(self, card_data):
        """เมื่อได้ข้อมูลบัตรแล้ว"""
        try:
            # ปิด progress dialog
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.close()
            
            # แสดงข้อมูลที่ได้
            info_text = "ข้อมูลที่ได้จากบัตร:\n"
            for key, value in card_data.items():
                if key != "photo" and value:  # ไม่แสดงรูปภาพ
                    info_text += f"{key}: {value}\n"
            
            # ถามว่าต้องการใช้ข้อมูลนี้หรือไม่
            reply = QMessageBox.question(
                self, 
                "ข้อมูลบัตรประชาชน", 
                f"{info_text}\nต้องการใช้ข้อมูลนี้เพื่อเพิ่มลูกค้าใหม่หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # เปิดหน้าจอเพิ่มข้อมูลลูกค้าและกรอกข้อมูลจากบัตร
                self.open_customer_dialog_with_card_data(card_data)
            
            QMessageBox.information(self, "สำเร็จ", "อ่านข้อมูลบัตรประชาชนเรียบร้อย")
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการประมวลผลข้อมูล: {str(e)}")
        finally:
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.close()
    
    def on_scan_error(self, error_message):
        """เมื่อเกิดข้อผิดพลาดในการสแกน"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        # แสดงข้อความแจ้งเตือนที่เหมาะสม
        if "No card" in error_message or "No smart card inserted" in error_message:
            QMessageBox.information(self, "แจ้งเตือน", 
                "ไม่พบบัตรประชาชนใน card reader\n\n"
                "กรุณาใส่บัตรประชาชนใน card reader แล้วลองใหม่อีกครั้ง")
        elif "Card is unresponsive" in error_message:
            QMessageBox.warning(self, "แจ้งเตือน", 
                "บัตรประชาชนไม่ตอบสนอง\n\n"
                "กรุณาลอง:\n"
                "1. ลบและใส่บัตรใหม่\n"
                "2. ทำความสะอาดหน้าสัมผัสของบัตร\n"
                "3. ตรวจสอบว่าบัตรเสียหายหรือไม่")
        elif "Unable to connect" in error_message:
            QMessageBox.warning(self, "แจ้งเตือน", 
                "ไม่สามารถเชื่อมต่อกับ card reader ได้\n\n"
                "กรุณาตรวจสอบ:\n"
                "1. การเชื่อมต่อ USB\n"
                "2. Driver ของ card reader\n"
                "3. PC/SC service ทำงานอยู่หรือไม่")
        else:
            QMessageBox.warning(self, "แจ้งเตือน", error_message)
    
    def open_customer_dialog_with_card_data(self, card_data):
        """เปิดหน้าจอเพิ่มข้อมูลลูกค้าพร้อมข้อมูลจากบัตร"""
        try:
            # สร้างหน้าจอเพิ่มข้อมูลลูกค้า
            customer_dialog = CustomerDialog(self)
            
            # กรอกข้อมูลจากบัตรลงในฟอร์ม
            customer_dialog.fill_form_with_card_data(card_data)
            
            # บันทึกรูปภาพถ้ามี
            if "photo" in card_data and card_data["photo"]:
                customer_dialog.save_card_photo(card_data["photo"], card_data.get("CID", "unknown"))
            
            # แสดงหน้าจอ
            if customer_dialog.exec():
                # หากบันทึกสำเร็จ ให้อัปเดตข้อมูลลูกค้าปัจจุบัน
                if customer_dialog.customer_data:
                    self.current_customer = customer_dialog.customer_data
                    self.load_customer_data()
                    QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลลูกค้าจากบัตรประชาชนเรียบร้อย")
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"ไม่สามารถเปิดหน้าจอเพิ่มข้อมูลลูกค้าได้: {str(e)}")

    def show_pdf_generation_dialog(self, contract_data):
        """แสดง dialog ให้เลือกสร้าง PDF หลังจากบันทึกสัญญา"""
        try:
            reply = QMessageBox.question(
                self,
                "สร้าง PDF ใบขายฝาก",
                "บันทึกสัญญาเรียบร้อยแล้ว\n\nต้องการสร้าง PDF ใบขายฝากหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # เรียกใช้ฟังก์ชันสร้าง PDF
                self.generate_pawn_contract_pdf()
                
        except Exception as e:
            print(f"Error showing PDF dialog: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Force a consistent light theme regardless of OS dark mode
    app.setStyle("Fusion")
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window, QColor(248, 249, 250))
    light_palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
    light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
    light_palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ToolTipText, QColor(33, 37, 41))
    light_palette.setColor(QPalette.Text, QColor(33, 37, 41))
    light_palette.setColor(QPalette.Button, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
    light_palette.setColor(QPalette.BrightText, QColor(220, 53, 69))
    light_palette.setColor(QPalette.Highlight, QColor(0, 123, 255))
    light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    light_palette.setColor(QPalette.PlaceholderText, QColor(108, 117, 125))
    app.setPalette(light_palette)
    window = PawnShopUI()
    window.show()
    sys.exit(app.exec())