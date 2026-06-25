from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.spine.l6_shadow_eval_runner import (
    maybe_run_l6_v40_shadow_eval_for_section,
    run_l6_v40_shadow_eval_for_section,
)

from tests.l6_observability.test_runtime_exhaust_v40_adapter import _seed_artifacts


def test_apps_rg_v40_runner_writes_package_and_spans(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)

    outputs = run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
    )

    package = json.loads(outputs["l6_v40_shadow_eval_package"].read_text(encoding="utf-8"))
    assert package["valid_v40_shadow_exhaust"] is True
    assert package["g28_audit_completeness"]["verdict"] == "PASS"
    assert package["g29_learning_firewall"]["verdict"] == "PASS"
    assert package["current_run_x3_mutation_assertion"] is False
    assert outputs["l6_v40_shadow_eval_spans"].is_file()


def test_apps_rg_v40_runner_is_env_gated(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)

    default_outputs = maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={},
    )
    assert default_outputs["l6_v40_shadow_eval_package"].is_file()

    assert maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        env={"APPS_RG_L6_V40_SHADOW_EVAL_SKIP": "1"},
    ) == {}

    outputs = maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={"APPS_RG_L6_V40_SHADOW_EVAL": "1"},
    )
    assert outputs["l6_v40_shadow_eval_package"].is_file()
