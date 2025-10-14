# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

class PawnShopDatabase:
    def __init__(self, db_path: str = "pawnshop.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager สำหรับการจัดการ database connection"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=20.0)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def init_database(self):
        """สร้างตารางฐานข้อมูล"""
        with self.get_connection() as conn:
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
                    model TEXT,
                    size TEXT,
                    weight REAL,
                    weight_unit TEXT,
                    serial_number TEXT,
                    imei1 TEXT,
                    imei2 TEXT,
                    condition TEXT,
                    accessories TEXT,
                    other_details TEXT,
                    image_path TEXT,
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
                    withholding_tax_rate REAL DEFAULT 0.0,
                    withholding_tax_amount REAL DEFAULT 0.0,
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
            
            # ตารางค่าธรรมเนียม
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fee_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    days_count INTEGER NOT NULL UNIQUE,
                    fee_rate REAL NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # ตารางการต่อดอก
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS renewals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id INTEGER NOT NULL,
                    renewal_count INTEGER NOT NULL,
                    fee_amount REAL DEFAULT 0,
                    penalty_amount REAL DEFAULT 0,
                    discount_amount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    renewal_date DATE NOT NULL,
                    current_due_date DATE NOT NULL,
                    new_due_date DATE NOT NULL,
                    deposit_days INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contract_id) REFERENCES contracts (id)
                )
            ''')
            
            # ตารางการไถ่คืน
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS redemptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id INTEGER NOT NULL,
                    redemption_date DATE NOT NULL,
                    redemption_amount REAL NOT NULL,
                    deposit_date DATE,
                    due_date DATE,
                    total_days INTEGER,
                    principal_amount REAL,
                    fee_amount REAL,
                    penalty_amount REAL,
                    discount_amount REAL,
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
            
            # อัปเกรดฐานข้อมูลเพื่อเพิ่มคอลัมน์ที่ขาดหายไป
            self.upgrade_database(cursor)
            
            # เพิ่มข้อมูลเริ่มต้น
            self._insert_default_settings(cursor)
            
            # เพิ่มข้อมูลค่าธรรมเนียมเริ่มต้น
            self._insert_default_fee_rates(cursor)
            
            conn.commit()
    
    def upgrade_database(self, cursor):
        """อัปเกรดฐานข้อมูลโดยเพิ่มคอลัมน์ใหม่"""
        try:
            # ตรวจสอบและเพิ่มคอลัมน์ weight_unit ในตาราง products
            cursor.execute("PRAGMA table_info(products)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'weight_unit' not in columns:
                cursor.execute('ALTER TABLE products ADD COLUMN weight_unit TEXT')
                print("Added weight_unit column to products table")
            
            if 'image_path' not in columns:
                cursor.execute('ALTER TABLE products ADD COLUMN image_path TEXT')
                print("Added image_path column to products table")
            
            # เพิ่มคอลัมน์ใหม่สำหรับข้อมูลสินค้าตามฟอร์มใหม่
            new_columns = [
                ('model', 'TEXT'),
                ('imei1', 'TEXT'),
                ('imei2', 'TEXT'),
                ('condition', 'TEXT'),
                ('accessories', 'TEXT')
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    cursor.execute(f'ALTER TABLE products ADD COLUMN {column_name} {column_type}')
                    print(f"Added {column_name} column to products table")
            
            # ตรวจสอบและเพิ่มคอลัมน์ใหม่ในตาราง redemptions
            cursor.execute("PRAGMA table_info(redemptions)")
            redemption_columns = [column[1] for column in cursor.fetchall()]
            
            new_redemption_columns = [
                ('deposit_date', 'DATE'),
                ('due_date', 'DATE'),
                ('total_days', 'INTEGER'),
                ('principal_amount', 'REAL'),
                ('fee_amount', 'REAL'),
                ('penalty_amount', 'REAL'),
                ('discount_amount', 'REAL')
            ]
            
            for col_name, col_type in new_redemption_columns:
                if col_name not in redemption_columns:
                    cursor.execute(f'ALTER TABLE redemptions ADD COLUMN {col_name} {col_type}')
                    print(f"Added {col_name} column to redemptions table")
                
        except Exception as e:
            print(f"Error upgrading database: {e}")
    
    def _insert_default_settings(self, cursor):
        """เพิ่มการตั้งค่าเริ่มต้น"""
        default_settings = [
            ('default_interest_rate', '3.0'),
            ('default_contract_days', '30'),
            ('default_withholding_tax_rate', '3.0'),
            ('company_name', 'ร้านรับจำนำ อัญชัน'),
            ('company_address', ''),
            ('company_phone', ''),
            ('contract_prefix', '53-10-4-'),
            ('customer_prefix', 'C'),
        ]
        
        for key, value in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
    
    def _insert_default_fee_rates(self, cursor):
        """เพิ่มข้อมูลค่าธรรมเนียมเริ่มต้น"""
        # ตรวจสอบว่ามีข้อมูลค่าธรรมเนียมแล้วหรือไม่
        cursor.execute("SELECT COUNT(*) FROM fee_rates")
        if cursor.fetchone()[0] == 0:
            default_fee_rates = [
                (5, 1.5, 'ค่าธรรมเนียม 5 วัน'),
                (10, 2.0, 'ค่าธรรมเนียม 10 วัน'),
                (15, 2.5, 'ค่าธรรมเนียม 15 วัน'),
                (30, 3.0, 'ค่าธรรมเนียม 30 วัน'),
                (45, 6.0, 'ค่าธรรมเนียม 45 วัน')
            ]
            
            for days, rate, description in default_fee_rates:
                cursor.execute('''
                    INSERT INTO fee_rates (days_count, fee_rate, description) 
                    VALUES (?, ?, ?)
                ''', (days, rate, description))
    
    def add_customer(self, customer_data: Dict) -> int:
        """เพิ่มลูกค้าใหม่"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ตรวจสอบความซ้ำซ้อนก่อนเพิ่มข้อมูล
            if customer_data.get('customer_code'):
                cursor.execute('SELECT COUNT(*) FROM customers WHERE customer_code = ?', (customer_data['customer_code'],))
                if cursor.fetchone()[0] > 0:
                    raise ValueError(f"รหัสลูกค้า {customer_data['customer_code']} มีอยู่ในระบบแล้ว")
            
            if customer_data.get('id_card'):
                cursor.execute('SELECT COUNT(*) FROM customers WHERE id_card = ?', (customer_data['id_card'],))
                if cursor.fetchone()[0] > 0:
                    raise ValueError(f"เลขบัตรประชาชน {customer_data['id_card']} มีอยู่ในระบบแล้ว")
            
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
            return customer_id
    
    def add_product(self, product_data: Dict) -> int:
        """เพิ่มสินค้าใหม่"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO products (
                    name, brand, size, weight, weight_unit, serial_number, other_details, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data['name'],
                product_data.get('brand', ''),
                product_data.get('size', ''),
                product_data.get('weight', 0),
                product_data.get('weight_unit', ''),
                product_data.get('serial_number', ''),
                product_data.get('other_details', ''),
                product_data.get('image_path', '')
            ))
            
            product_id = cursor.lastrowid
            conn.commit()
            return product_id
    
    def create_contract(self, contract_data: Dict) -> int:
        """สร้างสัญญาใหม่"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO contracts (
                    contract_number, customer_id, product_id, pawn_amount,
                    interest_rate, fee_amount, withholding_tax_rate, withholding_tax_amount,
                    total_paid, total_redemption, start_date, end_date, days_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_data['contract_number'],
                contract_data['customer_id'],
                contract_data['product_id'],
                contract_data['pawn_amount'],
                contract_data['interest_rate'],
                contract_data['fee_amount'],
                contract_data.get('withholding_tax_rate', 0.0),
                contract_data.get('withholding_tax_amount', 0.0),
                contract_data['total_paid'],
                contract_data['total_redemption'],
                contract_data['start_date'],
                contract_data['end_date'],
                contract_data['days_count']
            ))
            
            contract_id = cursor.lastrowid
            conn.commit()
            return contract_id
    
    def update_contract(self, contract_data: Dict) -> int:
        """อัพเดทสัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE contracts SET
                    customer_id = ?, product_id = ?, pawn_amount = ?,
                    interest_rate = ?, fee_amount = ?, withholding_tax_rate = ?, 
                    withholding_tax_amount = ?, total_paid = ?, total_redemption = ?, 
                    start_date = ?, end_date = ?, days_count = ?
                WHERE id = ?
            ''', (
                contract_data['customer_id'],
                contract_data['product_id'],
                contract_data['pawn_amount'],
                contract_data['interest_rate'],
                contract_data['fee_amount'],
                contract_data.get('withholding_tax_rate', 0.0),
                contract_data.get('withholding_tax_amount', 0.0),
                contract_data['total_paid'],
                contract_data['total_redemption'],
                contract_data['start_date'],
                contract_data['end_date'],
                contract_data['days_count'],
                contract_data['id']
            ))
            
            conn.commit()
            return contract_data['id']
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """ดึงข้อมูลลูกค้าตาม ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def search_customers(self, search_term: str) -> List[Dict]:
        """ค้นหาลูกค้า - ค้นหาจากชื่อก่อน แล้วตามด้วยนามสกุล, เลขบัตร, และรหัสลูกค้า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ค้นหาจากชื่อก่อน (first_name) แล้วตามด้วยนามสกุล, เลขบัตร, และรหัสลูกค้า
            cursor.execute('''
                SELECT *, 
                CASE 
                    WHEN first_name LIKE ? THEN 1
                    WHEN last_name LIKE ? THEN 2
                    WHEN id_card LIKE ? THEN 3
                    WHEN customer_code LIKE ? THEN 4
                    ELSE 5
                END as search_priority
                FROM customers 
                WHERE first_name LIKE ? OR last_name LIKE ? OR id_card LIKE ? OR customer_code LIKE ?
                ORDER BY search_priority, first_name, last_name
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%',
                  f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                # ลบ search_priority column ออกจากผลลัพธ์
                return [dict(zip(columns[:-1], row[:-1])) for row in rows]
            return []
    
    def search_products(self, search_term: str) -> List[Dict]:
        """ค้นหาสินค้า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM products 
                WHERE name LIKE ? OR brand LIKE ? OR serial_number LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
    
    def get_contract_by_number(self, contract_number: str) -> Optional[Dict]:
        """ดึงข้อมูลสัญญาตามเลขที่สัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.contract_number = ?
            ''', (contract_number,))
            
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def search_contracts(self, search_term: str, status: str = 'all') -> List[Dict]:
        """ค้นหาสัญญา (legacy function - ใช้ฟังก์ชันใหม่แทน)"""
        # เรียกใช้ฟังก์ชันใหม่ตามประเภทการค้นหา
        return self.search_contracts_by_number(search_term, status)

    def search_contracts_by_number(self, contract_number: str, status: str = 'all') -> List[Dict]:
        """ค้นหาสัญญาตามเลขที่สัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # สร้าง query ตามสถานะ
            if status == 'all':
                status_condition = ""
            else:
                status_condition = "AND c.status = ?"
            
            query = f'''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.contract_number LIKE ?
                {status_condition}
                ORDER BY c.created_at DESC
            '''
            
            search_pattern = f"%{contract_number}%"
            if status == 'all':
                cursor.execute(query, (search_pattern,))
            else:
                cursor.execute(query, (search_pattern, status))
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def search_contracts_by_id_card(self, id_card: str, status: str = 'all') -> List[Dict]:
        """ค้นหาสัญญาตามเลขบัตรประชาชน"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # สร้าง query ตามสถานะ
            if status == 'all':
                status_condition = ""
            else:
                status_condition = "AND c.status = ?"
            
            query = f'''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE cu.id_card LIKE ?
                {status_condition}
                ORDER BY c.created_at DESC
            '''
            
            search_pattern = f"%{id_card}%"
            if status == 'all':
                cursor.execute(query, (search_pattern,))
            else:
                cursor.execute(query, (search_pattern, status))
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def search_contracts_by_name(self, first_name: str = "", last_name: str = "", status: str = 'all') -> List[Dict]:
        """ค้นหาสัญญาตามชื่อและนามสกุล"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # สร้าง query ตามสถานะ
            if status == 'all':
                status_condition = ""
            else:
                status_condition = "AND c.status = ?"
            
            # สร้างเงื่อนไขการค้นหาตามชื่อ
            name_conditions = []
            params = []
            
            if first_name:
                name_conditions.append("cu.first_name LIKE ?")
                params.append(f"%{first_name}%")
            
            if last_name:
                name_conditions.append("cu.last_name LIKE ?")
                params.append(f"%{last_name}%")
            
            if not name_conditions:
                # ถ้าไม่มีการกรอกชื่อใดๆ ให้ค้นหาทั้งหมด
                name_conditions.append("1=1")
            
            name_condition = " AND ".join(name_conditions)
            
            query = f'''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE {name_condition}
                {status_condition}
                ORDER BY c.created_at DESC
            '''
            
            if status == 'all':
                cursor.execute(query, params)
            else:
                params.append(status)
                cursor.execute(query, params)
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
    
    def add_interest_payment(self, payment_data: Dict) -> int:
        """เพิ่มการชำระดอกเบี้ย"""
        with self.get_connection() as conn:
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
            return payment_id
    
    def add_renewal(self, renewal_data: Dict) -> int:
        """เพิ่มการต่อดอก"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ค้นหา contract_id จาก contract_number
            contract_number = renewal_data.get('contract_number')
            if contract_number:
                cursor.execute('SELECT id FROM contracts WHERE contract_number = ?', (contract_number,))
                contract_result = cursor.fetchone()
                if contract_result:
                    contract_id = contract_result[0]
                else:
                    raise ValueError(f"ไม่พบสัญญาที่มีเลขที่: {contract_number}")
            else:
                contract_id = renewal_data.get('contract_id')
                if not contract_id:
                    raise ValueError("ต้องระบุ contract_number หรือ contract_id")
            
            # คำนวณ renewal_count
            cursor.execute('''
                SELECT COUNT(*) + 1 FROM renewals WHERE contract_id = ?
            ''', (contract_id,))
            renewal_count = cursor.fetchone()[0]
            
            # ค้นหาวันที่ครบกำหนดปัจจุบัน
            cursor.execute('''
                SELECT end_date FROM contracts WHERE id = ?
            ''', (contract_id,))
            current_due_date = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO renewals (
                    contract_id, renewal_count, fee_amount, penalty_amount,
                    discount_amount, total_amount, renewal_date, current_due_date,
                    new_due_date, deposit_days
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_id,
                renewal_count,
                renewal_data.get('fee_amount', 0),
                renewal_data.get('penalty_amount', 0),
                renewal_data.get('discount_amount', 0),
                renewal_data.get('total_amount', 0),
                renewal_data.get('renewal_date', datetime.now().strftime("%Y-%m-%d")),
                current_due_date,
                renewal_data.get('new_due_date'),
                renewal_data.get('extension_days', 0)
            ))
            
            renewal_id = cursor.lastrowid
            conn.commit()
            return renewal_id
    
    def update_contract_due_date(self, contract_id: int, new_due_date: str) -> bool:
        """อัปเดตวันที่ครบกำหนดใหม่ในสัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE contracts SET end_date = ? WHERE id = ?
                ''', (new_due_date, contract_id))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating contract due date: {e}")
                return False
    
    def get_renewals_by_contract(self, contract_id: int) -> List[Dict]:
        """ดึงข้อมูลการต่อดอกตามสัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM renewals 
                WHERE contract_id = ? 
                ORDER BY renewal_count ASC, created_at ASC
            ''', (contract_id,))
            
            columns = [description[0] for description in cursor.description]
            renewals = []
            
            for row in cursor.fetchall():
                renewal = dict(zip(columns, row))
                renewals.append(renewal)
            
            return renewals
    
    def get_all_renewals(self) -> List[Dict]:
        """ดึงข้อมูลการต่อดอกทั้งหมด"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, c.contract_number, cu.first_name, cu.last_name, p.name as product_name
                FROM renewals r
                JOIN contracts c ON r.contract_id = c.id
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                ORDER BY r.created_at DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            renewals = []
            
            for row in cursor.fetchall():
                renewal = dict(zip(columns, row))
                renewals.append(renewal)
            
            return renewals
    
    def redeem_contract(self, redemption_data: Dict) -> int:
        """ไถ่คืนสัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # เพิ่มข้อมูลการไถ่คืน
            cursor.execute('''
                INSERT INTO redemptions (
                    contract_id, redemption_date, redemption_amount,
                    deposit_date, due_date, total_days,
                    principal_amount, fee_amount, penalty_amount, discount_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                redemption_data['contract_id'],
                redemption_data['redemption_date'],
                redemption_data['redemption_amount'],
                redemption_data.get('deposit_date'),
                redemption_data.get('due_date'),
                redemption_data.get('total_days'),
                redemption_data.get('principal_amount'),
                redemption_data.get('fee_amount'),
                redemption_data.get('penalty_amount'),
                redemption_data.get('discount_amount')
            ))
            
            # อัปเดตสถานะสัญญา
            cursor.execute('''
                UPDATE contracts SET status = 'redeemed' WHERE id = ?
            ''', (redemption_data['contract_id'],))
            
            redemption_id = cursor.lastrowid
            conn.commit()
            return redemption_id
    
    def get_daily_summary(self, date: str) -> Dict:
        """สรุปรายวัน"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # สัญญาใหม่
            cursor.execute('''
                SELECT COUNT(*), SUM(pawn_amount) FROM contracts 
                WHERE DATE(start_date) = ?
            ''', (date,))
            new_contracts = cursor.fetchone()
            
            # การไถ่คืน
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
            
            # การต่อดอก
            cursor.execute('''
                SELECT COUNT(*), SUM(total_amount) FROM renewals 
                WHERE DATE(renewal_date) = ?
            ''', (date,))
            renewals = cursor.fetchone()
            
            return {
                'date': date,
                'new_contracts_count': new_contracts[0] or 0,
                'new_contracts_amount': new_contracts[1] or 0,
                'redemptions_count': redemptions[0] or 0,
                'redemptions_amount': redemptions[1] or 0,
                'interest_payments_count': interest_payments[0] or 0,
                'interest_payments_amount': interest_payments[1] or 0,
                'renewals_count': renewals[0] or 0,
                'renewals_amount': renewals[1] or 0
            }
    
    def get_expiring_contracts(self, days: int = 7) -> List[Dict]:
        """ดึงสัญญาที่ใกล้ครบกำหนด"""
        with self.get_connection() as conn:
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
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
    
    def get_forfeited_contracts(self) -> List[Dict]:
        """ดึงสัญญาที่หลุดจำนำ (ครบกำหนดแล้วแต่ยังไม่ได้ไถ่คืน)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, cu.first_name, cu.last_name, cu.phone, cu.id_card, 
                       p.name as product_name, p.brand as product_brand
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.status = 'active' 
                AND c.end_date < DATE('now')
                ORDER BY c.end_date DESC
            ''')
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
    
    def get_setting(self, key: str) -> str:
        """ดึงการตั้งค่า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            return row[0] if row else ''
    
    def update_setting(self, key: str, value: str):
        """อัปเดตการตั้งค่า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
    
    def update_customer(self, customer_id: int, customer_data: Dict) -> bool:
        """อัปเดตข้อมูลลูกค้า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE customers SET
                    customer_code = ?, first_name = ?, last_name = ?, id_card = ?,
                    address = ?, house_number = ?, street = ?, subdistrict = ?,
                    district = ?, province = ?, phone = ?, other_details = ?
                WHERE id = ?
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
                customer_data.get('other_details', ''),
                customer_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_product(self, product_id: int, product_data: Dict) -> bool:
        """อัปเดตข้อมูลสินค้า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE products SET
                    name = ?, brand = ?, size = ?, weight = ?, weight_unit = ?,
                    serial_number = ?, other_details = ?, image_path = ?
                WHERE id = ?
            ''', (
                product_data['name'],
                product_data.get('brand', ''),
                product_data.get('size', ''),
                product_data.get('weight', 0),
                product_data.get('weight_unit', ''),
                product_data.get('serial_number', ''),
                product_data.get('other_details', ''),
                product_data.get('image_path', ''),
                product_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def check_customer_exists(self, id_card: str = None, customer_code: str = None) -> bool:
        """ตรวจสอบว่าลูกค้ามีอยู่ในฐานข้อมูลหรือไม่"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if id_card and customer_code:
                cursor.execute('SELECT COUNT(*) FROM customers WHERE id_card = ? OR customer_code = ?', (id_card, customer_code))
            elif id_card:
                cursor.execute('SELECT COUNT(*) FROM customers WHERE id_card = ?', (id_card,))
            elif customer_code:
                cursor.execute('SELECT COUNT(*) FROM customers WHERE customer_code = ?', (customer_code,))
            else:
                return False
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def check_product_exists(self, serial_number: str = None) -> bool:
        """ตรวจสอบว่าสินค้ามีอยู่ในฐานข้อมูลหรือไม่"""
        if not serial_number:
            return False
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products WHERE serial_number = ?', (serial_number,))
            count = cursor.fetchone()[0]
            return count > 0
    
    def get_next_customer_code(self, prefix: str = "C") -> str:
        """สร้างรหัสลูกค้าใหม่"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ค้นหารหัสลูกค้าล่าสุดที่มี prefix เดียวกัน
            cursor.execute('''
                SELECT customer_code FROM customers 
                WHERE customer_code LIKE ? 
                ORDER BY customer_code DESC 
                LIMIT 1
            ''', (f'{prefix}%',))
            
            row = cursor.fetchone()
            if row:
                last_code = row[0]
                try:
                    # แยกลำดับออกจากรหัส
                    sequence_part = last_code[len(prefix):]
                    last_sequence = int(sequence_part)
                    next_sequence = last_sequence + 1
                except:
                    next_sequence = 1
            else:
                next_sequence = 1
            
            # สร้างรหัสใหม่
            from utils import PawnShopUtils
            return PawnShopUtils.generate_customer_code(prefix, next_sequence)

    def get_next_contract_sequence(self, prefix: str = "CN") -> int:
        """ดึงลำดับถัดไปของเลขที่สัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ค้นหาเลขที่สัญญาล่าสุดที่มี prefix เดียวกัน
            cursor.execute('''
                SELECT contract_number FROM contracts 
                WHERE contract_number LIKE ? 
                ORDER BY contract_number DESC 
                LIMIT 1
            ''', (f'{prefix}%',))
            
            row = cursor.fetchone()
            if row:
                last_contract_number = row[0]
                try:
                    # แยกลำดับออกจากเลขที่สัญญา
                    sequence_part = last_contract_number[len(prefix):]
                    last_sequence = int(sequence_part)
                    next_sequence = last_sequence + 1
                except:
                    next_sequence = 1
            else:
                next_sequence = 1
            
            return next_sequence

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """ดึงข้อมูลสินค้าตาม ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def delete_customer(self, customer_id: int) -> bool:
        """ลบข้อมูลลูกค้า"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # ตรวจสอบว่าลูกค้ามีสัญญาที่เกี่ยวข้องหรือไม่
                cursor.execute('SELECT COUNT(*) FROM contracts WHERE customer_id = ?', (customer_id,))
                contract_count = cursor.fetchone()[0]
                
                if contract_count > 0:
                    return False  # ไม่สามารถลบได้เพราะมีสัญญาเกี่ยวข้อง
                
                # ลบข้อมูลลูกค้า
                cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """ลบข้อมูลสินค้า"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # ตรวจสอบว่าสินค้ามีสัญญาที่เกี่ยวข้องหรือไม่
                cursor.execute('SELECT COUNT(*) FROM contracts WHERE product_id = ?', (product_id,))
                contract_count = cursor.fetchone()[0]
                
                if contract_count > 0:
                    return False  # ไม่สามารถลบได้เพราะมีสัญญาเกี่ยวข้อง
                
                # ลบข้อมูลสินค้า
                cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def delete_contract(self, contract_id: int) -> bool:
        """ลบข้อมูลสัญญา"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # ลบข้อมูลสัญญา
                cursor.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting contract: {e}")
            return False
    
    def get_customer_id_by_code(self, customer_code: str) -> Optional[int]:
        """ดึง ID ของลูกค้าตามรหัสลูกค้า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM customers WHERE customer_code = ?', (customer_code,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_product_id_by_serial(self, serial_number: str) -> Optional[int]:
        """ดึง ID ของสินค้าตามหมายเลขซีเรียล"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM products WHERE serial_number = ?', (serial_number,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    # ฟังก์ชันสำหรับจัดการค่าธรรมเนียม
    def get_all_fee_rates(self) -> List[Dict]:
        """ดึงข้อมูลค่าธรรมเนียมทั้งหมด"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, days_count, fee_rate, description, is_active, created_at, updated_at
                FROM fee_rates 
                ORDER BY days_count
            ''')
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_fee_rate_by_days(self, days: int) -> Optional[Dict]:
        """ดึงข้อมูลค่าธรรมเนียมตามจำนวนวัน"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, days_count, fee_rate, description, is_active
                FROM fee_rates 
                WHERE days_count = ? AND is_active = 1
            ''', (days,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def add_fee_rate(self, fee_data: Dict) -> int:
        """เพิ่มข้อมูลค่าธรรมเนียมใหม่"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fee_rates (days_count, fee_rate, description, is_active)
                VALUES (?, ?, ?, ?)
            ''', (
                fee_data['days_count'],
                fee_data['fee_rate'],
                fee_data.get('description', ''),
                fee_data.get('is_active', True)
            ))
            
            fee_id = cursor.lastrowid
            conn.commit()
            return fee_id
    
    def update_fee_rate(self, fee_id: int, fee_data: Dict) -> bool:
        """อัปเดตข้อมูลค่าธรรมเนียม"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE fee_rates 
                    SET days_count = ?, fee_rate = ?, description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    fee_data['days_count'],
                    fee_data['fee_rate'],
                    fee_data.get('description', ''),
                    fee_data.get('is_active', True),
                    fee_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating fee rate: {e}")
            return False
    
    def delete_fee_rate(self, fee_id: int) -> bool:
        """ลบข้อมูลค่าธรรมเนียม"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM fee_rates WHERE id = ?', (fee_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting fee rate: {e}")
            return False
    
    def calculate_fee_amount(self, pawn_amount: float, days: int) -> float:
        """คำนวณค่าธรรมเนียมตามจำนวนวันและยอดฝาก"""
        fee_rate = self.get_fee_rate_by_days(days)
        if fee_rate:
            return pawn_amount * (fee_rate['fee_rate'] / 100)
        return 0.0
    
    def calculate_withholding_tax(self, interest_amount: float, tax_rate: float) -> float:
        """คำนวณหัก ณ ที่จ่าย"""
        return interest_amount * (tax_rate / 100)
    
    def get_withholding_tax_rate(self) -> float:
        """ดึงอัตราหัก ณ ที่จ่ายเริ่มต้น"""
        try:
            return float(self.get_setting('default_withholding_tax_rate'))
        except:
            return 3.0
    
    def update_withholding_tax_rate(self, new_rate: float) -> bool:
        """อัปเดตอัตราหัก ณ ที่จ่าย"""
        try:
            return self.update_setting('default_withholding_tax_rate', str(new_rate))
        except:
            return False
    
    def get_contracts_with_withholding_tax(self) -> List[Dict]:
        """ดึงข้อมูลสัญญาที่มีการหัก ณ ที่จ่าย"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.contract_number,
                    c.pawn_amount,
                    c.interest_rate,
                    c.days_count,
                    c.withholding_tax_rate,
                    c.withholding_tax_amount,
                    c.start_date,
                    c.end_date,
                    cu.first_name,
                    cu.last_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                WHERE c.withholding_tax_amount > 0
                ORDER BY c.start_date DESC
            ''')
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            contracts = []
            for row in rows:
                contract = dict(zip(columns, row))
                # คำนวณดอกเบี้ย
                interest_amount = (contract['pawn_amount'] * contract['interest_rate'] * contract['days_count']) / 100
                contract['interest_amount'] = interest_amount
                contracts.append(contract)
            
            return contracts

    def get_contracts_by_customer(self, customer_id: int) -> List[Dict]:
        """ดึงข้อมูลสัญญาของลูกค้าคนหนึ่ง"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.*,
                    cu.first_name,
                    cu.last_name,
                    cu.id_card,
                    p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.customer_id = ?
                ORDER BY c.created_at DESC
            ''', (customer_id,))
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def fix_duplicate_customer_codes(self):
        """แก้ไขปัญหารหัสลูกค้าซ้ำซ้อน"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ค้นหารหัสลูกค้าที่ซ้ำซ้อน
            cursor.execute('''
                SELECT customer_code, COUNT(*) as count
                FROM customers 
                GROUP BY customer_code 
                HAVING COUNT(*) > 1
            ''')
            
            duplicates = cursor.fetchall()
            fixed_count = 0
            
            for duplicate_code, count in duplicates:
                if count > 1:
                    # ค้นหาลูกค้าทั้งหมดที่มีรหัสซ้ำ
                    cursor.execute('''
                        SELECT id, customer_code, first_name, last_name, created_at
                        FROM customers 
                        WHERE customer_code = ?
                        ORDER BY created_at ASC
                    ''', (duplicate_code,))
                    
                    customers = cursor.fetchall()
                    
                    # เก็บลูกค้าคนแรกไว้ เปลี่ยนรหัสของคนอื่น
                    for i, (customer_id, old_code, first_name, last_name, created_at) in enumerate(customers[1:], 1):
                        # สร้างรหัสใหม่
                        new_code = f"{old_code}-{i:02d}"
                        
                        # อัปเดตรหัสใหม่
                        cursor.execute('''
                            UPDATE customers 
                            SET customer_code = ? 
                            WHERE id = ?
                        ''', (new_code, customer_id))
                        
                        fixed_count += 1
            
            conn.commit()
            return fixed_count

    def fix_duplicate_id_cards(self):
        """แก้ไขปัญหาเลขบัตรประชาชนซ้ำซ้อน"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # ค้นหาเลขบัตรประชาชนที่ซ้ำซ้อน
            cursor.execute('''
                SELECT id_card, COUNT(*) as count
                FROM customers 
                WHERE id_card IS NOT NULL AND id_card != ''
                GROUP BY id_card 
                HAVING COUNT(*) > 1
            ''')
            
            duplicates = cursor.fetchall()
            fixed_count = 0
            
            for duplicate_id_card, count in duplicates:
                if count > 1:
                    # ค้นหาลูกค้าทั้งหมดที่มีเลขบัตรซ้ำ
                    cursor.execute('''
                        SELECT id, id_card, first_name, last_name, created_at
                        FROM customers 
                        WHERE id_card = ?
                        ORDER BY created_at ASC
                    ''', (duplicate_id_card,))
                    
                    customers = cursor.fetchall()
                    
                    # เก็บลูกค้าคนแรกไว้ ลบเลขบัตรของคนอื่น
                    for i, (customer_id, id_card, first_name, last_name, created_at) in enumerate(customers[1:], 1):
                        # ลบเลขบัตรประชาชน
                        cursor.execute('''
                            UPDATE customers 
                            SET id_card = '' 
                            WHERE id = ?
                        ''', (customer_id,))
                        
                        fixed_count += 1
            
            conn.commit()
            return fixed_count

    def get_contract_by_id(self, contract_id: int) -> Optional[Dict]:
        """ดึงข้อมูลสัญญาตาม ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, cu.first_name, cu.last_name, cu.id_card, p.name as product_name
                FROM contracts c
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.id = ?
            ''', (contract_id,))
            
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_renewals_by_contract(self, contract_number: str) -> List[Dict]:
        """ดึงข้อมูลการต่อดอกตามเลขที่สัญญา"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, c.contract_number, cu.first_name, cu.last_name, p.name as product_name
                FROM renewals r
                JOIN contracts c ON r.contract_id = c.id
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE c.contract_number = ?
                ORDER BY r.renewal_date DESC
            ''', (contract_number,))
            
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def update_contract_end_date(self, contract_number: str, new_end_date: str) -> bool:
        """อัปเดตวันที่ครบกำหนดใหม่ในสัญญา"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE contracts 
                    SET end_date = ?, 
                        days_count = (julianday(?) - julianday(start_date))
                    WHERE contract_number = ?
                ''', (new_end_date, new_end_date, contract_number))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating contract end date: {e}")
            return False

    def get_all_redemptions(self) -> List[Dict]:
        """ดึงข้อมูลการไถ่คืนทั้งหมด"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, c.contract_number, cu.first_name, cu.last_name, p.name as product_name,
                       r.deposit_date, r.due_date, r.total_days, r.principal_amount,
                       r.fee_amount, r.penalty_amount, r.discount_amount
                FROM redemptions r
                JOIN contracts c ON r.contract_id = c.id
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                ORDER BY r.redemption_date DESC
            ''')
            
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_redemptions_by_contract(self, contract_id: int) -> List[Dict]:
        """ดึงข้อมูลการไถ่คืนตาม contract_id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, c.contract_number, cu.first_name, cu.last_name, p.name as product_name,
                       r.deposit_date, r.due_date, r.total_days, r.principal_amount,
                       r.fee_amount, r.penalty_amount, r.discount_amount
                FROM redemptions r
                JOIN contracts c ON r.contract_id = c.id
                JOIN customers cu ON c.customer_id = cu.id
                JOIN products p ON c.product_id = p.id
                WHERE r.contract_id = ?
                ORDER BY r.redemption_date DESC
            ''', (contract_id,))
            
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def update_contract_status(self, contract_id: int, status: str) -> bool:
        """อัปเดตสถานะสัญญา"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE contracts SET status = ? WHERE id = ?
                ''', (status, contract_id))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating contract status: {e}")
            return False

    def get_contracts_by_date(self, date: str) -> List[Dict]:
        """ดึงข้อมูลสัญญาตามวันที่สร้าง"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM contracts 
                WHERE DATE(created_at) = ?
                ORDER BY created_at DESC
            ''', (date,))
            
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_renewals_by_date(self, date: str) -> List[Dict]:
        """ดึงข้อมูลการต่อดอกตามวันที่ต่อดอก"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM renewals 
                WHERE DATE(renewal_date) = ?
                ORDER BY renewal_date DESC
            ''', (date,))
            
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_redemptions_by_date(self, date: str) -> List[Dict]:
        """ดึงข้อมูลการไถ่คืนตามวันที่ไถ่คืน"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM redemptions 
                WHERE DATE(redemption_date) = ?
                ORDER BY redemption_date DESC
            ''', (date,))
            
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
