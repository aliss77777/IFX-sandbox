import os
from freeplay import Freeplay
from freeplay_integration import FreeplayLLM, FreeplayRuntimeCallback, TraceContext
from tools import (
    PlayerSearchTool,
    GameSearchTool,
)

project_id = os.getenv("FREEPLAY_PROJECT_ID")
api_key = os.getenv("FREEPLAY_API_KEY")
available_tools = [
    GameSearchTool(),
    PlayerSearchTool(),
]

# Initialize Freeplay client
fp_client = Freeplay(
    api_key=api_key,
    project_id=project_id
)

# Initialize FreeplayLLM for prompt management
freeplay_llm = FreeplayLLM(
    freeplay_client=fp_client,
    project_id=project_id,
)

# Create session for tracking related prompt and agent interactions below
fp_session = fp_client.sessions.create(project_id)

# Optionally, create trace context for end-to-end agent tracing
trace_context = TraceContext()


# Freeplay integration - prompts now managed centrally
casual_fan_llm = freeplay_llm.create_llm("casual_fan_prompt", tools=available_tools)