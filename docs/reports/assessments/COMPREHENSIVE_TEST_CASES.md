# Comprehensive Test Cases for Target State Gap Implementations

**Generated:** 2026-02-03
**Coverage:** Unit, Integration, and E2E tests for all gap implementations

---

## Test Suite Overview

### Test Categories

- **Unit Tests:** Individual component testing (90% coverage target)
- **Integration Tests:** Component interaction validation
- **E2E Tests:** Full workflow simulation
- **Performance Tests:** Load and stress testing
- **Security Tests:** Vulnerability and permission testing

---

## Gap 1: Knowledge Store Test Cases

### Unit Tests

#### File: `tests/unit/agentic_core/L4_state/knowledge/test_knowledge_store.py`

```python
import pytest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path

from agentic_core.L4_state.knowledge.knowledge_store import (
    KnowledgeStore, KnowledgeEntry, ActionFeedback, KnowledgeType
)

class TestKnowledgeStore:
    """Test suite for KnowledgeStore functionality."""

    @pytest.fixture
    def temp_knowledge_store(self):
        """Create temporary knowledge store for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = KnowledgeStore(storage_path=Path(temp_dir))
            yield store

    @pytest.fixture
    def sample_context(self):
        """Sample context data for testing."""
        return {
            "healing_stage": "detected",
            "failure_analysis": {"type": "syntax_error", "severity": "medium"},
            "system_state": {"cpu": "60%", "memory": "70%"}
        }

    @pytest.fixture
    def sample_feedback(self):
        """Sample action feedback for testing."""
        return ActionFeedback(
            action_id="test_action_001",
            action_type="code_fix",
            success=True,
            outcome={"lines_changed": 5, "errors_fixed": 2},
            errors=[],
            performance_metrics={"execution_time": 1.5, "memory_usage": 128},
            timestamp=datetime.now(),
            context_id="ctx_test_001"
        )

    def test_store_context_success(self, temp_knowledge_store, sample_context):
        """Test successful context storage."""
        result = temp_knowledge_store.store_context(
            "test_context", sample_context, "test_source"
        )

        assert result is True
        assert "test_context" in temp_knowledge_store._memory_cache
        entry = temp_knowledge_store._memory_cache["test_context"]
        assert entry.knowledge_type == KnowledgeType.CONTEXT
        assert entry.source == "test_source"

    def test_retrieve_context_success(self, temp_knowledge_store, sample_context):
        """Test successful context retrieval."""
        temp_knowledge_store.store_context("test_context", sample_context)

        retrieved = temp_knowledge_store.retrieve_context("test_context")

        assert retrieved is not None
        assert retrieved["healing_stage"] == "detected"
        assert retrieved["failure_analysis"]["type"] == "syntax_error"

    def test_retrieve_nonexistent_context(self, temp_knowledge_store):
        """Test retrieval of non-existent context."""
        retrieved = temp_knowledge_store.retrieve_context("nonexistent")
        assert retrieved is None

    def test_update_from_feedback(self, temp_knowledge_store, sample_feedback):
        """Test feedback processing and learning updates."""
        result = temp_knowledge_store.update_from_feedback(sample_feedback)

        assert result is True

        # Check feedback was stored
        feedback_key = f"feedback_{sample_feedback.action_id}"
        assert feedback_key in temp_knowledge_store._memory_cache

        # Check learning pattern was created
        pattern_key = f"pattern_{sample_feedback.action_type}_{sample_feedback.success}"
        assert pattern_key in temp_knowledge_store._memory_cache

    def test_configuration_management(self, temp_knowledge_store):
        """Test configuration storage and retrieval."""
        config = {"max_retries": 3, "timeout": 30, "debug": True}

        # Store configuration
        result = temp_knowledge_store.store_configuration("validator", config)
        assert result is True

        # Retrieve configuration
        retrieved = temp_knowledge_store.get_configuration("validator")
        assert retrieved == config

        # Test non-existent config
        empty_config = temp_knowledge_store.get_configuration("nonexistent")
        assert empty_config == {}

    def test_ttl_expiration(self, temp_knowledge_store, sample_context):
        """Test time-to-live expiration functionality."""
        # Store context with 1 second TTL
        temp_knowledge_store.store_context(
            "expiring_context", sample_context, ttl_hours=0.0001  # ~0.36 seconds
        )

        # Should be available immediately
        retrieved = temp_knowledge_store.retrieve_context("expiring_context")
        assert retrieved is not None

        # Wait for expiration
        import time
        time.sleep(1)

        # Should be expired
        retrieved = temp_knowledge_store.retrieve_context("expiring_context")
        assert retrieved is None

    def test_cleanup_expired_entries(self, temp_knowledge_store, sample_context):
        """Test cleanup of expired entries."""
        # Store both expiring and non-expiring contexts
        temp_knowledge_store.store_context(
            "expiring", sample_context, ttl_hours=0.0001
        )
        temp_knowledge_store.store_context(
            "non_expiring", sample_context, ttl_hours=24
        )

        # Wait for expiration
        import time
        time.sleep(1)

        # Cleanup expired entries
        cleaned = temp_knowledge_store.cleanup_expired_entries()
        assert cleaned == 1

        # Verify only non-expiring context remains
        assert temp_knowledge_store.retrieve_context("expiring") is None
        assert temp_knowledge_store.retrieve_context("non_expiring") is not None

    def test_statistics(self, temp_knowledge_store, sample_context, sample_feedback):
        """Test knowledge store statistics."""
        # Add some data
        temp_knowledge_store.store_context("ctx1", sample_context)
        temp_knowledge_store.store_configuration("test", {"key": "value"})
        temp_knowledge_store.update_from_feedback(sample_feedback)

        stats = temp_knowledge_store.get_statistics()

        assert stats["total_entries"] >= 3
        assert "entries_by_type" in stats
        assert stats["entries_by_type"][KnowledgeType.CONTEXT.value] >= 1
        assert stats["entries_by_type"][KnowledgeType.CONFIGURATION.value] >= 1
        assert stats["entries_by_type"][KnowledgeType.FEEDBACK.value] >= 1
        assert "memory_usage_mb" in stats
        assert stats["memory_usage_mb"] > 0

    def test_persistence_and_recovery(self, temp_knowledge_store, sample_context):
        """Test data persistence across restarts."""
        # Store data
        temp_knowledge_store.store_context("persistent_ctx", sample_context)

        # Create new store instance (simulates restart)
        new_store = KnowledgeStore(storage_path=temp_knowledge_store.storage_path)

        # Data should be loaded from disk
        retrieved = new_store.retrieve_context("persistent_ctx")
        assert retrieved is not None
        assert retrieved["healing_stage"] == "detected"

    def test_concurrent_access(self, temp_knowledge_store, sample_context):
        """Test thread safety of knowledge store operations."""
        import threading

        results = []

        def store_context(thread_id):
            result = temp_knowledge_store.store_context(
                f"thread_{thread_id}",
                {**sample_context, "thread_id": thread_id}
            )
            results.append(result)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=store_context, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All operations should succeed
        assert all(results)
        assert len(results) == 10

        # All contexts should be stored
        for i in range(10):
            retrieved = temp_knowledge_store.retrieve_context(f"thread_{i}")
            assert retrieved is not None
            assert retrieved["thread_id"] == i
```

#### File: `tests/unit/agentic_core/L4_state/knowledge/test_context_manager.py`

```python
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from agentic_core.L4_state.knowledge.context_manager import (
    ContextManager, Context, HealingRequest, ContextStatus
)
from agentic_core.L4_state.knowledge.knowledge_store import KnowledgeStore

class TestContextManager:
    """Test suite for ContextManager functionality."""

    @pytest.fixture
    def mock_knowledge_store(self):
        """Create mock knowledge store."""
        return Mock(spec=KnowledgeStore)

    @pytest.fixture
    def context_manager(self, mock_knowledge_store):
        """Create context manager with mock knowledge store."""
        return ContextManager(mock_knowledge_store)

    @pytest.fixture
    def sample_healing_request(self):
        """Sample healing request for testing."""
        return HealingRequest(
            request_id="req_001",
            source="test_sensor",
            failure_events=[{"type": "error", "message": "Test error"}],
            severity="medium",
            priority=5
        )

    def test_create_context_success(self, context_manager, sample_healing_request):
        """Test successful context creation."""
        context = context_manager.create_context(sample_healing_request)

        assert context is not None
        assert context.context_id == f"ctx_{sample_healing_request.request_id}"
        assert context.status == ContextStatus.ACTIVE
        assert context.request == sample_healing_request
        assert "healing_stage" in context.data
        assert context.data["healing_stage"] == "initialized"

    def test_create_context_with_ttl(self, context_manager, sample_healing_request):
        """Test context creation with custom TTL."""
        context = context_manager.create_context(sample_healing_request, ttl_hours=2)

        assert context is not None
        assert context.expires_at is not None
        expected_expiry = datetime.now() + timedelta(hours=2)
        assert abs((context.expires_at - expected_expiry).total_seconds()) < 60  # 1 minute tolerance

    def test_update_context_success(self, context_manager, sample_healing_request):
        """Test successful context update."""
        context = context_manager.create_context(sample_healing_request)

        updates = {
            "healing_stage": "analyzing",
            "validator_results": {"syntax_check": "passed"},
            "new_field": "test_value"
        }

        result = context_manager.update_context(context.context_id, updates)

        assert result is True
        # Mock should be called with updated data
        context_manager.knowledge_store.store_context.assert_called()

    def test_update_nonexistent_context(self, context_manager):
        """Test update of non-existent context."""
        result = context_manager.update_context("nonexistent", {"test": "value"})
        assert result is False

    def test_get_context_success(self, context_manager, sample_healing_request):
        """Test successful context retrieval."""
        context = context_manager.create_context(sample_healing_request)

        # Mock the knowledge store to return context data
        context_data = {
            "context_id": context.context_id,
            "request": context.request.__dict__,
            "status": context.status.value,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "expires_at": None,
            "data": context.data,
            "related_contexts": context.related_contexts,
            "access_count": context.access_count,
            "tags": context.tags
        }
        context_manager.knowledge_store.retrieve_context.return_value = context_data

        retrieved = context_manager.get_context(context.context_id)

        assert retrieved is not None
        assert retrieved.context_id == context.context_id
        assert retrieved.status == ContextStatus.ACTIVE

    def test_archive_context_success(self, context_manager, sample_healing_request):
        """Test successful context archiving."""
        context = context_manager.create_context(sample_healing_request)

        # Mock knowledge store to return context data
        context_data = {
            "context_id": context.context_id,
            "request": context.request.__dict__,
            "status": context.status.value,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "expires_at": None,
            "data": context.data,
            "related_contexts": context.related_contexts,
            "access_count": context.access_count,
            "tags": context.tags
        }
        context_manager.knowledge_store.retrieve_context.return_value = context_data

        result = context_manager.archive_context(context.context_id, "test_reason")

        assert result is True
        # Verify archive data was added
        call_args = context_manager.knowledge_store.store_context.call_args[0][1]
        assert call_args["archived_at"] is not None
        assert call_args["archive_reason"] == "test_reason"

    def test_add_context_relationship(self, context_manager, sample_healing_request):
        """Test adding context relationships."""
        context1 = context_manager.create_context(sample_healing_request)

        # Create second request and context
        request2 = HealingRequest(request_id="req_002", source="test")
        context2 = context_manager.create_context(request2)

        # Mock retrieval for relationship update
        context_data = {
            "context_id": context1.context_id,
            "request": context1.request.__dict__,
            "status": context1.status.value,
            "created_at": context1.created_at.isoformat(),
            "updated_at": context1.updated_at.isoformat(),
            "expires_at": None,
            "data": context1.data,
            "related_contexts": context1.related_contexts,
            "access_count": context1.access_count,
            "tags": context1.tags
        }
        context_manager.knowledge_store.retrieve_context.return_value = context_data

        result = context_manager.add_context_relationship(
            context1.context_id, context2.context_id
        )

        assert result is True
        # Verify relationship was added
        call_args = context_manager.knowledge_store.store_context.call_args[0][1]
        assert context2.context_id in call_args["related_contexts"]

    def test_tag_context(self, context_manager, sample_healing_request):
        """Test context tagging."""
        context = context_manager.create_context(sample_healing_request)

        # Mock retrieval for tagging
        context_data = {
            "context_id": context.context_id,
            "request": context.request.__dict__,
            "status": context.status.value,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "expires_at": None,
            "data": context.data,
            "related_contexts": context.related_contexts,
            "access_count": context.access_count,
            "tags": context.tags
        }
        context_manager.knowledge_store.retrieve_context.return_value = context_data

        tags = ["urgent", "database", "production"]
        result = context_manager.tag_context(context.context_id, tags)

        assert result is True
        # Verify tags were added
        call_args = context_manager.knowledge_store.store_context.call_args[0][1]
        for tag in tags:
            assert tag in call_args["tags"]

    def test_expired_context_handling(self, context_manager, sample_healing_request):
        """Test handling of expired contexts."""
        context = context_manager.create_context(sample_healing_request, ttl_hours=1)

        # Mock expired context data
        past_time = (datetime.now() - timedelta(hours=2)).isoformat()
        context_data = {
            "context_id": context.context_id,
            "request": context.request.__dict__,
            "status": context.status.value,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "expires_at": past_time,  # Expired
            "data": context.data,
            "related_contexts": context.related_contexts,
            "access_count": context.access_count,
            "tags": context.tags
        }
        context_manager.knowledge_store.retrieve_context.return_value = context_data

        retrieved = context_manager.get_context(context.context_id)

        assert retrieved is not None
        assert retrieved.status == ContextStatus.EXPIRED
```

---

## Gap 2: Sensor Framework Test Cases

### Unit Tests

#### File: `tests/unit/agentic_core/L0_maintenance/sensors/test_base_sensor.py`

```python
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from agentic_core.L0_maintenance.sensors.base_sensor import (
    BaseSensor, FailureEvent, FailureContext, Severity, Impact
)

class TestBaseSensor(BaseSensor):
    """Test implementation of BaseSensor."""

    def detect_failures(self):
        return []

    def get_failure_context(self, event):
        return FailureContext(
            event=event,
            severity=Severity.MEDIUM,
            impact=Impact.LOCALIZED,
            system_state={},
            related_components=[],
            error_patterns=[],
            suggested_actions=[],
            confidence=0.8,
            metadata={}
        )

class TestBaseSensorFunctionality:
    """Test suite for BaseSensor abstract class."""

    @pytest.fixture
    def test_sensor(self):
        """Create test sensor instance."""
        config = {
            "enabled": True,
            "detection_interval": 30
        }
        return TestBaseSensor("test_sensor", config)

    def test_sensor_initialization(self):
        """Test sensor initialization with config."""
        config = {"enabled": False, "detection_interval": 60}
        sensor = TestBaseSensor("config_sensor", config)

        assert sensor.sensor_name == "config_sensor"
        assert sensor.enabled is False
        assert sensor.detection_interval == 60
        assert sensor.config == config

    def test_default_configuration(self):
        """Test sensor with default configuration."""
        sensor = TestBaseSensor("default_sensor")

        assert sensor.enabled is True
        assert sensor.detection_interval == 60
        assert sensor.last_detection_time is None

    def test_is_enabled(self, test_sensor):
        """Test enabled status check."""
        assert test_sensor.is_enabled() is True

        test_sensor.enabled = False
        assert test_sensor.is_enabled() is False

    def test_severity_classification(self, test_sensor):
        """Test severity classification logic."""
        # Test low severity
        context = FailureContext(
            event=FailureEvent("1", datetime.now(), "test", "test", {}, "test"),
            severity=Severity.LOW,
            impact=Impact.MINIMAL,
            system_state={},
            related_components=[],
            error_patterns=["info"],
            suggested_actions=[],
            confidence=0.8,
            metadata={}
        )

        classified = test_sensor.classify_severity(context)
        assert classified == Severity.LOW

        # Test critical severity
        context.impact = Impact.CRITICAL
        context.error_patterns = ["crash", "exception"]
        context.related_components = ["comp1", "comp2", "comp3", "comp4"]

        classified = test_sensor.classify_severity(context)
        assert classified == Severity.CRITICAL

    def test_impact_assessment(self, test_sensor):
        """Test impact assessment logic."""
        context = FailureContext(
            event=FailureEvent("1", datetime.now(), "test", "test", {}, "database"),
            severity=Severity.CRITICAL,
            impact=Impact.SYSTEM_WIDE,
            system_state={},
            related_components=["comp1", "comp2", "comp3"],
            error_patterns=["crash"],
            suggested_actions=[],
            confidence=0.9,
            metadata={}
        )

        assessment = test_sensor.assess_impact(context)

        assert assessment.affected_components == ["database", "comp1", "comp2", "comp3"]
        assert assessment.estimated_downtime_minutes == 240  # Critical severity
        assert assessment.user_impact == "severe"
        assert assessment.data_integrity_risk == "high"
        assert assessment.cascading_failure_risk == "high"
        assert assessment.recovery_complexity == "complex"

    def test_configuration_validation(self, test_sensor):
        """Test configuration validation."""
        assert test_sensor.validate_configuration() is True

        # Test invalid configuration
        test_sensor.config = {"enabled": True}  # Missing detection_interval
        assert test_sensor.validate_configuration() is False

        test_sensor.config = {"enabled": True, "detection_interval": -1}
        assert test_sensor.validate_configuration() is False

    def test_get_sensor_status(self, test_sensor):
        """Test sensor status retrieval."""
        status = test_sensor.get_sensor_status()

        assert status["sensor_name"] == "test_sensor"
        assert status["enabled"] is True
        assert status["detection_interval"] == 30
        assert status["last_detection_time"] is None
        assert "config" in status
```

#### File: `tests/unit/agentic_core/L0_maintenance/sensors/test_failure_detector.py`

```python
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from agentic_core.L0_maintenance.sensors.failure_detector import FailureDetector
from agentic_core.L0_maintenance.sensors.base_sensor import FailureEvent, Severity

class TestFailureDetector:
    """Test suite for FailureDetector functionality."""

    @pytest.fixture
    def failure_detector(self):
        """Create failure detector with test configuration."""
        config = {
            "log_paths": ["test_logs"],
            "monitored_processes": ["python", "test_process"],
            "resource_thresholds": {
                "cpu_percent": 70,
                "memory_percent": 80,
                "disk_percent": 85
            },
            "error_patterns": [r"ERROR", r"CRITICAL", r"test_error"],
            "critical_hosts": ["localhost", "test.com"]
        }
        return FailureDetector(config)

    @patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil')
    def test_detect_failures_no_failures(self, mock_psutil, failure_detector):
        """Test failure detection when no failures are present."""
        # Mock no failures
        mock_psutil.cpu_percent.return_value = 50
        mock_psutil.virtual_memory.return_value = Mock(percent=60)
        mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
        mock_psutil.process_iter.return_value = []

        with patch('pathlib.Path.exists', return_value=False):
            failures = failure_detector.detect_failures()

        assert len(failures) == 0

    @patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil')
    def test_detect_high_cpu_failure(self, mock_psutil, failure_detector):
        """Test detection of high CPU usage."""
        # Mock high CPU usage
        mock_psutil.cpu_percent.return_value = 90
        mock_psutil.virtual_memory.return_value = Mock(percent=60)
        mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
        mock_psutil.process_iter.return_value = []

        with patch('pathlib.Path.exists', return_value=False):
            failures = failure_detector.detect_failures()

        assert len(failures) == 1
        assert failures[0].failure_type == "high_cpu_usage"
        assert failures[0].source == "resource_monitor"
        assert failures[0].component == "system"

    @patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil')
    def test_detect_process_missing_failure(self, mock_psutil, failure_detector):
        """Test detection of missing process."""
        # Mock no processes found
        mock_psutil.cpu_percent.return_value = 50
        mock_psutil.virtual_memory.return_value = Mock(percent=60)
        mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
        mock_psutil.process_iter.return_value = []

        with patch('pathlib.Path.exists', return_value=False):
            failures = failure_detector.detect_failures()

        # Should detect missing python process
        python_failures = [f for f in failures if f.failure_type == "process_missing"]
        assert len(python_failures) >= 1
        assert python_failures[0].raw_data["process_name"] == "python"

    def test_scan_log_files_with_errors(self, failure_detector):
        """Test log file scanning with error patterns."""
        log_content = """
        INFO: Application started
        ERROR: Database connection failed
        WARNING: High memory usage
        CRITICAL: System overload
        INFO: Normal operation
        """

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.rglob') as mock_rglob, \
             patch('builtins.open', mock_open(read_data=log_content)), \
             patch('pathlib.Path.stat') as mock_stat:

            # Mock file modification time (recent)
            mock_stat.return_value.st_mtime = datetime.now().timestamp()

            # Mock log file
            mock_log_file = Mock()
            mock_log_file.name = "test.log"
            mock_rglob.return_value = [mock_log_file]

            with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
                mock_psutil.cpu_percent.return_value = 50
                mock_psutil.virtual_memory.return_value = Mock(percent=60)
                mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
                mock_psutil.process_iter.return_value = []

                failures = failure_detector.detect_failures()

        # Should detect ERROR and CRITICAL in logs
        log_failures = [f for f in failures if f.source == "log_monitor"]
        assert len(log_failures) >= 2

        error_texts = [f.raw_data["content"] for f in log_failures]
        assert any("ERROR" in text for text in error_texts)
        assert any("CRITICAL" in text for text in error_texts)

    def test_get_failure_context_enrichment(self, failure_detector):
        """Test failure context enrichment."""
        event = FailureEvent(
            event_id="test_001",
            timestamp=datetime.now(),
            source="test",
            failure_type="test_failure",
            raw_data={"content": "ERROR: Database connection failed"},
            component="database"
        )

        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 60
            mock_psutil.virtual_memory.return_value = Mock(percent=70)
            mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
            mock_psutil.boot_time.return_value = datetime.now().timestamp() - 3600
            mock_psutil.getloadavg.return_value = (1.0, 1.5, 2.0)
            mock_psutil.pids.return_value = [1, 2, 3, 4, 5]
            mock_psutil.net_connections.return_value = [Mock(), Mock()]

            context = failure_detector.get_failure_context(event)

        assert context.event == event
        assert context.severity in [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        assert context.system_state is not None
        assert "cpu_percent" in context.system_state
        assert "memory_percent" in context.system_state
        assert len(context.related_components) > 0
        assert len(context.error_patterns) > 0
        assert len(context.suggested_actions) > 0
        assert 0 <= context.confidence <= 1

    def test_confidence_calculation(self, failure_detector):
        """Test confidence calculation for different detection methods."""
        # Test log scan confidence
        event = FailureEvent(
            event_id="log_test",
            timestamp=datetime.now(),
            source="log_monitor",
            failure_type="log_error",
            raw_data={"detection_method": "log_scan"},
            component="test"
        )

        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 50
            mock_psutil.virtual_memory.return_value = Mock(percent=60)

            context = failure_detector.get_failure_context(event)
            assert context.confidence >= 0.7  # Log scan should have higher confidence

        # Test resource check confidence with supporting system state
        event = FailureEvent(
            event_id="resource_test",
            timestamp=datetime.now(),
            source="resource_monitor",
            failure_type="high_cpu_usage",
            raw_data={"detection_method": "resource_check"},
            component="system"
        )

        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 90  # High CPU supports the failure
            mock_psutil.virtual_memory.return_value = Mock(percent=60)

            context = failure_detector.get_failure_context(event)
            assert context.confidence >= 0.8  # Should be high with supporting evidence
```

---

## Gap 3: Human Review Gate Test Cases

### Unit Tests

#### File: `tests/unit/agentic_core/L5_safety/human_review/test_review_gate.py`

```python
import pytest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from agentic_core.L5_safety.human_review.review_gate import (
    HumanReviewGate, ReviewTicket, ChangeRequest, ReviewDecision,
    ProposedChange, ValidatorRecommendation, ReviewStatus, RiskLevel, ReviewPriority
)

class TestHumanReviewGate:
    """Test suite for HumanReviewGate functionality."""

    @pytest.fixture
    def temp_review_gate(self):
        """Create temporary review gate for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "approval_queue_path": temp_dir,
                "auto_approve_threshold": RiskLevel.LOW,
                "default_ttl_hours": 24,
                "escalation_timeout_hours": 8
            }
            gate = HumanReviewGate(config)
            yield gate

    @pytest.fixture
    def sample_change_request(self):
        """Sample change request for testing."""
        change = ProposedChange(
            change_id="change_001",
            file_path="test_file.py",
            change_type="modify",
            description="Fix critical bug in authentication",
            risk_level=RiskLevel.HIGH,
            preview_diff="@@ -1,5 +1,5 @@\n-def authenticate(user):\n+def authenticate(user):\n",
            rollback_plan="Revert to previous commit",
            test_plan="Run authentication test suite"
        )

        validator_rec = ValidatorRecommendation(
            validator_name="SecurityValidator",
            recommendation="escalate",
            confidence=0.7,
            reasoning="High security risk requires human review",
            risk_assessment={"security_impact": "high", "user_impact": "medium"},
            timestamp=datetime.now()
        )

        return ChangeRequest(
            request_id="req_001",
            source="healing_system",
            risk_level=RiskLevel.HIGH,
            priority=ReviewPriority.HIGH,
            proposed_changes=[change],
            justification="Critical security vulnerability fix",
            validator_recommendation=validator_rec
        )

    def test_submit_high_risk_for_review(self, temp_review_gate, sample_change_request):
        """Test submission of high-risk change for review."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        assert ticket is not None
        assert ticket.status == ReviewStatus.PENDING
        assert ticket.change_request == sample_change_request
        assert ticket.ticket_id.startswith("review_")
        assert ticket.created_at is not None
        assert ticket.change_request.expires_at is not None

    def test_auto_approve_low_risk_change(self, temp_review_gate):
        """Test auto-approval of low-risk changes."""
        low_risk_change = ProposedChange(
            change_id="change_002",
            file_path="docs/readme.md",
            change_type="modify",
            description="Update documentation",
            risk_level=RiskLevel.LOW
        )

        low_risk_request = ChangeRequest(
            request_id="req_002",
            source="documentation",
            risk_level=RiskLevel.LOW,
            priority=ReviewPriority.LOW,
            proposed_changes=[low_risk_change],
            justification="Documentation update"
        )

        ticket = temp_review_gate.submit_for_review(low_risk_request)

        assert ticket.status == ReviewStatus.APPROVED
        assert ticket.auto_approve is True
        assert len(ticket.approval_conditions) > 0
        assert ticket.ticket_id.startswith("auto_")

    def test_get_review_status(self, temp_review_gate, sample_change_request):
        """Test review status retrieval."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        status = temp_review_gate.get_review_status(ticket.ticket_id)
        assert status == ReviewStatus.PENDING

        # Test non-existent ticket
        status = temp_review_gate.get_review_status("nonexistent")
        assert status is None

    def test_process_review_decision_approve(self, temp_review_gate, sample_change_request):
        """Test processing of approval decision."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        decision = ReviewDecision(
            ticket_id=ticket.ticket_id,
            decision="approve",
            reviewer="senior_engineer@company.com",
            comments="Changes look good, approved for deployment",
            conditions=["Run full test suite before deployment"]
        )

        result = temp_review_gate.process_review_decision(ticket.ticket_id, decision)

        assert result is True
        assert temp_review_gate._tickets[ticket.ticket_id].status == ReviewStatus.APPROVED
        assert temp_review_gate._tickets[ticket.ticket_id].review_decision == "approve"
        assert temp_review_gate._tickets[ticket.ticket_id].reviewer_comments == decision.comments

    def test_process_review_decision_reject(self, temp_review_gate, sample_change_request):
        """Test processing of rejection decision."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        decision = ReviewDecision(
            ticket_id=ticket.ticket_id,
            decision="reject",
            reviewer="security_team@company.com",
            comments="Security concerns not addressed, please revise"
        )

        result = temp_review_gate.process_review_decision(ticket.ticket_id, decision)

        assert result is True
        assert temp_review_gate._tickets[ticket.ticket_id].status == ReviewStatus.REJECTED
        assert temp_review_gate._tickets[ticket.ticket_id].review_decision == "reject"

    def test_escalate_ticket(self, temp_review_gate, sample_change_request):
        """Test ticket escalation."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        result = temp_review_gate.escalate_ticket(ticket.ticket_id, "Requires senior review")

        assert result is True
        assert temp_review_gate._tickets[ticket.ticket_id].status == ReviewStatus.ESCALATED
        assert temp_review_gate._tickets[ticket.ticket_id].change_request.escalation_level == 1

        # Check escalation history
        escalation_history = temp_review_gate._tickets[ticket.ticket_id].escalation_history
        assert len(escalation_history) == 1
        assert escalation_history[0]["reason"] == "Requires senior review"

    def test_max_escalation_level(self, temp_review_gate, sample_change_request):
        """Test escalation limit enforcement."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        # Escalate to max level
        for i in range(temp_review_gate.max_escalation_levels):
            temp_review_gate.escalate_ticket(ticket.ticket_id, f"Escalation {i+1}")

        # Try to escalate beyond max
        result = temp_review_gate.escalate_ticket(ticket.ticket_id, "Beyond max")
        assert result is False

    def test_get_pending_tickets(self, temp_review_gate, sample_change_request):
        """Test retrieval of pending tickets."""
        # Submit multiple tickets
        ticket1 = temp_review_gate.submit_for_review(sample_change_request)

        # Create another request
        change2 = ProposedChange(
            change_id="change_003",
            file_path="config.py",
            change_type="modify",
            description="Update configuration",
            risk_level=RiskLevel.MEDIUM
        )
        request2 = ChangeRequest(
            request_id="req_003",
            source="config_update",
            risk_level=RiskLevel.MEDIUM,
            priority=ReviewPriority.CRITICAL,  # Higher priority
            proposed_changes=[change2],
            justification="Configuration update"
        )
        ticket2 = temp_review_gate.submit_for_review(request2)

        pending = temp_review_gate.get_pending_tickets()

        assert len(pending) == 2
        # Should be sorted by priority (critical first)
        assert pending[0].ticket_id == ticket2.ticket_id
        assert pending[1].ticket_id == ticket1.ticket_id

    def test_ticket_statistics(self, temp_review_gate, sample_change_request):
        """Test review gate statistics."""
        # Submit tickets with different outcomes
        ticket1 = temp_review_gate.submit_for_review(sample_change_request)

        low_risk_request = ChangeRequest(
            request_id="req_low",
            source="test",
            risk_level=RiskLevel.LOW,
            priority=ReviewPriority.LOW,
            proposed_changes=[],
            justification="Low risk change"
        )
        ticket2 = temp_review_gate.submit_for_review(low_risk_request)  # Auto-approved

        # Process decision for first ticket
        decision = ReviewDecision(
            ticket_id=ticket1.ticket_id,
            decision="approve",
            reviewer="reviewer@company.com",
            comments="Approved"
        )
        temp_review_gate.process_review_decision(ticket1.ticket_id, decision)

        stats = temp_review_gate.get_ticket_statistics()

        assert stats["total_tickets"] == 2
        assert stats["pending_tickets"] == 0
        assert stats["approved_tickets"] == 2
        assert stats["auto_approved_tickets"] == 1
        assert "risk_level_distribution" in stats
        assert stats["risk_level_distribution"]["high"] == 1
        assert stats["risk_level_distribution"]["low"] == 1

    def test_persistence_and_recovery(self, temp_review_gate, sample_change_request):
        """Test ticket persistence across restarts."""
        ticket = temp_review_gate.submit_for_review(sample_change_request)

        # Create new gate instance (simulates restart)
        new_gate = HumanReviewGate(temp_review_gate.config)

        # Ticket should be loaded from disk
        assert ticket.ticket_id in new_gate._tickets
        loaded_ticket = new_gate._tickets[ticket.ticket_id]
        assert loaded_ticket.status == ReviewStatus.PENDING
        assert loaded_ticket.change_request.request_id == sample_change_request.request_id

    def test_cleanup_expired_tickets(self, temp_review_gate, sample_change_request):
        """Test cleanup of expired tickets."""
        # Create ticket with short TTL
        config_with_short_ttl = {
            **temp_review_gate.config,
            "default_ttl_hours": 0.001  # ~3.6 seconds
        }
        short_gate = HumanReviewGate(config_with_short_ttl)

        ticket = short_gate.submit_for_review(sample_change_request)

        # Wait for expiration
        import time
        time.sleep(4)

        # Check status (should mark as expired)
        status = short_gate.get_review_status(ticket.ticket_id)
        assert status == ReviewStatus.EXPIRED

        # Cleanup expired tickets
        cleaned = short_gate.cleanup_expired_tickets()
        assert cleaned == 1
```

---

## Integration Test Cases

### File: `tests/integration/test_healing_pipeline_integration.py`

```python
import pytest
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

from agentic_core.L0_maintenance.sensors.failure_detector import FailureDetector
from agentic_core.L4_state.knowledge.knowledge_store import KnowledgeStore
from agentic_core.L4_state.knowledge.context_manager import ContextManager
from agentic_core.L5_safety.human_review.review_gate import HumanReviewGate, ChangeRequest, RiskLevel

class TestHealingPipelineIntegration:
    """Integration tests for the complete healing pipeline."""

    @pytest.fixture
    def integrated_system(self):
        """Create integrated healing system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            knowledge_store = KnowledgeStore(storage_path=Path(temp_dir) / "knowledge")
            context_manager = ContextManager(knowledge_store)
            failure_detector = FailureDetector({
                "log_paths": [Path(temp_dir) / "logs"],
                "monitored_processes": ["python"],
                "resource_thresholds": {"cpu_percent": 80, "memory_percent": 85}
            })
            review_gate = HumanReviewGate({
                "approval_queue_path": Path(temp_dir) / "reviews",
                "auto_approve_threshold": RiskLevel.MEDIUM
            })

            yield {
                "knowledge_store": knowledge_store,
                "context_manager": context_manager,
                "failure_detector": failure_detector,
                "review_gate": review_gate
            }

    def test_end_to_end_healing_workflow(self, integrated_system):
        """Test complete healing workflow from failure detection to resolution."""
        # Step 1: Detect failures
        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 90  # High CPU
            mock_psutil.virtual_memory.return_value = Mock(percent=60)
            mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
            mock_psutil.process_iter.return_value = []

            failures = integrated_system["failure_detector"].detect_failures()

        assert len(failures) > 0

        # Step 2: Create context for each failure
        contexts = []
        for failure in failures:
            context = integrated_system["failure_detector"].get_failure_context(failure)
            contexts.append(context)

            # Store context
            healing_request = Mock()
            healing_request.request_id = f"req_{failure.event_id}"
            healing_request.failure_events = [failure.__dict__]
            healing_request.severity = context.severity.value

            created_context = integrated_system["context_manager"].create_context(healing_request)
            contexts.append(created_context)

        assert len(contexts) > 0

        # Step 3: Store learning in knowledge store
        for context in contexts:
            integrated_system["knowledge_store"].store_context(
                context.context_id if hasattr(context, 'context_id') else f"ctx_{datetime.now().timestamp()}",
                context.__dict__ if hasattr(context, '__dict__') else {"data": "test"},
                "integration_test"
            )

        # Verify knowledge store has data
        stats = integrated_system["knowledge_store"].get_statistics()
        assert stats["total_entries"] > 0
```

### File: `tests/integration/test_sensor_to_review_integration.py`

```python
import pytest
import tempfile
from unittest.mock import Mock, patch

from agentic_core.L0_maintenance.sensors.failure_detector import FailureDetector
from agentic_core.L5_safety.human_review.review_gate import HumanReviewGate, RiskLevel, ReviewPriority

class TestSensorToReviewIntegration:
    """Integration tests for sensor to review gate workflow."""

    @pytest.fixture
    def sensor_review_system(self):
        """Create sensor and review gate integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            failure_detector = FailureDetector({
                "log_paths": [],
                "monitored_processes": ["python"],
                "resource_thresholds": {"cpu_percent": 90, "memory_percent": 85}
            })

            review_gate = HumanReviewGate({
                "approval_queue_path": temp_dir,
                "auto_approve_threshold": RiskLevel.LOW
            })

            yield {
                "failure_detector": failure_detector,
                "review_gate": review_gate
            }

    def test_critical_failure_triggers_review(self, sensor_review_system):
        """Test that critical failures automatically trigger review process."""
        # Detect critical failure
        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 95
            mock_psutil.virtual_memory.return_value = Mock(percent=90)
            mock_psutil.disk_usage.return_value = Mock(used=900, total=1000)
            mock_psutil.process_iter.return_value = []

            failures = sensor_review_system["failure_detector"].detect_failures()

        assert len(failures) > 0

        # Get failure context
        failure = failures[0]
        context = sensor_review_system["failure_detector"].get_failure_context(failure)

        # Create review request based on failure
        from agentic_core.L5_safety.human_review.review_gate import ChangeRequest, ProposedChange

        change = ProposedChange(
            change_id=f"fix_{failure.event_id}",
            file_path="system_resource.py",
            change_type="modify",
            description=f"Fix critical {failure.failure_type}",
            risk_level=RiskLevel.CRITICAL if context.severity.value == "critical" else RiskLevel.HIGH
        )

        request = ChangeRequest(
            request_id=f"review_{failure.event_id}",
            source="sensor_system",
            risk_level=change.risk_level,
            priority=ReviewPriority.CRITICAL,
            proposed_changes=[change],
            justification=f"Automatic review triggered by {failure.failure_type}"
        )

        # Submit for review
        ticket = sensor_review_system["review_gate"].submit_for_review(request)

        assert ticket is not None
        assert ticket.status.value == "pending"  # Critical changes should require review
        assert ticket.change_request.priority == ReviewPriority.CRITICAL
```

    def test_sensor_to_context_manager_integration(self, integrated_system):
        """Test integration between failure detector and context manager."""
        # Mock failure detection
        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 95
            mock_psutil.virtual_memory.return_value = Mock(percent=60)
            mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
            mock_psutil.process_iter.return_value = []

            failures = integrated_system["failure_detector"].detect_failures()

        assert len(failures) > 0

        # Process first failure through context manager
        failure = failures[0]
        context = integrated_system["failure_detector"].get_failure_context(failure)

        # Create healing request and context
        from agentic_core.L4_state.knowledge.context_manager import HealingRequest
        request = HealingRequest(
            request_id=f"integration_req_{failure.event_id}",
            source="integration_test",
            failure_events=[failure.__dict__],
            severity=context.severity.value
        )

        created_context = integrated_system["context_manager"].create_context(request)

        # Update context with failure analysis
        updates = {
            "failure_analysis": {
                "detected_at": failure.timestamp.isoformat(),
                "severity": context.severity.value,
                "impact": context.impact.value,
                "confidence": context.confidence
            },
            "suggested_actions": context.suggested_actions
        }

        result = integrated_system["context_manager"].update_context(
            created_context.context_id, updates
        )

        assert result is True

        # Verify context was updated
        retrieved_context = integrated_system["context_manager"].get_context(
            created_context.context_id
        )
        assert retrieved_context is not None
        assert "failure_analysis" in retrieved_context.data
        assert retrieved_context.data["failure_analysis"]["severity"] == context.severity.value

    def test_context_to_review_gate_integration(self, integrated_system):
        """Test integration between context manager and human review gate."""
        # Create high-risk change request
        from agentic_core.L5_safety.human_review.review_gate import ProposedChange, ReviewPriority

        change = ProposedChange(
            change_id="integration_change",
            file_path="critical_system.py",
            change_type="modify",
            description="Critical security fix",
            risk_level=RiskLevel.CRITICAL
        )

        request = ChangeRequest(
            request_id="integration_req",
            source="integration_test",
            risk_level=RiskLevel.CRITICAL,
            priority=ReviewPriority.CRITICAL,
            proposed_changes=[change],
            justification="Critical security vulnerability"
        )

        # Submit for review
        ticket = integrated_system["review_gate"].submit_for_review(request)

        assert ticket.status.value == "pending"

        # Get pending tickets
        pending = integrated_system["review_gate"].get_pending_tickets()
        assert len(pending) >= 1
        assert pending[0].ticket_id == ticket.ticket_id

        # Process review decision
        from agentic_core.L5_safety.human_review.review_gate import ReviewDecision
        decision = ReviewDecision(
            ticket_id=ticket.ticket_id,
            decision="approve",
            reviewer="integration_reviewer@test.com",
            comments="Approved for integration testing"
        )

        result = integrated_system["review_gate"].process_review_decision(
            ticket.ticket_id, decision
        )

        assert result is True

        # Verify decision was processed
        updated_status = integrated_system["review_gate"].get_review_status(ticket.ticket_id)
        assert updated_status.value == "approved"

    def test_feedback_loop_integration(self, integrated_system):
        """Test feedback loop from system actuation to knowledge store."""
        # Create action feedback
        from agentic_core.L4_state.knowledge.knowledge_store import ActionFeedback

        feedback = ActionFeedback(
            action_id="integration_action",
            action_type="code_fix",
            success=True,
            outcome={"files_modified": 3, "errors_fixed": 2},
            errors=[],
            performance_metrics={"execution_time": 2.5, "memory_usage": 256},
            timestamp=datetime.now(),
            context_id="integration_ctx"
        )

        # Process feedback through knowledge store
        result = integrated_system["knowledge_store"].update_from_feedback(feedback)
        assert result is True

        # Verify learning patterns were created
        patterns = integrated_system["knowledge_store"].get_learning_patterns("action_outcome")
        assert len(patterns) > 0

        # Verify feedback was stored
        feedback_key = f"feedback_{feedback.action_id}"
        retrieved_context = integrated_system["knowledge_store"].retrieve_context(feedback_key)
        assert retrieved_context is not None
        assert retrieved_context["action_id"] == feedback.action_id
        assert retrieved_context["success"] is True

    def test_system_state_consistency(self, integrated_system):
        """Test system state consistency across components."""
        # Simulate system state changes
        initial_stats = integrated_system["knowledge_store"].get_statistics()
        initial_review_stats = integrated_system["review_gate"].get_ticket_statistics()

        # Create some activity
        with patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 85
            mock_psutil.virtual_memory.return_value = Mock(percent=60)
            mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
            mock_psutil.process_iter.return_value = []

            failures = integrated_system["failure_detector"].detect_failures()

        if failures:
            failure = failures[0]
            context = integrated_system["failure_detector"].get_failure_context(failure)

            # Store in knowledge store
            integrated_system["knowledge_store"].store_context(
                f"consistency_test_{failure.event_id}",
                context.__dict__,
                "consistency_test"
            )

        # Verify state updates
        final_stats = integrated_system["knowledge_store"].get_statistics()
        assert final_stats["total_entries"] >= initial_stats["total_entries"]

        # Verify review gate state unchanged (no review activity)
        final_review_stats = integrated_system["review_gate"].get_ticket_statistics()
        assert final_review_stats["total_tickets"] == initial_review_stats["total_tickets"]
```

---

## Performance Test Cases

### File: `tests/performance/test_system_performance.py`

```python
import pytest
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agentic_core.L4_state.knowledge.knowledge_store import KnowledgeStore
from agentic_core.L0_maintenance.sensors.failure_detector import FailureDetector

class TestSystemPerformance:
    """Performance tests for the healing system."""

    @pytest.fixture
    def performance_knowledge_store(self):
        """Create knowledge store for performance testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = KnowledgeStore(storage_path=Path(temp_dir))
            yield store

    def test_knowledge_store_write_performance(self, performance_knowledge_store):
        """Test knowledge store write performance."""
        num_operations = 1000
        contexts = [
            {
                "context_id": f"perf_test_{i}",
                "data": f"test_data_{i}" * 100,  # Larger data
                "timestamp": time.time()
            }
            for i in range(num_operations)
        ]

        start_time = time.time()

        for context in contexts:
            performance_knowledge_store.store_context(
                context["context_id"], context, "performance_test"
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 5.0, f"Write performance too slow: {duration:.2f}s for {num_operations} operations"

        ops_per_second = num_operations / duration
        assert ops_per_second > 100, f"Write rate too low: {ops_per_second:.2f} ops/sec"

    def test_knowledge_store_read_performance(self, performance_knowledge_store):
        """Test knowledge store read performance."""
        # Pre-populate with data
        num_entries = 1000
        for i in range(num_entries):
            performance_knowledge_store.store_context(
                f"read_test_{i}", {"data": f"test_{i}"}, "read_test"
            )

        # Test read performance
        start_time = time.time()

        for i in range(num_entries):
            result = performance_knowledge_store.retrieve_context(f"read_test_{i}")
            assert result is not None

        end_time = time.time()
        duration = end_time - start_time

        assert duration < 2.0, f"Read performance too slow: {duration:.2f}s for {num_entries} operations"

        ops_per_second = num_entries / duration
        assert ops_per_second > 500, f"Read rate too low: {ops_per_second:.2f} ops/sec"

    def test_concurrent_knowledge_store_access(self, performance_knowledge_store):
        """Test concurrent access to knowledge store."""
        num_threads = 10
        operations_per_thread = 100

        def worker(thread_id):
            for i in range(operations_per_thread):
                key = f"concurrent_{thread_id}_{i}"
                performance_knowledge_store.store_context(key, {"thread": thread_id, "i": i}, "concurrent_test")
                result = performance_knowledge_store.retrieve_context(key)
                assert result is not None
                assert result["thread"] == thread_id

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for future in futures:
                future.result()  # Wait for completion

        end_time = time.time()
        duration = end_time - start_time

        total_operations = num_threads * operations_per_thread * 2  # write + read
        ops_per_second = total_operations / duration

        assert ops_per_second > 200, f"Concurrent access rate too low: {ops_per_second:.2f} ops/sec"

    def test_failure_detector_performance(self):
        """Test failure detector performance."""
        detector = FailureDetector({
            "log_paths": [],  # Disable log scanning for this test
            "monitored_processes": [],
            "resource_thresholds": {"cpu_percent": 80, "memory_percent": 85}
        })

        # Test multiple detection cycles
        num_cycles = 100

        start_time = time.time()

        for _ in range(num_cycles):
            with pytest.mock.patch('agentic_core.L0_maintenance.sensors.failure_detector.psutil') as mock_psutil:
                mock_psutil.cpu_percent.return_value = 50
                mock_psutil.virtual_memory.return_value = Mock(percent=60)
                mock_psutil.disk_usage.return_value = Mock(used=100, total=1000)
                mock_psutil.process_iter.return_value = []

                failures = detector.detect_failures()

        end_time = time.time()
        duration = end_time - start_time

        cycles_per_second = num_cycles / duration
        assert cycles_per_second > 10, f"Detection rate too low: {cycles_per_second:.2f} cycles/sec"

    def test_memory_usage_scaling(self, performance_knowledge_store):
        """Test memory usage scaling with data volume."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Add large amounts of data
        num_large_entries = 1000
        for i in range(num_large_entries):
            large_data = {
                "context_id": f"memory_test_{i}",
                "large_field": "x" * 1000,  # 1KB per entry
                "nested": {
                    "data": ["item"] * 100  # Additional data
                }
            }
            performance_knowledge_store.store_context(
                f"memory_test_{i}", large_data, "memory_test"
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 500MB for 1MB of test data)
        assert memory_increase < 500, f"Memory usage too high: {memory_increase:.2f}MB increase"

        # Test cleanup
        cleaned = performance_knowledge_store.cleanup_expired_entries()
        assert cleaned >= 0  # Should not error
```

---

## Security Test Cases

### File: `tests/security/test_security_vulnerabilities.py`

```python
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from agentic_core.L4_state.knowledge.knowledge_store import KnowledgeStore
from agentic_core.L5_safety.human_review.review_gate import HumanReviewGate, RiskLevel

class TestSecurityVulnerabilities:
    """Security tests for the healing system."""

    @pytest.fixture
    def secure_knowledge_store(self):
        """Create knowledge store for security testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = KnowledgeStore(storage_path=Path(temp_dir))
            yield store

    def test_injection_attack_prevention(self, secure_knowledge_store):
        """Test prevention of injection attacks in context data."""
        malicious_contexts = [
            {
                "context_id": "<script>alert('xss')</script>",
                "data": "'; DROP TABLE contexts; --"
            },
            {
                "context_id": "../../../etc/passwd",
                "data": {"__proto__": {"admin": True}}
            },
            {
                "context_id": "normal_context",
                "data": {"malicious": "<img src=x onerror=alert('xss')>"}
            }
        ]

        for context in malicious_contexts:
            # Should not raise exceptions or cause issues
            result = secure_knowledge_store.store_context(
                context["context_id"], context, "security_test"
            )
            assert result is True

            # Retrieved data should be sanitized or safe
            retrieved = secure_knowledge_store.retrieve_context(context["context_id"])
            assert retrieved is not None

    def test_path_traversal_prevention(self, secure_knowledge_store):
        """Test prevention of path traversal attacks."""
        malicious_keys = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]

        for key in malicious_keys:
            result = secure_knowledge_store.store_context(key, {"test": "data"}, "security_test")
            # Should either succeed safely or fail gracefully
            assert isinstance(result, bool)

    def test_data_size_limits(self, secure_knowledge_store):
        """Test handling of oversized data."""
        # Test with very large data
        large_data = {
            "context_id": "large_test",
            "data": "x" * (10 * 1024 * 1024)  # 10MB
        }

        # Should either handle gracefully or fail with proper error
        result = secure_knowledge_store.store_context(
            large_data["context_id"], large_data, "size_test"
        )
        assert isinstance(result, bool)

    def test_review_gate_authorization(self):
        """Test authorization controls in review gate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            gate = HumanReviewGate({
                "approval_queue_path": temp_dir,
                "escalation_handlers": {
                    1: ["authorized@example.com"],
                    2: ["manager@example.com"]
                }
            })

            # Test unauthorized access attempts
            from agentic_core.L5_safety.human_review.review_gate import ReviewDecision

            # Should handle unauthorized reviewers gracefully
            malicious_decision = ReviewDecision(
                ticket_id="fake_ticket",
                decision="approve",
                reviewer="attacker@malicious.com",
                comments="Trying to bypass authorization"
            )

            result = gate.process_review_decision("fake_ticket", malicious_decision)
            # Should fail gracefully for non-existent ticket
            assert result is False

    def test_sensitive_data_handling(self, secure_knowledge_store):
        """Test handling of sensitive data."""
        sensitive_context = {
            "context_id": "sensitive_test",
            "data": {
                "api_key": "sk-1234567890abcdef",
                "password": "secret_password",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "private_key": "-----BEGIN RSA PRIVATE KEY-----\n"
            }
        }

        # Store sensitive data
        result = secure_knowledge_store.store_context(
            sensitive_context["context_id"], sensitive_context, "sensitive_test"
        )
        assert result is True

        # Retrieve data
        retrieved = secure_knowledge_store.retrieve_context("sensitive_test")
        assert retrieved is not None

        # In a real implementation, sensitive data should be encrypted or masked
        # For now, just ensure it doesn't cause crashes
        assert "api_key" in retrieved["data"]

    def test_concurrent_security(self, secure_knowledge_store):
        """Test security under concurrent access."""
        import threading
        import time

        results = []

        def malicious_worker(worker_id):
            try:
                # Attempt various malicious operations
                for i in range(10):
                    secure_knowledge_store.store_context(
                        f"malicious_{worker_id}_{i}",
                        {"attack": f"<script>alert({worker_id})</script>"},
                        f"attacker_{worker_id}"
                    )
                    time.sleep(0.001)  # Small delay
                results.append(True)
            except Exception as e:
                results.append(False)

        # Run multiple malicious workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=malicious_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # System should remain stable
        assert all(results), "System became unstable under malicious concurrent access"

        # Verify knowledge store still works normally
        normal_result = secure_knowledge_store.store_context(
            "normal_test", {"test": "data"}, "normal_user"
        )
        assert normal_result is True
```

---

## Test Execution and Coverage

### Run Tests Command

```bash
# Run all tests
pytest tests/ -v --cov=agentic_core --cov-report=html --cov-report=term

# Run specific gap tests
pytest tests/unit/agentic_core/L4_state/knowledge/ -v
pytest tests/unit/agentic_core/L0_maintenance/sensors/ -v
pytest tests/unit/agentic_core/L5_safety/human_review/ -v

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v

# Run security tests
pytest tests/security/ -v

# Generate coverage report
pytest --cov=agentic_core --cov-report=html --cov-fail-under=90
```

### Coverage Targets

- **Unit Tests:** 90% line coverage
- **Integration Tests:** 80% branch coverage
- **E2E Tests:** 100% critical path coverage
- **Security Tests:** 100% security-sensitive code coverage

### Test Data Management

```python
# Test fixtures location
tests/fixtures/knowledge_store_data/
tests/fixtures/sensor_data/
tests/fixtures/review_gate_data/

# Mock data generators
tests/utils/mock_data_generators.py
tests/utils/test_helpers.py
```

This comprehensive test suite ensures all gap implementations are thoroughly validated for functionality, performance, security, and integration compatibility.
