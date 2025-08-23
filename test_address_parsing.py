#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบการแยกชื่อ-นามสกุลและที่อยู่จากบัตรประชาชน
"""

import re

def parse_thai_name(full_name):
    """แยกชื่อและนามสกุลไทย"""
    print(f"=== ทดสอบการแยกชื่อ: {full_name} ===")
    
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
    
    print(f"คำนำหน้า: {prefix}")
    print(f"ชื่อที่ไม่มีคำนำหน้า: {name_without_prefix}")
    
    # แยกชื่อและนามสกุล
    name_parts = name_without_prefix.split()
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        # รวมคำนำหน้าเข้ากับชื่อ
        if prefix:
            result_first_name = f"{prefix} {first_name}"
        else:
            result_first_name = first_name
        result_last_name = last_name
        print(f"ชื่อ: {result_first_name}")
        print(f"นามสกุล: {result_last_name}")
    else:
        if prefix:
            result_first_name = f"{prefix} {full_name}"
        else:
            result_first_name = full_name
        result_last_name = ""
        print(f"ชื่อ: {result_first_name}")
        print(f"นามสกุล: {result_last_name}")
    
    print()
    return result_first_name, result_last_name

def parse_thai_address(address):
    """แยกที่อยู่ไทยเป็นส่วนๆ"""
    print(f"=== ทดสอบการแยกที่อยู่: {address} ===")
    
    address_parts = {}
    
    try:
        # ลบช่องว่างที่ไม่จำเป็น
        address = " ".join(address.split())
        print(f"ที่อยู่ที่ทำความสะอาดแล้ว: {address}")
        
        # แยกบ้านเลขที่ (มักอยู่ต้นข้อความ)
        house_match = re.match(r'^(\d+)\s*', address)
        if house_match:
            address_parts["house_number"] = house_match.group(1)
            address = address[house_match.end():].strip()
            print(f"บ้านเลขที่: {address_parts['house_number']}")
            print(f"ที่เหลือหลังจากแยกบ้านเลขที่: {address}")
        
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
                print(f"จังหวัด: {province}")
                # ตัดจังหวัดออกจากที่อยู่
                address = address.replace(province, "").strip()
                print(f"ที่เหลือหลังจากแยกจังหวัด: {address}")
                break
        
        # แยกเขต/อำเภอ (มักมีคำว่า "เขต" หรือ "อำเภอ")
        district_match = re.search(r'(เขต|อำเภอ)\s*([^\s]+)', address)
        if district_match:
            district_type = district_match.group(1)
            district_name = district_match.group(2)
            address_parts["district"] = f"{district_type}{district_name}"
            print(f"เขต/อำเภอ: {address_parts['district']}")
            # ตัดเขต/อำเภอออกจากที่อยู่
            address = address.replace(district_match.group(0), "").strip()
            print(f"ที่เหลือหลังจากแยกเขต/อำเภอ: {address}")
        
        # แยกแขวง/ตำบล (มักมีคำว่า "แขวง" หรือ "ตำบล")
        subdistrict_match = re.search(r'(แขวง|ตำบล)\s*([^\s]+)', address)
        if subdistrict_match:
            subdistrict_type = subdistrict_match.group(1)
            subdistrict_name = subdistrict_match.group(2)
            address_parts["subdistrict"] = f"{subdistrict_type}{subdistrict_name}"
            print(f"แขวง/ตำบล: {address_parts['subdistrict']}")
            # ตัดแขวง/ตำบลออกจากที่อยู่
            address = address.replace(subdistrict_match.group(0), "").strip()
            print(f"ที่เหลือหลังจากแยกแขวง/ตำบล: {address}")
        
        # แยกถนน/ซอย
        street_match = re.search(r'(ถนน|ซอย)\s*([^\s]+)', address)
        if street_match:
            street_type = street_match.group(1)
            street_name = street_match.group(2)
            address_parts["street"] = f"{street_type}{street_name}"
            print(f"ถนน/ซอย: {address_parts['street']}")
            # ตัดถนน/ซอยออกจากที่อยู่
            address = address.replace(street_match.group(0), "").strip()
            print(f"ที่เหลือหลังจากแยกถนน/ซอย: {address}")
        
        # ที่เหลือเก็บใน remaining
        if address.strip():
            address_parts["remaining"] = address.strip()
            print(f"ที่เหลือ: {address_parts['remaining']}")
        
        print(f"\nสรุปการแยกที่อยู่:")
        for key, value in address_parts.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error parsing address: {e}")
        # หากแยกไม่ได้ ให้เก็บทั้งหมดใน remaining
        address_parts["remaining"] = address
    
    print()
    return address_parts

def main():
    """ฟังก์ชันหลัก"""
    print("=== ทดสอบการแยกชื่อ-นามสกุลและที่อยู่จากบัตรประชาชน ===\n")
    
    # ทดสอบการแยกชื่อ-นามสกุล
    test_names = [
        "นางสาว ปาริชาต  ตรีมาศ",
        "นาย สมชาย ใจดี",
        "สมหญิง รักดี",
        "นางสาว สมหญิง สวยงาม"
    ]
    
    for name in test_names:
        parse_thai_name(name)
    
    # ทดสอบการแยกที่อยู่
    test_addresses = [
        "83   ซอยประเสริฐมนูกิจ 14 ถนนประเสริฐมนูกิจ แขวงจรเข้บัว เขตลาดพร้าว กรุงเทพมหานคร",
        "123 ถนนสุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพมหานคร",
        "456 ซอยลาดพร้าว 1 แขวงลาดพร้าว เขตลาดพร้าว กรุงเทพมหานคร"
    ]
    
    for address in test_addresses:
        parse_thai_address(address)
    
    print("=== การทดสอบเสร็จสิ้น ===")

if __name__ == "__main__":
    main()
