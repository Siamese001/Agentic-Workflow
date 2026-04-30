"""Tests for the Layer 3 required-spans coverage gate."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class TestRequiredSpansGate(unittest.TestCase):
    """Layer 3 gate — verifies the manifest matches reality."""

    def test_manifest_loads(self) -> None:
        from ops_scripts.ci.check_required_spans_coverage import _load_manifest

        manifest = _load_manifest()
        self.assertIsInstance(manifest, dict)
        # All 6 apps_* with phase B coverage must be present.
        for app in (
            "apps_eval", "apps_exec", "apps_lic", "apps_research",
            "apps_rfp", "apps_underwriting_ai",
        ):
            self.assertIn(app, manifest, f"{app} missing from manifest")
            self.assertIn("required_spans", manifest[app])
            self.assertGreater(
                len(manifest[app]["required_spans"]), 0,
                f"{app} has empty required_spans list",
            )

    def test_apps_eval_spans_match_decorators(self) -> None:
        from ops_scripts.ci.check_required_spans_coverage import (
            _candidate_modules, _collect_decorated_qualnames, _load_manifest,
        )

        manifest = _load_manifest()
        required = set(manifest["apps_eval"]["required_spans"])
        decorated = _collect_decorated_qualnames(_candidate_modules("apps_eval"))
        missing = required - decorated
        self.assertEqual(
            missing, set(),
            f"apps_eval required_spans not found as @traces_execute markers: {missing}",
        )

    def test_apps_underwriting_ai_spans_match_decorators(self) -> None:
        from ops_scripts.ci.check_required_spans_coverage import (
            _candidate_modules, _collect_decorated_qualnames, _load_manifest,
        )

        manifest = _load_manifest()
        required = set(manifest["apps_underwriting_ai"]["required_spans"])
        decorated = _collect_decorated_qualnames(_candidate_modules("apps_underwriting_ai"))
        missing = required - decorated
        self.assertEqual(missing, set(), f"missing: {missing}")

    def test_gate_exits_zero_on_full_coverage(self) -> None:
        from ops_scripts.ci.check_required_spans_coverage import main

        # Capture stdout and assert exit code 0.
        rc = main()
        self.assertEqual(rc, 0, "Layer 3 gate should pass with current decorations")


if __name__ == "__main__":
    unittest.main()
