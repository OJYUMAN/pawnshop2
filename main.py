# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QToolBar,
    QMenuBar, QMessageBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit,
    QScrollArea, QFrame, QFileDialog
)
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtCore import Qt, QSize, QDate
from datetime import datetime, timedelta
from database import PawnShopDatabase
from utils import PawnShopUtils
from dialogs import CustomerDialog, ProductDialog, InterestPaymentDialog, RedemptionDialog
from data_viewer import DataViewerDialog
from customer_search import CustomerSearchDialog
from product_search import ProductSearchDialog
from fee_management import FeeManagementDialog

class PawnShopUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = PawnShopDatabase()
        self.current_customer = None
        self.current_product = None
        self.current_contract = None
        
        self.setWindowTitle("Pownshop")
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

        # --- Menu Bar ---
        self.create_menu_bar()

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



    def create_customer_tab(self):
        """สร้างแท็บข้อมูลลูกค้า"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)  # เพิ่มระยะห่างระหว่างกลุ่ม
        layout.setContentsMargins(20, 20, 20, 20)  # เพิ่ม margin รอบๆ
        
        # Customer search section
        search_group = QGroupBox("ค้นหาลูกค้า")
        search_layout = QGridLayout(search_group)
        search_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        search_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        search_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        self.customer_code_edit = QLineEdit()
        search_layout.addWidget(self.customer_code_edit, 0, 1)
        
        self.customer_search_btn = QPushButton("ค้นหา")
        self.customer_search_btn.clicked.connect(self.search_customer)
        self.customer_search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.customer_search_btn.setMinimumHeight(32)
        search_layout.addWidget(self.customer_search_btn, 0, 2)
        
        self.add_customer_btn = QPushButton("เพิ่มลูกค้าใหม่")
        self.add_customer_btn.clicked.connect(self.toggle_customer_mode)
        self.add_customer_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_customer_btn.setMinimumHeight(32)
        search_layout.addWidget(self.add_customer_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Customer info section
        self.customer_info_group = QGroupBox("ข้อมูลลูกค้า")
        self.customer_info_layout = QGridLayout(self.customer_info_group)
        self.customer_info_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างแถว
        self.customer_info_layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        # ชื่อลูกค้า
        self.customer_info_layout.addWidget(QLabel("ชื่อผู้กู้:"), 0, 0)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.customer_name_edit, 0, 1)
        
        # ที่อยู่
        self.customer_info_layout.addWidget(QLabel("ที่อยู่:"), 1, 0)
        self.customer_address_edit = QLineEdit()
        self.customer_address_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.customer_address_edit, 1, 1)
        
        # เลขบัตรประชาชน
        self.customer_info_layout.addWidget(QLabel("บัตร:"), 2, 0)
        self.id_card_type_combo = QComboBox()
        self.id_card_type_combo.addItems(["บัตรประชาชน", "ใบขับขี่", "พาสปอร์ต"])
        self.id_card_type_combo.setEnabled(False)
        self.customer_info_layout.addWidget(self.id_card_type_combo, 2, 1)
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.id_card_edit, 2, 2)
        
        # ที่อยู่บ้าน
        self.customer_info_layout.addWidget(QLabel("ที่อยู่บ้านเลขที่:"), 3, 0)
        self.house_number_edit = QLineEdit()
        self.house_number_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.house_number_edit, 3, 1)
        
        # ซอย/ถนน
        self.customer_info_layout.addWidget(QLabel("ซอย/ถนน:"), 4, 0)
        self.street_edit = QLineEdit()
        self.street_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.street_edit, 4, 1)
        
        # ตำบล
        self.customer_info_layout.addWidget(QLabel("ตำบล:"), 5, 0)
        self.subdistrict_edit = QLineEdit()
        self.subdistrict_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.subdistrict_edit, 5, 1)
        
        # อำเภอ
        self.customer_info_layout.addWidget(QLabel("อำเภอ:"), 6, 0)
        self.district_edit = QLineEdit()
        self.district_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.district_edit, 6, 1)
        
        # จังหวัด
        self.customer_info_layout.addWidget(QLabel("จังหวัด:"), 7, 0)
        self.province_edit = QLineEdit()
        self.province_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.province_edit, 7, 1)
        
        # โทรศัพท์
        self.customer_info_layout.addWidget(QLabel("โทรศัพท์:"), 8, 0)
        self.phone_edit = QLineEdit()
        self.phone_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.phone_edit, 8, 1)
        
        # รายละเอียดอื่นๆ
        self.customer_info_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 9, 0)
        self.other_details_edit = QLineEdit()
        self.other_details_edit.setReadOnly(True)
        self.customer_info_layout.addWidget(self.other_details_edit, 9, 1)
        
        layout.addWidget(self.customer_info_group)
        
        # Customer add form section (initially hidden)
        self.customer_add_group = QGroupBox("เพิ่มลูกค้าใหม่")
        self.customer_add_layout = QGridLayout(self.customer_add_group)
        self.customer_add_layout.setSpacing(10)
        self.customer_add_layout.setContentsMargins(15, 20, 15, 15)
        
        # รหัสลูกค้า (สร้างอัตโนมัติ)
        self.customer_add_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        self.customer_code_display_edit = QLineEdit()
        self.customer_code_display_edit.setReadOnly(True)
        self.customer_code_display_edit.setStyleSheet("background-color: #F0F0F0; color: #666;")
        self.customer_add_layout.addWidget(self.customer_code_display_edit, 0, 1, 1, 3)
        
        # ชื่อ-นามสกุล
        self.customer_add_layout.addWidget(QLabel("ชื่อ:"), 1, 0)
        self.customer_first_name_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_first_name_edit, 1, 1)
        
        self.customer_add_layout.addWidget(QLabel("นามสกุล:"), 1, 2)
        self.customer_last_name_edit = QLineEdit()
        self.customer_add_layout.addWidget(self.customer_last_name_edit, 1, 3)
        
        # เลขบัตรประชาชน
        self.customer_add_layout.addWidget(QLabel("เลขบัตรประชาชน:"), 2, 0)
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
        self.customer_save_btn = QPushButton("บันทึก")
        self.customer_save_btn.clicked.connect(self.save_new_customer)
        self.customer_save_btn.setIcon(QIcon.fromTheme("document-save"))
        button_layout.addWidget(self.customer_save_btn)
        
        self.customer_cancel_btn = QPushButton("ยกเลิก")
        self.customer_cancel_btn.clicked.connect(self.toggle_customer_mode)
        self.customer_cancel_btn.setIcon(QIcon.fromTheme("edit-clear"))
        button_layout.addWidget(self.customer_cancel_btn)
        
        self.customer_add_layout.addLayout(button_layout, 8, 0, 1, 4)
        
        # ซ่อนฟอร์มเพิ่มลูกค้าไว้ก่อน
        self.customer_add_group.hide()
        layout.addWidget(self.customer_add_group)
        
        return tab

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
        group_box = QGroupBox("ค้นหา")
        group_box.setObjectName("SearchGroup")
        layout = QVBoxLayout(group_box)
        layout.setSpacing(15)  # เพิ่มระยะห่างระหว่างส่วนต่างๆ
        layout.setContentsMargins(15, 20, 15, 15)  # เพิ่ม margin รอบๆ
        
        form_layout = QGridLayout()
        form_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างคอลัมน์
        form_layout.addWidget(QLabel("เลขที่สัญญา"), 0, 0)
        self.search_contract_combo = QComboBox()
        self.search_contract_combo.addItems(["=", ">", "<", ">=", "<="])
        form_layout.addWidget(self.search_contract_combo, 0, 1)
        self.search_contract_edit = QLineEdit()
        form_layout.addWidget(self.search_contract_edit, 0, 2)

        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # เพิ่มระยะห่างระหว่างปุ่ม
        self.search_next_btn = QPushButton("ถัดไป")
        self.search_next_btn.clicked.connect(self.search_next)
        self.search_next_btn.setIcon(QIcon.fromTheme("go-next"))
        button_layout.addWidget(self.search_next_btn)
        self.search_name_btn = QPushButton("หาชื่อนอกรีต")
        self.search_name_btn.clicked.connect(self.search_by_name)
        self.search_name_btn.setIcon(QIcon.fromTheme("system-search"))
        button_layout.addWidget(self.search_name_btn)
        layout.addLayout(button_layout)

        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(15)  # เพิ่มระยะห่างระหว่าง radio button
        radio_layout.addWidget(QLabel("(F5)"))
        self.active_radio = QRadioButton("สัญญาเปิด")
        self.closed_radio = QRadioButton("สัญญาปิด")
        self.all_radio = QRadioButton("ทั้งหมด")
        self.all_radio.setChecked(True)
        radio_layout.addWidget(self.active_radio)
        radio_layout.addWidget(self.closed_radio)
        radio_layout.addWidget(self.all_radio)
        layout.addLayout(radio_layout)
        
        return group_box

    def create_data_table(self):
        self.contract_table = QTableWidget(0, 8)  # เพิ่มคอลัมน์หัก ณ ที่จ่าย
        headers = ["ลำดับ", "ค่าเช่า", "ค่าปรับ", "ส่วนลด", "หัก ณ ที่จ่าย", "รวม", "วันที่กำหนดส่ง", "ครบกำหนด"]
        self.contract_table.setHorizontalHeaderLabels(headers)
        
        # ไม่แสดงข้อมูลใดๆ เมื่อเริ่มต้น
        self.contract_table.setRowCount(0)
        
        # ตั้งค่าความกว้างคอลัมน์
        header = self.contract_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ลำดับ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ค่าเช่า
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # ค่าปรับ
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # ส่วนลด
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # หัก ณ ที่จ่าย
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # รวม
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # วันที่กำหนดส่ง
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # ครบกำหนด
        
        # ตั้งค่าการแสดงผลตาราง
        self.contract_table.setAlternatingRowColors(True)  # สลับสีแถว
        self.contract_table.setSelectionBehavior(QTableWidget.SelectRows)  # เลือกทั้งแถว
        self.contract_table.setEditTriggers(QTableWidget.NoEditTriggers)  # ไม่ให้แก้ไขได้
        
        return self.contract_table

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # เมนูไฟล์
        file_menu = menu_bar.addMenu("ไฟล์")
        view_data_action = QAction("ดูข้อมูลทั้งหมด", self)
        view_data_action.triggered.connect(self.view_contracts)
        file_menu.addAction(view_data_action)
        
        # เมนูลูกค้า
        customer_menu = menu_bar.addMenu("ลูกค้า")
        add_customer_action = QAction("เพิ่มลูกค้า", self)
        add_customer_action.triggered.connect(self.toggle_customer_mode)
        customer_menu.addAction(add_customer_action)
        
        # เมนูรายงาน
        report_menu = menu_bar.addMenu("รายงาน")
        daily_report_action = QAction("รายงานประจำวัน", self)
        daily_report_action.triggered.connect(self.show_daily_report)
        report_menu.addAction(daily_report_action)
        
        monthly_report_action = QAction("รายงานประจำเดือน", self)
        monthly_report_action.triggered.connect(self.show_monthly_report)
        report_menu.addAction(monthly_report_action)
        
        withholding_tax_report_action = QAction("รายงานหัก ณ ที่จ่าย", self)
        withholding_tax_report_action.triggered.connect(self.show_withholding_tax_report)
        report_menu.addAction(withholding_tax_report_action)
        
        # เมนูจัดการค่าธรรมเนียม
        fee_menu = menu_bar.addMenu("จัดการค่าธรรมเนียม")
        fee_management_action = QAction("ตารางจัดการค่าธรรมเนียม", self)
        fee_management_action.triggered.connect(self.show_fee_management)
        fee_menu.addAction(fee_management_action)

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

        # ปรับปรุง icon names ให้เหมาะสมและมี icon ทุกปุ่ม
        actions = [
            ("สร้างสัญญาใหม่", "document-new", self.generate_new_contract),
            ("ล้างฟอร์ม", "edit-clear", self.clear_form),
            ("บันทึกสัญญา", "document-save", self.save_contract),
            ("ต่อดอก", "view-refresh", self.extend_interest),
            ("ไถ่ถอน", "go-previous", self.redeem_contract),
            ("หลุดจำนำ", "edit-delete", self.lost_contract),
            ("ในขายฝาก", "folder-open", self.view_contracts),
            ("สรุปขายฝาก", "document-properties", self.summary_report),
            ("รับ", "arrow-down", self.receive_payment),
            ("หัก ณ ที่จ่าย", "document-edit", self.calculate_withholding_tax),
            ("รายงานหัก ณ ที่จ่าย", "document-properties", self.show_withholding_tax_report),
            ("บัญชีรายวัน", "x-office-calendar", self.daily_account),
            ("ตารางดอก", "insert-object", self.interest_schedule),
            ("ค่าธรรมเนียม", "preferences-system", self.show_fee_management)
        ]

        for i, (text, icon_name, slot) in enumerate(actions):
            # สร้าง icon ที่เหมาะสมสำหรับแต่ละปุ่ม
            icon = self.create_icon_for_action(icon_name, text)
            action = QAction(icon, text, self)
            action.triggered.connect(slot)
            
            # เพิ่ม tooltip เพื่อความชัดเจน
            action.setToolTip(text)
            
            # เพิ่ม status tip สำหรับ status bar
            action.setStatusTip(f"คลิกเพื่อ {text}")
            
            toolbar.addAction(action)
            
            # เพิ่ม separator หลังปุ่มที่ 3 และ 6 เพื่อแบ่งกลุ่ม
            if i == 2 or i == 5:
                toolbar.addSeparator()

    def create_icon_for_action(self, icon_name, text):
        """สร้าง icon ที่เหมาะสมสำหรับแต่ละปุ่ม"""
        # ลองใช้ system theme icons ก่อน
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
            else:
                # fallback ไปใช้ icon ทั่วไป
                icon = QIcon.fromTheme("applications-other", QIcon.fromTheme("help", QIcon.fromTheme("info")))
        
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
        
        # ยอดไถ่ถอน
        total_redemption = pawn_amount + interest_amount + fee_amount
        
        # แสดงผล
        self.fee_amount_label.setText("{:,.2f} บาท".format(fee_amount))
        self.withholding_tax_amount_label.setText("{:,.2f} บาท".format(withholding_tax_amount))
        self.total_paid_label.setText("{:,.2f} บาท".format(total_paid))
        self.total_redemption_label.setText("{:,.2f} บาท".format(total_redemption))

    def add_customer(self):
        """เพิ่มลูกค้า (legacy - เรียกใช้ฟังก์ชันใหม่แทน)"""
        self.toggle_customer_mode()

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
        self.toggle_product_mode()

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

    def extend_interest(self):
        """ต่อดอกเบี้ย"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        dialog = InterestPaymentDialog(self, self.current_contract)
        dialog.exec()

    def redeem_contract(self):
        """ไถ่ถอนสัญญา"""
        if not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาก่อน")
            return
        
        dialog = RedemptionDialog(self, self.current_contract)
        dialog.exec()

    def lost_contract(self):
        """หลุดจำนำ"""
        QMessageBox.information(self, "หลุดจำนำ", "ฟีเจอร์หลุดจำนำ")

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
            'days_count': self.days_spin.value()
        }
        
        try:
            contract_id = self.db.create_contract(contract_data)
            QMessageBox.information(self, "สำเร็จ", "บันทึกสัญญาเรียบร้อย")
            self.generate_new_contract_number()
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))

    def view_contracts(self):
        """ดูข้อมูลทั้งหมด"""
        dialog = DataViewerDialog(self)
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

    def search_next(self):
        """ค้นหาถัดไป"""
        search_term = self.search_contract_edit.text().strip()
        if not search_term:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกคำค้นหา")
            return
        
        # กำหนดสถานะการค้นหา
        status = 'all'
        if self.active_radio.isChecked():
            status = 'active'
        elif self.closed_radio.isChecked():
            status = 'redeemed'
        
        # ค้นหาสัญญา
        contracts = self.db.search_contracts(search_term, status)
        if contracts:
            self.current_contract = contracts[0]
            self.load_contract_data()
            self.display_contract_in_table(contracts)
        else:
            QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสัญญาที่ตรงกับคำค้นหา")
    
    def display_contract_in_table(self, contracts: list):
        """แสดงข้อมูลสัญญาในตาราง"""
        self.contract_table.setRowCount(len(contracts))
        
        for row, contract in enumerate(contracts):
            # ลำดับ
            self.contract_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # ค่าเช่า (ดอกเบี้ย)
            interest_amount = (contract.get('pawn_amount', 0) * contract.get('interest_rate', 0) * contract.get('days_count', 0)) / 100
            self.contract_table.setItem(row, 1, QTableWidgetItem(f"{interest_amount:,.2f}"))
            
            # ค่าปรับ
            penalty_amount = contract.get('penalty_amount', 0)
            self.contract_table.setItem(row, 2, QTableWidgetItem(f"{penalty_amount:,.2f}"))
            
            # ส่วนลด
            discount_amount = contract.get('discount_amount', 0)
            self.contract_table.setItem(row, 3, QTableWidgetItem(f"{discount_amount:,.2f}"))
            
            # หัก ณ ที่จ่าย
            withholding_tax_amount = contract.get('withholding_tax_amount', 0)
            self.contract_table.setItem(row, 4, QTableWidgetItem(f"{withholding_tax_amount:,.2f}"))
            
            # รวม
            total_amount = interest_amount + penalty_amount - discount_amount - withholding_tax_amount
            self.contract_table.setItem(row, 5, QTableWidgetItem(f"{total_amount:,.2f}"))
            
            # วันที่กำหนดส่ง
            end_date = contract.get('end_date', '')
            self.contract_table.setItem(row, 6, QTableWidgetItem(end_date))
            
            # ครบกำหนด
            is_overdue = "ครบกำหนด" if contract.get('status') == 'active' else "ไถ่ถอนแล้ว"
            self.contract_table.setItem(row, 7, QTableWidgetItem(is_overdue))
            
            # เก็บข้อมูล ID ไว้ใน item
            self.contract_table.item(row, 0).setData(Qt.UserRole, contract.get('id'))

    def search_by_name(self):
        """ค้นหาตามชื่อ"""
        # เปิดหน้าต่างค้นหาลูกค้า
        dialog = CustomerSearchDialog(self)
        if dialog.exec():
            selected_customer = dialog.selected_customer
            if selected_customer:
                # ค้นหาสัญญาของลูกค้าคนนี้
                contracts = self.db.get_contracts_by_customer(selected_customer['id'])
                if contracts:
                    self.current_contract = contracts[0]
                    self.load_contract_data()
                    self.display_contract_in_table(contracts)
                else:
                    QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสัญญาของลูกค้าคนนี้")

    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.current_contract:
            self.contract_number_edit.setText(self.current_contract.get('contract_number', ''))
            # โหลดข้อมูลลูกค้า
            customer_name = "{} {}".format(self.current_contract.get('first_name', ''), self.current_contract.get('last_name', ''))
            self.customer_name_edit.setText(customer_name)
            # โหลดข้อมูลสินค้า
            self.product_name_display_edit.setText(self.current_contract.get('product_name', ''))
            
            # โหลดข้อมูลหัก ณ ที่จ่าย
            if 'withholding_tax_rate' in self.current_contract:
                self.withholding_tax_rate_spin.setValue(self.current_contract.get('withholding_tax_rate', 3.0))
            
            # คำนวณยอดต่างๆ ใหม่
            self.calculate_amounts()

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
การไถ่ถอน: {} สัญญา ({:,.2f} บาท)
การชำระดอกเบี้ย: {} ครั้ง ({:,.2f} บาท)
            """.format(
                today,
                summary['new_contracts_count'],
                summary['new_contracts_amount'],
                summary['redemptions_count'],
                summary['redemptions_amount'],
                summary['interest_payments_count'],
                summary['interest_payments_amount']
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
    
    def update_withholding_tax_rate(self):
        """อัปเดตอัตราหัก ณ ที่จ่าย"""
        current_rate = self.withholding_tax_rate_spin.value()
        
        # อัปเดตในฐานข้อมูล
        if self.db.update_withholding_tax_rate(current_rate):
            QMessageBox.information(self, "สำเร็จ", f"อัปเดตอัตราหัก ณ ที่จ่ายเป็น {current_rate:.2f}% เรียบร้อย")
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
        prefix = self.db.get_setting('customer_prefix') if hasattr(self.db, 'get_setting') else "C"
        # คำนวณลำดับถัดไปจากฐานข้อมูล
        sequence = self.db.get_next_customer_sequence(prefix)
        customer_code = PawnShopUtils.generate_customer_code(prefix, sequence)
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
        """คัดลอกรูปภาพสินค้าไปยังโฟลเดอร์ของโปรแกรม"""
        if not source_path or not os.path.exists(source_path):
            return ""
        
        try:
            # สร้างโฟลเดอร์สำหรับรูปภาพสินค้า
            images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "product_images")
            os.makedirs(images_dir, exist_ok=True)
            
            # สร้างชื่อไฟล์ใหม่
            file_ext = os.path.splitext(source_path)[1]
            new_filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
            new_path = os.path.join(images_dir, new_filename)
            
            # คัดลอกไฟล์
            import shutil
            shutil.copy2(source_path, new_path)
            
            return new_path
        except Exception as e:
            print(f"Error copying image: {e}")
            return source_path  # คืนค่า path เดิมถ้าเกิดข้อผิดพลาด

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PawnShopUI()
    window.show()
    sys.exit(app.exec())