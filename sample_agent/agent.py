from google.adk.agents import Agent
from .tools.tools import get_greeting, get_farewell, get_current_time

root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge, additionally you can use tools for greeting, farewell and current time.',
    tools=[get_greeting, get_farewell, get_current_time],
)
