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


def test_overlay_valid_when_any_canonical_contract_imported(tmp_path: Path) -> None:
    """Importing one canonical contract directly from agentic_core suffices."""
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
    assert runtime_mode == "APP_OVERLAY_VALID"
    assert "RouteContract" in sc["distinct_contracts"]
    assert "RouteContract" in evidence
    assert sc["claims_domain_runtime"] is True


def test_overlay_valid_with_multiple_contracts(tmp_path: Path) -> None:
    """Multiple contracts are reported in the evidence."""
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
    runtime_mode, evidence, sc = _classify(app)
    assert runtime_mode == "APP_OVERLAY_VALID"
    assert sc["contract_count"] == 6
    assert set(sc["distinct_contracts"]) == {
        "L1PlanContract", "RouteContract",
        "FinalEvidenceContract", "CompiledPromptArtifact",
        "SealedArtifact", "ExitReviewPacket",
    }


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
    assert runtime_mode != "APP_OVERLAY_VALID"
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
    bulk_imports = "\n".join(
        f"from agentic_core.utils.module_{i} import helper_{i}" for i in range(40)
    )
    app = _make_app(
        tmp_path,
        "apps_synth_heavy_no_contracts",
        files={
            "engines/__init__.py": "",
            "engines/heavy_consumer.py": f"""
                {bulk_imports}

                def run(req):
                    return helper_0(req)
            """,
        },
    )
    runtime_mode, _evidence, sc = _classify(app)
    # Legacy spine_coverage_pct will be very high because most non-stdlib
    # imports are agentic_core. But runtime_mode must NOT be valid.
    assert sc["spine_coverage_pct"] > 50
    assert runtime_mode != "APP_OVERLAY_VALID"
    assert runtime_mode == "PARTIAL_SPINE_STATIC_ONLY"


# ---------------------------------------------------------------------------
# Live workspace — apps_qna evidence
# ---------------------------------------------------------------------------


def test_apps_qna_currently_partial_or_forbidden() -> None:
    """apps_qna in the LIVE workspace must NOT be APP_OVERLAY_VALID.

    Per the evidence audit: apps_qna imports zero canonical contracts.
    It claims a domain runtime (engines / integrations / router / CLI /
    wizard). The classification must be one of the two demotion buckets.
    """
    repo_root = Path(__file__).resolve().parents[4]
    apps_qna = repo_root / "apps_qna"
    if not apps_qna.is_dir():
        pytest.skip("apps_qna not present in this checkout")
    runtime_mode, _evidence, sc = _classify(apps_qna)
    assert runtime_mode in {
        "PARTIAL_SPINE_STATIC_ONLY",
        "APP_STANDALONE_FORBIDDEN",
    }, f"got {runtime_mode}; expected forbidden-tier classification"
    assert sc["contract_count"] == 0
    assert sc["claims_domain_runtime"] is True


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
