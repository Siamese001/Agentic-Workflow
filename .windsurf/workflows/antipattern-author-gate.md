---
description: Author-Gate prompt before introducing any new anti-pattern instance (except Exception, os.path.*, string path concat)
---

> **Cascade workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

## Anti-Pattern Author-Gate Gate

Run this workflow BEFORE making any code change that would introduce:
- A new `except Exception` / `except BaseException` / bare `except:` block
- A new `os.path.*` call or string path concatenation
- Any other pattern detected by `AntiPatternScanner`

### Step 1 — Scan the planned change

// turbo
Run the scanner on the target files to get a before-count:

```
python -c "
from pathlib import Path
from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner
from agentic_core.L5_safety.validators.base_detector_validator import EnforcementLevel
import sys
files = sys.argv[1:]
scanner = AntiPatternScanner(project_root=Path('.'), enforcement_level=EnforcementLevel.WARNING)
report = scanner.scan_changed_files([Path(f) for f in files])
for v in report.all_violations:
    print(f'{v.file_path}:{v.line_number}  [{v.category.value}]  {v.evidence[:80]}')
print(f'Total violations: {len(report.all_violations)}')
" <file1> <file2> ...
```

### Step 2 — STOP and prompt the user

**Before writing any code**, present this prompt to the user:

> This change will introduce N new `<category>` instance(s) in `<file>`.
> **Options:**
> A) Narrow the exception type to `(ImportError, AttributeError, OSError)` — no guardian comment needed
> B) Add `# guardian: allow-<category>` on the preceding line — counted in ratchet but exempt from blocking
> C) Restructure to avoid the pattern entirely
> D) Proceed as-is and accept the ratchet increase
>
> Which approach?

Do NOT proceed with the edit until the user selects an option.

### Step 3 — Apply the chosen approach

- **Option A**: Use specific exception tuple. No guardian comment. Preferred.
- **Option B**: Add guardian comment on the line immediately before the violation. Update ratchet via `ADG_BURNDOWN_INIT=1 python -m pre_commit run adg-burndown-gate` if count legitimately increases.
- **Option C**: Refactor — ask for guidance if scope is unclear.
- **Option D**: Proceed. Run `ADG_BURNDOWN_INIT=1 python -m pre_commit run adg-burndown-gate` to absorb into ratchet only after explicit user confirmation.

### Step 4 — Verify post-edit

// turbo
Re-run scanner on modified files to confirm count matches expectation:

```
python -m pre_commit run --files <modified_files> 2>&1
```

Gate must pass (exit 0) before committing.

### Trigger conditions (Cascade must invoke this workflow)

- Any new `try/except` block catching `Exception`, `BaseException`, or bare `except`
- Any new `os.path.join`, `os.path.exists`, `os.path.isfile`, etc.
- Any new string concatenation used for path building (`path + "/" + name`)
- Any copy-paste of the ADG behavioral enrichment block pattern into a new file
