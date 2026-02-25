# SSOT Runtime State Digest — Phase 1 Evidence

## EXCLUDE_PATHS

```python
EXCLUDE_PATHS: list[str] = [
    "start_time",
    "end_time",
    "events[*].time",
    "completed_agents[*].time",
    "runtime_state_digest_sha256",
]
```

## Function Locations

| Function | File | Line |
| :--- | :--- | :--- |
| `RuntimeStateManager.save` (writer) | `agentic_core/L0_routing/scripts/execute_ssot.py` | 1131 |
| `EXCLUDE_PATHS` | `agentic_core/L0_routing/scripts/runtime_state_digest.py` | 19 |
| `runtime_state_digest_view` | `agentic_core/L0_routing/scripts/runtime_state_digest.py` | 31 |
| `compute_runtime_state_digest` | `agentic_core/L0_routing/scripts/runtime_state_digest.py` | 57 |
| `canonical_hash` (reused) | `agentic_core/utils/canonical_serializer_util.py` | 66 |

## Commit Topology

### git show --name-only --oneline
```
654dbff19 (HEAD -> SSOT) feat: deterministic runtime_state_digest_sha256 + unit tests + evidence
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L0_routing/scripts/runtime_state_digest.py
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py
agentic_core/L5_safety/runners/agent_roster_runner.py
docs/evidence/SSOT_RUNTIME_STATE_DIGEST_PHASE1.md
tests/unit/test_runtime_state_digest.py
```

## Wave 2 — Unit Test Proof

### Command
```
python -m pytest tests/unit/test_runtime_state_digest.py -v -m unit
```

### Output
```
collected 5 items

tests/unit/test_runtime_state_digest.py::test_timestamp_variance_same_digest PASSED   [ 20%]
tests/unit/test_runtime_state_digest.py::test_semantic_variance_changes_digest PASSED  [ 40%]
tests/unit/test_runtime_state_digest.py::test_digest_view_does_not_mutate_input PASSED [ 60%]
tests/unit/test_runtime_state_digest.py::test_digest_field_excluded_from_own_computation PASSED [ 80%]
tests/unit/test_runtime_state_digest.py::test_exclude_paths_contains_expected_entries PASSED [100%]

5 passed in 0.04s
```

## Wave 3 — End-to-End Dry-Run Proof

### Dry-run 1
```
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS="1"
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --dry-run --domains
Exit code: 0
```

### Dry-run 2
```
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS="1"
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --dry-run --domains
Exit code: 0
```

### Digest extraction
```
python -c "import json; d=json.load(open('runtime_state.run1.json')); print(d.get('runtime_state_digest_sha256','MISSING'))"
23aed57a063ea7cd499dcbb7d02365b7951bc4c577682d21e474663a7365fcc9

python -c "import json; d=json.load(open('runtime_state.run2.json')); print(d.get('runtime_state_digest_sha256','MISSING'))"
23aed57a063ea7cd499dcbb7d02365b7951bc4c577682d21e474663a7365fcc9
```

**Digests match: `23aed57a063ea7cd499dcbb7d02365b7951bc4c577682d21e474663a7365fcc9`**

### File SHA256 hashes
```
Get-FileHash -Algorithm SHA256 runtime_state.run1.json
SHA256  20581F27E4988A07267344B28E61E4469A2DDB66AB0D2CEABD0100D192D7416A

Get-FileHash -Algorithm SHA256 runtime_state.run2.json
SHA256  9A62A639337604A3D3281EA798252D471C8C92557A83017312CB41D74E1E69DB
```

File hashes differ (expected). Minimal diff limited to excluded fields:

```
python -c "<diff script>"
Differing fields (all excluded):
  start_time: '2026-02-19T19:19:32.108541' vs '2026-02-19T19:20:30.897571'
  end_time: '2026-02-19T19:20:25.434345' vs '2026-02-19T19:21:24.338397'
  events[0].time differs
  events[1].time differs
  ... (183 total differing excluded-timestamp fields)
Total differing excluded fields: 183
```

All differences are in EXCLUDE_PATHS fields only. No semantic content differs.

## Evidence Footer

- **Evidence commit hash:** `654dbff19062885dcd9735b8599cb3ba68230759`
- **git status --porcelain:** staged files clean; untracked: runtime_state*.json, docs/evidence/*_transcript.txt (artifacts, not tracked)
