"""Governance — Exit → RuntimeExhaustBundle handoff (W3).

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_build_exhaust_bundle_populates_required_fields() -> None:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from apps_rg.runtime.bindings.exit_binding import (
        build_exhaust_bundle_from_exit,
        exit_finalize_apps_rg,
    )
    from agentic_core.runtime.exhaust.runtime_exhaust_bundle import RuntimeExhaustBundle

    sealed = SealedL2Artifact(
        request_id="req-h1",
        run_id="run-h1",
        app_id="apps_rg",
        trace_id="trace-h1",
        execution_status="completed",
        compilation_hash="sha256::exit_digest_123",
        gate_verdict_refs=("gmesh::demo",),
        l5_certification_ref="cert-harness",
    )
    exit_res = exit_finalize_apps_rg(sealed, target_company="Co", target_role="Role")
    bundle = build_exhaust_bundle_from_exit(exit_res, sealed)
    assert isinstance(bundle, RuntimeExhaustBundle)
    assert bundle.run_id == "run-h1"
    assert bundle.trace_root == "trace-h1"
    assert bundle.exit_disposition_ref


def test_exhaust_bundle_dataclass_is_frozen() -> None:
    from dataclasses import is_dataclass

    from agentic_core.runtime.exhaust.runtime_exhaust_bundle import RuntimeExhaustBundle

    assert is_dataclass(RuntimeExhaustBundle)
    assert RuntimeExhaustBundle.__dataclass_params__.frozen is True


def test_canonical_exhaust_bundle_raises_without_exit_ref() -> None:
    from agentic_core.runtime.exhaust.runtime_exhaust_bundle import build_runtime_exhaust_bundle

    with pytest.raises(ValueError, match="exit_disposition_ref"):
        build_runtime_exhaust_bundle(
            request_id="r",
            run_id="run",
            trace_root="t",
            exit_disposition_ref="",
        )


def test_canonical_exhaust_bundle_raises_if_not_after_exit() -> None:
    from agentic_core.runtime.exhaust.runtime_exhaust_bundle import RuntimeExhaustBundle

    with pytest.raises(ValueError, match="created_after_exit"):
        RuntimeExhaustBundle(
            created_after_exit=False,
            current_run_closed=True,
        )


def test_build_exhaust_bundle_uses_canonical_factory() -> None:
    from apps_rg.runtime.bindings import exit_binding

    src = inspect.getsource(exit_binding.build_exhaust_bundle_from_exit)
    assert "build_runtime_exhaust_bundle" in src
    assert "agentic_core.runtime.exhaust.runtime_exhaust_bundle" in src


def test_exhaust_bundle_builder_only_in_apps_rg() -> None:
    from apps_rg.runtime.bindings.exit_binding import build_exhaust_bundle_from_exit

    assert "apps_rg" in build_exhaust_bundle_from_exit.__module__


def test_runtime_exhaust_bundle_source_has_no_apps_rg_executable_literals() -> None:
    path = REPO_ROOT / "agentic_core" / "runtime" / "exhaust" / "runtime_exhaust_bundle.py"
    text = path.read_text(encoding="utf-8")
    for idx, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "apps_rg" in line:
            pytest.fail(f"apps_rg literal in executable line {idx}: {line!r}")
