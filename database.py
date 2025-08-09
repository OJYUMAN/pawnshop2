import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class PawnShopDatabase:
    def __init__(self, db_path: str = "pawnshop.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """สร้างตารางฐานข้อมูล"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตารางลูกค้า
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                id_card TEXT UNIQUE,
                address TEXT,
                house_number TEXT,
                street TEXT,
                subdistrict TEXT,
                district TEXT,
                province TEXT,
                phone TEXT,
                other_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางสินค้า
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                size TEXT,
                weight REAL,
                serial_number TEXT,
                other_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางสัญญา
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                pawn_amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                fee_amount REAL NOT NULL,
                total_paid REAL NOT NULL,
                total_redemption REAL NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                days_count INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # ตารางการชำระดอกเบี้ย
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interest_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                interest_amount REAL NOT NULL,
                penalty_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_type TEXT DEFAULT 'interest',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES contracts (id)
            )
        ''')
        
        # ตารางการไถ่ถอน
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS redemptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER NOT NULL,
                redemption_date DATE NOT NULL,
                redemption_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES contracts (id)
            )
        ''')
        
        # ตารางการตั้งค่า
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # เพิ่มข้อมูลเริ่มต้น
        self._insert_default_settings(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_settings(self, cursor):
        """เพิ่มการตั้งค่าเริ่มต้น"""
        default_settings = [
            ('default_interest_rate', '3.0'),
            ('default_contract_days', '30'),
            ('company_name', 'ร้านรับจำนำ อัญชัน'),
            ('company_address', ''),
            ('company_phone', ''),
            ('contract_prefix', '53-10-4-'),
        ]
        
        for key, value in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
    
    def add_customer(self, customer_data: Dict) -> int:
        """เพิ่มลูกค้าใหม่"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers (
                customer_code, first_name, last_name, id_card, address,
                house_number, street, subdistrict, district, province,
                phone, other_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data['customer_code'],
            customer_data['first_name'],
            customer_data['last_name'],
            customer_data.get('id_card', ''),
            customer_data.get('address', ''),
            customer_data.get('house_number', ''),
            customer_data.get('street', ''),
            customer_data.get('subdistrict', ''),
            customer_data.get('district', ''),
            customer_data.get('province', ''),
            customer_data.get('phone', ''),
            customer_data.get('other_details', '')
        ))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id
    
    def add_product(self, product_data: Dict) -> int:
        """เพิ่มสินค้าใหม่"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (
                name, brand, size, weight, serial_number, other_details
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            product_data['name'],
            product_data.get('brand', ''),
            product_data.get('size', ''),
            product_data.get('weight', 0),
            product_data.get('serial_number', ''),
            product_data.get('other_details', '')
        ))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def create_contract(self, contract_data: Dict) -> int:
        """สร้างสัญญาใหม่"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contracts (
                contract_number, customer_id, product_id, pawn_amount,
                interest_rate, fee_amount, total_paid, total_redemption,
                start_date, end_date, days_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contract_data['contract_number'],
            contract_data['customer_id'],
            contract_data['product_id'],
            contract_data['pawn_amount'],
            contract_data['interest_rate'],
            contract_data['fee_amount'],
            contract_data['total_paid'],
            contract_data['total_redemption'],
            contract_data['start_date'],
            contract_data['end_date'],
            contract_data['days_count']
        ))
        
        contract_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contract_id
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """ดึงข้อมูลลูกค้าตาม ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def search_customers(self, search_term: str) -> List[Dict]:
        """ค้นหาลูกค้า"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM customers 
            WHERE first_name LIKE ? OR last_name LIKE ? OR id_card LIKE ? OR customer_code LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    
    def get_contract_by_number(self, contract_number: str) -> Optional[Dict]:
        """ดึงข้อมูลสัญญาตามเลขที่สัญญา"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
            FROM contracts c
            JOIN customers cu ON c.customer_id = cu.id
            JOIN products p ON c.product_id = p.id
            WHERE c.contract_number = ?
        ''', (contract_number,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def search_contracts(self, search_term: str, status: str = 'all') -> List[Dict]:
        """ค้นหาสัญญา"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status == 'all':
            cursor.execute('''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.contract_number LIKE ? OR cu.first_name LIKE ? OR cu.last_name LIKE ? OR cu.id_card LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            cursor.execute('''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE (c.contract_number LIKE ? OR cu.first_name LIKE ? OR cu.last_name LIKE ? OR cu.id_card LIKE ?)
                AND c.status = ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', status))
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    
    def add_interest_payment(self, payment_data: Dict) -> int:
        """เพิ่มการชำระดอกเบี้ย"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interest_payments (
                contract_id, payment_date, interest_amount, penalty_amount,
                discount_amount, total_amount, payment_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_data['contract_id'],
            payment_data['payment_date'],
            payment_data['interest_amount'],
            payment_data.get('penalty_amount', 0),
            payment_data.get('discount_amount', 0),
            payment_data['total_amount'],
            payment_data.get('payment_type', 'interest')
        ))
        
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def redeem_contract(self, redemption_data: Dict) -> int:
        """ไถ่ถอนสัญญา"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # เพิ่มข้อมูลการไถ่ถอน
        cursor.execute('''
            INSERT INTO redemptions (
                contract_id, redemption_date, redemption_amount
            ) VALUES (?, ?, ?)
        ''', (
            redemption_data['contract_id'],
            redemption_data['redemption_date'],
            redemption_data['redemption_amount']
        ))
        
        # อัปเดตสถานะสัญญา
        cursor.execute('''
            UPDATE contracts SET status = 'redeemed' WHERE id = ?
        ''', (redemption_data['contract_id'],))
        
        redemption_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return redemption_id
    
    def get_daily_summary(self, date: str) -> Dict:
        """สรุปรายวัน"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # สัญญาใหม่
        cursor.execute('''
            SELECT COUNT(*), SUM(pawn_amount) FROM contracts 
            WHERE DATE(start_date) = ?
        ''', (date,))
        new_contracts = cursor.fetchone()
        
        # การไถ่ถอน
        cursor.execute('''
            SELECT COUNT(*), SUM(redemption_amount) FROM redemptions 
            WHERE DATE(redemption_date) = ?
        ''', (date,))
        redemptions = cursor.fetchone()
        
        # การชำระดอกเบี้ย
        cursor.execute('''
            SELECT COUNT(*), SUM(total_amount) FROM interest_payments 
            WHERE DATE(payment_date) = ?
        ''', (date,))
        interest_payments = cursor.fetchone()
        
        conn.close()
        
        return {
            'date': date,
            'new_contracts_count': new_contracts[0] or 0,
            'new_contracts_amount': new_contracts[1] or 0,
            'redemptions_count': redemptions[0] or 0,
            'redemptions_amount': redemptions[1] or 0,
            'interest_payments_count': interest_payments[0] or 0,
            'interest_payments_amount': interest_payments[1] or 0
        }
    
    def get_expiring_contracts(self, days: int = 7) -> List[Dict]:
        """ดึงสัญญาที่ใกล้ครบกำหนด"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, cu.first_name, cu.last_name, cu.phone, p.name as product_name
            FROM contracts c
            JOIN customers cu ON c.customer_id = cu.id
            JOIN products p ON c.product_id = p.id
            WHERE c.status = 'active' 
            AND c.end_date BETWEEN DATE('now') AND DATE('now', '+' || ? || ' days')
            ORDER BY c.end_date
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    
    def get_setting(self, key: str) -> str:
        """ดึงการตั้งค่า"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else ''
    
    def update_setting(self, key: str, value: str):
        """อัปเดตการตั้งค่า"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
