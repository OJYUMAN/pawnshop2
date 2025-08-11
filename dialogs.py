# -*- coding: utf-8 -*-
import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QRadioButton, QCheckBox, QFileDialog, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QIcon
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from database import PawnShopDatabase
from utils import PawnShopUtils

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer_data=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.customer_data = customer_data
        self.setup_ui()
        if customer_data:
            self.load_customer_data()
        else:
            # สร้างรหัสลูกค้าอัตโนมัติเมื่อเพิ่มลูกค้าใหม่
            self.generate_customer_code()
    
    def setup_ui(self):
        self.setWindowTitle("ข้อมูลลูกค้า")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลพื้นฐาน
        basic_group = QGroupBox("ข้อมูลพื้นฐาน")
        basic_layout = QGridLayout(basic_group)
        
        self.customer_code_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.id_card_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        
        # เพิ่มปุ่มสร้างรหัสลูกค้าอัตโนมัติ
        generate_code_button = QPushButton("สร้างรหัสอัตโนมัติ")
        generate_code_button.clicked.connect(self.generate_customer_code)
        
        basic_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        basic_layout.addWidget(self.customer_code_edit, 0, 1)
        basic_layout.addWidget(generate_code_button, 0, 2)
        basic_layout.addWidget(QLabel("ชื่อ:"), 1, 0)
        basic_layout.addWidget(self.first_name_edit, 1, 1)
        basic_layout.addWidget(QLabel("นามสกุล:"), 2, 0)
        basic_layout.addWidget(self.last_name_edit, 2, 1)
        basic_layout.addWidget(QLabel("เลขบัตรประชาชน:"), 3, 0)
        basic_layout.addWidget(self.id_card_edit, 3, 1)
        basic_layout.addWidget(QLabel("เบอร์โทรศัพท์:"), 4, 0)
        basic_layout.addWidget(self.phone_edit, 4, 1)
        
        layout.addWidget(basic_group)
        
        # ที่อยู่
        address_group = QGroupBox("ที่อยู่")
        address_layout = QGridLayout(address_group)
        
        self.house_number_edit = QLineEdit()
        self.street_edit = QLineEdit()
        self.subdistrict_edit = QLineEdit()
        self.district_edit = QLineEdit()
        self.province_edit = QLineEdit()
        self.other_details_edit = QTextEdit()
        self.other_details_edit.setMaximumHeight(60)
        
        address_layout.addWidget(QLabel("บ้านเลขที่:"), 0, 0)
        address_layout.addWidget(self.house_number_edit, 0, 1)
        address_layout.addWidget(QLabel("ซอย/ถนน:"), 1, 0)
        address_layout.addWidget(self.street_edit, 1, 1)
        address_layout.addWidget(QLabel("ตำบล/แขวง:"), 2, 0)
        address_layout.addWidget(self.subdistrict_edit, 2, 1)
        address_layout.addWidget(QLabel("อำเภอ/เขต:"), 3, 0)
        address_layout.addWidget(self.district_edit, 3, 1)
        address_layout.addWidget(QLabel("จังหวัด:"), 4, 0)
        address_layout.addWidget(self.province_edit, 4, 1)
        address_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 5, 0)
        address_layout.addWidget(self.other_details_edit, 5, 1)
        
        layout.addWidget(address_group)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        save_button = QPushButton("บันทึก")
        cancel_button = QPushButton("ยกเลิก")
        
        save_button.clicked.connect(self.save_customer)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_customer_data(self):
        """โหลดข้อมูลลูกค้า"""
        self.customer_code_edit.setText(self.customer_data.get('customer_code', ''))
        self.first_name_edit.setText(self.customer_data.get('first_name', ''))
        self.last_name_edit.setText(self.customer_data.get('last_name', ''))
        self.id_card_edit.setText(self.customer_data.get('id_card', ''))
        self.phone_edit.setText(self.customer_data.get('phone', ''))
        self.house_number_edit.setText(self.customer_data.get('house_number', ''))
        self.street_edit.setText(self.customer_data.get('street', ''))
        self.subdistrict_edit.setText(self.customer_data.get('subdistrict', ''))
        self.district_edit.setText(self.customer_data.get('district', ''))
        self.province_edit.setText(self.customer_data.get('province', ''))
        self.other_details_edit.setPlainText(self.customer_data.get('other_details', ''))
    
    def generate_customer_code(self):
        """สร้างรหัสลูกค้าอัตโนมัติ"""
        try:
            next_code = self.db.get_next_customer_code()
            self.customer_code_edit.setText(next_code)
        except Exception as e:
            QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถสร้างรหัสลูกค้าได้: {str(e)}")
    
    def clean_input_data(self, text: str) -> str:
        """ทำความสะอาดข้อมูลที่กรอก"""
        if not text:
            return ""
        # ลบช่องว่างและเครื่องหมายที่ไม่จำเป็น
        cleaned = re.sub(r'[\s\-\(\)]', '', text.strip())
        return cleaned
    
    def save_customer(self):
        """บันทึกข้อมูลลูกค้า"""
        # ตรวจสอบข้อมูลที่จำเป็น
        customer_code = self.customer_code_edit.text().strip()
        if not customer_code:
            # สร้างรหัสลูกค้าอัตโนมัติถ้าไม่ได้กรอก
            try:
                customer_code = self.db.get_next_customer_code()
                self.customer_code_edit.setText(customer_code)
            except Exception as e:
                QMessageBox.warning(self, "แจ้งเตือน", f"ไม่สามารถสร้างรหัสลูกค้าได้: {str(e)}")
                return
        
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อ")
            return
        
        # ตรวจสอบเลขบัตรประชาชน
        id_card = self.id_card_edit.text().strip()
        if id_card and not PawnShopUtils.validate_id_card(id_card):
            QMessageBox.warning(self, "แจ้งเตือน", 
                "เลขบัตรประชาชนไม่ถูกต้อง\nกรุณาตรวจสอบว่าเป็นเลข 13 หลักและไม่มีช่องว่าง")
            return
        
        # ตรวจสอบเบอร์โทรศัพท์
        phone = self.phone_edit.text().strip()
        if phone and not PawnShopUtils.validate_phone(phone):
            QMessageBox.warning(self, "แจ้งเตือน", 
                "เบอร์โทรศัพท์ไม่ถูกต้อง\nกรุณาตรวจสอบรูปแบบเบอร์โทรศัพท์ไทย")
            return
        
        customer_data = {
            'customer_code': customer_code,
            'first_name': self.first_name_edit.text().strip(),
            'last_name': self.last_name_edit.text().strip(),
            'id_card': self.clean_input_data(id_card),
            'phone': self.clean_input_data(phone),
            'house_number': self.house_number_edit.text().strip(),
            'street': self.street_edit.text().strip(),
            'subdistrict': self.subdistrict_edit.text().strip(),
            'district': self.district_edit.text().strip(),
            'province': self.province_edit.text().strip(),
            'other_details': self.other_details_edit.toPlainText().strip()
        }
        
        try:
            if self.customer_data:  # แก้ไข
                # ตรวจสอบข้อมูลซ้ำก่อนอัปเดต (ยกเว้นตัวเอง)
                existing_customer = self.db.get_customer_by_id(self.customer_data['id'])
                if existing_customer:
                    # ตรวจสอบว่าข้อมูลที่เปลี่ยนไปซ้ำกับลูกค้าอื่นหรือไม่
                    if (id_card and id_card != existing_customer.get('id_card', '') and 
                        self.db.check_customer_exists(id_card=id_card)):
                        QMessageBox.warning(self, "แจ้งเตือน", 
                            "เลขบัตรประชาชนนี้มีลูกค้าอื่นใช้อยู่แล้ว")
                        return
                    
                    if (customer_data['customer_code'] != existing_customer.get('customer_code', '') and 
                        self.db.check_customer_exists(customer_code=customer_data['customer_code'])):
                        QMessageBox.warning(self, "แจ้งเตือน", 
                            "รหัสลูกค้านี้มีลูกค้าอื่นใช้อยู่แล้ว")
                        return
                
                success = self.db.update_customer(self.customer_data['id'], customer_data)
                if success:
                    QMessageBox.information(self, "สำเร็จ", "อัปเดตข้อมูลลูกค้าเรียบร้อย")
                    self.accept()
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถอัปเดตข้อมูลลูกค้าได้")
            else:  # เพิ่มใหม่
                # ตรวจสอบข้อมูลซ้ำก่อนเพิ่ม
                if self.db.check_customer_exists(id_card=id_card, customer_code=customer_data['customer_code']):
                    QMessageBox.warning(self, "แจ้งเตือน", 
                        "ลูกค้านี้มีอยู่ในระบบแล้ว (เลขบัตรประชาชนหรือรหัสลูกค้าซ้ำ)")
                    return
                
                customer_id = self.db.add_customer(customer_data)
                customer_data['id'] = customer_id
                QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลลูกค้าเรียบร้อย")
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.product_data = product_data
        self.setup_ui()
        if product_data:
            self.load_product_data()
    
    def setup_ui(self):
        self.setWindowTitle("ข้อมูลสินค้า")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลสินค้า
        product_group = QGroupBox("ข้อมูลสินค้า")
        product_layout = QGridLayout(product_group)
        
        self.name_edit = QLineEdit()
        self.brand_edit = QLineEdit()
        self.size_edit = QLineEdit()
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 999999)
        self.weight_spin.setSuffix(" กรัม")
        self.serial_edit = QLineEdit()
        self.other_details_edit = QTextEdit()
        self.other_details_edit.setMaximumHeight(80)
        
        product_layout.addWidget(QLabel("ชื่อสินค้า:"), 0, 0)
        product_layout.addWidget(self.name_edit, 0, 1)
        product_layout.addWidget(QLabel("ยี่ห้อ/รุ่น:"), 1, 0)
        product_layout.addWidget(self.brand_edit, 1, 1)
        product_layout.addWidget(QLabel("ขนาด:"), 2, 0)
        product_layout.addWidget(self.size_edit, 2, 1)
        product_layout.addWidget(QLabel("น้ำหนัก:"), 3, 0)
        product_layout.addWidget(self.weight_spin, 3, 1)
        product_layout.addWidget(QLabel("หมายเลขซีเรียล:"), 4, 0)
        product_layout.addWidget(self.serial_edit, 4, 1)
        product_layout.addWidget(QLabel("รายละเอียดอื่นๆ:"), 5, 0)
        product_layout.addWidget(self.other_details_edit, 5, 1)
        
        layout.addWidget(product_group)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        save_button = QPushButton("บันทึก")
        cancel_button = QPushButton("ยกเลิก")
        
        save_button.clicked.connect(self.save_product)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_product_data(self):
        """โหลดข้อมูลสินค้า"""
        self.name_edit.setText(self.product_data.get('name', ''))
        self.brand_edit.setText(self.product_data.get('brand', ''))
        self.size_edit.setText(self.product_data.get('size', ''))
        self.weight_spin.setValue(self.product_data.get('weight', 0))
        self.serial_edit.setText(self.product_data.get('serial_number', ''))
        self.other_details_edit.setPlainText(self.product_data.get('other_details', ''))
    
    def save_product(self):
        """บันทึกข้อมูลสินค้า"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อสินค้า")
            return
        
        product_data = {
            'name': self.name_edit.text().strip(),
            'brand': self.brand_edit.text().strip(),
            'size': self.size_edit.text().strip(),
            'weight': self.weight_spin.value(),
            'serial_number': self.serial_edit.text().strip(),
            'other_details': self.other_details_edit.toPlainText().strip()
        }
        
        try:
            if self.product_data:  # แก้ไข
                # ตรวจสอบหมายเลขซีเรียลซ้ำก่อนอัปเดต (ยกเว้นตัวเอง)
                existing_product = self.db.get_product_by_id(self.product_data['id'])
                if existing_product:
                    serial_number = product_data['serial_number']
                    if (serial_number and serial_number != existing_product.get('serial_number', '') and 
                        self.db.check_product_exists(serial_number=serial_number)):
                        QMessageBox.warning(self, "แจ้งเตือน", 
                            "หมายเลขซีเรียลนี้มีสินค้าอื่นใช้อยู่แล้ว")
                        return
                
                success = self.db.update_product(self.product_data['id'], product_data)
                if success:
                    QMessageBox.information(self, "สำเร็จ", "อัปเดตข้อมูลสินค้าเรียบร้อย")
                    self.accept()
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถอัปเดตข้อมูลสินค้าได้")
            else:  # เพิ่มใหม่
                # ตรวจสอบหมายเลขซีเรียลซ้ำก่อนเพิ่ม
                serial_number = product_data['serial_number']
                if serial_number and self.db.check_product_exists(serial_number=serial_number):
                    QMessageBox.warning(self, "แจ้งเตือน", 
                        "สินค้านี้มีอยู่ในระบบแล้ว (หมายเลขซีเรียลซ้ำ)")
                    return
                
                product_id = self.db.add_product(product_data)
                product_data['id'] = product_id
                QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลสินค้าเรียบร้อย")
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))

class InterestPaymentDialog(QDialog):
    def __init__(self, parent=None, contract_data=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.contract_data = contract_data
        self.setup_ui()
        if contract_data:
            self.load_contract_data()
    
    def setup_ui(self):
        self.setWindowTitle("ชำระดอกเบี้ย")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลสัญญา
        contract_group = QGroupBox("ข้อมูลสัญญา")
        contract_layout = QGridLayout(contract_group)
        
        self.contract_number_label = QLabel()
        self.customer_name_label = QLabel()
        self.pawn_amount_label = QLabel()
        self.interest_rate_label = QLabel()
        
        contract_layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        contract_layout.addWidget(self.contract_number_label, 0, 1)
        contract_layout.addWidget(QLabel("ชื่อลูกค้า:"), 1, 0)
        contract_layout.addWidget(self.customer_name_label, 1, 1)
        contract_layout.addWidget(QLabel("ยอดฝาก:"), 2, 0)
        contract_layout.addWidget(self.pawn_amount_label, 2, 1)
        contract_layout.addWidget(QLabel("อัตราดอกเบี้ย:"), 3, 0)
        contract_layout.addWidget(self.interest_rate_label, 3, 1)
        
        layout.addWidget(contract_group)
        
        # ข้อมูลการชำระ
        payment_group = QGroupBox("ข้อมูลการชำระ")
        payment_layout = QGridLayout(payment_group)
        
        self.payment_date_edit = QDateEdit()
        self.payment_date_edit.setDate(QDate.currentDate())
        self.interest_amount_spin = QDoubleSpinBox()
        self.interest_amount_spin.setRange(0, 999999)
        self.interest_amount_spin.setSuffix(" บาท")
        self.penalty_amount_spin = QDoubleSpinBox()
        self.penalty_amount_spin.setRange(0, 999999)
        self.penalty_amount_spin.setSuffix(" บาท")
        self.discount_amount_spin = QDoubleSpinBox()
        self.discount_amount_spin.setRange(0, 999999)
        self.discount_amount_spin.setSuffix(" บาท")
        self.total_amount_label = QLabel("0.00 บาท")
        
        payment_layout.addWidget(QLabel("วันที่ชำระ:"), 0, 0)
        payment_layout.addWidget(self.payment_date_edit, 0, 1)
        payment_layout.addWidget(QLabel("ดอกเบี้ย:"), 1, 0)
        payment_layout.addWidget(self.interest_amount_spin, 1, 1)
        payment_layout.addWidget(QLabel("ค่าปรับ:"), 2, 0)
        payment_layout.addWidget(self.penalty_amount_spin, 2, 1)
        payment_layout.addWidget(QLabel("ส่วนลด:"), 3, 0)
        payment_layout.addWidget(self.discount_amount_spin, 3, 1)
        payment_layout.addWidget(QLabel("รวม:"), 4, 0)
        payment_layout.addWidget(self.total_amount_label, 4, 1)
        
        # เชื่อมต่อสัญญาณ
        self.interest_amount_spin.valueChanged.connect(self.calculate_total)
        self.penalty_amount_spin.valueChanged.connect(self.calculate_total)
        self.discount_amount_spin.valueChanged.connect(self.calculate_total)
        
        layout.addWidget(payment_group)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        save_button = QPushButton("บันทึก")
        cancel_button = QPushButton("ยกเลิก")
        
        save_button.clicked.connect(self.save_payment)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.contract_data:
            self.contract_number_label.setText(self.contract_data.get('contract_number', ''))
            customer_name = "{} {}".format(self.contract_data.get('first_name', ''), self.contract_data.get('last_name', ''))
            self.customer_name_label.setText(customer_name)
            self.pawn_amount_label.setText("{:,.2f} บาท".format(self.contract_data.get('pawn_amount', 0)))
            self.interest_rate_label.setText("{:.2f}%".format(self.contract_data.get('interest_rate', 0)))
    
    def calculate_total(self):
        """คำนวณยอดรวม"""
        interest = self.interest_amount_spin.value()
        penalty = self.penalty_amount_spin.value()
        discount = self.discount_amount_spin.value()
        total = interest + penalty - discount
        self.total_amount_label.setText("{:,.2f} บาท".format(total))
    
    def save_payment(self):
        """บันทึกการชำระ"""
        if not self.contract_data:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
            return
        
        payment_data = {
            'contract_id': self.contract_data['id'],
            'payment_date': self.payment_date_edit.date().toString("yyyy-MM-dd"),
            'interest_amount': self.interest_amount_spin.value(),
            'penalty_amount': self.penalty_amount_spin.value(),
            'discount_amount': self.discount_amount_spin.value(),
            'total_amount': float(self.total_amount_label.text().replace(' บาท', '').replace(',', ''))
        }
        
        try:
            payment_id = self.db.add_interest_payment(payment_data)
            QMessageBox.information(self, "สำเร็จ", "บันทึกการชำระดอกเบี้ยเรียบร้อย")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))

class RedemptionDialog(QDialog):
    def __init__(self, parent=None, contract_data=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.contract_data = contract_data
        self.setup_ui()
        if contract_data:
            self.load_contract_data()
    
    def setup_ui(self):
        self.setWindowTitle("ไถ่ถอนสัญญา")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลสัญญา
        contract_group = QGroupBox("ข้อมูลสัญญา")
        contract_layout = QGridLayout(contract_group)
        
        self.contract_number_label = QLabel()
        self.customer_name_label = QLabel()
        self.pawn_amount_label = QLabel()
        self.total_redemption_label = QLabel()
        
        contract_layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        contract_layout.addWidget(self.contract_number_label, 0, 1)
        contract_layout.addWidget(QLabel("ชื่อลูกค้า:"), 1, 0)
        contract_layout.addWidget(self.customer_name_label, 1, 1)
        contract_layout.addWidget(QLabel("ยอดฝาก:"), 2, 0)
        contract_layout.addWidget(self.pawn_amount_label, 2, 1)
        contract_layout.addWidget(QLabel("ยอดไถ่ถอน:"), 3, 0)
        contract_layout.addWidget(self.total_redemption_label, 3, 1)
        
        layout.addWidget(contract_group)
        
        # ข้อมูลการไถ่ถอน
        redemption_group = QGroupBox("ข้อมูลการไถ่ถอน")
        redemption_layout = QGridLayout(redemption_group)
        
        self.redemption_date_edit = QDateEdit()
        self.redemption_date_edit.setDate(QDate.currentDate())
        self.redemption_amount_spin = QDoubleSpinBox()
        self.redemption_amount_spin.setRange(0, 999999)
        self.redemption_amount_spin.setSuffix(" บาท")
        
        redemption_layout.addWidget(QLabel("วันที่ไถ่ถอน:"), 0, 0)
        redemption_layout.addWidget(self.redemption_date_edit, 0, 1)
        redemption_layout.addWidget(QLabel("ยอดไถ่ถอน:"), 1, 0)
        redemption_layout.addWidget(self.redemption_amount_spin, 1, 1)
        
        layout.addWidget(redemption_group)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        save_button = QPushButton("บันทึก")
        cancel_button = QPushButton("ยกเลิก")
        
        save_button.clicked.connect(self.save_redemption)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.contract_data:
            self.contract_number_label.setText(self.contract_data.get('contract_number', ''))
            customer_name = "{} {}".format(self.contract_data.get('first_name', ''), self.contract_data.get('last_name', ''))
            self.customer_name_label.setText(customer_name)
            self.pawn_amount_label.setText("{:,.2f} บาท".format(self.contract_data.get('pawn_amount', 0)))
            self.total_redemption_label.setText("{:,.2f} บาท".format(self.contract_data.get('total_redemption', 0)))
            self.redemption_amount_spin.setValue(self.contract_data.get('total_redemption', 0))
    
    def save_redemption(self):
        """บันทึกการไถ่ถอน"""
        if not self.contract_data:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
            return
        
        redemption_data = {
            'contract_id': self.contract_data['id'],
            'redemption_date': self.redemption_date_edit.date().toString("yyyy-MM-dd"),
            'redemption_amount': self.redemption_amount_spin.value()
        }
        
        try:
            redemption_id = self.db.redeem_contract(redemption_data)
            QMessageBox.information(self, "สำเร็จ", "บันทึกการไถ่ถอนเรียบร้อย")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

class RenewalDialog(QDialog):
    def __init__(self, parent=None, contract_data=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.contract_data = contract_data
        self.setup_ui()
        if contract_data:
            self.load_contract_data()
    
    def setup_ui(self):
        self.setWindowTitle("ต่อดอก")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลสัญญา
        contract_group = QGroupBox("ข้อมูลสัญญา")
        contract_layout = QGridLayout(contract_group)
        
        self.contract_number_label = QLabel()
        self.customer_name_label = QLabel()
        self.pawn_amount_label = QLabel()
        self.interest_rate_label = QLabel()
        
        contract_layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        contract_layout.addWidget(self.contract_number_label, 0, 1)
        contract_layout.addWidget(QLabel("ชื่อลูกค้า:"), 1, 0)
        contract_layout.addWidget(self.customer_name_label, 1, 1)
        contract_layout.addWidget(QLabel("ยอดฝาก:"), 2, 0)
        contract_layout.addWidget(self.pawn_amount_label, 2, 1)
        contract_layout.addWidget(QLabel("อัตราดอกเบี้ย:"), 3, 0)
        contract_layout.addWidget(self.interest_rate_label, 3, 1)
        
        layout.addWidget(contract_group)
        
        # ข้อมูลการต่อดอก
        renewal_group = QGroupBox("ข้อมูลการต่อดอก")
        renewal_layout = QGridLayout(renewal_group)
        
        # จำนวนวันฝากนับถึงปัจจุบัน
        self.days_deposit_label = QLabel("0 วัน")
        renewal_layout.addWidget(QLabel("จำนวนวันฝากนับถึงปัจจุบัน:"), 0, 0)
        renewal_layout.addWidget(self.days_deposit_label, 0, 1)
        
        # ต่อดอกครั้งที่
        self.renewal_count_spin = QSpinBox()
        self.renewal_count_spin.setRange(1, 99)
        self.renewal_count_spin.setValue(1)
        renewal_layout.addWidget(QLabel("ต่อดอกครั้งที่:"), 1, 0)
        renewal_layout.addWidget(self.renewal_count_spin, 1, 1)
        
        # ค่าธรรมเนียม
        self.fee_amount_spin = QDoubleSpinBox()
        self.fee_amount_spin.setRange(0, 999999)
        self.fee_amount_spin.setSuffix(" บาท")
        renewal_layout.addWidget(QLabel("ค่าธรรมเนียม:"), 2, 0)
        renewal_layout.addWidget(self.fee_amount_spin, 2, 1)
        
        # ค่าปรับ
        self.penalty_amount_spin = QDoubleSpinBox()
        self.penalty_amount_spin.setRange(0, 999999)
        self.penalty_amount_spin.setSuffix(" บาท")
        renewal_layout.addWidget(QLabel("ค่าปรับ:"), 3, 0)
        renewal_layout.addWidget(self.penalty_amount_spin, 3, 1)
        
        # ส่วนลด
        self.discount_amount_spin = QDoubleSpinBox()
        self.discount_amount_spin.setRange(0, 999999)
        self.discount_amount_spin.setSuffix(" บาท")
        renewal_layout.addWidget(QLabel("ส่วนลด:"), 4, 0)
        renewal_layout.addWidget(self.discount_amount_spin, 4, 1)
        
        # รวม
        self.total_amount_label = QLabel("0.00 บาท")
        renewal_layout.addWidget(QLabel("รวม:"), 5, 0)
        renewal_layout.addWidget(self.total_amount_label, 5, 1)
        
        # วันที่ต่อดอก
        self.renewal_date_edit = QDateEdit()
        self.renewal_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(QLabel("วันต่อดอก:"), 6, 0)
        renewal_layout.addWidget(self.renewal_date_edit, 6, 1)
        
        # วันครบกำหนดปัจจุบัน
        self.current_due_date_edit = QDateEdit()
        self.current_due_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(QLabel("วันครบกำหนดปัจจุบัน:"), 7, 0)
        renewal_layout.addWidget(self.current_due_date_edit, 7, 1)
        
        # วันครบกำหนดใหม่
        self.new_due_date_edit = QDateEdit()
        self.new_due_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(QLabel("วันครบกำหนดใหม่:"), 8, 0)
        renewal_layout.addWidget(self.new_due_date_edit, 8, 1)
        
        # เชื่อมต่อสัญญาณ
        self.fee_amount_spin.valueChanged.connect(self.calculate_total)
        self.penalty_amount_spin.valueChanged.connect(self.calculate_total)
        self.discount_amount_spin.valueChanged.connect(self.calculate_total)
        
        layout.addWidget(renewal_group)
        
        # ข้อความยืนยัน
        confirm_label = QLabel("คุณต้องการต่อดอกสัญญานี้ใช่หรือไม่")
        confirm_label.setAlignment(Qt.AlignCenter)
        confirm_label.setStyleSheet("font-weight: bold; color: #2E86AB; font-size: 14px;")
        layout.addWidget(confirm_label)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        save_button = QPushButton("ตกลง")
        save_button.setIcon(QIcon.fromTheme("document-save"))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        cancel_button = QPushButton("ไม่ใช่")
        cancel_button.setIcon(QIcon.fromTheme("edit-delete"))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        
        save_button.clicked.connect(self.save_renewal)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.contract_data:
            self.contract_number_label.setText(self.contract_data.get('contract_number', ''))
            customer_name = "{} {}".format(self.contract_data.get('first_name', ''), self.contract_data.get('last_name', ''))
            self.customer_name_label.setText(customer_name)
            self.pawn_amount_label.setText("{:,.2f} บาท".format(self.contract_data.get('pawn_amount', 0)))
            self.interest_rate_label.setText("{:.2f}%".format(self.contract_data.get('interest_rate', 0)))
            
            # คำนวณจำนวนวันฝาก
            self.calculate_deposit_days()
            
            # ตั้งค่าวันที่เริ่มต้น
            if self.contract_data.get('start_date'):
                try:
                    start_date = QDate.fromString(self.contract_data['start_date'], "yyyy-MM-dd")
                    if start_date.isValid():
                        self.current_due_date_edit.setDate(start_date.addDays(self.contract_data.get('days_count', 30)))
                except:
                    pass
    
    def calculate_deposit_days(self):
        """คำนวณจำนวนวันฝากนับถึงปัจจุบัน"""
        if self.contract_data and self.contract_data.get('start_date'):
            try:
                start_date = datetime.strptime(self.contract_data['start_date'], "%Y-%m-%d")
                current_date = datetime.now()
                days_diff = (current_date - start_date).days
                self.days_deposit_label.setText(f"{days_diff} วัน")
            except:
                self.days_deposit_label.setText("0 วัน")
    
    def calculate_total(self):
        """คำนวณยอดรวม"""
        fee = self.fee_amount_spin.value()
        penalty = self.penalty_amount_spin.value()
        discount = self.discount_amount_spin.value()
        total = fee + penalty - discount
        self.total_amount_label.setText("{:,.2f} บาท".format(total))
    
    def save_renewal(self):
        """บันทึกการต่อดอก"""
        if not self.contract_data:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
            return
        
        # ตรวจสอบข้อมูลที่จำเป็น
        if self.fee_amount_spin.value() == 0 and self.penalty_amount_spin.value() == 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกค่าธรรมเนียมหรือค่าปรับอย่างน้อยหนึ่งรายการ")
            return
        
        renewal_data = {
            'contract_id': self.contract_data['id'],
            'renewal_count': self.renewal_count_spin.value(),
            'fee_amount': self.fee_amount_spin.value(),
            'penalty_amount': self.penalty_amount_spin.value(),
            'discount_amount': self.discount_amount_spin.value(),
            'total_amount': float(self.total_amount_label.text().replace(' บาท', '').replace(',', '')),
            'renewal_date': self.renewal_date_edit.date().toString("yyyy-MM-dd"),
            'current_due_date': self.current_due_date_edit.date().toString("yyyy-MM-dd"),
            'new_due_date': self.new_due_date_edit.date().toString("yyyy-MM-dd"),
            'deposit_days': int(self.days_deposit_label.text().replace(' วัน', ''))
        }
        
        try:
            # บันทึกการต่อดอกในฐานข้อมูล
            renewal_id = self.db.add_renewal(renewal_data)
            
            # อัปเดตวันที่ครบกำหนดใหม่ในสัญญา
            self.db.update_contract_due_date(
                self.contract_data['id'], 
                renewal_data['new_due_date']
            )
            
            QMessageBox.information(self, "สำเร็จ", "บันทึกการต่อดอกเรียบร้อย")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))
