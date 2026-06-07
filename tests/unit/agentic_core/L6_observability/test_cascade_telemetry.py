"""G7 — cascade telemetry consumer tests.

Plan ref: ``docs/archive/windsurf/legacy-tree/plans/qwen-confidence-routing-hardening-d4e7b1.md`` G7.
"""

from __future__ import annotations

import unittest

from agentic_core.L6_observability.cascade_telemetry import (
    CascadeEvent,
    CascadeTelemetryRecorder,
    get_recorder,
    reset_for_tests,
)


class CascadeTelemetryRecorderTest(unittest.TestCase):
    def setUp(self) -> None:
        reset_for_tests()

    def tearDown(self) -> None:
        reset_for_tests()

    def test_record_dispatch_dict_form(self) -> None:
        rec = CascadeTelemetryRecorder()
        rec.record_dispatch(
            {
                "tier_attempted": "MEDIUM",
                "tier_used": "LOW",
                "fallback_reason": "qwen_health_probe_failed",
                "success": True,
            },
            app_name="apps_eval",
        )
        stats = rec.stats()
        self.assertEqual(stats.total, 1)
        self.assertEqual(stats.cascades, 1)
        self.assertEqual(stats.cascade_rate, 1.0)
        self.assertEqual(stats.by_fallback_reason["qwen_health_probe_failed"], 1)
        self.assertEqual(stats.by_app["apps_eval"], 1)

    def test_record_dispatch_object_form(self) -> None:
        rec = CascadeTelemetryRecorder()

        class _R:
            tier_attempted = "MEDIUM"
            tier_used = "MEDIUM"
            fallback_reason = ""
            success = True

        rec.record_dispatch(_R(), app_name="apps_lic")
        stats = rec.stats()
        self.assertEqual(stats.total, 1)
        self.assertEqual(stats.cascades, 0)
        self.assertEqual(stats.cascade_rate, 0.0)

    def test_buffer_caps_at_max_events(self) -> None:
        rec = CascadeTelemetryRecorder(max_events=3)
        for i in range(5):
            rec.record(
                CascadeEvent(
                    app_name=f"app_{i}",
                    tier_attempted="MEDIUM",
                    tier_used="LOW",
                    fallback_reason="x",
                    success=True,
                )
            )
        self.assertEqual(rec.event_count, 3)
        # The 3 newest should remain (app_2, app_3, app_4)
        apps = {e.app_name for e in rec.snapshot()}
        self.assertEqual(apps, {"app_2", "app_3", "app_4"})

    def test_zero_max_events_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CascadeTelemetryRecorder(max_events=0)

    def test_empty_stats_are_well_defined(self) -> None:
        stats = CascadeTelemetryRecorder().stats()
        self.assertEqual(stats.total, 0)
        self.assertEqual(stats.cascades, 0)
        self.assertEqual(stats.cascade_rate, 0.0)
        self.assertEqual(stats.by_fallback_reason, {})
        self.assertEqual(stats.by_app, {})

    def test_singleton_is_shared(self) -> None:
        a = get_recorder()
        b = get_recorder()
        self.assertIs(a, b)
        a.record_dispatch(
            {"tier_attempted": "MEDIUM", "tier_used": "LOW", "fallback_reason": "z", "success": False},
            app_name="t",
        )
        self.assertEqual(b.event_count, 1)

    def test_failures_counted(self) -> None:
        rec = CascadeTelemetryRecorder()
        for ok in (True, False, False, True):
            rec.record_dispatch(
                {
                    "tier_attempted": "MEDIUM",
                    "tier_used": "MEDIUM",
                    "fallback_reason": "",
                    "success": ok,
                },
                app_name="t",
            )
        stats = rec.stats()
        self.assertEqual(stats.successes, 2)
        self.assertEqual(stats.failures, 2)


if __name__ == "__main__":
    unittest.main()
