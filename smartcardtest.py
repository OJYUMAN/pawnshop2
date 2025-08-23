#  install pcscd python-pyscard python-pil
import os
import io
import binascii
import sys
import codecs
from PIL import Image
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes
from smartcard.Exceptions import NoCardException, CardConnectionException

# Thailand ID Smartcard
def thai2unicode(data):
    """Convert TIS-620 encoded data to Unicode"""
    try:
        if not data:
            return ""
        result = bytes(data).decode('tis-620', errors='ignore').replace("#", " ")
        return result.strip()
    except Exception as e:
        print(f"Error converting data to unicode: {e}")
        return ""

def getData(connection, cmd, req=[0x00, 0xc0, 0x00, 0x00]):
    """Get data from smartcard with proper error handling"""
    try:
        # First command
        data, sw1, sw2 = connection.transmit(cmd)
        
        # Check if we need to get response data
        if sw1 == 0x61:  # More data available
            # Get response data
            response_data, sw1, sw2 = connection.transmit(req + [sw2])
            return [response_data, sw1, sw2]
        elif sw1 == 0x90 and sw2 == 0x00:  # Success
            return [data, sw1, sw2]
        else:
            print(f"Command failed: SW1={sw1:02X}, SW2={sw2:02X}")
            return [data, sw1, sw2]
    except Exception as e:
        print(f"Error executing command: {e}")
        return [[], 0xFF, 0xFF]

def check_card_type(atr):
    """Check card type based on ATR"""
    if len(atr) >= 2:
        if atr[0] == 0x3B and atr[1] == 0x67:
            return "THAI_ID", [0x00, 0xc0, 0x00, 0x01]
        elif atr[0] == 0x3B and atr[1] == 0xF8:
            return "EMV_CARD", [0x00, 0xc0, 0x00, 0x00]
        elif atr[0] == 0x3B and atr[1] == 0x79:
            # New pattern for Thai ID cards
            return "THAI_ID", [0x00, 0xc0, 0x00, 0x00]
    return "UNKNOWN", [0x00, 0xc0, 0x00, 0x00]

def detect_emv_card(connection):
    """Detect EMV card type (VISA, MasterCard, etc.)"""
    try:
        # Select PSE (Payment System Environment)
        SELECT_PSE = [0x00, 0xA4, 0x04, 0x00, 0x0E, 0x32, 0x50, 0x41, 0x59, 0x2E, 0x53, 0x59, 0x53, 0x2E, 0x44, 0x44, 0x46, 0x30, 0x31]
        data, sw1, sw2 = connection.transmit(SELECT_PSE)
        print(f"Select PSE -> {data} (SW1={sw1:02X} SW2={sw2:02X})")
        
        if sw1 == 0x90 and sw2 == 0x00:
            # Try VISA AID
            VISA_AID = [0x00, 0xA4, 0x04, 0x00, 0x07, 0xA0, 0x00, 0x00, 0x00, 0x03, 0x10, 0x10]
            data, sw1, sw2 = connection.transmit(VISA_AID)
            print(f"Select VISA AID -> {data} (SW1={sw1:02X} SW2={sw2:02X})")
            
            if sw1 == 0x90 and sw2 == 0x00:
                return "VISA"
            
            # Try MasterCard AID
            MASTERCARD_AID = [0x00, 0xA4, 0x04, 0x00, 0x07, 0xA0, 0x00, 0x00, 0x00, 0x04, 0x10, 0x10]
            data, sw1, sw2 = connection.transmit(MASTERCARD_AID)
            print(f"Select MasterCard AID -> {data} (SW1={sw1:02X} SW2={sw2:02X})")
            
            if sw1 == 0x90 and sw2 == 0x00:
                return "MasterCard"
        
        return "Unknown EMV"
        
    except Exception as e:
        print(f"Error detecting EMV card: {e}")
        return "Unknown EMV"

def try_read_thai_id_card(connection, req):
    """Try to read Thai ID card with multiple applet selection methods"""
    print("\n🔍 Trying to read Thai ID card...")
    
    # Method 1: Standard Thai ID Card applet
    SELECT_THAI_1 = [0x00, 0xA4, 0x04, 0x00, 0x08]
    THAI_CARD_1 = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
    
    data, sw1, sw2 = connection.transmit(SELECT_THAI_1 + THAI_CARD_1)
    print(f"Select Thai ID Applet 1: {sw1:02X} {sw2:02X}")
    
    if sw1 == 0x90 and sw2 == 0x00:
        print("✅ Successfully selected Thai ID applet (Method 1)")
        return read_thai_id_card(connection, req)
    
    # Method 2: Alternative Thai ID Card applet
    SELECT_THAI_2 = [0x00, 0xA4, 0x04, 0x00, 0x08]
    THAI_CARD_2 = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x00]
    
    data, sw1, sw2 = connection.transmit(SELECT_THAI_2 + THAI_CARD_2)
    print(f"Select Thai ID Applet 2: {sw1:02X} {sw2:02X}")
    
    if sw1 == 0x90 and sw2 == 0x00:
        print("✅ Successfully selected Thai ID applet (Method 2)")
        return read_thai_id_card(connection, req)
    
    # Method 3: Try to read directly without applet selection
    print("🔄 Trying direct read method...")
    return read_thai_id_card_direct(connection, req)

def read_thai_id_card_direct(connection, req):
    """Read Thai ID card data directly without applet selection"""
    print("\n=== Reading Thai ID Card Data (Direct Method) ===")
    
    # Define commands for different data fields
    commands = {
        "CID": [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d],
        "TH Fullname": [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64],
        "EN Fullname": [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64],
        "Date of birth": [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08],
        "Gender": [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01],
        "Card Issuer": [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64],
        "Issue Date": [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08],
        "Expire Date": [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08],
        "Address": [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]
    }

    # Read text data
    card_data = {}
    for field_name, cmd in commands.items():
        try:
            data, sw1, sw2 = getData(connection, cmd, req)
            if sw1 == 0x90 and sw2 == 0x00 and data:
                value = thai2unicode(data)
                card_data[field_name] = value
                print(f"✅ {field_name}: {value}")
            else:
                print(f"❌ {field_name}: Failed to read (SW1={sw1:02X}, SW2={sw2:02X})")
        except Exception as e:
            print(f"❌ {field_name}: Error - {e}")

    # Try alternative command formats
    print("\n🔄 Trying alternative command formats...")
    alt_commands = {
        "CID (Alt)": [0x80, 0xb0, 0x00, 0x04, 0x01, 0x00, 0x0d],
        "Name (Alt)": [0x80, 0xb0, 0x00, 0x11, 0x01, 0x00, 0x64],
    }
    
    for field_name, cmd in alt_commands.items():
        try:
            data, sw1, sw2 = getData(connection, cmd, req)
            if sw1 == 0x90 and sw2 == 0x00 and data:
                value = thai2unicode(data)
                print(f"✅ {field_name}: {value}")
            else:
                print(f"❌ {field_name}: Failed (SW1={sw1:02X}, SW2={sw2:02X})")
        except Exception as e:
            print(f"❌ {field_name}: Error - {e}")

    # Read photo data (20 parts)
    photo_parts = []
    photo_commands = []
    
    # Generate photo commands
    for i in range(20):
        if i < 10:
            cmd = [0x80, 0xb0, 0x00, 0x7B + i, 0x02, 0x00, 0xFF]
        else:
            cmd = [0x80, 0xb0, 0x01, 0x7B - (i - 10), 0x02, 0x00, 0xFF]
        photo_commands.append(cmd)

    print("\n📸 Reading photo data...")
    for i, cmd in enumerate(photo_commands):
        try:
            data, sw1, sw2 = getData(connection, cmd, req)
            if sw1 == 0x90 and sw2 == 0x00 and data:
                photo_parts.append(data)
                print(f"✅ Photo part {i+1}: {len(data)} bytes")
            else:
                print(f"❌ Photo part {i+1}: Failed or empty")
        except Exception as e:
            print(f"❌ Error reading photo part {i+1}: {e}")

    # Combine photo parts
    if photo_parts:
        try:
            photo_data = b''
            for part in photo_parts:
                photo_data += bytes(part)
            
            # Save photo
            cid = card_data.get("CID", "unknown")
            if cid == "unknown":
                cid = "thai_id_card"
            
            photo_filename = f"{cid}.jpg"
            with open(photo_filename, "wb") as f:
                f.write(photo_data)
            print(f"\n💾 Photo saved as: {photo_filename}")
            print(f"📏 Photo size: {len(photo_data)} bytes")
            
        except Exception as e:
            print(f"❌ Error saving photo: {e}")
    else:
        print("❌ No photo data could be read")

    return card_data

def read_thai_id_card(connection, req):
    """Read data from Thai ID card"""
    print("\n=== Reading Thai ID Card Data ===")
    
    # Define commands for different data fields
    commands = {
        "CID": [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d],
        "TH Fullname": [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64],
        "EN Fullname": [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64],
        "Date of birth": [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08],
        "Gender": [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01],
        "Card Issuer": [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64],
        "Issue Date": [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08],
        "Expire Date": [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08],
        "Address": [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]
    }

    # Read text data
    card_data = {}
    for field_name, cmd in commands.items():
        data, sw1, sw2 = getData(connection, cmd, req)
        if sw1 == 0x90 and sw2 == 0x00:
            value = thai2unicode(data)
            card_data[field_name] = value
            print(f"{field_name}: {value}")
        else:
            print(f"{field_name}: Failed to read (SW1={sw1:02X}, SW2={sw2:02X})")

    # Read photo data (20 parts)
    photo_parts = []
    photo_commands = []
    
    # Generate photo commands
    for i in range(20):
        if i < 10:
            cmd = [0x80, 0xb0, 0x00, 0x7B + i, 0x02, 0x00, 0xFF]
        else:
            cmd = [0x80, 0xb0, 0x01, 0x7B - (i - 10), 0x02, 0x00, 0xFF]
        photo_commands.append(cmd)

    print("\nReading photo data...")
    for i, cmd in enumerate(photo_commands):
        try:
            data, sw1, sw2 = getData(connection, cmd, req)
            if sw1 == 0x90 and sw2 == 0x00 and data:
                photo_parts.append(data)
                print(f"Photo part {i+1}: {len(data)} bytes")
            else:
                print(f"Photo part {i+1}: Failed or empty")
        except Exception as e:
            print(f"Error reading photo part {i+1}: {e}")

    # Combine photo parts
    if photo_parts:
        try:
            photo_data = b''
            for part in photo_parts:
                photo_data += bytes(part)
            
            # Save photo
            cid = card_data.get("CID", "unknown")
            if cid == "unknown":
                cid = "thai_id_card"
            
            photo_filename = f"{cid}.jpg"
            with open(photo_filename, "wb") as f:
                f.write(photo_data)
            print(f"\nPhoto saved as: {photo_filename}")
            print(f"Photo size: {len(photo_data)} bytes")
            
        except Exception as e:
            print(f"Error saving photo: {e}")
    else:
        print("No photo data could be read")

def main():
    try:
        # Get all the available readers
        readerList = readers()
        if not readerList:
            print("❌ No card readers found. Please check if:")
            print("1. PCSC service is running (pcscd)")
            print("2. Card reader is properly connected")
            print("3. You have proper permissions")
            return
        
        print('📱 Available readers:')
        for readerIndex, readerItem in enumerate(readerList):
            print(f"- {readerIndex}: {readerItem}")

        # Select reader
        readerSelectIndex = 0
        if len(readerList) > 1:
            try:
                readerSelectIndex = int(input("Select reader [0]: ") or "0")
            except ValueError:
                readerSelectIndex = 0
        
        if readerSelectIndex >= len(readerList):
            print("❌ Invalid reader selection")
            return
            
        reader = readerList[readerSelectIndex]
        print(f"✅ Using: {reader}")

        # Try to connect with different protocols and retry logic
        connection = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"\n🔄 Attempt {attempt + 1}/{max_retries} to connect to card...")
                
                # Create new connection for each attempt
                if connection:
                    try:
                        connection.disconnect()
                    except:
                        pass
                
                connection = reader.createConnection()
                
                # Try different connection methods
                connection_methods = [
                    ("Default", None),
                    ("T0", 0),
                    ("T1", 1),
                ]
                
                connected = False
                for method_name, protocol in connection_methods:
                    try:
                        print(f"  🔌 Trying method: {method_name}")
                        if protocol is None:
                            connection.connect()
                        else:
                            connection.connect(protocol)
                        
                        # If we get here, connection was successful
                        print(f"  ✅ Connected successfully with method: {method_name}")
                        connected = True
                        break
                        
                    except CardConnectionException as e:
                        print(f"  ❌ Method {method_name} failed: {e}")
                        continue
                    except Exception as e:
                        print(f"  ❌ Unexpected error with {method_name}: {e}")
                        continue
                
                if connected:
                    break
                else:
                    # All methods failed, try next attempt
                    print(f"  ❌ All methods failed for attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        print("  ⏳ Waiting 2 seconds before retry...")
                        import time
                        time.sleep(2)
                    continue
                
            except Exception as e:
                print(f"  ❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("  ⏳ Waiting 2 seconds before retry...")
                    import time
                    time.sleep(2)
                continue
        
        if not connection:
            print("❌ Failed to connect to card after all attempts")
            return
            
        # Get ATR (Answer To Reset)
        try:
            atr = connection.getATR()
            print(f"🔍 ATR: {toHexString(atr)}")
        except Exception as e:
            print(f"❌ Failed to get ATR: {e}")
            return
        
        # Determine card type and request format
        card_type, req = check_card_type(atr)
        print(f"🎴 Card type detected: {card_type}")
        print(f"📋 Using request format: {toHexString(req)}")

        if card_type == "THAI_ID":
            # Try to read Thai ID card with multiple methods
            try_read_thai_id_card(connection, req)
                
        elif card_type == "EMV_CARD":
            print("\n💳 EMV Card detected (Credit/Debit card)")
            emv_type = detect_emv_card(connection)
            print(f"Card type: {emv_type}")
            print("\n⚠️  This is not a Thai ID card!")
            print("Please insert a Thai ID card to read personal information.")
            print("Credit/Debit cards only contain payment information.")
            
        else:
            print(f"\n❓ Unknown card type: {card_type}")
            print("🔄 Trying to read as Thai ID card anyway...")
            try_read_thai_id_card(connection, req)

    except NoCardException:
        print("❌ No card detected. Please insert a card.")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure the card is fully inserted")
        print("2. Try removing and reinserting the card")
        print("3. Check if the card reader light is on")
        print("4. Try a different card if available")
        
    except CardConnectionException as e:
        print(f"❌ Card connection error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Card is not properly inserted")
        print("2. Card reader is not working properly")
        print("3. Card might be damaged or expired")
        print("4. Try cleaning the card contacts")
        print("5. Check if card reader drivers are installed")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n💡 Please try:")
        print("1. Restart the program")
        print("2. Check card reader connection")
        print("3. Try a different card")
        
    finally:
        try:
            if 'connection' in locals() and connection:
                connection.disconnect()
                print("✅ Card disconnected")
        except:
            pass

if __name__ == "__main__":
    main()