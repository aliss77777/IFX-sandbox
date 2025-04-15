# Game Recap Feature Implementation Instructions

## Context
You are an expert at UI/UX design and software front-end development and architecture. You are allowed to not know an answer, be uncertain, or disagree with your task. If any of these occur, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

## Objective
Refactor the game_recap_component.py and underlying code so that the game recap function can be called by the user and displayed as a dynamic UI element – instead of the current build in which it is 'pinned' to the top of the gradio app and appears statically. The user will be able to ask the app a question about a specific game and get the result including a text summary of the result as well as a visual UI component.

## Implementation Steps

### 1. Neo4j Database Update
1. Review the current Neo4j schema for games nodes
2. Create a new subfolder in the 'new_final_april 11' directory for the Neo4j update script
3. Use neo4j_ingestion.py as a reference for previous Neo4j uploads
4. Implement a function to update existing game nodes with new attributes:
   - home_team_logo_url
   - away_team_logo_url
   - game_id
   - highlight_video_url
5. Use game_id as the primary key for updates
6. Add verification steps during the insertion process
7. Request user confirmation in the cloud interface
8. Document the updated schema for future reference

### 2. LangChain Integration
1. Review existing LangChain <-> Neo4j integration functions in agent.py and cypher.py
2. Create a new LangChain function specific to game recap search:
   - Define clear tool description for LangChain recognition
   - Implement text-to-cypher query generation
   - Ensure proper variable passing
3. Implement game-specific search functionality:
   - Use game_id as primary key
   - Retrieve all necessary game attributes
   - Handle edge cases and errors gracefully
4. Develop natural language understanding for game identification:
   - Parse date formats (e.g., "October 11th", "10/11/24")
   - Recognize team names (e.g., "49ers", "San Francisco", "Buccaneers", "Tampa Bay")
   - Handle relative references (e.g., "last game", "first game of the season")
   - Support multiple identification methods (date, opponent, game number)

### 3. Component Refactoring
1. Analyze current game_recap_component.py implementation
2. Identify static elements that need to be made dynamic
3. Create new function structure:
   - Accept game_id as input
   - Return both text summary and UI component
4. Update variable passing mechanism
5. Implement error handling and loading states
6. Add caching mechanism for frequently accessed games
7. Implement progressive loading for media elements

### 4. Gradio App Integration
1. Review current gradio_app.py implementation
2. Identify integration points for dynamic game recap
3. Update app architecture:
   - Remove static game recap component
   - Add dynamic component loading
   - Implement proper state management
4. Add user input handling for game queries
5. Implement response formatting
6. Add feedback mechanism for user queries
7. Implement session persistence for game context

### 5. Testing and Validation
1. Test Neo4j data updates
2. Verify LangChain query generation
3. Test component rendering with various game data
4. Validate error handling
5. Test user interaction flow
6. Specific test cases to include:
   - Queries with different date formats
   - Queries with team name variations
   - Queries with relative time references
   - Queries with missing or incomplete information
   - Edge cases (first/last game of season, special games)
   - Performance testing with multiple concurrent users
   - Error recovery testing

## Data Flow Architecture
1. User submits a natural language query about a specific game
2. LangChain processes the query to identify the game of interest
3. LangChain generates a Cypher query to retrieve game data from Neo4j
4. Neo4j returns the game data including all required attributes
5. LangChain formats the data into a structured response
6. The formatted data is passed to the game recap component
7. The component renders the UI elements with the game data
8. The UI is displayed to the user along with a text summary

## Error Handling Strategy
1. Implement specific error handling for:
   - Game not found in database
   - Ambiguous game identification
   - Missing required attributes
   - Database connection issues
   - Invalid data formats
   - UI rendering failures
2. Provide user-friendly error messages
3. Implement graceful degradation when partial data is available
4. Add logging for debugging purposes
5. Create fallback mechanisms for critical components

## Performance Optimization
1. Implement data caching for frequently accessed games
2. Use lazy loading for media elements
3. Optimize database queries for speed
4. Implement request debouncing for rapid user queries
5. Consider implementing a service worker for offline capabilities
6. Optimize image loading and caching
7. Implement pagination for large result sets

## Failure Conditions
- Halt process if any step fails after 3 attempts
- Document failure point and reason
- Consult with user for guidance
- Do not proceed without resolution

## Success Criteria
- Neo4j database successfully updated with new game attributes
- LangChain correctly identifies and processes game recap queries
- Component successfully refactored to be dynamic
- Gradio app properly integrates dynamic component
- User can query specific games and receive both text and visual responses
- All existing functionality remains intact
- Error handling properly implemented
- Performance meets or exceeds current static implementation
- User can identify games using various natural language patterns

## Notes
- Maintain existing Neo4j node structure
- Preserve all current functionality
- Document all changes for future reference
- Test thoroughly before proceeding to next phase
- Consider performance implications of dynamic loading
- Ensure proper error handling at all levels
- Follow the existing code style and patterns
- Document any assumptions made during implementation 