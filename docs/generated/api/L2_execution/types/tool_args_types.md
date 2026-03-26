# API Documentation: tool_args_types

**Target Audience**: developers, api_users

# tool_args_types API Documentation

**File**: `tool_args_types.py`
**Classes**: 7
**Functions**: 0

## Classes

- **ReadFileArgs** (inherits from BaseModel)
- **WriteFileArgs** (inherits from BaseModel)
- **ListFilesArgs** (inherits from BaseModel)
- **MoveFileArgs** (inherits from BaseModel)
- **DeleteFileArgs** (inherits from BaseModel)
- **CreateDirectoryArgs** (inherits from BaseModel)
- **ExecuteCommandArgs** (inherits from BaseModel)


## Class: ReadFileArgs

**Description**: Arguments for reading a file.

**Inherits from**: BaseModel



## Class: WriteFileArgs

**Description**: Arguments for writing to a file.

**Inherits from**: BaseModel



## Class: ListFilesArgs

**Description**: Arguments for listing files in a directory.

**Inherits from**: BaseModel



## Class: MoveFileArgs

**Description**: Arguments for moving/renaming a file.

**Inherits from**: BaseModel



## Class: DeleteFileArgs

**Description**: Arguments for deleting a file.

**Inherits from**: BaseModel



## Class: CreateDirectoryArgs

**Description**: Arguments for creating a directory.

**Inherits from**: BaseModel



## Class: ExecuteCommandArgs

**Description**: Arguments for executing a shell command.

**Inherits from**: BaseModel



## Usage Examples

### Class Usage

```python
# Using ReadFileArgs
readfileargs = ReadFileArgs()
```

```python
# Using WriteFileArgs
writefileargs = WriteFileArgs()
```

```python
# Using ListFilesArgs
listfilesargs = ListFilesArgs()
```



---
**Generated**: 2026-03-26T09:39:04.012133
**Type**: api_reference
**Quality**: comprehensive
