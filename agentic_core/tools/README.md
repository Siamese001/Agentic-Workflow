# Agentic Core Tools - Phase 3: Toolset & Sandbox Shield

## Overview

The **Agentic Core Tools** module provides a secure, type-safe registry for file operations and subprocess execution, designed to integrate seamlessly with Gemini 2.5/3.0 and the AtomicBlackboard system from Phase 2.

This module replaces dangerous direct file I/O with sandboxed operations that prevent:
- Path traversal attacks
- Unauthorized access to critical directories (`.git`, `__pycache__`, `archives`, etc.)
- Livelock conditions from runaway subprocess calls
- Pydantic validation errors ("23 validation errors", "Extra inputs")

## Architecture

```
agentic_core/tools/
├── __init__.py           # Public API exports
├── definitions.py        # Pydantic models for tool arguments
├── filesystem.py         # Sandboxed file operations
├── execution.py          # Timeout-protected subprocess execution
├── registry.py           # FunctionDeclaration generator for Gemini
└── README.md            # This file
```

## Key Features

### 1. Type-Safe Tool Definitions (`definitions.py`)

All tool arguments are defined as Pydantic models, ensuring:
- Automatic validation of inputs
- Clear error messages for invalid arguments
- No "Extra inputs" errors with Gemini 2.5/3.0

**Example:**
```python
from agentic_core.tools import ReadFileArgs, WriteFileArgs

# Type-safe arguments
read_args = ReadFileArgs(path="apps_shared/canon_validator_v2_agentic.py")
write_args = WriteFileArgs(
    path="output/result.txt",
    content="Hello, World!",
    create_dirs=True
)
```

### 2. Sandboxed Filesystem (`filesystem.py`)

All file operations are validated against:
- **Project Root**: Paths must be relative to project root
- **Excluded Directories**: Cannot access `.git`, `__pycache__`, `archives`, `data`, etc.
- **Path Traversal**: Prevents `../../../etc/passwd` style attacks

**Sandbox Decorator:**
```python
from agentic_core.tools import validate_sandbox

# Automatically validates path is within sandbox
resolved_path = validate_sandbox("apps_shared/file.py")  # ✅ OK
resolved_path = validate_sandbox("../../../etc/passwd")  # ❌ SandboxViolationError
resolved_path = validate_sandbox(".git/config")         # ❌ SandboxViolationError
```

### 3. HealingLease Integration

Write operations integrate with the AtomicBlackboard's HealingLease system:

```python
from agentic_core.tools import write_file, WriteFileArgs

# Requires HealingLease verification
write_file(
    WriteFileArgs(path="file.py", content="code"),
    blackboard=blackboard,
    agent_id="healer_agent_001"
)
# ❌ Raises HealingLeaseError if agent doesn't hold lease
```

### 4. Timeout-Protected Execution (`execution.py`)

Subprocess calls are protected against livelocks:

```python
from agentic_core.tools import execute_command, ExecuteCommandArgs

# Max 300s timeout prevents runaway processes
result = execute_command(ExecuteCommandArgs(
    command="pytest",
    args=["tests/"],
    timeout=60  # Max 300s
))
# Returns: (return_code, stdout, stderr)
```

**Allowed Commands:**
- Python: `python`, `python3`
- Linters: `isort`, `autoflake`, `black`, `flake8`, `mypy`
- Testing: `pytest`
- Package management: `pip`

**Blocked Commands:**
- Destructive: `rm`, `del`, `format`, `dd`
- System control: `shutdown`, `reboot`, `halt`

### 5. Gemini FunctionDeclaration Registry (`registry.py`)

Automatically generates `google.genai.types.FunctionDeclaration` from Pydantic models:

```python
from agentic_core.tools import create_tool_registry, get_function_declarations

# Create registry
registry = create_tool_registry()

# Get FunctionDeclarations for Gemini
declarations = get_function_declarations()

# Use with Gemini
config = types.GenerateContentConfig(
    tools=declarations  # ✅ Type-safe, no validation errors
)
```

## Usage Examples

### Basic File Operations

```python
from agentic_core.tools import (
    read_file, write_file, move_file, list_files,
    ReadFileArgs, WriteFileArgs, MoveFileArgs, ListFilesArgs
)

# Read file
content = read_file(ReadFileArgs(path="apps_shared/file.py"))

# Write file (with HealingLease)
write_file(
    WriteFileArgs(path="output/result.py", content="# Code"),
    blackboard=blackboard,
    agent_id="agent_001"
)

# Move file
move_file(MoveFileArgs(
    source="old.py",
    destination="new.py",
    overwrite=False
))

# List files
files = list_files(ListFilesArgs(
    path="apps_shared",
    pattern="*.py",
    recursive=True
))
```

### Subprocess Execution

```python
from agentic_core.tools import execute_command, ExecuteCommandArgs

# Run linter
returncode, stdout, stderr = execute_command(ExecuteCommandArgs(
    command="isort",
    args=[".", "--skip", ".venv"],
    timeout=60
))

# Run tests
returncode, stdout, stderr = execute_command(ExecuteCommandArgs(
    command="pytest",
    args=["tests/", "-v"],
    timeout=120
))
```

### Tool Registry with Gemini

```python
from agentic_core.tools import create_tool_registry
from google import genai
from google.genai import types

# Create registry
registry = create_tool_registry()

# Get FunctionDeclarations
tools = registry.get_function_declarations()

# Configure Gemini with tools
config = types.GenerateContentConfig(
    temperature=0.2,
    tools=tools  # ✅ No validation errors
)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Fix the file at apps_shared/file.py",
    config=config
)

# Execute tool call
if response.candidates[0].content.parts[0].function_call:
    call = response.candidates[0].content.parts[0].function_call
    result = registry.execute_tool(
        name=call.name,
        args=dict(call.args),
        blackboard=blackboard,
        agent_id="agent_001"
    )
```

## Security Features

### Sandbox Validation

1. **Path Normalization**: All paths resolved to absolute paths
2. **Root Containment**: Paths must be within project root
3. **Directory Exclusion**: Cannot access `.git`, `__pycache__`, `archives`, `data`
4. **Relative Paths Only**: Absolute paths rejected

### HealingLease Verification

1. **Write Protection**: Agents must hold HealingLease to write files
2. **Lease Validation**: Verified against AtomicBlackboard
3. **Atomic Operations**: Writes are atomic with timestamped backups

### Execution Protection

1. **Command Allowlist**: Only approved commands can execute
2. **Timeout Enforcement**: Max 300s per command (configurable)
3. **Working Directory Validation**: CWD must be within sandbox
4. **Dangerous Command Blocking**: `rm`, `format`, `shutdown`, etc. blocked

## Error Handling

### SandboxViolationError
Raised when path violates sandbox constraints:
```python
try:
    validate_sandbox("../../../etc/passwd")
except SandboxViolationError as e:
    print(f"Sandbox violation: {e}")
```

### HealingLeaseError
Raised when agent doesn't hold HealingLease:
```python
try:
    write_file(args, blackboard=bb, agent_id="unauthorized")
except HealingLeaseError as e:
    print(f"Lease required: {e}")
```

### ExecutionTimeoutError
Raised when command exceeds timeout:
```python
try:
    execute_command(ExecuteCommandArgs(command="sleep", args=["1000"], timeout=5))
except ExecutionTimeoutError as e:
    print(f"Command timed out: {e}")
```

## Integration with Phase 2

The tools module integrates with the AtomicBlackboard from Phase 2:

```python
from agentic_core.L4_state.atomic_blackboard import AtomicBlackboard
from agentic_core.tools import write_file, WriteFileArgs

# Create blackboard
blackboard = AtomicBlackboard()

# Agent acquires HealingLease
blackboard.acquire_healing_lease("agent_001", "file.py")

# Write file (verified against lease)
write_file(
    WriteFileArgs(path="file.py", content="code"),
    blackboard=blackboard,
    agent_id="agent_001"
)

# Release lease
blackboard.release_healing_lease("agent_001", "file.py")
```

## Testing

Run tests to verify tool functionality:

```bash
# Test sandbox validation
python -m pytest tests/test_tools_sandbox.py

# Test HealingLease integration
python -m pytest tests/test_tools_lease.py

# Test execution protection
python -m pytest tests/test_tools_execution.py
```

## Migration from Monolithic Validator

The tools module replaces direct file I/O in the monolithic canon validator:

**Before:**
```python
# Direct file I/O (unsafe)
with open(file_path, 'w') as f:
    f.write(content)

# Unprotected subprocess
subprocess.run(["isort", "."], timeout=None)  # ❌ No timeout
```

**After:**
```python
# Sandboxed file I/O
write_file(
    WriteFileArgs(path=file_path, content=content),
    blackboard=blackboard,
    agent_id=agent_id
)

# Protected subprocess
execute_command(ExecuteCommandArgs(
    command="isort",
    args=["."],
    timeout=60  # ✅ Timeout protection
))
```

## Future Enhancements

1. **Async Operations**: Add async versions of file operations
2. **Batch Operations**: Support batch file reads/writes
3. **Streaming**: Stream large file contents
4. **Compression**: Built-in compression for large files
5. **Encryption**: Optional file encryption at rest
6. **Audit Logging**: Comprehensive audit trail for all operations

## References

- **Phase 1**: Atomic Blackboard (L4_state/)
- **Phase 2**: HealingLease System
- **Phase 3**: This module (tools/)
- **Gemini Docs**: https://ai.google.dev/gemini-api/docs/function-calling
- **Pydantic Docs**: https://docs.pydantic.dev/
