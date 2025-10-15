import json
import os
from PySide6.QtCore import QObject, Signal

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

_TRANSLATIONS = {
    "th": {
        # Common
        "ok": "ตกลง",
        "cancel": "ยกเลิก",
        "save": "บันทึก",
        "language": "ภาษา",
        "settings_title": "ตั้งค่า",

        # Toolbar
        "tb_new_contract": "สร้างสัญญาใหม่",
        "tb_clear_form": "ล้างฟอร์ม",
        "tb_save_contract": "บันทึกสัญญา",
        "tb_generate_pawn_pdf": "สร้างใบขายฝาก",
        "tb_extend_interest": "ต่อดอก",
        "tb_generate_renewal_pdf": "สร้างใบฝากต่อ",
        "tb_redeem_contract": "ไถ่คืน",
        "tb_view_all": "ดูข้อมูลทั้งหมด",
        "tb_view_redemptions": "ดูประวัติการไถ่คืน",
        "tb_daily_income": "สรุปรายได้รายวัน",
        "tb_fee_management": "ค่าธรรมเนียม",
        "tb_scan_id": "สแกนบัตรประชาชน",
        "tb_settings": "ตั้งค่า",
        "tb_toggle_language": "สลับภาษา",

        # Customer Tab
        "customer_search_group": "ค้นหาลูกค้า",
        "customer_code": "ชื่อลูกค้า:",
        "search": "ค้นหา",
        "add_new_customer": "เพิ่มลูกค้าใหม่",
        "customer_info_group": "ข้อมูลลูกค้า",
        "borrower_name": "ชื่อผู้กู้:",
        "address": "ที่อยู่:",
        "id_card_short": "บัตร:",
        "id_card_type_citizen": "บัตรประชาชน",
        "id_card_type_driver": "ใบขับขี่",
        "id_card_type_passport": "พาสปอร์ต",
        "house_number": "ที่อยู่บ้านเลขที่:",
        "street": "ซอย/ถนน:",
        "subdistrict": "ตำบล:",
        "district": "อำเภอ:",
        "province": "จังหวัด:",
        "phone": "โทรศัพท์:",
        "other_details": "รายละเอียดอื่นๆ:",
        "customer_add_group": "เพิ่มลูกค้าใหม่",
        "first_name": "ชื่อ:",
        "last_name": "นามสกุล:",
        "id_card_number": "เลขบัตรประชาชน:",

        # Tabs
        "tab_customer": "ข้อมูลลูกค้า",
        "tab_product": "ข้อมูลสินค้าขายฝาก",
        "tab_renewal": "ข้อมูลต่อดอก",

        # Product Tab
        "product_search_group": "ค้นหาสินค้า",
        "product_name": "ชื่อสินค้า:",
        "product_search": "ค้นหา",
        "add_new_product": "เพิ่มสินค้าใหม่",
        "product_info_group": "ข้อมูลสินค้า",
        "pawned_product": "สินค้าฝากขาย:",
        "brand": "ยี่ห้อ:",
        "model": "รุ่น:",
        "brand_model": "ยี่ห้อ/รุ่น:",
        "imei1": "IMEI 1:",
        "imei2": "IMEI 2 (ถ้ามี):",
        "condition": "สภาพเครื่อง:",
        "accessories": "อุปกรณ์ที่มาพร้อมเครื่อง:",
        "size": "ขนาด:",
        "weight": "น้ำหนัก:",
        "unit_gram": "กรัม",
        "unit_kilogram": "กิโลกรัม",
        "unit_baht": "บาท",
        "serial_number": "หมายเลขซีเรียล:",
        "product_other_details": "รายละเอียดอื่นๆ:",
        "product_image": "รูปภาพสินค้า:",
        "no_image": "ไม่มีรูปภาพ",
        "product_add_group": "เพิ่มสินค้าใหม่",
        "choose_file": "เลือกไฟล์",
        "choose_image_placeholder": "เลือกไฟล์รูปภาพ...",
        "image_preview": "ตัวอย่างรูปภาพ:",

        # Right Panel: Contract Info
        "contract_info_group": "ข้อมูลสัญญา",
        "contract_number": "เลขที่สัญญา:",
        "start_date": "วันที่เริ่มต้น:",
        "days": "จำนวนวัน:",
        "end_date": "วันที่สิ้นสุด:",
        "contract_status": "สถานะสัญญา:",
        "status_active": "สัญญาเปิด",
        "status_redeemed": "ไถ่คืนแล้ว",
        "status_lost": "สูญหาย",
        "update_status": "อัปเดตสถานะ",

        # Right Panel: Results
        "results_group": "ผลจัดทำ",
        "pawn_amount": "ยอดฝาก",
        "fee_amount": "ค่าธรรมเนียม",
        "update": "อัปเดต",
        "total_paid": "ยอดจ่าย",
        "total_redemption": "ยอดไถ่คืน",

        # Search Group
        "search_group": "ค้นหาสัญญา",
        "search_by": "ค้นหาตาม:",
        "search_type_contract": "เลขที่สัญญา",
        "search_type_idcard": "เลขบัตรประชาชน",
        "search_type_name": "ชื่อนามสกุล",
        "enter_contract_number": "กรอกเลขที่สัญญา...",
        "enter_id_card": "กรอกเลขบัตรประชาชน...",
        "first_name": "ชื่อ:",
        "last_name": "นามสกุล:",
        "enter_first_name": "กรอกชื่อ...",
        "enter_last_name": "กรอกนามสกุล...",
        "clear_search": "ล้างการค้นหา",
        "status_open": "สัญญาเปิด",
        "status_closed": "สัญญาปิด",
        "all": "ทั้งหมด",

        # Data table headers
        "th_sequence": "ลำดับ",
        "th_contract_no": "เลขที่สัญญา",
        "th_customer_name": "ชื่อลูกค้า",
        "th_product_name": "ชื่อสินค้า",
        "th_pawn_amount": "ยอดจำนำ",
        "th_fee_amount": "ค่าธรรมเนียม",
        "th_start_date": "วันที่เริ่มต้น",
        "th_end_date": "วันที่สิ้นสุด",
        "th_days": "จำนวนวัน",
        "th_interest": "ดอกเบี้ย",
        "th_total": "ยอดรวม",
        "th_status": "สถานะ",

        # Renewal Tab (main page)
        "renewal_history_group": "ประวัติการต่อดอก",
        "renewal_h_seq": "ลำดับ",
        "renewal_h_date": "วันที่ต่อดอก",
        "renewal_h_days": "จำนวนวันต่อ",
        "renewal_h_fee": "ค่าธรรมเนียม",
        "renewal_h_penalty": "ค่าปรับ",
        "renewal_h_discount": "ส่วนลด",
        "renewal_h_total": "ยอดรวม",
        "renewal_h_new_due": "วันที่ครบกำหนดใหม่",
        "renewal_process": "ดำเนินการต่อดอก",
        "clear_form": "ล้างฟอร์ม",

        # Renewal Dialog
        "renewal_title": "ต่อดอก",
        "renewal_info_group": "ข้อมูลสัญญา",
        "renewal_contract_number": "เลขที่สัญญา:",
        "renewal_customer_name": "ชื่อลูกค้า:",
        "renewal_pawn_amount": "ยอดฝาก:",
        "renewal_group": "ข้อมูลการต่อดอก",
        "renewal_days_deposit": "จำนวนวันฝากนับถึงปัจจุบัน:",
        "renewal_count": "ต่อดอกครั้งที่:",
        "renewal_fee": "ค่าธรรมเนียม:",
        "renewal_penalty": "ค่าปรับ:",
        "renewal_discount": "ส่วนลด:",
        "renewal_total": "รวม:",
        "renewal_date": "วันต่อดอก:",
        "renewal_current_due": "วันครบกำหนดปัจจุบัน:",
        "renewal_new_due": "วันครบกำหนดใหม่:",
        "renewal_confirm_text": "คุณต้องการต่อดอกสัญญานี้ใช่หรือไม่",
        "ok": "ตกลง",
        "no": "ไม่ใช่",

        # Redemption Dialog
        "redemption_title": "ไถ่คืน",
        "redemption_date_group": "ข้อมูลวันที่",
        "redemption_deposit_or_extend": "วันที่รับฝาก / ผากต่อ:",
        "redemption_date": "วันที่ไถ่คืน:",
        "redemption_due_date": "วันที่ครบกำหนด:",
        "redemption_total_days": "รวมวันที่ฝากไว้:",
        "redemption_amount_group": "ข้อมูลจำนวนเงิน",
        "redemption_principal": "เงินต้น:",
        "redemption_fee": "ค่าธรรมเนียม:",
        "redemption_penalty": "ค่าปรับ:",
        "redemption_discount": "ส่วนลด:",
        "redemption_total": "รวม:",
        "redemption_confirm": "ต้องการไถ่คืนสัญญานี้ใช่หรือไม่",

        # PDF Settings
        "pdf_settings": "การตั้งค่า PDF",
        "shop_name": "ชื่อร้าน:",
        "shop_branch": "สาขา:",
        "shop_address": "ที่อยู่:",
        "tax_id": "เลขประจำตัวผู้เสียภาษี:",
        "shop_phone": "เบอร์โทรศัพท์:",
        "authorized_signer": "ผู้มีอำนาจลงนาม:",
        "buyer_signer_name": "ชื่อผู้ซื้อฝาก:",
        "witness_name": "ชื่อพยาน:",
    },
    "en": {
        # Common
        "ok": "OK",
        "cancel": "Cancel",
        "save": "Save",
        "language": "Language",
        "settings_title": "Settings",

        # Toolbar
        "tb_new_contract": "New Contract",
        "tb_clear_form": "Clear",
        "tb_save_contract": "Save Contract",
        "tb_generate_pawn_pdf": "Pawn PDF",
        "tb_extend_interest": "Renew",
        "tb_generate_renewal_pdf": "Renewal PDF",
        "tb_redeem_contract": "Redeem",
        "tb_view_all": "View All",
        "tb_view_redemptions": "Redemption History",
        "tb_daily_income": "Daily Income",
        "tb_fee_management": "Fees",
        "tb_scan_id": "Scan ID",
        "tb_settings": "Settings",
        "tb_toggle_language": "Toggle Language",

        # Customer Tab
        "customer_search_group": "Search Customer",
        "customer_code": "Customer Name:",
        "search": "Search",
        "add_new_customer": "Add New Customer",
        "customer_info_group": "Customer Information",
        "borrower_name": "Borrower Name:",
        "address": "Address:",
        "id_card_short": "ID Type:",
        "id_card_type_citizen": "National ID",
        "id_card_type_driver": "Driver License",
        "id_card_type_passport": "Passport",
        "house_number": "House No.:",
        "street": "Lane/Street:",
        "subdistrict": "Subdistrict:",
        "district": "District:",
        "province": "Province:",
        "phone": "Phone:",
        "other_details": "Other Details:",
        "customer_add_group": "Add New Customer",
        "first_name": "First Name:",
        "last_name": "Last Name:",
        "id_card_number": "National ID Number:",

        # Tabs
        "tab_customer": "Customer",
        "tab_product": "Pawned Product",
        "tab_renewal": "Renewal",

        # Product Tab
        "product_search_group": "Search Product",
        "product_name": "Product Name:",
        "product_search": "Search",
        "add_new_product": "Add New Product",
        "product_info_group": "Product Information",
        "pawned_product": "Pawned Product:",
        "brand": "Brand:",
        "model": "Model:",
        "brand_model": "Brand/Model:",
        "imei1": "IMEI 1:",
        "imei2": "IMEI 2 (if available):",
        "condition": "Device Condition:",
        "accessories": "Included Accessories:",
        "size": "Size:",
        "weight": "Weight:",
        "unit_gram": "Gram",
        "unit_kilogram": "Kilogram",
        "unit_baht": "Baht",
        "serial_number": "Serial Number:",
        "product_other_details": "Other Details:",
        "product_image": "Product Image:",
        "no_image": "No Image",
        "product_add_group": "Add New Product",
        "choose_file": "Choose File",
        "choose_image_placeholder": "Choose an image file...",
        "image_preview": "Image Preview:",

        # Right Panel: Contract Info
        "contract_info_group": "Contract Info",
        "contract_number": "Contract No:",
        "start_date": "Start Date:",
        "days": "Days:",
        "end_date": "End Date:",
        "contract_status": "Contract Status:",
        "status_active": "Active",
        "status_redeemed": "Redeemed",
        "status_lost": "Lost",
        "update_status": "Update Status",

        # Right Panel: Results
        "results_group": "Results",
        "pawn_amount": "Pawn Amount",
        "fee_amount": "Fee",
        "update": "Update",
        "total_paid": "Total Paid",
        "total_redemption": "Total Redemption",

        # Search Group
        "search_group": "Search Contracts",
        "search_by": "Search by:",
        "search_type_contract": "Contract No",
        "search_type_idcard": "National ID",
        "search_type_name": "Name",
        "enter_contract_number": "Enter contract no...",
        "enter_id_card": "Enter national ID...",
        "first_name": "First Name:",
        "last_name": "Last Name:",
        "enter_first_name": "Enter first name...",
        "enter_last_name": "Enter last name...",
        "clear_search": "Clear Search",
        "status_open": "Open",
        "status_closed": "Closed",
        "all": "All",

        # Data table headers
        "th_sequence": "#",
        "th_contract_no": "Contract No",
        "th_customer_name": "Customer",
        "th_product_name": "Product",
        "th_pawn_amount": "Pawn Amount",
        "th_fee_amount": "Fee",
        "th_start_date": "Start Date",
        "th_end_date": "End Date",
        "th_days": "Days",
        "th_interest": "Interest",
        "th_total": "Total",
        "th_status": "Status",

        # Renewal Tab (main page)
        "renewal_history_group": "Renewal History",
        "renewal_h_seq": "#",
        "renewal_h_date": "Renewal Date",
        "renewal_h_days": "Days Extended",
        "renewal_h_fee": "Fee",
        "renewal_h_penalty": "Penalty",
        "renewal_h_discount": "Discount",
        "renewal_h_total": "Total",
        "renewal_h_new_due": "New Due Date",
        "renewal_process": "Process Renewal",
        "clear_form": "Clear Form",

        # Renewal Dialog
        "renewal_title": "Renew",
        "renewal_info_group": "Contract Info",
        "renewal_contract_number": "Contract No:",
        "renewal_customer_name": "Customer:",
        "renewal_pawn_amount": "Pawn Amount:",
        "renewal_group": "Renewal Details",
        "renewal_days_deposit": "Days deposited until today:",
        "renewal_count": "Renewal No:",
        "renewal_fee": "Fee:",
        "renewal_penalty": "Penalty:",
        "renewal_discount": "Discount:",
        "renewal_total": "Total:",
        "renewal_date": "Renewal Date:",
        "renewal_current_due": "Current Due Date:",
        "renewal_new_due": "New Due Date:",
        "renewal_confirm_text": "Do you want to renew this contract?",
        "ok": "OK",
        "no": "No",

        # Redemption Dialog
        "redemption_title": "Redeem",
        "redemption_date_group": "Date Information",
        "redemption_deposit_or_extend": "Deposit / Extend Date:",
        "redemption_date": "Redemption Date:",
        "redemption_due_date": "Due Date:",
        "redemption_total_days": "Total Days Deposited:",
        "redemption_amount_group": "Amount Information",
        "redemption_principal": "Principal:",
        "redemption_fee": "Fee:",
        "redemption_penalty": "Penalty:",
        "redemption_discount": "Discount:",
        "redemption_total": "Total:",
        "redemption_confirm": "Do you want to redeem this contract?",

        # PDF Settings
        "pdf_settings": "PDF Settings",
        "shop_name": "Shop Name:",
        "shop_branch": "Branch:",
        "shop_address": "Address:",
        "tax_id": "Tax ID:",
        "shop_phone": "Phone:",
        "authorized_signer": "Authorized Signer:",
        "buyer_signer_name": "Buyer Signer Name:",
        "witness_name": "Witness Name:",
    },
    "lo": {
        # Common
        "ok": "ຕົກລົງ",
        "cancel": "ຍົກເລີກ",
        "save": "ບັນທຶກ",
        "language": "ພາສາ",
        "settings_title": "ການຕັ້ງຄ່າ",

        # Toolbar
        "tb_new_contract": "ສັນຍາໃໝ່",
        "tb_clear_form": "ລ້າງ",
        "tb_save_contract": "ບັນທຶກສັນຍາ",
        "tb_generate_pawn_pdf": "ໃບຂາຍຝາກ",
        "tb_extend_interest": "ຕໍ່ດອກ",
        "tb_generate_renewal_pdf": "ໃບຝາກຕໍ່",
        "tb_redeem_contract": "ໄຖ່ຖອນ",
        "tb_view_all": "ເບິ່ງທັງໝົດ",
        "tb_view_redemptions": "ປະຫວັດໄຖ່ຖອນ",
        "tb_daily_income": "ລາຍຮັບປະຈໍາວັນ",
        "tb_fee_management": "ຄ່າທໍານຽມ",
        "tb_scan_id": "ສະແກນບັດປະຊາຊົນ",
        "tb_toggle_language": "ສະລັບພາສາ",

        # Customer Tab
        "customer_search_group": "ຄົ້ນຫາລູກຄ້າ",
        "customer_code": "ຊື່ລູກຄ້າ:",
        "search": "ຄົ້ນຫາ",
        "add_new_customer": "ເພີ່ມລູກຄ້າໃໝ່",
        "customer_info_group": "ຂໍ້ມູນລູກຄ້າ",
        "borrower_name": "ຊື່ຜູ້ກູ້:",
        "address": "ທີ່ຢູ່:",
        "id_card_short": "ບັດ:",
        "id_card_type_citizen": "ບັດປະຊາຊົນ",
        "id_card_type_driver": "ໃບຂັບຂີ່",
        "id_card_type_passport": "ພາສປອດ",
        "house_number": "ເລກທີ່ບ້ານ:",
        "street": "ຊອຍ/ຖະໜົນ:",
        "subdistrict": "ເມືອງນ້ອຍ:",
        "district": "ເມືອງ:",
        "province": "ແຂວງ:",
        "phone": "ໂທລະສັບ:",
        "other_details": "ລາຍລະອຽດອື່ນໆ:",
        "customer_add_group": "ເພີ່ມລູກຄ້າໃໝ່",
        "first_name": "ຊື່:",
        "last_name": "ນາມສະກຸນ:",
        "id_card_number": "ເລກບັດປະຊາຊົນ:",

        # Tabs
        "tab_customer": "ຂໍ້ມູນລູກຄ້າ",
        "tab_product": "ຂໍ້ມູນສິນຄ້າຝາກຂາຍ",
        "tab_renewal": "ຂໍ້ມູນຕໍ່ດອກ",

        # Product Tab
        "product_search_group": "ຄົ້ນຫາສິນຄ້າ",
        "product_name": "ຊື່ສິນຄ້າ:",
        "product_search": "ຄົ້ນຫາ",
        "add_new_product": "ເພີ່ມສິນຄ້າໃໝ່",
        "product_info_group": "ຂໍ້ມູນສິນຄ້າ",
        "pawned_product": "ສິນຄ້າຝາກຂາຍ:",
        "brand_model": "ຍີ່ຫໍ້/ແບບ:",
        "condition": "ສະພາບເຄື່ອງ:",
        "accessories": "ອຸປະກອນທີ່ມາພ້ອມເຄື່ອງ:",
        "size": "ຂນາດ:",
        "weight": "ນ້ຳໜັກ:",
        "unit_gram": "ກຣາມ",
        "unit_kilogram": "ກິໂລກຣາມ",
        "unit_baht": "ບາດ",
        "serial_number": "ເລກ Serial:",
        "product_other_details": "ລາຍລະອຽດອື່ນໆ:",
        "product_image": "ຮູບພາບສິນຄ້າ:",
        "no_image": "ບໍ່ມີຮູບພາບ",
        "product_add_group": "ເພີ່ມສິນຄ້າໃໝ່",
        "choose_file": "ເລືອກໄຟລ໌",
        "choose_image_placeholder": "ເລືອກໄຟລ໌ຮູບພາບ...",
        "image_preview": "ຕົວຢ່າງຮູບພາບ:",

        # Right Panel: Contract Info
        "contract_info_group": "ຂໍ້ມູນສັນຍາ",
        "contract_number": "ເລກສັນຍາ:",
        "start_date": "ວັນທີ່ເລີ່ມ:",
        "days": "ຈຳນວນວັນ:",
        "end_date": "ວັນທີ່ສິ້ນສຸດ:",
        "contract_status": "ສະຖານະສັນຍາ:",
        "status_active": "ເປີດ",
        "status_redeemed": "ໄຖ່ຖອນແລ້ວ",
        "status_lost": "ສູນຫາຍ",
        "update_status": "ອັບເດດສະຖານະ",

        # Right Panel: Results
        "results_group": "ຜົນຈັດທຳ",
        "pawn_amount": "ຍອດຝາກ",
        "fee_amount": "ຄ່າທຳນຽມ",
        "update": "ອັບເດດ",
        "total_paid": "ຍອດຈ່າຍ",
        "total_redemption": "ຍອດໄຖ່ຖອນ",

        # Search Group
        "search_group": "ຄົ້ນຫາສັນຍາ",
        "search_by": "ຄົ້ນຫາຕາມ:",
        "search_type_contract": "ເລກສັນຍາ",
        "search_type_idcard": "ເລກບັດປະຊາຊົນ",
        "search_type_name": "ຊື່",
        "enter_contract_number": "ປ້ອນເລກສັນຍາ...",
        "enter_id_card": "ປ້ອນເລກບັດ...",
        "first_name": "ຊື່:",
        "last_name": "ນາມສະກຸນ:",
        "enter_first_name": "ປ້ອນຊື່...",
        "enter_last_name": "ປ້ອນນາມສະກຸນ...",
        "clear_search": "ລ້າງການຄົ້ນຫາ",
        "status_open": "ເປີດ",
        "status_closed": "ປິດ",
        "all": "ທັງໝົດ",

        # Data table headers
        "th_sequence": "ລຳດັບ",
        "th_contract_no": "ເລກສັນຍາ",
        "th_customer_name": "ຊື່ລູກຄ້າ",
        "th_product_name": "ຊື່ສິນຄ້າ",
        "th_pawn_amount": "ຍອດຈຳນຳ",
        "th_fee_amount": "ຄ່າທຳນຽມ",
        "th_start_date": "ວັນເລີ່ມ",
        "th_end_date": "ວັນສິ້ນສຸດ",
        "th_days": "ຈຳນວນວັນ",
        "th_interest": "ດອກເບ້ຍ",
        "th_total": "ຍອດລວມ",
        "th_status": "ສະຖານະ",

        # Renewal Tab (main page)
        "renewal_history_group": "ປະຫວັດການຕໍ່ດອກ",
        "renewal_h_seq": "ລຳດັບ",
        "renewal_h_date": "ວັນທີ່ຕໍ່ດອກ",
        "renewal_h_days": "ຈຳນວນວັນຕໍ່",
        "renewal_h_fee": "ຄ່າທຳນຽມ",
        "renewal_h_penalty": "ຄ່າປັບ",
        "renewal_h_discount": "ສ່ວນຫຼຸດ",
        "renewal_h_total": "ຍອດລວມ",
        "renewal_h_new_due": "ວັນຄົບກຳນົດໃໝ່",
        "renewal_process": "ດຳເນີນການຕໍ່ດອກ",
        "clear_form": "ລ້າງແບບຟອມ",

        # Renewal Dialog
        "renewal_title": "ຕໍ່ດອກ",
        "renewal_info_group": "ຂໍ້ມູນສັນຍາ",
        "renewal_contract_number": "ເລກສັນຍາ:",
        "renewal_customer_name": "ລູກຄ້າ:",
        "renewal_pawn_amount": "ຍອດຝາກ:",
        "renewal_group": "ລາຍລະອຽດການຕໍ່ດອກ",
        "renewal_days_deposit": "ຈຳນວນວັນຝາກຮອດມື້ນີ້:",
        "renewal_count": "ຕໍ່ດອກຄັ້ງທີ:",
        "renewal_fee": "ຄ່າທຳນຽມ:",
        "renewal_penalty": "ຄ່າປັບ:",
        "renewal_discount": "ສ່ວນຫຼຸດ:",
        "renewal_total": "ລວມ:",
        "renewal_date": "ວັນຕໍ່ດອກ:",
        "renewal_current_due": "ວັນຄົບກຳນົດປັດຈຸບັນ:",
        "renewal_new_due": "ວັນຄົບກຳນົດໃໝ່:",
        "renewal_confirm_text": "ທ່ານຕ້ອງການຕໍ່ດອກສັນຍານີ້ບໍ?",
        "ok": "ຕົກລົງ",
        "no": "ບໍ່ແມ່ນ",

        # Redemption Dialog
        "redemption_title": "ໄຖ່ຖອນ",
        "redemption_date_group": "ຂໍ້ມູນວັນທີ",
        "redemption_deposit_or_extend": "ວັນທີຮັບຝາກ / ຝາກຕໍ່:",
        "redemption_date": "ວັນທີໄຖ່ຖອນ:",
        "redemption_due_date": "ວັນຄົບກຳນົດ:",
        "redemption_total_days": "ລວມວັນທີ່ຝາກໄວ້:",
        "redemption_amount_group": "ຂໍ້ມູນຈຳນວນເງິນ",
        "redemption_principal": "ເງິນຕົ້ນ:",
        "redemption_fee": "ຄ່າທຳນຽມ:",
        "redemption_penalty": "ຄ່າປັບ:",
        "redemption_discount": "ສ່ວນຫຼຸດ:",
        "redemption_total": "ລວມ:",
        "redemption_confirm": "ຕ້ອງການໄຖ່ຖອນສັນຍານີ້ບໍ?",
    },
    "my": {
        # Common
        "ok": "အိုကေ",
        "cancel": "မလုပ်တော့",
        "save": "သိမ်းမည်",
        "language": "ဘာသာစကား",
        "settings_title": "ဆက်တင်များ",

        # Toolbar
        "tb_new_contract": "စာချုပ်အသစ်",
        "tb_clear_form": "ရှင်းလင်း",
        "tb_save_contract": "စာချုပ် သိမ်းမည်",
        "tb_generate_pawn_pdf": "Pawn PDF",
        "tb_extend_interest": "တိုးချဲ့",
        "tb_generate_renewal_pdf": "တိုးချဲ့ PDF",
        "tb_redeem_contract": "ပြန်ရယူ",
        "tb_view_all": "အားလုံးကြည့်မည်",
        "tb_view_redemptions": "ပြန်ရယူမှတ်တမ်း",
        "tb_daily_income": "နေ့စဉ် ဝင်ငွေ",
        "tb_fee_management": "ကြေးသတ်မှတ်",
        "tb_scan_id": "ID ကတ် စကန်",
        "tb_toggle_language": "ဘာသာစကားပြောင်း",

        # Customer Tab
        "customer_search_group": "ဈေးသည်ရှာဖွေ",
        "customer_code": "ဈေးသည်အမည်:",
        "search": "ရှာဖွေ",
        "add_new_customer": "ဈေးသည်အသစ်ထည့်",
        "customer_info_group": "ဈေးသည်အချက်အလက်",
        "borrower_name": "အပေးအယူရှင်:",
        "address": "လိပ်စာ:",
        "id_card_short": "ကတ်:",
        "id_card_type_citizen": "အမျိုးသားကတ်",
        "id_card_type_driver": "ယာဉ်မောင်းလိုင်စင်",
        "id_card_type_passport": "နိုင်ငံကူးလက်မှတ်",
        "house_number": "အိမ်အမှတ်:",
        "street": "လမ်း/巷:",
        "subdistrict": "မြို့နယ်သစ်:",
        "district": "မြို့နယ်:",
        "province": "တိုင်း/ပြည်နယ်:",
        "phone": "ဖုန်း:",
        "other_details": "အသေးစိတ် အခြား:",
        "customer_add_group": "ဈေးသည်အသစ်ထည့်",
        "first_name": "နာမည်:",
        "last_name": "အမျိုးအမည်:",
        "id_card_number": "အမျိုးသားကတ်နံပါတ်:",

        # Tabs
        "tab_customer": "ဈေးသည်",
        "tab_product": "သောင်ချေးထားသည့်ပစ္စည်း",
        "tab_renewal": "တိုးချဲ့",

        # Product Tab
        "product_search_group": "ကုန်ပစ္စည်း ရှာဖွေ",
        "product_name": "ကုန်ပစ္စည်းအမည်:",
        "product_search": "ရှာဖွေ",
        "add_new_product": "ကုန်ပစ္စည်းအသစ် ထည့်",
        "product_info_group": "ကုန်ပစ္စည်း အချက်အလက်",
        "pawned_product": "အပေါင်ထားကုန်ပစ္စည်း:",
        "brand_model": "အမှတ်တံဆိပ်/မော်ဒယ်:",
        "condition": "ကိရိယာအခြေအနေ:",
        "accessories": "ကိရိယာနှင့်အတူပါလာသောပစ္စည်းများ:",
        "size": "အရွယ်အစား:",
        "weight": "အလေးချိန်:",
        "unit_gram": "ဂရမ်",
        "unit_kilogram": "ကီလိုဂရမ်",
        "unit_baht": "ဘတ်",
        "serial_number": "Serial နံပါတ်:",
        "product_other_details": "အသေးစိတ် အခြား:",
        "product_image": "ကုန်ပစ္စည်း ဓာတ်ပုံ:",
        "no_image": "ဓာတ်ပုံမရှိ",
        "product_add_group": "ကုန်ပစ္စည်းအသစ် ထည့်",
        "choose_file": "ဖိုင်ရွေးရန်",
        "choose_image_placeholder": "ဓာတ်ပုံဖိုင် ရွေးပါ...",
        "image_preview": "ဓာတ်ပုံ အမျိုးအစား:",

        # Right Panel: Contract Info
        "contract_info_group": "စာချုပ် အချက်အလက်",
        "contract_number": "စာချုပ်နံပါတ်:",
        "start_date": "စတင်သည့်ရက်:",
        "days": "ရက်များ:",
        "end_date": "ပြီးဆုံးသည့်ရက်:",
        "contract_status": "စာချုပ်အနေအထား:",
        "status_active": "ဖွင့်",
        "status_redeemed": "ပြန်ရယူပြီး",
        "status_lost": "ဆုံးရှုံး",
        "update_status": "အနေအထား အပ်ဒိတ်",

        # Right Panel: Results
        "results_group": "ရလဒ်",
        "pawn_amount": "အပေါင်ငွေ",
        "fee_amount": "ကြေး",
        "update": "အပ်ဒိတ်",
        "total_paid": "ပေးသွက်စုစုပေါင်း",
        "total_redemption": "ပြန်ရယူစုစုပေါင်း",

        # Search Group
        "search_group": "စာချုပ် ရှာဖွေ",
        "search_by": "ရှာဖွေခြင်း:",
        "search_type_contract": "စာချုပ်နံပါတ်",
        "search_type_idcard": "အမျိုးသားကတ်",
        "search_type_name": "အမည်",
        "enter_contract_number": "စာချုပ်နံပါတ် ထည့်ပါ...",
        "enter_id_card": "အမျိုးသားကတ်နံပါတ် ထည့်ပါ...",
        "first_name": "နာမည်:",
        "last_name": "အမျိုးအမည်:",
        "enter_first_name": "နာမည် ထည့်ပါ...",
        "enter_last_name": "အမျိုးအမည် ထည့်ပါ...",
        "clear_search": "ရှာဖွေမှုကို ဖြုတ်",
        "status_open": "ဖွင့်",
        "status_closed": "ပိတ်",
        "all": "အားလုံး",

        # Data table headers
        "th_sequence": "စဉ်",
        "th_contract_no": "စာချုပ်နံပါတ်",
        "th_customer_name": "ဈေးသည်",
        "th_product_name": "ကုန်ပစ္စည်း",
        "th_pawn_amount": "အပေါင်ငွေ",
        "th_fee_amount": "ကြေး",
        "th_start_date": "စတင်ရက်",
        "th_end_date": "ပြီးဆုံးရက်",
        "th_days": "ရက်",
        "th_interest": "အတိုး",
        "th_total": "စုစုပေါင်း",
        "th_status": "အနေအထား",

        # Renewal Tab (main page)
        "renewal_history_group": "တိုးချဲ့ မှတ်တမ်း",
        "renewal_h_seq": "စဉ်",
        "renewal_h_date": "တိုးချဲ့ရက်",
        "renewal_h_days": "တိုးချဲ့ရက်အရေအတွက်",
        "renewal_h_fee": "ကြေး",
        "renewal_h_penalty": "ပြစ်ဒဏ်",
        "renewal_h_discount": "လျော့စျေး",
        "renewal_h_total": "စုစုပေါင်း",
        "renewal_h_new_due": "သတ်မှတ်ပြီးရက်အသစ်",
        "renewal_process": "တိုးချဲ့လုပ်ဆောင်ခြင်း",
        "clear_form": "ဖောင် ရှင်းလင်း",

        # Renewal Dialog
        "renewal_title": "တိုးချဲ့",
        "renewal_info_group": "စာချုပ် အချက်အလက်",
        "renewal_contract_number": "စာချုပ်နံပါတ်:",
        "renewal_customer_name": "ဈေးသည်:",
        "renewal_pawn_amount": "အပေါင်ငွေ:",
        "renewal_group": "တိုးချဲ့ အသေးစိတ်",
        "renewal_days_deposit": "ယေန့ထိ ငွေစောင့်ရက်:",
        "renewal_count": "တိုးချဲ့ အကြိမ်:",
        "renewal_fee": "ကြေး:",
        "renewal_penalty": "ပြစ်ဒဏ်:",
        "renewal_discount": "လျော့စျေး:",
        "renewal_total": "စုစုပေါင်း:",
        "renewal_date": "တိုးချဲ့ရက်:",
        "renewal_current_due": "လက်ရှိ သတ်မှတ်ရက်:",
        "renewal_new_due": "သတ်မှတ်ရက်အသစ်:",
        "renewal_confirm_text": "ဤစာချုပ်ကို တိုးချဲ့မည်လား?",
        "ok": "အိုကေ",
        "no": "မဟုတ်ပါ",

        # Redemption Dialog
        "redemption_title": "ပြန်ရယူ",
        "redemption_date_group": "ရက်စွဲ အချက်အလက်",
        "redemption_deposit_or_extend": "အပေါင် / တိုးချဲ့ ရက်:",
        "redemption_date": "ပြန်ရယူရက်:",
        "redemption_due_date": "ဆုံးရက်:",
        "redemption_total_days": "စုစုပေါင်းသိုလှောင်ရက်:",
        "redemption_amount_group": "ငွေပမာဏ အချက်အလက်",
        "redemption_principal": "ရင်းနှီးငွေ:",
        "redemption_fee": "ကြေး:",
        "redemption_penalty": "ပြစ်ဒဏ်:",
        "redemption_discount": "လျော့စျေး:",
        "redemption_total": "စုစုပေါင်း:",
        "redemption_confirm": "ဤစာချုပ်ကို ပြန်ရယူမည်လား?",
    },
}


class LanguageManager(QObject):
    language_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._current_language = "th"
        self._language_order = ["th", "en", "lo", "my"]
        self._load_language_from_config()

    def _load_language_from_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    lang = data.get("language")
                    if lang in _TRANSLATIONS:
                        self._current_language = lang
        except Exception:
            pass

    def _save_language_to_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"language": self._current_language}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_current_language(self) -> str:
        return self._current_language

    def set_language(self, language: str):
        if language not in _TRANSLATIONS:
            return
        if language != self._current_language:
            self._current_language = language
            self._save_language_to_config()
            self.language_changed.emit(language)

    def toggle_language(self):
        try:
            idx = self._language_order.index(self._current_language)
        except ValueError:
            idx = 0
        next_lang = self._language_order[(idx + 1) % len(self._language_order)]
        self.set_language(next_lang)

    def get_text(self, key: str) -> str:
        return _TRANSLATIONS.get(self._current_language, {}).get(key, key)

    def get_available_languages(self):
        return list(self._language_order)


language_manager = LanguageManager()


