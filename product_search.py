# -*- coding: utf-8 -*-
"""
หน้าต่างค้นหาสินค้า
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from datetime import datetime
from typing import Dict, Optional, List
from database import PawnShopDatabase

class ProductSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = PawnShopDatabase()
        self.selected_product = None
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        self.setWindowTitle("ค้นหาสินค้า")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # ตัวกรอง
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("ค้นหา:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ชื่อสินค้า, ยี่ห้อ, ซีเรียล")
        self.search_edit.textChanged.connect(self.filter_products)
        filter_layout.addWidget(self.search_edit)
        
        self.search_button = QPushButton("ค้นหา")
        self.search_button.clicked.connect(self.search_products)
        filter_layout.addWidget(self.search_button)
        
        layout.addLayout(filter_layout)
        
        # ตารางสินค้า
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels([
            "ชื่อสินค้า", "ยี่ห้อ/รุ่น", "ขนาด", "น้ำหนัก", 
            "หมายเลขซีเรียล", "รายละเอียด", "วันที่สร้าง"
        ])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.itemDoubleClicked.connect(self.select_product)
        layout.addWidget(self.product_table)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("เลือกสินค้า")
        self.select_button.clicked.connect(self.select_product)
        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def load_products(self):
        """โหลดข้อมูลสินค้าทั้งหมด"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
            products = cursor.fetchall()
            conn.close()
            
            if products:
                columns = [description[0] for description in cursor.description]
                self.display_products([dict(zip(columns, product_data)) for product_data in products])
            else:
                self.display_products([])
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถโหลดข้อมูลสินค้า: {str(e)}")
    
    def search_products(self):
        """ค้นหาสินค้า"""
        search_term = self.search_edit.text().strip()
        if not search_term:
            self.load_products()
            return
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM products 
                WHERE name LIKE ? OR brand LIKE ? OR serial_number LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            products = cursor.fetchall()
            conn.close()
            
            if products:
                columns = [description[0] for description in cursor.description]
                self.display_products([dict(zip(columns, product_data)) for product_data in products])
            else:
                self.display_products([])
                
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถค้นหาสินค้า: {str(e)}")
    
    def filter_products(self):
        """กรองข้อมูลสินค้า"""
        search_term = self.search_edit.text().strip()
        if search_term:
            self.search_products()
    
    def display_products(self, products):
        """แสดงข้อมูลสินค้าในตาราง"""
        self.product_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
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
    
    def select_product(self):
        """เลือกสินค้า"""
        current_row = self.product_table.currentRow()
        if current_row >= 0:
            # ดึงข้อมูลสินค้าที่เลือก
            product_name = self.product_table.item(current_row, 0).text()
            serial_number = self.product_table.item(current_row, 4).text()
            
            try:
                import sqlite3
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                
                if serial_number:
                    cursor.execute('SELECT * FROM products WHERE serial_number = ?', (serial_number,))
                else:
                    cursor.execute('SELECT * FROM products WHERE name = ?', (product_name,))
                
                product_data = cursor.fetchone()
                conn.close()
                
                if product_data:
                    columns = [description[0] for description in cursor.description]
                    self.selected_product = dict(zip(columns, product_data))
                    self.accept()
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสินค้า")
                    
            except Exception as e:
                QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถเลือกสินค้า: {str(e)}")
        else:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสินค้า")

