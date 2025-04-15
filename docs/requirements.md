# IFX Companion – Product & Technical Requirements (WIP)

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

### 3. Game Search
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

| Layer | Tool / Approach | Goal |
|-------|----------------|------|
| Service Layer | pytest unit tests | Validate correct behavior of each MCP service (team_service, player_service, etc.) |
| Graph Queries | Neo4j test container or schema mocks | Ensure Cypher queries return structured data as expected |
| Gradio UI | Manual session testing per persona | Simulate key user journeys across personas |
| Memory System | Mocked Zep client in pytest | Ensure persona selection creates correct memory structure |
| Integration | Persona-based E2E tests (manual) | Confirm chat-to-output loop works as designed for each use case |

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

### Sample CSS (for embedding in Gradio app):

```css
body {
  font-family: 'Open Sans', sans-serif;
  background-color: #111111;
  color: #E6E6E6;
}

h1, h2 {
  font-family: 'Impact', sans-serif;
  color: #AA0000;
}

button {
  background-color: #B3995D;
  color: #111111;
  border-radius: 8px;
  padding: 8px 16px;
  border: none;
}
```

## 8. Component Library – Gradio Components for Reuse

| Component Name | Description | Gradio Element(s) |
|----------------|-------------|-------------------|
| Persona Selector | Three fan-type buttons (novice/intermediate/super fan). | gr.Row, gr.Button |
| Chat Window | Textbox for user query + LLM response. | gr.Textbox, gr.Markdown |
| Team Summary Card | Team logo, summary, record, etc. | gr.Image, gr.Markdown, gr.Row |
| Player Stat Card | Player image, name, key stats. | gr.Column, gr.Image, gr.Text |
| Game Recap Card | Score, highlight clip, key play. | gr.Row, gr.Image or gr.Video |
| Fan Group Finder | Location input + search results. | gr.Textbox, gr.Dataframe or gr.Accordion |

All components:
- Must be responsive
- Use the 49ers-themed CSS above
- Allow easy import from a components/ folder in the codebase

## 9. Open Items / Next Steps

| Topic | Action |
|-------|--------|
| Personas | Finalize attributes for each of the 3 fan levels |
| Graph Schema | Reupload graph schema including links to media |
| Data Ingestion | Download team logo files + download game recaps |
| Component Dev | Build/test each Gradio component independently |
| Deployment | Set up GitHub+HF Spaces config for clean deployment cycle |
| CSS | Embed or reference the custom stylesheet for theme |

## 10. Detailed Work Plan

Based on a review of the existing codebase and requirements, here's a structured implementation plan:

### Phase 1: Foundation (April 14 - 25)

| Task | Description | Dependencies |
|------|-------------|--------------|
| **1.1 Complete data ingestion of team thumbnail images** | Download and integrate team logo files into the database | None |
| **1.1 data extracted on 4.13 ✅** |
| **1.2 Build and test gradio components locally** | Create components using CSV files instead of Neo4j, including multimedia integration | 1.1 |
| **1.2.1 Team Result Search** | Returning queries about the team using a multi-media component | 1.1 |
| **1.2.1 Player Search** | Return queries about the player using a multi-media component | 1.1 |
| **1.2.3 Game Search** | Return queries about a game using a multi-media component  | 1.1 |
| **1.3 Develop memory system and UI integration with Zep** | Implement persona-based memory system with Zep | None |

**Demo 1 Milestone:** April 22

### Phase 2: Core Integration (April 28 - May 9)

| Task | Description | Dependencies |
|------|-------------|--------------|
| **2.1 Rebuild graph with full asset integration** | Develop and test low-latency approach for media assets | 1.1 |
| **2.2 Refactor ALL OF THE SERVICES** | Update services using updated graph and gradio UI integration | 1.2, 2.1 |

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

## 11. Feature Work Log

### Phase 1, Step 1.2: Team Search Feature Implementation

#### Objective
Implement the Team Search feature (Feature 1 from Feature Overview) with focus on game recap display functionality.

#### Prerequisites
- Access to `schedule_with_result_april_11.csv`
- Access to `nfl_team_logos_revised.csv`
- Reference to `game recap layout example.png`
- Gradio app instance
- Neo4j database instance

#### Implementation Steps

1. **CSS Integration ✅**
   - Add required CSS styles to the Gradio app
   - Ensure styles support responsive layout
   - Implement 49ers theme colors from Design System section
   - **Implementation:** CSS styles were embedded directly in the Gradio app as a string variable, ensuring compatibility with both local development and Hugging Face Spaces deployment. The implementation includes comprehensive styling for all UI components with the 49ers theme colors.

2. **Data Requirements Enhancement ✅**
   - Review existing game score & result data
   - Identify home team name and logo source
   - Identify away team name and logo source
   - Document data structure requirements
   - **Implementation:** Analyzed the schedule CSV file and identified that home team names are in the "Home Team" column and away team names are in the "Away Team" column. Logo sources were identified in the "logo_url" column of the team logos CSV file, which provides direct URLs to team logos from ESPN's CDN.

3. **CSV File Update ✅**
   - Open `schedule_with_result_april_11.csv`
   - Add columns for home team logo
   - Add columns for away team logo
   - Merge data from `nfl_team_logos_revised.csv`
   - Validate data integrity
   - Save as new version
   - **Implementation:** Created a Python script to merge the schedule data with team logo URLs. The script maps team names to their corresponding logo URLs and adds two new columns to the schedule CSV: 'home_team_logo_url' and 'away_team_logo_url'. The merged data was saved as 'schedule_with_result_and_logo_urls.csv'.

4. **Static Gradio Component Development 🔁**
   - Create new component file
   - Implement layout matching `game recap layout example.png`:
     - Top row: away team elements
     - Bottom row: home team elements
     - Score display with winning team highlight
     - Video preview box
   - Use static assets for 49ers first game
   - Implement responsive design
   - **Implementation:** Created a reusable game recap component in `components/game_recap_component.py` that displays team logos, names, scores, and highlights the winning team. The component uses the data from the merged CSV file and applies the 49ers theme styling. The component was integrated into the main Gradio app and tested independently. ❌ What Needs Attention: Video player does not display links it shows 'link coming soon'

5. **Component Testing**
   - Add component as first element in Gradio app
   - Test CSV data integration
   - Verify static display
   - Document any display issues

6. **Function-Calling Implementation**
   - Prepare Neo4j merge operations
   - Update graph with new game data
   - Preserve existing nodes
   - Add new attributes
   - Test data integrity

7. **LangChain Integration**
   - Adapt graph search function
   - Implement game-specific search
   - Test attribute retrieval
   - Verify data flow to Gradio component

8. **Final Deployment**
   - Deploy to Gradio
   - Perform final UI checks
   - Verify data accuracy
   - Document any issues

#### Failure Conditions
- Halt process if any step fails after 3 attempts
- Document failure point and reason
- Consult with user for guidance
- Do not proceed without resolution

#### Success Criteria
- Component displays correctly in Gradio
- Data flows accurately from CSV to display
- Graph integration works without data loss
- LangChain search returns correct game data
- UI matches design specifications

#### Notes
- Maintain existing Neo4j node structure
- Preserve all current functionality
- Document all changes for future reference
- Test thoroughly before proceeding to next phase
