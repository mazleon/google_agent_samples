"""
Test script for bank agent tools.

This script tests all the tool functions in the bank_agent.tools.tool module
to verify they are working correctly with the sample data.
"""

import sys
import os
import logging
from typing import Dict, Any
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to import bank_agent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the database and tools
from entities.database import db
from entities.sample_data import populate_database
from tools.tool import ToolContext
from tools.tool import (
    verify_customer,
    get_customer_account,
    get_customer_account_balance,
    get_customer_account_transactions,
    get_customer_account_transactions_by_date,
    get_customer_account_transactions_by_type,
    get_customer_complaint,
    get_customer_complaint_by_id,
    create_customer_complaint,
    get_product,
    get_current_offers,
)

def setup_database():
    """Set up the database with sample data and return the inserted IDs."""
    # Check if database exists and has data
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info(f"Database already has {count} customers, skipping population")
                
                # Get existing customer IDs
                cursor.execute("SELECT id FROM customers")
                customer_ids = [row['id'] for row in cursor.fetchall()]
                
                # Get existing account IDs
                cursor.execute("SELECT id FROM accounts")
                account_ids = [row['id'] for row in cursor.fetchall()]
                
                return {
                    "customers": customer_ids,
                    "accounts": account_ids
                }
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.info(f"Database setup needed: {str(e)}")
    
    # Populate database with sample data
    logger.info("Populating database with sample data...")
    return populate_database()

def create_tool_context(params=None, state=None):
    """Create a tool context with the given parameters and state."""
    context = ToolContext()
    if params:
        context.params = params
    if state:
        context.state = state
    return context

def test_verify_customer(customer_id):
    """Test the verify_customer tool."""
    logger.info(f"Testing verify_customer with customer_id={customer_id}")
    context = create_tool_context()
    result = verify_customer(customer_id, context)
    logger.info(f"Result: {result}")
    
    # Check if customer was verified
    if result.get("success"):
        logger.info("✅ verify_customer test passed")
        # Check if customer info was stored in context state
        if hasattr(context, 'state') and context.state.get('verified_customer'):
            logger.info("✅ Customer info stored in context state")
        else:
            logger.warning("❌ Customer info not stored in context state")
    else:
        logger.warning(f"❌ verify_customer test failed: {result.get('error')}")
    
    return result, context

def test_get_customer_account(customer_id, context):
    """Test the get_customer_account tool."""
    logger.info(f"Testing get_customer_account with customer_id={customer_id}")
    result = get_customer_account(customer_id, context)
    logger.info(f"Result: {result}")
    
    if result.get("success"):
        logger.info("✅ get_customer_account test passed")
    else:
        logger.warning(f"❌ get_customer_account test failed: {result.get('error')}")
    
    return result

def test_get_customer_account_balance(customer_id, account_id):
    """Test the get_customer_account_balance tool."""
    logger.info(f"Testing get_customer_account_balance with customer_id={customer_id}, account_id={account_id}")
    context = create_tool_context(params={"account_id": account_id})
    result = get_customer_account_balance(customer_id, context)
    logger.info(f"Result: {result}")
    
    if result.get("success"):
        logger.info("✅ get_customer_account_balance test passed")
    else:
        logger.warning(f"❌ get_customer_account_balance test failed: {result.get('error')}")
    
    return result

def test_get_customer_account_transactions(customer_id, account_id):
    """Test the get_customer_account_transactions tool."""
    logger.info(f"Testing get_customer_account_transactions with customer_id={customer_id}, account_id={account_id}")
    context = create_tool_context(params={"account_id": account_id})
    result = get_customer_account_transactions(customer_id, context)
    logger.info(f"Result: {result}")
    
    if result.get("success"):
        logger.info("✅ get_customer_account_transactions test passed")
    else:
        logger.warning(f"❌ get_customer_account_transactions test failed: {result.get('error')}")
    
    return result

def test_get_customer_account_transactions_by_date(customer_id, account_id):
    """Test the get_customer_account_transactions_by_date tool."""
    logger.info(f"Testing get_customer_account_transactions_by_date with customer_id={customer_id}, account_id={account_id}")
    
    # Get a transaction to find its date
    context = create_tool_context(params={"account_id": account_id})
    transactions_result = get_customer_account_transactions(customer_id, context)
    
    if transactions_result.get("success") and transactions_result.get("data", {}).get("transactions"):
        # Get the date of the first transaction
        first_transaction = transactions_result["data"]["transactions"][0]
        transaction_date = first_transaction.get("transaction_date", "").split("T")[0]
        
        # Use the same date for start and end date to ensure we get at least one transaction
        context = create_tool_context(params={
            "account_id": account_id,
            "start_date": transaction_date,
            "end_date": transaction_date
        })
        
        result = get_customer_account_transactions_by_date(customer_id, context)
        logger.info(f"Result: {result}")
        
        if result.get("success"):
            logger.info("✅ get_customer_account_transactions_by_date test passed")
        else:
            logger.warning(f"❌ get_customer_account_transactions_by_date test failed: {result.get('error')}")
        
        return result
    else:
        logger.warning("❌ Cannot test get_customer_account_transactions_by_date: No transactions found")
        return {"success": False, "error": "No transactions found for testing"}

def test_get_customer_account_transactions_by_type(customer_id, account_id):
    """Test the get_customer_account_transactions_by_type tool."""
    logger.info(f"Testing get_customer_account_transactions_by_type with customer_id={customer_id}, account_id={account_id}")
    
    # Get a transaction to find its type
    context = create_tool_context(params={"account_id": account_id})
    transactions_result = get_customer_account_transactions(customer_id, context)
    
    if transactions_result.get("success") and transactions_result.get("data", {}).get("transactions"):
        # Get the type of the first transaction
        first_transaction = transactions_result["data"]["transactions"][0]
        transaction_type = first_transaction.get("type")
        
        context = create_tool_context(params={
            "account_id": account_id,
            "transaction_type": transaction_type
        })
        
        result = get_customer_account_transactions_by_type(customer_id, context)
        logger.info(f"Result: {result}")
        
        if result.get("success"):
            logger.info("✅ get_customer_account_transactions_by_type test passed")
        else:
            logger.warning(f"❌ get_customer_account_transactions_by_type test failed: {result.get('error')}")
        
        return result
    else:
        logger.warning("❌ Cannot test get_customer_account_transactions_by_type: No transactions found")
        return {"success": False, "error": "No transactions found for testing"}

def test_get_customer_complaint(customer_id):
    """Test the get_customer_complaint tool."""
    logger.info(f"Testing get_customer_complaint with customer_id={customer_id}")
    context = create_tool_context()
    result = get_customer_complaint(customer_id, context)
    logger.info(f"Result: {result}")
    
    if result.get("success"):
        logger.info("✅ get_customer_complaint test passed")
    else:
        logger.warning(f"❌ get_customer_complaint test failed: {result.get('error')}")
    
    return result

def test_get_customer_complaint_by_id(customer_id):
    """Test the get_customer_complaint_by_id tool."""
    logger.info(f"Testing get_customer_complaint_by_id with customer_id={customer_id}")
    
    # First get all complaints for the customer
    context = create_tool_context()
    complaints_result = get_customer_complaint(customer_id, context)
    
    if complaints_result.get("success") and complaints_result.get("data", {}).get("complaints"):
        # Get the ID of the first complaint
        first_complaint = complaints_result["data"]["complaints"][0]
        complaint_id = first_complaint.get("id")
        
        context = create_tool_context(params={"complaint_id": complaint_id})
        result = get_customer_complaint_by_id(customer_id, context)
        logger.info(f"Result: {result}")
        
        if result.get("success"):
            logger.info("✅ get_customer_complaint_by_id test passed")
        else:
            logger.warning(f"❌ get_customer_complaint_by_id test failed: {result.get('error')}")
        
        return result
    else:
        logger.warning("❌ Cannot test get_customer_complaint_by_id: No complaints found")
        return {"success": False, "error": "No complaints found for testing"}

def test_create_customer_complaint(customer_id):
    """Test the create_customer_complaint tool."""
    logger.info(f"Testing create_customer_complaint with customer_id={customer_id}")
    
    # Get complaint types
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM complaint_types LIMIT 1")
        result = cursor.fetchone()
        
    if result:
        complaint_type_id = result["id"]
        
        context = create_tool_context(params={
            "type_id": complaint_type_id,
            "title": "Test Complaint",
            "description": "This is a test complaint created by the test script",
            "priority": "Medium"
        })
        
        result = create_customer_complaint(customer_id, context)
        logger.info(f"Result: {result}")
        
        if result.get("success"):
            logger.info("✅ create_customer_complaint test passed")
        else:
            logger.warning(f"❌ create_customer_complaint test failed: {result.get('error')}")
        
        return result
    else:
        logger.warning("❌ Cannot test create_customer_complaint: No complaint types found")
        return {"success": False, "error": "No complaint types found for testing"}

def test_get_product():
    """Test the get_product tool."""
    logger.info("Testing get_product")
    context = create_tool_context()
    result = get_product(context)
    logger.info(f"Result: {result}")
    
    if result.get("success"):
        logger.info("✅ get_product test passed")
    else:
        logger.warning(f"❌ get_product test failed: {result.get('error')}")
    
    return result

def test_get_current_offers():
    """Test the get_current_offers tool."""
    logger.info("Testing get_current_offers")
    context = create_tool_context()
    result = get_current_offers(context)
    logger.info(f"Result: {result}")
    
    if result.get("success"):
        logger.info("✅ get_current_offers test passed")
    else:
        logger.warning(f"❌ get_current_offers test failed: {result.get('error')}")
    
    return result

def run_all_tests():
    """Run all tool tests."""
    logger.info("Starting tool tests...")
    
    # Set up database and get sample data IDs
    data = setup_database()
    
    if not data.get("customers"):
        logger.error("❌ No customers found in database. Tests cannot proceed.")
        return False
    
    # Get the first customer and account for testing
    customer_id = data["customers"][0]
    account_id = None
    
    # Get an account ID for the customer
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE customer_id = ? LIMIT 1", (customer_id,))
        result = cursor.fetchone()
        if result:
            account_id = result["id"]
    
    if not account_id:
        logger.error(f"❌ No accounts found for customer {customer_id}. Some tests will fail.")
    
    # Run tests
    test_results = {}
    
    # Customer verification
    result, context = test_verify_customer(customer_id)
    test_results["verify_customer"] = result.get("success", False)
    
    # Account tests
    if account_id:
        # Get customer account
        result = test_get_customer_account(customer_id, context)
        test_results["get_customer_account"] = result.get("success", False)
        
        # Get account balance
        result = test_get_customer_account_balance(customer_id, account_id)
        test_results["get_customer_account_balance"] = result.get("success", False)
        
        # Get account transactions
        result = test_get_customer_account_transactions(customer_id, account_id)
        test_results["get_customer_account_transactions"] = result.get("success", False)
        
        # Get transactions by date
        result = test_get_customer_account_transactions_by_date(customer_id, account_id)
        test_results["get_customer_account_transactions_by_date"] = result.get("success", False)
        
        # Get transactions by type
        result = test_get_customer_account_transactions_by_type(customer_id, account_id)
        test_results["get_customer_account_transactions_by_type"] = result.get("success", False)
    
    # Complaint tests
    result = test_get_customer_complaint(customer_id)
    test_results["get_customer_complaint"] = result.get("success", False)
    
    result = test_get_customer_complaint_by_id(customer_id)
    test_results["get_customer_complaint_by_id"] = result.get("success", False)
    
    result = test_create_customer_complaint(customer_id)
    test_results["create_customer_complaint"] = result.get("success", False)
    
    # Product and offer tests
    result = test_get_product()
    test_results["get_product"] = result.get("success", False)
    
    result = test_get_current_offers()
    test_results["get_current_offers"] = result.get("success", False)
    
    # Print summary
    logger.info("\n=== TEST SUMMARY ===")
    passed = sum(1 for success in test_results.values() if success)
    total = len(test_results)
    logger.info(f"Passed: {passed}/{total} tests ({passed/total*100:.1f}%)")
    
    for test_name, success in test_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
