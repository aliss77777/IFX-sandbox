## Context
You are an expert at  UI/UX design and software front-end development and architecture.  You are allowed to not know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.

When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.

# Task 1.3 Memory & Persona Implementation Instructions

## Objective
You are to follow the step-by-step process in order to implement Feature 0 (Persona Selection) / Task 1.3 (Memory System and UI Persona Integration with Zep) as defined in `ifx-sandbox/docs/requirements.md`. This involves creating Zep users/memory, adding UI selection in Gradio, integrating Zep memory into the agent, and performing related housekeeping. The goal is to allow users to select a persona ("Casual Fan" or "Super Fan") which loads pre-defined user profiles and memory contexts via Zep Cloud, personalizing the chat experience.

## Instruction Steps

1.  **Codebase Review:** Familiarize yourself with the existing project structure:
    *   `gradio_app.py`: Understand the current UI structure, the `AppState` class, and how Zep is already integrated. Pay close attention to `initialize_chat()` and `process_message()` functions which handle session creation and message processing.
    *   `gradio_agent.py`: Examine the agent setup, tool integration, and especially the `get_memory()` function which currently uses `Neo4jChatMessageHistory` instead of Zep memory.
    *   `gradio_utils.py`: Review for utility functions, especially those related to session/user ID generation.
    *   `tools/vector.py`: Examine this file as it needs to be removed in the housekeeping phase.
    *   `.env`: Check for `ZEP_API_KEY` to ensure Zep Cloud access is configured. Note that Zep Cloud API keys start with "z_" prefix.
    *   Read `requirements.txt` to verify Zep client libraries are available (specifically `zep-cloud>=0.1.0`).

2.  **Create Directory Structure:**
    *   **Note:** The directory `ifx-sandbox/z_utils/` already exists with other utility scripts like `set_secrets.py` and `restart_space.py`. Follow their patterns for loading environment variables and error handling.

3.  **Zep User & Memory Setup Script:**
    *   Create a new file: `ifx-sandbox/z_utils/zep_setup.py`.
    *   **Implement the script:**
        *   Import `asyncio`, `os`, `uuid`.
        *   Import `AsyncZep`, `User`, `Message` from `zep_cloud`.
        *   Load `ZEP_API_KEY` (and optionally `ZEP_API_URL`) from environment variables using `dotenv` like other scripts. Handle missing keys gracefully (e.g., raise error).
        *   Initialize `AsyncZep` client.
        *   **Define Persona Data:** Create dictionaries mapping persona names to details:
            ```python
            PERSONAS = {
                "Casual Fan": {
                    "user_id": str(uuid.uuid4()), # Generate and store fixed UUIDs
                    "email": "casual.fan@example.com",
                    "first_name": "Casual",
                    "last_name": "Fan",
                    "metadata": {"fan_type": "casual"}
                },
                "Super Fan": {
                    "user_id": str(uuid.uuid4()), # Generate and store fixed UUIDs
                    "email": "super.fan@example.com",
                    "first_name": "Super",
                    "last_name": "Fan",
                    "metadata": {"fan_type": "super"}
                }
            }
            ```
            *Print these generated UUIDs to the console when the script runs.*
            **IMPORTANT:** The UUIDs must be saved to a file (e.g., `z_utils/persona_uuids.json`) for later use by the application, as these will be used to link users to their persona data.
        *   **Define User Creation Function:** Create an `async def create_zep_user(client, user_data)` function that calls `client.user.add(**user_data)`. Include error handling (e.g., user already exists). Consider adding a `client.user.get(user_id)` check first.
        *   **Define Memory Pre-loading:**
            *   Define sample `Message` lists for each persona reflecting their interests:
                * **Casual Fan**: Focus on big stars (QB, star receivers), game outcomes, simple recaps with minimal stats, excitement for big plays.
                * **Super Fan**: Focus on detailed stats, role players, strategy discussion, defensive play analysis, references to historical context.
            *   Create an `async def preload_memory(client, user_id, memories)` function.
            *   **Implementation approach**: Using the Zep Cloud API, create a temporary session for the user with `await client.memory.add_session(session_id=str(uuid.uuid4()), user_id=user_id)`, then add the messages with `await client.memory.add(session_id=session_id, messages=memories)`.
        *   **Main Execution Block:** Create an `async def main()` function and use `asyncio.run(main())` in `if __name__ == "__main__":`.
            *   In `main()`, iterate through `PERSONAS`, call `create_zep_user` for each.
            *   Call memory pre-loading function for each persona.
            *   Save the persona UUIDs to a JSON file.
            *   Print confirmations or errors.
    *   **Run the Script:** Execute `python ifx-sandbox/z_utils/zep_setup.py` once to create the users in Zep Cloud. Note the generated UUIDs.

4.  **Modify Gradio UI & State Management:**
    *   Update `gradio_app.py` to:
        *   Add imports: Ensure `AsyncZep`, `Message` are imported. Add `uuid` and `json` for reading the persona UUIDs file.
        *   Enhance `AppState` class with persona-related fields:
            ```python
            def __init__(self):
                self.chat_history = []
                self.initialized = False
                self.user_id = None
                self.session_id = None
                self.zep_client = None
                self.current_persona = None  # New field to track selected persona
                self.persona_data = None  # New field to store persona details
            ```
        *   Load persona data from the saved JSON file at application start.
        *   Add a Persona Selector UI component (radio buttons) at the top of the UI, above the chat interface:
            ```python
            persona_selector = gr.Radio(
                choices=["Casual Fan", "Super Fan"],
                label="Select your 49ers Fan Type:",
                value="Casual Fan",  # Default selection
                interactive=True
            )
            ```
        *   Modify `initialize_chat()` to use persona-specific user IDs:
            * Use the UUID corresponding to the selected persona from the saved JSON file
            * Update the existing code that calls `zep.user.add` with the persona-specific data
        *   Implement a new `handle_persona_change(persona_name)` function for switching personas:
            * Update `state.current_persona` with the new persona
            * Set `state.user_id` to the corresponding UUID
            * Generate a new `session_id` using `gradio_utils.reset_ids()`
            * Create a new Zep session with `await zep.memory.add_session()`
            * Clear the chat history display to start fresh
        *   Register this function as a callback for the persona selector.
        *   Update `process_message()` to ensure the persona-specific context is used.

5.  **Integrate Zep Memory into Agent:**
    *   Modify `gradio_agent.py` to:
        *   Replace `Neo4jChatMessageHistory` import with:
            ```python
            from langchain_community.memory.zep_cloud_memory import ZepCloudChatMessageHistory
            ```
        *   Update the `get_memory()` function to return a Zep memory instance:
            ```python
            def get_memory(session_id):
                """Get the chat history from Zep for the given session"""
                return ZepCloudChatMessageHistory(
                    session_id=session_id,
                    api_key=os.environ.get("ZEP_API_KEY"),
                )
            ```
        *   Ensure all agent components correctly use the new memory interface (which should be 100% compatible with the existing code).

6.  **Perform Housekeeping Tasks:**
    *   **Create and Execute Neo4j Cleanup Script:**
        *   Create a new script, `ifx-sandbox/z_utils/neo4j_cleanup.py`.
        *   This script should connect to Neo4j using the existing `graph` object from `gradio_graph.py` (similar to the pattern in `ifx-sandbox/data/april_11_multimedia_data_collect/neo4j_article_uploader.py`).
        *   The script's sole purpose is to execute the following Cypher query to safely remove only the `embedding` property from `Game` nodes:
            ```cypher
            MATCH (g:Game)
            WHERE g.embedding IS NOT NULL
            REMOVE g.embedding
            RETURN count(*) as removed_count
            ```
        *   Ensure the script includes appropriate logging or print statements to confirm success (reporting the number of nodes affected) or indicate errors.
        *   Execute the script once using `python ifx-sandbox/z_utils/neo4j_cleanup.py`.
    *   **Delete Obsolete File:** Delete the `ifx-sandbox/tools/vector.py` file.
    *   **Remove Tool from Agent:** Remove the "Game Summary Search" tool and related imports from `ifx-sandbox/gradio_agent.py`:
        *   Remove the import statement: `from tools.vector import get_game_summary`
        *   Remove the tool entry from the `tools` list:
        ```python
        Tool.from_function(
            name="Game Summary Search",
            description="""ONLY use for detailed game summaries or specific match results if the 'Game Recap' tool fails or doesn't provide enough detail.
        Examples: "Summarize the 49ers vs Seahawks game", "Give me details about the last playoff game results"
        Do NOT use for general schedule questions.""",
            func=get_game_summary,
        ),
        ```

7.  **Test the Implementation:**
    *   Run the application and verify the persona selector is present.
    *   Test both personas with appropriate questions:
        * For Casual Fan: "Who's the quarterback for the 49ers?" (should give basic info)
        * For Super Fan: "Tell me about the 49ers offensive line strategy" (should give detailed analysis)
    *   Ensure switching personas correctly clears chat history and establishes a new session.
    *   Verify all existing functionality continues to work.

8.  **Update Documentation:**
    *   Edit `ifx-sandbox/docs/requirements.md` to reflect completed work:
        * Update the "Persona Memory Structure (Zep)" section with actual implementation details
        * Mark Feature 0 (Persona Selection) as completed

## Data Flow Architecture (Simplified)
1.  User selects a persona ("Casual Fan" or "Super Fan") in the Gradio UI.
2.  The UI triggers the persona change callback, which:
    *   Updates the application state with the selected persona.
    *   Sets the `user_id` to the corresponding pre-generated UUID from the persona JSON file.
    *   Generates a new `session_id` for this interaction.
    *   Creates a new Zep session linked to the persona's user ID.
    *   Clears the chat history to start fresh.
3.  User sends a message through the chat interface.
4.  The message is processed by `process_message()`, which:
    *   Stores the message in Zep memory for the current session.
    *   Calls the agent with the current `session_id`.
5.  The agent retrieves the chat history via `get_memory(session_id)`, which:
    *   Returns a Zep memory instance tied to the current session.
    *   This memory contains context appropriate to the selected persona.
6.  The agent generates a response influenced by the persona-specific memory context.
7.  The response is stored in Zep memory and displayed to the user.

## Error Handling Strategy
1.  **Zep API Connection:** Implement robust error handling for Zep API calls, including fallback options if Zep Cloud is unavailable:
    * For critical initialization calls, show a clear error message to the user
    * For non-critical calls during operation, log the error but continue with degraded functionality
    * Add retry logic for temporary network issues where appropriate
2.  **UUID Management:** Store persona UUIDs in a JSON file that can be loaded by the application. Add error handling for file access issues.
3.  **State Transitions:** Handle potential race conditions during persona switching:
    * Disable UI interaction during the transition
    * Re-enable only after all async operations are complete
    * Add a loading indicator during transitions
4.  **Session Management:** Properly clean up old sessions when switching personas.
5.  **Missing Dependencies:** Check for required environment variables at startup and show clear error messages if missing.

## Performance Optimization
1.  **Memory Context Size:** Keep pre-loaded memories concise and relevant to avoid excessive token usage.
2.  **Session Creation:** Only create a new Zep session when switching personas or when a session doesn't exist.
3.  **Lazy Loading:** Load persona details only when needed rather than all at application startup.
4.  **Caching:** Store the persona UUIDs in the AppState to avoid repeated file access.

## Failure Conditions
*   If you are unable to complete any step after 3 attempts, immediately halt the process and consult with the user on how to continue.
*   Document the failure point and the reason for failure.
*   Do not proceed with subsequent steps until the issue is resolved.

## Completion Criteria & Potential Concerns

**Success Criteria:**
1.  Users can select between "Casual Fan" and "Super Fan" personas in the UI.
2.  Switching personas correctly clears chat history and establishes a new session.
3.  The LangChain agent successfully retrieves and uses Zep memory for the current persona and session.
4.  Responses are contextually appropriate to the selected persona (more basic for casual fans, more detailed for super fans).
5.  Neo4j game nodes have been cleaned up by removing embedding properties.
6.  The vector search tool has been removed without breaking other functionality.

**Deliverables:**
*   The `z_utils/zep_setup.py` script for user creation and memory initialization.
*   The `z_utils/persona_uuids.json` file storing the generated UUIDs.
*   Modified `gradio_app.py` with persona selector UI and appropriate state management.
*   Modified `gradio_agent.py` with Zep memory integration replacing Neo4j chat history.
*   Updated `docs/requirements.md` reflecting completed implementation.

**Challenges / Potential Concerns & Mitigation Strategies:**

1.  **Zep Integration:**
    *   *Concern:* Ensuring correct usage of the Zep Cloud SDK, especially across async/sync contexts.
    *   *Mitigation:* Carefully review Zep documentation for best practices. Follow the `AsyncZep` usage pattern already in place in `gradio_app.py`. Ensure proper async/await handling in all Zep operations.

2.  **Gradio State Management:**
    *   *Concern:* Properly handling persona switching and session management to avoid race conditions or context contamination.
    *   *Mitigation:* Use clear state management in the UI callbacks. Ensure the persona selector is disabled during transitions. Add status indicators for long operations.

3.  **Regression Risks:**
    *   *Concern:* Changes to core files like `gradio_app.py` and `gradio_agent.py` could break existing functionality.
    *   *Mitigation:* Make incremental changes with thorough testing after each modification. Use version control to track changes. Follow the existing coding patterns. Present changes to core functions for review before implementing.

4.  **Neo4j Cleanup:**
    *   *Concern:* Removing embeddings from Game nodes could affect other components relying on this data.
    *   *Mitigation:* Verify all dependencies before removal. The `vector.py` file is the only component using these embeddings. Run the cleanup in a separate step and test afterwards.

5.  **Vector Tool Removal:**
    *   *Concern:* Removing the vector search tool might have unexpected dependencies.
    *   *Mitigation:* Check all imports and references. Verify the tool removal doesn't break any other functionality by testing all other tools after removal.

## Appendix: Zep Memory Pre-loading Implementation

Based on the Zep memory graph structure described in [Zep documentation](https://help.getzep.com/facts), here's a detailed implementation of how to pre-load memory graphs for the Casual Fan and Super Fan personas.

### Understanding Zep's Memory Model

In Zep, memory consists of:
1. **Facts** - Stored on edges, representing precise relationships with timestamps for when they are valid/invalid
2. **Summaries** - Stored on nodes, providing high-level overviews of entities

Our implementation will focus on:
1. Creating appropriate nodes (team concepts, games, general information)
2. Establishing facts via edges that connect these nodes
3. Adding fact ratings to prioritize important knowledge for each persona

### Implementation in `zep_setup.py`

# file: z_utils/zep_setup.py
"""
Create two persona users in Zep Cloud and preload their memory graphs.
Run once:  python z_utils/zep_setup.py
"""

```python
// Removed the full Python code block for zep_setup.py as it exists in the actual file
// See ifx-sandbox/z_utils/zep_setup.py for the implementation.
```

### Key Features of This Implementation

1. **Graph-Based Memory Structure**
   - Creates entity nodes for team information, games, and football concepts
   - Establishes facts through conversations and structured JSON data
   - Simulates natural knowledge through conversation-based memory

2. **Fact Rating System**
   - Implements custom fact rating instructions for each persona
   - Casual Fan: Prioritizes star players, major game outcomes, and memorable moments
   - Super Fan: Prioritizes detailed statistics, strategic insights, and historical context

3. **Knowledge Depth Differentiation**
   - **Casual Fan**: Limited to recent memorable games and basic team facts
   - **Super Fan**: Includes scheme knowledge, strategic insights, salary cap information, and draft capital

4. **Temporal Accuracy**
   - Facts include temporal information (game dates, current season)
   - Ensures agent responses are grounded in the correct time context

5. **User-Specific Conversation History**
   - Each persona has its own conversation history with appropriate depth
   - Casual conversations focus on stars and outcomes
   - Super fan conversations delve into schemes and personnel management

This implementation leverages Zep's memory graph to create distinctly different knowledge profiles that the agent can access based on the selected persona. Instead of storing detailed player information directly in the graph, it captures this knowledge through conversation samples, which is a more natural way that fans would recall information about their team.

---

## Implementation Summary & Notes (July 2024)

This task was completed following the steps outlined above, with some refinements and debugging along the way.

**Key Outcomes & Changes:**

1.  **`z_utils/zep_setup.py` Created & Refined:**
    *   Implemented using the script structure provided in the Appendix.
    *   Required several debugging iterations to correctly handle Zep SDK exceptions (`NotFoundError` from `zep_cloud.errors` for 404 checks, generic `Exception` for others with added type logging).
    *   Corrected the `zep.graph.add` call to pass profile data as a JSON string using `json.dumps()`, resolving a `BadRequestError` from the Zep API.
    *   Script successfully creates/updates users, preloads profile data to the graph, preloads sample chat messages to memory, and generates `z_utils/persona_uuids.json`.

2.  **`gradio_app.py` Modified:**
    *   Added imports for `json` and `uuid`.
    *   `AppState` class updated:
        *   Added `current_persona` and `persona_data` attributes.
        *   Integrated Zep client initialization (`_initialize_zep`) handling `ZEP_API_KEY` and optional `ZEP_API_URL`.
        *   Added logic (`_load_persona_data`) to load UUIDs from `persona_uuids.json` with error handling.
    *   `initialize_chat` refactored: Removed `zep.user.add`, sets default persona state (`current_persona`, `user_id`), generates a new `session_id`, and attempts to create the initial Zep session using the loaded `user_id`.
    *   `process_message` updated to use `state.zep_client` and `state.session_id` when interacting with Zep memory.
    *   Added `handle_persona_change` async function to update state (`current_persona`, `user_id`), generate a new `session_id`, create a new Zep session, and return an empty list to clear the Gradio chatbot UI.
    *   Added `gr.Radio` component (`persona_selector`) to the `create_ui` function.
    *   Wired UI events:
        *   `demo.load` calls `initialize_chat` (outputs: `chatbot`, `persona_selector`).
        *   `persona_selector.change` calls `handle_persona_change` (output: `chatbot`).
        *   Added an explicit `clear_button` wired to an updated `clear_chat` function which resets components and the persona selector.
        *   `msg.submit` calls `process_and_respond` which handles agent calls and component updates.

3.  **`gradio_agent.py` Modified:**
    *   Replaced `langchain_neo4j.Neo4jChatMessageHistory` import with `langchain_community.memory.zep_cloud_memory.ZepCloudChatMessageHistory`.
    *   Updated `get_memory` function to instantiate `ZepCloudChatMessageHistory`, passing `session_id` and retrieving Zep API key/URL from environment variables. Added basic error handling for missing API key.
    *   Removed the import `from tools.vector import get_game_summary`.
    *   Removed the "Game Summary Search" `Tool.from_function` definition from the `tools` list.

4.  **Housekeeping Performed:**
    *   Original plan to run manual Cypher query was updated.
    *   Created `z_utils/neo4j_cleanup.py` script using `gradio_graph` to connect to Neo4j.
    *   Executed `neo4j_cleanup.py` successfully, removing the `embedding` property from :Game nodes.
    *   Deleted the obsolete `ifx-sandbox/tools/vector.py` file.

5.  **Documentation Updated:**
    *   Updated `ifx-sandbox/docs/requirements.md` (Feature 0 description, Persona Memory Structure example) and marked Task 1.3 as complete.

**Current Status:** All implementation steps are complete. The application should now support persona selection integrated with Zep memory. Manual testing (Step 7) is required to verify functionality. 