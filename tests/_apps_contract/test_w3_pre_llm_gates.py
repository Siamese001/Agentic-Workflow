"""W3 — PRE-LLM Input/Reply Integrity Gates Tests.

Verifies the W3 input/replay integrity gates:
- Prompt assembly SHA logging for replay verification
- Master resume SHA pinning and concurrent edit detection
- Verification helper for checkpointing

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W3)
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

from apps_rg.integrations.gates.pre_llm_gates import (
    _compute_sha256,
    prompt_assembly_sha_gate,
    master_resume_sha_pinned_gate,
    verify_master_resume_unchanged,
)


class TestComputeSha256:
    """Test SHA256 computation utility."""

    def test_compute_sha256_bytes(self) -> None:
        """SHA256 of bytes returns hex digest."""
        data = b"hello world"
        sha = _compute_sha256(data)
        
        expected = hashlib.sha256(data).hexdigest()
        assert sha == expected
        assert len(sha) == 64  # hex digest length

    def test_compute_sha256_str(self) -> None:
        """SHA256 of string encodes to UTF-8 first."""
        data = "hello world"
        sha = _compute_sha256(data)
        
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert sha == expected

    def test_sha256_deterministic(self) -> None:
        """Same input produces same SHA."""
        data = "test data"
        sha1 = _compute_sha256(data)
        sha2 = _compute_sha256(data)
        assert sha1 == sha2

    def test_sha256_changes_with_input(self) -> None:
        """Different inputs produce different SHA."""
        sha1 = _compute_sha256("data1")
        sha2 = _compute_sha256("data2")
        assert sha1 != sha2


class TestPromptAssemblyShaGate:
    """Test prompt assembly SHA logging gate."""

    def test_prompt_sha_computed_from_dict_artifact(self) -> None:
        """Gate computes SHA when artifact is dict with prompt key."""
        context: dict = {}
        artifact = {"prompt": "This is a test prompt for generation"}
        
        verdict = prompt_assembly_sha_gate(artifact, context)
        
        assert verdict.gate_id == "prompt_assembly_sha"
        assert verdict.result == Result.PASS
        assert "sha256_computed" in verdict.reason_codes
        assert "prompt_assembly_sha" in context
        assert len(context["prompt_assembly_sha"]) == 64

    def test_prompt_sha_computed_from_object_artifact(self) -> None:
        """Gate computes SHA when artifact has prompt attribute."""
        context: dict = {}
        
        class Artifact:
            prompt = "Object prompt text"
        
        verdict = prompt_assembly_sha_gate(Artifact(), context)
        
        assert verdict.result == Result.PASS
        assert "sha256_computed" in verdict.reason_codes

    def test_prompt_sha_falls_back_to_context(self) -> None:
        """Gate falls back to context["prompt"] if artifact has no prompt."""
        context = {"prompt": "Context prompt text"}
        artifact = {}
        
        verdict = prompt_assembly_sha_gate(artifact, context)
        
        assert verdict.result == Result.PASS
        assert "sha256_computed" in verdict.reason_codes

    def test_missing_prompt_returns_unknown(self) -> None:
        """No prompt available returns UNKNOWN verdict."""
        context: dict = {}
        artifact = {}
        
        verdict = prompt_assembly_sha_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_prompt" in verdict.reason_codes
        assert "replay_impossible" in verdict.reason_codes

    def test_sha_logged_in_evidence_refs(self) -> None:
        """Full SHA and length logged in evidence refs."""
        context: dict = {}
        prompt = "Test prompt content"
        
        verdict = prompt_assembly_sha_gate({"prompt": prompt}, context)
        
        expected_sha = _compute_sha256(prompt)
        assert f"sha256:{expected_sha}" in verdict.evidence_refs
        assert f"len:{len(prompt)}" in verdict.evidence_refs


class TestMasterResumeShaPinnedGate:
    """Test master resume SHA pinning gate."""

    def test_sha_pinned_when_file_exists(self, tmp_path: Path) -> None:
        """Gate pins SHA when master_resume.json exists."""
        resume_file = tmp_path / "master_resume.json"
        content = b'{"name": "Test Candidate", "experience": []}'
        resume_file.write_bytes(content)
        
        context = {"master_resume_path": str(resume_file)}
        
        verdict = master_resume_sha_pinned_gate({}, context)
        
        assert verdict.gate_id == "master_resume_sha_pinned"
        assert verdict.result == Result.PASS
        assert "sha256_pinned" in verdict.reason_codes
        assert "master_resume_sha" in context
        assert len(context["master_resume_sha"]) == 64

    def test_missing_file_returns_fail(self, tmp_path: Path) -> None:
        """Missing master_resume.json returns FAIL."""
        nonexistent = tmp_path / "does_not_exist.json"
        context = {"master_resume_path": str(nonexistent)}
        
        verdict = master_resume_sha_pinned_gate({}, context)
        
        assert verdict.result == Result.FAIL
        assert "master_resume_missing" in verdict.reason_codes

    def test_missing_path_returns_unknown(self) -> None:
        """No master_resume_path in context returns UNKNOWN."""
        context: dict = {}
        
        verdict = master_resume_sha_pinned_gate({}, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_master_resume_path" in verdict.reason_codes

    def test_concurrent_modification_detected(self, tmp_path: Path) -> None:
        """SHA mismatch when file modified during pipeline."""
        resume_file = tmp_path / "master_resume.json"
        original_content = b'{"name": "Original"}'
        resume_file.write_bytes(original_content)
        
        original_sha = _compute_sha256(original_content)
        modified_sha = "a" * 64  # Different SHA
        
        context = {
            "master_resume_path": str(resume_file),
            "master_resume_expected_sha": modified_sha,  # Wrong SHA
        }
        
        verdict = master_resume_sha_pinned_gate({}, context)
        
        assert verdict.result == Result.FAIL
        assert "concurrent_modification_detected" in verdict.reason_codes
        assert f"expected:{modified_sha[:16]}" in verdict.reason_codes
        assert f"actual:{original_sha[:16]}" in verdict.reason_codes

    def test_no_expected_sha_allows_any(self, tmp_path: Path) -> None:
        """No expected_sha means any current SHA is accepted (first pin)."""
        resume_file = tmp_path / "master_resume.json"
        resume_file.write_bytes(b'{"data": "test"}')
        
        context = {"master_resume_path": str(resume_file)}
        # No master_resume_expected_sha set
        
        verdict = master_resume_sha_pinned_gate({}, context)
        
        assert verdict.result == Result.PASS
        assert "sha256_pinned" in verdict.reason_codes

    def test_file_size_in_evidence_refs(self, tmp_path: Path) -> None:
        """File size logged in evidence refs."""
        resume_file = tmp_path / "master_resume.json"
        content = b'{"large": "content here"}'
        resume_file.write_bytes(content)
        
        context = {"master_resume_path": str(resume_file)}
        
        verdict = master_resume_sha_pinned_gate({}, context)
        
        assert f"size:{len(content)}" in verdict.evidence_refs
        assert f"path:{resume_file}" in verdict.evidence_refs


class TestVerifyMasterResumeUnchanged:
    """Test verification helper for checkpointing."""

    def test_verification_passes_when_sha_matches(self, tmp_path: Path) -> None:
        """Verification passes when SHA matches expected."""
        resume_file = tmp_path / "master_resume.json"
        content = b'{"stable": "data"}'
        resume_file.write_bytes(content)
        
        expected_sha = _compute_sha256(content)
        
        verdict = verify_master_resume_unchanged(resume_file, expected_sha)
        
        assert verdict.result == Result.PASS
        assert "sha_verified" in verdict.reason_codes

    def test_verification_fails_when_sha_mismatches(self, tmp_path: Path) -> None:
        """Verification fails when SHA doesn't match."""
        resume_file = tmp_path / "master_resume.json"
        resume_file.write_bytes(b'{"data": "version1"}')
        
        wrong_sha = "b" * 64
        
        verdict = verify_master_resume_unchanged(resume_file, wrong_sha)
        
        assert verdict.result == Result.FAIL
        assert "sha_mismatch" in verdict.reason_codes

    def test_verification_fails_when_file_missing(self, tmp_path: Path) -> None:
        """Verification fails when file not found."""
        nonexistent = tmp_path / "missing.json"
        
        verdict = verify_master_resume_unchanged(nonexistent, "any_sha")
        
        assert verdict.result == Result.FAIL
        assert "file_not_found" in verdict.reason_codes


class TestW3Integration:
    """Integration tests for W3 gates working together."""

    def test_pipeline_checkpoint_pattern(self, tmp_path: Path) -> None:
        """Simulate full pipeline: pin at start, verify at checkpoints."""
        # Create master resume
        resume_file = tmp_path / "master_resume.json"
        content = b'{"name": "Test", "sections": []}'
        resume_file.write_bytes(content)
        
        # Phase 1: Pin SHA at pipeline start
        context = {"master_resume_path": str(resume_file)}
        pin_verdict = master_resume_sha_pinned_gate({}, context)
        assert pin_verdict.result == Result.PASS
        
        pinned_sha = context["master_resume_sha"]
        
        # Phase 2: Verify at checkpoint before LLM call
        check1 = verify_master_resume_unchanged(resume_file, pinned_sha)
        assert check1.result == Result.PASS
        
        # Phase 3: Verify at checkpoint after LLM call
        check2 = verify_master_resume_unchanged(resume_file, pinned_sha)
        assert check2.result == Result.PASS

    def test_detects_concurrent_edit_mid_pipeline(self, tmp_path: Path) -> None:
        """Pipeline detects if file modified between checkpoints."""
        resume_file = tmp_path / "master_resume.json"
        original = b'{"version": 1}'
        resume_file.write_bytes(original)
        
        # Pin at start
        context = {"master_resume_path": str(resume_file)}
        master_resume_sha_pinned_gate({}, context)
        pinned_sha = context["master_resume_sha"]
        
        # Concurrent edit happens
        resume_file.write_bytes(b'{"version": 2}')  # Modified!
        
        # Verification at next checkpoint detects change
        check = verify_master_resume_unchanged(resume_file, pinned_sha)
        assert check.result == Result.FAIL
        assert "sha_mismatch" in check.reason_codes


class TestReplayIntegrity:
    """Test replay verification patterns."""

    def test_prompt_sha_for_replay_verification(self, tmp_path: Path) -> None:
        """Prompt SHA can be logged and later verified during replay."""
        # Original run: log prompt SHA
        prompt = "Generate executive summary for SVP AI Strategy role..."
        context = {}
        artifact = {"prompt": prompt}
        
        verdict = prompt_assembly_sha_gate(artifact, context)
        logged_sha = context["prompt_assembly_sha"]
        
        # Replay: verify same prompt SHA
        replay_context = {}
        replay_artifact = {"prompt": prompt}  # Same prompt
        replay_verdict = prompt_assembly_sha_gate(replay_artifact, replay_context)
        replay_sha = replay_context["prompt_assembly_sha"]
        
        assert logged_sha == replay_sha
        assert verdict.result == Result.PASS
        assert replay_verdict.result == Result.PASS

    def test_different_prompt_different_sha(self) -> None:
        """Different prompts produce different SHAs."""
        context1 = {}
        context2 = {}
        
        prompt_assembly_sha_gate({"prompt": "Prompt A"}, context1)
        prompt_assembly_sha_gate({"prompt": "Prompt B"}, context2)
        
        assert context1["prompt_assembly_sha"] != context2["prompt_assembly_sha"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
