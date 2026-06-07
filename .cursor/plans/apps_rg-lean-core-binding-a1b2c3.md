# apps_rg Lean-Core Spine Contract Binding + Authority Collapse

## Zero-Loss Refactor Plan

**Plan ID:** `apps_rg_lean_core_binding_a1b2c3`  
**Status:** NOT STARTED → REGISTERED  
**Created:** 2026-06-07  
**Target Completion:** TBD (wave-based execution)  
**Plan File:** `docs/reports/apps_rg/apps_rg_lean_core_contract_binding_plan.md`  

---

## Context (SCQA)

**Situation:** apps_rg has grown duplicated authority, hard-wired imports to agentic_core runtime internals, cross-app research delegation complexity, and oversized judge/repair machinery that obscures the core product value.

**Complication:** Direct coupling to agentic_core implementation internals creates brittle architecture, prevents clean spine contract binding, and complicates testing/verification. The apps_research delegation creates cross-app failure modes and briefing fallback that violates product integrity.

**Question:** How can we lean out apps_rg to bind cleanly to spine contracts while preserving graph-grounded career arcs, section debugging, and evidence-bound resume generation?

**Answer:** Execute an 11-wave zero-loss refactor that: (1) freezes binding law, (2) creates contract facade, (3) removes apps_research delegation, (4) disables R1B semantic cache by default, (5) unifies section/full-run contract paths, (6-7) consolidates section machinery, (8) documents assumptions, (9) cleans gate taxonomy, (10) minimizes judges, (11) establishes provider strategy, (12) reduces artifacts, and (13) validates via test matrix.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Priority | Est. Files Changed | Blockers |
|------|-------|--------|----------|-------------------|----------|
| 0 | Inventory + Binding Law | NOT STARTED | P0 | 2 | None |
| 1 | Contract Facade + Import Boundary | NOT STARTED | P0 | 4 | Wave 0 |
| 2 | Remove apps_research from Critical Path | NOT STARTED | P0 | 12 | Wave 1 |
| 3 | Disable R1B Semantic Cache Default | NOT STARTED | P1 | 6 | Wave 2 |
| 4 | One Contract Authority Path | NOT STARTED | P1 | 8 | Wave 3 |
| 5 | SectionSpec + SectionRunner Consolidation | NOT STARTED | P1 | 20 | Wave 4 |
| 6 | U0 Through Exit Assumption Ledger | NOT STARTED | P2 | 2 | Wave 5 |
| 7 | Gate Taxonomy Reset | NOT STARTED | P2 | 10 | Wave 6 |
| 8 | Judge Minimization + Token Efficiency | NOT STARTED | P2 | 8 | Wave 7 |
| 9 | Provider Strategy: External Default | NOT STARTED | P2 | 6 | Wave 8 |
| 10 | Artifact Diet | NOT STARTED | P3 | 4 | Wave 9 |
| 11 | Test Matrix Execution | NOT STARTED | P0 | 15 | Waves 0-10 |

### Risk Register

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R01 | Contract facade incomplete causes import errors | Medium | High | Temporary re-export with deprecation warnings |
| R02 | apps_research removal breaks existing workflows | Medium | Medium | Fail-closed with clear error messages |
| R03 | R1B disable affects perceived performance | Low | Low | Document opt-in procedure |
| R04 | Section consolidation loses independent run capability | Low | High | SectionRunner must preserve CLI entrypoints |
| R05 | Gate taxonomy reset weakens product safety | Low | Critical | Test matrix validates every release blocker |

---

## Wave 0 — Inventory + Binding Law

### Goal
Freeze the rules before refactoring. Document binding laws and create architectural guardrails.

### Deliverables

#### 1. Create `docs/reports/apps_rg/apps_rg_lean_core_contract_binding_plan.md`
**Status:** COMPLETE (this document)

#### 2. Create `apps_rg/LEAN_CORE.md`

```markdown
# apps_rg Lean-Core Architecture Contract

## Binding Law

1. **apps_rg binds to spine contracts, not agentic_core implementation.**
   - All production imports of spine functionality must route through `apps_rg.runtime.spine_contracts`
   - Concrete agentic_core runtime internals are FORBIDDEN in production code

2. **Graph is mandatory for apps_rg product value.**
   - C0.3 graph context must be emitted for all active generation routes
   - Graph traversal policy must be present in route contracts

3. **Sections remain independently runnable.**
   - Section CLI entrypoints must function without full-run orchestration
   - Section debugging capability preserved

4. **Candidate facts prove claims.**
   - No JD or briefing text may be used as candidate claim proof
   - All claims must reference verified fact IDs from candidate graph

5. **Graph supports role/phase/skill routing unless fact-bound.**
   - Role-family projection uses graph topology
   - Phase changes use graph-traversal reasoning

6. **JD and briefing are targeting only.**
   - JD text informs positioning, never proves candidate claims
   - Briefing informs strategic targeting, never proves candidate claims

7. **One authority per decision.**
   - U0 validates structure
   - L1 plans deterministically
   - L0 routes deterministically
   - C0 resolves evidence
   - PA compiles prompts
   - L2 executes generation
   - Exit aggregates and emits X3

8. **Missing briefing fails closed.**
   - No apps_research delegation
   - No fallback briefing generation
   - Clear product error on missing briefing

9. **R1B semantic output reuse is opt-in only.**
   - Default: OFF
   - Activation requires APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1
   - R1B never bypasses graph validation unless explicitly enabled

10. **LLM judges evaluate compact packets only; they do not repair.**
    - Judges receive JudgePacket, not full prompts
    - No repair loops in product path
    - Deterministic X2 gates enforce hard correctness

11. **Exit emits exactly one X3 for product-visible full runs.**
    - Section dispositions map to same Exit model
    - No section-local final authority bypass

12. **UWG alone writes durable state.**
    - No durable writes from L2, L3, judges, or apps_rg runtime

13. **L6 remains post-run only.**
    - L6 cannot rescue the current run
    - L6 operates on completed run artifacts only
```

### Acceptance Criteria
- [ ] LEAN_CORE.md created with all 13 laws
- [ ] Architecture guardrail documented
- [ ] Team acknowledgment of binding law (implicit via plan registration)

---

## Wave 1 — Contract Facade + Import Boundary

### Goal
Stop apps_rg from being hard-wired to concrete agentic_core implementation.

### Deliverables

#### 1. Create `apps_rg/runtime/spine_contracts.py`

```python
"""Temporary migration facade: re-exports contract types only from agentic_core.

This module is the ONLY permitted import path for spine contracts during migration.
All other apps_rg production modules must import contracts through this facade.

TODO: Migrate to neutral shared contract package (apps_shared/spine_contracts or agentic_spine_contracts).
"""

from __future__ import annotations

# Contract types only - NO executors, NO runtime engines, NO judges
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.graph_traverse_policy import GraphTraversePolicy
from agentic_core.runtime.contracts.fec_packet import FinalEvidenceContract
from agentic_core.runtime.contracts.section_contracts import SectionEvidenceContract
from agentic_core.runtime.contracts.compiled_prompt import CompiledPromptArtifact
from agentic_core.runtime.contracts.l3_l2_step import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_l2 import SealedL2Artifact
from agentic_core.runtime.contracts.exit_receipt import ExitDispositionReceipt
from agentic_core.runtime.contracts.runtime_exhaust import RuntimeExhaustBundle
from agentic_core.runtime.contracts.commit_request import CommitRequest

__all__ = [
    "ValidatedRequest",
    "RejectedRequest",
    "L1PlanContract",
    "RouteContract",
    "GraphTraversePolicy",
    "FinalEvidenceContract",
    "SectionEvidenceContract",
    "CompiledPromptArtifact",
    "L3ToL2StepContract",
    "SealedL2Artifact",
    "SealedSectionArtifact",
    "ExitReviewPacket",
    "ExitDispositionReceipt",
    "RuntimeExhaustBundle",
    "CommitRequest",
]

# Forward references for types that may not exist yet in agentic_core
RejectedRequest = ValidatedRequest  # Placeholder - update when available
SealedSectionArtifact = SealedL2Artifact  # Placeholder - update when available
ExitReviewPacket = dict  # Placeholder - update when available
```

#### 2. Create `apps_rg/runtime/ports.py`

```python
"""Protocol interfaces for spine runtime ports.

apps_rg binds to these protocols, not to concrete agentic_core implementations.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from pathlib import Path

from apps_rg.runtime.spine_contracts import (
    ValidatedRequest,
    CompiledPromptArtifact,
    SealedL2Artifact,
    ExitDispositionReceipt,
)


@runtime_checkable
class SpineRuntimePort(Protocol):
    """Port for spine runtime operations."""

    def execute_single_action_spine(
        self,
        validated_request: ValidatedRequest,
        *,
        artifact_dir: Path,
    ) -> RuntimeExhaustBundle:
        ...


@runtime_checkable
class EvidenceResolverPort(Protocol):
    """Port for C0 evidence resolution."""

    def resolve_proof_pool(
        self,
        request: ValidatedRequest,
        graph_policy: GraphTraversePolicy | None,
    ) -> FinalEvidenceContract:
        ...


@runtime_checkable
class PromptCompilerPort(Protocol):
    """Port for PA prompt compilation."""

    def compile_section_prompt(
        self,
        evidence_contract: FinalEvidenceContract,
        section_spec: SectionSpec,
    ) -> CompiledPromptArtifact:
        ...


@runtime_checkable
class ProviderGatewayPort(Protocol):
    """Port for L2 model execution."""

    def generate(
        self,
        compiled_prompt: CompiledPromptArtifact,
        *,
        provider_profile: str,
        token_budget: int,
    ) -> SealedL2Artifact:
        ...


@runtime_checkable
class ExitEvaluatorPort(Protocol):
    """Port for Exit evaluation."""

    def evaluate_exit(
        self,
        section_receipts: list[SectionExitReceipt],
    ) -> ExitDispositionReceipt:
        ...


@runtime_checkable
class SectionSpec(Protocol):
    """Protocol for section specification (placeholder - fully defined in Wave 5)."""

    section_id: str
    provider_budget: int


@runtime_checkable
class SectionExitReceipt(Protocol):
    """Protocol for section exit receipt."""

    section_id: str
    x3_disposition: str
```

#### 3. Create `tests/architecture/test_apps_rg_spine_contract_binding.py`

```python
"""CI/static test: apps_rg production code binds to spine contracts, not core internals.

This test walks all apps_rg production .py files via AST and fails if forbidden
cre agentic_core imports appear.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Set

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
APPS_RG_ROOT = REPO_ROOT / "apps_rg"

# Forbidden concrete agentic_core runtime imports
FORBIDDEN_IMPORTS: Set[str] = {
    "agentic_core.runtime.entrypoints",
    "agentic_core.runtime.entry",
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.runtime.exit",
    "agentic_core.runtime.judges",
    "agentic_core.runtime.l6",
}

# Allowed contract-only imports (must route through spine_contracts facade)
CONTRACT_ONLY_IMPORTS: Set[str] = {
    "agentic_core.runtime.contracts",
}

# Files exempt from this test (temporary migration exceptions)
EXEMPT_FILES: Set[str] = {
    # Temporary: spine_contracts.py itself re-exports from agentic_core
    "apps_rg/runtime/spine_contracts.py",
    # Tests may import directly for mocking/integration
}


def get_all_apps_rg_py_files() -> list[Path]:
    """Return all .py files under apps_rg (excluding tests/)."""
    py_files = []
    for path in APPS_RG_ROOT.rglob("*.py"):
        if "test" in path.parts or "tests" in path.parts:
            continue
        rel_path = path.relative_to(REPO_ROOT).as_posix()
        if rel_path in EXEMPT_FILES:
            continue
        py_files.append(path)
    return py_files


def extract_imports(source: str) -> tuple[Set[str], Set[str]]:
    """Extract (from_imports, direct_imports) from Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set(), set()

    from_imports: Set[str] = set()
    direct_imports: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            from_imports.add(module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                direct_imports.add(alias.name)

    return from_imports, direct_imports


def check_forbidden_imports(
    file_path: Path,
) -> list[str]:
    """Return list of forbidden imports found in file."""
    violations = []
    source = file_path.read_text(encoding="utf-8")
    from_imports, direct_imports = extract_imports(source)

    for forbidden in FORBIDDEN_IMPORTS:
        for imp in from_imports:
            if imp.startswith(forbidden):
                violations.append(f"{file_path}: from {imp} import ...")
        for imp in direct_imports:
            if imp.startswith(forbidden):
                violations.append(f"{file_path}: import {imp}")

    return violations


def test_no_forbidden_concrete_core_imports():
    """All apps_rg production files must avoid forbidden agentic_core imports."""
    py_files = get_all_apps_rg_py_files()
    all_violations: list[str] = []

    for file_path in py_files:
        violations = check_forbidden_imports(file_path)
        all_violations.extend(violations)

    if all_violations:
        msg = "Forbidden concrete agentic_core imports detected:\n"
        msg += "\n".join(f"  - {v}" for v in all_violations)
        msg += "\n\nAll production imports must route through apps_rg/runtime/spine_contracts.py"
        pytest.fail(msg)


def test_spine_contracts_facade_imports_only_contracts():
    """The spine_contracts facade must only import contract types, not executors."""
    facade_path = APPS_RG_ROOT / "runtime" / "spine_contracts.py"
    if not facade_path.exists():
        pytest.skip("spine_contracts.py not yet created")

    source = facade_path.read_text(encoding="utf-8")
    from_imports, direct_imports = extract_imports(source)

    # Facade should only import from contracts module
    for imp in from_imports:
        if "agentic_core" in imp and not imp.startswith("agentic_core.runtime.contracts"):
            pytest.fail(
                f"spine_contracts.py imports from concrete module: {imp}\n"
                "Facade must only re-export from agentic_core.runtime.contracts"
            )
```

### File Impact Table

| File | Action | Lines | Notes |
|------|--------|-------|-------|
| `apps_rg/runtime/spine_contracts.py` | CREATE | ~60 | Re-export contract types only |
| `apps_rg/runtime/ports.py` | CREATE | ~100 | Protocol interfaces |
| `tests/architecture/test_apps_rg_spine_contract_binding.py` | CREATE | ~150 | CI guard for import boundary |
| `apps_rg/runtime/orchestration/canonical_dispatch.py` | MODIFY | -5/+5 | Import through facade |
| `apps_rg/runtime/bindings/u0_binding.py` | MODIFY | -2/+2 | Import through facade |
| `apps_rg/runtime/judges/x1d_panel_adapters.py` | MODIFY | -5/+5 | Import through facade |

### Acceptance Criteria
- [ ] `spine_contracts.py` created with all required contract types
- [ ] `ports.py` created with all Protocol interfaces
- [ ] Architecture test passes (zero forbidden imports detected)
- [ ] All existing behavior passes targeted tests

---

## Wave 2 — Remove apps_research from apps_rg Critical Path

### Goal
Eliminate cross-app research delegation and make briefing mandatory.

### Current Problem
- `apps_research_call_required_at_u0()` signals delegation needed
- `apps_research_bridge.py` implements the bridge
- `route_profiles.yaml` has `apps_research_delegated_managed` route
- Missing briefing falls back to apps_research delegation

### Deliverables

#### 1. Modify `apps_rg/runtime/bindings/briefing_u0_signals.py`

```python
"""U0 briefing presence signals for apps_rg L1/L0 planning.

Vocabulary (product):
- ``grounding_required``: resume fact evidence binding (C0.1-C0.7) - always True for active generation.
- ``briefing_required``: targeting briefing is MANDATORY for active generation modes.
  apps_research delegation is DISABLED. Missing briefing fails closed.
"""

from __future__ import annotations

from typing import Any, Mapping

from apps_rg.runtime.spine_contracts import ValidatedRequest

_BRIEFING_REF_KEYS = ("briefing_artifact_ref", "manual_brief_path")


class BriefingMissingError(RuntimeError):
    """Raised when active generation mode requires briefing but none supplied."""

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


def briefing_required_at_u0(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
) -> None:
    """Validate briefing is present for active generation; fail closed if missing.

    Raises:
        BriefingMissingError: If active generation mode and briefing not supplied.
    """
    if not active_generation_mode:
        return

    if not briefing_supplied_at_u0(
        getattr(validated_request, "app_payload", None) or {}
    ):
        raise BriefingMissingError(
            context=f"request_id={getattr(validated_request, 'request_id', 'unknown')}"
        )


# DEPRECATED: apps_research delegation removed
# def apps_research_call_required_at_u0(...) -> bool:
#     """REMOVED: apps_research delegation is disabled."""
#     return False


__all__ = [
    "briefing_supplied_at_u0",
    "briefing_required_at_u0",
    "BriefingMissingError",
    # "apps_research_call_required_at_u0",  # REMOVED
]
```

#### 2. Quarantine `apps_rg/integrations/apps_research_bridge.py`

```python
"""DEPRECATED: apps_research bridge - QUARANTINED.

This module is quarantined and no longer used in production paths.
apps_research delegation has been removed from apps_rg critical path.
Briefing is now mandatory; missing briefing fails closed.

Retention reason: May be referenced by tests or other apps.
Planned removal: Wave 5+ after full migration verification.
"""

# ... existing implementation with deprecation warnings ...

import warnings
warnings.warn(
    "apps_research_bridge is deprecated. apps_research delegation disabled.",
    DeprecationWarning,
    stacklevel=2,
)
```

#### 3. Modify `apps_rg/runtime/bindings/l0_binding.py`

Remove `apps_research_call_required` handling from route logic.

#### 4. Modify `apps_rg/runtime/bindings/l1_binding.py`

Remove apps_research delegation planning.

#### 5. Update `apps_rg/config/domain_contract/route_profiles.yaml`

Remove the `apps_research_delegated_managed` route profile:

```yaml
# REMOVED:
# - route_profile_id: arpf::apps_rg::resume_generation::apps_research_delegated_managed::v1
#   conditions:
#     apps_research_call_required: true
```

#### 6. Modify `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`

Remove `_run_r3r4_research_hop` and delegated briefing behavior.

#### 7. Quarantine `apps_rg/integrations/managed_research_delegation.py`

Similar to apps_research_bridge - mark deprecated/quarantined.

### Deletion/Quarantine Table

| File | Action | Notes |
|------|--------|-------|
| `apps_research_bridge.py` | QUARANTINE | Mark deprecated, add warning |
| `managed_research_delegation.py` | QUARANTINE | Mark deprecated, add warning |
| `route_profiles.yaml` | DELETE rows | Remove apps_research_delegated_managed profile |
| `briefing_u0_signals.py` | MODIFY | Remove delegation function, add mandatory check |
| `l0_binding.py` | MODIFY | Remove delegation route handling |
| `l1_binding.py` | MODIFY | Remove delegation planning |
| `r3r4_whole_run_orchestration.py` | MODIFY | Remove research hop orchestration |
| `briefing_mode_classifier.py` | REVIEW | Remove delegation classification |
| `c0_briefing_bypass.py` | DELETE | No longer needed |

### Acceptance Criteria
- [ ] Missing briefing for `strategic_tailor` fails closed
- [ ] Missing briefing for `generate_scratch` fails closed
- [ ] Missing briefing for `section_regen` fails closed
- [ ] No apps_rg production path imports apps_research
- [ ] `route_profiles.yaml` contains no apps_research_delegated_managed row
- [ ] Valid briefing path proceeds normally

---

## Wave 3 — Disable R1B Semantic Output Cache by Default

### Goal
Prevent semantic cache from bypassing graph-grounded career reasoning.

### Current State
- `_semantic_cache_r1b_enabled()` returns True without env check
- R1B semantic cache is active default path
- Can bypass graph validation

### Deliverables

#### 1. Modify `apps_rg/runtime/embedding_settings.py`

```python
"""Embedding and semantic cache settings."""

import os


def semantic_cache_r1b_eligible() -> bool:
    """R1B semantic cache eligibility - opt-in only.

    Default: DISABLED (returns False)
    Opt-in: Set APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1
    """
    env_flag = os.environ.get("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", "").strip().lower()
    return env_flag in ("1", "true", "yes", "enabled")


def exact_cache_eligible() -> bool:
    """Exact deterministic cache - enabled by default for exact replay."""
    env_flag = os.environ.get("APPS_RG_ENABLE_EXACT_CACHE", "1").strip().lower()
    return env_flag not in ("0", "false", "no", "disabled")
```

#### 2. Modify `apps_rg/cache/whole_run_entrypoint_preflight.py`

Update `_semantic_cache_r1b_enabled()` to check env flag.

#### 3. Modify `apps_rg/cache/r1b_whole_run_preflight.py`

Update cache key generation to include strict components:

```python
"""R1B semantic cache key must include:
- source_resume_hash
- JD digest
- briefing digest
- candidate graph digest
- section spec version
- prompt/profile hash
- model/provider version
"""
```

#### 4. Update `apps_rg/runtime/c0/c02_semantic_cache_payload.py`

Add validation that R1B hit still runs graph validation unless explicitly bypassed.

### Acceptance Criteria
- [ ] R1B semantic cache disabled by default (no env var)
- [ ] Normal generation runs when semantic cache env absent
- [ ] R1B activates only with APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1
- [ ] Graph/C0 section proof logic still runs in default mode
- [ ] Exact cache (R1A) still functions by default

---

## Wave 4 — One Contract Authority Path for Section + Full Run

### Goal
Keep section debugging, but stop sections from acting like separate mini-spines.

### Problem
Section CLI and integrated full run diverge in C0/PA/L2/Exit authority.

### Target
Section and full-resume paths emit the same contract family:
- ValidatedRequest
- L1PlanContract
- RouteContract
- EvidenceContract / SectionEvidenceContract
- CompiledPromptArtifact
- SealedL2Artifact / SealedSectionArtifact
- X2 receipt
- ExitDispositionReceipt or SectionExitReceipt mapped to Exit
- RuntimeExhaustBundle

### Deliverables

#### 1. Modify `apps_rg/runtime/spine/front_contracts.py`

Update `SectionFrontSpineBridge` to emit full contract family:

```python
@dataclass(frozen=True, slots=True)
class SectionFrontSpineBridge:
    """Front-spine contract bundle for a section lane invocation."""

    section_id: str
    validated_request: Any
    l1_plan: Any
    route: Any
    # NEW: Full contract chain
    evidence_contract: Any = None  # C0 output
    compiled_prompt: Any = None  # PA output
    sealed_artifact: Any = None  # L2 output
    x2_receipt: Any = None  # X2 output
    section_exit_receipt: Any = None  # Section X3 equivalent
    product_visible: bool = True
    # ... existing fields ...
```

#### 2. Create `apps_rg/runtime/section_l2_spine_receipt.py`

Standardize L2 handoff receipt format.

#### 3. Create `apps_rg/runtime/section_runtime_exhaust_spine_receipt.py`

Standardize section completion receipt.

#### 4. Modify `apps_rg/runtime/spine/exit_artifacts.py`

Ensure section receipts map to Exit model.

#### 5. Modify `apps_rg/runtime/orchestration/canonical_dispatch.py`

Update to use unified contract path.

#### 6. Update `apps_rg/l2_recipe/*`

Migrate to common contract vocabulary.

### File Impact Table

| File | Action | Notes |
|------|--------|-------|
| `front_contracts.py` | MODIFY | Add full contract chain fields |
| `section_l2_spine_receipt.py` | CREATE | Standardize L2 handoff |
| `section_runtime_exhaust_spine_receipt.py` | CREATE | Standardize completion |
| `exit_artifacts.py` | MODIFY | Map section to Exit model |
| `canonical_dispatch.py` | MODIFY | Use unified contracts |
| `l2_recipe/*` | MODIFY | Migrate to common vocabulary |
| `section_bindings/*` | MODIFY | Unified contract emission |

### Acceptance Criteria
- [ ] Section runs still work independently
- [ ] Full runs still work
- [ ] Both paths use same contract vocabulary
- [ ] Section path no longer acts as separate C0/PA/L2/Exit authority
- [ ] Tests prove emitted contract family for each generated lane

---

## Wave 5 — Section Spec + Section Runner Consolidation

### Goal
Keep section functionality but collapse duplicated section machinery.

### Create Files

#### 1. `apps_rg/runtime/sections/section_spec.py`

```python
"""Section specification - single source of truth for section shape/gates/repair/policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceAuthoritySpec:
    """Proof source authority configuration."""

    candidate_facts_as_proof: bool = True
    graph_as_claim_proof: bool = True
    jd_as_proof_allowed: bool = False
    briefing_as_proof_allowed: bool = False
    companion_context_authority: bool = False


@dataclass(frozen=True)
class ShapeBounds:
    """Output shape constraints."""

    sentence_bounds: tuple[int, int] = (1, 10)
    word_bounds: tuple[int, int] = (20, 200)
    bullet_count: tuple[int, int] | None = None
    char_bounds: tuple[int, int] | None = None


@dataclass(frozen=True)
class SectionSpec:
    """Complete specification for a resume section."""

    section_id: str
    display_field: str
    template_ref: str
    x2_module_ref: str
    graph_mode: str  # "role_episode", "skills", "hybrid", "none"

    source_authority: SourceAuthoritySpec = field(default_factory=SourceAuthoritySpec)

    section_ownership: str = "candidate_facts"  # "candidate_facts", "jd_targeting", "hybrid"

    shape: ShapeBounds = field(default_factory=ShapeBounds)

    style_forbids: list[str] = field(default_factory=list)

    evidence_gates: list[str] = field(default_factory=list)

    allowed_repair: bool = False
    max_regen_attempts: int = 1

    required_artifacts: list[str] = field(default_factory=list)

    judge_policy: str = "deterministic_only"  # "deterministic_only", "compact_x1d"
    rubric_ref: str = ""

    provider_budget: int = 4000  # tokens
    provider_profile: str = "external_default"  # "external_default", "local_qwen"

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "SectionSpec":
        """Load from YAML spec file."""
        import yaml
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

#### 2. `apps_rg/runtime/sections/section_runner.py`

```python
"""Unified section runner - common lifecycle for all sections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.spine_contracts import (
    ValidatedRequest,
    CompiledPromptArtifact,
    SealedL2Artifact,
)
from apps_rg.runtime.ports import ProviderGatewayPort, PromptCompilerPort
from apps_rg.runtime.sections.section_spec import SectionSpec


class SectionRunner:
    """Execute section generation through common contract pipeline."""

    def __init__(
        self,
        *,
        provider_gateway: ProviderGatewayPort,
        prompt_compiler: PromptCompilerPort,
    ):
        self._provider = provider_gateway
        self._compiler = prompt_compiler

    def run(
        self,
        spec: SectionSpec,
        validated_request: ValidatedRequest,
        evidence_contract: Any,
        artifact_dir: Path,
    ) -> dict[str, Any]:
        """Execute full section lifecycle.

        Lifecycle:
        1. Load SectionSpec
        2. Resolve section proof pool
        3. Attach graph context (if graph_mode != "none")
        4. Compile prompt through common PA path
        5. Call model through ProviderGatewayPort
        6. Parse output
        7. Run deterministic validators
        8. Run section-specific X2 plugin (if needed)
        9. Seal artifact
        10. Emit section receipt
        """
        # 1. Load spec (already loaded as parameter)

        # 2. Resolve proof pool (from evidence_contract)
        proof_pool = self._resolve_proof_pool(evidence_contract, spec)

        # 3. Attach graph context
        graph_context = None
        if spec.graph_mode != "none":
            graph_context = self._attach_graph_context(proof_pool, spec)

        # 4. Compile prompt
        compiled_prompt = self._compiler.compile_section_prompt(
            evidence_contract,
            spec,
        )

        # 5. Call model
        sealed_artifact = self._provider.generate(
            compiled_prompt,
            provider_profile=spec.provider_profile,
            token_budget=spec.provider_budget,
        )

        # 6. Parse output
        parsed = self._parse_output(sealed_artifact, spec)

        # 7. Run deterministic validators (X2)
        x2_result = self._run_x2_validators(parsed, spec)

        # 8. Section-specific X2 plugin
        if spec.x2_module_ref:
            x2_result = self._run_section_x2(x2_result, spec)

        # 9. Seal artifact
        final_artifact = self._seal_artifact(parsed, x2_result, spec)

        # 10. Emit receipt
        receipt = self._emit_receipt(
            spec,
            validated_request,
            compiled_prompt,
            sealed_artifact,
            x2_result,
            final_artifact,
            artifact_dir,
        )

        return receipt

    def _resolve_proof_pool(self, evidence_contract: Any, spec: SectionSpec) -> Any:
        """Extract section-relevant facts from evidence contract."""
        # Implementation
        pass

    def _attach_graph_context(self, proof_pool: Any, spec: SectionSpec) -> Any:
        """Attach graph context based on graph_mode."""
        # Implementation
        pass

    def _parse_output(self, sealed: SealedL2Artifact, spec: SectionSpec) -> dict[str, Any]:
        """Parse model output based on section type."""
        # Implementation
        pass

    def _run_x2_validators(self, parsed: dict[str, Any], spec: SectionSpec) -> dict[str, Any]:
        """Run deterministic X2 validation."""
        # Implementation
        pass

    def _run_section_x2(self, x2_result: dict[str, Any], spec: SectionSpec) -> dict[str, Any]:
        """Run section-specific X2 validation."""
        # Implementation
        pass

    def _seal_artifact(
        self,
        parsed: dict[str, Any],
        x2_result: dict[str, Any],
        spec: SectionSpec,
    ) -> Any:
        """Seal final artifact."""
        # Implementation
        pass

    def _emit_receipt(
        self,
        spec: SectionSpec,
        validated_request: ValidatedRequest,
        compiled_prompt: CompiledPromptArtifact,
        sealed_artifact: SealedL2Artifact,
        x2_result: dict[str, Any],
        final_artifact: Any,
        artifact_dir: Path,
    ) -> dict[str, Any]:
        """Emit section exit receipt."""
        # Implementation
        pass
```

#### 3. Create Section Spec YAML Files

**`apps_rg/runtime/sections/specs/headline.yaml`**
```yaml
section_id: headline
display_field: headline
template_ref: apps_rg/sections/headline_v2.txt
x2_module_ref: apps_rg.runtime.validators.headline_x2
graph_mode: role_episode

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false
  companion_context_authority: false

section_ownership: candidate_facts

shape:
  sentence_bounds: [1, 2]
  word_bounds: [8, 20]
  char_bounds: [50, 150]

style_forbids:
  - "cliche_openers"
  - "vague_adjectives"
  - "unsupported_superlatives"

evidence_gates:
  - "fact_ids_present"
  - "no_jd_as_proof"
  - "no_briefing_as_proof"

allowed_repair: false
max_regen_attempts: 0

required_artifacts:
  - "source_resume_json"
  - "candidate_facts_graph"

judge_policy: deterministic_only
rubric_ref: ""

provider_budget: 2000
provider_profile: external_default
```

**`apps_rg/runtime/sections/specs/executive_summary.yaml`**
```yaml
section_id: executive_summary
display_field: executive_summary
template_ref: apps_rg/sections/executive_summary_v3.txt
x2_module_ref: apps_rg.runtime.validators.executive_summary_x2
graph_mode: skills

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false
  companion_context_authority: true

section_ownership: hybrid

shape:
  sentence_bounds: [3, 6]
  word_bounds: [80, 180]
  char_bounds: [500, 1200]

style_forbids:
  - "narrative_drift"
  - "generic_claims"
  - "jd_mimicry"

evidence_gates:
  - "fact_ids_present"
  - "role_fit_demonstrated"
  - "no_jd_as_proof"

allowed_repair: true
max_regen_attempts: 1

required_artifacts:
  - "source_resume_json"
  - "candidate_facts_graph"
  - "briefing_text"

judge_policy: compact_x1d
rubric_ref: "apps_rg/rubrics/executive_summary_compact_v1.yaml"

provider_budget: 8000
provider_profile: external_default
```

**`apps_rg/runtime/sections/specs/competencies.yaml`**
```yaml
section_id: competencies
display_field: competencies
template_ref: apps_rg/sections/competencies_v2.txt
x2_module_ref: apps_rg.runtime.validators.competencies_x2
graph_mode: skills

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false
  companion_context_authority: false

section_ownership: candidate_facts

shape:
  bullet_count: [6, 10]
  word_bounds: [10, 25]

style_forbids:
  - "skill_inflation"
  - "unsupported_years"
  - "vague_proficiency"

evidence_gates:
  - "fact_ids_present"
  - "skills_graph_aligned"
  - "no_jd_as_proof"

allowed_repair: false
max_regen_attempts: 0

required_artifacts:
  - "source_resume_json"
  - "skills_graph"

judge_policy: deterministic_only

provider_budget: 4000
provider_profile: external_default
```

**`apps_rg/runtime/sections/specs/unify_bullets.yaml`**
```yaml
section_id: unify_bullets
display_field: bullets
template_ref: apps_rg/sections/unify_bullets_v2.txt
x2_module_ref: apps_rg.runtime.validators.unify_bullets_x2
graph_mode: role_episode

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false

section_ownership: candidate_facts

shape:
  bullet_count: [3, 6]
  word_bounds: [15, 40]

style_forbids:
  - "weak_verbs"
  - "missing_metrics"
  - "unsupported_claims"

evidence_gates:
  - "fact_ids_present"
  - "achievement_focus"

allowed_repair: true
max_regen_attempts: 1

provider_budget: 6000
provider_profile: external_default
```

**`apps_rg/runtime/sections/specs/unify_narrative.yaml`**
```yaml
section_id: unify_narrative
display_field: narrative
template_ref: apps_rg/sections/unify_narrative_v2.txt
x2_module_ref: null  # uses unified validator
graph_mode: role_episode

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false

section_ownership: candidate_facts

shape:
  sentence_bounds: [2, 4]
  word_bounds: [40, 100]

allowed_repair: false

provider_budget: 4000
provider_profile: external_default
```

**`apps_rg/runtime/sections/specs/ibm_bullets.yaml`**
```yaml
section_id: ibm_bullets
display_field: bullets
template_ref: apps_rg/sections/ibm_bullets_v2.txt
x2_module_ref: apps_rg.runtime.validators.ibm_bullets_x2
graph_mode: role_episode

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false

section_ownership: candidate_facts

shape:
  bullet_count: [2, 4]
  word_bounds: [12, 30]

style_forbids:
  - "ibm_jargon"
  - "unverified_client_names"

evidence_gates:
  - "fact_ids_present"
  - "client_confidentiality"

allowed_repair: true
max_regen_attempts: 1

provider_budget: 4000
provider_profile: external_default
```

**`apps_rg/runtime/sections/specs/ibm_narrative.yaml`**
```yaml
section_id: ibm_narrative
display_field: narrative
template_ref: apps_rg/sections/ibm_narrative_v2.txt
x2_module_ref: apps_rg.runtime.validators.ibm_narrative_x2
graph_mode: role_episode

source_authority:
  candidate_facts_as_proof: true
  graph_as_claim_proof: true
  jd_as_proof_allowed: false
  briefing_as_proof_allowed: false

section_ownership: candidate_facts

shape:
  sentence_bounds: [2, 3]
  word_bounds: [30, 80]

style_forbids:
  - "ibm_specific_jargon"
  - "unverified_scope"

evidence_gates:
  - "fact_ids_present"

allowed_repair: false

provider_budget: 3000
provider_profile: external_default
```

### Collapse Over Time

| Component | Status | Replacement |
|-----------|--------|-------------|
| per-section PA wrappers | DEPRECATED | SectionRunner |
| per-section dispatch wrappers | DEPRECATED | SectionRunner |
| duplicated section_contract YAML | DELETE | section_spec YAML |
| duplicated product-shape constants | DELETE | SectionSpec.shape |
| bespoke section repair stacks | DELETE | SectionSpec.allowed_repair |
| lane_runtime + lane_execution split | CONSOLIDATE | SectionRunner.run() |
| per-lane infer_product_quality copies | DELETE | common X2 validator |

### Acceptance Criteria
- [ ] All seven sections still independently runnable
- [ ] SectionSpec is source of section shape/gate/repair/artifact policy
- [ ] SectionRunner executes common lifecycle
- [ ] Product behavior preserved

---

## Wave 6 — U0 Through Exit Assumption Ledger

### Goal
Re-review assumptions across U0 -> Exit and remove unreasonable or duplicate gates.

### Deliverable: `apps_rg/runtime/contracts/apps_rg_assumptions.yaml`

```yaml
assumptions:
  # U0 Stage
  - assumption_id: U0-001
    stage: U0
    owner: apps_rg.runtime.bindings.u0_binding
    decision_authority: structure_validation
    description: "U0 validates structure only, does not route"
    input_fields:
      - source_resume_text
      - job_description_text
      - briefing_text
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
    output_contract: ValidatedRequest
    failure_behavior: reject
    gate_ids: [U0-G-002]
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_u0_identity.py

  - assumption_id: U0-003
    stage: U0
    owner: apps_rg.runtime.bindings.briefing_u0_signals
    decision_authority: briefing_presence
    description: "U0 rejects missing required inputs, does not infer missing briefing"
    input_fields:
      - briefing_artifact_ref
      - manual_brief_path
    output_contract: ValidatedRequest
    failure_behavior: fail_closed
    gate_ids: [U0-G-003]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_briefing_mandatory.py

  # L1 Stage
  - assumption_id: L1-001
    stage: L1
    owner: apps_rg.runtime.bindings.l1_binding
    decision_authority: deterministic_planning
    description: "L1 deterministic planning, no evidence retrieval"
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
    decision_authority: route_hints
    description: "Route hints are advisory only, not authority"
    input_fields:
      - user_constraints.route_hint
    output_contract: L1PlanContract
    failure_behavior: ignore_hint_on_conflict
    gate_ids: []
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_route_hints.py

  # L0 Stage
  - assumption_id: L0-001
    stage: L0
    owner: apps_rg.runtime.bindings.l0_binding
    decision_authority: deterministic_route
    description: "L0 one deterministic route, cheapest safe route"
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
    decision_authority: no_retrieval
    description: "L0 no retrieval, no model call, R1B off by default"
    input_fields: []
    output_contract: RouteContract
    failure_behavior: n/a
    gate_ids: []
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_l0_no_model.py

  # C0 Stage
  - assumption_id: C0-001
    stage: C0
    owner: apps_rg.runtime.c0.c01_retrieval_plan
    decision_authority: candidate_facts_proof
    description: "Candidate facts prove claims, graph supports routing"
    input_fields:
      - source_resume_facts
      - skills_graph
      - role_episode_graph
    output_contract: FinalEvidenceContract
    failure_behavior: empty_proof_pool
    gate_ids: [C0-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_c0_fact_proof.py

  - assumption_id: C0-002
    stage: C0
    owner: apps_rg.runtime.c0.c03_graph_ref_policy
    decision_authority: graph_routing
    description: "Graph supports role/phase/skill routing unless fact-bound"
    input_fields:
      - GraphTraversePolicy
    output_contract: FinalEvidenceContract
    failure_behavior: fallback_to_facts_only
    gate_ids: [C0-G-002]
    x3_effect: ADVISORY
    test_ref: tests/unit/apps_rg/test_c0_graph_routing.py

  - assumption_id: C0-003
    stage: C0
    owner: apps_rg.runtime.c0.c01_retrieval_plan
    decision_authority: targeting_only
    description: "JD targeting only, never proof; briefing targeting only, never proof"
    input_fields:
      - job_description_text
      - briefing_text
    output_contract: FinalEvidenceContract
    failure_behavior: n/a  # used for positioning only
    gate_ids: [C0-G-003]
    x3_effect: none
    test_ref: tests/unit/apps_rg/test_c0_targeting_only.py

  # PA Stage
  - assumption_id: PA-001
    stage: PA
    owner: apps_rg.l2_recipe.pa_to_core_cpa
    decision_authority: single_compiler
    description: "PA one compiler, one artifact shape, canonical slot order"
    input_fields:
      - FinalEvidenceContract
      - SectionSpec
    output_contract: CompiledPromptArtifact
    failure_behavior: compilation_error
    gate_ids: [PA-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_pa_compilation.py

  # L2 Stage
  - assumption_id: L2-001
    stage: L2
    owner: apps_rg.runtime.ports.ProviderGatewayPort
    decision_authority: provider_execution
    description: "All model calls through ProviderGatewayPort, no direct qwen calls"
    input_fields:
      - CompiledPromptArtifact
    output_contract: SealedL2Artifact
    failure_behavior: provider_error
    gate_ids: [L2-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_l2_provider_port.py

  - assumption_id: L2-002
    stage: L2
    owner: apps_rg.runtime.sections.section_runner
    decision_authority: generation_attempts
    description: "One generation attempt by default, one optional regen if SectionSpec permits"
    input_fields:
      - SectionSpec.max_regen_attempts
    output_contract: SealedL2Artifact
    failure_behavior: fail_after_max_attempts
    gate_ids: [L2-G-002]
    x3_effect: REVIEW
    test_ref: tests/unit/apps_rg/test_l2_regen_policy.py

  # Exit Stage
  - assumption_id: Exit-001
    stage: Exit
    owner: agentic_core.runtime.exit
    decision_authority: x1_checkout
    description: "X1 checkout before Exit evaluation"
    input_fields:
      - section_receipts
    output_contract: ExitReviewPacket
    failure_behavior: checkout_failure
    gate_ids: [Exit-G-001]
    x3_effect: BLOCK
    test_ref: tests/unit/apps_rg/test_exit_x1.py

  - assumption_id: Exit-002
    stage: Exit
    owner: agentic_core.runtime.exit
    decision_authority: x2_aggregation
    description: "X2 deterministic aggregation plus optional judge"
    input_fields:
      - X2 receipts from all sections
    output_contract: ExitDispositionReceipt
    failure_behavior: aggregation_failure
    gate_ids: [Exit-G-002]
    x3_effect: REVIEW
    test_ref: tests/unit/apps_rg/test_exit_x2.py

  - assumption_id: Exit-003
    stage: Exit
    owner: agentic_core.runtime.exit
    decision_authority: x3_disposition
    description: "X3 exactly one disposition, UNKNOWN is never PASS"
    input_fields:
      - aggregated_X2_results
    output_contract: ExitDispositionReceipt
    failure_behavior: explicit_error
    gate_ids: [Exit-G-003]
    x3_effect: FINAL
    test_ref: tests/unit/apps_rg/test_exit_x3.py

  - assumption_id: Exit-004
    stage: Exit
    owner: apps_rg.runtime.spine.exit_artifacts
    decision_authority: section_disposition_mapping
    description: "Section dispositions map into same Exit model"
    input_fields:
      - section_exit_receipts
    output_contract: ExitDispositionReceipt
    failure_behavior: mapping_error
    gate_ids: [Exit-G-004]
    x3_effect: FINAL
    test_ref: tests/unit/apps_rg/test_section_exit_mapping.py
```

### Stage Rules Summary

| Stage | Decision Authority | Key Constraint | Failure Behavior |
|-------|-------------------|----------------|------------------|
| U0 | structure_validation | no routing, no inference | reject explicit |
| U0 | identity_digest | stamps for traceability | reject |
| U0 | briefing_presence | mandatory, no delegation | fail closed |
| L1 | deterministic_planning | no evidence retrieval | ambiguity register |
| L1 | route_hints | advisory only | ignore on conflict |
| L0 | deterministic_route | cheapest safe | fail closed |
| L0 | no_retrieval | no model call | n/a |
| C0 | candidate_facts_proof | primary authority | empty proof pool |
| C0 | graph_routing | supports role/phase/skill | fallback to facts |
| C0 | targeting_only | JD/briefing never proof | n/a |
| PA | single_compiler | one artifact shape | compilation error |
| L2 | provider_execution | through ProviderGatewayPort | provider error |
| L2 | generation_attempts | max 1 regen if permitted | fail after max |
| Exit | x1_checkout | checkout before eval | checkout failure |
| Exit | x2_aggregation | deterministic + optional judge | aggregation failure |
| Exit | x3_disposition | exactly one, UNKNOWN != PASS | explicit error |

### Acceptance Criteria
- [ ] Assumption ledger exists at `apps_rg/runtime/contracts/apps_rg_assumptions.yaml`
- [ ] Tests reference assumptions for critical gates
- [ ] Contradictory assumptions removed
- [ ] No stage takes authority from another stage

---

## Wave 7 — Gate Taxonomy Reset

### Goal
Make gates reasonable, consistent, and non-duplicative.

### Gate Classes

| Class | Can Drive X3A | Can Trigger Regen | Examples |
|-------|---------------|-------------------|----------|
| RELEASE_BLOCKER | Yes | No | unsupported claim, missing proof IDs, JD used as proof, malformed output |
| QUALITY_ADVISORY | No (X3A=ALLOW) | Yes (if SectionSpec permits) | weak tone, repetition, low sharpness |
| DEBUG_METRIC | No | No | token counts, latency, provider attempts |

### Rules
- RELEASE_BLOCKER can drive X3A (ALLOW/REVIEW/BLOCK)
- QUALITY_ADVISORY can trigger one regen only if SectionSpec permits
- DEBUG_METRIC never blocks release
- No skip-PASS gates
- No ghost gates
- No retired gates
- No duplicate release-blocking gate definitions

### Files to Update

| File | Action | Notes |
|------|--------|-------|
| `apps_rg/runtime/rigor/lane_registry.py` | MODIFY | Classify all gates |
| `apps_rg/runtime/sections/section_product_shape_ssot.py` | MODIFY | Remove duplicates |
| `apps_rg/runtime/validators/*_x2.py` | MODIFY | Tag gate classes |
| `tests/unit/apps_rg/section_rigor/*` | UPDATE | Test gate classification |
| `ops_scripts/apps_rg/section_complexity_reduction_audit.py` | UPDATE | Audit for ghost gates |

### Acceptance Criteria
- [ ] SectionSpec declares intended release blockers
- [ ] X2 emits actual release blockers
- [ ] Exit consumes actual release blockers
- [ ] Tests prove declared release blockers == emitted release blockers
- [ ] Audit shows no skip-PASS or ghost release gates

---

## Wave 8 — Judge Minimization + Token Efficiency

### Goal
Reduce LLM-as-Judge cost, variance, and token burn.

### Policy
- Deterministic X2 gates first
- LLM judge only runs after hard deterministic gates pass
- Judge cannot repair
- Judge receives compact JudgePacket only
- No full prompt, JD, briefing, or chat thread
- One judge attempt by default
- Multi-provider quorum only in calibration/CI

### JudgePacket Shape

```python
@dataclass(frozen=True)
class JudgePacket:
    """Compact packet for LLM judge evaluation."""

    section_id: str
    target_company: str
    target_role: str
    display_text: str  # The actual generated text to evaluate

    claim_ledger: list[ClaimEntry]  # Claims with fact_ids and proof_status
    fact_abstracts: list[FactAbstract]  # Compressed <=120 chars each

    deterministic_gate_summary: GateSummary  # Hard failures and warnings

    rubric_ref: str
    rubric_compact: str  # 8-12 checks max


@dataclass(frozen=True)
class ClaimEntry:
    claim: str
    fact_ids: list[str]
    proof_status: str  # "verified", "unverified", "unsupported"


@dataclass(frozen=True)
class FactAbstract:
    fact_id: str
    text: str  # <= 120 chars compressed


@dataclass(frozen=True)
class GateSummary:
    hard_failures: list[str]
    advisory_warnings: list[str]
```

### Budgets

| Item | Target |
|------|--------|
| Judge input | 2k-4k tokens |
| Judge output | <500 tokens JSON |
| Attempts | 1 (default) |

### Good Judge Use
- Executive plausibility
- Narrative coherence
- Role fit
- Tone
- Overclaim smell
- Cross-section contradiction

### Bad Judge Use (Move to X2)
- JSON validation
- Word/sentence counts
- Fact ID existence
- Proof joins
- JD/briefing proof flags
- Artifact presence

### Files to Update

| File | Action | Notes |
|------|--------|-------|
| `apps_rg/runtime/x1d_judge_policy.py` | MODIFY | Compact packet policy |
| `apps_rg/runtime/judges/*` | MODIFY | Remove repair loops |
| `apps_rg/runtime/validators/*_x2.py` | ENHANCE | Move bad judge uses to X2 |
| `executive_summary_judge_regen_loop.py` | QUARANTINE | Remove from product path |

### Acceptance Criteria
- [ ] Default run uses deterministic X2 heavily
- [ ] Default judge calls reduced by 50%+
- [ ] Judge packets compact (<4k tokens)
- [ ] No judge repair loop in product path
- [ ] Multi-judge quorum off by default

---

## Wave 9 — Provider Strategy: External Default, Qwen Optional

### Goal
Stop local Qwen/vLLM constraints from shaping apps_rg architecture.

### Recommendation
- External LLM API becomes default product generation provider
- External LLM API becomes default final judge provider
- Qwen/vLLM remains optional local/private/offline provider
- Graph/retrieval/validators remain local

### Provider Profiles

| Profile | Generation Provider | Judge Provider | Use Case |
|---------|-------------------|----------------|----------|
| `external_default` | Claude/OpenAI compatible | External API | Default production |
| `local_qwen` | qwen_vllm | qwen_vllm | Local/private/offline mode |
| `calibration_multi_judge` | Multiple external | Multiple judges | CI/soak only |

### external_default Profile
- Generation provider: Claude/OpenAI compatible external API
- Judge provider: external API
- No local vLLM requirement
- Long context available
- Stable JSON expected
- Token budgets per SectionSpec

### local_qwen Profile
- Provider: qwen_vllm
- Optional, local/private/offline mode
- Smaller budgets
- No multi-judge default
- Regen max 0 or 1
- No architecture coupling to vLLM

### Files to Update

| File | Action | Notes |
|------|--------|-------|
| `apps_rg/runtime/providers/*` | MODIFY | Add profile selection |
| `apps_rg/runtime/providers/qwen_vllm_provider.py` | QUARANTINE | Mark optional |
| `apps_rg/config/domain_contract/provider_profiles.yaml` | CREATE | Define profiles |
| Section provider selection | MODIFY | Use SectionSpec.provider_profile |

### Rules
- All model calls go through ProviderGatewayPort
- No direct qwen_vllm calls from section lanes
- Provider profile determines token budget
- SectionSpec owns per-section provider budget

### Acceptance Criteria
- [ ] Default apps_rg product run does not require local vLLM
- [ ] qwen/vLLM still works when explicitly selected
- [ ] No product section directly imports qwen provider
- [ ] Provider switch requires config/profile only

---

## Wave 10 — Artifact Diet

### Goal
Reduce proof clutter without losing auditability.

### Release Artifacts per Section

```
section_artifact_dir/
├── section_manifest.json
├── validated_request.json
├── route_contract.json
├── evidence_contract.json
├── compiled_prompt_artifact.json
├── provider_request_redacted.json
├── provider_response_redacted.json
├── parsed_output.json
├── x2_gate_outputs.json
└── section_exit_receipt.json
```

### Debug Artifacts (opt-in)

```
debug/  # only emitted when APPS_RG_DEBUG_ARTIFACTS=1
├── full_prompt.txt
├── graph_traversal_log.json
├── embedding_retrieval_log.json
├── judge_packets/
├── provider_raw_responses/
└── intermediate_parsed/
```

### Full Run Artifacts

```
run_artifact_dir/
├── operator_index.json
├── final_resume_artifact.json
├── exit_disposition_receipt.json
├── runtime_exhaust_bundle.json
└── section_refs/  # links to section artifacts
```

### Acceptance Criteria
- [ ] Release artifact count materially reduced (50%+ reduction)
- [ ] Debug artifacts available on opt-in (APPS_RG_DEBUG_ARTIFACTS=1)
- [ ] Review bundle easier to inspect
- [ ] No loss of required replay evidence

---

## Wave 11 — Test Matrix

### Required Tests

#### Binding Tests
```python
def test_apps_rg_zero_forbidden_core_imports():
    """All apps_rg production code has zero forbidden agentic_core imports."""


def test_contract_facade_imports_only_contracts():
    """spine_contracts.py imports contracts only, not executors."""


def test_apps_rg_runs_via_test_harness_through_contracts():
    """apps_rg can run against test runtime through contract ports."""
```

#### Briefing Tests
```python
def test_missing_briefing_strategic_tailor_fails_closed():
    """Missing briefing for strategic_tailor raises BriefingMissingError."""


def test_missing_briefing_generate_scratch_fails_closed():
    """Missing briefing for generate_scratch raises BriefingMissingError."""


def test_missing_briefing_section_regen_fails_closed():
    """Missing briefing for section_regen raises BriefingMissingError."""


def test_valid_briefing_proceeds():
    """Valid briefing path proceeds normally."""
```

#### Research Removal Tests
```python
def test_apps_rg_no_production_apps_research_imports():
    """No apps_rg production module imports apps_research."""


def test_route_profile_no_research_delegation():
    """route_profiles.yaml has no apps_research_delegated_managed row."""


def test_no_delegated_briefing_artifacts_emitted():
    """Delegated briefing artifacts no longer emitted."""
```

#### Cache Tests
```python
def test_r1b_semantic_disabled_by_default():
    """R1B semantic cache disabled without env var."""


def test_r1b_opt_in_only():
    """R1B activates only with APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1."""


def test_graph_generation_still_runs_by_default():
    """Graph/C0 section proof logic still runs in default mode."""
```

#### Graph Tests
```python
def test_graph_traverse_policy_present_on_active_routes():
    """GraphTraversePolicy present in RouteContract for active routes."""


def test_c03_graph_context_emitted():
    """C0.3 graph context still emitted."""


def test_section_graph_skills_proof_pool_active():
    """section_graph_skills_proof_pool still active."""


def test_jd_briefing_never_become_proof():
    """JD and briefing never become candidate claim proof."""
```

#### Section Tests
```python
def test_all_seven_sections_independently_runnable():
    """All 7 sections run via CLI independently."""


def test_all_seven_emit_common_contract_family():
    """All 7 sections emit same contract vocabulary."""


def test_section_spec_drives_shape_gates_repair_artifacts():
    """SectionSpec drives all section policy."""


def test_section_runner_used_by_all_sections():
    """SectionRunner executes all section lifecycles."""
```

#### Gate Tests
```python
def test_no_skip_pass_release_blockers():
    """No gates skip-PASS on release blockers."""


def test_no_ghost_release_blockers():
    """No ghost gates in release blocker list."""


def test_declared_gates_eq_emitted_release_blockers():
    """SectionSpec declared == X2 emitted release blockers."""


def test_unknown_never_pass():
    """UNKNOWN is never PASS in X3."""
```

#### Judge Tests
```python
def test_default_judge_packet_compact():
    """Default judge packet < 4k tokens."""


def test_no_judge_repair_loop():
    """No judge-initiated repair loops in product path."""


def test_multi_provider_quorum_off_by_default():
    """Multi-provider judge quorum not default."""
```

#### Provider Tests
```python
def test_external_default_no_vllm_requirement():
    """external_default profile runs without vLLM."""


def test_local_qwen_works_when_selected():
    """local_qwen profile works when explicitly selected."""


def test_no_section_direct_qwen_import():
    """No section lane directly imports qwen provider."""
```

#### Exit Tests
```python
def test_full_run_emits_exactly_one_x3():
    """Full run emits exactly one X3 disposition."""


def test_section_dispositions_map_to_exit_model():
    """Section exit receipts map to Exit model."""


def test_no_section_local_authority_bypass():
    """No section bypasses Exit for final authority."""
```

### Test Execution Order

1. Binding tests (Wave 1)
2. Briefing tests (Wave 2)
3. Research removal tests (Wave 2)
4. Cache tests (Wave 3)
5. Graph tests (Wave 4-5)
6. Section tests (Wave 5)
7. Gate tests (Wave 7)
8. Judge tests (Wave 8)
9. Provider tests (Wave 9)
10. Exit tests (Wave 4)
11. Integration tests (all waves)

---

## Final Acceptance Criteria

apps_rg lean-core target is complete when:

1. [ ] apps_rg binds to spine contracts, not concrete agentic_core runtime internals
2. [ ] Import-boundary CI proves the binding law (zero forbidden imports)
3. [ ] Graph skills remain mandatory and observable
4. [ ] Section debugging remains intact
5. [ ] apps_research is removed from apps_rg critical path
6. [ ] Briefing is mandatory and missing briefing fails closed
7. [ ] R1B semantic output shortcut is disabled by default
8. [ ] Section and full-run paths share the same contract family
9. [ ] SectionSpec + SectionRunner remove duplicated mini-spines
10. [ ] Gates are classified as release blocker, advisory, or debug metric
11. [ ] LLM judges are compact, rare, and non-repairing
12. [ ] External LLM API is default product provider
13. [ ] Qwen/vLLM is optional local mode, not architectural center of gravity
14. [ ] Full run emits one coherent X3 disposition
15. [ ] No durable writes occur outside UWG
16. [ ] L6 remains post-run only

---

## Deletion/Quarantine Table

| File/Pattern | Wave | Action | Replacement | Rollback Note |
|--------------|------|--------|-------------|---------------|
| `apps_research_bridge.py` | 2 | QUARANTINE | None (briefing mandatory) | Keep for reference, add deprecation warning |
| `managed_research_delegation.py` | 2 | QUARANTINE | None | Same as above |
| `briefing_mode_classifier.py` | 2 | REVIEW | Inline validation | Check for non-delegation uses |
| `c0_briefing_bypass.py` | 2 | DELETE | None | N/A |
| apps_research route profile | 2 | DELETE rows | None | Remove from route_profiles.yaml |
| `r1b_semantic_cache_payload.py` | 3 | MODIFY | Add opt-in check | Feature flag controlled |
| per-section PA wrappers | 5 | DELETE | SectionRunner | Migrate to common runner |
| per-section dispatch wrappers | 5 | DELETE | SectionRunner | Migrate to common runner |
| duplicated section_contract YAML | 5 | DELETE | SectionSpec YAML | Consolidate to specs/ |
| lane_runtime + lane_execution split | 5 | CONSOLIDATE | SectionRunner.run() | Single lifecycle method |
| per-lane infer_product_quality | 5 | DELETE | common X2 validator | Consolidate validators |
| `executive_summary_judge_regen_loop.py` | 8 | QUARANTINE | Deterministic X2 | Move to calibration/tools |
| `qwen_vllm_provider.py` | 9 | QUARANTINE | Optional local mode | Mark optional in registry |
| debug artifacts | 10 | OPT-IN | APPS_RG_DEBUG_ARTIFACTS=1 | Hidden by default |

---

## Explicit Non-Goals

The following are explicitly NOT in scope to prevent scope creep:

1. **Do NOT** rewrite agentic_core - this is an apps_rg binding refactor only
2. **Do NOT** delete apps_research package entirely - quarantine from apps_rg only
3. **Do NOT** change graph algorithm implementations - preserve existing graph logic
4. **Do NOT** modify locked deterministic sections (InsurTech, EY, Early Career, Education, Certifications)
5. **Do NOT** add new AI/ML capabilities - this is architectural cleanup only
6. **Do NOT** change resume output format or schema - preserve external contracts
7. **Do NOT** implement multi-region deployment - provider strategy is about API selection only
8. **Do NOT** create new UWG or L4 implementations - those remain in agentic_core
9. **Do NOT** add new CLI commands - preserve existing CLI interface
10. **Do NOT** modify Notion integration - this is runtime architecture only

---

## Rollback Notes

### Wave 1 Rollback
```bash
# If contract facade causes issues:
git checkout HEAD -- apps_rg/runtime/spine_contracts.py
# Restore direct imports temporarily while fixing facade
```

### Wave 2 Rollback
```bash
# If briefing mandatory breaks workflows:
git checkout HEAD -- apps_rg/runtime/bindings/briefing_u0_signals.py
# Restore apps_research delegation temporarily
```

### Wave 3 Rollback
```bash
# If R1B disable causes performance issues:
export APPS_RG_ENABLE_R1B_SEMANTIC_CACHE=1
# Or revert embedding_settings.py
```

### Wave 5 Rollback
```bash
# If SectionRunner consolidation breaks sections:
git checkout HEAD -- apps_rg/runtime/sections/  # Restore per-section files
# Keep SectionSpec/SectionRunner as optional path
```

---

## Exact CI Guard Descriptions

### CI Guard: `test_apps_rg_spine_contract_binding.py`

**Trigger:** Every PR touching `apps_rg/`
**Behavior:** FAIL if any production .py file imports forbidden agentic_core modules
**Exemptions:** `spine_contracts.py` (the facade itself), test files
**Bypass:** `SPINE_CONTRACT_BINDING_BYPASS=1` (emergency only, requires CTO approval)

### CI Guard: `test_briefing_mandatory.py`

**Trigger:** Every PR touching `apps_rg/runtime/bindings/`
**Behavior:** FAIL if missing briefing does not raise BriefingMissingError for active generation modes
**Bypass:** None (product requirement)

### CI Guard: `test_r1b_opt_in.py`

**Trigger:** Every PR touching `apps_rg/cache/`
**Behavior:** FAIL if R1B semantic cache enabled without env flag
**Bypass:** None (architectural requirement)

### CI Guard: `test_section_contract_family.py`

**Trigger:** Every PR touching `apps_rg/runtime/sections/`
**Behavior:** FAIL if section runs emit contracts outside standard family
**Bypass:** None

---

## File Impact Summary Table

| Wave | New Files | Modified Files | Deleted Files | Quarantined Files |
|------|-----------|----------------|---------------|-------------------|
| 0 | 2 | 0 | 0 | 0 |
| 1 | 3 | 6 | 0 | 0 |
| 2 | 0 | 6 | 1 | 3 |
| 3 | 0 | 4 | 0 | 0 |
| 4 | 3 | 8 | 0 | 0 |
| 5 | 9 | 20 | 8 | 0 |
| 6 | 1 | 0 | 0 | 0 |
| 7 | 0 | 10 | 0 | 0 |
| 8 | 0 | 6 | 0 | 2 |
| 9 | 1 | 4 | 0 | 1 |
| 10 | 0 | 4 | 0 | 0 |
| 11 | 15 | 0 | 0 | 0 |
| **TOTAL** | **33** | **58** | **9** | **6** |

---

## Execution Recommendations

### Recommended Wave Order
Waves are designed to be executed sequentially, but Waves 0-2 are critical path blockers for subsequent waves. Consider parallel execution of Waves 6-10 after Wave 5 completes.

### Resource Allocation
- **Architecture Lead**: Waves 0, 1, 4, 6 (binding law, facade, contracts, assumptions)
- **Backend Engineers**: Waves 2, 3, 7, 9 (research removal, cache, gates, providers)
- **Section Specialists**: Wave 5 (SectionSpec consolidation)
- **QA/Testing**: Wave 11 (test matrix)
- **DevOps**: Waves 8, 10 (judge optimization, artifact cleanup)

### Estimated Timeline
- Wave 0-1: 3-5 days
- Wave 2-3: 5-7 days
- Wave 4-5: 10-14 days (largest wave)
- Wave 6-10: 7-10 days (parallelizable)
- Wave 11: 5-7 days
- **Total**: 30-43 days with 2-3 engineers

---

## Plan Metadata

```yaml
plan_id: apps_rg_lean_core_binding_a1b2c3
version: 1.0.0
status: REGISTERED
waves: 11
files_new: 33
files_modified: 58
files_deleted: 9
files_quarantined: 6
zero_loss: true
binding_law: apps_rg/LEAN_CORE.md
notion_plan_slug: apps_rg_lean_core_binding_a1b2c3
```

---

## PLAN_CREATED

**PLAN_CREATED:** slug=apps_rg_lean_core_binding_a1b2c3 path=docs/reports/apps_rg/apps_rg_lean_core_contract_binding_plan.md status=Registered
