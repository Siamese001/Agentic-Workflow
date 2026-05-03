"""W6 tests: HITL bridge (P6.3) and DOCX re-seal helper (P6.2).

Plan: apps-rg-runtime-cert-hardening-a3f8c2.md
Phases: W6.P2 (reseal_artifact), W6.P3 (HITLApprovalGate bridge)
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestHITLBridge:
    """Test apps_rg HITL bridge to agentic_core L5 HITLApprovalGate."""

    def test_hitl_bridge_importable(self) -> None:
        """hitl_bridge module imports cleanly."""
        from apps_rg.integrations.hitl_bridge import (
            read_run_report,
            build_hitl_context,
            evaluate_hitl,
        )
        assert callable(read_run_report)
        assert callable(build_hitl_context)
        assert callable(evaluate_hitl)

    def test_read_run_report_missing(self, tmp_path: Path) -> None:
        """read_run_report returns None when file missing."""
        from apps_rg.integrations.hitl_bridge import read_run_report
        assert read_run_report(tmp_path) is None

    def test_read_run_report_present(self, tmp_path: Path) -> None:
        """read_run_report returns parsed JSON when file present."""
        from apps_rg.integrations.hitl_bridge import read_run_report
        report = {"status": "OK", "run_id": "test-123"}
        (tmp_path / "run_report.json").write_text(json.dumps(report))
        result = read_run_report(tmp_path)
        assert result == report

    def test_build_hitl_context_human_review(self) -> None:
        """build_hitl_context sets review_requested=True when status=HUMAN_REVIEW."""
        from apps_rg.integrations.hitl_bridge import build_hitl_context
        run_report = {
            "status": "HUMAN_REVIEW",
            "provenance_report": {"valid": False, "reason": "no_master_bullets"},
        }
        ctx = build_hitl_context(run_report, replay_key="test-replay-key")
        assert ctx.hitl["review_requested"] is True
        assert ctx.hitl["verdict"] == "pending"
        assert ctx.hitl["replay_key"] == "test-replay-key"
        assert ctx.hitl["reason"] == "no_master_bullets"

    def test_build_hitl_context_ok_status(self) -> None:
        """build_hitl_context sets review_requested=False when status=OK."""
        from apps_rg.integrations.hitl_bridge import build_hitl_context
        ctx = build_hitl_context({"status": "OK"})
        assert ctx.hitl["review_requested"] is False

    def test_evaluate_hitl_human_review_pending(self, tmp_path: Path) -> None:
        """evaluate_hitl returns GateDecision with escalate for pending verdict."""
        from apps_rg.integrations.hitl_bridge import evaluate_hitl
        report = {
            "status": "HUMAN_REVIEW",
            "provenance_report": {"valid": False, "reason": "no_master_bullets"},
        }
        (tmp_path / "run_report.json").write_text(json.dumps(report))

        decision = evaluate_hitl(tmp_path, replay_key="test-key")
        assert decision is not None
        # Pending verdict -> escalate disposition
        assert "pending" in decision.reason_codes or "verdict_pending" in str(decision.reason_codes)

    def test_evaluate_hitl_no_run_report(self, tmp_path: Path) -> None:
        """evaluate_hitl returns None when no run_report.json."""
        from apps_rg.integrations.hitl_bridge import evaluate_hitl
        assert evaluate_hitl(tmp_path) is None


class TestResealHelper:
    """Test DOCX re-seal helper for post-run patches."""

    def test_reseal_module_importable(self) -> None:
        """reseal module imports cleanly."""
        from apps_shared.spine_emission.reseal import (
            compute_sha256,
            read_exhaust_bundle,
            reseal_artifact,
        )
        assert callable(compute_sha256)
        assert callable(read_exhaust_bundle)
        assert callable(reseal_artifact)

    def test_compute_sha256(self, tmp_path: Path) -> None:
        """compute_sha256 returns valid hex digest."""
        from apps_shared.spine_emission.reseal import compute_sha256
        path = tmp_path / "test.txt"
        path.write_bytes(b"hello world")
        sha = compute_sha256(path)
        assert len(sha) == 64  # SHA-256 is 64 hex chars
        assert all(c in "0123456789abcdef" for c in sha)

    def test_reseal_artifact_outside_run_dir_raises(self, tmp_path: Path) -> None:
        """reseal_artifact raises ValueError when artifact outside run_dir."""
        import pytest
        from apps_shared.spine_emission.reseal import reseal_artifact

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        external = other_dir / "external.docx"
        external.write_bytes(b"content")

        with pytest.raises(ValueError, match="not within run_dir"):
            reseal_artifact(run_dir, external)

    def test_reseal_artifact_missing_returns_failure(self, tmp_path: Path) -> None:
        """reseal_artifact returns success=False when artifact missing."""
        from apps_shared.spine_emission.reseal import reseal_artifact

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        missing = run_dir / "missing.docx"

        result = reseal_artifact(run_dir, missing)
        assert result["success"] is False
        assert "artifact_missing" in result["reason_failed"]

    def test_reseal_artifact_updates_bundle(self, tmp_path: Path) -> None:
        """reseal_artifact updates artifact_sha256_map in exhaust bundle."""
        from apps_shared.spine_emission.reseal import reseal_artifact

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        artifact = run_dir / "resume.docx"
        artifact.write_bytes(b"docx-content-v1")

        # Seed bundle with stale sha
        bundle = {
            "artifact_sha256_map": {"resume.docx": "old_sha_placeholder"},
        }
        (run_dir / "runtime_exhaust_bundle.json").write_text(json.dumps(bundle))

        result = reseal_artifact(
            run_dir, artifact,
            reason="manual_edit",
            patcher="test_user",
        )
        assert result["success"] is True
        assert result["old_sha256"] == "old_sha_placeholder"
        assert result["new_sha256"] != "old_sha_placeholder"
        assert len(result["new_sha256"]) == 64
        assert result["bundle_updated"] is True

        # Bundle was rewritten
        updated_bundle = json.loads(
            (run_dir / "runtime_exhaust_bundle.json").read_text()
        )
        assert updated_bundle["artifact_sha256_map"]["resume.docx"] == result["new_sha256"]
        assert len(updated_bundle["reseal_events"]) == 1
        assert updated_bundle["reseal_events"][0]["reason"] == "manual_edit"
        assert updated_bundle["reseal_events"][0]["patcher"] == "test_user"

    def test_reseal_artifact_no_bundle(self, tmp_path: Path) -> None:
        """reseal_artifact works even when no exhaust bundle exists."""
        from apps_shared.spine_emission.reseal import reseal_artifact

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        artifact = run_dir / "resume.docx"
        artifact.write_bytes(b"content")

        result = reseal_artifact(run_dir, artifact)
        assert result["success"] is True
        assert result["bundle_updated"] is False
        assert len(result["new_sha256"]) == 64
