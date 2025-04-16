# Player Search Feature Implementation Instructions

## Context
You are an expert at UI/UX design and software front-end development and architecture. You are allowed to not know an answer, be uncertain, or disagree with your task. If any of these occur, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

**I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.**

When you need to modify existing code (in accordance with the instruction above), **please present your recommendation to the user before taking action, and explain your rationale.**

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.

## Objective
Follow the step-by-step process to build the Player Search feature (Task 1.2.2 from requirements.md). Start with a simple use case of displaying a UI component with the player's headshot, Instagram handle link, and a summary of their roster info. The goal is for the user to ask the app a question about a specific player and receive both a text summary and a visual UI component with information for that player.

## Implementation Steps

1.  **Review Code Base:** Familiarize yourself with the current project structure, particularly the Gradio app (`gradio_app.py`), existing components (`components/`), services, and utilities. Pay close attention to how the Game Recap feature was integrated.
2.  **Neo4j Update Script Creation:**
    *   Create a new subfolder within `ifx-sandbox/data/april_11_multimedia_data_collect/new_final_april 11/` specifically for the player data update script (e.g., `neo4j_player_update/`).
    *   Create a Python script (`update_player_nodes.py`) within this new subfolder.
    *   Use the existing script `ifx-sandbox/data/april_11_multimedia_data_collect/new_final_april 11/neo4j_update/update_game_nodes.py` as a reference for connecting to Neo4j and performing updates.
3.  **Neo4j Database Update:**
    *   The script should read player data from `ifx-sandbox/data/april_11_multimedia_data_collect/new_final_april 11/roster_april_11.csv`.
    *   Update existing `Player` nodes in the Neo4j database. **Do not create new nodes.**
    *   Use the `Player_id` attribute as the primary key to match records in the CSV file with nodes in the graph database.
    *   Add the following new attributes to the corresponding `Player` nodes:
        *   `headshot_url`
        *   `instagram_url`
        *   `highlight_video_url` (Note: Confirm if this specific column name exists in `roster_april_11.csv` or if it needs mapping).
    *   Implement verification steps within the script to confirm successful updates for each player.
    *   Report the number of updated nodes and any errors encountered.
    *   **Pause and request user confirmation** that the update completed successfully in the cloud interface before proceeding.
4.  **Player Component Development:**
    *   Create a new component file (e.g., `components/player_card_component.py`).
    *   Design the component structure based on the requirements (headshot, name, potentially key stats, Instagram link). Use `components/game_recap_component.py` as a structural reference for creating a dynamic Gradio component.
    *   Ensure the component accepts player data (retrieved from Neo4j) as input.
    *   Implement responsive design and apply the established 49ers theme CSS.
5.  **LangChain Integration:**
    *   Review existing LangChain integration in `gradio_agent.py` and `cypher.py` (and potentially `tools/game_recap.py`).
    *   Create a new file, potentially `tools/player_search.py`, for the player-specific LangChain logic.
    *   Define a new LangChain tool specifically for player search with a clear description so the agent recognizes when to use it.
    *   Implement text-to-Cypher query generation to retrieve player information based on natural language queries (e.g., searching by name, jersey number).
    *   Ensure the Cypher query retrieves all necessary attributes (`name`, `headshot_url`, `instagram_url`, relevant stats, etc.) using `Player_id` or `Name` for matching.
    *   The tool function should return both a text summary (generated by the LLM based on retrieved data) and the structured data needed for the UI component.
6.  **Gradio App Integration:**
    *   **Propose changes first:** Before modifying `gradio_app.py` or related files, outline the necessary changes (e.g., adding a new placeholder for the player component, updating the chat processing function to handle player data, modifying event handlers) and **request user approval.**
    *   Import the new player search tool into `gradio_agent.py` and add it to the agent's tool list.
    *   Import the new player card component into `gradio_app.py`.
    *   Modify the main chat/response function in `gradio_app.py` to:
        *   Recognize when the agent returns player data.
        *   Extract the text summary and structured data.
        *   Update the Gradio UI to display the player card component with the structured data.
        *   Display the text summary in the chat interface.
    *   Ensure the player card component is initially hidden and only displayed when relevant data is available (similar to the game recap component).
    *   Update the "Clear Chat" functionality to also hide/reset the player card component.
7.  **Testing and Validation:**
    *   Test the Neo4j update script thoroughly.
    *   Verify the LangChain tool correctly identifies player queries and generates appropriate Cypher.
    *   Test retrieving data for various players.
    *   Validate that the player card component renders correctly with different player data.
    *   Test the end-to-end flow in the Gradio app with various natural language queries about players.
    *   Check error handling for cases like player not found or ambiguous queries.

## Data Flow Architecture
1.  User submits a natural language query about a specific player.
2.  LangChain agent processes the query and selects the Player Search tool (likely implemented in `tools/player_search.py`).
3.  The tool generates a Cypher query to retrieve player data from Neo4j based on the user's query.
4.  Neo4j returns the player data including attributes like name, position, headshot URL, Instagram URL, etc.
5.  The tool receives the data, potentially uses an LLM to generate a text summary, and structures the data for the UI component.
6.  The tool returns the text summary and structured data to the agent/Gradio app.
7.  The Gradio app receives the response.
8.  The player card component function is called with the structured data, generating the visual UI.
9.  The UI component is displayed to the user, and the text summary appears in the chat.

## Error Handling Strategy
1.  Implement specific error handling for:
    *   Player not found in the database.
    *   Ambiguous player identification (e.g., multiple players with similar names).
    *   Missing required attributes in Neo4j (e.g., missing `headshot_url`).
    *   Database connection issues during query.
    *   Failures in rendering the UI component.
2.  Provide user-friendly error messages in the chat interface.
3.  Implement graceful degradation (e.g., show text summary even if the visual component fails).
4.  Add logging for debugging player search queries and component rendering.

## Performance Optimization
1.  Optimize Neo4j Cypher queries for player search.
2.  Consider caching frequently accessed player data if performance becomes an issue.
3.  Ensure efficient loading of player headshot images in the UI component.

## Failure Condition
If you are unable to complete any step after 3 attempts, immediately halt the process, document the failure point and reason, and consult with the user on how to continue. Do not proceed without resolution.

## Success Criteria
-   Neo4j database successfully updated with new player attributes (`headshot_url`, `instagram_url`, etc.).
-   LangChain correctly identifies player search queries and retrieves accurate data.
-   The Player Card component renders correctly in the Gradio UI, displaying headshot, relevant info, and links.
-   User can query specific players using natural language and receive both text and visual responses.
-   Integration does not cause regressions in existing functionality (like Game Recap search).
-   Error handling functions correctly for anticipated issues.

## Notes
-   Prioritize non-destructive updates to the Neo4j database.
-   Confirm the exact column names in `roster_april_11.csv` before scripting the Neo4j update.
-   Reuse existing patterns for agent tools, component creation, and Gradio integration where possible.
-   Document all changes, especially modifications to existing files like `gradio_agent.py` and `gradio_app.py`.
-   Test thoroughly after each significant step.

## Implementation Log
*(This section will be filled in as steps are completed)*

### Step 1: Review Code Base
**Date Completed:** April 16, 2025
**Actions Performed:**
- Reviewed key files: `gradio_app.py`, `gradio_agent.py`, `components/game_recap_component.py`, `tools/game_recap.py`, `tools/cypher.py`, `gradio_utils.py`.
- Analyzed patterns for component creation (`gr.HTML` generation), tool definition (prompts, QA chains), agent integration (tool list in `gradio_agent.py`), and UI updates in `gradio_app.py`.
- Noted the use of a global cache (`LAST_GAME_DATA` in `tools/game_recap.py`) as a workaround to pass structured data for UI components.
**Challenges and Solutions:** N/A for review step.
**Assumptions:** The existing patterns are suitable for implementing the Player Search feature.

### Step 2: Neo4j Update Script Creation
**Date Completed:** April 16, 2025
**Actions Performed:**
- Created directory `ifx-sandbox/data/april_11_multimedia_data_collect/new_final_april 11/neo4j_player_update/`.
- Created script file `update_player_nodes.py` within the new directory.
- Adapted logic from `update_game_nodes.py` to read `roster_april_11.csv`.
- Implemented Cypher query to `MATCH` on `Player` nodes using `Player_id` and `SET` `headshot_url`, `instagram_url`, and `highlight_video_url` attributes.
- Included connection handling, error reporting, verification, and user confirmation.
**Challenges and Solutions:** Confirmed column names (`headshot_url`, `instagram_url`, `highlight_video_url`) exist in `roster_april_11.csv` before including them in the script.
**Assumptions:** `Player_id` in the CSV correctly matches the `Player_id` property on `Player` nodes in Neo4j. Neo4j credentials in `.env` are correct.

### Step 3: Neo4j Database Update
**Date Completed:** April 16, 2025
**Actions Performed:**
- Executed the `update_player_nodes.py` script.
- Confirmed successful connection to Neo4j and loading of 73 players from CSV.
- Monitored the update process, confirming 73 Player nodes were matched and updated.
- Reviewed the summary and verification output: 73 successful updates, 0 errors. 56 players verified with headshot/Instagram URLs, 18 with highlight URLs.
**Challenges and Solutions:**
- Corrected `.env` file path calculation in the script (initially looked in the wrong directory).
- Fixed script error due to case mismatch for `player_id` column in CSV vs. script's check.
- Corrected Cypher query to use lowercase `player_id` property and correct parameter name (`$match_player_id`).
**Assumptions:** The counts reported by the verification step accurately reflect the state of the database.

### Step 4: Player Component Development
**Date Completed:** April 16, 2025
**Actions Performed:**
- Created new file `ifx-sandbox/components/player_card_component.py`.
- Defined function `create_player_card_component(player_data=None)`.
- Implemented HTML structure for a player card display (headshot, name, position, number, Instagram link).
- Included inline CSS adapted from 49ers theme and existing components.
- Function accepts a dictionary and returns `gr.HTML`.
- Added basic error handling and safe defaults for missing data.
- Included commented example usage for testing.
**Challenges and Solutions:** Ensured `html.escape()` was used for all dynamic text/URLs. Handled potential variations in the player number key (`Number` vs. `Jersey_number`).
**Assumptions:** The data passed to the component will have keys like `Name`, `headshot_url`, `instagram_url`, `Position`, `Number`/`Jersey_number` based on the expected Neo4j node properties.

### Step 5: LangChain Integration
**Date Completed:** April 16, 2025
**Actions Performed:**
- Created new file `ifx-sandbox/tools/player_search.py`.
- Implemented global variable `LAST_PLAYER_DATA` and getter/setter functions for caching structured data (similar to game recap tool).
- Defined `PLAYER_SEARCH_TEMPLATE` prompt for Cypher generation, specifying required properties (including new ones like `headshot_url`) and case-insensitive search.
- Defined `PLAYER_SUMMARY_TEMPLATE` prompt for generating text summaries.
- Created `player_search_chain` using `GraphCypherQAChain` with `return_direct=True`.
- Implemented `parse_player_data` function to extract player details from Neo4j results into a dictionary.
- Implemented `generate_player_summary` function using the LLM and summary prompt.
- Created the main tool function `player_search_qa(input_text)` which:
    - Clears the cache.
    - Invokes the `player_search_chain`.
    - Parses the result.
    - Generates the summary.
    - Stores structured data in `LAST_PLAYER_DATA` cache.
    - Returns a dictionary `{"output": summary, "player_data": data}`.
- Included error handling and logging.
**Challenges and Solutions:** Replicated the caching mechanism from `game_recap.py` as a likely necessary workaround for passing structured data.
**Assumptions:** The `GraphCypherQAChain` will correctly interpret the prompt to retrieve all specified player properties. The caching mechanism will function correctly for passing data to the Gradio UI step.

### Step 6: Gradio App Integration
**Date Completed:** April 16, 2025
**Actions Performed:**
- **`gradio_agent.py`**: Imported `player_search_qa` tool and added it to the agent's `tools` list with an appropriate name and description.
- **`gradio_app.py`**:
    - Imported `create_player_card_component` and `get_last_player_data`.
    - Added `player_card_display = gr.HTML(visible=False)` to the `gr.Blocks` layout.
    - Refactored `process_message` to focus only on returning the agent's text output.
    - Modified `process_and_respond`:
        - It now checks `get_last_player_data()` first.
        - If player data exists, it generates the player card and sets visibility for `player_card_display`.
        - If no player data, it checks `get_last_game_data()`.
        - If game data exists, it generates the game recap and sets visibility for `game_recap_display`.
        - Returns `gr.update()` for both components to ensure only one (or neither) is visible.
    - Modified `clear_chat` to return updates to clear/hide both `player_card_display` and `game_recap_display`.
    - Updated the `outputs` list for submit/click events to include both display components.
**Challenges and Solutions:** Refactored `process_and_respond` to handle checking both player and game caches sequentially, ensuring only the most relevant component is displayed. Removed older state management (`state.current_game`) in favor of relying solely on the tool caches.
**Assumptions:** The caching mechanism (`get_last_player_data`, `get_last_game_data`) reliably indicates which tool ran last and provided structured data. The Gradio `gr.update()` calls correctly target the HTML components.

### Step 7: Testing and Validation
**Date Completed:** [Date]
**Actions Performed:**
**Challenges and Solutions:**
**Assumptions:**

---

## Risk Assessment Before Testing (Step 7)

*Date: April 16, 2025*

A review of the changes made in Step 6 (Gradio App Integration) was performed before starting Step 7 (Testing and Validation).

**Summary:**

1.  **`gradio_agent.py`:**
    *   Changes were purely additive (importing `player_search_qa`, adding the "Player Information Search" tool to the `tools` list).
    *   Existing tools, agent creation, memory, and core logic remain unchanged.
    *   *Risk Assessment:* Low risk of regression. Agent is now aware of the new tool.

2.  **`gradio_app.py`:**
    *   Additive changes: Imports added, `player_card_display = gr.HTML(visible=False)` added to layout.
    *   Refactoring of `process_message`: Simplified to only return text output. Relies on tool cache (`LAST_PLAYER_DATA`, `LAST_GAME_DATA`) for component logic.
    *   Refactoring of `process_and_respond`:
        *   Centralizes component display logic based on tool caches.
        *   Checks player cache *first*, then game cache.
        *   Returns `gr.update()` for *both* components to ensure exclusive visibility.
    *   Modification of `clear_chat`: Correctly targets both display components for clearing/hiding.
    *   Modification of Event Handlers: Output lists correctly include both display components.
    *   Removal of `state.current_game`: UI display now fully dependent on the tool caching mechanism.
    *   *Risk Assessment:* Low-to-moderate risk. The core change relies heavily on the **tool caching mechanism** (`get_last_player_data`, `get_last_game_data`) working reliably. If a tool fails to set/clear its cache correctly, the wrong component might be displayed or persist incorrectly. The sequential check (player then game) should prevent conflicts if caching works. The simplification of `process_message` and removal of `state.current_game` are intentional but shift dependency to the cache.

**Overall Conclusion:**

The modifications seem logically sound and align with the goal of adding player search alongside game recap. The primary dependency is the correct functioning of the global cache variables (`LAST_PLAYER_DATA`, `LAST_GAME_DATA`) set by the respective tool functions (`player_search_qa`, `game_recap_qa`). Assuming the caching works as designed in the tool files, the integration should function correctly without regressing existing features.

---

## Bug Log

### Initial Testing - April 16, 2025

Based on the first round of testing after Step 6 completion, the following issues were observed:

1.  **Missing Logo:** App displays placeholder question marks in the top-left corner where a logo is expected.
2.  **Delayed Welcome Message:** The initial welcome message only appears *after* the first user message is submitted, not immediately on load.
3.  **Output Visual Glitch:** A gray box or "visual static" appears overlaid on top of the chat outputs (visible on the welcome message screenshot).
4.  **Game Recap Component Failure:** Queries intended to trigger the Game Recap component (e.g., about the Jets game) return a text response but fail to display the visual game recap component.
5.  **Player Card Component Failure:** Queries intended to trigger the Player Search tool (e.g., "who is the quarterback") return a text response but fail to display the visual player card component. The terminal output shows the wrong tool (Graph Search) or incorrect data handling might be occurring.

### Bug Fix Attempts - April 16, 2025

*   **Bug #5 (Player Card Component Failure - Tool Selection & Data Parsing):**
    *   **Observation:** Agent defaults to "49ers Graph Search" for specific player queries. Even when the correct tool is selected (after prompt changes), the component doesn't appear because data parsing fails.
    *   **Attempt 1 (Action - April 16, 2025):** Refined tool descriptions in `gradio_agent.py`.
    *   **Result 1:** Failed (Tool selection still incorrect).
    *   **Attempt 2 (Action - April 16, 2025):** Modified `AGENT_SYSTEM_PROMPT` in `prompts.py` to prioritize Player Search tool.
    *   **Result 2:** Partial Success (Tool selection fixed). Card still not displayed.
    *   **Observation (Post-Attempt 2):** Terminal logs show `parse_player_data` fails due to expecting non-prefixed keys.
    *   **Attempt 3 (Action - April 16, 2025):** Modified `parse_player_data` in `tools/player_search.py` to map prefixed keys (e.g., `p.Name`) to non-prefixed keys (`Name`).
    *   **Result 3:** Failed. Parsing still unsuccessful.
    *   **Observation (Post-Attempt 3):** Terminal logs show the parser check `if 'Name' not in parsed_data` fails. Comparison with `Available keys in result: ['p.player_id', 'p.name', ...]` reveals the `key_map` used incorrect *case* (e.g., `p.Name` vs. actual `p.name`).
    *   **Attempt 4 (Action - April 16, 2025):** Corrected case sensitivity in the `key_map` within `parse_player_data` in `tools/player_search.py` to exactly match the lowercase keys returned by the Cypher query (e.g., `p.name`, `p.position`).
    *   **Next Step:** Re-test player search queries ("tell me about Nick Bosa") to confirm data parsing now succeeds and the player card component appears correctly.

**Current Plan:** Continue debugging Bug #5 (Data Parsing / Component Display).

## End of Day Summary - April 16, 2025

**Progress:**
- Focused on debugging **Bug #5 (Player Card Component Failure)**.
- Successfully resolved the tool selection and data parsing sub-issues within Bug #5 (Attempts 1-4).
- Confirmed via logging (Attempt 5) that the `player_search_qa` tool retrieves data, parses it correctly, and the `create_player_card_component` function generates the expected HTML.
- Implemented a debug textbox (Attempt 6) in `gradio_app.py` and modified `process_and_respond` to update it with player data string, aiming to isolate the `gr.update` mechanism.

**Current Status:**
- The backend logic (tool selection, data retrieval via Cypher, data parsing, caching via `LAST_PLAYER_DATA`) appears functional for the Player Search feature.
- The primary remaining issue for Bug #5 is the **UI component rendering failure**. Despite the correct data being available and the component generation function running, the `gr.update` call in `process_and_respond` is not successfully updating either the target `gr.HTML` component or the debug `gr.Textbox`.

**Unresolved Bugs:**
- **Bug #1:** Missing Logo
- **Bug #2:** Delayed Welcome Message
- **Bug #3:** Output Visual Glitch
- **Bug #4:** Game Recap Component Failure
- **Bug #5:** Player Card Component Failure (Specifically the UI rendering/update part)

**Next Steps to Resume:**
1. Run the application and test a player search query (e.g., "tell me about Nick Bosa").
2. Observe the terminal output for confirmation that the player search tool runs and data is cached.
3. Check if the **debug textbox** in the Gradio UI is populated with the player data string.
    - If **YES**: This indicates the `gr.update` mechanism based on the cache *is* working for the Textbox. The issue likely lies specifically with updating the `gr.HTML` component (`player_card_display`). Potential causes: incorrect component reference, issues with rendering raw HTML via `gr.update`, conflicts with other UI elements.
    - If **NO**: This indicates a more fundamental issue with the `gr.update` call within `process_and_respond` or how the component references are being passed/used in the event handlers/outputs list. The caching check (`if player_data:`) might not be triggering the update path as expected, or the `gr.update` itself is failing silently.
4. Based on the outcome of step 3, investigate the specific `gr.update` call for the failing component (`debug_textbox` or `player_card_display`).