from google.adk.agents import Agent
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import before_agent
from customer_service_agent.tools.tool import (
    search_products, 
    get_order_status,
    get_cart_contents,
    modify_cart,
    get_payment_methods,
    get_return_policy,
)

root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='root_agent',
    description=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    tools=[search_products, get_order_status, get_cart_contents, modify_cart, get_payment_methods, get_return_policy],
)

# Example of running the agent
