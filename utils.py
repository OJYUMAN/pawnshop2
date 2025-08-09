from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import re

class PawnShopUtils:
    @staticmethod
    def calculate_interest(principal: float, rate: float, days: int) -> float:
        """คำนวณดอกเบี้ย"""
        return (principal * rate * days) / 100
    
    @staticmethod
    def calculate_penalty(principal: float, overdue_days: int, penalty_rate: float = 1.0) -> float:
        """คำนวณค่าปรับ"""
        return (principal * penalty_rate * overdue_days) / 100
    
    @staticmethod
    def generate_contract_number(prefix: str, sequence: int) -> str:
        """สร้างเลขที่สัญญา"""
        return f"{prefix}{sequence:04d}"
    
    @staticmethod
    def generate_customer_code(prefix: str = "C", sequence: int = 1) -> str:
        """สร้างรหัสลูกค้า"""
        return f"{prefix}{sequence:04d}"
    
    @staticmethod
    def calculate_contract_dates(start_date: datetime, days: int) -> Tuple[datetime, datetime]:
        """คำนวณวันที่เริ่มต้นและสิ้นสุดสัญญา"""
        end_date = start_date + timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def calculate_total_redemption(pawn_amount: float, interest_amount: float, 
                                 penalty_amount: float = 0, discount_amount: float = 0) -> float:
        """คำนวณยอดไถ่ถอนรวม"""
        return pawn_amount + interest_amount + penalty_amount - discount_amount
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """จัดรูปแบบเงิน"""
        return f"{amount:,.2f}"
    
    @staticmethod
    def format_date(date: datetime) -> str:
        """จัดรูปแบบวันที่"""
        return date.strftime("%d/%m/%Y")
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """แปลงสตริงเป็นวันที่"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return datetime.now()
    
    @staticmethod
    def validate_id_card(id_card: str) -> bool:
        """ตรวจสอบเลขบัตรประชาชน"""
        if not id_card or len(id_card) != 13:
            return False
        
        try:
            digits = [int(d) for d in id_card]
        except ValueError:
            return False
        
        # คำนวณ checksum
        sum_val = 0
        for i in range(12):
            sum_val += digits[i] * (13 - i)
        
        check_digit = (11 - (sum_val % 11)) % 10
        return check_digit == digits[12]
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """ตรวจสอบเบอร์โทรศัพท์"""
        # ลบช่องว่างและเครื่องหมาย
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # ตรวจสอบรูปแบบเบอร์โทรศัพท์ไทย
        patterns = [
            r'^0[689]\d{8}$',  # เบอร์มือถือ
            r'^0[234567]\d{7}$',  # เบอร์บ้าน
        ]
        
        for pattern in patterns:
            if re.match(pattern, phone):
                return True
        
        return False
    
    @staticmethod
    def calculate_interest_schedule(contract_data: Dict) -> List[Dict]:
        """คำนวณตารางดอกเบี้ย"""
        schedule = []
        start_date = contract_data['start_date']
        end_date = contract_data['end_date']
        principal = contract_data['pawn_amount']
        rate = contract_data['interest_rate']
        
        current_date = start_date
        sequence = 1
        
        while current_date <= end_date:
            # คำนวณวันที่ครบกำหนด
            due_date = current_date + timedelta(days=30)
            
            # คำนวณดอกเบี้ย
            interest_amount = PawnShopUtils.calculate_interest(principal, rate, 30)
            
            # คำนวณค่าปรับ (ถ้าครบกำหนดแล้ว)
            penalty_amount = 0
            if due_date < datetime.now():
                overdue_days = (datetime.now() - due_date).days
                penalty_amount = PawnShopUtils.calculate_penalty(principal, overdue_days)
            
            schedule.append({
                'sequence': sequence,
                'due_date': due_date,
                'interest_amount': interest_amount,
                'penalty_amount': penalty_amount,
                'discount_amount': 0,
                'total_amount': interest_amount + penalty_amount
            })
            
            current_date = due_date
            sequence += 1
        
        return schedule
    
    @staticmethod
    def calculate_overdue_amount(contract_data: Dict) -> Dict:
        """คำนวณยอดค้างชำระ"""
        today = datetime.now()
        end_date = contract_data['end_date']
        
        if today <= end_date:
            return {
                'is_overdue': False,
                'overdue_days': 0,
                'penalty_amount': 0
            }
        
        overdue_days = (today - end_date).days
        penalty_amount = PawnShopUtils.calculate_penalty(
            contract_data['pawn_amount'], 
            overdue_days
        )
        
        return {
            'is_overdue': True,
            'overdue_days': overdue_days,
            'penalty_amount': penalty_amount
        }
    
    @staticmethod
    def format_thai_date(date: datetime) -> str:
        """จัดรูปแบบวันที่ภาษาไทย"""
        thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        
        day = date.day
        month = thai_months[date.month - 1]
        year = date.year + 543  # แปลงเป็น พ.ศ.
        
        return f"{day} {month} {year}"
    
    @staticmethod
    def calculate_monthly_summary(year: int, month: int, db) -> Dict:
        """คำนวณสรุปรายเดือน"""
        # สัญญาใหม่
        new_contracts = db.execute('''
            SELECT COUNT(*), SUM(pawn_amount) FROM contracts 
            WHERE strftime('%Y-%m', start_date) = ?
        ''', (f"{year:04d}-{month:02d}",)).fetchone()
        
        # การไถ่ถอน
        redemptions = db.execute('''
            SELECT COUNT(*), SUM(redemption_amount) FROM redemptions 
            WHERE strftime('%Y-%m', redemption_date) = ?
        ''', (f"{year:04d}-{month:02d}",)).fetchone()
        
        # การชำระดอกเบี้ย
        interest_payments = db.execute('''
            SELECT COUNT(*), SUM(total_amount) FROM interest_payments 
            WHERE strftime('%Y-%m', payment_date) = ?
        ''', (f"{year:04d}-{month:02d}",)).fetchone()
        
        return {
            'year': year,
            'month': month,
            'new_contracts_count': new_contracts[0] or 0,
            'new_contracts_amount': new_contracts[1] or 0,
            'redemptions_count': redemptions[0] or 0,
            'redemptions_amount': redemptions[1] or 0,
            'interest_payments_count': interest_payments[0] or 0,
            'interest_payments_amount': interest_payments[1] or 0
        }
    
    @staticmethod
    def backup_database(source_path: str, backup_path: str) -> bool:
        """สำรองฐานข้อมูล"""
        try:
            import shutil
            shutil.copy2(source_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
    
    @staticmethod
    def restore_database(backup_path: str, target_path: str) -> bool:
        """กู้คืนฐานข้อมูล"""
        try:
            import shutil
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False
