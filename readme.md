# Google Agent Development Kit (ADK)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains example implementations of intelligent agents built using Google's Agent Development Kit (ADK). These examples demonstrate best practices and common patterns for building AI-powered agents.

## 📚 Examples

- [Sample Agent](sample_agent/README.md) - A basic agent implementation showcasing core ADK features and patterns

## � Repository

```bash
git clone https://github.com/princexoleo/google_agent_samples.git
cd google_agent_samples
```

## �🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended)

### Installation

1. Install the `uv` package manager:
```bash
pip install uv
```

2. Initialize and activate the virtual environment:
```bash
uv init
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install google-adk
```

### Creating a New Agent

Create a new agent project using the ADK CLI:
```bash
adk create name_of_agent_directory
```

This will generate the following project structure:
```
name_of_agent_directory/
├── __init__.py
├── agent.py
└── .env
```

### Configuration

1. Set up your environment variables:
```bash
cp .env.example .env
```

2. Open `.env` and configure your API keys and other settings

### Running Your Agent

#### CLI Mode
```bash
adk run name_of_agent_directory
```

#### Web Interface
```bash
adk web
```
Then visit `http://localhost:8000` in your browser to access the web interface.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request to [our repository](https://github.com/princexoleo/google_agent_samples).
