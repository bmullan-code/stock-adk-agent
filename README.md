# Stock ADK Agent

A Python-based Google Agent Development Kit (ADK) agent that provides real-time stock information and financial data using a remote MCP server.

## Overview

This agent integrates with a remote Model Context Protocol (MCP) server to fetch stock prices and recent news headlines. It is designed to run in three different modes:
1.  **Standalone**: A direct Python script for quick testing.
2.  **Interactive CLI**: The official ADK interactive terminal interface.
3.  **Web UI**: A modern, feature-rich web interface for interacting with the agent.

## Setup

1.  **Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    The agent uses environment variables for configuration. Copy the template and update it with your settings:
    ```bash
    cp .env.example .env
    ```
    Alternatively, you can provide an ID token obtained from `gcloud auth print-identity-token` directly in the `.env` file or as an environment variable `MCP_ACCESS_TOKEN`.

    **Required Variables in `.env`**:
    - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
    - `GOOGLE_CLOUD_LOCATION`: The location for Vertex AI (default: `global`).
    - `GEMINI_MODEL`: The Gemini model version (default: `gemini-3-flash-preview`).
    - `MCP_SERVER_URL`: The URL of the remote MCP server.
    - `MCP_ACCESS_TOKEN`: Your Google ID token for authentication.



## Running the Agent

### 1. Standalone Mode
Run the agent as a simple Python script:
```bash
python agent.py
```

### 2. Interactive CLI Mode
Use the ADK CLI to run the agent in your terminal:
```bash
adk run agents/stock_agent
```

### 3. Web UI Mode
Launch the ADK Web UI for a richer experience:
```bash
adk web agents --port 8081
```
Then navigate to `http://127.0.0.1:8081` in your browser.

## Project Structure

- `agent.py`: Standalone entry point.
- `agents/stock_agent/`: The core agent package.
    - `agent.py`: Agent definition and tool configuration.
    - `__init__.py`: Package initialization.
- `requirements.txt`: Python dependencies.
