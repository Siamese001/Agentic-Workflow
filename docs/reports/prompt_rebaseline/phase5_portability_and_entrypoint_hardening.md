# Phase 5 Portability and Entrypoint Hardening Evidence

## Pre-change HEAD
247ee79e7

## Clean Tree Proof
**Before:**
```
git status --porcelain=v1
<clean>
```

**After:**
```
git status --porcelain=v1
M agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md
M agentic_core/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md
M data/manifests/full_data_manifest_20251209.sha256
M tests/architecture/test_prompt_root_boundary.py
A agentic_core/prompt_governance/validation/validate_assembly.py
A agentic_core/prompt_governance/validate_assembly.py
A docs/reports/assessments/prompt-modules/validation/validate_assembly.py
?? docs/reports/prompt_rebaseline/phase5_portability_and_entrypoint_hardening.md
```

## Shim Source Excerpt (Phase 5.2)
**Original shim (imported from docs/reports):**
```python
"""Shim to canonicalize prompt assembly validation entrypoint.

This shim provides the expected path agentic_core/prompt_governance/validate_assembly.py
while delegating to the real validator at docs/reports/assessments/prompt-modules/validation/validate_assembly.py
"""

import importlib.util
import sys
from pathlib import Path

# Import and delegate to the real validator using importlib
def load_real_validator():
    """Load the real validator module using importlib."""
    REAL_VALIDATOR_PATH = (
        Path(__file__).parents[4]
        / "docs"
        / "reports"
        / "assessments"
        / "prompt-modules"
        / "validation"
        / "validate_assembly.py"
    )

    if not REAL_VALIDATOR_PATH.exists():
        return None

    spec = importlib.util.spec_from_file_location("validate_assembly", REAL_VALIDATOR_PATH)
    if spec is None:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_assembly"] = module
    spec.loader.exec_module(module)
    return module

# Try to load the real validator
real_validator = load_real_validator()

if real_validator and hasattr(real_validator, "validate"):
    validate = real_validator.validate
else:
    # Fallback if the real validator is not available
    def validate():
        print("Real validator not found at expected location")
        return 1

def main():
    """Entry point for prompt assembly validation."""
    return validate()

if __name__ == "__main__":
    sys.exit(main())
```

**New shim (canonical import from runtime):**
```python
"""Canonical prompt assembly validation entrypoint.

This module provides the expected entrypoint for prompt assembly validation
with the real validation logic located in the validation subpackage.
"""

from .validation.validate_assembly import validate

__all__ = ["validate"]


def main() -> int:
    """Entry point for prompt assembly validation."""
    return validate()


if __name__ == "__main__":
    import sys
    sys.exit(main())
```

## Git Diff Summary
```
git --no-pager diff --name-status
M       agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md
M       agentic_core/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md
M       data/manifests/full_data_manifest_20251209.sha256
M       tests/architecture/test_prompt_root_boundary.py
A       agentic_core/prompt_governance/validation/validate_assembly.py
A       agentic_core/prompt_governance/validate_assembly.py
A       docs/reports/assessments/prompt-modules/validation/validate_assembly.py
```

## Test Outputs (Phase 5.3)

### Boundary Guard Test (Pure Python Implementation)
```
pytest -q tests/architecture/test_prompt_root_boundary.py
.                                                                                     [100%]
1 passed in 11.10s
```

### Assembly Validation Import
```
python -c "from agentic_core.prompt_governance.validate_assembly import validate; print('validate_symbol_ok')"
validate_symbol_ok
```

## Violations Fixed
1. **agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md**
   - Changed `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md` to `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md`
   - Changed `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md` to `data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md`

2. **data/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md**
   - Changed `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md` to `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md`
   - Changed `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md` to `data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md`

3. **data/manifests/full_data_manifest_20251209.sha256**
   - Removed entire "Prompt Libraries" section referencing non-existent `data/prompt_libraries/` files

## FINAL ASSESSMENT: PASS

✅ **Guard test portability**: Zero external tool dependencies (no rg, no PowerShell)
✅ **Precise exclusions**: Only excludes docs/** and archives/**, everything else is enforcement-bearing
✅ **Canonical entrypoint**: validate_assembly imports from runtime location, not docs/reports
✅ **No sys.path manipulation**: Uses standard Python import structure
✅ **All tests passing**: Boundary guard and import validation pass

## Conclusion
Phase 5 successfully eliminated platform/tooling fragility and stabilized the validate_assembly entrypoint with zero docs/reports dependencies.
