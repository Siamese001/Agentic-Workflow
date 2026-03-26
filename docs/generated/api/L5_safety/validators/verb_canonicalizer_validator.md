# API Documentation: verb_canonicalizer_validator

**Target Audience**: developers, api_users

# verb_canonicalizer_validator API Documentation

**File**: `verb_canonicalizer_validator.py`
**Classes**: 1
**Functions**: 2

## Classes

- **VerbCanonicalizer**

## Functions

- **canonicalize** -> list[str]
- **check_for_forbidden_verbs** -> list[str]


## Class: VerbCanonicalizer

**Description**: Canonicalize action verbs to approved list.



## Function: canonicalize

**Parameters**: self, text
**Returns**: list[str]
**Description**: Extract and canonicalize verbs from text.



## Function: check_for_forbidden_verbs

**Parameters**: self, text
**Returns**: list[str]
**Description**: Check for forbidden verbs in the text.



## Usage Examples

### Class Usage

```python
# Using VerbCanonicalizer
verbcanonicalizer = VerbCanonicalizer()
```

### Function Usage

```python
# Using canonicalize
result = canonicalize(text)
```

```python
# Using check_for_forbidden_verbs
result = check_for_forbidden_verbs(text)
```



---
**Generated**: 2026-03-26T09:39:05.898866
**Type**: api_reference
**Quality**: comprehensive
