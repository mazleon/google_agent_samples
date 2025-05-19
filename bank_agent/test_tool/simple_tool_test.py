"""
Simple test script for bank agent database operations.

This script tests the database operations directly without depending on pydantic
or other external packages.
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime, date

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

# Import the database
from entities.database import db

def test_customer_operations():
    """Test customer operations."""
    logger.info("=== Testing Customer Operations ===")
    
    # Test customer verification
    customer_id = "cust-001"
    result = db.verify_customer(customer_id)
    logger.info(f"Verify customer {customer_id}: {result}")
    
    # Test get customer
    customer = db.get_customer(customer_id)
    logger.info(f"Get customer {customer_id}: {customer is not None}")
    if customer:
        logger.info(f"Customer details: {customer}")
    
    return True

def test_account_operations():
    """Test account operations."""
    logger.info("\n=== Testing Account Operations ===")
    
    # Test get customer accounts
    customer_id = "cust-001"
    accounts = db.get_customer_accounts(customer_id)
    logger.info(f"Get accounts for customer {customer_id}: {len(accounts) if accounts else 0} accounts found")
    if accounts:
        logger.info(f"First account: {accounts[0]}")
    
    # Test get specific account
    if accounts:
        account_id = accounts[0]["id"]
        account = db.get_customer_account(customer_id, account_id)
        logger.info(f"Get account {account_id} for customer {customer_id}: {account is not None}")
        if account:
            logger.info(f"Account details: {account}")
        
        # Test get account balance
        balance = db.get_account_balance(account_id)
        logger.info(f"Get balance for account {account_id}: {balance}")
    
    return True

def test_transaction_operations():
    """Test transaction operations."""
    logger.info("\n=== Testing Transaction Operations ===")
    
    # Get an account ID first
    customer_id = "cust-001"
    accounts = db.get_customer_accounts(customer_id)
    if not accounts:
        logger.error("No accounts found for testing transactions")
        return False
    
    account_id = accounts[0]["id"]
    
    # Test get account transactions
    transactions = db.get_account_transactions(account_id)
    logger.info(f"Get transactions for account {account_id}: {len(transactions) if transactions else 0} transactions found")
    if transactions:
        logger.info(f"First transaction: {transactions[0]}")
    
    # Test get transactions by date range
    today = date.today()
    start_date = "2025-05-01"
    end_date = today.isoformat()
    transactions = db.get_transactions_by_date_range(account_id, start_date, end_date)
    logger.info(f"Get transactions for account {account_id} from {start_date} to {end_date}: {len(transactions) if transactions else 0} transactions found")
    
    # Test get transactions by type
    transaction_type = "Deposit"
    transactions = db.get_transactions_by_type(account_id, transaction_type)
    logger.info(f"Get {transaction_type} transactions for account {account_id}: {len(transactions) if transactions else 0} transactions found")
    
    return True

def test_complaint_operations():
    """Test complaint operations."""
    logger.info("\n=== Testing Complaint Operations ===")
    
    # Test get customer complaints
    customer_id = "cust-001"
    complaints = db.get_customer_complaints(customer_id)
    logger.info(f"Get complaints for customer {customer_id}: {len(complaints) if complaints else 0} complaints found")
    if complaints:
        logger.info(f"First complaint: {complaints[0]}")
        
        # Test get specific complaint
        complaint_id = complaints[0]["id"]
        complaint = db.get_complaint_by_id(complaint_id)
        logger.info(f"Get complaint {complaint_id}: {complaint is not None}")
        if complaint:
            logger.info(f"Complaint details: {complaint}")
    
    # Test create complaint
    complaint_id = db.create_complaint(
        customer_id=customer_id,
        type_id="ct-001",
        title="Test Complaint",
        description="This is a test complaint created by the test script",
        priority="Medium"
    )
    logger.info(f"Created complaint with ID: {complaint_id}")
    
    # Verify the complaint was created
    if complaint_id:
        complaint = db.get_complaint_by_id(complaint_id)
        logger.info(f"Verify complaint {complaint_id} was created: {complaint is not None}")
        if complaint:
            logger.info(f"New complaint details: {complaint}")
    
    return True

def test_product_operations():
    """Test product operations."""
    logger.info("\n=== Testing Product Operations ===")
    
    # Test get products
    products = db.get_products()
    logger.info(f"Get products: {len(products) if products else 0} products found")
    if products:
        logger.info(f"First product: {products[0]}")
    
    # Test get offers
    offers = db.get_current_offers()
    logger.info(f"Get offers: {len(offers) if offers else 0} offers found")
    if offers:
        logger.info(f"First offer: {offers[0]}")
    
    # Test get personalized offers
    customer_id = "cust-001"
    offers = db.get_current_offers(customer_id)
    logger.info(f"Get offers for customer {customer_id}: {len(offers) if offers else 0} offers found")
    
    return True

def run_all_tests():
    """Run all tests."""
    logger.info("Starting all database operation tests...")
    
    # Run tests
    tests = [
        test_customer_operations,
        test_account_operations,
        test_transaction_operations,
        test_complaint_operations,
        test_product_operations
    ]
    
    results = {}
    for test_func in tests:
        test_name = test_func.__name__
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Error in {test_name}: {str(e)}")
            results[test_name] = False
    
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
