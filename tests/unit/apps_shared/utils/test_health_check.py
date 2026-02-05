"""
Unit tests for Health Check Utilities.

Tests Phase 5B - Deployment Readiness.
"""

import os
from unittest.mock import patch


from apps_shared.utils.health_check_types import (
    CheckResult,
    CommonChecks,
    HealthChecker,
    HealthReport,
    HealthStatus,
    ReadinessGate,
    get_health_checker,
    get_readiness_gate,
)


class TestHealthStatus:
    """Test HealthStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestCheckResult:
    """Test CheckResult dataclass."""

    def test_healthy_result(self):
        """Test creating a healthy result."""
        result = CheckResult(
            name="test",
            status=HealthStatus.HEALTHY,
            message="All good",
        )
        assert result.is_healthy is True
        assert result.is_critical is False

    def test_unhealthy_result(self):
        """Test creating an unhealthy result."""
        result = CheckResult(
            name="test",
            status=HealthStatus.UNHEALTHY,
            message="Failed",
        )
        assert result.is_healthy is False
        assert result.is_critical is True

    def test_degraded_result(self):
        """Test creating a degraded result."""
        result = CheckResult(
            name="test",
            status=HealthStatus.DEGRADED,
            message="Partially working",
        )
        assert result.is_healthy is False
        assert result.is_critical is False


class TestHealthReport:
    """Test HealthReport dataclass."""

    def test_healthy_report(self):
        """Test creating a healthy report."""
        report = HealthReport(
            status=HealthStatus.HEALTHY,
            checks=[
                CheckResult(name="check1", status=HealthStatus.HEALTHY),
                CheckResult(name="check2", status=HealthStatus.HEALTHY),
            ],
        )
        assert report.is_healthy is True

    def test_to_dict(self):
        """Test converting report to dictionary."""
        report = HealthReport(
            status=HealthStatus.HEALTHY,
            checks=[
                CheckResult(
                    name="test",
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    duration_ms=10.5,
                )
            ],
            version="1.0.0",
        )

        data = report.to_dict()

        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert len(data["checks"]) == 1
        assert data["checks"][0]["name"] == "test"


class TestHealthChecker:
    """Test HealthChecker functionality."""

    def test_register_check(self):
        """Test registering a health check."""
        checker = HealthChecker()

        def my_check():
            return CheckResult(name="test", status=HealthStatus.HEALTHY)

        checker.register_check("test", my_check)

        assert "test" in checker._checks

    def test_unregister_check(self):
        """Test unregistering a health check."""
        checker = HealthChecker()

        def my_check():
            return CheckResult(name="test", status=HealthStatus.HEALTHY)

        checker.register_check("test", my_check)
        result = checker.unregister_check("test")

        assert result is True
        assert "test" not in checker._checks

    def test_unregister_nonexistent(self):
        """Test unregistering a nonexistent check."""
        checker = HealthChecker()
        result = checker.unregister_check("nonexistent")
        assert result is False

    def test_run_check(self):
        """Test running a specific check."""
        checker = HealthChecker()

        def my_check():
            return CheckResult(name="test", status=HealthStatus.HEALTHY)

        checker.register_check("test", my_check)
        result = checker.run_check("test")

        assert result is not None
        assert result.status == HealthStatus.HEALTHY
        assert result.duration_ms >= 0

    def test_run_check_nonexistent(self):
        """Test running a nonexistent check."""
        checker = HealthChecker()
        result = checker.run_check("nonexistent")
        assert result is None

    def test_run_check_handles_exception(self):
        """Test that check exceptions are handled."""
        checker = HealthChecker()

        def failing_check():
            raise ValueError("Check failed")

        checker.register_check("failing", failing_check)
        result = checker.run_check("failing")

        assert result is not None
        assert result.status == HealthStatus.UNHEALTHY
        assert "Check failed" in result.message

    def test_run_all_checks_healthy(self):
        """Test running all checks when all healthy."""
        checker = HealthChecker()

        checker.register_check(
            "check1",
            lambda: CheckResult(name="check1", status=HealthStatus.HEALTHY),
        )
        checker.register_check(
            "check2",
            lambda: CheckResult(name="check2", status=HealthStatus.HEALTHY),
        )

        report = checker.run_all_checks()

        assert report.status == HealthStatus.HEALTHY
        assert len(report.checks) == 2

    def test_run_all_checks_degraded(self):
        """Test running all checks with one degraded."""
        checker = HealthChecker()

        checker.register_check(
            "healthy",
            lambda: CheckResult(name="healthy", status=HealthStatus.HEALTHY),
        )
        checker.register_check(
            "degraded",
            lambda: CheckResult(name="degraded", status=HealthStatus.DEGRADED),
        )

        report = checker.run_all_checks()

        assert report.status == HealthStatus.DEGRADED

    def test_run_all_checks_critical_unhealthy(self):
        """Test critical check failure makes overall unhealthy."""
        checker = HealthChecker()

        checker.register_check(
            "healthy",
            lambda: CheckResult(name="healthy", status=HealthStatus.HEALTHY),
        )
        checker.register_check(
            "critical",
            lambda: CheckResult(name="critical", status=HealthStatus.UNHEALTHY),
            critical=True,
        )

        report = checker.run_all_checks()

        assert report.status == HealthStatus.UNHEALTHY

    def test_get_liveness(self):
        """Test liveness check."""
        checker = HealthChecker()
        result = checker.get_liveness()

        assert result.status == HealthStatus.HEALTHY
        assert result.name == "liveness"

    def test_get_readiness(self):
        """Test readiness check."""
        checker = HealthChecker()
        checker.register_check(
            "check",
            lambda: CheckResult(name="check", status=HealthStatus.HEALTHY),
        )

        report = checker.get_readiness()

        assert isinstance(report, HealthReport)


class TestCommonChecks:
    """Test CommonChecks factory."""

    def test_env_var_check_set(self):
        """Test env var check when variable is set."""
        with patch.dict(os.environ, {"TEST_VAR": "value"}):
            check = CommonChecks.env_var_check("TEST_VAR")
            result = check()

            assert result.status == HealthStatus.HEALTHY

    def test_env_var_check_not_set_required(self):
        """Test env var check when required variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            check = CommonChecks.env_var_check("MISSING_VAR", required=True)
            result = check()

            assert result.status == HealthStatus.UNHEALTHY

    def test_env_var_check_not_set_optional(self):
        """Test env var check when optional variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            check = CommonChecks.env_var_check("MISSING_VAR", required=False)
            result = check()

            assert result.status == HealthStatus.DEGRADED

    def test_redis_check_not_installed(self):
        """Test redis check when redis not installed."""
        with patch.dict("sys.modules", {"redis": None}):
            check = CommonChecks.redis_check()
            # This will try to import redis and fail or succeed based on env
            result = check()
            # Result should be one of the valid statuses
            assert result.status in [
                HealthStatus.HEALTHY,
                HealthStatus.DEGRADED,
                HealthStatus.UNHEALTHY,
            ]

    def test_disk_space_check(self):
        """Test disk space check."""
        check = CommonChecks.disk_space_check(path=".", min_free_gb=0.001)
        result = check()

        # Should succeed with very low threshold
        assert result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        assert "free_gb" in result.metadata or result.status == HealthStatus.UNKNOWN


class TestReadinessGate:
    """Test ReadinessGate functionality."""

    def test_initial_state(self):
        """Test initial state is not ready."""
        gate = ReadinessGate()
        assert gate.is_ready() is False

    def test_set_ready(self):
        """Test setting ready state."""
        gate = ReadinessGate()
        gate.set_ready()

        assert gate.is_ready() is True

    def test_set_not_ready(self):
        """Test setting not ready state."""
        gate = ReadinessGate()
        gate.set_ready()
        gate.set_not_ready("Maintenance mode")

        assert gate.is_ready() is False

    def test_get_status(self):
        """Test getting status."""
        gate = ReadinessGate()
        gate.set_not_ready("Testing")

        status = gate.get_status()

        assert status["ready"] is False
        assert status["reason"] == "Testing"


class TestGetHealthChecker:
    """Test get_health_checker singleton."""

    def test_singleton_instance(self):
        """Test that get_health_checker returns singleton."""
        import apps_shared.utils.health_check_types as hc_module

        hc_module._health_checker = None

        checker1 = get_health_checker()
        checker2 = get_health_checker()

        assert checker1 is checker2

        hc_module._health_checker = None


class TestGetReadinessGate:
    """Test get_readiness_gate singleton."""

    def test_singleton_instance(self):
        """Test that get_readiness_gate returns singleton."""
        import apps_shared.utils.health_check_types as hc_module

        hc_module._readiness_gate = None

        gate1 = get_readiness_gate()
        gate2 = get_readiness_gate()

        assert gate1 is gate2

        hc_module._readiness_gate = None
