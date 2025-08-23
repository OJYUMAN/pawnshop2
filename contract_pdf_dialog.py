# -*- coding: utf-8 -*-
"""
หน้าต่างสำหรับสร้างใบขายฝาก PDF จากสัญญาที่มีอยู่แล้ว
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from database import PawnShopDatabase
from contract_pdf_generator import ContractPDFGenerator
import os
import subprocess
import platform

class ContractPDFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = PawnShopDatabase()
        self.setup_ui()
        self.load_contracts()
    
    def setup_ui(self):
        self.setWindowTitle("สร้างใบขายฝาก PDF")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # ส่วนค้นหา
        search_group = QGroupBox("ค้นหาสัญญา")
        search_layout = QFormLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ค้นหาด้วยเลขที่สัญญา หรือชื่อลูกค้า")
        self.search_edit.textChanged.connect(self.filter_contracts)
        search_layout.addRow("ค้นหา:", self.search_edit)
        
        layout.addWidget(search_group)
        
        # ตารางแสดงสัญญา
        self.contracts_table = QTableWidget()
        self.contracts_table.setColumnCount(7)
        self.contracts_table.setHorizontalHeaderLabels([
            "เลขที่สัญญา", "ชื่อลูกค้า", "สินค้า", "ยอดฝาก", "วันที่เริ่ม", "วันที่สิ้นสุด", "สถานะ"
        ])
        
        # ตั้งค่าตาราง
        header = self.contracts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.contracts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contracts_table.setSelectionMode(QTableWidget.SingleSelection)
        self.contracts_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.contracts_table)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        self.generate_pdf_button = QPushButton("สร้าง PDF")
        self.generate_pdf_button.clicked.connect(self.generate_pdf)
        self.generate_pdf_button.setEnabled(False)
        self.close_button = QPushButton("ปิด")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.generate_pdf_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
    
    def load_contracts(self):
        """โหลดข้อมูลสัญญาทั้งหมด"""
        try:
            # ดึงข้อมูลสัญญาทั้งหมด
            contracts = self.db.get_all_contracts()
            self.display_contracts(contracts)
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
    
    def display_contracts(self, contracts):
        """แสดงข้อมูลสัญญาในตาราง"""
        self.contracts_table.setRowCount(len(contracts))
        
        for row, contract in enumerate(contracts):
            # เลขที่สัญญา
            self.contracts_table.setItem(row, 0, QTableWidgetItem(contract.get('contract_number', '')))
            
            # ชื่อลูกค้า
            customer_name = f"{contract.get('first_name', '')} {contract.get('last_name', '')}"
            self.contracts_table.setItem(row, 1, QTableWidgetItem(customer_name))
            
            # สินค้า
            self.contracts_table.setItem(row, 2, QTableWidgetItem(contract.get('product_name', '')))
            
            # ยอดฝาก
            pawn_amount = contract.get('pawn_amount', 0)
            self.contracts_table.setItem(row, 3, QTableWidgetItem(f"{pawn_amount:,.2f}"))
            
            # วันที่เริ่ม
            start_date = contract.get('start_date', '')
            if start_date:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d/%m/%Y')
                    self.contracts_table.setItem(row, 4, QTableWidgetItem(formatted_date))
                except:
                    self.contracts_table.setItem(row, 4, QTableWidgetItem(start_date))
            else:
                self.contracts_table.setItem(row, 4, QTableWidgetItem(''))
            
            # วันที่สิ้นสุด
            end_date = contract.get('end_date', '')
            if end_date:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d/%m/%Y')
                    self.contracts_table.setItem(row, 5, QTableWidgetItem(formatted_date))
                except:
                    self.contracts_table.setItem(row, 5, QTableWidgetItem(end_date))
            else:
                self.contracts_table.setItem(row, 5, QTableWidgetItem(''))
            
            # สถานะ
            status = contract.get('status', 'active')
            status_text = 'ใช้งาน' if status == 'active' else 'สิ้นสุด'
            self.contracts_table.setItem(row, 6, QTableWidgetItem(status_text))
            
            # เก็บ contract_id ไว้ใน item
            self.contracts_table.item(row, 0).setData(Qt.UserRole, contract.get('id'))
    
    def filter_contracts(self):
        """กรองสัญญาตามคำค้นหา"""
        search_term = self.search_edit.text().strip()
        
        if not search_term:
            self.load_contracts()
            return
        
        try:
            # ค้นหาสัญญา
            contracts = self.db.search_contracts(search_term)
            self.display_contracts(contracts)
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")
    
    def on_selection_changed(self):
        """เมื่อเลือกแถวในตาราง"""
        selected_rows = self.contracts_table.selectionModel().selectedRows()
        self.generate_pdf_button.setEnabled(len(selected_rows) > 0)
    
    def get_selected_contract_id(self):
        """ดึง ID ของสัญญาที่เลือก"""
        selected_rows = self.contracts_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        item = self.contracts_table.item(row, 0)
        return item.data(Qt.UserRole) if item else None
    
    def generate_pdf(self):
        """สร้างใบขายฝาก PDF"""
        contract_id = self.get_selected_contract_id()
        if not contract_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกสัญญาที่ต้องการสร้าง PDF")
            return
        
        try:
            # ดึงข้อมูลสัญญาเพื่อแสดงเลขที่สัญญา
            contract_data = self.db.get_contract_by_id(contract_id)
            if not contract_data:
                QMessageBox.critical(self, "ผิดพลาด", "ไม่พบข้อมูลสัญญา")
                return
            
            # สร้าง PDF Generator
            pdf_generator = ContractPDFGenerator()
            
            # ให้ผู้ใช้เลือกตำแหน่งที่จะบันทึก
            output_path = pdf_generator.select_save_location(contract_data['contract_number'])
            
            if not output_path:
                return  # ผู้ใช้ยกเลิกการเลือกตำแหน่ง
            
            # สร้าง PDF
            result_path = pdf_generator.generate_contract_pdf(contract_id, output_path)
            
            if result_path:
                QMessageBox.information(self, "สำเร็จ", f"สร้างใบขายฝาก PDF สำเร็จ\nบันทึกที่: {result_path}")
                
                # เปิดไฟล์ PDF
                if os.path.exists(result_path):
                    try:
                        if platform.system() == "Darwin":  # macOS
                            subprocess.call(('open', result_path))
                        elif platform.system() == "Windows":
                            os.startfile(result_path)
                        else:  # Linux
                            subprocess.call(('xdg-open', result_path))
                    except:
                        pass  # ถ้าเปิดไม่ได้ก็ไม่เป็นไร
            else:
                QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาดในการสร้าง PDF")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการสร้าง PDF: {str(e)}")


# ฟังก์ชันสำหรับใช้งานจากภายนอก
def show_contract_pdf_dialog(parent=None):
    """แสดงหน้าต่างสร้าง PDF จากสัญญา"""
    dialog = ContractPDFDialog(parent)
    dialog.exec()


if __name__ == "__main__":
    # ทดสอบการทำงาน
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = ContractPDFDialog()
    dialog.show()
    
    sys.exit(app.exec())

