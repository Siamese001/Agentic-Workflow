"""Minimal sovereignty interface contracts used by the mandatory Guardian gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.sealed_interface_check_enforcer import (
    check_file,
    run_check,
)
from agentic_core.L6_system_learning.adapters.live_run_pipeline_adapter import (
    ActivationAuthorizationError,
    LiveRunPipelineAdapter,
)
from agentic_core.L6_system_learning.enforcement.dual_injection_proposal_gate import (
    decide_activation_mode,
)
from agentic_core.L6_system_learning.engines.change_package_impl import ChangePackage


def _write_module(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def test_change_package_canonical_bytes_are_json_only() -> None:
    package = ChangePackage(
        source="l6-shadow",
        target="future-run",
        changes=b'{"threshold":0.82}',
        confidence=0.91,
        reason=("shadow-eval-ready",),
        timestamp_utc=1_750_000_000,
        authority_sensitivity="LOW",
        target_surface="runtime_proposal",
    )

    payload = json.loads(package.canonical_bytes().decode("utf-8"))

    assert payload["source"] == "l6-shadow"
    assert payload["target"] == "future-run"
    assert payload["changes"] == '{"threshold":0.82}'
    assert payload["reason"] == ["shadow-eval-ready"]
    assert package.canonical_bytes() == package.canonical_bytes()


def test_activation_defaults_to_proposal_only_without_dual_injection() -> None:
    decision = decide_activation_mode(
        requested_proposal_only=False,
        version_store=None,
        approval_gate=object(),
    )

    assert decision.is_active is False
    assert decision.proposal_only is True
    assert decision.reason_code == "FALLBACK_PROPOSAL_ONLY_MISSING_DEPENDENCY"


def test_activation_allowed_only_when_both_dependencies_are_injected() -> None:
    decision = decide_activation_mode(
        requested_proposal_only=False,
        version_store=object(),
        approval_gate=object(),
    )

    assert decision.is_active is True
    assert decision.proposal_only is False
    assert decision.reason_code == "ACTIVATION_GRANTED_MANDATORY_APPLICATION"


def test_live_run_adapter_blocks_mutation_without_approval_token() -> None:
    adapter = LiveRunPipelineAdapter(intake_adapter=object())

    with pytest.raises(ActivationAuthorizationError):
        adapter.run(
            repo_root=Path.cwd(),
            now_utc=1_750_000_000,
            window_start_utc=1_749_999_000,
            proposal_only=False,
        )


def test_sealed_interface_check_allows_public_interfaces(tmp_path: Path) -> None:
    module = _write_module(
        tmp_path / "apps_demo" / "clean.py",
        "from agentic_core.interfaces.execution import ExecutionAgentProtocol\n",
    )

    assert check_file(module) == []
    assert run_check([tmp_path / "apps_demo"]) == []


def test_sealed_interface_check_detects_direct_layer_import(tmp_path: Path) -> None:
    module = _write_module(
        tmp_path / "apps_demo" / "bad_layer.py",
        "from agentic_core.L4_state.reasoning.meta_learning_feedback import CompletenessChangePackage\n",
    )

    violations = check_file(module)

    assert any("DIRECT_LAYER_IMPORT" in violation for violation in violations)


def test_sealed_interface_check_detects_private_interface_import(tmp_path: Path) -> None:
    module = _write_module(
        tmp_path / "apps_demo" / "bad_private.py",
        "import agentic_core.interfaces._execution_impl\n",
    )

    violations = check_file(module)

    assert any("SEALED_IMPL_BYPASS" in violation for violation in violations)
