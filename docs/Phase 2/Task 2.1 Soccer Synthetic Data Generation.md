# Task 2.1 Soccer Synthetic Data Generation

---
## Context

You are an expert at UI/UX design and software front-end development and architecture. You are allowed to NOT know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.

When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.

---

## Objective

*Create comprehensive synthetic data for the Huge Soccer League (HSL) with a **careful, precise, surgical** approach. Ensure data integrity and prepare for Neo4j integration.*

---

## INSTRUCTION STEPS

> **Follow exactly. Do NOT improvise.**

### 1 │ Data Structure Overview

Create a complete synthetic data structure for the Huge Soccer League with the following components:

**League Structure:**
- League name: Huge Soccer League (HSL)
- 24 teams from USA, Canada, Mexico, and Central America (as defined in team_names.md)
- Season schedule with home/away games
- League standings
- League news articles (game recaps)

**Team Data:**
- Team details (name, location, colors, stadium, etc.)
- Team logos (URLs to images)
- Team social media profiles

**Player Data:**
- 25 players per team (600 total players)
- Appropriate position distribution for soccer (GK, DF, MF, FW)
- Player statistics
- Player headshots (URLs to images)
- Player social media profiles

**Game Data:**
- Full season schedule
- Game results and statistics
- Game highlights (URLs to YouTube videos)
- Game relationships to teams and players

**Multimedia Assets:**
- Player headshots
- Team logos
- Game highlights
- Social media links

---

### 2 │ Review Existing CSV Structure & Data Generation Patterns

Analyze the structure of existing CSVs in the `/data/april_11_multimedia_data_collect/new_final_april 11/` folder:

**Key files to review:**
- `roster_april_11.csv` - Player roster structure
- `schedule_with_result_april_11.csv` - Game schedule structure
- `neo4j_ingestion.py` - Database ingestion patterns

Use these as templates for the new data structure, ensuring compatibility with the existing Neo4j ingestion process while adapting for soccer-specific data.

---

### 3 │ Create Data Generation Scripts

1. **Team Generation Script**
   - Create 24 teams based on team_names.md
   - Generate team attributes (colors, stadiums, founding dates, etc.)
   - Create team logo URLs
   - Add team social media profiles

2. **Player Generation Script**
   - Generate 25 players for each team (600 total)
   - Ensure appropriate position distribution:
     - Goalkeepers (GK): 2-3 per team
     - Defenders (DF): 8-9 per team
     - Midfielders (MF): 8-9 per team
     - Forwards (FW): 5-6 per team
   - Create realistic player attributes (height, weight, age, nationality, etc.)
   - Generate player headshot URLs
   - Create player social media profiles

3. **Schedule Generation Script**
   - Create a balanced home/away schedule for all teams
   - Generate at least 23 games per team (each team plays all others at least once)
   - Include match details (date, time, location, stadium)

4. **Game Results & Statistics Generation Script**
   - Generate realistic game scores
   - Create detailed statistics for each game
   - Ensure player statistics aggregate to match game statistics
   - Generate highlight video URLs for games

5. **News Article Generation Script**
   - Create game recap articles
   - Include team and player mentions
   - Generate article timestamps aligned with game schedule

---

### 4 │ Data Files to Create

The following files should be generated in a new folder `/data/hsl_data/`:

**Core Data:**
1. `hsl_teams.csv` - Team information
2. `hsl_players.csv` - Complete player roster with attributes
3. `hsl_schedule.csv` - Season schedule with game results
4. `hsl_player_stats.csv` - Individual player statistics
5. `hsl_game_stats.csv` - Game-level statistics
6. `hsl_news_articles.csv` - Game recap articles

**Multimedia & Relationship Data:**
1. `hsl_team_logos.csv` - Team logo URLs
2. `hsl_player_headshots.csv` - Player headshot URLs
3. `hsl_game_highlights.csv` - Game highlight video URLs
4. `hsl_player_socials.csv` - Player social media links
5. `hsl_team_socials.csv` - Team social media links
6. `hsl_player_team_rel.csv` - Player-to-team relationships
7. `hsl_game_team_rel.csv` - Game-to-team relationships
8. `hsl_player_game_rel.csv` - Player-to-game relationships (for statistics)

---

### 5 │ Data Validation Process

Create Python scripts to validate the generated data:

1. **Schema Validation Script**
   - Verify all required columns exist in each CSV
   - Check data types are correct
   - Validate no missing values in required fields

2. **Relational Integrity Script**
   - Ensure team IDs in player data match existing teams
   - Verify game IDs in statistics match schedule
   - Confirm player IDs in statistics match roster

3. **Statistical Consistency Script**
   - Verify player statistics sum to match game statistics
   - Ensure game results in schedule match statistics
   - Validate team win/loss records match game results

4. **Completeness Check Script**
   - Verify all teams have the required number of players
   - Ensure all games have statistics and highlights
   - Confirm all players have complete profiles

---

### 6 │ Neo4j Integration Test

Develop a test script to verify data can be properly ingested into Neo4j:

1. Create a modified version of the existing `neo4j_ingestion.py` script that works with the new data structure
2. Test the script on a sample of the generated data
3. Verify relationship creation between entities
4. Ensure querying capabilities work as expected

---

### 7 │ Migration Strategy

**Recommended Approach: New Repository and HF Space**

Given the sweeping changes required to support a completely different sport with different data structures:

1. **Create a new repository**
   - Fork the existing repository as a starting point
   - Adapt components for soccer data
   - Update agent functions for HSL context
   - Modify UI/UX elements for soccer presentation

2. **Develop in parallel**
   - Keep the NFL version operational while developing the HSL version
   - Reuse core architecture components but adapt for soccer data
   - Test thoroughly before deployment

3. **Deploy to new HF space**
   - Create new deployment to avoid disrupting the existing application
   - Update configuration for the new data sources
   - Ensure proper database connection

4. **Documentation**
   - Create clear documentation for the HSL version
   - Maintain separate documentation for each version
   - Create cross-reference guides for developers working on both

---

## Failure Condition

> **If any step fails 3×, STOP and consult the user**.

---

## Completion Deliverables

1. **Markdown file** (this document) titled **"Task 2.1 Soccer Synthetic Data Generation"**.
2. **List of Challenges / Potential Concerns** (see below).

---

## List of Challenges / Potential Concerns

1. **Data Volume Management**
   - With 600 players and hundreds of games, data generation and processing will be computationally intensive
   - Database performance may be impacted if data is not properly optimized
   - **Mitigation**: Implement batch processing for data generation and database ingestion

2. **Realistic Statistics Generation**
   - Creating statistically realistic soccer data is complex (goals, assists, etc.)
   - Player performance should correlate with team performance
   - **Mitigation**: Research soccer statistics distributions and implement weighted random generation based on position and player attributes

3. **Media Asset Management**
   - Need placeholder URLs for hundreds of player images and videos
   - Must ensure URLs are valid for testing
   - **Mitigation**: Create a structured naming system for placeholder URLs that follows a consistent pattern

4. **Relationship Integrity**
   - Complex relationships between players, teams, games and statistics
   - Must ensure bidirectional consistency (e.g., player stats sum to team stats)
   - **Mitigation**: Implement comprehensive validation checks before database ingestion

5. **Agent Function Updates**
   - All agent functions must be updated for soccer context
   - Changes must preserve existing patterns while adapting to new sport
   - **Mitigation**: Create a comprehensive function update plan with test cases

6. **UI/UX Adaptations**
   - UI components designed for NFL may not be appropriate for soccer
   - Soccer-specific visualizations needed (field positions, formations, etc.)
   - **Mitigation**: Review UI mockups with stakeholders before implementation

7. **Migration Risks**
   - Potential for data inconsistencies during migration
   - Risk of breaking existing code patterns
   - **Mitigation**: Develop in a separate branch/repo and use comprehensive testing before merging

8. **Regression Prevention**
   - Soccer implementation should not break NFL implementation
   - Common components must work for both sports
   - **Mitigation**: Create a test suite that verifies both implementations

9. **Documentation Overhead**
   - Need to maintain documentation for two different sport implementations
   - **Mitigation**: Create clear documentation templates and use consistent patterns

10. **Timeline Management**
    - Comprehensive data generation is time-consuming
    - Integration testing adds additional time
    - **Mitigation**: Focus on core data first, then progressively enhance

---

## Test Plan

To ensure data integrity before Neo4j ingestion, the following tests should be performed:

1. **Column Header Validation**
   - Verify all CSV files have required columns
   - Check for consistent naming conventions
   - Test for typos or case inconsistencies

2. **Data Type Validation**
   - Verify numeric fields contain valid numbers
   - Ensure date fields have consistent format
   - Check that IDs follow the expected format

3. **Foreign Key Testing**
   - Verify all player IDs exist in the master player list
   - Ensure all team IDs exist in the team list
   - Confirm all game IDs exist in the schedule

4. **Cardinality Testing**
   - Verify each team has exactly 25 players
   - Ensure each game has exactly 2 teams
   - Confirm each player has statistics for games they participated in

5. **Statistical Consistency**
   - Verify player statistics sum to team statistics
   - Ensure game scores match player goals
   - Check that team standings match game results

6. **URL Validation**
   - Test sample URLs for images and videos
   - Verify URL formats are consistent
   - Ensure no duplicate URLs exist

7. **Duplicate Detection**
   - Check for duplicate player IDs
   - Verify no duplicate game IDs
   - Ensure no duplicate team IDs

8. **Null Value Handling**
   - Identify required fields that cannot be null
   - Verify optional fields are handled correctly
   - Check for unexpected null values

9. **Edge Case Testing**
   - Test with minimum/maximum value ranges
   - Verify handling of tie games
   - Check for player transfers between teams

10. **Integration Testing**
    - Test data loading into Neo4j
    - Verify graph relationships
    - Test sample queries against the database 