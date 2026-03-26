# API Documentation: context_session_manager_enforcer

**Target Audience**: developers, api_users

# context_session_manager_enforcer API Documentation

**File**: `context_session_manager_enforcer.py`
**Classes**: 4
**Functions**: 24

## Classes

- **RiskLevel** (inherits from Enum)
- **AttentionState**
- **ContextSession**
- **ContextSessionManager**

## Functions

- **get_session_manager** -> ContextSessionManager
- **get_current_session** -> ContextSession | None
- **classify_risk** -> RiskLevel
- **get** -> Any
- **set** -> None
- **delete** -> None
- **add_focus_file** -> None
- **add_focus_agent** -> None
- **add_priority_violation** -> None
- **escalate_risk** -> None
- **get_history** -> list[dict[str, Any]]
- **to_dict** -> dict[str, Any]
- **from_dict** -> 'ContextSession'
- **__new__**
- **_init**
- **current_session** -> ContextSession | None
- **current_session** -> None
- **create_session** -> ContextSession
- **get_session** -> ContextSession | None
- **end_session** -> None
- **session_scope**
- **get_or_create_session** -> ContextSession
- **get_all_sessions** -> dict[str, ContextSession]
- **cleanup_expired** -> int


## Class: RiskLevel

**Description**: Risk classification per V10 Contextual Router.

**Inherits from**: Enum



## Class: AttentionState

**Description**: Attention mechanism state for context window management.



## Class: ContextSession

**Description**: 
    Session context for V10 request tracking and state management.

    Provides:
    - Unique session identification
    - Risk level classification
    - Working memory state
    - Cross-agent context propagation
    

### Methods

#### get
**Parameters**: self, key, default
**Returns**: Any
**Description**: Get value from session state.

#### set
**Parameters**: self, key, value
**Returns**: None
**Description**: Set value in session state with history tracking.

#### delete
**Parameters**: self, key
**Returns**: None
**Description**: Delete key from session state.

#### add_focus_file
**Parameters**: self, file_path
**Returns**: None
**Description**: Add a file to the attention focus set.

#### add_focus_agent
**Parameters**: self, agent_name
**Returns**: None
**Description**: Add an agent to the attention focus set.

#### add_priority_violation
**Parameters**: self, violation_id
**Returns**: None
**Description**: Add a violation to priority queue.

#### escalate_risk
**Parameters**: self, new_level
**Returns**: None
**Description**: Escalate risk level (never decrease).

#### get_history
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get state change history.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Serialize session for propagation.

#### from_dict
**Parameters**: cls, data
**Returns**: 'ContextSession'
**Description**: Deserialize session from dictionary.



## Class: ContextSessionManager

**Description**: 
    Thread-safe session manager for V10 context propagation.

    Implements the Working Memory component from V10:
    - Session creation and lifecycle
    - Thread-local session access
    - Session inheritance for sub-operations
    

### Methods

#### __new__
**Parameters**: cls
**Description**: Singleton pattern for global session management.

#### _init
**Parameters**: self
**Description**: Initialize the session manager.

#### current_session
**Parameters**: self
**Returns**: ContextSession | None
**Description**: Get the current thread's active session.

#### current_session
**Parameters**: self, session
**Returns**: None
**Description**: Set the current thread's active session.

#### create_session
**Parameters**: self, risk_level, parent_session, metadata
**Returns**: ContextSession
**Description**: 
        Create a new context session.

        Args:
            risk_level: Initial risk classification
            parent_session: Optional parent for session inheritance
            metadata: Optional session metadata

        Returns:
            New ContextSession instance
        

#### get_session
**Parameters**: self, session_id
**Returns**: ContextSession | None
**Description**: Get a session by ID.

#### end_session
**Parameters**: self, session_id
**Returns**: None
**Description**: End and cleanup a session.

#### session_scope
**Parameters**: self, risk_level, inherit_parent, metadata
**Description**: 
        Context manager for session lifecycle.

        Usage:
            with session_manager.session_scope(RiskLevel.HIGH) as session:
                # Operations within this session
                session.set("key", "value")

        Args:
            risk_level: Initial risk level
            inherit_parent: Whether to inherit from current session
            metadata: Optional session metadata

        Yields:
            ContextSession for the scope
        

#### get_or_create_session
**Parameters**: self, session_id, risk_level
**Returns**: ContextSession
**Description**: Get existing session or create new one.

#### get_all_sessions
**Parameters**: self
**Returns**: dict[str, ContextSession]
**Description**: Get all active sessions for monitoring.

#### cleanup_expired
**Parameters**: self, max_age_seconds
**Returns**: int
**Description**: Cleanup sessions older than max_age_seconds.



## Function: get_session_manager

**Returns**: ContextSessionManager
**Description**: Get the global session manager instance.



## Function: get_current_session

**Returns**: ContextSession | None
**Description**: Get the current thread's active session.



## Function: classify_risk

**Parameters**: file_count, has_external_touch, cyclomatic_complexity, is_base_agent
**Returns**: RiskLevel
**Description**: 
    Classify risk level per V10 Contextual Router logic.

    Args:
        file_count: Number of files affected
        has_external_touch: Whether operation touches external systems
        cyclomatic_complexity: Code complexity score
        is_base_agent: Whether operation affects base agent files

    Returns:
        Classified RiskLevel
    



## Function: get

**Parameters**: self, key, default
**Returns**: Any
**Description**: Get value from session state.



## Function: set

**Parameters**: self, key, value
**Returns**: None
**Description**: Set value in session state with history tracking.



## Function: delete

**Parameters**: self, key
**Returns**: None
**Description**: Delete key from session state.



## Function: add_focus_file

**Parameters**: self, file_path
**Returns**: None
**Description**: Add a file to the attention focus set.



## Function: add_focus_agent

**Parameters**: self, agent_name
**Returns**: None
**Description**: Add an agent to the attention focus set.



## Function: add_priority_violation

**Parameters**: self, violation_id
**Returns**: None
**Description**: Add a violation to priority queue.



## Function: escalate_risk

**Parameters**: self, new_level
**Returns**: None
**Description**: Escalate risk level (never decrease).



## Function: get_history

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get state change history.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Serialize session for propagation.



## Function: from_dict

**Parameters**: cls, data
**Returns**: 'ContextSession'
**Description**: Deserialize session from dictionary.



## Function: __new__

**Parameters**: cls
**Description**: Singleton pattern for global session management.



## Function: _init

**Parameters**: self
**Description**: Initialize the session manager.



## Function: current_session

**Parameters**: self
**Returns**: ContextSession | None
**Description**: Get the current thread's active session.



## Function: current_session

**Parameters**: self, session
**Returns**: None
**Description**: Set the current thread's active session.



## Function: create_session

**Parameters**: self, risk_level, parent_session, metadata
**Returns**: ContextSession
**Description**: 
        Create a new context session.

        Args:
            risk_level: Initial risk classification
            parent_session: Optional parent for session inheritance
            metadata: Optional session metadata

        Returns:
            New ContextSession instance
        



## Function: get_session

**Parameters**: self, session_id
**Returns**: ContextSession | None
**Description**: Get a session by ID.



## Function: end_session

**Parameters**: self, session_id
**Returns**: None
**Description**: End and cleanup a session.



## Function: session_scope

**Parameters**: self, risk_level, inherit_parent, metadata
**Description**: 
        Context manager for session lifecycle.

        Usage:
            with session_manager.session_scope(RiskLevel.HIGH) as session:
                # Operations within this session
                session.set("key", "value")

        Args:
            risk_level: Initial risk level
            inherit_parent: Whether to inherit from current session
            metadata: Optional session metadata

        Yields:
            ContextSession for the scope
        



## Function: get_or_create_session

**Parameters**: self, session_id, risk_level
**Returns**: ContextSession
**Description**: Get existing session or create new one.



## Function: get_all_sessions

**Parameters**: self
**Returns**: dict[str, ContextSession]
**Description**: Get all active sessions for monitoring.



## Function: cleanup_expired

**Parameters**: self, max_age_seconds
**Returns**: int
**Description**: Cleanup sessions older than max_age_seconds.



## Usage Examples

### Class Usage

```python
# Using RiskLevel
risklevel = RiskLevel()
```

```python
# Using AttentionState
attentionstate = AttentionState()
```

```python
# Using ContextSession
contextsession = ContextSession()
contextsession.get()
contextsession.set()
```

### Function Usage

```python
# Using get_session_manager
result = get_session_manager()
```

```python
# Using get_current_session
result = get_current_session()
```

```python
# Using classify_risk
result = classify_risk(file_count, has_external_touch)
```



---
**Generated**: 2026-03-26T09:39:04.794861
**Type**: api_reference
**Quality**: comprehensive
