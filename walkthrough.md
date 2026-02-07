# Stock ADK Agent Walkthrough

I have successfully implemented and verified the Stock ADK Agent. The agent can now connect to the remote MCP server and retrieve real-time stock information.

## Key Accomplishments

- **Corrected MCP Connection**: Switched from SSE to `StreamableHTTPConnectionParams` to match the Cloud Run server's protocol.
- **Authentication**: Implemented Bearer token authentication using an ID token for the remote MCP server.
- **LLM Backend Configuration**: Resolved the "Missing key inputs" error by monkeypatching the `google.genai.Client` to force Vertex AI usage with the correct project and location.
- **Standalone Execution**: Added a `run_standalone` method to `agent.py` to allow the agent to be run directly via `python agent.py`.

## Implementation Details

### MCP Connection Setup
The agent now uses the following configuration to connect to the remote MCP server:

```python
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://stock-mcp-xklq3ziy3q-uc.a.run.app/mcp",
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
    )
)
```

### LLM Backend Fix
To ensure the Gemini model works with Vertex AI without requiring complex manual setup, I've applied a client monkeypatch:

```python
_original_client_init = google.genai.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs['vertexai'] = True
    kwargs['project'] = "mullan-gmail-com"
    kwargs['location'] = "us-central1"
    _original_client_init(self, *args, **kwargs)
google.genai.Client.__init__ = _patched_client_init
```

## Verification Results

I verified the agent's functionality with a mock input query: "What is the current stock price of Google (GOOGL)?".

### Proof of Work

```bash
Stock Agent is ready. Type 'exit' to quit.

You: What is the current stock price of Google (GOOGL)?
Agent: The current stock price of Google (GOOGL) is $322.86.
```

The agent successfully called the `get_stock_price` tool from the remote MCP server and provided the correct response.

## Running with ADK Web

You can also run the agent using the ADK Web UI. I've restructured the project to support this by creating an `agents/` directory.

To start the web UI:
```bash
source .venv/bin/activate
adk web agents --port 8081
```

### Web UI Verification
The agent is correctly discovered and listed in the ADK Web UI.

### Final Query Test
I tested the agent with the complex query: **"show price and news for avgo"**.

The agent successfully:
1.  Called `get_stock_price` for AVGO.
2.  Called `get_stock_news` for AVGO.
3.  Synthesized the data into a final response.

## Configuration Refactoring

I've refactored the project to use a `.env` file for all confidential and project-specific configurations.

### Key Changes
- **Environment Variables**: Moved `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `MCP_SERVER_URL`, and `MCP_ACCESS_TOKEN` to `.env`.
- **Template**: Created `.env.example` as a starting point for new environments.
- **Code Cleanup**: Updated both `agent.py` and `agents/stock_agent/agent.py` to use `os.getenv()`.
- **README Update**: Added detailed configuration instructions to the `README.md`.

The agent remains fully functional and more secure!

## Gemini 3 and Global Location Test

I've updated the agent to use the **`gemini-3-flash-preview`** model and the **`global`** location for Vertex AI.

### Verification Results
I tested the agent with both **AVGO** and **MSFT** queries in the Web UI:
- **AVGO**: Correctly identified price and news headlines.
- **MSFT**: Correctly identified price ($401.14) and news headlines.

## Deployment to Vertex AI Agent Engine

I've created a deployment script to automate the process of moving this agent to a hosted environment.

### Deployment Script: `deploy_to_agent_engine.sh`
This script:
1.  **Loads Configuration**: Reads Project ID and Location from `.env`.
2.  **Handles GCS Bucket**: Automatically creates a staging bucket (`[project]-adk-staging`) if it doesn't already exist.
3.  **Regional Deployment**: Maps the `global` location to a valid Agent Engine region (defaulting to `us-central1` if needed).
4.  **Executes Deployment**: Runs `adk deploy agent_engine` with all necessary flags.

### Deployment Successful
The agent has been successfully deployed to Vertex AI Agent Engine.

**Deployment ID**: `projects/173481798756/locations/us-central1/reasoningEngines/8002372070790922240`

The script successfully:
1.  Created the `mullan-gmail-com-adk-staging` GCS bucket in `us-central1`.
2.  Staged the agent source code.
3.  Configured the Gemini 3 model and global endpoints.
4.  Uploaded and registered the agent with Vertex AI.

The agent is now live and hosted on Google Cloud!

## Next Steps

1. **Token Management**: In a production environment, the `ACCESS_TOKEN` should be refreshed dynamically using `gcloud auth print-identity-token`.
2. **Environment Variables**: Use the `.env` file for all project and location configurations.
