import os
import asyncio

# Set environment variables for Vertex AI (Gemini)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "mullan-gmail-com")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

from google.adk.agents.llm_agent import Agent
import google.genai

# Monkeypatch google.genai.Client to force Vertex AI usage
_original_client_init = google.genai.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs['vertexai'] = True
    kwargs['project'] = os.getenv("GOOGLE_CLOUD_PROJECT", PROJECT_ID)
    kwargs['location'] = os.getenv("GOOGLE_CLOUD_LOCATION", LOCATION)
    _original_client_init(self, *args, **kwargs)
google.genai.Client.__init__ = _patched_client_init

from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.genai import types

# ID token obtained from `gcloud auth print-identity-token`
ACCESS_TOKEN = os.getenv("MCP_ACCESS_TOKEN", "")

# Configuration for the remote MCP server
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://stock-mcp-xklq3ziy3q-uc.a.run.app/mcp")

# Setup MCP Toolset with Streamable HTTP connection and Bearer token authentication
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
    )
)

# Define the root agent
root_agent = Agent(
    model=f'projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}',
    name='stock_agent',
    description="An agent that provides real-time stock information and financial data.",
    instruction=(
        "You are a professional financial assistant. Your goal is to provide accurate stock information. "
        "Use the tools provided in the 'stock_tools' toolset to fetch real-time data for stocks. "
        "When a user asks about a stock price, volume, or other metrics, call the appropriate tool. "
        "Always provide clear and concise answers based on the tool results."
    ),
    tools=[mcp_toolset],
)

# To support `adk run`, we expose `root_agent` at the module level.

async def run_standalone():
    """Run the agent interactively in a standalone Python script."""
    app = App(name="stock_info_app", root_agent=root_agent)
    
    # Initialize necessary services for the Runner
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service,
    )
    
    # Create a session
    user_id = "default_user"
    session = await session_service.create_session(app_name=app.name, user_id=user_id)
    
    print("\nStock Agent is ready. Type 'exit' to quit.")
    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                break
            
            # Create content for the runner
            new_message = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Execute the agent and stream events
            found_response = False
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=new_message
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            if not found_response:
                                print("Agent: ", end="", flush=True)
                                found_response = True
                            print(part.text, end="", flush=True)
            
            if not found_response:
                print("Agent: (No response text)")
            else:
                print() # New line after response
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

    await runner.close()

if __name__ == "__main__":
    asyncio.run(run_standalone())
