# API Documentation: verify_mro_util

**Target Audience**: developers, api_users

# verify_mro_util API Documentation

**File**: `verify_mro_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **print_mro**
- **verify_sovereign_base_agent**
- **verify_meta_learning_agent**
- **verify_location_validator_agent**
- **verify_hierarchy_agent**
- **main**


## Function: print_mro

**Parameters**: agent_class, agent_name
**Description**: Print the MRO for an agent class.



## Function: verify_sovereign_base_agent

**Description**: Verify SovereignBaseAgent MRO.



## Function: verify_meta_learning_agent

**Description**: Verify MetaLearningAgent MRO (complex case).



## Function: verify_location_validator_agent

**Description**: Verify LocationValidatorAgent MRO.



## Function: verify_hierarchy_agent

**Description**: Verify HierarchyAgent MRO via subprocess.



## Function: main

**Description**: Run MRO verification for multiple agents.



## Usage Examples

### Function Usage

```python
# Using print_mro
result = print_mro(agent_class, agent_name)
```

```python
# Using verify_sovereign_base_agent
result = verify_sovereign_base_agent()
```

```python
# Using verify_meta_learning_agent
result = verify_meta_learning_agent()
```



---
**Generated**: 2026-03-26T09:39:03.312220
**Type**: api_reference
**Quality**: comprehensive
