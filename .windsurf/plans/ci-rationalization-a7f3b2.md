# ops_scripts/ci/ Rationalization Plan

## Executive Summary

**183 Python files** in `ops_scripts/ci/` totaling ~42,000 lines.
**~125 files (68%) are orphaned** — not wired into ANY governance layer.
**~26,750 lines of dead governance code** providing zero runtime protection.

This violates the **defense-in-depth** principle from NIST AI RMF and Skywork's 2025
Agentic Safety Blueprint: "One-and-done testing is an anti-pattern." An unwired gate
is worse than no gate — it creates false confidence.

---

## Evidence Sources

### ADG Graph Analysis
- 100 ADG nodes scanned via `mcp1_adg_nodes_by_file("ops_scripts/ci")`
- All files classified as `L_OPS` layer, `repo_module` identity
- No cross-layer imports from production code into these scripts

### Industry Research
1. **Skywork "Safety & Guardrails for Agentic AI Systems (2025)"**
   - Anti-pattern: "One-and-done testing. Models, tools, and data change constantly."
   - Anti-pattern: "Relying on prompts as primary safety control" → gates must be WIRED
   - Reference architecture: Identity → Policy → Execution → Data → Observability → Assurance planes
   - "Revisit metrics quarterly. If Author-Gate queues lengthen, you're over-indexing on human gates."

2. **CSA AAGATE (NIST AI RMF-Aligned Governance, Dec 2025)**
   - "Tool-Gateway Chokepoint — funnels every interaction through ONE auditable gate"
   - Four functions: Govern, Map, Measure, Manage → each has ONE authoritative entry
   - "Continuous telemetry scored and prioritized" → consolidate, don't scatter

3. **NIST AI RMF Playbook**
   - Govern → Map → Measure → Manage pipeline
   - Emphasis on "living governance" not static checks

### Five Governance Layers (This Repo)

| Layer | Wired Files | Purpose |
|-------|-------------|---------|
| 1. Windsurf hooks/rules | 0 from ci/ | IDE-time guardrails |
| 2. ADG CI gates | ~15 (adg_gates/ + _adg_ci_gates) | Graph-based regression |
| 3. tests/ | ~39 referenced | Correctness verification |
| 4. Pre-commit | 9 wired | Commit-time fast gates |
| 5. GitHub CI | 5 wired (excluded) | PR-time enforcement |

**Cross-ref**: `run_contract_gates.py` wires 11 scripts. `run_all_guardrails.py` wires 5.

---

## Wiring Audit Results

### WIRED (54 files — KEEP)
Files referenced from at least one governance layer:
- Pre-commit: 9 files
- run_contract_gates.py: 11 files
- run_all_guardrails.py: 5 files
- GitHub CI workflows: 5 files
- tests/: 39 files
- adg_gates/ transitively via p0_runner: 8 files (gate_p0_*, gate_base, gate_policy)
(Overlaps reduce unique count to ~54)

### ORPHANED (125+ files — ACTION NEEDED)
Not referenced from any governance layer. Zero protection value.

---

## Batch Recommendations

### Batch 1: DELETE — Placeholder stubs (3 files, 27 lines)
| File | Lines | Evidence |
|------|-------|----------|
| adg_harden_gate.py | 9 | `print("PASSED"); sys.exit(0)` — always passes |
| adg_lifecycle_gate.py | 9 | `print("PASSED"); sys.exit(0)` — always passes |
| adg_test_gate.py | 9 | `print("PASSED"); sys.exit(0)` — always passes |

**Rationale**: These are no-op stubs that print "PASSED" and exit 0. They provide
no governance value and could mask real failures if accidentally wired. Per CSA AAGATE:
"a single hallucinated command can rewrite infrastructure" — dummy gates create false confidence.

### Batch 2: ARCHIVE — One-time proofs & diagnostics (7 files, ~797 lines)
| File | Lines | Evidence |
|------|-------|----------|
| prove_layer1_exact_cache.py | 166 | One-time cache proof |
| prove_layer1_true_acceleration.py | 223 | One-time acceleration proof |
| prove_layer2_semantic_cache.py | 143 | One-time semantic cache proof |
| prove_redis_kv_layer1.py | 118 | One-time Redis KV proof |
| benchmark_sqlite_vs_redis.py | 80 | One-time benchmark |
| test_bge_only.py | 80 | Quick BGE test (not in tests/) |
| diagnose_openai.py | 27 | 27-line diagnostic script |

**Rationale**: Per NIST AI RMF Measure function: governance proofs should be
captured as evidence artifacts, not maintained as runnable scripts. These proved
specific capabilities at a point in time. Archive to `archives/ops_scripts/ci/proofs/`.

### Batch 3: ARCHIVE — Historical evidence & inventory (10 files, ~3,327 lines)
| File | Lines | Evidence |
|------|-------|----------|
| evidence_collect_phase1.py | 444 | "V15 Phase 1 D-Evidence Collector" |
| evidence_collect_phase2.py | 133 | "V15 Phase 2 D-Evidence Collector" |
| capture_ssot_cleanup_evidence.py | 96 | Cleanup evidence capture |
| inventory_collect_full.py | 655 | Full inventory collector |
| validate_evidence_contract.py | 59 | Evidence contract validator |
| enforcement_audit.py | 141 | "W-FINAL Phase 2: REQ-416" |
| enforcement_metadata_tagger.py | 310 | Metadata tagger |
| coverage_scoreboard.py | 276 | Coverage scoreboard |
| gap_regenerate_p0.py | 468 | "V15 P0 Gap Regeneration" |
| assess_phase_wave_tests.py | 1070 | Phase wave test assessment |

**Rationale**: These reference specific project milestones (V15, W-FINAL, REQ-416).
Per Skywork: "Threats iterate. So should your guardrails." — historical collection
scripts are not iterative governance. Archive to `archives/ops_scripts/ci/evidence/`.

### Batch 4: ARCHIVE — Superseded AST analysis (9 files, ~3,145 lines)
| File | Lines | Evidence |
|------|-------|----------|
| ast_canonical_scanner.py | 129 | Raw AST scanning |
| ast_gap_analysis.py | 385 | AST gap analysis |
| ast_gap_deep.py | 442 | Deep AST analysis |
| ast_gap_report.py | 256 | AST gap reporting |
| ast_gap_strict.py | 484 | Strict AST checks |
| ast_hardcoded_path_scanner.py | 222 | Hardcoded path detection |
| ast_layer_sovereignty_scanner.py | 494 | Layer sovereignty via raw AST |
| dump_adg_to_file.py | 237 | Dump AST graph to file |
| dependency_graph_hardening_verifier.py | 476 | Graph hardening verification |

**Rationale**: The ADG (AST Dependency Graph) system now provides all this
functionality through `_adg_ci_gates.py` (M1-M12) and the `adg_gates/` package.
Per AAGATE principle: "Tool-Gateway Chokepoint — funnels every interaction through
ONE auditable gate." Having duplicate AST scanners outside the ADG pipeline
violates single-gate-of-record. Archive to `archives/ops_scripts/ci/ast_legacy/`.

### Batch 5: ARCHIVE — One-time audit scripts (6 files, ~1,695 lines)
| File | Lines | Evidence |
|------|-------|----------|
| audit_agent_registry_enforcement.py | 393 | One-time registry audit |
| audit_dynamic_imports.py | 160 | One-time import audit |
| audit_embedding_surface.py | 177 | One-time embedding audit |
| audit_generation_routing_enforcement.py | 159 | One-time routing audit |
| audit_healing_tier_enforcement.py | 667 | One-time healing audit |
| audit_qwen_sovereignty.py | 139 | One-time Qwen audit |

**Rationale**: All `audit_*.py` files are point-in-time governance audits.
Per NIST AI RMF Manage function: audit results should be retained as evidence,
but audit scripts that aren't re-run provide no ongoing governance.
Archive to `archives/ops_scripts/ci/audits/`.

### Batch 6: ARCHIVE — Orphaned misc scripts (50 files, ~10,000+ lines)
These include multiple sub-categories of orphaned scripts:

**ADG operational orphans** (7 files):
active_set_helper, active_set_snapshot_check, active_set_ssot_check,
adg_fanin_triage_gate, adg_layer_violation_gate, adg_p1_defect_gate,
adg_skip_file_ratchet

**Orphaned guards** (8 files):
guard_agent_deletion, guard_guardian_hitl, guard_no_verify, guard_pytest_ini_scope,
gateway_bypass_scanner, centrality_gate, ci_integrity_gate_fallback, classify_utility_scripts

**Drift/discovery tools** (5 files):
drift_ratchet_gate, drift_scoped_test_runner, discovery_registry_consistency_check,
structure_drift_validator, ssot_violation_scanner

**Infrastructure/misc** (9 files):
infra_wiring_postprocess, init_contract_check, manifest_ssot_check, mcp_health_check,
mro_contract_check, mro_new_diamond_check, exclusion_sync_gate, sovereign_lockdown_check,
verify_stack_runtime

**Import/validation** (7 files):
import_resolution_guardian, validate_import_dependencies, validate_layer_violations,
validate_mcp_config, validate_timeout_progress, validate_timeout_recovery,
validate_yaml_configs, validate_hitl_format, validate_hitl_rules

**Orphaned adg_gates package members** (4 files):
gate_p1_lifecycle, gate_p1_trace_replay, gate_m_gates, gate_ssot_catalog

**Rationale**: These scripts were created for specific purposes but never wired
into any governance layer. Per Skywork: unwired gates are worse than no gates
because they create false confidence that something is being checked.
Archive to `archives/ops_scripts/ci/orphaned/`.

### Batch 7: CONSOLIDATE — ADG ban gates (5 files, ~1,344 lines → 1 file)
| File | Lines | Evidence |
|------|-------|----------|
| adg_grep_ban_gate.py | 229 | Grep pattern bans |
| adg_mypy_ban_gate.py | 257 | Mypy ban patterns |
| adg_pytest_ban_gate.py | 222 | Pytest ban patterns |
| adg_python_ban_gate.py | 380 | Python ban patterns |
| adg_yaml_grep_ban_gate.py | 256 | YAML grep ban patterns |

**Rationale**: Five files doing essentially the same thing — scanning files for
banned patterns. Per CSA AAGATE "Tool-Gateway Chokepoint" principle, these should
be a single parameterized scanner. `_adg_ci_gates.py` already has a
`_check_banned_patterns()` function. Consolidate into one `ban_gate_scanner.py`
or merge patterns into existing infrastructure.

### Batch 8: ARCHIVE — Orphaned check_* guards (38 files, ~5,600 lines)
The largest group. Notable files and their dispositions:

**Security-relevant (6 files — consider wiring instead of archiving)**:
check_secrets_scan, check_sensitive_logs, check_no_unconditional_xfail,
check_sovereign_llm_gateway, check_terminal_cleanup, check_system_learning_boundary

**Historical one-off checks (32 files)**:
check_adapter_prohibition, check_adg_ingestion, check_adg_proof_artifact_truthfulness,
check_adg_schema_field_names, check_agent_registry_completeness, check_apps_output_contract,
check_c0_boundary, check_ci_integrity, check_determinism_replay, check_direct_execute_calls,
check_directory_deletion_sweep, check_embedding_instantiation, check_environment_contract,
check_evidence_contract_v2, check_healer_direct_model, check_hitl_decision_record,
check_kernel_extension_boundary, check_layer_write_sovereignty, check_llm_sdk_imports,
check_model_string_literals, check_object_dunder_setattr, check_policy_drift_classification,
check_rca_closure, check_skip_convergence_gate, check_spine_adapter_contract,
check_spine_bypass, check_structured_output_emission, check_test_integrity,
check_test_quality, check_test_silent_skips, check_tooling_apps_boundary,
check_wall_clock_in_determinism

**Rationale**: Per Skywork's anti-pattern list: "One-and-done testing" — scripts
that were run once and never wired provide no ongoing protection.
For the 6 security-relevant files, recommend wiring into pre-commit manual lane
or run_all_guardrails.py rather than archiving.

---

## Impact Summary

| Batch | Action | Files | Lines | Risk |
|-------|--------|-------|-------|------|
| 1 | DELETE | 3 | 27 | None (no-ops) |
| 2 | ARCHIVE | 7 | ~797 | None (one-time proofs) |
| 3 | ARCHIVE | 10 | ~3,327 | Low (historical) |
| 4 | ARCHIVE | 9 | ~3,145 | Low (superseded by ADG) |
| 5 | ARCHIVE | 6 | ~1,695 | None (one-time audits) |
| 6 | ARCHIVE | 50 | ~10,000+ | Medium (some may have latent value) |
| 7 | CONSOLIDATE | 5 | ~1,344 | Low (merge into 1 file) |
| 8 | ARCHIVE/WIRE | 38 | ~5,600 | Medium (6 should be wired) |
| **Total** | | **128** | **~26,000** | |

Files remaining after rationalization: **55 wired, active files** (down from 183).
