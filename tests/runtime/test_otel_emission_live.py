"""Live OTEL emission proof — closes the gap in the 150-requirements baseline.

Source-of-truth: docs/reference/contracts/enforcement/ALL_REQUIREMENTS_ENFORCEMENT_BASELINE.md:181-185
    "Real OTEL emission proof — exporter-in-CI verifying span shapes match
     otel_span_refs declarations."

This test exercises a representative apps_rg run end-to-end with the OTEL
lifecycle bridge installed, then asserts the runtime ADG store actually
received spans. Until this test passes:
  - REQ-L6-OBS-ANTI-BYPASS-001
  - REQ-L6-OUTCOME-TRAJECTORY-001
  - REQ-L6-PROPOSAL-ADMISSION-001
  - REQ-L6-MEMORY-PROMOTION-IFACE-001
  - REQ-L0-ROUTECONTRACT-TELEMETRY-001
  - REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001
remain at STATIC fixture proof, not RUNTIME emission proof.
"""

from __future__ import annotations

import asyncio
import importlib
import logging
import sys
from pathlib import Path

import pytest

# Pre-import the real lifecycle_trace_contract by absolute path so all adg.*
# loggers exist before we attach our handler. We avoid `from agentic_core...`
# because tests/agentic_core/runtime/contracts/__init__.py shadows the real
# package during pytest collection.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_LIFECYCLE_FILE = _REPO_ROOT / "agentic_core" / "runtime" / "contracts" / "lifecycle_trace_contract.py"
_BRIDGE_FILE = _REPO_ROOT / "agentic_core" / "runtime" / "contracts" / "otel_lifecycle_bridge.py"


def _load_by_path(name: str, file_path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot build spec for {name}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_load_by_path("agentic_core.runtime.contracts.lifecycle_trace_contract", _LIFECYCLE_FILE)
_bridge_mod = _load_by_path("agentic_core.runtime.contracts.otel_lifecycle_bridge", _BRIDGE_FILE)
install_bridge = _bridge_mod.install_bridge
uninstall_bridge = _bridge_mod.uninstall_bridge


@pytest.fixture(autouse=True)
def reset_bridge():
    """Ensure each test starts with a fresh bridge."""
    uninstall_bridge()
    yield
    uninstall_bridge()


def test_install_bridge_idempotent():
    """Bridge install is idempotent — second call returns same instance."""
    b1 = install_bridge()
    b2 = install_bridge()
    assert b1 is b2


def test_bridge_captures_adg_emissions_subprocess(tmp_path):
    """Bridge captures adg.* records in a clean subprocess.

    pytest's LogCaptureHandler interferes with logging handler chains in the
    same process. Running in a subprocess gives us a clean logging environment
    that mirrors how apps_rg actually runs.
    """
    import subprocess  # noqa: PLC0415

    out_file = tmp_path / "spans.json"
    # Use normal Python imports inside the subprocess — importlib direct-file
    # loading triggers a circular ImportError because lifecycle_trace_contract
    # imports from agentic_core which re-imports lifecycle_trace_contract.
    # Putting repo root at sys.path[0] lets the standard import system handle
    # the cycle correctly.
    script = f"""
import json, sys, logging
sys.path.insert(0, r"{_REPO_ROOT}")
import agentic_core.runtime.contracts.lifecycle_trace_contract  # noqa
from agentic_core.runtime.contracts.otel_lifecycle_bridge import install_bridge

bridge = install_bridge()
adg = logging.getLogger("adg.test_edge_kind")
adg.debug("test layer=L3_ORCHESTRATION op=test")
adg.debug("test layer=L0_ROUTING op=test2")
logging.getLogger("not_adg").debug("ignored")
spans = bridge.buffered_spans()
with open(r"{out_file}", "w") as f:
    json.dump(spans, f)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, f"subprocess failed: {result.stderr}"
    import json as _json  # noqa: PLC0415

    spans = _json.loads(out_file.read_text())
    assert len(spans) == 2
    assert all(s["name"].startswith("adg.") for s in spans)
    edge_kinds = {s["attributes"]["edge_kind"] for s in spans}
    assert edge_kinds == {"test_edge_kind"}
    layers = {s["attributes"].get("layer") for s in spans}
    assert "L3_ORCHESTRATION" in layers and "L0_ROUTING" in layers


def test_bridge_flush_with_zero_spans_returns_success():
    """Empty buffer flush is a no-op success, never an error."""
    bridge = install_bridge()
    result = bridge.flush_to_runtime_adg(mission="empty_test")
    assert result["success"] is True
    assert result["spans_ingested"] == 0


def test_apps_rg_run_emits_spans_to_runtime_adg():
    """End-to-end: a real apps_rg run persists spans to the runtime ADG store.

    This is the assertion gate that closes ALL_REQUIREMENTS_ENFORCEMENT_BASELINE.md
    §181-185 (Real OTEL emission proof). Run apps_rg in a subprocess for a
    clean logging environment; assert the runtime_adg snapshot dir on disk
    contains fresh, non-trivial snapshot files. The disk artifacts are the
    canonical proof — the otel_mcp server's in-memory counter is irrelevant
    because that's a different process.
    """
    import subprocess  # noqa: PLC0415
    import time as _time  # noqa: PLC0415

    snap_dir = _REPO_ROOT / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
    test_start = _time.time()

    result = subprocess.run(
        [sys.executable, "-m", "apps_rg.scripts.generate_resume"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, (
        f"apps_rg subprocess failed (rc={result.returncode}). stderr tail: {result.stderr[-500:]}"
    )

    # Disk-based persistence proof: the runtime_adg pipeline writes spans into
    # the aggregate index files (_trace_index.json, _index.json) and may also
    # produce per-snapshot JSONs depending on store config. Either fresh
    # snapshot OR fresh index-file mtime is acceptable proof of ingestion.
    # Allow 2-second tolerance for filesystem clock granularity on Windows.
    threshold = test_start - 2.0
    all_json = list(snap_dir.glob("*.json"))
    fresh_files = [p for p in all_json if p.stat().st_mtime >= threshold]
    assert fresh_files, (
        f"No JSON files in {snap_dir} updated since {threshold}. "
        f"Existing files: {[(p.name, p.stat().st_mtime) for p in all_json]}. "
        "The OTEL ingest pipeline did not persist any spans."
    )
    largest = max(fresh_files, key=lambda p: p.stat().st_size)
    assert largest.stat().st_size > 10_000, (
        f"Largest fresh runtime_adg JSON {largest.name} is only "
        f"{largest.stat().st_size} bytes; expected > 10 KB after a real run."
    )
    # Verify the OTEL bridge log line appeared in subprocess stdout/stderr,
    # confirming the bridge actually flushed (not just that some other code
    # wrote to runtime_adg).
    combined = (result.stdout or "") + (result.stderr or "")
    assert "OTEL bridge:" in combined and "success=True" in combined, (
        f"apps_rg subprocess did not log the OTEL bridge success line. Output tail: {combined[-1500:]}"
    )
