"""
Test script for bank agent tool functions.

This script tests all the tool functions that are used by the agent
to verify they are working correctly with the sample data.
"""

import os
import sys
import logging
from typing import Dict, Any
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

# Import the tool functions and ToolContext
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

def create_tool_context(params=None, state=None):
    """Create a tool context with the given parameters and state."""
    context = ToolContext()
    if params:
        context.params = params
    if state:
        context.state = state
    return context

def pretty_print_json(data):
    """Pretty print JSON data."""
    return json.dumps(data, indent=2)

def test_verify_customer():
    """Test the verify_customer tool."""
    logger.info("=== Testing verify_customer ===")
    
    # Test with valid customer ID
    customer_id = "cust-001"
    context = create_tool_context()
    result = verify_customer(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}:\n{pretty_print_json(result)}")
    
    # Test with invalid customer ID
    customer_id = "cust-999"
    context = create_tool_context()
    result = verify_customer(customer_id, context)
    logger.info(f"Result for invalid customer {customer_id}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_account():
    """Test the get_customer_account tool."""
    logger.info("\n=== Testing get_customer_account ===")
    
    # Test with valid customer ID
    customer_id = "cust-001"
    context = create_tool_context()
    result = get_customer_account(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}:\n{pretty_print_json(result)}")
    
    # Test with invalid customer ID
    customer_id = "cust-999"
    context = create_tool_context()
    result = get_customer_account(customer_id, context)
    logger.info(f"Result for invalid customer {customer_id}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_account_balance():
    """Test the get_customer_account_balance tool."""
    logger.info("\n=== Testing get_customer_account_balance ===")
    
    # Test with valid customer ID and account ID
    customer_id = "cust-001"
    account_id = "acc-001"
    context = create_tool_context(params={"account_id": account_id})
    result = get_customer_account_balance(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and account {account_id}:\n{pretty_print_json(result)}")
    
    # Test with invalid account ID
    account_id = "acc-999"
    context = create_tool_context(params={"account_id": account_id})
    result = get_customer_account_balance(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and invalid account {account_id}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_account_transactions():
    """Test the get_customer_account_transactions tool."""
    logger.info("\n=== Testing get_customer_account_transactions ===")
    
    # Test with valid customer ID and account ID
    customer_id = "cust-001"
    account_id = "acc-001"
    context = create_tool_context(params={"account_id": account_id})
    result = get_customer_account_transactions(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and account {account_id}:\n{pretty_print_json(result)}")
    
    # Test with invalid account ID
    account_id = "acc-999"
    context = create_tool_context(params={"account_id": account_id})
    result = get_customer_account_transactions(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and invalid account {account_id}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_account_transactions_by_date():
    """Test the get_customer_account_transactions_by_date tool."""
    logger.info("\n=== Testing get_customer_account_transactions_by_date ===")
    
    # Test with valid customer ID, account ID, and date range
    customer_id = "cust-001"
    account_id = "acc-001"
    start_date = "2025-05-10"
    end_date = "2025-05-20"
    context = create_tool_context(params={
        "account_id": account_id,
        "start_date": start_date,
        "end_date": end_date
    })
    result = get_customer_account_transactions_by_date(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}, account {account_id}, and date range {start_date} to {end_date}:\n{pretty_print_json(result)}")
    
    # Test with invalid date range
    start_date = "2025-06-01"
    end_date = "2025-06-10"
    context = create_tool_context(params={
        "account_id": account_id,
        "start_date": start_date,
        "end_date": end_date
    })
    result = get_customer_account_transactions_by_date(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}, account {account_id}, and future date range {start_date} to {end_date}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_account_transactions_by_type():
    """Test the get_customer_account_transactions_by_type tool."""
    logger.info("\n=== Testing get_customer_account_transactions_by_type ===")
    
    # Test with valid customer ID, account ID, and transaction type
    customer_id = "cust-001"
    account_id = "acc-001"
    transaction_type = "Deposit"
    context = create_tool_context(params={
        "account_id": account_id,
        "transaction_type": transaction_type
    })
    result = get_customer_account_transactions_by_type(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}, account {account_id}, and type {transaction_type}:\n{pretty_print_json(result)}")
    
    # Test with invalid transaction type
    transaction_type = "InvalidType"
    context = create_tool_context(params={
        "account_id": account_id,
        "transaction_type": transaction_type
    })
    result = get_customer_account_transactions_by_type(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}, account {account_id}, and invalid type {transaction_type}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_complaint():
    """Test the get_customer_complaint tool."""
    logger.info("\n=== Testing get_customer_complaint ===")
    
    # Test with valid customer ID
    customer_id = "cust-001"
    context = create_tool_context()
    result = get_customer_complaint(customer_id, context)
    logger.info(f"Result for valid customer {customer_id}:\n{pretty_print_json(result)}")
    
    # Test with invalid customer ID
    customer_id = "cust-999"
    context = create_tool_context()
    result = get_customer_complaint(customer_id, context)
    logger.info(f"Result for invalid customer {customer_id}:\n{pretty_print_json(result)}")
    
    return True

def test_get_customer_complaint_by_id():
    """Test the get_customer_complaint_by_id tool."""
    logger.info("\n=== Testing get_customer_complaint_by_id ===")
    
    # Test with valid customer ID and complaint ID
    customer_id = "cust-001"
    complaint_id = "comp-001"
    context = create_tool_context(params={"complaint_id": complaint_id})
    result = get_customer_complaint_by_id(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and complaint {complaint_id}:\n{pretty_print_json(result)}")
    
    # Test with invalid complaint ID
    complaint_id = "comp-999"
    context = create_tool_context(params={"complaint_id": complaint_id})
    result = get_customer_complaint_by_id(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and invalid complaint {complaint_id}:\n{pretty_print_json(result)}")
    
    return True

def test_create_customer_complaint():
    """Test the create_customer_complaint tool."""
    logger.info("\n=== Testing create_customer_complaint ===")
    
    # Test with valid customer ID and complaint details
    customer_id = "cust-001"
    context = create_tool_context(params={
        "type_id": "ct-001",
        "title": "Test Complaint from Tool Test",
        "description": "This is a test complaint created by the tool test script",
        "priority": "Medium"
    })
    result = create_customer_complaint(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and complaint details:\n{pretty_print_json(result)}")
    
    # Test with invalid type_id
    context = create_tool_context(params={
        "type_id": "ct-999",
        "title": "Test Complaint with Invalid Type",
        "description": "This complaint has an invalid type ID",
        "priority": "Medium"
    })
    result = create_customer_complaint(customer_id, context)
    logger.info(f"Result for valid customer {customer_id} and invalid type_id:\n{pretty_print_json(result)}")
    
    return True

def test_get_product():
    """Test the get_product tool."""
    logger.info("\n=== Testing get_product ===")
    
    # Test with no parameters
    context = create_tool_context()
    result = get_product(context)
    logger.info(f"Result for get_product with no parameters:\n{pretty_print_json(result)}")
    
    # Test with product_id parameter
    context = create_tool_context(params={"product_id": "prod-001"})
    result = get_product(context)
    logger.info(f"Result for get_product with product_id=prod-001:\n{pretty_print_json(result)}")
    
    # Test with invalid product_id
    context = create_tool_context(params={"product_id": "prod-999"})
    result = get_product(context)
    logger.info(f"Result for get_product with invalid product_id=prod-999:\n{pretty_print_json(result)}")
    
    return True

def test_get_current_offers():
    """Test the get_current_offers tool."""
    logger.info("\n=== Testing get_current_offers ===")
    
    # Test with no parameters
    context = create_tool_context()
    result = get_current_offers(context)
    logger.info(f"Result for get_current_offers with no parameters:\n{pretty_print_json(result)}")
    
    # Test with customer_id parameter
    context = create_tool_context(params={"customer_id": "cust-001"})
    result = get_current_offers(context)
    logger.info(f"Result for get_current_offers with customer_id=cust-001:\n{pretty_print_json(result)}")
    
    return True

def run_all_tests():
    """Run all tests."""
    logger.info("Starting all tool tests...")
    
    # Run tests
    tests = [
        test_verify_customer,
        test_get_customer_account,
        test_get_customer_account_balance,
        test_get_customer_account_transactions,
        test_get_customer_account_transactions_by_date,
        test_get_customer_account_transactions_by_type,
        test_get_customer_complaint,
        test_get_customer_complaint_by_id,
        test_create_customer_complaint,
        test_get_product,
        test_get_current_offers
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
