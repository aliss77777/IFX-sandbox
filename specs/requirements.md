# Requirements (EARS)

## Functional Requirements
- FR-001: The system **shall** designate exactly one player per team as the captain.
  - Acceptance: A query for captains returns one and only one player for each team.
- FR-002: When a player is designated as captain, their player profile JSON **shall** be updated with a new boolean field `is_captain` set to `true`.
  - Acceptance: The specified player's JSON file in `data/huge-league/players/` contains `"is_captain": true`.
- FR-003: When a player is designated as captain, their player bio **shall** be updated to include the phrase "is the team captain".
  - Acceptance: The `bio` field in the captain's player profile JSON contains the specified text.
- FR-004: When player profiles are updated, the vector store **shall** be re-loaded to reflect the changes.
  - Acceptance: The `vectorstore_load.py` script runs successfully after player profiles are modified.

## Non-Functional Requirements
- None specified.

## Out of Scope
- A user interface for selecting or changing team captains.
- The process or logic for how a captain is initially chosen.

## Open Questions
- Q-001: What is the process for selecting a captain for each team? (For now, one will be chosen at random).
- Q-002: If a new captain is assigned, should the previous captain be automatically un-assigned? (Assumption: Yes).
