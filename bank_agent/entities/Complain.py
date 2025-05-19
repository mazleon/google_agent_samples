"""Pydantic models for handling customer complaints in the banking system.

This module defines the data models for complaint types and customer complaints,
including validation and helper methods for complaint management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator, constr
from uuid import uuid4, UUID


class ComplaintStatus(str, Enum):
    """Enumeration of possible complaint statuses."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    REJECTED = "Rejected"
    REOPENED = "Reopened"
    ESCALATED = "Escalated"


class ComplaintPriority(str, Enum):
    """Enumeration of complaint priorities."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComplaintType(str, Enum):
    """Enumeration of standard complaint types."""
    ACCOUNT_ISSUE = "Account Issue"
    TRANSACTION_PROBLEM = "Transaction Problem"
    CARD_ISSUE = "Card Issue"
    LOAN_QUERY = "Loan Query"
    INTERNET_BANKING = "Internet Banking"
    CUSTOMER_SERVICE = "Customer Service"
    FRAUD = "Fraud"
    OTHER = "Other"


class ComplainType(BaseModel):
    """Model representing a type of complaint with its metadata.
    
    Attributes:
        id: Unique identifier for the complaint type (UUID)
        name: Human-readable name of the complaint type
        description: Detailed description of when to use this complaint type
        is_active: Whether this complaint type is currently active
        requires_escalation: Whether this type of complaint requires escalation
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the complaint type")
    name: str = Field(..., min_length=3, max_length=100, description="Name of the complaint type")
    description: str = Field(..., min_length=10, max_length=500, description="Description of the complaint type")
    is_active: bool = Field(True, description="Whether this complaint type is active")
    requires_escalation: bool = Field(False, description="Whether this type requires escalation")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()


class Complain(BaseModel):
    """Model representing a customer complaint.
    
    Attributes:
        id: Unique identifier for the complaint (UUID)
        customer_id: Reference to the customer who made the complaint
        complain_type: Type of complaint
        title: Brief title/summary of the complaint
        description: Detailed description of the complaint
        status: Current status of the complaint
        priority: Priority level of the complaint
        created_at: Timestamp when the complaint was created
        updated_at: Timestamp when the complaint was last updated
        resolved_at: Timestamp when the complaint was resolved (if applicable)
        resolution_notes: Notes about how the complaint was resolved
        assigned_to: ID of the staff member assigned to handle the complaint
        attachments: List of file paths or references to attached documents
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the complaint")
    customer_id: UUID = Field(..., description="ID of the customer making the complaint")
    complain_type: ComplaintType = Field(..., description="Type of complaint")
    title: str = Field(..., min_length=5, max_length=200, description="Brief title of the complaint")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description of the complaint")
    status: ComplaintStatus = Field(default=ComplaintStatus.OPEN, description="Current status of the complaint")
    priority: ComplaintPriority = Field(default=ComplaintPriority.MEDIUM, description="Priority level of the complaint")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the complaint was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the complaint was last updated")
    resolved_at: Optional[datetime] = Field(None, description="When the complaint was resolved")
    resolution_notes: Optional[str] = Field(None, max_length=2000, description="Notes about how the complaint was resolved")
    assigned_to: Optional[UUID] = Field(None, description="ID of staff member assigned to handle the complaint")
    attachments: List[str] = Field(default_factory=list, description="List of file paths or references to attachments")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()

    def update_status(self, new_status: ComplaintStatus, notes: Optional[str] = None) -> None:
        """Update the status of the complaint and add resolution notes if provided."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == ComplaintStatus.RESOLVED and not self.resolved_at:
            self.resolved_at = datetime.utcnow()
        
        if notes:
            self.resolution_notes = notes if not self.resolution_notes else f"{self.resolution_notes}\n\n{notes}"

    def add_attachment(self, file_reference: str) -> None:
        """Add a reference to an attachment."""
        if file_reference not in self.attachments:
            self.attachments.append(file_reference)
            self.updated_at = datetime.utcnow()

    def assign_to(self, staff_id: UUID) -> None:
        """Assign the complaint to a staff member."""
        self.assigned_to = staff_id
        self.updated_at = datetime.utcnow()


# Sample complaint type definitions
STANDARD_COMPLAINT_TYPES = {
    ComplaintType.ACCOUNT_ISSUE: ComplainType(
        name=ComplaintType.ACCOUNT_ISSUE,
        description="Issues related to account access, statements, or account settings"
    ),
    ComplaintType.TRANSACTION_PROBLEM: ComplainType(
        name=ComplaintType.TRANSACTION_PROBLEM,
        description="Problems with transactions, including missing, incorrect, or unauthorized transactions"
    ),
    # Add other standard complaint types as needed
}