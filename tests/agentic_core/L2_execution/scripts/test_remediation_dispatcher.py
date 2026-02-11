"""
Tests for the L2 remediation dispatcher skeleton.

Proves:
1. Dispatcher writes combined_heal_result.json.
2. Output validates via CombinedHealResult.validate().
3. Results sorted by check_id; all status SKIPPED; notes == "no healer registered".
4. approved_by includes only APPROVED tokens and is sorted.
5. Unknown aggregate shape raises ValueError.
6. created_utc is exactly the provided CLI value.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L2_execution.scripts.remediation_dispatcher import (
    NOTE_MAPPED,
    NOTE_UNMAPPED,
    OUTPUT_FILENAME,
    SANDBOX_SENTINEL,
    TOOL_ID,
    ApprovalGatingError,
    MutationGuardError,
    approvals_satisfy_phase,
    classify_check_ids,
    extract_check_ids,
    run_dispatcher,
    validate_phase_names,
)
from agentic_core.L2_execution.types.heal_contract import (
    HealStatus,
    check_schema_compatibility,
)
from agentic_core.L2_execution.types.l2_phase_spec import (
    L2ExecutionPlan,
    PhaseSpec,
)

TIMESTAMP = "2026-01-01T00:00:00Z"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _write_guardian_aggregate(
    path: Path,
    check_ids: list[str],
    evidence_overrides: dict[str, dict] | None = None,
) -> Path:
    """Write a minimal guardian aggregate JSON with given check_ids."""
    overrides = evidence_overrides or {}
    data = {
        "guardian_id": "combined",
        "version": 2,
        "status": "FAIL",
        "summary": "test aggregate",
        "checks": [
            {
                "check_id": cid,
                "status": "FAIL",
                "details": f"check {cid}",
                "evidence": overrides.get(cid, {}),
            }
            for cid in check_ids
        ],
        "artifacts": [],
        "metrics": {},
        "remediation_hints": [],
        "artifact_class": "aggregate",
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _write_approval_bundle(path: Path) -> Path:
    """Write an approval bundle with mixed decisions and out-of-order tokens."""
    data = {
        "contract_version": 1,
        "records": [
            {
                "phase_name": "healing",
                "guardian_id": None,
                "check_ids": [],
                "decision": "REJECTED",
                "approver": "admin@example.com",
                "rationale": "Not ready",
                "token": "t1",
                "created_utc": TIMESTAMP,
            },
            {
                "phase_name": "discovery",
                "guardian_id": None,
                "check_ids": [],
                "decision": "APPROVED",
                "approver": "lead@example.com",
                "rationale": None,
                "token": "t2",
                "created_utc": TIMESTAMP,
            },
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture()
def guardian_aggregate(tmp_path: Path) -> Path:
    """Guardian aggregate with 3 check_ids in unsorted order."""
    return _write_guardian_aggregate(
        tmp_path / "combined_guardian_result.json",
        ["guardian_hygiene", "guardian_drift_detection", "guardian_location_alignment"],
    )


@pytest.fixture()
def approval_bundle(tmp_path: Path) -> Path:
    return _write_approval_bundle(tmp_path / "approval_bundle.json")


@pytest.fixture()
def output_dir(tmp_path: Path) -> Path:
    out = tmp_path / "output"
    out.mkdir()
    return out


# ---------------------------------------------------------------------------
# Core dispatcher tests
# ---------------------------------------------------------------------------


class TestDispatcherOutput:
    """Proves dispatcher writes valid, deterministic output."""

    def test_writes_combined_heal_result(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        assert (output_dir / OUTPUT_FILENAME).exists()

    def test_output_validates(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        assert result.validate() == []

    def test_schema_compatibility(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_output_json_parseable(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        data = json.loads((output_dir / OUTPUT_FILENAME).read_text(encoding="utf-8"))
        assert data["tool_id"] == TOOL_ID

    def test_created_utc_exact(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        assert result.created_utc == TIMESTAMP
        data = json.loads((output_dir / OUTPUT_FILENAME).read_text(encoding="utf-8"))
        assert data["created_utc"] == TIMESTAMP


# ---------------------------------------------------------------------------
# Sorting and status
# ---------------------------------------------------------------------------


class TestDispatcherSortingAndStatus:
    """Proves results are sorted, all SKIPPED, with correct notes."""

    def test_results_sorted_by_check_id(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        d = result.to_dict()
        ids = [r["check_id"] for r in d["results"]]
        assert ids == sorted(ids)

    def test_all_statuses_skipped(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        for check in result.results:
            assert check.status == HealStatus.SKIPPED

    def test_mapped_notes(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        notes_by_id = {c.check_id: c.notes for c in result.results}
        assert notes_by_id["guardian_drift_detection"] == "dry-run healer planned actions"
        assert notes_by_id["guardian_location_alignment"] == NOTE_MAPPED
        assert notes_by_id["guardian_hygiene"] == NOTE_UNMAPPED

    def test_non_healer_changes_made_empty(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        for check in result.results:
            if check.check_id != "guardian_drift_detection":
                assert check.changes_made == ()

    def test_plan_name_default(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        assert result.plan_name == "LEGACY_MIRROR_PLAN"


# ---------------------------------------------------------------------------
# Approval bundle integration
# ---------------------------------------------------------------------------


class TestDispatcherApproval:
    """Proves approval bundle is consumed correctly."""

    def test_approved_tokens_included(
        self,
        guardian_aggregate: Path,
        approval_bundle: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
            approval_bundle_path=approval_bundle,
        )
        assert "t2" in result.approved_by

    def test_rejected_tokens_excluded(
        self,
        guardian_aggregate: Path,
        approval_bundle: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
            approval_bundle_path=approval_bundle,
        )
        assert "t1" not in result.approved_by

    def test_approved_by_sorted(
        self,
        tmp_path: Path,
        output_dir: Path,
    ) -> None:
        # Create bundle with multiple approved tokens out of order
        bundle_data = {
            "contract_version": 1,
            "records": [
                {
                    "phase_name": "healing",
                    "guardian_id": None,
                    "check_ids": [],
                    "decision": "APPROVED",
                    "approver": "a@x.com",
                    "rationale": None,
                    "token": "z_tok",
                    "created_utc": TIMESTAMP,
                },
                {
                    "phase_name": "discovery",
                    "guardian_id": None,
                    "check_ids": [],
                    "decision": "APPROVED",
                    "approver": "b@x.com",
                    "rationale": None,
                    "token": "a_tok",
                    "created_utc": TIMESTAMP,
                },
            ],
        }
        bundle_path = tmp_path / "bundle.json"
        bundle_path.write_text(json.dumps(bundle_data), encoding="utf-8")
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["check_a"],
        )
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
            approval_bundle_path=bundle_path,
        )
        d = result.to_dict()
        assert d["approved_by"] == ["a_tok", "z_tok"]

    def test_no_approval_bundle_empty_approved_by(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        assert result.approved_by == ()


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------


class TestDispatcherNegative:
    """Proves error handling for invalid inputs."""

    def test_unknown_aggregate_shape_raises(self, tmp_path: Path) -> None:
        bad_agg = tmp_path / "bad.json"
        bad_agg.write_text(json.dumps({"not_checks": []}), encoding="utf-8")
        with pytest.raises(ValueError, match="Unrecognised guardian aggregate shape"):
            run_dispatcher(
                guardian_result_path=bad_agg,
                write_artifacts_dir=tmp_path / "out",
                created_utc=TIMESTAMP,
            )

    def test_bad_check_item_raises(self, tmp_path: Path) -> None:
        bad_agg = tmp_path / "bad2.json"
        bad_agg.write_text(
            json.dumps({"checks": ["not_a_dict"]}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Unexpected check item shape"):
            run_dispatcher(
                guardian_result_path=bad_agg,
                write_artifacts_dir=tmp_path / "out",
                created_utc=TIMESTAMP,
            )

    def test_extract_check_ids_deduplicates(self) -> None:
        data = {
            "checks": [
                {"check_id": "a", "status": "PASS", "details": "", "evidence": {}},
                {"check_id": "a", "status": "FAIL", "details": "", "evidence": {}},
                {"check_id": "b", "status": "PASS", "details": "", "evidence": {}},
            ],
        }
        ids = extract_check_ids(data)
        assert ids == ["a", "b"]


# ---------------------------------------------------------------------------
# PhaseSpec validation
# ---------------------------------------------------------------------------


class TestPhaseSpecValidation:
    """Proves PhaseSpec name integrity is enforced."""

    def test_valid_plan_passes(self) -> None:
        from agentic_core.L2_execution.types.l2_phase_spec import LEGACY_MIRROR_PLAN

        validate_phase_names(LEGACY_MIRROR_PLAN)

    def test_wrong_names_raises(self) -> None:
        bad_plan = L2ExecutionPlan(
            phases=(
                PhaseSpec(name="wrong_phase_1"),
                PhaseSpec(name="wrong_phase_2"),
            ),
        )
        with pytest.raises(ValueError, match="PhaseSpec name integrity violation"):
            validate_phase_names(bad_plan)

    def test_wrong_order_raises(self) -> None:
        bad_plan = L2ExecutionPlan(
            phases=(
                PhaseSpec(name="discovery"),
                PhaseSpec(name="pre_audit"),
                PhaseSpec(name="reconciliation"),
                PhaseSpec(name="alignment"),
                PhaseSpec(name="arch_validation"),
                PhaseSpec(name="healing"),
                PhaseSpec(name="certification"),
            ),
        )
        with pytest.raises(ValueError, match="PhaseSpec name integrity violation"):
            validate_phase_names(bad_plan)

    def test_missing_phase_raises(self) -> None:
        bad_plan = L2ExecutionPlan(
            phases=(
                PhaseSpec(name="pre_audit"),
                PhaseSpec(name="discovery"),
            ),
        )
        with pytest.raises(ValueError, match="PhaseSpec name integrity violation"):
            validate_phase_names(bad_plan)


# ---------------------------------------------------------------------------
# Phase mapping classification
# ---------------------------------------------------------------------------


class TestClassifyCheckIds:
    """Proves check_id classification into mapped/unmapped."""

    def test_mapped_ids(self) -> None:
        mapped, unmapped = classify_check_ids(
            ["guardian_drift_detection", "guardian_location_alignment", "guardian_hygiene"],
        )
        assert "guardian_drift_detection" in mapped
        assert "guardian_location_alignment" in mapped
        assert "guardian_hygiene" in unmapped

    def test_all_unmapped(self) -> None:
        mapped, unmapped = classify_check_ids(["guardian_foo", "guardian_bar"])
        assert mapped == set()
        assert unmapped == {"guardian_foo", "guardian_bar"}

    def test_empty_input(self) -> None:
        mapped, unmapped = classify_check_ids([])
        assert mapped == set()
        assert unmapped == set()

    def test_prefix_matching(self) -> None:
        mapped, unmapped = classify_check_ids(
            ["guardian_drift_detection_extra"],
        )
        assert "guardian_drift_detection_extra" in mapped


# ---------------------------------------------------------------------------
# Approval gating enforcement
# ---------------------------------------------------------------------------


class TestApprovalGating:
    """Proves approval gating blocks/allows correctly."""

    def test_healing_phase_blocks_without_approval(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="healing"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
            )

    def test_healing_phase_allows_with_phase_wide_approval(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        bundle_data = {
            "contract_version": 1,
            "records": [
                {
                    "phase_name": "healing",
                    "guardian_id": None,
                    "check_ids": [],
                    "decision": "APPROVED",
                    "approver": "lead@example.com",
                    "rationale": None,
                    "token": "t-ok",
                    "created_utc": TIMESTAMP,
                },
            ],
        }
        bundle_path = tmp_path / "bundle.json"
        bundle_path.write_text(json.dumps(bundle_data), encoding="utf-8")
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            approval_bundle_path=bundle_path,
        )
        assert result.validate() == []
        d = result.to_dict()
        assert d["approved_by"] == ["t-ok"]

    def test_non_healing_phases_do_not_require_approval(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        assert result.validate() == []

    def test_healing_phase_rejected_only_still_blocks(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        bundle_data = {
            "contract_version": 1,
            "records": [
                {
                    "phase_name": "healing",
                    "guardian_id": None,
                    "check_ids": [],
                    "decision": "REJECTED",
                    "approver": "lead@example.com",
                    "rationale": "Not ready",
                    "token": "t-rej",
                    "created_utc": TIMESTAMP,
                },
            ],
        }
        bundle_path = tmp_path / "bundle.json"
        bundle_path.write_text(json.dumps(bundle_data), encoding="utf-8")
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="healing"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
                approval_bundle_path=bundle_path,
            )

    def test_wrong_phase_approval_does_not_satisfy(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        bundle_data = {
            "contract_version": 1,
            "records": [
                {
                    "phase_name": "discovery",
                    "guardian_id": None,
                    "check_ids": [],
                    "decision": "APPROVED",
                    "approver": "lead@example.com",
                    "rationale": None,
                    "token": "t-wrong",
                    "created_utc": TIMESTAMP,
                },
            ],
        }
        bundle_path = tmp_path / "bundle.json"
        bundle_path.write_text(json.dumps(bundle_data), encoding="utf-8")
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="healing"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
                approval_bundle_path=bundle_path,
            )


class TestApprovalsSatisfyPhase:
    """Proves the pure approval matcher function."""

    def test_none_bundle_returns_false(self) -> None:
        assert approvals_satisfy_phase(None, "healing") is False

    def test_matching_approval_returns_true(self) -> None:
        from agentic_core.L3_orchestration.types.approval_contract import (
            ApprovalBundle,
            ApprovalDecision,
            ApprovalRecord,
        )

        bundle = ApprovalBundle(
            records=(
                ApprovalRecord(
                    phase_name="healing",
                    decision=ApprovalDecision.APPROVED,
                    approver="a@x.com",
                    token="t1",
                    created_utc=TIMESTAMP,
                ),
            ),
        )
        assert approvals_satisfy_phase(bundle, "healing") is True

    def test_wrong_phase_returns_false(self) -> None:
        from agentic_core.L3_orchestration.types.approval_contract import (
            ApprovalBundle,
            ApprovalDecision,
            ApprovalRecord,
        )

        bundle = ApprovalBundle(
            records=(
                ApprovalRecord(
                    phase_name="discovery",
                    decision=ApprovalDecision.APPROVED,
                    approver="a@x.com",
                    token="t1",
                    created_utc=TIMESTAMP,
                ),
            ),
        )
        assert approvals_satisfy_phase(bundle, "healing") is False

    def test_rejected_returns_false(self) -> None:
        from agentic_core.L3_orchestration.types.approval_contract import (
            ApprovalBundle,
            ApprovalDecision,
            ApprovalRecord,
        )

        bundle = ApprovalBundle(
            records=(
                ApprovalRecord(
                    phase_name="healing",
                    decision=ApprovalDecision.REJECTED,
                    approver="a@x.com",
                    token="t1",
                    created_utc=TIMESTAMP,
                ),
            ),
        )
        assert approvals_satisfy_phase(bundle, "healing") is False


# ---------------------------------------------------------------------------
# Deterministic result set
# ---------------------------------------------------------------------------


class TestDispatcherResultSetUnchanged:
    """Proves same check_ids in output for same input."""

    def test_same_check_ids_as_input(
        self,
        guardian_aggregate: Path,
        output_dir: Path,
    ) -> None:
        result = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=output_dir,
            created_utc=TIMESTAMP,
        )
        output_ids = sorted(c.check_id for c in result.results)
        assert output_ids == [
            "guardian_drift_detection",
            "guardian_hygiene",
            "guardian_location_alignment",
        ]

    def test_idempotent_runs(
        self,
        guardian_aggregate: Path,
        tmp_path: Path,
    ) -> None:
        out1 = tmp_path / "out1"
        out1.mkdir()
        out2 = tmp_path / "out2"
        out2.mkdir()
        r1 = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=out1,
            created_utc=TIMESTAMP,
        )
        r2 = run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=out2,
            created_utc=TIMESTAMP,
        )
        assert r1.to_dict() == r2.to_dict()


# ---------------------------------------------------------------------------
# Healer wiring in dispatcher
# ---------------------------------------------------------------------------


class TestDispatcherHealerWiring:
    """Proves dispatcher calls registered healers and records results."""

    def test_drift_healer_invoked_with_evidence(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection", "guardian_hygiene"],
            evidence_overrides={
                "guardian_drift_detection": {
                    "forbidden_folders": ["z_bad", "a_bad"],
                    "archived_files_at_root": ["old.bak"],
                },
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        drift_result = next(c for c in result.results if c.check_id == "guardian_drift_detection")
        assert drift_result.notes == "dry-run healer planned actions"
        assert len(drift_result.changes_made) > 0
        assert drift_result.changes_made == tuple(sorted(drift_result.changes_made))

    def test_drift_healer_planned_actions_content(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {
                    "forbidden_folders": ["tmp"],
                    "duplicate_folders": ["utils_copy"],
                },
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        drift_result = next(c for c in result.results if c.check_id == "guardian_drift_detection")
        assert "would_remove_root_folder:tmp" in drift_result.changes_made
        assert "would_resolve_duplicate_folder:utils_copy" in drift_result.changes_made

    def test_unmapped_checks_unchanged_with_healer(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection", "guardian_hygiene"],
            evidence_overrides={
                "guardian_drift_detection": {"forbidden_folders": ["x"]},
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        hygiene_result = next(c for c in result.results if c.check_id == "guardian_hygiene")
        assert hygiene_result.notes == NOTE_UNMAPPED
        assert hygiene_result.changes_made == ()

    def test_healer_with_empty_evidence_still_skipped(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        drift_result = next(c for c in result.results if c.check_id == "guardian_drift_detection")
        assert drift_result.status == HealStatus.SKIPPED
        assert drift_result.changes_made == ()
        assert drift_result.notes == "dry-run healer planned actions"

    def test_approval_gating_still_enforced_with_healer(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="healing"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
            )


# ---------------------------------------------------------------------------
# Mutation guard + apply mode
# ---------------------------------------------------------------------------


class TestDispatcherMutationGuard:
    """Proves mutation guard blocks apply without sandbox or override."""

    def test_apply_without_repo_root_raises(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(MutationGuardError, match="--repo-root"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
                apply=True,
            )

    def test_apply_without_sandbox_raises(self, tmp_path: Path) -> None:
        repo = tmp_path / "real_repo"
        repo.mkdir()
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(MutationGuardError, match="not a sandbox"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
                apply=True,
                repo_root=repo,
            )

    def test_apply_with_sandbox_sentinel_succeeds(self, tmp_path: Path) -> None:
        repo = tmp_path / "sandbox_repo"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
        )
        assert result is not None

    def test_apply_with_override_succeeds(self, tmp_path: Path) -> None:
        repo = tmp_path / "real_repo"
        repo.mkdir()
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
            allow_repo_mutation=True,
        )
        assert result is not None


class TestDispatcherApplyMode:
    """Proves apply mode performs mutations in sandbox and is idempotent."""

    def test_apply_mutates_sandbox(self, tmp_path: Path) -> None:
        repo = tmp_path / "sandbox"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        (repo / "empty_bad").mkdir()
        (repo / "old.bak").write_text("x", encoding="utf-8")

        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {
                    "forbidden_folders": ["empty_bad"],
                    "archived_files_at_root": ["old.bak"],
                },
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
        )
        drift = next(c for c in result.results if c.check_id == "guardian_drift_detection")
        assert not (repo / "empty_bad").exists()
        assert not (repo / "old.bak").exists()
        assert "removed_root_folder:empty_bad" in drift.changes_made
        assert "removed_archived_file:old.bak" in drift.changes_made
        assert drift.status == HealStatus.HEALED

    def test_apply_idempotent_second_run(self, tmp_path: Path) -> None:
        repo = tmp_path / "sandbox"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        (repo / "empty_bad").mkdir()

        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {
                    "forbidden_folders": ["empty_bad"],
                },
            },
        )
        out1 = tmp_path / "out1"
        out1.mkdir()
        r1 = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out1,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
        )
        d1 = next(c for c in r1.results if c.check_id == "guardian_drift_detection")
        assert len(d1.changes_made) == 1

        out2 = tmp_path / "out2"
        out2.mkdir()
        r2 = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out2,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
        )
        d2 = next(c for c in r2.results if c.check_id == "guardian_drift_detection")
        assert d2.changes_made == ()
        assert d2.notes == "healed: nothing to do"

    def test_dry_run_default_no_mutation(self, tmp_path: Path) -> None:
        repo = tmp_path / "sandbox"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        (repo / "empty_bad").mkdir()

        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {
                    "forbidden_folders": ["empty_bad"],
                },
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        assert (repo / "empty_bad").exists()


# ---------------------------------------------------------------------------
# No side effects
# ---------------------------------------------------------------------------


class TestDispatcherNoSideEffects:
    """Proves only the output JSON is written."""

    def test_only_output_json(
        self,
        guardian_aggregate: Path,
        tmp_path: Path,
    ) -> None:
        out_dir = tmp_path / "clean_out"
        out_dir.mkdir()
        before = {str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*") if f.is_file()}

        run_dispatcher(
            guardian_result_path=guardian_aggregate,
            write_artifacts_dir=out_dir,
            created_utc=TIMESTAMP,
        )

        after = {str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*") if f.is_file()}
        new_files = after - before
        assert len(new_files) == 1
        assert OUTPUT_FILENAME in new_files.pop()

    def test_healer_no_filesystem_mutations(
        self,
        tmp_path: Path,
    ) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {
                    "forbidden_folders": ["should_not_be_deleted"],
                },
            },
        )
        out_dir = tmp_path / "clean_out"
        out_dir.mkdir()
        before = {str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*") if f.is_file()}

        run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out_dir,
            created_utc=TIMESTAMP,
        )

        after = {str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*") if f.is_file()}
        new_files = after - before
        assert len(new_files) == 1
        assert OUTPUT_FILENAME in new_files.pop()
