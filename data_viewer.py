# -*- coding: utf-8 -*-
"""
หน้าต่างดูข้อมูลทั้งหมด
"""

# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QGroupBox, QTabWidget, QWidget, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QInputDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from database import PawnShopDatabase
from utils import PawnShopUtils

class DataViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.setup_ui()
        self.load_data()
    
    def verify_delete_password(self):
        """ขอรหัสผ่านก่อนอนุญาตให้ลบข้อมูล"""
        password, ok = QInputDialog.getText(
            self,
            "ยืนยันรหัสผ่าน",
            "กรอกรหัสผ่านเพื่อลบ:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return False
        if password != "ipro1101":
            QMessageBox.warning(self, "รหัสผ่านไม่ถูกต้อง", "รหัสผ่านไม่ถูกต้อง")
            return False
        return True
    
    def verify_edit_password(self):
        """ขอรหัสผ่านก่อนอนุญาตให้แก้ไขข้อมูล"""
        password, ok = QInputDialog.getText(
            self,
            "ยืนยันรหัสผ่าน",
            "กรอกรหัสผ่านเพื่อแก้ไขข้อมูล:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return False
        if password != "ipro1101":
            QMessageBox.warning(self, "รหัสผ่านไม่ถูกต้อง", "รหัสผ่านไม่ถูกต้อง")
            return False
        return True

    def setup_ui(self):
        self.setWindowTitle("ดูข้อมูลทั้งหมด")
        self.setModal(True)
        self.resize(1200, 800)
        
        layout = QVBoxLayout(self)
        
        # สร้าง Tab Widget
        tab_widget = QTabWidget()
        
        # Tab 1: ข้อมูลลูกค้า
        customer_tab = self.create_customer_tab()
        tab_widget.addTab(customer_tab, "ข้อมูลลูกค้า")
        
        # Tab 2: ข้อมูลสินค้า
        product_tab = self.create_product_tab()
        tab_widget.addTab(product_tab, "ข้อมูลสินค้า")
        
        # Tab 3: ข้อมูลสัญญา
        contract_tab = self.create_contract_tab()
        tab_widget.addTab(contract_tab, "ข้อมูลสัญญา")
        
        # Tab 4: รายการครบกําหนด
        forfeited_tab = self.create_forfeited_tab()
        tab_widget.addTab(forfeited_tab, "รายการครบกําหนด")
        
        # Tab 5: รายงานสรุป
        summary_tab = self.create_summary_tab()
        tab_widget.addTab(summary_tab, "รายงานสรุป")
        
        layout.addWidget(tab_widget)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("รีเฟรชข้อมูล")
        self.refresh_button.clicked.connect(self.load_data)
        self.close_button = QPushButton("ปิด")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
    
    def create_customer_tab(self):
        """สร้าง Tab ข้อมูลลูกค้า"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ตัวกรอง
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("ค้นหา:"))
        self.customer_search_edit = QLineEdit()
        self.customer_search_edit.setPlaceholderText("ชื่อ, เลขบัตร, รหัสลูกค้า")
        self.customer_search_edit.textChanged.connect(self.filter_customers)
        filter_layout.addWidget(self.customer_search_edit)
        layout.addLayout(filter_layout)
        
        # ตารางลูกค้า
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(9)  # เพิ่มคอลัมน์สำหรับปุ่มแก้ไขและลบ
        self.customer_table.setHorizontalHeaderLabels([
            "รหัสลูกค้า", "ชื่อ", "นามสกุล", "เลขบัตรประชาชน", 
            "เบอร์โทรศัพท์", "ที่อยู่", "รายละเอียด", "แก้ไข", "ลบ"
        ])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.customer_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.customer_table.setColumnWidth(7, 80)
        self.customer_table.setColumnWidth(8, 80)
        layout.addWidget(self.customer_table)
        
        return widget
    
    def create_product_tab(self):
        """สร้าง Tab ข้อมูลสินค้า"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ตัวกรอง
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("ค้นหา:"))
        self.product_search_edit = QLineEdit()
        self.product_search_edit.setPlaceholderText("ชื่อสินค้า, ยี่ห้อ, ซีเรียล")
        self.product_search_edit.textChanged.connect(self.filter_products)
        filter_layout.addWidget(self.product_search_edit)
        layout.addLayout(filter_layout)
        
        # ตารางสินค้า
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(9)  # เพิ่มคอลัมน์สำหรับปุ่มลบ
        self.product_table.setHorizontalHeaderLabels([
            "ชื่อสินค้า", "ยี่ห้อ", "IMEI 1", "IMEI 2", "Serial Number", 
            "สภาพเครื่อง", "อุปกรณ์ที่มาพร้อม", "วันที่สร้าง", "การดำเนินการ"
        ])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.product_table.setColumnWidth(7, 100)
        layout.addWidget(self.product_table)
        
        return widget
    
    def create_contract_tab(self):
        """สร้าง Tab ข้อมูลสัญญา"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ตัวกรอง
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("ค้นหา:"))
        self.contract_search_edit = QLineEdit()
        self.contract_search_edit.setPlaceholderText("เลขที่สัญญา, ชื่อลูกค้า")
        self.contract_search_edit.textChanged.connect(self.filter_contracts)
        
        filter_layout.addWidget(QLabel("สถานะ:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ทั้งหมด", "สัญญาเปิด", "สัญญาปิด"])
        self.status_combo.currentTextChanged.connect(self.filter_contracts)
        filter_layout.addWidget(self.status_combo)
        
        layout.addLayout(filter_layout)
        
        # ตารางสัญญา
        self.contract_table = QTableWidget()
        self.contract_table.setColumnCount(10)  # เพิ่มคอลัมน์สำหรับปุ่มลบ
        self.contract_table.setHorizontalHeaderLabels([
            "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", "ยอดฝาก", 
            "วันที่เริ่มต้น", "วันที่สิ้นสุด", 
            "สถานะ", "ยอดไถ่คืน", "วันที่สร้าง", "การดำเนินการ"
        ])
        self.contract_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contract_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.contract_table.setColumnWidth(9, 100)
        layout.addWidget(self.contract_table)
        
        return widget
    
    def create_forfeited_tab(self):
        """สร้าง Tab รายการครบกำหนด"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ตัวกรอง
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("ค้นหา:"))
        self.forfeited_search_edit = QLineEdit()
        self.forfeited_search_edit.setPlaceholderText("เลขที่สัญญา, ชื่อลูกค้า, ชื่อสินค้า")
        self.forfeited_search_edit.textChanged.connect(self.filter_forfeited_contracts)
        filter_layout.addWidget(self.forfeited_search_edit)
        
        # ตัวกรองวันที่
        filter_layout.addWidget(QLabel("วันที่ครบกำหนด:"))
        self.forfeited_date_from = QDateEdit()
        self.forfeited_date_from.setDate(QDate.currentDate().addDays(-30))
        self.forfeited_date_from.setCalendarPopup(True)
        self.forfeited_date_from.dateChanged.connect(self.filter_forfeited_contracts)
        filter_layout.addWidget(self.forfeited_date_from)
        
        filter_layout.addWidget(QLabel("ถึง"))
        self.forfeited_date_to = QDateEdit()
        self.forfeited_date_to.setDate(QDate.currentDate())
        self.forfeited_date_to.setCalendarPopup(True)
        self.forfeited_date_to.dateChanged.connect(self.filter_forfeited_contracts)
        filter_layout.addWidget(self.forfeited_date_to)
        
        layout.addLayout(filter_layout)
        
        # ตารางรายการครบกำหนด
        self.forfeited_table = QTableWidget()
        self.forfeited_table.setColumnCount(8)
        self.forfeited_table.setHorizontalHeaderLabels([
            "เลขที่สัญญา", "ชื่อลูกค้า", "เบอร์โทรศัพท์", "ชื่อสินค้า", "ยี่ห้อ", 
            "ยอดฝาก", "วันที่ครบกำหนด", "การดำเนินการ"
        ])
        self.forfeited_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.forfeited_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.forfeited_table.setColumnWidth(7, 180)
        layout.addWidget(self.forfeited_table)
        
        return widget
    
    def create_summary_tab(self):
        """สร้าง Tab รายงานสรุป"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # สรุปข้อมูล
        summary_group = QGroupBox("สรุปข้อมูล")
        summary_layout = QGridLayout(summary_group)
        
        # จำนวนลูกค้า
        summary_layout.addWidget(QLabel("จำนวนลูกค้า:"), 0, 0)
        self.customer_count_label = QLabel("0")
        summary_layout.addWidget(self.customer_count_label, 0, 1)
        
        # จำนวนสินค้า
        summary_layout.addWidget(QLabel("จำนวนสินค้า:"), 1, 0)
        self.product_count_label = QLabel("0")
        summary_layout.addWidget(self.product_count_label, 1, 1)
        
        # จำนวนสัญญา
        summary_layout.addWidget(QLabel("จำนวนสัญญา:"), 2, 0)
        self.contract_count_label = QLabel("0")
        summary_layout.addWidget(self.contract_count_label, 2, 1)
        
        # สัญญาที่เปิด
        summary_layout.addWidget(QLabel("สัญญาที่เปิด:"), 3, 0)
        self.active_contract_label = QLabel("0")
        summary_layout.addWidget(self.active_contract_label, 3, 1)
        
        # สัญญาที่ไถ่คืน
        summary_layout.addWidget(QLabel("สัญญาที่ไถ่คืน:"), 4, 0)
        self.redeemed_contract_label = QLabel("0")
        summary_layout.addWidget(self.redeemed_contract_label, 4, 1)
        
        # ยอดฝากรวม
        summary_layout.addWidget(QLabel("ยอดฝากรวม:"), 5, 0)
        self.total_pawn_label = QLabel("0.00 บาท")
        summary_layout.addWidget(self.total_pawn_label, 5, 1)
        
        # ยอดไถ่คืนรวม
        summary_layout.addWidget(QLabel("ยอดไถ่คืนรวม:"), 6, 0)
        self.total_redemption_label = QLabel("0.00 บาท")
        summary_layout.addWidget(self.total_redemption_label, 6, 1)
        
        # ดอกเบี้ยรวม
        summary_layout.addWidget(QLabel("ดอกเบี้ยรวม:"), 7, 0)
        self.total_interest_label = QLabel("0.00 บาท")
        summary_layout.addWidget(self.total_interest_label, 7, 1)
        
        # กำไรสุทธิ
        summary_layout.addWidget(QLabel("กำไรสุทธิ:"), 8, 0)
        self.total_profit_label = QLabel("0.00 บาท")
        self.total_profit_label.setStyleSheet("font-weight: bold; color: #28a745; font-size: 14px;")
        summary_layout.addWidget(self.total_profit_label, 8, 1)
        
        layout.addWidget(summary_group)
        
        # รายงานประจำวัน
        daily_group = QGroupBox("รายงานประจำวัน")
        daily_layout = QGridLayout(daily_group)
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_summary = self.db.get_daily_summary(today)
        
        daily_layout.addWidget(QLabel("วันที่:"), 0, 0)
        daily_layout.addWidget(QLabel(today), 0, 1)
        
        daily_layout.addWidget(QLabel("สัญญาใหม่:"), 1, 0)
        daily_layout.addWidget(QLabel("{} สัญญา".format(daily_summary['new_contracts_count'])), 1, 1)
        
        daily_layout.addWidget(QLabel("การไถ่คืน:"), 2, 0)
        daily_layout.addWidget(QLabel("{} สัญญา".format(daily_summary['redemptions_count'])), 2, 1)
        
        daily_layout.addWidget(QLabel("การชำระดอกเบี้ย:"), 3, 0)
        daily_layout.addWidget(QLabel("{} ครั้ง".format(daily_summary['interest_payments_count'])), 3, 1)
        
        layout.addWidget(daily_group)
        
        # สัญญาที่ใกล้ครบกำหนด
        expiring_group = QGroupBox("สัญญาที่ใกล้ครบกำหนด (7 วัน)")
        expiring_layout = QVBoxLayout(expiring_group)
        
        self.expiring_table = QTableWidget()
        self.expiring_table.setColumnCount(5)
        self.expiring_table.setHorizontalHeaderLabels([
            "เลขที่สัญญา", "ชื่อลูกค้า", "เบอร์โทรศัพท์", "วันที่ครบกำหนด", "ยอดไถ่คืน"
        ])
        self.expiring_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        expiring_layout.addWidget(self.expiring_table)
        
        layout.addWidget(expiring_group)
        
        return widget
    
    def load_data(self):
        """โหลดข้อมูลทั้งหมด"""
        self.load_customers()
        self.load_products()
        self.load_contracts()
        self.load_forfeited_contracts()
        self.load_summary()
        self.load_expiring_contracts()
    
    def load_customers(self):
        """โหลดข้อมูลลูกค้า"""
        try:
            customers = self.db.search_customers("")  # ดึงทั้งหมด
            self.customer_table.setRowCount(len(customers))
            
            for row, customer in enumerate(customers):
                self.customer_table.setItem(row, 0, QTableWidgetItem(customer.get('customer_code', '')))
                self.customer_table.setItem(row, 1, QTableWidgetItem(customer.get('first_name', '')))
                self.customer_table.setItem(row, 2, QTableWidgetItem(customer.get('last_name', '')))
                self.customer_table.setItem(row, 3, QTableWidgetItem(customer.get('id_card', '')))
                self.customer_table.setItem(row, 4, QTableWidgetItem(customer.get('phone', '')))
                
                # ที่อยู่
                address_parts = [
                    customer.get('house_number', ''),
                    customer.get('street', ''),
                    customer.get('subdistrict', ''),
                    customer.get('district', ''),
                    customer.get('province', '')
                ]
                address = ' '.join(filter(None, address_parts))
                self.customer_table.setItem(row, 5, QTableWidgetItem(address))
                
                self.customer_table.setItem(row, 6, QTableWidgetItem(customer.get('other_details', '')))
                
                # เพิ่มปุ่มแก้ไข
                edit_button = QPushButton("แก้ไข")
                edit_button.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: none; padding: 5px; }")
                edit_button.clicked.connect(lambda checked, row=row: self.edit_customer(row))
                self.customer_table.setCellWidget(row, 7, edit_button)
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_customer(row))
                self.customer_table.setCellWidget(row, 8, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถโหลดข้อมูลลูกค้า: {}".format(str(e)))
    
    def load_products(self):
        """โหลดข้อมูลสินค้า"""
        try:
            # ดึงข้อมูลสินค้าทั้งหมด
            conn = self.db.db_path
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
            products = cursor.fetchall()
            conn.close()
            
            if products:
                columns = [description[0] for description in cursor.description]
                self.product_table.setRowCount(len(products))
                
                for row, product_data in enumerate(products):
                    product = dict(zip(columns, product_data))
                    self.product_table.setItem(row, 0, QTableWidgetItem(product.get('name', '')))
                    self.product_table.setItem(row, 1, QTableWidgetItem(product.get('brand', '')))
                    self.product_table.setItem(row, 2, QTableWidgetItem(product.get('imei1', '')))
                    self.product_table.setItem(row, 3, QTableWidgetItem(product.get('imei2', '')))
                    self.product_table.setItem(row, 4, QTableWidgetItem(product.get('serial_number', '')))
                    self.product_table.setItem(row, 5, QTableWidgetItem(product.get('condition', '')))
                    
                    # วันที่สร้าง
                    created_at = product.get('created_at', '')
                    if created_at:
                        try:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = date_obj.strftime('%d/%m/%Y')
                        except:
                            date_str = created_at
                    else:
                        date_str = ''
                    self.product_table.setItem(row, 6, QTableWidgetItem(product.get('accessories', '')))
                    self.product_table.setItem(row, 7, QTableWidgetItem(date_str))
                    
                    # เพิ่มปุ่มลบ
                    delete_button = QPushButton("ลบ")
                    delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                    delete_button.clicked.connect(lambda checked, row=row: self.delete_product(row))
                    self.product_table.setCellWidget(row, 8, delete_button)
                    
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถโหลดข้อมูลสินค้า: {}".format(str(e)))
    
    def load_contracts(self):
        """โหลดข้อมูลสัญญา"""
        try:
            contracts = self.db.search_contracts("", "all")
            self.contract_table.setRowCount(len(contracts))
            
            for row, contract in enumerate(contracts):
                self.contract_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = "{} {}".format(contract.get('first_name', ''), contract.get('last_name', ''))
                self.contract_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.contract_table.setItem(row, 2, QTableWidgetItem(contract.get('product_name', '')))
                self.contract_table.setItem(row, 3, QTableWidgetItem("{:,.2f}".format(contract.get('pawn_amount', 0))))
                
                # วันที่เริ่มต้น
                start_date = contract.get('start_date', '')
                if start_date:
                    try:
                        date_obj = datetime.fromisoformat(start_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = start_date
                else:
                    date_str = ''
                self.contract_table.setItem(row, 4, QTableWidgetItem(date_str))
                
                # วันที่สิ้นสุด
                end_date = contract.get('end_date', '')
                if end_date:
                    try:
                        date_obj = datetime.fromisoformat(end_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = end_date
                else:
                    date_str = ''
                self.contract_table.setItem(row, 5, QTableWidgetItem(date_str))
                
                # สถานะ
                status = contract.get('status', '')
                status_text = "เปิด" if status == 'active' else "ไถ่คืน" if status == 'redeemed' else status
                self.contract_table.setItem(row, 6, QTableWidgetItem(status_text))
                
                self.contract_table.setItem(row, 7, QTableWidgetItem("{:,.2f}".format(contract.get('total_redemption', 0))))
                
                # วันที่สร้าง
                created_at = contract.get('created_at', '')
                if created_at:
                    try:
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = created_at
                else:
                    date_str = ''
                self.contract_table.setItem(row, 8, QTableWidgetItem(date_str))
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_contract(row))
                self.contract_table.setCellWidget(row, 9, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถโหลดข้อมูลสัญญา: {}".format(str(e)))
    
    def load_forfeited_contracts(self):
        """โหลดข้อมูลสินค้าที่ครบกำหนด"""
        try:
            forfeited_contracts = self.db.get_forfeited_contracts()
            self.forfeited_table.setRowCount(len(forfeited_contracts))
            
            for row, contract in enumerate(forfeited_contracts):
                self.forfeited_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = "{} {}".format(contract.get('first_name', ''), contract.get('last_name', ''))
                self.forfeited_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.forfeited_table.setItem(row, 2, QTableWidgetItem(contract.get('phone', '')))
                self.forfeited_table.setItem(row, 3, QTableWidgetItem(contract.get('product_name', '')))
                self.forfeited_table.setItem(row, 4, QTableWidgetItem(contract.get('product_brand', '')))
                self.forfeited_table.setItem(row, 5, QTableWidgetItem("{:,.2f}".format(contract.get('pawn_amount', 0))))
                
                # วันที่ครบกำหนด
                end_date = contract.get('end_date', '')
                if end_date:
                    try:
                        date_obj = datetime.fromisoformat(end_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = end_date
                else:
                    date_str = ''
                self.forfeited_table.setItem(row, 6, QTableWidgetItem(date_str))
                
                # เก็บ contract_id ไว้ใน item
                self.forfeited_table.item(row, 0).setData(Qt.UserRole, contract.get('id'))
                
                # สร้าง widget สำหรับปุ่ม
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.setContentsMargins(5, 2, 5, 2)
                button_layout.setSpacing(5)
                
                # ปุ่มหลุด
                forfeit_button = QPushButton("หลุด")
                forfeit_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; } QPushButton:hover { background-color: #c82333; }")
                forfeit_button.clicked.connect(lambda checked, row=row: self.forfeit_contract(row))
                button_layout.addWidget(forfeit_button)
                
                # ปุ่มซื้อคืน
                buy_back_button = QPushButton("ซื้อคืน")
                buy_back_button.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 4px; } QPushButton:hover { background-color: #218838; }")
                buy_back_button.clicked.connect(lambda checked, row=row: self.buy_back_contract(row))
                button_layout.addWidget(buy_back_button)
                
                button_layout.addStretch()
                self.forfeited_table.setCellWidget(row, 7, button_widget)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถโหลดข้อมูลรายการครบกำหนด: {}".format(str(e)))
    
    def filter_forfeited_contracts(self):
        """กรองข้อมูลรายการครบกำหนด"""
        search_term = self.forfeited_search_edit.text().strip()
        date_from = self.forfeited_date_from.date().toString('yyyy-MM-dd')
        date_to = self.forfeited_date_to.date().toString('yyyy-MM-dd')
        
        try:
            # ดึงข้อมูลรายการหลุดทั้งหมดก่อน
            forfeited_contracts = self.db.get_forfeited_contracts()
            filtered_contracts = []
            
            for contract in forfeited_contracts:
                # กรองตามคำค้นหา
                if search_term:
                    search_fields = [
                        contract.get('contract_number', ''),
                        contract.get('first_name', ''),
                        contract.get('last_name', ''),
                        contract.get('product_name', ''),
                        contract.get('product_brand', '')
                    ]
                    if not any(search_term.lower() in field.lower() for field in search_fields):
                        continue
                
                # กรองตามวันที่
                end_date = contract.get('end_date', '')
                if end_date:
                    try:
                        contract_date = datetime.fromisoformat(end_date).strftime('%Y-%m-%d')
                        if contract_date < date_from or contract_date > date_to:
                            continue
                    except:
                        continue
                
                filtered_contracts.append(contract)
            
            # แสดงผลในตาราง
            self.forfeited_table.setRowCount(len(filtered_contracts))
            
            for row, contract in enumerate(filtered_contracts):
                self.forfeited_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = "{} {}".format(contract.get('first_name', ''), contract.get('last_name', ''))
                self.forfeited_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.forfeited_table.setItem(row, 2, QTableWidgetItem(contract.get('phone', '')))
                self.forfeited_table.setItem(row, 3, QTableWidgetItem(contract.get('product_name', '')))
                self.forfeited_table.setItem(row, 4, QTableWidgetItem(contract.get('product_brand', '')))
                self.forfeited_table.setItem(row, 5, QTableWidgetItem("{:,.2f}".format(contract.get('pawn_amount', 0))))
                
                # วันที่ครบกำหนด
                end_date = contract.get('end_date', '')
                if end_date:
                    try:
                        date_obj = datetime.fromisoformat(end_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = end_date
                else:
                    date_str = ''
                self.forfeited_table.setItem(row, 6, QTableWidgetItem(date_str))
                
                # เก็บ contract_id ไว้ใน item
                self.forfeited_table.item(row, 0).setData(Qt.UserRole, contract.get('id'))
                
                # สร้าง widget สำหรับปุ่ม
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.setContentsMargins(5, 2, 5, 2)
                button_layout.setSpacing(5)
                
                # ปุ่มหลุด
                forfeit_button = QPushButton("หลุด")
                forfeit_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; } QPushButton:hover { background-color: #c82333; }")
                forfeit_button.clicked.connect(lambda checked, row=row: self.forfeit_contract(row))
                button_layout.addWidget(forfeit_button)
                
                # ปุ่มซื้อคืน
                buy_back_button = QPushButton("ซื้อคืน")
                buy_back_button.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 4px; } QPushButton:hover { background-color: #218838; }")
                buy_back_button.clicked.connect(lambda checked, row=row: self.buy_back_contract(row))
                button_layout.addWidget(buy_back_button)
                
                button_layout.addStretch()
                self.forfeited_table.setCellWidget(row, 7, button_widget)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถกรองข้อมูลรายการครบกำหนด: {}".format(str(e)))
    
    def forfeit_contract(self, row: int):
        """หลุดจำนำสินค้า"""
        try:
            # ดึง contract_id จาก table item
            contract_id = self.forfeited_table.item(row, 0).data(Qt.UserRole)
            if not contract_id:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
                return
            
            contract_number = self.forfeited_table.item(row, 0).text()
            customer_name = self.forfeited_table.item(row, 1).text()
            product_name = self.forfeited_table.item(row, 3).text()
            
            # ยืนยันการหลุดจำนำ
            reply = QMessageBox.question(
                self,
                "ยืนยันการหลุดจำนำ",
                f"คุณต้องการให้สินค้าหลุดจำนำหรือไม่?\n\nเลขที่สัญญา: {contract_number}\nชื่อลูกค้า: {customer_name}\nชื่อสินค้า: {product_name}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # อัปเดตสถานะสัญญาเป็น 'lost'
                if self.db.update_contract_status(contract_id, 'lost'):
                    QMessageBox.information(self, "สำเร็จ", f"สินค้าหลุดจำนำเรียบร้อยแล้ว\n\nเลขที่สัญญา: {contract_number}")
                    # รีเฟรชข้อมูล
                    self.load_forfeited_contracts()
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถอัปเดตสถานะสัญญาได้")
            
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถหลุดจำนำได้: {}".format(str(e)))
    
    def buy_back_contract(self, row: int):
        """ซื้อคืนสินค้า"""
        try:
            # ดึง contract_id จาก table item
            contract_id = self.forfeited_table.item(row, 0).data(Qt.UserRole)
            if not contract_id:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
                return
            
            # ดึงข้อมูลสัญญาจากฐานข้อมูล
            contract = self.db.get_contract_by_id(contract_id)
            if not contract:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
                return
            
            # ดึงข้อมูลลูกค้าและสินค้า
            customer = self.db.get_customer_by_id(contract.get('customer_id'))
            product = self.db.get_product_by_id(contract.get('product_id'))
            
            # สร้างข้อมูลสัญญาที่ครบถ้วน
            full_contract_data = {
                **contract,
                'customer_id': contract.get('customer_id'),
                'first_name': customer.get('first_name', '') if customer else '',
                'last_name': customer.get('last_name', '') if customer else '',
                'customer_code': customer.get('customer_code', '') if customer else '',
                'id_card': customer.get('id_card', '') if customer else '',
                'phone': customer.get('phone', '') if customer else '',
                'product_name': product.get('name', '') if product else '',
                'brand': product.get('brand', '') if product else '',
                'serial_number': product.get('serial_number', '') if product else ''
            }
            
            # เปิด dialog ซื้อคืน
            from dialogs import RedemptionDialog
            dialog = RedemptionDialog(self, full_contract_data)
            if dialog.exec() == QDialog.Accepted:
                QMessageBox.information(self, "สำเร็จ", "ซื้อคืนสินค้าเรียบร้อยแล้ว")
                # รีเฟรชข้อมูล
                self.load_forfeited_contracts()
            
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถซื้อคืนได้: {}".format(str(e)))
    
    def load_summary(self):
        """โหลดข้อมูลสรุป"""
        try:
            # นับจำนวนลูกค้า
            customers = self.db.search_customers("")
            self.customer_count_label.setText(str(len(customers)))
            
            # นับจำนวนสินค้า
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            product_count = cursor.fetchone()[0]
            self.product_count_label.setText(str(product_count))
            
            # นับจำนวนสัญญา
            contracts = self.db.search_contracts("", "all")
            self.contract_count_label.setText(str(len(contracts)))
            
            # นับสัญญาที่เปิด
            active_contracts = self.db.search_contracts("", "active")
            self.active_contract_label.setText(str(len(active_contracts)))
            
            # นับสัญญาที่ไถ่คืน
            redeemed_contracts = self.db.search_contracts("", "redeemed")
            self.redeemed_contract_label.setText(str(len(redeemed_contracts)))
            
            # คำนวณยอดฝากรวม
            cursor.execute('SELECT SUM(pawn_amount) FROM contracts')
            total_pawn = cursor.fetchone()[0] or 0
            self.total_pawn_label.setText("{:,.2f} บาท".format(total_pawn))
            
            # คำนวณยอดไถ่คืนรวม
            cursor.execute('SELECT SUM(total_redemption) FROM contracts')
            total_redemption = cursor.fetchone()[0] or 0
            self.total_redemption_label.setText("{:,.2f} บาท".format(total_redemption))
            
            # คำนวณดอกเบี้ยรวม (ดอกเบี้ย + การต่อดอก)
            cursor.execute('SELECT SUM(total_amount) FROM interest_payments')
            total_interest_payments = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT SUM(total_amount) FROM renewals')
            total_renewals = cursor.fetchone()[0] or 0
            
            total_interest = total_interest_payments + total_renewals
            self.total_interest_label.setText("{:,.2f} บาท".format(total_interest))
            
            # คำนวณกำไรสุทธิ (ดอกเบี้ยรวมเป็นกำไรหลัก)
            total_profit = total_interest
            self.total_profit_label.setText("{:,.2f} บาท".format(total_profit))
            
            conn.close()
            
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถโหลดข้อมูลสรุป: {}".format(str(e)))
    
    def load_expiring_contracts(self):
        """โหลดสัญญาที่ใกล้ครบกำหนด"""
        try:
            expiring_contracts = self.db.get_expiring_contracts(7)
            self.expiring_table.setRowCount(len(expiring_contracts))
            
            for row, contract in enumerate(expiring_contracts):
                self.expiring_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = "{} {}".format(contract.get('first_name', ''), contract.get('last_name', ''))
                self.expiring_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.expiring_table.setItem(row, 2, QTableWidgetItem(contract.get('phone', '')))
                
                # วันที่ครบกำหนด
                end_date = contract.get('end_date', '')
                if end_date:
                    try:
                        date_obj = datetime.fromisoformat(end_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = end_date
                else:
                    date_str = ''
                self.expiring_table.setItem(row, 3, QTableWidgetItem(date_str))
                
                self.expiring_table.setItem(row, 4, QTableWidgetItem("{:,.2f}".format(contract.get('total_redemption', 0))))
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถโหลดสัญญาที่ใกล้ครบกำหนด: {}".format(str(e)))
    
    def filter_customers(self):
        """กรองข้อมูลลูกค้า"""
        search_term = self.customer_search_edit.text().strip()
        try:
            customers = self.db.search_customers(search_term)
            self.customer_table.setRowCount(len(customers))
            
            for row, customer in enumerate(customers):
                self.customer_table.setItem(row, 0, QTableWidgetItem(customer.get('customer_code', '')))
                self.customer_table.setItem(row, 1, QTableWidgetItem(customer.get('first_name', '')))
                self.customer_table.setItem(row, 2, QTableWidgetItem(customer.get('last_name', '')))
                self.customer_table.setItem(row, 3, QTableWidgetItem(customer.get('id_card', '')))
                self.customer_table.setItem(row, 4, QTableWidgetItem(customer.get('phone', '')))
                
                # ที่อยู่
                address_parts = [
                    customer.get('house_number', ''),
                    customer.get('street', ''),
                    customer.get('subdistrict', ''),
                    customer.get('district', ''),
                    customer.get('province', '')
                ]
                address = ' '.join(filter(None, address_parts))
                self.customer_table.setItem(row, 5, QTableWidgetItem(address))
                
                self.customer_table.setItem(row, 6, QTableWidgetItem(customer.get('other_details', '')))
                
                # เพิ่มปุ่มแก้ไข
                edit_button = QPushButton("แก้ไข")
                edit_button.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: none; padding: 5px; }")
                edit_button.clicked.connect(lambda checked, row=row: self.edit_customer(row))
                self.customer_table.setCellWidget(row, 7, edit_button)
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_customer(row))
                self.customer_table.setCellWidget(row, 8, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถกรองข้อมูลลูกค้า: {}".format(str(e)))
    
    def filter_products(self):
        """กรองข้อมูลสินค้า"""
        search_term = self.product_search_edit.text().strip()
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            if search_term:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE name LIKE ? OR brand LIKE ? OR serial_number LIKE ?
                    ORDER BY created_at DESC
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
            
            products = cursor.fetchall()
            conn.close()
            
            if products:
                columns = [description[0] for description in cursor.description]
                self.product_table.setRowCount(len(products))
                
                for row, product_data in enumerate(products):
                    product = dict(zip(columns, product_data))
                    self.product_table.setItem(row, 0, QTableWidgetItem(product.get('name', '')))
                    self.product_table.setItem(row, 1, QTableWidgetItem(product.get('brand', '')))
                    self.product_table.setItem(row, 2, QTableWidgetItem(product.get('imei1', '')))
                    self.product_table.setItem(row, 3, QTableWidgetItem(product.get('imei2', '')))
                    self.product_table.setItem(row, 4, QTableWidgetItem(product.get('serial_number', '')))
                    self.product_table.setItem(row, 5, QTableWidgetItem(product.get('condition', '')))
                    
                    # วันที่สร้าง
                    created_at = product.get('created_at', '')
                    if created_at:
                        try:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = date_obj.strftime('%d/%m/%Y')
                        except:
                            date_str = created_at
                    else:
                        date_str = ''
                    self.product_table.setItem(row, 6, QTableWidgetItem(product.get('accessories', '')))
                    self.product_table.setItem(row, 7, QTableWidgetItem(date_str))
                    
                    # เพิ่มปุ่มลบ
                    delete_button = QPushButton("ลบ")
                    delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                    delete_button.clicked.connect(lambda checked, row=row: self.delete_product(row))
                    self.product_table.setCellWidget(row, 8, delete_button)
                    
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถกรองข้อมูลสินค้า: {}".format(str(e)))
    
    def filter_contracts(self):
        """กรองข้อมูลสัญญา"""
        search_term = self.contract_search_edit.text().strip()
        status_text_combo = self.status_combo.currentText()
        
        # แปลงสถานะจากภาษาไทยเป็นค่าที่ใช้ในฐานข้อมูล
        if status_text_combo == "ทั้งหมด":
            status = "all"
        elif status_text_combo == "สัญญาเปิด":
            status = "active"
        elif status_text_combo == "สัญญาปิด":
            status = "redeemed"
        else:
            status = "all"
        
        try:
            contracts = self.db.search_contracts(search_term, status)
            self.contract_table.setRowCount(len(contracts))
            
            for row, contract in enumerate(contracts):
                self.contract_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = "{} {}".format(contract.get('first_name', ''), contract.get('last_name', ''))
                self.contract_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.contract_table.setItem(row, 2, QTableWidgetItem(contract.get('product_name', '')))
                self.contract_table.setItem(row, 3, QTableWidgetItem("{:,.2f}".format(contract.get('pawn_amount', 0))))
                
                # วันที่เริ่มต้น
                start_date = contract.get('start_date', '')
                if start_date:
                    try:
                        date_obj = datetime.fromisoformat(start_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = start_date
                else:
                    date_str = ''
                self.contract_table.setItem(row, 4, QTableWidgetItem(date_str))
                
                # วันที่สิ้นสุด
                end_date = contract.get('end_date', '')
                if end_date:
                    try:
                        date_obj = datetime.fromisoformat(end_date)
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = end_date
                else:
                    date_str = ''
                self.contract_table.setItem(row, 5, QTableWidgetItem(date_str))
                
                # สถานะ
                contract_status = contract.get('status', '')
                status_display = "เปิด" if contract_status == 'active' else "ไถ่คืน" if contract_status == 'redeemed' else contract_status
                self.contract_table.setItem(row, 6, QTableWidgetItem(status_display))
                
                self.contract_table.setItem(row, 7, QTableWidgetItem("{:,.2f}".format(contract.get('total_redemption', 0))))
                
                # วันที่สร้าง
                created_at = contract.get('created_at', '')
                if created_at:
                    try:
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        date_str = created_at
                else:
                    date_str = ''
                self.contract_table.setItem(row, 8, QTableWidgetItem(date_str))
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_contract(row))
                self.contract_table.setCellWidget(row, 9, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถกรองข้อมูลสัญญา: {}".format(str(e)))
    
    def delete_customer(self, row: int):
        """ลบข้อมูลลูกค้า"""
        try:
            # ตรวจรหัสผ่านก่อน
            if not self.verify_delete_password():
                return

            customer_code = self.customer_table.item(row, 0).text()
            customer_name = "{} {}".format(self.customer_table.item(row, 1).text(), self.customer_table.item(row, 2).text())
            
            # ยืนยันการลบ
            reply = QMessageBox.question(
                self, 
                "ยืนยันการลบ", 
                "คุณต้องการลบข้อมูลลูกค้า {} (รหัส: {}) หรือไม่?\n\nการลบนี้จะลบข้อมูลลูกค้าออกจากระบบอย่างถาวร".format(customer_name, customer_code),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # ดึง ID ของลูกค้า
                customer_id = self.db.get_customer_id_by_code(customer_code)
                if customer_id:
                    # ลบข้อมูลลูกค้า
                    if self.db.delete_customer(customer_id):
                        QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลลูกค้า {customer_name} เรียบร้อยแล้ว")
                        self.load_data()  # รีเฟรชข้อมูล
                    else:
                        QMessageBox.warning(self, "ไม่สามารถลบได้", 
                                          "ไม่สามารถลบข้อมูลลูกค้าได้ เนื่องจากมีสัญญาที่เกี่ยวข้องอยู่")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลลูกค้าที่ต้องการลบ")
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", "เกิดข้อผิดพลาดในการลบข้อมูล: {}".format(str(e)))
    
    def delete_product(self, row: int):
        """ลบข้อมูลสินค้า"""
        try:
            # ตรวจรหัสผ่านก่อน
            if not self.verify_delete_password():
                return

            product_name = self.product_table.item(row, 0).text()
            serial_number = self.product_table.item(row, 4).text()
            
            # ยืนยันการลบ
            reply = QMessageBox.question(
                self, 
                "ยืนยันการลบ", 
                "คุณต้องการลบข้อมูลสินค้า {product_name} (ซีเรียล: {serial_number}) หรือไม่?\n\nการลบนี้จะลบข้อมูลสินค้าออกจากระบบอย่างถาวร",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # ดึง ID ของสินค้า
                product_id = self.db.get_product_id_by_serial(serial_number)
                if product_id:
                    # ลบข้อมูลสินค้า
                    if self.db.delete_product(product_id):
                        QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลสินค้า {product_name} เรียบร้อยแล้ว")
                        self.load_data()  # รีเฟรชข้อมูล
                    else:
                        QMessageBox.warning(self, "ไม่สามารถลบได้", 
                                          "ไม่สามารถลบข้อมูลสินค้าได้ เนื่องจากมีสัญญาที่เกี่ยวข้องอยู่")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลสินค้าที่ต้องการลบ")
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", "เกิดข้อผิดพลาดในการลบข้อมูล: {}".format(str(e)))
    
    def delete_contract(self, row: int):
        """ลบข้อมูลสัญญา"""
        try:
            # ตรวจรหัสผ่านก่อน
            if not self.verify_delete_password():
                return

            contract_number = self.contract_table.item(row, 0).text()
            customer_name = self.contract_table.item(row, 1).text()
            
            # ยืนยันการลบ
            reply = QMessageBox.question(
                self, 
                "ยืนยันการลบ", 
                "คุณต้องการลบข้อมูลสัญญา {contract_number} ของ {customer_name} หรือไม่?\n\nการลบนี้จะลบข้อมูลสัญญาออกจากระบบอย่างถาวร",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # ดึง ID ของสัญญา
                contract_id = self.db.get_contract_by_number(contract_number).get('id')
                if contract_id:
                    # ลบข้อมูลสัญญา
                    if self.db.delete_contract(contract_id):
                        QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลสัญญา {contract_number} เรียบร้อยแล้ว")
                        self.load_data()  # รีเฟรชข้อมูล
                    else:
                        QMessageBox.warning(self, "ไม่สามารถลบได้", "ไม่สามารถลบข้อมูลสัญญาได้")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลสัญญาที่ต้องการลบ")
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", "เกิดข้อผิดพลาดในการลบข้อมูล: {}".format(str(e)))
    
    def edit_customer(self, row: int):
        """แก้ไขข้อมูลลูกค้า"""
        try:
            # ตรวจรหัสผ่านก่อน
            if not self.verify_edit_password():
                return

            customer_code = self.customer_table.item(row, 0).text()
            customer_name = "{} {}".format(self.customer_table.item(row, 1).text(), self.customer_table.item(row, 2).text())
            
            # ดึงข้อมูลลูกค้าจากฐานข้อมูล
            customer_data = self.db.get_customer_by_code(customer_code)
            if not customer_data:
                QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลลูกค้าที่ต้องการแก้ไข")
                return
            
            # เปิดหน้าต่างแก้ไขข้อมูลลูกค้า
            from dialogs import CustomerDialog
            dialog = CustomerDialog(self, customer_data)
            if dialog.exec():
                # รีเฟรชข้อมูลหลังจากแก้ไข
                self.load_data()
                QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลลูกค้า {} เรียบร้อยแล้ว".format(customer_name))
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", "เกิดข้อผิดพลาดในการแก้ไขข้อมูล: {}".format(str(e)))
