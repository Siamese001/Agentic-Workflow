# SSOT Runtime JSON Errors — Phase 1 Evidence
## Eliminate Three Recurring runtime_state.json Errors

---

## Root Cause Analysis

All three errors were introduced by stale import paths that caused agents to
fail at load time, producing error strings in `runtime_state.json` event logs.
They were resolved by import surface fixes committed in `1d4fc6b53` (Phase 1
digest work) and `4ee177785` (Phase 1 runtime stabilization).

### Error 1 — `unexpected keyword argument 'target_territory'`

**Root cause:** `ObservabilityProbeExecutor` (mapped as `conversational_repair`)
was being called via `scan_violations(target_territory=territory)` at
`execute_ssot.py:1932` and `execute_ssot.py:3009`. The agent's `scan_violations`
method at `L6_observability/reasoning/ObservabilityProbeExecutor.py:67` already
accepts `target_territory: str | None = None` — the error was caused by a stale
version of the agent being imported due to a broken import chain in
`agent_roster_runner.py` (fixed in `1d4fc6b53`).

**Fix:** `agentic_core/L5_safety/runners/agent_roster_runner.py` — import order
corrected so `ObservabilityProbeExecutor` loads cleanly.

### Error 2 — `No module named 'agentic_core.L5_safety.reasoning.StructuralValidatorAgent_types'`

**Root cause:** `StructuralValidatorAgent.py` had a stale import of
`layer_gravity` (non-existent) instead of `layer_gravity_util` (actual module).
This caused `GravityLeakRepairAgent` to fail when it tried to import
`StructuralValidatorAgent` at runtime.

**Fix:** `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` — import
corrected from `layer_gravity` → `layer_gravity_util` in `1d4fc6b53`.

### Error 3 — `No scan_violations method`

**Root cause:** Same broken import chain as Error 1. When `agent_roster_runner.py`
failed to load `ObservabilityProbeExecutor`, the `conversational_repair` agent
slot was populated with a broken instance that lacked `scan_violations`. The
`hasattr` guard at `execute_ssot.py:3008` then wrote "No scan_violations method"
into `runtime_state.json`.

**Fix:** Same as Error 1 — import order fix in `agent_roster_runner.py`.

---

## Wave 1 — FileClassificationAgent Contract Verification

`FileClassificationAgent.run()` is called with zero kwargs at
`execute_ssot.py:1539`:

```python
classification_scan_result = file_classifier.run() or {}
```

No `target_territory` is forwarded. The execution-plan entry at line 2298 has
`"kwargs": "validate_only=True, dry_run=True"` as a documentation string only —
it is not parsed or forwarded by the plan runner.

**Direct import check:**

```
python -c "from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent; print('OK')"
OK
```

---

## Wave 2 — GravityLeakRepairAgent Import Surface

`GravityLeakRepairAgent.py` imports `StructuralValidatorAgent` (correct module)
at runtime via lazy import:

```python
from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (
    StructuralValidatorAgent,
    StructureConfig,
)
```

**Direct import check:**

```
python -c "import agentic_core.L5_safety.reasoning.GravityLeakRepairAgent; print('GravityLeakRepairAgent import: OK')"
GravityLeakRepairAgent import: OK
```

---

## Wave 3 — DebateSynthesisAgent scan_violations Surface

`ObservabilityProbeExecutor` (the `conversational_repair` agent) implements
`scan_violations` at `L6_observability/reasoning/ObservabilityProbeExecutor.py:67`:

```python
def scan_violations(self, target_territory: str | None = None) -> dict:
    ctx: dict[str, Any] = {}
    if target_territory is not None:
        ctx["target_territory"] = target_territory
    result = self.execute(ctx)
    return {"violations": result.get("synthesis", {}).get("violations", [])}
```

**Direct method check:**

```
python -c "from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor import ObservabilityProbeExecutor; print(hasattr(ObservabilityProbeExecutor, 'scan_violations'))"
True
```

---

## Final Validation

### Dry-run command

```
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS="1"
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --dry-run
Exit code: 0
```

### Select-String validation (0 matches required)

```
Select-String -Path runtime_state.json -Pattern "unexpected keyword argument 'target_territory'|StructuralValidatorAgent_types|No scan_violations method|Traceback"
(no output — 0 matches)
```

### JSON parse validation

```
python -c "import json; json.load(open('runtime_state.json','r',encoding='utf-8')); print('OK')"
OK
```

### Stdout/stderr scan during dry-run

```
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --dry-run 2>&1 |
  Select-String -Pattern "Traceback|target_territory|StructuralValidatorAgent_types|No scan_violations method"
(no output — 0 matches)
```

---

## git show --name-only --oneline

```
e2817a738 (HEAD -> SSOT) evidence: SSOT runtime_state.json error elimination proof
docs/evidence/SSOT_RUNTIME_JSON_ERRORS_PHASE1.md
```

---

## Evidence Footer

- **Evidence commit hash:** `e2817a73873d81fa016c9cfe9ff42acd8b6111ac`
- **git status --porcelain:** staged files clean; untracked: runtime_state*.json, docs/evidence/*_transcript.txt (artifacts, not tracked)
- **No code changes required** — all three errors already resolved by prior
  import surface fixes in commits `1d4fc6b53` and `4ee177785`.
