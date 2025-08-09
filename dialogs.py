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
        self.db = PawnShopDatabase()
        self.customer_data = customer_data
        self.setup_ui()
        if customer_data:
            self.load_customer_data()
    
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
        
        basic_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        basic_layout.addWidget(self.customer_code_edit, 0, 1)
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
    
    def save_customer(self):
        """บันทึกข้อมูลลูกค้า"""
        # ตรวจสอบข้อมูลที่จำเป็น
        if not self.customer_code_edit.text().strip():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกรหัสลูกค้า")
            return
        
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อ")
            return
        
        # ตรวจสอบเลขบัตรประชาชน
        id_card = self.id_card_edit.text().strip()
        if id_card and not PawnShopUtils.validate_id_card(id_card):
            QMessageBox.warning(self, "แจ้งเตือน", "เลขบัตรประชาชนไม่ถูกต้อง")
            return
        
        # ตรวจสอบเบอร์โทรศัพท์
        phone = self.phone_edit.text().strip()
        if phone and not PawnShopUtils.validate_phone(phone):
            QMessageBox.warning(self, "แจ้งเตือน", "เบอร์โทรศัพท์ไม่ถูกต้อง")
            return
        
        customer_data = {
            'customer_code': self.customer_code_edit.text().strip(),
            'first_name': self.first_name_edit.text().strip(),
            'last_name': self.last_name_edit.text().strip(),
            'id_card': id_card,
            'phone': phone,
            'house_number': self.house_number_edit.text().strip(),
            'street': self.street_edit.text().strip(),
            'subdistrict': self.subdistrict_edit.text().strip(),
            'district': self.district_edit.text().strip(),
            'province': self.province_edit.text().strip(),
            'other_details': self.other_details_edit.toPlainText().strip()
        }
        
        try:
            if self.customer_data:  # แก้ไข
                # TODO: เพิ่มฟังก์ชันอัปเดตลูกค้า
                pass
            else:  # เพิ่มใหม่
                customer_id = self.db.add_customer(customer_data)
                customer_data['id'] = customer_id
            
            self.customer_data = customer_data
            QMessageBox.information(self, "สำเร็จ", "บันทึกข้อมูลลูกค้าเรียบร้อย")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
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
                # TODO: เพิ่มฟังก์ชันอัปเดตสินค้า
                pass
            else:  # เพิ่มใหม่
                product_id = self.db.add_product(product_data)
                product_data['id'] = product_id
            
            self.product_data = product_data
            QMessageBox.information(self, "สำเร็จ", "บันทึกข้อมูลสินค้าเรียบร้อย")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

class InterestPaymentDialog(QDialog):
    def __init__(self, parent=None, contract_data=None):
        super().__init__(parent)
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
            customer_name = f"{self.contract_data.get('first_name', '')} {self.contract_data.get('last_name', '')}"
            self.customer_name_label.setText(customer_name)
            self.pawn_amount_label.setText(f"{self.contract_data.get('pawn_amount', 0):,.2f} บาท")
            self.interest_rate_label.setText(f"{self.contract_data.get('interest_rate', 0):.2f}%")
    
    def calculate_total(self):
        """คำนวณยอดรวม"""
        interest = self.interest_amount_spin.value()
        penalty = self.penalty_amount_spin.value()
        discount = self.discount_amount_spin.value()
        total = interest + penalty - discount
        self.total_amount_label.setText(f"{total:,.2f} บาท")
    
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
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

class RedemptionDialog(QDialog):
    def __init__(self, parent=None, contract_data=None):
        super().__init__(parent)
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
            customer_name = f"{self.contract_data.get('first_name', '')} {self.contract_data.get('last_name', '')}"
            self.customer_name_label.setText(customer_name)
            self.pawn_amount_label.setText(f"{self.contract_data.get('pawn_amount', 0):,.2f} บาท")
            self.total_redemption_label.setText(f"{self.contract_data.get('total_redemption', 0):,.2f} บาท")
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
