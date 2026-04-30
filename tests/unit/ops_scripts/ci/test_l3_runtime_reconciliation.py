"""Tests for the L3 runtime reconciliation gate and OTEL poller."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class TestL3RuntimeReconciliation(unittest.TestCase):
    """Gate logic — manifest vs observed runtime spans."""

    def test_manifest_loads(self) -> None:
        from ops_scripts.ci.check_l3_runtime_reconciliation import _load_manifest_spans
        spans = _load_manifest_spans()
        self.assertGreater(len(spans), 0, "manifest is empty")
        # Sanity — at least one canonical engine method.
        sample_method = next(s for s in spans if "Engine" in s and ".execute" in s)
        self.assertIsNotNone(sample_method)

    def test_advisory_mode_never_fails(self) -> None:
        from ops_scripts.ci.check_l3_runtime_reconciliation import main
        rc = main(["--mode", "advisory"])
        self.assertEqual(rc, 0, "advisory mode must always exit 0")

    def test_strict_mode_with_no_data_returns_4(self) -> None:
        """When no observation source exists, strict mode exits 4 (data unavailable)."""
        from ops_scripts.ci import check_l3_runtime_reconciliation as module

        # Force the cache lookup to return empty by patching the path.
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(module, "LAST_OBSERVED_PATH", Path(tmp) / "nonexistent.json"):
                rc = module.main(["--mode", "strict"])
                self.assertEqual(rc, 4)

    def test_strict_mode_detects_manifest_only(self) -> None:
        """When observed is a strict subset of declared, exit 1 (manifest_only)."""
        from ops_scripts.ci import check_l3_runtime_reconciliation as module

        # Build a fake observation file with only ONE span seen.
        with tempfile.TemporaryDirectory() as tmp:
            fake_obs = Path(tmp) / "obs.json"
            # Pick first span from real manifest, then claim only it was seen.
            real = list(module._load_manifest_spans())[:1]
            fake_obs.write_text(json.dumps({
                "collected_at": "2026-04-30T00:00:00",
                "spans": real,
            }), encoding="utf-8")
            with mock.patch.object(module, "LAST_OBSERVED_PATH", fake_obs):
                rc = module.main(["--mode", "strict"])
                # All but 1 declared spans are missing → manifest_only flag (1).
                self.assertEqual(rc & 1, 1, f"expected bit 1 set, got rc={rc}")

    def test_strict_mode_detects_runtime_only(self) -> None:
        """When observed contains spans not in manifest, exit 2 (runtime_only)."""
        from ops_scripts.ci import check_l3_runtime_reconciliation as module

        with tempfile.TemporaryDirectory() as tmp:
            fake_obs = Path(tmp) / "obs.json"
            # Combine ALL declared + a fake undeclared span.
            spans = list(module._load_manifest_spans()) + ["GhostEngine.haunt"]
            fake_obs.write_text(json.dumps({
                "collected_at": "2026-04-30T00:00:00",
                "spans": spans,
            }), encoding="utf-8")
            with mock.patch.object(module, "LAST_OBSERVED_PATH", fake_obs):
                rc = module.main(["--mode", "strict"])
                self.assertEqual(rc & 2, 2, f"expected bit 2 set, got rc={rc}")
                # And bit 1 should NOT be set (all manifest spans seen).
                self.assertEqual(rc & 1, 0)

    def test_clean_run_returns_zero(self) -> None:
        """When observed exactly matches declared, exit 0."""
        from ops_scripts.ci import check_l3_runtime_reconciliation as module

        with tempfile.TemporaryDirectory() as tmp:
            fake_obs = Path(tmp) / "obs.json"
            spans = list(module._load_manifest_spans())
            fake_obs.write_text(json.dumps({
                "collected_at": "2026-04-30T00:00:00",
                "spans": spans,
            }), encoding="utf-8")
            with mock.patch.object(module, "LAST_OBSERVED_PATH", fake_obs):
                rc = module.main(["--mode", "strict"])
                self.assertEqual(rc, 0, f"expected 0, got rc={rc}")


class TestOtelSpanPoller(unittest.TestCase):
    """Poller writes a well-formed observation file."""

    def test_poller_writes_json(self) -> None:
        from ops_scripts.calibration import otel_span_poller as module
        # When no cache exists, source should be 'no-otel-cache' and count=0.
        rc = module.main(["--time-window-hours", "24"])
        self.assertIn(rc, (0, 4))  # 4 if no data, 0 if cache had data
        self.assertTrue(module.OUT_PATH.is_file())
        data = json.loads(module.OUT_PATH.read_text(encoding="utf-8"))
        self.assertIn("collected_at", data)
        self.assertIn("source", data)
        self.assertIn("spans", data)
        self.assertEqual(data["time_window_hours"], 24)


if __name__ == "__main__":
    unittest.main()
