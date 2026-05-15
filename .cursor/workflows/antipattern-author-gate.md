---
description: Author-Gate prompt before introducing any new anti-pattern instance (except Exception, os.path.*, string path concat)
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

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

### Step 2 — STOP and emit AUTHOR_GATE_PACKET via canonical pipeline

**Before writing any code**, use the canonical Author-Gate pipeline:

```python
from .cursor.skills.author_gate_packet_builder import emit_packet

# Build AUTHOR_GATE_PACKET for anti-pattern introduction decision
packet = emit_packet.build_author_gate_packet(
    decision_type="anti_pattern_introduction",
    question=f"This change will introduce {n} new {category} instance(s) in {file}. Which approach?",
    options=[
        {
            "id": "A",
            "label": "Narrow exception type — specific exceptions only",
            "description": "Use (ImportError, AttributeError, OSError) instead of broad Exception",
            "tradeoff": "Requires understanding error types; no guardian comment needed",
            "confidence": 0.88,
        },
        {
            "id": "B",
            "label": "Add guardian exemption — explicit allow with justification",
            "description": "Add # guardian: allow-<category> on preceding line",
            "tradeoff": "Counted in ratchet but exempt from blocking; requires specific justification",
            "confidence": 0.75,
        },
        {
            "id": "C",
            "label": "Restructure — avoid the pattern entirely",
            "description": "Refactor code to eliminate the anti-pattern",
            "tradeoff": "May require significant restructuring; ask for guidance if scope unclear",
            "confidence": 0.82,
        },
        {
            "id": "D",
            "label": "Proceed as-is — accept ratchet increase",
            "description": "Accept the anti-pattern into the ratchet baseline",
            "tradeoff": "Technical debt increases; requires ADG_BURNDOWN_INIT after explicit confirmation",
            "confidence": 0.65,
        },
    ],
    recommended_id="A",  # ⭐ Narrow exception is preferred
)

# Emit AUTHOR_GATE_PACKET (canonical path only)
print("AUTHOR_GATE_PACKET: " + json.dumps(packet))

# Present to user via ask_user_question
ask_user_question(
    question=packet["question"],
    options=packet["options"],
    allowMultiple=False,
)
```

**Authority boundary**: AUTHOR_GATE_PACKET reserved for governance-class decisions (anti-pattern introduction). This workflow is AUTHOR_GATE classification per hardened plan review #4.

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

### Trigger conditions (Cursor Agent must invoke this workflow)

- Any new `try/except` block catching `Exception`, `BaseException`, or bare `except`
- Any new `os.path.join`, `os.path.exists`, `os.path.isfile`, etc.
- Any new string concatenation used for path building (`path + "/" + name`)
- Any copy-paste of the ADG behavioral enrichment block pattern into a new file
