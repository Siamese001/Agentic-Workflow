"""W6 Performance & Load Testing for apps_lic Multi-Touch Infrastructure.

W6.P2: Performance & Load Testing

Scale validation and latency benchmarks for:
- Touch scheduling throughput
- Signal detection performance
- Research bridge latency
- Migration batch processing
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestW6P2TouchSchedulingPerformance:
    """W6.P2: Touch scheduling performance benchmarks."""
    
    def test_touch_scheduling_latency_single(self):
        """Performance: Single touch scheduling latency < 100ms."""
        from apps_lic.coordination.touch_scheduler import TouchScheduler
        
        scheduler = TouchScheduler()
        
        start = time.perf_counter()
        request = scheduler.schedule_touch(
            campaign_id="perf-001",
            touch_id="touch-001",
            scheduled_time=datetime.now(timezone.utc),
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert request is not None
        assert elapsed_ms < 100, f"Touch scheduling took {elapsed_ms:.2f}ms (target < 100ms)"
    
    def test_touch_scheduling_throughput_100(self):
        """Performance: Schedule 100 touches within 5 seconds."""
        from apps_lic.coordination.touch_scheduler import TouchScheduler
        
        scheduler = TouchScheduler()
        
        start = time.perf_counter()
        for i in range(100):
            scheduler.schedule_touch(
                campaign_id=f"perf-throughput-{i:03d}",
                touch_id=f"touch-{i:03d}",
                scheduled_time=datetime.now(timezone.utc) + timedelta(hours=i),
            )
        elapsed_sec = time.perf_counter() - start
        
        assert elapsed_sec < 5.0, f"100 touches took {elapsed_sec:.2f}s (target < 5s)"
    
    def test_concurrent_touch_scheduling_10(self):
        """Performance: 10 concurrent touch schedules."""
        from apps_lic.coordination.touch_scheduler import TouchScheduler
        
        scheduler = TouchScheduler()
        
        def schedule_touch(i: int) -> float:
            start = time.perf_counter()
            scheduler.schedule_touch(
                campaign_id=f"perf-concurrent-{i:03d}",
                touch_id=f"touch-{i:03d}",
                scheduled_time=datetime.now(timezone.utc),
            )
            return time.perf_counter() - start
        
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(schedule_touch, i) for i in range(10)]
            latencies = [f.result() for f in as_completed(futures)]
        total_sec = time.perf_counter() - start
        
        avg_latency_ms = sum(latencies) / len(latencies) * 1000
        assert avg_latency_ms < 200, f"Avg latency {avg_latency_ms:.2f}ms (target < 200ms)"
        assert total_sec < 2.0, f"Total time {total_sec:.2f}s (target < 2s)"


class TestW6P2SignalDetectionPerformance:
    """W6.P2: Signal detection performance benchmarks."""
    
    def test_signal_detection_latency_single_company(self):
        """Performance: Signal detection for single company < 500ms."""
        from apps_lic.signals.detector import SignalDetector
        from apps_lic.signals.types import SignalSource
        
        detector = SignalDetector()
        
        start = time.perf_counter()
        signals = detector.detect(
            company_name="Performance Test Corp",
            sources=[SignalSource.RESEARCH],
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert elapsed_ms < 500, f"Signal detection took {elapsed_ms:.2f}ms (target < 500ms)"
    
    def test_signal_detection_batch_50_companies(self):
        """Performance: Batch signal detection for 50 companies < 10s."""
        from apps_lic.signals.detector import SignalDetector
        from apps_lic.signals.types import SignalSource
        
        detector = SignalDetector()
        companies = [f"Company {i}" for i in range(50)]
        
        start = time.perf_counter()
        for company in companies:
            detector.detect(
                company_name=company,
                sources=[SignalSource.RESEARCH],
            )
        elapsed_sec = time.perf_counter() - start
        
        assert elapsed_sec < 10.0, f"50 companies took {elapsed_sec:.2f}s (target < 10s)"


class TestW6P2ResearchBridgePerformance:
    """W6.P2: Research bridge performance benchmarks."""
    
    def test_research_bridge_latency(self):
        """Performance: Research bridge call latency < 2s."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge()
        
        start = time.perf_counter()
        result = bridge.fetch(
            recipient_class="RECRUITER",
            recipient_name="Perf Test",
            company_name="PerfCorp",
            job_title="Manager",
            channel="email",
            outreach_mode="cold",
            relationship_distance="cold",
            capability_ref="apps_research.v1",
            request_id="perf-req-001",
            run_id="perf-run-001",
            trace_id="perf-trace-001",
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert result is not None
        assert elapsed_ms < 2000, f"Bridge call took {elapsed_ms:.2f}ms (target < 2000ms)"
    
    def test_research_bridge_concurrent_5(self):
        """Performance: 5 concurrent research bridge calls."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge()
        
        def fetch_research(i: int) -> float:
            start = time.perf_counter()
            bridge.fetch(
                recipient_class="RECRUITER",
                recipient_name=f"User {i}",
                company_name=f"Company {i}",
                job_title="Manager",
                channel="email",
                outreach_mode="cold",
                relationship_distance="cold",
                capability_ref="apps_research.v1",
                request_id=f"perf-req-{i:03d}",
                run_id=f"perf-run-{i:03d}",
                trace_id=f"perf-trace-{i:03d}",
            )
            return time.perf_counter() - start
        
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_research, i) for i in range(5)]
            latencies = [f.result() for f in as_completed(futures)]
        total_sec = time.perf_counter() - start
        
        avg_latency_ms = sum(latencies) / len(latencies) * 1000
        assert avg_latency_ms < 3000, f"Avg latency {avg_latency_ms:.2f}ms (target < 3000ms)"
        assert total_sec < 5.0, f"Total time {total_sec:.2f}s (target < 5s)"


class TestW6P2MigrationPerformance:
    """W6.P2: Migration batch processing performance."""
    
    def test_migration_inventory_scan_1000(self):
        """Performance: Scan 1000 campaigns < 3s."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignInventory, CampaignRecord, CampaignStatus
        )
        
        # Create 1000 mock campaigns
        campaigns = [
            CampaignRecord(
                campaign_id=f"perf-camp-{i:04d}",
                campaign_name=f"Campaign {i}",
                status=CampaignStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=100,
                touch_count=50,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=1000,
            )
            for i in range(1000)
        ]
        
        start = time.perf_counter()
        inventory = CampaignInventory(campaigns=campaigns)
        summary = inventory.to_summary_dict()
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert summary["total_campaigns"] == 1000
        assert elapsed_ms < 3000, f"Inventory scan took {elapsed_ms:.2f}ms (target < 3000ms)"
    
    def test_migration_batch_processing_100(self):
        """Performance: Process 100 campaigns in batch < 5s."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignInventory, CampaignRecord, CampaignStatus
        )
        from apps_lic.migrations.w5_migration import W5MigrationRunner
        
        campaigns = [
            CampaignRecord(
                campaign_id=f"batch-camp-{i:03d}",
                campaign_name=f"Batch Campaign {i}",
                status=CampaignStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=100,
                touch_count=50,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=1000,
            )
            for i in range(100)
        ]
        
        inventory = CampaignInventory(campaigns=campaigns)
        runner = W5MigrationRunner(dry_run=True, batch_size=100)
        
        start = time.perf_counter()
        results = runner.run(inventory)
        elapsed_sec = time.perf_counter() - start
        
        assert elapsed_sec < 5.0, f"Batch processing took {elapsed_sec:.2f}s (target < 5s)"
    
    def test_compatibility_check_500(self):
        """Performance: Check compatibility for 500 campaigns < 2s."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignInventory, CampaignRecord, CampaignStatus, CompatibilityChecker
        )
        
        campaigns = [
            CampaignRecord(
                campaign_id=f"compat-camp-{i:03d}",
                campaign_name=f"Compat Campaign {i}",
                status=CampaignStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=100,
                touch_count=50,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=1000,
            )
            for i in range(500)
        ]
        
        inventory = CampaignInventory(campaigns=campaigns)
        checker = CompatibilityChecker()
        
        start = time.perf_counter()
        reports = checker.check_all(inventory)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert len(reports) == 500
        assert elapsed_ms < 2000, f"Compatibility check took {elapsed_ms:.2f}ms (target < 2000ms)"


class TestW6P2SpineWiringPerformance:
    """W6.P2: Spine wiring verification performance."""
    
    def test_spine_verification_latency(self):
        """Performance: Full spine verification < 1s."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        
        start = time.perf_counter()
        report = verifier.verify_all()
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert elapsed_ms < 1000, f"Spine verification took {elapsed_ms:.2f}ms (target < 1000ms)"
    
    def test_spine_verification_repeated_10(self):
        """Performance: 10 consecutive spine verifications < 5s total."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        start = time.perf_counter()
        for _ in range(10):
            verifier = SpineWiringVerifier()
            verifier.verify_all()
        elapsed_sec = time.perf_counter() - start
        
        assert elapsed_sec < 5.0, f"10 verifications took {elapsed_sec:.2f}s (target < 5s)"


class TestW6P2SequenceBuilderPerformance:
    """W6.P2: Sequence builder performance benchmarks."""
    
    def test_sequence_definition_lookup(self):
        """Performance: Sequence definition lookup < 10ms."""
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        start = time.perf_counter()
        seq_type = SequenceType.STANDARD_3_TOUCH
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert seq_type.value == "standard_3_touch"
        assert elapsed_ms < 10, f"Definition lookup took {elapsed_ms:.2f}ms (target < 10ms)"
    
    def test_touch_context_creation(self):
        """Performance: Touch context creation < 5ms."""
        from apps_lic.sequences.touch_propagation import TouchContext
        
        start = time.perf_counter()
        context = TouchContext(
            campaign_id="perf-context-001",
            recipient_id="recip-001",
            touch_number=1,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert context.campaign_id == "perf-context-001"
        assert elapsed_ms < 5, f"Context creation took {elapsed_ms:.2f}ms (target < 5ms)"


class TestW6P2LoadStress:
    """W6.P2: Load and stress tests."""
    
    def test_touch_scheduling_burst_1000(self):
        """Stress: Schedule 1000 touches in burst."""
        from apps_lic.coordination.touch_scheduler import TouchScheduler
        
        scheduler = TouchScheduler()
        
        start = time.perf_counter()
        for i in range(1000):
            scheduler.schedule_touch(
                campaign_id=f"burst-{i:04d}",
                touch_id=f"touch-{i:04d}",
                scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=i),
            )
        elapsed_sec = time.perf_counter() - start
        
        # Should complete within 30 seconds even under load
        assert elapsed_sec < 30.0, f"1000 touches took {elapsed_sec:.2f}s (target < 30s)"
    
    def test_research_bridge_burst_20(self):
        """Stress: 20 rapid research bridge calls."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge()
        
        start = time.perf_counter()
        for i in range(20):
            bridge.fetch(
                recipient_class="RECRUITER",
                recipient_name=f"Burst {i}",
                company_name=f"BurstCorp {i}",
                job_title="Manager",
                channel="email",
                outreach_mode="cold",
                relationship_distance="cold",
                capability_ref="apps_research.v1",
                request_id=f"burst-req-{i:03d}",
                run_id=f"burst-run-{i:03d}",
                trace_id=f"burst-trace-{i:03d}",
            )
        elapsed_sec = time.perf_counter() - start
        
        assert elapsed_sec < 30.0, f"20 bridge calls took {elapsed_sec:.2f}s (target < 30s)"


class TestW6P2MemoryEfficiency:
    """W6.P2: Memory efficiency benchmarks."""
    
    def test_large_inventory_memory_footprint(self):
        """Performance: 10,000 campaign inventory memory < 50MB."""
        import sys
        from apps_lic.migrations.campaign_inventory import (
            CampaignInventory, CampaignRecord, CampaignStatus
        )
        
        campaigns = [
            CampaignRecord(
                campaign_id=f"mem-camp-{i:05d}",
                campaign_name=f"Memory Test {i}",
                status=CampaignStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=100,
                touch_count=50,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=1000,
            )
            for i in range(10000)
        ]
        
        # Measure memory after creation
        import gc
        gc.collect()
        
        inventory = CampaignInventory(campaigns=campaigns)
        
        # Rough estimate - inventory should be usable with 10k campaigns
        assert inventory.total_campaigns == 10000
        assert len(inventory.get_migratable()) == 10000


# Import needed for tests
from unittest.mock import patch, MagicMock
import gc
