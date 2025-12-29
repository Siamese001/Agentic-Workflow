# AST Validator Refactoring Status

## Objective
Refactor all compliance agents and key validators to use `CanonASTValidator` infrastructure instead of regex or string matching to eliminate false positives (e.g., matching text in comments or `TYPE_CHECKING` blocks).

## Completed Work

### 1. Infrastructure Created ✅

**File:** `agentic_core/runtime/shared_runtime/ast_validator.py`
- Base class `CanonASTValidator` with automatic TYPE_CHECKING suppression
- Exception ledger integration via `is_excepted_from_key()`
- Helper function `parse_and_validate()` for safe execution
- Automatic violation reporting with line numbers and code snippets

**File:** `agentic_core/config/blueprint_sovereign/structure_blueprint.py`
- Added `CANON_KEY_EXCEPTIONS` dict for false positive suppression
- Key 23: Exception for `fetch_client_sovereign.py` with TYPE_CHECKING patterns
- Key 20: Exception for `canon_validator_agentic_v2.py` and `pyproject.toml`

**File:** `agentic_core/runtime/shared_runtime/void_compliance.py`
- Added `is_excepted_from_key()` function (lines 637-672)
- Added `get_ast_safe_imports()` function (lines 675-699)
- Imports `CANON_KEY_EXCEPTIONS` and `fnmatch` for pattern matching

### 2. AST Validators Created ✅

**File:** `agentic_core/L1_cognition/thought_engine/canon_validators_ast.py`

Created 8 AST-based validators:

| Key | Validator Class | Description | Status |
|-----|----------------|-------------|--------|
| 2 | `PrintStatementValidator` | Detects print() statements | ✅ Complete |
| 3 | `DebuggerValidator` | Detects breakpoint() and pdb.set_trace() | ✅ Complete |
| 4 | `EmptyExceptValidator` | Detects empty except blocks | ✅ Complete |
| 5 | `BareExceptValidator` | Detects bare except: statements | ✅ Complete |
| 6 | `EvalExecValidator` | Detects eval() and exec() calls | ✅ Complete |
| 23 | `ExternalHTTPValidator` | Detects forbidden HTTP imports (requests, urllib, httpx) | ✅ Complete |
| 31 | `AsyncBlockingValidator` | Detects blocking calls in async functions | ✅ Complete |
| 42 | `DangerousBuiltinsValidator` | Detects dangerous builtins (compile, __import__, globals) | ✅ Complete |

Helper functions exported:
- `validate_print_statements()`
- `validate_eval_exec()`
- `validate_debugger()`
- `validate_empty_except()`
- `validate_bare_except()`
- `validate_external_http()`
- `validate_async_blocking()`
- `validate_dangerous_builtins()`

### 3. Agents Refactored ✅

**File:** `agentic_core/L1_cognition/thought_engine/canon_agents_quality.py`

`SafetyInspector` class refactored:
- ✅ Key 2: `check_key_02_no_print_statements()` - Now uses `validate_print_statements()`
- ✅ Key 3: `check_key_03_no_debugger_statements()` - Now uses `validate_debugger()`
- ✅ Key 4: `check_key_04_no_empty_except_blocks()` - Now uses `validate_empty_except()`
- ✅ Key 5: `check_key_05_no_bare_except()` - Now uses `validate_bare_except()`
- ✅ Key 6: `check_key_06_no_eval_exec()` - Now uses `validate_eval_exec()`

**Benefits:**
- Automatic TYPE_CHECKING block suppression
- Exception ledger integration (checks `CANON_KEY_EXCEPTIONS`)
- No false positives from comments or docstrings
- Consistent error reporting format

## Remaining Work

### High Priority

1. **ConcurrencyGuardian** (`agentic_core/L2_execution/tool_registry/security.py`)
   - Lines 121-131: Uses regex patterns for livelock detection
   - Lines 127-131: Uses regex patterns for blocking call detection
   - **Action:** Create AST validators for Keys 61, 63, 64

2. **Import Validators** (`agentic_core/runtime/shared_runtime/void_compliance.py`)
   - Lines 174-236: `validate_import_conventions()` uses AST but could integrate with exception ledger
   - Lines 547-603: `check_import_waterfall_violations()` uses regex for import detection
   - **Action:** Refactor to use `ExternalHTTPValidator` and integrate exception checking

3. **Key 23 Integration**
   - Update agents that check for HTTP imports to use `validate_external_http()`
   - Ensure `fetch_client_sovereign.py` exception is working correctly

### Medium Priority

4. **Complexity Validators** (if they exist)
   - Search for Key 12 validators (function/file complexity)
   - Refactor to use AST-based cyclomatic complexity calculation

5. **Pattern Matching Agents** (`canon_agents_pattern.py`)
   - Review for regex-based code validation
   - Refactor to AST where applicable

6. **Additional Security Checks**
   - Key 0: Hardcoded secrets (currently regex-based, may need AST for context)
   - Key 1: TODO/FIXME (comment-based, regex is appropriate)

### Testing & Validation

7. **Test Exception Ledger**
   - Verify `fetch_client_sovereign.py` passes Key 23 validation
   - Verify TYPE_CHECKING blocks are properly ignored
   - Test glob pattern matching for file exceptions

8. **Integration Testing**
   - Run `canon_validator_agentic_v2.py` with new validators
   - Verify no false positives in known-good files
   - Confirm violations are still caught correctly

## Usage Examples

### For Agent Developers

```python
from pathlib import Path
from agentic_core.L1_cognition.thought_engine.canon_validators_ast import validate_print_statements

# In your agent's execute() or validate() method:
violations = []
for file_path in self.ctx.python_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = validate_print_statements(Path(file_path), content)
    for result in results:
        violations.append(f"{file_path}:{result['line']} - {result['msg']}")

return len(violations) == 0, violations
```

### Creating New Validators

```python
from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator

class MyCustomValidator(CanonASTValidator):
    """Key XX: Description of what this validates."""
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Check function definitions."""
        if some_condition(node):
            # Automatically checks exception ledger and TYPE_CHECKING
            self.report("Violation message", node)
        self.generic_visit(node)
```

## Key Benefits

1. **Zero False Positives from Comments/Docstrings**
   - AST parsing ignores comments and string literals
   - Only validates actual executable code

2. **Automatic TYPE_CHECKING Suppression**
   - Base class tracks `if TYPE_CHECKING:` blocks
   - Violations inside these blocks are automatically ignored

3. **Central Exception Management**
   - `CANON_KEY_EXCEPTIONS` in `structure_blueprint.py` is SSOT
   - Supports file-level and line-level exceptions
   - Glob patterns for flexible matching

4. **Consistent Error Reporting**
   - All validators return same format: `{"msg": str, "line": int, "column": int, "code": str}`
   - Easy to integrate with existing reporting systems

5. **Fail-Safe Design**
   - Syntax errors are handled gracefully (deferred to SyntaxHealer)
   - Complex AST errors fail open to avoid crashing validator

## Next Steps

1. Create AST validators for remaining keys (61, 63, 64)
2. Refactor `ConcurrencyGuardian` to use new validators
3. Update import validation in `void_compliance.py`
4. Run full validation suite to verify no regressions
5. Document any new exceptions needed in `CANON_KEY_EXCEPTIONS`

---

**Last Updated:** December 29, 2025
**Status:** Phase 1 Complete (Infrastructure + Keys 2,3,4,5,6,23,31,42)
