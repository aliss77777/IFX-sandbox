# Freeplay Traces Implementation Plan

## Overview

This document outlines the implementation plan for integrating Freeplay Traces into the existing Huge League Soccer application. Traces provide enhanced observability by grouping LLM interactions within a session, allowing us to track input questions, LLM responses, and associated metadata.

## Current Architecture

### Existing Freeplay Integration Points

1. **Session Management** (`api/server_gradio.py`)
   - `AppState.ensure_sessions()` - Creates Freeplay session on first user interaction
   - Session ID preserved across state changes

2. **Prompt Management** (`api/workflows/base.py`)
   - `call_model()` - Retrieves persona-specific prompts via `get_prompt_by_persona()`
   - Uses Freeplay prompt templates (casual_fan_prompt, super_fan_prompt)

3. **Session Recording** (`api/workflows/base.py`)
   - `should_continue()` - Records final LLM responses to Freeplay session
   - Uses `record_session()` method

## Proposed Traces Implementation

### AppState Enhancement

The `AppState` class will be enhanced to store the actual Freeplay session object, allowing direct access to `session.create_trace()` as shown in the original documentation.

### Modified Methods

```python
# api/utils/freeplay_helpers.py - Modified method
def record_session(self, state, end: Optional[float] = time.time(),
                  formatted_prompt: Optional[FormattedPrompt] = None,
                  prompt_vars: Optional[dict] = None,
                  trace_info: Optional[TraceInfo] = None):  # NEW PARAMETER
    # ... existing code ...
    payload = RecordPayload(
        # ... existing fields ...
        trace_info=trace_info  # NEW FIELD
    )
```

## Implementation Flow

### 1. AppState Enhancement
**Location:** `api/server_gradio.py` - `AppState` class

```python
class AppState(BaseModel):
    # ... existing fields ...
    freeplay_session_id: str = ""
    freeplay_session: Optional[Any] = None  # NEW: Store the actual session object
    
    def ensure_sessions(self):
        if not self.zep_session_id:
            self.zep_session_id = ZepClient() \
                .get_or_create_user(self.email, self.first_name, self.last_name) \
                .create_session() \
                .session_id
        if not self.freeplay_session_id:
            freeplay_client = FreeplayClient()
            self.freeplay_session = freeplay_client.create_session()  # Store session object
            self.freeplay_session_id = self.freeplay_session.session_id
```

### 2. User Input & Trace Creation
**Location:** `api/server_gradio.py` - `submit_helper()`

```python
def submit_helper(state, handler, user_query):
    state.ensure_sessions()  # Freeplay session already exists
    
    # Create trace directly on the session object
    trace_info = state.freeplay_session.create_trace(
        input=user_query, # optional metadata not included
    )
    
    # Pass trace_info to workflow
    workflow_bundle, workflow_state = build_workflow_with_state(
        handler=handler,
        zep_session_id=state.zep_session_id,
        freeplay_session_id=state.freeplay_session_id,
        email=state.email,
        first_name=state.first_name,
        last_name=state.last_name,
        persona=state.persona,
        messages=state.history,
        trace_info=trace_info,  # NEW: Pass trace_info to workflow
    )
```

### 3. Workflow State Enhancement
**Location:** `api/workflows/base.py` - `AgentState`

```python
class AgentState(TypedDict):
    # ... existing fields ...
    trace_info: Optional[TraceInfo] = None  # NEW
```

### 4. Workflow Builder Enhancement
**Location:** `api/workflows/base.py` - `build_workflow_with_state()`

```python
def build_workflow_with_state(handler: AsyncCallbackHandler,
                              zep_session_id: Optional[str] = None,
                              freeplay_session_id: Optional[str] = None,
                              email: Optional[str] = None,
                              first_name: Optional[str] = None,
                              last_name: Optional[str] = None,
                              persona: Optional[str] = None,
                              messages: Optional[List[BaseMessage]] = None,
                              trace_info: Optional[TraceInfo] = None) -> Tuple[WorkflowBundle, AgentState]:  # NEW PARAMETER
    """
    Utility to build workflow and initial state in one step.
    """
    bundle = build_workflow(handler)
    state = {
        "zep_session_id": zep_session_id,
        "freeplay_session_id": freeplay_session_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "persona": persona,
        "messages": messages or [],
        "start_time": time.time(),
        "zep_memory": None,
        "trace_info": trace_info,  # NEW: Populate trace_info in AgentState
    }
    return bundle, state
```

### 5. LLM Processing with Trace Association
**Location:** `api/workflows/base.py` - `call_model()`

```python
async def call_model(state: AgentState,
                     handler: AsyncCallbackHandler,
                     zep_client: ZepClient,
                     freeplay_client: FreeplayClient) -> dict:
    
    # ... existing prompt and LLM logic ...
    
    # Record trace output with LLM response
    if state.get("trace_info"):
        final_response = response.content if hasattr(response, 'content') else str(response)
        state["trace_info"].record_output(
            project_id=FREEPLAY_PROJECT_ID,
            output=final_response
        )
    
    return {'messages': [response], 'zep_memory': memory}
```

### 6. Session Recording with Trace
**Location:** `api/workflows/base.py` - `should_continue()`

```python
async def should_continue(state: AgentState,
                          handler: AsyncCallbackHandler,
                          zep_client: ZepClient,
                          freeplay_client: FreeplayClient) -> str:
    # ... existing logic ...
    
    if 'tool_calls' not in last_message.additional_kwargs:
        # Record session with trace association
        freeplay_client.record_session(state, trace_info=state.get("trace_info"))
        return 'end'
    return 'continue'
```

## Data Flow Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │    │  submit_helper   │    │ AppState        │
│                 │    │                  │    │                 │
│ "Tell me about  │───▶│ 1. ensure_sessions│───▶│ freeplay_session│
│  Ryan Martinez" │    │ 2. create_trace() │    │ .create_trace() │
└─────────────────┘    │ 3. pass trace_info│    │                 │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ build_workflow_  │    │   Trace Info    │
                       │ with_state()     │    │                 │
                       │                  │    │ - trace_id      │
                       │ - trace_info     │    │ - input         │
                       │ - user_query     │    │ - metadata      │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AgentState     │
                       │                  │
                       │ - trace_info     │
                       │ - messages       │
                       │ - persona        │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Workflow       │
                       │   Execution      │
                       │                  │
                       │ call_model()     │
                       │ - get_prompt()   │
                       │ - LLM call       │
                       │ - record_output()│
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ should_continue()│
                       │                  │
                       │ record_session() │
                       │ with trace_info  │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Freeplay Session │
                       │ Recording        │
                       │                  │
                       │ - Session ID     │
                       │ - Trace Info     │
                       │ - Input/Output   │
                       └──────────────────┘
```

## Trace Lifecycle

### 1. **Creation Phase**
- **Trigger:** User submits question
- **Location:** `submit_helper()`
- **Action:** Create trace with user input and metadata
- **Output:** `TraceInfo` object with `trace_id`

### 2. **Association Phase**
- **Trigger:** Workflow initialization
- **Location:** `build_workflow_with_state()`
- **Action:** Pass `trace_info` to workflow state
- **Output:** `AgentState` with trace context

### 3. **Processing Phase**
- **Trigger:** LLM interaction
- **Location:** `call_model()`
- **Action:** Record LLM output to trace
- **Output:** Trace with input/output pair

### 4. **Recording Phase**
- **Trigger:** Workflow completion
- **Location:** `should_continue()`
- **Action:** Associate trace with session recording
- **Output:** Complete session with trace linkage

## Benefits

### Enhanced Observability
- **Input/Output Tracking:** Complete visibility of user questions and LLM responses
- **Metadata Association:** Persona, user info, and interaction context
- **Performance Metrics:** Response times, tool usage, and evaluation results

### Debugging & Analysis
- **Trace Isolation:** Individual interactions can be analyzed separately
- **Session Context:** Traces maintain session-level context
- **Evaluation Support:** Built-in support for feedback and evaluation metrics

### Backward Compatibility
- **Optional Implementation:** Traces are opt-in, existing functionality unchanged
- **Graceful Degradation:** System works without traces if disabled
- **Incremental Rollout:** Can be enabled per user or session

## Implementation Phases

### Phase 1: AppState Enhancement
1. Add `freeplay_session` property to `AppState` class
2. Modify `ensure_sessions()` to store session object
3. Test session object storage and retrieval

### Phase 2: Workflow Integration
1. Update `AgentState` to include `trace_info` field
2. Modify `build_workflow_with_state()` to accept `trace_info` parameter
3. Update `call_model()` to record trace outputs
4. Update `should_continue()` to associate traces with sessions

### Phase 3: Server Integration
1. Update `submit_helper()` to create traces using session object
2. Pass `trace_info` through workflow initialization
3. Test complete trace lifecycle

### Phase 4: Session Recording Enhancement
1. Modify `record_session()` to accept `trace_info` parameter
2. Update `RecordPayload` to include trace information
3. Test session recording with trace association

### Phase 5: Testing & Validation
1. Unit tests for trace creation and recording
2. Integration tests for workflow trace integration
3. End-to-end tests for complete trace lifecycle
4. Performance impact assessment

## Risk Mitigation

### High Risk Areas
1. **Session State Management**
   - **Risk:** Breaking existing session flow
   - **Mitigation:** Optional trace parameters, backward compatibility

2. **Workflow State Changes**
   - **Risk:** Breaking existing state structure
   - **Mitigation:** Optional fields with defaults, thorough testing

### Medium Risk Areas
1. **Performance Impact**
   - **Risk:** Slowing down workflow execution
   - **Mitigation:** Lazy trace creation, optional features

2. **Data Consistency**
   - **Risk:** Trace/recording mismatches
   - **Mitigation:** Validation and error handling

## Success Criteria

1. **Functionality:** Traces created and recorded for all user interactions
2. **Performance:** No measurable impact on workflow execution time
3. **Compatibility:** All existing functionality continues to work
4. **Observability:** Complete trace data available in Freeplay dashboard
5. **Reliability:** Graceful handling of trace creation/recording failures

## Next Steps

1. **User Approval:** Review and approve implementation plan
2. **Phase 1 Implementation:** Begin with core infrastructure
3. **Testing Strategy:** Validate each phase before proceeding
4. **Documentation:** Update API documentation with trace features
5. **Monitoring:** Implement trace-specific logging and metrics 