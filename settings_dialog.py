from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from language_manager import language_manager

class SettingsDialog(QDialog):
    """หน้าต่างตั้งค่าแอปพลิเคชั่น"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(language_manager.get_text("settings_title"))
        self.setMinimumSize(360, 200)
        self.resize(480, 260)
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
        
        # กลุ่มการตั้งค่าภาษา
        self.language_group = QGroupBox(language_manager.get_text("language"))
        language_layout = QFormLayout(self.language_group)
        
        # ComboBox สำหรับเลือกภาษา
        self.language_combo = QComboBox()
        self.language_combo.addItem("ไทย", "th")
        self.language_combo.addItem("English", "en")
        language_layout.addRow(language_manager.get_text("language"), self.language_combo)
        
        # เก็บข้อความภาษาไทยและอังกฤษสำหรับอัปเดต
        self.thai_text = "ไทย"
        self.english_text = "English"
        
        layout.addWidget(self.language_group)
        
        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(language_manager.get_text("save"))
        self.save_button.setDefault(True)
        
        self.cancel_button = QPushButton(language_manager.get_text("cancel"))
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def connect_signals(self):
        """เชื่อมต่อสัญญาณ"""
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def load_current_settings(self):
        """โหลดการตั้งค่าปัจจุบัน"""
        current_lang = language_manager.get_current_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # อัปเดตข้อความใน ComboBox ตามภาษาปัจจุบัน
        self.update_combo_texts()
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        # บันทึกการตั้งค่าภาษา
        selected_language = self.language_combo.currentData()
        if selected_language != language_manager.get_current_language():
            language_manager.set_language(selected_language)
        
        # ปิดหน้าต่างตั้งค่า
        self.accept()
    
    def get_selected_language(self):
        """ดึงภาษาที่เลือก"""
        return self.language_combo.currentData()
    
    def on_language_changed(self, language):
        """จัดการการเปลี่ยนแปลงภาษา"""
        # อัปเดตชื่อหน้าต่าง
        self.setWindowTitle(language_manager.get_text("settings_title"))
        
        # อัปเดตข้อความใน GroupBox
        self.language_group.setTitle(language_manager.get_text("language"))
        
        # อัปเดตข้อความในปุ่ม
        self.save_button.setText(language_manager.get_text("save"))
        self.cancel_button.setText(language_manager.get_text("cancel"))
        
        # อัปเดตข้อความใน ComboBox
        self.update_combo_texts()
    
    def update_combo_texts(self):
        """อัปเดตข้อความใน ComboBox"""
        # อัปเดตข้อความใน ComboBox ตามภาษาปัจจุบัน
        if language_manager.get_current_language() == "th":
            self.language_combo.setItemText(0, "ไทย")
            self.language_combo.setItemText(1, "English")
        else:
            self.language_combo.setItemText(0, "Thai")
            self.language_combo.setItemText(1, "English")
