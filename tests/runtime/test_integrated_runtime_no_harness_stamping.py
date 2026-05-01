"""W2 — No artifact may be stamped by the harness.

Every artifact under artifacts/certification/integrated_runtime/latest/
must carry a producer_component starting with "agentic_core.". The
verifier matches the harness regex; here we add structural assertions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    W2_ARTIFACT_FILENAMES,
    is_harness_stamp,
)

LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"

import pytest  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (LATEST / "integrated_runtime_artifact_manifest.json").exists(),
    reason=(
        "W2b honest non-green: latest/ empty without approved live provider. "
        "Run probe_integrated_runtime_safe_reuse.py with local_qwen reachable "
        "or ANTHROPIC_API_KEY set."
    ),
)


class TestNoHarnessStamping:
    def test_no_artifact_in_latest_is_harness_stamped(self):
        for fn in W2_ARTIFACT_FILENAMES:
            env = json.loads((LATEST / fn).read_text(encoding="utf-8"))
            producer = env.get("producer_component", "")
            assert not is_harness_stamp(producer), f"{fn}:producer={producer!r}"

    def test_every_artifact_producer_is_agentic_core(self):
        for fn in W2_ARTIFACT_FILENAMES:
            env = json.loads((LATEST / fn).read_text(encoding="utf-8"))
            assert env["producer_component"].startswith("agentic_core."), (
                f"{fn}: producer_component must be production code"
            )

    def test_no_harness_receipt_self_attests_pass(self):
        env = json.loads((LATEST / "no_harness_stamp_receipt.json").read_text(encoding="utf-8"))
        assert env["payload"]["all_artifacts_stamped_by_production"] is True
        assert env["payload"]["harness_check"] == "passed_self_attestation"
