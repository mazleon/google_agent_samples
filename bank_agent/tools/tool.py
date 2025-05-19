"""
Tools for bank agent to interact with customer data and banking operations.

This module implements Google ADK tools for the bank agent system, providing
functionality for customer verification, account management, transaction history,
and complaint handling through the database interface.

Each tool follows the Google ADK tool pattern, accepting a customer_id and tool_context
parameter, and returning structured data that can be used by the agent.
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, validator

# Google ADK imports
from google.genai import types
from google.adk.tools import ToolContext

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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Request/Response Models ---

class ToolResponse(BaseModel):
    """Base response model for all tool responses."""
    success: bool = Field(True, description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Optional message about the operation")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    
    model_config = ConfigDict(extra="allow")
    
    @validator("error", always=True)
    def set_success_based_on_error(cls, v, values):
        """Set success to False if error is present."""
        if v is not None:
            values["success"] = False
        return v

class AccountResponse(ToolResponse):
    """Response model for account information."""
    account_id: Optional[str] = Field(None, description="Unique identifier for the account")
    account_number: Optional[str] = Field(None, description="Account number")
    account_type: Optional[str] = Field(None, description="Type of account")
    balance: Optional[float] = Field(None, description="Current account balance")
    status: Optional[str] = Field(None, description="Account status")
    created_at: Optional[str] = Field(None, description="Account creation date")
    accounts: Optional[List[Dict[str, Any]]] = Field(None, description="List of accounts if multiple")

class TransactionResponse(ToolResponse):
    """Response model for transaction information."""
    account_id: Optional[str] = Field(None, description="Account ID the transactions belong to")
    account_number: Optional[str] = Field(None, description="Account number")
    transactions: Optional[List[Dict[str, Any]]] = Field(None, description="List of transactions")
    count: Optional[int] = Field(None, description="Number of transactions returned")
    start_date: Optional[str] = Field(None, description="Start date for filtered transactions")
    end_date: Optional[str] = Field(None, description="End date for filtered transactions")
    transaction_type: Optional[str] = Field(None, description="Type filter applied to transactions")
    pagination: Optional[Dict[str, Any]] = Field(None, description="Pagination information")

class ComplaintResponse(ToolResponse):
    """Response model for complaint information."""
    customer_id: Optional[str] = Field(None, description="Customer ID the complaints belong to")
    complaint_id: Optional[str] = Field(None, description="Unique identifier for the complaint")
    title: Optional[str] = Field(None, description="Complaint title")
    type: Optional[str] = Field(None, description="Type of complaint")
    status: Optional[str] = Field(None, description="Current status of the complaint")
    priority: Optional[str] = Field(None, description="Priority level of the complaint")
    created_at: Optional[str] = Field(None, description="Complaint creation date")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp if resolved")
    complaints: Optional[List[Dict[str, Any]]] = Field(None, description="List of complaints if multiple")
    pagination: Optional[Dict[str, Any]] = Field(None, description="Pagination information")

class ProductResponse(ToolResponse):
    """Response model for product information."""
    products: Optional[List[Dict[str, Any]]] = Field(None, description="List of products")
    count: Optional[int] = Field(None, description="Number of products returned")
    product_id: Optional[str] = Field(None, description="Product identifier if single product")
    name: Optional[str] = Field(None, description="Product name if single product")
    type: Optional[str] = Field(None, description="Product type if single product")
    description: Optional[str] = Field(None, description="Product description if single product")

class OfferResponse(ToolResponse):
    """Response model for special offers."""
    offers: Optional[List[Dict[str, Any]]] = Field(None, description="List of offers")
    count: Optional[int] = Field(None, description="Number of offers returned")
    personalized: Optional[bool] = Field(None, description="Whether offers are personalized")
    customer_id: Optional[str] = Field(None, description="Customer ID if personalized")

# --- Tool Implementations ---

def verify_customer(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Verify if a customer exists in the system and return basic customer information.
    
    This tool checks if a customer with the given ID exists in the database and
    returns basic customer information if found. It can be used to validate customer
    identity before performing other operations.
    
    Args:
        customer_id: The unique identifier of the customer to verify
        tool_context: Context object containing additional tool parameters
        
    Returns:
        A dictionary with verification status and customer details if found
        
    Example:
        ```python
        # Verify customer with ID 1 integer
        result = verify_customer(1, tool_context)
        if result['success']:
            print(f"Customer verified: {result['customer']['name']}")
        else:
            print(f"Verification failed: {result['error']}")
        ```
    """
    logger.info(f"Verifying customer with ID: {customer_id}")
    
    try:
        # Attempt to retrieve customer from database
        customer = db.get_customer(customer_id)
        
        if not customer:
            logger.warning(f"Customer not found with ID: {customer_id}")
            # Store the verifcation status of customer in tool_context
            tool_context.state["customer_verified"] = False
            return ToolResponse(
                success=False,
                error=f"No customer found with ID: {customer_id}",
                status="not_found"
            ).model_dump()
        
        # Customer found, return basic information
        logger.info(f"Customer verified successfully: {customer['name']}")
        # Store the verifcation status of customer in tool_context
        tool_context.state["customer_verified"] = True
        tool_context.state["customer_id"] = customer_id
        return ToolResponse(
            success=True,
            message="Customer verified successfully",
            status="verified",
            customer={
                "id": customer["id"],
                "name": customer["name"],
                "email": customer["email"],
                "phone": customer["phone"]
            }
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error verifying customer {customer_id}: {str(e)}")
        return ToolResponse(
            success=False,
            error=f"Error verifying customer: {str(e)}",
            status="error"
        ).model_dump()

def get_customer_account(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve account information for a specific customer.
    
    This tool retrieves account information for a customer. If an account_id is provided
    in the tool_context.params, it returns information for that specific account.
    Otherwise, it returns a list of all accounts belonging to the customer.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing additional parameters
            - account_id: (Optional) Specific account to retrieve
        
    Returns:
        A dictionary containing account information or an error message
        
    Example:
        ```python
        # Get all accounts for a customer
        all_accounts = get_customer_account(1, tool_context)
        
        # Get a specific account
        specific_account = get_customer_account(1, 
                                              tool_context.with_params(account_id=2))
        ```
    """
    logger.info(f"Retrieving account information for customer: {customer_id}")
    
    try:
        # Verify customer exists
        if not tool_context.state["customer_verified"]:
            logger.warning(f"Customer not found with ID: {customer_id}")
            return AccountResponse(
                success=False,
                error=f"Customer not found with ID: {customer_id}"
            ).model_dump()
        
        # Check if a specific account ID was provided
        account_id = tool_context.state.get("account_id")
        
        if account_id:
            # Get specific account
            logger.info(f"Retrieving specific account {account_id} for customer {customer_id}")
            account = db.get_customer_account(customer_id, account_id)
            
            if not account:
                logger.warning(f"Account {account_id} not found or doesn't belong to customer {customer_id}")
                return AccountResponse(
                    success=False,
                    error=f"Account {account_id} not found or doesn't belong to customer {customer_id}"
                ).model_dump()
            
            # Return the specific account information
            return AccountResponse(
                success=True,
                message=f"Account retrieved successfully",
                account_id=account["id"],
                account_number=account["account_number"],
                account_type=account["account_type"],
                balance=account["balance"],
                status=account["status"],
                created_at=account["created_at"]
            ).model_dump()
        else:
            # Get all accounts for customer
            logger.info(f"Retrieving all accounts for customer {customer_id}")
            accounts = db.get_customer_accounts(customer_id)
            
            # Format the accounts for the response
            account_list = [{
                "account_id": acc["id"],
                "account_number": acc["account_number"],
                "account_type": acc["account_type"],
                "balance": acc["balance"],
                "status": acc["status"],
                "created_at": acc["created_at"]
            } for acc in accounts]
            
            return AccountResponse(
                success=True,
                message=f"Retrieved {len(accounts)} accounts for customer {customer_id}",
                accounts=account_list
            ).model_dump()
            
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving accounts for customer {customer_id}: {str(e)}")
        return AccountResponse(
            success=False,
            error=f"Error retrieving accounts: {str(e)}"
        ).model_dump()

def get_customer_account_balance(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve the current balance for a customer's account.
    
    This tool retrieves the current balance for a specific account belonging to a customer.
    The account_id must be provided in the tool_context.params. The tool verifies that
    the account belongs to the specified customer before returning the balance.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - account_id: (Required) The account to retrieve the balance for
        
    Returns:
        A dictionary containing the account balance information or an error message
        
    Example:
        ```python
        # Get balance for account 'acc-456' belonging to customer 'cust-123'
        balance_info = get_customer_account_balance('cust-123', 
                                                  tool_context.with_params(account_id='acc-456'))
        if balance_info['success']:
            print(f"Current balance: {balance_info['balance']} {balance_info['currency']}")
        ```
    """
    logger.info(f"Retrieving account balance for customer: {customer_id}")
    
    try:
        # Check if account_id parameter was provided
        account_id = tool_context.params.get("account_id")
        is_verified = tool_context.state.get("customer_verified")
        if not is_verified:
            logger.warning("Customer not verified")
            return AccountResponse(
                success=False,
                error="Customer not verified ! Please enter your customer id again"
            ).model_dump()
        
        # Verify the account belongs to the customer
        logger.info(f"Verifying account {account_id} belongs to customer {customer_id}")
        account = db.get_customer_account(customer_id, account_id)
        
        if not account:
            logger.warning(f"Account {account_id} not found or doesn't belong to customer {customer_id}")
            return AccountResponse(
                success=False,
                error=f"Account {account_id} not found or doesn't belong to customer {customer_id}"
            ).model_dump()
        
        # Get the account balance
        balance = db.get_account_balance(account_id)
        current_time = datetime.now().isoformat()
        logger.info(f"Retrieved balance for account {account_id}: {balance} USD as of {current_time}")
        
        # Return the balance information
        return AccountResponse(
            success=True,
            message="Account balance retrieved successfully",
            account_id=account_id,
            account_number=account["account_number"],
            account_type=account["account_type"],
            balance=balance,
            currency="USD",  # Assuming USD as default
            status=account["status"],
            as_of=current_time
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving balance for account {account_id}: {str(e)}")
        return AccountResponse(
            success=False,
            error=f"Error retrieving account balance: {str(e)}"
        ).model_dump()

def get_customer_account_transactions(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve recent transactions for a customer's account.
    
    This tool retrieves recent transactions for a specific account belonging to a customer.
    The account_id must be provided in the tool_context.params. The tool supports pagination
    through optional limit and offset parameters.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - account_id: (Required) The account to retrieve transactions for
            - limit: (Optional) Maximum number of transactions to return (default: 10)
            - offset: (Optional) Number of transactions to skip for pagination (default: 0)
        
    Returns:
        A dictionary containing the list of transactions or an error message
        
    Example:
        ```python
        # Get the 10 most recent transactions for account 'acc-456'
        transactions = get_customer_account_transactions('cust-123', 
                                                      tool_context.with_params(account_id='acc-456'))
                                                      
        # Get the next page of transactions
        next_page = get_customer_account_transactions('cust-123', 
                                                   tool_context.with_params(
                                                       account_id='acc-456',
                                                       offset=10,
                                                       limit=10
                                                   ))
        ```
    """
    logger.info(f"Retrieving transactions for customer: {customer_id}")
    
    try:
        # Check if account_id parameter was provided
        account_id = tool_context.params.get("account_id")
        is_verified = tool_context.state.get("customer_verified")
        if not is_verified:
            logger.warning("Customer not verified")
            return TransactionResponse(
                success=False,
                error="Customer not verified ! Please enter your customer id again"
            ).model_dump()
        
        # Verify the account belo  ngs to the customer
        logger.info(f"Verifying account {account_id} belongs to customer {customer_id}")
        account = db.get_customer_account(customer_id, account_id)
        
        if not account:
            logger.warning(f"Account {account_id} not found or doesn't belong to customer {customer_id}")
            return TransactionResponse(
                success=False,
                error=f"Account {account_id} not found or doesn't belong to customer {customer_id}"
            ).model_dump()
        
        # Parse pagination parameters
        try:
            limit = int(tool_context.params.get("limit", 10))
            offset = int(tool_context.params.get("offset", 0))
        except ValueError:
            logger.warning("Invalid pagination parameters")
            return TransactionResponse(
                success=False,
                error="Invalid pagination parameters: limit and offset must be integers"
            ).model_dump()
        
        # Get the transactions
        logger.info(f"Retrieving transactions for account {account_id} (limit={limit}, offset={offset})")
        transactions = db.get_account_transactions(account_id, limit=limit, offset=offset)
        
        # Format the transactions for the response
        transaction_list = [{
            "transaction_id": tx["id"],
            "amount": tx["amount"],
            "type": tx["type"],
            "description": tx.get("description"),
            "date": tx["transaction_date"],
            "created_at": tx["created_at"]
        } for tx in transactions]
        
        # Return the transactions
        return TransactionResponse(
            success=True,
            message=f"Retrieved {len(transactions)} transactions for account {account_id}",
            account_id=account_id,
            account_number=account["account_number"],
            transactions=transaction_list,
            count=len(transactions),
            pagination={
                "limit": limit,
                "offset": offset,
                "total": len(transactions)  # Note: For accurate total count, we'd need a count query
            }
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving transactions for account {account_id}: {str(e)}")
        return TransactionResponse(
            success=False,
            error=f"Error retrieving transactions: {str(e)}"
        ).model_dump()

def get_customer_account_transactions_by_date(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve transactions for a customer's account within a specific date range.
    
    This tool retrieves transactions for a specific account belonging to a customer
    within a date range. The account_id and start_date must be provided in the
    tool_context.params. If end_date is not provided, it defaults to the current date.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - account_id: (Required) The account to retrieve transactions for
            - start_date: (Required) Start date in YYYY-MM-DD format
            - end_date: (Optional) End date in YYYY-MM-DD format (default: current date)
        
    Returns:
        A dictionary containing the filtered transactions or an error message
        
    Example:
        ```python
        # Get transactions between Jan 1, 2025 and Mar 31, 2025
        transactions = get_customer_account_transactions_by_date(
            1, 
            tool_context.with_params(
                account_id=2,
                start_date='2025-01-01',
                end_date='2025-03-31'
            )
        )
        ```
    """
    logger.info(f"Retrieving transactions by date range for customer: {customer_id}")
    
    try:
        # Get and validate required parameters
        account_id = tool_context.params.get("account_id")
        start_date = tool_context.params.get("start_date")
        end_date = tool_context.params.get("end_date", datetime.now().date().isoformat())
        
        # Check required parameters
        if not all([account_id, start_date]):
            logger.warning("Missing required parameters")
            return TransactionResponse(
                success=False,
                error="account_id and start_date parameters are required"
            ).model_dump()
        
        # Validate date formats
        try:
            # Attempt to parse dates to validate format
            datetime.fromisoformat(start_date)
            datetime.fromisoformat(end_date)
        except ValueError:
            logger.warning("Invalid date format")
            return TransactionResponse(
                success=False,
                error="Invalid date format. Dates must be in YYYY-MM-DD format."
            ).model_dump()
        
        # Verify the account belongs to the customer
        logger.info(f"Verifying account {account_id} belongs to customer {customer_id}")
        account = db.get_customer_account(customer_id, account_id)
        
        if not account:
            logger.warning(f"Account {account_id} not found or doesn't belong to customer {customer_id}")
            return TransactionResponse(
                success=False,
                error=f"Account {account_id} not found or doesn't belong to customer {customer_id}"
            ).model_dump()
        
        # Get transactions within the date range
        logger.info(f"Retrieving transactions for account {account_id} between {start_date} and {end_date}")
        transactions = db.get_transactions_by_date_range(account_id, start_date, end_date)
        
        # Format the transactions for the response
        transaction_list = [{
            "transaction_id": tx["id"],
            "amount": tx["amount"],
            "type": tx["type"],
            "description": tx.get("description"),
            "date": tx["transaction_date"],
            "created_at": tx["created_at"]
        } for tx in transactions]
        
        # Return the transactions
        return TransactionResponse(
            success=True,
            message=f"Retrieved {len(transactions)} transactions between {start_date} and {end_date}",
            account_id=account_id,
            account_number=account["account_number"],
            transactions=transaction_list,
            count=len(transactions),
            start_date=start_date,
            end_date=end_date
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving transactions by date: {str(e)}")
        return TransactionResponse(
            success=False,
            error=f"Error retrieving transactions by date: {str(e)}"
        ).model_dump()

def get_customer_account_transactions_by_type(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve transactions of a specific type for a customer's account.
    
    This tool retrieves transactions of a specific type for an account belonging to a customer.
    Both account_id and transaction_type must be provided in the tool_context.params.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - account_id: (Required) The account to retrieve transactions for
            - transaction_type: (Required) Type of transactions to retrieve (e.g., 'Deposit', 'Withdrawal')
        
    Returns:
        A dictionary containing the filtered transactions or an error message
        
    Example:
        ```python
        # Get all deposit transactions for account 'acc-456'
        deposits = get_customer_account_transactions_by_type(
            1, 
            tool_context.with_params(
                account_id=2,
                transaction_type='Deposit'
            )
        )
        ```
    """
    logger.info(f"Retrieving transactions by type for customer: {customer_id}")
    
    try:
        # Get required parameters
        account_id = tool_context.params.get("account_id")
        transaction_type = tool_context.params.get("transaction_type")
        
        # Check required parameters
        if not all([account_id, transaction_type]):
            logger.warning("Missing required parameters")
            return TransactionResponse(
                success=False,
                error="account_id and transaction_type parameters are required"
            ).model_dump()
        
        # Verify the account belongs to the customer
        logger.info(f"Verifying account {account_id} belongs to customer {customer_id}")
        account = db.get_customer_account(customer_id, account_id)
        
        if not account:
            logger.warning(f"Account {account_id} not found or doesn't belong to customer {customer_id}")
            return TransactionResponse(
                success=False,
                error=f"Account {account_id} not found or doesn't belong to customer {customer_id}"
            ).model_dump()
        
        # Get transactions of the specified type
        logger.info(f"Retrieving {transaction_type} transactions for account {account_id}")
        transactions = db.get_transactions_by_type(account_id, transaction_type)
        
        # Format the transactions for the response
        transaction_list = [{
            "transaction_id": tx["id"],
            "amount": tx["amount"],
            "type": tx["type"],
            "description": tx.get("description"),
            "date": tx["transaction_date"],
            "created_at": tx["created_at"]
        } for tx in transactions]
        
        # Return the transactions
        return TransactionResponse(
            success=True,
            message=f"Retrieved {len(transactions)} {transaction_type} transactions",
            account_id=account_id,
            account_number=account["account_number"],
            transactions=transaction_list,
            count=len(transactions),
            transaction_type=transaction_type
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving transactions by type: {str(e)}")
        return TransactionResponse(
            success=False,
            error=f"Error retrieving transactions by type: {str(e)}"
        ).model_dump()

def get_customer_complaint(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve all complaints for a customer.
    
    This tool retrieves complaints for a customer. It supports pagination through
    optional limit and offset parameters in the tool_context.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - limit: (Optional) Maximum number of complaints to return (default: 10)
            - offset: (Optional) Number of complaints to skip for pagination (default: 0)
        
    Returns:
        A dictionary containing the list of complaints or an error message
        
    Example:
        ```python
        # Get the 10 most recent complaints for customer 1
        complaints = get_customer_complaint(1, tool_context)
        
        # Get the next page of complaints
        next_page = get_customer_complaint(1, 
                                        tool_context.with_params(offset=10, limit=10))
        ```
    """
    logger.info(f"Retrieving complaints for customer: {customer_id}")
    
    try:
        # Verify customer exists
        if not db.verify_customer(customer_id):
            logger.warning(f"Customer not found with ID: {customer_id}")
            return ComplaintResponse(
                success=False,
                error=f"Customer not found with ID: {customer_id}"
            ).model_dump()
        
        # Parse pagination parameters
        try:
            limit = int(tool_context.params.get("limit", 10))
            offset = int(tool_context.params.get("offset", 0))
        except ValueError:
            logger.warning("Invalid pagination parameters")
            return ComplaintResponse(
                success=False,
                error="Invalid pagination parameters: limit and offset must be integers"
            ).model_dump()
        
        # Get the complaints
        logger.info(f"Retrieving complaints for customer {customer_id} (limit={limit}, offset={offset})")
        complaints = db.get_customer_complaints(customer_id, limit=limit, offset=offset)
        
        # Format the complaints for the response
        complaint_list = [{
            "complaint_id": comp["id"],
            "title": comp["title"],
            "type": comp.get("complaint_type_name", "Unknown"),
            "status": comp["status"],
            "priority": comp["priority"],
            "created_at": comp["created_at"],
            "updated_at": comp.get("updated_at"),
            "resolved_at": comp.get("resolved_at")
        } for comp in complaints]
        
        # Return the complaints
        return ComplaintResponse(
            success=True,
            message=f"Retrieved {len(complaints)} complaints for customer {customer_id}",
            customer_id=customer_id,
            complaints=complaint_list,
            pagination={
                "limit": limit,
                "offset": offset,
                "total": len(complaints)  # Note: For accurate total count, we'd need a count query
            }
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving complaints for customer {customer_id}: {str(e)}")
        return ComplaintResponse(
            success=False,
            error=f"Error retrieving complaints: {str(e)}"
        ).model_dump()

def get_customer_complaint_by_id(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve a specific complaint by ID for a customer.
    
    This tool retrieves a specific complaint by its ID for a customer. The complaint_id
    must be provided in the tool_context.params. The tool verifies that the complaint
    belongs to the specified customer before returning the details.
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - complaint_id: (Required) The unique identifier of the complaint to retrieve
        
    Returns:
        A dictionary containing the complaint details or an error message
        
    Example:
        ```python
        # Get details for complaint 'comp-789' belonging to customer 'cust-123'
        complaint = get_customer_complaint_by_id(
            1, 
            tool_context.with_params(complaint_id=2)
        )
        ```
    """
    logger.info(f"Retrieving complaint by ID for customer: {customer_id}")
    
    try:
        # Check if complaint_id parameter was provided
        complaint_id = tool_context.params.get("complaint_id")
        if not complaint_id:
            logger.warning("Missing required parameter: complaint_id")
            return ComplaintResponse(
                success=False,
                error="complaint_id parameter is required"
            ).model_dump()
        
        # Get the complaint
        logger.info(f"Retrieving complaint {complaint_id} for customer {customer_id}")
        complaint = db.get_complaint_by_id(complaint_id, customer_id=customer_id)
        
        if not complaint:
            logger.warning(f"Complaint {complaint_id} not found or doesn't belong to customer {customer_id}")
            return ComplaintResponse(
                success=False,
                error=f"Complaint {complaint_id} not found or doesn't belong to customer {customer_id}"
            ).model_dump()
        
        # Return the complaint details
        return ComplaintResponse(
            success=True,
            message="Complaint retrieved successfully",
            customer_id=customer_id,
            complaint_id=complaint["id"],
            title=complaint["title"],
            type=complaint.get("complaint_type_name", "Unknown"),
            status=complaint["status"],
            priority=complaint["priority"],
            created_at=complaint["created_at"],
            updated_at=complaint.get("updated_at"),
            resolved_at=complaint.get("resolved_at")
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving complaint {complaint_id}: {str(e)}")
        return ComplaintResponse(
            success=False,
            error=f"Error retrieving complaint: {str(e)}"
        ).model_dump()

def create_customer_complaint(customer_id: int, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Create a new complaint for a customer.
    
    This tool creates a new complaint for a customer. The required parameters
    (type_id, title, description) must be provided in the tool_context.params.
    The priority parameter is optional and defaults to "Medium".
    
    Args:
        customer_id: The unique identifier of the customer
        tool_context: Context object containing parameters
            - type_id: (Required) The type of complaint (e.g., 'ct-001' for Account Issue)
            - title: (Required) A brief title for the complaint
            - description: (Required) Detailed description of the complaint
            - priority: (Optional) Priority level (default: "Medium")
        
    Returns:
        A dictionary containing the created complaint details or an error message
        
    Example:
        ```python
        # Create a new complaint for customer 'cust-123'
        new_complaint = create_customer_complaint(
            1, 
            tool_context.with_params(
                type_id='ct-001',
                title='Unauthorized Transaction',
                description='I noticed an unauthorized transaction on my account...',
                priority='High'
            )
        )
        ```
    """
    logger.info(f"Creating new complaint for customer: {customer_id}")
    
    try:
        # Verify customer exists
        if not db.verify_customer(customer_id):
            logger.warning(f"Customer not found with ID: {customer_id}")
            return ComplaintResponse(
                success=False,
                error=f"Customer not found with ID: {customer_id}"
            ).model_dump()
        
        # Check required parameters
        required_fields = ["type_id", "title", "description"]
        missing_fields = [field for field in required_fields if field not in tool_context.params]
        
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            logger.warning(f"Missing required fields: {missing_fields_str}")
            return ComplaintResponse(
                success=False,
                error=f"Missing required fields: {missing_fields_str}"
            ).model_dump()
        
        # Create the complaint
        logger.info(f"Creating complaint for customer {customer_id} with type {tool_context.params['type_id']}")
        
        try:
            complaint_id = db.create_complaint(
                customer_id=customer_id,
                type_id=tool_context.params["type_id"],
                title=tool_context.params["title"],
                description=tool_context.params["description"],
                priority=tool_context.params.get("priority", "Medium")
            )
            
            # Get the created complaint
            complaint = db.get_complaint_by_id(complaint_id)
            
            if not complaint:
                logger.error(f"Failed to retrieve created complaint with ID: {complaint_id}")
                return ComplaintResponse(
                    success=False,
                    error="Complaint was created but could not be retrieved"
                ).model_dump()
            
            # Return the created complaint
            logger.info(f"Successfully created complaint with ID: {complaint_id}")
            return ComplaintResponse(
                success=True,
                message="Complaint created successfully",
                customer_id=customer_id,
                complaint_id=complaint["id"],
                title=complaint["title"],
                type=complaint.get("complaint_type_name", "Unknown"),
                status=complaint["status"],
                priority=complaint["priority"],
                created_at=complaint["created_at"],
                updated_at=complaint.get("updated_at")
            ).model_dump()
            
        except Exception as e:
            logger.error(f"Database error creating complaint: {str(e)}")
            return ComplaintResponse(
                success=False,
                error=f"Database error creating complaint: {str(e)}"
            ).model_dump()
            
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error creating complaint for customer {customer_id}: {str(e)}")
        return ComplaintResponse(
            success=False,
            error=f"Error creating complaint: {str(e)}"
        ).model_dump()

def get_product(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve information about banking products.
    
    This tool retrieves information about available banking products. It supports
    optional filtering by product_id or product type.
    
    Args:
        tool_context: Context object containing parameters
            - product_id: (Optional) Filter by specific product ID
            - type: (Optional) Filter by product type (e.g., 'Savings', 'Checking', 'Loan')
        
    Returns:
        A dictionary containing product information or an error message
        
    Example:
        ```python
        # Get all products
        all_products = get_product(tool_context)
        
        # Get products of a specific type
        savings_products = get_product(tool_context.with_params(type='Savings'))
        
        # Get a specific product by ID
        specific_product = get_product(tool_context.with_params(product_id='prod-001'))
        ```
    """
    logger.info("Retrieving banking products")
    
    try:
        # Get filter parameters
        product_id = tool_context.params.get("product_id")
        product_type = tool_context.params.get("type")
        
        # Log the filter parameters if provided
        if product_id:
            logger.info(f"Filtering products by ID: {product_id}")
        if product_type:
            logger.info(f"Filtering products by type: {product_type}")
        
        # Get all products from the database
        products = db.get_products()
        
        # Apply filters if provided
        filtered_products = products
        if product_id:
            filtered_products = [p for p in filtered_products if p["id"] == product_id]
        if product_type:
            filtered_products = [p for p in filtered_products if p["type"].lower() == product_type.lower()]
        
        # Format the products for the response
        product_list = [{
            "id": prod["id"],
            "name": prod["name"],
            "type": prod["type"],
            "description": prod.get("description")
        } for prod in filtered_products]
        
        # Return the products
        logger.info(f"Retrieved {len(filtered_products)} products matching the criteria")
        return ProductResponse(
            success=True,
            message=f"Retrieved {len(filtered_products)} products",
            products=product_list,
            count=len(filtered_products)
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving products: {str(e)}")
        return ProductResponse(
            success=False,
            error=f"Error retrieving products: {str(e)}"
        ).model_dump()

def get_current_offers(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve current banking offers, optionally personalized for a customer.
    
    This tool retrieves current banking offers. If a customer_id is provided in the
    tool_context.params, it returns personalized offers for that customer. Otherwise,
    it returns general offers available to all customers.
    
    Args:
        tool_context: Context object containing parameters
            - customer_id: (Optional) Customer ID to retrieve personalized offers for
        
    Returns:
        A dictionary containing current offers or an error message
        
    Example:
        ```python
        # Get general offers
        general_offers = get_current_offers(tool_context)
        
        # Get personalized offers for a specific customer
        personalized_offers = get_current_offers(
            tool_context.with_params(customer_id=1)
        )
        ```
    """
    logger.info("Retrieving current banking offers")
    
    try:
        # Check if customer_id parameter was provided
        customer_id = tool_context.params.get("customer_id")
        
        # If customer_id is provided, verify the customer exists
        if customer_id:
            logger.info(f"Retrieving personalized offers for customer: {customer_id}")
            if not db.verify_customer(customer_id):
                logger.warning(f"Customer not found with ID: {customer_id}")
                return OfferResponse(
                    success=False,
                    error=f"Customer not found with ID: {customer_id}"
                ).model_dump()
        else:
            logger.info("Retrieving general offers for all customers")
        
        # Get offers from the database
        offers = db.get_current_offers(customer_id)
        
        # Format the offers for the response
        offer_list = [{
            "id": offer["id"],
            "title": offer["title"],
            "description": offer["description"]
        } for offer in offers]
        
        # Return the offers
        is_personalized = customer_id is not None
        message = f"Retrieved {len(offers)} {'personalized' if is_personalized else 'general'} offers"
        logger.info(message)
        
        return OfferResponse(
            success=True,
            message=message,
            offers=offer_list,
            count=len(offers),
            personalized=is_personalized,
            customer_id=customer_id if is_personalized else None
        ).model_dump()
        
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error retrieving offers: {str(e)}")
        return OfferResponse(
            success=False,
            error=f"Error retrieving offers: {str(e)}"
        ).model_dump()



