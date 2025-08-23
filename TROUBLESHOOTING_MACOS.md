# คู่มือการแก้ไขปัญหาสแกนบัตรประชาชนบน macOS

## ปัญหา: "Card is unresponsive" หรือ "Unable to connect with protocol: T0 or T1"

### สาเหตุ
ปัญหานี้มักเกิดจาก:
1. Card reader ไม่รองรับโปรโตคอลที่ใช้
2. บัตรเสียหายหรือหน้าสัมผัสสกปรก
3. Driver ของ card reader ไม่เหมาะสม
4. PC/SC service ไม่ทำงาน
5. การตั้งค่าระบบไม่ถูกต้อง

### วิธีแก้ไข

#### 1. ตรวจสอบ PC/SC Service
```bash
# ตรวจสอบว่า pcscd ทำงานอยู่หรือไม่
ps aux | grep pcscd

# ถ้าไม่ทำงาน ให้เริ่มต้น
brew services start pcsc-lite
```

#### 2. ตรวจสอบ Card Reader
```bash
# ตรวจสอบ card reader ที่เชื่อมต่อ
system_profiler SPUSBDataType | grep -A 10 -i "card\|reader\|smart"

# ตรวจสอบ device ในระบบ
ls -la /dev/usb*
```

#### 3. ติดตั้ง/อัปเดต Driver
```bash
# ติดตั้ง pcsc-lite ใหม่
brew uninstall pcsc-lite
brew install pcsc-lite

# ติดตั้ง pcsclite development tools
brew install pcsclite-dev
```

#### 4. ตรวจสอบสิทธิ์การเข้าถึง
```bash
# ตรวจสอบสิทธิ์ของ /dev/usb*
ls -la /dev/usb*

# ถ้าจำเป็น ให้เพิ่มสิทธิ์
sudo chmod 666 /dev/usb*
```

#### 5. รีสตาร์ท PC/SC Service
```bash
# หยุด service
brew services stop pcsc-lite

# รอ 5 วินาที
sleep 5

# เริ่ม service ใหม่
brew services start pcsc-lite

# ตรวจสอบสถานะ
brew services list | grep pcsc
```

#### 6. ตรวจสอบการเชื่อมต่อ
```bash
# ทดสอบการเชื่อมต่อ card reader
python3 -c "
from smartcard.System import readers
readers = readers()
print(f'พบ card reader: {len(readers)} ตัว')
for i, reader in enumerate(readers):
    print(f'  {i}: {reader}')
"
```

### การทดสอบ Card Reader

#### ทดสอบการเชื่อมต่อพื้นฐาน
```python
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException

try:
    # ตรวจสอบ card reader
    reader_list = readers()
    if not reader_list:
        print("ไม่พบ card reader")
        exit(1)
    
    reader = reader_list[0]
    print(f"ใช้ card reader: {reader}")
    
    # ลองเชื่อมต่อ
    connection = reader.createConnection()
    
    # ลองโปรโตคอลต่างๆ
    protocols = [None, 0, 1]
    protocol_names = ["Default", "T0", "T1"]
    
    for protocol, name in zip(protocols, protocol_names):
        try:
            if protocol is None:
                connection.connect()
            else:
                connection.connect(protocol)
            
            print(f"✅ เชื่อมต่อสำเร็จด้วยโปรโตคอล: {name}")
            
            # อ่าน ATR
            atr = connection.getATR()
            print(f"ATR: {atr}")
            
            # ปิดการเชื่อมต่อ
            connection.disconnect()
            break
            
        except CardConnectionException as e:
            print(f"❌ โปรโตคอล {name} ล้มเหลว: {e}")
            continue
        except Exception as e:
            print(f"❌ ข้อผิดพลาดกับโปรโตคอล {name}: {e}")
            continue
    
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
```

### การแก้ไขปัญหาเฉพาะ

#### ปัญหา: "Card is unresponsive"
1. **ลบและใส่บัตรใหม่** - บางครั้งบัตรไม่ได้ใส่ในตำแหน่งที่ถูกต้อง
2. **ทำความสะอาดหน้าสัมผัส** - ใช้ผ้าแห้งทำความสะอาดหน้าสัมผัสของบัตร
3. **ตรวจสอบทิศทาง** - ใส่บัตรในทิศทางที่ถูกต้อง
4. **ลองใช้บัตรอื่น** - เพื่อตรวจสอบว่าเป็นปัญหาของบัตรหรือ card reader

#### ปัญหา: "Unable to connect with protocol: T0 or T1"
1. **ใช้โปรโตคอล Default** - ลองใช้การเชื่อมต่อแบบ default
2. **ตรวจสอบ card reader** - บาง card reader รองรับเฉพาะโปรโตคอลใดโปรโตคอลหนึ่ง
3. **อัปเดต driver** - ติดตั้ง driver ล่าสุดสำหรับ card reader

#### ปัญหา: "No card detected"
1. **ตรวจสอบการเชื่อมต่อ USB** - ตรวจสอบว่า card reader เชื่อมต่อถูกต้อง
2. **ตรวจสอบไฟ LED** - card reader ควรมีไฟ LED แสดงสถานะ
3. **ลองใช้ USB port อื่น** - บางครั้ง USB port มีปัญหา

### การตั้งค่าระบบ

#### เพิ่มสิทธิ์การเข้าถึง USB
```bash
# สร้างไฟล์ rules สำหรับ udev (Linux) หรือใช้การตั้งค่า macOS
sudo nano /etc/udev/rules.d/99-smartcard.rules

# เพิ่มบรรทัดนี้
SUBSYSTEM=="usb", ATTR{idVendor}=="XXXX", ATTR{idProduct}=="YYYY", MODE="0666"
```

#### ตั้งค่า PC/SC
```bash
# ตรวจสอบการตั้งค่า pcscd
sudo nano /etc/pcsc/pcscd.conf

# เพิ่มหรือแก้ไขบรรทัดเหล่านี้
# Enable USB support
usb = yes

# Enable debugging
debug = yes
```

### การทดสอบขั้นสูง

#### ทดสอบการอ่านข้อมูลบัตร
```python
# ทดสอบการอ่านข้อมูลจากบัตรประชาชน
def test_read_thai_id():
    try:
        from smartcard.System import readers
        from smartcard.util import toHexString
        
        reader = readers()[0]
        connection = reader.createConnection()
        connection.connect()
        
        # ทดสอบคำสั่งพื้นฐาน
        SELECT_CMD = [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
        response, sw1, sw2 = connection.transmit(SELECT_CMD)
        
        if sw1 == 0x90 and sw2 == 0x00:
            print("✅ เลือก applet สำเร็จ")
            
            # ทดสอบการอ่านข้อมูล
            READ_CMD = [0x80, 0xB0, 0x00, 0x04, 0x02, 0x00, 0x0D]
            data, sw1, sw2 = connection.transmit(READ_CMD)
            
            if sw1 == 0x90 and sw2 == 0x00:
                print(f"✅ อ่านข้อมูลสำเร็จ: {toHexString(data)}")
            else:
                print(f"❌ อ่านข้อมูลล้มเหลว: SW1={sw1:02X}, SW2={sw2:02X}")
        else:
            print(f"❌ เลือก applet ล้มเหลว: SW1={sw1:02X}, SW2={sw2:02X}")
        
        connection.disconnect()
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

# รันการทดสอบ
test_read_thai_id()
```

### สรุป

หากยังคงมีปัญหา ให้ลอง:
1. **รีสตาร์ทระบบ** - บางครั้งการรีสตาร์ทช่วยแก้ปัญหาได้
2. **ใช้ card reader อื่น** - เพื่อตรวจสอบว่าเป็นปัญหาของ card reader หรือระบบ
3. **ตรวจสอบ log** - ดู log ของ pcscd เพื่อหาสาเหตุ
4. **ติดต่อผู้ผลิต** - หากเป็นปัญหาของ card reader โดยเฉพาะ

### ข้อมูลเพิ่มเติม
- [PCSC-Lite Documentation](https://pcsclite.apdu.fr/)
- [Smart Card Development](https://smartcard.de/)
- [PySCard Documentation](https://pyscard.sourceforge.io/)
