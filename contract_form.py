# -*- coding: utf-8 -*-
"""
หน้าต่างฟอร์มเพิ่มสัญญาใหม่
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QGroupBox, QTabWidget, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
from datetime import datetime, timedelta
from typing import Dict, Optional
from database import PawnShopDatabase
from utils import PawnShopUtils
from dialogs import CustomerDialog, ProductDialog
from customer_search import CustomerSearchDialog
from product_search import ProductSearchDialog

class NewContractDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = PawnShopDatabase()
        self.current_customer = None
        self.current_product = None
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        self.setWindowTitle("เพิ่มสัญญาใหม่")
        self.setModal(True)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # สร้าง Tab Widget
        tab_widget = QTabWidget()
        
        # Tab 1: ข้อมูลสัญญา
        contract_tab = self.create_contract_tab()
        tab_widget.addTab(contract_tab, "ข้อมูลสัญญา")
        
        # Tab 2: ข้อมูลลูกค้า
        customer_tab = self.create_customer_tab()
        tab_widget.addTab(customer_tab, "ข้อมูลลูกค้า")
        
        # Tab 3: ข้อมูลสินค้า
        product_tab = self.create_product_tab()
        tab_widget.addTab(product_tab, "ข้อมูลสินค้า")
        
        # Tab 4: ข้อมูลการต่อดอก
        renewal_tab = self.create_renewal_tab()
        tab_widget.addTab(renewal_tab, "ข้อมูลการต่อดอก")
        
        layout.addWidget(tab_widget)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        
        # ปุ่มโหลดสัญญาเดิม
        self.load_existing_contract_btn = QPushButton("โหลดสัญญาเดิม")
        self.load_existing_contract_btn.clicked.connect(self.load_existing_contract)
        
        # ปุ่มบันทึก
        self.save_button = QPushButton("บันทึกสัญญา")
        self.save_button.clicked.connect(self.save_contract)
        
        # ปุ่มยกเลิก
        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.load_existing_contract_btn)
        button_layout.addWidget(self.save_button)
        
        # ปุ่มล้างฟอร์ม
        self.clear_form_btn = QPushButton("ล้างฟอร์ม")
        self.clear_form_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_form_btn)
        
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def create_contract_tab(self):
        """สร้าง Tab ข้อมูลสัญญา"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ข้อมูลสัญญา
        contract_group = QGroupBox("ข้อมูลสัญญา")
        contract_layout = QGridLayout(contract_group)
        
        # เลขที่สัญญา
        contract_layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        self.contract_number_edit = QLineEdit()
        self.contract_number_edit.setReadOnly(True)
        contract_layout.addWidget(self.contract_number_edit, 0, 1)
        
        # วันที่เริ่มต้น
        contract_layout.addWidget(QLabel("วันที่เริ่มต้น:"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.dateChanged.connect(self.calculate_end_date)
        contract_layout.addWidget(self.start_date_edit, 1, 1)
        
        # จำนวนวัน
        contract_layout.addWidget(QLabel("จำนวนวัน:"), 2, 0)
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.valueChanged.connect(self.calculate_end_date)
        contract_layout.addWidget(self.days_spin, 2, 1)
        
        # วันที่สิ้นสุด
        contract_layout.addWidget(QLabel("วันที่สิ้นสุด:"), 3, 0)
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setReadOnly(True)
        contract_layout.addWidget(self.end_date_edit, 3, 1)
        
        layout.addWidget(contract_group)
        
        # ข้อมูลการเงิน
        finance_group = QGroupBox("ข้อมูลการเงิน")
        finance_layout = QGridLayout(finance_group)
        
        # ยอดฝาก
        finance_layout.addWidget(QLabel("ยอดฝาก:"), 0, 0)
        self.pawn_amount_spin = QDoubleSpinBox()
        self.pawn_amount_spin.setRange(0, 999999)
        self.pawn_amount_spin.setSuffix(" บาท")
        self.pawn_amount_spin.valueChanged.connect(self.calculate_amounts)
        finance_layout.addWidget(self.pawn_amount_spin, 0, 1)
        
        # ยอดจ่าย
        finance_layout.addWidget(QLabel("ยอดจ่าย:"), 1, 0)
        self.total_paid_label = QLabel("0.00 บาท")
        finance_layout.addWidget(self.total_paid_label, 1, 1)
        
        # ยอดไถ่คืน
        finance_layout.addWidget(QLabel("ยอดไถ่คืน:"), 2, 0)
        self.total_redemption_label = QLabel("0.00 บาท")
        finance_layout.addWidget(self.total_redemption_label, 2, 1)
        
        layout.addWidget(finance_group)
        
        # คำนวณวันที่สิ้นสุด
        self.calculate_end_date()
        
        return widget
    
    def create_customer_tab(self):
        """สร้าง Tab ข้อมูลลูกค้า"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ปุ่มค้นหา/เพิ่มลูกค้า
        button_layout = QHBoxLayout()
        self.search_customer_btn = QPushButton("ค้นหาลูกค้า")
        self.search_customer_btn.clicked.connect(self.search_customer)
        self.add_customer_btn = QPushButton("เพิ่มลูกค้าใหม่")
        self.add_customer_btn.clicked.connect(self.add_customer)
        button_layout.addWidget(self.search_customer_btn)
        button_layout.addWidget(self.add_customer_btn)
        layout.addLayout(button_layout)
        
        # ข้อมูลลูกค้า
        customer_group = QGroupBox("ข้อมูลลูกค้า")
        customer_layout = QGridLayout(customer_group)
        
        # รหัสลูกค้า
        customer_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        self.customer_code_edit = QLineEdit()
        self.customer_code_edit.setReadOnly(True)
        customer_layout.addWidget(self.customer_code_edit, 0, 1)
        
        # ชื่อลูกค้า
        customer_layout.addWidget(QLabel("ชื่อลูกค้า:"), 1, 0)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setReadOnly(True)
        customer_layout.addWidget(self.customer_name_edit, 1, 1)
        
        # เลขบัตรประชาชน
        customer_layout.addWidget(QLabel("เลขบัตรประชาชน:"), 2, 0)
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setReadOnly(True)
        customer_layout.addWidget(self.id_card_edit, 2, 1)
        
        # เบอร์โทรศัพท์
        customer_layout.addWidget(QLabel("เบอร์โทรศัพท์:"), 3, 0)
        self.phone_edit = QLineEdit()
        self.phone_edit.setReadOnly(True)
        customer_layout.addWidget(self.phone_edit, 3, 1)
        
        # ที่อยู่
        customer_layout.addWidget(QLabel("ที่อยู่:"), 4, 0)
        self.address_edit = QLineEdit()
        self.address_edit.setReadOnly(True)
        customer_layout.addWidget(self.address_edit, 4, 1)
        
        layout.addWidget(customer_group)
        
        return widget
    
    def create_product_tab(self):
        """สร้าง Tab ข้อมูลสินค้า"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ปุ่มเพิ่ม/ค้นหาสินค้า
        button_layout = QHBoxLayout()
        self.search_product_btn = QPushButton("ค้นหาสินค้า")
        self.search_product_btn.clicked.connect(self.search_product)
        self.add_product_btn = QPushButton("เพิ่มสินค้าใหม่")
        self.add_product_btn.clicked.connect(self.add_product)
        button_layout.addWidget(self.search_product_btn)
        button_layout.addWidget(self.add_product_btn)
        layout.addLayout(button_layout)
        
        # ข้อมูลสินค้า
        product_group = QGroupBox("ข้อมูลสินค้า")
        product_layout = QGridLayout(product_group)
        
        # ชื่อสินค้า
        product_layout.addWidget(QLabel("ชื่อสินค้า:"), 0, 0)
        self.product_name_edit = QLineEdit()
        self.product_name_edit.setReadOnly(True)
        product_layout.addWidget(self.product_name_edit, 0, 1)
        
        # ยี่ห้อ/รุ่น
        product_layout.addWidget(QLabel("ยี่ห้อ/รุ่น:"), 1, 0)
        self.product_brand_edit = QLineEdit()
        self.product_brand_edit.setReadOnly(True)
        product_layout.addWidget(self.product_brand_edit, 1, 1)
        
        # ขนาด
        product_layout.addWidget(QLabel("ขนาด:"), 2, 0)
        self.product_size_edit = QLineEdit()
        self.product_size_edit.setReadOnly(True)
        product_layout.addWidget(self.product_size_edit, 2, 1)
        
        # น้ำหนัก
        product_layout.addWidget(QLabel("น้ำหนัก:"), 3, 0)
        self.product_weight_edit = QLineEdit()
        self.product_weight_edit.setReadOnly(True)
        product_layout.addWidget(self.product_weight_edit, 3, 1)
        
        # หมายเลขซีเรียล
        product_layout.addWidget(QLabel("หมายเลขซีเรียล:"), 4, 0)
        self.serial_number_edit = QLineEdit()
        self.serial_number_edit.setReadOnly(True)
        product_layout.addWidget(self.serial_number_edit, 4, 1)
        
        # รายละเอียดอื่นๆ
        product_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 5, 0)
        self.product_details_edit = QLineEdit()
        self.product_details_edit.setReadOnly(True)
        product_layout.addWidget(self.product_details_edit, 5, 1)
        
        layout.addWidget(product_group)
        
        return widget
    
    def create_renewal_tab(self):
        """สร้าง Tab ข้อมูลการต่อดอก"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ข้อมูลการต่อดอก
        renewal_group = QGroupBox("ข้อมูลการต่อดอก")
        renewal_layout = QGridLayout(renewal_group)
        
        # จำนวนวันฝากนับถึงปัจจุบัน
        renewal_layout.addWidget(QLabel("จำนวนวันฝากนับถึงปัจจุบัน:"), 0, 0)
        self.days_deposit_label = QLabel("0 วัน")
        renewal_layout.addWidget(self.days_deposit_label, 0, 1)
        
        # ต่อดอกครั้งที่
        renewal_layout.addWidget(QLabel("ต่อดอกครั้งที่:"), 1, 0)
        self.renewal_count_spin = QSpinBox()
        self.renewal_count_spin.setRange(1, 99)
        self.renewal_count_spin.setValue(1)
        self.renewal_count_spin.valueChanged.connect(self.calculate_renewal_amounts)
        renewal_layout.addWidget(self.renewal_count_spin, 1, 1)
        
        
        # ค่าปรับ
        renewal_layout.addWidget(QLabel("ค่าปรับ:"), 2, 0)
        self.renewal_penalty_amount_spin = QDoubleSpinBox()
        self.renewal_penalty_amount_spin.setRange(0, 999999)
        self.renewal_penalty_amount_spin.setSuffix(" บาท")
        self.renewal_penalty_amount_spin.valueChanged.connect(self.calculate_renewal_amounts)
        renewal_layout.addWidget(self.renewal_penalty_amount_spin, 2, 1)
        
        # ส่วนลด
        renewal_layout.addWidget(QLabel("ส่วนลด:"), 3, 0)
        self.renewal_discount_amount_spin = QDoubleSpinBox()
        self.renewal_discount_amount_spin.setRange(0, 999999)
        self.renewal_discount_amount_spin.setSuffix(" บาท")
        self.renewal_discount_amount_spin.valueChanged.connect(self.calculate_renewal_amounts)
        renewal_layout.addWidget(self.renewal_discount_amount_spin, 3, 1)
        
        # รวม
        renewal_layout.addWidget(QLabel("รวม:"), 4, 0)
        self.renewal_total_amount_label = QLabel("0.00 บาท")
        renewal_layout.addWidget(self.renewal_total_amount_label, 4, 1)
        
        # วันที่ต่อดอก
        renewal_layout.addWidget(QLabel("วันต่อดอก:"), 5, 0)
        self.renewal_date_edit = QDateEdit()
        self.renewal_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(self.renewal_date_edit, 5, 1)
        
        # วันครบกำหนดปัจจุบัน
        renewal_layout.addWidget(QLabel("วันครบกำหนดปัจจุบัน:"), 6, 0)
        self.current_due_date_edit = QDateEdit()
        self.current_due_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(self.current_due_date_edit, 6, 1)
        
        # วันครบกำหนดใหม่
        renewal_layout.addWidget(QLabel("วันครบกำหนดใหม่:"), 7, 0)
        self.new_due_date_edit = QDateEdit()
        self.new_due_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(self.new_due_date_edit, 7, 1)
        
        # จำนวนวันต่อดอก
        renewal_layout.addWidget(QLabel("จำนวนวันต่อดอก:"), 8, 0)
        self.extension_days_spin = QSpinBox()
        self.extension_days_spin.setRange(1, 365)
        self.extension_days_spin.setValue(30)
        self.extension_days_spin.valueChanged.connect(self.calculate_extension_dates)
        renewal_layout.addWidget(self.extension_days_spin, 8, 1)
        
        layout.addWidget(renewal_group)
        
        # ปุ่มบันทึกการต่อดอก
        button_layout = QHBoxLayout()
        self.save_renewal_btn = QPushButton("บันทึกการต่อดอก")
        self.save_renewal_btn.clicked.connect(self.save_renewal)
        button_layout.addWidget(self.save_renewal_btn)
        layout.addLayout(button_layout)
        
        return widget
    
    def calculate_renewal_amounts(self):
        """คำนวณยอดการต่อดอก"""
        penalty_amount = self.renewal_penalty_amount_spin.value()
        discount_amount = self.renewal_discount_amount_spin.value()
        
        total_amount = penalty_amount - discount_amount
        self.renewal_total_amount_label.setText(f"{total_amount:,.2f} บาท")
    
    def calculate_extension_dates(self):
        """คำนวณวันที่ต่อดอก"""
        current_due_date = self.current_due_date_edit.date()
        extension_days = self.extension_days_spin.value()
        new_due_date = current_due_date.addDays(extension_days)
        self.new_due_date_edit.setDate(new_due_date)
    
    def save_renewal(self):
        """บันทึกการต่อดอก"""
        if not hasattr(self, 'current_contract') or not self.current_contract:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาสร้างสัญญาก่อนบันทึกการต่อดอก")
            return
        
        try:
            renewal_data = {
                'contract_id': self.current_contract['id'],
                'contract_number': self.current_contract['contract_number'],
                'renewal_count': self.renewal_count_spin.value(),
                'fee_amount': self.renewal_fee_amount_spin.value(),
                'penalty_amount': self.renewal_penalty_amount_spin.value(),
                'discount_amount': self.renewal_discount_amount_spin.value(),
                'total_amount': float(self.renewal_total_amount_label.text().replace(' บาท', '').replace(',', '')),
                'renewal_date': self.renewal_date_edit.date().toString("yyyy-MM-dd"),
                'current_due_date': self.current_due_date_edit.date().toString("yyyy-MM-dd"),
                'new_due_date': self.new_due_date_edit.date().toString("yyyy-MM-dd"),
                'extension_days': self.extension_days_spin.value()
            }
            
            renewal_id = self.db.add_renewal(renewal_data)
            QMessageBox.information(self, "สำเร็จ", "บันทึกการต่อดอกเรียบร้อย")
            
            # อัพเดทข้อมูลสัญญา
            self.current_contract = self.db.get_contract_by_id(self.current_contract['id'])
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def load_existing_contract(self):
        """โหลดสัญญาเดิมมาแก้ไข"""
        try:
            # สร้าง dialog สำหรับค้นหาสัญญา
            from PySide6.QtWidgets import QInputDialog
            
            contract_number, ok = QInputDialog.getText(
                self, 
                "โหลดสัญญาเดิม", 
                "กรุณากรอกเลขที่สัญญาที่ต้องการแก้ไข:"
            )
            
            if ok and contract_number.strip():
                # ค้นหาสัญญาในฐานข้อมูล
                contract = self.db.get_contract_by_number(contract_number.strip())
                
                if contract:
                    # ตั้งค่า current_contract
                    self.current_contract = contract
                    
                    # โหลดข้อมูลสัญญา
                    self.load_contract_data(contract)
                    
                    # โหลดข้อมูลลูกค้า
                    customer = self.db.get_customer_by_id(contract['customer_id'])
                    if customer:
                        self.current_customer = customer
                        self.load_customer_data()
                    
                    # โหลดข้อมูลสินค้า
                    product = self.db.get_product_by_id(contract['product_id'])
                    if product:
                        self.current_product = product
                        self.load_product_data()
                    
                    QMessageBox.information(self, "สำเร็จ", f"โหลดสัญญา {contract_number} เรียบร้อยแล้ว")
                else:
                    QMessageBox.warning(self, "ไม่พบข้อมูล", f"ไม่พบสัญญาเลขที่ {contract_number}")
            else:
                QMessageBox.information(self, "ยกเลิก", "ยกเลิกการโหลดสัญญา")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def load_contract_data(self, contract_data):
        """โหลดข้อมูลสัญญา"""
        if contract_data:
            # โหลดข้อมูลสัญญา
            self.contract_number_edit.setText(contract_data.get('contract_number', ''))
            self.pawn_amount_spin.setValue(contract_data.get('pawn_amount', 0))
            
            # โหลดวันที่
            start_date = contract_data.get('start_date', '')
            if start_date:
                try:
                    if isinstance(start_date, str):
                        if '-' in start_date:
                            from PySide6.QtCore import QDate
                            date_obj = QDate.fromString(start_date, "yyyy-MM-dd")
                            if date_obj.isValid():
                                self.start_date_edit.setDate(date_obj)
                except:
                    pass
            
            # โหลดจำนวนวัน
            days_count = contract_data.get('days_count', 0)
            if days_count > 0:
                self.days_spin.setValue(days_count)
            
            # คำนวณวันที่สิ้นสุด
            self.calculate_end_date()
            
            # คำนวณยอดต่างๆ
            self.calculate_amounts()
    
    def clear_form(self):
        """ล้างฟอร์ม"""
        self.current_customer = None
        self.current_product = None
        self.current_contract = None
        
        # ล้างข้อมูลสัญญา
        self.contract_number_edit.clear()
        self.pawn_amount_spin.setValue(0)
        self.days_spin.setValue(30)
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.clear()
        
        # ล้างข้อมูลลูกค้า
        self.customer_code_edit.clear()
        self.customer_name_edit.clear()
        self.address_edit.clear()
        self.id_card_edit.clear()
        self.phone_edit.clear()
        
        # ล้างข้อมูลสินค้า
        self.product_name_edit.clear()
        self.product_brand_edit.clear()
        self.product_size_edit.clear()
        self.product_weight_edit.clear()
        self.serial_number_edit.clear()
        self.product_details_edit.clear()
        
        # ล้างข้อมูลการต่อดอก
        if hasattr(self, 'renewal_penalty_amount_spin'):
            self.renewal_penalty_amount_spin.setValue(0)
            self.renewal_discount_amount_spin.setValue(0)
            self.renewal_total_amount_label.setText("0.00 บาท")
            self.renewal_date_edit.setDate(QDate.currentDate())
            self.extension_days_spin.setValue(30)
        
        # สร้างเลขที่สัญญาใหม่
        self.generate_new_contract_number()
        
        # คำนวณวันที่สิ้นสุด
        self.calculate_end_date()
        
        # คำนวณยอดต่างๆ
        self.calculate_amounts()
    
    def load_settings(self):
        """โหลดการตั้งค่า"""
        default_days = int(self.db.get_setting('default_contract_days'))
        
        self.days_spin.setValue(default_days)
        
        # ตั้งค่าเริ่มต้นสำหรับข้อมูลการต่อดอก
        if hasattr(self, 'extension_days_spin'):
            self.extension_days_spin.setValue(default_days)
            self.calculate_extension_dates()
        
        # สร้างเลขที่สัญญาใหม่
        self.generate_new_contract_number()
        
        # เพิ่มปุ่มโหลดสัญญาเดิม
        if hasattr(self, 'load_existing_contract_btn'):
            self.load_existing_contract_btn.clicked.connect(self.load_existing_contract)
    
    def generate_new_contract_number(self):
        """สร้างเลขที่สัญญาใหม่"""
        prefix = self.db.get_setting('contract_prefix')
        # คำนวณลำดับถัดไปจากฐานข้อมูล
        sequence = self.db.get_next_contract_sequence(prefix)
        contract_number = PawnShopUtils.generate_contract_number(prefix, sequence)
        self.contract_number_edit.setText(contract_number)
    
    def calculate_end_date(self):
        """คำนวณวันที่สิ้นสุด"""
        start_date = self.start_date_edit.date()
        days = self.days_spin.value()
        end_date = start_date.addDays(days)
        self.end_date_edit.setText(end_date.toString("dd/MM/yyyy"))
        
        # อัพเดทวันที่ครบกำหนดปัจจุบันในการต่อดอก
        if hasattr(self, 'current_due_date_edit'):
            self.current_due_date_edit.setDate(end_date)
            self.calculate_extension_dates()
    
    def calculate_amounts(self):
        """คำนวณยอดต่างๆ"""
        pawn_amount = self.pawn_amount_spin.value()
        
        # ยอดจ่าย
        total_paid = pawn_amount
        
        # ยอดไถ่คืน
        total_redemption = pawn_amount
        
        # แสดงผล
        self.total_paid_label.setText(f"{total_paid:,.2f} บาท")
        self.total_redemption_label.setText(f"{total_redemption:,.2f} บาท")
    
    def search_customer(self):
        """ค้นหาลูกค้า"""
        dialog = CustomerSearchDialog(self)
        if dialog.exec():
            self.current_customer = dialog.selected_customer
            self.load_customer_data()
    
    def add_customer(self):
        """เพิ่มลูกค้าใหม่"""
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.current_customer = dialog.customer_data
            self.load_customer_data()
    
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
            self.address_edit.setText(address)
    
    def search_product(self):
        """ค้นหาสินค้า"""
        dialog = ProductSearchDialog(self)
        if dialog.exec():
            self.current_product = dialog.selected_product
            self.load_product_data()
    
    def add_product(self):
        """เพิ่มสินค้าใหม่"""
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
            self.product_weight_edit.setText(f"{self.current_product.get('weight', 0)} กรัม")
            self.serial_number_edit.setText(self.current_product.get('serial_number', ''))
            self.product_details_edit.setText(self.current_product.get('other_details', ''))
    

    
    def save_contract(self):
        """บันทึกสัญญา"""
        # ตรวจสอบข้อมูลที่จำเป็น
        if not self.current_customer:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกลูกค้าก่อน")
            return
        
        if not self.current_product:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสินค้าก่อน")
            return
        
        if self.pawn_amount_spin.value() <= 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกยอดฝาก")
            return
        
        # สร้างข้อมูลสัญญา
        contract_data = {
            'contract_number': self.contract_number_edit.text(),
            'customer_id': self.current_customer['id'],
            'product_id': self.current_product['id'],
            'pawn_amount': self.pawn_amount_spin.value(),
            'total_paid': float(self.total_paid_label.text().replace(' บาท', '').replace(',', '')),
            'total_redemption': float(self.total_redemption_label.text().replace(' บาท', '').replace(',', '')),
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_edit.text(),
            'days_count': self.days_spin.value()
        }
        
        try:
            # ตรวจสอบว่ามีสัญญาอยู่แล้วหรือไม่
            if hasattr(self, 'current_contract') and self.current_contract:
                # อัพเดทสัญญาเดิม
                contract_data['id'] = self.current_contract['id']
                contract_id = self.db.update_contract(contract_data)
                action_message = "อัพเดทสัญญาเรียบร้อย"
            else:
                # สร้างสัญญาใหม่
                contract_id = self.db.create_contract(contract_data)
                action_message = "บันทึกสัญญาเรียบร้อย"
            
            # บันทึกข้อมูลการต่อดอกถ้ามี
            if hasattr(self, 'renewal_penalty_amount_spin') and (self.renewal_penalty_amount_spin.value() > 0 or self.renewal_discount_amount_spin.value() > 0):
                renewal_data = {
                    'contract_id': contract_id,
                    'contract_number': contract_data['contract_number'],
                    'renewal_count': self.renewal_count_spin.value(),
                    'penalty_amount': self.renewal_penalty_amount_spin.value(),
                    'discount_amount': self.renewal_discount_amount_spin.value(),
                    'total_amount': float(self.renewal_total_amount_label.text().replace(' บาท', '').replace(',', '')),
                    'renewal_date': self.renewal_date_edit.date().toString("yyyy-MM-dd"),
                    'current_due_date': self.current_due_date_edit.date().toString("yyyy-MM-dd"),
                    'new_due_date': self.new_due_date_edit.date().toString("yyyy-MM-dd"),
                    'extension_days': self.extension_days_spin.value()
                }
                
                self.db.add_renewal(renewal_data)
            
            QMessageBox.information(self, "สำเร็จ", action_message)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
