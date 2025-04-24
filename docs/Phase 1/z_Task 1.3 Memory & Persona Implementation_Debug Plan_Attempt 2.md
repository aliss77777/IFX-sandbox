# Task 1.3 Memory & Persona Implementation - Debug Plan

This document tracks the step-by-step implementation and debugging process for Task 1.3, integrating Zep Memory and Persona selection into the 49ers FanAI Hub, following a revised plan based on codebase review and Zep documentation analysis.

**Important Design Intent:** The goal is to leverage Zep Cloud to load pre-defined knowledge graphs associated with specific user personas ("Casual Fan", "Super Fan") based on the user's selection in the UI. This pre-loaded knowledge will provide long-term context for the agent. However, the messages exchanged during a specific Gradio chat session are intended to be **ephemeral** regarding Zep's persistent storage. That is, user inputs and assistant responses **should NOT be added back** to the Zep user's memory graph or session history using `memory.add`. The Zep integration focuses *only* on retrieving relevant context from the pre-loaded persona graphs.

## Revised Implementation Steps (Updated Order)

1.  **Implement Zep User & Memory Setup Script (`z_utils/zep_setup.py`)**
    *   [X] Create `z_utils/zep_setup.py`.
    *   [X] Load `ZEP_API_KEY`, `ZEP_API_URL` (optional).
    *   [X] Initialize `AsyncZep` client.
    *   [X] Define `PERSONAS` dictionary.
    *   [X] Generate fixed UUIDs for each persona.
    *   [X] Save UUIDs to `z_utils/persona_uuids.json`.
    *   [X] Implement `async def create_zep_user(client, user_data)` (check existence first).
    *   [X] Define persona-specific knowledge (text/JSON suitable for `graph.add`).
    *   [X] Implement `async def preload_knowledge(client, user_id, persona_knowledge)` using `client.graph.add`. (Renamed from preload_memory)
    *   [X] Implement `async def main()` to orchestrate user creation, knowledge pre-loading, and UUID saving.
    *   [X] Add `if __name__ == "__main__": asyncio.run(main())`.
    *   **Status:** Completed

2.  **Refactor ID Management & AppState (`gradio_utils.py`, `gradio_app.py`)**
    *   [X] Modify `gradio_utils.py`: Remove global ID state, create generator functions.
        *   **Details:** Removed the global variables `_session_id` and `_user_id`. Removed the `reset_ids` function. Renamed existing internal functions to `generate_session_id()` and `generate_user_id()`, making them simple wrappers around `str(uuid.uuid4())` to provide unique IDs on demand without relying on global state.
    *   [X] Modify `gradio_app.py`:
        *   [X] Enhance `AppState` (add `current_persona`, `persona_data`, ensure `user_id`, `session_id` are instance vars).
            *   **Details:** Added `current_persona = DEFAULT_PERSONA` and `persona_data = None` as instance attributes to the `AppState` class `__init__` method. Confirmed `user_id` and `session_id` were already instance attributes (initialized to `None`). Added helper methods `_initialize_zep` (to create the `AsyncZep` client using environment variables `ZEP_API_KEY`/`ZEP_API_URL` with error handling) and `_load_persona_data` (to load the `z_utils/persona_uuids.json` file into the `self.persona_data` attribute with error handling for file not found or JSON parsing issues).
        *   [X] Load persona UUIDs from JSON into `AppState.persona_data`.
            *   **Details:** This is handled within the `_load_persona_data` method called by `initialize_chat`. It opens `z_utils/persona_uuids.json`, uses `json.load()` to parse it, and stores the resulting dictionary in `current_state.persona_data`.
        *   [X] Update `initialize_chat`: Set default persona, generate initial `user_id` (from loaded data) & `session_id`, store in `state`, create initial Zep session.
            *   **Details:** This async function is triggered by `demo.load`. It first calls `_initialize_zep` and `_load_persona_data`. It then sets `current_state.current_persona` to `DEFAULT_PERSONA`. It retrieves the corresponding `user_id` from `current_state.persona_data` and stores it in `current_state.user_id`. It calls `generate_session_id()` (from `gradio_utils`) and stores the result in `current_state.session_id`. Finally, if the Zep client is ready and a `user_id` was successfully loaded, it calls `await current_state.zep_client.memory.add_session(...)` using the generated `session_id` and loaded `user_id` to establish the initial session context in Zep Cloud. The original logic involving `zep.user.add` was removed as user creation is now handled by the separate `zep_setup.py` script.
        *   [X] Update `process_message`: Use `state.session_id`, `state.zep_client`.
            *   **Details:** Modified the `process_message` function (which handles the core agent interaction logic) to retrieve the Zep client (`current_state.zep_client`) and the current `session_id` (`current_state.session_id`) directly from the `AppState` object passed into it. This ensures it uses the correct context set by `initialize_chat` or `handle_persona_change`. **Crucially**, the calls to `await current_state.zep_client.memory.add(...)` for both user and assistant messages within this function were **commented out** to implement the design intent of keeping the Gradio chat ephemeral and *not* persistently storing conversation history back into the Zep memory for the selected persona.
        *   [X] Add `handle_persona_change` async function: Update `state` (`current_persona`, `user_id`), generate *new* `session_id`, store in `state`, create new Zep session, clear UI.
            *   **Details:** Created a new async function `handle_persona_change` designed to be triggered by the `persona_selector.change` event. It receives the selected `persona_name` and the `current_state`. It looks up the corresponding `new_user_id` from `current_state.persona_data`. It updates `current_state.current_persona` and `current_state.user_id`. It calls `generate_session_id()` to get a *new* session ID for the new persona context and stores it in `current_state.session_id`. If the Zep client is available, it calls `await current_state.zep_client.memory.add_session(...)` with the new `session_id` and `user_id`. It also clears internal caches used by tools (like `game_recap.last_game_data`) and returns `[]` to clear the Gradio chatbot UI.
        *   [X] Add Persona Selector UI (`gr.Radio`).
            *   **Details:** Added a `gr.Radio` component named `persona_selector` within the `create_ui` function. Configured with `choices=["Casual Fan", "Super Fan"]`, a label, the `DEFAULT_PERSONA` as the initial value, and `interactive=True`.
        *   [X] Wire UI events (`demo.load`, `persona_selector.change`, `msg.submit`, `clear_button`).
            *   **Details:** Configured the event listeners within `create_ui`:
                *   `demo.load` was wired to call `initialize_chat`, passing the initial `gr.State(state)` and updating the `chatbot` and `persona_selector` components (and later, `gr.State(state)` itself during debugging attempts).
                *   `persona_selector.change` was wired to call `handle_persona_change`, passing the `persona_selector` value and `gr.State(state)`, updating the `chatbot` component.
                *   `msg.submit` was initially wired using `.then()` chaining involving `user_input` and `process_and_respond`. During debugging, this was simplified to directly call `process_and_respond`, passing `msg`, `chatbot`, and `gr.State(state)` (later removed/re-added `gr.State` during debugging) as inputs, and updating `msg`, `chatbot`, and the dynamic info components.
                *   `clear_button.click` was wired to call `clear_chat`, passing `gr.State(state)` and updating various UI components including `persona_selector` back to default.
    *   **Status:** Completed

3.  **Integrate Zep Memory into Agent (`gradio_agent.py`)**
    *   [X] Replace `Neo4jChatMessageHistory` import with `ZepCloudChatMessageHistory`.
        *   **Details:** Changed the import statement from `from langchain_neo4j import Neo4jChatMessageHistory` to `from langchain_community.memory.zep_cloud_memory import ZepCloudChatMessageHistory`.
    *   [X] Update `get_memory` function to instantiate `ZepCloudChatMessageHistory` using `session_id` argument and Zep credentials from env vars. Add error handling for missing key / Zep init failure (fallback to basic history).
        *   **Details:** Rewritten the `get_memory(session_id)` function. It now retrieves `ZEP_API_KEY` and optionally `ZEP_API_URL` from environment variables. It includes a check: if `ZEP_API_KEY` is missing, it prints an error and returns a basic fallback `langchain.memory.ChatMessageHistory()`. Otherwise, it constructs the arguments dictionary (`session_id`, `api_key`, optional `url`) and instantiates `ZepCloudChatMessageHistory(**history_args)`. A `try...except` block was added around the instantiation to catch potential Zep client initialization errors, also falling back to `ChatMessageHistory` if an exception occurs. This ensures the agent receives a valid memory object, albeit potentially a non-persistent one if Zep connection fails.
    *   **Status:** Completed

4.  **Perform Housekeeping Tasks** (Already Completed)
    *   [X] Create `z_utils/neo4j_cleanup.py` script using `gradio_graph`.
    *   [X] Add Cypher query `MATCH (g:Game) WHERE g.embedding IS NOT NULL REMOVE g.embedding RETURN count(*)` to script.
    *   [X] Add execution logic and logging/print statements to `neo4j_cleanup.py`.
    *   [X] *Action:* Run `python ifx-sandbox/z_utils/neo4j_cleanup.py` (User needs to run this).
    *   [X] Delete `ifx-sandbox/tools/vector.py`.
    *   [X] Remove "Game Summary Search" tool (`get_game_summary`) import and definition from `tools` list in `gradio_agent.py`. (Verified Complete)
    *   **Status:** Completed (Pre-existing / Verified)

5.  **Update Documentation (`docs/requirements.md`)**
    *   [X] Update "Persona Memory Structure (Zep)" section with actual implementation details.
    *   [X] Mark Feature 0 (Persona Selection) as completed.
    *   [X] Update Task 1.3 Description/Status in Detailed Work Plan.
    *   **Status:** Completed

## Execution Log & Review Points

*   **2024-07-27:** Created debug plan file.
*   **2024-07-27:** Refactored `gradio_utils.py` to remove global state and use ID generator functions.
*   **2024-07-27:** Updated plan order: Step 2 (`zep_setup.py`) moved to first, Step 4 marked as completed.
*   **2024-07-27:** Implemented `zep_setup.py`, fixed import errors, fixed async context manager issue, fixed UUID loading/saving logic. Script executed successfully, creating users and preloading knowledge.
*   **2024-07-27:** Modified `gradio_app.py`: Enhanced `AppState`, added persona loading/handling, integrated UI selector, updated initialization/message processing, wired events.
*   **2024-07-27:** Clarified design intent: Zep context retrieval only; Gradio chat messages are ephemeral, not added back to Zep via `memory.add`.
*   **2024-07-27:** Modified `gradio_app.py` again: Commented out `zep_client.memory.add` calls in `process_message` to implement ephemeral chat regarding Zep persistence.
*   **2024-07-27:** Modified `gradio_agent.py`: Replaced Neo4j memory with `ZepCloudChatMessageHistory`, updated `get_memory` function with env var loading and error handling/fallback, ensured `session_id` is passed correctly to agent invocation.
*   **2024-07-27:** Verified Step 4 Housekeeping: Confirmed removal of vector tool import and definition in `gradio_agent.py`.
*   **2024-07-27:** Updated `docs/requirements.md` to reflect completed implementation details for Feature 0/Task 1.3 and marked as complete.

*(This section will be updated after each step)*

**Implementation Complete.**

---

## Debugging Log (Post-Implementation)

**2024-07-28:** Began testing the implementation.

*   **Issue 1: Startup Error - `Attempted to process message before state initialization.`**
    *   **Observation:** Error occurred immediately after `Application state initialized.` log during startup.
    *   **Root Cause:** The `initialize_chat` function completed its setup but failed to set the `state.initialized` flag to `True` before returning.
    *   **Fix 1:** Added `current_state.initialized = True` before the return statement in `initialize_chat`. -> *Failed to resolve fully.*

*   **Issue 2: Startup Error Persists / State Propagation Delay**
    *   **Observation:** After Fix 1, the same error occurred, originating from `process_and_respond` being called with an empty message immediately after initialization. Debug logs showed `process_and_respond` received a state object where `initialized`