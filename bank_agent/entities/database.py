"""Database module for bank agent using SQLite."""

import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from uuid import UUID, uuid4

# Type aliases
ID = int  # Using integer IDs instead of strings

class Database:
    """Database handler for the bank agent system."""
    
    def __init__(self, db_path: str = "bank_agent.db"):
        """Initialize the database connection and create tables if needed."""
        self.db_path = db_path
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a new database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    
    def _initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL,
                    dob DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    account_number TEXT UNIQUE NOT NULL,
                    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.0,
                    account_type TEXT NOT NULL,
                    account_status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
            """)
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    transaction_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
                )
            """)
            
            # Complaint types table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS complaint_types (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Complaints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    type_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    resolution_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                    FOREIGN KEY (type_id) REFERENCES complaint_types(id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.executescript("""
                CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);
                CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
                CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
                CREATE INDEX IF NOT EXISTS idx_complaints_customer ON complaints(customer_id);
                CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
            """)
            
            # Insert default complaint types if they don't exist
            self._initialize_default_data(cursor)
            
            conn.commit()
    
    def _initialize_default_data(self, cursor: sqlite3.Cursor) -> None:
        """Initialize default data like complaint types."""
        default_types = [
            (1, "Account Issue", "Problems related to account access or management"),
            (2, "Transaction Problem", "Issues with transactions or payments"),
            (3, "Card Issue", "Problems with debit/credit cards"),
            (4, "Internet Banking", "Online banking access or functionality issues"),
            (5, "Loan Query", "Questions or issues regarding loans"),
            (6, "Other", "Any other type of complaint")
        ]
        
        cursor.executemany(
            """
            INSERT OR IGNORE INTO complaint_types (id, name, description)
            VALUES (?, ?, ?)
            """,
            default_types
        )
    
    # ===== CUSTOMER METHODS =====
    
    def verify_customer(self, customer_id: int) -> bool:
        """Verify if a customer exists in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM customers WHERE id = ?", (customer_id,))
            return cursor.fetchone() is not None
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a customer by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ===== ACCOUNT METHODS =====
    
    def get_customer_accounts(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get all accounts for a customer."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE customer_id = ?
                ORDER BY created_at DESC
            """, (customer_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_customer_account(self, customer_id: int, account_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific account for a customer."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE id = ? AND customer_id = ?
            """, (account_id, customer_id))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_account_balance(self, account_id: int) -> Optional[float]:
        """Get the current balance of an account."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    # ===== TRANSACTION METHODS =====
    
    def get_account_transactions(
        self, 
        account_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get recent transactions for an account."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE account_id = ?
                ORDER BY transaction_date DESC, created_at DESC
                LIMIT ? OFFSET ?
            """, (account_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_transactions_by_date_range(
        self, 
        account_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get transactions within a date range for an account."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE account_id = ? 
                AND transaction_date BETWEEN ? AND ?
                ORDER BY transaction_date DESC, created_at DESC
            """, (account_id, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_transactions_by_type(
        self, 
        account_id: int, 
        transaction_type: str
    ) -> List[Dict[str, Any]]:
        """Get transactions of a specific type for an account."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE account_id = ? AND type = ?
                ORDER BY transaction_date DESC, created_at DESC
            """, (account_id, transaction_type))
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== COMPLAINT METHODS =====
    
    def get_customer_complaints(
        self, 
        customer_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all complaints for a customer."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, ct.name as complaint_type_name
                FROM complaints c
                JOIN complaint_types ct ON c.type_id = ct.id
                WHERE c.customer_id = ?
                ORDER BY c.created_at DESC
                LIMIT ? OFFSET ?
            """, (customer_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_complaint_by_id(
        self, 
        complaint_id: int,
        customer_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a specific complaint by ID, optionally filtered by customer."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if customer_id:
                cursor.execute("""
                    SELECT c.*, ct.name as complaint_type_name
                    FROM complaints c
                    JOIN complaint_types ct ON c.type_id = ct.id
                    WHERE c.id = ? AND c.customer_id = ?
                """, (complaint_id, customer_id))
            else:
                cursor.execute("""
                    SELECT c.*, ct.name as complaint_type_name
                    FROM complaints c
                    JOIN complaint_types ct ON c.type_id = ct.id
                    WHERE c.id = ?
                """, (complaint_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_complaint(
        self,
        customer_id: int,
        type_id: int,
        title: str,
        description: str,
        priority: str = "Medium"
    ) -> int:
        """Create a new complaint."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO complaints (
                    customer_id, type_id, title, description, status, priority
                ) VALUES (?, ?, ?, ?, 'Open', ?)
            """, (customer_id, type_id, title, description, priority))
            complaint_id = cursor.lastrowid  # Get the auto-incremented ID
            conn.commit()
        return complaint_id
    
    # ===== PRODUCT METHODS =====
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Get all available banking products."""
        # This is a placeholder. In a real app, this would query a products table
        return [
            {"id": 1, "name": "Savings Account", "type": "Deposit"},
            {"id": 2, "name": "Checking Account", "type": "Deposit"},
            {"id": 3, "name": "Personal Loan", "type": "Loan"},
            {"id": 4, "name": "Credit Card", "type": "Credit"},
            {"id": 5, "name": "Mortgage", "type": "Loan"}
        ]
    
    def get_current_offers(self, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get current offers, optionally personalized for a customer."""
        # This is a placeholder. In a real app, this would query an offers table
        # and potentially personalize offers based on customer data
        base_offers = [
            {"id": 1, "title": "Premium Credit Card", "description": "0% APR for 12 months"},
            {"id": 2, "title": "Personal Loan", "description": "Low interest rates starting at 5.99%"},
            {"id": 3, "title": "High-Yield Savings", "description": "Earn 2.5% APY on your savings"}
        ]
        
        if customer_id:
            # In a real app, we might personalize offers based on customer data
            customer = self.get_customer(customer_id)
            if customer:
                base_offers.append({
                    "id": 100,
                    "title": f"Special Offer for {customer['name'].split()[0]}",
                    "description": "Exclusive deal just for you!"
                })
        
        return base_offers

# Create a singleton instance
db = Database()
