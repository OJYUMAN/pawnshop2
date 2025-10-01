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
        "tb_redeem_contract": "ไถ่ถอน",
        "tb_view_all": "ดูข้อมูลทั้งหมด",
        "tb_view_redemptions": "ดูประวัติการไถ่ถอน",
        "tb_daily_income": "สรุปรายได้รายวัน",
        "tb_fee_management": "ค่าธรรมเนียม",
        "tb_scan_id": "สแกนบัตรประชาชน",
        "tb_toggle_language": "สลับภาษา",

        # Customer Tab
        "customer_search_group": "ค้นหาลูกค้า",
        "customer_code": "รหัสลูกค้า:",
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
        "brand_model": "ยี่ห้อ/รุ่น:",
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
        "tb_toggle_language": "Toggle Language",

        # Customer Tab
        "customer_search_group": "Search Customer",
        "customer_code": "Customer Code:",
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
        "brand_model": "Brand/Model:",
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
        "customer_code": "ລະຫັດລູກຄ້າ:",
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
        "customer_code": "ဈေးသည်ကုဒ်:",
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


