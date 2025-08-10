# -*- coding: utf-8 -*-
"""
หน้าต่างดูข้อมูลทั้งหมด
"""

# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QGroupBox, QTabWidget, QWidget, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter
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
        
        # Tab 4: รายงานสรุป
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
        self.customer_table.setColumnCount(8)  # เพิ่มคอลัมน์สำหรับปุ่มลบ
        self.customer_table.setHorizontalHeaderLabels([
            "รหัสลูกค้า", "ชื่อ", "นามสกุล", "เลขบัตรประชาชน", 
            "เบอร์โทรศัพท์", "ที่อยู่", "รายละเอียด", "การดำเนินการ"
        ])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.customer_table.setColumnWidth(7, 100)
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
        self.product_table.setColumnCount(8)  # เพิ่มคอลัมน์สำหรับปุ่มลบ
        self.product_table.setHorizontalHeaderLabels([
            "ชื่อสินค้า", "ยี่ห้อ/รุ่น", "ขนาด", "น้ำหนัก", 
            "หมายเลขซีเรียล", "รายละเอียด", "วันที่สร้าง", "การดำเนินการ"
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
        self.status_combo.addItems(["ทั้งหมด", "active", "redeemed"])
        self.status_combo.currentTextChanged.connect(self.filter_contracts)
        filter_layout.addWidget(self.status_combo)
        
        layout.addLayout(filter_layout)
        
        # ตารางสัญญา
        self.contract_table = QTableWidget()
        self.contract_table.setColumnCount(11)  # เพิ่มคอลัมน์สำหรับปุ่มลบ
        self.contract_table.setHorizontalHeaderLabels([
            "เลขที่สัญญา", "ชื่อลูกค้า", "ชื่อสินค้า", "ยอดฝาก", 
            "อัตราดอกเบี้ย", "วันที่เริ่มต้น", "วันที่สิ้นสุด", 
            "สถานะ", "ยอดไถ่ถอน", "วันที่สร้าง", "การดำเนินการ"
        ])
        self.contract_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contract_table.horizontalHeader().setSectionResizeMode(10, QHeaderView.Fixed)
        self.contract_table.setColumnWidth(10, 100)
        layout.addWidget(self.contract_table)
        
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
        
        # สัญญาที่ไถ่ถอน
        summary_layout.addWidget(QLabel("สัญญาที่ไถ่ถอน:"), 4, 0)
        self.redeemed_contract_label = QLabel("0")
        summary_layout.addWidget(self.redeemed_contract_label, 4, 1)
        
        # ยอดฝากรวม
        summary_layout.addWidget(QLabel("ยอดฝากรวม:"), 5, 0)
        self.total_pawn_label = QLabel("0.00 บาท")
        summary_layout.addWidget(self.total_pawn_label, 5, 1)
        
        # ยอดไถ่ถอนรวม
        summary_layout.addWidget(QLabel("ยอดไถ่ถอนรวม:"), 6, 0)
        self.total_redemption_label = QLabel("0.00 บาท")
        summary_layout.addWidget(self.total_redemption_label, 6, 1)
        
        layout.addWidget(summary_group)
        
        # รายงานประจำวัน
        daily_group = QGroupBox("รายงานประจำวัน")
        daily_layout = QGridLayout(daily_group)
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_summary = self.db.get_daily_summary(today)
        
        daily_layout.addWidget(QLabel("วันที่:"), 0, 0)
        daily_layout.addWidget(QLabel(today), 0, 1)
        
        daily_layout.addWidget(QLabel("สัญญาใหม่:"), 1, 0)
        daily_layout.addWidget(QLabel(f"{daily_summary['new_contracts_count']} สัญญา"), 1, 1)
        
        daily_layout.addWidget(QLabel("การไถ่ถอน:"), 2, 0)
        daily_layout.addWidget(QLabel(f"{daily_summary['redemptions_count']} สัญญา"), 2, 1)
        
        daily_layout.addWidget(QLabel("การชำระดอกเบี้ย:"), 3, 0)
        daily_layout.addWidget(QLabel(f"{daily_summary['interest_payments_count']} ครั้ง"), 3, 1)
        
        layout.addWidget(daily_group)
        
        # สัญญาที่ใกล้ครบกำหนด
        expiring_group = QGroupBox("สัญญาที่ใกล้ครบกำหนด (7 วัน)")
        expiring_layout = QVBoxLayout(expiring_group)
        
        self.expiring_table = QTableWidget()
        self.expiring_table.setColumnCount(5)
        self.expiring_table.setHorizontalHeaderLabels([
            "เลขที่สัญญา", "ชื่อลูกค้า", "เบอร์โทรศัพท์", "วันที่ครบกำหนด", "ยอดไถ่ถอน"
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
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_customer(row))
                self.customer_table.setCellWidget(row, 7, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดข้อมูลลูกค้า: {str(e)}")
    
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
                    self.product_table.setItem(row, 2, QTableWidgetItem(product.get('size', '')))
                    self.product_table.setItem(row, 3, QTableWidgetItem(f"{product.get('weight', 0)} กรัม"))
                    self.product_table.setItem(row, 4, QTableWidgetItem(product.get('serial_number', '')))
                    self.product_table.setItem(row, 5, QTableWidgetItem(product.get('other_details', '')))
                    
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
                    self.product_table.setItem(row, 6, QTableWidgetItem(date_str))
                    
                    # เพิ่มปุ่มลบ
                    delete_button = QPushButton("ลบ")
                    delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                    delete_button.clicked.connect(lambda checked, row=row: self.delete_product(row))
                    self.product_table.setCellWidget(row, 7, delete_button)
                    
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดข้อมูลสินค้า: {str(e)}")
    
    def load_contracts(self):
        """โหลดข้อมูลสัญญา"""
        try:
            contracts = self.db.search_contracts("", "all")
            self.contract_table.setRowCount(len(contracts))
            
            for row, contract in enumerate(contracts):
                self.contract_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = f"{contract.get('first_name', '')} {contract.get('last_name', '')}"
                self.contract_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.contract_table.setItem(row, 2, QTableWidgetItem(contract.get('product_name', '')))
                self.contract_table.setItem(row, 3, QTableWidgetItem(f"{contract.get('pawn_amount', 0):,.2f}"))
                self.contract_table.setItem(row, 4, QTableWidgetItem(f"{contract.get('interest_rate', 0):.2f}%"))
                
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
                self.contract_table.setItem(row, 5, QTableWidgetItem(date_str))
                
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
                self.contract_table.setItem(row, 6, QTableWidgetItem(date_str))
                
                # สถานะ
                status = contract.get('status', '')
                status_text = "เปิด" if status == 'active' else "ไถ่ถอน" if status == 'redeemed' else status
                self.contract_table.setItem(row, 7, QTableWidgetItem(status_text))
                
                self.contract_table.setItem(row, 8, QTableWidgetItem(f"{contract.get('total_redemption', 0):,.2f}"))
                
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
                self.contract_table.setItem(row, 9, QTableWidgetItem(date_str))
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_contract(row))
                self.contract_table.setCellWidget(row, 10, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดข้อมูลสัญญา: {str(e)}")
    
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
            
            # นับสัญญาที่ไถ่ถอน
            redeemed_contracts = self.db.search_contracts("", "redeemed")
            self.redeemed_contract_label.setText(str(len(redeemed_contracts)))
            
            # คำนวณยอดฝากรวม
            cursor.execute('SELECT SUM(pawn_amount) FROM contracts')
            total_pawn = cursor.fetchone()[0] or 0
            self.total_pawn_label.setText(f"{total_pawn:,.2f} บาท")
            
            # คำนวณยอดไถ่ถอนรวม
            cursor.execute('SELECT SUM(total_redemption) FROM contracts')
            total_redemption = cursor.fetchone()[0] or 0
            self.total_redemption_label.setText(f"{total_redemption:,.2f} บาท")
            
            conn.close()
            
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดข้อมูลสรุป: {str(e)}")
    
    def load_expiring_contracts(self):
        """โหลดสัญญาที่ใกล้ครบกำหนด"""
        try:
            expiring_contracts = self.db.get_expiring_contracts(7)
            self.expiring_table.setRowCount(len(expiring_contracts))
            
            for row, contract in enumerate(expiring_contracts):
                self.expiring_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = f"{contract.get('first_name', '')} {contract.get('last_name', '')}"
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
                
                self.expiring_table.setItem(row, 4, QTableWidgetItem(f"{contract.get('total_redemption', 0):,.2f}"))
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดสัญญาที่ใกล้ครบกำหนด: {str(e)}")
    
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
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_customer(row))
                self.customer_table.setCellWidget(row, 7, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถกรองข้อมูลลูกค้า: {str(e)}")
    
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
                    self.product_table.setItem(row, 2, QTableWidgetItem(product.get('size', '')))
                    self.product_table.setItem(row, 3, QTableWidgetItem(f"{product.get('weight', 0)} กรัม"))
                    self.product_table.setItem(row, 4, QTableWidgetItem(product.get('serial_number', '')))
                    self.product_table.setItem(row, 5, QTableWidgetItem(product.get('other_details', '')))
                    
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
                    self.product_table.setItem(row, 6, QTableWidgetItem(date_str))
                    
                    # เพิ่มปุ่มลบ
                    delete_button = QPushButton("ลบ")
                    delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                    delete_button.clicked.connect(lambda checked, row=row: self.delete_product(row))
                    self.product_table.setCellWidget(row, 7, delete_button)
                    
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถกรองข้อมูลสินค้า: {str(e)}")
    
    def filter_contracts(self):
        """กรองข้อมูลสัญญา"""
        search_term = self.contract_search_edit.text().strip()
        status = self.status_combo.currentText()
        
        if status == "ทั้งหมด":
            status = "all"
        elif status == "active":
            status = "active"
        elif status == "redeemed":
            status = "redeemed"
        
        try:
            contracts = self.db.search_contracts(search_term, status)
            self.contract_table.setRowCount(len(contracts))
            
            for row, contract in enumerate(contracts):
                self.contract_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
                
                customer_name = f"{contract.get('first_name', '')} {contract.get('last_name', '')}"
                self.contract_table.setItem(row, 1, QTableWidgetItem(customer_name))
                
                self.contract_table.setItem(row, 2, QTableWidgetItem(contract.get('product_name', '')))
                self.contract_table.setItem(row, 3, QTableWidgetItem(f"{contract.get('pawn_amount', 0):,.2f}"))
                self.contract_table.setItem(row, 4, QTableWidgetItem(f"{contract.get('interest_rate', 0):.2f}%"))
                
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
                self.contract_table.setItem(row, 5, QTableWidgetItem(date_str))
                
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
                self.contract_table.setItem(row, 6, QTableWidgetItem(date_str))
                
                # สถานะ
                status = contract.get('status', '')
                status_text = "เปิด" if status == 'active' else "ไถ่ถอน" if status == 'redeemed' else status
                self.contract_table.setItem(row, 7, QTableWidgetItem(status_text))
                
                self.contract_table.setItem(row, 8, QTableWidgetItem(f"{contract.get('total_redemption', 0):,.2f}"))
                
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
                self.contract_table.setItem(row, 9, QTableWidgetItem(date_str))
                
                # เพิ่มปุ่มลบ
                delete_button = QPushButton("ลบ")
                delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
                delete_button.clicked.connect(lambda checked, row=row: self.delete_contract(row))
                self.contract_table.setCellWidget(row, 10, delete_button)
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถกรองข้อมูลสัญญา: {str(e)}")
    
    def delete_customer(self, row: int):
        """ลบข้อมูลลูกค้า"""
        try:
            customer_code = self.customer_table.item(row, 0).text()
            customer_name = f"{self.customer_table.item(row, 1).text()} {self.customer_table.item(row, 2).text()}"
            
            # ยืนยันการลบ
            reply = QMessageBox.question(
                self, 
                "ยืนยันการลบ", 
                f"คุณต้องการลบข้อมูลลูกค้า {customer_name} (รหัส: {customer_code}) หรือไม่?\n\nการลบนี้จะลบข้อมูลลูกค้าออกจากระบบอย่างถาวร",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # ดึง ID ของลูกค้า
                customer_id = self.db.get_customer_id_by_code(customer_code)
                if customer_id:
                    # ลบข้อมูลลูกค้า
                    if self.db.delete_customer(customer_id):
                        QMessageBox.information(self, "สำเร็จ", f"ลบข้อมูลลูกค้า {customer_name} เรียบร้อยแล้ว")
                        self.load_data()  # รีเฟรชข้อมูล
                    else:
                        QMessageBox.warning(self, "ไม่สามารถลบได้", 
                                          "ไม่สามารถลบข้อมูลลูกค้าได้ เนื่องจากมีสัญญาที่เกี่ยวข้องอยู่")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลลูกค้าที่ต้องการลบ")
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการลบข้อมูล: {str(e)}")
    
    def delete_product(self, row: int):
        """ลบข้อมูลสินค้า"""
        try:
            product_name = self.product_table.item(row, 0).text()
            serial_number = self.product_table.item(row, 4).text()
            
            # ยืนยันการลบ
            reply = QMessageBox.question(
                self, 
                "ยืนยันการลบ", 
                f"คุณต้องการลบข้อมูลสินค้า {product_name} (ซีเรียล: {serial_number}) หรือไม่?\n\nการลบนี้จะลบข้อมูลสินค้าออกจากระบบอย่างถาวร",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # ดึง ID ของสินค้า
                product_id = self.db.get_product_id_by_serial(serial_number)
                if product_id:
                    # ลบข้อมูลสินค้า
                    if self.db.delete_product(product_id):
                        QMessageBox.information(self, "สำเร็จ", f"ลบข้อมูลสินค้า {product_name} เรียบร้อยแล้ว")
                        self.load_data()  # รีเฟรชข้อมูล
                    else:
                        QMessageBox.warning(self, "ไม่สามารถลบได้", 
                                          "ไม่สามารถลบข้อมูลสินค้าได้ เนื่องจากมีสัญญาที่เกี่ยวข้องอยู่")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลสินค้าที่ต้องการลบ")
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการลบข้อมูล: {str(e)}")
    
    def delete_contract(self, row: int):
        """ลบข้อมูลสัญญา"""
        try:
            contract_number = self.contract_table.item(row, 0).text()
            customer_name = self.contract_table.item(row, 1).text()
            
            # ยืนยันการลบ
            reply = QMessageBox.question(
                self, 
                "ยืนยันการลบ", 
                f"คุณต้องการลบข้อมูลสัญญา {contract_number} ของ {customer_name} หรือไม่?\n\nการลบนี้จะลบข้อมูลสัญญาออกจากระบบอย่างถาวร",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # ดึง ID ของสัญญา
                contract_id = self.db.get_contract_by_number(contract_number).get('id')
                if contract_id:
                    # ลบข้อมูลสัญญา
                    if self.db.delete_contract(contract_id):
                        QMessageBox.information(self, "สำเร็จ", f"ลบข้อมูลสัญญา {contract_number} เรียบร้อยแล้ว")
                        self.load_data()  # รีเฟรชข้อมูล
                    else:
                        QMessageBox.warning(self, "ไม่สามารถลบได้", "ไม่สามารถลบข้อมูลสัญญาได้")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลสัญญาที่ต้องการลบ")
                    
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการลบข้อมูล: {str(e)}")
