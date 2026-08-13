"""S2R1 atomic Apps Research handoff persistence contracts."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import apps_research.integrations.apps_rg_handoff as handoff
from apps_rg.prerequisites.briefing_validator import validate_apps_research_handoff
from tests.unit.apps_research.test_apps_rg_handoff_canonical_exit import _record

_COMPANY = "Anthropic"
_ROLE = "Manager Applied AI Architecture Partnerships"
_JD = "Lead partner solution architecture for Claude."


def _publish(runs_root: Path, run_id: str):
    return handoff.persist_apps_rg_targeting_brief_artifacts(
        record=_record(run_id),
        target_company=_COMPANY,
        target_role=_ROLE,
        jd_text=_JD,
        runs_root=runs_root,
    )


def test_explicit_writable_artifact_root_succeeds(tmp_path: Path) -> None:
    base = tmp_path / "active_s2"
    padding = max(1, 172 - len(str(base)) - 1)
    runs_root = base / ("r" * padding)
    run_id = "bridge_rg_research_bridge_fcc0977f_cabee413-0d26-4c60-8d3c-50e70c8a15e0"

    bundle = _publish(runs_root, run_id)

    assert bundle.run_dir.parent == runs_root.resolve()
    assert bundle.run_dir.name == handoff._bundle_directory_name(
        root=runs_root.resolve(), run_id=run_id
    )
    assert bundle.briefing_path.is_file()
    assert max(len(str(path)) for path in bundle.run_dir.rglob("*")) < 260
    temporary_ref = Path(bundle.envelope["commit_protocol"]["temporary_bundle_ref"])
    assert len(str(temporary_ref / "apps_research_apps_rg_handoff_v2.json")) < 260
    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=_JD,
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )
    assert validation.valid, validation.reason
    assert (bundle.run_dir / "apps_research_handoff_validation_receipt.json").is_file()


def test_explicit_root_never_uses_repository_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        handoff,
        "_default_apps_research_runs_root",
        lambda: pytest.fail("repository-default root must not be resolved"),
    )

    bundle = _publish(tmp_path / "authorized" / "runs", "no-default")

    assert bundle.run_dir.is_dir()


def test_read_only_root_permission_error_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runs_root = (tmp_path / "read_only" / "runs").resolve()
    runs_root.mkdir(parents=True)
    original_mkdir = Path.mkdir

    def deny_stage_mkdir(self: Path, *args: object, **kwargs: object) -> None:
        if self.parent.resolve() == runs_root:
            raise PermissionError(13, "Permission denied", str(self))
        original_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", deny_stage_mkdir)

    with pytest.raises(PermissionError, match="Permission denied"):
        _publish(runs_root, "read-only-root")

    assert not list(runs_root.iterdir())


def test_existing_committed_run_directory_fails_closed(tmp_path: Path) -> None:
    runs_root = tmp_path / "runs"
    committed = runs_root / handoff._bundle_directory_name(
        root=runs_root.resolve(), run_id="existing-run"
    )
    committed.mkdir(parents=True)
    sentinel = committed / "sentinel.txt"
    sentinel.write_text("immutable\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="committed run directory already exists"):
        _publish(runs_root, "existing-run")

    assert sentinel.read_text(encoding="utf-8") == "immutable\n"


def test_unowned_stale_stage_is_not_deleted(tmp_path: Path) -> None:
    runs_root = tmp_path / "runs"
    stale = runs_root / ".s-abandoned-owner"
    stale.mkdir(parents=True)
    sentinel = stale / "owner.json"
    sentinel.write_text("{}\n", encoding="utf-8")

    bundle = _publish(runs_root, "stale-stage")

    assert bundle.run_dir.is_dir()
    assert stale.is_dir()
    assert sentinel.is_file()


def test_atomic_rename_failure_is_not_bypassed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runs_root = (tmp_path / "runs").resolve()
    original_replace = handoff.os.replace

    def deny_stage_commit(source: os.PathLike[str], target: os.PathLike[str]) -> None:
        source_path = Path(source)
        if source_path.parent.resolve() == runs_root:
            raise PermissionError(13, "atomic rename denied", str(source_path))
        original_replace(source, target)

    monkeypatch.setattr(handoff.os, "replace", deny_stage_commit)

    with pytest.raises(PermissionError, match="atomic rename denied"):
        _publish(runs_root, "rename-required")

    committed = runs_root / handoff._bundle_directory_name(
        root=runs_root.resolve(), run_id="rename-required"
    )
    assert not committed.exists()
    assert not list(runs_root.glob(".s-*"))


def test_commit_marker_is_the_last_staged_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writes: list[str] = []
    original_write = handoff._write_fsync

    def record_write(path: Path, payload: bytes) -> None:
        writes.append(path.name)
        original_write(path, payload)

    monkeypatch.setattr(handoff, "_write_fsync", record_write)

    _publish(tmp_path / "runs", "marker-last")

    assert writes[-1] == "bundle_commit_manifest.json"
    assert writes.count("bundle_commit_manifest.json") == 1


def test_every_staged_file_keeps_file_fsync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    original_fsync = handoff.os.fsync

    def record_fsync(descriptor: int) -> None:
        calls.append(descriptor)
        original_fsync(descriptor)

    monkeypatch.setattr(handoff.os, "fsync", record_fsync)

    _publish(tmp_path / "runs", "file-fsync")

    assert len(calls) >= 13


def test_directory_fsync_platform_status_is_explicit(tmp_path: Path) -> None:
    status = handoff._fsync_directory(tmp_path)

    assert status == ("UNSUPPORTED" if os.name == "nt" else "PASS")
    bundle = _publish(tmp_path / "runs", "fsync-status")
    receipt = bundle.envelope["commit_protocol"]["directory_fsync"]
    assert receipt == {
        "platform": os.name,
        "stage": status,
        "root": status,
    }


def test_permission_error_from_file_creation_is_not_swallowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def deny_write(path: Path, payload: bytes) -> None:
        del payload
        raise PermissionError(13, "file creation denied", str(path))

    monkeypatch.setattr(handoff, "_write_fsync", deny_write)

    with pytest.raises(PermissionError, match="file creation denied"):
        _publish(tmp_path / "runs", "permission-propagates")


def test_receipts_bind_exact_root_and_final_bundle_digest(tmp_path: Path) -> None:
    runs_root = (tmp_path / "active_s2" / "apps_research" / "runs").resolve()
    bundle = _publish(runs_root, "receipt-binding")
    protocol = bundle.envelope["commit_protocol"]
    manifest = bundle.envelope["artifact_manifest"]

    assert protocol["artifact_runs_root"] == str(runs_root)
    assert protocol["final_bundle_digest"] == manifest["manifest_sha256"]

    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=_JD,
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )
    assert validation.valid, validation.reason
    assert validation.receipt is not None
    assert validation.receipt["artifact_runs_root"] == str(runs_root)
    assert validation.receipt["final_bundle_digest"] == manifest["manifest_sha256"]
