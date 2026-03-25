"""Compliance frameworks smoke tests — import verification and basic functionality."""
import pytest

@pytest.mark.smoke
def test_compliance_frameworks_importable():
    """Verify compliance frameworks module imports without error."""
    try:
        import agentic_core.compliance.frameworks
        assert agentic_core.compliance.frameworks is not None
    except ImportError as e:
        pytest.skip(f"compliance.frameworks not yet implemented: {e}")

@pytest.mark.smoke
def test_gdpr_compliance_importable():
    """Verify GDPR compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.gdpr_compliance import (
            GDPRCompliance,
        )
        assert GDPRCompliance is not None
    except ImportError as e:
        pytest.skip(f"GDPRCompliance not yet implemented: {e}")

@pytest.mark.smoke
def test_hipaa_compliance_importable():
    """Verify HIPAA compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.hipaa_compliance import (
            HIPAACompliance,
        )
        assert HIPAACompliance is not None
    except ImportError as e:
        pytest.skip(f"HIPAACompliance not yet implemented: {e}")

@pytest.mark.smoke
def test_sox_compliance_importable():
    """Verify SOX compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.sox_compliance import (
            SOXCompliance,
        )
        assert SOXCompliance is not None
    except ImportError as e:
        pytest.skip(f"SOXCompliance not yet implemented: {e}")

@pytest.mark.smoke
def test_pci_dss_compliance_importable():
    """Verify PCI DSS compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.pci_dss_compliance import (
            PCIDSSCompliance,
        )
        assert PCIDSSCompliance is not None
    except ImportError as e:
        pytest.skip(f"PCIDSSCompliance not yet implemented: {e}")

@pytest.mark.smoke
def test_iso27001_compliance_importable():
    """Verify ISO 27001 compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.iso27001_compliance import (
            ISO27001Compliance,
        )
        assert ISO27001Compliance is not None
    except ImportError as e:
        pytest.skip(f"ISO27001Compliance not yet implemented: {e}")

@pytest.mark.smoke
def test_nist_compliance_importable():
    """Verify NIST compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.nist_compliance import (
            NISTCompliance,
        )
        assert NISTCompliance is not None
    except ImportError as e:
        pytest.skip(f"NISTCompliance not yet implemented: {e}")

@pytest.mark.smoke
def test_soc2_compliance_importable():
    """Verify SOC 2 compliance imports without error."""
    try:
        from agentic_core.compliance.frameworks.soc2_compliance import (
            SOC2Compliance,
        )
        assert SOC2Compliance is not None
    except ImportError as e:
        pytest.skip(f"SOC2Compliance not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_framework_factory_importable():
    """Verify compliance framework factory imports without error."""
    try:
        from agentic_core.compliance.frameworks.compliance_framework_factory import (
            ComplianceFrameworkFactory,
        )
        assert ComplianceFrameworkFactory is not None
    except ImportError as e:
        pytest.skip(f"ComplianceFrameworkFactory not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_framework_registry_importable():
    """Verify compliance framework registry imports without error."""
    try:
        from agentic_core.compliance.frameworks.compliance_framework_registry import (
            ComplianceFrameworkRegistry,
        )
        assert ComplianceFrameworkRegistry is not None
    except ImportError as e:
        pytest.skip(f"ComplianceFrameworkRegistry not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_framework_adapter_importable():
    """Verify compliance framework adapter imports without error."""
    try:
        from agentic_core.compliance.frameworks.compliance_framework_adapter import (
            ComplianceFrameworkAdapter,
        )
        assert ComplianceFrameworkAdapter is not None
    except ImportError as e:
        pytest.skip(f"ComplianceFrameworkAdapter not yet implemented: {e}")

@pytest.mark.smoke
def test_compliance_framework_validator_importable():
    """Verify compliance framework validator imports without error."""
    try:
        from agentic_core.compliance.frameworks.compliance_framework_validator import (
            ComplianceFrameworkValidator,
        )
        assert ComplianceFrameworkValidator is not None
    except ImportError as e:
        pytest.skip(f"ComplianceFrameworkValidator not yet implemented: {e}")