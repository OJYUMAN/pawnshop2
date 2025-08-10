# -*- coding: utf-8 -*-
"""
หน้าต่างจัดการค่าธรรมเนียม
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDoubleSpinBox, QSpinBox, QCheckBox, QGroupBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from typing import Dict, Optional
from database import PawnShopDatabase

class FeeRateDialog(QDialog):
    """หน้าต่างเพิ่ม/แก้ไขข้อมูลค่าธรรมเนียม"""
    
    def __init__(self, parent=None, fee_data: Optional[Dict] = None):
        super().__init__(parent)
        self.fee_data = fee_data
        self.is_edit_mode = fee_data is not None
        self.setup_ui()
        if self.is_edit_mode:
            self.load_fee_data()
    
    def setup_ui(self):
        title = "แก้ไขข้อมูลค่าธรรมเนียม" if self.is_edit_mode else "เพิ่มข้อมูลค่าธรรมเนียมใหม่"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # ฟอร์มข้อมูล
        form_group = QGroupBox("ข้อมูลค่าธรรมเนียม")
        form_layout = QGridLayout(form_group)
        
        # จำนวนวัน
        form_layout.addWidget(QLabel("จำนวนวัน:"), 0, 0)
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        form_layout.addWidget(self.days_spin, 0, 1)
        
        # อัตราค่าธรรมเนียม
        form_layout.addWidget(QLabel("อัตราค่าธรรมเนียม (%):"), 1, 0)
        self.fee_rate_spin = QDoubleSpinBox()
        self.fee_rate_spin.setRange(0, 100)
        self.fee_rate_spin.setValue(3.0)
        self.fee_rate_spin.setDecimals(2)
        self.fee_rate_spin.setSuffix(" %")
        form_layout.addWidget(self.fee_rate_spin, 1, 1)
        
        # คำอธิบาย
        form_layout.addWidget(QLabel("คำอธิบาย:"), 2, 0)
        self.description_edit = QLineEdit()
        form_layout.addWidget(self.description_edit, 2, 1)
        
        # สถานะ
        form_layout.addWidget(QLabel("สถานะ:"), 3, 0)
        self.is_active_check = QCheckBox("ใช้งาน")
        self.is_active_check.setChecked(True)
        form_layout.addWidget(self.is_active_check, 3, 1)
        
        layout.addWidget(form_group)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("บันทึก")
        self.save_button.clicked.connect(self.save_fee_rate)
        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def load_fee_data(self):
        """โหลดข้อมูลค่าธรรมเนียมสำหรับแก้ไข"""
        if self.fee_data:
            self.days_spin.setValue(self.fee_data.get('days_count', 30))
            self.fee_rate_spin.setValue(self.fee_data.get('fee_rate', 3.0))
            self.description_edit.setText(self.fee_data.get('description', ''))
            self.is_active_check.setChecked(self.fee_data.get('is_active', True))
    
    def save_fee_rate(self):
        """บันทึกข้อมูลค่าธรรมเนียม"""
        days = self.days_spin.value()
        fee_rate = self.fee_rate_spin.value()
        description = self.description_edit.text().strip()
        is_active = self.is_active_check.isChecked()
        
        if days <= 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกจำนวนวันให้ถูกต้อง")
            return
        
        if fee_rate < 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกอัตราค่าธรรมเนียมให้ถูกต้อง")
            return
        
        fee_data = {
            'days_count': days,
            'fee_rate': fee_rate,
            'description': description,
            'is_active': is_active
        }
        
        self.fee_data = fee_data
        self.accept()

class FeeManagementDialog(QDialog):
    """หน้าต่างจัดการค่าธรรมเนียม"""
    
    fee_updated = Signal()  # สัญญาณเมื่อมีการอัปเดตข้อมูล
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = PawnShopDatabase()
        self.setup_ui()
        self.load_fee_rates()
    
    def setup_ui(self):
        self.setWindowTitle("ตารางจัดการค่าธรรมเนียม")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # ปุ่มจัดการ
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("เพิ่มข้อมูลใหม่")
        self.add_button.clicked.connect(self.add_fee_rate)
        self.edit_button = QPushButton("แก้ไข")
        self.edit_button.clicked.connect(self.edit_fee_rate)
        self.delete_button = QPushButton("ลบ")
        self.delete_button.clicked.connect(self.delete_fee_rate)
        self.refresh_button = QPushButton("รีเฟรช")
        self.refresh_button.clicked.connect(self.load_fee_rates)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # ตารางข้อมูล
        self.fee_table = QTableWidget()
        self.fee_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fee_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.fee_table.setAlternatingRowColors(True)
        
        # ตั้งค่าหัวตาราง
        headers = ["ลำดับ", "จำนวนวัน", "ค่าธรรมเนียม (%)", "คำอธิบาย", "สถานะ", "วันที่สร้าง", "วันที่อัปเดต"]
        self.fee_table.setColumnCount(len(headers))
        self.fee_table.setHorizontalHeaderLabels(headers)
        
        # ตั้งค่าความกว้างคอลัมน์
        header = self.fee_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ลำดับ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # จำนวนวัน
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # ค่าธรรมเนียม
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # คำอธิบาย
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # สถานะ
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # วันที่สร้าง
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # วันที่อัปเดต
        
        layout.addWidget(self.fee_table)
        
        # ปุ่มปิด
        close_button = QPushButton("ปิด")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def load_fee_rates(self):
        """โหลดข้อมูลค่าธรรมเนียมทั้งหมด"""
        try:
            fee_rates = self.db.get_all_fee_rates()
            self.fee_table.setRowCount(len(fee_rates))
            
            for row, fee_rate in enumerate(fee_rates):
                # ลำดับ
                self.fee_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                
                # จำนวนวัน
                self.fee_table.setItem(row, 1, QTableWidgetItem(str(fee_rate['days_count'])))
                
                # ค่าธรรมเนียม
                fee_rate_text = f"{fee_rate['fee_rate']:.2f}"
                self.fee_table.setItem(row, 2, QTableWidgetItem(fee_rate_text))
                
                # คำอธิบาย
                self.fee_table.setItem(row, 3, QTableWidgetItem(fee_rate.get('description', '')))
                
                # สถานะ
                status_text = "ใช้งาน" if fee_rate.get('is_active', True) else "ไม่ใช้งาน"
                status_item = QTableWidgetItem(status_text)
                if not fee_rate.get('is_active', True):
                    status_item.setBackground(Qt.lightGray)
                self.fee_table.setItem(row, 4, status_item)
                
                # วันที่สร้าง
                created_at = fee_rate.get('created_at', '')
                if created_at:
                    created_at = created_at.split(' ')[0] if ' ' in created_at else created_at
                self.fee_table.setItem(row, 5, QTableWidgetItem(created_at))
                
                # วันที่อัปเดต
                updated_at = fee_rate.get('updated_at', '')
                if updated_at:
                    updated_at = updated_at.split(' ')[0] if ' ' in updated_at else updated_at
                self.fee_table.setItem(row, 6, QTableWidgetItem(updated_at))
                
                # เก็บข้อมูล ID ไว้ใน item
                self.fee_table.item(row, 0).setData(Qt.UserRole, fee_rate['id'])
            
            # ปิดการแก้ไข
            self.fee_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
    
    def get_selected_fee_id(self) -> Optional[int]:
        """ดึง ID ของค่าธรรมเนียมที่เลือก"""
        current_row = self.fee_table.currentRow()
        if current_row >= 0:
            item = self.fee_table.item(current_row, 0)
            if item:
                return item.data(Qt.UserRole)
        return None
    
    def add_fee_rate(self):
        """เพิ่มข้อมูลค่าธรรมเนียมใหม่"""
        dialog = FeeRateDialog(self)
        if dialog.exec():
            try:
                fee_id = self.db.add_fee_rate(dialog.fee_data)
                if fee_id:
                    QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลค่าธรรมเนียมเรียบร้อย")
                    self.load_fee_rates()
                    self.fee_updated.emit()
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถเพิ่มข้อมูลได้")
            except Exception as e:
                QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def edit_fee_rate(self):
        """แก้ไขข้อมูลค่าธรรมเนียม"""
        fee_id = self.get_selected_fee_id()
        if not fee_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกข้อมูลที่ต้องการแก้ไข")
            return
        
        # ดึงข้อมูลปัจจุบัน
        try:
            fee_rates = self.db.get_all_fee_rates()
            current_fee = None
            for fee_rate in fee_rates:
                if fee_rate['id'] == fee_id:
                    current_fee = fee_rate
                    break
            
            if not current_fee:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลที่ต้องการแก้ไข")
                return
            
            dialog = FeeRateDialog(self, current_fee)
            if dialog.exec():
                try:
                    success = self.db.update_fee_rate(fee_id, dialog.fee_data)
                    if success:
                        QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลค่าธรรมเนียมเรียบร้อย")
                        self.load_fee_rates()
                        self.fee_updated.emit()
                    else:
                        QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถแก้ไขข้อมูลได้")
                except Exception as e:
                    QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
                    
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def delete_fee_rate(self):
        """ลบข้อมูลค่าธรรมเนียม"""
        fee_id = self.get_selected_fee_id()
        if not fee_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกข้อมูลที่ต้องการลบ")
            return
        
        # ยืนยันการลบ
        reply = QMessageBox.question(
            self, 
            "ยืนยันการลบ", 
            "คุณต้องการลบข้อมูลค่าธรรมเนียมนี้หรือไม่?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.db.delete_fee_rate(fee_id)
                if success:
                    QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลค่าธรรมเนียมเรียบร้อย")
                    self.load_fee_rates()
                    self.fee_updated.emit()
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถลบข้อมูลได้")
            except Exception as e:
                QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
