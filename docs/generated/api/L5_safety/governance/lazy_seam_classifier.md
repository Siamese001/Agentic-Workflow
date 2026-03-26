# API Documentation: lazy_seam_classifier

**Target Audience**: developers, api_users

# lazy_seam_classifier API Documentation

**File**: `lazy_seam_classifier.py`
**Classes**: 1
**Functions**: 7

## Classes

- **LazySeamClassifier**

## Functions

- **main**
- **__init__**
- **_load_allowlist** -> dict[str, Any]
- **_classify_seam** -> tuple[str, str]
- **classify_all_seams** -> None
- **save_allowlist** -> None
- **print_summary** -> None


## Class: LazySeamClassifier

**Description**: Classifies lazy seams into reason categories.

### Methods

#### __init__
**Parameters**: self, allowlist_path

#### _load_allowlist
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load allowlist from file.

#### _classify_seam
**Parameters**: self, seam
**Returns**: tuple[str, str]
**Description**: Classify a single seam and return (reason_code, justification).

#### classify_all_seams
**Parameters**: self
**Returns**: None
**Description**: Classify all seams in the allowlist.

#### save_allowlist
**Parameters**: self
**Returns**: None
**Description**: Save updated allowlist to file.

#### print_summary
**Parameters**: self
**Returns**: None
**Description**: Print classification summary.



## Function: main

**Description**: Main execution.



## Function: __init__

**Parameters**: self, allowlist_path


## Function: _load_allowlist

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load allowlist from file.



## Function: _classify_seam

**Parameters**: self, seam
**Returns**: tuple[str, str]
**Description**: Classify a single seam and return (reason_code, justification).



## Function: classify_all_seams

**Parameters**: self
**Returns**: None
**Description**: Classify all seams in the allowlist.



## Function: save_allowlist

**Parameters**: self
**Returns**: None
**Description**: Save updated allowlist to file.



## Function: print_summary

**Parameters**: self
**Returns**: None
**Description**: Print classification summary.



## Usage Examples

### Class Usage

```python
# Using LazySeamClassifier
lazyseamclassifier = LazySeamClassifier()
lazyseamclassifier.classify_all_seams()
lazyseamclassifier.save_allowlist()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(allowlist_path)
```

```python
# Using _load_allowlist
result = _load_allowlist()
```



---
**Generated**: 2026-03-26T09:39:04.999258
**Type**: api_reference
**Quality**: comprehensive
