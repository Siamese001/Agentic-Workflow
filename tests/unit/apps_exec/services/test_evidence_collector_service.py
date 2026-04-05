"""Test EvidenceCollectorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEvidenceCollectorService:
    """Test EvidenceCollectorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.evidence_collector_service import EvidenceCollectorService

        config = {"max_evidence": 10}
        service = EvidenceCollectorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.evidence_collector_service import EvidenceCollectorService

        service = EvidenceCollectorService()
        assert service.config == {}

    @patch("apps_exec.services.evidence_collector_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_exec.services.evidence_collector_service import EvidenceCollectorService

        EvidenceCollectorService()
        mock_emit.assert_called_once_with("p4", "evidence_collector", "init")

    def test_collect_evidence(self):
        """Test collecting evidence for a claim."""
        from apps_exec.services.evidence_collector_service import EvidenceCollectorService

        service = EvidenceCollectorService()
        evidence = service.collect_evidence("Test claim")

        assert evidence == []

    def test_collect_evidence_empty_claim(self):
        """Test collecting evidence with empty claim (edge case)."""
        from apps_exec.services.evidence_collector_service import EvidenceCollectorService

        service = EvidenceCollectorService()
        evidence = service.collect_evidence("")

        assert evidence == []

    def test_collect_evidence_long_claim(self):
        """Test collecting evidence with long claim (edge case)."""
        from apps_exec.services.evidence_collector_service import EvidenceCollectorService

        service = EvidenceCollectorService()
        long_claim = "x" * 1000
        evidence = service.collect_evidence(long_claim)

        assert evidence == []
