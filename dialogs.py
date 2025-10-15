# -*- coding: utf-8 -*-
import re
import os
import io
import binascii
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QRadioButton, QCheckBox, QFileDialog, QScrollArea, QWidget, QProgressBar
)
from PySide6.QtCore import Qt, QDate, QThread, Signal
import tempfile
import shutil
from PySide6.QtGui import QPixmap, QIcon
from language_manager import language_manager
from datetime import datetime, timedelta
from language_manager import language_manager
from typing import Dict, Optional, List
from database import PawnShopDatabase
from utils import PawnShopUtils
from app_services import copy_product_image as svc_copy_product_image, send_line_message
from shop_config_loader import load_shop_config
from line_config import ENABLE_LINE_NOTIFICATION, SEND_RENEWAL_NOTIFICATION, SEND_REDEMPTION_NOTIFICATION, MESSAGE_TEMPLATE


# เพิ่มคลาสสำหรับการสแกนบัตรประชาชน
class ThaiIDCardScanner(QThread):
    """คลาสสำหรับการสแกนบัตรประชาชนในเธรดแยก"""
    card_data_ready = Signal(dict)  # สัญญาณเมื่อได้ข้อมูลบัตร
    error_occurred = Signal(str)    # สัญญาณเมื่อเกิดข้อผิดพลาด
    progress_updated = Signal(int)  # สัญญาณอัปเดตความคืบหน้า
    
    def __init__(self):
        super().__init__()
        self.card_data = {}
        
    def run(self):
        """รันการสแกนบัตรในเธรดแยก"""
        try:
            # Import smartcard modules
            from smartcard.System import readers
            from smartcard.util import toHexString
            from smartcard.Exceptions import NoCardException, CardConnectionException
            from smartcard.pcsc.PCSCExceptions import EstablishContextException
            
            # ตรวจสอบว่ามี card reader หรือไม่
            reader_list = readers()
            if not reader_list:
                self.error_occurred.emit("ไม่พบ card reader กรุณาตรวจสอบการเชื่อมต่อ")
                return
            
            # เลือก reader แรก
            reader = reader_list[0]
            self.progress_updated.emit(20)
            
            # ลองเชื่อมต่อกับบัตรหลายครั้ง
            connection = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    self.progress_updated.emit(30 + attempt * 10)
                    
                    # สร้างการเชื่อมต่อใหม่
                    if connection:
                        try:
                            connection.disconnect()
                        except:
                            pass
                    
                    connection = reader.createConnection()
                    
                    # ลองใช้โปรโตคอลต่างๆ
                    protocols = [None, 0, 1]  # Default, T0, T1
                    protocol_names = ["Default", "T0", "T1"]
                    
                    connected = False
                    for i, protocol in enumerate(protocols):
                        try:
                            if protocol is None:
                                connection.connect()
                            else:
                                connection.connect(protocol)
                            
                            # ถ้าเชื่อมต่อสำเร็จ
                            connected = True
                            print("เชื่อมต่อสำเร็จด้วยโปรโตคอล: {}".format(protocol_names[i]))
                            break
                            
                        except CardConnectionException as e:
                            print("โปรโตคอล {} ล้มเหลว: {}".format(protocol_names[i], e))
                            continue
                        except Exception as e:
                            print("ข้อผิดพลาดกับโปรโตคอล {}: {}".format(protocol_names[i], e))
                            continue
                    
                    if connected:
                        break
                    else:
                        print("ความพยายาม {} ล้มเหลว".format(attempt + 1))
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)  # รอ 2 วินาทีก่อนลองใหม่
                        continue
                
                except Exception as e:
                    print("ความพยายามเชื่อมต่อ {} ล้มเหลว: {}".format(attempt + 1, e))
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)
                    continue
            
            if not connection or not connected:
                self.error_occurred.emit("ไม่สามารถเชื่อมต่อกับบัตรได้หลังจากลองหลายครั้ง\nกรุณาตรวจสอบ:\n1. บัตรใส่ถูกต้องหรือไม่\n2. Card reader ทำงานปกติหรือไม่\n3. ลองใส่บัตรใหม่")
                return
            
            self.progress_updated.emit(60)
            
            # อ่านข้อมูลบัตร
            card_data = self.read_thai_id_card(connection)
            self.progress_updated.emit(80)
            
            # ปิดการเชื่อมต่อ
            try:
                connection.disconnect()
            except:
                pass
            
            self.progress_updated.emit(100)
            
            # ส่งข้อมูลที่ได้
            self.card_data_ready.emit(card_data)
            
        except NoCardException:
            self.error_occurred.emit("ไม่พบบัตร กรุณาใส่บัตรประชาชนใน card reader")
        except CardConnectionException as e:
            error_msg = "ไม่สามารถเชื่อมต่อกับบัตรได้: {str(e)}\n\nวิธีแก้ไข:\n"
            error_msg += "1. ตรวจสอบว่าบัตรใส่ในทิศทางที่ถูกต้อง\n"
            error_msg += "2. ลบและใส่บัตรใหม่\n"
            error_msg += "3. ทำความสะอาดหน้าสัมผัสของบัตร\n"
            error_msg += "4. ลองใช้ card reader อื่น\n"
            error_msg += "5. ตรวจสอบว่า card reader รองรับ PC/SC"
            self.error_occurred.emit(error_msg)
        except EstablishContextException:
            self.error_occurred.emit("ไม่สามารถสร้าง PC/SC context ได้\nกรุณาตรวจสอบว่า PC/SC service ทำงานอยู่")
        except ImportError:
            self.error_occurred.emit("ไม่พบโมดูล smartcard กรุณาติดตั้ง pyscard")
        except Exception as e:
            self.error_occurred.emit("เกิดข้อผิดพลาดที่ไม่คาดคิด: {str(e)}\nกรุณาลองใหม่อีกครั้ง")
    
    def read_thai_id_card(self, connection):
        """อ่านข้อมูลจากบัตรประชาชนไทย"""
        card_data = {}
        
        # ลองเลือก applet บัตรประชาชนหลายแบบ
        applet_commands = [
            # รุ่นเก่า
            [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01],
            # รุ่นใหม่
            [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x00],
            # รุ่นอื่นๆ
            [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x02],
            # รุ่นใหม่แบบไม่ต้องเลือก applet
            None
        ]
        
        applet_selected = False
        
        # ลองเลือก applet
        for i, cmd in enumerate(applet_commands):
            if cmd is None:
                # ไม่ต้องเลือก applet (สำหรับบัตรรุ่นใหม่บางรุ่น)
                print("ลองอ่านข้อมูลโดยไม่เลือก applet...")
                applet_selected = True
                break
            
            try:
                response, sw1, sw2 = connection.transmit(cmd)
                if sw1 == 0x90 and sw2 == 0x00:
                    print("เลือก applet สำเร็จ (รุ่น {i+1})")
                    applet_selected = True
                    break
                elif sw1 == 0x61:  # More data available
                    print("เลือก applet สำเร็จ (รุ่น {i+1}) - มีข้อมูลเพิ่มเติม")
                    applet_selected = True
                    break
                else:
                    print("เลือก applet รุ่น {i+1} ล้มเหลว: SW1={sw1:02X}, SW2={sw2:02X}")
            except Exception as e:
                print("ข้อผิดพลาดกับ applet รุ่น {i+1}: {e}")
                continue
        
        if not applet_selected:
            print("ไม่สามารถเลือก applet ได้ แต่จะลองอ่านข้อมูลโดยตรง")
        
        # คำสั่งสำหรับอ่านข้อมูลต่างๆ
        commands = {
            "CID": [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d],
            "TH_Fullname": [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64],
            "EN_Fullname": [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64],
            "Date_of_birth": [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08],
            "Gender": [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01],
            "Card_Issuer": [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64],
            "Issue_Date": [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08],
            "Expire_Date": [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08],
            "Address": [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]
        }
        
        # อ่านข้อมูลข้อความ
        for field_name, cmd in commands.items():
            try:
                data, sw1, sw2 = connection.transmit(cmd)
                
                if sw1 == 0x90 and sw2 == 0x00 and data:
                    # แปลงข้อมูลจาก TIS-620 เป็น Unicode
                    value = self.thai2unicode(data)
                    card_data[field_name] = value
                    print("✅ {field_name}: {value}")
                elif sw1 == 0x61:  # More data available
                    # ใช้คำสั่ง GET RESPONSE เพื่ออ่านข้อมูลเพิ่มเติม
                    print("📖 {field_name}: มีข้อมูลเพิ่มเติม (SW1=61, SW2={sw2:02X})")
                    response_data = self.get_response_data(connection, sw2)
                    if response_data:
                        value = self.thai2unicode(response_data)
                        card_data[field_name] = value
                        print("✅ {field_name}: {value} (จาก GET RESPONSE)")
                    else:
                        print("❌ {field_name}: ไม่สามารถอ่านข้อมูลเพิ่มเติมได้")
                        card_data[field_name] = ""
                else:
                    print("❌ {field_name}: อ่านไม่สำเร็จ (SW1={sw1:02X}, SW2={sw2:02X})")
                    card_data[field_name] = ""
                    
            except Exception as e:
                print("❌ {field_name}: เกิดข้อผิดพลาด - {e}")
                card_data[field_name] = ""
        
        # ลองใช้คำสั่งแบบอื่นสำหรับบัตรรุ่นใหม่
        if not any(card_data.values()):
            print("ลองใช้คำสั่งแบบอื่นสำหรับบัตรรุ่นใหม่...")
            self.try_alternative_commands(connection, card_data)
        
        # อ่านรูปภาพ (ถ้ามี)
        try:
            photo_data = self.read_photo_data(connection)
            if photo_data:
                card_data["photo"] = photo_data
                print("✅ อ่านรูปภาพสำเร็จ")
        except Exception as e:
            print("❌ อ่านรูปภาพไม่สำเร็จ: {e}")
        
        return card_data
    
    def get_response_data(self, connection, sw2):
        """ใช้คำสั่ง GET RESPONSE เพื่ออ่านข้อมูลเพิ่มเติม"""
        try:
            # คำสั่ง GET RESPONSE
            get_response_cmd = [0x00, 0xC0, 0x00, 0x00, sw2]
            response_data, sw1, sw2 = connection.transmit(get_response_cmd)
            
            if sw1 == 0x90 and sw2 == 0x00 and response_data:
                return response_data
            else:
                print("GET RESPONSE ล้มเหลว: SW1={sw1:02X}, SW2={sw2:02X}")
                return None
                
        except Exception as e:
            print("ข้อผิดพลาดในการใช้ GET RESPONSE: {e}")
            return None
    
    def try_alternative_commands(self, connection, card_data):
        """ลองใช้คำสั่งแบบอื่นสำหรับบัตรรุ่นใหม่"""
        # คำสั่งแบบอื่นสำหรับบัตรรุ่นใหม่
        alt_commands = {
            "CID_Alt": [0x80, 0xb0, 0x00, 0x04, 0x01, 0x00, 0x0d],
            "Name_Alt": [0x80, 0xb0, 0x00, 0x11, 0x01, 0x00, 0x64],
            "CID_Direct": [0x80, 0xca, 0x00, 0x04, 0x00],
            "Name_Direct": [0x80, 0xca, 0x00, 0x11, 0x00]
        }
        
        for field_name, cmd in alt_commands.items():
            try:
                data, sw1, sw2 = connection.transmit(cmd)
                
                if sw1 == 0x90 and sw2 == 0x00 and data:
                    value = self.thai2unicode(data)
                    if value and value.strip():
                        # กำหนดชื่อฟิลด์ที่เหมาะสม
                        if "CID" in field_name:
                            card_data["CID"] = value
                            print("✅ CID (Alt): {value}")
                        elif "Name" in field_name:
                            card_data["TH_Fullname"] = value
                            print("✅ ชื่อ (Alt): {value}")
                        break
                        
            except Exception as e:
                print("❌ {field_name}: เกิดข้อผิดพลาด - {e}")
                continue
    
    def thai2unicode(self, data):
        """แปลงข้อมูลจาก TIS-620 เป็น Unicode"""
        try:
            if not data:
                return ""
            result = bytes(data).decode('tis-620', errors='ignore').replace("#", " ")
            return result.strip()
        except:
            return ""
    
    def read_photo_data(self, connection):
        """อ่านข้อมูลรูปภาพจากบัตร"""
        photo_parts = []
        
        # สร้างคำสั่งสำหรับอ่านรูปภาพ 20 ส่วน
        for i in range(20):
            if i < 10:
                cmd = [0x80, 0xb0, 0x00, 0x7B + i, 0x02, 0x00, 0xFF]
            else:
                cmd = [0x80, 0xb0, 0x01, 0x7B - (i - 10), 0x02, 0x00, 0xFF]
            
            try:
                data, sw1, sw2 = connection.transmit(cmd)
                if sw1 == 0x90 and sw2 == 0x00 and data:
                    photo_parts.append(data)
            except:
                continue
        
        # รวมข้อมูลรูปภาพ
        if photo_parts:
            photo_data = b''
            for part in photo_parts:
                photo_data += bytes(part)
            return photo_data
        
        return None

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer_data=None):
        super().__init__(parent)
        # ใช้ database connection จาก parent window
        if hasattr(parent, 'db') and parent.db is not None:
            self.db = parent.db
        else:
            self.db = PawnShopDatabase()
        self.customer_data = customer_data
        self.card_scanner = None
        self.setup_ui()
        if customer_data:
            self.load_customer_data()
        else:
            # สร้างรหัสลูกค้าอัตโนมัติเมื่อเพิ่มลูกค้าใหม่
            self.generate_customer_code()
    
    def setup_ui(self):
        self.setWindowTitle("ข้อมูลลูกค้า")
        self.setModal(True)
        self.resize(700, 600)
        
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
        
        # เพิ่มปุ่มสแกนบัตรประชาชน
        scan_card_button = QPushButton("สแกนบัตรประชาชน")
        scan_card_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        scan_card_button.clicked.connect(self.scan_id_card)
        
        # เพิ่ม progress bar สำหรับการสแกน
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        self.scan_progress.setRange(0, 100)
        
        basic_layout.addWidget(QLabel("รหัสลูกค้า:"), 0, 0)
        basic_layout.addWidget(self.customer_code_edit, 0, 1)
        basic_layout.addWidget(generate_code_button, 0, 2)
        basic_layout.addWidget(QLabel("ชื่อ:"), 1, 0)
        basic_layout.addWidget(self.first_name_edit, 1, 1)
        basic_layout.addWidget(QLabel("นามสกุล:"), 2, 0)
        basic_layout.addWidget(self.last_name_edit, 2, 1)
        basic_layout.addWidget(QLabel("เลขบัตรประชาชน:"), 3, 0)
        basic_layout.addWidget(self.id_card_edit, 3, 1)
        basic_layout.addWidget(scan_card_button, 3, 2)
        basic_layout.addWidget(self.scan_progress, 4, 0, 1, 3)
        basic_layout.addWidget(QLabel("เบอร์โทรศัพท์:"), 5, 0)
        basic_layout.addWidget(self.phone_edit, 5, 1)
        
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
    
    def scan_id_card(self):
        """เริ่มการสแกนบัตรประชาชน"""
        try:
            # ตรวจสอบสถานะ card reader ก่อน
            if not self.check_card_reader_status():
                return
            
            # แสดง progress bar
            self.scan_progress.setVisible(True)
            self.scan_progress.setValue(0)
            
            # สร้างและเริ่มการสแกนในเธรดแยก
            self.card_scanner = ThaiIDCardScanner()
            self.card_scanner.card_data_ready.connect(self.on_card_data_ready)
            self.card_scanner.error_occurred.connect(self.on_scan_error)
            self.card_scanner.progress_updated.connect(self.scan_progress.setValue)
            
            self.card_scanner.start()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "ไม่สามารถเริ่มการสแกนได้: {str(e)}")
            self.scan_progress.setVisible(False)
    
    def check_card_reader_status(self):
        """ตรวจสอบสถานะ card reader"""
        try:
            from smartcard.System import readers
            
            reader_list = readers()
            if not reader_list:
                QMessageBox.warning(self, "แจ้งเตือน", 
                    "ไม่พบ card reader\n\nกรุณาตรวจสอบ:\n"
                    "1. Card reader เชื่อมต่อ USB หรือไม่\n"
                    "2. Driver ติดตั้งแล้วหรือไม่\n"
                    "3. PC/SC service ทำงานอยู่หรือไม่")
                return False
            
            # ตรวจสอบว่ามีบัตรใน reader หรือไม่
            try:
                reader = reader_list[0]
                connection = reader.createConnection()
                connection.connect()
                connection.disconnect()
                return True
            except Exception as e:
                if "No card" in str(e) or "Card is unresponsive" in str(e):
                    QMessageBox.information(self, "แจ้งเตือน", 
                        "ไม่พบบัตรใน card reader\n\nกรุณาใส่บัตรประชาชนก่อนคลิกสแกน")
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", 
                        "ไม่สามารถเชื่อมต่อกับ card reader ได้: {str(e)}\n\n"
                        "กรุณาตรวจสอบการเชื่อมต่อและ driver")
                return False
                
        except ImportError:
            QMessageBox.critical(self, "ผิดพลาด", 
                "ไม่พบโมดูล smartcard\n\nกรุณาติดตั้งด้วยคำสั่ง:\npip install pyscard")
            return False
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาดในการตรวจสอบ card reader: {str(e)}")
            return False
    
    def on_card_data_ready(self, card_data):
        """เมื่อได้ข้อมูลบัตรแล้ว"""
        try:
            # ซ่อน progress bar
            self.scan_progress.setVisible(False)
            
            # แสดงข้อมูลที่ได้
            info_text = "ข้อมูลที่ได้จากบัตร:\n"
            for key, value in card_data.items():
                if key != "photo" and value:  # ไม่แสดงรูปภาพ
                    info_text += "{key}: {value}\n"
            
            # ถามว่าต้องการใช้ข้อมูลนี้หรือไม่
            reply = QMessageBox.question(
                self, 
                "ข้อมูลบัตรประชาชน", 
                "{info_text}\nต้องการใช้ข้อมูลนี้หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # กรอกข้อมูลลงในฟอร์ม
                self.fill_form_with_card_data(card_data)
                
                # บันทึกรูปภาพถ้ามี
                if "photo" in card_data and card_data["photo"]:
                    self.save_card_photo(card_data["photo"], card_data.get("CID", "unknown"))
            
            QMessageBox.information(self, "สำเร็จ", "อ่านข้อมูลบัตรประชาชนเรียบร้อย")
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาดในการประมวลผลข้อมูล: {str(e)}")
        finally:
            self.scan_progress.setVisible(False)
    
    def on_scan_error(self, error_message):
        """เมื่อเกิดข้อผิดพลาดในการสแกน"""
        self.scan_progress.setVisible(False)
        QMessageBox.warning(self, "แจ้งเตือน", error_message)
    
    def fill_form_with_card_data(self, card_data):
        """กรอกข้อมูลจากบัตรลงในฟอร์ม"""
        try:
            # กรอกข้อมูลพื้นฐาน
            if card_data.get("CID"):
                self.id_card_edit.setText(card_data["CID"])
            
            if card_data.get("TH_Fullname"):
                # แยกชื่อและนามสกุลอย่างถูกต้อง
                full_name = card_data["TH_Fullname"].strip()
                
                # ตรวจสอบรูปแบบชื่อไทย
                if "นางสาว" in full_name:
                    # กรณีมีคำนำหน้า "นางสาว"
                    prefix = "นางสาว"
                    name_without_prefix = full_name.replace("นางสาว", "").strip()
                elif "นาง" in full_name:
                    # กรณีมีคำนำหน้า "นาง"
                    prefix = "นาง"
                    name_without_prefix = full_name.replace("นาง", "").strip()
                elif "นาย" in full_name:
                    # กรณีมีคำนำหน้า "นาย"
                    prefix = "นาย"
                    name_without_prefix = full_name.replace("นาย", "").strip()
                else:
                    # กรณีไม่มีคำนำหน้า
                    prefix = ""
                    name_without_prefix = full_name
                
                # แยกชื่อและนามสกุล
                name_parts = name_without_prefix.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:])
                    # รวมคำนำหน้าเข้ากับชื่อ
                    if prefix:
                        self.first_name_edit.setText("{prefix} {first_name}")
                    else:
                        self.first_name_edit.setText(first_name)
                    self.last_name_edit.setText(last_name)
                else:
                    if prefix:
                        self.first_name_edit.setText("{prefix} {full_name}")
                    else:
                        self.first_name_edit.setText(full_name)
                    self.last_name_edit.setText("")
            
            # กรอกข้อมูลที่อยู่อย่างถูกต้อง
            if card_data.get("Address"):
                address = card_data["Address"].strip()
                print("ที่อยู่จากบัตร: {address}")
                
                # แยกที่อยู่เป็นส่วนๆ
                address_parts = self.parse_thai_address(address)
                
                # กรอกข้อมูลที่อยู่ในฟอร์ม
                if address_parts.get("house_number"):
                    self.house_number_edit.setText(address_parts["house_number"])
                
                if address_parts.get("street"):
                    self.street_edit.setText(address_parts["street"])
                
                if address_parts.get("subdistrict"):
                    self.subdistrict_edit.setText(address_parts["subdistrict"])
                
                if address_parts.get("district"):
                    self.district_edit.setText(address_parts["district"])
                
                if address_parts.get("province"):
                    self.province_edit.setText(address_parts["province"])
                
                # เก็บที่อยู่ที่แยกไม่ได้ในรายละเอียดอื่นๆ
                remaining_address = address_parts.get("remaining", "")
                if remaining_address:
                    self.other_details_edit.setPlainText("ที่อยู่เพิ่มเติม: {remaining_address}")
            
        except Exception as e:
            print("Error filling form: {e}")
    
    def parse_thai_address(self, address):
        """แยกที่อยู่ไทยเป็นส่วนๆ"""
        address_parts = {}
        
        try:
            # ลบช่องว่างที่ไม่จำเป็น
            address = " ".join(address.split())
            
            # แยกบ้านเลขที่ (มักอยู่ต้นข้อความ)
            house_match = re.match(r'^(\d+)\s*', address)
            if house_match:
                address_parts["house_number"] = house_match.group(1)
                address = address[house_match.end():].strip()
            
            # แยกจังหวัด (มักอยู่ท้ายข้อความ)
            provinces = [
                "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา",
                "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก",
                "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน",
                "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา",
                "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "พะเยา", "ภูเก็ต",
                "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยะลา", "ยโสธร", "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี",
                "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ",
                "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี",
                "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อุดรธานี", "อุทัยธานี", "อุตรดิตถ์", "อุบลราชธานี",
                "อำนาจเจริญ"
            ]
            
            for province in provinces:
                if province in address:
                    address_parts["province"] = province
                    # ตัดจังหวัดออกจากที่อยู่
                    address = address.replace(province, "").strip()
                    break
            
            # แยกเขต/อำเภอ (มักมีคำว่า "เขต" หรือ "อำเภอ")
            district_match = re.search(r'(เขต|อำเภอ)\s*([^\s]+)', address)
            if district_match:
                district_type = district_match.group(1)
                district_name = district_match.group(2)
                address_parts["district"] = "{district_type}{district_name}"
                # ตัดเขต/อำเภอออกจากที่อยู่
                address = address.replace(district_match.group(0), "").strip()
            
            # แยกแขวง/ตำบล (มักมีคำว่า "แขวง" หรือ "ตำบล")
            subdistrict_match = re.search(r'(แขวง|ตำบล)\s*([^\s]+)', address)
            if subdistrict_match:
                subdistrict_type = subdistrict_match.group(1)
                subdistrict_name = subdistrict_match.group(2)
                address_parts["subdistrict"] = "{subdistrict_type}{subdistrict_name}"
                # ตัดแขวง/ตำบลออกจากที่อยู่
                address = address.replace(subdistrict_match.group(0), "").strip()
            
            # แยกถนน/ซอย
            street_match = re.search(r'(ถนน|ซอย)\s*([^\s]+)', address)
            if street_match:
                street_type = street_match.group(1)
                street_name = street_match.group(2)
                address_parts["street"] = "{street_type}{street_name}"
                # ตัดถนน/ซอยออกจากที่อยู่
                address = address.replace(street_match.group(0), "").strip()
            
            # ที่เหลือเก็บใน remaining
            if address.strip():
                address_parts["remaining"] = address.strip()
            
            print("แยกที่อยู่: {address_parts}")
            
        except Exception as e:
            print("Error parsing address: {e}")
            # หากแยกไม่ได้ ให้เก็บทั้งหมดใน remaining
            address_parts["remaining"] = address
        
        return address_parts
    
    def save_card_photo(self, photo_data, cid):
        """บันทึกรูปภาพจากบัตร"""
        try:
            if not os.path.exists("product_images"):
                os.makedirs("product_images")
            
            photo_filename = "product_images/{cid}.jpg"
            with open(photo_filename, "wb") as f:
                f.write(photo_data)
            
            print("บันทึกรูปภาพเรียบร้อย: {photo_filename}")
            
        except Exception as e:
            print("Error saving photo: {e}")
    
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
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถสร้างรหัสลูกค้าได้: {str(e)}")
    
    def clean_input_data(self, text):
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
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถสร้างรหัสลูกค้าได้: {str(e)}")
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
                    # อัปเดตข้อมูลใน dialog เพื่อให้ภายนอกสามารถอ่านได้
                    updated = dict(customer_data)
                    updated['id'] = self.customer_data['id']
                    self.customer_data = updated
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
                # เก็บข้อมูลลูกค้าที่เพิ่งบันทึกไว้ใน dialog
                self.customer_data = dict(customer_data)
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
        self.resize(600, 700)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลสินค้า
        product_group = QGroupBox("ข้อมูลสินค้า")
        product_layout = QGridLayout(product_group)
        product_layout.setSpacing(10)
        
        # ฟิลด์ใหม่ตามรูปภาพ
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("ชื่อสินค้า เช่น iPhone 15 Pro Max")
        
        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText("Apple, Samsung, Oppo")
        
        self.imei1_edit = QLineEdit()
        self.imei1_edit.setPlaceholderText("เลข IMEI เครื่อง")
        
        self.imei2_edit = QLineEdit()
        self.imei2_edit.setPlaceholderText("เลข IMEI 2 (ถ้ามี)")
        
        self.serial_edit = QLineEdit()
        self.serial_edit.setPlaceholderText("เลข Serial Number")
        
        self.condition_edit = QTextEdit()
        self.condition_edit.setMaximumHeight(80)
        self.condition_edit.setPlaceholderText("เช่น ใหม่มาก, มีรอยขนแมวเล็กน้อย, จอแตกมุมขวาบน")
        
        self.accessories_edit = QTextEdit()
        self.accessories_edit.setMaximumHeight(80)
        self.accessories_edit.setPlaceholderText("เช่น กล่อง, สายชาร์จแท้, อแดปเตอร์, หูฟัง")
        
        # ฟิลด์ที่ยังคงใช้
        self.other_details_edit = QTextEdit()
        self.other_details_edit.setMaximumHeight(80)

        # ตัวแปรสำหรับจัดการรูปภาพ
        self._image_source_path = ""
        
        # จัดเรียงฟิลด์ตามรูปภาพ
        from language_manager import language_manager
        
        product_layout.addWidget(QLabel("ชื่อสินค้า:"), 0, 0)
        product_layout.addWidget(self.name_edit, 0, 1)
        
        product_layout.addWidget(QLabel("ยี่ห้อ:"), 1, 0)
        product_layout.addWidget(self.brand_edit, 1, 1)
        
        product_layout.addWidget(QLabel("IMEI 1:"), 2, 0)
        product_layout.addWidget(self.imei1_edit, 2, 1)
        
        product_layout.addWidget(QLabel("IMEI 2 (ถ้ามี):"), 3, 0)
        product_layout.addWidget(self.imei2_edit, 3, 1)
        
        product_layout.addWidget(QLabel("Serial Number:"), 4, 0)
        product_layout.addWidget(self.serial_edit, 4, 1)
        
        product_layout.addWidget(QLabel("สภาพเครื่อง:"), 5, 0)
        product_layout.addWidget(self.condition_edit, 5, 1)
        
        product_layout.addWidget(QLabel("อุปกรณ์ที่มาพร้อมเครื่อง:"), 6, 0)
        product_layout.addWidget(self.accessories_edit, 6, 1)
        
        # ฟิลด์ที่ยังคงใช้
        product_layout.addWidget(QLabel("รูปภาพสินค้า:"), 7, 0)
        
        # สร้าง layout สำหรับรูปภาพและปุ่มอัปโหลด
        image_container = QVBoxLayout()
        
        # แสดงรูปภาพตัวอย่าง
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(160, 120)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid #CCC; background: #FAFAFA;")
        self.image_preview.setText("ไม่มีรูปภาพ")
        image_container.addWidget(self.image_preview)
        
        # ปุ่มอัปโหลดรูปภาพ
        self.image_browse_btn = QPushButton("เลือกรูปภาพ...")
        self.image_browse_btn.clicked.connect(self.browse_product_image)
        self.image_browse_btn.setMaximumWidth(160)
        image_container.addWidget(self.image_browse_btn)
        
        # ฟิลด์ path (ซ่อนไว้)
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setReadOnly(True)
        self.image_path_edit.hide()  # ซ่อนฟิลด์ path
        
        # เพิ่ม container ลงใน layout
        image_widget = QWidget()
        image_widget.setLayout(image_container)
        product_layout.addWidget(image_widget, 7, 1)
        
        layout.addWidget(product_group)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        save_button = QPushButton(language_manager.get_text("save"))
        cancel_button = QPushButton(language_manager.get_text("cancel"))
        
        save_button.clicked.connect(self.save_product)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def load_product_data(self):
        """โหลดข้อมูลสินค้า"""
        # ฟิลด์ใหม่ตามรูปภาพ
        self.name_edit.setText(self.product_data.get('name', ''))
        self.brand_edit.setText(self.product_data.get('brand', ''))
        self.imei1_edit.setText(self.product_data.get('imei1', ''))
        self.imei2_edit.setText(self.product_data.get('imei2', ''))
        self.serial_edit.setText(self.product_data.get('serial_number', ''))
        self.condition_edit.setPlainText(self.product_data.get('condition', ''))
        self.accessories_edit.setPlainText(self.product_data.get('accessories', ''))
        
        # โหลดรูปภาพหากมี
        image_path = self.product_data.get('image_path', '')
        if image_path and os.path.exists(image_path):
            self.image_path_edit.setText(image_path)
            pix = QPixmap(image_path)
            if not pix.isNull():
                self.image_preview.setPixmap(pix.scaled(self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_path_edit.clear()
            self.image_preview.setText("ไม่มีรูปภาพ")
    
    def save_product(self):
        """บันทึกข้อมูลสินค้า"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อสินค้า")
            return
        
        
        product_data = {
            'name': self.name_edit.text().strip(),
            'brand': self.brand_edit.text().strip(),
            'imei1': self.imei1_edit.text().strip(),
            'imei2': self.imei2_edit.text().strip(),
            'serial_number': self.serial_edit.text().strip(),
            'condition': self.condition_edit.toPlainText().strip(),
            'accessories': self.accessories_edit.toPlainText().strip()
        }
        # จัดการคัดลอกรูปภาพไปยังโฟลเดอร์ของโปรแกรม
        try:
            source_path = getattr(self, '_image_source_path', '') or self.image_path_edit.text().strip()
            if source_path:
                new_path = svc_copy_product_image(source_path)
                product_data['image_path'] = new_path
        except Exception as _e:
            # ถ้าคัดลอกไม่ได้ ให้ข้ามและใช้ path เดิม (หรือว่าง)
            if self.image_path_edit.text().strip():
                product_data['image_path'] = self.image_path_edit.text().strip()
        
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
                    # อัปเดตข้อมูลใน dialog เพื่อให้ภายนอกสามารถอ่านได้
                    updated = dict(product_data)
                    updated['id'] = self.product_data['id']
                    self.product_data = updated
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
                # เก็บข้อมูลสินค้าไว้ใน dialog
                self.product_data = dict(product_data)
                QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลสินค้าเรียบร้อย")
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))

    def browse_product_image(self):
        """เลือกไฟล์รูปภาพสินค้าและแสดงตัวอย่าง"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกรูปภาพสินค้า",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
            options=options
        )
        if file_name:
            self._image_source_path = file_name
            self.image_path_edit.setText(file_name)
            pix = QPixmap(file_name)
            if not pix.isNull():
                self.image_preview.setPixmap(pix.scaled(self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_preview.setText("ดูตัวอย่างไม่ได้")

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
        
        contract_layout.addWidget(QLabel("เลขที่สัญญา:"), 0, 0)
        contract_layout.addWidget(self.contract_number_label, 0, 1)
        contract_layout.addWidget(QLabel("ชื่อลูกค้า:"), 1, 0)
        contract_layout.addWidget(self.customer_name_label, 1, 1)
        contract_layout.addWidget(QLabel("ยอดฝาก:"), 2, 0)
        contract_layout.addWidget(self.pawn_amount_label, 2, 1)
        
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
        self.setWindowTitle(language_manager.get_text("redemption_title"))
        self.setModal(True)
        self.resize(600, 700)
        
        # ใช้สีพื้นหลังเหมือนรูปภาพ
        self.setStyleSheet("""
            QDialog {
                background-color: #F5E6D3;
            }
            QGroupBox {
                font-weight: bold;
                color: #8B4513;
                border: 2px solid #D2691E;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                margin-left: 15px;
                background-color: #F5E6D3;
                color: #8B4513;
            }
            QLabel {
                color: #8B4513;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox {
                border: 2px solid #D2691E;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                color: #8B4513;
            }
            QPushButton {
                background-color: #D2691E;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #CD853F;
            }
            QPushButton:pressed {
                background-color: #A0522D;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # หัวข้อหลัก
        title_label = QLabel(language_manager.get_text("redemption_title"))
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #8B4513;
            text-align: center;
            margin: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # ข้อมูลวันที่และจำนวนวัน
        date_group = QGroupBox(language_manager.get_text("redemption_date_group"))
        date_layout = QGridLayout(date_group)
        
        self.deposit_date_edit = QDateEdit()
        self.deposit_date_edit.setDate(QDate.currentDate())
        self.deposit_date_edit.setCalendarPopup(True)
        
        self.redemption_date_edit = QDateEdit()
        self.redemption_date_edit.setDate(QDate.currentDate())
        self.redemption_date_edit.setCalendarPopup(True)
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setCalendarPopup(True)
        
        self.total_days_label = QLabel("0")
        self.total_days_label.setStyleSheet("""
            background-color: #FFD700;
            border: 2px solid #D2691E;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            color: #8B4513;
        """)
        
        date_layout.addWidget(QLabel(language_manager.get_text("redemption_deposit_or_extend")), 0, 0)
        date_layout.addWidget(self.deposit_date_edit, 0, 1)
        date_layout.addWidget(QLabel(language_manager.get_text("redemption_date")), 1, 0)
        date_layout.addWidget(self.redemption_date_edit, 1, 1)
        date_layout.addWidget(QLabel(language_manager.get_text("redemption_due_date")), 2, 0)
        date_layout.addWidget(self.due_date_edit, 2, 1)
        date_layout.addWidget(QLabel(language_manager.get_text("redemption_total_days")), 3, 0)
        date_layout.addWidget(self.total_days_label, 3, 1)
        
        layout.addWidget(date_group)
        
        # ข้อมูลจำนวนเงิน
        amount_group = QGroupBox(language_manager.get_text("redemption_amount_group"))
        amount_layout = QGridLayout(amount_group)
        
        self.principal_amount_label = QLabel("0")
        self.principal_amount_label.setStyleSheet("""
            background-color: white;
            border: 2px solid #D2691E;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            color: #8B4513;
        """)
        
        
        self.penalty_amount_label = QLabel("0")
        self.penalty_amount_label.setStyleSheet("""
            background-color: white;
            border: 2px solid #D2691E;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            color: #8B4513;
        """)
        
        self.discount_amount_label = QLabel("0")
        self.discount_amount_label.setStyleSheet("""
            background-color: white;
            border: 2px solid #D2691E;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            color: #8B4513;
        """)
        
        self.total_amount_label = QLabel("0.00 บาท")
        self.total_amount_label.setStyleSheet("""
            background-color: #FFD700;
            border: 2px solid #D2691E;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            color: #8B4513;
            font-size: 16px;
        """)
        
        amount_layout.addWidget(QLabel(language_manager.get_text("redemption_principal")), 0, 0)
        amount_layout.addWidget(self.principal_amount_label, 0, 1)
        amount_layout.addWidget(QLabel(language_manager.get_text("redemption_penalty")), 1, 0)
        amount_layout.addWidget(self.penalty_amount_label, 1, 1)
        amount_layout.addWidget(QLabel(language_manager.get_text("redemption_discount")), 2, 0)
        amount_layout.addWidget(self.discount_amount_label, 2, 1)
        amount_layout.addWidget(QLabel(language_manager.get_text("redemption_total")), 3, 0)
        amount_layout.addWidget(self.total_amount_label, 3, 1)
        
        layout.addWidget(amount_group)
        
        # คำถามยืนยัน
        confirm_label = QLabel(language_manager.get_text("redemption_confirm"))
        confirm_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #8B4513;
            text-align: center;
            margin: 20px;
        """)
        confirm_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(confirm_label)
        
        # ปุ่มยืนยัน
        button_layout = QHBoxLayout()
        
        # ปุ่มตกลง
        yes_button = QPushButton(language_manager.get_text("ok"))
        yes_button.setIcon(self.create_fire_icon())
        yes_button.clicked.connect(self.confirm_redemption)
        
        # ปุ่มไม่ใช่ (มีไอคอนถังขยะ)
        no_button = QPushButton(language_manager.get_text("no"))
        no_button.setIcon(self.create_trash_icon())
        no_button.clicked.connect(self.reject)
        
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        layout.addLayout(button_layout)
        
        # เชื่อมต่อสัญญาณการเปลี่ยนแปลงวันที่
        self.deposit_date_edit.dateChanged.connect(self.calculate_total_days)
        self.redemption_date_edit.dateChanged.connect(self.calculate_total_days)
        self.due_date_edit.dateChanged.connect(self.calculate_total_days)

        # ผูกภาษา
        language_manager.language_changed.connect(self.apply_language)
        self.apply_language()

    def apply_language(self, *_args):
        self.setWindowTitle(language_manager.get_text("redemption_title"))
    
    def create_fire_icon(self):
        """สร้างไอคอนไฟสำหรับปุ่มใช่"""
        # สร้างไอคอนแบบง่ายๆ ด้วยข้อความ
        return QIcon()
    
    def create_document_icon(self):
        """สร้างไอคอนเอกสารสำหรับปุ่มสร้างสัญญา (ยังคงไว้เพื่อความเข้ากันได้)"""
        return QIcon()
    
    def create_trash_icon(self):
        """สร้างไอคอนถังขยะสำหรับปุ่มไม่ใช่"""
        # สร้างไอคอนแบบง่ายๆ ด้วยข้อความ
        return QIcon()
    
    def calculate_total_days(self):
        """คำนวณจำนวนวันที่ฝากไว้"""
        try:
            deposit_date = self.deposit_date_edit.date()
            redemption_date = self.redemption_date_edit.date()
            
            # คำนวณจำนวนวันระหว่างวันที่รับฝากกับวันที่ไถ่คืน
            days = deposit_date.daysTo(redemption_date)
            if days < 0:
                days = 0
            
            self.total_days_label.setText(str(days))
            
            # คำนวณค่าต่างๆ ใหม่
            self.calculate_amounts()
            
        except Exception as e:
            print("Error calculating days: {e}")
    
    def calculate_amounts(self):
        """คำนวณจำนวนเงินต่างๆ"""
        try:
            # ดึงข้อมูลจากสัญญา
            if not self.contract_data:
                return
            
            # ใช้ยอดไถ่คืนที่ตั้งไว้ในสัญญาเดิมแทนที่จะใช้แค่ยอดเงินต้น
            principal = self.contract_data.get('total_redemption', self.contract_data.get('pawn_amount', 0))
            
            # คำนวณค่าปรับ (ถ้าเกินกำหนด)
            penalty = 0
            if self.redemption_date_edit.date() > self.due_date_edit.date():
                overdue_days = self.due_date_edit.date().daysTo(self.redemption_date_edit.date())
                penalty = overdue_days * 10  # ค่าปรับวันละ 10 บาท
            
            # คำนวณส่วนลด (ถ้ามี)
            discount = 0
            
            # คำนวณยอดรวม
            total = principal + penalty - discount
            
            # แสดงผลลัพธ์
            self.principal_amount_label.setText(f"{principal:,.2f} บาท")
            self.penalty_amount_label.setText(f"{penalty:,.2f} บาท")
            self.discount_amount_label.setText(f"{discount:,.2f} บาท")
            self.total_amount_label.setText(f"{total:,.2f} บาท")
            
        except Exception as e:
            print("Error calculating amounts: {e}")
    
    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if not self.contract_data:
            return
        
        try:
            # ตั้งค่าวันที่
            if 'start_date' in self.contract_data:
                start_date = QDate.fromString(self.contract_data['start_date'], "yyyy-MM-dd")
                self.deposit_date_edit.setDate(start_date)
            
            if 'end_date' in self.contract_data:
                end_date = QDate.fromString(self.contract_data['end_date'], "yyyy-MM-dd")
                self.due_date_edit.setDate(end_date)
            
            # ตั้งค่าวันที่ไถ่คืนเป็นวันปัจจุบัน
            self.redemption_date_edit.setDate(QDate.currentDate())
            
            # คำนวณจำนวนวันและจำนวนเงิน
            self.calculate_total_days()
            
        except Exception as e:
            print("Error loading contract data: {e}")
    
    def confirm_redemption(self):
        """ยืนยันการไถ่คืน"""
        try:
            if not self.contract_data:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
                return
            
            # สร้างข้อมูลการไถ่คืน
            redemption_data = {
                'contract_id': self.contract_data['id'],
                'redemption_date': self.redemption_date_edit.date().toString("yyyy-MM-dd"),
                'redemption_amount': float(self.total_amount_label.text().replace(' บาท', '').replace(',', '')),
                'deposit_date': self.deposit_date_edit.date().toString("yyyy-MM-dd"),
                'due_date': self.due_date_edit.date().toString("yyyy-MM-dd"),
                'total_days': int(self.total_days_label.text()),
                'principal_amount': float(self.principal_amount_label.text().replace(' บาท', '').replace(',', '')),
                'penalty_amount': float(self.penalty_amount_label.text().replace(' บาท', '').replace(',', '')),
                'discount_amount': float(self.discount_amount_label.text().replace(' บาท', '').replace(',', ''))
            }
            
            # บันทึกการไถ่คืน
            redemption_id = self.db.redeem_contract(redemption_data)
            
            # ส่งข้อความแจ้งเตือนไลน์เมื่อมีการไถ่คืน
            self.send_redemption_line_notification(redemption_data)
            
            # ถามว่าจะสร้างสัญญาไถ่คืนหรือไม่
            reply = QMessageBox.question(
                self,
                "สร้างสัญญาไถ่คืน",
                "ต้องการจะสร้างสัญญาไถ่คืนหรือไม่?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.generate_redemption_contract_pdf(redemption_data, redemption_id)
                QMessageBox.information(self, "สำเร็จ", "บันทึกการไถ่คืนเรียบร้อย\nสร้างสัญญาไถ่คืนเรียบร้อยแล้ว")
            else:
                QMessageBox.information(self, "สำเร็จ", "บันทึกการไถ่คืนเรียบร้อย")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {str(e)}")
    
    def send_redemption_line_notification(self, redemption_data):
        """ส่งข้อความแจ้งเตือนไลน์เมื่อมีการไถ่คืน"""
        try:
            # ตรวจสอบการตั้งค่าการส่งข้อความ
            if not ENABLE_LINE_NOTIFICATION or not SEND_REDEMPTION_NOTIFICATION:
                return
            
            # ดึงข้อมูลลูกค้าและสินค้า
            customer = self.db.get_customer_by_id(self.contract_data.get('customer_id'))
            if not customer:
                print("ไม่พบข้อมูลลูกค้าสำหรับส่งข้อความแจ้งเตือน")
                return
                
            product = self.db.get_product_by_id(self.contract_data.get('product_id'))
            if not product:
                print("ไม่พบข้อมูลสินค้าสำหรับส่งข้อความแจ้งเตือน")
                return
            
            # เตรียมข้อมูลสำหรับส่งเข้า Line
            customer_name = "{} {}".format(
                customer.get('first_name', ''), 
                customer.get('last_name', '')
            ).strip()
            customer_phone = customer.get('phone', 'ไม่ระบุ')
            customer_id_card = customer.get('id_card', 'ไม่ระบุ')
            
            product_name = product.get('model', '') or product.get('name', 'ไม่ระบุ')
            product_brand = product.get('brand', 'ไม่ระบุ')
            product_size = product.get('size', 'ไม่ระบุ')
            product_serial = product.get('serial_number', 'ไม่ระบุ')
            
            # สร้างข้อความแจ้งเตือน
            message = MESSAGE_TEMPLATE['redemption'].format(
                contract_number=self.contract_data.get('contract_number', ''),
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_id_card=customer_id_card,
                product_name=product_name,
                product_brand=product_brand,
                product_size=product_size,
                product_serial=product_serial,
                pawn_amount=self.contract_data.get('pawn_amount', 0),
                fee_amount=self.contract_data.get('fee_amount', 0.0),
                total_paid=self.contract_data.get('total_paid', 0),
                redemption_amount=redemption_data['redemption_amount'],
                start_date=self.contract_data.get('start_date', 'ไม่ระบุ'),
                end_date=self.contract_data.get('end_date', 'ไม่ระบุ'),
                redemption_date=redemption_data['redemption_date'],
                days_count=self.contract_data.get('days_count', 0),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # ส่งข้อความ
            success = send_line_message(message)
            if success:
                print("ส่งข้อความแจ้งเตือนการไถ่คืนสำเร็จ")
            else:
                print("ส่งข้อความแจ้งเตือนการไถ่คืนไม่สำเร็จ")
                
        except Exception as e:
            print("เกิดข้อผิดพลาดในการส่งข้อความแจ้งเตือนการไถ่คืน: {str(e)}")
    
    def generate_redemption_contract_pdf(self, redemption_data, redemption_id):
        """สร้างสัญญาไถ่คืนเป็น PDF"""
        try:
            # นำเข้า pdf3.py
            from pdf3 import generate_redemption_contract_pdf
            
            # ดึงข้อมูลลูกค้าและสินค้าเพิ่มเติม
            contract_id = self.contract_data['id']
            customer = self.db.get_customer_by_id(self.contract_data.get('customer_id'))
            product = self.db.get_product_by_id(self.contract_data.get('product_id'))
            
            if not customer or not product:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลลูกค้าหรือสินค้า")
                return
            
            # สร้างข้อมูลการไถ่คืนสำหรับ PDF
            redemption_pdf_data = {
                'redemption_date': redemption_data['redemption_date'],
                'deposit_date': redemption_data['deposit_date'],
                'due_date': redemption_data['due_date'],
                'total_days': redemption_data['total_days'],
                'principal_amount': redemption_data['principal_amount'],
                'penalty_amount': redemption_data['penalty_amount'],
                'discount_amount': redemption_data['discount_amount'],
                'redemption_amount': redemption_data['redemption_amount']
            }
            
            # สร้างข้อมูลสัญญาเดิมที่ครบถ้วน
            original_contract_data = {
                'contract_number': self.contract_data.get('contract_number', ''),
                'start_date': self.contract_data.get('start_date', ''),
                'end_date': self.contract_data.get('end_date', ''),
                'days_count': self.contract_data.get('days_count', 0),
                'pawn_amount': self.contract_data.get('pawn_amount', 0),
                'estimated_value': self.contract_data.get('estimated_value', 0)
            }
            
            # สร้างข้อมูลลูกค้าที่ครบถ้วน
            customer_data = {
                'customer_code': customer.get('customer_code', ''),
                'first_name': customer.get('first_name', ''),
                'last_name': customer.get('last_name', ''),
                'phone': customer.get('phone', ''),
                'id_card': customer.get('id_card', ''),
                'house_number': customer.get('house_number', ''),
                'street': customer.get('street', ''),
                'subdistrict': customer.get('subdistrict', ''),
                'district': customer.get('district', ''),
                'province': customer.get('province', '')
            }
            
            default_shop_config = load_shop_config()
           # shop_name1 = (shop_data or {}).get('name', default_shop_config['name'])
          #  shop_branch2 = (shop_data or {}).get('branch', default_shop_config['branch'])
          #  shop_address3 = (shop_data or {}).get('address', default_shop_config['address'])

               # ข้อมูลร้านค้า
            shop_data = {
                'name': default_shop_config['name'],
                'branch': default_shop_config['branch'],
                'address': default_shop_config['address']
            }

            # สร้างข้อมูลสินค้าที่ครบถ้วน
            product_data = {
                'name': product.get('name', ''),
                'brand': product.get('brand', ''),
                'size': product.get('size', ''),
                'weight': product.get('weight', ''),
                'weight_unit': product.get('weight_unit', ''),
                'serial_number': product.get('serial_number', ''),
                'other_details': product.get('other_details', '')
            }
            
         
            
            # สร้างไฟล์ชั่วคราวสำหรับพรีวิวและให้ผู้ใช้เลือกบันทึก
            contract_number = self.contract_data.get('contract_number', 'unknown')
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_file = os.path.join(tmpdir, f"redemption_preview_{contract_number}.pdf")

                # สร้าง PDF ลงไฟล์ชั่วคราว
                result = generate_redemption_contract_pdf(
                    redemption_data=redemption_pdf_data,
                    customer_data=customer_data,
                    product_data=product_data,
                    original_contract_data=original_contract_data,
                    shop_data=shop_data,
                    output_file=temp_file,
                    output_folder=None
                )

                if result and os.path.exists(result):
                    # เปิดไฟล์ PDF ภายนอกเพื่อพรีวิว
                    import subprocess
                    import platform

                    try:
                        if platform.system() == "Darwin":
                            subprocess.run(["open", result])
                        elif platform.system() == "Windows":
                            os.startfile(result)
                        else:
                            subprocess.run(["xdg-open", result])
                    except Exception:
                        pass

                    # ให้ผู้ใช้เลือกตำแหน่งบันทึกไฟล์
                    suggested_name = f"ใบไถ่คืน_{contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    save_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "บันทึก PDF",
                        suggested_name,
                        "PDF Files (*.pdf)"
                    )
                    if save_path:
                        shutil.copyfile(result, save_path)
                        QMessageBox.information(self, "สำเร็จ", f"บันทึกสัญญาไถ่คืนแล้วที่:\n{save_path}")
                        # ในกรณีเป็นการไถ่คืนจริง สามารถสั่งพิมพ์ต่อได้ถ้าต้องการ
                        if redemption_id is not None:
                            self.print_redemption_contract(save_path)
                else:
                    QMessageBox.warning(self, "แจ้งเตือน", "สร้างสัญญาไถ่คืนไม่สำเร็จ")
                
        except ImportError:
            QMessageBox.critical(self, "ผิดพลาด", "ไม่สามารถนำเข้า pdf3.py ได้\nกรุณาตรวจสอบว่าไฟล์ pdf3.py อยู่ในโฟลเดอร์เดียวกัน")
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาดในการสร้าง PDF: {str(e)}")
    
    def print_redemption_contract(self, pdf_file_path):
        """พิมพ์สัญญาไถ่คืน"""
        try:
            import subprocess
            import platform
            
            # ตรวจสอบว่าไฟล์ PDF มีอยู่จริง
            if not os.path.exists(pdf_file_path):
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบไฟล์ PDF: {pdf_file_path}")
                return
            
            # พิมพ์ไฟล์ PDF ตามระบบปฏิบัติการ
            if platform.system() == "Darwin":  # macOS
                # ใช้ lpr สำหรับ macOS
                try:
                    subprocess.run(["lpr", pdf_file_path], check=True)
                    QMessageBox.information(self, "สำเร็จ", "ส่งงานพิมพ์เรียบร้อยแล้ว")
                except subprocess.CalledProcessError:
                    # หาก lpr ไม่ทำงาน ให้เปิด Preview และให้ผู้ใช้พิมพ์เอง
                    subprocess.run(["open", "-a", "Preview", pdf_file_path])
                    QMessageBox.information(self, "แจ้งเตือน", 
                        "เปิดไฟล์ใน Preview แล้ว\nกรุณาเลือกพิมพ์จากเมนู File > Print")
            elif platform.system() == "Windows":
                # ใช้ start สำหรับ Windows
                subprocess.run(["start", "/print", pdf_file_path], shell=True)
                QMessageBox.information(self, "สำเร็จ", "ส่งงานพิมพ์เรียบร้อยแล้ว")
            else:  # Linux
                # ใช้ lpr สำหรับ Linux
                try:
                    subprocess.run(["lpr", pdf_file_path], check=True)
                    QMessageBox.information(self, "สำเร็จ", "ส่งงานพิมพ์เรียบร้อยแล้ว")
                except subprocess.CalledProcessError:
                    # หาก lpr ไม่ทำงาน ให้เปิดไฟล์และให้ผู้ใช้พิมพ์เอง
                    subprocess.run(["xdg-open", pdf_file_path])
                    QMessageBox.information(self, "แจ้งเตือน", 
                        "เปิดไฟล์แล้ว\nกรุณาเลือกพิมพ์จากเมนู File > Print")
                        
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาดในการพิมพ์: {str(e)}")
    
    def generate_redemption_contract_only(self):
        """สร้างเฉพาะสัญญาไถ่คืนโดยไม่บันทึกการไถ่คืน"""
        try:
            if not self.contract_data:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
                return
            
            # สร้างข้อมูลการไถ่คืนสำหรับ PDF
            redemption_data = {
                'contract_id': self.contract_data['id'],
                'redemption_date': self.redemption_date_edit.date().toString("yyyy-MM-dd"),
                'redemption_amount': float(self.total_amount_label.text().replace(' บาท', '').replace(',', '')),
                'deposit_date': self.deposit_date_edit.date().toString("yyyy-MM-dd"),
                'due_date': self.due_date_edit.date().toString("yyyy-MM-dd"),
                'total_days': int(self.total_days_label.text()),
                'principal_amount': float(self.principal_amount_label.text().replace(' บาท', '').replace(',', '')),
                'penalty_amount': float(self.penalty_amount_label.text().replace(' บาท', '').replace(',', '')),
                'discount_amount': float(self.discount_amount_label.text().replace(' บาท', '').replace(',', ''))
            }
            
            # สร้างสัญญาไถ่คืน PDF
            self.generate_redemption_contract_pdf(redemption_data, None)
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {str(e)}")

class FolderSelectionDialog(QDialog):
    """Dialog สำหรับเลือกโฟลเดอร์ในการจัดเก็บไฟล์ PDF"""
    
    def __init__(self, parent=None, title="เลือกโฟลเดอร์สำหรับจัดเก็บไฟล์ PDF"):
        super().__init__(parent)
        self.selected_folder = ""
        self.setup_ui(title)
    
    def setup_ui(self, title):
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 150)
        
        layout = QVBoxLayout(self)
        
        # หัวข้อ
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # เลือกโฟลเดอร์
        folder_layout = QHBoxLayout()
        
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("เลือกโฟลเดอร์สำหรับจัดเก็บไฟล์ PDF...")
        self.folder_path_edit.setReadOnly(True)
        
        browse_button = QPushButton("เลือกโฟลเดอร์")
        browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(browse_button)
        
        layout.addLayout(folder_layout)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("ตกลง")
        ok_button.clicked.connect(self.accept)
        ok_button.setEnabled(False)
        
        cancel_button = QPushButton("ยกเลิก")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # เชื่อมต่อสัญญาณ
        self.folder_path_edit.textChanged.connect(lambda: ok_button.setEnabled(bool(self.folder_path_edit.text().strip())))
    
    def browse_folder(self):
        """เปิด dialog เลือกโฟลเดอร์"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "เลือกโฟลเดอร์สำหรับจัดเก็บไฟล์ PDF",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.folder_path_edit.setText(folder)
            self.selected_folder = folder
    
    def get_selected_folder(self):
        """ส่งคืนโฟลเดอร์ที่เลือก"""
        return self.selected_folder


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
        self.setWindowTitle(language_manager.get_text("renewal_title"))
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # ข้อมูลสัญญา
        contract_group = QGroupBox(language_manager.get_text("renewal_info_group"))
        contract_layout = QGridLayout(contract_group)
        
        self.contract_number_label = QLabel()
        self.customer_name_label = QLabel()
        self.pawn_amount_label = QLabel()
        
        contract_layout.addWidget(QLabel(language_manager.get_text("renewal_contract_number")), 0, 0)
        contract_layout.addWidget(self.contract_number_label, 0, 1)
        contract_layout.addWidget(QLabel(language_manager.get_text("renewal_customer_name")), 1, 0)
        contract_layout.addWidget(self.customer_name_label, 1, 1)
        contract_layout.addWidget(QLabel(language_manager.get_text("renewal_pawn_amount")), 2, 0)
        contract_layout.addWidget(self.pawn_amount_label, 2, 1)
        
        layout.addWidget(contract_group)
        
        # ข้อมูลการต่อดอก
        renewal_group = QGroupBox(language_manager.get_text("renewal_group"))
        renewal_layout = QGridLayout(renewal_group)
        
        # จำนวนวันฝากนับถึงปัจจุบัน
        self.days_deposit_label = QLabel("0")
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_days_deposit")), 0, 0)
        renewal_layout.addWidget(self.days_deposit_label, 0, 1)
        
        # ต่อดอกครั้งที่
        self.renewal_count_spin = QSpinBox()
        self.renewal_count_spin.setRange(1, 99)
        self.renewal_count_spin.setValue(1)
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_count")), 1, 0)
        renewal_layout.addWidget(self.renewal_count_spin, 1, 1)
        
        
        # ค่าปรับ
        self.penalty_amount_spin = QDoubleSpinBox()
        self.penalty_amount_spin.setRange(0, 999999)
        self.penalty_amount_spin.setSuffix(" บาท")
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_penalty")), 2, 0)
        renewal_layout.addWidget(self.penalty_amount_spin, 2, 1)
        
        # ส่วนลด
        self.discount_amount_spin = QDoubleSpinBox()
        self.discount_amount_spin.setRange(0, 999999)
        self.discount_amount_spin.setSuffix(" บาท")
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_discount")), 3, 0)
        renewal_layout.addWidget(self.discount_amount_spin, 3, 1)
        
        # รวม
        self.total_amount_label = QLabel("0.00 บาท")
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_total")), 4, 0)
        renewal_layout.addWidget(self.total_amount_label, 4, 1)
        
        # วันที่ต่อดอก
        self.renewal_date_edit = QDateEdit()
        self.renewal_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_date")), 5, 0)
        renewal_layout.addWidget(self.renewal_date_edit, 5, 1)
        
        # วันครบกำหนดปัจจุบัน
        self.current_due_date_edit = QDateEdit()
        self.current_due_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_current_due")), 6, 0)
        renewal_layout.addWidget(self.current_due_date_edit, 6, 1)
        
        # วันครบกำหนดใหม่
        self.new_due_date_edit = QDateEdit()
        self.new_due_date_edit.setDate(QDate.currentDate())
        renewal_layout.addWidget(QLabel(language_manager.get_text("renewal_new_due")), 7, 0)
        renewal_layout.addWidget(self.new_due_date_edit, 7, 1)
        
        # เชื่อมต่อสัญญาณ
        self.penalty_amount_spin.valueChanged.connect(self.calculate_total)
        self.discount_amount_spin.valueChanged.connect(self.calculate_total)
        
        layout.addWidget(renewal_group)
        
        # ข้อความยืนยัน
        confirm_label = QLabel(language_manager.get_text("renewal_confirm_text"))
        confirm_label.setAlignment(Qt.AlignCenter)
        confirm_label.setStyleSheet("font-weight: bold; color: #2E86AB; font-size: 14px;")
        layout.addWidget(confirm_label)
        
        # ปุ่ม
        button_layout = QHBoxLayout()
        
        save_button = QPushButton(language_manager.get_text("ok"))
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
        cancel_button = QPushButton(language_manager.get_text("no"))
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

        # ผูกภาษา
        language_manager.language_changed.connect(self.apply_language)
        self.apply_language()

    def apply_language(self, *_args):
        self.setWindowTitle(language_manager.get_text("renewal_title"))
    
    def load_contract_data(self):
        """โหลดข้อมูลสัญญา"""
        if self.contract_data:
            self.contract_number_label.setText(self.contract_data.get('contract_number', ''))
            customer_name = "{} {}".format(self.contract_data.get('first_name', ''), self.contract_data.get('last_name', ''))
            self.customer_name_label.setText(customer_name)
            self.pawn_amount_label.setText("{:,.2f} บาท".format(self.contract_data.get('pawn_amount', 0)))
            
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
                self.days_deposit_label.setText("{days_diff} วัน")
            except:
                self.days_deposit_label.setText("0 วัน")
    
    def calculate_total(self):
        """คำนวณยอดรวม"""
        penalty = self.penalty_amount_spin.value()
        discount = self.discount_amount_spin.value()
        total = penalty - discount
        self.total_amount_label.setText("{:,.2f} บาท".format(total))
    
    def save_renewal(self):
        """บันทึกการต่อดอก"""
        if not self.contract_data:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
            return
        
        # ตรวจสอบข้อมูลที่จำเป็น
        if self.penalty_amount_spin.value() == 0 and self.discount_amount_spin.value() == 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกค่าปรับหรือส่วนลดอย่างน้อยหนึ่งรายการ")
            return
        
        renewal_data = {
            'contract_id': self.contract_data['id'],
            'renewal_count': self.renewal_count_spin.value(),
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
            
            # ส่งข้อความแจ้งเตือนไลน์เมื่อมีการต่อดอก
            self.send_renewal_line_notification(renewal_data)
            
            QMessageBox.information(self, "สำเร็จ", "บันทึกการต่อดอกเรียบร้อย")
            
            # ถามว่าต้องการสร้างใบฝากต่อไหม
            reply = QMessageBox.question(
                self, 
                "สร้างใบฝากต่อ", 
                "ต้องการสร้างใบฝากต่อไหม?", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.generate_renewal_pdf()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {}".format(str(e)))
    
    def send_renewal_line_notification(self, renewal_data):
        """ส่งข้อความแจ้งเตือนไลน์เมื่อมีการต่อดอก"""
        try:
            # ตรวจสอบการตั้งค่าการส่งข้อความ
            if not ENABLE_LINE_NOTIFICATION or not SEND_RENEWAL_NOTIFICATION:
                return
            
            # ดึงข้อมูลลูกค้าและสัญญา
            customer = self.db.get_customer_by_id(self.contract_data.get('customer_id'))
            if not customer:
                print("ไม่พบข้อมูลลูกค้าสำหรับส่งข้อความแจ้งเตือน")
                return
            
            # สร้างข้อความแจ้งเตือน
            message = MESSAGE_TEMPLATE['renewal'].format(
                contract_number=self.contract_data.get('contract_number', ''),
                customer_name="{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                original_amount=self.contract_data.get('pawn_amount', 0),
                renewal_fee=renewal_data['total_amount'],
                renewal_date=renewal_data['renewal_date'],
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # ส่งข้อความ
            success = send_line_message(message)
            if success:
                print("ส่งข้อความแจ้งเตือนการต่อดอกสำเร็จ")
            else:
                print("ส่งข้อความแจ้งเตือนการต่อดอกไม่สำเร็จ")
                
        except Exception as e:
            print("เกิดข้อผิดพลาดในการส่งข้อความแจ้งเตือนการต่อดอก: {str(e)}")
    
    def generate_renewal_pdf(self):
        """สร้างใบฝากต่อ PDF"""
        if not self.contract_data:
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสัญญา")
            return
        
        try:
            # ดึงข้อมูลลูกค้าและสินค้าเพิ่มเติม
            contract_id = self.contract_data['id']
            customer = self.db.get_customer_by_id(self.contract_data.get('customer_id'))
            product = self.db.get_product_by_id(self.contract_data.get('product_id'))
            
            if not customer or not product:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลลูกค้าหรือสินค้า")
                return
            
            # สร้างข้อมูลการต่อดอกสำหรับ PDF
            renewal_data = {
                'renewal_date': self.renewal_date_edit.date().toString("yyyy-MM-dd"),
                'extension_days': (self.new_due_date_edit.date().toJulianDay() - self.current_due_date_edit.date().toJulianDay()),
                'total_amount': float(self.total_amount_label.text().replace(' บาท', '').replace(',', ''))
            }
            
            # สร้างข้อมูลสัญญาที่ครบถ้วน
            original_contract_data = {
                'contract_number': self.contract_data.get('contract_number', ''),
                'start_date': self.contract_data.get('start_date', ''),
                'end_date': self.contract_data.get('end_date', ''),
                'days_count': self.contract_data.get('days_count', 0),
                'pawn_amount': self.contract_data.get('pawn_amount', 0),
                'estimated_value': self.contract_data.get('estimated_value', 0)
            }
            
            # สร้างข้อมูลลูกค้าที่ครบถ้วน
            customer_data = {
                'customer_code': customer.get('customer_code', ''),
                'first_name': customer.get('first_name', ''),
                'last_name': customer.get('last_name', ''),
                'phone': customer.get('phone', ''),
                'id_card': customer.get('id_card', ''),
                'house_number': customer.get('house_number', ''),
                'street': customer.get('street', ''),
                'subdistrict': customer.get('subdistrict', ''),
                'district': customer.get('district', ''),
                'province': customer.get('province', '')
            }
            
            # สร้างข้อมูลสินค้าที่ครบถ้วน
            product_data = {
                'name': product.get('name', ''),
                'brand': product.get('brand', ''),
                'size': product.get('size', ''),
                'weight': product.get('weight', ''),
                'weight_unit': product.get('weight_unit', ''),
                'serial_number': product.get('serial_number', ''),
                'other_details': product.get('other_details', '')
            }
            
            # ข้อมูลร้านค้า - ใช้ข้อมูลจาก pdf3.py
            shop_data = None  # ให้ใช้ค่า default จาก pdf3.py
            
            # นำเข้า pdf2.py และสร้างไฟล์ชั่วคราวสำหรับพรีวิว แล้วค่อย Save As
            try:
                from pdf2 import generate_renewal_contract_pdf

                contract_number = self.contract_data.get('contract_number', 'unknown')
                with tempfile.TemporaryDirectory() as tmpdir:
                    temp_file = os.path.join(tmpdir, "renewal_preview_{contract_number}.pd")

                    result = generate_renewal_contract_pdf(
                        original_contract_data=original_contract_data,
                        customer_data=customer_data,
                        product_data=product_data,
                        renewal_data=renewal_data,
                        shop_data=shop_data,
                        output_file=temp_file,
                        output_folder=None
                    )

                    if result and os.path.exists(result):
                        # เปิดไฟล์ PDF ภายนอกเพื่อพรีวิว
                        import subprocess
                        import platform

                        try:
                            if platform.system() == "Darwin":
                                subprocess.run(["open", result])
                            elif platform.system() == "Windows":
                                os.startfile(result)
                            else:
                                subprocess.run(["xdg-open", result])
                        except Exception:
                            pass

                        # ให้ผู้ใช้เลือกตำแหน่งบันทึกไฟล์
                        suggested_name = "ใบฝากต่อ_{contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pd"
                        save_path, _ = QFileDialog.getSaveFileName(
                            self,
                            "บันทึก PDF",
                            suggested_name,
                            "PDF Files (*.pdf)"
                        )
                        if save_path:
                            shutil.copyfile(result, save_path)
                            QMessageBox.information(self, "สำเร็จ", "บันทึกใบฝากต่อแล้วที่:\n{save_path}")
                    else:
                        QMessageBox.warning(self, "แจ้งเตือน", "สร้างใบฝากต่อไม่สำเร็จ")
            except ImportError:
                QMessageBox.critical(self, "ผิดพลาด", "ไม่สามารถนำเข้า pdf2.py ได้\nกรุณาตรวจสอบว่าไฟล์ pdf2.py อยู่ในโฟลเดอร์เดียวกัน")
            except Exception as e:
                QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาดในการสร้าง PDF: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: {str(e)}")
