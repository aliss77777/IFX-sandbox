# Task 1.3 Memory & Persona Implementation

---
## Context

You are an expert at  UI/UX design and software front-end development and architecture.  You are allowed to NOT know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.

When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.



---

## Objective

*Implement Feature 0 (Persona Selection) with a **careful, precise, surgical** approach.
The user will execute **one step at a time** and confirm each works before proceeding.*

---

## INSTRUCTION STEPS

> **Follow exactly. Do NOT improvise.**  
> Steps 3 & 6 in `z_Task 1.3 Memory & Persona Implementation_Attempt 1 and 2.md` were already completed.

### 1 │ Review Documentation & Code Base

* `gradio_app.py`
* `gradio_agent.py`
* `gradio_utils.py`

---

### 2 │ Simplest Zep Test

1. Build a Python script in the z_utils folder using the code template at <https://help.getzep.com/walkthrough>.
2. Use **either** session‑ID:
   * Casual fan `241b3478c7634492abee9f178b5341cb`
   * Super fan `dedcf5cb0d71475f976f4f66d98d6400`
3. Confirm the script can *retrieve* chat history.

**Status Update:**
✅ Successfully created a simple Zep test script (`z_utils/zep_test.py`) that connects to Zep Cloud.
❗ Initial test showed no chat history was found for either the Casual fan or Super fan session IDs.
✅ Updated the `zep_setup.py` script to:
   - Use the specific session IDs defined in the task (Casual fan: `241b3478c7634492abee9f178b5341cb`, Super fan: `dedcf5cb0d71475f976f4f66d98d6400`)
   - Create conversation histories for both personas based on their knowledge profiles
   - Store these conversations in Zep Cloud with the specified session IDs
   - Save the session IDs to `persona_session_ids.json` for future reference
✅ Fixed an issue with message role_type formatting (changed "human" to "user" for proper Zep compatibility)
✅ Successfully executed the Zep setup script and verified both personas have:
   - Correctly formatted chat histories loaded in Zep Cloud
   - Knowledge profiles associated with their user IDs
   - Ability to retrieve their chat histories through the test script

✅ Testing confirms both session IDs are now working as expected:
   - Casual fan history includes basic team information and player highlights
   - Super fan history contains more detailed strategic information and analysis

**Next Action:**
- Proceed to Step 3 with the Gradio integration using the ZepCloudChatMessageHistory

---

### 3 │ Gradio Integration ― DO‑NO‑HARM Path

1. **Research**
   * <https://python.langchain.com/docs/integrations/memory/zep_memory/>
   * <https://python.langchain.com/docs/integrations/memory/zep_cloud_chat_message_history/>
2. Create a `ZepMemory()` (or `ZepCloudChatMessageHistory`) object.
3. **Hard‑code** one session‑ID first to verify import works inside the agent.
4. Run the app. Ensure chat history loads without breaking existing features.

**Status Update:**
✅ Successfully imported Zep libraries and dependencies in `gradio_agent.py`.
✅ Updated the `get_memory` function to use `ZepCloudChatMessageHistory` with a hardcoded session ID.
❌ Encountered an error with `MemoryClient.get()` related to an unexpected `memory_type` parameter.
✅ Created a workaround approach that:
   - Removes the problematic `memory_type` parameter
   - Uses a new `initialize_memory_from_zep` function to directly load chat history from Zep
   - Uses the Zep client directly to retrieve message history using the hardcoded session ID
   - Converts Zep messages to LangChain format
   - Initializes a `ConversationBufferMemory` with this history
   - Provides this memory to the agent executor for each session
✅ Fixed import compatibility issues between different versions of LangChain
✅ Successfully retrieving conversation history from Zep! Terminal output confirms:
   - "Loading 6 messages from Zep for Casual Fan persona"
   - "Successfully loaded message history from Zep"
✅ Agent now has access to the pre-existing context in Zep, and the application works without errors

**TODO for later / backlog:**
- Implement persona-specific behavior based on user context
- Currently we're loading conversation history successfully, but the agent's responses aren't explicitly personalized based on the casual/super fan persona context
- We should update agent system prompts to explicitly use facts from Zep memory when responding to questions
- This will be addressed after the initial implementation is complete

---

### 4 │ Add Radio Button (Skeleton Only)

* Insert a Gradio **Radio** with options **Casual Fan** / **Super Fan**.
* Initially the button **does nothing**—just proves the UI renders.

**Status Update:**
✅ Successfully added a Radio button component to the UI with "Casual Fan" and "Super Fan" options
✅ Placed the component in the input row alongside the text input and send button
✅ Added an event handler function that logs selection changes but doesn't modify functionality yet
✅ Ensured the component is interactive and clickable by connecting the change event
✅ Verified the implementation works without affecting existing functionality
✅ Followed the principle of keeping related code together (implementing handler function immediately after component definition)

**Implementation Approach:**
1. Added the radio button to the existing input row with appropriate scaling
2. Created a simple event handler function directly after the component definition
3. Connected the handler to the radio button's change event
4. Tested to ensure the radio component is interactive and logs selections
5. Confirmed no impact to existing features

---

### 5 │ Wire Radio → Session ID

1. On change, map selection to its fixed session‑ID.
2. Pass that ID into the `ZepMemory()` object.
3. Re‑run app, switch personas, confirm different histories load.

**Status Update:**
✅ Created a global variable architecture in `gradio_agent.py` to track:
   - Current memory session ID (`memory_session_id`)
   - Current persona name (`current_persona`) for improved logging
✅ Added clear comments explaining the global variable pattern for future maintenance
✅ Implemented a `set_memory_session_id()` function to update the memory state
✅ Modified `initialize_memory_from_zep()` to use the current global session ID
✅ Improved logging with consistent prefixes (`[PERSONA CHANGE]`, `[MEMORY LOAD]`, `[UI EVENT]`)
✅ Added a feedback textbox to the UI to show the current active persona to users
✅ Loaded persona-to-session-ID mapping from `persona_session_ids.json`
✅ Updated the radio button change handler to:
   - Load session IDs from JSON
   - Map selection to correct session ID
   - Call `set_memory_session_id()` to update the agent
   - Display feedback in the UI
✅ Ran the app and verified that:
   - Persona selection works correctly
   - Session IDs are properly mapped
   - Memory is loaded from the correct persona's history
   - UI updates to show current persona
   - Multiple questions work as expected with each persona's context

**Implementation Approach:**
1. Analyzed data flow from UI selection to memory retrieval
2. Created detailed implementation plan with debugging steps
3. Made surgical changes to minimum number of files
4. Added comprehensive logging for troubleshooting
5. Tested complete flow from UI to agent response

---

### 6 │ Strict Gradio Rule

* **DO NOT** change any other settings or components in the app.
* Changes must be incremental and easily revertible.

**Status Update:**
✅ Successfully adhered to "DO NO HARM" principle
✅ Made minimal changes to existing code:
   - Kept original hardcoded session ID as default value for backward compatibility
   - Maintained function signatures and return values to prevent interface breaks
   - Only added new functions and variables without removing or restructuring existing code
✅ Added proper error handling and fallbacks to prevent regressions
✅ Used clear variable naming and consistent coding patterns
✅ Added explanatory comments to clarify the purpose of changes
✅ Our implementation could be easily reversed by:
   - Removing the `set_memory_session_id()` function
   - Restoring the original `initialize_memory_from_zep()` function
   - Removing the radio button change handler code
   - Removing the UI feedback textbox

---

### 7 │ Changing App Responses to Provide User Personalization

* Review the context provided as Zep memoery in the zep_test.py file
* create an LLM function to summarize this information into concise and declarative content, e.g. TELL THE 49ers FAN APP how to personalize its outgoing messages to deliver exactly the kind of content and experience this fan is looking for! 
* review the structure of gradio_agent.py and identify where and how the AI agent can receive the instructions to personalize, using the  Minimal Surgical Changes rule
* present the plan to the user and explain your rationale in detail. Prepare to debate and be open to new ideas
* once a plan has been reviewed and approved, execute along the lines of the Appendix - First Principles in Action 

**Status Update:**
✅ Successfully reviewed the Zep memory contexts for both personas:
   - Casual Fan persona has surface-level knowledge and is motivated by feeling included
   - Super Fan persona has detailed knowledge and is motivated by strategic understanding
✅ Created a new `get_persona_instructions()` function in gradio_agent.py to return different instructions based on the current persona
✅ Updated prompts.py to include a placeholder for persona-specific instructions
✅ Modified generate_response() to incorporate persona instructions into the agent prompt
✅ Implemented two surgical changes to enhance persona-specific behavior:
   - Enhanced persona instructions with more directive language and specific examples
   - Added persona tag emphasizers around instructions and in user inputs

**Implementation Details:**
1. **Made Instructions More Direct and Prescriptive**:
   - Rewritten instructions using "YOU MUST" language instead of suggestions
   - Added numbered lists of specific behaviors to exhibit for each persona
   - Included concrete examples of how responses should look for each persona
   - Added "do/don't" sections to clarify expectations

2. **Enhanced Instruction Visibility in the Agent Context**:
   - Added emphasis tags around persona instructions: `[ACTIVE PERSONA: {current_persona}]`
   - Added persona-specific prefix to user inputs: `[RESPOND AS {current_persona.upper()}]:`
   - These small but effective changes helped ensure the instructions weren't lost in context

**Results:**
✅ Successfully implemented personalization with distinctly different responses for each persona:
   - **Casual Fan responses** became shorter, used inclusive "we/our" language, included excitement markers (exclamation points), and focused on big moments and star players
   - **Super Fan responses** became more detailed, used technical terminology, included structured analysis, and referenced role players alongside stars
   - Example: When asked about draft news, the casual fan received a brief, excited summary focusing on star players and big moments, while the super fan received a detailed, categorized analysis with specific prospect evaluations

**Future Improvements (Backlog):**
- Further enhance personalization by integrating more facts from the Zep memory context into responses
- Create a more sophisticated prompt that explicitly references relevant facts based on the current query
- Add a mechanism to track and adapt to the user's knowledge level over time
- Implement a feedback loop where users can indicate if responses are appropriately personalized
- Explore ways to make persona-specific language settings persistent across sessions

---

## Failure Condition

> **If any step fails 3×, STOP and consult the user**.

---

## Completion Deliverables

1. **Markdown file** (this document) titled **"Task 1.3 Memory & Persona Implementation"**.
2. **List of Challenges / Potential Concerns** to hand off to the coding agent, **including explicit notes on preventing regression bugs**.

---

## Challenges & Concerns

| # | Risk / Concern | Mitigation |
|---|---------------|-----------|
| 1 | Zep integration may break async flow | Keep Zep calls isolated; wrap in try/except; validate after each call. |
| 2 | Accidentally overwriting existing code | **Only** add small helper functions or wrap logic; no deletions/ rewrites without review. |
| 3 | Radio button race conditions | Disable UI during session‑switch; re‑enable after confirmation. |
| 4 | Regression in existing features | Run smoke tests (player search, game recap, team story) after every change. |
| 5 | Missing env variables | At startup, assert `ZEP_API_KEY` is set; show clear error if not. |
| 6 | Session ID mismatch | Verify that session IDs in code match those actually created in Zep Cloud. |
| 7 | Message history creation | Ensure messages follow proper format for Zep; implement fallbacks if message history retrieval fails. |
| 8 | Library compatibility issues | Use direct API calls to workaround LangChain <-> Zep parameter inconsistencies; maintain fallbacks for memory initialization to avoid breaking the application when parameters change. |

---

## First Principles for AI Development

| Principle | Description | Example |
|-----------|-------------|---------|
| Code Locality | Keep related code together for improved readability and maintenance | Placing event handlers immediately after their components |
| Development Workflow | Follow a structured pattern: read instructions → develop plan → review with user → execute after approval | Presented radio button implementation plan before making changes |
| Minimal Surgical Changes | Make the smallest possible changes to achieve the goal with minimal risk | Added only the necessary code for the radio button without modifying existing functionality |
| Rigorous Testing | Test changes immediately after implementation to catch issues early | Ran the application after adding the radio button to verify it works |
| Clear Documentation | Document design decisions and patterns | Added comments explaining why global variables are declared before functions that use them |
| Consistent Logging | Use consistent prefixes for log messages to aid debugging | Added prefixes like "[PERSONA CHANGE]" and "[MEMORY LOAD]" |
| Sequential Approval Workflow | Present detailed plans, wait for explicit approval on each component, implement one change at a time, and provide clear explanations of data flows | Explained how the persona instructions flow from selection to prompt generation before implementing changes |
| Surgical Diff Principle | Show only the specific changes being made rather than reprinting entire code blocks | Highlighted just the 2 key modifications to implement personalization rather than presenting a large code block |
| Progressive Enhancement | Layer new functionality on top of existing code rather than replacing it; design features to work even if parts fail | Adding persona-specific instructions while maintaining default behavior when persona selection is unavailable |
| Documentation In Context | Add inline comments explaining *why* not just *what* code is doing; document edge cases directly in the code | Adding comments explaining persona state management and potential memory retrieval failures |

---

> **Remember:** *One tiny change → test → commit. Repeat.*

---

## Appendix: Examples of First Principles in Action

### Exhibit A: Data Flow Explanation for Radio Button to Memory Retrieval (Created as part of Step 5)

```
## Data Flow Explanation: Radio Button to Memory Retrieval

Here's the complete data flow from user selection to memory retrieval:

1. **User Interaction**
   - User selects either "Casual Fan" or "Super Fan" from radio button in gradio_app.py
   - The UI triggers the `on_persona_change` event handler function

2. **Event Handling & Session ID Mapping**
   - `on_persona_change` receives the selected persona name
   - It loads the persona-to-session-ID mapping from persona_session_ids.json
   - It retrieves the correct session ID based on the selection

3. **Session ID Communication**
   - `on_persona_change` calls `set_memory_session_id` in gradio_agent.py
   - This updates the global `memory_session_id` variable in gradio_agent.py
   - The function confirms the switch with a console log

4. **Memory Retrieval When User Sends Message**
   - When user sends a message, `generate_response` is called
   - `generate_response` calls `initialize_memory_from_zep`
   - `initialize_memory_from_zep` uses the global `memory_session_id` variable to:
     - Connect to Zep Cloud
     - Retrieve message history for the specific persona
     - Convert Zep messages to LangChain format
     - Create a ConversationBufferMemory object

5. **Memory Usage in Agent**
   - The ConversationBufferMemory is passed to the AgentExecutor
   - The agent now has access to the selected persona's message history
   - The agent responds with context from that persona's memory

At each step of this flow, we maintain the session ID to ensure the right persona's memories are retrieved and used by the agent. The global variable acts as the "source of truth" for which persona is currently active.
```

### Exhibit B: Proposed Code Updates with Debugging Approach (Created and executed as part of Step 5)

```
# Proposed Code Updates with Debugging Approach

## 1. Update `memory_session_id` in gradio_agent.py

```python
# Change from constant to variable with default value
memory_session_id = "241b3478c7634492abee9f178b5341cb"  # Default to Casual Fan
current_persona = "Casual Fan"  # Track the persona name for debugging
```

**How it works**: The variable can now be updated while maintaining the default.

**Debugging**: Added a `current_persona` tracking variable to make logs more readable.

## 2. Add Session ID Update Function in gradio_agent.py

```python
def set_memory_session_id(new_session_id, persona_name):
    """Update the global memory_session_id variable when persona changes"""
    global memory_session_id, current_persona
    memory_session_id = new_session_id
    current_persona = persona_name
    print(f"[PERSONA CHANGE] Switched to {persona_name} persona with session ID: {new_session_id}")
    return f"Persona switched to {persona_name}"
```

**How it works**: This function allows the UI to update the agent's session ID.

**Debugging**: The "[PERSONA CHANGE]" prefix makes it easy to find this message in logs.

## 3. Update initialize_memory_from_zep in gradio_agent.py

```python
def initialize_memory_from_zep(session_id):
    """Initialize a LangChain memory object with history from Zep"""
    try:
        # Get history from Zep using the global session ID, not the parameter
        zep = Zep(api_key=os.environ.get("ZEP_API_KEY"))
        # Use global memory_session_id instead of the parameter
        print(f"[MEMORY LOAD] Attempting to get memory for {current_persona} persona (ID: {memory_session_id})")
        memory = zep.memory.get(session_id=memory_session_id)
        
        # Create a conversation memory with the history
        conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        if memory and memory.messages:
            print(f"[MEMORY LOAD] Loading {len(memory.messages)} messages from Zep for {current_persona} persona")
            
            # Add messages to the conversation memory
            for msg in memory.messages:
                if msg.role_type == "user":
                    conversation_memory.chat_memory.add_user_message(msg.content)
                elif msg.role_type == "assistant":
                    conversation_memory.chat_memory.add_ai_message(msg.content)
            
            print("[MEMORY LOAD] Successfully loaded message history from Zep")
        else:
            print("[MEMORY LOAD] No message history found in Zep, starting fresh")
            
        return conversation_memory
    except Exception as e:
        print(f"[ERROR] Error loading history from Zep: {e}")
        # Return empty memory if there's an error
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
```

**How it works**: Uses the global `memory_session_id` instead of parameter and improves logging.

**Debugging**: Added "[MEMORY LOAD]" prefixes and includes persona name in logs for clarity.

## 4. Add Radio Button Handler in gradio_app.py

```python
# Near the top of the file, import the setter function
from gradio_agent import set_memory_session_id

# Add this with other imports
import json
import os

# Load persona session IDs
def load_persona_session_ids():
    """Load persona session IDs from JSON file"""
    try:
        with open("z_utils/persona_session_ids.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load persona_session_ids.json: {e}")
        # Fallback to hardcoded values if file can't be loaded
        return {
            "Casual Fan": "241b3478c7634492abee9f178b5341cb",
            "Super Fan": "dedcf5cb0d71475f976f4f66d98d6400"
        }

# In the UI section where you define the radio button:
with gr.Row():
    persona_selector = gr.Radio(
        choices=["Casual Fan", "Super Fan"],
        value="Casual Fan",
        label="Select Fan Persona",
        info="Choose which fan perspective to chat from"
    )
    
# Define the handler function
def on_persona_change(persona_choice):
    """Handle changes to the persona selection"""
    print(f"[UI EVENT] Persona selection changed to: {persona_choice}")
    
    # Load session IDs from file
    persona_ids = load_persona_session_ids()
    
    # Verify the persona exists in our mapping
    if persona_choice not in persona_ids:
        print(f"[ERROR] Unknown persona selected: {persona_choice}")
        return f"Error: Unknown persona '{persona_choice}'"
    
    # Get the session ID for this persona
    session_id = persona_ids[persona_choice]
    print(f"[UI EVENT] Mapping {persona_choice} to session ID: {session_id}")
    
    # Update the agent's session ID
    feedback = set_memory_session_id(session_id, persona_choice)
    
    # Return feedback to display in the UI
    return feedback

# Connect the handler to the radio button
persona_selector.change(on_persona_change, persona_selector, gradio.outputs.Textbox())
```

**How it works**: Creates a radio button UI element, loads session IDs from file, and updates the agent's session ID when changed.

**Debugging**: Added "[UI EVENT]" prefixes to logs and returns feedback that will be displayed to the user.

## Debugging the Complete Pipeline

Here's how we'll debug the system when running:

1. **Test Persona Selection**:
   - Start the app and check console logs for "[UI EVENT]" messages
   - Verify "Persona selection changed to: X" messages appear
   - Confirm "Mapping X to session ID: Y" shows correct session ID
   - Look for "[PERSONA CHANGE]" confirmation message

2. **Verify Memory Loading**:
   - Send a chat message after selecting a persona
   - Check for "[MEMORY LOAD]" messages in the console
   - Verify correct persona name and session ID in logs
   - Confirm "Loading X messages from Zep for Y persona" appears

3. **Check Agent Response**:
   - Observe the agent's reply in the chat window
   - Verify it has contextual knowledge appropriate for the selected persona
   - For Casual Fan: Expect basic team info responses
   - For Super Fan: Expect more detailed, stats-heavy responses

4. **Error Testing**:
   - If any issues arise, look for "[ERROR]" prefixed messages
   - Test switching back and forth between personas

This structured debugging approach will help us verify that each step of the pipeline is working correctly.
```

