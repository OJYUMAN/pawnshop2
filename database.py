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
        with self.get_connection() as conn:
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
            return customer_id
    
    def add_product(self, product_data: Dict) -> int:
        """เพิ่มสินค้าใหม่"""
        with self.get_connection() as conn:
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
            return product_id
    
    def create_contract(self, contract_data: Dict) -> int:
        """สร้างสัญญาใหม่"""
        with self.get_connection() as conn:
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
            return contract_id
    
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
        """ค้นหาลูกค้า"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM customers 
                WHERE first_name LIKE ? OR last_name LIKE ? OR id_card LIKE ? OR customer_code LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
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
        """ค้นหาสัญญา"""
        with self.get_connection() as conn:
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
    
    def redeem_contract(self, redemption_data: Dict) -> int:
        """ไถ่ถอนสัญญา"""
        with self.get_connection() as conn:
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
                    name = ?, brand = ?, size = ?, weight = ?,
                    serial_number = ?, other_details = ?
                WHERE id = ?
            ''', (
                product_data['name'],
                product_data.get('brand', ''),
                product_data.get('size', ''),
                product_data.get('weight', 0),
                product_data.get('serial_number', ''),
                product_data.get('other_details', ''),
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
