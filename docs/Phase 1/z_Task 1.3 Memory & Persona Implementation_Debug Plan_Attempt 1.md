# AI Agent Testing Plan: Task 1.3 Memory & Persona Implementation

## Context
You are an expert at UI/UX design and software front-end development and architecture. You are allowed to not know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.
You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.
You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.
When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell the human user for review before going ahead. We want to avoid software regression as much as possible. 
WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD. 
When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale. 
If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.
If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.

## Objective
Your objective is to systematically test the implementation of Task 1.3 (Memory & Persona Implementation) as described in `ifx-sandbox/docs/Phase 1/Task 1.3 Memory & Persona Implementation.md`. This involves verifying the UI changes, persona switching logic, Zep memory integration, and ensuring no regressions were introduced. The user will perform the tests in the Gradio application and report the results.

## Instruction Steps

**Prerequisites:**
1.  The Gradio application (`ifx-sandbox/gradio_app.py`) should be running.
    *   **Resolution Status:** Completed (App is running in the background).
    *   **Actions Taken:** Resolved initial errors (file path, theme, NameError) and successfully launched the app using `python gradio_app.py`.

**Test 1: Verify Persona Selector UI**
1.  **Check UI:** Open the Gradio application URL in a browser.
2.  **Confirm Component:** Verify that the "Select your 49ers Fan Type:" radio button component is present, with "Casual Fan" and "Super Fan" options visible. Check that "Casual Fan" is selected by default.
    *   **Resolution Status:** Unresolved.
    *   **Actions Taken:**

**Test 2: Test "Casual Fan" Persona**
1.  **Ensure Persona:** Confirm "Casual Fan" is selected.
2.  **Ask Question:** Enter a question suitable for a casual fan, e.g., "Who's the quarterback for the 49ers?" or "Did the 49ers win their last game?".
3.  **Evaluate Response:** Check if the response is basic, focusing on high-level information or well-known players/outcomes, consistent with the persona's expected knowledge level (as defined in `zep_setup.py` preloading).
    *   **Resolution Status:** Unresolved.
    *   **Actions Taken:**

**Test 3: Test "Super Fan" Persona**
1.  **Switch Persona:** Select the "Super Fan" radio button.
2.  **Verify Chat Clear:** Confirm that the chat history displayed in the UI clears immediately after switching the persona. Check terminal logs for confirmation of a new Zep session being created.
3.  **Ask Question:** Enter a question suitable for a super fan, e.g., "Tell me about the 49ers offensive line strategy", "What were the key defensive plays in the last game?", or "Discuss the impact of the recent draft picks".
4.  **Evaluate Response:** Check if the response is more detailed, potentially including player specifics, strategic analysis, or historical context, consistent with the "Super Fan" persona's preloaded memory/profile.
    *   **Resolution Status:** Unresolved.
    *   **Actions Taken:**

**Test 4: Verify Persona Switching Robustness**
1.  **Switch Back:** Switch back to "Casual Fan". Confirm chat clears again.
2.  **Ask Casual Question Again:** Ask another simple question like "Who is the head coach?". Verify the response is appropriate for the Casual Fan persona.
3.  **Rapid Switching (Optional):** Try switching personas back and forth a few times quickly to check for any state management issues or errors (monitor terminal logs).
    *   **Resolution Status:** Unresolved.
    *   **Actions Taken:**

**Test 5: Verify Existing Functionality (Regression Test)**
1.  **Test Other Tools:** If possible, try interacting with the agent in ways that should trigger other tools (e.g., Player Search, Team Story, Game Recap if applicable).
2.  **Confirm Behavior:** Verify that these tools still function as expected and that their corresponding UI components (Player Card, Team Story, Game Recap HTML) display correctly when triggered. Ensure the removal of the "Game Summary Search" tool didn't negatively impact other operations.
    *   **Resolution Status:** Unresolved.
    *   **Actions Taken:**

## Failure Condition
If any test consistently fails after attempting minor fixes (if applicable and agreed upon), or if unexpected critical errors occur, halt the testing process and consult with the user on how to proceed with debugging.

## Completion 
The testing process is complete when all specified tests have been performed, the results have been documented in this file (updating 'Resolution Status' and 'Actions Taken'), and the user confirms the functionality meets the requirements outlined in Task 1.3.

## Challenges / Potential Concerns (from Task 1.3 Doc)

*   **Zep Integration:** Ensuring correct usage of the Zep Cloud SDK, especially across async/sync contexts and correct session handling based on `user_id` and `session_id`.
*   **Gradio State Management:** Properly handling persona switching and session management in `AppState` and UI callbacks (`handle_persona_change`) to avoid race conditions or context contamination. Verifying chat clearing works reliably.
*   **Context Differentiation:** Confirming that the agent's responses noticeably differ between personas based on the Zep memory context. This relies on both successful Zep integration *and* effective memory pre-loading via `zep_setup.py`.
*   **Regression Risks:** Changes to core files (`gradio_app.py`, `gradio_agent.py`) might have broken existing tool functionality or general chat behavior. Removal of the vector tool or Neo4j memory dependency could have unintended consequences.
*   **Data Dependency:** Test outcomes depend on the successful execution of `zep_setup.py` (creating users, preloading memory) and the availability of the `persona_uuids.json` file. 

## Appendix: Debugging Plan for "MemoryClient.get() got an unexpected keyword argument 'memory_type'" Error

This plan addresses the specific error encountered during testing: `MemoryClient.get() got an unexpected keyword argument 'memory_type'`

### Root Cause Analysis
The error indicates a mismatch between how the ZepCloudChatMessageHistory is being initialized and what its API actually accepts. The error specifically points to the `memory_type` parameter being passed to a method that doesn't accept it.

### Step-by-Step Debugging Plan

#### Step 1: Fix memory initialization in `gradio_agent.py`
1. Modify the `get_memory()` function to properly initialize ZepCloudChatMessageHistory
2. Remove any incompatible parameters (specifically `memory_type`)
3. Add error handling with appropriate fallbacks

#### Step 2: Test simplified agent without RunnableWithMessageHistory
1. Create a simplified agent using basic memory components
2. Test basic chat functionality to isolate memory issues from agent issues

#### Step 3: Update persona handling in `gradio_app.py`
1. Ensure persona switching correctly initializes new Zep sessions
2. Verify user_id and session_id are properly passed between components

#### Step 4: Check message format compatibility
1. Ensure messages sent to Zep API have the correct schema
2. Fix any format inconsistencies in how messages are stored and retrieved

#### Step 5: Test the complete integration
1. Test Casual Fan persona functionality
2. Test Super Fan persona functionality
3. Test persona switching
4. Verify persistence of chat history within sessions

### Version Compatibility Check
- Confirm that installed package versions are compatible
- Review any recent changes to the Zep Cloud SDK or LangChain that might affect integration

### Fallback Options
If Zep Cloud integration continues to be problematic:
1. Temporary fallback to in-memory ChatMessageHistory
2. Implement a simpler Redis-based memory solution 

## Key Learning: Zep Memory Retrieval Architecture

### Critical Discovery: Session ID vs User ID for Memory Retrieval

The most important discovery during debugging was understanding how Zep's memory architecture works:

1. **Memory Retrieval Uses Session ID, Not User ID:**
   - According to the Zep documentation, memory retrieval should be done using `session_id` rather than `user_id`
   - The `memory.get()` method specifically requires a `session_id` parameter
   - While each user can have multiple sessions, memory is accessed at the session level
   - The documentation states: "Note that although `memory.get()` only requires a session ID, it is able to return memory derived from any session of that user. The session is just used to determine what's relevant."

2. **Memory Persistence for Personas:**
   - To maintain persistent memory for different personas, we need to:
     - Create fixed, persistent session IDs for each persona
     - Store these session IDs alongside user IDs in our configuration
     - Use the specific session ID when retrieving memory with `memory.get()`
     - This ensures each persona maintains its distinct conversation history

3. **Parameter Mismatch with LangChain:**
   - The `ZepCloudChatMessageHistory` implementation in LangChain was passing parameters to Zep that aren't supported:
     - `memory_type` parameter was included in the LangChain wrapper but not accepted by the Zep client
     - Official Zep SDK examples show no such parameter for `memory.get()`
     - The current error occurs when `memory.messages` is accessed, which internally calls `_get_memory()`, which calls `self.zep_client.memory.get()`
   - The solution is to remove unsupported parameters from the LangChain initialization

4. **Proper Implementation for Our App:**
   - We need to modify our implementation to align with Zep's design:
     - Generate and store fixed session IDs for our personas
     - Use these IDs in `get_memory()` without any additional problematic parameters
     - Access chat history by retrieving from the specific session associated with each persona

This understanding fundamentally changes our approach to implementing the persona memory system.

## TO-DO: Zep Memory & Fan Profile Integration Plan

### 1. Update `zep_setup.py` to Associate Fan Profiles with Session IDs

```python
# file: z_utils/zep_setup.py
"""
Create two persona users in Zep Cloud and preload their memory graphs.
Run once:  python z_utils/zep_setup.py
"""

import asyncio, os, uuid, json
from datetime import datetime, timezone
from dotenv import load_dotenv
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message
from zep_cloud.errors import NotFoundError

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("ZEP_API_KEY")
BASE_URL = os.getenv("ZEP_API_URL")  # optional for self-hosted

if not API_KEY:
    raise RuntimeError("ZEP_API_KEY missing in environment variables.")

# Initialize AsyncZep client, handling optional base_url
zep_client_args = {"api_key": API_KEY}
if BASE_URL:
    zep_client_args["base_url"] = BASE_URL
zep = AsyncZep(**zep_client_args)

# -------- persona blue-prints -------------------------------------------------
PERSONAS = {
    "Casual Fan": {
        "user_id": uuid.uuid4().hex,
        "session_id": uuid.uuid4().hex,  # Add persistent session_id for this persona
        "email": "casual.fan@example.com",
        "first_name": "Casual",
        "last_name": "Fan",
        "metadata": {"fan_type": "casual"},
        "profile": {
            "entity_type": "fan_profile",
            "fan_type": "casual",
            "motivations": ["feel included", "see spectacular plays"],
            "behaviour_patterns": ["checks scores Monday", "shares memes"],
            "knowledge_depth": "surface",
            "favorite_team": "49ers",
        },
        "sample_chat": [
            ("user",  "Who's the quarterback for the 49ers?"),
            ("assistant", "It's Brock Purdy, the breakout star of 2023."),
            ("user",  "Did we win last night?"),
            ("assistant", "Yes! The Niners beat Seattle 31-17."),
        ],
    },
    "Super Fan": {
        "user_id": uuid.uuid4().hex,
        "session_id": uuid.uuid4().hex,  # Add persistent session_id for this persona
        "email": "super.fan@example.com",
        "first_name": "Super",
        "last_name": "Fan",
        "metadata": {"fan_type": "super"},
        "profile": {
            "entity_type": "fan_profile",
            "fan_type": "super",
            "motivations": ["understand strategy", "debate roster moves"],
            "behaviour_patterns": ["reads All-22", "posts long analyses"],
            "knowledge_depth": "detailed",
            "favorite_team": "49ers",
        },
        "sample_chat": [
            ("user",  "Break down our outside-zone success rate vs top-10 fronts."),
            ("assistant", "49ers average 5.6 YPC on outside-zone against top-10 run Ds..."),
            ("user",  "Any cap room left after Aiyuk's extension?"),
            ("assistant", "Roughly $1.2 M pre-June-1; expect a McCaffrey restructure."),
        ],
    },
}

# -------- helper --------------------------------------------------------------
async def create_user_if_needed(p):
    """Creates a Zep user if they don't already exist."""
    user_id = p["user_id"]
    try:
        await zep.user.get(user_id=user_id)
        print(f"User '{user_id}' already exists. Skipping creation.")
    except NotFoundError:
        # User not found, safe to create
        try:
            await zep.user.add(
                user_id=user_id,
                email=p["email"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                metadata=p["metadata"],
            )
            print(f"Successfully created user '{user_id}'.")
        except Exception as add_ex:
            print(f"Error creating user '{user_id}'. Type: {type(add_ex).__name__}, Details: {add_ex}")
    except Exception as ex:
        print(f"Error checking user '{user_id}'. Type: {type(ex).__name__}, Details: {ex}")


async def preload(p):
    """Preloads user profile graph data and sample chat memory."""
    user_id = p["user_id"]
    # Use the persistent session_id for this persona
    session_id = p["session_id"]
    
    print(f"Preloading data for user '{user_id}' with session '{session_id}'...")

    # Preload fan profile using Zep Graph API
    try:
        await zep.graph.add(
            user_id=user_id,
            type="json",
            data=json.dumps(p["profile"]),
        )
        print(f" - Added profile graph data for user '{user_id}'.")
    except Exception as graph_ex:
        print(f" - Error adding profile graph data for user '{user_id}'. Type: {type(graph_ex).__name__}, Details: {graph_ex}")

    # Create a persistent session specifically for this persona
    try:
        await zep.memory.add_session(session_id=session_id, user_id=user_id)
        print(f" - Created persistent session '{session_id}' for user '{user_id}'.")

        msgs = [
            Message(role=role, content=text, role_type=role) # Assuming role maps directly to role_type
            for role, text in p["sample_chat"]
        ]
        await zep.memory.add(session_id=session_id, messages=msgs)
        print(f" - Added {len(msgs)} sample messages to session '{session_id}'.")
    except Exception as mem_ex:
        print(f" - Error preloading memory for user '{user_id}' (session '{session_id}'). Type: {type(mem_ex).__name__}, Details: {mem_ex}")


# -------- main ----------------------------------------------------------------
async def main():
    """Main function to create users, preload data, and save UUIDs."""
    print("Starting Zep setup process...")
    for name, persona in PERSONAS.items():
        print(f"\nProcessing Persona: {name}")
        await create_user_if_needed(persona)
        await preload(persona)

    # Persist generated UUIDs and session IDs for the Gradio app
    output_dir = "ifx-sandbox/z_utils"
    output_file = os.path.join(output_dir, "persona_uuids.json")
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, "w") as f:
            # Include both user_id and session_id in the JSON file
            json.dump({k: {"user_id": v["user_id"], "session_id": v["session_id"]} for k, v in PERSONAS.items()}, f, indent=2)
        print(f"\nSuccessfully saved persona data to {output_file}")
    except IOError as e:
        print(f"\nError saving persona data to {output_file}: {e}")
    except Exception as ex:
        print(f"\nUnexpected error saving persona data: {ex}")


    print("\n--- Generated Persona Data ---")
    for name, p in PERSONAS.items():
        print(f"{name}: user_id={p['user_id']}, session_id={p['session_id']}")
    print("-----------------------------")
    print("Zep setup process complete.")

if __name__ == "__main__":
    # Ensure the script is run from the workspace root or adjust paths accordingly
    # Basic check: Does 'ifx-sandbox' exist in the current directory?
    if not os.path.isdir("ifx-sandbox"):
         print("Warning: This script assumes it's run from the workspace root directory")
         print("containing 'ifx-sandbox'. If running from elsewhere, paths might be incorrect.")

    asyncio.run(main())
```

### 2. TO-DO: Update `gradio_app.py` to Handle New Session IDs 

```python
# Update AppState to load both user_id and session_id
def _load_persona_data(self):
    """Load persona UUID mappings from file."""
    persona_file = os.path.join(os.path.dirname(__file__), 'z_utils', 'persona_uuids.json')
    try:
        with open(persona_file, 'r') as f:
            self.persona_data = json.load(f)
        print(f"Loaded persona UUIDs: {self.persona_data}")
    except Exception as e:
        print(f"Error loading persona data: {e}")
        self.persona_data = {
            "Casual Fan": {"user_id": uuid.uuid4().hex, "session_id": uuid.uuid4().hex},
            "Super Fan": {"user_id": uuid.uuid4().hex, "session_id": uuid.uuid4().hex}
        }
        print(f"Using fallback persona data: {self.persona_data}")
```

```python
# Update handle_persona_change to use the saved session_id instead of creating a new one
async def handle_persona_change(persona_name, state: AppState):
    """Handle persona switch: update state and create new Zep session."""
    try:
        print(f"Handling persona change to: {persona_name}")
        state.current_persona = persona_name
        
        # Use the user_id associated with this persona
        if state.persona_data and persona_name in state.persona_data:
            persona_info = state.persona_data[persona_name]
            state.user_id = persona_info["user_id"]
            state.session_id = persona_info["session_id"]  # Use the persistent session_id
            
            print(f"Using persistent session for persona '{persona_name}'. User ID: {state.user_id}, Session ID: {state.session_id}")
        else:
            # Fallback if persona data not available
            state.user_id = str(uuid.uuid4())
            state.session_id = str(uuid.uuid4())
            print(f"Creating new user/session IDs. User ID: {state.user_id}, Session ID: {state.session_id}")
        
        return []  # Return empty list to clear chatbot
    except Exception as e:
        print(f"Error in handle_persona_change: {e}")
        return []
```

### 3. TO-DO: Fix `gradio_agent.py` ZepCloudChatMessageHistory Implementation

```python
# Update imports to use the correct path for ZepCloudChatMessageHistory
from langchain_community.chat_message_histories.zep_cloud import ZepCloudChatMessageHistory

def get_memory(session_id):
    """Get memory for a specific session, or create a new one if it doesn't exist"""
    # First check if ZEP API key is available
    zep_api_key = os.environ.get("ZEP_API_KEY")
    
    if zep_api_key:
        try:
            # Use Zep Cloud for memory storage with only required parameters
            message_history = ZepCloudChatMessageHistory(
                session_id=session_id,
                api_key=zep_api_key
            )
            print(f"Using ZepCloudChatMessageHistory for session {session_id}")
            return message_history
        except Exception as e:
            print(f"Error initializing ZepCloudChatMessageHistory: {e}")
            print("Falling back to in-memory ChatMessageHistory")
    else:
        print("ZEP_API_KEY not found in environment variables")
        print("Falling back to in-memory ChatMessageHistory")
    
    # Fallback to in-memory chat history
    from langchain_community.chat_message_histories import ChatMessageHistory
    return ChatMessageHistory()
```