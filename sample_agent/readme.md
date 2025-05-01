# Google Agent Development Kit (ADK) - Project: Sample Agent

A Python-based agent implementation using Google's ADK with simple responsibilities.

## Project Structure
- `sample_agent/`: Main agent implementation directory
- `.venv/`: Virtual environment directory
- sample_agent/
  - __init__.py
  - agent.py
  - tools/
    - __init__.py
    - tools.py

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install google-adk
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
4. Run the agent:
   - CLI based run
   ```bash
   adk run sample_agent
   ```
- Web based run
   ```bash
   adk web
   ```
Then go to `http://localhost:8000` in your browser.
## Tools
- [tools.py](cci:7://file:///Users/saniyasultanatuba/Desktop/Python-dev/llm/google_agemt/sample_agent/tools/tools.py:0:0-0:0): Contains custom tools for the agent

## Custom Tools
- Greetings: Returns a random greeting from the greeting_styles list.
- Farewell: Returns a random farewell from the farewell_styles list.
- Current Time: Returns the current time.

