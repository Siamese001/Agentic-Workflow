"""W1 phase 4 — certification_scope field on semantic_cache_model_proof."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

MODEL_PROOF = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_model_proof.json"

from tools.certification.evidence.probe_semantic_cache_model import (  # noqa: E402
    _compute_certification_scope,
)


class TestScopeUnit:
    """Unit tests for _compute_certification_scope."""

    def test_local_false_regardless_gives_insufficient(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        scope = _compute_certification_scope(
            live_verified=False, embedding_enabled=True, op={}
        )
        assert scope["final_model_certification_scope"] == "INSUFFICIENT"
        assert scope["local_model_operational"] is False

    def test_local_true_no_ci_gives_local_only(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        scope = _compute_certification_scope(
            live_verified=True, embedding_enabled=True, op={"present": True, "status": "OPERATIONAL", "fallback_used": False}
        )
        assert scope["final_model_certification_scope"] == "LOCAL_ONLY"
        assert scope["ci_model_operational"] == "UNKNOWN"
        assert scope["local_model_operational"] is True

    def test_local_true_ci_true_gives_production_ready(self, monkeypatch):
        monkeypatch.setenv("CI", "true")
        scope = _compute_certification_scope(
            live_verified=True, embedding_enabled=True, op={"present": True, "status": "OPERATIONAL", "fallback_used": False}
        )
        assert scope["final_model_certification_scope"] == "PRODUCTION_READY"
        assert scope["ci_model_operational"] is True

    def test_local_true_ci_failed_gives_local_only(self, monkeypatch):
        monkeypatch.setenv("CI", "true")
        scope = _compute_certification_scope(
            live_verified=True, embedding_enabled=True,
            op={"present": True, "status": "LOAD_ERROR", "fallback_used": False},
        )
        assert scope["final_model_certification_scope"] == "LOCAL_ONLY"
        assert scope["ci_model_operational"] is False

    def test_github_actions_env_detected_as_ci(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        scope = _compute_certification_scope(
            live_verified=True, embedding_enabled=True, op={"present": True, "status": "OPERATIONAL", "fallback_used": False}
        )
        assert scope["ci_signal_detected"] is True
        assert scope["ci_model_operational"] is True
        assert scope["final_model_certification_scope"] == "PRODUCTION_READY"

    def test_note_documents_invariant(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        scope = _compute_certification_scope(
            live_verified=True, embedding_enabled=True, op={}
        )
        assert "LOCAL_ONLY" in scope["note"]
        assert "ACCEPTED" in scope["note"]


@pytest.mark.skipif(not MODEL_PROOF.exists(), reason="model proof artifact absent")
class TestScopeInArtifact:
    @pytest.fixture(scope="class")
    def payload(self) -> dict:
        return json.loads(MODEL_PROOF.read_text(encoding="utf-8"))

    def test_certification_scope_present(self, payload):
        assert "certification_scope" in payload

    def test_scope_has_all_three_fields(self, payload):
        scope = payload["certification_scope"]
        assert "local_model_operational" in scope
        assert "ci_model_operational" in scope
        assert "final_model_certification_scope" in scope

    def test_scope_value_is_valid_enum(self, payload):
        valid = {"LOCAL_ONLY", "CI_READY", "PRODUCTION_READY", "INSUFFICIENT"}
        assert payload["certification_scope"]["final_model_certification_scope"] in valid

    def test_scope_note_present(self, payload):
        assert "note" in payload["certification_scope"]


class TestComposerSurfacesScope:
    """Composer must write scope info into subclaim notes for verifier caveat."""

    def test_composer_output_mentions_certification_scope(self):
        sidecar_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_subclaims.json"
        if not sidecar_path.exists():
            pytest.skip("sidecar not present")
        sc = json.loads(sidecar_path.read_text(encoding="utf-8"))
        model_subclaim = sc["subclaims"]["R1B_APPROVED_MODEL_PROOF"]
        notes = model_subclaim.get("notes", "")
        # Notes should mention scope OR the model evidence didn't include scope yet
        if not notes:
            pytest.skip("subclaim has empty notes")
        # We only assert scope IS mentioned when the model evidence carried it
        model_proof = json.loads(MODEL_PROOF.read_text(encoding="utf-8")) if MODEL_PROOF.exists() else {}
        if "certification_scope" in model_proof:
            assert "certification_scope=" in notes
