# API Documentation: deterministic_cleaner_util

**Target Audience**: developers, api_users

# deterministic_cleaner_util API Documentation

**File**: `deterministic_cleaner_util.py`
**Classes**: 2
**Functions**: 15

## Classes

- **DeterministicCleaner**
- **CompliantFileWriter**

## Functions

- **get_deterministic_cleaner** -> DeterministicCleaner
- **get_compliant_writer** -> CompliantFileWriter
- **deterministic_clean** -> tuple[str, bool]
- **write_compliant_file** -> bool
- **__init__**
- **_check_tool** -> bool
- **deterministic_clean** -> tuple[str, bool]
- **_scrub_markdown_artifacts** -> str
- **_apply_isort** -> str
- **_apply_autopep8** -> str
- **_basic_cleanup** -> str
- **__init__**
- **write_compliant_file** -> bool
- **_check_root_hygiene** -> bool
- **_validate_syntax** -> bool


## Class: DeterministicCleaner

**Description**: 
    Applies deterministic formatting and cleaning to code
    before it reaches the LLM for processing.
    

### Methods

#### __init__
**Parameters**: self, enable_isort, enable_autopep8
**Description**: 
        Initialize the deterministic cleaner.

        Args:
            enable_isort: Whether to run isort for import sorting
            enable_autopep8: Whether to run autopep8 for PEP8 formatting
        

#### _check_tool
**Parameters**: self, tool_name
**Returns**: bool
**Description**: Check if a formatting tool is available.

#### deterministic_clean
**Parameters**: self, code, file_path
**Returns**: tuple[str, bool]
**Description**: 
        Apply deterministic cleaning to code.

        Args:
            code: The code to clean
            file_path: Optional file path for context

        Returns:
            Tuple of (cleaned_code, was_modified)
        

#### _scrub_markdown_artifacts
**Parameters**: self, code
**Returns**: str
**Description**: 
        Remove markdown artifacts from LLM responses.

        Args:
            code: Code that may contain markdown artifacts

        Returns:
            Clean Python code
        

#### _apply_isort
**Parameters**: self, code, file_path
**Returns**: str
**Description**: Apply isort to sort imports.

#### _apply_autopep8
**Parameters**: self, code, file_path
**Returns**: str
**Description**: Apply autopep8 for PEP8 formatting.

#### _basic_cleanup
**Parameters**: self, code
**Returns**: str
**Description**: Apply basic cleanup operations.



## Class: CompliantFileWriter

**Description**: 
    Writes files with compliance checks and validation.
    

### Methods

#### __init__
**Parameters**: self, root_dir
**Description**: 
        Initialize the compliant file writer.

        Args:
            root_dir: Root directory for hygiene checks
        

#### write_compliant_file
**Parameters**: self, file_path, content, pre_clean
**Returns**: bool
**Description**: 
        Write a file with compliance checks.

        Args:
            file_path: Path to write the file
            content: Content to write
            pre_clean: Whether to apply deterministic cleaning first

        Returns:
            True if write was successful, False otherwise
        

#### _check_root_hygiene
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file complies with root hygiene.

#### _validate_syntax
**Parameters**: self, content
**Returns**: bool
**Description**: Validate Python syntax using AST.



## Function: get_deterministic_cleaner

**Returns**: DeterministicCleaner
**Description**: Get or create the global deterministic cleaner instance.



## Function: get_compliant_writer

**Parameters**: root_dir
**Returns**: CompliantFileWriter
**Description**: Get or create the global compliant file writer instance.



## Function: deterministic_clean

**Parameters**: code, file_path
**Returns**: tuple[str, bool]
**Description**: 
    Apply deterministic cleaning to code.
    Args:
        code: The code to clean
        file_path: Optional file path for context

    Returns:
        Tuple of (cleaned_code, was_modified)
    



## Function: write_compliant_file

**Parameters**: file_path, content, pre_clean
**Returns**: bool
**Description**: 
    Write a file with compliance checks.

    Args:
        file_path: Path to write the file
        content: Content to write
        pre_clean: Whether to apply deterministic cleaning first

    Returns:
        True if write was successful, False otherwise
    



## Function: __init__

**Parameters**: self, enable_isort, enable_autopep8
**Description**: 
        Initialize the deterministic cleaner.

        Args:
            enable_isort: Whether to run isort for import sorting
            enable_autopep8: Whether to run autopep8 for PEP8 formatting
        



## Function: _check_tool

**Parameters**: self, tool_name
**Returns**: bool
**Description**: Check if a formatting tool is available.



## Function: deterministic_clean

**Parameters**: self, code, file_path
**Returns**: tuple[str, bool]
**Description**: 
        Apply deterministic cleaning to code.

        Args:
            code: The code to clean
            file_path: Optional file path for context

        Returns:
            Tuple of (cleaned_code, was_modified)
        



## Function: _scrub_markdown_artifacts

**Parameters**: self, code
**Returns**: str
**Description**: 
        Remove markdown artifacts from LLM responses.

        Args:
            code: Code that may contain markdown artifacts

        Returns:
            Clean Python code
        



## Function: _apply_isort

**Parameters**: self, code, file_path
**Returns**: str
**Description**: Apply isort to sort imports.



## Function: _apply_autopep8

**Parameters**: self, code, file_path
**Returns**: str
**Description**: Apply autopep8 for PEP8 formatting.



## Function: _basic_cleanup

**Parameters**: self, code
**Returns**: str
**Description**: Apply basic cleanup operations.



## Function: __init__

**Parameters**: self, root_dir
**Description**: 
        Initialize the compliant file writer.

        Args:
            root_dir: Root directory for hygiene checks
        



## Function: write_compliant_file

**Parameters**: self, file_path, content, pre_clean
**Returns**: bool
**Description**: 
        Write a file with compliance checks.

        Args:
            file_path: Path to write the file
            content: Content to write
            pre_clean: Whether to apply deterministic cleaning first

        Returns:
            True if write was successful, False otherwise
        



## Function: _check_root_hygiene

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file complies with root hygiene.



## Function: _validate_syntax

**Parameters**: self, content
**Returns**: bool
**Description**: Validate Python syntax using AST.



## Usage Examples

### Class Usage

```python
# Using DeterministicCleaner
deterministiccleaner = DeterministicCleaner()
deterministiccleaner.deterministic_clean()
```

```python
# Using CompliantFileWriter
compliantfilewriter = CompliantFileWriter()
compliantfilewriter.write_compliant_file()
```

### Function Usage

```python
# Using get_deterministic_cleaner
result = get_deterministic_cleaner()
```

```python
# Using get_compliant_writer
result = get_compliant_writer(root_dir)
```

```python
# Using deterministic_clean
result = deterministic_clean(code, file_path)
```



---
**Generated**: 2026-03-26T09:39:04.057908
**Type**: api_reference
**Quality**: comprehensive
