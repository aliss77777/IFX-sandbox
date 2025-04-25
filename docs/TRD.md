# IFX AI Companion –  Technical Requirements (WIP)

## 1. App at a Glance

**Name:** IFX Companion

**Summary:**
An AI-powered sports fan assistant that creates immersive, multimodal, and personalized experiences around NFL teams, players, games, rules, and fan communities. The app delivers conversational responses enhanced with visuals and session memory.

**Primary Users:**
- **Novice Fans:** Curious about the sport
- **Intermediate Fans:** Seeking updates and highlights
- **Super Fans:** Wanting in-depth stats, analysis, and community connection

**Key Value Proposition:**
IFX Companion makes fans feel seen, informed, and connected — through natural language, visual storytelling, and personalized interactions tailored to their fandom level.

## 2. Experience Principles

### Natural Language Question and Answers
Give the user a search interface to immediately find the focus of their intention, improving on existing league and teams apps (NFL, SF 49ers) that don't provide similar functionality.

### Dynamic UI Outputs Tailored to User's Query
Dynamic layout and content of AI responses, based on the user's query (player / game / team) give the user an engaging and contextually relevant experience.

### Personalization Based on User Profile
Pre-created fan profiles allow the user to select archetypes (casual fan, consistent fan, superfan) and experience different content and recommendations.

### Connection with Communities of Like-Minded Fans
Recommendations for how to engage and participate with real-world fan communities allows the fan to join a bigger movement.

## 3. Feature Overview

### 0. Persona Selection
- **Description:**
  User chooses a predefined persona that represents their level of engagement (novice, intermediate, super fan). This sets a `persona_id` and initializes a memory object in Zep.
- **Inputs:**
  Button click (Gradio)
- **Outputs:**
  Persona object passed into session memory for use in future context
- **Priority:**
  **High**

**Persona Memory Structure (Zep)**  
```json
{
  "persona_id": "superfan",
  "name": "The Strategist",
  "fan_level": "advanced",
  "favorite_team": "49ers",
  "preferred_channels": ["YouTube", "Twitter"]
}
```

### 1. Team Search
- **Description:** Natural language queries about team history, season recaps, outlooks, and trending stories.
- **Data Source:** Preloaded Neo4j graph database (no external SERP/API)
- **Display:** Dynamic Gradio widget layout with text + media (image, video preview)
- **Examples:**
  - "Tell me about the 49ers"
  - "How did they do in the offseason?"
  - "Are they going to be good this year?"
- **Priority:** High

### 2. Player Search
- **Description:** Player-specific queries, from basic info to advanced game-by-game stat breakdowns.
- **Data Source:** Preloaded Neo4j
- **Display:** Profile image + stat preview components
- **Examples:**
  - "Who is the starting QB?"
  - "What was Deebo Samuel's best game?"
  - "How accurate is Brock Purdy's deep ball?"
- **Priority:** High

### 3. Game Recap Search
- **Description:** Game-level summaries and key moments/highlights.
- **Data Source:** Preloaded Neo4j
- **Display:** Recap text block + embedded image or video preview
- **Examples:**
  - "How did the 49ers do vs Dolphins?"
  - "What was the key play in the Seahawks loss?"
- **Priority:** High

### 4. Fan Community Search
- **Description:** Allows users to find fan communities in a given location.
- **Data Source:** Neo4j (chapter name, location, contact info)
- **Input:** Location (e.g. city/state)
- **Output:** Community info cards
- **Examples:**
  - "Are there any 49ers fan groups in Iowa?"
- **Priority:** Medium

### 5. Rule Search (Deferred)
- **Description:** Future use of RAG or LLMs to answer football rules queries.
- **Status:** Deferred from MVP

### 6. Synthetic Data Generation
- **Description:** Create fictional mens pro soccer league, teams, players, and associated media assets.
- **Data Source:** AI-generated content with consistent patterns and relationships
- **Output:** Complete dataset of fictional sports entities with media assets
- **Status:** High risk, requiring detailed workplan and level of effort assessment
- **Priority:** High (scheduled for Phase 2)

## 4. Technical Stack & Constraints

### Frontend:
- Gradio (Python)
- Responsive, widget-based layout for chat and dynamic components
- Designed to be portable to other frameworks after POC

### Backend:
- Modular microservices using MCP (Model Context Protocol)
- Each feature (team, player, game, fan) is its own callable service module
- Stateless with Zep memory injected as needed

### Memory:
- Zep memory management using persona_id
- Memory updates per session stored but without historical user data in MVP

### Database:
- Neo4j for all structured data:
  - Teams
  - Players
  - Games
  - Fan communities

### Hosting:
- Hugging Face Spaces (initial deployment)

### Constraints:
- No social logins or dynamic user accounts (MVP only)
- All personalization is based on preselected personas
- AI must not hallucinate or create false summaries — must stick to data in graph or defined assets

## 5. App Architecture & Workflow

```mermaid
flowchart TD
    A[Select Persona] --> B[Load Zep Persona Memory]
    B --> C[User Query (Text Input)]
    C --> D[Classify Intent (Team/Player/Game/Fan)]
    D --> E[Call MCP Service]
    E --> F[Retrieve from Neo4j]
    F --> G[Render Output in Gradio]
    G --> H[Update Zep Memory]
```

## 6. Deployment & Testing

### Deployment:
- Code managed via GitHub
- Hugging Face Spaces deployment using standard YAML metadata
- All assets and dependencies pinned in requirements.txt

### Testing Strategy:
- Manual testing of each feature during development
- Integration testing when components are connected
- User acceptance testing before release

## 7. Design System (49ers Themed)

### Color Palette:
- Primary Red: #AA0000
- Gold Accent: #B3995D
- Shadow Black: #111111
- Cool Gray: #E6E6E6
- White: #FFFFFF

### Typography:
- Headlines: "Impact," sans-serif (or similar bold typeface)
- Body: "Open Sans," sans-serif

## 8. Component Library – Actual Project Components

The application is structured around modular components and tools that handle different aspects of the fan experience:

| Component | File | Purpose |
|-----------|------|---------|
| **Tool Components (Logic)** |
| Player Search | `tools/player_search.py` | Retrieves and processes player data from Neo4j |
| Game Recap | `tools/game_recap.py` | Handles game information and highlight retrieval |
| Team Story | `tools/team_story.py` | Manages team news, information, and narratives |
| Cypher | `tools/cypher.py` | Provides generic Neo4j database query functionality |
| **UI Components (Gradio)** |
| Player Card | `components/player_card_component.py` | Displays player information with headshots and stats |
| Game Recap | `components/game_recap_component.py` | Shows game summary with highlight videos |
| Team Story | `components/team_story_component.py` | Presents team news and information in a UI-friendly format |

Each component follows a modular design pattern:
1. Tool components handle data retrieval and processing logic
2. UI components focus on presentation and user interaction
3. The main application connects these through the LangChain agent

## 9. Open Items / Next Steps

| Topic | Action |
|-------|--------|
| Personas | Finalize attributes for each of the 3 fan levels |
| Graph Schema | Reupload graph schema including links to media |
| Data Ingestion | Download team logo files + download game recaps |
| Component Dev | Build/test each Gradio component independently |
| Deployment | Set up GitHub+HF Spaces config for clean deployment cycle |
| CSS | Embed or reference the custom stylesheet for theme |



## 11. Detailed Work Plan

Based on a review of the existing codebase and requirements, here's a structured implementation plan:

### Phase 1: Foundation (April 14 - 25)

| Task | Description | Dependencies |
|------|-------------|--------------|
| **1.1 ✅ Data ingestion of multimedia (team thumbnails, video highlights, player headshots)** | Download and integrate image files into the graphe database | None |
| **1.2 Build and test v1 Gradio UI components** | Create components with multimedia integration, focusing on feasability rather than design polish | 1.1 |
| **1.2.1 ✅ Game Recap Search (WIP)** | Returning queries about the a specific game, display through a multi-media component in the UI *(Backend logic implemented, visual component integration pending)* | 1.1 |
| **1.2.2 ✅ Player Search (WIP)** | Return queries about the player using a multi-media component *(Backend logic implemented, visual component integration pending)* | 1.1 |
| **1.2.3 ✅ Team Info Search** | Scraped, summarized, and stored recent team news articles in Neo4j; implemented a Gradio tool and component to query and display relevant news summaries and links in the chat. | 1.1 |
| **1.3 ✅ Develop memory system and UI integration with Zep** | Implement persona-based memory system with Zep | None |

**Demo 1 Milestone:** April 22

### Phase 2: Core Integration (April 28 - May 9)

| Task | Description | Dependencies |
|------|-------------|--------------|
| **2.1 Build and Ingest Synthetic Data for Feature 6** | Create fictional mens pro soccer league, teams, players, and associated media assets | 1.1 |
| **2.2 Rebuild graph with full asset integration** | Develop and test low-latency approach for media assets | 1.1, 2.1 |
| **2.3 Refactor graph search for speed** | Optimize Neo4j queries and response time for all search features | 2.1, 2.2 |
| **2.4 Integrate with MCP** | Refactor all services to use MCP architecture for modularity and reusability | 2.2, 1.2 |
| **2.5 Onboard F/E designer** | Develop plan for Figma prototype -> Front End in Node | None |

**Demo 2 Milestone:** May 6

### Phase 3: Enhancement & Refinement (May 12 - May 23)

| Task | Description | Dependencies |
|------|-------------|--------------|
| **3.1 Cloud deployment to Hugging Face spaces** | Set up and configure deployment environment | 2.1, 2.2 |
| **3.2 Testing the tuning through FreePlay.AI** | Validate AI responses and performance | 3.1 |
| **3.3 Fine tuning responses between personality types and fan skill levels** | Customize responses based on persona | 1.3, 3.1 |
| **3.4 Refining precision of game recap search** | Improve search accuracy and relevance | 2.1, 2.2 |

**Demo 3 Milestone:** May 20

### Phase 4: Final Launch (May 26 - 29)

| Task | Description | Dependencies |
|------|-------------|--------------|
| **4.1 Final testing and adjustments** | Address any remaining issues | 3.1, 3.2, 3.3, 3.4 |
| **4.2 Documentation and handoff** | Complete all documentation | 4.1 |

**FINAL GO LIVE:** May 29

## Implementation Details

### Technical Implementation Notes

1. **Gradio Migration**
   - Update existing `gradio_app.py` to support all required components
   - Refactor `gradio_utils.py` to handle persona-based memory

2. **Neo4j Schema Enhancements**
   - Add media links to Player nodes (images, videos)
   - Ensure Game nodes have highlight video links
   - Add team-level properties for team info/history
   - Reupload graph schema including links to media

3. **Persona System**
   - Create `persona.py` module with persona definitions and selection logic
   - Enhance Zep integration to store persona context
   - Develop memory system and UI integration with Zep (Phase 1)

4. **MCP Services**
   - Create `services/` directory with modules for each domain:
     - `team_service.py`
     - `player_service.py`
     - `game_service.py`
     - `community_service.py`
   - Implement service registry and routing in `service_router.py`
   - Refactor all services using updated graph and gradio UI integration (Phase 2)

5. **UI Components**
   - Create `components/` directory with reusable components:
     - `persona_selector.py`
     - `team_card.py`
     - `player_card.py`
     - `game_recap.py`
     - `community_finder.py`
   - Build and test gradio components locally using CSV files (Phase 1)

6. **CSS Implementation**
   - Create `static/styles.css` with 49ers theming
   - Integrate with Gradio using custom CSS parameter

7. **Data Integration**
   - Complete data ingestion of team thumbnail images (Phase 1)
   - Download game recaps (Phase 1)
   - Rebuild graph with full asset integration (Phase 2)

8. **Deployment & Testing**
   - Cloud deployment to Hugging Face spaces (Phase 3)
   - Testing the tuning through FreePlay.AI (Phase 3)
   - Fine tuning responses between personality types and fan skill levels (Phase 3)
   - Refining precision of game recap search (Phase 3)
   - Final testing and adjustments (Phase 4)
   - FINAL GO LIVE on May 29

### Feature Gap Analysis

| Feature | Current Status | Work Needed |
|---------|---------------|-------------|
| Basic Chat | Implemented | Enhance with persona awareness |
| Neo4j Integration | Implemented | Add media fields to schema |
| Zep Memory | Basic implementation | Add persona structure |
| Gradio UI | Basic implementation | Add themed components |
| Persona Selection | Not implemented | Create from scratch |
| Media Components | Not implemented | Create from scratch |
| Service Architecture | Not implemented | Refactor into MCP services |
| Intent Classification | Basic implementation | Enhance with persona context |

### Resource Requirements

1. **Development Environment**
   - Python 3.9+
   - Neo4j database (access to update schema)
   - OpenAI API key
   - Zep account for memory management

2. **Assets Needed**
   - 49ers team imagery
   - Player headshots
   - Game highlight clips/thumbnails
   - Custom CSS for theming

3. **External Services**
   - Hugging Face Spaces for deployment
   - (Optional) Content hosting for media assets

### Risk Management

| Risk | Mitigation Strategy |
|------|---------------------|
| Neo4j data completeness | Conduct audit of required fields before implementation |
| Media asset availability | Create fallback text-only components if media is unavailable |
| Persona complexity | Start with simplified personas, then enhance |
| Deployment constraints | Test with Hugging Face resource limits early |
| Memory persistence | Implement simple local fallback if Zep has issues |

```## 11. Prompt Template for AI SWE Instructions

When requesting a new AI development task, execute in two phases: planning and coding. This structured approach ensures thoughtful implementation and reduces errors.

### Phase 1: Planning
The user supplies the instructions below and asks the AI to develop a comprehensive plan before any code is written. This plan should include:
- Data flow diagrams
- Component structure
- Implementation strategy
- Potential risks and mitigations
- Test approach

### Phase 2: Execution
Once the plan has been approved, the AI proceeds with implementation, making changes in a slow and careful manner in line with the First Principles below.

### Context Template

```## Context

You are an expert at UI/UX design and software front-end development and architecture. You are allowed to NOT know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.

When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.
```

### First Principles for AI Development

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
| Risk-Based Approval Scaling | Level of user approval should scale proportionately to the risk level of the task - code changes require thorough review; document edits can proceed with less oversight | Implementing a new function in the agent required step-by-step approval, while formatting improvements to markdown files could be completed in a single action |

> **Remember:** *One tiny change → test → commit. Repeat.*

### Instructions [to be updated for each task]

```
## Instruction Steps (example – update with user input below)

1. Review the player roster which is located from the workspace root at ./niners_players_headshots_with_socials_merged.csv
2. Review the 2024 game schedule located from the workspace root at ./nfl-2024-san-francisco-49ers-with-results.csv
3. Review the video highlights located from the workspace root at ./youtube_highlights.csv
4. Determine which videos are associated with which players and which games.
5. Verify the ./llm_output directory exists from the workspace root. If it does not, create it.
6. Create the players_highlights_{unix timestamp}.csv file in the llm_output directory. This is the original player roster with an additional column named "highlights" that represents an array of video URLs associated with that player
7. Create the games_highlights_{unix_timestamp}.csv file in the llm_output directory. This is the original game schedule csv with an additional column named "highlights" that represents an array of video URLs associated with that game
8. If any video(s) is neither associated with a player or a game, create a no_associations_{unix_timestamp}.csv file in the llm_output directory. This is a single column of highlights. Each line is a video that is not associated with either a player or a game.
9. Report your results to me via the completion process.

## Failure Condition

If you are unable to complete any step after 3 attempts, immediately halt the process and consult with the user on how to continue.

## Completion 

1. A markdown file providing a detailed set of instructions to the AI coding agent to execute this workflow as a next step
2. A list of challenges / potential concerns you have based on the users instructions and the current state of the code base of the app. These challenges will be passed to the AI coding agent along with the markdowns to ensure potential bottlenecks and blockers can be navigated appropriately, INCLUDING HOW YOU PLAN TO AVOID REGRESSION BUGS WHEN IMPLEMENTING NEW COMPONENTS AND FUNCTIONALITY


## Appendix: Project File Structure

This outlines the main files and directories in the `ifx-sandbox` project, highlighting those critical for the current Gradio application and noting potentially outdated ones.

```
ifx-sandbox/
├── .env                    # **CRITICAL**: API keys and environment variables (OpenAI, Neo4j, Zep etc.)
├── .env.example            # Example environment file structure.
├── .git/                   # Git repository data.
├── .github/                # GitHub specific files (e.g., workflows - check if used).
├── .gitignore              # Specifies intentionally untracked files that Git should ignore.
├── .gradio/                # Gradio cache/temporary files.
├── components/             # **CRITICAL**: Directory for Gradio UI components.
│   ├── __init__.py
│   ├── game_recap_component.py # **CRITICAL**: Component for displaying game recaps.
│   ├── player_card_component.py # **CRITICAL**: Component for displaying player cards.
│   └── team_story_component.py  # **CRITICAL**: Component for displaying team news stories.
├── data/
│   └── april_11_multimedia_data_collect/ # Contains various data ingestion scripts.
│       ├── team_news_articles.csv      # **CRITICAL DATA**: Source for team news uploads.
│       ├── team_news_scraper.py        # Script to scrape team news (moved here).
│       ├── get_player_socials.py       # **ARCHIVABLE?**: One-off data collection?
│       ├── player_headshots.py         # **ARCHIVABLE?**: One-off data collection?
│       └── get_youtube_playlist_videos.py # **ARCHIVABLE?**: One-off data collection?
│       └── ... (other potential one-off scripts)
├── docs/
│   ├── requirements.md       # **CRITICAL DOC**: This file (Product/Technical Requirements).
│   └── Phase 1/
│       └── Task 1.2.3 Team Search Implementation.md # **CRITICAL DOC**: Implementation plan/notes for recent task.
│       └── ... (Other phase/task docs - check relevance)
├── tools/
│   ├── __init__.py
│   ├── cypher.py             # **CRITICAL**: Tool for generic Cypher QA.
│   ├── game_recap.py         # **CRITICAL**: Tool logic for game recaps.
│   ├── neo4j_article_uploader.py # Tool to upload team news CSV (depends on data folder).
│   ├── player_search.py      # **CRITICAL**: Tool logic for player search.
│   ├── team_story.py         # **CRITICAL**: Tool logic for team news search.
│   └── vector.py             # **CRITICAL?**: Tool for game summary search (check if used by agent).
├── gradio_app.py           # **CRITICAL**: Main Gradio application entry point and UI definition.
├── gradio_agent.py         # **CRITICAL**: LangChain agent definition, tool integration, response generation.
├── gradio_graph.py         # **CRITICAL**: Neo4j graph connection setup for Gradio.
├── gradio_llm.py           # **CRITICAL**: OpenAI LLM setup for Gradio.
├── gradio_requirements.txt # **OLD?**: Specific Gradio requirements? Check if needed alongside main requirements.txt.
├── gradio_utils.py         # **CRITICAL**: Utility functions for the Gradio app (e.g., session IDs).
├── prompts.py              # **CRITICAL**: System prompts for the agent and LLM chains.
├── requirements.txt        # **CRITICAL**: Main Python package dependencies.
├── README.md               # Main project README (check if up-to-date vs GRADIO_README).
├── __pycache__/            # Python bytecode cache.
└── .DS_Store               # macOS folder metadata.




