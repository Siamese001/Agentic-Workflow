"""
Unit tests for ToxicDependencyAuditor with coverage weighting.
Phase 10: L1 Cognition Scaling - Reputation Audit Enhancement
"""
import pytest
from pathlib import Path
from agentic_core.L5_safety.validators.ToxicDependencyAuditor import ToxicDependencyAuditor


class TestToxicDependencyAuditorCoverage:
    """Test suite for ToxicDependencyAuditor coverage weighting feature."""
    
    def test_initialization(self):
        """Test ToxicDependencyAuditor initializes correctly."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=10)
        
        assert auditor.root == Path(".")
        assert auditor.threshold == 10
        assert auditor.dependency_map == {}
    
    def test_audit_toxicity_without_coverage(self):
        """Test audit_toxicity works without coverage data."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=10)
        
        # Run audit without coverage data
        hubs = auditor.audit_toxicity()
        
        # Should return a list
        assert isinstance(hubs, list)
        
        # Each hub should have required fields
        for hub in hubs:
            assert 'module' in hub
            assert 'fan_in' in hub
            assert 'dependents' in hub
            assert 'systemic_risk' in hub
    
    def test_audit_toxicity_with_coverage_data(self):
        """Test audit_toxicity applies coverage weighting correctly."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=5)
        
        # Mock coverage data
        coverage_data = {
            "agentic_core.utils.core_extensions": 0.8,  # 80% coverage
            "agentic_core.L0_maintenance.scripts": 0.3,  # 30% coverage
            "agentic_core.L5_safety.validators": 0.0,    # 0% coverage
        }
        
        # Run audit with coverage data
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        
        # Verify coverage fields are present
        for hub in hubs:
            if hub['module'] in coverage_data:
                assert 'coverage' in hub
                assert 'coverage_weight' in hub
                assert 'systemic_risk' in hub
                assert hub['coverage'] is not None
    
    def test_coverage_weight_calculation(self):
        """Test that coverage weight is calculated correctly."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        # Manually build a simple dependency map for testing
        auditor.dependency_map = {
            "test_module": {"dep1", "dep2", "dep3", "dep4", "dep5"}
        }
        
        coverage_data = {
            "test_module": 0.5  # 50% coverage
        }
        
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        
        # Should have one hub
        assert len(hubs) >= 1
        
        # Find our test module
        test_hub = next((h for h in hubs if h['module'] == 'test_module'), None)
        if test_hub:
            # Coverage weight should be 2.0 - 0.5 = 1.5
            assert test_hub['coverage_weight'] == 1.5
            # Systemic risk should be fan_in * coverage_weight = 5 * 1.5 = 7.5
            assert test_hub['systemic_risk'] == 7.5
    
    def test_coverage_weight_extremes(self):
        """Test coverage weight calculation at extremes."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "zero_coverage": {"dep1", "dep2"},
            "full_coverage": {"dep1", "dep2"}
        }
        
        coverage_data = {
            "zero_coverage": 0.0,   # 0% coverage
            "full_coverage": 1.0    # 100% coverage
        }
        
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        
        # Find hubs
        zero_hub = next((h for h in hubs if h['module'] == 'zero_coverage'), None)
        full_hub = next((h for h in hubs if h['module'] == 'full_coverage'), None)
        
        if zero_hub:
            # 0% coverage: weight = 2.0 - 0.0 = 2.0
            assert zero_hub['coverage_weight'] == 2.0
            # Risk = 2 * 2.0 = 4.0
            assert zero_hub['systemic_risk'] == 4.0
        
        if full_hub:
            # 100% coverage: weight = 2.0 - 1.0 = 1.0
            assert full_hub['coverage_weight'] == 1.0
            # Risk = 2 * 1.0 = 2.0
            assert full_hub['systemic_risk'] == 2.0
    
    def test_systemic_risk_sorting(self):
        """Test that hubs are sorted by systemic risk."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "low_risk": {"dep1"},           # fan_in=1
            "medium_risk": {"dep1", "dep2"},  # fan_in=2
            "high_risk": {"dep1", "dep2", "dep3"}  # fan_in=3
        }
        
        coverage_data = {
            "low_risk": 1.0,      # 100% coverage, weight=1.0, risk=1.0
            "medium_risk": 0.5,   # 50% coverage, weight=1.5, risk=3.0
            "high_risk": 0.0      # 0% coverage, weight=2.0, risk=6.0
        }
        
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        
        # Should be sorted by systemic_risk descending
        if len(hubs) >= 3:
            # First should be highest risk
            assert hubs[0]['systemic_risk'] >= hubs[1]['systemic_risk']
            assert hubs[1]['systemic_risk'] >= hubs[2]['systemic_risk']
    
    def test_missing_coverage_data_for_module(self):
        """Test handling when coverage data is missing for a module."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "covered_module": {"dep1", "dep2"},
            "uncovered_module": {"dep1", "dep2"}
        }
        
        coverage_data = {
            "covered_module": 0.8  # Only one module has coverage data
        }
        
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        
        # Find uncovered module
        uncovered = next((h for h in hubs if h['module'] == 'uncovered_module'), None)
        
        if uncovered:
            # Should default to coverage_weight=1.0 when no coverage data
            assert uncovered['coverage_weight'] == 1.0
            assert uncovered['coverage'] == 0.0  # Default to 0.0
    
    def test_report_with_coverage(self, capsys):
        """Test that report displays coverage information."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "test_module": {"dep1", "dep2", "dep3"}
        }
        
        coverage_data = {
            "test_module": 0.75  # 75% coverage
        }
        
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        auditor.report(hubs)
        
        captured = capsys.readouterr()
        
        # Should display coverage information
        assert "Coverage:" in captured.out
        assert "Coverage Weight:" in captured.out
        assert "Systemic Risk Score:" in captured.out
    
    def test_report_without_coverage(self, capsys):
        """Test that report works without coverage data."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "test_module": {"dep1", "dep2", "dep3"}
        }
        
        hubs = auditor.audit_toxicity()  # No coverage data
        auditor.report(hubs)
        
        captured = capsys.readouterr()
        
        # Should display basic toxicity score
        assert "Toxicity Score:" in captured.out or "Fan-in" in captured.out
    
    def test_empty_coverage_data(self):
        """Test handling of empty coverage data dictionary."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "test_module": {"dep1", "dep2"}
        }
        
        hubs = auditor.audit_toxicity(coverage_data={})
        
        # Should handle empty dict gracefully
        assert isinstance(hubs, list)
        
        for hub in hubs:
            # Should default to weight=1.0
            assert hub['coverage_weight'] == 1.0
    
    def test_threshold_filtering(self):
        """Test that threshold filters out low fan-in modules."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=5)
        
        auditor.dependency_map = {
            "below_threshold": {"dep1", "dep2"},  # fan_in=2, below threshold
            "above_threshold": {"dep1", "dep2", "dep3", "dep4", "dep5", "dep6"}  # fan_in=6
        }
        
        hubs = auditor.audit_toxicity()
        
        # Only above_threshold should be in results
        module_names = [h['module'] for h in hubs]
        assert "below_threshold" not in module_names
        assert "above_threshold" in module_names
    
    def test_coverage_percentage_display(self, capsys):
        """Test that coverage is displayed as percentage."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=1)
        
        auditor.dependency_map = {
            "test_module": {"dep1", "dep2"}
        }
        
        coverage_data = {
            "test_module": 0.856  # 85.6% coverage
        }
        
        hubs = auditor.audit_toxicity(coverage_data=coverage_data)
        auditor.report(hubs)
        
        captured = capsys.readouterr()
        
        # Should display as percentage with one decimal
        assert "85.6%" in captured.out
    
    def test_backward_compatibility(self):
        """Test that audit_toxicity is backward compatible without coverage_data."""
        auditor = ToxicDependencyAuditor(root_dir=".", toxic_threshold=10)
        
        # Should work without coverage_data parameter
        hubs = auditor.audit_toxicity()
        
        assert isinstance(hubs, list)
        
        # Should still have systemic_risk field (equals fan_in when no coverage)
        for hub in hubs:
            assert 'systemic_risk' in hub
            if hub.get('coverage') is None:
                # When no coverage, systemic_risk should equal fan_in
                assert hub['systemic_risk'] == hub['fan_in']
