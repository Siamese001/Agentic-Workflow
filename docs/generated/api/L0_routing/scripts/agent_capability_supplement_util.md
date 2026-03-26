# API Documentation: agent_capability_supplement_util

**Target Audience**: developers, api_users

# agent_capability_supplement_util API Documentation

**File**: `agent_capability_supplement_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **extract_capabilities_from_source** -> dict
- **generate_markdown_report** -> str
- **analyze_supplementation**


## Function: extract_capabilities_from_source

**Parameters**: source, class_node
**Returns**: dict
**Description**: 
    Extract rich capability metadata from a single agent class.
    Returns dict with:
      - semantic_tags: high-level capabilities (healing, detection, git, etc.)
      - unique_methods: method names not common in live agents
      - patterns: regex-detected specialized operations
    



## Function: generate_markdown_report

**Parameters**: live_cap_counter, dead_cap_detail, unique_to_dead, underrepresented, recommendations
**Returns**: str
**Description**: Generate detailed markdown report.



## Function: analyze_supplementation



## Usage Examples

### Function Usage

```python
# Using extract_capabilities_from_source
result = extract_capabilities_from_source(source, class_node)
```

```python
# Using generate_markdown_report
result = generate_markdown_report(live_cap_counter, dead_cap_detail)
```

```python
# Using analyze_supplementation
result = analyze_supplementation()
```



---
**Generated**: 2026-03-26T09:39:02.744345
**Type**: api_reference
**Quality**: comprehensive
