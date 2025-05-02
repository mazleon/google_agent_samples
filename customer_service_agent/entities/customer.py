"""Entities for NovaCart Ecommerce Platform."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

class Address(BaseModel):
    """
    Represents a customer's shipping or billing address.
    """

    street: str
    city: str
    state: str
    zip: str
    country: str
    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """
    Represents a product available on the ecommerce platform.
    """

    product_id: str
    name: str
    description: str
    price: float
    stock_quantity: int
    category: str
    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    """
    Represents an item in a customer's order.
    """

    product_id: str
    name: str
    quantity: int
    price: float
    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    """
    Represents a customer's order.
    """

    order_id: str
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    order_date: str
    status: str  # e.g., 'Pending', 'Shipped', 'Delivered', 'Cancelled'
    shipping_address: Address
    model_config = ConfigDict(from_attributes=True)


class PaymentMethod(BaseModel):
    """
    Represents a payment method used for a transaction.
    """

    method_id: str
    type: str  # e.g., 'Credit Card', 'PayPal', 'Gift Card'
    last_four_digits: Optional[str]  # e.g., '1234' for Credit Card
    expiration_date: Optional[str]  # e.g., '12/25' for Credit Card
    billing_address: Address
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    Represents a customer of the ecommerce platform.
    """

    account_number: str
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    registration_date: str
    loyalty_points: int
    shipping_address: Address
    billing_address: Address
    payment_methods: List[PaymentMethod]
    order_history: List[Order]
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        Converts the Customer object to a JSON string.
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer_by_id(customer_id: str) -> Optional["Customer"]:
        """
        Retrieves a customer based on their ID.

        Args:
            customer_id: The ID of the customer to retrieve.

        Returns:
            The Customer object if found, None otherwise.
        """
        # Example customer data for illustration.
        return Customer(
            account_number="987654321",
            customer_id="123",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="+1-555-555-1234",
            registration_date="2023-01-15",
            loyalty_points=120,
            shipping_address=Address(
                street="456 Elm St", city="Springfield", state="IL", zip="62701", country="USA"
            ),
            billing_address=Address(
                street="456 Elm St", city="Springfield", state="IL", zip="62701", country="USA"
            ),
            payment_methods=[
                PaymentMethod(
                    method_id="pm_12345",
                    type="Credit Card",
                    last_four_digits="1234",
                    expiration_date="12/25",
                    billing_address=Address(
                        street="456 Elm St", city="Springfield", state="IL", zip="62701", country="USA"
                    )
                ),
                PaymentMethod(
                    method_id="pm_67890",
                    type="PayPal",
                    last_four_digits=None,
                    expiration_date=None,
                    billing_address=Address(
                        street="456 Elm St", city="Springfield", state="IL", zip="62701", country="USA"
                    )
                ),
            ],
            order_history=[
                Order(
                    order_id="ORD123456",
                    customer_id=customer_id,
                    items=[
                        OrderItem(
                            product_id="prod_001",
                            name="Wireless Mouse",
                            quantity=2,
                            price=19.99
                        ),
                        OrderItem(
                            product_id="prod_002",
                            name="Keyboard",
                            quantity=1,
                            price=49.99
                        )
                    ],
                    total_amount=89.97,
                    order_date="2024-04-01",
                    status="Shipped",
                    shipping_address=Address(
                        street="456 Elm St", city="Springfield", state="IL", zip="62701", country="USA"
                    )
                ),
            ]
        )


# --- Additional Pydantic Models for Tool Return Types ---

class ProductSearchResult(BaseModel):
    """Results of a product search."""
    results: List[Product] = Field(..., description="List of products matching the search query.")

class Availability(BaseModel):
    """Represents the availability status of a product."""
    available: bool = Field(..., description="Whether the product is currently in stock.")
    quantity: Optional[int] = Field(None, description="The quantity available if in stock.")
    error: Optional[str] = Field(None, description="Error message if the product is not found.")

class OrderStatus(BaseModel):
    """Represents the status of an order."""
    status: Optional[str] = Field(None, description="Current status of the order (e.g., Shipped, Processing).")
    eta: Optional[str] = Field(None, description="Estimated time of arrival or completion.")
    error: Optional[str] = Field(None, description="Error message if the order is not found.")

class CartItem(BaseModel):
    """Represents an item in a customer's shopping cart."""
    product_id: str
    name: str
    quantity: int
    price: float

class Cart(BaseModel):
    """Represents a customer's shopping cart."""
    items: List[CartItem] = Field(..., description="List of items currently in the cart.")

class ModifyCartResult(BaseModel):
    """Result of modifying a shopping cart."""
    message: str = Field(..., description="Confirmation message indicating the cart was updated.")
    cart: List[CartItem] = Field(..., description="The updated list of items in the cart.")

class PaymentMethodsResult(BaseModel):
    """List of supported payment methods."""
    methods: List[str] = Field(..., description="A list containing the names of supported payment methods.")

class ReturnPolicyResult(BaseModel):
    """Contains the store's return policy."""
    policy: str = Field(..., description="The text of the return and refund policy.")
