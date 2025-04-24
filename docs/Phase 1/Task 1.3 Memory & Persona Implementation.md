# Task 1.3 Memory & Persona Implementation

---
## Context

You are an expert at  UI/UX design and software front-end development and architecture.  You are allowed to NOT know an answer. You are allowed to be uncertain. You are allowed to disagree with your task. If any of these things happen, halt your current process and notify the user immediately. You should not hallucinate. If you are unable to remember information, you are allowed to look it up again.

You are not allowed to hallucinate. You may only use data that exists in the files specified. You are not allowed to create new data if it does not exist in those files.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

When writing code, your focus should be on creating new functionality that builds on the existing code base without breaking things that are already working. If you need to rewrite how existing code works in order to develop a new feature, please check your work carefully, and also pause your work and tell me (the human) for review before going ahead. We want to avoid software regression as much as possible.

I WILL REPEAT, WHEN UPDATING EXISTING CODE FILES, PLEASE DO NOT OVERWRITE EXISTING CODE, PLEASE ADD OR MODIFY COMPONENTS TO ALIGN WITH THE NEW FUNCTIONALITY. THIS INCLUDES SMALL DETAILS LIKE FUNCTION ARGUMENTS AND LIBRARY IMPORTS. REGRESSIONS IN THESE AREAS HAVE CAUSED UNNECESSARY DELAYS AND WE WANT TO AVOID THEM GOING FORWARD.

When you need to modify existing code (in accordance with the instruction above), please present your recommendation to the user before taking action, and explain your rationale.

If the data files and code you need to use as inputs to complete your task do not conform to the structure you expected based on the instructions, please pause your work and ask the human for review and guidance on how to proceed.

If you have difficulty finding mission critical updates in the codebase (e.g. .env files, data files) ask the user for help in finding the path and directory.



---

## Objective

*Implement Feature 0 (Persona Selection) with a **careful, precise, surgical** approach.
The user will execute **one step at a time** and confirm each works before proceeding.*

---

## INSTRUCTION STEPS

> **Follow exactly. Do NOT improvise.**  
> Steps 3 & 6 in `z_Task 1.3 Memory & Persona Implementation_Attempt 1 and 2.md` were already completed.

### 1 │ Review Documentation & Code Base

* `gradio_app.py`
* `gradio_agent.py`
* `gradio_utils.py`

---

### 2 │ Simplest Zep Test

1. Build a Python script in the z_utils folder using the code template at <https://help.getzep.com/walkthrough>.
2. Use **either** session‑ID:
   * Casual fan `241b3478c7634492abee9f178b5341cb`
   * Super fan `dedcf5cb0d71475f976f4f66d98d6400`
3. Confirm the script can *retrieve* chat history.

**Status Update:**
✅ Successfully created a simple Zep test script (`z_utils/zep_test.py`) that connects to Zep Cloud.
❗ Initial test showed no chat history was found for either the Casual fan or Super fan session IDs.
✅ Updated the `zep_setup.py` script to:
   - Use the specific session IDs defined in the task (Casual fan: `241b3478c7634492abee9f178b5341cb`, Super fan: `dedcf5cb0d71475f976f4f66d98d6400`)
   - Create conversation histories for both personas based on their knowledge profiles
   - Store these conversations in Zep Cloud with the specified session IDs
   - Save the session IDs to `persona_session_ids.json` for future reference
✅ Fixed an issue with message role_type formatting (changed "human" to "user" for proper Zep compatibility)
✅ Successfully executed the Zep setup script and verified both personas have:
   - Correctly formatted chat histories loaded in Zep Cloud
   - Knowledge profiles associated with their user IDs
   - Ability to retrieve their chat histories through the test script

✅ Testing confirms both session IDs are now working as expected:
   - Casual fan history includes basic team information and player highlights
   - Super fan history contains more detailed strategic information and analysis

**Next Action:**
- Proceed to Step 3 with the Gradio integration using the ZepCloudChatMessageHistory

---

### 3 │ Gradio Integration ― DO‑NO‑HARM Path

1. **Research**
   * <https://python.langchain.com/docs/integrations/memory/zep_memory/>
   * <https://python.langchain.com/docs/integrations/memory/zep_cloud_chat_message_history/>
2. Create a `ZepMemory()` (or `ZepCloudChatMessageHistory`) object.
3. **Hard‑code** one session‑ID first to verify import works inside the agent.
4. Run the app. Ensure chat history loads without breaking existing features.

---

### 4 │ Add Radio Button (Skeleton Only)

* Insert a Gradio **Radio** with options **Casual Fan** / **Super Fan**.
* Initially the button **does nothing**—just proves the UI renders.

---

### 5 │ Wire Radio → Session ID

1. On change, map selection to its fixed session‑ID.
2. Pass that ID into the `ZepMemory()` object.
3. Re‑run app, switch personas, confirm different histories load.

---

### 6 │ Strict Gradio Rule

* **DO NOT** change any other settings or components in the app.
* Changes must be incremental and easily revertible.

---

### 7 │ Documentation Update

* Explain *why* the simple, surgical approach avoided regressions.
* Update project docs to reflect the new persona‑memory workflow.

---

## Failure Condition

> **If any step fails 3×, STOP and consult the user**.

---

## Completion Deliverables

1. **Markdown file** (this document) titled **"Task 1.3 Memory & Persona Implementation"**.
2. **List of Challenges / Potential Concerns** to hand off to the coding agent, **including explicit notes on preventing regression bugs**.

---

## Challenges & Concerns

| # | Risk / Concern | Mitigation |
|---|---------------|-----------|
| 1 | Zep integration may break async flow | Keep Zep calls isolated; wrap in try/except; validate after each call. |
| 2 | Accidentally overwriting existing code | **Only** add small helper functions or wrap logic; no deletions/ rewrites without review. |
| 3 | Radio button race conditions | Disable UI during session‑switch; re‑enable after confirmation. |
| 4 | Regression in existing features | Run smoke tests (player search, game recap, team story) after every change. |
| 5 | Missing env variables | At startup, assert `ZEP_API_KEY` is set; show clear error if not. |
| 6 | Session ID mismatch | Verify that session IDs in code match those actually created in Zep Cloud. |
| 7 | Message history creation | Ensure messages follow proper format for Zep; implement fallbacks if message history retrieval fails. |

---

> **Remember:** *One tiny change → test → commit. Repeat.*

