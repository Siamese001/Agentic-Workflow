# API Documentation: handshake_state_machine

**Target Audience**: developers, api_users

# handshake_state_machine API Documentation

**File**: `handshake_state_machine.py`
**Classes**: 3
**Functions**: 15

## Classes

- **HandshakeState** (inherits from Enum)
- **StateTransition**
- **HandshakeStateMachine**

## Functions

- **create_handshake_machine** -> HandshakeStateMachine
- **__init__**
- **current_state** -> HandshakeState
- **transition_history** -> tuple[StateTransition, ...]
- **reset** -> None
- **request_preclear** -> None
- **certify** -> None
- **seal** -> None
- **dispatch** -> None
- **modify_diff** -> None
- **get_sequence_hash** -> str
- **_compute_sequence_hash** -> str
- **_transition_to** -> None
- **__str__** -> str
- **__repr__** -> str


## Class: HandshakeState

**Description**: States in the sequential handshake protocol.

**Inherits from**: Enum



## Class: StateTransition

**Description**: Record of a state transition for audit trail.



## Class: HandshakeStateMachine

**Description**: 
    Deterministic sequential handshake state machine.

    Enforces strict state transitions:
    - Cannot reach SEALED without CERTIFIED
    - MODIFY_DIFF forces CERTIFIED → PRECLEAR_REQUESTED
    - No direct jump INIT → SEALED
    - No dispatch without SEALED
    

### Methods

#### __init__
**Parameters**: self

#### current_state
**Parameters**: self
**Returns**: HandshakeState
**Description**: Get current handshake state.

#### transition_history
**Parameters**: self
**Returns**: tuple[StateTransition, ...]
**Description**: Get immutable copy of transition history.

#### reset
**Parameters**: self
**Returns**: None
**Description**: Reset state machine to INIT state.

#### request_preclear
**Parameters**: self
**Returns**: None
**Description**: 
        Transition to PRECLEAR_REQUESTED state.

        Only allowed from INIT state.
        

#### certify
**Parameters**: self
**Returns**: None
**Description**: 
        Transition to CERTIFIED state.

        Only allowed from PRECLEAR_REQUESTED state.
        

#### seal
**Parameters**: self
**Returns**: None
**Description**: 
        Transition to SEALED state.

        Only allowed from CERTIFIED state.
        

#### dispatch
**Parameters**: self
**Returns**: None
**Description**: 
        Transition to DISPATCHED state.

        Only allowed from SEALED state.
        

#### modify_diff
**Parameters**: self
**Returns**: None
**Description**: 
        Handle MODIFY_DIFF operation.

        Forces CERTIFIED → PRECLEAR_REQUESTED transition.
        Invalidates prior certification.
        

#### get_sequence_hash
**Parameters**: self
**Returns**: str
**Description**: 
        Compute hash of the complete state transition sequence.

        Used for determinism digest calculation.
        

#### _compute_sequence_hash
**Parameters**: self
**Returns**: str
**Description**: Compute SHA256 hash of transition sequence.

#### _transition_to
**Parameters**: self, new_state, reason
**Returns**: None
**Description**: 
        Internal method to perform state transition.

        Records transition in history for audit trail.
        

#### __str__
**Parameters**: self
**Returns**: str
**Description**: String representation of current state.

#### __repr__
**Parameters**: self
**Returns**: str
**Description**: Detailed string representation.



## Function: create_handshake_machine

**Returns**: HandshakeStateMachine
**Description**: Create a new handshake state machine instance.



## Function: __init__

**Parameters**: self


## Function: current_state

**Parameters**: self
**Returns**: HandshakeState
**Description**: Get current handshake state.



## Function: transition_history

**Parameters**: self
**Returns**: tuple[StateTransition, ...]
**Description**: Get immutable copy of transition history.



## Function: reset

**Parameters**: self
**Returns**: None
**Description**: Reset state machine to INIT state.



## Function: request_preclear

**Parameters**: self
**Returns**: None
**Description**: 
        Transition to PRECLEAR_REQUESTED state.

        Only allowed from INIT state.
        



## Function: certify

**Parameters**: self
**Returns**: None
**Description**: 
        Transition to CERTIFIED state.

        Only allowed from PRECLEAR_REQUESTED state.
        



## Function: seal

**Parameters**: self
**Returns**: None
**Description**: 
        Transition to SEALED state.

        Only allowed from CERTIFIED state.
        



## Function: dispatch

**Parameters**: self
**Returns**: None
**Description**: 
        Transition to DISPATCHED state.

        Only allowed from SEALED state.
        



## Function: modify_diff

**Parameters**: self
**Returns**: None
**Description**: 
        Handle MODIFY_DIFF operation.

        Forces CERTIFIED → PRECLEAR_REQUESTED transition.
        Invalidates prior certification.
        



## Function: get_sequence_hash

**Parameters**: self
**Returns**: str
**Description**: 
        Compute hash of the complete state transition sequence.

        Used for determinism digest calculation.
        



## Function: _compute_sequence_hash

**Parameters**: self
**Returns**: str
**Description**: Compute SHA256 hash of transition sequence.



## Function: _transition_to

**Parameters**: self, new_state, reason
**Returns**: None
**Description**: 
        Internal method to perform state transition.

        Records transition in history for audit trail.
        



## Function: __str__

**Parameters**: self
**Returns**: str
**Description**: String representation of current state.



## Function: __repr__

**Parameters**: self
**Returns**: str
**Description**: Detailed string representation.



## Usage Examples

### Class Usage

```python
# Using HandshakeState
handshakestate = HandshakeState()
```

```python
# Using StateTransition
statetransition = StateTransition()
```

```python
# Using HandshakeStateMachine
handshakestatemachine = HandshakeStateMachine()
handshakestatemachine.current_state()
handshakestatemachine.transition_history()
```

### Function Usage

```python
# Using create_handshake_machine
result = create_handshake_machine()
```

```python
# Using __init__
result = __init__()
```

```python
# Using current_state
result = current_state()
```



---
**Generated**: 2026-03-26T09:39:04.169568
**Type**: api_reference
**Quality**: comprehensive
