# Technical Design Document: Gradio UI Enhancements & Card Display Logic

**Version:** 1.0
**Date:** 6/3/2025
**Author:** @ylasso

## 1. Overview

This document outlines a series of enhancements and bug fixes applied to the Gradio-based application. The primary goals of these changes were to improve user experience by enabling seamless multiple submissions, ensuring correct UI state resets, enhancing the reliability of dynamic card displays (for players, games, teams), and introducing new features like session persistence on state clear and specific handling for semi-final game cards.

## 2. Problems Addressed and Solutions Implemented

### 2.1. Consecutive Submissions Requiring "Clear State"

*   **Problem:** Users could not make a second successful submission without first clicking the "Clear State" button. The first submission would work, but subsequent ones would fail to produce the expected output or behavior.
*   **Root Cause:** The `GradioEventHandler` instance, which manages a queue for streaming responses, was initialized globally once. Its internal queue was not reset between submissions. If a previous workflow ended by placing a `None` (end-of-stream marker) in the queue, subsequent submissions would immediately read this `None` and terminate prematurely.
*   **Solution:**
    *   The `GradioEventHandler` instantiation was moved from a global scope within the Gradio Blocks definition to occur locally within the `submit` and `user_query_submit` event handler functions in `api/server_gradio.py`.
    *   This ensures that a fresh `GradioEventHandler` (and thus a new, empty queue) is created for each user submission, preventing interference from previous submission states.

### 2.2. Persistent OTS (One-True-Shot) Content

*   **Problem:** After a player card (or other specialized content in the "OTS" display area) was shown, it would remain visible even after a new, unrelated query was submitted. The OTS area was not resetting to its default landing state.
*   **Root Cause:** The `ots_content` attribute in the `AppState` was not being explicitly reset at the beginning of a new submission.
*   **Solution:**
    *   A constant `INITIAL_OTS_IMAGE_HTML` was defined in `api/server_gradio.py` holding the HTML for the default landing image.
    *   The `AppState` model's `ots_content` field now defaults to this initial image.
    *   Crucially, at the beginning of the `submit_helper` function (called by both submit actions), `state.ots_content` is explicitly reset to `ots_default.format(content=INITIAL_OTS_IMAGE_HTML)`. This ensures the OTS display area starts fresh with the landing image for every new query.

### 2.3. Intermittent Failure to Render UI Cards (OTS Content)

*   **Problem:** Even when a tool was correctly invoked (indicated by a diagnostic message), the corresponding UI card (e.g., player card, game card) would sometimes fail to render, and only a text response would be shown. This behavior was inconsistent.
*   **Root Cause:** The Gradio UI might not have been updated with the new `state.ots_content` if the "ots" token from the `handler.queue` was the last meaningful token before the stream ended, or if no further text tokens followed to trigger another `yield`. The state update with the card HTML might have been "missed."
*   **Solution:**
    *   In the `submit_helper` function in `api/server_gradio.py`, an explicit `yield state, result` was added immediately after an "ots" type token is processed and `state.ots_content` is updated. This forces Gradio to update with the card content as soon as it's ready.
    *   An additional final `yield state, result` was added at the very end of the `submit_helper` function, after the main processing loop, to ensure the absolute final state (including any last-minute `ots_content` or the complete `result`) is always rendered.

### 2.4. Session ID Reset on "Clear State"

*   **Problem:** Clicking the "Clear State" button would reset all application state, including Zep and Freeplay session IDs. This meant subsequent interactions would start entirely new sessions, losing context from the prior interaction if the user only intended to clear the current query and history.
*   **Desired Behavior:** Preserve Zep and Freeplay session IDs when "Clear State" is used, allowing the user to continue the same underlying session while clearing the immediate UI and chat history.
*   **Root Cause:** The `clear_state` function created a completely new `AppState()` instance, which initializes session IDs to empty strings by default.
*   **Solution:**
    *   The `clear_state` function in `api/server_gradio.py` was modified to accept the current `state` (as `current_app_state: AppState`) as an input.
    *   Before creating the `new_state`, it now extracts `existing_zep_session_id` and `existing_freeplay_session_id` from `current_app_state`.
    *   These preserved session IDs are then passed explicitly when instantiating the `new_state = AppState(zep_session_id=..., freeplay_session_id=...)`. Other fields are reset to their defaults.

### 2.5. Game and Team Cards Not Displaying (Player Card Priority Issue)

*   **Problem:** Only player cards were being displayed. Queries that should have resulted in game cards or team cards were not showing these specific UIs.
*   **Root Cause:** Within the `on_tool_end` method of `api/event_handlers/gradio_handler.py`, the logic for displaying player cards was checked first. If a player card was generated, the method would `return` immediately, preventing the subsequent `if/elif` blocks for game cards and team cards from being evaluated.
*   **Solution:**
    *   The conditional logic in `on_tool_end` was restructured to prioritize more specific card types. The new order of checks is:
        1.  (New) Specific check for "Semi-Final" game cards (see section 3.1).
        2.  Generic Game Cards (based on `output[0].metadata.get('type') == 'event'`).
        3.  Team Cards (based on `output[0].metadata.get("show_team_card")`).
        4.  Player Cards (iterating `output` for `doc.metadata.get("show_profile_card")`).
    *   Each primary card-type block still `return`s after successfully queuing its card via `self.ots_box()`, assuming only one card is displayed per tool end.

## 3. New Features

### 3.1. Dedicated Semi-Final Game Card Display

*   **Requirement:** Provide a distinct card display for queries related to "semi-finals," similar to the existing game card.
*   **Implementation:**
    *   An `if` condition was added at the beginning of the `on_tool_end` method in `api/event_handlers/gradio_handler.py`.
    *   This condition specifically checks if `output[0].metadata.get('game_name')` (case-insensitive) contains the string "semi-final".
    *   If true, the existing game card generation logic (`game_card_html` and associated data extraction) is used to render the semi-final information.
    *   This ensures that semi-final games are explicitly identified and displayed using the game card format.
    *   **Dependency:** This relies on the upstream tool providing `game_name` in `output[0].metadata` for semi-final related queries.

## 4. Affected Files

*   `api/server_gradio.py`:
    *   Modified `submit` and `user_query_submit` event handlers.
    *   Modified `submit_helper` function.
    *   Modified `clear_state` function and its Gradio registration.
    *   Added `INITIAL_OTS_IMAGE_HTML` constant and updated `AppState` default for `ots_content`.
*   `api/event_handlers/gradio_handler.py`:
    *   Significantly refactored the `on_tool_end` method's conditional logic for card display.
