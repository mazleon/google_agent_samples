"""
Sample data generator for the bank agent database.

This module provides functions to populate the database with sample data
for testing and demonstration purposes.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from uuid import uuid4
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Import the database instance
import os
import sys

# Get the current directory and add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now import the database
from entities.database import db

# No longer needed as we're using integer IDs
# def generate_uuid() -> str:
#     """Generate a random UUID string."""
#     return str(uuid4())

def insert_sample_customers() -> List[int]:
    """
    Insert sample customers into the database.
    
    Returns:
        List of customer IDs that were inserted
    """
    customers = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "address": "123 Main St, Anytown, USA",
            "dob": "1985-05-15"
        },
        {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "555-987-6543",
            "address": "456 Oak Ave, Somewhere, USA",
            "dob": "1990-08-22"
        },
        {
            "name": "Michael Johnson",
            "email": "michael.johnson@example.com",
            "phone": "555-456-7890",
            "address": "789 Pine Rd, Elsewhere, USA",
            "dob": "1978-12-10"
        },
        {
            "name": "Sarah Williams",
            "email": "sarah.williams@example.com",
            "phone": "555-234-5678",
            "address": "321 Elm St, Nowhere, USA",
            "dob": "1992-03-28"
        },
        {
            "name": "Robert Brown",
            "email": "robert.brown@example.com",
            "phone": "555-876-5432",
            "address": "654 Maple Dr, Anywhere, USA",
            "dob": "1983-07-04"
        }
    ]
    
    customer_ids = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        for customer in customers:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO customers 
                    (name, email, phone, address, dob)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        customer["name"],
                        customer["email"],
                        customer["phone"],
                        customer["address"],
                        customer["dob"]
                    )
                )
                if cursor.rowcount > 0:
                    # Get the auto-incremented ID
                    customer_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                print(f"Customer {customer['name']} already exists, skipping.")
        
        conn.commit()
    
    print(f"Inserted {len(customer_ids)} customers")
    return customer_ids

def insert_sample_accounts(customer_ids: List[int]) -> List[int]:
    """
    Insert sample accounts for the given customers.
    
    Args:
        customer_ids: List of customer IDs to create accounts for
        
    Returns:
        List of account IDs that were inserted
    """
    account_types = ["Checking", "Savings", "Credit", "Investment"]
    account_statuses = ["Active", "Inactive", "Suspended", "Closed"]
    
    accounts = []
    for customer_id in customer_ids:
        # Each customer gets 1-3 accounts
        num_accounts = random.randint(1, 3)
        for i in range(num_accounts):
            account_type = random.choice(account_types)
            account = {
                "customer_id": customer_id,
                "account_number": f"{random.randint(1000000000, 9999999999)}",
                "balance": round(random.uniform(100, 10000), 2),
                "account_type": account_type,
                "account_status": "Active" if random.random() < 0.9 else random.choice(account_statuses[1:])
            }
            accounts.append(account)
    
    account_ids = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        for account in accounts:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO accounts 
                    (customer_id, account_number, balance, account_type, account_status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        account["customer_id"],
                        account["account_number"],
                        account["balance"],
                        account["account_type"],
                        account["account_status"]
                    )
                )
                if cursor.rowcount > 0:
                    # Get the auto-incremented ID
                    account_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                print(f"Account with number {account['account_number']} already exists, skipping.")
        
        conn.commit()
    
    print(f"Inserted {len(account_ids)} accounts")
    return account_ids

def insert_sample_transactions(account_ids: List[int]) -> List[int]:
    """
    Insert sample transactions for the given accounts.
    
    Args:
        account_ids: List of account IDs to create transactions for
        
    Returns:
        List of transaction IDs that were inserted
    """
    transaction_types = ["Deposit", "Withdrawal", "Transfer", "Payment", "Fee", "Interest"]
    transaction_descriptions = {
        "Deposit": ["Salary", "Refund", "Cash Deposit", "Check Deposit", "Direct Deposit"],
        "Withdrawal": ["ATM Withdrawal", "Cash Withdrawal", "Check Withdrawal"],
        "Transfer": ["Internal Transfer", "External Transfer", "Wire Transfer"],
        "Payment": ["Utility Bill", "Rent Payment", "Credit Card Payment", "Loan Payment", "Subscription"],
        "Fee": ["Monthly Fee", "Overdraft Fee", "ATM Fee", "Late Payment Fee"],
        "Interest": ["Interest Payment", "Dividend", "Investment Return"]
    }
    
    today = date.today()
    transactions = []
    
    for account_id in account_ids:
        # Each account gets 5-20 transactions
        num_transactions = random.randint(5, 20)
        for i in range(num_transactions):
            # Transactions within the last 90 days
            transaction_date = today - timedelta(days=random.randint(0, 90))
            transaction_type = random.choice(transaction_types)
            
            # Determine amount based on transaction type
            if transaction_type in ["Deposit", "Interest"]:
                amount = round(random.uniform(10, 2000), 2)
            elif transaction_type in ["Fee"]:
                amount = round(random.uniform(1, 50), 2) * -1
            elif transaction_type in ["Withdrawal", "Payment"]:
                amount = round(random.uniform(10, 1000), 2) * -1
            else:  # Transfer
                amount = round(random.uniform(10, 1000), 2) * (1 if random.random() < 0.5 else -1)
            
            description = random.choice(transaction_descriptions[transaction_type])
            
            transaction = {
                "account_id": account_id,
                "amount": amount,
                "type": transaction_type,
                "description": f"{description} - {transaction_date.strftime('%b %d')}",
                "transaction_date": transaction_date.isoformat()
            }
            transactions.append(transaction)
    
    transaction_ids = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        for transaction in transactions:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO transactions 
                    (account_id, amount, type, description, transaction_date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        transaction["account_id"],
                        transaction["amount"],
                        transaction["type"],
                        transaction["description"],
                        transaction["transaction_date"]
                    )
                )
                if cursor.rowcount > 0:
                    # Get the auto-incremented ID
                    transaction_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                print(f"Transaction for account {transaction['account_id']} already exists, skipping.")
        
        conn.commit()
    
    print(f"Inserted {len(transaction_ids)} transactions")
    return transaction_ids

def insert_sample_complaints(customer_ids: List[int]) -> List[int]:
    """
    Insert sample complaints for the given customers.
    
    Args:
        customer_ids: List of customer IDs to create complaints for
        
    Returns:
        List of complaint IDs that were inserted
    """
    # Get complaint types from the database
    complaint_types = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM complaint_types")
        for row in cursor.fetchall():
            complaint_types.append(row["id"])
    
    complaint_titles = {
        1: ["Account Access Issue", "Can't Login", "Account Locked", "Missing Statements"],
        2: ["Unauthorized Transaction", "Double Charge", "Missing Deposit", "Wrong Amount"],
        3: ["Lost Card", "Card Declined", "Card Damaged", "Fraudulent Charges"],
        4: ["App Not Working", "Website Error", "Transfer Failed", "Password Reset Issue"],
        5: ["Loan Application Status", "Interest Rate Question", "Payment Not Applied", "Payoff Amount"],
        6: ["General Inquiry", "Branch Hours", "Fee Dispute", "Service Feedback"]
    }
    
    complaint_descriptions = {
        1: [
            "I can't access my account online. I've tried resetting my password multiple times.",
            "My account appears to be locked after several login attempts. Please help me regain access.",
            "I haven't received my monthly statements for the past 3 months.",
            "My account details are showing incorrect information."
        ],
        2: [
            "I noticed an unauthorized transaction of $XX.XX on my account dated XX/XX/XXXX.",
            "I was charged twice for the same purchase at STORE on XX/XX/XXXX.",
            "My deposit from XX/XX/XXXX is not showing in my account.",
            "A transaction amount is incorrect. It should be $XX.XX but shows as $YY.YY."
        ],
        3: [
            "I've lost my debit card and need to report it missing.",
            "My card was declined at a store even though I have sufficient funds.",
            "My card is damaged and not working properly. I need a replacement.",
            "I've noticed several charges on my card that I did not make."
        ],
        4: [
            "The mobile app keeps crashing when I try to log in.",
            "I'm getting an error message when trying to use the website.",
            "I tried to transfer money between accounts but it failed.",
            "I can't reset my password. The reset link in the email doesn't work."
        ],
        5: [
            "I applied for a loan last week and want to know its status.",
            "I believe my loan interest rate is higher than what was promised.",
            "My loan payment wasn't applied to my account.",
            "I need to know the payoff amount for my loan."
        ],
        6: [
            "What are the hours for the Main Street branch?",
            "I believe I was charged a fee incorrectly and would like it reviewed.",
            "I had a poor experience with a teller at your downtown branch.",
            "I have a question about a new service I saw advertised."
        ]
    }
    
    statuses = ["Open", "In Progress", "Resolved", "Closed"]
    priorities = ["Low", "Medium", "High", "Critical"]
    
    today = date.today()
    complaints = []
    
    for customer_id in customer_ids:
        # Each customer gets 0-3 complaints
        num_complaints = random.randint(0, 3)
        for i in range(num_complaints):
            # Complaints within the last 30 days
            created_date = today - timedelta(days=random.randint(0, 30))
            
            # Select random complaint type
            type_id = random.choice(complaint_types)
            
            # Select random title and description for the type
            title = random.choice(complaint_titles[type_id])
            description = random.choice(complaint_descriptions[type_id])
            
            # Determine status and dates
            status = random.choice(statuses)
            updated_date = created_date + timedelta(days=random.randint(1, 5))
            resolved_date = None
            if status in ["Resolved", "Closed"]:
                resolved_date = updated_date + timedelta(days=random.randint(1, 5))
            
            priority = random.choice(priorities)
            
            complaint = {
                "customer_id": customer_id,
                "type_id": type_id,
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "resolution_notes": "Issue resolved to customer satisfaction." if status in ["Resolved", "Closed"] else None,
                "created_at": created_date.isoformat(),
                "updated_at": updated_date.isoformat(),
                "resolved_at": resolved_date.isoformat() if resolved_date else None
            }
            complaints.append(complaint)
    
    complaint_ids = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        for complaint in complaints:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO complaints 
                    (customer_id, type_id, title, description, status, priority, resolution_notes, created_at, updated_at, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
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
                if cursor.rowcount > 0:
                    # Get the auto-incremented ID
                    complaint_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                print(f"Complaint for customer {complaint['customer_id']} already exists, skipping.")
        
        conn.commit()
    
    print(f"Inserted {len(complaint_ids)} complaints")
    return complaint_ids

def insert_sample_products() -> List[int]:
    """
    Insert sample banking products into the database.
    
    Returns:
        List of product IDs that were inserted
    """
    # Create products table if it doesn't exist
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
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
        conn.commit()
    
    products = [
        {
            "name": "Basic Checking Account",
            "type": "Checking",
            "description": "A simple checking account for everyday banking needs.",
            "features": "No minimum balance, Free debit card, Online and mobile banking, Bill pay",
            "requirements": "Valid ID, SSN, Initial deposit of $25",
            "fees": "Monthly maintenance fee: $5 (waived with direct deposit)",
            "interest_rate": 0.01
        },
        {
            "name": "Premium Checking Account",
            "type": "Checking",
            "description": "A premium checking account with additional benefits.",
            "features": "No ATM fees, Free checks, Higher daily limits, Priority customer service",
            "requirements": "Valid ID, SSN, Initial deposit of $100",
            "fees": "Monthly maintenance fee: $15 (waived with $5,000 minimum balance)",
            "interest_rate": 0.05
        },
        {
            "name": "High-Yield Savings Account",
            "type": "Savings",
            "description": "A savings account with competitive interest rates.",
            "features": "Competitive interest rates, Online and mobile banking, Automatic transfers",
            "requirements": "Valid ID, SSN, Initial deposit of $100",
            "fees": "No monthly maintenance fee",
            "interest_rate": 1.25
        },
        {
            "name": "Student Checking Account",
            "type": "Checking",
            "description": "A checking account designed for students.",
            "features": "No minimum balance, Free debit card, Online and mobile banking, ATM fee reimbursement",
            "requirements": "Valid student ID, Valid ID, SSN",
            "fees": "No monthly maintenance fee for students",
            "interest_rate": 0.01
        },
        {
            "name": "Home Mortgage Loan",
            "type": "Loan",
            "description": "Fixed and adjustable rate mortgages for home purchases.",
            "features": "Competitive rates, Flexible terms, Online application",
            "requirements": "Credit check, Income verification, Property appraisal",
            "fees": "Application fee: $300, Origination fee: 0.5% of loan amount",
            "interest_rate": 3.75
        },
        {
            "name": "Personal Loan",
            "type": "Loan",
            "description": "Unsecured personal loans for various needs.",
            "features": "Fixed rates, Flexible terms, No collateral required",
            "requirements": "Credit check, Income verification",
            "fees": "Origination fee: 1% of loan amount",
            "interest_rate": 7.99
        },
        {
            "name": "Credit Builder Card",
            "type": "Credit",
            "description": "A credit card designed to help build or rebuild credit.",
            "features": "Low credit limit, Reports to all credit bureaus, Online account management",
            "requirements": "Valid ID, SSN, Income verification",
            "fees": "Annual fee: $39",
            "interest_rate": 19.99
        },
        {
            "name": "Rewards Credit Card",
            "type": "Credit",
            "description": "A credit card with cashback rewards on purchases.",
            "features": "2% cashback on all purchases, No foreign transaction fees, Travel insurance",
            "requirements": "Good credit score, Valid ID, SSN, Income verification",
            "fees": "Annual fee: $95 (waived first year)",
            "interest_rate": 16.99
        }
    ]
    
    product_ids = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        for product in products:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO products 
                    (name, type, description, features, requirements, fees, interest_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product["name"],
                        product["type"],
                        product["description"],
                        product["features"],
                        product["requirements"],
                        product["fees"],
                        product["interest_rate"]
                    )
                )
                if cursor.rowcount > 0:
                    # Get the auto-incremented ID
                    product_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                print(f"Product {product['name']} already exists, skipping.")
        
        conn.commit()
    
    print(f"Inserted {len(product_ids)} products")
    return product_ids

def insert_sample_offers() -> List[int]:
    """
    Insert sample special offers into the database.
    
    Returns:
        List of offer IDs that were inserted
    """
    # Create offers table if it doesn't exist
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                product_id INTEGER,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                terms TEXT,
                is_personalized BOOLEAN DEFAULT 0,
                customer_segment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        conn.commit()
    
    today = date.today()
    offers = [
        {
            "title": "New Customer Bonus",
            "description": "Open a new checking account and receive a $200 bonus when you set up direct deposit.",
            "product_id": 1,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=90)).isoformat(),
            "terms": "Direct deposit must be at least $500. Bonus will be deposited within 60 days of meeting requirements.",
            "is_personalized": False,
            "customer_segment": "New Customers"
        },
        {
            "title": "High-Yield Savings Promotion",
            "description": "Open a new High-Yield Savings account and receive a 1.5% APY for the first 6 months.",
            "product_id": 3,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
            "terms": "Minimum balance of $1,000 required to receive promotional rate. Rate reverts to standard after 6 months.",
            "is_personalized": False,
            "customer_segment": "All Customers"
        },
        {
            "title": "Credit Card Balance Transfer",
            "description": "Transfer balances to our Rewards Credit Card and pay 0% interest for 18 months.",
            "product_id": 8,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=45)).isoformat(),
            "terms": "3% balance transfer fee applies. 0% APR for 18 months on balance transfers made within 60 days of account opening.",
            "is_personalized": False,
            "customer_segment": "All Customers"
        },
        {
            "title": "Mortgage Rate Discount",
            "description": "Receive a 0.25% rate discount on new home mortgages when you set up automatic payments.",
            "product_id": 5,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=120)).isoformat(),
            "terms": "Automatic payments must be set up from a RedDot checking account. Discount applies for the life of the loan.",
            "is_personalized": False,
            "customer_segment": "All Customers"
        },
        {
            "title": "Student Account Promotion",
            "description": "Open a Student Checking Account and receive a $50 bonus plus a free college-themed debit card.",
            "product_id": 4,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
            "terms": "Must provide valid student ID. Bonus will be deposited within 30 days of account opening.",
            "is_personalized": False,
            "customer_segment": "Students"
        },
        {
            "title": "Personal Loan Rate Reduction",
            "description": "Existing customers can receive a 0.5% rate reduction on new personal loans.",
            "product_id": 6,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=90)).isoformat(),
            "terms": "Must have an existing account in good standing for at least 6 months. Minimum loan amount of $5,000.",
            "is_personalized": True,
            "customer_segment": "Existing Customers"
        }
    ]
    
    offer_ids = []
    with db._get_connection() as conn:
        cursor = conn.cursor()
        for offer in offers:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO offers 
                    (title, description, product_id, start_date, end_date, terms, is_personalized, customer_segment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
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
                if cursor.rowcount > 0:
                    # Get the auto-incremented ID
                    offer_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                print(f"Offer {offer['title']} already exists, skipping.")
        
        conn.commit()
    
    print(f"Inserted {len(offer_ids)} offers")
    return offer_ids

def populate_database():
    """Populate the database with sample data for all tables."""
    print("Populating database with sample data...")
    
    # Insert sample data in order of dependencies
    customer_ids = insert_sample_customers()
    account_ids = insert_sample_accounts(customer_ids)
    transaction_ids = insert_sample_transactions(account_ids)
    complaint_ids = insert_sample_complaints(customer_ids)
    product_ids = insert_sample_products()
    offer_ids = insert_sample_offers()
    
    print("\nDatabase population complete!")
    print(f"Inserted {len(customer_ids)} customers")
    print(f"Inserted {len(account_ids)} accounts")
    print(f"Inserted {len(transaction_ids)} transactions")
    print(f"Inserted {len(complaint_ids)} complaints")
    print(f"Inserted {len(product_ids)} products")
    print(f"Inserted {len(offer_ids)} offers")
    
    return {
        "customers": customer_ids,
        "accounts": account_ids,
        "transactions": transaction_ids,
        "complaints": complaint_ids,
        "products": product_ids,
        "offers": offer_ids
    }

if __name__ == "__main__":
    # When run directly, populate the database
    populate_database()
