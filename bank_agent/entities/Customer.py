"""Pydantic models for bank customer data management."""
from datetime import date
from enum import Enum
from typing import List, Optional, Dict, ForwardRef
from pydantic import BaseModel, Field, EmailStr, validator, constr

# Forward reference for Customer class to handle circular imports
Customer.update_forward_refs()

class TransactionType(str, Enum):
    """Enumeration of possible transaction types."""
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"
    PAYMENT = "Payment"

class AccountStatus(str, Enum):
    """Enumeration of possible account statuses."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    CLOSED = "Closed"

class AccountType(str, Enum):
    """Enumeration of possible account types."""
    SAVINGS = "Savings"
    CHECKING = "Checking"
    CREDIT = "Credit"
    LOAN = "Loan"

class Transaction(BaseModel):
    """Represents a financial transaction."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    type: TransactionType = Field(..., description="Type of transaction")
    date: date = Field(..., description="Date of transaction")
    description: Optional[str] = Field(None, max_length=200, description="Optional transaction description")
    
    @field_validator('date')
    def validate_date_not_future(cls, v):
        if v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v

class Account(BaseModel):
    """Represents a bank account."""
    account_id: str = Field(..., description="Unique account identifier")
    account_number: constr(min_length=10, max_length=20) = Field(..., description="Account number")
    balance: float = Field(0.0, description="Current account balance")
    account_type: AccountType = Field(..., description="Type of account")
    account_status: AccountStatus = Field(AccountStatus.ACTIVE, description="Current status of the account")
    transactions: List[Transaction] = Field(default_factory=list, description="List of account transactions")
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the account and update balance."""
        if transaction.type == TransactionType.WITHDRAWAL and transaction.amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal")
            
        self.transactions.append(transaction)
        if transaction.type in [TransactionType.DEPOSIT, TransactionType.TRANSFER]:
            self.balance += transaction.amount
        else:
            self.balance -= transaction.amount

class Customer(BaseModel):
    """Represents a bank customer with associated accounts."""
    customer_id: str = Field(..., description="Unique customer identifier")
    name: str = Field(..., min_length=2, max_length=100, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer's email address")
    phone: constr(regex=r'^\+?[0-9]{10,15}$') = Field(..., description="Customer's phone number")
    address: str = Field(..., min_length=5, max_length=200, description="Customer's address")
    dob: date = Field(..., description="Customer's date of birth")
    accounts: List[Account] = Field(default_factory=list, description="List of customer's accounts")
    
    @field_validator('dob')
    def validate_age(cls, v):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        return v

# Type hints for forward references
Customer.model_rebuild()

# Sample data
SAMPLE_CUSTOMERS: Dict[str, Customer] = {
    "customer-001": Customer(
        customer_id="customer-001",
        name="Mazharul Islam Leon",
        email="mazharul.islam@example.com",
        phone="+8801833184122",
        address="Dhaka, Bangladesh",
        dob=date(1995, 5, 1),
        accounts=[
            Account(
                account_id="acc-001",
                account_number="1234567890",
                balance=100000.00,
                account_type=AccountType.SAVINGS,
                account_status=AccountStatus.ACTIVE,
                transactions=[
                    Transaction(
                        transaction_id="trans-001",
                        amount=100.00,
                        type=TransactionType.DEPOSIT,
                        date=date(2025, 5, 19),
                        description="Initial deposit"
                    ),
                    # Add more transactions as needed
                ]
            )
        ]
    ),
    # Add more customers as needed
    "customer-002": Customer(
        customer_id="customer-002",
        name="Mr. John Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        address="123 Main St, Springfield, IL 62701, USA",
        dob=date(1995, 5, 2),
        accounts=[
            Account(
                account_id="acc-002",
                account_number="1234567890",
                balance=100000.00,
                account_type=AccountType.SAVINGS,
                account_status=AccountStatus.ACTIVE,
                transactions=[
                    Transaction(
                        transaction_id="trans-001",
                        amount=100.00,
                        type=TransactionType.DEPOSIT,
                        date=date(2025, 5, 19),
                        description="Initial deposit"
                    ),
                    # Add more transactions as needed
                ]
            )
        ]
    )
}
