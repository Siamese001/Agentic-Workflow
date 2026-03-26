# API Documentation: verify_intentional_variants_util

**Target Audience**: developers, api_users

# verify_intentional_variants_util API Documentation

**File**: `verify_intentional_variants_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **read_file_content** -> str
- **extract_key_identifiers** -> dict
- **analyze_variant_likelihood** -> dict
- **scan_for_duplicates**
- **main**


## Function: read_file_content

**Parameters**: file_path
**Returns**: str
**Description**: Read file content as string.



## Function: extract_key_identifiers

**Parameters**: content, file_ext
**Returns**: dict
**Description**: Extract key identifiers from file content to determine if it's a variant.



## Function: analyze_variant_likelihood

**Parameters**: file1, file2
**Returns**: dict
**Description**: 
    Analyze if two files with same name are intentional variants or true duplicates.

    Returns:
        dict with 'is_variant', 'confidence', 'reasons'
    



## Function: scan_for_duplicates

**Description**: Scan project for duplicate files.



## Function: main



## Usage Examples

### Function Usage

```python
# Using read_file_content
result = read_file_content(file_path)
```

```python
# Using extract_key_identifiers
result = extract_key_identifiers(content, file_ext)
```

```python
# Using analyze_variant_likelihood
result = analyze_variant_likelihood(file1, file2)
```



---
**Generated**: 2026-03-26T09:39:03.305093
**Type**: api_reference
**Quality**: comprehensive
