# Global Constraints - Canon Validator

## Zero-Tolerance Deletion Rule

- **NEVER** truncate files or use placeholders like `# ... rest of code` or `# existing code`
- **NEVER** delete more than 10% of lines without structural reason
- Every mutation must be a COMPLETE, functional file
- Preserve ALL sections exactly as-is unless directly fixing the violation
- Output must contain the FULL file with ALL original lines preserved

## Prohibited Modules (Hard-Coded Blacklist)

These modules **DO NOT EXIST** in this codebase. They are **HALLUCINATIONS**:

- **BANNED**: `import base`
- **BANNED**: `import context`
- **BANNED**: `import L3_orchestration`
- **BANNED**: `import conversational_repair`
- **BANNED**: `from base import ...`
- **BANNED**: `from context import ...`
- **BANNED**: `from L3_orchestration import ...`
- **BANNED**: `from conversational_repair import ...`

## Allowed Imports Only

- **ONLY** use Python standard library: `os`, `sys`, `pathlib`, `typing`, `dataclasses`, `asyncio`, etc.
- **ONLY** use fully qualified paths: `from agentic_workflow.runtime.shared import ...`
- **VERIFY** all imports exist before using them

## Elite Engineer Rules

1. **NEVER** hallucinate imports - verify all imports are real
2. **NEVER** delete logic, comments, or docstrings
3. **NEVER** use tools or function calls - return code as TEXT only
4. Fix the specific violation ONLY - surgical precision
5. Return ONLY valid Python code. No markdown blocks.

## Code Integrity Rules

- **DO NOT** generate imports for modules that don't exist
- **DO NOT** use relative imports without verifying the module structure
- **DO NOT** assume internal modules exist without checking
- **DO NOT** create circular dependencies
- **DO NOT** modify code outside the violation scope

## Structural Integrity

- Preserve all class definitions
- Preserve all function signatures
- Preserve all docstrings and comments
- Preserve all type hints
- Preserve all decorators
- Only modify the specific lines that fix the violation

## Output Format Rules

- Return ONLY valid Python code
- No markdown code blocks (no ```python)
- No explanatory text before or after code
- No comments about what was changed
- Complete, runnable file only
