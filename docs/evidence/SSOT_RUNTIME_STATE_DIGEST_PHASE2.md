# SSOT Runtime State Digest — Phase 2 Evidence
## Deterministic Digest Hardening

---

## Wave 1 — Upstream Ordering Stabilization

### List Field Classification

| Path | Classification | Rationale |
| :--- | :--- | :--- |
| `events` | ORDERED | Event log; insertion sequence is semantic |
| `completed_agents` | ORDERED | Execution timeline |
| `agents_order` | ORDERED | Fixed registry roster |
| `compliance_report.violations` | UNORDERED | Filesystem/scan-order dependent |
| `location_violations` | UNORDERED | Filesystem scan order |
| `location_scan_result.violations` | UNORDERED | Filesystem scan order |
| `hygiene_violations` | UNORDERED | Scan order |
| `gravity_violations` | UNORDERED | Scan order |
| `classification_violations` | UNORDERED | Scan order |
| `conversational_violations` | UNORDERED | Scan order |
| `compliance_report.drift_violations` | UNORDERED | Scan order |

### Stabilization Approach

UNORDERED lists are sorted **inside `runtime_state_digest_view()`** (view copy only, not at source).
Sort keys per list are defined in `_SORT_SPECS` in `runtime_state_digest.py`.

```python
_SORT_SPECS = [
    ("compliance_report.violations", ("type", "file", "message")),
    ("location_violations", ("file", "reason")),
    ("location_scan_result.violations", ("file", "reason")),
    ("hygiene_violations", ("type", "file", "message")),
    ("gravity_violations", ("type", "message")),
    ("classification_violations", ("type", "file", "message")),
    ("conversational_violations", ("type", "file", "message")),
    ("compliance_report.drift_violations", ("type", "file", "message")),
]
```

---

## Wave 2 — Volatile Field Sentinel

### VOLATILE_FIELD_PATTERNS

```python
VOLATILE_FIELD_PATTERNS = [
    "time", "timestamp", "elapsed", "uuid",
    "pid", "host", "nonce", "random", "seed",
]
```

Value-level detection: ISO-8601 datetime strings (`^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}`).

### Sentinel Against Actual runtime_state.json

```
python -c "
import json
from agentic_core.L0_routing.scripts.runtime_state_digest import detect_unexcluded_volatile_fields
state = json.load(open('runtime_state.p2run1.json'))
findings = detect_unexcluded_volatile_fields(state)
print(f'Sentinel findings: {len(findings)}')
"
Sentinel findings: 0
```

**Zero unexcluded volatile fields detected.**

---

## Wave 3 — Digest Schema Contract

### Schema Version

```python
DIGEST_SCHEMA_VERSION: int = 1
```

Persisted in `runtime_state.json` as `runtime_state_digest_schema_version`.
Added to `EXCLUDE_PATHS` so it does not affect its own digest computation.
Injected into the digest view as `_digest_schema_version` so the digest is version-stamped.

### Back-to-Back Dry-Run Proof (Post-Hardening)

```
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS="1"
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --dry-run --domains
Exit code: 0  (run 1)

python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --dry-run --domains
Exit code: 0  (run 2)
```

### Digest Extraction

```
python -c "import json; ..."
Run1 digest: 505d6156324809a06cdc3c194410ebb7e6c946e0b2d88414526c8e2736f8c421
Run2 digest: 505d6156324809a06cdc3c194410ebb7e6c946e0b2d88414526c8e2736f8c421
Match: True
Schema version run1: 1
Schema version run2: 1
```

**Digests match: `505d6156324809a06cdc3c194410ebb7e6c946e0b2d88414526c8e2736f8c421`**

---

## Unit Test Proof (All Waves)

### Command

```
python -m pytest tests/unit/test_runtime_state_digest_phase2.py tests/unit/test_runtime_state_digest.py -q -m unit
```

### Output

```
tests/unit/test_runtime_state_digest_phase2.py::test_shuffled_unordered_list_same_digest PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_shuffled_location_violations_same_digest PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_ordered_events_list_order_matters PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_ordered_completed_agents_order_matters PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_sentinel_detects_new_volatile_key PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_sentinel_detects_iso_datetime_value PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_sentinel_no_false_positives_on_stable_fields PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_sentinel_excluded_fields_not_reported PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_volatile_field_patterns_non_empty PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_schema_version_present_in_view PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_schema_version_is_integer PASSED
tests/unit/test_runtime_state_digest_phase2.py::test_golden_hash_contract PASSED
tests/unit/test_runtime_state_digest.py::test_timestamp_variance_same_digest PASSED
tests/unit/test_runtime_state_digest.py::test_semantic_variance_changes_digest PASSED
tests/unit/test_runtime_state_digest.py::test_digest_view_does_not_mutate_input PASSED
tests/unit/test_runtime_state_digest.py::test_digest_field_excluded_from_own_computation PASSED
tests/unit/test_runtime_state_digest.py::test_exclude_paths_contains_expected_entries PASSED

17 passed in 0.05s
```

---

## git show --name-only --oneline

```
d18c954ad (HEAD -> SSOT) feat: Phase 2 digest hardening — ordering, sentinel, schema version
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L0_routing/scripts/runtime_state_digest.py
docs/evidence/SSOT_RUNTIME_STATE_DIGEST_PHASE2.md
tests/unit/test_runtime_state_digest_phase2.py
```

---

## Evidence Footer

- **Evidence commit hash:** `d18c954adac70e10fb509fac5b9a452517ba8254`
- **git status --porcelain:** staged files clean; untracked: runtime_state*.json, docs/evidence/*_transcript.txt (artifacts, not tracked)
