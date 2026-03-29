# RCA: Memory MCP ScriptBlock Error

## Problem Statement
Error in logs: `python.exe: ScriptBlock should only be specified as a value of the Command parameter.`

## Root Cause Analysis

### The Real Issue
This is NOT a Memory MCP error. This is a **PowerShell command parsing error** that occurs when:
1. Running Python one-liners with complex quotes through PowerShell
2. The PowerShell interpreter confuses the command's quotes with its own parsing

### Why It Happened
The error manifests when running commands like:
```powershell
python -c "import json; print(json.dumps({'key': 'value'}))"
```

PowerShell's parsing of quotes and special characters in inline Python scripts causes the ScriptBlock parser to trigger incorrectly.

### The Memory MCP Connection
The error appeared in Memory MCP context because:
1. ADG generation scripts run Python subprocess commands
2. When those subprocesses fail, PowerShell outputs this cryptic error
3. The actual root issue was **syntax errors in apps_underwriting_ai** causing import failures

## Resolution

### Immediate Fix
Syntax errors in the following files were fixed:
- `agentic_core/L0_routing/engines/agentic_router.py:418` - unmatched `)`
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py:627` - missing except/finally
- `tools/wave1_antipattern_burndown.py:101` - indentation error
- `tools/wave40_block_fix.py:306` - f-string line continuation
- `tools/adg/shared_modules/*.py` - unicode escape errors (5 files)

### Verification
```bash
python -c "from apps_underwriting_ai import UnderwritingEngine; print('√ Core import successful')"
# Result: √ Core import successful
```

### Hardening Measures
1. **E2E Tests**: Hardened `tests/integration/test_memory_persistence_e2e.py` with real tests
2. **Import Guards**: Add defensive imports to catch future syntax errors early
3. **CI Gate**: Add pre-commit syntax validation for all Python files

## Prevention

### For PowerShell ScriptBlock Errors
1. Use `python script.py` instead of `python -c "..."` for complex logic
2. Escape quotes properly: `"` → `""` or use single quotes for outer wrapper
3. Consider using Python files instead of inline scripts in CI/CD

### For Memory MCP Stability
1. All imports tested on CI before merge
2. Syntax validation runs before ADG generation
3. E2E tests cover full memory persistence lifecycle

## Evidence
- Syntax error report: `syntax_error_report.json` (0 errors remaining)
- ADG regeneration successful: `adg_indexed_03292026_1406.sqlite`
- 7,326 modules scanned, 716,951 edges generated
