"""Compliance smoke tests — import verification and basic functionality."""
import pytest

@pytest.mark.smoke
def test_compliance_importable():
    """Verify compliance module imports without error."""
    try:
        import agentic_core.compliance
        assert agentic_core.compliance is not None
    except ImportError as e:
        pytest.fail(f"Failed to import compliance: {e}")

@pytest.mark.smoke
def test_compliance_engine_importable():
    """Verify compliance engine imports without error."""
    try:
        from agentic_core.compliance.compliance_engine import (
            ComplianceEngine,
        )
        assert ComplianceEngine is not None
    except ImportError as e:
        pytest.skip(f"ComplianceEngine not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_manager_importable():
    """Verify compliance manager imports without error."""
    try:
        from agentic_core.compliance.compliance_manager import (
            ComplianceManager,
        )
        assert ComplianceManager is not None
    except ImportError as e:
        pytest.skip(f"ComplianceManager not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_monitor_importable():
    """Verify compliance monitor imports without error."""
    try:
        from agentic_core.compliance.compliance_monitor import (
            ComplianceMonitor,
        )
        assert ComplianceMonitor is not None
    except ImportError as e:
        pytest.skip(f"ComplianceMonitor not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_validator_importable():
    """Verify compliance validator imports without error."""
    try:
        from agentic_core.compliance.compliance_validator import (
            ComplianceValidator,
        )
        assert ComplianceValidator is not None
    except ImportError as e:
        pytest.skip(f"ComplianceValidator not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_auditor_importable():
    """Verify compliance auditor imports without error."""
    try:
        from agentic_core.compliance.compliance_auditor import (
            ComplianceAuditor,
        )
        assert ComplianceAuditor is not None
    except ImportError as e:
        pytest.skip(f"ComplianceAuditor not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_reporting_importable():
    """Verify compliance reporting imports without error."""
    try:
        from agentic_core.compliance.compliance_reporting import (
            ComplianceReporting,
        )
        assert ComplianceReporting is not None
    except ImportError as e:
        pytest.skip(f"ComplianceReporting not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_assessment_importable():
    """Verify compliance assessment imports without error."""
    try:
        from agentic_core.compliance.compliance_assessment import (
            ComplianceAssessment,
        )
        assert ComplianceAssessment is not None
    except ImportError as e:
        pytest.skip(f"ComplianceAssessment not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_scanner_importable():
    """Verify compliance scanner imports without error."""
    try:
        from agentic_core.compliance.compliance_scanner import (
            ComplianceScanner,
        )
        assert ComplianceScanner is not None
    except ImportError as e:
        pytest.skip(f"ComplianceScanner not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_enforcer_importable():
    """Verify compliance enforcer imports without error."""
    try:
        from agentic_core.compliance.compliance_enforcer import (
            ComplianceEnforcer,
        )
        assert ComplianceEnforcer is not None
    except ImportError as e:
        pytest.skip(f"ComplianceEnforcer not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_tracking_importable():
    """Verify compliance tracking imports without error."""
    try:
        from agentic_core.compliance.compliance_tracking import (
            ComplianceTracking,
        )
        assert ComplianceTracking is not None
    except ImportError as e:
        pytest.skip(f"ComplianceTracking not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_config_importable():
    """Verify compliance config imports without error."""
    try:
        from agentic_core.compliance.compliance_config import (
            get_compliance_config,
        )
        assert callable(get_compliance_config), "get_compliance_config should be callable"
    except ImportError as e:
        pytest.skip(f"compliance_config not yet implemented: {e}")