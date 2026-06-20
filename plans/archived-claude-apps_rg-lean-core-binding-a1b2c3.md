---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\apps_rg-lean-core-binding-a1b2c3.md'
original_relative_path: 'apps_rg-lean-core-binding-a1b2c3.md'
source_sha256: 22dec8361a801d668f9ca0bc0eab8ec3282d21be7c594580e51b2953d5303035
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Lean-Core Spine Contract Binding + Authority Collapse

## Zero-Loss Refactor Plan (Revised)

**Plan ID:** `apps_rg_lean_core_binding_a1b2c3`  
**Version:** 2.1.0 (Rebaselined against disk state)  
**Status:** IN PROGRESS (partial execution verified)  
**Created:** 2026-06-07  
**Revised:** 2026-06-07  
**Rebaselined:** 2026-06-07 (statuses re-derived from files on disk)  
**Plan File:** `.cursor/plans/apps_rg-lean-core-binding-a1b2c3.md`

---

## Revision Summary

This revision addresses 10 hardening requirements:

1. **Contract-Symbol Verification:** All illustrative code converted to requirements; only verified symbols from `agentic_core/runtime/contracts` are assumed available
2. **Contract Inventory:** Wave 1A added to inventory existing contracts before facade creation
3. **Placeholder Removal:** No placeholder aliases (RejectedRequest=ValidatedRequest, ExitReviewPacket=dict, etc.)
4. **Import-Boundary Ratchet:** Three-phase approach: (a) inventory violations, (b) block new violations via CI, (c) burn down existing violations
5. **apps_research Migration:** Keep `apps_research_call_required=False` during migration; schema-check before field removal
6. **SectionSpec Defaults:** Changed from `graph_as_claim_proof: true` to `graph_as_routing_support: true` with `graph_as_claim_proof: false` (unless fact-bound)
7. **Fixture/Debug Preserved:** Briefing requirement applies only to `product_visible=True`; fixture/dev with `non_product_certified=True` bypasses briefing check
8. **SectionFrontSpineBridge Cleanup:** Downstream artifacts moved to separate `SectionRunContractBundle`; bridge keeps only front-spine contracts
9. **Wave Reconciliation:** Waves renumbered to 1A, 1B, 2-12; metadata aligned
10. **Provider Staging:** Waves 10A-C: 10A create abstraction, 10B validate parity, 10C make external_default target

---

## Context (SCQA)

**Situation:** apps_rg has grown duplicated authority, hard-wired imports to agentic_core runtime internals, cross-app research delegation complexity, and oversized judge/repair machinery that obscures the core product value.

**Complication:** Direct coupling to agentic_core implementation internals creates brittle architecture, prevents clean spine contract binding, and complicates testing/verification. The apps_research delegation creates cross-app failure modes and briefing fallback that violates product integrity.

**Question:** How can we lean out apps_rg to bind cleanly to spine contracts while preserving graph-grounded career arcs, section debugging, and evidence-bound resume generation?

**Answer:** Execute a 12-wave zero-loss refactor that: (1A) inventories existing contracts, (1B) freezes binding law, (2) creates import-boundary ratchet, (3) removes apps_research delegation, (4) disables R1B semantic cache by default, (5) unifies section/full-run contract paths, (6) consolidates section machinery, (7) documents assumptions with port-based ownership, (8) cleans gate taxonomy, (9) minimizes judges, (10A-C) stages provider changes, (11) reduces artifacts, with comprehensive test matrix.

---

## Status Tables

### Wave Progress

> **Status legend (rebaseline 2026-06-07):** DONE = deliverable verified on disk · DONE (variant) = goal met via a different artifact than the plan specced · PARTIAL = some deliverables present, named gaps remain · NOT STARTED = no deliverable on disk · UNVERIFIED = wave has no concrete deliverable in this file and was not audited this pass.

| Wave | Focus | Status | Priority | Est. Files Changed | Blockers |
|------|-------|--------|----------|-------------------|----------|
| 1A | Contract-Symbol Inventory | DONE (variant) | P0 | 1 | None |
| 1B | Binding Law Documentation | DONE | P0 | 2 | Wave 1A |
| 2 | Import-Boundary Ratchet | DONE | P0 | 6 | Waves 1A-1B |
| 3 | Remove apps_research from Critical Path | DONE | P0 | 12 | Wave 2 |
| 4 | Disable R1B Semantic Cache Default | DONE | P1 | 6 | Wave 3 |
| 5 | One Contract Authority Path | DONE | P1 | 8 | Wave 4 |
| 6 | SectionSpec + SectionRunner Consolidation | DONE | P1 | 20 | Wave 5 |
| 7 | U0 Through Exit Assumption Ledger | DONE | P2 | 2 | Wave 6 |
| 8 | Gate Taxonomy Reset | UNVERIFIED | P2 | 10 | Wave 7 |
| 9 | Judge Minimization + Token Efficiency | VERIFIED | P2 | 8 | Wave 8 |
| 10A | Provider Abstraction Creation | VERIFIED | P2 | 4 | Wave 9 |
| 10B | Provider Parity Validation | NOT STARTED | P2 | 3 | Wave 10A |
| 10C | external_default Target Transition | NOT STARTED | P2 | 3 | Wave 10B |
| 11 | Artifact Diet | VERIFIED | P3 | 4 | Wave 10C |
| 12 | Test Matrix Execution | PARTIAL | P0 | 15 | Waves 1A-11 |

### Rebaseline Evidence (2026-06-07)

| Wave | Evidence on disk | Gap |
|------|------------------|-----|
| 1A | `docs/reports/apps_rg/apps_rg_contract_symbol_inventory.md` | Specced JSON (`artifacts/apps_rg/contract_symbol_inventory.json`) + `tools/apps_rg/inventory_contract_symbols.py` never created — facade cites the markdown instead |
| 1B | `apps_rg/LEAN_CORE.md` (ACTIVE) | — |
| 2 | Binding law **holds in code** — independent AST scan of apps_rg production = **0 forbidden concrete-core imports**. `spine_contracts.py` (verified facade, no placeholder aliases) + `test_spine_contracts_facade.py`; baseline `docs/reports/apps_rg/apps_rg_forbidden_core_import_baseline.json` (0 violations); ratchet `tests/architecture/test_apps_rg_import_boundary_ratchet.py` (correct logic) | **CLOSED 2026-06-07:** ratchet now registered as commit-lane gate `apps-rg-import-boundary-ratchet` (T7v) in `.pre-commit-config.yaml` → block-new enforced (hook Passed). `ports.py` + burn-down doc remain moot (zero violations to migrate). Codex used different filenames than plan specced. |
| 3 | `briefing_u0_signals.py` (`briefing_required_for_run` w/ `product_visible`/`non_product_certified`), `apps_research_call_required_at_u0`, `tools/apps_rg/check_schema_field_usage.py`, `tests/_apps_contract/test_w3_briefing_bypass_gate.py`; `apps_research_call_required` removed from `route_profiles.yaml` | — |
| 4 | `tests/unit/apps_rg/test_r1b_semantic_cache_opt_in.py` proves: no env var → R1B disabled; `bootstrap_apps_rg_embedding_env` no longer sets `SEMANTIC_CACHE_D2_ENABLED`; opt-in only via `APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1`; graph/C0 env preserved. Logic in `apps_rg/runtime/embedding_settings.py` (`semantic_cache_r1b_eligible`) | — |
| 5 | `apps_rg/runtime/spine/section_contract_bundles.py` (`SectionFrontSpineBridge` + `SectionRunContractBundle`) | — |
| 6 | `apps_rg/runtime/sections/section_spec.py` (`graph_as_claim_proof=False`, `graph_as_routing_support=True`, fact-bound guard) | Per-section YAML spec sweep not located at planned path; SectionRunner consolidation not audited |
| 7 | `apps_rg/runtime/contracts/apps_rg_assumptions.yaml` created (17 assumptions, U0→Exit, all 7 stages; YAML valid; 0 owners reference concrete `agentic_core.runtime.*`) | C0/PA/L2/Exit owners name Port interfaces; dedicated `ports.py` still deferred (header note documents this) |
| 8 | `apps_rg/runtime/contracts/gate_taxonomy.py`, `apps_rg/runtime/contracts/apps_rg_gate_taxonomy.yaml`, gate taxonomy tests | Wave 8 taxonomy verified separately; final acceptance row still tracks broader gate classification audit |
| 9 | `apps_rg/runtime/section_cli_defaults.py`, `docs/reports/apps_rg/judge_minimization_wave9.md`, Wave 9 tests | LLM judge defaults compact/non-repairing; full-panel retained only where X2 still requires it |
| 10A | `provider_gateway.py`, `external_provider.py`, `QwenVLLMProvider`, `provider_profiles.yaml` | Qwen remains default; external profiles selectable for Wave 10B parity |
| 10B | none | `tests/integration/providers/test_provider_parity.py` absent |
| 10C | none | depends on 10B |
| 11 | `apps_rg/runtime/artifact_diet.py`, `runtime_proof_layout.py`, `docs/reports/apps_rg/artifact_diet_wave11.md`, `test_artifact_diet_wave11.py` | Executed out of dependency order as a non-destructive manifest diet: legacy links retained; compact proof links + diet receipt added |
| 12 | ratchet + briefing-bypass tests | No consolidated test matrix |

### Risk Register

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R01 | Contract facade incomplete causes import errors | Medium | High | Inventory-first approach; no placeholders |
| R02 | Import-boundary ratchet breaks incremental dev | Low | Medium | Exempt list for gradual migration |
| R03 | apps_research removal breaks existing workflows | Medium | Medium | Keep field=False during migration; schema check first |
| R04 | R1B disable affects perceived performance | Low | Low | Document opt-in procedure |
| R05 | Section consolidation loses independent run capability | Low | High | SectionRunner preserves CLI entrypoints |
| R06 | Gate taxonomy reset weakens product safety | Low | Critical | Test matrix validates every release blocker |
| R07 | Provider parity tests fail on Qwen | Medium | Medium | Keep Qwen as optional; external_default after parity |

---

## Wave 1A — Contract-Symbol Inventory

### Goal
Verify all contract symbols in `agentic_core/runtime/contracts` before creating facade. No placeholder aliases in production code.

### Deliverables

#### 1. Create `artifacts/apps_rg/contract_symbol_inventory.json`

**REQUIREMENT:** Generate exhaustive inventory of all symbols in `agentic_core/runtime/contracts/` before Wave 1.

```json
{
  "inventory_version": "1.0.0",
  "generated_at": "2026-06-07T00:00:00Z",
  "source_path": "agentic_core/runtime/contracts",
  "symbol_categories": {
    "verified_dataclasses": [],
    "verified_protocols": [],
    "verified_type_aliases": [],
    "verified_exceptions": [],
    "missing_expected": [],
    "excess_unexpected": []
  },
  "required_by_apps_rg": {
    "VALIDATED": {
      "ValidatedRequest": {
        "source": "agentic_core/runtime/contracts/apps_rg_ingress_payload.py",
        "class": true,
        "verified": null
      },
      "L1PlanContract": {
        "source": "agentic_core/runtime/contracts/l1_plan_contract.py",
        "class": true,
        "verified": null
      },
      "RouteContract": {
        "source": "agentic_core/runtime/contracts/route_contract.py",
        "class": true,
        "verified": null
      },
      "GraphTraversePolicy": {
        "source": "agentic_core/runtime/contracts/route_contract.py",
        "class": true,
        "verified": null
      },
      "FinalEvidenceContract": {
        "source": "agentic_core/runtime/contracts/final_evidence_contract.py",
        "class": true,
        "verified": null
      },
      "CompiledPromptArtifact": {
        "source": "agentic_core/runtime/contracts/compiled_prompt_artifact.py",
        "class": true,
        "verified": null
      },
      "L3ToL2StepContract": {
        "source": "agentic_core/runtime/contracts/l3_to_l2_step_contract.py",
        "class": true,
        "verified": null
      },
      "SealedL2Artifact": {
        "source": "agentic_core/runtime/contracts/sealed_l2_artifact.py",
        "class": true,
        "verified": null
      },
      "X3Disposition": {
        "source": "agentic_core/runtime/contracts/x3_disposition.py",
        "class": true,
        "verified": null
      }
    },
    "NOT_FOUND": {
      "RejectedRequest": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - define properly or defer"
      },
      "SectionEvidenceContract": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - use FinalEvidenceContract with section context"
      },
      "SealedSectionArtifact": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - use SealedL2Artifact with section context"
      },
      "ExitReviewPacket": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - define properly or use X1CheckoutResult"
      },
      "ExitDispositionReceipt": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - X3Disposition exists; reconcile naming"
      },
      "RuntimeExhaustBundle": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - define properly or defer"
      },
      "CommitRequest": {
        "expected_source": "agentic_core/runtime/contracts",
        "found": false,
        "action": "DO_NOT_ALIAS - use runtime_customization_package"
      }
    }
  },
  "alias_forbidden": [
    "RejectedRequest = ValidatedRequest",
    "SealedSectionArtifact = SealedL2Artifact",
    "ExitReviewPacket = dict",
    "ExitDispositionReceipt = X3Disposition",
    "RuntimeExhaustBundle = dict",
    "CommitRequest = dict"
  ]
}
```

### Acceptance Criteria
- [ ] Inventory script created at `tools/apps_rg/inventory_contract_symbols.py`
- [ ] Inventory output at `artifacts/apps_rg/contract_symbol_inventory.json`
- [ ] All required symbols verified or marked NOT_FOUND
- [ ] No placeholder aliases in facade (remove or properly define)

---

## Wave 1B — Binding Law Documentation

### Goal
Freeze the rules before refactoring. Document binding laws and create architectural guardrails.

### Deliverables

#### 1. Create `apps_rg/LEAN_CORE.md`

**REQUIREMENT:** Document 13 immutable architectural rules.

See file: `apps_rg/LEAN_CORE.md` (already created, verify alignment with revision)

Key additions for this revision:
- Rule 14: No placeholder type aliases in production facade
- Rule 15: Import-boundary ratchet: inventory → block new → burn down
- Rule 16: Contract-symbol verification before facade creation

#### 2. Update `apps_rg/LEAN_CORE.md` Section on Fixture/Dev

**REQUIREMENT:** Preserve fixture/dev section debugging.

```markdown
### Fixture and Development Section Runs

- `non_product_certified=True` bypasses briefing requirement
- `product_visible=False` allows missing briefing (fixture/dev mode)
- Briefing is mandatory ONLY when `product_visible=True` AND active generation mode
- CLI section debugging (`--section` flag) defaults to `product_visible=False` unless `--production` flag set
```

### Acceptance Criteria
- [ ] LEAN_CORE.md created with all 13+ laws
- [ ] Fixture/dev bypass documented
- [ ] Architecture guardrail documented

---

## Wave 2 — Import-Boundary Ratchet

### Goal
Implement three-phase import boundary hardening: inventory violations, block new violations, then burn down existing.

### Deliverables

#### 1. Phase A: Inventory Current Violations

**REQUIREMENT:** Create `artifacts/apps_rg/import_violations_inventory_<timestamp>.json`

```json
{
  "inventory_version": "1.0.0",
  "phases": ["A_inventory", "B_block_new", "C_burn_down"],
  "current_phase": "A",
  "forbidden_patterns": [
    "agentic_core.runtime.entrypoints",
    "agentic_core.runtime.entry",
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.runtime.exit",
    "agentic_core.runtime.judges",
    "agentic_core.runtime.l6"
  ],
  "allowed_patterns": [
    "agentic_core.runtime.contracts"
  ],
  "violations_found": [],
  "exempt_files": [
    "apps_rg/runtime/spine_contracts.py",
    "apps_rg/runtime/ports.py"
  ],
  "migration_priority": {
    "P0": [],
    "P1": [],
    "P2": []
  }
}
```

**Script:** `tools/apps_rg/inventory_import_violations.py`

#### 2. Phase B: Block New Violations (CI Guard)

**REQUIREMENT:** Create `tests/architecture/test_apps_rg_import_boundary_ratchet.py`

```python
"""Import-boundary ratchet: block NEW violations, allow EXISTING with deprecation.

Phase B: Block new violations. Existing violations from inventory are allowed
with deprecation warnings. New violations fail CI.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Set

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
APPS_RG_ROOT = REPO_ROOT / "apps_rg"
INVENTORY_PATH = REPO_ROOT / "artifacts" / "apps_rg" / "import_violations_inventory_latest.json"

# Forbidden concrete agentic_core runtime imports
FORBIDDEN_PATTERNS: Set[str] = {
    "agentic_core.runtime.entrypoints",
    "agentic_core.runtime.entry",
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.runtime.exit",
    "agentic_core.runtime.judges",
    "agentic_core.runtime.l6",
}

# Allowed contract-only imports
ALLOWED_PATTERNS: Set[str] = {
    "agentic_core.runtime.contracts",
}


def load_existing_violations() -> Set[str]:
    """Load existing violations from Phase A inventory."""
    if not INVENTORY_PATH.exists():
        return set()
    data = json.loads(INVENTORY_PATH.read_text())
    return {v["file"] for v in data.get("violations_found", [])}


def get_all_apps_rg_py_files() -> list[Path]:
    """Return all .py files under apps_rg (excluding tests/)."""
    py_files = []
    for path in APPS_RG_ROOT.rglob("*.py"):
        if "test" in path.parts or "tests" in path.parts:
            continue
        rel_path = path.relative_to(REPO_ROOT).as_posix()
        py_files.append((path, rel_path))
    return py_files


def extract_imports(source: str) -> Set[str]:
    """Extract from-import module paths from Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.add(module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
    return imports


def check_forbidden_imports(
    file_path: Path,
    rel_path: str,
) -> list[dict]:
    """Return list of forbidden imports found in file."""
    violations = []
    source = file_path.read_text(encoding="utf-8")
    imports = extract_imports(source)

    for forbidden in FORBIDDEN_PATTERNS:
        for imp in imports:
            if imp.startswith(forbidden):
                violations.append({
                    "file": rel_path,
                    "import": imp,
                    "pattern": forbidden,
                    "line": None,  # Could add line number extraction
                })
    return violations


def test_no_new_forbidden_imports():
    """RATCET PHASE B: Block NEW violations. Existing violations allowed with warning."""
    existing_violations = load_existing_violations()
    py_files = get_all_apps_rg_py_files()

    new_violations: list[dict] = []

    for file_path, rel_path in py_files:
        file_violations = check_forbidden_imports(file_path, rel_path)
        for v in file_violations:
            if v["file"] not in existing_violations:
                new_violations.append(v)

    if new_violations:
        msg = "\n".join(
            f"NEW VIOLATION: {v['file']}: from {v['import']} import ..."
            for v in new_violations
        )
        msg += f"\n\nUpdate {INVENTORY_PATH} to add to existing violations if intentional."
        pytest.fail(msg)


def test_existing_violations_have_tickets():
    """All existing violations must have migration tickets."""
    existing = load_existing_violations()
    for file in existing:
        # Verify each has a migration plan
        pass  # Implementation: check for TODO or ticket reference
```

#### 3. Phase C: Burn Down Existing Violations

**REQUIREMENT:** Gradual migration with sprint goals.

Create `artifacts/apps_rg/import_boundary_burn_down.md`:

```markdown
# Import Boundary Burn-Down

## Sprint Goals

| Sprint | Target Files | Migration Strategy |
|--------|--------------|-------------------|
| 1 | canonical_dispatch.py, u0_binding.py | Create facade, switch imports |
| 2 | x1d_panel_adapters.py, x1d_panel_preflight.py | Use ports.py protocols |
| 3 | l0_binding.py, l1_binding.py | Refactor to facade |
| 4 | c0_binding.py, exit_binding.py | Refactor to facade |
| 5 | Remaining files | Complete migration |

## Per-File Migration Template

### apps_rg/runtime/orchestration/canonical_dispatch.py

**Current Violations:**
- `from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import ...`

**Migration:**
1. Import `SpineRuntimePort` from `apps_rg.runtime.ports`
2. Receive port implementation via dependency injection
3. Remove direct import

**Ticket:** LINK-1234
**Target Sprint:** 1
```

#### 4. Create `apps_rg/runtime/spine_contracts.py` (Verified Symbols Only)

**REQUIREMENT:** Only import verified symbols. No placeholders.

```python
"""Temporary migration facade: re-exports VERIFIED contract types only.

This module is the ONLY permitted import path for spine contracts during migration.
All other apps_rg production modules must import contracts through this facade.

Contract Symbol Verification:
- All symbols here are VERIFIED to exist in agentic_core/runtime/contracts
- See: artifacts/apps_rg/contract_symbol_inventory.json
- If a symbol is needed but not found, DO NOT add placeholder alias.
  Instead: (1) check if it exists under different name, (2) request core addition,
  (3) defer usage until available.

TODO: Migrate to neutral shared contract package.
"""

from __future__ import annotations

# VERIFIED contract types from agentic_core/runtime/contracts
# Source locations verified in Wave 0.1 inventory
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract, GraphTraversePolicy
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition

# NOT VERIFIED - DO NOT ADD PLACEHOLDER ALIASES
# The following are NOT found in agentic_core/runtime/contracts:
# - RejectedRequest: use explicit Optional[ValidatedRequest] or create proper class
# - SectionEvidenceContract: use FinalEvidenceContract with section_id field
# - SealedSectionArtifact: use SealedL2Artifact with section_id field
# - ExitReviewPacket: use X1CheckoutResult (verify in judge_types.py)
# - ExitDispositionReceipt: X3Disposition exists; use that or request rename
# - RuntimeExhaustBundle: define properly in apps_rg or request core addition
# - CommitRequest: use runtime_customization_package flow

__all__ = [
    # Verified dataclasses
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "GraphTraversePolicy",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "L3ToL2StepContract",
    "SealedL2Artifact",
    "X3Disposition",
]
```

#### 5. Create `apps_rg/runtime/ports.py`

**REQUIREMENT:** Protocol interfaces using only verified symbols.

```python
"""Protocol interfaces for spine runtime ports.

apps_rg binds to these protocols, not to concrete agentic_core implementations.

Uses only VERIFIED contract symbols from spine_contracts.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from apps_rg.runtime.spine_contracts import (
        ValidatedRequest,
        CompiledPromptArtifact,
        SealedL2Artifact,
        X3Disposition,
        FinalEvidenceContract,
        GraphTraversePolicy,
    )


@runtime_checkable
class SpineRuntimePort(Protocol):
    """Port for spine runtime operations."""

    def execute_single_action_spine(
        self,
        validated_request: "ValidatedRequest",
        *,
        artifact_dir: Path,
    ) -> Any:  # Returns runtime exhaust; define properly or use Protocol
        ...


@runtime_checkable
class EvidenceResolverPort(Protocol):
    """Port for C0 evidence resolution."""

    def resolve_proof_pool(
        self,
        request: "ValidatedRequest",
        graph_policy: "GraphTraversePolicy | None",
    ) -> "FinalEvidenceContract":
        ...


@runtime_checkable
class PromptCompilerPort(Protocol):
    """Port for PA prompt compilation."""

    def compile_section_prompt(
        self,
        evidence_contract: "FinalEvidenceContract",
        section_spec: "SectionSpec",
    ) -> "CompiledPromptArtifact":
        ...


@runtime_checkable
class ProviderGatewayPort(Protocol):
    """Port for L2 model execution."""

    def generate(
        self,
        compiled_prompt: "CompiledPromptArtifact",
        *,
        provider_profile: str,
        token_budget: int,
    ) -> "SealedL2Artifact":
        ...


@runtime_checkable
class ExitEvaluatorPort(Protocol):
    """Port for Exit evaluation."""

    def evaluate_exit(
        self,
        section_receipts: list["SectionExitReceipt"],
    ) -> "X3Disposition":
        ...


@runtime_checkable
class SectionSpec(Protocol):
    """Protocol for section specification (fully defined in Wave 5)."""

    section_id: str
    provider_budget: int


@runtime_checkable
class SectionExitReceipt(Protocol):
    """Protocol for section exit receipt."""

    section_id: str
    x3_disposition: str
```

### Acceptance Criteria
- [ ] Phase A inventory created
- [ ] Phase B CI guard passes (no new violations)
- [ ] Phase C burn-down plan created
- [ ] spine_contracts.py uses only verified symbols
- [ ] No placeholder aliases in facade
- [ ] All existing violations catalogued with migration tickets

---

## Wave 3 — Remove apps_research from apps_rg Critical Path

### Goal
Eliminate cross-app research delegation and make briefing mandatory for product-visible runs only.

### Deliverables

#### 1. Schema Check Before Field Removal

**REQUIREMENT:** Before removing `apps_research_call_required`, verify no runtime contracts require it.

```python
# tools/apps_rg/check_schema_field_usage.py
"""Verify apps_research_call_required field usage before removal."""

# Check these files for field usage:
CHECK_FILES = [
    "agentic_core/runtime/contracts/apps_rg_ingress_payload.py",
    "agentic_core/runtime/contracts/route_contract.py",
    "agentic_core/runtime/contracts/l1_plan_contract.py",
    "apps_rg/runtime/bindings/l0_binding.py",
    "apps_rg/runtime/bindings/l1_binding.py",
    "apps_rg/runtime/bindings/briefing_u0_signals.py",
]

# If any file references apps_research_call_required as required field,
# migration must keep it (set to False) rather than remove.
```

#### 2. Modify `apps_rg/runtime/bindings/briefing_u0_signals.py`

**REQUIREMENT:** Keep `apps_research_call_required=False` during migration. Require briefing only for product-visible.

```python
"""U0 briefing presence signals for apps_rg L1/L0 planning.

Vocabulary (product):
- ``grounding_required``: resume fact evidence binding (C0.1-C0.7) - always True for active generation.
- ``briefing_required``: targeting briefing is MANDATORY for product-visible active generation modes.
  apps_research delegation is DISABLED. Missing briefing fails closed for product-visible.

Fixture/Dev Bypass:
- If ``non_product_certified=True``, briefing requirement is bypassed
- Section CLI debugging defaults to non_product_certified
"""

from __future__ import annotations

from typing import Any, Mapping

from apps_rg.runtime.spine_contracts import ValidatedRequest

_BRIEFING_REF_KEYS = ("briefing_artifact_ref", "manual_brief_path")


class BriefingMissingError(RuntimeError):
    """Raised when product-visible active generation mode requires briefing but none supplied."""

    def __init__(self, context: str = ""):
        msg = (
            "apps_rg requires an uploaded briefing artifact or authoritative briefing text; "
            "apps_research delegation is disabled."
        )
        if context:
            msg += f" Context: {context}"
        super().__init__(msg)


def briefing_supplied_at_u0(app_payload: Mapping[str, Any] | None) -> bool:
    """True when U0 carried an uploaded path ref or non-empty inline briefing text."""
    # ... existing implementation unchanged ...


def briefing_required_for_run(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
    product_visible: bool = True,
    non_product_certified: bool = False,
) -> bool:
    """Determine if briefing is required for this run.

    Briefing is required when ALL of:
    - active_generation_mode is True
    - product_visible is True
    - non_product_certified is False
    """
    if not active_generation_mode:
        return False
    if not product_visible:
        return False
    if non_product_certified:
        return False
    return not briefing_supplied_at_u0(
        getattr(validated_request, "app_payload", None) or {}
    )


def briefing_validate_or_raise(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
    product_visible: bool = True,
    non_product_certified: bool = False,
    context: str = "",
) -> None:
    """Validate briefing is present for product-visible active generation; fail closed if missing.

    Raises:
        BriefingMissingError: If product-visible active generation mode and briefing not supplied.
    """
    if briefing_required_for_run(
        validated_request,
        active_generation_mode=active_generation_mode,
        product_visible=product_visible,
        non_product_certified=non_product_certified,
    ):
        raise BriefingMissingError(context=context)


# MIGRATION: Keep apps_research_call_required_at_u0 returning False during migration
# Do not remove until schema check confirms no contracts require this field.
def apps_research_call_required_at_u0(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
) -> bool:
    """DEPRECATED: apps_research delegation is disabled. Always returns False.

    This function is kept during migration for schema compatibility.
    Remove only after verifying no runtime contracts require this field.

    See: tools/apps_rg/check_schema_field_usage.py
    """
    return False  # ALWAYS False - delegation disabled


__all__ = [
    "briefing_supplied_at_u0",
    "briefing_required_for_run",
    "briefing_validate_or_raise",
    "BriefingMissingError",
    "apps_research_call_required_at_u0",  # DEPRECATED - keep for migration
]
```

#### 3. Update route_profiles.yaml

**REQUIREMENT:** Change `apps_research_call_required: true` to `apps_research_call_required: false`

```yaml
# BEFORE:
# conditions:
#   apps_research_call_required: true

# AFTER:
# conditions:
#   apps_research_call_required: false
# Note: Field kept for schema compatibility during migration.
#       Will be removed after schema check confirms no dependencies.
```

### Acceptance Criteria
- [ ] Schema check script verifies no contract dependencies on `apps_research_call_required`
- [ ] `apps_research_call_required_at_u0()` returns False (migration compatibility)
- [ ] Briefing requirement applies only when `product_visible=True`
- [ ] Fixture/dev with `non_product_certified=True` bypasses briefing check
- [ ] BriefingMissingError raised with clear message for product-visible missing briefing

---

## Wave 4 — Disable R1B Semantic Cache by Default

*(Unchanged from original plan - see original for details)*

### Acceptance Criteria
- [ ] R1B semantic cache disabled by default (no env var)
- [ ] Normal generation runs when semantic cache env absent
- [ ] R1B activates only with APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1
- [ ] Graph/C0 section proof logic still runs in default mode

---

## Wave 5 — One Contract Authority Path for Section + Full Run

### Goal
Keep section debugging, but stop sections from acting like separate mini-spines.

### Key Revision: Separate SectionRunContractBundle

**REQUIREMENT:** Do not add downstream artifacts to SectionFrontSpineBridge. Create separate bundle.

```python
# apps_rg/runtime/spine/section_contract_bundles.py
"""Contract bundles for section runs.

SectionFrontSpineBridge: U0/L1/L0 contracts only (front-spine)
SectionRunContractBundle: C0/PA/L2/Exit contracts (downstream runtime)
"""

from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.spine_contracts import (
    ValidatedRequest,
    L1PlanContract,
    RouteContract,
    FinalEvidenceContract,
    CompiledPromptArtifact,
    SealedL2Artifact,
    X3Disposition,
)


@dataclass(frozen=True, slots=True)
class SectionFrontSpineBridge:
    """Front-spine contract bundle for a section lane invocation.

    Contains ONLY U0/L1/L0 contracts. No downstream artifacts.
    """

    section_id: str
    validated_request: ValidatedRequest
    l1_plan: L1PlanContract
    route: RouteContract

    # Execution context
    product_visible: bool = True
    fixture_dev_only_bypass: bool = False
    non_product_certified: bool = False

    # Bridge metadata
    spine_lane_mode: str = "section_spine_run"
    is_canonical_c0_path: bool = False
    whole_run_envelope: bool = False

    def contracts_emitted(self) -> dict[str, bool]:
        return {
            "ValidatedRequest": self.validated_request is not None,
            "L1PlanContract": self.l1_plan is not None,
            "RouteContract": self.route is not None,
        }


@dataclass(frozen=True, slots=True)
class SectionRunContractBundle:
    """Downstream contract bundle for section lane runtime.

    Contains C0/PA/L2/Exit contracts. Separate from front-spine bridge.
    """

    # From C0
    evidence_contract: FinalEvidenceContract | None = None

    # From PA
    compiled_prompt: CompiledPromptArtifact | None = None

    # From L2
    sealed_artifact: SealedL2Artifact | None = None

    # From Exit/X2
    section_exit_receipt: "SectionExitReceipt | None" = None
    x3_disposition: X3Disposition | None = None

    def runtime_complete(self) -> bool:
        """True if all runtime stages have emitted contracts."""
        return all([
            self.evidence_contract is not None,
            self.compiled_prompt is not None,
            self.sealed_artifact is not None,
            self.section_exit_receipt is not None,
        ])
```

### Acceptance Criteria
- [ ] SectionFrontSpineBridge contains only U0/L1/L0 contracts
- [ ] SectionRunContractBundle contains C0/PA/L2/Exit contracts
- [ ] Section runs still work independently
- [ ] Full runs still work
- [ ] Both paths use same contract vocabulary

---

## Wave 6 — SectionSpec + SectionRunner Consolidation

### Key Revision: SectionSpec Defaults

**REQUIREMENT:** Change defaults from `graph_as_claim_proof: true` to `graph_as_routing_support: true` with `graph_as_claim_proof: false` (unless fact-bound).

```python
# apps_rg/runtime/sections/section_spec.py

@dataclass(frozen=True)
class SourceAuthoritySpec:
    """Proof source authority configuration.

    Revised per hardening review:
    - graph_as_routing_support: True (graph informs routing decisions)
    - graph_as_claim_proof: False (graph never proves claims)
    - graph_claim_proof_allowed_only_when_fact_bound: True (even if graph_as_claim_proof=True, must be fact-bound)
    - candidate_facts_as_proof: True (only facts prove claims)
    """

    # REVISED: False by default - graph never proves claims
    candidate_facts_as_proof: bool = True

    # REVISED: graph_as_claim_proof defaults to False
    # Graph topology supports routing, but never proves claims
    graph_as_claim_proof: bool = False

    # NEW: Explicit graph routing support (True by default)
    graph_as_routing_support: bool = True

    # NEW: Even when graph_as_claim_proof=True, only allowed when fact-bound
    graph_claim_proof_allowed_only_when_fact_bound: bool = True

    # Unchanged: JD and briefing never proof
    jd_as_proof_allowed: bool = False
    briefing_as_proof_allowed: bool = False
    companion_context_authority: bool = False

    def effective_claim_proof(self, fact_bound: bool = True) -> bool:
        """Determine if graph can prove claims.

        Claims are proven only by:
        1. candidate_facts_as_proof=True AND fact has supporting evidence
        2. graph_as_claim_proof=True AND explicitly fact-bound AND graph_claim_proof_allowed_only_when_fact_bound=True

        Default: graph_as_claim_proof=False, so facts only.
        """
        if self.candidate_facts_as_proof and fact_bound:
            return True
        if self.graph_as_claim_proof and fact_bound and self.graph_claim_proof_allowed_only_when_fact_bound:
            return True
        return False
```

```yaml
# apps_rg/runtime/sections/specs/headline.yaml
# REVISED defaults per hardening review

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: false                           # REVISED: was true
  graph_as_routing_support: true                      # NEW: explicit routing support
  graph_claim_proof_allowed_only_when_fact_bound: true # NEW: safety guard
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false

# Similar changes to all section YAML specs:
# - executive_summary.yaml
# - competencies.yaml
# - unify_bullets.yaml
# - unify_narrative.yaml
# - ibm_bullets.yaml
# - ibm_narrative.yaml
```

### Acceptance Criteria
- [ ] All seven section YAML specs use revised defaults
- [ ] SectionSpec graph_as_claim_proof defaults to False
- [ ] SectionSpec graph_as_routing_support defaults to True
- [ ] SectionSpec graph_claim_proof_allowed_only_when_fact_bound defaults to True
- [ ] Product behavior preserved (graph still informs routing)

---

## Wave 7 — U0 Through Exit Assumption Ledger

### Goal
Re-review assumptions across U0 → Exit and remove unreasonable or duplicate gates. Use port-based ownership, not concrete runtime internals.

### Deliverable

**REQUIREMENT:** Create `apps_rg/runtime/contracts/apps_rg_assumptions.yaml`

Each assumption specifies:
- `assumption_id`: Unique identifier
- `stage`: U0, L1, L0, C0, PA, L2, Exit
- `owner`: Port interface or apps_rg binding module (NOT concrete agentic_core.runtime.*)
- `decision_authority`: What this stage decides
- `input_fields`: Required inputs
- `output_contract`: Contract type produced
- `failure_behavior`: How failures are handled
- `gate_ids`: Associated gate identifiers
- `x3_effect`: Impact on final X3 disposition
- `test_ref`: Test file validating this assumption

```yaml
# apps_rg/runtime/contracts/apps_rg_assumptions.yaml
assumptions:
  # ============================================================================
  # U0 STAGE - Intake Validation
  # ============================================================================
  - assumption_id: U0-001
    stage: U0
    owner: apps_rg.runtime.bindings.u0_binding  # apps_rg binding, not core
    decision_authority: structure_validation
    description: "U0 validates input structure only, does not route"
    input_fields:
      - source_resume_text
      - job_description_text
      - briefing_text (optional for fixture/dev)
    output_contract: ValidatedRequest
    failure_behavior: reject_with_explicit_error
    gate_ids: [U0-G-001]
    x3_effect: none  # X3 not yet reached
    test_ref: tests/unit/apps_rg/test_u0_validation.py

  - assumption_id: U0-002
    stage: U0
    owner: apps_rg.runtime.bindings.u0_binding
    decision_authority: identity_digest
    description: "U0 stamps identity/digests for traceability"
    input_fields:
      - request_id
      - run_id
      - trace_id
      - tenant_id
    output_contract: ValidatedRequest
    failure_behavior: reject
    gate_ids: [U0-G-002]
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_u0_identity.py

  - assumption_id: U0-003
    stage: U0
    owner: apps_rg.runtime.bindings.briefing_u0_signals
    decision_authority: briefing_presence
    description: "U0 validates briefing for product-visible runs; fixture/dev bypass allowed"
    input_fields:
      - briefing_artifact_ref
      - manual_brief_path
      - product_visible (context)
      - non_product_certified (context)
    output_contract: ValidatedRequest
    failure_behavior: fail_closed_for_product_visible
    gate_ids: [U0-G-003]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_briefing_mandatory.py

  # ============================================================================
  # L1 STAGE - Deterministic Planning
  # ============================================================================
  - assumption_id: L1-001
    stage: L1
    owner: apps_rg.runtime.bindings.l1_binding
    decision_authority: deterministic_planning
    description: "L1 deterministic planning, no evidence retrieval, no model calls"
    input_fields:
      - ValidatedRequest
    output_contract: L1PlanContract
    failure_behavior: explicit_ambiguity_register
    gate_ids: [L1-G-001]
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_l1_planning.py

  - assumption_id: L1-002
    stage: L1
    owner: apps_rg.runtime.bindings.l1_binding
    decision_authority: route_hints_advisory
    description: "Route hints are advisory only, never binding authority"
    input_fields:
      - user_constraints.route_hint
    output_contract: L1PlanContract
    failure_behavior: ignore_hint_on_conflict
    gate_ids: []
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_route_hints.py

  # ============================================================================
  # L0 STAGE - Deterministic Routing
  # ============================================================================
  - assumption_id: L0-001
    stage: L0
    owner: apps_rg.runtime.bindings.l0_binding
    decision_authority: deterministic_route
    description: "L0 selects one cheapest safe route deterministically"
    input_fields:
      - L1PlanContract
    output_contract: RouteContract
    failure_behavior: fail_closed
    gate_ids: [L0-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_l0_routing.py

  - assumption_id: L0-002
    stage: L0
    owner: apps_rg.runtime.bindings.l0_binding
    decision_authority: no_retrieval_no_model
    description: "L0 performs no retrieval, no model calls, R1B off by default"
    input_fields: []
    output_contract: RouteContract
    failure_behavior: n/a
    gate_ids: []
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_l0_no_model.py

  # ============================================================================
  # C0 STAGE - Evidence Resolution
  # ============================================================================
  - assumption_id: C0-001
    stage: C0
    owner: apps_rg.runtime.ports.EvidenceResolverPort  # PORT, not concrete
    decision_authority: candidate_facts_proof
    description: "Candidate facts prove claims; graph supports routing unless fact-bound"
    input_fields:
      - source_resume_facts
      - skills_graph
      - role_episode_graph
      - GraphTraversePolicy
    output_contract: FinalEvidenceContract
    failure_behavior: empty_proof_pool
    gate_ids: [C0-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_c0_fact_proof.py

  - assumption_id: C0-002
    stage: C0
    owner: apps_rg.runtime.ports.EvidenceResolverPort
    decision_authority: graph_routing_support
    description: "Graph supports role/phase/skill routing; never proves claims unless fact-bound"
    input_fields:
      - GraphTraversePolicy
      - source_authority.graph_as_routing_support
    output_contract: FinalEvidenceContract
    failure_behavior: fallback_to_facts_only
    gate_ids: [C0-G-002]
    x3_effect: ADVISORY
    test_ref: tests/unit/apps_rg/test_c0_graph_routing.py

  - assumption_id: C0-003
    stage: C0
    owner: apps_rg.runtime.ports.EvidenceResolverPort
    decision_authority: targeting_only
    description: "JD and briefing are targeting only, never proof sources"
    input_fields:
      - job_description_text
      - briefing_text
    output_contract: FinalEvidenceContract
    failure_behavior: n/a  # Used for positioning, never proof
    gate_ids: [C0-G-003]
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_c0_targeting_only.py

  # ============================================================================
  # PA STAGE - Prompt Assembly
  # ============================================================================
  - assumption_id: PA-001
    stage: PA
    owner: apps_rg.runtime.ports.PromptCompilerPort  # PORT, not concrete
    decision_authority: single_compiler_single_shape
    description: "PA uses one compiler, one artifact shape, canonical slot order"
    input_fields:
      - FinalEvidenceContract
      - SectionSpec
    output_contract: CompiledPromptArtifact
    failure_behavior: compilation_error
    gate_ids: [PA-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_pa_compilation.py

  # ============================================================================
  # L2 STAGE - Model Execution
  # ============================================================================
  - assumption_id: L2-001
    stage: L2
    owner: apps_rg.runtime.ports.ProviderGatewayPort  # PORT, not concrete
    decision_authority: provider_execution
    description: "All model calls through ProviderGatewayPort; no direct qwen calls"
    input_fields:
      - CompiledPromptArtifact
      - provider_profile
      - token_budget
    output_contract: SealedL2Artifact
    failure_behavior: provider_error
    gate_ids: [L2-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_l2_provider_port.py

  - assumption_id: L2-002
    stage: L2
    owner: apps_rg.runtime.ports.ProviderGatewayPort
    decision_authority: generation_attempts
    description: "One generation attempt by default; one optional regen if SectionSpec permits"
    input_fields:
      - SectionSpec.max_regen_attempts
      - SectionSpec.allowed_repair
    output_contract: SealedL2Artifact
    failure_behavior: fail_after_max_attempts
    gate_ids: [L2-G-002]
    x3_effect: REVIEW
    test_ref: tests/unit/apps_rg/test_l2_regen_policy.py

  # ============================================================================
  # EXIT STAGE - Disposition Aggregation
  # ============================================================================
  - assumption_id: Exit-001
    stage: Exit
    owner: apps_rg.runtime.ports.ExitEvaluatorPort  # PORT, not concrete
    decision_authority: x1_checkout
    description: "X1 checkout before Exit evaluation"
    input_fields:
      - section_receipts
      - X2 receipts from all sections
    output_contract: X3Disposition  # Using verified core contract
    failure_behavior: checkout_failure
    gate_ids: [Exit-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_exit_x1.py

  - assumption_id: Exit-002
    stage: Exit
    owner: apps_rg.runtime.ports.ExitEvaluatorPort
    decision_authority: x2_aggregation
    description: "X2 deterministic aggregation plus optional judge"
    input_fields:
      - X2 receipts from all sections
      - GateSummary from each section
    output_contract: X3Disposition
    failure_behavior: aggregation_failure
    gate_ids: [Exit-G-002]
    x3_effect: REVIEW
    test_ref: tests/unit/apps_rg/test_exit_x2.py

  - assumption_id: Exit-003
    stage: Exit
    owner: apps_rg.runtime.ports.ExitEvaluatorPort
    decision_authority: x3_disposition
    description: "Exactly one X3 disposition; UNKNOWN is never PASS"
    input_fields:
      - aggregated_X2_results
      - judge_evaluations (optional)
    output_contract: X3Disposition
    failure_behavior: explicit_error
    gate_ids: [Exit-G-003]
    x3_effect: FINAL
    test_ref: tests/unit/apps_rg/test_exit_x3.py

  - assumption_id: Exit-004
    stage: Exit
    owner: apps_rg.runtime.spine.exit_artifacts  # apps_rg binding layer
    decision_authority: section_disposition_mapping
    description: "Section dispositions map into same Exit model via ExitEvaluatorPort"
    input_fields:
      - section_exit_receipts
    output_contract: X3Disposition
    failure_behavior: mapping_error
    gate_ids: [Exit-G-004]
    x3_effect: FINAL
    test_ref: tests/unit/apps_rg/test_section_exit_mapping.py
```

### Stage Rules Summary

| Stage | Decision Authority | Key Constraint | Failure Behavior | Owner (Port-Based) |
|-------|-------------------|----------------|------------------|-------------------|
| U0 | structure_validation | no routing, no inference | reject explicit | apps_rg U0 binding |
| U0 | identity_digest | stamps for traceability | reject | apps_rg U0 binding |
| U0 | briefing_presence | mandatory for product_visible | fail closed | apps_rg briefing signals |
| L1 | deterministic_planning | no evidence retrieval | ambiguity register | apps_rg L1 binding |
| L1 | route_hints | advisory only | ignore on conflict | apps_rg L1 binding |
| L0 | deterministic_route | cheapest safe | fail closed | apps_rg L0 binding |
| L0 | no_retrieval | no model call | n/a | apps_rg L0 binding |
| C0 | candidate_facts_proof | primary authority | empty proof pool | EvidenceResolverPort |
| C0 | graph_routing_support | supports role/phase/skill | fallback to facts | EvidenceResolverPort |
| C0 | targeting_only | JD/briefing never proof | n/a | EvidenceResolverPort |
| PA | single_compiler | one artifact shape | compilation error | PromptCompilerPort |
| L2 | provider_execution | through ProviderGatewayPort | provider error | ProviderGatewayPort |
| L2 | generation_attempts | max 1 regen if permitted | fail after max | ProviderGatewayPort |
| Exit | x1_checkout | checkout before eval | checkout failure | ExitEvaluatorPort |
| Exit | x2_aggregation | deterministic + optional judge | aggregation failure | ExitEvaluatorPort |
| Exit | x3_disposition | exactly one, UNKNOWN != PASS | explicit error | ExitEvaluatorPort |

### Acceptance Criteria
- [ ] Assumption ledger exists at `apps_rg/runtime/contracts/apps_rg_assumptions.yaml`
- [ ] All owners are apps_rg bindings or Port interfaces (NOT concrete agentic_core.runtime.*)
- [ ] Exit stage uses `ExitEvaluatorPort` (port interface), not `agentic_core.runtime.exit`
- [ ] Tests reference assumptions for critical gates
- [ ] Contradictory assumptions removed
- [ ] No stage takes authority from another stage

---

## Wave 8 — Gate Taxonomy Reset

*(Unchanged from original plan - see original for details)*

---

## Wave 9 — Judge Minimization + Token Efficiency

### Goal

Make X1D judge defaults compact and explicit without weakening proof gates.

### Delivered

- Centralized the lane-aware judge default policy in `apps_rg/runtime/section_cli_defaults.py`.
- Added `summarize_section_x1d_minimization_policy()` so tests and closeout reports can inspect the policy without duplicating constants.
- Set advisory/low-risk composite lanes to one default judge:
  - `competencies` -> `gemini_pro`
  - `unify_bullets` -> `anthropic_claude`
  - `ibm_bullets` -> `anthropic_claude`
- Preserved full-panel defaults for lanes whose X2 `x2_x1d_required_judges_present` gates still require the complete provider set:
  - `headline`
  - `unify_narrative`
  - `ibm_narrative`
  - `executive_summary`
  - `final_aggregate_resume`
- Preserved explicit CLI/env overrides for diagnostics and adjudicator escalation.
- Added closeout evidence in `docs/reports/apps_rg/judge_minimization_wave9.md`.

### Acceptance Criteria

- [x] Judge defaults are exported from one policy surface.
- [x] Bullet lanes default to one composite judge.
- [x] Competencies default to one advisory judge and remain optional for proof.
- [x] Full-panel defaults remain where X2 still requires all provider rows.
- [x] Judge packets remain compact `GRADE_ONLY` packets.
- [x] Judge repair/rewrite remains forbidden by packet boundary.
- [x] CLI/env overrides still win.

---

## Wave 10A — Provider Abstraction Creation

### Goal
Create ProviderGateway and profile abstraction. Qwen remains functional.

### Deliverables

#### 1. Create `apps_rg/runtime/providers/provider_gateway.py`

**REQUIREMENT:** Abstract provider interface. No external_default mandate yet.

```python
"""Provider Gateway abstraction for model execution.

Wave 10A: Create abstraction. Both qwen and external providers functional.
Wave 10B: Parity tests validate external = qwen quality.
Wave 10C: external_default becomes default after parity proven.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from enum import Enum

from apps_rg.runtime.spine_contracts import CompiledPromptArtifact, SealedL2Artifact


class ProviderProfile(str, Enum):
    """Provider profile selection.

    Wave 10A: Both functional. Qwen remains default.
    Wave 10C: external_default becomes default after parity tests pass.
    """
    QWEN_VLLM = "qwen_vllm"
    EXTERNAL_CLAUDE = "external_claude"
    EXTERNAL_OPENAI = "external_openai"
    EXTERNAL_DEFAULT = "external_default"  # Wave 10C target


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol for model providers."""

    def generate(
        self,
        compiled_prompt: CompiledPromptArtifact,
        *,
        token_budget: int,
        temperature: float = 0.7,
    ) -> SealedL2Artifact:
        ...


class ProviderGateway:
    """Gateway for provider selection and execution.

    Wave 10A: Creates abstraction. Both qwen and external functional.
    """

    def __init__(self):
        self._providers: dict[ProviderProfile, ModelProvider] = {}

    def register_provider(self, profile: ProviderProfile, provider: ModelProvider) -> None:
        """Register a provider implementation."""
        self._providers[profile] = provider

    def generate(
        self,
        profile: ProviderProfile,
        compiled_prompt: CompiledPromptArtifact,
        *,
        token_budget: int,
    ) -> SealedL2Artifact:
        """Generate via selected provider."""
        if profile not in self._providers:
            raise ValueError(f"Provider not registered: {profile}")
        return self._providers[profile].generate(
            compiled_prompt,
            token_budget=token_budget,
        )
```

#### 2. Create `apps_rg/runtime/providers/qwen_vllm_provider.py`

**REQUIREMENT:** Qwen provider wrapped in new abstraction. Fully functional.

```python
"""Qwen/vLLM provider implementation.

Remains fully functional during Wave 10A-10B.
"""

from apps_rg.runtime.spine_contracts import CompiledPromptArtifact, SealedL2Artifact
from apps_rg.runtime.providers.provider_gateway import ModelProvider


class QwenVLLMProvider(ModelProvider):
    """Qwen/vLLM provider - remains functional during migration."""

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        # Existing qwen initialization

    def generate(
        self,
        compiled_prompt: CompiledPromptArtifact,
        *,
        token_budget: int,
        temperature: float = 0.7,
    ) -> SealedL2Artifact:
        """Generate using Qwen/vLLM."""
        # Existing qwen generation logic wrapped
        pass
```

#### 3. Create `apps_rg/runtime/providers/external_provider.py`

**REQUIREMENT:** External API provider (Claude/OpenAI compatible).

```python
"""External API provider implementation (Claude/OpenAI compatible)."""

from apps_rg.runtime.spine_contracts import CompiledPromptArtifact, SealedL2Artifact
from apps_rg.runtime.providers.provider_gateway import ModelProvider


class ExternalProvider(ModelProvider):
    """External API provider - functional but not default in Wave 10A."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url

    def generate(
        self,
        compiled_prompt: CompiledPromptArtifact,
        *,
        token_budget: int,
        temperature: float = 0.7,
    ) -> SealedL2Artifact:
        """Generate using external API."""
        pass
```

### Acceptance Criteria
- [x] ProviderGateway abstraction created
- [x] QwenVLLMProvider wrapped and functional
- [x] ExternalProvider created and functional
- [x] Both providers can be selected via configuration
- [x] Qwen remains default (no change to current behavior)

### Closeout Evidence

- `apps_rg/runtime/providers/provider_gateway.py`
- `apps_rg/runtime/providers/external_provider.py`
- `apps_rg/runtime/providers/qwen_vllm_provider.py`
- `apps_rg/config/provider_profiles.yaml`
- `tests/unit/apps_rg/test_provider_gateway_wave10.py`
- `docs/reports/apps_rg/provider_abstraction_wave10a.md`

---

## Wave 10B — Provider Parity Validation

### Goal
Validate external provider parity with Qwen before making external_default the target.

### Deliverables

#### 1. Create `tests/integration/providers/test_provider_parity.py`

**REQUIREMENT:** Parity tests comparing external vs Qwen outputs.

```python
"""Provider parity validation tests.

Wave 10B: Validate external provider quality equals or exceeds Qwen.
Must pass before Wave 10C (external_default target).
"""

import pytest
from apps_rg.runtime.providers.provider_gateway import ProviderGateway, ProviderProfile
from apps_rg.runtime.providers.qwen_vllm_provider import QwenVLLMProvider
from apps_rg.runtime.providers.external_provider import ExternalProvider


@pytest.fixture
def gateway():
    g = ProviderGateway()
    g.register_provider(ProviderProfile.QWEN_VLLM, QwenVLLMProvider())
    g.register_provider(ProviderProfile.EXTERNAL_CLAUDE, ExternalProvider())
    return g


def test_headline_generation_parity(gateway):
    """Headline section generates equivalent quality via external vs Qwen."""
    # Compare outputs for same input
    pass


def test_executive_summary_parity(gateway):
    """Executive summary generates equivalent quality via external vs Qwen."""
    pass


def test_competencies_parity(gateway):
    """Competencies section generates equivalent quality via external vs Qwen."""
    pass


def test_all_sections_parity_suite(gateway):
    """All 7 sections pass parity threshold.

    Threshold: External output quality score >= Qwen quality score - 0.05
    """
    pass
```

#### 2. Create Parity Report Template

```markdown
# Provider Parity Report

| Section | Qwen Score | External Score | Delta | Pass |
|---------|-----------|---------------|-------|------|
| headline | 0.92 | 0.91 | -0.01 | ✓ |
| executive_summary | 0.88 | 0.89 | +0.01 | ✓ |
| competencies | 0.90 | 0.90 | 0.00 | ✓ |
| ... | | | | |

**Overall**: PASS / FAIL
**Recommendation**: Proceed to Wave 10C / Fix parity gaps
```

### Acceptance Criteria
- [ ] Parity test suite created
- [ ] All 7 sections tested
- [ ] Quality threshold defined (external >= Qwen - 0.05)
- [ ] Parity report template
- [ ] Wave 10C conditional on parity PASS

---

## Wave 10C — external_default Target Transition

### Goal
Make external_default the default provider after parity proven.

### Deliverables

#### 1. Update Default Provider Selection

**REQUIREMENT:** Only after Wave 10B parity PASS.

```python
# In apps_rg/config/domain_contract/provider_profiles.yaml

# Wave 10A-10B:
default_provider: qwen_vllm

# Wave 10C (after parity PASS):
default_provider: external_default
```

#### 2. Create Migration Notice

```markdown
# Provider Default Migration Notice

**Date**: [After Wave 10C]
**Change**: Default provider changed from Qwen to external_default

**Qwen Status**: Still supported as optional local provider
**Migration**: Set `provider_profile: qwen_vllm` in config to keep Qwen
```

### Acceptance Criteria
- [ ] Default provider changed to external_default
- [ ] Qwen remains supported as optional
- [ ] Parity tests continue to pass (CI guard)
- [ ] Migration notice published

---

## Wave 11 — Artifact Diet

**Status**: VERIFIED 2026-06-07.

Wave 11 was executed out of dependency order after Wave 10A. Because Wave 10B provider parity and Wave 10C default transition remain open, this wave intentionally avoids destructive artifact deletion or default-provider behavior changes.

### Delivered
- Added `apps_rg/runtime/artifact_diet.py` as the artifact classification SSOT.
- Preserved legacy `artifact_links` in runtime proof manifests and latest-run pointers.
- Added `artifact_links_compact` for reader-facing proof surfaces.
- Added `artifact_diet` receipt metadata with proof-core, optional-proof, heavy-diagnostic, and unknown buckets.
- Retained heavy diagnostic artifacts on disk while excluding them from compact links:
  - `compiled_prompt.txt`
  - `command_output.txt`
  - `provider_response.json`
  - `parsed_output.json`
  - `prompt_selection_trace.json`
- Published receipt: `docs/reports/apps_rg/artifact_diet_wave11.md`.

### Acceptance Criteria
- [x] Runtime proof manifests expose compact artifact links.
- [x] Latest successful real-run pointers expose compact artifact links.
- [x] Legacy artifact links are retained for backwards compatibility.
- [x] Heavy diagnostics are retained on disk but removed from compact proof surfaces.
- [x] Focused Wave 11 tests cover policy classification and manifest/pointer emission.

---

## Wave 12 — Test Matrix

*(Updated to include new test requirements from revisions)*

### Additional Test Requirements

#### Import-Boundary Ratchet Tests
```python
def test_no_new_forbidden_imports():
    """Phase B: No new import violations allowed."""


def test_existing_violations_have_migration_tickets():
    """All existing violations catalogued with tickets."""
```

#### Contract Symbol Verification Tests
```python
def test_spine_contracts_no_placeholder_aliases():
    """No placeholder type aliases in spine_contracts facade."""


def test_all_exported_symbols_verified():
    """All symbols in __all__ exist in agentic_core contracts."""
```

#### Fixture/Dev Briefing Bypass Tests
```python
def test_fixture_dev_bypasses_briefing_requirement():
    """non_product_certified=True bypasses briefing check."""


def test_product_visible_requires_briefing():
    """product_visible=True with non_product_certified=False requires briefing."""
```

#### Provider Staging Tests
```python
def test_provider_abstraction_functional():
    """Both Qwen and external providers functional via abstraction."""


def test_parity_threshold_met():
    """External provider meets parity threshold vs Qwen."""
```

---

## Final Acceptance Criteria

apps_rg lean-core target is complete when (checkboxes rebaselined 2026-06-07 against disk — `[~]` = partial/variant):

1. [x] Import-boundary ratchet implemented (block-new gate `apps-rg-import-boundary-ratchet` registered in pre-commit; inventory baseline = 0 violations; burn-down moot)
2. [x] Contract-symbol inventory complete; no placeholder aliases in facade (inventory is markdown, not specced JSON)
3. [x] apps_rg binds to spine contracts, not concrete internals (facade present; 0 forbidden concrete-core imports, enforced by ratchet gate; ports.py moot)
4. [x] Import-boundary CI proves the binding law (blocks new violations)
5. [ ] Graph skills remain mandatory and observable (not audited this pass)
6. [x] Section debugging remains intact with fixture/dev bypass
7. [x] apps_research is removed from apps_rg critical path (returns False during migration)
8. [x] Briefing is mandatory only for product-visible runs; fixture/dev bypass preserved
9. [x] R1B semantic output shortcut is disabled by default (proven by `test_r1b_semantic_cache_opt_in.py`)
10. [x] section and full-run paths share the same contract family
11. [x] SectionFrontSpineBridge contains only front-spine contracts; downstream in separate bundle
12. [~] SectionSpec + SectionRunner remove duplicated mini-spines (spec done; runner consolidation unaudited)
13. [x] SectionSpec defaults: graph_as_routing_support=true, graph_as_claim_proof=false
14. [ ] gates are classified as release blocker, advisory, or debug metric (Wave 8 unaudited)
15. [x] LLM judges are compact, rare, and non-repairing (Wave 9 policy + tests)
16. [x] Provider abstraction created (Wave 10A verified)
17. [ ] Provider parity validated (Wave 10B — not started)
18. [ ] external_default becomes default after parity (Wave 10C — not started)
19. [x] Runtime proof artifacts expose a compact reader-facing surface while preserving heavy diagnostics on disk (Wave 11)
20. [ ] full run emits one coherent X3 disposition (not audited this pass)
21. [ ] no durable writes occur outside UWG (not audited this pass)
22. [ ] L6 remains post-run only (not audited this pass)

---

## Deletion/Quarantine Table

| File/Pattern | Wave | Action | Replacement | Rollback Note |
|--------------|------|--------|-------------|---------------|
| `apps_research_bridge.py` | 2 | QUARANTINE | None (briefing mandatory) | Keep for reference, add deprecation warning |
| `managed_research_delegation.py` | 2 | QUARANTINE | None | Same as above |
| `briefing_mode_classifier.py` | 2 | REVIEW | Inline validation | Check for non-delegation uses |
| `c0_briefing_bypass.py` | 2 | DELETE | None | N/A |
| apps_research route profile | 2 | MODIFY (to False) | `apps_research_call_required: false` | Remove field after schema check |
| per-section PA wrappers | 5 | DELETE | SectionRunner | Migrate to common runner |
| per-section dispatch wrappers | 5 | DELETE | SectionRunner | Migrate to common runner |
| duplicated section_contract YAML | 5 | DELETE | SectionSpec YAML | Consolidate to specs/ |
| lane_runtime + lane_execution split | 5 | CONSOLIDATE | SectionRunner.run() | Single lifecycle method |
| per-lane infer_product_quality | 5 | DELETE | common X2 validator | Consolidate validators |
| `executive_summary_judge_regen_loop.py` | 8 | QUARANTINE | Deterministic X2 | Move to calibration/tools |
| `qwen_vllm_provider.py` direct calls | 10A | WRAP in abstraction | ProviderGateway | Qwen still functional |

---

## Explicit Non-Goals

(Unchanged from original plan)

---

## Rollback Notes

### Wave 1A Rollback
```bash
# If contract inventory reveals unexpected gaps:
git checkout HEAD -- artifacts/apps_rg/contract_symbol_inventory.json
# Extend timeline for core contract additions
```

### Wave 1 Rollback
```bash
# If import-boundary ratchet breaks CI:
export IMPORT_BOUNDARY_RATChet_BYPASS=1  # Emergency only
# Or restore to Phase A (inventory only)
```

### Wave 2 Rollback
```bash
# If briefing mandatory breaks workflows:
git checkout HEAD -- apps_rg/runtime/bindings/briefing_u0_signals.py
# Keep apps_research_call_required returning False during investigation
```

### Wave 10 Rollback
```bash
# If provider parity fails:
# Stay on Wave 10A (abstraction created, both functional)
# Fix external provider quality
# Re-run Wave 10B before 10C
```

---

## Plan Metadata

```yaml
plan_id: apps_rg_lean_core_binding_a1b2c3
version: 2.1.0
revision_date: 2026-06-07
rebaseline_date: 2026-06-07
status: IN_PROGRESS
waves_done: [1A, 1B, 2, 3, 4, 5, 6, 7]
waves_partial: [12]
waves_not_started: [10A, 10B, 10C]
waves_unverified: [8, 9, 11]
waves: 12 (1A, 1B, 2-11, 10A/B/C substages)
files_new: 38 (+5 from revision)
files_modified: 60 (+2 from revision)
files_deleted: 9
files_quarantined: 6
zero_loss: true
binding_law: apps_rg/LEAN_CORE.md
notion_plan_slug: apps_rg_lean_core_binding_a1b2c3
hardening_review: 10 points addressed
```

---

## PLAN_REVISED

**PLAN_REVISED:** slug=apps_rg_lean_core_binding_a1b2c3 version=2.0.0 waves=12

**Revision Checklist:**
- [x] 1. Illustrative code → requirements unless symbols verified
- [x] 2. Contract-symbol inventory added (Wave 1A)
- [x] 3. Placeholder aliases removed (no RejectedRequest=ValidatedRequest, etc.)
- [x] 4. Import-boundary ratchet (Phase A/B/C)
- [x] 5. apps_research_call_required=False during migration; schema check first
- [x] 6. SectionSpec defaults: graph_as_routing_support=true, graph_as_claim_proof=false
- [x] 7. Fixture/dev preserved: briefing only for product_visible
- [x] 8. SectionRunContractBundle created; SectionFrontSpineBridge cleaned
- [x] 9. Waves reconciled: 1A, 1B, 2-11, 10A/B/C
- [x] 10. Provider staged: 10A abstraction, 10B parity, 10C external_default
