# API Documentation: secure_tools_impl

**Target Audience**: developers, api_users

# secure_tools_impl API Documentation

**File**: `secure_tools_impl.py`
**Classes**: 1
**Functions**: 8

## Classes

- **SecureToolsImpl**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **__init__**
- **_safe_path** -> Path
- **tool_write_file** -> str
- **tool_read_file** -> str
- **tool_list_files** -> str
- **tool_run_command** -> str


## Class: SecureToolsImpl

**Description**: 
    Secure tool implementations with path validation and command blacklisting.
    

### Methods

#### __init__
**Parameters**: self, work_dir
**Description**: 
        Initialize secure tools.

        Args:
            work_dir (Path): Working directory for sandboxing
        

#### _safe_path
**Parameters**: self, filename
**Returns**: Path
**Description**: 
        Security: Prevents Directory Traversal (e.g. ../../etc/passwd).
        Ensures that any path accessed is strictly within the designated workspace.

        Args:
            filename (str): The filename or path relative to the workspace.

        Returns:
            Path: The resolved, safe absolute path within the workspace.

        Raises:
            ValueError: If the path attempts to escape the workspace directory.
        

#### tool_write_file
**Parameters**: self, filename, content
**Returns**: str
**Description**: 
        Writes content to a file within the workspace.

        Args:
            filename (str): The name of the file to write.
            content (str): The content to write into the file.

        Returns:
            str: A success message.
        

#### tool_read_file
**Parameters**: self, filename
**Returns**: str
**Description**: 
        Reads content from a file within the workspace.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file, or an error message if the file does not exist.
        

#### tool_list_files
**Parameters**: self, subdir
**Returns**: str
**Description**: 
        Lists files and directories within a specified subdirectory of the workspace.

        Args:
            subdir (str): The subdirectory to list files from, relative to the workspace.
                          Defaults to the root of the workspace.

        Returns:
            str: A newline-separated string of file/directory names, or an error message.
        

#### tool_run_command
**Parameters**: self, command
**Returns**: str
**Description**: 
        Executes a shell command within the workspace.
        WARNING: This tool is highly dangerous. In a production environment,
        it MUST be wrapped in a secure, isolated execution environment (e.g., Docker).

        Args:
            command (str): The shell command string to execute.

        Returns:
            str: The stdout of the command if successful, or an error message.

        Raises:
            ValueError: If the command contains blacklisted patterns.
        



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target, action_class_name


## Function: __init__

**Parameters**: self, work_dir
**Description**: 
        Initialize secure tools.

        Args:
            work_dir (Path): Working directory for sandboxing
        



## Function: _safe_path

**Parameters**: self, filename
**Returns**: Path
**Description**: 
        Security: Prevents Directory Traversal (e.g. ../../etc/passwd).
        Ensures that any path accessed is strictly within the designated workspace.

        Args:
            filename (str): The filename or path relative to the workspace.

        Returns:
            Path: The resolved, safe absolute path within the workspace.

        Raises:
            ValueError: If the path attempts to escape the workspace directory.
        



## Function: tool_write_file

**Parameters**: self, filename, content
**Returns**: str
**Description**: 
        Writes content to a file within the workspace.

        Args:
            filename (str): The name of the file to write.
            content (str): The content to write into the file.

        Returns:
            str: A success message.
        



## Function: tool_read_file

**Parameters**: self, filename
**Returns**: str
**Description**: 
        Reads content from a file within the workspace.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file, or an error message if the file does not exist.
        



## Function: tool_list_files

**Parameters**: self, subdir
**Returns**: str
**Description**: 
        Lists files and directories within a specified subdirectory of the workspace.

        Args:
            subdir (str): The subdirectory to list files from, relative to the workspace.
                          Defaults to the root of the workspace.

        Returns:
            str: A newline-separated string of file/directory names, or an error message.
        



## Function: tool_run_command

**Parameters**: self, command
**Returns**: str
**Description**: 
        Executes a shell command within the workspace.
        WARNING: This tool is highly dangerous. In a production environment,
        it MUST be wrapped in a secure, isolated execution environment (e.g., Docker).

        Args:
            command (str): The shell command string to execute.

        Returns:
            str: The stdout of the command if successful, or an error message.

        Raises:
            ValueError: If the command contains blacklisted patterns.
        



## Usage Examples

### Class Usage

```python
# Using SecureToolsImpl
securetoolsimpl = SecureToolsImpl()
securetoolsimpl.tool_write_file()
securetoolsimpl.tool_read_file()
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
# Using __init__
result = __init__(work_dir)
```



---
**Generated**: 2026-03-26T09:39:03.771225
**Type**: api_reference
**Quality**: comprehensive
