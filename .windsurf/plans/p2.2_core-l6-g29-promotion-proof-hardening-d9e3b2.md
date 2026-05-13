---
plan_id: core-l6-g29-promotion-proof-hardening-d9e3b2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

> [!IMPORTANT]
> PORTFOLIO_STATUS: CONSOLIDATED_UNDER_MASTER
> MASTER_PLAN_REF: .windsurf/plans/apps-rg-master-governed-runtime-hardening.md
> DISPOSITION: ACTIVE_SEPARATE_CORE_PLAN
> SUPERSEDED_BY_PHASES: Phase 4B and downstream Phase 12 verification
> RETAINED_SCOPE:
> - PromotionGauntlet.GATE_ID
> - L6GauntletResult.gate_id
> - FutureRunPromotionRequest proof fields
> - generic L4 namespace parser
> MOVED_SCOPE:
> - apps_rg-local L6 handoff tests are in Master Phase 12
> DEFERRED_SCOPE:
> - None
> CONFLICTS_RESOLVED:
> - Owns generic core G29/promotion/L4 parser work. apps_rg plans must not duplicate these core edits.

## Portfolio Consolidation Notes
This plan remains an active separate core-enabling plan. It is referenced by the master plan for Phase 4B (Core G29/L4 namespace parser) and Phase 12 verification. No consolidation changes to this plan's scope.

---

# Core L6 G29 Promotion & Proof Hardening — Generic Contract Evolution

Add G29 gate identifier to PromotionGauntlet, extend FutureRunPromotionRequest with proof fields, and create generic L4 namespace contract parser. These are agentic_core generic contract changes enabling all apps (including apps_rg) to have proper promotion validation and L4 namespace governance.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — `agentic_core/L6_learning/promotion_gauntlet.py` lacks canonical gate identifier. `FutureRunPromotionRequest` lacks proof fields required for mission-critical promotion validation. No generic L4 namespace contract parser exists for apps to supply typed, versioned, ACL-bound read surface manifests.

- **Complication** — Without G29 gate ID, gauntlet decisions cannot be tracked in closed-loop router ledger per constitutional §29. Without proof fields, promotion requests cannot validate required evidence (completed eval record, RCA packet, audit manifest). Without generic L4 namespace parser, each app would need to hardcode validation logic.

- **Question** — How do we evolve core L6 contracts to support proper gate identification, proof validation, and generic L4 namespace parsing for all apps?

- **Answer** — Implement 3 waves: W1 adds G29 gate ID to PromotionGauntlet and proof fields to FutureRunPromotionRequest; W2 creates generic L4 namespace contract parser in agentic_core; W3 adds core tests and verifies companion apps_rg plan tests pass. All changes are generic (no app-specific literals) and reusable across all apps_*.

---

## Wave Overview

**Waves**: 3 total (W1–W3)
**Total Estimate**: ~8K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — G29 Gate ID & Promotion Proof Fields | ~3K tokens | Checkpoint A | STATUS: TODO
- **W2** — Generic L4 Namespace Contract Parser | ~3K tokens | Checkpoint B | STATUS: TODO
- **W3** — Core Tests & Cross-Plan Verification | ~2K tokens | Checkpoint C | STATUS: TODO

---

## Pre-Flight (W0) — Author-Gate Receipt Capture

**W0 Acceptance** (MUST complete before W1 modifications):
- CoreAdditionAuthorGateReceipt exists at `artifacts/governance/core_addition_author_gate_receipt.json`
- Receipt verdict = PASS
- Receipt explicitly covers:
  - `PromotionGauntlet.GATE_ID`
  - `L6GauntletResult.gate_id`
  - `FutureRunPromotionRequest` proof fields
  - L4 namespace parser module
- No code changes under `agentic_core/` before receipt capture
- Receipt capture command: `python tools/capture/core_addition_receipt.py --plan core-l6-g29-promotion-proof-hardening`

---

## Wave 1 — G29 Gate ID & Promotion Proof Fields

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: A

**Authorization**: REQUIRED — Modifies shared core contracts (PromotionGauntlet, FutureRunPromotionRequest).

**Author-Gate Trigger**: core_addition_author_gate_required=true per constitutional §32. Requires CoreAdditionAuthorGateReceipt with verdict=PASS (captured in W0).

**Phases**:
- **W1.1** — Add `GATE_ID = "G29"` to PromotionGauntlet | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Add `gate_id: str` to L6GauntletResult with default "" | ~0.7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Populate gate_id in `run_gauntlet()` return | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — Add proof fields to FutureRunPromotionRequest | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.5** — Add gauntlet checks for proof refs | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W1.4 Proof Fields**:
```python
@dataclass(frozen=True)
class FutureRunPromotionRequest:
    # ... existing fields ...
    # W1.4 new proof fields (default "" for backward compat)
    completed_eval_record_ref: str = ""      # ref to CompletedEvalRecord
    rca_packet_ref: str = ""                # ref to RCAPacket
    audit_manifest_ref: str = ""              # ref to AuditManifest
    # Future-proof: calibration_proof_ref for judge/evaluator changes
    calibration_proof_ref: str = ""           # ref to CalibrationCertificate
```

**W1.5 Gauntlet Checks (Hardened)**:
- Check 7: `audit_manifest_ref` **required** for every FutureRunPromotionRequest (no exceptions)
- Check 8: `completed_eval_record_ref` **required** for every promotion derived from completed runtime exhaust
- Check 9: `rca_packet_ref` **required** for any corrective/pattern/policy/prompt/rubric/evaluator/cache/index change
- Check 10: `calibration_proof_ref` **required** for judge/evaluator changes if field present (future-proof)

**Acceptance**:
- `PromotionGauntlet.GATE_ID == "G29"` (class constant)
- `L6GauntletResult.gate_id` field exists, populated by `run_gauntlet()`
- `FutureRunPromotionRequest` has proof fields with defaults
- Gauntlet fails if proof refs missing for applicable promotion types
- Tests: `pytest tests/unit/agentic_core/L6_learning/test_promotion_gauntlet.py -v` passes
- CoreAdditionAuthorGateReceipt emitted and captured

---

## Wave 2 — Generic L4 Namespace Contract Parser

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Authorization**: REQUIRED — Creates new core contract module.

**Phases**:
- **W2.1** — Create `agentic_core/L4_state/contracts/l4_namespace_contract.py` | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Add L4NamespaceManifest dataclass with surface types | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Add parser/validator for YAML/JSON manifests | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W2.1 Contract Design (Expanded Fields)**:
```python
@dataclass(frozen=True)
class L4ReadSurface:
    surface_id: str
    surface_type: str                          # cache, vector_index, graph_projection, etc.
    schema_version: str
    schema_ref: str                            # URL or path to schema definition
    acl_profile: str
    authority_class: str                       # runtime, offline, admin, etc.
    replay_key_pattern: str
    audit_manifest_ref: str
    lineage_required: bool = True
    retention_policy: str
    allowed_operations: tuple[str, ...]        # query, get, search, etc.
    writer_policy: str = ""                    # UWG-mediated | admin-only | offline-only
    read_policy: str = "governed"              # governed | audited | open
    owner_app_id: str = ""                     # namespace owner
    pii_or_sensitive_data_class: str = ""      # pii | financial | healthcare | none

@dataclass(frozen=True)
class L4NamespaceManifest:
    app_id: str
    version: str
    surfaces: tuple[L4ReadSurface, ...]

class L4NamespaceParser:
    @staticmethod
    def parse_yaml(path: Path) -> L4NamespaceManifest: ...
    @staticmethod
    def validate(manifest: L4NamespaceManifest) -> ValidationResult: ...
```

**W2.3 Validation Failures**:
- surface_id duplicate → ValidationError
- unknown surface_type → ValidationError  
- missing schema_version → ValidationError
- missing ACL profile → ValidationError
- missing replay key pattern → ValidationError
- missing audit ref → ValidationError
- write-capable surface lacks writer_policy → ValidationError
- allowed_operations includes write/mutate but writer_policy does not route through UWG → ValidationError

**Generic Principle**: No app-specific literals. Parser works for any app supplying manifest.

**No App Literals Protection**:
- `grep -r "apps_rg" agentic_core/L4_state/contracts/` must return zero
- Core parser tests use neutral fixture app ids like `sample_app`, `test_app_1`
- Cross-plan integration tests may parse apps_rg/config, but core correctness tests must not depend on apps_rg

**Acceptance**:
- `L4NamespaceManifest` dataclass exists with 14 surface fields
- Parser validates manifest shape (no app-specific hardcoding)
- Core tests use generic fixtures only:
  - `tests/fixtures/l4_namespace_manifest_valid.yaml`
  - `tests/fixtures/l4_namespace_manifest_invalid.yaml`
- Cross-plan verification can additionally parse apps_rg/config, but core tests pass without it
- `grep -r "apps_rg" agentic_core/L4_state/contracts/` returns zero
- Tests: `pytest tests/unit/agentic_core/L4_state/contracts/test_l4_namespace_contract.py -v` passes
- CoreAdditionAuthorGateReceipt emitted for new contract module

---

## Wave 3 — Core Tests & Cross-Plan Verification

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Add core tests for G29 gate | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Add core tests for proof fields | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — Verify companion apps_rg plan tests pass | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.4** — Run full contract gate suite | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W3.3 Cross-Plan Verification (Downstream Only)**:
- Run `pytest tests/_apps_contract/test_w4_core_field_expectations.py` (from apps_rg plan)
- Tests should pass now that core fields exist
- If tests fail, sync with apps_rg plan author
- **apps_rg W4 tests are downstream verification only and must not drive additional core scope**

**Acceptance**:
- `pytest tests/unit/agentic_core/L6_learning/ -v` passes (G29, proof fields)
- `pytest tests/unit/agentic_core/L4_state/contracts/ -v` passes (namespace contract)
- Companion apps_rg plan tests pass (`pytest tests/_apps_contract/ -k "core_field" -v`)
- `python ops_scripts/ci/run_contract_gates.py` exits 0 (no new violations)
- CoreAdditionAuthorGateReceipt captured for both W1 and W2

---

## Out Of Scope

- apps_rg-specific changes (in companion plan `apps-rg-l4-boundary-hardening-c8f2a1`)
- UWG implementation changes (assumed exists)
- L4 StateStore mutation logic (assumed exists)
- Specific audit manifest schemas (generic contract only)
- Chroma/vector store implementation details (surface type only)

---

## Gap Register

**GAP-C1: Missing G29 Gate Identifier**
- Location: `agentic_core/L6_learning/promotion_gauntlet.py`
- Impact: Cannot track gauntlet decisions in closed-loop router ledger per §29
- Close criteria: `GATE_ID = "G29"` present, populated in results

**GAP-C2: Missing Promotion Proof Fields**
- Location: `agentic_core/L6_learning/__init__.py:FutureRunPromotionRequest`
- Impact: Cannot validate required evidence for mission-critical promotions
- Close criteria: Proof fields present, gauntlet checks enforce them

**GAP-C3: Missing Generic L4 Namespace Parser**
- Location: `agentic_core/L4_state/contracts/` (missing)
- Impact: Apps cannot supply typed, versioned, ACL-bound read surface manifests
- Close criteria: Generic parser exists, validates any app manifest without hardcoding

---

## Execution Details

### W1.1 — Add GATE_ID to PromotionGauntlet
**Scope**: Add class constant `GATE_ID = "G29"`
**Files**: `agentic_core/L6_learning/promotion_gauntlet.py`
**Commands**:
```bash
python -c "from agentic_core.L6_learning.promotion_gauntlet import PromotionGauntlet; assert PromotionGauntlet.GATE_ID == 'G29'"
```

### W1.4 — Add Proof Fields
**Scope**: Extend FutureRunPromotionRequest dataclass
**Files**: `agentic_core/L6_learning/__init__.py`
**Commands**:
```bash
python -c "from agentic_core.L6_learning import FutureRunPromotionRequest; f = FutureRunPromotionRequest(...); assert hasattr(f, 'completed_eval_record_ref')"
```

### W2.1 — Create L4 Namespace Contract
**Scope**: New module with parser/validator
**Files**: `agentic_core/L4_state/contracts/l4_namespace_contract.py` (new)
**Commands** (generic fixture-based, not apps_rg):
```bash
python -c "from pathlib import Path; from agentic_core.L4_state.contracts.l4_namespace_contract import L4NamespaceParser; m = L4NamespaceParser.parse_yaml(Path('tests/fixtures/l4_namespace_manifest_valid.yaml')); assert m.app_id == 'sample_app'"
```

---

## Definition of Done

DoD-1: G29 gate identifier present and populated
- Evidence: `python -c "from agentic_core.L6_learning.promotion_gauntlet import PromotionGauntlet; print(PromotionGauntlet.GATE_ID)"` outputs "G29"
- Status: TODO

DoD-2: FutureRunPromotionRequest proof fields present with defaults
- Evidence: `python -c "from agentic_core.L6_learning import FutureRunPromotionRequest; print([f for f in FutureRunPromotionRequest.__dataclass_fields__ if '_ref' in f])"` lists proof fields
- Status: TODO

DoD-3: Smoke-run tests pass
- Evidence: `pytest tests/unit/agentic_core/L6_learning/test_promotion_gauntlet.py -v` exits 0
- Status: TODO

DoD-4: CI gates green / no new violations
- Evidence: `python ops_scripts/ci/run_contract_gates.py` exits 0
- Status: TODO

DoD-5: CoreAdditionAuthorGateReceipt captured
- Evidence: Receipt exists at `artifacts/governance/core_addition_author_gate_receipt.json`
- Status: TODO

DoD-6: Cross-plan tests pass (companion apps_rg plan)
- Evidence: `pytest tests/_apps_contract/test_w4_core_field_expectations.py -v` passes
- Status: TODO

---

## Companion Plan Linkage

**Depends on**: None (this is the core-enabling plan)
**Enables**: `apps-rg-l4-boundary-hardening-c8f2a1` W4 (core field expectations)
**Sequence**: This plan W1-W2 must complete before apps_rg plan W4 tests can pass
**Sync mechanism**: Core field tests in apps_rg plan xfail gracefully until this plan lands

---

## Scope Expansion Authorization

Per plan-lifecycle-procedures.md §2:

**DISCOVERED_SCOPE** marker required for any new core contract surfaces.
**AUTHORIZATION_DECISION** required before modifying agentic_core beyond W1-W2 scope.

This plan is intentionally bounded to G29 + proof fields + L4 namespace parser. Any additional core contract changes require new plan.

---

## Cascade Alignment Checks

- All changes are generic (no app_id literals)
- L4 namespace parser validates any app manifest without hardcoding
- CoreAdditionAuthorGateReceipt required and will be captured
- Tests verify both core correctness and companion plan compatibility
