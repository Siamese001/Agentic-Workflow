from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


def test_product_entry_mints_preflight_before_whole_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from apps_rg.runtime import product_entry

    run_dir = tmp_path / "full_resume_product"
    calls: list[str] = []

    monkeypatch.setattr(product_entry, "find_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        product_entry,
        "allocate_full_resume_artifact_dir",
        lambda repo, explicit: run_dir,
    )

    def _preflight(**kwargs: object) -> SimpleNamespace:
        calls.append("preflight")
        (run_dir / "e2e_preflight_continuation_receipt.json").write_text(
            "{}\n", encoding="utf-8"
        )
        return SimpleNamespace(passed=True, result={}, receipt={}, bootstrap_receipt={})

    def _whole_run(**kwargs: object) -> dict[str, object]:
        calls.append("whole_run")
        assert kwargs["artifact_dir"] == str(run_dir)
        assert kwargs["require_fresh_preflight"] is True
        assert str(kwargs["preflight_continuation_ref"]).endswith(
            "e2e_preflight_continuation_receipt.json"
        )
        return {"product_authorized": False, "pipeline_complete": False}

    monkeypatch.setattr(
        "apps_rg.runtime.e2e_preflight.run_fresh_e2e_preflight", _preflight
    )
    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration."
        "run_whole_run_with_route_governance",
        _whole_run,
    )

    result = product_entry.run_product_whole_run_from_primitives(
        target_company="Anthropic",
        target_role="Manager",
    )

    assert calls == ["preflight", "whole_run"]
    assert result["authority_contract_id"] == "apps_research_rg_e2e_authority"


def test_product_entry_stops_when_preflight_blocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from apps_rg.runtime import product_entry

    run_dir = tmp_path / "full_resume_blocked"
    monkeypatch.setattr(product_entry, "find_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        product_entry,
        "allocate_full_resume_artifact_dir",
        lambda repo, explicit: run_dir,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.e2e_preflight.run_fresh_e2e_preflight",
        lambda **kwargs: SimpleNamespace(
            passed=False,
            result={"exit_status": "error", "fault": "PREFLIGHT_BLOCKED"},
            receipt={"status": "BLOCKED"},
            bootstrap_receipt={},
        ),
    )

    result = product_entry.run_product_whole_run_from_primitives(
        target_company="Anthropic",
        target_role="Manager",
    )

    assert result["fault"] == "PREFLIGHT_BLOCKED"
    assert result["product_authorized"] is False
    assert result["pipeline_complete"] is False


def test_product_entry_rejects_non_fresh_explicit_artifact_dir(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime import product_entry

    run_dir = tmp_path / "existing"
    run_dir.mkdir()
    (run_dir / "stale.json").write_text("{}\n", encoding="utf-8")

    result = product_entry.run_product_whole_run_from_primitives(
        target_company="Anthropic",
        target_role="Manager",
        artifact_dir=str(run_dir),
    )

    assert result["fault"] == "PRODUCT_ARTIFACT_DIR_NOT_FRESH"
    assert result["product_authorized"] is False


def test_canonical_dispatch_routes_only_full_scope_to_product_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.orchestration import canonical_dispatch

    monkeypatch.setattr(
        "apps_rg.runtime.product_entry.run_product_whole_run_from_primitives",
        lambda **kwargs: {"route": "product"},
    )
    monkeypatch.setattr(
        "apps_rg.runtime.spine.apps_rg_spine_run.run_apps_rg_spine",
        lambda **kwargs: {"route": "section", "scope": kwargs["scope"]},
    )

    product = canonical_dispatch.run_canonical_apps_rg_from_cli_primitives(
        target_company="Anthropic",
        target_role="Manager",
    )
    section = canonical_dispatch.run_canonical_apps_rg_from_cli_primitives(
        target_company="Anthropic",
        target_role="Manager",
        section="headline",
    )

    assert product == {"route": "product"}
    assert section == {"route": "section", "scope": "section"}
