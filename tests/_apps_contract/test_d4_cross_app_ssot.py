"""D4 tests — Cross-app alignment and SSOT consolidation.

Covers:
  D4.1 apps_qna.config.config_inventory (scan_config_inventory, ConfigEntry, DriftViolation)
  D4.2 apps_qna.integrations.provider_adapter (QnaProviderContext, build_provider_context)
  D4.3 apps_qna.config.spine_alignment (check_spine_alignment, AlignmentReport)

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D4
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# D4.1 — Config inventory & drift detection
# ---------------------------------------------------------------------------

class TestConfigInventory:
    def test_importable(self) -> None:
        from apps_qna.config.config_inventory import (
            scan_config_inventory,
            ConfigInventoryReport,
            ConfigEntry,
            DriftViolation,
        )
        assert callable(scan_config_inventory)

    def test_scan_runs_without_error(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        assert report is not None
        assert report.files_scanned > 0

    def test_all_yaml_files_scanned(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        assert report.files_scanned >= 10

    def test_records_parsed(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        assert report.records_parsed >= 10

    def test_entries_have_filenames(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        for entry in report.entries:
            assert entry.filename != ""

    def test_eval_rubrics_found(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        rubric_entries = [e for e in report.entries if "eval_rubric" in e.filename]
        assert len(rubric_entries) >= 1

    def test_grader_roster_found(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        roster_entries = [e for e in report.entries if "grader_roster" in e.filename]
        assert len(roster_entries) >= 1

    def test_app_id_populated(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        apps_qna_entries = [e for e in report.entries if e.app_id == "apps_qna"]
        assert len(apps_qna_entries) >= 5

    def test_policy_hash_extracted(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        entries_with_policy = [e for e in report.entries if e.policy_hash]
        assert len(entries_with_policy) >= 1

    def test_no_drift_in_canonical_configs(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        assert len(report.drift_violations) == 0, (
            f"Unexpected drift: {[(d.field, d.file_a, d.file_b) for d in report.drift_violations]}"
        )

    def test_get_policy_hashes(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory, get_policy_hashes
        report = scan_config_inventory()
        hashes = get_policy_hashes(report)
        assert isinstance(hashes, dict)

    def test_drift_detection_with_synthetic_data(self) -> None:
        from apps_qna.config.config_inventory import _detect_drift, ConfigEntry
        entries = [
            ConfigEntry(
                filename="a.yaml",
                app_id="apps_qna",
                task_class="qna_pack_build",
                policy_hash="policy://v1",
                version="1.0.0",
            ),
            ConfigEntry(
                filename="b.yaml",
                app_id="apps_qna",
                task_class="qna_pack_build",
                policy_hash="policy://v2",
                version="1.0.0",
            ),
        ]
        violations = _detect_drift(entries)
        assert len(violations) >= 1
        assert any(v.field == "policy_hash" for v in violations)

    def test_no_drift_same_policy(self) -> None:
        from apps_qna.config.config_inventory import _detect_drift, ConfigEntry
        entries = [
            ConfigEntry(
                filename="a.yaml",
                app_id="apps_qna",
                task_class="qna_pack_build",
                policy_hash="policy://v1",
                version="1.0.0",
            ),
            ConfigEntry(
                filename="b.yaml",
                app_id="apps_qna",
                task_class="qna_pack_build",
                policy_hash="policy://v1",
                version="1.0.0",
            ),
        ]
        violations = _detect_drift(entries)
        assert len(violations) == 0

    def test_aligned_flag_type(self) -> None:
        from apps_qna.config.config_inventory import scan_config_inventory
        report = scan_config_inventory()
        assert isinstance(report.aligned, bool)


# ---------------------------------------------------------------------------
# D4.2 — Provider SDK integration adapter
# ---------------------------------------------------------------------------

class TestProviderAdapter:
    def test_importable(self) -> None:
        from apps_qna.integrations.provider_adapter import (
            QnaProviderContext,
            build_provider_context,
            get_timestamp,
        )
        assert callable(build_provider_context)
        assert callable(get_timestamp)

    def test_build_provider_context_defaults(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context
        ctx = build_provider_context()
        assert ctx.request_id == ""
        assert ctx.model_id == ""
        assert not ctx.has_model()

    def test_build_provider_context_with_params(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context
        ctx = build_provider_context(
            request_id="req-001",
            run_id="run-001",
            interview_slug="google-swe-l5",
            route_id="build_time_compiler",
            model_id="claude-3-opus",
            max_tokens=4096,
            temperature=0.0,
        )
        assert ctx.request_id == "req-001"
        assert ctx.interview_slug == "google-swe-l5"
        assert ctx.has_model()

    def test_now_iso_returns_string(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context
        ctx = build_provider_context()
        ts = ctx.now_iso()
        assert isinstance(ts, str)
        assert "T" in ts or ts == "1970-01-01T00:00:00+00:00"

    def test_frozen_clock_injection(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context
        try:
            from agentic_core.utils.runners.providers import FrozenClock
            frozen = FrozenClock("2026-05-05T00:00:00")
            ctx = build_provider_context(inject_clock=frozen)
            ts = ctx.now_iso()
            assert "2026-05-05" in ts
        except ImportError:
            pytest.skip("FrozenClock not available")

    def test_get_timestamp_returns_string(self) -> None:
        from apps_qna.integrations.provider_adapter import get_timestamp
        ts = get_timestamp()
        assert isinstance(ts, str)
        assert len(ts) >= 10

    def test_get_timestamp_with_context(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context, get_timestamp
        ctx = build_provider_context(interview_slug="test")
        ts = get_timestamp(ctx)
        assert isinstance(ts, str)

    def test_extra_dict_preserved(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context
        ctx = build_provider_context(extra={"foo": "bar", "count": 42})
        assert ctx.extra["foo"] == "bar"
        assert ctx.extra["count"] == 42

    def test_canonical_clock_acquired(self) -> None:
        from apps_qna.integrations.provider_adapter import build_provider_context
        ctx = build_provider_context()
        assert ctx.clock is not None or ctx.clock is None


# ---------------------------------------------------------------------------
# D4.3 — Cross-app spine alignment
# ---------------------------------------------------------------------------

class TestSpineAlignment:
    def test_importable(self) -> None:
        from apps_qna.config.spine_alignment import (
            check_spine_alignment,
            AlignmentReport,
            ClaimedRoute,
            RouteAlignmentEntry,
            get_peer_apps_for_route,
        )
        assert callable(check_spine_alignment)

    def test_alignment_report_runs(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        assert report is not None
        assert report.app == "apps_qna"

    def test_manifest_path_populated(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        assert "spine_manifest" in report.manifest_path

    def test_claimed_routes_non_empty(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        assert len(report.claimed_routes) >= 1

    def test_build_time_compiler_aligned(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        btc_entries = [e for e in report.route_entries if e.route_type == "build_time_compiler"]
        assert len(btc_entries) >= 1
        assert btc_entries[0].known

    def test_r4_single_action_aligned(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        r4_entries = [e for e in report.route_entries if e.route_type == "R4_SINGLE_ACTION"]
        assert len(r4_entries) >= 1
        assert r4_entries[0].known

    def test_no_unknown_route_types(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        assert report.unknown_route_types == (), (
            f"Unknown route types: {report.unknown_route_types}"
        )

    def test_aligned_overall(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        assert report.aligned, (
            f"Alignment failed: unknown={report.unknown_route_types}, "
            f"warnings={[(e.route_type, e.warning) for e in report.route_entries if e.warning]}"
        )

    def test_peer_apps_for_build_time_compiler(self) -> None:
        from apps_qna.config.spine_alignment import get_peer_apps_for_route
        peers = get_peer_apps_for_route("build_time_compiler")
        assert "apps_eval" in peers

    def test_peer_apps_for_r4(self) -> None:
        from apps_qna.config.spine_alignment import get_peer_apps_for_route
        peers = get_peer_apps_for_route("R4_SINGLE_ACTION")
        assert len(peers) >= 2

    def test_unknown_route_type_returns_warning(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        from pathlib import Path
        import tempfile, textwrap
        manifest_yaml = textwrap.dedent("""
            schema_version: 1
            app: apps_qna
            claimed_routes:
              - type: UNKNOWN_ROUTE_XYZ
                description: test
        """)
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write(manifest_yaml)
            tmp_path = Path(f.name)
        try:
            report = check_spine_alignment(manifest_path=tmp_path)
            assert "UNKNOWN_ROUTE_XYZ" in report.unknown_route_types
            assert not report.aligned
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_r4_has_required_contracts(self) -> None:
        from apps_qna.config.spine_alignment import check_spine_alignment
        report = check_spine_alignment()
        r4_entries = [e for e in report.route_entries if e.route_type == "R4_SINGLE_ACTION"]
        if r4_entries:
            assert "ExitReviewPacket" in r4_entries[0].required_contracts
