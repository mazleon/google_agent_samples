# Proposed change for /Users/saniyasultanatuba/Downloads/Python-dev/llm/google_agemt/customer_service_agent/tools/tools.py
from typing import List, Dict, Optional
# Import models from your entities file
from customer_service_agent.entities.customer import (
    Product,
    ProductSearchResult,
    Availability,
    OrderStatus,
    CartItem,
    Cart,
    ModifyCartResult,
    PaymentMethodsResult,
    ReturnPolicyResult
)

# --- Dummy Data ---

# Using imported Pydantic models for dummy data
PRODUCT_CATALOG: List[Product] = [
    # Adjusted to match the likely fields in entities.customer.Product
    Product(
        product_id="prd001",
        name="Garden Shovel",
        stock_quantity=15, # Changed from quantity
        description="A sturdy garden shovel.", # Added
        price=25.99, # Added
        category="Gardening Tools" # Added
    ),
    Product(
        product_id="prd002",
        name="Tomato Seeds Pack",
        stock_quantity=50, # Changed from quantity
        description="Pack of 50 heirloom tomato seeds.", # Added
        price=4.99, # Added
        category="Seeds" # Added
    ),
    Product(
        product_id="prd003",
        name="Plant Fertilizer",
        stock_quantity=25, # Changed from quantity
        description="All-purpose plant fertilizer (1kg).", # Added
        price=12.50, # Added
        category="Garden Supplies" # Added
    ),
]

CUSTOMER_CART: Dict[str, List[CartItem]] = {
    "customer-001": [
        # Assuming CartItem needs product_id, name, quantity, price
        # Note: Check if CartItem in entities/customer.py also requires price
        CartItem(product_id="prd002", name="Tomato Seeds Pack", quantity=2, price=4.99),
    ]
}

# Data for orders, payments, and policy
ORDER_STATUS_DATA: Dict[str, Dict[str, str]] = {
    "order123": {"status": "Shipped", "eta": "2025-05-05"},
    "order456": {"status": "Processing", "eta": "2025-05-07"},
}
PAYMENT_METHODS_DATA: List[str] = ["Credit Card", "PayPal", "Google Pay"]
RETURN_POLICY_DATA: str = "Returns accepted within 30 days of delivery. Refunds issued to original payment method."


# --- Tool Functions ---
def search_products(query: str) -> ProductSearchResult:
    """
    Searches the product catalog for items matching the query string.

    Args:
        query: The keyword(s) to search for in product names.

    Returns:
        A ProductSearchResult object containing a list of matching products.
    """
    results = [
        p for p in PRODUCT_CATALOG if query.lower() in p.name.lower()
    ]
    return ProductSearchResult(results=results)

def check_product_availability(product_id: str) -> Availability:
    """
    Checks the availability and quantity of a specific product.

    Args:
        product_id: The unique identifier of the product to check.

    Returns:
        An Availability object indicating if the product is available,
        its quantity, or an error if not found.
    """
    for product in PRODUCT_CATALOG:
        if product.product_id == product_id:
            return Availability(available=product.stock_quantity > 0, quantity=product.stock_quantity)
    return Availability(available=False, error="Product not found.")

def get_order_status(order_id: str) -> OrderStatus:
    """
    Retrieves the status and estimated time of arrival (ETA) for a given order ID.

    Args:
        order_id: The unique identifier of the order.

    Returns:
        An OrderStatus object containing the order's status and ETA,
        or an error if the order is not found.
    """
    status_data = ORDER_STATUS_DATA.get(order_id)
    if status_data:
        return OrderStatus(**status_data)
    return OrderStatus(status="Unknown", eta="N/A", error="Order not found.")

def get_cart_contents(customer_id: str) -> Cart:
    """
    Gets the items currently in the specified customer's shopping cart.

    Args:
        customer_id: The unique identifier of the customer.

    Returns:
        A Cart object containing a list of items in the customer's cart.
        Returns an empty cart if the customer is not found or cart is empty.
    """
    cart_items = CUSTOMER_CART.get(customer_id, [])
    return Cart(items=cart_items)

def modify_cart(customer_id: str, add: List[str] = [], remove: List[str] = []) -> ModifyCartResult:
    """
    Modifies the customer's shopping cart by adding or removing specified product IDs.
    Note: Currently adds items with a quantity of 1 or increments existing items.

    Args:
        customer_id: The unique identifier of the customer.
        add: A list of product IDs to add to the cart.
        remove: A list of product IDs to remove from the cart.

    Returns:
        A ModifyCartResult object confirming the update and showing the new cart contents.
    """
    cart = CUSTOMER_CART.get(customer_id, [])
    cart_dict: Dict[str, CartItem] = {item.product_id: item for item in cart}

    # Process removals
    for pid in remove:
        if pid in cart_dict:
            del cart_dict[pid]

    # Process additions
    for pid in add:
        product_in_catalog = next((p for p in PRODUCT_CATALOG if p.product_id == pid), None)
        if product_in_catalog:
            if pid in cart_dict:
                cart_dict[pid].quantity += 1
            else:
                cart_dict[pid] = CartItem(product_id=pid, name=product_in_catalog.name, quantity=1, price=product_in_catalog.price)

    updated_cart_list = list(cart_dict.values())
    CUSTOMER_CART[customer_id] = updated_cart_list
    return ModifyCartResult(message="Cart updated successfully.", cart=updated_cart_list)

def get_payment_methods() -> PaymentMethodsResult:
    """
    Retrieves the list of available payment methods.

    Returns:
        A PaymentMethodsResult object containing a list of supported payment method names.
    """
    return PaymentMethodsResult(methods=PAYMENT_METHODS_DATA)

def get_return_policy() -> ReturnPolicyResult:
    """
    Retrieves the store's return policy information.

    Returns:
        A ReturnPolicyResult object containing the text of the return policy.
    """
    return ReturnPolicyResult(policy=RETURN_POLICY_DATA)
