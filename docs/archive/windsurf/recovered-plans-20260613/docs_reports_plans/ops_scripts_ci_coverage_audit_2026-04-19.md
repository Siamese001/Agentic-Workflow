# `ops_scripts/ci/` Enforcement Coverage Audit

**Date**: 2026-04-19
**Scope**: Every file in `ops_scripts/ci/` mapped to its enforcement layer (Windsurf rule, ADG P0–P3 suite, or `.pre-commit-config.yaml`).

## Enforcement Layers

| Layer | Purpose | Entry Point |
|---|---|---|
| **PC** | Pre-commit (commit-time auto-block) | `.pre-commit-config.yaml` |
| **ADG** | ADG P0/P1 gate suite, auto-run on `generate_full_adg.py` | `ops_scripts/ci/adg_gates/p0_runner.py` + `GATE_REGISTRY` |
| **RCG** | `run_contract_gates.py` — canonical CI entry (Constitutional §4) | `python ops_scripts/ci/run_contract_gates.py` |
| ~~RAG~~ | ~~`run_all_guardrails.py`~~ — **deleted 2026-04-19** (see HITL below) | — |
| **RAP** | `run_architecture_proof.py` — governed-app release gate | manual |
| **REP** | `run_eval_pipeline_acceptance.py` — eval pipeline release gate | manual |
| **LIB** | Library/helper module (not a gate entrypoint) | imported by above |
| **MAN** | Manual-only lane in pre-commit (`stages: [manual]`) | `pre-commit run <id> --hook-stage manual` |

## Coverage Matrix — `ops_scripts/ci/`

| File | Role | PC | ADG | RCG | RAG | RAP | REP | LIB | MAN | Status |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `_adg_ci_gates.py` | private ADG helper | | | | | | | ✓ | | ✅ |
| `_validate_pytest_config.py` | pytest config SSOT | T6 | | | | | | | | ✅ |
| `adg_gates/__init__.py` | gate registry (12 gates) | | ✓ | ✓ | | | | ✓ | | ✅ |
| `adg_gates/__main__.py` | CLI entry (was broken, **fixed this session**) | | | | | | | | | ✅ |
| `adg_gates/cli.py` | `list`/`run-phase`/`run-gate`/`run-all` | | ✓ | | | | | | | ✅ |
| `adg_gates/gate_base.py` | `ADGGateBase` parent class | | | | | | | ✓ | | ✅ |
| `adg_gates/gate_policy.py` | `ExecutionPolicy` | | | | | | | ✓ | | ✅ |
| `adg_gates/gate_ssot_catalog.py` | gate catalogue SSOT | | | | | | | ✓ | | ✅ |
| `adg_gates/gate_m_gates.py` | M-gate helpers | | | | | | | ✓ | | ✅ |
| `adg_gates/gate_p0_authority.py` | AuthorityBoundaryGate | | ✓ (2) | ✓ | | | | | | ✅ |
| `adg_gates/gate_p0_capability_egress.py` | CapabilityEgressGate | | ✓ (4) | ✓ | | | | | | ✅ |
| `adg_gates/gate_p0_critical_path.py` | CriticalPathIntegrityGate | | ✓ (1) | ✓ | | | | | | ✅ |
| `adg_gates/gate_p0_determinism.py` | DeterminismProvenanceGate | | ✓ (6) | ✓ | | | | | | ✅ |
| `adg_gates/gate_p0_text_to_action.py` | TextToActionGate | | ✓ (5) | ✓ | | | | | | ✅ |
| `adg_gates/gate_p0_write_sovereignty.py` | WriteSovereigntyGate | | ✓ (3) | ✓ | | | | | | ✅ |
| `adg_gates/gate_executor_theater.py` | **ExecutorTheaterGate (new)** | | ✓ (9) | ✓ | | | | | | ✅ |
| `adg_gates/gate_infra_wiring.py` | **InfraWiringGate (new)** | | ✓ (10) | ✓ | | | | | | ✅ |
| `adg_gates/gate_p1_lifecycle.py` | LifecycleCoverageGate | | ✓ (7) | | | | | | | ✅ |
| `adg_gates/gate_p1_trace_replay.py` | TraceReplayEvalGate | | ✓ (8) | | | | | | | ✅ |
| `adg_gates/gate_p1_architecture_witness.py` | ArchitectureWitnessGate (**wired this session**) | | ✓ (11) | | | | | | | ✅ |
| `adg_gates/gate_p1_prompt_wiring.py` | PromptAssemblyWiringGate (**wired this session**) | | ✓ (12) | | | | | | | ✅ |
| `adg_gates/p0_runner.py` | P0 two-pass orchestrator | | ✓ | ✓ | | | | | | ✅ |
| `adg_gates/p3_trend_runner.py` | P3 trend-watch runner | | ✓ | ✓ | | | | | | ✅ |
| `check_agents_mcp_coverage.py` | MCP config ↔ AGENTS.md coverage | T6c | | ✓ | | | | | | ✅ |
| `check_agents_md_sync.py` | AGENTS.md autogen byte-match | T6d | | | | | | | | ✅ |
| `check_governed_app_conformance.py` | governed-app contract | T7a | | | | ✓ | | | | ✅ |
| `check_mcp_sync_integrity.py` | mcp_config.json ↔ AGENTS.md strict | T6b | | ✓ | | | | | | ✅ |
| `check_query_progress_bar.py` | §16 progress bar | T7d | | | | | | | | ✅ |
| `check_structure_policy.py` | structure_policy.yaml | T7b | | | | | | | | ✅ |
| `ci_timeout_decorator.py` | orphaned utility (was used by deleted `run_all_guardrails.py`) | | | | | | | ✓ | | ⚠️ |
| `executor_theater_gate.py` | standalone (wrapped as ADG gate 9) | | ✓ (via 9) | ✓ | | | | | | ✅ |
| `infra_wiring_scan.py` | standalone (wrapped as ADG gate 10) | MAN | ✓ (via 10) | ✓ | | | | | ✓ | ✅ |
| ~~`run_all_guardrails.py`~~ | **deleted 2026-04-19** — duplicate of canonical `run_contract_gates.py` | | | | | | | | | 🗑️ |
| `run_architecture_proof.py` | release gate S1+S2+S3 | | | | | ✓ | | | | ✅ |
| `run_contract_gates.py` | **canonical CI entry** (Constitutional §4) | | | ✓ | | | | | | ✅ |
| `run_eval_pipeline_acceptance.py` | eval pipeline acceptance | | | | | | ✓ | | | ✅ |
| `validate_hitl_format.py` | HITL packet format | T7c | | | | | | | | ✅ |
| `validate_hitl_rules.py` | HITL corpus validator | T7e | | | | | | | | ✅ |

**Totals**: 37 files (was 38 before `run_all_guardrails.py` deletion) — **36 green, 1 orphaned helper**.

## �️ Resolved: `run_all_guardrails.py` — DELETED

**HITL decision 2026-04-19**: Delete `run_all_guardrails.py` (HITL packet recorded this session).

**Root cause**: The file referenced 4 scripts that no longer exist (`check_anti_patterns.py`, `check_utility_silent_swallowers.py`, `check_plan_location_compliance.py`, `check_powershell_ban.py`) — removed during the 2026-03-11 consolidation (per `.windsurf/RULES_INDEX.md:325`) when their functionality was merged into `run_contract_gates.py`, but the orchestrator config was never updated.

**Verdict**: Constitutional §4 designates `run_contract_gates.py` as the canonical CI entry point. `run_all_guardrails.py` duplicated that role and had been silently broken for ~5 weeks.

**Actions taken**:
- Deleted `ops_scripts/ci/run_all_guardrails.py`
- Marked entry as `__DELETED_2026-04-19` in `@c:\Git\Agentic-Workflow\ops_scripts\ci\hollow_file_baseline.json:10933`
- `ci_timeout_decorator.py` is now orphaned (its only consumer was `run_all_guardrails.py`) — flagged in matrix for future cleanup, kept for now in case future orchestrators want the `ci_progress_reporter`/`generate_rca` helpers.

## Changes This Session

### Remediation
- ✅ Refactored 3 Google Gemini SDK callsites (`@c:\Git\Agentic-Workflow\agentic_core\evaluation\judges\llm_judge.py:21`, `@c:\Git\Agentic-Workflow\agentic_core\evaluation\judges\provider_registry.py:28`, `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\validators\dependencygraph_validator.py:102`) through new `create_gemini_model()` adapter in `@c:\Git\Agentic-Workflow\infrastructure\sdks_mcps\__init__.py:96-122`
- ✅ Refactored `@c:\Git\Agentic-Workflow\agentic_core\L1_cognition\reasoning\semantic_retriever.py` to drop redundant `import chromadb` and use existing `SovereignChromaClient` adapter
- ✅ Added `bm25_store.py` to `SANCTIONED_ADAPTER_FILES` at `@c:\Git\Agentic-Workflow\ops_scripts\ci\infra_wiring_scan.py:80` (legitimate L4 SQLite adapter)
- ✅ `infra_wiring_scan.py` file scan now reports **0 violations** (was 5)

### New ADG Gate
- ✅ Created `@c:\Git\Agentic-Workflow\ops_scripts\ci\adg_gates\gate_infra_wiring.py` — `InfraWiringGate(ADGGateBase)` wrapping `scan_directory()` with full `GateViolation` provenance
- ✅ Registered as gate 10 in P0 phase A (`GATE_REGISTRY`) and in `FULL_GATE_CLASSES` (`p0_runner.py`)

### Registry Completeness
- ✅ Registered 4 previously unreachable gates in `GATE_REGISTRY`: `ExecutorTheaterGate` (9), `InfraWiringGate` (10), `ArchitectureWitnessGate` (11), `PromptAssemblyWiringGate` (12). CLI `python -m ops_scripts.ci.adg_gates list` now shows all 12.
- ✅ Fixed `NameError: name 'sys' is not defined` in `@c:\Git\Agentic-Workflow\ops_scripts\ci\adg_gates\__main__.py` — added missing `import sys`

## Verification

```
# File scan clean
python ops_scripts/ci/infra_wiring_scan.py
  → ✅ exit 0 (file scan); ADG view warning clears on next `generate_full_adg.py`

# ADG gate passes standalone
python -m ops_scripts.ci.adg_gates.gate_infra_wiring
  → [CI-GATE] PASSED: infra_wiring (0 violations)

# CLI lists all 12 gates
python -m ops_scripts.ci.adg_gates list
  → Total: 12 gates (was 8)

# Full P0 two-pass executes all 8 P0 gates (ExecutorTheater + InfraWiring clean)
python -m ops_scripts.ci.adg_gates.p0_runner --skip-preflight --no-artifacts
  → 8/8 P0 gates execute; new gates not in blocked set
```
