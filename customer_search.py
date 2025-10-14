# -*- coding: utf-8 -*-
"""
หน้าต่างค้นหาลูกค้า
"""

# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from typing import Dict, Optional, List
from database import PawnShopDatabase

class CustomerSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.selected_customer = None
        self.setup_ui()
        self.load_customers()
    
    def setup_ui(self):
        self.setWindowTitle("ค้นหาลูกค้า")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # ตัวกรอง
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("ค้นหา:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ชื่อลูกค้า, นามสกุล, เลขบัตร, รหัสลูกค้า")
        self.search_edit.textChanged.connect(self.filter_customers)
        filter_layout.addWidget(self.search_edit)
        
        self.search_button = QPushButton("ค้นหา")
        self.search_button.clicked.connect(self.search_customers)
        filter_layout.addWidget(self.search_button)
        
        layout.addLayout(filter_layout)
        
        # ตารางลูกค้า
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(6)
        self.customer_table.setHorizontalHeaderLabels([
            "รหัสลูกค้า", "ชื่อ", "นามสกุล", "เลขบัตรประชาชน", 
            "เบอร์โทรศัพท์", "ที่อยู่"
        ])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.itemDoubleClicked.connect(self.select_customer)
        layout.addWidget(self.customer_table)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        self.add_new_button = QPushButton("เพิ่มลูกค้าใหม่")
        self.add_new_button.clicked.connect(self.add_new_customer)
        self.select_button = QPushButton("เลือกลูกค้า")
        self.select_button.clicked.connect(self.select_customer)
        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.add_new_button)
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def load_customers(self):
        """โหลดข้อมูลลูกค้าทั้งหมด"""
        try:
            customers = self.db.search_customers("")  # ดึงทั้งหมด
            self.display_customers(customers)
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดข้อมูลลูกค้า: {str(e)}")
    
    def search_customers(self):
        """ค้นหาลูกค้า"""
        search_term = self.search_edit.text().strip()
        if not search_term:
            self.load_customers()
            return
        
        try:
            customers = self.db.search_customers(search_term)
            self.display_customers(customers)
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถค้นหาลูกค้า: {str(e)}")
    
    def filter_customers(self):
        """กรองข้อมูลลูกค้า"""
        search_term = self.search_edit.text().strip()
        if search_term:
            self.search_customers()
    
    def display_customers(self, customers):
        """แสดงข้อมูลลูกค้าในตาราง"""
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
    
    def select_customer(self):
        """เลือกลูกค้า"""
        current_row = self.customer_table.currentRow()
        if current_row >= 0:
            # ดึงข้อมูลลูกค้าที่เลือกโดยใช้ชื่อและนามสกุล
            first_name = self.customer_table.item(current_row, 1).text()
            last_name = self.customer_table.item(current_row, 2).text()
            customer_name = f"{first_name} {last_name}".strip()
            
            # ค้นหาลูกค้าด้วยชื่อ
            customers = self.db.search_customers(customer_name)
            
            if customers:
                # หาลูกค้าที่ตรงกับชื่อและนามสกุลที่เลือก
                for customer in customers:
                    if (customer.get('first_name', '') == first_name and 
                        customer.get('last_name', '') == last_name):
                        self.selected_customer = customer
                        self.accept()
                        return
                
                # ถ้าไม่เจอที่ตรงกัน ให้ใช้ลูกค้าคนแรกที่เจอ
                self.selected_customer = customers[0]
                self.accept()
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลลูกค้า")
        else:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกลูกค้า")
    
    def add_new_customer(self):
        """เพิ่มลูกค้าใหม่"""
        from dialogs import CustomerDialog
        dialog = CustomerDialog(self)
        if dialog.exec():
            # โหลดข้อมูลลูกค้าใหม่
            self.load_customers()
            # เลือกลูกค้าที่เพิ่งเพิ่ม
            if dialog.customer_data:
                self.selected_customer = dialog.customer_data
                self.accept()
