"""Tests — W1 phase 2 R1B approved-model probe."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_semantic_cache_model.py"
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_model_proof.json"


def _run(env_override: dict | None = None) -> int:
    env = dict(os.environ)
    if env_override:
        for k, v in env_override.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    return subprocess.run(
        [sys.executable, str(PROBE)], cwd=str(REPO_ROOT),
        timeout=30, check=False, capture_output=True, env=env,
    ).returncode


def _read_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class TestProbeEmitsValidArtifact:
    def test_probe_exits_zero(self):
        assert _run() == 0

    def test_artifact_file_exists(self):
        _run()
        assert ARTIFACT.exists()

    def test_artifact_schema_fields(self):
        _run()
        a = _read_artifact()
        assert a["probe"] == "semantic_cache_model_proof"
        assert a["blocker"] == "a"
        assert a["subclaim_target"] == "R1B_APPROVED_MODEL_PROOF"
        assert "model_match_status" in a
        assert "expected" in a and "actual" in a
        assert a["expected"]["provider"] == "bge-m3"
        assert a["expected"]["model_id"] == "bge-m3-v1"


class TestAntiCheatRule2NeverSilentPass:
    def test_no_final_acceptance_status_field(self):
        _run()
        a = _read_artifact()
        assert "final_acceptance_status" not in a, (
            "Evidence harness must not emit final_acceptance_status"
        )
        assert "actual_proof_depth" not in a
        assert "acceptance_caveat" not in a
        assert "blocking_gap" not in a

    def test_embedding_disabled_env_blocks_match(self):
        """When EMBEDDING_ENABLED is absent/false, match_status must NOT be MATCH."""
        _run({"EMBEDDING_ENABLED": None})
        a = _read_artifact()
        assert a["model_match_status"] != "MATCH", (
            f"Got {a['model_match_status']}: identifier parity without "
            f"EMBEDDING_ENABLED=true must not be marked MATCH"
        )
        assert a["model_match_status"] in {"MISMATCH_EXPLAINED", "UNRESOLVED",
                                            "INFRASTRUCTURE_GAP", "BLOCKED"}

    def test_minilm_provider_marked_mismatch_explained(self):
        # Simulating a MiniLM fallback by overriding the provider env
        rc = _run({"AGENTIC_EMBEDDING_PROVIDER": "minilm", "EMBEDDING_ENABLED": "true"})
        assert rc == 0
        a = _read_artifact()
        # Identifier doesn't match bge-m3 so it cannot be MATCH
        assert a["model_match_status"] != "MATCH"

    def test_rule_2_flag_recorded(self):
        _run()
        a = _read_artifact()
        assert a["anti_cheat_rules_honored"]["rule_2_no_silent_fallback_pass"] is True
        assert a["anti_cheat_rules_honored"]["probe_did_not_instantiate_live_model"] is True
        assert a["anti_cheat_rules_honored"]["probe_did_not_write_sidecar"] is True


class TestExpectedModelSSOT:
    def test_expected_model_is_bge_m3(self):
        _run()
        a = _read_artifact()
        assert a["expected"]["model_id"] == "bge-m3-v1"
        assert a["expected"]["provider"] == "bge-m3"
        assert a["expected"]["hf_id"] == "BAAI/bge-m3"
        assert a["expected"]["dimension"] == 1024
