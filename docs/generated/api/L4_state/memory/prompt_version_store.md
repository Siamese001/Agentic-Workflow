# API Documentation: prompt_version_store

**Target Audience**: developers, api_users

# prompt_version_store API Documentation

**File**: `prompt_version_store.py`
**Classes**: 1
**Functions**: 5

## Classes

- **PromptVersionStore**

## Functions

- **commit_version** -> str
- **get_s0** -> str
- **get_i0** -> str
- **list_versions** -> list[str]
- **clear** -> None


## Class: PromptVersionStore

**Description**: Immutable versioned storage for S0/I0 prompts.

    - commit_version() returns SHA-256 of content (immutable version ID)
    - Same content → same version ID (deduplication)
    - Versions are write-once; no delete, no overwrite
    

### Methods

#### commit_version
**Parameters**: self, prompt_type, content
**Returns**: str
**Description**: Commit a prompt version and return its SHA-256 version ID.

        Args:
            prompt_type: Either "S0" (SYSTEM) or "I0" (INSTRUCTIONAL)
            content: Prompt text content

        Returns:
            SHA-256 hex digest as version ID

        Raises:
            ValueError: If prompt_type is not "S0" or "I0"
        

#### get_s0
**Parameters**: self, version
**Returns**: str
**Description**: Retrieve S0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        

#### get_i0
**Parameters**: self, version
**Returns**: str
**Description**: Retrieve I0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        

#### list_versions
**Parameters**: self
**Returns**: list[str]
**Description**: Return all stored version IDs.

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear all stored versions. For tests only.



## Function: commit_version

**Parameters**: self, prompt_type, content
**Returns**: str
**Description**: Commit a prompt version and return its SHA-256 version ID.

        Args:
            prompt_type: Either "S0" (SYSTEM) or "I0" (INSTRUCTIONAL)
            content: Prompt text content

        Returns:
            SHA-256 hex digest as version ID

        Raises:
            ValueError: If prompt_type is not "S0" or "I0"
        



## Function: get_s0

**Parameters**: self, version
**Returns**: str
**Description**: Retrieve S0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        



## Function: get_i0

**Parameters**: self, version
**Returns**: str
**Description**: Retrieve I0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        



## Function: list_versions

**Parameters**: self
**Returns**: list[str]
**Description**: Return all stored version IDs.



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear all stored versions. For tests only.



## Usage Examples

### Class Usage

```python
# Using PromptVersionStore
promptversionstore = PromptVersionStore()
promptversionstore.commit_version()
promptversionstore.get_s0()
```

### Function Usage

```python
# Using commit_version
result = commit_version(prompt_type, content)
```

```python
# Using get_s0
result = get_s0(version)
```

```python
# Using get_i0
result = get_i0(version)
```



---
**Generated**: 2026-03-26T09:39:04.579909
**Type**: api_reference
**Quality**: comprehensive
