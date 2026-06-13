# RCA: L5_safety/enforcement Functional Duplicates + Naming Convention Remediation Plan

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 1. Root Cause Analysis: enforcement/ Duplicates

### Finding

**35 byte-identical duplicate file pairs** exist in `agentic_core/L5_safety/enforcement/`.
110 `.py` files total, only 75 unique content hashes.

### Root Cause

Commit `04651c8e1` ("governance(purity): scope folder purity invariant to compliant folders + fix import contracts", 2026-02-16) mass-created copies to satisfy `FOLDER_PURITY_RULES["enforcement"]`.

The purity rules require enforcement/ files to match one of:
```
*_guardrail.py | *_enforcer.py | *_gate.py | *_strategy.py
*Strategy.py   | *Adapter.py   | *Monitor.py | *Factory.py | *Gateway.py
```

Files like `agent_info.py`, `circuit_breaker.py`, `archival_gatekeeper.py` don't match. Instead of **renaming** them to compliant names, the commit **copied** them with compliant suffixes — creating dead duplicates.

### Duplicate Suffix Patterns

| Pattern | Count | Example |
|---------|-------|---------|
| `_enforcer` | 27 | `agent_info.py` == `agent_info_enforcer.py` |
| `_gate` | 3 | `circuit_breaker.py` == `circuit_breaker_gate.py` |
| `_guardrail` | 3 | `process_guard.py` == `process_guardrail.py` |
| `_strategy` | 1 | `canary_token_defense.py` == `canary_token_defense_strategy.py` |
| `Factory` | 1 | `AdapterBase.py` == `AdapterBaseFactory.py` |

### Near-Duplicates (same origin, diverged slightly)

These pairs are NOT byte-identical but share the same origin:
- `data.py` (12803) vs `data_enforcer.py` (12562)
- `human_review_queue.py` (16830) vs `human_review_queue_enforcer.py` (14213)
- `module_collision_guard.py` (14701) vs `module_collision_guardrail.py` (14678)

### Impact

- **70 files** where only 35 are needed (50% bloat)
- Import confusion: unclear which name is canonical
- Agent discovery scans count duplicate classes
- Maintenance risk: edits to one copy don't propagate to the other

---

## 2. Naming Convention Audit

### utils/ folders — expected `_util` suffix

**18 violations** across 7 utils/ directories:

| File | Layer |
|------|-------|
| `path_utils.py` | L0_routing |
| `project_root.py` | L0_routing |
| `subprocess_runner.py` | L0_routing |
| `guardrails.py` | L1_cognition |
| `history_merger.py` | L1_cognition |
| `profile_updater.py` | L1_cognition |
| `template_finder.py` | L1_cognition |
| `template_matcher.py` | L1_cognition |
| `token_updater.py` | L1_cognition |
| `log_orchestration_metrics.py` | L3_orchestration |
| `local_disk_adapter.py` | L4_state |
| `_fca_safety_gates.py` | L5_safety |
| `cache_invalidation_utils.py` | L5_safety |
| `code_tool_runner_core.py` | L5_safety |
| `ConstitutionalOverseer.py` | L5_safety |
| `cst_transformers_types.py` | L5_safety |
| `surgical_context_types.py` | L5_safety |
| `canonical_json.py` | agentic_core (root) |

Note: many of these are already in the `UTILS_SUFFIX_ALLOWLIST` in the purity test.

### types/ folders — expected `_types` suffix

**46 violations** across 9 types/ directories (many in L2_execution).

Largest offenders:
- `L2_execution/types/`: 16 files without `_types` suffix (vllm_*, tool_intent, sandbox_envelope, etc.)
- `L0_routing/types/`: 8 files (routing_contracts, guardian_registry, etc.)
- `L5_safety/types/`: 6 files

Note: many already in `TYPES_SUFFIX_ALLOWLIST`.

### validators/ folders

**0 violations** — all validator files already conform.

---

## 3. Remediation Plan

### Phase A: Delete Enforcement Duplicates (35 byte-identical pairs)

For each pair, determine canonical name via import scan, delete the dead copy.

**Decision rule:**
- If only one name is imported anywhere → keep that one, delete the other
- If neither is imported → keep the purity-compliant name, delete the base name
- If both imported → merge imports to the purity-compliant name, delete the base

**Estimated scope:** Delete 35 files, update ~0-10 imports.

### Phase B: Resolve Near-Duplicate Diverged Pairs (3 pairs)

Manual diff to understand divergence, then merge and delete.

### Phase C: Rename Non-Conforming Files in utils/ (18 files)

Rename to add `_util` suffix, update all imports.

### Phase D: Rename Non-Conforming Files in types/ (46 files)

Rename to add `_types` suffix, update all imports.
This is the largest phase due to L2_execution having 16 non-conforming files.

### Phase E: Shrink Allowlists

After renames, remove entries from `UTILS_SUFFIX_ALLOWLIST` and `TYPES_SUFFIX_ALLOWLIST` in `test_folder_purity_hardening.py`.

---

## 4. Risk Notes

- **Import breakage**: Every rename requires updating all import sites across the repo.
- **Test breakage**: Tests referencing old module names will fail.
- **Git blame disruption**: Renames break `git blame` continuity.
- **Agent registry**: `agent_discovery_full.json` may reference old names.
- Recommend: one git commit per phase, run full pytest after each.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

