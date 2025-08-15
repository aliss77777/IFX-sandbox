# Design: Team Captain Designation

## Technical Context
- **Language**: Python
- **Framework**: CLI (Command-Line Interface)
- **Reasoning**: The existing project structure is Python-based, and the requirements do not specify a need for a persistent server or UI, making a simple CLI script the most direct approach.

## Architecture (prose, 1–2 paragraphs)
The solution will be a single Python script executed via a CLI. This script will handle the logic for designating a team captain. It will leverage the existing player data model to find and modify player profiles.

The script will first identify and demote any existing captain for the specified team by setting the `is_captain` flag to `false` and removing the captain text from their bio. It will then promote the newly designated captain by updating their JSON profile with `is_captain: true` and adding the corresponding text to their bio. Finally, after successfully modifying the player profile(s), the script will invoke the existing `api/scripts/vectorstore_load.py` to ensure the changes are reflected in the application's vector store.

## Interface
### CLI example
- **Command:** `python api/scripts/set_captain.py <team_name> <player_jersey_number>`
  - **Args:**
    - `team_name`: The name of the team (e.g., "Everglade_FC").
    - `player_jersey_number`: The jersey number of the player to be made captain.
  - **Output:** A success or failure message to standard output.
  - **Exit codes:** 0 on success, 1 on error (e.g., player not found).

## File Plan
| Path | Purpose | New/Modify |
|------|---------|------------|
| `api/scripts/set_captain.py` | Main script to handle captain designation logic. | New |
| `api/scripts/model_player.py` | To be modified to include functions for finding and updating captain status. | Modify |
| `api/scripts/test_set_captain.py` | Unit and integration tests for the captain designation feature. | New |
| `specs/design.md` | This design document. | New |

## Test Plan (no code)
- **FR-001**: `test_only_one_captain_per_team` → `api/scripts/test_set_captain.py`
- **FR-002**: `test_captain_json_flag_is_set` → `api/scripts/test_set_captain.py`
- **FR-003**: `test_captain_bio_is_updated` → `api/scripts/test_set_captain.py`
- **FR-004**: `test_vector_store_is_reloaded` → `api/scripts/test_set_captain.py` (verify the script is called)
- **Q-002 Assumption**: `test_previous_captain_is_demoted` → `api/scripts/test_set_captain.py`

## Decisions
- D1: A CLI script is the chosen interface. This avoids the overhead of a web server and aligns with the existing script-based tooling in the project. It directly addresses the requirements without adding unnecessary complexity.

## Assumptions
- A1: The script will be run from the root of the repository, allowing predictable relative pathing to player data and other scripts.
- A2: As per Q-002, if a team already has a captain, assigning a new captain will automatically demote the old one. The script will handle this transfer of captaincy.

## Open Questions
- Q-001: The initial selection of a captain is out of scope. This script assumes a user has already decided which player to designate.

## Requirements Traceability
| Requirement | Component/File | Test idea |
|------------|-----------------|-----------|
| FR-001 | `api/scripts/set_captain.py`, `api/scripts/model_player.py` | `test_only_one_captain_per_team` |
| FR-002 | `api/scripts/set_captain.py`, `api/scripts/model_player.py` | `test_captain_json_flag_is_set` |
| FR-003 | `api/scripts/set_captain.py`, `api/scripts/model_player.py` | `test_captain_bio_is_updated` |
| FR-004 | `api/scripts/set_captain.py` | `test_vector_store_is_reloaded` |
