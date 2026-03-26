# API Documentation: write_gateway

**Target Audience**: developers, api_users

# write_gateway API Documentation

**File**: `write_gateway.py`
**Classes**: 3
**Functions**: 30

## Classes

- **WriteSizeCapError** (inherits from RuntimeError)
- **WriteAmplificationError** (inherits from RuntimeError)
- **MutationEntropyError** (inherits from RuntimeError)

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **_check_write_amplification** -> None
- **record_prohibition_hit** -> None
- **get_prohibition_hit_count** -> int
- **_get_repo_root** -> Path
- **_deny_writes_into_source_roots** -> None
- **set_mutation_ledger_path** -> None
- **_append_ledger_entry** -> None
- **write_text** -> str
- **write_bytes** -> str
- **write_json** -> str
- **append_text** -> str
- **open_write** -> str
- **ensure_dir** -> Path
- **remove_file** -> None
- **remove_dir** -> None
- **remove_tree** -> None
- **copy_file** -> str
- **move_path** -> str
- **rename_path** -> Path
- **touch_file** -> Path
- **copy_tree** -> str
- **makedirs** -> str
- **write_json_atomic** -> str
- **init_csv** -> str
- **append_csv_row** -> str
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None


## Class: WriteSizeCapError

**Description**: Raised when proposed write exceeds MAX_WRITE_BYTES.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, path, proposed_bytes, max_bytes
**Returns**: None



## Class: WriteAmplificationError

**Description**: Raised when proposed write exceeds MAX_GROWTH_RATIO.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, path, original_bytes, proposed_bytes, growth_ratio
**Returns**: None



## Class: MutationEntropyError

**Description**: Raised when substitution count exceeds expected maximum.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, path, substitution_count, expected_max
**Returns**: None



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: _check_write_amplification

**Parameters**: path, content, encoding
**Returns**: None
**Description**: Enforce write amplification and size cap guards.

    Raises:
        WriteSizeCapError: If proposed content exceeds MAX_WRITE_BYTES
        WriteAmplificationError: If growth ratio exceeds MAX_GROWTH_RATIO
    



## Function: record_prohibition_hit

**Parameters**: layer, op, path
**Returns**: None
**Description**: Record a mutation prohibition hit; emit warning on second occurrence.

    This is a detection-only signal, not a bypass. It does not change behavior.

    Args:
        layer: Layer identifier (e.g., "L0", "L4", "L6")
        op: Operation name (e.g., "json.dump", "write_text")
        path: Normalized path string
    



## Function: get_prohibition_hit_count

**Parameters**: layer, op, path
**Returns**: int
**Description**: Get the number of prohibition hits for a given key (for testing).



## Function: _get_repo_root

**Returns**: Path
**Description**: Lazily resolve repo root (parent of agentic_core).



## Function: _deny_writes_into_source_roots

**Parameters**: path, verb
**Returns**: None
**Description**: Raise RuntimeError if path is under a tracked source root.

    NOTE: This is a legacy defense-in-depth check. Primary protection is via
    enforce_protected_root() which uses ProtectedRootPolicy (no env vars).
    This function remains active for non-protected source roots.
    



## Function: set_mutation_ledger_path

**Parameters**: ledger_path, trace_id
**Returns**: None
**Description**: Configure mutation ledger output path and trace_id for this run.

    Must be called before any writes to enable ledger recording.
    Per hostile audit Section C3: mutation_ledger.jsonl is mandatory.
    



## Function: _append_ledger_entry

**Parameters**: operation, path, before_hash, after_hash, gateway_approved, result, error
**Returns**: None
**Description**: Append a JSONL entry to the mutation ledger.

    Per hostile audit Section C3: one line per attempted mutation.
    Per .windsurfrules §2.2: Evidence must be deterministic, ASCII-only.
    



## Function: write_text

**Parameters**: path, content, encoding
**Returns**: str
**Description**: Write text content to a file, creating parent dirs as needed.

    Args:
        path: Target file path
        content: Text content to write
        encoding: Text encoding (default: utf-8)
        allow_override: Allow writes to protected roots (audited override)
        substitution_count: Number of substitutions made (for entropy check)
        expected_max_substitutions: Expected maximum substitutions (default: 1)

    Raises:
        WriteSizeCapError: If content exceeds MAX_WRITE_BYTES
        WriteAmplificationError: If growth ratio exceeds MAX_GROWTH_RATIO
        MutationEntropyError: If substitution_count > expected_max_substitutions
    



## Function: write_bytes

**Parameters**: path, data
**Returns**: str
**Description**: Write binary content to a file, creating parent dirs as needed.



## Function: write_json

**Parameters**: path, obj, indent
**Returns**: str
**Description**: Serialize obj as JSON and write to file.



## Function: append_text

**Parameters**: path, content, encoding
**Returns**: str
**Description**: Append text to a file, creating parent dirs as needed.



## Function: open_write

**Parameters**: path, content, encoding
**Returns**: str
**Description**: Open file in write mode and write content.



## Function: ensure_dir

**Parameters**: path
**Returns**: Path
**Description**: Create directory (and parents) if it does not exist.



## Function: remove_file

**Parameters**: path, missing_ok
**Returns**: None
**Description**: Remove a file.



## Function: remove_dir

**Parameters**: path
**Returns**: None
**Description**: Remove an empty directory.



## Function: remove_tree

**Parameters**: path
**Returns**: None
**Description**: Recursively remove a directory tree.



## Function: copy_file

**Parameters**: src, dst
**Returns**: str
**Description**: Copy a file preserving metadata.



## Function: move_path

**Parameters**: src, dst
**Returns**: str
**Description**: Move/rename a file or directory.



## Function: rename_path

**Parameters**: src, dst
**Returns**: Path
**Description**: Rename a file or directory.



## Function: touch_file

**Parameters**: path
**Returns**: Path
**Description**: Create an empty file or update its timestamp.



## Function: copy_tree

**Parameters**: src, dst
**Returns**: str
**Description**: Recursively copy a directory tree.



## Function: makedirs

**Parameters**: path, exist_ok
**Returns**: str
**Description**: Create directories (os.makedirs equivalent).



## Function: write_json_atomic

**Parameters**: path, obj, indent
**Returns**: str
**Description**: Serialize obj as JSON via temp file + atomic rename.



## Function: init_csv

**Parameters**: path, header
**Returns**: str
**Description**: Create a CSV file with a header row, creating parent dirs.



## Function: append_csv_row

**Parameters**: path, row
**Returns**: str
**Description**: Append a single row to an existing CSV file.



## Function: __init__

**Parameters**: self, path, proposed_bytes, max_bytes
**Returns**: None


## Function: __init__

**Parameters**: self, path, original_bytes, proposed_bytes, growth_ratio
**Returns**: None


## Function: __init__

**Parameters**: self, path, substitution_count, expected_max
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using WriteSizeCapError
writesizecaperror = WriteSizeCapError()
```

```python
# Using WriteAmplificationError
writeamplificationerror = WriteAmplificationError()
```

```python
# Using MutationEntropyError
mutationentropyerror = MutationEntropyError()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using _check_write_amplification
result = _check_write_amplification(path, content)
```



---
**Generated**: 2026-03-26T09:39:03.937658
**Type**: api_reference
**Quality**: comprehensive
