# Task 1.2.3 Team Search Implementation Instructions

## Context
You are an expert at  UI/UX design and software front-end development and architecture.  You are allowed to not know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.

When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.

## Objective
You are to follow the step-by-step process in order to build the Team Info Search feature (Task 1.2.3). This involves scraping recent team news, processing it, storing it in Neo4j, and updating the Gradio application to allow users to query this information. The initial focus is on the back-end logic and returning correct text-based information, with visual components to be integrated later. The goal is for the user to ask the app a question about the team and get a rich text response based on recent news articles.

## Instruction Steps

1.  **Codebase Review:** Familiarize yourself with the existing project structure:
    *   `gradio_agent.py`: Understand how LangChain Tools (`Tool.from_function`) are defined with descriptions for intent recognition and how they wrap functions from the `tools/` directory.
    *   `tools/`: Review `player_search.py`, `game_recap.py`, and `cypher.py` for examples of tool functions, Neo4j interaction, and data handling.
    *   `components/`: Examine `player_card_component.py` and `game_recap_component.py` for UI component structure.
    *   `gradio_app.py`: Analyze how it integrates components, handles user input/output (esp. `process_message`, `process_and_respond`), and interacts with the agent.
    *   `.env`/`gradio_agent.py`: Note how API keys are loaded.
2.  **Web Scraping Script:**
    *   Create a new Python script (e.g., in the `tools/` directory named `team_news_scraper.py`) dedicated to scraping articles.  
    *   **Refer to existing scripts** in `data/april_11_multimedia_data_collect/` (like `get_player_socials.py`, `player_headshots.py`, `get_youtube_playlist_videos.py`) for examples of:
        *   Loading API keys/config from `.env` using `dotenv` and `os.getenv()`.
        *   Making HTTP requests (likely using the `requests` library).
        *   Handling potential errors using `try...except` blocks.
        *   Implementing delays (`time.sleep()`) between requests.
        *   Writing data to CSV files using the `csv` module.
    *   Target URL: `https://www.ninersnation.com/san-francisco-49ers-news`
    *   Use libraries like `requests` to fetch the page content and `BeautifulSoup4` (you may need to add this to `requirements.txt`) to parse the HTML.
    *   Scrape articles published within the past 60 days.
    *   For each article, extract:
        *   Title
        *   Content/Body
        *   Publication Date
        *   Article URL (`link_to_article`)
        *   Content Tags (e.g., Roster, Draft, Depth Chart - these often appear on the article page). Create a comprehensive set of unique tags encountered.
    *   Refer to any previously created scraping files for examples of libraries and techniques used (e.g., BeautifulSoup, requests).
3.  **Data Structuring (CSV):**
    *   Process the scraped data to fit the following CSV structure:
        *   `Team_name`: (e.g., "San Francisco 49ers" - Determine how to handle articles not specific to the 49ers, discuss if unclear)
        *   `season`: (e.g., 2024 - Determine how to assign this)
        *   `city`: (e.g., "San Francisco")
        *   `conference`: (e.g., "NFC")
        *   `division`: (e.g., "West")
        *   `logo_url`: (URL for the 49ers logo - Confirm source or leave blank)
        *   `summary`: (Placeholder for LLM summary)
        *   `topic`: (Assign appropriate tag(s) extracted during scraping)
        *   `link_to_article`: (URL extracted during scraping)
    *   Consider the fixed nature of some columns (Team\_name, city, conference, etc.) and how to populate them accurately, especially if articles cover other teams or general news.
4.  **LLM Summarization:**
    *   For each scraped article's content, use the OpenAI GPT-4o model (configured via credentials in the `.env` file) *within the scraping/ingestion script* to generate a concise 3-4 sentence summary.
    *   **Do NOT use `gradio_llm.py` for this task.**
    *   Populate the `summary` column in your data structure with the generated summary.
5.  **Prepare CSV for Upload:**
    *   Save the structured and summarized data into a CSV file (e.g., `team_news_articles.csv`).
6.  **Neo4j Upload:**
    *   Develop a script or function (potentially augmenting existing Neo4j tools) to upload the data from the CSV to the Neo4j database.
    *   Ensure the main `:Team` node exists and has the correct season record: `MERGE (t:Team {name: "San Francisco 49ers"}) SET t.season_record_2024 = "6-11", t.city = "San Francisco", t.conference = "NFC", t.division = "West"`. Add other static team attributes here as needed.
    *   Create new `:Team_Story` nodes for the team content.
    *   Define appropriate properties for these nodes based on the CSV columns.
    *   Establish relationships connecting each `:Team_Story` node to the central `:Team` node (e.g., `MATCH (t:Team {name: "San Francisco 49ers"}), (s:Team_Story {link_to_article: row.link_to_article}) MERGE (s)-[:STORY_ABOUT]->(t)`). Consult existing schema or propose a schema update if necessary.
    *   Ensure idempotency by using `MERGE` on `:Team_Story` nodes using the `link_to_article` as a unique key.
7.  **Gradio App Stack Update:**
    *   **Define New Tool:** In `gradio_agent.py`, define a new `Tool.from_function` named e.g., "Team News Search". Provide a clear `description` guiding the LangChain agent to use this tool for queries about recent team news, articles, or topics (e.g., "Use for questions about recent 49ers news, articles, summaries, or specific topics like 'draft' or 'roster moves'. Examples: 'What's the latest team news?', 'Summarize recent articles about the draft'").
    *   **Create Tool Function:** Create the underlying Python function (e.g., `team_story_qa` in a new file `tools/team_story.py` or within the scraper script if combined) that this new Tool will call. Import it into `gradio_agent.py`.
    *   **Neo4j Querying (within Tool Function):** The `team_story_qa` function should take the user query/intent, construct an appropriate Cypher query against Neo4j to find relevant `:Team_Story` nodes (searching summaries, titles, or topics), execute the query (using helpers from `tools/cypher.py`), and process the results.
    *   **Return Data (from Tool Function):** The `team_story_qa` function should return the necessary data, primarily the text `summary` and `link_to_article` for relevant stories.
    *   **Display Logic (in `gradio_app.py`):** Modify the response handling logic in `gradio_app.py` (likely within `process_and_respond` or similar functions) to detect when the "Team News Search" tool was used. When detected, extract the data returned by `team_story_qa` and pass it to the new component (from Step 8) for rendering in the UI.
8.  **Create New Gradio Component (Placeholder):**
    *   Create a new component file (e.g., `components/team_story_component.py`) based on the style of `components/player_card_component.py`.
    *   This component should accept the data returned by the `team_story_qa` function (e.g., a list of dictionaries, each with 'summary' and 'link_to_article').
    *   For now, it should format and display this information as clear text (e.g., iterate through results, display summary, display link).
    *   Ensure this component is used by the updated display logic in `gradio_app.py` (Step 7).

## Data Flow Architecture (Simplified)
1.  User submits a natural language query via the Gradio interface.
2.  The query is processed by the agent (`gradio_agent.py`) which selects the "Team News Search" tool based on its description.
3.  The agent executes the tool, calling the `team_story_qa` function.
4.  The `team_story_qa` function queries Neo4j via `tools/cypher.py`.
5.  Neo4j returns relevant `:Team_Story` node data (summary, link, topic, etc.).
6.  The `team_story_qa` function processes and returns this data.
7.  The agent passes the data back to `gradio_app.py`.
8.  `gradio_app.py`'s response logic identifies the tool used, extracts the data, and passes it to the `team_story_component`.
9.  The `team_story_component` renders the text information within the Gradio UI.

## Error Handling Strategy
1.  Implement robust error handling in the scraping script (handle network issues, website changes, missing elements).
2.  Add error handling for LLM API calls (timeouts, rate limits, invalid responses).
3.  Include checks and error handling during CSV generation and Neo4j upload (data validation, connection errors, query failures).
4.  Gracefully handle cases where no relevant articles are found in Neo4j for a user's query.
5.  Provide informative (though perhaps technical for now) feedback if intent recognition or query mapping fails.

## Performance Optimization
1.  Implement polite scraping practices (e.g., delays between requests) to avoid being blocked.
2.  Consider caching LLM summaries locally if articles are scraped repeatedly, though the 60-day window might limit the benefit.
3.  Optimize Neo4j Cypher queries for efficiency, potentially creating indexes on searchable properties like `topic` or keywords within `summary`.

## Failure Conditions
- If you are unable to complete any step after 3 attempts, immediately halt the process and consult with the user on how to continue.
- Document the failure point and the reason for failure.
- Do not proceed with subsequent steps until the issue is resolved.

## Completion Criteria & Potential Concerns

**Success Criteria:**
1.  A functional Python script exists that scrapes articles from the specified URL according to the requirements.
2.  A CSV file is generated containing the scraped, processed, and summarized data in the specified format.
3.  The data from the CSV is successfully uploaded as new nodes (e.g., `:Team_Story`) into the Neo4j database, linked to a `:Team` node which includes the `season_record_2024` property set to "6-11".
4.  The Gradio application correctly identifies user queries about team news/information.
5.  The application queries Neo4j via the new tool function (`team_story_qa`) and displays relevant article summaries and links (text-only) using the new component (`team_story_component.py`) integrated into `gradio_app.py`.
6.  **Crucially:** No existing functionality (Player Search, Game Recap Search etc.) is broken. All previous features work as expected.

**Deliverables:**
*   This markdown file (`Task 1.2.3 Team Search Implementation.md`).
*   The Python script for web scraping.
*   The Python script or function(s) used for Neo4j upload.
*   Modified files (`gradio_app.py`, `gradio_agent.py`, `tools/cypher.py`, potentially others) incorporating the new feature.
*   The new Gradio component file (`components/team_story_component.py`).

**Challenges / Potential Concerns & Mitigation Strategies:**

1.  **Web Scraping Stability:**
    *   *Concern:* The structure of `ninersnation.com` might change, breaking the scraper. The site might use JavaScript to load content dynamically. Rate limiting or IP blocking could occur.
    *   *Mitigation:* Build the scraper defensively (e.g., check if elements exist before accessing them). Use libraries like `requests-html` or `selenium` if dynamic content is an issue (check existing scrapers first). Implement delays and potentially user-agent rotation. Log errors clearly. Be prepared to adapt the scraper if the site changes.
2.  **LLM Summarization:**
    *   *Concern:* LLM calls (specifically to OpenAI GPT-4o) can be slow and potentially expensive. Summary quality might vary or contain hallucinations. API keys need secure handling.
    *   *Mitigation:* Implement the summarization call within the ingestion script. Process summaries asynchronously if feasible within the script's logic. Implement retries for API errors. Use clear prompts to guide the LLM towards factual summarization based *only* on the provided text. Ensure API keys are loaded securely from `.env` following the pattern in `gradio_agent.py`.
3.  **Data Schema & Neo4j:**
    *   *Concern:* How should non-49ers articles scraped from the site be handled if the focus is 49ers-centric `:Team_Story` nodes? Defining the `:Team_Story` node properties and relationships needs care. Ensuring idempotent uploads is important.
    *   *Mitigation:* Filter scraped articles to only include those explicitly tagged or clearly about the 49ers before ingestion. Alternatively, **Consult User** on whether to create generic `:Article` nodes for non-49ers content or simply discard them. Propose a clear schema for `:Team_Story` nodes and their relationship to the `:Team` node. Use `MERGE` in Cypher queries with the article URL as a unique key for `:Team_Story` nodes and the team name for the `:Team` node to ensure idempotency.
4.  **Gradio Integration & Regression:**
    *   *Concern:* Modifying the core agent (`gradio_agent.py` - adding a Tool) and app files (`gradio_app.py` - modifying response handling) carries a risk of introducing regressions. Ensuring the new logic integrates smoothly is vital.
    *   *Mitigation:* **Prioritize Non-Invasive Changes:** Add the new Tool and its underlying function cleanly. **Isolate Changes:** Keep the new `team_story_qa` function and `team_story_component.py` self-contained. **Thorough Review:** Before applying changes to `gradio_agent.py` (new Tool) and especially `gradio_app.py` (response handling logic), present the diff to the user for review. **Testing:** Manually test existing features (Player Search, Game Recap) after integration. Add comments. Follow existing patterns closely.

## Notes
*   Focus on delivering the text-based summary and link first; UI polish can come later.
*   Review existing code for patterns related to scraping, Neo4j interaction, LLM calls, and Gradio component creation.
*   Adhere strictly to the instructions regarding modifying existing code – additively and with caution, seeking review for core file changes.
*   Document any assumptions made during implementation.

## Implementation Notes

### Step 1: Codebase Review

Reviewed the following files to understand the existing architecture and patterns:

*   **`gradio_agent.py`**: Defines the LangChain agent (`create_react_agent`, `AgentExecutor`), loads API keys from `.env`, imports tool functions from `tools/`, defines tools using `Tool.from_function` (emphasizing the `description`), manages chat history via Neo4j, and orchestrates agent interaction in `generate_response`.
*   **`tools/player_search.py` & `tools/game_recap.py`**: Define specific tools. They follow a pattern: define prompts (`PromptTemplate`), use `GraphCypherQAChain` for Neo4j, parse results into structured dictionaries, generate summaries/recaps with LLM, and return both text `output` and structured `*_data`. They use a global variable cache (`LAST_*_DATA`) to pass structured data to the UI, retrieved by `get_last_*_data()`.
*   **`tools/cypher.py`**: Contains a generic `GraphCypherQAChain` (`cypher_qa`) with a detailed prompt (`CYPHER_GENERATION_TEMPLATE`) for translating NL to Cypher. It includes the `cypher_qa_wrapper` function used by the general "49ers Graph Search" tool. It doesn't provide reusable direct Neo4j execution helpers; specific tools import the `graph` object directly.
*   **`components/player_card_component.py` & `components/game_recap_component.py`**: Define functions (`create_*_component`) that take structured data dictionaries and return `gr.HTML` components with formatted HTML/CSS. `game_recap_component.py` also has `process_game_recap_response` to extract structured data from the agent response.
*   **`gradio_app.py`**: Sets up the Gradio UI (`gr.Blocks`, `gr.ChatInterface`). Imports components and agent functions. Manages chat state. The core logic is in `process_and_respond`, which calls the agent, retrieves cached structured data using `get_last_*_data()`, creates the relevant component, and returns text/components to the UI. This function will need modification to integrate the new Team Story component.
*   **`.env`**: Confirms storage of necessary API keys (OpenAI, Neo4j, Zep, etc.) and the `OPENAI_MODEL` ("gpt-4o"). Keys are accessed via `os.environ.get()`.

**Conclusion**: ✅ The codebase uses LangChain agents with custom tools for specific Neo4j tasks. Tools return text and structured data; structured data is passed to UI components via a global cache workaround. UI components render HTML based on this data. The main `gradio_app.py` orchestrates the flow and updates the UI. This pattern should be followed for the new Team News Search feature.

### Step 2: Web Scraping Script

1.  **File Creation**: Created `ifx-sandbox/tools/team_news_scraper.py`.
2.  **Dependencies**: Added `requests` and `beautifulsoup4` to `ifx-sandbox/requirements.txt`.
3.  **Structure**: Implemented the script structure with functions for:
    *   `fetch_html(url)`: Fetches HTML using `requests`.
    *   `parse_article_list(html_content)`: Parses the main news page using `BeautifulSoup` to find article links (`div.c-entry-box--compact h2 a`) and publication dates (`time[datetime]`). Includes fallback selectors.
    *   `parse_article_details(html_content, url)`: Parses individual article pages using `BeautifulSoup` to extract title (`h1`), content (`div.c-entry-content p`), publication date (`span.c-byline__item time[datetime]` or fallback `time[datetime]`), and tags (`ul.m-tags__list a` or fallback `div.c-entry-group-labels a`). Includes fallback selectors and warnings.
    *   `is_within_timeframe(date_str, days)`: Checks if the ISO date string is within the last 60 days.
    *   `scrape_niners_nation()`: Orchestrates fetching, parsing, filtering (last 60 days), and applies a 1-second delay between requests.
    *   `structure_data_for_csv(scraped_articles)`: Placeholder function to prepare data for CSV (Step 3).
    *   `write_to_csv(data, filename)`: Writes data to CSV using `csv.DictWriter`.
4.  **Execution**: Added `if __name__ == "__main__":` block to run the scraper directly, saving results to `team_news_articles_raw.csv`.
5.  **Parsing Logic**: Implemented specific HTML parsing logic based on analysis of the provided sample URL (`https://www.ninersnation.com/2025/4/16/24409910/...`) and common SBNation website structures. Includes basic error handling and logging for missing elements.

**Status**: ✅ The script is implemented but depends on the stability of Niners Nation's HTML structure. It currently saves raw scraped data; Step 3 will refine the output format, and Step 4 will add LLM summarization.

### Step 3: Data Structuring (CSV)

1.  **Review Requirements**: Confirmed the target CSV columns: `Team_name`, `season`, `city`, `conference`, `division`, `logo_url`, `summary`, `topic`, `link_to_article`.
2.  **Address Ambiguities**: 
    *   `Team_name`, `city`, `conference`, `division`: Hardcoded static values ("San Francisco 49ers", "San Francisco", "NFC", "West"). Added a comment noting the assumption that all scraped articles are 49ers-related.
    *   `season`: Decided to derive this from the publication year of the article.
    *   `logo_url`: Left blank as instructed.
    *   `topic`: Decided to use a comma-separated string of the tags extracted in Step 2 (defaulting to "General News" if no tags were found).
    *   `summary`: Left as an empty string placeholder for Step 4.
3.  **Implement `structure_data_for_csv`**: Updated the function in `team_news_scraper.py` to iterate through the raw scraped article dictionaries and create new dictionaries matching the target CSV structure, performing the mappings and derivations decided above.
4.  **Update `write_to_csv`**: Modified the CSV writing function to use a fixed list of `fieldnames` ensuring correct column order. Updated the output filename constant to `team_news_articles_structured.csv`.
5.  **Refinements**: Improved date parsing in `is_within_timeframe` for timezone handling. Added checks in `scrape_niners_nation` to skip articles missing essential details (title, content, date) and avoid duplicate URLs.

**Status**: ✅ The scraper script now outputs a CSV file (`team_news_articles_structured.csv`) conforming to the required structure, with the `summary` column ready for population in the next step.

### Step 4: LLM Summarization

1.  **Dependencies & Config**: Added `openai` import to `team_news_scraper.py`. Added logic to load `OPENAI_API_KEY` and `OPENAI_MODEL` (defaulting to `gpt-4o`) from `.env` using `dotenv`. Added `ENABLE_SUMMARIZATION` flag based on API key presence.
2.  **Summarization Function**: Created `generate_summary(article_content)` function:
    *   Initializes OpenAI client (`openai.OpenAI`).
    *   Uses a prompt instructing the model (`gpt-4o`) to generate a 3-4 sentence summary based *only* on the provided content.
    *   Includes basic error handling for `openai` API errors (APIError, ConnectionError, RateLimitError) returning an empty string on failure.
    *   Includes basic content length truncation before sending to API to prevent excessive token usage.
3.  **Integration**: 
    *   Refactored the main loop into `scrape_and_summarize_niners_nation()`.
    *   Modified `parse_article_details` to ensure raw `content` is returned.
    *   The main loop now calls `generate_summary()` after successfully parsing an article's details (if content exists).
    *   The generated summary is added to the article details dictionary.
    *   Created `structure_data_for_csv_row()` helper to structure each article's data *including the summary* within the loop.
4.  **Output File**: Updated `OUTPUT_CSV_FILE` constant to `team_news_articles.csv`.

**Status**: ✅ The scraper script (`team_news_scraper.py`) now integrates LLM summarization using the OpenAI API. When run directly, it scrapes articles, generates summaries for their content, structures the data (including summaries) into the target CSV format, and saves the final result to `team_news_articles.csv`.

### Step 5: Prepare CSV for Upload

1.  **CSV Generation**: The `team_news_scraper.py` script, upon successful execution via the `if __name__ == "__main__":` block, now generates the final CSV file (`ifx-sandbox/tools/team_news_articles.csv`) containing the structured and summarized data as required by previous steps.

**Status**: ✅ The prerequisite CSV file for the Neo4j upload is prepared by running the scraper script.

### Step 6: Neo4j Upload

1.  **Develop Neo4j Upload Script**: Create a script to upload the data from the CSV to the Neo4j database.
2.  **Ensure Neo4j Connection**: Ensure the script can connect to the Neo4j database.
3.  **Implement Upload Logic**: Implement the logic to upload the data to Neo4j.
4.  **Error Handling**: Add error handling for connection errors and query failures.

**Status**: ✅ The data from the CSV is successfully uploaded as new nodes (e.g., `:Team_Story`) into the Neo4j database, linked to a `:Team` node which includes the `season_record_2024` property set to "6-11".

### Step 7: Gradio App Stack Update

1.  **Define New Tool**: In `gradio_agent.py`, define a new `Tool.from_function` named e.g., "Team News Search".
2.  **Create Tool Function**: Create the underlying Python function (e.g., `team_story_qa` in a new file `tools/team_story.py` or within the scraper script if combined) that this new Tool will call. Import it into `gradio_agent.py`.
3.  **Neo4j Querying**: The `team_story_qa` function should take the user query/intent, construct an appropriate Cypher query against Neo4j to find relevant `:Team_Story` nodes (searching summaries, titles, or topics), execute the query (using helpers from `tools/cypher.py`), and process the results.
4.  **Return Data**: The `team_story_qa` function should return the necessary data, primarily the text `summary` and `link_to_article` for relevant stories.
5.  **Display Logic**: Modify the response handling logic in `gradio_app.py` (likely within `process_and_respond` or similar functions) to detect when the "Team News Search" tool was used. When detected, extract the data returned by `team_story_qa` and pass it to the new component (from Step 8) for rendering in the UI.

**Status**: The Gradio application correctly identifies user queries about team news/information and queries Neo4j via the new tool function (`team_story_qa`).

### Step 8: Create New Gradio Component

1.  **Create New Component**: Create a new component file (e.g., `components/team_story_component.py`) based on the style of `components/player_card_component.py`.
2.  **Accept Data**: The component should accept the data returned by the `team_story_qa` function (e.g., a list of dictionaries, each with 'summary' and 'link_to_article').
3.  **Format Display**: For now, it should format and display this information as clear text (e.g., iterate through results, display summary, display link).
4.  **Use Component**: Ensure this component is used by the updated display logic in `gradio_app.py` (Step 5).

**Status**: The new Gradio component file (`components/team_story_component.py`) is created and integrated into the Gradio application.

### Step 9: Error Handling

1.  **Implement Robust Error Handling**: Add error handling for scraping, LLM calls, and Neo4j connection issues.
2.  **Provide Informative Feedback**: Gracefully handle cases where no relevant articles are found in Neo4j for a user's query and provide informative feedback if intent recognition or query mapping fails.

**Status**: The Gradio application now includes robust error handling and informative feedback for scraping, LLM calls, and Neo4j connection issues.

### Step 10: Performance Optimization

1.  **Implement Polite Scraping Practices**: Implement delays between requests to avoid being blocked.
2.  **Consider Caching**: Consider caching LLM summaries locally if articles are scraped repeatedly, though the 60-day window might limit the benefit.
3.  **Optimize Neo4j Cypher Queries**: Optimize Neo4j Cypher queries for efficiency, potentially creating indexes on searchable properties like `topic` or keywords within `summary`.

**Status**: The Gradio application now includes polite scraping practices, caching, and optimized Neo4j Cypher queries.

### Step 11: Failure Handling

1.  **Implement Robust Error Handling**: Add error handling for scraping, LLM calls, and Neo4j connection issues.
2.  **Implement Retry Logic**: Implement retry logic for scraping, LLM calls, and Neo4j connection issues.
3.  **Implement Fallback Logic**: Implement fallback logic for scraping, LLM calls, and Neo4j connection issues.

**Status**: The Gradio application now includes robust error handling, retry logic, and fallback logic for scraping, LLM calls, and Neo4j connection issues.

### Step 12: Completion Criteria

1.  **Verify CSV Generation**: Verify that the CSV file is generated correctly.
2.  **Verify Neo4j Upload**: Verify that the data from the CSV is successfully uploaded as new nodes (e.g., `:Team_Story`) into the Neo4j database, linked to a `:Team` node which includes the `