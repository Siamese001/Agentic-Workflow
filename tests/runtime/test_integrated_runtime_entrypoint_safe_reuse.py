"""W2 — Positive entry-point + 4 fail-closed scenarios.

Covers:
  - Production entry point is the only API the test calls.
  - integrated_runtime_entrypoint_used flag is set on the manifest.
  - Fail-closed:
      * harness directly calls layer component → fail
      * missing ValidatedRequest artifact → verifier fail
      * missing integrated_runtime_artifact_manifest → composer NOT_APPLICABLE
      * artifact producer is harness-shaped → emitter raises
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    ProvenanceStamp,
    is_harness_stamp,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    PRODUCER_COMPONENT,
    run_integrated_safe_reuse,
)
from tools.certification.safety.deterministic_proof_stage import DeterministicProofStage
from tools.certification.safety.veto_orchestrator import VetoOrchestrator


LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"


def _drive_allow_path(tmp: Path) -> None:
    """Drive the entry point with a deterministic SAFE veto. Returns artifact_dir."""
    user_q = "What is the capital of France?"
    cached_q = "Tell me the capital of France."
    namespace = "test_w2_allow"
    # Real cache seed (production class).
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )
    cache = SemanticCacheManager.get_instance()
    ctx = json.dumps(
        {"body_text": user_q, "namespace": namespace, "tenant_id": "", "policy_hash": "no-policy"},
        sort_keys=True, separators=(",", ":"),
    )
    cache.learn(ctx, namespace, {"text": "Paris.", "answer": "Paris.",
                                  "cached_query_text": cached_q})
    import os
    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    proof = VetoOrchestrator(stages=[
        DeterministicProofStage(verdicts={(user_q, cached_q): "SAFE"})
    ])
    return run_integrated_safe_reuse(
        {"body_text": user_q, "transport": "api"},
        namespace=namespace, tenant_id="",
        artifact_dir=tmp,
        veto_orchestrator=proof,
    )


# ──────────────────────────────────────────────────────────────────────
# Positive
# ──────────────────────────────────────────────────────────────────────


_LATEST_MANIFEST = LATEST / "integrated_runtime_artifact_manifest.json"


class TestEntryPointPositive:
    @pytest.mark.skipif(
        not _LATEST_MANIFEST.exists(),
        reason=(
            "W2b honest non-green: no approved live provider available → "
            "probe does not populate artifacts/.../latest/. Run the probe "
            "with local_qwen reachable OR ANTHROPIC_API_KEY set to exercise "
            "this assertion end-to-end."
        ),
    )
    def test_entry_point_used_on_real_run(self):
        """The latest artifact dir was produced by the real entry point."""
        manifest = json.loads(_LATEST_MANIFEST.read_text(encoding="utf-8"))
        assert manifest["payload"]["integrated_runtime_entrypoint_used"] is True
        assert manifest["payload"]["entry_point"].endswith("run_integrated_safe_reuse")

    @pytest.mark.skipif(
        not _LATEST_MANIFEST.exists(),
        reason="W2b honest non-green: latest/ empty without approved provider.",
    )
    def test_producer_is_agentic_core(self):
        for fn in (LATEST.glob("*.json")):
            env = json.loads(fn.read_text(encoding="utf-8"))
            assert env["producer_component"].startswith("agentic_core."), f"{fn.name}"

    def test_run_returns_allow_for_seeded_safe_pair(self, tmp_path):
        result = _drive_allow_path(tmp_path)
        assert result.cache_hit is True
        assert result.safe_reuse_decision.allow is True
        assert result.x3_disposition == "X3D"


# ──────────────────────────────────────────────────────────────────────
# Fail-closed
# ──────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_harness_direct_layer_call_is_forbidden_by_pattern(self):
        """The is_harness_stamp regex would catch a harness-stamped artifact.
        The verifier rejects any producer_component matching tests.* / scripts.verify_*.
        """
        assert is_harness_stamp("tests.unit.test_foo")
        assert is_harness_stamp("scripts.verify_integrated_runtime_entrypoint")
        assert is_harness_stamp("ops_scripts.ci.verify_integrated_runtime_entrypoint")
        assert is_harness_stamp("some.module.harness")
        assert not is_harness_stamp(PRODUCER_COMPONENT)

    def test_emitter_raises_on_harness_producer(self):
        # The regex matches the standalone word "harness" — the emitter
        # also rejects any non-agentic_core producer (covered separately).
        with pytest.raises(ValueError, match="harness"):
            ProvenanceStamp(
                producer_component="agentic_core.runtime.test.harness.runner",
                producer_module="runner",
                producer_function_or_class="run",
            )

    def test_emitter_raises_on_non_agentic_core_producer(self):
        with pytest.raises(ValueError, match="agentic_core"):
            ProvenanceStamp(
                producer_component="tools.foo.bar",  # not under agentic_core.*
                producer_module="bar",
                producer_function_or_class="run",
            )

    def test_missing_validated_request_breaks_chain(self, tmp_path):
        result = _drive_allow_path(tmp_path)
        # Remove a chain artifact and re-run the chain verifier.
        (tmp_path / "validated_request.json").unlink()
        proc = subprocess.run(
            [sys.executable, "ops_scripts/ci/verify_integrated_runtime_artifact_chain.py", str(tmp_path)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, shell=False,
        )
        assert proc.returncode == 2, proc.stdout + proc.stderr
        assert "ARTIFACT_MISSING" in proc.stdout

    def test_missing_manifest_keeps_composer_not_applicable(self, tmp_path, monkeypatch):
        """Without the manifest, _map_integrated_runtime_proof refuses PASS.

        We simulate "missing manifest" by pointing at a non-existent
        subdirectory under REPO_ROOT so .relative_to() works in the error
        notes."""
        from scripts import compose_semantic_cache_subclaims as csc
        empty = REPO_ROOT / "artifacts" / "_w2_test_empty_dir_does_not_exist"
        monkeypatch.setattr(csc, "W2_INTEGRATED_LATEST", empty)
        monkeypatch.setattr(csc, "W2_VERIFIER_RESULTS", empty / "verifier_results.json")
        status, notes = csc._map_integrated_runtime_proof()
        assert status == "NOT_APPLICABLE"
        assert "missing" in notes.lower()
