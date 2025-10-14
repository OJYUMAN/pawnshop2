import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QToolBar,
    QMenuBar, QMessageBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit,
    QScrollArea, QFrame, QFileDialog, QDialog, QProgressDialog, QInputDialog,
    QSizePolicy
)
from resource_path import resource_path, get_font_path, get_icon_path
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
#hi
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
        self.setMinimumSize(1024, 700)
        self.resize(1600, 900)

        # Apply modern styles for better UI appearance
        self.setStyleSheet("""
/* ========== THEME: Minimal Pro (Colorful, Clean) ========== */
/* พาเลตต์มืออาชีพ */
 /* Surface BG  */  /* #F6F8FB */
 /* Card BG     */  /* #FFFFFF */
 /* Border      */  /* #E5EAF2 */
 /* Text main   */  /* #0F172A */
 /* Text mute   */  /* #64748B */
 /* Primary     */  /* #3B82F6 */
 /* Teal        */  /* #06B6D4 */
 /* Violet      */  /* #7C3AED */
 /* Emerald     */  /* #10B981 */
 /* Amber       */  /* #F59E0B */
 /* Rose        */  /* #F43F5E */

QWidget {
  font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
  font-size: 12px;
  color: #0F172A;
  background: #F6F8FB;
}

/* ---------------- Card / Group ---------------- */
QGroupBox {
  margin-top: 12px;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  border-radius: 12px;
  font-weight: 600;
  color: #0F172A;
  padding-top: 18px;
}
QGroupBox::title {
  subcontrol-origin: margin;
  subcontrol-position: top left;
  margin-left: 12px;
  padding: 0 8px;
  color: #64748B;
}

/* ซ่อน title บล็อกบน 3 ใบ แต่คงสีโทนอ่อนให้พอมีชีวิตชีวา */
#TopLeftGroup, #TopMiddleGroup, #SearchGroup { margin-top: 0; }
#TopLeftGroup::title, #TopMiddleGroup::title, #SearchGroup::title {
  height: 0; margin: 0; padding: 0; color: transparent;
}
#TopLeftGroup   { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                      stop:0 rgba(16,185,129,0.08), stop:1 #FFFFFF);
                  border-color: rgba(16,185,129,0.35); }   /* Emerald tint */
#TopMiddleGroup { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                      stop:0 rgba(245,158,11,0.10), stop:1 #FFFFFF);
                  border-color: rgba(245,158,11,0.40); }   /* Amber tint */
#SearchGroup    { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                      stop:0 rgba(59,130,246,0.10), stop:1 #FFFFFF);
                  border-color: rgba(59,130,246,0.40); }   /* Primary tint */

/* ---------------- Inputs ---------------- */
QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox {
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  border-radius: 10px;
  padding: 9px 12px;
}
QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
  border: 1px solid #3B82F6;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.18);
  outline: none;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow {
  width: 0; height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #64748B;
  margin-right: 8px;
}

/* ---------------- Buttons ---------------- */
/* ปุ่มหลัก */
QPushButton {
  background: #3B82F6;
  color: #FFFFFF;
  border: none;
  border-radius: 10px;
  padding: 9px 14px;
  font-weight: 700;
}
QPushButton:hover   { background: #2563EB; }
QPushButton:pressed { background: #1D4ED8; }
QPushButton:disabled{ background: #E5EAF2; color: #94A3B8; }

/* ปุ่มรองแบบเส้น (ตั้ง objectName="OutlineButton") */
#OutlineButton {
  background: #FFFFFF;
  color: #0F172A;
  border: 1px solid #D7DEEA;
}
#OutlineButton:hover   { background: #F2F6FC; }
#OutlineButton:pressed { background: #E9EEF7; }

/* ปุ่มนุ่ม (ตั้ง objectName="SubtleButton") ใช้พื้นหลังสีจาง */
#SubtleButton {
  background: rgba(59,130,246,0.12);
  color: #1E3A8A;
  border: 1px solid rgba(59,130,246,0.22);
}
#SubtleButton:hover   { background: rgba(59,130,246,0.18); }
#SubtleButton:pressed { background: rgba(59,130,246,0.24); }

/* ปุ่มสถานะอื่นๆ: ตั้ง objectName ตามนี้ */
#SuccessButton  { background: #10B981; }
#SuccessButton:hover  { background: #059669; }
#WarningButton  { background: #F59E0B; }
#WarningButton:hover  { background: #D97706; }
#DangerButton   { background: #F43F5E; }
#DangerButton:hover   { background: #E11D48; }

/* ---------------- Tool Buttons (แถบล่าง) ---------------- */
QToolButton {
  background: #FFFFFF;
  color: #0F172A;
  border: 1px solid #E5EAF2;
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 70px; min-height: 44px;
  font-weight: 600;
}
QToolButton:hover   { background: #F2F6FC; }
QToolButton:pressed { background: #E9EEF7; }
QToolButton:checked {
  background: rgba(6,182,212,0.14);
  border-color: rgba(6,182,212,0.35);
  color: #115E59;
}

/* ---------------- Tables ---------------- */
QTableWidget {
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  border-radius: 12px;
  gridline-color: #E5EAF2;
  alternate-background-color: #F8FAFE;
}
QHeaderView::section {
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
              stop:0 #F3F6FC, stop:1 #FFFFFF);
  color: #334155;
  border: 1px solid #E5EAF2;
  padding: 9px;
  font-weight: 800;
}
QTableWidget::item:selected {
  background: rgba(124,58,237,0.14);  /* violet selection */
  color: #1F2937;
}

/* ---------------- Tabs ---------------- */
#TabWidget, #TabWidget > QWidget > QWidget { background: transparent; }
QTabBar::tab {
  background: #FFFFFF;
  color: #334155;
  border: 1px solid #E5EAF2;
  border-bottom: none;
  padding: 9px 14px;
  margin-right: 6px;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}
QTabBar::tab:selected {
  background: #06B6D4;
  color: #FFFFFF;
  border-color: #06B6D4;
}
QTabBar::tab:hover { background: #F2F6FC; }

/* ---------------- Toolbar ---------------- */
QToolBar {
  background: #FFFFFF;
  border-top: 1px solid #E5EAF2;
  padding: 8px;
  spacing: 8px;
}
QToolBar::separator { background: #E5EAF2; width: 1px; margin: 4px; }

/* ---------------- Scrollbar ---------------- */
QScrollBar:vertical {
  background: transparent; width: 10px; margin: 4px;
}
QScrollBar::handle:vertical {
  background: #D5DCE7; border-radius: 6px; min-height: 28px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
  background: transparent; height: 10px; margin: 4px;
}
QScrollBar::handle:horizontal {
  background: #D5DCE7; border-radius: 6px; min-width: 28px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ---------------- Badges / Tags (ใส่กับ QLabel) ---------------- */
/* ใช้: label.setObjectName("TagPrimary") เป็นต้น */
#TagPrimary, #TagTeal, #TagViolet, #TagSuccess, #TagWarning, #TagDanger {
  padding: 4px 8px;
  border-radius: 999px;
  font-weight: 700;
  border: 1px solid transparent;
  color: #0F172A;
}
#TagPrimary { background: rgba(59,130,246,0.18);  border-color: rgba(59,130,246,0.28); }
#TagTeal    { background: rgba(6,182,212,0.18);    border-color: rgba(6,182,212,0.28); }
#TagViolet  { background: rgba(124,58,237,0.18);  border-color: rgba(124,58,237,0.28); }
#TagSuccess { background: rgba(16,185,129,0.18);  border-color: rgba(16,185,129,0.28); }
#TagWarning { background: rgba(245,158,11,0.20);  border-color: rgba(245,158,11,0.32); }
#TagDanger  { background: rgba(244,63,94,0.18);   border-color: rgba(244,63,94,0.30); }

/* ---------------- Helpers ---------------- */
*:disabled { color: #94A3B8; }
.QLabel[hint="true"] { color: #64748B; }


        """)


        # --- Main Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # จัดให้ชิดขอบทั้งหมด ไม่มีช่องว่างรอบนอก
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Main Content Area - 2x3 Grid Layout ---
        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        # ทำให้คอลัมน์ขยายเท่ากัน และจัดให้แถวล่างสูงกว่าแถวบน
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 1)
        content_layout.setColumnStretch(2, 1)
        content_layout.setRowStretch(0, 1)   # แถวบนเตี้ยกว่า
        content_layout.setRowStretch(1, 2)   # แถวล่างสูงกว่า
        # ไม่มีช่องไฟระหว่างกล่อง และไม่มี margin รอบ grid
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top row (row 0)
        # เลขที่สัญญา (0,0)
        contract_section = self.create_contract_info_section()
        content_layout.addWidget(contract_section, 0, 0)
        
        # ยอดฝาก (0,1)
        deposit_section = self.create_results_section()
        content_layout.addWidget(deposit_section, 0, 1)
        
        # ค้นหาสัญญา (0,2)
        search_section = self.create_search_group()
        content_layout.addWidget(search_section, 0, 2)
        
        # Bottom row (row 1)
        # ข้อมูลลูกค้า (1,0)
        customer_section = self.create_customer_tab()
        content_layout.addWidget(customer_section, 1, 0)
        
        # ข้อมูลสินค้าฝาก (1,1)
        product_section = self.create_product_tab()
        content_layout.addWidget(product_section, 1, 1)
        
        # ยืนยันสัดส่วนคอลัมน์เท่ากันและแถวล่างสูงกว่า
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 1)
        content_layout.setRowStretch(0, 1)
        content_layout.setRowStretch(1, 2)
        
        main_layout.addWidget(content_widget)

        # --- Bottom Toolbar ---
        self.create_bottom_toolbar()

        # --- Initialize UI ---
        self.initialize_ui()
        
        # ตรวจสอบสินค้าหลุดจำนำเมื่อเปิดโปรแกรม
        self.check_forfeited_products_on_startup()

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
            default_days = int(self.db.get_setting('default_contract_days'))
            self.days_spin.setValue(default_days)
        except:
            # ใช้ค่าเริ่มต้นถ้าไม่มีการตั้งค่า
            self.days_spin.setValue(30)

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
        """สร้างส่วนข้อมูลลูกค้า (รองรับหลายภาษา)"""
        # สร้าง GroupBox หลักสำหรับข้อมูลลูกค้า
        main_group = QGroupBox()
        main_group.setObjectName("TopLeftGroup")
        self.customer_main_group = main_group  # เก็บอ้างอิงเพื่ออัปเดตชื่อ
        layout = QVBoxLayout(main_group)
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
        self.add_customer_btn.clicked.connect(self.open_customer_dialog)
        self.add_customer_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_customer_btn.setMinimumHeight(32)
        search_layout.addWidget(self.add_customer_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Customer info section
        self.customer_info_group = QGroupBox()
        self.customer_info_layout = QGridLayout(self.customer_info_group)
        self.customer_info_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        self.customer_info_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        # ทำให้คอลัมน์ input ขยายตัวได้ โดยคอลัมน์ label แคบกว่า
        self.customer_info_layout.setColumnStretch(0, 0)
        self.customer_info_layout.setColumnStretch(1, 1)
        self.customer_info_layout.setColumnStretch(2, 1)
        
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
        
        # ใส่ ScrollArea ให้ส่วนข้อมูลลูกค้า
        customer_scroll = QScrollArea()
        customer_scroll.setWidget(self.customer_info_group)
        customer_scroll.setWidgetResizable(True)
        customer_scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(customer_scroll)
        
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

        return main_group

    def apply_customer_tab_language(self, *_args):
        """อัปเดตข้อความของส่วนข้อมูลลูกค้าตามภาษาปัจจุบัน"""
        # ตั้งชื่อ GroupBox หลัก
        if hasattr(self, "customer_main_group"):
            self.customer_main_group.setTitle(language_manager.get_text("tab_customer"))
        
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
        """สร้างส่วนข้อมูลสินค้า"""
        # สร้าง GroupBox หลักสำหรับข้อมูลสินค้า
        main_group = QGroupBox()
        main_group.setObjectName("TopMiddleGroup")
        self.product_main_group = main_group  # เก็บอ้างอิงเพื่ออัปเดตชื่อ
        layout = QVBoxLayout(main_group)
        layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างกลุ่ม
        layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ
        
        # Product search section
        search_group = QGroupBox()
        self.product_search_group = search_group
        search_layout = QGridLayout(search_group)
        search_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        search_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        self.lbl_product_name = QLabel()
        search_layout.addWidget(self.lbl_product_name, 0, 0)
        self.product_name_edit = QLineEdit()
        search_layout.addWidget(self.product_name_edit, 0, 1)
        
        self.product_search_btn = QPushButton()
        self.product_search_btn.clicked.connect(self.search_product)
        self.product_search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.product_search_btn.setMinimumHeight(32)
        search_layout.addWidget(self.product_search_btn, 0, 2)
        
        self.add_product_btn = QPushButton()
        self.add_product_btn.clicked.connect(self.open_product_dialog)
        self.add_product_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_product_btn.setMinimumHeight(32)
        search_layout.addWidget(self.add_product_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Product info section
        self.product_info_group = QGroupBox()
        self.product_info_layout = QGridLayout(self.product_info_group)
        self.product_info_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        self.product_info_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        # ทำให้คอลัมน์ input ขยายตัวได้ โดยคอลัมน์ label แคบกว่า
        self.product_info_layout.setColumnStretch(0, 0)
        self.product_info_layout.setColumnStretch(1, 1)
        
        # สินค้าฝากขาย
        self.lbl_pawned_product = QLabel()
        self.product_info_layout.addWidget(self.lbl_pawned_product, 0, 0)
        self.product_name_display_edit = QLineEdit()
        self.product_name_display_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_name_display_edit, 0, 1)
        
        # ยี่ห้อ/รุ่น
        self.lbl_brand_model = QLabel()
        self.product_info_layout.addWidget(self.lbl_brand_model, 1, 0)
        self.product_brand_edit = QLineEdit()
        self.product_brand_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_brand_edit, 1, 1)
        
        # ขนาด
        self.lbl_size = QLabel()
        self.product_info_layout.addWidget(self.lbl_size, 2, 0)
        self.product_size_edit = QLineEdit()
        self.product_size_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_size_edit, 2, 1)
        
        # น้ำหนัก
        self.lbl_weight = QLabel()
        self.product_info_layout.addWidget(self.lbl_weight, 3, 0)
        self.product_weight_combo = QComboBox()
        self.product_weight_combo.addItems([
            language_manager.get_text("unit_gram"),
            language_manager.get_text("unit_kilogram"),
            language_manager.get_text("unit_baht"),
        ])
        self.product_weight_combo.setEnabled(False)
        self.product_info_layout.addWidget(self.product_weight_combo, 3, 1)
        
        # หมายเลขซีเรียล
        self.lbl_serial = QLabel()
        self.product_info_layout.addWidget(self.lbl_serial, 4, 0)
        self.serial_number_edit = QLineEdit()
        self.serial_number_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.serial_number_edit, 4, 1)
        
        # รายละเอียดอื่นๆ
        self.lbl_product_other = QLabel()
        self.product_info_layout.addWidget(self.lbl_product_other, 5, 0)
        self.product_details_edit = QLineEdit()
        self.product_details_edit.setReadOnly(True)
        self.product_info_layout.addWidget(self.product_details_edit, 5, 1)
        
        # รูปภาพสินค้า
        self.lbl_product_image = QLabel()
        self.product_info_layout.addWidget(self.lbl_product_image, 6, 0)
        self.product_image_display = QLabel()
        self.product_image_display.setMinimumSize(200, 150)
        # อนุญาตให้รูปภาพขยายตามพื้นที่ โดยไม่ล็อกขนาดสูงสุด
        self.product_image_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.product_image_display.setStyleSheet("border: 2px solid #ccc; background-color: #f9f9f9;")
        self.product_image_display.setAlignment(Qt.AlignCenter)
        self.product_image_display.setText(language_manager.get_text("no_image"))
        self.product_info_layout.addWidget(self.product_image_display, 6, 1)
        
        # ใส่ ScrollArea ให้ส่วนข้อมูลสินค้า
        product_scroll = QScrollArea()
        product_scroll.setWidget(self.product_info_group)
        product_scroll.setWidgetResizable(True)
        product_scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(product_scroll)
        
        # Product add form section (initially hidden)
        self.product_add_group = QGroupBox()
        self.product_add_layout = QGridLayout(self.product_add_group)
        self.product_add_layout.setSpacing(10)
        self.product_add_layout.setContentsMargins(15, 20, 15, 15)
        
        # ชื่อสินค้า
        self.lbl_add_product_name = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_product_name, 0, 0)
        self.product_add_name_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_name_edit, 0, 1, 1, 3)
        
        # ยี่ห้อ/รุ่น
        self.lbl_add_brand_model = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_brand_model, 1, 0)
        self.product_add_brand_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_brand_edit, 1, 1, 1, 3)
        
        # ขนาด
        self.lbl_add_size = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_size, 2, 0)
        self.product_add_size_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_size_edit, 2, 1, 1, 3)
        
        # น้ำหนัก
        self.lbl_add_weight = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_weight, 3, 0)
        self.product_add_weight_combo = QComboBox()
        self.product_add_weight_combo.addItems([
            language_manager.get_text("unit_gram"),
            language_manager.get_text("unit_kilogram"),
            language_manager.get_text("unit_baht"),
        ])
        self.product_add_layout.addWidget(self.product_add_weight_combo, 3, 1, 1, 3)
        
        # หมายเลขซีเรียล
        self.lbl_add_serial = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_serial, 4, 0)
        self.product_add_serial_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_serial_edit, 4, 1, 1, 3)
        
        # รายละเอียดอื่นๆ
        self.lbl_add_other_details = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_other_details, 5, 0)
        self.product_add_details_edit = QLineEdit()
        self.product_add_layout.addWidget(self.product_add_details_edit, 5, 1, 1, 3)
        
        # รูปภาพสินค้า
        self.lbl_add_product_image = QLabel()
        self.product_add_layout.addWidget(self.lbl_add_product_image, 6, 0)
        self.product_add_image_path_edit = QLineEdit()
        self.product_add_image_path_edit.setPlaceholderText(language_manager.get_text("choose_image_placeholder"))
        self.product_add_image_path_edit.setReadOnly(True)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.product_add_image_path_edit)
        
        self.product_add_image_browse_btn = QPushButton()
        self.product_add_image_browse_btn.clicked.connect(self.browse_product_image)
        self.product_add_image_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        image_layout.addWidget(self.product_add_image_browse_btn)
        
        self.product_add_layout.addLayout(image_layout, 6, 1, 1, 3)
        
        # แสดงรูปภาพตัวอย่าง
        self.lbl_image_preview = QLabel()
        self.product_add_layout.addWidget(self.lbl_image_preview, 7, 0)
        self.product_image_preview = QLabel()
        self.product_image_preview.setMinimumSize(200, 150)
        self.product_image_preview.setMaximumSize(300, 200)
        self.product_image_preview.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.product_image_preview.setAlignment(Qt.AlignCenter)
        self.product_image_preview.setText(language_manager.get_text("no_image"))
        self.product_add_layout.addWidget(self.product_image_preview, 7, 1, 1, 3)
        
        # ปุ่มบันทึกและยกเลิก
        button_layout = QHBoxLayout()
        self.product_save_btn = QPushButton()
        self.product_save_btn.clicked.connect(self.save_new_product)
        self.product_save_btn.setIcon(QIcon.fromTheme("document-save"))
        button_layout.addWidget(self.product_save_btn)
        
        self.product_cancel_btn = QPushButton()
        self.product_cancel_btn.clicked.connect(self.toggle_product_mode)
        self.product_cancel_btn.setIcon(QIcon.fromTheme("edit-clear"))
        button_layout.addWidget(self.product_cancel_btn)
        
        self.product_add_layout.addLayout(button_layout, 8, 0, 1, 4)
        
        # ซ่อนฟอร์มเพิ่มสินค้าไว้ก่อน
        self.product_add_group.hide()
        layout.addWidget(self.product_add_group)

        # เชื่อมต่ออัปเดตภาษา
        language_manager.language_changed.connect(self.apply_product_tab_language)
        self.apply_product_tab_language()
        
        return main_group

    def apply_product_tab_language(self, *_args):
        """อัปเดตข้อความของส่วนข้อมูลสินค้า ตามภาษาปัจจุบัน"""
        # ตั้งชื่อ GroupBox หลัก
        if hasattr(self, "product_main_group"):
            self.product_main_group.setTitle(language_manager.get_text("tab_product"))
        
        if hasattr(self, "product_search_group") and self.product_search_group is not None:
            self.product_search_group.setTitle(language_manager.get_text("product_search_group"))
        self.product_info_group.setTitle(language_manager.get_text("product_info_group"))
        self.product_add_group.setTitle(language_manager.get_text("product_add_group"))

        # Search section
        self.lbl_product_name.setText(language_manager.get_text("product_name"))
        self.product_search_btn.setText(language_manager.get_text("product_search"))
        self.add_product_btn.setText(language_manager.get_text("add_new_product"))

        # Info section
        self.lbl_pawned_product.setText(language_manager.get_text("pawned_product"))
        self.lbl_brand_model.setText(language_manager.get_text("brand_model"))
        self.lbl_size.setText(language_manager.get_text("size"))
        self.lbl_weight.setText(language_manager.get_text("weight"))
        # units combo
        self.product_weight_combo.clear()
        self.product_weight_combo.addItems([
            language_manager.get_text("unit_gram"),
            language_manager.get_text("unit_kilogram"),
            language_manager.get_text("unit_baht"),
        ])
        self.lbl_serial.setText(language_manager.get_text("serial_number"))
        self.lbl_product_other.setText(language_manager.get_text("product_other_details"))
        self.lbl_product_image.setText(language_manager.get_text("product_image"))
        self.product_image_display.setText(language_manager.get_text("no_image"))

        # Add section
        self.lbl_add_product_name.setText(language_manager.get_text("product_name"))
        self.lbl_add_brand_model.setText(language_manager.get_text("brand_model"))
        self.lbl_add_size.setText(language_manager.get_text("size"))
        self.lbl_add_weight.setText(language_manager.get_text("weight"))
        self.product_add_weight_combo.clear()
        self.product_add_weight_combo.addItems([
            language_manager.get_text("unit_gram"),
            language_manager.get_text("unit_kilogram"),
            language_manager.get_text("unit_baht"),
        ])
        self.lbl_add_serial.setText(language_manager.get_text("serial_number"))
        self.lbl_add_other_details.setText(language_manager.get_text("product_other_details"))
        self.lbl_add_product_image.setText(language_manager.get_text("product_image"))
        self.product_add_image_path_edit.setPlaceholderText(language_manager.get_text("choose_image_placeholder"))
        self.product_add_image_browse_btn.setText(language_manager.get_text("choose_file"))
        self.lbl_image_preview.setText(language_manager.get_text("image_preview"))
        self.product_image_preview.setText(language_manager.get_text("no_image"))
        self.product_save_btn.setText(language_manager.get_text("save"))
        self.product_cancel_btn.setText(language_manager.get_text("cancel"))




    def create_contract_info_section(self):
        """สร้างส่วนข้อมูลสัญญา (รองรับหลายภาษา)"""
        group_box = QGroupBox()
        group_box.setObjectName("TopLeftGroup")
        layout = QGridLayout(group_box)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # เลขที่สัญญา
        self.lbl_contract_number = QLabel()
        layout.addWidget(self.lbl_contract_number, 0, 0)
        self.contract_number_edit = QLineEdit()
        self.contract_number_edit.setReadOnly(True)
        layout.addWidget(self.contract_number_edit, 0, 1)
        
        # วันที่เริ่มต้น
        self.lbl_start_date = QLabel()
        layout.addWidget(self.lbl_start_date, 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.start_date_edit, 1, 1)
        
        # จำนวนวัน
        self.lbl_days = QLabel()
        layout.addWidget(self.lbl_days, 2, 0)
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        layout.addWidget(self.days_spin, 2, 1)
        
        # วันที่สิ้นสุด
        self.lbl_end_date = QLabel()
        layout.addWidget(self.lbl_end_date, 3, 0)
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setReadOnly(True)
        layout.addWidget(self.end_date_edit, 3, 1)
        
        # เชื่อมต่อสัญญาณ
        self.start_date_edit.dateChanged.connect(self.calculate_end_date)
        self.days_spin.valueChanged.connect(self.calculate_end_date)
        
        # สถานะสัญญา
        self.lbl_contract_status = QLabel()
        layout.addWidget(self.lbl_contract_status, 4, 0)
        status_layout = QHBoxLayout()
        self.active_radio = QRadioButton()
        self.redeemed_radio = QRadioButton()
        self.lost_radio = QRadioButton()
        self.active_radio.setChecked(True)
        status_layout.addWidget(self.active_radio)
        status_layout.addWidget(self.redeemed_radio)
        status_layout.addWidget(self.lost_radio)
        layout.addLayout(status_layout, 4, 1)
        
        # ปุ่มอัปเดตสถานะ
        self.update_status_btn = QPushButton()
        self.update_status_btn.clicked.connect(self.update_contract_status)
        self.update_status_btn.setMaximumWidth(120)
        self.update_status_btn.setIcon(QIcon.fromTheme("view-refresh"))
        layout.addWidget(self.update_status_btn, 4, 2)
        
        # เชื่อมต่อภาษา
        language_manager.language_changed.connect(self.apply_contract_info_language)
        self.apply_contract_info_language()

        return group_box

    def apply_contract_info_language(self, *_args):
        if (w := self.findChild(QGroupBox, "TopLeftGroup")) is not None:
            w.setTitle(language_manager.get_text("contract_info_group"))
        self.lbl_contract_number.setText(language_manager.get_text("contract_number"))
        self.lbl_start_date.setText(language_manager.get_text("start_date"))
        self.lbl_days.setText(language_manager.get_text("days"))
        self.lbl_end_date.setText(language_manager.get_text("end_date"))
        self.lbl_contract_status.setText(language_manager.get_text("contract_status"))
        self.active_radio.setText(language_manager.get_text("status_active"))
        self.redeemed_radio.setText(language_manager.get_text("status_redeemed"))
        self.lost_radio.setText(language_manager.get_text("status_lost"))
        self.update_status_btn.setText(language_manager.get_text("update_status"))

    def create_results_section(self):
        """สร้างส่วนผลจัดทำ (รองรับหลายภาษา)"""
        group_box = QGroupBox()
        group_box.setObjectName("TopMiddleGroup")
        layout = QGridLayout(group_box)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # ยอดฝาก
        self.lbl_pawn_amount = QLabel()
        layout.addWidget(self.lbl_pawn_amount, 0, 0)
        self.pawn_amount_spin = QDoubleSpinBox()
        self.pawn_amount_spin.setRange(0, 999999)
        self.pawn_amount_spin.setSuffix(" บาท")
        layout.addWidget(self.pawn_amount_spin, 0, 1)

        # ยอดไถ่คืน
        self.lbl_total_redemption = QLabel()
        layout.addWidget(self.lbl_total_redemption, 1, 0)
        self.total_redemption_spin = QDoubleSpinBox()
        self.total_redemption_spin.setRange(0, 999999)
        self.total_redemption_spin.setSuffix(" บาท")
        layout.addWidget(self.total_redemption_spin, 1, 1)

        # เชื่อมภาษา
        language_manager.language_changed.connect(self.apply_results_language)
        self.apply_results_language()

        return group_box

    def apply_results_language(self, *_args):
        if (w := self.findChild(QGroupBox, "TopMiddleGroup")) is not None:
            w.setTitle(language_manager.get_text("results_group"))
        self.lbl_pawn_amount.setText(language_manager.get_text("pawn_amount"))
        self.lbl_total_redemption.setText(language_manager.get_text("total_redemption"))

    def create_search_group(self):
        group_box = QGroupBox()
        group_box.setObjectName("SearchGroup")
        layout = QVBoxLayout(group_box)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # เลือกประเภทการค้นหา
        search_type_layout = QHBoxLayout()
        self.lbl_search_by = QLabel()
        search_type_layout.addWidget(self.lbl_search_by)
        self.search_type_combo = QComboBox()
        # เพิ่มด้วย userData คงที่ เพื่อไม่พังเมื่อเปลี่ยนภาษา
        self.search_type_combo.addItem(language_manager.get_text("search_type_contract"), "contract")
        self.search_type_combo.addItem(language_manager.get_text("search_type_idcard"), "idcard")
        self.search_type_combo.addItem(language_manager.get_text("search_type_name"), "name")
        self.search_type_combo.currentTextChanged.connect(self.on_search_type_changed)
        search_type_layout.addWidget(self.search_type_combo)
        layout.addLayout(search_type_layout)
        
        # ฟอร์มค้นหา
        form_layout = QGridLayout()
        form_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างคอลัมน์
        
        # เลขที่สัญญา (เริ่มต้น)
        self.lbl_search_contract = QLabel()
        form_layout.addWidget(self.lbl_search_contract, 0, 0)
        self.search_contract_combo = QComboBox()
        self.search_contract_combo.addItems(["=", ">", "<", ">=", "<="])
        form_layout.addWidget(self.search_contract_combo, 0, 1)
        self.search_contract_edit = QLineEdit()
        self.search_contract_edit.setPlaceholderText(language_manager.get_text("enter_contract_number"))
        form_layout.addWidget(self.search_contract_edit, 0, 2)
        
        # เลขบัตรประชาชน (ซ่อนไว้)
        self.lbl_search_idcard = QLabel()
        form_layout.addWidget(self.lbl_search_idcard, 1, 0)
        self.search_id_card_edit = QLineEdit()
        self.search_id_card_edit.setPlaceholderText(language_manager.get_text("enter_id_card"))
        self.search_id_card_edit.hide()
        form_layout.addWidget(self.search_id_card_edit, 1, 1, 1, 2)
        
        # ชื่อนามสกุล (ซ่อนไว้)
        self.lbl_search_first_name = QLabel()
        form_layout.addWidget(self.lbl_search_first_name, 2, 0)
        self.search_first_name_edit = QLineEdit()
        self.search_first_name_edit.setPlaceholderText(language_manager.get_text("enter_first_name"))
        self.search_first_name_edit.hide()
        form_layout.addWidget(self.search_first_name_edit, 2, 1)
        
        self.lbl_search_last_name = QLabel()
        form_layout.addWidget(self.lbl_search_last_name, 2, 2)
        self.search_last_name_edit = QLineEdit()
        self.search_last_name_edit.setPlaceholderText(language_manager.get_text("enter_last_name"))
        self.search_last_name_edit.hide()
        form_layout.addWidget(self.search_last_name_edit, 2, 3)

        layout.addLayout(form_layout)
        
        # ปุ่มค้นหา
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างปุ่ม
        
        self.search_btn = QPushButton()
        self.search_btn.clicked.connect(self.search_contracts)
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.setMinimumHeight(32)
        button_layout.addWidget(self.search_btn)
        
        self.clear_search_btn = QPushButton()
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_search_btn.setMinimumHeight(32)
        button_layout.addWidget(self.clear_search_btn)
        
        layout.addLayout(button_layout)

        # ตัวเลือกสถานะสัญญา
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(15)  # เพิ่มระยะห่างระหว่าง radio button
        self.lbl_search_status = QLabel()
        radio_layout.addWidget(self.lbl_search_status)
        self.search_active_radio = QRadioButton()
        self.search_closed_radio = QRadioButton()
        self.search_all_radio = QRadioButton()
        self.search_all_radio.setChecked(True)
        radio_layout.addWidget(self.search_active_radio)
        radio_layout.addWidget(self.search_closed_radio)
        radio_layout.addWidget(self.search_all_radio)
        layout.addLayout(radio_layout)
        
        # ผูกภาษา
        language_manager.language_changed.connect(self.apply_search_language)
        self.apply_search_language()

        return group_box

    def apply_search_language(self, *_args):
        if (w := self.findChild(QGroupBox, "SearchGroup")) is not None:
            w.setTitle(language_manager.get_text("search_group"))
        self.lbl_search_by.setText(language_manager.get_text("search_by"))
        # reset search type items
        current_idx = self.search_type_combo.currentIndex()
        self.search_type_combo.blockSignals(True)
        self.search_type_combo.clear()
        self.search_type_combo.addItem(language_manager.get_text("search_type_contract"), "contract")
        self.search_type_combo.addItem(language_manager.get_text("search_type_idcard"), "idcard")
        self.search_type_combo.addItem(language_manager.get_text("search_type_name"), "name")
        self.search_type_combo.blockSignals(False)
        self.search_type_combo.setCurrentIndex(max(0, min(current_idx, 2)))
        self.lbl_search_contract.setText(language_manager.get_text("contract_number"))
        self.search_contract_edit.setPlaceholderText(language_manager.get_text("enter_contract_number"))
        self.lbl_search_idcard.setText(language_manager.get_text("id_card_number"))
        self.search_id_card_edit.setPlaceholderText(language_manager.get_text("enter_id_card"))
        self.lbl_search_first_name.setText(language_manager.get_text("first_name"))
        self.search_first_name_edit.setPlaceholderText(language_manager.get_text("enter_first_name"))
        self.lbl_search_last_name.setText(language_manager.get_text("last_name"))
        self.search_last_name_edit.setPlaceholderText(language_manager.get_text("enter_last_name"))
        self.search_btn.setText(language_manager.get_text("search"))
        self.clear_search_btn.setText(language_manager.get_text("clear_search"))
        self.lbl_search_status.setText(language_manager.get_text("contract_status"))
        self.search_active_radio.setText(language_manager.get_text("status_open"))
        self.search_closed_radio.setText(language_manager.get_text("status_closed"))
        self.search_all_radio.setText(language_manager.get_text("all"))



  

    def create_bottom_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))  # ลดขนาด icon ให้เล็กลง
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
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
                min-height: 48px;
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
            icon_path = get_icon_path(ICON_MAP[icon_name])
            icon = QIcon(icon_path)
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
            elif "ไถ่คืน" in text:
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
        

        

    def open_customer_dialog(self):
        """เปิดหน้าต่างป็อปอัพเพิ่ม/แก้ไขลูกค้า"""
        try:
            dialog = CustomerDialog(self)
            if dialog.exec():
                if getattr(dialog, 'customer_data', None):
                    # โหลดลูกค้าที่เพิ่งเพิ่ม/แก้ไข
                    self.current_customer = dialog.customer_data
                    self.load_customer_data()
                    # แสดงรหัสลูกค้าถ้ามี
                    code = self.current_customer.get('customer_code', '')
                    if code:
                        QMessageBox.information(self, "สำเร็จ", f"เพิ่ม/อัปเดตลูกค้าเรียบร้อย\nรหัสลูกค้า: {code}")
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"ไม่สามารถเปิดหน้าต่างลูกค้าได้: {str(e)}")

    def open_product_dialog(self):
        """เปิดหน้าต่างป็อปอัพเพิ่ม/แก้ไขสินค้า"""
        try:
            dialog = ProductDialog(self)
            if dialog.exec():
                if getattr(dialog, 'product_data', None):
                    # โหลดสินค้าที่เพิ่งเพิ่ม/แก้ไข
                    self.current_product = dialog.product_data
                    self.load_product_data()
                    QMessageBox.information(self, "สำเร็จ", "เพิ่ม/อัปเดตสินค้าเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"ไม่สามารถเปิดหน้าต่างสินค้าได้: {str(e)}")

    def add_customer(self):
        """เพิ่มลูกค้า (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.open_customer_dialog()
        

    def search_customer(self):
        """ค้นหาลูกค้า"""
        search_term = self.customer_code_edit.text().strip()
        if not search_term:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อลูกค้า, นามสกุล, เลขบัตร, หรือรหัสลูกค้า")
            return
        
        # ค้นหาลูกค้าในฐานข้อมูล (ค้นหาจากชื่อก่อน)
        customers = self.db.search_customers(search_term)
        if customers:
            self.current_customer = customers[0]
            self.load_customer_data()
        else:
            QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบลูกค้าที่ตรงกับคำค้นหา")
        

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
            

    def add_product(self):
        """เพิ่มสินค้า (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.open_product_dialog()
        

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
            

    
    def refresh_contract_data(self):
        """รีเฟรชข้อมูลสัญญา"""
        try:
            if self.current_contract:
                # โหลดข้อมูลสัญญาใหม่
                updated_contract = self.db.get_contract_by_id(self.current_contract['id'])
                if updated_contract:
                    self.current_contract = updated_contract
                    # อัปเดตข้อมูลในฟอร์ม
                    self.load_contract_data()
                    
                    contract_number = self.current_contract.get('contract_number', '')
                    if contract_number:
                        self.load_renewal_history(contract_number)
        except Exception as e:
            print(f"Error refreshing contract data: {e}")

    def redeem_contract(self):
        """ไถ่คืนสัญญา"""
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
                # หลังจากไถ่คืนสำเร็จ ให้แสดงประวัติการไถ่คืน
                try:
                    # ดึงข้อมูลการไถ่คืนของสัญญานี้
                    redemptions = self.db.get_redemptions_by_contract(contract_id)
                    
                    if redemptions:
                        # แสดงประวัติการไถ่คืนเฉพาะสัญญานี้
                        self.show_redemptions_table(redemptions, contract_specific=True)
                    else:
                        QMessageBox.information(self, "ข้อมูลการไถ่คืน", "ไม่พบข้อมูลการไถ่คืนของสัญญานี้")
                    
                    # อัปเดตข้อมูลสัญญาปัจจุบันในฟอร์มหลัก
                    updated_contract = self.db.get_contract_by_id(self.current_contract['id'])
                    if updated_contract:
                        self.current_contract = updated_contract
                        self.load_contract_data()
                        
                        # อัปเดตสถานะสัญญาในฟอร์ม
                        if hasattr(self, 'redeemed_radio') and updated_contract.get('status') == 'redeemed':
                            self.redeemed_radio.setChecked(True)
                        
                except Exception as e:
                    QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดประวัติการไถ่คืน: {str(e)}")
                    
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
            'interest_rate': 0.0,  # ไม่ใช้แล้ว
            'fee_amount': 0.0,  # ไม่ใช้แล้ว
            'withholding_tax_rate': 0.0,  # ไม่ใช้แล้ว
            'withholding_tax_amount': 0.0,  # ไม่ใช้แล้ว
            'total_paid': self.pawn_amount_spin.value(),  # ใช้ยอดฝากเป็นยอดจ่าย
            'total_redemption': self.total_redemption_spin.value(),  # ใช้ยอดที่ผู้ใช้กรอก
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
        
    
    

    def view_redemptions(self):
        """ดูข้อมูลการไถ่คืน"""
        try:
            # ดึงข้อมูลการไถ่คืนทั้งหมด
            redemptions = self.db.get_all_redemptions()
            
            if not redemptions:
                QMessageBox.information(self, "ข้อมูลการไถ่คืน", "ไม่พบข้อมูลการไถ่คืน")
                return
            
            # สร้างหน้าต่างแสดงข้อมูลการไถ่คืน
            self.show_redemptions_table(redemptions)
            
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
    
    def show_redemptions_table(self, redemptions: list, contract_specific: bool = False):
        """แสดงตารางข้อมูลการไถ่คืน"""
        if contract_specific:
            dialog = QDialog(self)
            dialog.setWindowTitle("ประวัติการไถ่คืน - สัญญาเฉพาะ")
            dialog.setModal(True)
            dialog.resize(1200, 500)
        else:
            dialog = QDialog(self)
            dialog.setWindowTitle("ข้อมูลการไถ่คืน")
            dialog.setModal(True)
            dialog.resize(1400, 600)
        
        layout = QVBoxLayout(dialog)
        
        # สร้างตาราง
        table = QTableWidget()
        if contract_specific:
            table.setColumnCount(12)
            headers = [
                "ลำดับ", "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", 
                "วันที่รับฝาก", "วันที่ครบกำหนด", "วันที่ไถ่คืน", "จำนวนวันที่ฝาก",
                "เงินต้น", "ค่าธรรมเนียม", "ค่าปรับ", "ยอดไถ่คืน"
            ]
        else:
            table.setColumnCount(10)
            headers = [
                "ลำดับ", "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", 
                "วันที่ไถ่คืน", "จำนวนวันที่ฝาก", "เงินต้น", "ค่าธรรมเนียม", "ค่าปรับ", "ยอดไถ่คืน"
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
                
                # วันที่ไถ่คืน
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
                
                # ยอดไถ่คืน
                redemption_amount = redemption.get('redemption_amount', 0)
                table.setItem(row, 11, QTableWidgetItem(f"{redemption_amount:,.2f}"))
            else:
                # วันที่ไถ่คืน
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
                
                # ยอดไถ่คืน
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
        

    def receive_payment(self):
        """รับเงิน"""
        QMessageBox.information(self, "รับเงิน", "ฟีเจอร์รับเงิน")
        

    def daily_account(self):
        """บัญชีรายวัน"""
        QMessageBox.information(self, "บัญชีรายวัน", "ฟีเจอร์บัญชีรายวัน")
        

    def interest_schedule(self):
        """ตารางดอกเบี้ย"""
        QMessageBox.information(self, "ตารางดอกเบี้ย", "ฟีเจอร์ตารางดอกเบี้ย")
        

    def on_search_type_changed(self):
        """เมื่อเปลี่ยนประเภทการค้นหา"""
        # ใช้ userData ที่ไม่แปลเพื่อกำหนดโหมด
        search_type = self.search_type_combo.currentData()
        
        # ซ่อนฟอร์มทั้งหมดก่อน
        self.search_contract_edit.hide()
        self.search_contract_combo.hide()
        self.search_id_card_edit.hide()
        self.search_first_name_edit.hide()
        self.search_last_name_edit.hide()
        
        # แสดงฟอร์มที่เหมาะสม
        if search_type == "contract":
            self.search_contract_edit.show()
            self.search_contract_combo.show()
        elif search_type == "idcard":
            self.search_id_card_edit.show()
        elif search_type == "name":
            self.search_first_name_edit.show()
            self.search_last_name_edit.show()
        
        # ล้างข้อมูลการค้นหา
        self.clear_search_fields()
        

    def clear_search_fields(self):
        """ล้างข้อมูลในฟิลด์ค้นหา"""
        self.search_contract_edit.clear()
        self.search_id_card_edit.clear()
        self.search_first_name_edit.clear()
        self.search_last_name_edit.clear()
        

    def search_contracts(self):
        """ค้นหาสัญญาตามประเภทที่เลือก"""
        search_type = self.search_type_combo.currentData()
        
        # ตรวจสอบข้อมูลการค้นหา
        if search_type == "contract":
            search_term = self.search_contract_edit.text().strip()
            if not search_term:
                QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกเลขที่สัญญา")
                return
        elif search_type == "idcard":
            search_term = self.search_id_card_edit.text().strip()
            if not search_term:
                QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกเลขบัตรประชาชน")
                return
        elif search_type == "name":
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
            if search_type == "contract":
                contracts = self.db.search_contracts_by_number(search_term, status)
            elif search_type == "idcard":
                contracts = self.db.search_contracts_by_id_card(search_term, status)
            elif search_type == "name":
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
                
                contract_number = contracts[0].get('contract_number', '')
                if contract_number:
                    self.load_renewal_history(contract_number)
                
                # ข้อมูลสัญญาถูกโหลดในฟอร์มแล้ว
                
                QMessageBox.information(self, "ผลการค้นหา", f"พบ {len(contracts)} สัญญา\nข้อมูลสัญญาแรกถูกโหลดในฟอร์มแล้ว")
            else:
                QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสัญญาที่ตรงกับคำค้นหา")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")

    def clear_search(self):
        """ล้างการค้นหา"""
        self.clear_search_fields()
        self.current_contract = None
        
        
        QMessageBox.information(self, "ล้างการค้นหา", "ล้างการค้นหาเรียบร้อยแล้ว")

    def search_next(self):
        """ค้นหาถัดไป (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.search_contracts()
        
    

    def search_by_name(self):
        """ค้นหาตามชื่อ (legacy - ใช้ฟังก์ชันใหม่แทน)"""
        # เปลี่ยนไปใช้การค้นหาตามชื่อนามสกุล
        self.search_type_combo.setCurrentText("ชื่อนามสกุล")
        self.on_search_type_changed()
        QMessageBox.information(self, "การค้นหา", "กรุณาเลือกประเภทการค้นหาเป็น 'ชื่อนามสกุล' และกรอกข้อมูล")
        

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
            self.total_redemption_spin.setValue(self.current_contract.get('total_redemption', 0))
            
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

    def load_renewal_history(self, contract_number):
        """โหลดประวัติการต่อดอกของสัญญา"""
        try:
            if not contract_number:
                return
            
            # ดึงข้อมูลการต่อดอกจากฐานข้อมูล
            renewals = self.db.get_renewals_by_contract(contract_number)
            
            # ตรวจสอบว่ามี UI elements สำหรับแสดง renewal history หรือไม่
            if hasattr(self, 'renewal_history_table'):
                # ล้างข้อมูลเก่า
                self.renewal_history_table.setRowCount(0)
                
                # แสดงข้อมูลการต่อดอก
                for renewal in renewals:
                    row_position = self.renewal_history_table.rowCount()
                    self.renewal_history_table.insertRow(row_position)
                    
                    # ข้อมูลการต่อดอก
                    self.renewal_history_table.setItem(row_position, 0, QTableWidgetItem(str(renewal.get('renewal_date', ''))))
                    self.renewal_history_table.setItem(row_position, 1, QTableWidgetItem(f"{renewal.get('interest_amount', 0):,.2f}"))
                    self.renewal_history_table.setItem(row_position, 2, QTableWidgetItem(f"{renewal.get('fee_amount', 0):,.2f}"))
                    self.renewal_history_table.setItem(row_position, 3, QTableWidgetItem(f"{renewal.get('total_amount', 0):,.2f}"))
                    self.renewal_history_table.setItem(row_position, 4, QTableWidgetItem(renewal.get('notes', '')))
            
            # อัปเดตข้อมูลใน UI อื่นๆ ที่เกี่ยวข้อง
            if hasattr(self, 'renewal_count_label'):
                self.renewal_count_label.setText(f"{len(renewals)} ครั้ง")
                
        except Exception as e:
            print(f"Error loading renewal history: {e}")

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
        self.total_redemption_spin.setValue(0)
        
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
        

    def generate_new_contract_number(self):
        """สร้างเลขที่สัญญาใหม่"""
        prefix = self.db.get_setting('contract_prefix') if hasattr(self.db, 'get_setting') else "CN"
        # คำนวณลำดับถัดไปจากฐานข้อมูล
        sequence = self.db.get_next_contract_sequence(prefix)
        contract_number = PawnShopUtils.generate_contract_number(prefix, sequence)
        self.contract_number_edit.setText(contract_number)
        

    def show_daily_report(self):
        """แสดงรายงานประจำวัน"""
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            summary = self.db.get_daily_summary(today)
            
            message = """
รายงานประจำวัน: {}
สัญญาใหม่: {} สัญญา ({:,.2f} บาท)
การไถ่คืน: {} สัญญา ({:,.2f} บาท)
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
        

    def show_monthly_report(self):
        """แสดงรายงานประจำเดือน"""
        QMessageBox.information(self, "รายงานประจำเดือน", "ฟีเจอร์รายงานประจำเดือน")
        
    
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
            
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")
    
    
    
    def show_fee_management(self):
        """แสดงหน้าต่างจัดการค่าธรรมเนียม"""
        dialog = FeeManagementDialog(self)
        dialog.fee_updated.connect(self.on_fee_updated)
        dialog.exec()
    
    def on_fee_updated(self):
        """เมื่อมีการอัปเดตข้อมูลค่าธรรมเนียม"""
        # รีเฟรชการคำนวณค่าธรรมเนียมในฟอร์ม
        self.calculate_amounts()
        

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
                'interest_rate': 0.0,  # ไม่ใช้แล้ว
                'fee_amount': 0.0,  # ไม่ใช้แล้ว
                'withholding_tax_rate': 0.0,  # ไม่ใช้แล้ว
                'withholding_tax_amount': 0.0,  # ไม่ใช้แล้ว
                'total_paid': self.pawn_amount_spin.value(),  # ใช้ยอดฝากเป็นยอดจ่าย
                'total_redemption': self.total_redemption_spin.value()  # ใช้ยอดที่ผู้ใช้กรอก
            }
            
            # ข้อมูลร้านค้า - ใช้ข้อมูลจาก pdf files
            shop_data = None  # ให้ใช้ค่า default จาก pdf files
            
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
            ["ยอดไถ่คืน:", f"{self.total_redemption_spin.value():,.2f} บาท"]
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
            "3. ลูกค้าสามารถไถ่คืนสินค้าได้ตลอดเวลาก่อนครบกำหนด",
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
                
            else:
                QMessageBox.information(self, "ไม่พบปัญหา", "ไม่พบข้อมูลซ้ำซ้อนในฐานข้อมูล")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการแก้ไขข้อมูลซ้ำซ้อน: {str(e)}")









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
            
            renewals = self.db.get_renewals_by_date(date)
            daily_income['renewals'] = len(renewals)
            
            
            # นับการไถ่คืน
            redemptions = self.db.get_redemptions_by_date(date)
            daily_income['redemptions'] = len(redemptions)
            
            # คำนวณจำนวนเงินไถ่คืน
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
            ("💎 การไถ่คืน", f"{daily_income['redemptions']} ครั้ง"),
            ("💰 ดอกเบี้ยรวม", f"{daily_income['total_interest']:,.2f} บาท"),
            ("💵 ค่าธรรมเนียมรวม", f"{daily_income['total_fees']:,.2f} บาท"),
            ("💎 จำนวนเงินไถ่คืน", f"{daily_income['total_redemption_amount']:,.2f} บาท"),
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

    def check_forfeited_products_on_startup(self):
        """ตรวจสอบสินค้าหลุดจำนำเมื่อเปิดโปรแกรมและแจ้งเตือนเข้าไลน์"""
        try:
            from line_config import ENABLE_LINE_NOTIFICATION, SEND_FORFEITURE_NOTIFICATION
            
            # ตรวจสอบว่าการแจ้งเตือนเปิดอยู่หรือไม่
            if not ENABLE_LINE_NOTIFICATION or not SEND_FORFEITURE_NOTIFICATION:
                return
            
            # ดึงสัญญาที่หลุดจำนำ
            forfeited_contracts = self.db.get_forfeited_contracts()
            
            if forfeited_contracts:
                # ส่งแจ้งเตือนสำหรับแต่ละสัญญาที่หลุดจำนำ
                for contract in forfeited_contracts:
                    try:
                        # เตรียมข้อมูลสำหรับข้อความ
                        enriched_contract = {
                            **contract,
                            'customer_name': f"{contract.get('first_name', '')} {contract.get('last_name', '')}".strip(),
                            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        }
                        
                        # ส่งแจ้งเตือนเข้าไลน์
                        self.send_forfeiture_to_line(enriched_contract)
                        
                    except Exception as e:
                        print(f"ไม่สามารถส่งแจ้งเตือนสำหรับสัญญา {contract.get('contract_number', 'N/A')}: {e}")
                
                # แสดงข้อความแจ้งเตือนในโปรแกรม
                QMessageBox.warning(
                    self, 
                    "แจ้งเตือนสินค้าหลุดจำนำ", 
                    f"พบสินค้าหลุดจำนำ {len(forfeited_contracts)} รายการ\n\n"
                    "ระบบได้ส่งแจ้งเตือนเข้าไลน์เรียบร้อยแล้ว\n"
                    "กรุณาตรวจสอบและดำเนินการตามความเหมาะสม"
                )
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบสินค้าหลุดจำนำ: {e}")

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