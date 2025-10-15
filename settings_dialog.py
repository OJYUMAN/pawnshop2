from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QGroupBox, QFormLayout, QTabWidget, QLineEdit, QTextEdit,
    QDoubleSpinBox, QCheckBox
)
from PySide6.QtCore import Qt
from language_manager import language_manager
from shop_config_loader import load_shop_config, save_shop_config

class SettingsDialog(QDialog):
    """หน้าต่างตั้งค่าแอปพลิเคชั่น"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(language_manager.get_text("settings_title"))
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        self.setModal(True)
        
        # ตั้งค่า UI
        self.setup_ui()
        
        # เชื่อมต่อสัญญาณ
        self.connect_signals()
        
        # โหลดการตั้งค่าปัจจุบัน
        self.load_current_settings()
        
        # เชื่อมต่อการเปลี่ยนแปลงภาษา
        language_manager.language_changed.connect(self.on_language_changed)
    
    def setup_ui(self):
        """ตั้งค่า UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # สร้าง TabWidget
        self.tab_widget = QTabWidget()
        
        # แท็บการตั้งค่าภาษา
        self.setup_language_tab()
        
        # แท็บการตั้งค่า PDF
        self.setup_pdf_tab()
        
        # แท็บการตั้งค่าดอกเบี้ย
        self.setup_interest_tab()
        
        layout.addWidget(self.tab_widget)
        
        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(language_manager.get_text("save"))
        self.save_button.setDefault(True)
        
        self.cancel_button = QPushButton(language_manager.get_text("cancel"))
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def setup_language_tab(self):
        """ตั้งค่าแท็บภาษา"""
        language_widget = QGroupBox()
        language_layout = QFormLayout(language_widget)
        
        # ComboBox สำหรับเลือกภาษา
        self.language_combo = QComboBox()
        self.language_combo.addItem("ไทย", "th")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("ລາວ", "lo")
        self.language_combo.addItem("မြန်မာ", "my")
        language_layout.addRow(language_manager.get_text("language"), self.language_combo)
        
        # เก็บข้อความภาษาต่างๆ สำหรับอัปเดต
        self.language_texts = {
            "th": {"th": "ไทย", "en": "English", "lo": "ລາວ", "my": "မြန်မာ"},
            "en": {"th": "Thai", "en": "English", "lo": "Lao", "my": "Myanmar"},
            "lo": {"th": "ไทย", "en": "English", "lo": "ລາວ", "my": "မြန်မာ"},
            "my": {"th": "ไทย", "en": "English", "lo": "ລາວ", "my": "မြန်မာ"}
        }
        
        self.tab_widget.addTab(language_widget, language_manager.get_text("language"))
    
    def setup_pdf_tab(self):
        """ตั้งค่าแท็บ PDF"""
        pdf_widget = QGroupBox()
        pdf_layout = QFormLayout(pdf_widget)
        
        # ฟิลด์ข้อมูลร้านค้า
        self.shop_name_edit = QLineEdit()
        self.shop_branch_edit = QLineEdit()
        self.shop_address_edit = QTextEdit()
        self.shop_address_edit.setMaximumHeight(80)
        self.tax_id_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.authorized_signer_edit = QLineEdit()
        self.buyer_signer_name_edit = QLineEdit()
        self.witness_name_edit = QLineEdit()
        
        # เพิ่มฟิลด์ลงในฟอร์ม
        pdf_layout.addRow(language_manager.get_text("shop_name"), self.shop_name_edit)
        pdf_layout.addRow(language_manager.get_text("shop_branch"), self.shop_branch_edit)
        pdf_layout.addRow(language_manager.get_text("shop_address"), self.shop_address_edit)
        pdf_layout.addRow(language_manager.get_text("tax_id"), self.tax_id_edit)
        pdf_layout.addRow(language_manager.get_text("shop_phone"), self.phone_edit)
        pdf_layout.addRow(language_manager.get_text("authorized_signer"), self.authorized_signer_edit)
        pdf_layout.addRow(language_manager.get_text("buyer_signer_name"), self.buyer_signer_name_edit)
        pdf_layout.addRow(language_manager.get_text("witness_name"), self.witness_name_edit)
        
        self.tab_widget.addTab(pdf_widget, language_manager.get_text("pdf_settings"))
    
    def setup_interest_tab(self):
        """ตั้งค่าแท็บดอกเบี้ย"""
        interest_widget = QGroupBox()
        interest_layout = QFormLayout(interest_widget)
        
        # อัตราดอกเบี้ยต่อเดือน
        self.interest_rate_spin = QDoubleSpinBox()
        self.interest_rate_spin.setRange(0.0, 100.0)
        self.interest_rate_spin.setSuffix(" %")
        self.interest_rate_spin.setDecimals(2)
        self.interest_rate_spin.setValue(10.0)  # ค่าเริ่มต้น 10%
        interest_layout.addRow(language_manager.get_text("interest_rate"), self.interest_rate_spin)
        
        # เปิด/ปิดการคำนวณอัตโนมัติ
        self.auto_calculate_checkbox = QCheckBox()
        self.auto_calculate_checkbox.setChecked(True)
        interest_layout.addRow("คำนวณอัตโนมัติ", self.auto_calculate_checkbox)
        
        # เชื่อมต่อสัญญาณ
        self.interest_rate_spin.valueChanged.connect(self.on_interest_rate_changed)
        self.auto_calculate_checkbox.toggled.connect(self.on_auto_calculate_toggled)
        
        self.tab_widget.addTab(interest_widget, "การตั้งค่าดอกเบี้ย")
    
    def connect_signals(self):
        """เชื่อมต่อสัญญาณ"""
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def load_current_settings(self):
        """โหลดการตั้งค่าปัจจุบัน"""
        # โหลดการตั้งค่าภาษา
        current_lang = language_manager.get_current_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # โหลดการตั้งค่า PDF
        shop_config = load_shop_config()
        self.shop_name_edit.setText(shop_config.get('name', ''))
        self.shop_branch_edit.setText(shop_config.get('branch', ''))
        self.shop_address_edit.setPlainText(shop_config.get('address', ''))
        self.tax_id_edit.setText(shop_config.get('tax_id', ''))
        self.phone_edit.setText(shop_config.get('phone', ''))
        self.authorized_signer_edit.setText(shop_config.get('authorized_signer', ''))
        self.buyer_signer_name_edit.setText(shop_config.get('buyer_signer_name', ''))
        self.witness_name_edit.setText(shop_config.get('witness_name', ''))
        
        # อัปเดตข้อความใน ComboBox ตามภาษาปัจจุบัน
        self.update_combo_texts()
        
        # โหลดการตั้งค่าดอกเบี้ย
        shop_config = load_shop_config()
        self.interest_rate_spin.setValue(shop_config.get('interest_rate', 10.0))
        self.auto_calculate_checkbox.setChecked(shop_config.get('auto_calculate_interest', True))
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        # บันทึกการตั้งค่าภาษา
        selected_language = self.language_combo.currentData()
        if selected_language != language_manager.get_current_language():
            language_manager.set_language(selected_language)
        
        # บันทึกการตั้งค่า PDF และดอกเบี้ย
        shop_data = {
            'name': self.shop_name_edit.text(),
            'branch': self.shop_branch_edit.text(),
            'address': self.shop_address_edit.toPlainText(),
            'tax_id': self.tax_id_edit.text(),
            'phone': self.phone_edit.text(),
            'authorized_signer': self.authorized_signer_edit.text(),
            'buyer_signer_name': self.buyer_signer_name_edit.text(),
            'witness_name': self.witness_name_edit.text(),
            'interest_rate': self.interest_rate_spin.value(),
            'auto_calculate_interest': self.auto_calculate_checkbox.isChecked()
        }
        save_shop_config(shop_data)
        
        # ปิดหน้าต่างตั้งค่า
        self.accept()
    
    def get_selected_language(self):
        """ดึงภาษาที่เลือก"""
        return self.language_combo.currentData()
    
    def on_language_changed(self, language):
        """จัดการการเปลี่ยนแปลงภาษา"""
        # อัปเดตชื่อหน้าต่าง
        self.setWindowTitle(language_manager.get_text("settings_title"))
        
        # อัปเดตข้อความในแท็บ
        self.tab_widget.setTabText(0, language_manager.get_text("language"))
        self.tab_widget.setTabText(1, language_manager.get_text("pdf_settings"))
        
        # อัปเดตข้อความในปุ่ม
        self.save_button.setText(language_manager.get_text("save"))
        self.cancel_button.setText(language_manager.get_text("cancel"))
        
        # อัปเดตข้อความใน ComboBox
        self.update_combo_texts()
    
    def on_interest_rate_changed(self, value):
        """จัดการการเปลี่ยนแปลงอัตราดอกเบี้ย"""
        # สามารถเพิ่มการตรวจสอบหรือการแจ้งเตือนได้ที่นี่
        pass
    
    def on_auto_calculate_toggled(self, checked):
        """จัดการการเปิด/ปิดการคำนวณอัตโนมัติ"""
        # สามารถเพิ่มการตรวจสอบหรือการแจ้งเตือนได้ที่นี่
        pass
    
    def update_combo_texts(self):
        """อัปเดตข้อความใน ComboBox"""
        # อัปเดตข้อความใน ComboBox ตามภาษาปัจจุบัน
        current_lang = language_manager.get_current_language()
        texts = self.language_texts.get(current_lang, self.language_texts["th"])
        
        self.language_combo.setItemText(0, texts["th"])
        self.language_combo.setItemText(1, texts["en"])
        self.language_combo.setItemText(2, texts["lo"])
        self.language_combo.setItemText(3, texts["my"])
