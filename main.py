# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QToolBar,
    QMenuBar, QMessageBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit,
    QScrollArea, QFrame
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize, QDate
from datetime import datetime, timedelta
from database import PawnShopDatabase
from utils import PawnShopUtils
from dialogs import CustomerDialog, ProductDialog, InterestPaymentDialog, RedemptionDialog
from data_viewer import DataViewerDialog
from customer_search import CustomerSearchDialog
from product_search import ProductSearchDialog

class PawnShopUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = PawnShopDatabase()
        self.current_customer = None
        self.current_product = None
        self.current_contract = None
        
        self.setWindowTitle("โปรแกรมรับจำนำ")
        self.setGeometry(100, 100, 1600, 900)

        # Apply styles to mimic the original UI
        self.setStyleSheet("""
            QWidget {
                font-family: Tahoma;
                font-size: 11px;
            }
            QMainWindow {
                background-color: #F0F0F0;
            }
            QGroupBox {
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                margin-left: 10px;
            }
            #TopLeftGroup {
                background-color: #E6EFDE;
            }
            #TopMiddleGroup {
                background-color: #FEFDE4;
            }
            #SearchGroup {
                background-color: #DCEAF6;
            }
            #TabWidget, #TabWidget > QWidget > QWidget{
                background-color: #FDECEC;
            }
            QTabBar::tab {
                background: #F0F0F0;
                padding: 5px 10px;
                border: 1px solid #B0B0B0;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #FDECEC;
                border: 1px solid #888;
                border-bottom: 1px solid #FDECEC;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #D0D0D0;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                padding: 4px;
                border: 1px solid #C0C0C0;
            }
            QPushButton {
                background-color: #F0F0F0;
                min-height: 23px;
                border: 1px solid #888;
            }
            QToolButton {
                 background-color: #F0F0F0;
            }
            QLineEdit {
                padding: 2px;
                border: 1px solid #888;
            }
            QDateEdit {
                padding: 2px;
                border: 1px solid #888;
            }
            QSpinBox, QDoubleSpinBox {
                padding: 2px;
                border: 1px solid #888;
            }
        """)

        # --- Menu Bar ---
        self.create_menu_bar()

        # --- Main Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Section ---
        main_layout.addWidget(self.create_top_section())

        # --- Main Content Area ---
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        
        # Left side - Contract form
        content_layout.addWidget(self.create_contract_form(), 2)
        
        # Right side - Search and data
        content_layout.addWidget(self.create_right_panel(), 1)
        
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
            
            self.interest_rate_spin.setValue(default_interest_rate)
            self.days_spin.setValue(default_days)
        except:
            # ใช้ค่าเริ่มต้นถ้าไม่มีการตั้งค่า
            self.interest_rate_spin.setValue(3.0)
            self.days_spin.setValue(30)

    def create_top_section(self):
        """สร้างส่วนบนของ UI"""
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        
        # Left group - Contract info
        left_group = self.create_top_left_group()
        top_layout.addWidget(left_group)
        
        # Middle group - Financial calculations
        middle_group = self.create_top_middle_group()
        top_layout.addWidget(middle_group)
        
        # Right group - Action buttons
        right_group = self.create_top_right_group()
        top_layout.addWidget(right_group)
        
        return top_widget

    def create_top_left_group(self):
        group_box = QGroupBox("ข้อมูลสัญญา")
        group_box.setObjectName("TopLeftGroup")
        layout = QGridLayout(group_box)
        
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

    def create_top_middle_group(self):
        group_box = QGroupBox("ผลจัดทำ")
        group_box.setObjectName("TopMiddleGroup")
        layout = QGridLayout(group_box)

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
        
        # ยอดจ่าย
        layout.addWidget(QLabel("ยอดจ่าย"), 3, 0)
        self.total_paid_label = QLabel("0.00 บาท")
        layout.addWidget(self.total_paid_label, 3, 1)

        # ยอดไถ่ถอน
        layout.addWidget(QLabel("ยอดไถ่ถอน"), 4, 0)
        self.total_redemption_label = QLabel("0.00 บาท")
        layout.addWidget(self.total_redemption_label, 4, 1)

        # เชื่อมต่อสัญญาณ
        self.pawn_amount_spin.valueChanged.connect(self.calculate_amounts)
        self.interest_rate_spin.valueChanged.connect(self.calculate_amounts)

        group_box.setFixedWidth(350)
        return group_box

    def create_top_right_group(self):
        group_box = QGroupBox("การดำเนินการ")
        layout = QVBoxLayout(group_box)
        
        # ปุ่มสร้างสัญญาใหม่
        self.new_contract_btn = QPushButton("สร้างสัญญาใหม่")
        self.new_contract_btn.clicked.connect(self.generate_new_contract)
        self.new_contract_btn.setMinimumHeight(40)
        layout.addWidget(self.new_contract_btn)
        
        # ปุ่มล้างฟอร์ม
        clear_btn = QPushButton("ล้างฟอร์ม")
        clear_btn.clicked.connect(self.clear_form)
        clear_btn.setMinimumHeight(30)
        layout.addWidget(clear_btn)
        
        # ปุ่มบันทึกสัญญา
        save_btn = QPushButton("บันทึกสัญญา")
        save_btn.clicked.connect(self.save_contract)
        save_btn.setMinimumHeight(30)
        layout.addWidget(save_btn)
        
        group_box.setFixedWidth(200)
        return group_box

    def create_contract_form(self):
        """สร้างฟอร์มสัญญา"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Tab widget for contract form
        tab_widget = QTabWidget()
        tab_widget.setObjectName("TabWidget")
        
        # Tab 1: Customer Info
        customer_tab = self.create_customer_tab()
        tab_widget.addTab(customer_tab, "ข้อมูลผู้ขายฝาก (F2)")
        
        # Tab 2: Product Info
        product_tab = self.create_product_tab()
        tab_widget.addTab(product_tab, "ข้อมูลสินค้าขายฝาก (F3)")
        

        
        form_layout.addWidget(tab_widget)
        scroll_area.setWidget(form_widget)
        
        return scroll_area

    def create_customer_tab(self):
        """สร้างแท็บข้อมูลลูกค้า"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Customer search section
        search_group = QGroupBox("ค้นหาลูกค้า")
        search_layout = QGridLayout(search_group)
        
        search_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        self.customer_code_edit = QLineEdit()
        search_layout.addWidget(self.customer_code_edit, 0, 1)
        
        self.customer_search_btn = QPushButton("ค้นหา")
        self.customer_search_btn.clicked.connect(self.search_customer)
        search_layout.addWidget(self.customer_search_btn, 0, 2)
        
        self.add_customer_btn = QPushButton("เพิ่มลูกค้าใหม่")
        self.add_customer_btn.clicked.connect(self.add_customer)
        search_layout.addWidget(self.add_customer_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Customer info section
        info_group = QGroupBox("ข้อมูลลูกค้า")
        info_layout = QGridLayout(info_group)
        
        # ชื่อลูกค้า
        info_layout.addWidget(QLabel("ชื่อผู้กู้:"), 0, 0)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setReadOnly(True)
        info_layout.addWidget(self.customer_name_edit, 0, 1)
        
        # ที่อยู่
        info_layout.addWidget(QLabel("ที่อยู่:"), 1, 0)
        self.customer_address_edit = QLineEdit()
        self.customer_address_edit.setReadOnly(True)
        info_layout.addWidget(self.customer_address_edit, 1, 1)
        
        # เลขบัตรประชาชน
        info_layout.addWidget(QLabel("บัตร:"), 2, 0)
        self.id_card_type_combo = QComboBox()
        self.id_card_type_combo.addItems(["บัตรประชาชน", "ใบขับขี่", "พาสปอร์ต"])
        info_layout.addWidget(self.id_card_type_combo, 2, 1)
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setReadOnly(True)
        info_layout.addWidget(self.id_card_edit, 2, 2)
        
        # ที่อยู่บ้าน
        info_layout.addWidget(QLabel("ที่อยู่บ้านเลขที่:"), 3, 0)
        self.house_number_edit = QLineEdit()
        self.house_number_edit.setReadOnly(True)
        info_layout.addWidget(self.house_number_edit, 3, 1)
        
        # ซอย/ถนน
        info_layout.addWidget(QLabel("ซอย/ถนน:"), 4, 0)
        self.street_edit = QLineEdit()
        self.street_edit.setReadOnly(True)
        info_layout.addWidget(self.street_edit, 4, 1)
        
        # ตำบล
        info_layout.addWidget(QLabel("ตำบล:"), 5, 0)
        self.subdistrict_edit = QLineEdit()
        self.subdistrict_edit.setReadOnly(True)
        info_layout.addWidget(self.subdistrict_edit, 5, 1)
        
        # อำเภอ
        info_layout.addWidget(QLabel("อำเภอ:"), 6, 0)
        self.district_edit = QLineEdit()
        self.district_edit.setReadOnly(True)
        info_layout.addWidget(self.district_edit, 6, 1)
        
        # จังหวัด
        info_layout.addWidget(QLabel("จังหวัด:"), 7, 0)
        self.province_edit = QLineEdit()
        self.province_edit.setReadOnly(True)
        info_layout.addWidget(self.province_edit, 7, 1)
        
        # โทรศัพท์
        info_layout.addWidget(QLabel("โทรศัพท์:"), 8, 0)
        self.phone_edit = QLineEdit()
        self.phone_edit.setReadOnly(True)
        info_layout.addWidget(self.phone_edit, 8, 1)
        
        # รายละเอียดอื่นๆ
        info_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 9, 0)
        self.other_details_edit = QLineEdit()
        self.other_details_edit.setReadOnly(True)
        info_layout.addWidget(self.other_details_edit, 9, 1)
        
        layout.addWidget(info_group)
        
        return tab

    def create_product_tab(self):
        """สร้างแท็บข้อมูลสินค้า"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Product search section
        search_group = QGroupBox("ค้นหาสินค้า")
        search_layout = QGridLayout(search_group)
        
        search_layout.addWidget(QLabel("ชื่อสินค้า:"), 0, 0)
        self.product_name_edit = QLineEdit()
        search_layout.addWidget(self.product_name_edit, 0, 1)
        
        self.product_search_btn = QPushButton("ค้นหา")
        self.product_search_btn.clicked.connect(self.search_product)
        search_layout.addWidget(self.product_search_btn, 0, 2)
        
        self.add_product_btn = QPushButton("เพิ่มสินค้าใหม่")
        self.add_product_btn.clicked.connect(self.add_product)
        search_layout.addWidget(self.add_product_btn, 0, 3)
        
        layout.addWidget(search_group)
        
        # Product info section
        info_group = QGroupBox("ข้อมูลสินค้า")
        info_layout = QGridLayout(info_group)
        
        # สินค้าฝากขาย
        info_layout.addWidget(QLabel("สินค้าฝากขาย:"), 0, 0)
        self.product_name_display_edit = QLineEdit()
        self.product_name_display_edit.setReadOnly(True)
        info_layout.addWidget(self.product_name_display_edit, 0, 1)
        
        # ยี่ห้อ/รุ่น
        info_layout.addWidget(QLabel("ยี่ห้อ/รุ่น:"), 1, 0)
        self.product_brand_edit = QLineEdit()
        self.product_brand_edit.setReadOnly(True)
        info_layout.addWidget(self.product_brand_edit, 1, 1)
        
        # ขนาด
        info_layout.addWidget(QLabel("ขนาด:"), 2, 0)
        self.product_size_edit = QLineEdit()
        self.product_size_edit.setReadOnly(True)
        info_layout.addWidget(self.product_size_edit, 2, 1)
        
        # น้ำหนัก
        info_layout.addWidget(QLabel("น้ำหนัก:"), 3, 0)
        self.product_weight_combo = QComboBox()
        self.product_weight_combo.addItems(["กรัม", "กิโลกรัม", "บาท"])
        self.product_weight_combo.setEnabled(False)
        info_layout.addWidget(self.product_weight_combo, 3, 1)
        
        # หมายเลขซีเรียล
        info_layout.addWidget(QLabel("หมายเลขซีเรียล:"), 4, 0)
        self.serial_number_edit = QLineEdit()
        self.serial_number_edit.setReadOnly(True)
        info_layout.addWidget(self.serial_number_edit, 4, 1)
        
        # รายละเอียดอื่นๆ
        info_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 5, 0)
        self.product_details_edit = QLineEdit()
        self.product_details_edit.setReadOnly(True)
        info_layout.addWidget(self.product_details_edit, 5, 1)
        
        layout.addWidget(info_group)
        
        return tab



    def create_right_panel(self):
        """สร้างแผงด้านขวา"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Search group
        search_group = self.create_search_group()
        right_layout.addWidget(search_group)
        
        # Data table
        data_table = self.create_data_table()
        right_layout.addWidget(data_table)
        
        return right_widget

    def create_search_group(self):
        group_box = QGroupBox("ค้นหา")
        group_box.setObjectName("SearchGroup")
        layout = QVBoxLayout(group_box)
        
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("เลขที่สัญญา"), 0, 0)
        self.search_contract_combo = QComboBox()
        self.search_contract_combo.addItems(["=", ">", "<", ">=", "<="])
        form_layout.addWidget(self.search_contract_combo, 0, 1)
        self.search_contract_edit = QLineEdit()
        form_layout.addWidget(self.search_contract_edit, 0, 2)

        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        self.search_next_btn = QPushButton("ถัดไป")
        self.search_next_btn.clicked.connect(self.search_next)
        button_layout.addWidget(self.search_next_btn)
        self.search_name_btn = QPushButton("หาชื่อนอกรีต")
        self.search_name_btn.clicked.connect(self.search_by_name)
        button_layout.addWidget(self.search_name_btn)
        layout.addLayout(button_layout)

        radio_layout = QHBoxLayout()
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
        self.contract_table = QTableWidget(0, 7)  # Start with 0 rows
        headers = ["ลำดับ", "ค่าเช่า", "ค่าปรับ", "ส่วนลด", "รวม", "วันที่กำหนดส่ง", "ครบกำหนด"]
        self.contract_table.setHorizontalHeaderLabels(headers)
        
        # ไม่แสดงข้อมูลใดๆ เมื่อเริ่มต้น
        self.contract_table.setRowCount(0)
        
        self.contract_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        add_customer_action.triggered.connect(self.add_customer)
        customer_menu.addAction(add_customer_action)
        
        # เมนูรายงาน
        report_menu = menu_bar.addMenu("รายงาน")
        daily_report_action = QAction("รายงานประจำวัน", self)
        daily_report_action.triggered.connect(self.show_daily_report)
        report_menu.addAction(daily_report_action)
        
        monthly_report_action = QAction("รายงานประจำเดือน", self)
        monthly_report_action.triggered.connect(self.show_monthly_report)
        report_menu.addAction(monthly_report_action)

    def create_bottom_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)

        # Using standard icons as placeholders
        actions = [
            ("ต่อดอก", "view-refresh", self.extend_interest),
            ("ไถ่ถอน", "go-previous", self.redeem_contract),
            ("หลุดจำนำ", "edit-delete", self.lost_contract),
            ("ในขายฝาก", "folder-open", self.view_contracts),
            ("สรุปขายฝาก", "document-properties", self.summary_report),
            ("รับ", "arrow-down", self.receive_payment),
            ("บัญชีรายวัน", "x-office-calendar", self.daily_account),
            ("ตารางดอก", "insert-object", self.interest_schedule)
        ]

        for text, icon_name, slot in actions:
            icon = QIcon.fromTheme(icon_name) 
            action = QAction(icon, text, self)
            action.triggered.connect(slot)
            toolbar.addAction(action)

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
        
        # คำนวณดอกเบี้ย
        interest_amount = PawnShopUtils.calculate_interest(pawn_amount, interest_rate, days)
        
        # ค่าธรรมเนียม (ตัวอย่าง)
        fee_amount = interest_amount
        
        # ยอดจ่าย
        total_paid = pawn_amount
        
        # ยอดไถ่ถอน
        total_redemption = pawn_amount + interest_amount
        
        # แสดงผล
        self.fee_amount_label.setText("{:,.2f} บาท".format(fee_amount))
        self.total_paid_label.setText("{:,.2f} บาท".format(total_paid))
        self.total_redemption_label.setText("{:,.2f} บาท".format(total_redemption))

    def add_customer(self):
        """เพิ่มลูกค้า"""
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.current_customer = dialog.customer_data
            self.load_customer_data()

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
        """เพิ่มสินค้า"""
        dialog = ProductDialog(self)
        if dialog.exec():
            self.current_product = dialog.product_data
            self.load_product_data()

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
        else:
            QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบสัญญาที่ตรงกับคำค้นหา")

    def search_by_name(self):
        """ค้นหาตามชื่อ"""
        QMessageBox.information(self, "ค้นหาตามชื่อ", "ฟีเจอร์ค้นหาตามชื่อ")

    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.current_contract:
            self.contract_number_edit.setText(self.current_contract.get('contract_number', ''))
            # โหลดข้อมูลลูกค้า
            customer_name = "{} {}".format(self.current_contract.get('first_name', ''), self.current_contract.get('last_name', ''))
            self.customer_name_edit.setText(customer_name)
            # โหลดข้อมูลสินค้า
            self.product_name_display_edit.setText(self.current_contract.get('product_name', ''))

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
        
        # รีเซ็ตยอด
        self.pawn_amount_spin.setValue(0)
        self.calculate_amounts()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PawnShopUI()
    window.show()
    sys.exit(app.exec())