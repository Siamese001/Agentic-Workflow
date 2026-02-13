# Architectural Anomalies Report — Deep Static Analysis

**Generated:** 2026-02-07
**Scope:** `agentic_core/` directory (excluding `__pycache__`, `.healing_backups`, `.git`)
**Analyzer:** Deep Static Analysis with import/inheritance/content heuristics

---

## 1. Executive Summary

### File Inventory

| Metric | Count |
|--------|-------|
| **Total files scanned** | 1,167 |
| **Python files (.py)** | 1,032 |
| **Non-Python files** | 135 |
| **Excluded (__init__.py)** | ~85 |
| **Analyzable Python files** | ~947 |

### Distribution by Territory

| Territory | .py Files | % of Total | Role |
|-----------|-----------|------------|------|
| **L0_maintenance** | 322 | 34.0% | Maintenance, scripts, setup |
| **L5_safety** | 221 | 23.3% | Validators, guardrails, enforcement |
| **L3_orchestration** | 60 | 6.3% | Workflows, managers, orchestration |
| **L2_execution** | 52 | 5.5% | Tools, API clients, actions |
| **L1_cognition** | 64 | 6.8% | Reasoning, LLM interaction |
| **L4_state** | 46 | 4.9% | State, persistence, memory |
| **L6_observability** | 31 | 3.3% | Dashboards, logging, metrics |
| **mixins** | 51 | 5.4% | Cross-cutting behavior mixins |
| **runtime** | 42 | 4.4% | Engine, types, runtime config |
| **config** | 18 | 1.9% | Global configuration |
| **utils** | 18 | 1.9% | Global utilities |
| **knowledge** | 11 | 1.2% | RAG, document loaders |
| **prompt_governance** | 16 | 1.7% | Prompt management |
| **base_agents** | 9 | 1.0% | Base class hierarchy |
| **interfaces** | 6 | 0.6% | Protocol definitions |

### L0 Dominance Problem

**L0_maintenance/scripts alone holds 296 Python files (31.3% of all Python)**, making it the single largest concentration. A healthy L0 should be small (configs, bootstrap, occasional maintenance scripts). This 296-file dumping ground is the #1 structural debt.

### Health Score

| Category | Count | % |
|----------|-------|---|
| **Correctly placed** | ~871 | ~92.0% |
| **Functional mismatches (High)** | ~32 | ~3.4% |
| **Ambiguous zones (Medium)** | ~14 | ~1.5% |
| **Orphaned / dumping ground** | ~30 | ~3.2% |
| **Overall Health Score** | | **~92%** |

> **Note:** The 92% score is misleading — while most files are technically in the correct *subfolder* for their *type*, the L0/scripts dumping ground contains files that belong across 4+ different layers. The "real" health score accounting for layer-level correctness is closer to **~85%**.

---

## 2. Functional Mismatches (High Priority)

### 2.1 L5 Safety Files Importing `subprocess` (L5 → Likely L2 Execution)

Files in L5 (Safety) should validate and enforce — not execute external processes. `subprocess` calls are execution-layer (L2) behavior.

| File Path | Current Layer | Functional Layer | Evidence |
|-----------|--------------|-----------------|----------|
| `L5_safety/enforcement/dashboard_e2_e_pipeline.py` | L5 | **L2 (Execution)** | `import subprocess` — runs external dashboard pipeline commands |
| `L5_safety/reasoning/GitAgent.py` | L5 | **L2 (Execution)** | `import subprocess` — executes git commands (external tool integration) |
| `L5_safety/reasoning/ReportLocationAgent.py` | L5 | **L2 (Execution)** | `import subprocess` — executes external commands for report generation |
| `L5_safety/validators/analysis_ops_validator.py` | L5 | **L2 (Execution)** | `import subprocess` — executes analysis operations, not just validates them |
| `L5_safety/validators/deterministic_cleaner_validator.py` | L5 | **L2 (Execution)** | `import subprocess` — runs cleanup commands, not pure validation |

**Acceptable exceptions (not anomalies):**

| File Path | Why Acceptable |
|-----------|---------------|
| `L5_safety/enforcement/safe_subprocess_handler.py` | **IS** the safety wrapper around subprocess — correctly in L5 |
| `L5_safety/utils/subprocess_security_util.py` | **IS** the security utility for sanitizing subprocess calls — correctly in L5 |
| `L5_safety/reasoning/PreCommitSovereignAgent.py` | Safety agent that enforces pre-commit hooks — subprocess is the enforcement mechanism |
| `L5_safety/reasoning/ArchitectureGovernorAgent.py` | Governance agent — subprocess used to read architectural state |
| `L5_safety/reasoning/AutonomyGuardianAgent.py` | Safety guardian — subprocess used to check system state |
| `L5_safety/reasoning/SovereignActionPlaneAgent.py` | Safety-plane agent — subprocess used for safety enforcement actions |
| `L5_safety/utils/pre_deploy_check_util.py` | Pre-deployment safety check — subprocess validates deployment readiness |

### 2.2 L3 Orchestration Files Containing Validator Classes (L3 → Likely L5 Safety)

| File Path | Current Layer | Functional Layer | Evidence |
|-----------|--------------|-----------------|----------|
| `L3_orchestration/reasoning/UnifiedAgent.py` | L3 | **L3+L5 Hybrid** | Contains `class Validator`, `class StructuralValidator`, `class CodeValidator` — inline validation classes that should be extracted to L5 |

### 2.3 L4 State Files Containing Agent Classes Outside reasoning/ (L4 → Likely L3 Orchestration)

| File Path | Current Layer | Functional Layer | Evidence |
|-----------|--------------|-----------------|----------|
| `L4_state/enforcement/cached_state_ledger.py` | L4/enforcement | **L4/reasoning** | `class CachedStateLedgerAgent` — Agent class should be in reasoning/ |
| `L4_state/memory/checkpoint_manager.py` | L4/memory | **L4/reasoning** | `class CheckpointManagerAgent` — Agent with control flow loops |
| `L4_state/memory/gravity_state_store.py` | L4/memory | **L4/reasoning** | `class GravityStateAgent` — Agent class with complex state management logic |

**Verdict:** These are correctly in **L4** (they manage state/persistence), but are in the **wrong subfolder** — Agent classes belong in `L4/reasoning/`, not `memory/` or `enforcement/`.

### 2.4 Agent Classes Embedded in Non-reasoning Subfolders (Cross-Layer)

| File Path | Current Subfolder | Should Be | Evidence |
|-----------|------------------|-----------|----------|
| `L5_safety/types/code_detection_types.py` | types/ | reasoning/ or types/ (split) | `class CodeDetectorAgent` embedded in types file |
| `L5_safety/types/code_enforcement_types.py` | types/ | reasoning/ or types/ (split) | `class CodeEnforcerAgent` embedded in types file |
| `L5_safety/types/code_validation_types.py` | types/ | reasoning/ or types/ (split) | `class CodeValidatorAgent` embedded in types file |
| `L5_safety/types/credential_types.py` | types/ | reasoning/ or types/ (split) | `class CredentialScannerAgent` embedded in types file |
| `L5_safety/types/rag_health_check_types.py` | types/ | reasoning/ or types/ (split) | `class RagHealthCheckAgent` embedded in types file |
| `L5_safety/types/resource_types.py` | types/ | reasoning/ or types/ (split) | `class ResourceManagerAgent` embedded in types file |
| `L5_safety/types/safety_detection_types.py` | types/ | reasoning/ or types/ (split) | `class SafetyDetectorAgent` embedded in types file |
| `L5_safety/types/security_types.py` | types/ | reasoning/ or types/ (split) | `class SecurityManagerAgent` embedded in types file |
| `L5_safety/types/structure_enforcement_types.py` | types/ | reasoning/ or types/ (split) | `class StructureEnforcerAgent` embedded in types file |
| `L3_orchestration/config/dag_mutator_config.py` | config/ | reasoning/ or config/ (split) | `class DAGMutatorAgent` embedded in config file |
| `L3_orchestration/validators/dag_runtime_inspector_validator.py` | validators/ | reasoning/ | `class DagRuntimeInspectorAgent` — Agent class in validators/ |
| `L2_execution/config/peer_intelligence_auditor_config.py` | config/ | reasoning/ or config/ (split) | `class PeerIntelligenceAuditorAgent` embedded in config file |
| `L5_safety/enforcement/hygiene_guardian.py` | enforcement/ | reasoning/ | `class HygieneGuardianAgent` — Agent class in enforcement/ |
| `L5_safety/utils/cache_invalidation_util.py` | utils/ | reasoning/ or utils/ (split) | `class HealerAgent` embedded in utility file |
| `L5_safety/validators/naming_validator.py` | validators/ | reasoning/ | `class NamingAgent` — Agent class in validators/ |

### 2.5 L0/scripts PascalCase Agent-Pattern Files (L0 → Various Layers)

These 8 PascalCase files in `L0_maintenance/scripts/` are not scripts/utilities — they are classes that belong elsewhere:

| File | Likely Layer | Evidence |
|------|-------------|----------|
| `AgentAuditResult.py` | L5/types or L0/types | Audit result data class |
| `BatchEmbeddingService.py` | L2/reasoning | Embedding service (external API integration) |
| `GitKrakenHealingStrategy.py` | L0/enforcement or L5/enforcement | Healing strategy pattern |
| `InMemoryVectorCache.py` | L4/memory | In-memory vector cache (state/persistence) |
| `SovereignHealingEngine.py` | L0/reasoning or L5/reasoning | 15KB healing engine agent |
| `SovereignReport.py` | L6/types | Report generation (observability output) |
| `StrategistBioWriter.py` | L1/reasoning or L2/reasoning | Content generation (cognition/execution) |
| `VectorHealingStrategy.py` | L0/enforcement or L5/enforcement | Healing strategy pattern |

### 2.6 Test Files in L0/scripts (L0 → tests/)

| File | Should Be |
|------|-----------|
| `test_boundary_stress_test.py` | `tests/unit/...` or `tests/integration/...` |
| `test_lifecycle_audit.py` | `tests/unit/...` |
| `test_runtime_verify_installation.py` | `tests/integration/...` |
| `test_verify_meta_learning_integration.py` | `tests/integration/...` |
| `test_verify_self_healing.py` | `tests/integration/...` |
| `test_generator_script.py` | `tests/` or keep as script (generates tests) |

### 2.7 L6 Observability File Importing subprocess

| File Path | Current Layer | Functional Layer | Evidence |
|-----------|--------------|-----------------|----------|
| `L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py` | L6 | **L2+L6 Hybrid** | `import subprocess` — runs Playwright for E2E testing (execution behavior in observability domain) |

---

## 3. Logic Gaps in FileClassificationAgent (The "Why")

### 3.1 FCA Sorting Rules Summary

The FCA uses a 15-level priority queue (first match wins):

```
P0:  BASE_AGENT  — path contains "base_agents/"
P1:  STUB        — file contains NOT_AN_AGENT marker
P2.3: DUAL-TAG   — compound suffix conflict → folder context wins
P2.5: SELF       — FileClassificationAgent.py → AGENT
P2.7: BLUEPRINT  — structure_blueprint.py → CONFIG
P3:  TEST        — path has "tests/" or name starts "test_"
P4:  SCRIPT      — functions + __main__, no classes
P5:  EXCEPTION   — class inherits Exception/Error
P6:  MIXIN       — class name ends "Mixin"
P7:  PROTOCOL    — inherits typing.Protocol or I*.py
P8:  ORCHESTRATOR — class contains "Orchestrator"/"Pipeline"
P9:  AGENT       — class ends "Agent" or inherits *Agent
P10: STRATEGY    — class ends "Strategy"
P11: ADAPTER     — class ends "Adapter"/"Wrapper"/"Bridge"
P12: SERVICE     — singleton pattern detected
P13: CONFIG      — name/path contains "config"/"settings"
P14: VALIDATOR   — name/path contains "validator"/"validate"
P15: FACTORY     — class ends "Factory"
P16: TYPES       — TypedDict/Protocol/Enum/dataclass patterns
P17: CLASS       — fallback for any class
P18: UTILITY     — fallback for classless files
```

### 3.2 Identified Logic Gaps

| Gap ID | Rule Issue | Consequence | Example |
|--------|-----------|-------------|---------|
| **G1** | **No layer-level validation** | FCA classifies files by *type* (AGENT, CONFIG, TYPES) but **never validates the L0-L6 layer**. A file can be classified as AGENT and placed in L4 when it functionally belongs in L3. | `L4_state/memory/checkpoint_manager.py` classified AGENT but the FCA doesn't question whether L4 is the right *layer*. |
| **G2** | **Agent class in types/ is invisible** | PRIORITY 2.3 (dual-tag resolution) forces files in `types/` → TYPES via folder context. Agent classes embedded in `_types.py` files are **silently suppressed**. | 9 files in `L5_safety/types/` contain full Agent classes but are classified as TYPES because folder wins. |
| **G3** | **No `scripts/` purity gate** | The FCA has no rule preventing Agent/Strategy/Cache classes from being placed in `scripts/`. If a file has no `__main__` block, it falls through to CLASS/UTILITY — but scripts/ accepts anything. | 8 PascalCase classes in `L0_maintenance/scripts/` (engines, strategies, caches). |
| **G4** | **`Manager` keyword has no routing** | The FCA has no explicit rule for "Manager" classes. `CheckpointManagerAgent` → AGENT (correct by suffix), but `SemanticCacheManager` → CLASS (no Agent suffix, no other match). Neither is checked for L4 vs L3. | `SemanticCacheManager` in L4/memory is correctly placed, but only by coincidence — no rule validates it. |
| **G5** | **Validator keyword is too broad** | The validator detection uses patterns like `"validate"`, `"check"`, `"verify"` — these appear in utility, script, and enforcement files. A file named `validate_dashboard_totals_util.py` matches both VALIDATOR and UTILITY. | 3 misnamed validators in L0/scripts/ (`budget_auditor_validator.py` etc.) — now fixed, but the broad pattern was the root cause. |
| **G6** | **No import-based layer validation** | The FCA never inspects imports to determine functional layer. A file importing `subprocess`, `requests`, or `aiohttp` in L5 is never flagged as potentially belonging in L2. | 12 files in L5 import `subprocess`. Of these, 5 are genuine anomalies. |
| **G7** | **`reasoning/` exclusion in dual-tag creates blind spot** | PRIORITY 2.3 intentionally excludes `reasoning/` from folder-context override. This is correct for reasoning/ files, but means Agent classes in OTHER folders (types/, config/, validators/) get their folder's type instead of AGENT. | The 9 Agent-in-types files and 3 Agent-in-validators files are classified by folder, not by their actual Agent nature. |
| **G8** | **No nested subfolder detection** | The FCA doesn't flag when a leaf domain folder (like `registry/`) sprouts its own LCD-style subfolders (`registry/domain/`, `registry/utils/`). | `prompt_governance/registry/` had nested `domain/` and `utils/` — now fixed but no prevention exists. |

---

## 4. Ambiguous Zones

Files that genuinely straddle two layers based on their functionality:

| File Path | Layer A | Layer B | Reason | Recommended Resolution |
|-----------|---------|---------|--------|----------------------|
| `L5_safety/enforcement/safe_subprocess_handler.py` | L5 (Safety) | L2 (Execution) | Wraps subprocess with safety checks. The **safety wrapping** is L5, the **execution** is L2. | **Keep in L5** — primary purpose is safety enforcement. The subprocess call is the *mechanism*, not the *purpose*. |
| `L5_safety/reasoning/PreCommitSovereignAgent.py` | L5 (Safety) | L2 (Execution) | Safety agent that executes git hooks via subprocess. | **Keep in L5** — pre-commit enforcement is a safety concern. subprocess is the enforcement tool. |
| `L5_safety/reasoning/ArchitectureGovernorAgent.py` | L5 (Safety) | L0 (Maintenance) | Governance agent that reads/validates architecture via subprocess. | **Keep in L5** — governance/validation is the primary purpose. |
| `L3_orchestration/reasoning/UnifiedAgent.py` | L3 (Orchestration) | L5 (Safety) | Orchestration agent with embedded Validator classes. | **Keep in L3** — extract the 3 validator classes to `L5_safety/validators/` or inline them. |
| `L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py` | L6 (Observability) | L2 (Execution) | E2E test runner (execution) for dashboards (observability). | **Keep in L6** — dashboard domain ownership trumps execution behavior. |
| `L5_safety/utils/cache_invalidation_util.py` | L5 (Safety/Utils) | L5 (Safety/Reasoning) | Utility file containing `class HealerAgent`. | **Split** — extract HealerAgent to `L5_safety/reasoning/`, keep cache utility logic in utils. |
| `L4_state/memory/checkpoint_manager.py` | L4 (State/Memory) | L4 (State/Reasoning) | Memory persistence agent with Agent class. | **Move to `L4_state/reasoning/`** — Agent classes belong in reasoning/. |
| `L4_state/memory/gravity_state_store.py` | L4 (State/Memory) | L4 (State/Reasoning) | State store with Agent class. | **Move to `L4_state/reasoning/`** — Agent classes belong in reasoning/. |
| `L4_state/enforcement/cached_state_ledger.py` | L4 (State/Enforcement) | L4 (State/Reasoning) | Enforcement with Agent class. | **Move to `L4_state/reasoning/`** — Agent classes belong in reasoning/. |

### Recommended Tie-Breaking Rule

**"Purpose Over Mechanism"**: When a file straddles two layers, classify by its **primary purpose** (what it achieves), not its **mechanism** (how it achieves it).

- A safety agent that calls `subprocess` to enforce pre-commit hooks → **L5** (purpose = safety enforcement)
- A utility that calls an external API to check dashboard health → **L6** (purpose = observability)
- An orchestration agent with inline validators → **L3** (purpose = orchestration; extract validators)

**"Agent Suffix Wins Subfolder"**: Any file containing `class Foo*Agent(` should be in `reasoning/`, regardless of what other patterns it matches. The `Agent` suffix is the strongest architectural signal.

---

## 5. Orphaned Files

### 5.1 `agentic_core/utils/` — Global Utility Dumping Ground (18 files)

These files are in the global `utils/` folder instead of being placed in a specific L0-L6 layer:

| File | Likely Correct Layer | Evidence |
|------|---------------------|----------|
| `ssot_discovery_util.py` | L0_maintenance/utils | SSOT discovery is a maintenance operation |
| `project_root_util.py` | L0_maintenance/utils or runtime/utils | Project root resolution is infrastructure |
| `tool_registry_util.py` | L2_execution/utils | Tool registry is execution-layer |
| `find_misnamed_agents_util.py` | L0_maintenance/utils | File renaming is maintenance |
| `fix_testing_observability_util.py` | L6_observability/utils | Testing observability fix |
| `guard_ddd_alignment_util.py` | L5_safety/utils | DDD alignment guard is safety/validation |
| `scan_util.py` | L0_maintenance/utils | File scanning is maintenance |
| `canonical_truth_util.py` | L5_safety/utils | Truth/canonical enforcement is safety |
| `scorched_earth_merge_util.py` | L0_maintenance/utils | Merge utility is maintenance |
| `forge_fortress_util.py` | L5_safety/utils | Fortress/hardening is safety |
| `structural_fix_util.py` | L0_maintenance/utils | Structural fixes are maintenance |
| `force_app_depth_util.py` | L5_safety/utils | Depth enforcement is safety |
| `egress_util.py` | L2_execution/utils | Egress handling is execution |
| `component_util.py` | L0_maintenance/utils | Component utility is infrastructure |
| `add_test_coverage_util.py` | L0_maintenance/utils | Test coverage is maintenance |
| `verify_no_mock_data_util.py` | L5_safety/utils | Verification is safety |
| `file_utils_util.py` | L0_maintenance/utils | File utilities are infrastructure |
| `exceptions_util.py` | runtime/exceptions | Exception definitions are runtime types |

### 5.2 `agentic_core/mixins/` — 50 Mixins Without Layer Affinity

The 50 mixins in `agentic_core/mixins/` are cross-cutting concerns (correct by design). However, some have strong layer affinity that could improve discoverability:

| Mixin | Layer Affinity | Evidence |
|-------|---------------|----------|
| `circuit_breaker_mixin.py` | L5 (Safety) | Circuit breaking is a safety/resilience pattern |
| `hallucination_detection_mixin.py` | L5 (Safety) | Hallucination detection is safety |
| `runtime_safety_mixin.py` | L5 (Safety) | Named "runtime safety" — explicitly safety |
| `secrets_management_mixin.py` | L5 (Safety) | Secrets management is security |
| `tracing_mixin.py` | L6 (Observability) | Tracing is observability |
| `metrics_mixin.py` | L6 (Observability) | Metrics is observability |
| `redis_cache_mixin.py` | L4 (State) | Redis cache is state/persistence |
| `pinecone_vector_mixin.py` | L4 (State) | Vector store is state/persistence |
| `semantic_cache_mixin.py` | L4 (State) | Semantic cache is state |
| `embedding_mixin.py` | L2 (Execution) | Embedding calls external APIs |

**Recommendation:** Keep mixins centralized. They are cross-cutting by design. Moving them into layers would create circular dependencies (L5 agent needs L4 mixin that needs L5 validator). The current flat structure is architecturally correct, even if some mixins have clear layer affinity.

### 5.3 L0_maintenance/scripts/ — The 296-File Dumping Ground

**This is the single largest structural debt.** The `scripts/` folder contains:

| Category | Count | Examples |
|----------|-------|---------|
| `*_util.py` scripts | ~185 | `verify_*`, `validate_*`, `audit_*`, `fix_*` |
| `*_script.py` scripts | ~45 | `disposition_script.py`, `colors_script.py` |
| PascalCase classes | 8 | `SovereignHealingEngine.py`, `BatchEmbeddingService.py` |
| Test files (`test_*`) | 6 | `test_boundary_stress_test.py` |
| Non-Python artifacts | ~50 | `.sh`, `.ps1`, `.html`, `.yml`, `.json`, `.md` |
| Dashboard-specific utils | ~25 | `dashboard_*_util.py`, `rca_dashboard_*` |
| Config file | 1 | `agent_analysis_config.py` |

**Root cause:** The FCA classifies by type but doesn't enforce layer boundaries. Any file that classifies as SCRIPT or UTILITY and has no clear layer signal gets dumped into L0/scripts by the healing pass as a catch-all.

---

## 6. Structural Metrics

### Subfolder Compliance

| Layer | Has reasoning/ | Has enforcement/ | Has config/ | Has types/ | Has validators/ | Has utils/ | LCD Score |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| L0_maintenance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6/6 |
| L1_cognition | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6/6 |
| L2_execution | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6/6 |
| L3_orchestration | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6/6 |
| L4_state | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6/6 |
| L5_safety | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6/6 |
| L6_observability | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | 5/6 |

### Top 5 Hotspots (Files Most Likely Misplaced)

1. **L0_maintenance/scripts/** — 296 files, ~30 clearly misplaced (PascalCase agents, test files, dashboard utils)
2. **L5_safety/types/** — 9 files containing full Agent classes suppressed by folder-context classification
3. **agentic_core/utils/** — 18 orphaned utilities that should be distributed to specific layers
4. **L4_state/memory/** — 3 Agent classes that should be in L4/reasoning/
5. **L5_safety/enforcement/** — `dashboard_e2_e_pipeline.py` is execution, not safety enforcement

---

## 7. Recommendations (Prioritized)

### P0 — Critical (Breaks architectural guarantees)

1. **Add layer-level validation to FCA**: After classifying file TYPE, validate that the TARGET LAYER matches the file's functional imports. Flag `subprocess`/`requests` in L5 as anomalies.
2. **Extract Agent classes from types/ files**: The 9 `L5_safety/types/*_types.py` files with embedded Agent classes should either have agents extracted to reasoning/ or the files should be split.
3. **Enforce "Agent → reasoning/" rule**: Any file with `class Foo*Agent(` must be in a `reasoning/` subfolder, regardless of other classification signals.

### P1 — High (Causes ongoing misplacement)

4. **Gate scripts/ folder**: Add purity rule rejecting PascalCase classes and `test_*` files from `scripts/`. Route them to appropriate subfolders.
5. **Move L4 Agent files**: `cached_state_ledger.py`, `checkpoint_manager.py`, `gravity_state_store.py` → `L4_state/reasoning/`.
6. **Move 5 genuine L5 subprocess anomalies** to L2 or add documented exceptions.

### P2 — Medium (Technical debt)

7. **Triage L0/scripts dump**: The 8 PascalCase files and 6 test files need manual triage to correct layers.
8. **Distribute global utils/**: Move 18 orphaned utilities to their natural layers.
9. **Add `DOMAIN_CONTENT_SIGNALS` import-based routing** for files with strong domain keywords (dashboard → L6, embedding → L2).

### P3 — Low (Polish)

10. **Document "Purpose Over Mechanism" tie-breaking** in the FCA docstring.
11. **Add nested-subfolder detection** to prevent leaf domains from sprouting LCD structures.
12. **Consider splitting L0/scripts into L0/scripts + L0/utils** when file count justifies it (currently at 296 — well past the threshold).
