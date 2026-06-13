# Phase 2: LIC+RG Spine Adapters (Consolidated)

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope
Phase 2: LIC+RG Spine Adapters Implementation

## CODE_COMMIT
519ec8ee6bd719c271259b7e216e294370aca79c

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
```
docs/reports/plans/phase_03_04_consolidated.md
tools/evidence/phase03_04_consolidated_evidence_runner.py
```

## FILES_CHANGED_EVIDENCE
```
PENDING (will be filled after commit)
```

## INSPECTED_FILES
```
apps_lic/engines/lic_spine_adapter.py
apps_rg/engines/rg_spine_adapter.py
tools/evidence/phase02_consolidated_evidence_runner.py
```

## LIC Spine Adapter Tests
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests/unit_min_deps/test_apps_lic_spine_adapter.py
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_has_lic_prefix [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m7 passed[0m[32m in 0.05s[0m[32m ==============================[0m
```

## RG Spine Adapter Tests
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests/unit_min_deps/test_apps_rg_spine_adapter.py
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_has_rg_prefix [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m7 passed[0m[32m in 0.04s[0m[32m ==============================[0m
```

## INSPECTED_FILE_CONTENTS

### apps_lic/engines/lic_spine_adapter.py
```
"""
LIC Spine Adapter — pure wiring, no business logic.

Forces all LIC entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Null-object stubs are provided for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus — these seams are not yet wired for LIC and must remain no-ops
until the corresponding phases implement them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L2_execution.cid_registry import CIDRegistry
from agentic_core.L2_execution.reentry_loop import ReEntryLoop
from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

# Default maximum re-entry attempts for the LIC spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3

# ---------------------------------------------------------------------------
# Null-object stubs for unimplemented seams
# ---------------------------------------------------------------------------


class _NullD0Engine:
    """Null-object stub for D0 injection engine (not yet wired for LIC)."""

    def render_d0(self, d0_injections: str) -> str:
        return d0_injections


@dataclass(frozen=True)
class _RiskResult:
    allow: bool


class _NullRiskGate:
    """Null-object stub for risk gate (not yet wired for LIC)."""

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskResult:
        return _RiskResult(allow=True)


class _NullVigilanceDispatcher:
    """Null-object stub for vigilance dispatcher (not yet wired for LIC)."""

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        pass


class _NullMetaBus:
    """Null-object stub for meta-learning bus (not yet wired for LIC)."""

    def enqueue(self, *args: Any, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Assembler adapter: wraps AirlockAssembler to accept dict input
# ---------------------------------------------------------------------------


class _LicAssemblerAdapter:
    """
    Thin adapter so ExecutionOrchestrator.execute() can call
    self.assembler.assemble(intent_input: dict) with the LIC slot mapping.

    Slot mapping:
      s0_system       ← intent_input.get("s0_system", "")
      i0_instructional← intent_input.get("i0_instructional", "")
      c0_context      ← intent_input.get("c0_context", "")
      u0_user_prompt  ← intent_input.get("u0_user_prompt", "")
      d0_injections   ← intent_input.get("d0_injections", "")
    """

    def assemble(self, intent_input: dict[str, Any]) -> GovernedPayload:
        return AirlockAssembler.assemble(
            s0_system=intent_input.get("s0_system", ""),
            i0_instructional=intent_input.get("i0_instructional", ""),
            c0_context=intent_input.get("c0_context", ""),
            u0_user_prompt=intent_input.get("u0_user_prompt", ""),
            d0_injections=intent_input.get("d0_injections", ""),
        )


# ---------------------------------------------------------------------------
# LIC Spine Adapter — public entry point
# ---------------------------------------------------------------------------


class LicSpineAdapter(BaseSpineAdapter):
    """
    Canonical LIC spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    # LIC-specific prefix
    _PREFIX: str = "lic-"

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        """Initialize LIC spine adapter with dependency wiring."""
        # Create core dependencies
        cid_registry = CIDRegistry()
        reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=cid_registry,
        )
        orchestrator = ExecutionOrchestrator(
            assembler=_LicAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=_NullD0Engine(),
            risk_gate=_NullRiskGate(),
            cid_registry=cid_registry,
            reentry_loop=reentry_loop,
            vigilance_dispatcher=_NullVigilanceDispatcher(),
            meta_bus=_NullMetaBus(),
        )

        # Initialize base adapter with dependencies and LIC prefix
        super().__init__(
            cid_registry=cid_registry,
            orchestrator=orchestrator,
            prefix=self._PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )
```

### apps_rg/engines/rg_spine_adapter.py
```
"""
RG Spine Adapter — pure wiring, no business logic.

Forces all RG entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Null-object stubs are provided for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus — these seams are not yet wired for RG and must remain no-ops
until the corresponding phases implement them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L2_execution.cid_registry import CIDRegistry
from agentic_core.L2_execution.reentry_loop import ReEntryLoop
from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

# Default maximum re-entry attempts for the RG spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3

# ---------------------------------------------------------------------------
# Null-object stubs for unimplemented seams
# ---------------------------------------------------------------------------


class _NullD0Engine:
    """Null-object stub for D0 injection engine (not yet wired for RG)."""

    def render_d0(self, d0_injections: str) -> str:
        return d0_injections


@dataclass(frozen=True)
class _RiskResult:
    allow: bool


class _NullRiskGate:
    """Null-object stub for risk gate (not yet wired for RG)."""

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskResult:
        return _RiskResult(allow=True)


class _NullVigilanceDispatcher:
    """Null-object stub for vigilance dispatcher (not yet wired for RG)."""

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        pass


class _NullMetaBus:
    """Null-object stub for meta-learning bus (not yet wired for RG)."""

    def enqueue(self, *args: Any, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Assembler adapter: wraps AirlockAssembler to accept dict input
# ---------------------------------------------------------------------------


class _RgAssemblerAdapter:
    """
    Thin adapter so ExecutionOrchestrator.execute() can call
    self.assembler.assemble(intent_input: dict) with the RG slot mapping.

    Slot mapping:
      s0_system       ← intent_input.get("s0_system", "")
      i0_instructional← intent_input.get("i0_instructional", "")
      c0_context      ← intent_input.get("c0_context", "")
      u0_user_prompt  ← intent_input.get("u0_user_prompt", "")
      d0_injections   ← intent_input.get("d0_injections", "")
    """

    def assemble(self, intent_input: dict[str, Any]) -> GovernedPayload:
        return AirlockAssembler.assemble(
            s0_system=intent_input.get("s0_system", ""),
            i0_instructional=intent_input.get("i0_instructional", ""),
            c0_context=intent_input.get("c0_context", ""),
            u0_user_prompt=intent_input.get("u0_user_prompt", ""),
            d0_injections=intent_input.get("d0_injections", ""),
        )


# ---------------------------------------------------------------------------
# RG Spine Adapter — public entry point
# ---------------------------------------------------------------------------


class RgSpineAdapter(BaseSpineAdapter):
    """
    Canonical RG spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    # RG-specific prefix
    _PREFIX: str = "rg-"

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        """Initialize RG spine adapter with dependency wiring."""
        # Create core dependencies
        cid_registry = CIDRegistry()
        reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=cid_registry,
        )
        orchestrator = ExecutionOrchestrator(
            assembler=_RgAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=_NullD0Engine(),
            risk_gate=_NullRiskGate(),
            cid_registry=cid_registry,
            reentry_loop=reentry_loop,
            vigilance_dispatcher=_NullVigilanceDispatcher(),
            meta_bus=_NullMetaBus(),
        )

        # Initialize base adapter with dependencies and RG prefix
        super().__init__(
            cid_registry=cid_registry,
            orchestrator=orchestrator,
            prefix=self._PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )
```

### tools/evidence/phase02_consolidated_evidence_runner.py
```
#!/usr/bin/env python3
"""
Phase 2 Consolidated Evidence Runner (v2)

Generates consolidated evidence for Phase 2 LIC+RG spine adapters.
Updated to use Evidence Contract v2 helper for scope isolation and self-verification.
"""

import sys
from pathlib import Path

# Add the tools/evidence directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from evidence_contract_v2 import EvidenceContractV2


def main():
    """Generate Phase 2 consolidated evidence using Contract v2."""
    args = EvidenceContractV2.parse_args("Generate Phase 2 consolidated evidence")

    code_commit = args.code_commit
    evidence_commit = args.evidence_commit

    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_02_consolidated.md"

    print(f"Generating Phase 2 consolidated evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    if evidence_commit:
        print(f"EVIDENCE_COMMIT: {evidence_commit}")

    # Initialize contract helper with allowed prefixes for Phase 2
    allowed_prefixes = {
        "apps_shared/",
        "apps_lic/",
        "apps_rg/",
        "agentic_core/",
        "ops_scripts/",
        "tools/evidence/",
        "tests/",
        "docs/reports/plans/",
        ".github/workflows/",
        "pytest.ini",
        "docs/rules/",
    }

    contract = EvidenceContractV2(repo_root, allowed_prefixes)

    # Validate evidence contract structure
    require_evidence_commit = evidence_commit is not None
    contract.validate_evidence_contract_structure(
        code_commit, evidence_commit, require_evidence_commit
    )

    # Start building evidence content
    evidence_lines = []
    evidence_lines.append("# Phase 2: LIC+RG Spine Adapters (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 2: LIC+RG Spine Adapters Implementation")
    evidence_lines.append("")

    # Build evidence sections using contract helper
    inspected = [
        "apps_lic/engines/lic_spine_adapter.py",
        "apps_rg/engines/rg_spine_adapter.py",
        "tools/evidence/phase02_consolidated_evidence_runner.py",
    ]

    sections = contract.build_evidence_sections(
        code_commit, evidence_commit, inspected
    )

    # Add formatted sections
    evidence_lines.extend(contract.format_evidence_sections(sections))

    # Command outputs
    commands = [
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_lic_spine_adapter.py"],
            "LIC Spine Adapter Tests",
        ),
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_rg_spine_adapter.py"],
            "RG Spine Adapter Tests",
        ),
    ]

    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        evidence_lines.append(f"$ {' '.join(cmd)}")

        rc, out, err = contract.run_cmd(cmd)
        evidence_lines.append(out)
        if err:
            evidence_lines.append(f"STDERR: {err}")
        if rc != 0:
            evidence_lines.append(f"EXIT CODE: {rc}")

        evidence_lines.append("```")
        evidence_lines.append("")

    # Embed full contents of inspected files
    evidence_lines.append("## INSPECTED_FILE_CONTENTS")
    evidence_lines.append("")

    for filepath in sections["INSPECTED_FILES"]:
        full_path = repo_root / filepath
        evidence_lines.append(f"### {filepath}")
        evidence_lines.append("```")
        content = EvidenceContractV2.read_file_content(full_path)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    # Sanity check: evidence file should not start with Python code
    content_start = evidence_file.read_text(encoding="utf-8")[:200]
    if content_start.strip().startswith("#!/usr/bin/env python") or "def main()" in content_start[:200]:
        print("ERROR: Evidence file appears to contain Python code instead of markdown")
        print("This indicates the runner content was written to the evidence file.")
        sys.exit(1)

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    print(f"EVIDENCE_COMMIT: {sections['EVIDENCE_COMMIT']}")
    print(f"Current HEAD: {contract.get_current_head()}")

    if not evidence_commit:
        print("\nTo complete the evidence contract:")
        print("1. Commit this evidence file")
        print("2. Re-run with --evidence-commit <new_commit_hash>")
        print("3. The runner will update the sealed evidence file")


if __name__ == "__main__":
    main()
```

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

