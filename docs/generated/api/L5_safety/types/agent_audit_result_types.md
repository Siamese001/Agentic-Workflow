# API Documentation: agent_audit_result_types

**Target Audience**: developers, api_users

# agent_audit_result_types API Documentation

**File**: `agent_audit_result_types.py`
**Classes**: 1
**Functions**: 3

## Classes

- **AgentAuditResult**

## Functions

- **audit_agent_file** -> list[AgentAuditResult]
- **main**
- **verdict** -> str


## Class: AgentAuditResult

**Description**: Audit result for a single agent.

### Methods

#### verdict
**Parameters**: self
**Returns**: str
**Description**: Determine agent status.



## Function: audit_agent_file

**Parameters**: py_file, agentic_core
**Returns**: list[AgentAuditResult]
**Description**: Audit a single Python file for healer agents.



## Function: main

**Description**: Run the global healing capability audit.



## Function: verdict

**Parameters**: self
**Returns**: str
**Description**: Determine agent status.



## Usage Examples

### Class Usage

```python
# Using AgentAuditResult
agentauditresult = AgentAuditResult()
agentauditresult.verdict()
```

### Function Usage

```python
# Using audit_agent_file
result = audit_agent_file(py_file, agentic_core)
```

```python
# Using main
result = main()
```

```python
# Using verdict
result = verdict()
```



---
**Generated**: 2026-03-26T09:39:05.490849
**Type**: api_reference
**Quality**: comprehensive
