"""Tests for the runtime-mode classifier in tools/analysis/apps_spine_coverage.py.

Covers the five-bucket taxonomy from
``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``:

  CORE_ONLY_VALID
  APP_OVERLAY_VALID
  APP_STANDALONE_FORBIDDEN
  PARTIAL_SPINE_STATIC_ONLY
  UNKNOWN_NEEDS_RUNTIME_TRACE

Strategy: build synthetic ``apps_*`` packages on disk in tmp_path,
invoke ``scan_app`` + ``classify_app`` directly, and assert the bucket.
This isolates the classifier from the live workspace state and pins
the contract behavior so future scanner changes can't silently weaken
it.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from tools.analysis.apps_spine_coverage import (
    CANONICAL_CONTRACTS,
    classify_app,
    scan_app,
)


# ---------------------------------------------------------------------------
# Synthetic-app builders
# ---------------------------------------------------------------------------


def _make_app(
    root: Path,
    name: str,
    *,
    files: dict[str, str],
) -> Path:
    """Create an app directory with files under ``root / name``."""
    app_dir = root / name
    app_dir.mkdir(parents=True, exist_ok=True)
    for relpath, content in files.items():
        target = app_dir / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(textwrap.dedent(content), encoding="utf-8")
    return app_dir


def _classify(app_dir: Path) -> tuple[str, str, dict]:
    sc = scan_app(app_dir)
    runtime_mode, evidence = classify_app(sc)
    return runtime_mode, evidence, sc


# ---------------------------------------------------------------------------
# CORE_ONLY_VALID — reserved bucket; non-app paths
# ---------------------------------------------------------------------------


def test_core_only_does_not_require_apps_star() -> None:
    """The scanner must not need ``apps_*`` for generic core capabilities.

    A non-``apps_*`` path is not in scope at all; the classifier never
    assigns CORE_ONLY_VALID to apps. This codifies the rule that the
    spine itself is the canonical core-only path; generic core
    capabilities don't depend on ``apps_*``.
    """
    # The CORE_ONLY_VALID emoji exists in the renderer; it is reserved
    # for non-apps audited paths. We assert the bucket name is allowed
    # in the public set.
    from tools.analysis.apps_spine_coverage import _RUNTIME_MODE_EMOJI
    assert "CORE_ONLY_VALID" in _RUNTIME_MODE_EMOJI


# ---------------------------------------------------------------------------
# APP_OVERLAY_VALID — at least one canonical contract import from agentic_core
# ---------------------------------------------------------------------------


def test_overlay_static_evidence_when_any_canonical_contract_imported_no_manifest(
    tmp_path: Path,
) -> None:
    """Lenient legacy path: one canonical contract qualifies when no manifest."""
    app = _make_app(
        tmp_path,
        "apps_synth_overlay",
        files={
            "engines/__init__.py": "",
            "engines/sample_engine.py": """
                from agentic_core.runtime.contracts.route_contract import RouteContract

                def run(req):
                    rc = RouteContract(...)
                    return rc
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"
    assert "RouteContract" in sc["distinct_contracts"]
    assert "manifest" in evidence.lower()
    assert sc["claims_domain_runtime"] is True
    assert sc["manifest_present"] is False


def test_overlay_static_evidence_with_multiple_contracts_no_manifest(
    tmp_path: Path,
) -> None:
    """Multiple contracts are reported in the evidence (no-manifest path)."""
    app = _make_app(
        tmp_path,
        "apps_synth_overlay_multi",
        files={
            "engines/__init__.py": "",
            "engines/full_pipeline.py": """
                from agentic_core.X import L1PlanContract, RouteContract
                from agentic_core.Y import FinalEvidenceContract, CompiledPromptArtifact
                from agentic_core.Z import SealedArtifact, ExitReviewPacket
            """,
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"
    assert sc["contract_count"] == 6
    assert set(sc["distinct_contracts"]) == {
        "L1PlanContract", "RouteContract",
        "FinalEvidenceContract", "CompiledPromptArtifact",
        "SealedArtifact", "ExitReviewPacket",
    }


# ---------------------------------------------------------------------------
# Manifest-aware path (W7) -- route-typed contract requirements
# ---------------------------------------------------------------------------


def test_manifest_with_all_required_contracts_is_overlay_static(
    tmp_path: Path,
) -> None:
    """Manifest declares R2_grounded_read; all 8 required contracts present."""
    app = _make_app(
        tmp_path,
        "apps_synth_manifest_complete",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_manifest_complete
                claimed_routes:
                  - type: R2_grounded_read
                    description: "Grounded Q&A over the canonical KB."
            """,
            "engines/__init__.py": "",
            "engines/full_r2.py": """
                from agentic_core.contracts import (
                    ValidatedRequest, L1PlanContract, RouteContract,
                    RetrievalPlan, FinalEvidenceContract,
                    CompiledPromptArtifact, SealedArtifact, ExitReviewPacket,
                )
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"
    assert sc["manifest_present"] is True
    assert "R2_grounded_read" in sc["manifest_claimed_routes"]
    assert sc["manifest_missing_contracts"] == []
    assert "R2_grounded_read" in evidence


def test_manifest_with_missing_contracts_is_partial_spine(tmp_path: Path) -> None:
    """Manifest declares R3_action; only some required contracts present."""
    app = _make_app(
        tmp_path,
        "apps_synth_manifest_incomplete",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_manifest_incomplete
                claimed_routes:
                  - type: R3_action
            """,
            "engines/__init__.py": "",
            "engines/partial.py": """
                from agentic_core.contracts import ValidatedRequest, L1PlanContract
                # R3_action requires 7 contracts; only 2 imported.
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "PARTIAL_SPINE_STATIC_ONLY"
    assert sc["manifest_present"] is True
    assert sc["manifest_missing_contracts"]  # non-empty
    # Specific missing contracts are reported.
    assert "RouteContract" in sc["manifest_missing_contracts"]
    assert "CommitRequest" in sc["manifest_missing_contracts"]
    assert "missing" in evidence.lower()


def test_manifest_with_build_time_compiler_route_no_contracts_required(
    tmp_path: Path,
) -> None:
    """build_time_compiler route legitimately requires zero contracts.

    apps_qna shape: produces a context pack the operator pastes into an
    external agent. The spine is not in the runtime path of the pasted
    answer. Manifest must declare this explicitly to qualify.
    """
    app = _make_app(
        tmp_path,
        "apps_synth_build_compiler",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_build_compiler
                claimed_routes:
                  - type: build_time_compiler
                    description: "Compiles a context pack at build time."
            """,
            "engines/__init__.py": "",
            "engines/builder.py": """
                # Build-time tool. No canonical contracts required.
                def build():
                    return "pack"
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"
    assert "build_time_compiler" in sc["manifest_claimed_routes"]
    assert "no canonical contract handoff" in evidence


def test_manifest_with_unknown_route_type_surfaces_warning(
    tmp_path: Path,
) -> None:
    """Unknown route types contribute zero contracts AND surface in output."""
    app = _make_app(
        tmp_path,
        "apps_synth_unknown_route",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_unknown_route
                claimed_routes:
                  - type: not_a_real_route_type
                    description: "Typo in route type."
            """,
            "engines/__init__.py": "",
            "engines/something.py": "def run(): return None",
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    assert sc["manifest_present"] is True
    assert "not_a_real_route_type" in sc["manifest_unknown_routes"]
    # Unknown route contributes zero contracts -> empty required set ->
    # falls into the manifest-honored empty-required branch.
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"


# ---------------------------------------------------------------------------
# APP_STANDALONE_FORBIDDEN — claims runtime, zero contracts, zero spine edges
# ---------------------------------------------------------------------------


def test_standalone_forbidden_when_runtime_claim_no_spine(tmp_path: Path) -> None:
    """Local mini-runtime that bypasses the spine entirely."""
    app = _make_app(
        tmp_path,
        "apps_synth_standalone",
        files={
            "engines/__init__.py": "",
            "engines/local_runtime.py": """
                # No agentic_core imports. Mini-runtime owned by the app.
                import json

                def plan_and_run(req):
                    plan = {"step": "do_thing"}
                    return plan
            """,
            "scripts/__main__.py": """
                from .._not_a_real_module import nothing
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "APP_STANDALONE_FORBIDDEN"
    assert sc["contract_count"] == 0
    assert sc["agentic_core_edges"] == 0
    assert sc["claims_domain_runtime"] is True
    assert "shadow runtime" in evidence


# ---------------------------------------------------------------------------
# PARTIAL_SPINE_STATIC_ONLY — runtime claim, infra imports, no contracts
# ---------------------------------------------------------------------------


def test_partial_spine_when_only_infra_imports(tmp_path: Path) -> None:
    """Importing UWG / ledger / BGE alone is NOT delegation evidence."""
    app = _make_app(
        tmp_path,
        "apps_synth_partial",
        files={
            "engines/__init__.py": "",
            "engines/local_writer.py": """
                # Imports infrastructure (write_gateway) but no canonical
                # authority contracts.
                from agentic_core.L2_execution.utils.write_gateway import (
                    write_text,
                )

                def emit_artifact(path, content):
                    return write_text(path, content)
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "PARTIAL_SPINE_STATIC_ONLY"
    assert sc["contract_count"] == 0
    assert sc["has_uwg_usage"] is True
    assert sc["agentic_core_edges"] >= 1
    assert "static-only" in evidence


def test_apps_shared_alone_does_not_make_overlay_valid(tmp_path: Path) -> None:
    """Constitutional rule: importing apps_shared cannot make an app valid.

    Even if apps_shared internally re-exports authority contracts, the
    consumer must import them from agentic_core directly — apps_shared
    is shared resources, not the spine.
    """
    app = _make_app(
        tmp_path,
        "apps_synth_shared_only",
        files={
            "engines/__init__.py": "",
            "engines/uses_shared.py": """
                # Only apps_shared imports (which would re-export anything,
                # but the scanner does not count these as delegation evidence).
                from apps_shared.config.environment_config import EnvSpec
                from apps_shared.adapters.system_learning_facade import notify

                def run(req):
                    return EnvSpec()
            """,
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    assert runtime_mode != "APP_OVERLAY_STATIC_EVIDENCE"
    assert runtime_mode != "APP_OVERLAY_VALID"  # legacy-alias safety
    # Specifically, apps_shared edges count as apps_shared, not as
    # agentic_core authority contracts.
    assert sc["apps_shared_edges"] >= 2
    assert sc["contract_count"] == 0


# ---------------------------------------------------------------------------
# UNKNOWN_NEEDS_RUNTIME_TRACE — no runtime markers
# ---------------------------------------------------------------------------


def test_unknown_when_app_is_pure_types_package(tmp_path: Path) -> None:
    """A schemas-only app cannot be classified statically.

    Without engines/integrations/router/CLI/wizard markers the app is
    not on the hook for canonical contract evidence. The scanner
    refuses to call it FORBIDDEN; it reports UNKNOWN and asks for a
    runtime trace.
    """
    app = _make_app(
        tmp_path,
        "apps_synth_types_only",
        files={
            "types/__init__.py": "",
            "types/schemas.py": """
                from dataclasses import dataclass

                @dataclass
                class DomainSchema:
                    name: str
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "UNKNOWN_NEEDS_RUNTIME_TRACE"
    assert sc["claims_domain_runtime"] is False
    assert "runtime trace" in evidence


def test_unknown_when_app_is_empty(tmp_path: Path) -> None:
    """An app with no non-stdlib imports is UNKNOWN, not FORBIDDEN."""
    app = _make_app(
        tmp_path,
        "apps_synth_empty",
        files={
            "__init__.py": "",
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    assert runtime_mode == "UNKNOWN_NEEDS_RUNTIME_TRACE"
    assert sc["non_stdlib_edges"] == 0


# ---------------------------------------------------------------------------
# Import-only coverage cannot pass as runtime compliance
# ---------------------------------------------------------------------------


def test_import_only_coverage_is_not_runtime_compliance(tmp_path: Path) -> None:
    """An app can score ON_SPINE on the LEGACY metric and still be
    PARTIAL_SPINE_STATIC_ONLY on the canonical metric.

    Reproduces the apps_lic / apps_rg situation: heavy imports of
    agentic_core utilities, but no canonical contracts → not an overlay.
    """
    # Build an app with MANY agentic_core imports but ZERO contracts.
    # NOTE: do NOT inline bulk_imports into a triple-quoted block --
    # textwrap.dedent (used inside _make_app) won't see common leading
    # whitespace once the imports start at column 0, leaving the file
    # with mixed indentation that fails ast.parse. Construct the file
    # text explicitly with all lines at column 0.
    bulk_imports = "\n".join(
        f"from agentic_core.utils.module_{i} import helper_{i}" for i in range(40)
    )
    heavy_consumer = (
        bulk_imports
        + "\n\ndef run(req):\n    return helper_0(req)\n"
    )
    app_dir = tmp_path / "apps_synth_heavy_no_contracts"
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "engines").mkdir(parents=True, exist_ok=True)
    (app_dir / "engines" / "__init__.py").write_text("", encoding="utf-8")
    (app_dir / "engines" / "heavy_consumer.py").write_text(
        heavy_consumer, encoding="utf-8"
    )
    app = app_dir
    runtime_mode, _evidence, sc = _classify(app)
    # Legacy spine_coverage_pct will be very high because most non-stdlib
    # imports are agentic_core. But runtime_mode must NOT be valid.
    assert sc["spine_coverage_pct"] > 50
    assert runtime_mode != "APP_OVERLAY_STATIC_EVIDENCE"
    # Legacy alias check: the old name should also not be assigned.
    assert runtime_mode != "APP_OVERLAY_VALID"
    assert runtime_mode == "PARTIAL_SPINE_STATIC_ONLY"


# ---------------------------------------------------------------------------
# Live workspace — apps_qna evidence
# ---------------------------------------------------------------------------


def test_apps_qna_post_w7_classified_correctly() -> None:
    """apps_qna in the LIVE workspace post-W7 spine handoff.

    After W7 (apps_qna/spine_manifest.yaml + apps_qna/integrations/spine_handoff.py):
      - manifest_present is True
      - claimed_routes includes 'build_time_compiler'
      - contract_count >= 1 (ValidatedRequest from spine_handoff.py)
      - runtime_mode is APP_OVERLAY_STATIC_EVIDENCE

    If this test starts failing, either:
      (a) someone removed the manifest or the spine_handoff module, in
          which case the W7 migration regressed, OR
      (b) the scanner classification logic changed in a way that
          contradicts the doctrine -- review APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md
    """
    repo_root = Path(__file__).resolve().parents[4]
    apps_qna = repo_root / "apps_qna"
    if not apps_qna.is_dir():
        pytest.skip("apps_qna not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_qna)
    assert sc["manifest_present"] is True, "apps_qna spine_manifest.yaml missing"
    assert "build_time_compiler" in sc["manifest_claimed_routes"], (
        f"manifest claimed_routes={sc['manifest_claimed_routes']}"
    )
    assert sc["claims_domain_runtime"] is True
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE", (
        f"got runtime_mode={runtime_mode}; evidence={evidence}"
    )


def test_canonical_contracts_constant_is_frozen() -> None:
    """The contract set is immutable at runtime."""
    assert isinstance(CANONICAL_CONTRACTS, frozenset)
    # Smoke-test specific entries the spine relies on.
    for required in (
        "L1PlanContract",
        "RouteContract",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "SealedArtifact",
        "ExitReviewPacket",
        "CommitRequest",
        "RuntimeExhaustBundle",
    ):
        assert required in CANONICAL_CONTRACTS, (
            f"canonical contract {required!r} missing from CANONICAL_CONTRACTS"
        )


# ===========================================================================
# W8 -- Route-shape taxonomy + FORMAL_EXCEPTION_STATIC_EVIDENCE
# ===========================================================================


def test_route_type_table_has_canonical_taxonomy() -> None:
    """The five canonical route types must all be registered."""
    from tools.analysis.apps_spine_coverage import (
        ROUTE_TYPE_CONTRACT_REQUIREMENTS,
    )
    for canonical in (
        "build_time_compiler",
        "evaluator_only",
        "core_adjacent_utility",
        "R3_grounded_read",
        "R3R4_managed_workflow",
    ):
        assert canonical in ROUTE_TYPE_CONTRACT_REQUIREMENTS, (
            f"missing canonical route type {canonical!r}"
        )


def test_R3_grounded_read_requires_full_R3_chain() -> None:
    """R3_grounded_read requires the documented 8-contract chain."""
    from tools.analysis.apps_spine_coverage import (
        ROUTE_TYPE_CONTRACT_REQUIREMENTS,
    )
    required = ROUTE_TYPE_CONTRACT_REQUIREMENTS["R3_grounded_read"]
    for c in (
        "ValidatedRequest", "L1PlanContract", "RouteContract",
        "RetrievalPlan", "FinalEvidenceContract",
        "CompiledPromptArtifact", "SealedArtifact", "ExitReviewPacket",
    ):
        assert c in required, f"R3_grounded_read missing required {c!r}"
    # CommitRequest is NOT in R3_grounded_read.
    assert "CommitRequest" not in required


def test_R3R4_managed_workflow_adds_commit_request_to_R3_chain() -> None:
    from tools.analysis.apps_spine_coverage import (
        ROUTE_TYPE_CONTRACT_REQUIREMENTS,
    )
    r3 = ROUTE_TYPE_CONTRACT_REQUIREMENTS["R3_grounded_read"]
    r3r4 = ROUTE_TYPE_CONTRACT_REQUIREMENTS["R3R4_managed_workflow"]
    assert r3.issubset(r3r4)
    assert "CommitRequest" in r3r4
    # The exact difference is just CommitRequest.
    assert (r3r4 - r3) == frozenset({"CommitRequest"})


def test_formal_exception_route_types_are_empty_required_set() -> None:
    from tools.analysis.apps_spine_coverage import (
        ROUTE_TYPE_CONTRACT_REQUIREMENTS,
    )
    assert ROUTE_TYPE_CONTRACT_REQUIREMENTS["evaluator_only"] == frozenset()
    assert ROUTE_TYPE_CONTRACT_REQUIREMENTS["core_adjacent_utility"] == frozenset()


def test_evaluator_only_with_exception_record_is_formal_exception(
    tmp_path: Path,
) -> None:
    """evaluator_only + reason_code + compensating_controls -> FORMAL_EXCEPTION."""
    app = _make_app(
        tmp_path,
        "apps_synth_evaluator",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_evaluator
                claimed_routes:
                  - type: evaluator_only
                    description: "Synthetic evaluator surface."
                exception:
                  reason_code: circular_dependency
                  exception_record_class: SyntheticEvalException
                  compensating_controls:
                    - "CC-EVAL-01: telemetry without evaluate_and_emit"
                    - "CC-EVAL-02: exception record accessible"
                  review_cadence: annual
                  owner: synthetic-team
            """,
            "engines/__init__.py": "",
            "engines/runner.py": "def evaluate(): return None\n",
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "FORMAL_EXCEPTION_STATIC_EVIDENCE", (
        f"got {runtime_mode}; evidence={evidence}"
    )
    assert sc["manifest_has_formal_exception"] is True
    assert sc["manifest_exception_reason_code"] == "circular_dependency"
    assert sc["manifest_compensating_controls_count"] == 2
    assert "circular_dependency" in evidence


def test_core_adjacent_utility_with_exception_record_is_formal_exception(
    tmp_path: Path,
) -> None:
    """core_adjacent_utility + reason_code + compensating_controls -> FORMAL_EXCEPTION."""
    app = _make_app(
        tmp_path,
        "apps_synth_core_adjacent",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_core_adjacent
                claimed_routes:
                  - type: core_adjacent_utility
                    description: "Synthetic regulated-domain library."
                exception:
                  reason_code: regulatory_domain
                  exception_record_class: SyntheticUwException
                  compensating_controls:
                    - "CC-UW-01: ObservabilityAdapter telemetry"
                    - "CC-UW-02: CoreAdapter equivalent governance"
                    - "CC-UW-03: exception record accessible"
                  review_cadence: annual
                  owner: synthetic-team
            """,
            "engines/__init__.py": "",
            "engines/lib.py": "def underwrite(): return None\n",
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert sc["manifest_has_formal_exception"] is True
    assert sc["manifest_exception_reason_code"] == "regulatory_domain"
    assert sc["manifest_compensating_controls_count"] == 3


def test_evaluator_only_without_exception_record_does_not_pass(
    tmp_path: Path,
) -> None:
    """evaluator_only manifest WITHOUT an exception block must NOT classify
    as FORMAL_EXCEPTION_STATIC_EVIDENCE; an unverified formal claim is
    UNKNOWN_NEEDS_RUNTIME_TRACE."""
    app = _make_app(
        tmp_path,
        "apps_synth_evaluator_naked",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_evaluator_naked
                claimed_routes:
                  - type: evaluator_only
                    description: "No exception block; should be rejected."
            """,
            "engines/__init__.py": "",
            "engines/x.py": "def f(): return None\n",
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode != "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert runtime_mode != "APP_OVERLAY_STATIC_EVIDENCE"
    assert runtime_mode == "UNKNOWN_NEEDS_RUNTIME_TRACE"
    assert sc["manifest_has_formal_exception"] is False
    assert "exception" in evidence.lower()


def test_core_adjacent_with_reason_code_but_empty_controls_does_not_pass(
    tmp_path: Path,
) -> None:
    """Reason code alone is not sufficient; compensating_controls must be non-empty."""
    app = _make_app(
        tmp_path,
        "apps_synth_partial_exception",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_partial_exception
                claimed_routes:
                  - type: core_adjacent_utility
                exception:
                  reason_code: regulatory_domain
                  compensating_controls: []
            """,
            "engines/__init__.py": "",
            "engines/x.py": "def f(): return None\n",
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    assert runtime_mode == "UNKNOWN_NEEDS_RUNTIME_TRACE"
    assert sc["manifest_has_formal_exception"] is False


def test_build_time_compiler_remains_overlay_static_not_formal_exception(
    tmp_path: Path,
) -> None:
    """build_time_compiler is NOT a formal-exception route; the empty
    required-set is self-justifying. Even if an exception block is also
    present, the route type must classify as APP_OVERLAY_STATIC_EVIDENCE,
    not FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    app = _make_app(
        tmp_path,
        "apps_synth_build_time",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_build_time
                claimed_routes:
                  - type: build_time_compiler
                    description: "Build-time pack compiler."
            """,
            "engines/__init__.py": "",
            "engines/builder.py": "def build(): return 'pack'\n",
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"
    assert runtime_mode != "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert sc["manifest_has_formal_exception"] is False


def test_unknown_routes_field_is_populated_for_typos(tmp_path: Path) -> None:
    """Unknown route-type strings still surface via manifest_unknown_routes."""
    app = _make_app(
        tmp_path,
        "apps_synth_typo",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_typo
                claimed_routes:
                  - type: not_a_real_route_shape
            """,
            "engines/__init__.py": "",
            "engines/x.py": "def f(): return None\n",
        },
    )
    _runtime_mode, _evidence, sc = _classify(app)
    assert "not_a_real_route_shape" in sc["manifest_unknown_routes"]


def test_prompt_envelope_is_accepted_equivalent_for_compiled_prompt_artifact(
    tmp_path: Path,
) -> None:
    """An app importing PromptEnvelope satisfies a CompiledPromptArtifact requirement."""
    app = _make_app(
        tmp_path,
        "apps_synth_prompt_envelope_equiv",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_prompt_envelope_equiv
                claimed_routes:
                  - type: R3_grounded_read
            """,
            "engines/__init__.py": "",
            "engines/full_r3.py": """
                from agentic_core.contracts import (
                    ValidatedRequest, L1PlanContract, RouteContract,
                    RetrievalPlan, FinalEvidenceContract,
                    PromptEnvelope, SealedArtifact, ExitReviewPacket,
                )
            """,
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    # CompiledPromptArtifact is NOT in distinct_contracts, but PromptEnvelope is.
    assert "PromptEnvelope" in sc["distinct_contracts"]
    assert "CompiledPromptArtifact" not in sc["distinct_contracts"]
    # The equivalence rule must let R3_grounded_read pass anyway.
    assert sc["manifest_missing_contracts"] == []
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"


def test_R3R4_managed_workflow_missing_commit_request_is_partial(
    tmp_path: Path,
) -> None:
    """R3R4_managed_workflow with the R3 chain present but no CommitRequest
    must classify as PARTIAL_SPINE_STATIC_ONLY, missing CommitRequest."""
    app = _make_app(
        tmp_path,
        "apps_synth_r3r4_no_commit",
        files={
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_r3r4_no_commit
                claimed_routes:
                  - type: R3R4_managed_workflow
            """,
            "engines/__init__.py": "",
            "engines/full_r3.py": """
                from agentic_core.contracts import (
                    ValidatedRequest, L1PlanContract, RouteContract,
                    RetrievalPlan, FinalEvidenceContract,
                    CompiledPromptArtifact, SealedArtifact, ExitReviewPacket,
                )
            """,
        },
    )
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "PARTIAL_SPINE_STATIC_ONLY"
    assert "CommitRequest" in sc["manifest_missing_contracts"]
    assert "CommitRequest" in evidence


def test_unknown_needs_runtime_trace_remains_available_for_ambiguous_manifest(
    tmp_path: Path,
) -> None:
    """An app with no domain-runtime markers + a manifest that has no
    contract-bearing claim still falls through to UNKNOWN_NEEDS_RUNTIME_TRACE
    rather than being treated as APP_OVERLAY_STATIC_EVIDENCE."""
    app = _make_app(
        tmp_path,
        "apps_synth_ambiguous",
        files={
            # No engines/integrations/scripts/CLI -- this is a passive package.
            "spine_manifest.yaml": """
                schema_version: 1
                app: apps_synth_ambiguous
                claimed_routes:
                  - type: evaluator_only
            """,
            "types.py": "class Marker: pass\n",
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    # No exception block -> formal-exception path rejects -> UNKNOWN.
    assert runtime_mode == "UNKNOWN_NEEDS_RUNTIME_TRACE"


# ===========================================================================
# Live workspace -- apps_eval and apps_underwriting_ai (W8 manifests)
# ===========================================================================


def test_apps_eval_live_classifies_as_formal_exception_static_evidence() -> None:
    """apps_eval/spine_manifest.yaml + governed_eval_exception.py must combine
    to classify as FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_eval = repo_root / "apps_eval"
    if not apps_eval.is_dir():
        pytest.skip("apps_eval not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_eval)
    assert sc["manifest_present"] is True, "apps_eval/spine_manifest.yaml missing"
    assert "evaluator_only" in sc["manifest_claimed_routes"]
    assert sc["manifest_exception_reason_code"] == "circular_dependency"
    assert sc["manifest_compensating_controls_count"] >= 4, (
        f"got {sc['manifest_compensating_controls_count']} controls; "
        "expected the 4 CC-EVAL-* compensating controls"
    )
    assert sc["manifest_has_formal_exception"] is True
    assert runtime_mode == "FORMAL_EXCEPTION_STATIC_EVIDENCE", (
        f"got {runtime_mode}; evidence={evidence}"
    )


def test_apps_underwriting_ai_live_classifies_as_formal_exception_static_evidence() -> None:
    """apps_underwriting_ai/spine_manifest.yaml + governed_uw_exception.py must
    combine to classify as FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_uw = repo_root / "apps_underwriting_ai"
    if not apps_uw.is_dir():
        pytest.skip("apps_underwriting_ai not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_uw)
    assert sc["manifest_present"] is True
    assert "core_adjacent_utility" in sc["manifest_claimed_routes"]
    assert sc["manifest_exception_reason_code"] == "regulatory_domain"
    assert sc["manifest_compensating_controls_count"] >= 4, (
        f"got {sc['manifest_compensating_controls_count']} controls; "
        "expected the 4 CC-UW-* compensating controls"
    )
    assert sc["manifest_has_formal_exception"] is True
    assert runtime_mode == "FORMAL_EXCEPTION_STATIC_EVIDENCE", (
        f"got {runtime_mode}; evidence={evidence}"
    )


# ===========================================================================
# W9 -- apps_research migration to APP_OVERLAY_STATIC_EVIDENCE
# ===========================================================================


def test_apps_research_live_classifies_as_overlay_static_evidence() -> None:
    """apps_research/spine_manifest.yaml + integrations/spine_handoff.py must
    combine to classify as APP_OVERLAY_STATIC_EVIDENCE for R3_grounded_read.

    This is STATIC EVIDENCE only -- the test asserts that the 8 R3
    contracts are imported and the manifest declares the route, NOT
    that runtime exercises every contract on every call.
    """
    repo_root = Path(__file__).resolve().parents[4]
    apps_research = repo_root / "apps_research"
    if not apps_research.is_dir():
        pytest.skip("apps_research not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_research)
    assert sc["manifest_present"] is True, "apps_research/spine_manifest.yaml missing"
    assert "R3_grounded_read" in sc["manifest_claimed_routes"], (
        f"manifest claimed_routes={sc['manifest_claimed_routes']}"
    )
    assert sc["manifest_missing_contracts"] == [], (
        f"missing R3 contracts: {sc['manifest_missing_contracts']}"
    )
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE", (
        f"got runtime_mode={runtime_mode}; evidence={evidence}"
    )


def test_apps_research_surfaces_full_R3_contract_chain() -> None:
    """All 8 R3 contracts (with PromptEnvelope ↔ CompiledPromptArtifact equivalence)
    must be detected as direct imports in apps_research."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_research = repo_root / "apps_research"
    if not apps_research.is_dir():
        pytest.skip("apps_research not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_research)
    detected = set(sc["distinct_contracts"])
    # The R3 chain requires these 8; PromptEnvelope is an accepted equivalent
    # for CompiledPromptArtifact per CONTRACT_EQUIVALENT_GROUPS.
    for required in (
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "SealedArtifact",
        "ExitReviewPacket",
    ):
        assert required in detected, (
            f"R3 required contract {required!r} not detected; "
            f"detected={sorted(detected)}"
        )
    # Either the canonical name OR the equivalent must be present.
    assert (
        "CompiledPromptArtifact" in detected
        or "PromptEnvelope" in detected
    ), (
        "neither CompiledPromptArtifact nor PromptEnvelope detected; "
        f"detected={sorted(detected)}"
    )


def test_apps_research_is_not_build_time_compiler() -> None:
    """apps_research must NOT declare or be classified as build_time_compiler."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_research = repo_root / "apps_research"
    if not apps_research.is_dir():
        pytest.skip("apps_research not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_research)
    assert "build_time_compiler" not in sc["manifest_claimed_routes"]


def test_apps_research_is_not_formal_exception() -> None:
    """apps_research is not exempt; it uses the standard GovernedAppRunner
    substrate. The scanner must therefore NOT classify it as
    FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_research = repo_root / "apps_research"
    if not apps_research.is_dir():
        pytest.skip("apps_research not present in this checkout")
    runtime_mode, _evidence, sc = _classify(apps_research)
    assert runtime_mode != "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert sc["manifest_has_formal_exception"] is False
    assert sc["manifest_exception_reason_code"] == ""


def test_apps_research_does_not_require_commit_request() -> None:
    """R3_grounded_read intentionally excludes CommitRequest; apps_research
    must therefore have no CommitRequest gap (the route does not need it)."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_research = repo_root / "apps_research"
    if not apps_research.is_dir():
        pytest.skip("apps_research not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_research)
    assert "CommitRequest" not in sc["manifest_required_contracts"], (
        f"apps_research must not require CommitRequest; "
        f"required={sc['manifest_required_contracts']}"
    )
    assert "CommitRequest" not in sc["manifest_missing_contracts"]


def test_apps_research_spine_handoff_module_imports_cleanly() -> None:
    """The spine_handoff module must import without error and expose all
    8 R3 contract types via R3_CONTRACT_SURFACE."""
    from apps_research.integrations import spine_handoff

    assert hasattr(spine_handoff, "R3_CONTRACT_SURFACE")
    surface = spine_handoff.R3_CONTRACT_SURFACE
    assert len(surface) == 8
    expected_names = {
        "ValidatedRequest", "L1PlanContract", "RouteContract",
        "RetrievalPlan", "FinalEvidenceContract", "CompiledPromptArtifact",
        "SealedArtifact", "ExitReviewPacket",
    }
    assert set(surface.keys()) == expected_names
    # Each surface entry must be a class object (not None / placeholder).
    for name, cls in surface.items():
        assert cls is not None, f"surface entry {name!r} is None"
        assert isinstance(cls, type), f"surface entry {name!r} is not a class"
    # Validation helper returns all-True.
    valid = spine_handoff.validate_research_r3_contract_surface()
    assert valid == {n: True for n in expected_names}


# ===========================================================================
# W10 -- apps_exec migration to APP_OVERLAY_STATIC_EVIDENCE
# ===========================================================================


def test_apps_exec_live_classifies_as_overlay_static_evidence() -> None:
    """apps_exec/spine_manifest.yaml + integrations/spine_handoff.py must
    combine to classify as APP_OVERLAY_STATIC_EVIDENCE for R3_grounded_read.

    Static evidence only -- the test asserts that the 8 R3 contracts
    are imported and the manifest declares the route, NOT that runtime
    exercises every contract on every call.
    """
    repo_root = Path(__file__).resolve().parents[4]
    apps_exec = repo_root / "apps_exec"
    if not apps_exec.is_dir():
        pytest.skip("apps_exec not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_exec)
    assert sc["manifest_present"] is True, "apps_exec/spine_manifest.yaml missing"
    assert "R3_grounded_read" in sc["manifest_claimed_routes"], (
        f"manifest claimed_routes={sc['manifest_claimed_routes']}"
    )
    assert sc["manifest_missing_contracts"] == [], (
        f"missing R3 contracts: {sc['manifest_missing_contracts']}"
    )
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE", (
        f"got runtime_mode={runtime_mode}; evidence={evidence}"
    )


def test_apps_exec_surfaces_full_R3_contract_chain() -> None:
    """All 8 R3 contracts (with PromptEnvelope ↔ CompiledPromptArtifact equivalence)
    must be detected as direct imports in apps_exec."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_exec = repo_root / "apps_exec"
    if not apps_exec.is_dir():
        pytest.skip("apps_exec not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_exec)
    detected = set(sc["distinct_contracts"])
    for required in (
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "SealedArtifact",
        "ExitReviewPacket",
    ):
        assert required in detected, (
            f"R3 required contract {required!r} not detected; "
            f"detected={sorted(detected)}"
        )
    assert (
        "CompiledPromptArtifact" in detected
        or "PromptEnvelope" in detected
    ), (
        "neither CompiledPromptArtifact nor PromptEnvelope detected; "
        f"detected={sorted(detected)}"
    )


def test_apps_exec_is_not_build_time_compiler() -> None:
    """apps_exec must NOT declare or be classified as build_time_compiler."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_exec = repo_root / "apps_exec"
    if not apps_exec.is_dir():
        pytest.skip("apps_exec not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_exec)
    assert "build_time_compiler" not in sc["manifest_claimed_routes"]


def test_apps_exec_is_not_formal_exception() -> None:
    """apps_exec is not exempt; it uses the standard GovernedAppRunner
    substrate. The scanner must NOT classify it as
    FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_exec = repo_root / "apps_exec"
    if not apps_exec.is_dir():
        pytest.skip("apps_exec not present in this checkout")
    runtime_mode, _evidence, sc = _classify(apps_exec)
    assert runtime_mode != "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert sc["manifest_has_formal_exception"] is False
    assert sc["manifest_exception_reason_code"] == ""


def test_apps_exec_does_not_require_commit_request() -> None:
    """R3_grounded_read intentionally excludes CommitRequest. apps_exec's
    HITL_ENABLED=True is a runner posture, not evidence of a durable-write
    surface; the route shape stays R3_grounded_read, not
    R3R4_managed_workflow."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_exec = repo_root / "apps_exec"
    if not apps_exec.is_dir():
        pytest.skip("apps_exec not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_exec)
    assert "CommitRequest" not in sc["manifest_required_contracts"], (
        f"apps_exec must not require CommitRequest; "
        f"required={sc['manifest_required_contracts']}"
    )
    assert "CommitRequest" not in sc["manifest_missing_contracts"]
    # Reinforce that the route is R3_grounded_read, not R3R4_managed_workflow.
    assert "R3R4_managed_workflow" not in sc["manifest_claimed_routes"]


def test_apps_exec_hitl_enabled_does_not_force_R3R4_managed_workflow() -> None:
    """The runner-side HITL flag is documented in the manifest (informational)
    but does NOT promote apps_exec to R3R4_managed_workflow. The bucketing
    rule is: R3R4 requires CommitRequest in the required-contract set; HITL
    is orthogonal."""
    from tools.analysis.apps_spine_coverage import (
        ROUTE_TYPE_CONTRACT_REQUIREMENTS,
    )
    repo_root = Path(__file__).resolve().parents[4]
    apps_exec = repo_root / "apps_exec"
    if not apps_exec.is_dir():
        pytest.skip("apps_exec not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_exec)
    # The manifest only claims R3_grounded_read.
    assert sc["manifest_claimed_routes"] == ["R3_grounded_read"]
    # The R3 chain alone does not require CommitRequest, even though the
    # runner has HITL enabled.
    r3_required = ROUTE_TYPE_CONTRACT_REQUIREMENTS["R3_grounded_read"]
    assert "CommitRequest" not in r3_required


def test_apps_exec_spine_handoff_module_imports_cleanly() -> None:
    """The apps_exec spine_handoff module must import without error and
    expose all 8 R3 contract types via R3_CONTRACT_SURFACE."""
    from apps_exec.integrations import spine_handoff

    assert hasattr(spine_handoff, "R3_CONTRACT_SURFACE")
    surface = spine_handoff.R3_CONTRACT_SURFACE
    assert len(surface) == 8
    expected_names = {
        "ValidatedRequest", "L1PlanContract", "RouteContract",
        "RetrievalPlan", "FinalEvidenceContract", "CompiledPromptArtifact",
        "SealedArtifact", "ExitReviewPacket",
    }
    assert set(surface.keys()) == expected_names
    for name, cls in surface.items():
        assert cls is not None, f"surface entry {name!r} is None"
        assert isinstance(cls, type), f"surface entry {name!r} is not a class"
    valid = spine_handoff.validate_exec_r3_contract_surface()
    assert valid == {n: True for n in expected_names}


# ===========================================================================
# W11 -- apps_lic migration to APP_OVERLAY_STATIC_EVIDENCE
# ===========================================================================


def test_apps_lic_live_classifies_as_overlay_static_evidence() -> None:
    """apps_lic/spine_manifest.yaml + integrations/spine_handoff.py must
    combine to classify as APP_OVERLAY_STATIC_EVIDENCE for R3_grounded_read.

    Static evidence only -- the test asserts that the 8 R3 contracts
    are imported and the manifest declares the route, NOT that runtime
    exercises every contract on every call.
    """
    repo_root = Path(__file__).resolve().parents[4]
    apps_lic = repo_root / "apps_lic"
    if not apps_lic.is_dir():
        pytest.skip("apps_lic not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_lic)
    assert sc["manifest_present"] is True, "apps_lic/spine_manifest.yaml missing"
    assert "R3_grounded_read" in sc["manifest_claimed_routes"], (
        f"manifest claimed_routes={sc['manifest_claimed_routes']}"
    )
    assert sc["manifest_missing_contracts"] == [], (
        f"missing R3 contracts: {sc['manifest_missing_contracts']}"
    )
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE", (
        f"got runtime_mode={runtime_mode}; evidence={evidence}"
    )


def test_apps_lic_surfaces_full_R3_contract_chain() -> None:
    """All 8 R3 contracts (with PromptEnvelope ↔ CompiledPromptArtifact equivalence)
    must be detected as direct imports in apps_lic."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_lic = repo_root / "apps_lic"
    if not apps_lic.is_dir():
        pytest.skip("apps_lic not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_lic)
    detected = set(sc["distinct_contracts"])
    for required in (
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "SealedArtifact",
        "ExitReviewPacket",
    ):
        assert required in detected, (
            f"R3 required contract {required!r} not detected; "
            f"detected={sorted(detected)}"
        )
    assert (
        "CompiledPromptArtifact" in detected
        or "PromptEnvelope" in detected
    ), (
        "neither CompiledPromptArtifact nor PromptEnvelope detected; "
        f"detected={sorted(detected)}"
    )


def test_apps_lic_is_not_build_time_compiler() -> None:
    """apps_lic must NOT declare or be classified as build_time_compiler."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_lic = repo_root / "apps_lic"
    if not apps_lic.is_dir():
        pytest.skip("apps_lic not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_lic)
    assert "build_time_compiler" not in sc["manifest_claimed_routes"]


def test_apps_lic_is_not_formal_exception() -> None:
    """apps_lic is not exempt; it uses the standard GovernedAppRunner
    substrate. The scanner must NOT classify it as
    FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_lic = repo_root / "apps_lic"
    if not apps_lic.is_dir():
        pytest.skip("apps_lic not present in this checkout")
    runtime_mode, _evidence, sc = _classify(apps_lic)
    assert runtime_mode != "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert sc["manifest_has_formal_exception"] is False
    assert sc["manifest_exception_reason_code"] == ""


def test_apps_lic_does_not_require_commit_request() -> None:
    """The pre-migration audit proved no durable-write surface exists in
    apps_lic. R3_grounded_read intentionally excludes CommitRequest, and
    apps_lic must NOT be promoted to R3R4_managed_workflow."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_lic = repo_root / "apps_lic"
    if not apps_lic.is_dir():
        pytest.skip("apps_lic not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_lic)
    assert "CommitRequest" not in sc["manifest_required_contracts"], (
        f"apps_lic must not require CommitRequest; "
        f"required={sc['manifest_required_contracts']}"
    )
    assert "CommitRequest" not in sc["manifest_missing_contracts"]
    # Reinforce: route stays R3_grounded_read.
    assert "R3R4_managed_workflow" not in sc["manifest_claimed_routes"]


def test_apps_lic_manifest_claims_r3r4_and_r4_routes() -> None:
    """Hard-delete convergence: manifest must claim R3R4 + R4 (not legacy R3-only)."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_lic = repo_root / "apps_lic"
    if not apps_lic.is_dir():
        pytest.skip("apps_lic not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_lic)
    routes = sc["manifest_claimed_routes"]
    assert "R3R4_MANAGED_WORKFLOW" in routes or "R3R4_managed_workflow" in routes
    assert "R4_SINGLE_ACTION" in routes or "R4_MANAGED_DRAFT" in routes


def test_apps_lic_spine_handoff_module_deleted() -> None:
    """GovernedLic spine_handoff must be physically deleted."""
    import importlib
    with pytest.raises((ModuleNotFoundError, ImportError)):
        importlib.import_module("apps_lic.integrations.spine_handoff")


# ===========================================================================
# W13 -- apps_rg migration to APP_OVERLAY_STATIC_EVIDENCE
# ===========================================================================


def test_apps_rg_live_classifies_as_overlay_static_evidence() -> None:
    """apps_rg/spine_manifest.yaml + integrations/spine_handoff.py must
    combine to classify as APP_OVERLAY_STATIC_EVIDENCE for R3_grounded_read.

    Static evidence only -- the test asserts that the 8 R3 contracts
    are imported and the manifest declares the route, NOT that runtime
    exercises every contract on every call.
    """
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_rg)
    assert sc["manifest_present"] is True, "apps_rg/spine_manifest.yaml missing"
    assert "R3_grounded_read" in sc["manifest_claimed_routes"], (
        f"manifest claimed_routes={sc['manifest_claimed_routes']}"
    )
    assert sc["manifest_missing_contracts"] == [], (
        f"missing R3 contracts: {sc['manifest_missing_contracts']}"
    )
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE", (
        f"got runtime_mode={runtime_mode}; evidence={evidence}"
    )


def test_apps_rg_no_longer_on_legacy_any_contract_path() -> None:
    """After W13, apps_rg's classification must be manifest-honored, not
    derived from the legacy any-contract heuristic. The evidence string
    must NOT contain 'no spine_manifest.yaml' (which is the legacy-path
    marker)."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    _runtime_mode, evidence, sc = _classify(apps_rg)
    assert sc["manifest_present"] is True
    assert "no spine_manifest.yaml" not in evidence, (
        f"apps_rg still on legacy path; evidence={evidence}"
    )
    # Manifest-honored evidence cites the route(s).
    assert "R3_grounded_read" in evidence


def test_apps_rg_surfaces_full_R3_contract_chain() -> None:
    """All 8 R3 contracts must be detected as direct imports in apps_rg.
    Note: apps_rg also has a pre-existing PromptEnvelope import in
    utils/anthropic_rag_entrypoint.py, so the total contract_count is 9
    (8 from spine_handoff.py + 1 PromptEnvelope from the existing
    consumer)."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_rg)
    detected = set(sc["distinct_contracts"])
    for required in (
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "SealedArtifact",
        "ExitReviewPacket",
    ):
        assert required in detected, (
            f"R3 required contract {required!r} not detected; "
            f"detected={sorted(detected)}"
        )


def test_apps_rg_existing_prompt_envelope_consumer_preserved() -> None:
    """The pre-existing PromptEnvelope import in
    apps_rg/utils/anthropic_rag_entrypoint.py must remain present. This
    is the original load-bearing R3 contract surface that motivated
    declaring R3_grounded_read; the migration MUST NOT remove it."""
    repo_root = Path(__file__).resolve().parents[4]
    consumer_path = (
        repo_root / "apps_rg" / "utils" / "anthropic_rag_entrypoint.py"
    )
    if not consumer_path.is_file():
        pytest.skip("apps_rg/utils/anthropic_rag_entrypoint.py not present")
    text = consumer_path.read_text(encoding="utf-8")
    assert (
        "from agentic_core.knowledge.retrieval.prompt_envelope "
        "import PromptEnvelope"
    ) in text, (
        "existing PromptEnvelope import was removed or rewritten; the "
        "migration must preserve apps_rg/utils/anthropic_rag_entrypoint.py"
    )
    # Sanity: the scanner must also see PromptEnvelope as a detected contract.
    _runtime_mode, _evidence, sc = _classify(consumer_path.parent.parent)
    assert "PromptEnvelope" in sc["distinct_contracts"], (
        f"PromptEnvelope not detected; distinct_contracts={sc['distinct_contracts']}"
    )


def test_apps_rg_is_not_build_time_compiler() -> None:
    """apps_rg must NOT declare or be classified as build_time_compiler."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_rg)
    assert "build_time_compiler" not in sc["manifest_claimed_routes"]


def test_apps_rg_is_not_formal_exception() -> None:
    """apps_rg is not exempt; it uses the standard GovernedAppRunner
    substrate. The scanner must NOT classify it as
    FORMAL_EXCEPTION_STATIC_EVIDENCE."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    runtime_mode, _evidence, sc = _classify(apps_rg)
    assert runtime_mode != "FORMAL_EXCEPTION_STATIC_EVIDENCE"
    assert sc["manifest_has_formal_exception"] is False
    assert sc["manifest_exception_reason_code"] == ""


def test_apps_rg_does_not_require_commit_request() -> None:
    """The pre-migration audit proved no durable-write surface exists in
    apps_rg (ATS scoring is read-side, LinkedIn references are
    pattern-mining). R3_grounded_read intentionally excludes
    CommitRequest, and apps_rg must NOT be promoted to
    R3R4_managed_workflow."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_rg)
    assert "CommitRequest" not in sc["manifest_required_contracts"], (
        f"apps_rg must not require CommitRequest; "
        f"required={sc['manifest_required_contracts']}"
    )
    assert "CommitRequest" not in sc["manifest_missing_contracts"]
    # Reinforce: route stays R3_grounded_read.
    assert "R3R4_managed_workflow" not in sc["manifest_claimed_routes"]


def test_apps_rg_is_not_R3R4_managed_workflow() -> None:
    """apps_rg must NOT be classified as R3R4_managed_workflow. The
    pre-migration audit found no durable-write surface, no CommitRequest,
    no StateDiffCandidate, no LinkedIn / ATS / profile-store write
    surface. Adding R3R4 would be contract theater."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_rg)
    assert sc["manifest_claimed_routes"] == ["R3_grounded_read"]
    # CommitRequest must not be among the imported contracts.
    assert "CommitRequest" not in sc["distinct_contracts"], (
        f"apps_rg spine_handoff.py must not import CommitRequest; "
        f"distinct_contracts={sc['distinct_contracts']}"
    )


def test_apps_rg_hitl_absent_does_not_change_route_shape() -> None:
    """GovernedRgRun does NOT declare HITL_ENABLED (defaults False).
    Same posture as apps_research; weaker than apps_lic /
    apps_exec. HITL is orthogonal to route classification."""
    from tools.analysis.apps_spine_coverage import (
        ROUTE_TYPE_CONTRACT_REQUIREMENTS,
    )
    repo_root = Path(__file__).resolve().parents[4]
    apps_rg = repo_root / "apps_rg"
    if not apps_rg.is_dir():
        pytest.skip("apps_rg not present in this checkout")
    runtime_mode, _evidence, sc = _classify(apps_rg)
    assert sc["manifest_claimed_routes"] == ["R3_grounded_read"]
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE"
    # The R3 chain alone does not require CommitRequest.
    r3_required = ROUTE_TYPE_CONTRACT_REQUIREMENTS["R3_grounded_read"]
    assert "CommitRequest" not in r3_required


def test_apps_rg_spine_handoff_module_imports_cleanly() -> None:
    """The apps_rg spine_handoff module must import without error,
    expose all 8 R3 contract types via R3_CONTRACT_SURFACE, and NOT
    expose CommitRequest as part of the surface or __all__."""
    from apps_rg.integrations import spine_handoff

    assert hasattr(spine_handoff, "R3_CONTRACT_SURFACE")
    surface = spine_handoff.R3_CONTRACT_SURFACE
    assert len(surface) == 8
    expected_names = {
        "ValidatedRequest", "L1PlanContract", "RouteContract",
        "RetrievalPlan", "FinalEvidenceContract", "CompiledPromptArtifact",
        "SealedArtifact", "ExitReviewPacket",
    }
    assert set(surface.keys()) == expected_names
    # CommitRequest must NOT be in the surface.
    assert "CommitRequest" not in surface
    for name, cls in surface.items():
        assert cls is not None, f"surface entry {name!r} is None"
        assert isinstance(cls, type), f"surface entry {name!r} is not a class"
    valid = spine_handoff.validate_rg_r3_contract_surface()
    assert valid == {n: True for n in expected_names}
    # The module's __all__ must not advertise CommitRequest.
    assert "CommitRequest" not in spine_handoff.__all__


# ===========================================================================
# W14 -- apps_shared formal-exception classification (core_adjacent_utility)
# ===========================================================================


def test_apps_shared_live_classifies_as_formal_exception_static_evidence() -> None:
    """apps_shared/spine_manifest.yaml must combine with the package's
    library-surface shape to classify as FORMAL_EXCEPTION_STATIC_EVIDENCE.
    Mirrors the apps_underwriting_ai W8 manifest pattern (also
    core_adjacent_utility, but with reason_code regulatory_domain rather
    than shared_library_surface)."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_shared)
    assert sc["manifest_present"] is True, "apps_shared/spine_manifest.yaml missing"
    assert "core_adjacent_utility" in sc["manifest_claimed_routes"], (
        f"manifest claimed_routes={sc['manifest_claimed_routes']}"
    )
    assert sc["manifest_exception_reason_code"] == "shared_library_surface", (
        f"got reason_code={sc['manifest_exception_reason_code']!r}; "
        "expected 'shared_library_surface'"
    )
    assert sc["manifest_compensating_controls_count"] >= 4, (
        f"got {sc['manifest_compensating_controls_count']} controls; "
        "expected the 4 CC-SHARED-* compensating controls"
    )
    assert sc["manifest_has_formal_exception"] is True
    assert runtime_mode == "FORMAL_EXCEPTION_STATIC_EVIDENCE", (
        f"got {runtime_mode}; evidence={evidence}"
    )


def test_apps_shared_no_longer_on_legacy_any_contract_path() -> None:
    """Before W14, apps_shared was APP_OVERLAY_STATIC_EVIDENCE via the
    legacy any-contract heuristic (1 SealedArtifact import in proof
    harness). After W14, it must be FORMAL_EXCEPTION_STATIC_EVIDENCE
    via the explicit manifest -- no longer on the legacy path."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    runtime_mode, evidence, sc = _classify(apps_shared)
    assert sc["manifest_present"] is True
    # The legacy-path evidence string is "no spine_manifest.yaml; ..."
    assert "no spine_manifest.yaml" not in evidence
    # apps_shared must NOT be APP_OVERLAY_STATIC_EVIDENCE anymore.
    assert runtime_mode != "APP_OVERLAY_STATIC_EVIDENCE", (
        f"apps_shared still on overlay path; evidence={evidence}"
    )
    assert runtime_mode == "FORMAL_EXCEPTION_STATIC_EVIDENCE"


def test_apps_shared_has_no_required_contracts() -> None:
    """core_adjacent_utility has an empty required-contract set by
    design; apps_shared HOSTS the substrate rather than CONSUMING it,
    so it should not be required to import the R3 chain."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_shared)
    assert sc["manifest_required_contracts"] == [], (
        f"core_adjacent_utility must have empty required-contract set; "
        f"got {sc['manifest_required_contracts']}"
    )


def test_apps_shared_has_no_missing_contracts() -> None:
    """No required contracts means none can be missing."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_shared)
    assert sc["manifest_missing_contracts"] == []


def test_apps_shared_does_not_have_spine_handoff_module() -> None:
    """apps_shared must NOT have a spine_handoff.py module. It is the
    HOST of the substrate; making it import the R3 contracts directly
    would understate its role and conflict with its formal-exception
    charter."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    spine_handoff = apps_shared / "integrations" / "spine_handoff.py"
    assert not spine_handoff.is_file(), (
        "apps_shared/integrations/spine_handoff.py exists; "
        "apps_shared is a substrate host, not a substrate consumer, and "
        "must NOT have a spine_handoff module"
    )


def test_apps_shared_compensating_controls_have_expected_prefix() -> None:
    """All CC-SHARED-* compensating controls (>=5 after the shim
    addendum) must be present and cite the expected substrate /
    registry / proof-harness / quarterly-review / shim themes."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_shared)
    controls = sc["manifest_compensating_controls"]
    assert len(controls) >= 5, (
        f"expected >=5 controls after CC-SHARED-05 addendum; got {len(controls)}"
    )
    # Every control must start with CC-SHARED-NN: prefix.
    for cc in controls:
        assert cc.startswith("CC-SHARED-"), (
            f"compensating control does not use the CC-SHARED-NN prefix: {cc!r}"
        )
    # Substantive themes -- substrate, registry, proof-harness, quarterly review.
    joined = " ".join(controls).lower()
    assert "governedapprunner" in joined or "substrate" in joined
    assert "app_registry" in joined or "registry" in joined
    assert "proof" in joined or "scenario_base" in joined
    assert "quarterly" in joined


def test_apps_shared_cc_shared_05_documents_agentic_core_shim() -> None:
    """CC-SHARED-05 must explicitly document apps_shared/_compat/agentic_core_shim.py
    as a tolerated compensating control: the full-stack no-op / early-return
    behavior, the standalone-only fallback branch, and the explicit statement
    that standalone mode is not runtime-certified / must not be used for
    risk-bearing execution."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_shared)
    controls = sc["manifest_compensating_controls"]
    # Find the CC-SHARED-05 entry.
    cc05 = next((cc for cc in controls if cc.startswith("CC-SHARED-05:")), None)
    assert cc05 is not None, (
        f"CC-SHARED-05 not present in manifest compensating_controls; "
        f"got prefixes={[cc.split(':', 1)[0] for cc in controls]}"
    )
    cc05_lower = cc05.lower()
    # Mentions the shim by name.
    assert "agentic_core_shim" in cc05_lower, (
        f"CC-SHARED-05 must reference agentic_core_shim by name: {cc05!r}"
    )
    # Mentions the full-stack no-op / early return behavior.
    assert "no-op" in cc05_lower or "early" in cc05_lower or "returns early" in cc05_lower, (
        f"CC-SHARED-05 must document the full-stack no-op / early-return behavior: {cc05!r}"
    )
    # Mentions standalone mode.
    assert "standalone" in cc05_lower, (
        f"CC-SHARED-05 must explicitly mention standalone mode: {cc05!r}"
    )
    # Mentions the non-certification / non-risk-bearing posture.
    assert (
        "not runtime-certified" in cc05_lower
        or "not runtime certified" in cc05_lower
        or "risk-bearing" in cc05_lower
    ), (
        f"CC-SHARED-05 must state standalone mode is not runtime-certified or "
        f"not risk-bearing: {cc05!r}"
    )


def test_apps_shared_review_cadence_is_quarterly() -> None:
    """Per the SVP_ENGINEERING_REVIEW.md infrastructure cadence, apps_shared
    is reviewed quarterly -- distinct from the annual cadence used by
    the apps_eval / apps_underwriting_ai domain-app exceptions."""
    repo_root = Path(__file__).resolve().parents[4]
    apps_shared = repo_root / "apps_shared"
    if not apps_shared.is_dir():
        pytest.skip("apps_shared not present in this checkout")
    _runtime_mode, _evidence, sc = _classify(apps_shared)
    assert sc["manifest_review_cadence"] == "quarterly"
