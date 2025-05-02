"""Callback functions for Ecommerce Support Agent."""

import logging
import time
from typing import Any, Dict

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.adk.agents.invocation_context import InvocationContext

from customer_service_agent.entities.customer import Customer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RATE_LIMIT_SECS = 60
RPM_QUOTA = 10


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Rate-limits the number of requests per minute."""
    for content in llm_request.contents:
        for part in content.parts:
            if part.text == "":
                part.text = " "

    now = time.time()
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, req_count: 1, elapsed_secs: 0]",
            now,
        )
        return

    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i, elapsed_secs: %i]",
        now, request_count, elapsed_secs,
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("Sleeping for %i seconds", delay)
            time.sleep(delay)
        callback_context.state["timer_start"] = time.time()
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count


def lowercase_value(value):
    """Recursively convert all string values in a dictionary to lowercase."""
    if isinstance(value, dict):
        return {k: lowercase_value(v) for k, v in value.items()}
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


# def before_tool(
#     tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext
# ):
#     """Manipulate tool inputs and apply business rules before tool execution."""

#     args = lowercase_value(args)

#     # Example: automatic discount approval
#     if tool.name == "apply_discount":
#         amount = args.get("amount", 0)
#         if amount <= 5:
#             return {"result": "Discount approved automatically."}

#     # Example: handling shopping cart logic
#     if tool.name == "update_cart":
#         if args.get("items_added") and args.get("items_removed"):
#             return {"result": "Cart updated: items added and removed."}

#     # Example: check order status
#     if tool.name == "check_order_status":
#         order_id = args.get("order_id")
#         if not order_id:
#             return {"error": "Order ID is required to check status."}

#     return None


def before_agent(callback_context: InvocationContext):
    """Ensure that a customer profile is loaded into state."""
    if "customer_profile" not in callback_context.state:
        # In production, customer ID might be inferred from session or token
        callback_context.state["customer_profile"] = Customer.get_customer_by_id(
            "customer-001"
        ).to_json()
        logger.debug("Loaded customer profile into state.")
