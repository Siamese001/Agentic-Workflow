# Phase 1 — AST + Fuzzy SSOT Consolidation Discovery

**Status:** COMPLETE
**Date:** 2026-02-16

## Evidence File Commit Chain

- **Phase 1 remediation commit:** `9281a2d90`
- **Evidence repair commit:** `2c6321ef0`

## Execution Summary

Phase 1 discovery completed with deterministic, evidence-locked outputs. Three waves executed:

- **Wave 1.2:** Deterministic inventory of AST/fuzzy library usage and candidate definitions
- **Wave 1.3:** Near-duplicate clustering (exact + fuzzy matching)
- **Wave 1.4:** Call-site mapping for discovered symbols

All outputs are deterministic and byte-identical on rerun from clean tree.

---

## Wave 1.2 — Deterministic Inventory

### Command Executed

```bash
python tools/tmp_ok/scan_ast_fuzzy_defs.py
```

### Inventory Execution Output

```text
Scanning from: C:\Git\Agentic-Workflow
Scanned roots: ['agentic_core', 'tools', 'ops_scripts']
Excluded roots: ['.backup', 'apps_lic', 'apps_rg', 'apps_shared', 'archives', 'tests']

Files scanned: 1284
Files with AST imports: 197
Files with fuzzy imports: 6
Files with candidates: 396
Output written to: C:\Git\Agentic-Workflow\docs\reports\sub\ast_fuzzy_inventory.json
SHA256: c89140e4b8f6a7f4b2ea616a90b6a028d363164fd8a0b1b6d495cb2fbcc36aa2
Exit code: 0
```

### Inventory Statistics

- **Total files scanned:** 1,284
- **Files with AST library imports:** 197 (15.3%)
- **Files with fuzzy library imports:** 6 (0.5%)
- **Files with candidate definitions:** 396 (30.8%)
- **Parse failures:** 0

### AST Libraries Detected

- `ast` (stdlib)
- `inspect` (stdlib)
- `tokenize` (stdlib)
- `libcst` (third-party)
- `parso` (third-party)
- `astroid` (third-party)

### Fuzzy Libraries Detected

- `difflib` (stdlib)

### Candidate Definition Keywords

Scanned for: `parse`, `ast`, `dump`, `hash`, `normalize`, `token`, `similarity`, `fuzzy`, `match`, `compare`

### Inventory Output Artifact

**File:** `docs/reports/sub/ast_fuzzy_inventory.json`
**SHA256:** `c89140e4b8f6a7f4b2ea616a90b6a028d363164fd8a0b1b6d495cb2fbcc36aa2`

Schema:

```json
{
  "scanned_roots": ["agentic_core", "tools", "ops_scripts"],
  "excluded_roots": [".backup", "apps_lic", "apps_rg", "apps_shared", "archives", "tests"],
  "files": [
    {
      "path": "agentic_core/...",
      "imports": {"ast": [...], "fuzzy": [...]},
      "candidates": [{"kind": "function|class", "name": "...", "line": 0, "keywords": [...]}],
      "parse_status": "ok|failed",
      "parse_error": null
    }
  ]
}
```

---

## Wave 1.3 — Near-Duplicate Clustering

### Command Executed

```bash
python tools/tmp_ok/cluster_ast_fuzzy_defs.py
```

### Clustering Execution Output

```text
Loading inventory...
Building exact clusters...
Found 14 exact duplicate clusters
Building fuzzy pairs (threshold=0.6)...
Found 257 near-duplicate pairs (score >= 0.6)
Output written to: C:\Git\Agentic-Workflow\docs\reports\sub\ast_fuzzy_clusters.json
SHA256: 3aaf5319b15e92666d9305e8f4c41d6ab75f545ef9d7bad7a597ba5d4398d9cb
Exit code: 0
```

### Clustering Statistics

- **Exact duplicate clusters:** 14 (2+ members each)
- **Near-duplicate pairs (score ≥ 0.6):** 257
- **Clustering method:**
  - Exact: `ast.dump(node, include_attributes=False)` SHA256 for parsed defs
  - Fuzzy: `difflib.SequenceMatcher` on tokenized bodies
- **Fuzzy threshold:** 0.6 chosen as default for discovery process (no distribution analysis performed in Phase 1)

### Clustering Output Artifact

**File:** `docs/reports/sub/ast_fuzzy_clusters.json`
**SHA256:** `3aaf5319b15e92666d9305e8f4c41d6ab75f545ef9d7bad7a597ba5d4398d9cb`

Schema:

```json
{
  "exact_dupe_clusters": [
    {
      "hash": "sha256_of_ast_dump",
      "members": [
        {"path": "...", "name": "...", "line": 0, "kind": "function|class"}
      ]
    }
  ],
  "near_dupe_pairs": [
    {
      "a": {"path": "...", "name": "...", "line": 0},
      "b": {"path": "...", "name": "...", "line": 0},
      "score": 0.75,
      "method": "SequenceMatcher"
    }
  ]
}
```

---

## Wave 1.4 — Call-Site Mapping

### Command Executed

```bash
python tools/tmp_ok/callsite_ast_fuzzy_defs.py
```

### Call-Site Execution Output

```text
Loading inventory...
Building call-site map...
Found 784 unique symbols
Processing symbol 1/784: ASTAnalyzer
...
Processing symbol 751/784: validate_phase_names
Output written to: C:\Git\Agentic-Workflow\docs\reports\sub\ast_fuzzy_callsites.json
SHA256: b0bcf411553780cbb682dd17e508ae78b545fdbf23cf58b074360b76f8adee06

Statistics:
Total symbols: 784
Total inbound references: 18188

Top 20 symbols by inbound reference count:
  get: 3429
  report: 1306
  __init__: 1095
  set: 884
  check: 718
  execute: 686
  main: 676
  keys: 564
  heal: 561
  run: 515
  heal_repository: 499
  query: 346
  search: 321
  matches: 319
  plan: 312
  standard_heal: 279
  scan: 278
  to_dict: 273
  __post_init__: 182
  assert_no_persistent_write: 158
Exit code: 0
```

### Call-Site Statistics

- **Total unique symbols discovered:** 784
- **Total inbound references:** 18,188
- **Average references per symbol:** 23.2
- **Symbols with 0 references:** ~50 (internal/unused candidates)

### Central Candidates (Top 10 by AST/Fuzzy Scope Keywords)

**Mechanical Derivation Algorithm:**

1. Load callsites.json: extract (symbol -> inbound_ref_count, definitions[])
2. Sort symbols by inbound_ref_count DESC, then symbol ASC for tie-break
3. Filter symbol name contains (case-insensitive) any: `parse`, `ast`, `dump`, `hash`, `normalize`, `token`, `similarity`, `fuzzy`, `match`, `compare`
4. Exclude dunder names matching `^__.*__$`
5. Definition validation gate:
   - Symbol must have at least 1 definition entry in callsites.json
   - AND symbol must appear as candidate name in inventory.json (exact match)
6. Select top 10 passing the gate
7. Record: name, inbound_ref_count, definition location from callsites.json definitions[0]

**Total valid candidates passing gate:** 239

**Resulting Central Candidates (Top 10):**

1. **`matches`** (319 refs) — agentic_core/L3_orchestration/types/permission_scope_types.py:54
2. **`token`** (150 refs) — agentic_core/L2_execution/types/capability_token_types.py:299
3. **`file_hash`** (58 refs) — agentic_core/L0_routing/scripts/compare_archive_to_current_util.py:8
4. **`normalize_repo_path`** (49 refs) — agentic_core/L0_routing/types/guardian_contract_types.py:604
5. **`CapabilityTokenArtifact`** (33 refs) — agentic_core/L2_execution/types/capability_token_types.py:98
6. **`ASTValidatorAgent`** (25 refs) — agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py:60
7. **`ASTCoordinate`** (23 refs) — agentic_core/L5_safety/types/surgical_context_types.py:17
8. **`get_file_hash`** (23 refs) — agentic_core/L0_routing/scripts/investigate_overlaps_util.py:14
9. **`state_hash_fn`** (22 refs) — agentic_core/base_agents/SovereignBaseAgent.py:313
10. **`unparse`** (22 refs) — agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py:17

### Call-Site Output Artifact

**File:** `docs/reports/sub/ast_fuzzy_callsites.json`
**SHA256:** `b0bcf411553780cbb682dd17e508ae78b545fdbf23cf58b074360b76f8adee06`

Schema:

```json
{
  "symbol_name": {
    "definitions": [
      {"path": "...", "line": 0, "kind": "function|class"}
    ],
    "references": [
      {"path": "...", "line": 0, "snippet": "..."}
    ],
    "inbound_ref_count": 123
  }
}
```

---

## Repository State

### Pre-Phase Baseline

```text
Commit: 970668441
Message: docs(phase4): closeout evidence-lock + single-phase markdown enforcement
Status: clean (no uncommitted changes)
```

### Files Modified/Added in Phase 1 (Remediation)

```text
tools/tmp_ok/scan_ast_fuzzy_defs.py (NEW)
tools/tmp_ok/cluster_ast_fuzzy_defs.py (NEW)
tools/tmp_ok/callsite_ast_fuzzy_defs.py (NEW)
docs/reports/sub/ast_fuzzy_inventory.json (NEW)
docs/reports/sub/ast_fuzzy_clusters.json (NEW)
docs/reports/sub/ast_fuzzy_callsites.json (NEW)
docs/reports/sub/ast_fuzzy_ssot_consolidation_phase1.md (NEW)
```

### Governance Compliance

✅ No functional refactors outside tools/tmp_ok/ and docs/reports/sub/
✅ No scanning or outputs under apps_* or tests/
✅ All outputs deterministic and byte-identical on rerun
✅ All JSON outputs sorted for stability
✅ UTF-8 with error handling (errors="replace")
✅ Normalized newlines (LF only)
✅ No baseline/config file modifications (ops_scripts/hooks/landmine_baseline.txt NOT modified)

---

## Configuration

### Environment Variables

Phase 1 scripts support configuration via environment variables with sensible defaults:

- **`AST_FUZZY_THRESHOLD`** (default: `0.6`)
  - Fuzzy similarity threshold for near-duplicate detection in cluster_ast_fuzzy_defs.py
  - Controls the minimum SequenceMatcher ratio for clustering pairs
  - Usage: `AST_FUZZY_THRESHOLD=0.7 python tools/tmp_ok/cluster_ast_fuzzy_defs.py`

- **`AST_FUZZY_RG_TIMEOUT`** (default: `10`)
  - Ripgrep timeout in seconds for reference searches in callsite_ast_fuzzy_defs.py
  - Balances search completeness with responsiveness
  - Usage: `AST_FUZZY_RG_TIMEOUT=20 python tools/tmp_ok/callsite_ast_fuzzy_defs.py`

Both variables are externalized to satisfy governance constraints while maintaining discovery process flexibility.

---

## Remediation Proof (Hook-Clean)

### Phase 1 Remediation Commit

```text
9281a2d90 docs(sub): phase1 ast+fuzzy discovery evidence-lock (hook-clean)
docs/reports/sub/ast_fuzzy_callsites.json
docs/reports/sub/ast_fuzzy_clusters.json
docs/reports/sub/ast_fuzzy_inventory.json
docs/reports/sub/ast_fuzzy_ssot_consolidation_phase1.md
tools/tmp_ok/callsite_ast_fuzzy_defs.py
tools/tmp_ok/cluster_ast_fuzzy_defs.py
tools/tmp_ok/scan_ast_fuzzy_defs.py
```

### Repository Status at Remediation

Command: `git status --porcelain=v1`

```text
(no output - clean working tree)
```

### Evidence File Edit Commit

Command: `git --no-pager show --name-only --oneline 2c6321ef0`

```text
2c6321ef0 docs(sub): phase1 evidence repair (remediation proofs, contradictions fixed, mechanical central candidates)
docs/reports/sub/ast_fuzzy_ssot_consolidation_phase1.md
```

### Pre-Commit Hook Verification

```text
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Passed
T0: Enforce LF Line Endings..............................................Passed
T0: Check Merge Conflict Markers.........................................Passed
T1: Python Syntax Validation.............................................Passed
T2a: Ruff Lint & Auto-Fix................................................Passed
T2b: Ruff Format.........................................................Passed
T3a: Anti-Pattern Landmine Detection.....................................Passed
T3b: Report Location SSOT Check..........................................Passed
T3c: Reject Tracked Generated Artifacts..................................Passed
T3e: Pycache Purge.......................................................Passed
T3f: Module Collision Guard..............................................Passed
T3h: Evidence Contract Validator.........................................Passed
T3i: Guard pytest.ini scope changes..................(no files to check)Skipped
T3g: Governance Policy Validation........................................Passed
T3h: Guard apps_shared instructional layer imports.......................Passed
Exit code: 0
```

**Status:** ✅ PASS — All hooks passed without baseline updates or bypass flags.

---

## Acceptance Criteria Status

| Criterion | Status | Evidence |
| --- | --- | --- |
| Exactly ONE evidence file | ✅ | This file: `docs/reports/sub/ast_fuzzy_ssot_consolidation_phase1.md` |
| Commit hash in evidence | ✅ | `9281a2d90` (Phase 1 remediation commit) |
| Clean/dirty status | ✅ | Clean (no uncommitted changes) |
| Exact commands documented | ✅ | All three commands listed above |
| JSON hashes documented | ✅ | All three SHA256 hashes captured |
| `ast_fuzzy_inventory.json` exists | ✅ | `c89140e4b8f6a7f4b2ea616a90b6a028d363164fd8a0b1b6d495cb2fbcc36aa2` |
| `ast_fuzzy_clusters.json` exists | ✅ | `3aaf5319b15e92666d9305e8f4c41d6ab75f545ef9d7bad7a597ba5d4398d9cb` |
| `ast_fuzzy_callsites.json` exists | ✅ | `b0bcf411553780cbb682dd17e508ae78b545fdbf23cf58b074360b76f8adee06` |
| No functional refactors | ✅ | Only tools/tmp_ok/ scripts and docs/reports/sub/ outputs |
| Repository governance respected | ✅ | No apps_* or tests/ scanning; no baseline modifications |
| Scope-valid central candidates | ✅ | Derived mechanically from AST/fuzzy keywords |

---

## Phase 1 Completion

Phase 1 discovery is **COMPLETE** and ready for Phase 2 consolidation.

**Key Deliverables:**

- Deterministic inventory of 1,284 files with 784 unique candidate definitions
- 14 exact duplicate clusters identified
- 257 near-duplicate pairs identified (score ≥ 0.6)
- Call-site map with 18,188 total inbound references
- Central candidates shortlist (top 10 AST/fuzzy-scoped) for consolidation prioritization

**Next Phase (Phase 2):** Consolidation implementation using discovered inventory and call-site map.
