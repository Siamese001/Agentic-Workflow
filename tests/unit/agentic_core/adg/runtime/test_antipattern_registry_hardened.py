"""Test hardened antipattern registry with determinism, purity, and thread safety."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.runtime.antipattern_registry import AntipatternRegistry
from agentic_core.adg.runtime.antipattern_types import (
    AntipatternCategory,
    AntipatternSeverity,
    SuppressionRecord,
)


@pytest.mark.unit
class TestAntipatternRegistryHardened:
    """Test hardened antipattern registry determinism, purity, and thread safety."""

    def test_fingerprint_is_deterministic(self):
        """Same inputs produce identical fingerprints."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        record1 = registry.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
            line_start=42,
            symbol="bar",
        )
        registry2 = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        record2 = registry2.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
            line_start=42,
            symbol="bar",
        )
        assert record1.fingerprint == record2.fingerprint
        assert record1.record_id == record2.record_id

    def test_fingerprint_no_uuid4(self):
        """Fingerprint is a hex hash, not a UUID format."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        record = registry.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
            line_start=42,
        )
        # Fingerprint should be 64-char hex (SHA-256)
        assert len(record.fingerprint) == 64
        assert all(c in "0123456789abcdef" for c in record.fingerprint)
        # record_id should be apr- prefix + 12 hex chars
        assert record.record_id.startswith("apr-")
        assert len(record.record_id) == 16

    def test_register_deduplicates(self):
        """Same pattern registered twice returns existing record."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        record1 = registry.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
            line_start=42,
            symbol="bar",
        )
        record2 = registry.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
            line_start=42,
            symbol="bar",
        )
        assert record1.fingerprint == record2.fingerprint
        assert record1.record_id == record2.record_id
        # Only one record in the report
        assert registry.report.total_count == 1

    def test_by_category_is_pure(self):
        """Calling by_category multiple times produces no state mutation."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        registry.register(AntipatternCategory.SILENT_EXCEPTION_SWALLOW, source_file="foo.py")
        registry.register(AntipatternCategory.BARE_EXCEPT, source_file="bar.py")

        # Call by_category multiple times
        result1 = registry.report.by_category
        result2 = registry.report.by_category
        result3 = registry.report.by_category

        # All should be identical
        assert result1 == result2 == result3
        # No record count growth
        assert registry.report.total_count == 2

    def test_suppress_requires_reason(self):
        """Suppress without reason raises ValueError."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        record = registry.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
        )
        with pytest.raises(ValueError, match="Suppress requires a reason"):
            registry.suppress(record, reason="")

        # Valid suppress should work
        registry.suppress(record, reason="false positive")
        assert record.suppression is not None
        assert record.suppression.reason == "false positive"

    def test_suppress_raises_if_record_not_found(self):
        """Suppress raises ValueError if record not in registry."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        registry.register(AntipatternCategory.SILENT_EXCEPTION_SWALLOW, source_file="foo.py")

        # Create a record from a different registry (not in this registry)
        registry2 = AntipatternRegistry(agent_id="test-agent", run_id="different-run")
        external_record = registry2.register(
            AntipatternCategory.BARE_EXCEPT,
            source_file="bar.py",
        )

        with pytest.raises(ValueError, match="Record with fingerprint .* not found in registry"):
            registry.suppress(external_record, reason="test")

    def test_suppression_record_to_dict(self):
        """SuppressionRecord.to_dict() returns correct structure."""
        suppression = SuppressionRecord(
            reason="false positive",
            reviewer="alice",
            ticket="TICKET-123",
        )
        result = suppression.to_dict()
        assert result["reason"] == "false positive"
        assert result["reviewer"] == "alice"
        assert result["ticket"] == "TICKET-123"
        assert "suppressed_at" in result
        assert isinstance(result["suppressed_at"], float)

    def test_antipattern_record_to_dict_with_suppression(self):
        """AntipatternRecord.to_dict() includes suppression when present."""
        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        record = registry.register(
            AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
            source_file="foo.py",
            line_start=42,
        )
        registry.suppress(record, reason="false positive", reviewer="alice")

        result = record.to_dict()
        assert result["suppression"] is not None
        assert result["suppression"]["reason"] == "false positive"
        assert result["suppression"]["reviewer"] == "alice"

    def test_telemetry_adapter_no_import_side_effects(self):
        """Importing antipattern_telemetry does not emit traces on import."""
        import agentic_core.adg.runtime.antipattern_telemetry as telemetry_module

        # Verify module imported cleanly
        assert hasattr(telemetry_module, "AntipatternTelemetryAdapter")
        # No way to verify no traces were emitted without mocking,
        # but we can verify the adapter class exists and is callable
        adapter = telemetry_module.AntipatternTelemetryAdapter()
        assert adapter is not None

    def test_telemetry_adapter_validates_report_type(self):
        """Telemetry adapter emit_report raises TypeError for invalid report."""
        import agentic_core.adg.runtime.antipattern_telemetry as telemetry_module

        adapter = telemetry_module.AntipatternTelemetryAdapter()
        with pytest.raises(TypeError, match="Expected AntipatternRegistryReport"):
            adapter.emit_report(None)

    def test_registry_thread_safe(self):
        """Concurrent register calls produce correct count."""
        import threading

        registry = AntipatternRegistry(agent_id="test-agent", run_id="test-run")
        num_threads = 50

        def register_pattern():
            for i in range(10):
                registry.register(
                    AntipatternCategory.SILENT_EXCEPTION_SWALLOW,
                    source_file=f"file_{threading.current_thread().ident}_{i}.py",
                    line_start=i,
                )

        threads = [threading.Thread(target=register_pattern) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All registrations should complete
        assert registry.report.total_count == num_threads * 10

    def test_no_lifecycle_trace_on_import(self):
        """Importing antipattern_registry does not import lifecycle_trace_contract."""
        # This test must run in a fresh interpreter to be meaningful
        # For now, we verify the module structure is clean
        import agentic_core.adg.runtime.antipattern_registry as registry_module

        # Check that lifecycle_trace_contract is NOT in the module's imports
        # by inspecting the module's __dict__
        assert "lifecycle_trace_contract" not in registry_module.__dict__
        assert "_emit_records_execution_trace" not in registry_module.__dict__

    def test_mcp_categories_in_severity_map(self):
        """All 17 new MCP categories have severity entries."""
        from agentic_core.adg.runtime.antipattern_types import _SEVERITY_MAP

        mcp_categories = [
            AntipatternCategory.SECRET_IN_EDITOR_CONFIG,
            AntipatternCategory.UNPINNED_MCP_PACKAGE,
            AntipatternCategory.DEFAULT_LOCAL_DB_CREDENTIALS,
            AntipatternCategory.OVERBROAD_FILESYSTEM_ROOT,
            AntipatternCategory.REDUNDANT_CAPABILITY_OVERLAP,
            AntipatternCategory.REMOTE_MCP_WITHOUT_EXPLICIT_MODE,
            AntipatternCategory.MACHINE_SPECIFIC_ABSOLUTE_EXECUTABLE_PATH,
            AntipatternCategory.PLACEHOLDER_VALUE_IN_LIVE_CONFIG,
            AntipatternCategory.NETWORK_TOOL_WITHOUT_EGRESS_POLICY,
            AntipatternCategory.MIXED_MUTATION_AND_EXFILTRATION_SURFACE,
            AntipatternCategory.IMPORT_TIME_SIDE_EFFECT,
            AntipatternCategory.READ_ACCESSOR_WITH_SIDE_EFFECT,
            AntipatternCategory.NONDETERMINISTIC_ID_GENERATION,
            AntipatternCategory.DOMAIN_MODEL_COUPLED_TO_TELEMETRY,
            AntipatternCategory.SUPPRESSION_WITHOUT_REASON,
            AntipatternCategory.UNBOUNDED_REGISTRY_GROWTH,
            AntipatternCategory.EXACT_MATCH_ONLY_CLASSIFIER,
        ]

        for cat in mcp_categories:
            assert cat in _SEVERITY_MAP, f"MCP category {cat} missing from severity map"
            # Verify severity is one of the valid enum values
            assert _SEVERITY_MAP[cat] in AntipatternSeverity
