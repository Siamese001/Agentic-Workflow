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

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L2_execution.scripts.remediation_dispatcher import (
    HEALER_ESCALATION_ALLOWLIST,
    NOTE_MAPPED,
    NOTE_UNMAPPED,
    OUTPUT_FILENAME,
    SANDBOX_SENTINEL,
    TOOL_ID,
    ApprovalGatingError,
    EscalationContext,
    MutationGuardError,
    _invoke_healer,
    _tier_escalate,
    approvals_satisfy_phase,
    build_healer_worklist,
    classify_check_ids,
    extract_check_ids,
    extract_healable_items_from_guardian_check,
    run_dispatcher,
    validate_phase_names,
)
from agentic_core.L2_execution.types.heal_contract import (
    HealCheckResult,
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


def _write_healing_approval(path: Path, token: str = "t-heal") -> Path:  # noqa: S107
    """Write an approval bundle with a single APPROVED record for healing."""
    data = {
        "contract_version": 1,
        "records": [
            {
                "phase_name": "healing",
                "guardian_id": None,
                "check_ids": [],
                "decision": "APPROVED",
                "approver": "auto@test",
                "rationale": None,
                "token": token,
                "created_utc": TIMESTAMP,
            },
        ],
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

    def test_phase_blocks_without_approval(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from agentic_core.L2_execution.scripts import remediation_dispatcher as _mod

        monkeypatch.setitem(_mod.PHASE_APPROVAL_REQUIRED_OVERRIDES, "arch_validation", True)
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="arch_validation"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
            )

    def test_phase_allows_with_matching_approval(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from agentic_core.L2_execution.scripts import remediation_dispatcher as _mod

        monkeypatch.setitem(_mod.PHASE_APPROVAL_REQUIRED_OVERRIDES, "arch_validation", True)
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        bundle_data = {
            "contract_version": 1,
            "records": [
                {
                    "phase_name": "arch_validation",
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

    def test_rejected_only_still_blocks(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from agentic_core.L2_execution.scripts import remediation_dispatcher as _mod

        monkeypatch.setitem(_mod.PHASE_APPROVAL_REQUIRED_OVERRIDES, "arch_validation", True)
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        bundle_data = {
            "contract_version": 1,
            "records": [
                {
                    "phase_name": "arch_validation",
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
        with pytest.raises(ApprovalGatingError, match="arch_validation"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
                approval_bundle_path=bundle_path,
            )

    def test_wrong_phase_approval_does_not_satisfy(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from agentic_core.L2_execution.scripts import remediation_dispatcher as _mod

        monkeypatch.setitem(_mod.PHASE_APPROVAL_REQUIRED_OVERRIDES, "arch_validation", True)
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
        with pytest.raises(ApprovalGatingError, match="arch_validation"):
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
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from agentic_core.L2_execution.scripts import remediation_dispatcher as _mod

        monkeypatch.setitem(_mod.PHASE_APPROVAL_REQUIRED_OVERRIDES, "arch_validation", True)
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="arch_validation"):
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
        bundle = _write_healing_approval(tmp_path / "heal_bundle.json")
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
            approval_bundle_path=bundle,
        )
        assert result is not None

    def test_apply_with_override_succeeds(self, tmp_path: Path) -> None:
        repo = tmp_path / "real_repo"
        repo.mkdir()
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
        )
        bundle = _write_healing_approval(tmp_path / "heal_bundle.json")
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
            allow_repo_mutation=True,
            approval_bundle_path=bundle,
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
        bundle = _write_healing_approval(tmp_path / "heal_bundle.json")
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
            approval_bundle_path=bundle,
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
        bundle = _write_healing_approval(tmp_path / "heal_bundle.json")
        out1 = tmp_path / "out1"
        out1.mkdir()
        r1 = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out1,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
            approval_bundle_path=bundle,
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
            approval_bundle_path=bundle,
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


# ---------------------------------------------------------------------------
# Wave 2.1: Sub-check extraction + worklist unit tests
# ---------------------------------------------------------------------------


class TestExtractHealableItems:
    """Proves extract_healable_items_from_guardian_check handles all evidence shapes."""

    def test_evidence_checks_shape(self) -> None:
        check = {
            "check_id": "guardian_classification_compliance",
            "status": "FAIL",
            "details": "2/2 checks failed",
            "evidence": {
                "guardian_id": "classification_compliance",
                "checks": [
                    {
                        "check_id": "naming_compliance",
                        "status": "FAIL",
                        "details": "3 violations",
                        "evidence": {"violation_count": 3, "violations": ["a", "b", "c"]},
                    },
                    {
                        "check_id": "territory_compliance",
                        "status": "FAIL",
                        "details": "1 violation",
                        "evidence": {"violation_count": 1, "violations": ["d"]},
                    },
                ],
            },
        }
        items = extract_healable_items_from_guardian_check(check)
        ids = [i[0] for i in items]
        assert ids == ["naming_compliance", "territory_compliance"]
        assert items[0][1]["evidence"]["violation_count"] == 3
        assert items[1][1]["evidence"]["violation_count"] == 1

    def test_evidence_violations_shape(self) -> None:
        check = {
            "check_id": "guardian_classification_compliance",
            "status": "FAIL",
            "details": "violations",
            "evidence": {
                "violations": {
                    "naming_compliance": ["file_a.py", "file_b.py"],
                    "territory_compliance": ["file_c.py"],
                },
            },
        }
        items = extract_healable_items_from_guardian_check(check)
        ids = [i[0] for i in items]
        assert ids == ["naming_compliance", "territory_compliance"]
        assert items[0][1]["evidence"]["violations"] == ["file_a.py", "file_b.py"]

    def test_unsupported_evidence_returns_empty(self) -> None:
        check = {
            "check_id": "guardian_foo",
            "status": "FAIL",
            "details": "",
            "evidence": {"guardian_id": "foo", "status": "FAIL"},
        }
        assert extract_healable_items_from_guardian_check(check) == ()

    def test_no_evidence_returns_empty(self) -> None:
        check = {"check_id": "guardian_foo", "status": "FAIL", "details": ""}
        assert extract_healable_items_from_guardian_check(check) == ()

    def test_non_dict_evidence_returns_empty(self) -> None:
        check = {"check_id": "x", "status": "FAIL", "details": "", "evidence": "string"}
        assert extract_healable_items_from_guardian_check(check) == ()

    def test_sorted_output(self) -> None:
        check = {
            "check_id": "g",
            "status": "FAIL",
            "details": "",
            "evidence": {
                "checks": [
                    {"check_id": "z_check", "status": "FAIL", "details": "", "evidence": {}},
                    {"check_id": "a_check", "status": "FAIL", "details": "", "evidence": {}},
                ],
            },
        }
        items = extract_healable_items_from_guardian_check(check)
        assert [i[0] for i in items] == ["a_check", "z_check"]

    def test_missing_sub_evidence_defaults_to_empty_dict(self) -> None:
        check = {
            "check_id": "g",
            "status": "FAIL",
            "details": "",
            "evidence": {
                "checks": [
                    {"check_id": "sub1", "status": "FAIL", "details": "no evidence key"},
                ],
            },
        }
        items = extract_healable_items_from_guardian_check(check)
        assert items[0][1]["evidence"] == {}


class TestBuildHealerWorklist:
    """Proves build_healer_worklist deduplicates, sorts, and filters by registry."""

    def test_sub_checks_included_when_in_registry(self) -> None:
        checks = [
            {
                "check_id": "guardian_classification_compliance",
                "status": "FAIL",
                "details": "",
                "evidence": {
                    "checks": [
                        {"check_id": "naming_compliance", "status": "FAIL", "details": "", "evidence": {}},
                        {"check_id": "territory_compliance", "status": "FAIL", "details": "", "evidence": {}},
                    ],
                },
            },
        ]
        worklist = build_healer_worklist(checks)
        ids = [w[0] for w in worklist]
        assert "naming_compliance" in ids
        assert "territory_compliance" in ids

    def test_rollup_not_in_registry_excluded(self) -> None:
        checks = [
            {
                "check_id": "guardian_classification_compliance",
                "status": "FAIL",
                "details": "",
                "evidence": {
                    "checks": [
                        {"check_id": "naming_compliance", "status": "FAIL", "details": "", "evidence": {}},
                    ],
                },
            },
        ]
        worklist = build_healer_worklist(checks)
        ids = [w[0] for w in worklist]
        assert "guardian_classification_compliance" not in ids

    def test_rollup_in_registry_included(self) -> None:
        checks = [
            {
                "check_id": "guardian_drift_detection",
                "status": "FAIL",
                "details": "",
                "evidence": {},
            },
        ]
        worklist = build_healer_worklist(checks)
        ids = [w[0] for w in worklist]
        assert "guardian_drift_detection" in ids

    def test_sorted_deterministic(self) -> None:
        checks = [
            {
                "check_id": "guardian_hierarchy_compliance",
                "status": "FAIL",
                "details": "",
                "evidence": {
                    "checks": [
                        {"check_id": "subfolder_compliance", "status": "FAIL", "details": "", "evidence": {}},
                        {"check_id": "missing_structure", "status": "FAIL", "details": "", "evidence": {}},
                    ],
                },
            },
        ]
        worklist = build_healer_worklist(checks)
        ids = [w[0] for w in worklist]
        assert ids == sorted(ids)

    def test_empty_aggregate_returns_empty(self) -> None:
        assert build_healer_worklist([]) == ()

    def test_unknown_sub_check_not_in_registry_excluded(self) -> None:
        checks = [
            {
                "check_id": "guardian_classification_compliance",
                "status": "FAIL",
                "details": "",
                "evidence": {
                    "checks": [
                        {"check_id": "naming_compliance", "status": "FAIL", "details": "", "evidence": {}},
                        {"check_id": "unknown_check_xyz", "status": "FAIL", "details": "", "evidence": {}},
                    ],
                },
            },
        ]
        worklist = build_healer_worklist(checks)
        ids = [w[0] for w in worklist]
        assert "naming_compliance" in ids
        assert "unknown_check_xyz" not in ids


# ---------------------------------------------------------------------------
# Wave 2.2: Dispatcher integration — healer reachability via sub-check expansion
# ---------------------------------------------------------------------------


class TestSubCheckHealerReachability:
    """Proves sub-check healers are invoked when aggregate evidence contains sub-checks."""

    def test_naming_compliance_healer_reached(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_classification_compliance"],
            evidence_overrides={
                "guardian_classification_compliance": {
                    "guardian_id": "classification_compliance",
                    "checks": [
                        {
                            "check_id": "naming_compliance",
                            "status": "FAIL",
                            "details": "2 compound suffix conflicts",
                            "evidence": {
                                "violation_count": 2,
                                "violations": [
                                    {"file": "bad_agent_types.py", "suffixes": ["agent", "types"]},
                                ],
                            },
                        },
                        {
                            "check_id": "territory_compliance",
                            "status": "PASS",
                            "details": "All files correct",
                            "evidence": {"violation_count": 0, "violations": []},
                        },
                    ],
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
        ids_and_notes = {c.check_id: c.notes for c in result.results}
        assert "naming_compliance" in ids_and_notes
        assert ids_and_notes["naming_compliance"] != NOTE_MAPPED
        assert ids_and_notes["naming_compliance"] != NOTE_UNMAPPED

    def test_territory_compliance_healer_reached(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_classification_compliance"],
            evidence_overrides={
                "guardian_classification_compliance": {
                    "guardian_id": "classification_compliance",
                    "checks": [
                        {
                            "check_id": "territory_compliance",
                            "status": "FAIL",
                            "details": "1 violation",
                            "evidence": {
                                "violation_count": 1,
                                "violations": [{"file": "misplaced.py", "expected": "config/"}],
                            },
                        },
                    ],
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
        ids_and_notes = {c.check_id: c.notes for c in result.results}
        assert "territory_compliance" in ids_and_notes
        assert ids_and_notes["territory_compliance"] != NOTE_MAPPED

    def test_hierarchy_sub_checks_reached(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_hierarchy_compliance"],
            evidence_overrides={
                "guardian_hierarchy_compliance": {
                    "guardian_id": "hierarchy_compliance",
                    "checks": [
                        {
                            "check_id": "missing_structure",
                            "status": "FAIL",
                            "details": "2 missing dirs",
                            "evidence": {"violation_count": 2, "violations": ["a/b", "c/d"]},
                        },
                        {
                            "check_id": "subfolder_compliance",
                            "status": "PASS",
                            "details": "ok",
                            "evidence": {"violation_count": 0, "violations": []},
                        },
                    ],
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
        ids = {c.check_id for c in result.results}
        assert "missing_structure" in ids
        assert "subfolder_compliance" in ids

    def test_arch_sub_checks_reached(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_architecture_governance"],
            evidence_overrides={
                "guardian_architecture_governance": {
                    "guardian_id": "architecture_governance",
                    "checks": [
                        {
                            "check_id": "import_compliance",
                            "status": "FAIL",
                            "details": "1 violation",
                            "evidence": {"violation_count": 1, "violations": ["x"]},
                        },
                        {
                            "check_id": "layer_gravity",
                            "status": "PASS",
                            "details": "ok",
                            "evidence": {"violation_count": 0, "violations": []},
                        },
                    ],
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
        ids_and_notes = {c.check_id: c.notes for c in result.results}
        assert "import_compliance" in ids_and_notes
        assert "layer_gravity" in ids_and_notes
        assert ids_and_notes["import_compliance"] != NOTE_MAPPED

    def test_rollup_without_sub_checks_still_skipped(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_classification_compliance"],
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        rollup = next(
            (c for c in result.results if c.check_id == "guardian_classification_compliance"),
            None,
        )
        assert rollup is not None
        assert rollup.status == HealStatus.SKIPPED
        assert rollup.notes == NOTE_MAPPED

    def test_unmapped_rollup_remains_unmapped(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_hygiene", "guardian_classification_compliance"],
            evidence_overrides={
                "guardian_classification_compliance": {
                    "checks": [
                        {"check_id": "naming_compliance", "status": "FAIL", "details": "", "evidence": {}},
                    ],
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
        hygiene = next(c for c in result.results if c.check_id == "guardian_hygiene")
        assert hygiene.notes == NOTE_UNMAPPED

    def test_output_validates_with_sub_checks(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_classification_compliance", "guardian_hierarchy_compliance"],
            evidence_overrides={
                "guardian_classification_compliance": {
                    "checks": [
                        {"check_id": "naming_compliance", "status": "FAIL", "details": "", "evidence": {}},
                        {"check_id": "territory_compliance", "status": "FAIL", "details": "", "evidence": {}},
                    ],
                },
                "guardian_hierarchy_compliance": {
                    "checks": [
                        {"check_id": "missing_structure", "status": "FAIL", "details": "", "evidence": {}},
                    ],
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
        assert result.validate() == []

    def test_sub_check_ids_sorted_in_output(self, tmp_path: Path) -> None:
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_classification_compliance"],
            evidence_overrides={
                "guardian_classification_compliance": {
                    "checks": [
                        {"check_id": "territory_compliance", "status": "FAIL", "details": "", "evidence": {}},
                        {"check_id": "naming_compliance", "status": "FAIL", "details": "", "evidence": {}},
                    ],
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
        ids = [c.check_id for c in result.results]
        assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Mutation-dependent approval gating (APPROVAL_REQUIRED_FOR_APPLY)
# ---------------------------------------------------------------------------


class TestMutationDependentApproval:
    """Proves approval is required only when apply=True AND healers are reachable."""

    def test_apply_healer_reachable_no_approval_raises(self, tmp_path: Path) -> None:
        """apply + healer reachable + no approval => ApprovalGatingError."""
        repo = tmp_path / "sandbox"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {"forbidden_folders": ["bad"]},
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        with pytest.raises(ApprovalGatingError, match="Apply mode with planned healer"):
            run_dispatcher(
                guardian_result_path=agg,
                write_artifacts_dir=out,
                created_utc=TIMESTAMP,
                apply=True,
                repo_root=repo,
            )

    def test_apply_healer_reachable_approved_succeeds(self, tmp_path: Path) -> None:
        """apply + healer reachable + APPROVED => rc=0."""
        repo = tmp_path / "sandbox"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {"forbidden_folders": ["bad"]},
            },
        )
        bundle = _write_healing_approval(tmp_path / "heal_bundle.json")
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
            apply=True,
            repo_root=repo,
            approval_bundle_path=bundle,
        )
        assert result.validate() == []

    def test_apply_no_healers_no_approval_succeeds(self, tmp_path: Path) -> None:
        """apply + no healers => rc=0 without approval."""
        repo = tmp_path / "sandbox"
        repo.mkdir()
        (repo / SANDBOX_SENTINEL).write_text("", encoding="utf-8")
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_hygiene"],
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
        assert result.validate() == []

    def test_dry_run_healer_reachable_no_approval_succeeds(self, tmp_path: Path) -> None:
        """dry-run + healer reachable => rc=0 without approval."""
        agg = _write_guardian_aggregate(
            tmp_path / "agg.json",
            ["guardian_drift_detection"],
            evidence_overrides={
                "guardian_drift_detection": {"forbidden_folders": ["bad"]},
            },
        )
        out = tmp_path / "out"
        out.mkdir()
        result = run_dispatcher(
            guardian_result_path=agg,
            write_artifacts_dir=out,
            created_utc=TIMESTAMP,
        )
        assert result.validate() == []


# ---------------------------------------------------------------------------
# Phase B: Integration test — production entrypoint -> tier -> invocation
# ---------------------------------------------------------------------------


class _FakeInvokerForIntegration:
    """Minimal FakeInvoker for integration test (no network)."""

    def __init__(self) -> None:
        self.calls: list[InvocationRecord] = []

    def invoke_local(
        self, inp: HealingInput, dec: HealingDecision, cfg: HealingTierConfig, *, agent_name: str = ""
    ) -> InvocationRecord:
        rec = InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=inp.trace_id,
            heal_confidence=dec.heal_confidence,
            method_called="invoke_local",
        )
        self.calls.append(rec)
        return rec

    def invoke_qwen_vllm(
        self, inp: HealingInput, dec: HealingDecision, cfg: HealingTierConfig, *, agent_name: str = ""
    ) -> InvocationRecord:
        rec = InvocationRecord(
            tier=HealingTier.QWEN_VLLM,
            model_id=cfg.model_qwen_vllm_id,
            agent_name=agent_name,
            trace_id=inp.trace_id,
            heal_confidence=dec.heal_confidence,
            method_called="invoke_qwen_vllm",
        )
        self.calls.append(rec)
        return rec

    def invoke_gemini(
        self, inp: HealingInput, dec: HealingDecision, cfg: HealingTierConfig, *, agent_name: str = ""
    ) -> InvocationRecord:
        rec = InvocationRecord(
            tier=HealingTier.GEMINI_2_5_PRO,
            model_id=cfg.model_gemini_2_5_pro_id,
            agent_name=agent_name,
            trace_id=inp.trace_id,
            heal_confidence=dec.heal_confidence,
            method_called="invoke_gemini",
        )
        self.calls.append(rec)
        return rec


class TestProductionEntrypointTierIntegration:
    """Phase B: prove _invoke_healer -> tier -> invocation with all four guards.

    Refinements tested:
      1. needs_llm_escalation=True required for escalation (over-escalation guard)
      2. check_id must be in HEALER_ESCALATION_ALLOWLIST (allowlist bypass guard)
      3. EscalationContext builds FailureSignal deterministically (not from raw notes)
      4. retry_count drives tier selection (re-entrancy safety)
    """

    pytestmark = pytest.mark.unit_min_deps

    # ------------------------------------------------------------------
    # Refinement 1 + 2: allowlisted healer with needs_llm_escalation=True
    # triggers real escalation
    # ------------------------------------------------------------------

    def test_allowlisted_healer_with_flag_triggers_escalation(self) -> None:
        """Full E2E: allowlisted check_id + needs_llm_escalation=True -> FakeInvoker called."""
        from unittest.mock import patch

        fake = _FakeInvokerForIntegration()

        def _failing_healer(check_dict, *, repo_root=None, apply=False):
            return HealCheckResult(
                check_id="guardian_drift_detection",
                status=HealStatus.FAILED,
                notes="complex rewrite needed",
                needs_llm_escalation=True,
                escalation_hint="failure_type=code_edit_required blast_radius=0.7",
            )

        from agentic_core.L2_execution.scripts import remediation_dispatcher as _rd

        with patch.dict(_rd.HEALER_REGISTRY, {"guardian_drift_detection": _failing_healer}):
            result = _invoke_healer(
                "guardian_drift_detection",
                {},
                tier_invoker=fake,
                retry_count=0,
            )

        assert result.status == HealStatus.FAILED
        assert result.notes is not None
        assert "tier_escalation:" in result.notes
        assert "check_id=guardian_drift_detection" in result.notes
        assert "trace_id=" in result.notes
        assert len(fake.calls) == 1
        record = fake.calls[0]
        assert record.method_called in {"invoke_local", "invoke_qwen_vllm", "invoke_gemini"}
        assert record.agent_name == "remediation_dispatcher"

    # ------------------------------------------------------------------
    # Refinement 1: needs_llm_escalation=False blocks escalation
    # ------------------------------------------------------------------

    def test_failed_without_flag_does_not_escalate(self) -> None:
        """FAILED + needs_llm_escalation=False -> tier system NOT invoked (over-escalation guard)."""
        from unittest.mock import patch

        fake = _FakeInvokerForIntegration()

        def _policy_blocked_healer(check_dict, *, repo_root=None, apply=False):
            return HealCheckResult(
                check_id="guardian_drift_detection",
                status=HealStatus.FAILED,
                notes="policy blocked: missing permissions",
                needs_llm_escalation=False,
            )

        from agentic_core.L2_execution.scripts import remediation_dispatcher as _rd

        with patch.dict(_rd.HEALER_REGISTRY, {"guardian_drift_detection": _policy_blocked_healer}):
            result = _invoke_healer(
                "guardian_drift_detection",
                {},
                tier_invoker=fake,
            )

        assert result.status == HealStatus.FAILED
        assert len(fake.calls) == 0, "Policy-blocked failure must NOT escalate"
        assert "tier_escalation_skipped" in (result.notes or "")
        assert "needs_llm_escalation_false" in (result.notes or "")

    # ------------------------------------------------------------------
    # Refinement 2: non-allowlisted check_id blocks escalation
    # ------------------------------------------------------------------

    def test_non_allowlisted_check_id_does_not_escalate(self) -> None:
        """check_id not in HEALER_ESCALATION_ALLOWLIST -> tier system NOT invoked (allowlist guard)."""
        from unittest.mock import patch

        fake = _FakeInvokerForIntegration()
        non_allowlisted = "guardian_some_unrelated_check"
        assert non_allowlisted not in HEALER_ESCALATION_ALLOWLIST

        def _failing_healer(check_dict, *, repo_root=None, apply=False):
            return HealCheckResult(
                check_id=non_allowlisted,
                status=HealStatus.FAILED,
                notes="failed",
                needs_llm_escalation=True,
            )

        from agentic_core.L2_execution.scripts import remediation_dispatcher as _rd

        with patch.dict(_rd.HEALER_REGISTRY, {non_allowlisted: _failing_healer}):
            result = _invoke_healer(non_allowlisted, {}, tier_invoker=fake)

        assert result.status == HealStatus.FAILED
        assert len(fake.calls) == 0, "Non-allowlisted healer must NOT escalate"
        assert "tier_escalation_skipped" in (result.notes or "")
        assert "not_in_allowlist" in (result.notes or "")

    # ------------------------------------------------------------------
    # Refinement 3: EscalationContext builds FailureSignal deterministically
    # ------------------------------------------------------------------

    def test_escalation_context_is_deterministic(self) -> None:
        """EscalationContext.from_result produces identical output for identical input."""
        result = HealCheckResult(
            check_id="guardian_drift_detection",
            status=HealStatus.FAILED,
            notes="some failure",
            needs_llm_escalation=True,
            escalation_hint="failure_type=code_edit_required blast_radius=0.8",
        )
        ctx1 = EscalationContext.from_result("guardian_drift_detection", result, retry_count=1)
        ctx2 = EscalationContext.from_result("guardian_drift_detection", result, retry_count=1)

        assert ctx1 == ctx2
        assert ctx1.failure_type == "code_edit_required"
        assert ctx1.blast_radius_estimate == 0.8
        assert ctx1.trace_id.startswith("disp-")
        assert ctx1.retry_count == 1

    def test_escalation_context_hint_parsing(self) -> None:
        """EscalationContext parses escalation_hint key=value pairs correctly."""
        result = HealCheckResult(
            check_id="guardian_drift_detection",
            status=HealStatus.FAILED,
            escalation_hint="failure_type=complex_rewrite blast_radius=0.9",
        )
        ctx = EscalationContext.from_result("guardian_drift_detection", result, retry_count=0)
        assert ctx.failure_type == "complex_rewrite"
        assert ctx.blast_radius_estimate == 0.9

    def test_escalation_context_defaults_on_missing_hint(self) -> None:
        """EscalationContext uses safe defaults when escalation_hint is None."""
        result = HealCheckResult(
            check_id="guardian_drift_detection",
            status=HealStatus.FAILED,
            notes="raw error",
        )
        ctx = EscalationContext.from_result("guardian_drift_detection", result, retry_count=0)
        assert ctx.failure_type == "healer_failure"
        assert ctx.blast_radius_estimate == 0.5

    def test_escalation_note_contains_trace_id(self) -> None:
        """Escalation audit note includes deterministic trace_id from EscalationContext."""
        fake = _FakeInvokerForIntegration()
        failed_result = HealCheckResult(
            check_id="guardian_drift_detection",
            status=HealStatus.FAILED,
            notes="needs rewrite",
            needs_llm_escalation=True,
        )
        note = _tier_escalate("guardian_drift_detection", failed_result, retry_count=0, invoker=fake)

        assert "tier_escalation:" in note
        assert "trace_id=disp-" in note
        assert "tier=" in note
        assert "model=" in note
        assert "confidence=" in note
        assert len(fake.calls) == 1

    # ------------------------------------------------------------------
    # Refinement 4: retry_count drives tier selection (re-entrancy safety)
    # ------------------------------------------------------------------

    def test_retry_count_forces_gemini_tier(self) -> None:
        """retry_count >= max_heal_retries forces GEMINI_2_5_PRO (re-entrancy guard)."""
        fake = _FakeInvokerForIntegration()
        failed_result = HealCheckResult(
            check_id="guardian_drift_detection",
            status=HealStatus.FAILED,
            notes="failed",
            needs_llm_escalation=True,
        )
        # max_heal_retries=3; retry_count=3 forces GEMINI
        _tier_escalate("guardian_drift_detection", failed_result, retry_count=3, invoker=fake)

        assert len(fake.calls) == 1
        assert fake.calls[0].method_called == "invoke_gemini"
        assert fake.calls[0].tier == HealingTier.GEMINI_2_5_PRO

    # ------------------------------------------------------------------
    # Existing guards: success and exception paths
    # ------------------------------------------------------------------

    def test_successful_healer_does_not_trigger_escalation(self) -> None:
        """A healer that succeeds must NOT invoke the tier system."""
        from unittest.mock import patch

        fake = _FakeInvokerForIntegration()

        def _fake_healer(check_dict, *, repo_root=None, apply=False):
            return HealCheckResult(
                check_id="guardian_drift_detection",
                status=HealStatus.HEALED,
                changes_made=(),
            )

        from agentic_core.L2_execution.scripts import remediation_dispatcher as _rd

        with patch.dict(_rd.HEALER_REGISTRY, {"guardian_drift_detection": _fake_healer}):
            result = _invoke_healer(
                "guardian_drift_detection",
                {},
                tier_invoker=fake,
            )

        assert result.status == HealStatus.HEALED
        assert len(fake.calls) == 0, "Tier system must NOT be invoked on success"

    def test_exception_in_allowlisted_healer_auto_sets_flag(self) -> None:
        """When a registered healer raises, _invoke_healer auto-sets needs_llm_escalation=True
        for allowlisted check_ids, so the exception path escalates correctly."""
        fake = _FakeInvokerForIntegration()

        # guardian_drift_detection is allowlisted; empty check_dict causes exception
        result = _invoke_healer(
            "guardian_drift_detection",
            {},
            tier_invoker=fake,
            retry_count=0,
        )

        assert result.status == HealStatus.FAILED
        assert result.needs_llm_escalation is True
        assert len(fake.calls) == 1, "Exception in allowlisted healer must trigger escalation"
