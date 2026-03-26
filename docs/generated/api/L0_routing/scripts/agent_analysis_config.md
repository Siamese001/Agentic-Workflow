# API Documentation: agent_analysis_config

**Target Audience**: developers, api_users

# agent_analysis_config API Documentation

**File**: `agent_analysis_config.py`
**Classes**: 1
**Functions**: 4

## Classes

- **AgentAnalysis**

## Functions

- **analyze_file** -> AgentAnalysis | None
- **scan_ssot_folders** -> list[AgentAnalysis]
- **generate_report** -> str
- **needs_hardening** -> bool


## Class: AgentAnalysis

**Description**: Analysis result for a single agent file.

### Methods

#### needs_hardening
**Parameters**: self
**Returns**: bool
**Description**: Check if this agent needs cache-first hardening.



## Function: analyze_file

**Parameters**: file_path
**Returns**: AgentAnalysis | None
**Description**: Analyze a single agent file for cache-first patterns.



## Function: scan_ssot_folders

**Parameters**: project_root
**Returns**: list[AgentAnalysis]
**Description**: Scan all SSOT folders for agents needing hardening.



## Function: generate_report

**Parameters**: results
**Returns**: str
**Description**: Generate a formatted report.



## Function: needs_hardening

**Parameters**: self
**Returns**: bool
**Description**: Check if this agent needs cache-first hardening.



## Usage Examples

### Class Usage

```python
# Using AgentAnalysis
agentanalysis = AgentAnalysis()
agentanalysis.needs_hardening()
```

### Function Usage

```python
# Using analyze_file
result = analyze_file(file_path)
```

```python
# Using scan_ssot_folders
result = scan_ssot_folders(project_root)
```

```python
# Using generate_report
result = generate_report(results)
```



---
**Generated**: 2026-03-26T09:39:02.738952
**Type**: api_reference
**Quality**: comprehensive
