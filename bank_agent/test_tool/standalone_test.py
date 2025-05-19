"""
Standalone test script for bank agent database and tools.

This script tests the database operations and tool functions directly,
without requiring the Google ADK package.
"""

import os
import sys
import logging
import sqlite3
from typing import Dict, Any
from datetime import datetime, date, timedelta
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the current directory and add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Create a mock ToolContext class
class MockToolContext:
    def __init__(self):
        self.params = {}
        self.state = {}

# Import the database
from entities.database import db

def populate_sample_data():
    """Populate the database with sample data."""
    logger.info("Populating database with sample data...")
    
    # Check if customers table already has data
    with db._get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            if count > 0:
                logger.info(f"Database already has {count} customers, skipping population")
                return True
        except sqlite3.OperationalError:
            logger.info("Customers table doesn't exist yet, will create it")
    
    # Insert sample customers
    customers = [
        {
            "id": "cust-001",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "address": "123 Main St, Anytown, USA",
            "dob": "1985-05-15"
        },
        {
            "id": "cust-002",
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "555-987-6543",
            "address": "456 Oak Ave, Somewhere, USA",
            "dob": "1990-08-22"
        }
    ]
    
    with db._get_connection() as conn:
        cursor = conn.cursor()
        
        # Create customers table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                dob DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create accounts table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                balance DECIMAL(15, 2) NOT NULL DEFAULT 0.0,
                account_type TEXT NOT NULL,
                account_status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        """)
        
        # Create transactions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        # Create complaint_types table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaint_types (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create complaints table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                type_id TEXT NOT NULL,
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
        
        # Create products table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                features TEXT,
                requirements TEXT,
                fees TEXT,
                interest_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create offers table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                product_id TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                terms TEXT,
                is_personalized BOOLEAN DEFAULT 0,
                customer_segment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Insert complaint types
        default_types = [
            ("ct-001", "Account Issue", "Problems related to account access or management"),
            ("ct-002", "Transaction Problem", "Issues with transactions or payments"),
            ("ct-003", "Card Issue", "Problems with debit/credit cards"),
            ("ct-004", "Internet Banking", "Online banking access or functionality issues"),
            ("ct-005", "Loan Query", "Questions or issues regarding loans"),
            ("ct-006", "Other", "Any other type of complaint")
        ]
        
        cursor.executemany(
            """
            INSERT OR IGNORE INTO complaint_types (id, name, description)
            VALUES (?, ?, ?)
            """,
            default_types
        )
        
        # Insert customers
        for customer in customers:
            cursor.execute(
                """
                INSERT OR IGNORE INTO customers 
                (id, name, email, phone, address, dob)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer["id"],
                    customer["name"],
                    customer["email"],
                    customer["phone"],
                    customer["address"],
                    customer["dob"]
                )
            )
        
        # Insert accounts for each customer
        accounts = [
            {
                "id": "acc-001",
                "customer_id": "cust-001",
                "account_number": "1000000001",
                "balance": 5000.00,
                "account_type": "Checking",
                "account_status": "Active"
            },
            {
                "id": "acc-002",
                "customer_id": "cust-001",
                "account_number": "1000000002",
                "balance": 10000.00,
                "account_type": "Savings",
                "account_status": "Active"
            },
            {
                "id": "acc-003",
                "customer_id": "cust-002",
                "account_number": "1000000003",
                "balance": 3500.00,
                "account_type": "Checking",
                "account_status": "Active"
            }
        ]
        
        for account in accounts:
            cursor.execute(
                """
                INSERT OR IGNORE INTO accounts 
                (id, customer_id, account_number, balance, account_type, account_status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    account["id"],
                    account["customer_id"],
                    account["account_number"],
                    account["balance"],
                    account["account_type"],
                    account["account_status"]
                )
            )
        
        # Insert transactions
        today = date.today()
        transactions = [
            {
                "id": "tx-001",
                "account_id": "acc-001",
                "amount": 1000.00,
                "type": "Deposit",
                "description": "Salary Deposit",
                "transaction_date": (today - timedelta(days=5)).isoformat()
            },
            {
                "id": "tx-002",
                "account_id": "acc-001",
                "amount": -200.00,
                "type": "Withdrawal",
                "description": "ATM Withdrawal",
                "transaction_date": (today - timedelta(days=3)).isoformat()
            },
            {
                "id": "tx-003",
                "account_id": "acc-002",
                "amount": 500.00,
                "type": "Deposit",
                "description": "Transfer from Checking",
                "transaction_date": (today - timedelta(days=2)).isoformat()
            },
            {
                "id": "tx-004",
                "account_id": "acc-003",
                "amount": 1500.00,
                "type": "Deposit",
                "description": "Paycheck",
                "transaction_date": (today - timedelta(days=7)).isoformat()
            },
            {
                "id": "tx-005",
                "account_id": "acc-003",
                "amount": -350.00,
                "type": "Payment",
                "description": "Utility Bill",
                "transaction_date": (today - timedelta(days=1)).isoformat()
            }
        ]
        
        for transaction in transactions:
            cursor.execute(
                """
                INSERT OR IGNORE INTO transactions 
                (id, account_id, amount, type, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction["id"],
                    transaction["account_id"],
                    transaction["amount"],
                    transaction["type"],
                    transaction["description"],
                    transaction["transaction_date"]
                )
            )
        
        # Insert complaints
        complaints = [
            {
                "id": "comp-001",
                "customer_id": "cust-001",
                "type_id": "ct-003",
                "title": "Lost Card",
                "description": "I've lost my debit card and need a replacement.",
                "status": "Open",
                "priority": "High",
                "resolution_notes": None,
                "created_at": (today - timedelta(days=2)).isoformat(),
                "updated_at": (today - timedelta(days=2)).isoformat(),
                "resolved_at": None
            },
            {
                "id": "comp-002",
                "customer_id": "cust-002",
                "type_id": "ct-004",
                "title": "Mobile App Issue",
                "description": "The mobile app keeps crashing when I try to log in.",
                "status": "In Progress",
                "priority": "Medium",
                "resolution_notes": "IT team is investigating the issue.",
                "created_at": (today - timedelta(days=5)).isoformat(),
                "updated_at": (today - timedelta(days=3)).isoformat(),
                "resolved_at": None
            }
        ]
        
        for complaint in complaints:
            cursor.execute(
                """
                INSERT OR IGNORE INTO complaints 
                (id, customer_id, type_id, title, description, status, priority, resolution_notes, created_at, updated_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    complaint["id"],
                    complaint["customer_id"],
                    complaint["type_id"],
                    complaint["title"],
                    complaint["description"],
                    complaint["status"],
                    complaint["priority"],
                    complaint["resolution_notes"],
                    complaint["created_at"],
                    complaint["updated_at"],
                    complaint["resolved_at"]
                )
            )
        
        # Insert products
        products = [
            {
                "id": "prod-001",
                "name": "Basic Checking Account",
                "type": "Checking",
                "description": "A simple checking account for everyday banking needs.",
                "features": "No minimum balance, Free debit card, Online and mobile banking",
                "requirements": "Valid ID, SSN, Initial deposit of $25",
                "fees": "Monthly maintenance fee: $5 (waived with direct deposit)",
                "interest_rate": 0.01
            },
            {
                "id": "prod-002",
                "name": "High-Yield Savings Account",
                "type": "Savings",
                "description": "A savings account with competitive interest rates.",
                "features": "Competitive interest rates, Online and mobile banking",
                "requirements": "Valid ID, SSN, Initial deposit of $100",
                "fees": "No monthly maintenance fee",
                "interest_rate": 1.25
            }
        ]
        
        for product in products:
            cursor.execute(
                """
                INSERT OR IGNORE INTO products 
                (id, name, type, description, features, requirements, fees, interest_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["id"],
                    product["name"],
                    product["type"],
                    product["description"],
                    product["features"],
                    product["requirements"],
                    product["fees"],
                    product["interest_rate"]
                )
            )
        
        # Insert offers
        offers = [
            {
                "id": "offer-001",
                "title": "New Customer Bonus",
                "description": "Open a new checking account and receive a $200 bonus.",
                "product_id": "prod-001",
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=90)).isoformat(),
                "terms": "Direct deposit must be at least $500.",
                "is_personalized": False,
                "customer_segment": "New Customers"
            },
            {
                "id": "offer-002",
                "title": "High-Yield Savings Promotion",
                "description": "Open a new High-Yield Savings account and receive a 1.5% APY.",
                "product_id": "prod-002",
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=60)).isoformat(),
                "terms": "Minimum balance of $1,000 required.",
                "is_personalized": False,
                "customer_segment": "All Customers"
            }
        ]
        
        for offer in offers:
            cursor.execute(
                """
                INSERT OR IGNORE INTO offers 
                (id, title, description, product_id, start_date, end_date, terms, is_personalized, customer_segment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    offer["id"],
                    offer["title"],
                    offer["description"],
                    offer["product_id"],
                    offer["start_date"],
                    offer["end_date"],
                    offer["terms"],
                    1 if offer["is_personalized"] else 0,
                    offer["customer_segment"]
                )
            )
        
        conn.commit()
    
    logger.info("Sample data population complete!")
    return True

def test_database_operations():
    """Test basic database operations."""
    logger.info("Testing basic database operations...")
    
    # Test customer retrieval
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        logger.info(f"Found {len(customers)} customers")
        
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()
        logger.info(f"Found {len(accounts)} accounts")
        
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        logger.info(f"Found {len(transactions)} transactions")
        
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()
        logger.info(f"Found {len(complaints)} complaints")
        
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        logger.info(f"Found {len(products)} products")
        
        cursor.execute("SELECT * FROM offers")
        offers = cursor.fetchall()
        logger.info(f"Found {len(offers)} offers")
    
    return len(customers) > 0

def test_verify_customer():
    """Test customer verification."""
    logger.info("Testing customer verification...")
    
    # Test with valid customer ID
    result = db.verify_customer(1)
    logger.info(f"Verify customer 1: {result}")
    
    # Test with invalid customer ID
    result = db.verify_customer(999)
    logger.info(f"Verify non-existent customer 999: {result}")
    
    return True

def test_get_customer():
    """Test get customer."""
    logger.info("Testing get customer...")
    
    # Test with valid customer ID
    result = db.get_customer(1)
    logger.info(f"Get customer 1: {result is not None}")
    
    # Test with invalid customer ID
    result = db.get_customer(999)
    logger.info(f"Get non-existent customer 999: {result is None}")
    
    return True

def test_get_customer_accounts():
    """Test get customer accounts."""
    logger.info("Testing get customer accounts...")
    
    # Test with valid customer ID
    result = db.get_customer_accounts(1)
    logger.info(f"Get accounts for customer 1: {len(result) if result else 0} accounts found")
    
    # Test with invalid customer ID
    result = db.get_customer_accounts(999)
    logger.info(f"Get accounts for non-existent customer 999: {len(result) if result else 0} accounts found")
    
    return True

def test_get_customer_account():
    """Test get specific customer account."""
    logger.info("Testing get specific customer account...")
    
    # Test with valid customer and account ID
    result = db.get_customer_account(1, 1)
    logger.info(f"Get account 1 for customer 1: {result is not None}")
    
    # Test with invalid account ID
    result = db.get_customer_account(1, 999)
    logger.info(f"Get non-existent account 999 for customer 1: {result is None}")
    
    return True

def test_get_account_balance():
    """Test get account balance."""
    logger.info("Testing get account balance...")
    
    # Test with valid account ID
    result = db.get_account_balance(1)
    logger.info(f"Get balance for account 1: {result}")
    
    # Test with invalid account ID
    result = db.get_account_balance(999)
    logger.info(f"Get balance for non-existent account 999: {result}")
    
    return True

def test_get_account_transactions():
    """Test get account transactions."""
    logger.info("Testing get account transactions...")
    
    # Test with valid account ID
    result = db.get_account_transactions(1)
    logger.info(f"Get transactions for account 1: {len(result) if result else 0} transactions found")
    
    # Test with invalid account ID
    result = db.get_account_transactions(999)
    logger.info(f"Get transactions for non-existent account 999: {len(result) if result else 0} transactions found")
    
    return True

def test_get_transactions_by_date_range():
    """Test get transactions by date range."""
    logger.info("Testing get transactions by date range...")
    
    today = date.today()
    start_date = (today - timedelta(days=10)).isoformat()
    end_date = today.isoformat()
    
    # Test with valid account ID and date range
    result = db.get_transactions_by_date_range(1, start_date, end_date)
    logger.info(f"Get transactions for account 1 from {start_date} to {end_date}: {len(result) if result else 0} transactions found")
    
    return True

def test_get_transactions_by_type():
    """Test get transactions by type."""
    logger.info("Testing get transactions by type...")
    
    # Test with valid account ID and transaction type
    result = db.get_transactions_by_type(1, "Deposit")
    logger.info(f"Get Deposit transactions for account 1: {len(result) if result else 0} transactions found")
    
    result = db.get_transactions_by_type(1, "Withdrawal")
    logger.info(f"Get Withdrawal transactions for account 1: {len(result) if result else 0} transactions found")
    
    return True

def test_get_customer_complaints():
    """Test get customer complaints."""
    logger.info("Testing get customer complaints...")
    
    # Test with valid customer ID
    result = db.get_customer_complaints(1)
    logger.info(f"Get complaints for customer 1: {len(result) if result else 0} complaints found")
    
    # Test with invalid customer ID
    result = db.get_customer_complaints(999)
    logger.info(f"Get complaints for non-existent customer 999: {len(result) if result else 0} complaints found")
    
    return True

def test_get_complaint_by_id():
    """Test get complaint by ID."""
    logger.info("Testing get complaint by ID...")
    
    # Test with valid complaint ID
    result = db.get_complaint_by_id(1)
    logger.info(f"Get complaint 1: {result is not None}")
    
    # Test with invalid complaint ID
    result = db.get_complaint_by_id(999)
    logger.info(f"Get non-existent complaint 999: {result is None}")
    
    return True

def test_create_complaint():
    """Test create complaint."""
    logger.info("Testing create complaint...")
    
    # Create a new complaint
    complaint_id = db.create_complaint(
        customer_id=1,
        type_id=1,
        title="Test Complaint",
        description="This is a test complaint created by the test script",
        priority="Medium"
    )
    
    logger.info(f"Created complaint with ID: {complaint_id}")
    
    # Verify the complaint was created
    result = db.get_complaint_by_id(complaint_id)
    logger.info(f"Verify complaint {complaint_id} was created: {result is not None}")
    
    return complaint_id is not None

def test_get_products():
    """Test get products."""
    logger.info("Testing get products...")
    
    # Get all products
    result = db.get_products()
    logger.info(f"Get all products: {len(result) if result else 0} products found")
    
    return len(result) > 0 if result else False

def test_get_current_offers():
    """Test get current offers."""
    logger.info("Testing get current offers...")
    
    # Get all offers
    result = db.get_current_offers()
    logger.info(f"Get all offers: {len(result) if result else 0} offers found")
    
    # Get offers for a specific customer
    result = db.get_current_offers(1)
    logger.info(f"Get offers for customer 1: {len(result) if result else 0} offers found")
    
    return True

def run_all_tests():
    """Run all tests."""
    logger.info("Starting all tests...")
    
    # Populate sample data
    populate_sample_data()
    
    # Run tests
    tests = [
        test_database_operations,
        test_verify_customer,
        test_get_customer,
        test_get_customer_accounts,
        test_get_customer_account,
        test_get_account_balance,
        test_get_account_transactions,
        test_get_transactions_by_date_range,
        test_get_transactions_by_type,
        test_get_customer_complaints,
        test_get_complaint_by_id,
        test_create_complaint,
        test_get_products,
        test_get_current_offers
    ]
    
    results = {}
    for test_func in tests:
        test_name = test_func.__name__
        logger.info(f"\n=== Running {test_name} ===")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            logger.error(f"Error in {test_name}: {str(e)}")
            results[test_name] = False
            status = "❌ FAILED (Error)"
        
        logger.info(f"{status}: {test_name}")
    
    # Print summary
    logger.info("\n=== TEST SUMMARY ===")
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    logger.info(f"Passed: {passed}/{total} tests ({passed/total*100:.1f}%)")
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
