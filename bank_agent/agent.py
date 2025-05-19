""" Agent for bank assistant."""

import os
import sys

# Get the current directory and add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from google.adk.agents import Agent
from prompt import GLOBAL_INSTRUCTION, INSTRUCTION
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

root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='root_agent',
    description=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    tools=[
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
    ],
)
