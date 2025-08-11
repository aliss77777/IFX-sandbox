# Implementation Plan (NO CODE)

## Scope Summary
This plan outlines the tasks to create a CLI script that designates a team captain. The script will update player data files and trigger a reload of the vector store to reflect the changes.

## Milestones & Gates
- **M1 – Plan Approved:** /plan completed and approved by reviewer.
- **M2 – Minimal Feature Ready:** /implement completes core FRs; tests pass.
- **M3 – Review & Harden:** /test + /review address gaps/NFRs.

## Task List (Checklist)
- [x] T-001: Enhance Player Model for Captaincy
- [x] T-002: Create Captain Designation CLI Script
- [x] T-003: Implement Vector Store Reload
- [x] T-004: Write Tests for Captain Designation

## Task Details
### T-001: Enhance Player Model for Captaincy
- **Objective:** Modify the existing player model to include functions for finding the current captain of a team and for updating a player's captain status.
- **Files (create/modify):** `api/scripts/model_player.py`
- **Depends on:** none
- **Acceptance:** Functions to get a captain by team and to update a player's `is_captain` flag and bio are added to the model.
- **Traceability:** FR-001, FR-002, FR-003

### T-002: Create Captain Designation CLI Script
- **Objective:** Create a new CLI script that takes a team name and player jersey number as arguments and uses the player model to demote the old captain and promote the new one.
- **Files (create/modify):** `api/scripts/set_captain.py`
- **Depends on:** T-001
- **Acceptance:** The script correctly identifies and updates the relevant player JSON files based on CLI arguments. A success message is printed to standard output.
- **Traceability:** FR-001, FR-002, FR-003

### T-003: Implement Vector Store Reload
- **Objective:** Integrate the vector store reload functionality into the captain designation script.
- **Files (create/modify):** `api/scripts/set_captain.py`
- **Depends on:** T-002
- **Acceptance:** The `api/scripts/vectorstore_load.py` script is successfully executed after the player profiles are updated.
- **Traceability:** FR-004

### T-004: Write Tests for Captain Designation
- **Objective:** Create a new test file to verify the entire captain designation workflow.
- **Files (create/modify):** `api/scripts/test_set_captain.py`
- **Depends on:** T-003
- **Acceptance:** Tests pass, verifying that only one captain exists per team, the `is_captain` flag and bio are updated correctly, the old captain is demoted, and the vector store reload is triggered.
- **Traceability:** FR-001, FR-002, FR-003, FR-004

## Requirements Traceability
| Task  | FR/NFR Covered      | Files Touched                       |
|-------|---------------------|-------------------------------------|
| T-001 | FR-001, FR-002, FR-003 | `api/scripts/model_player.py`       |
| T-002 | FR-001, FR-002, FR-003 | `api/scripts/set_captain.py`        |
| T-003 | FR-004              | `api/scripts/set_captain.py`        |
| T-004 | FR-001, FR-002, FR-003, FR-004 | `api/scripts/test_set_captain.py`   |

## Risks / Assumptions / Open Questions
- **Risks:** None identified.
- **Assumptions:** The script will be run from the repository root, ensuring correct relative paths. Assigning a new captain implicitly demotes any existing captain for that team.
- **Open Questions:** The process for initially selecting a captain is out of scope.

## Next Step
Tell the user when this plan is approved, run **/implement** to create/modify the files listed above (no extra files).
