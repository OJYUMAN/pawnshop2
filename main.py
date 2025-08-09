import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QToolBar,
    QMenuBar, QMessageBox, QDateEdit, QDoubleSpinBox, QSpinBox
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize, QDate
from datetime import datetime, timedelta
from database import PawnShopDatabase
from utils import PawnShopUtils
from dialogs import CustomerDialog, ProductDialog, InterestPaymentDialog, RedemptionDialog
from contract_form import NewContractDialog
from data_viewer import DataViewerDialog

class PawnShopUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = PawnShopDatabase()
        self.current_customer = None
        self.current_product = None
        self.current_contract = None
        
        self.setWindowTitle("โปรแกรมรับจำนำ")
        self.setGeometry(100, 100, 1400, 800)

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
        """)

        # --- Menu Bar ---
        self.create_menu_bar()

        # --- Main Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_v_layout = QVBoxLayout()
        right_v_layout = QVBoxLayout()

        main_layout.addLayout(left_v_layout, 2)  # Left side takes more space
        main_layout.addLayout(right_v_layout, 1) # Right side

        # --- Top Section (Left and Middle) ---
        top_h_layout = QHBoxLayout()
        top_h_layout.addWidget(self.create_top_left_group())
        top_h_layout.addWidget(self.create_top_middle_group())
        left_v_layout.addLayout(top_h_layout)

        # --- Tab Widget ---
        left_v_layout.addWidget(self.create_main_tabs())

        # --- Right Section ---
        right_v_layout.addWidget(self.create_search_group())
        right_v_layout.addWidget(self.create_data_table())

        # --- Bottom Toolbar ---
        self.create_bottom_toolbar()

        # --- Initialize UI ---
        self.initialize_ui()

    def initialize_ui(self):
        """เริ่มต้น UI"""
        # สร้างเลขที่สัญญาใหม่
        self.generate_new_contract_number()
        
        # ตั้งค่าวันที่เริ่มต้น
        self.start_date_edit.setDate(QDate.currentDate())
        
        # โหลดการตั้งค่า
        self.load_settings()

    def load_settings(self):
        """โหลดการตั้งค่า"""
        default_interest_rate = float(self.db.get_setting('default_interest_rate'))
        default_days = int(self.db.get_setting('default_contract_days'))
        
        self.interest_rate_spin.setValue(default_interest_rate)
        self.days_spin.setValue(default_days)

    def generate_new_contract_number(self):
        """สร้างเลขที่สัญญาใหม่"""
        prefix = self.db.get_setting('contract_prefix')
        # TODO: คำนวณลำดับถัดไปจากฐานข้อมูล
        sequence = 1078  # ตัวอย่าง
        contract_number = PawnShopUtils.generate_contract_number(prefix, sequence)
        self.contract_number_edit.setText(contract_number)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # เมนูไฟล์
        file_menu = menu_bar.addMenu("ไฟล์")
        new_contract_action = QAction("สัญญาใหม่", self)
        new_contract_action.triggered.connect(self.new_contract)
        file_menu.addAction(new_contract_action)
        
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

    def create_top_left_group(self):
        group_box = QGroupBox()
        group_box.setObjectName("TopLeftGroup")
        layout = QGridLayout(group_box)
        
        # เลขที่สัญญา
        layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        self.contract_number_edit = QLineEdit()
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

    def create_main_tabs(self):
        tab_widget = QTabWidget()
        tab_widget.setObjectName("TabWidget")

        # Tab 1: Seller Info
        seller_tab = QWidget()
        seller_layout = QGridLayout(seller_tab)
        seller_layout.addWidget(QLabel("(F2)"), 0, 0)
        seller_group = QGroupBox("ข้อมูลผู้ขายฝาก")
        
        seller_form_layout = QGridLayout(seller_group)
        
        # รหัสลูกค้า
        seller_form_layout.addWidget(QLabel("รหัสลูกค้า"), 0, 0)
        self.customer_code_edit = QLineEdit()
        seller_form_layout.addWidget(self.customer_code_edit, 0, 1)
        self.customer_search_btn = QPushButton("ค้นหา")
        self.customer_search_btn.clicked.connect(self.search_customer)
        seller_form_layout.addWidget(self.customer_search_btn, 0, 2)
        
        # ชื่อลูกค้า
        seller_form_layout.addWidget(QLabel("ชื่อผู้กู้"), 1, 0)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.customer_name_edit, 1, 1)
        
        # ที่อยู่
        seller_form_layout.addWidget(QLabel("ที่อยู่"), 2, 0)
        self.customer_address_edit = QLineEdit()
        self.customer_address_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.customer_address_edit, 2, 1)
        
        # เลขบัตรประชาชน
        seller_form_layout.addWidget(QLabel("บัตร"), 3, 0)
        self.id_card_type_combo = QComboBox()
        self.id_card_type_combo.addItems(["บัตรประชาชน", "ใบขับขี่", "พาสปอร์ต"])
        seller_form_layout.addWidget(self.id_card_type_combo, 3, 1)
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.id_card_edit, 3, 2)
        
        # ที่อยู่บ้าน
        seller_form_layout.addWidget(QLabel("ที่อยู่บ้านเลขที่"), 4, 0)
        self.house_number_edit = QLineEdit()
        self.house_number_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.house_number_edit, 4, 1)
        
        # ซอย/ถนน
        seller_form_layout.addWidget(QLabel("ซอย/ถนน"), 5, 0)
        self.street_edit = QLineEdit()
        self.street_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.street_edit, 5, 1)
        
        # ตำบล
        seller_form_layout.addWidget(QLabel("ตำบล"), 6, 0)
        self.subdistrict_edit = QLineEdit()
        self.subdistrict_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.subdistrict_edit, 6, 1)
        
        # อำเภอ
        seller_form_layout.addWidget(QLabel("อำเภอ"), 7, 0)
        self.district_edit = QLineEdit()
        self.district_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.district_edit, 7, 1)
        
        # จังหวัด
        seller_form_layout.addWidget(QLabel("จังหวัด"), 8, 0)
        self.province_edit = QLineEdit()
        self.province_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.province_edit, 8, 1)
        
        # โทรศัพท์
        seller_form_layout.addWidget(QLabel("โทรศัพท์"), 9, 0)
        self.phone_edit = QLineEdit()
        self.phone_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.phone_edit, 9, 1)
        
        # รายละเอียดอื่นๆ
        seller_form_layout.addWidget(QLabel("รายละเอียดอื่นๆ"), 10, 0)
        self.other_details_edit = QLineEdit()
        self.other_details_edit.setReadOnly(True)
        seller_form_layout.addWidget(self.other_details_edit, 10, 1)
        
        seller_layout.addWidget(seller_group, 1, 0, 1, 2)
        tab_widget.addTab(seller_tab, "F2 ข้อมูลผู้ขายฝาก")

        # Tab 2: Product Info
        product_tab = QWidget()
        product_layout = QGridLayout(product_tab)
        product_layout.addWidget(QLabel("(F3)"), 0, 0)
        product_group = QGroupBox("ข้อมูลสินค้าขายฝาก")

        product_form_layout = QGridLayout(product_group)
        
        # สินค้าฝากขาย
        product_form_layout.addWidget(QLabel("สินค้าฝากขาย"), 0, 0)
        self.product_name_edit = QLineEdit()
        product_form_layout.addWidget(self.product_name_edit, 0, 1)
        self.product_add_btn = QPushButton("เพิ่ม")
        self.product_add_btn.clicked.connect(self.add_product)
        product_form_layout.addWidget(self.product_add_btn, 0, 2)

        # ยี่ห้อ/รุ่น
        product_form_layout.addWidget(QLabel("ยี่ห้อ/รุ่น"), 1, 0)
        self.product_brand_edit = QLineEdit()
        product_form_layout.addWidget(self.product_brand_edit, 1, 1)
        self.brand_add_btn = QPushButton("เพิ่ม")
        product_form_layout.addWidget(self.brand_add_btn, 1, 2)

        # ขนาด
        product_form_layout.addWidget(QLabel("ขนาด"), 2, 0)
        self.product_size_edit = QLineEdit()
        product_form_layout.addWidget(self.product_size_edit, 2, 1)
        self.size_add_btn = QPushButton("เพิ่ม")
        product_form_layout.addWidget(self.size_add_btn, 2, 2)

        # น้ำหนัก
        product_form_layout.addWidget(QLabel("น้ำหนัก"), 3, 0)
        self.product_weight_combo = QComboBox()
        self.product_weight_combo.addItems(["กรัม", "กิโลกรัม", "บาท"])
        product_form_layout.addWidget(self.product_weight_combo, 3, 1)
        self.weight_add_btn = QPushButton("เพิ่ม")
        product_form_layout.addWidget(self.weight_add_btn, 3, 2)

        # หมายเลขซีเรียล
        product_form_layout.addWidget(QLabel("หมายเลขซีเรียล"), 4, 0, Qt.AlignTop)
        self.serial_number_edit = QLineEdit()
        product_form_layout.addWidget(self.serial_number_edit, 4, 1)
        
        # รายละเอียดอื่นๆ
        product_form_layout.addWidget(QLabel("รายละเอียดอื่นๆ"), 5, 0, Qt.AlignTop)
        self.product_details_edit = QLineEdit()
        product_form_layout.addWidget(self.product_details_edit, 5, 1)

        # รูปภาพสินค้า
        image_layout = QVBoxLayout()
        image_layout.addWidget(QLabel("รูปภาพสินค้า"))
        for i in range(4):
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(QPushButton("📂"))
            btn_layout.addWidget(QPushButton("VIEW"))
            image_layout.addLayout(btn_layout)
        product_form_layout.addLayout(image_layout, 0, 3, 6, 1)
        
        product_layout.addWidget(product_group, 1, 0, 1, 2)
        tab_widget.addTab(product_tab, "F3 ข้อมูลสินค้าขายฝาก")

        return tab_widget

    def create_search_group(self):
        group_box = QGroupBox("ค้นหา")
        group_box.setObjectName("SearchGroup")
        layout = QVBoxLayout(group_box)
        
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("เลขที่สัญญา"), 0, 0)
        self.search_contract_combo = QComboBox()
        self.search_contract_combo.setEditable(True)
        form_layout.addWidget(self.search_contract_combo, 0, 1)
        form_layout.addWidget(QLabel("="), 0, 2)
        self.search_contract_edit = QLineEdit()
        form_layout.addWidget(self.search_contract_edit, 0, 3)

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
        self.contract_table = QTableWidget(19, 7)
        headers = ["ลำดับ", "ค่าเช่า", "ค่าปรับ", "ส่วนลด", "รวม", "วันที่กำหนดส่ง", "ครบกำหนด"]
        self.contract_table.setHorizontalHeaderLabels(headers)
        
        # Sample data
        data = [
            ("1", "300", "0", "0", "300", "23/11/2553", "23/12/2553"),
            ("2", "300", "100", "0", "400", "23/12/2553", "22/1/2554"),
            ("3", "300", "50", "0", "350", "22/1/2554", "21/2/2554")
        ]

        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                self.contract_table.setItem(row_idx, col_idx, QTableWidgetItem(cell_data))

        self.contract_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return self.contract_table

    def create_bottom_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)

        # Using standard icons as placeholders
        actions = [
            ("สัญญาใหม่", "document-new", self.new_contract),
            ("ต่อดอก", "view-refresh", self.extend_interest),
            ("ไถ่ถอน", "go-previous", self.redeem_contract),
            ("หลุดจำนำ", "edit-delete", self.lost_contract),
            ("จัดเก็บ", "document-save", self.save_contract),
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
        self.fee_amount_label.setText(f"{fee_amount:,.2f} บาท")
        self.total_paid_label.setText(f"{total_paid:,.2f} บาท")
        self.total_redemption_label.setText(f"{total_redemption:,.2f} บาท")

    def new_contract(self):
        """สร้างสัญญาใหม่"""
        dialog = NewContractDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "สำเร็จ", "สร้างสัญญาใหม่เรียบร้อย")
            # รีเฟรชข้อมูลในหน้าหลัก
            self.load_contract_data()

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
            customer_name = f"{self.current_customer.get('first_name', '')} {self.current_customer.get('last_name', '')}"
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

    def load_product_data(self):
        """โหลดข้อมูลสินค้า"""
        if self.current_product:
            self.product_name_edit.setText(self.current_product.get('name', ''))
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
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

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
            customer_name = f"{self.current_contract.get('first_name', '')} {self.current_contract.get('last_name', '')}"
            self.customer_name_edit.setText(customer_name)
            # โหลดข้อมูลสินค้า
            self.product_name_edit.setText(self.current_contract.get('product_name', ''))

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
        self.product_brand_edit.clear()
        self.product_size_edit.clear()
        self.serial_number_edit.clear()
        self.product_details_edit.clear()
        
        # รีเซ็ตยอด
        self.pawn_amount_spin.setValue(0)
        self.calculate_amounts()

    def show_daily_report(self):
        """แสดงรายงานประจำวัน"""
        today = datetime.now().strftime("%Y-%m-%d")
        summary = self.db.get_daily_summary(today)
        
        message = f"""
รายงานประจำวัน: {today}
สัญญาใหม่: {summary['new_contracts_count']} สัญญา ({summary['new_contracts_amount']:,.2f} บาท)
การไถ่ถอน: {summary['redemptions_count']} สัญญา ({summary['redemptions_amount']:,.2f} บาท)
การชำระดอกเบี้ย: {summary['interest_payments_count']} ครั้ง ({summary['interest_payments_amount']:,.2f} บาท)
        """
        
        QMessageBox.information(self, "รายงานประจำวัน", message)

    def show_monthly_report(self):
        """แสดงรายงานประจำเดือน"""
        QMessageBox.information(self, "รายงานประจำเดือน", "ฟีเจอร์รายงานประจำเดือน")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PawnShopUI()
    window.show()
    sys.exit(app.exec())