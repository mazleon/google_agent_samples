# Google Agent Development Kit (ADK) - Project: Sample Agent

A Python-based agent implementation using Google's ADK with simple responsibilities.

## Web Interface

The agent provides a user-friendly web interface for easy interaction:

![Sample Agent Web Interface](res/sample_agent.png)
*Web interface of the Sample Agent running on localhost:8000*

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

## Running the Agent

### CLI Mode
```bash
adk run sample_agent
```

### Web Interface
```bash
adk web
```
Then visit `http://localhost:8000` in your browser to interact with the agent through the web interface shown above.

## Available Tools

The agent comes with several built-in tools to enhance interaction:

### Custom Tools
- **Greetings**: Returns a random greeting from the greeting_styles list
- **Farewell**: Returns a random farewell from the farewell_styles list
- **Current Time**: Returns the current time

For implementation details, see [tools.py](tools/tools.py)
