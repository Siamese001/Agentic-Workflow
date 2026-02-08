"""Tests for DetectionSignalProtocol."""

from agentic_core.utils.detection_protocol import (
    DetectionRequest,
    DetectionResult,
    DetectionSignalProtocol,
    Severity,
)


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"

    def test_severity_from_string(self):
        """Test creating severity from string."""
        assert Severity("critical") == Severity.CRITICAL
        assert Severity("high") == Severity.HIGH


class TestDetectionRequest:
    """Tests for DetectionRequest dataclass."""

    def test_create_request(self):
        """Test creating a detection request."""
        request = DetectionRequest(
            file_path="/path/to/file.py",
            detection_type="naming_violation",
        )
        assert request.file_path == "/path/to/file.py"
        assert request.detection_type == "naming_violation"
        assert request.context == {}

    def test_create_request_with_context(self):
        """Test creating request with context."""
        context = {"rule": "pascal_case"}
        request = DetectionRequest(
            file_path="/path/to/file.py",
            detection_type="naming_violation",
            context=context,
        )
        assert request.context == context

    def test_request_none_context_defaults_to_empty_dict(self):
        """Test that None context becomes empty dict."""
        request = DetectionRequest(
            file_path="/path/to/file.py",
            detection_type="naming_violation",
            context=None,
        )
        assert request.context == {}


class TestDetectionResult:
    """Tests for DetectionResult dataclass."""

    def test_create_result(self):
        """Test creating a detection result."""
        result = DetectionResult(
            source_sensor="FileClassificationAgent",
            detection_type="naming_violation",
            severity=Severity.MEDIUM,
            file_path="/path/to/file.py",
            message="File name does not follow PascalCase convention",
        )
        assert result.source_sensor == "FileClassificationAgent"
        assert result.detection_type == "naming_violation"
        assert result.severity == Severity.MEDIUM
        assert result.file_path == "/path/to/file.py"
        assert result.auto_fixable is False

    def test_create_result_with_fix(self):
        """Test creating result with suggested fix."""
        result = DetectionResult(
            source_sensor="FileClassificationAgent",
            detection_type="naming_violation",
            severity=Severity.LOW,
            file_path="/path/to/file.py",
            message="File name issue",
            suggested_fix="Rename to PascalCase",
            auto_fixable=True,
        )
        assert result.suggested_fix == "Rename to PascalCase"
        assert result.auto_fixable is True

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = DetectionResult(
            source_sensor="TestAgent",
            detection_type="test_violation",
            severity=Severity.HIGH,
            file_path="/test.py",
            message="Test message",
            target_node="test_func",
        )
        d = result.to_dict()
        assert d["source_sensor"] == "TestAgent"
        assert d["detection_type"] == "test_violation"
        assert d["severity"] == "high"
        assert d["file_path"] == "/test.py"
        assert d["message"] == "Test message"
        assert d["target_node"] == "test_func"

    def test_result_classify_risk_level_high(self):
        """Test risk classification for critical/high severity."""
        result = DetectionResult(
            source_sensor="Test",
            detection_type="test",
            severity=Severity.CRITICAL,
            file_path="/test.py",
            message="test",
        )
        assert result.classify_risk_level() == "high"

        result.severity = Severity.HIGH
        assert result.classify_risk_level() == "high"

    def test_result_classify_risk_level_medium(self):
        """Test risk classification for medium severity."""
        result = DetectionResult(
            source_sensor="Test",
            detection_type="test",
            severity=Severity.MEDIUM,
            file_path="/test.py",
            message="test",
        )
        assert result.classify_risk_level() == "medium"

    def test_result_classify_risk_level_low(self):
        """Test risk classification for low/info severity."""
        result = DetectionResult(
            source_sensor="Test",
            detection_type="test",
            severity=Severity.LOW,
            file_path="/test.py",
            message="test",
        )
        assert result.classify_risk_level() == "low"

        result.severity = Severity.INFO
        assert result.classify_risk_level() == "low"

    def test_result_none_metadata_defaults_to_empty_dict(self):
        """Test that None metadata becomes empty dict."""
        result = DetectionResult(
            source_sensor="Test",
            detection_type="test",
            severity=Severity.LOW,
            file_path="/test.py",
            message="test",
            metadata=None,
        )
        assert result.metadata == {}


class MockDetectionSignalEmitter(DetectionSignalProtocol):
    """Mock implementation for testing."""

    def __init__(self, available: bool = True):
        self._available = available
        self._signals: list[DetectionResult] = []
        self._signal_counter = 0

    def emit_signal(self, result: DetectionResult) -> str:
        self._signal_counter += 1
        signal_id = f"SIG-{self._signal_counter:06d}"
        self._signals.append(result)
        return signal_id

    def get_signals(
        self,
        file_path: str | None = None,
        severity: Severity | None = None,
        limit: int = 100,
    ) -> list[DetectionResult]:
        results = self._signals
        if file_path:
            results = [r for r in results if r.file_path == file_path]
        if severity:
            results = [r for r in results if r.severity == severity]
        return results[:limit]

    def is_available(self) -> bool:
        return self._available


class TestDetectionSignalProtocol:
    """Tests for DetectionSignalProtocol."""

    def test_mock_emit_signal(self):
        """Test emitting a detection signal."""
        emitter = MockDetectionSignalEmitter()
        result = DetectionResult(
            source_sensor="TestAgent",
            detection_type="test",
            severity=Severity.LOW,
            file_path="/test.py",
            message="test message",
        )
        signal_id = emitter.emit_signal(result)
        assert signal_id.startswith("SIG-")

    def test_mock_get_signals(self):
        """Test getting signals."""
        emitter = MockDetectionSignalEmitter()
        result = DetectionResult(
            source_sensor="TestAgent",
            detection_type="test",
            severity=Severity.LOW,
            file_path="/test.py",
            message="test message",
        )
        emitter.emit_signal(result)
        signals = emitter.get_signals()
        assert len(signals) == 1
        assert signals[0].source_sensor == "TestAgent"

    def test_mock_get_signals_filter_by_file(self):
        """Test filtering signals by file path."""
        emitter = MockDetectionSignalEmitter()
        emitter.emit_signal(
            DetectionResult(
                source_sensor="Test",
                detection_type="test",
                severity=Severity.LOW,
                file_path="/file1.py",
                message="msg1",
            ),
        )
        emitter.emit_signal(
            DetectionResult(
                source_sensor="Test",
                detection_type="test",
                severity=Severity.LOW,
                file_path="/file2.py",
                message="msg2",
            ),
        )
        signals = emitter.get_signals(file_path="/file1.py")
        assert len(signals) == 1
        assert signals[0].file_path == "/file1.py"

    def test_mock_get_signals_filter_by_severity(self):
        """Test filtering signals by severity."""
        emitter = MockDetectionSignalEmitter()
        emitter.emit_signal(
            DetectionResult(
                source_sensor="Test",
                detection_type="test",
                severity=Severity.LOW,
                file_path="/test.py",
                message="low",
            ),
        )
        emitter.emit_signal(
            DetectionResult(
                source_sensor="Test",
                detection_type="test",
                severity=Severity.HIGH,
                file_path="/test.py",
                message="high",
            ),
        )
        signals = emitter.get_signals(severity=Severity.HIGH)
        assert len(signals) == 1
        assert signals[0].severity == Severity.HIGH

    def test_mock_is_available(self):
        """Test is_available method."""
        emitter = MockDetectionSignalEmitter(available=True)
        assert emitter.is_available() is True

        emitter = MockDetectionSignalEmitter(available=False)
        assert emitter.is_available() is False
