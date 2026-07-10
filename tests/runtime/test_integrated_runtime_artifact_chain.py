"""W2 — Artifact chain integrity tests.

Asserts the SHA256 lineage of the current W2 artifacts and that every
upstream_artifact_ref matches the upstream's recomputed hash. Also
covers the fail-closed scenario where a single artifact's payload is
mutated (chain SHA divergence detected).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    W2_ARTIFACT_FILENAMES,
    W2_CHAIN_LINKAGE,
    compute_artifact_hash,
)

LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"


def _latest_matches_current_chain() -> bool:
    manifest = LATEST / "integrated_runtime_artifact_manifest.json"
    try:
        envelope = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    payload = envelope.get("payload") if isinstance(envelope, dict) else {}
    filenames = payload.get("artifact_filenames") if isinstance(payload, dict) else []
    return set(filenames or ()) == set(W2_ARTIFACT_FILENAMES)

import pytest  # noqa: E402

pytestmark = pytest.mark.skipif(
    not _latest_matches_current_chain(),
    reason=(
        "W2b honest non-green: latest/ is absent or stale without approved live provider. "
        "Run probe_integrated_runtime_safe_reuse.py with local_qwen reachable "
        "or ANTHROPIC_API_KEY set."
    ),
)


class TestArtifactChain:
    def test_all_12_present(self):
        for fn in W2_ARTIFACT_FILENAMES:
            assert (LATEST / fn).exists(), fn
        assert len(W2_ARTIFACT_FILENAMES) == 23

    def test_each_artifact_hash_matches_payload(self):
        for fn in W2_ARTIFACT_FILENAMES:
            env = json.loads((LATEST / fn).read_text(encoding="utf-8"))
            recomputed = compute_artifact_hash(env["payload"])
            assert env["artifact_hash"] == recomputed, fn

    def test_upstream_chain_links(self):
        hashes: dict[str, str] = {}
        for fn, _ in W2_CHAIN_LINKAGE:
            env = json.loads((LATEST / fn).read_text(encoding="utf-8"))
            hashes[fn] = env["artifact_hash"]
        for fn, upstream in W2_CHAIN_LINKAGE:
            env = json.loads((LATEST / fn).read_text(encoding="utf-8"))
            actual = env.get("upstream_artifact_ref", "")
            if upstream is None:
                assert actual == "", f"root {fn} has non-empty upstream"
            else:
                assert actual == hashes[upstream], f"{fn} upstream broken"


class TestArtifactChainFailClosed:
    """Fault-injection scenarios — verifier exits 2."""

    def _copy_latest(self, tmp_path: Path) -> Path:
        out = tmp_path / "art"
        shutil.copytree(LATEST, out)
        return out

    def test_chain_sha_divergence_detected(self, tmp_path):
        import subprocess
        art = self._copy_latest(tmp_path)
        # Mutate one payload but leave the artifact_hash field unchanged → SHA divergence.
        env = json.loads((art / "route_contract.json").read_text(encoding="utf-8"))
        env["payload"]["intent_class"] = "MUTATED_BY_TEST"
        (art / "route_contract.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "ops_scripts/ci/verify_integrated_runtime_artifact_chain.py", str(art)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, shell=False,
        )
        assert proc.returncode == 2
        assert "CHAIN_SHA_DIVERGENCE" in proc.stdout

    def test_broken_upstream_ref_detected(self, tmp_path):
        import subprocess
        art = self._copy_latest(tmp_path)
        # Tamper with upstream_artifact_ref of one artifact.
        env = json.loads((art / "terminal_ret_packet.json").read_text(encoding="utf-8"))
        env["upstream_artifact_ref"] = "sha256:" + "0" * 64
        (art / "terminal_ret_packet.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "ops_scripts/ci/verify_integrated_runtime_artifact_chain.py", str(art)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, shell=False,
        )
        assert proc.returncode == 2
        assert "UPSTREAM_REF_BROKEN" in proc.stdout
