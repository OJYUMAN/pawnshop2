#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบการเชื่อมต่อบัตรประชาชน
สำหรับแก้ไขปัญหา "Card is unresponsive" และ "Unable to connect with protocol: T0 or T1"
"""

import sys
import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.pcsc.PCSCExceptions import EstablishContextException

def test_card_reader_detection():
    """ทดสอบการตรวจจับ card reader"""
    print("=== ทดสอบการตรวจจับ Card Reader ===")
    
    try:
        reader_list = readers()
        if not reader_list:
            print("❌ ไม่พบ card reader")
            print("กรุณาตรวจสอบ:")
            print("1. การเชื่อมต่อ USB")
            print("2. การติดตั้ง driver")
            print("3. PC/SC service ทำงานอยู่")
            return False
        
        print(f"✅ พบ card reader: {len(reader_list)} ตัว")
        for i, reader in enumerate(reader_list):
            print(f"  {i}: {reader}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจจับ card reader: {e}")
        return False

def test_card_connection(reader_index=0):
    """ทดสอบการเชื่อมต่อกับบัตร"""
    print(f"\n=== ทดสอบการเชื่อมต่อกับ Card Reader {reader_index} ===")
    
    try:
        reader_list = readers()
        if reader_index >= len(reader_list):
            print(f"❌ Card reader index {reader_index} ไม่มีอยู่")
            return False
        
        reader = reader_list[reader_index]
        print(f"ใช้ card reader: {reader}")
        
        # ทดสอบการเชื่อมต่อหลายครั้ง
        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"\n--- ความพยายาม {attempt + 1}/{max_attempts} ---")
            
            try:
                # สร้างการเชื่อมต่อใหม่
                connection = reader.createConnection()
                
                # ลองใช้โปรโตคอลต่างๆ
                protocols = [None, 0, 1]  # Default, T0, T1
                protocol_names = ["Default", "T0", "T1"]
                
                connected = False
                for i, protocol in enumerate(protocols):
                    try:
                        print(f"  ลองโปรโตคอล: {protocol_names[i]}...")
                        
                        if protocol is None:
                            connection.connect()
                        else:
                            connection.connect(protocol)
                        
                        # ถ้าเชื่อมต่อสำเร็จ
                        connected = True
                        print(f"  ✅ เชื่อมต่อสำเร็จด้วยโปรโตคอล: {protocol_names[i]}")
                        
                        # อ่าน ATR (Answer To Reset)
                        try:
                            atr = connection.getATR()
                            print(f"  📋 ATR: {toHexString(atr)}")
                            
                            # ตรวจสอบประเภทบัตร
                            if len(atr) >= 2:
                                if atr[0] == 0x3B and atr[1] == 0x67:
                                    print("  🎴 ประเภทบัตร: บัตรประชาชนไทย (รุ่นเก่า)")
                                elif atr[0] == 0x3B and atr[1] == 0x79:
                                    print("  🎴 ประเภทบัตร: บัตรประชาชนไทย (รุ่นใหม่)")
                                elif atr[0] == 0x3B and atr[1] == 0xF8:
                                    print("  💳 ประเภทบัตร: บัตร EMV (เครดิต/เดบิต)")
                                else:
                                    print(f"  ❓ ประเภทบัตร: ไม่ทราบ (ATR: {toHexString(atr)})")
                            
                        except Exception as e:
                            print(f"  ⚠️  ไม่สามารถอ่าน ATR ได้: {e}")
                        
                        # ทดสอบการเลือก applet บัตรประชาชน
                        test_thai_id_applet(connection)
                        
                        break
                        
                    except CardConnectionException as e:
                        print(f"  ❌ โปรโตคอล {protocol_names[i]} ล้มเหลว: {e}")
                        continue
                    except Exception as e:
                        print(f"  ❌ ข้อผิดพลาดกับโปรโตคอล {protocol_names[i]}: {e}")
                        continue
                
                if connected:
                    # ปิดการเชื่อมต่อ
                    try:
                        connection.disconnect()
                        print("  ✅ ปิดการเชื่อมต่อสำเร็จ")
                    except:
                        print("  ⚠️  ปิดการเชื่อมต่อไม่สำเร็จ")
                    
                    print(f"\n✅ การเชื่อมต่อสำเร็จในความพยายามที่ {attempt + 1}")
                    return True
                else:
                    print(f"  ❌ ความพยายามที่ {attempt + 1} ล้มเหลว")
                    if attempt < max_attempts - 1:
                        print("  ⏳ รอ 3 วินาทีก่อนลองใหม่...")
                        time.sleep(3)
                    continue
                
            except Exception as e:
                print(f"  ❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
                if attempt < max_attempts - 1:
                    print("  ⏳ รอ 3 วินาทีก่อนลองใหม่...")
                    time.sleep(3)
                continue
        
        print(f"\n❌ ไม่สามารถเชื่อมต่อได้หลังจากลอง {max_attempts} ครั้ง")
        return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_thai_id_applet(connection):
    """ทดสอบการเลือก applet บัตรประชาชน"""
    print("  🔍 ทดสอบการเลือก applet บัตรประชาชน...")
    
    # คำสั่งเลือก applet บัตรประชาชนไทย
    applet_commands = [
        # รุ่นเก่า
        [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01],
        # รุ่นใหม่
        [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x00],
        # รุ่นอื่นๆ
        [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x02]
    ]
    
    applet_names = ["รุ่นเก่า", "รุ่นใหม่", "รุ่นอื่นๆ"]
    
    for i, (cmd, name) in enumerate(zip(applet_commands, applet_names)):
        try:
            print(f"    ลอง applet {name}...")
            response, sw1, sw2 = connection.transmit(cmd)
            
            if sw1 == 0x90 and sw2 == 0x00:
                print(f"    ✅ เลือก applet {name} สำเร็จ")
                
                # ทดสอบการอ่านข้อมูลพื้นฐาน
                test_basic_reading(connection)
                return True
            else:
                print(f"    ❌ เลือก applet {name} ล้มเหลว: SW1={sw1:02X}, SW2={sw2:02X}")
                
        except Exception as e:
            print(f"    ❌ ข้อผิดพลาดกับ applet {name}: {e}")
            continue
    
    print("    ❌ ไม่สามารถเลือก applet บัตรประชาชนได้")
    return False

def test_basic_reading(connection):
    """ทดสอบการอ่านข้อมูลพื้นฐาน"""
    print("    📖 ทดสอบการอ่านข้อมูลพื้นฐาน...")
    
    # คำสั่งอ่านข้อมูลพื้นฐาน
    read_commands = {
        "เลขบัตรประชาชน": [0x80, 0xB0, 0x00, 0x04, 0x02, 0x00, 0x0D],
        "ชื่อภาษาไทย": [0x80, 0xB0, 0x00, 0x11, 0x02, 0x00, 0x64],
        "วันเกิด": [0x80, 0xB0, 0x00, 0xD9, 0x02, 0x00, 0x08]
    }
    
    for field_name, cmd in read_commands.items():
        try:
            data, sw1, sw2 = connection.transmit(cmd)
            
            if sw1 == 0x90 and sw2 == 0x00 and data:
                # แปลงข้อมูลจาก TIS-620 เป็น Unicode
                try:
                    value = bytes(data).decode('tis-620', errors='ignore').replace("#", " ").strip()
                    print(f"      ✅ {field_name}: {value}")
                except:
                    print(f"      ✅ {field_name}: {toHexString(data)} (ไม่สามารถแปลงเป็นข้อความได้)")
            else:
                print(f"      ❌ {field_name}: อ่านไม่สำเร็จ (SW1={sw1:02X}, SW2={sw2:02X})")
                
        except Exception as e:
            print(f"      ❌ {field_name}: เกิดข้อผิดพลาด - {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("=== ทดสอบการเชื่อมต่อบัตรประชาชน ===\n")
    
    # ทดสอบการตรวจจับ card reader
    if not test_card_reader_detection():
        print("\n❌ ไม่สามารถดำเนินการต่อได้")
        return
    
    # ทดสอบการเชื่อมต่อกับบัตร
    if test_card_connection():
        print("\n🎉 การทดสอบสำเร็จ! บัตรประชาชนพร้อมใช้งาน")
    else:
        print("\n❌ การทดสอบล้มเหลว")
        print("\n💡 ข้อเสนอแนะ:")
        print("1. ตรวจสอบว่าบัตรใส่ถูกต้องหรือไม่")
        print("2. ลบและใส่บัตรใหม่")
        print("3. ทำความสะอาดหน้าสัมผัสของบัตร")
        print("4. ลองใช้ card reader อื่น")
        print("5. ตรวจสอบ PC/SC service")
        print("6. รีสตาร์ทระบบ")

if __name__ == "__main__":
    main()
