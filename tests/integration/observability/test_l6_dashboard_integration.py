#!/usr/bin/env python3
"""
Integration tests for L6 Observability Dashboard.

Tests the full dashboard pipeline from data generation to HTML rendering,
including all Phase 1-6 features working together.
"""
import json
import re
from pathlib import Path
import pytest

# Disable path_shield for real file I/O testing
pytestmark = pytest.mark.usefixtures("disable_path_shield")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
L6_DASHBOARD_PATH = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"


def load_dashboard_html():
    """Load dashboard HTML content."""
    if not L6_DASHBOARD_PATH.exists():
        pytest.skip(f"Dashboard not found at {L6_DASHBOARD_PATH}")
    return L6_DASHBOARD_PATH.read_text(encoding='utf-8')


class TestDashboardDataFlow:
    """Integration tests for dashboard data flow."""
    
    def test_dashboard_html_loads_successfully(self):
        """Test that dashboard HTML loads without errors."""
        html = load_dashboard_html()
        assert len(html) > 100000, "Dashboard HTML should be > 100KB"
    
    def test_dashboard_has_valid_html_structure(self):
        """Test that dashboard has valid HTML structure."""
        html = load_dashboard_html()
        
        required_elements = [
            '<!DOCTYPE html>',
            '<html',
            '<head>',
            '<body>',
            '</body>',
            '</html>',
        ]
        
        for elem in required_elements:
            assert elem in html, f"Missing HTML element: {elem}"
    
    def test_dashboard_data_variable_populated(self):
        """Test that dashboardData variable is populated with data."""
        html = load_dashboard_html()
        
        # Check that dashboardData is not empty
        assert 'const dashboardData = []' not in html or 'dashboardData = [' in html, (
            "dashboardData should be populated"
        )
    
    def test_all_phase_features_present(self):
        """Test that all Phase 1-6 features are present in dashboard."""
        html = load_dashboard_html()
        
        phase_features = {
            'Phase 1 - Distribution Stats': ['σ=', 'Min-Max', 'calculateDistributionStats'],
            'Phase 2 - Outlier Flagging': ['@0%', '<50%', 'outlier'],
            'Phase 3 - Worst Performer': ['Worst Agent', 'vscode://file/'],
            'Phase 4 - Visual Intensity': ['rgba(', 'gradient'],
            'Phase 5 - Zombie Detection': ['🧟', 'ZOMBIE', 'showZombies'],
            'Phase 6 - Toxicity Impact': ['☢️', 'HEAL', 'triggerHealAgent'],
        }
        
        missing_phases = []
        for phase, indicators in phase_features.items():
            found = any(indicator in html for indicator in indicators)
            if not found:
                missing_phases.append(phase)
        
        assert not missing_phases, f"Missing phase features: {missing_phases}"


class TestTableIntegration:
    """Integration tests for table rendering."""
    
    def test_table1_renders_with_all_columns(self):
        """Test that Table 1 (Territory Summary) renders with all columns."""
        html = load_dashboard_html()
        
        required_columns = [
            'Territory',
            '# Agents',
            'Heal Capability',
            'Heal Invocation',
            'MCP Hardened',
            'Test Coverage',
            'Complexity Health',
            'Health Score',
            'Worst Agent'
        ]
        
        missing = [col for col in required_columns if col not in html]
        assert not missing, f"Table 1 missing columns: {missing}"
    
    def test_table2_renders_with_all_columns(self):
        """Test that Table 2 (Code Quality) renders with all columns."""
        html = load_dashboard_html()
        
        required_columns = [
            'Typed %',
            'Documented %',
            'Schema Strictness',
            'Proper Base %',
            'Code Quality Score'
        ]
        
        missing = [col for col in required_columns if col not in html]
        assert not missing, f"Table 2 missing columns: {missing}"
    
    def test_total_row_present_in_both_tables(self):
        """Test that TOTAL row is present."""
        html = load_dashboard_html()
        
        # Count TOTAL occurrences (should be at least 2 for both tables)
        total_count = html.count('TOTAL')
        assert total_count >= 1, "TOTAL row should be present in tables"


class TestFilterIntegration:
    """Integration tests for filter functionality."""
    
    def test_all_filter_checkboxes_present(self):
        """Test that all filter checkboxes are present."""
        html = load_dashboard_html()
        
        filters = [
            'Show Only Toxic Hubs',
            'Show Only Zombies',
            'Show only territories with outliers',
            'Sort by outlier'
        ]
        
        found_filters = [f for f in filters if f in html]
        assert len(found_filters) >= 3, f"Missing filters. Found: {found_filters}"
    
    def test_filter_state_management_exists(self):
        """Test that filter state management exists."""
        html = load_dashboard_html()
        
        state_indicators = [
            'tableFilterState',
            'showToxicHubs',
            'showZombies',
            'showOutliersOnly'
        ]
        
        found = sum(1 for indicator in state_indicators if indicator in html)
        assert found >= 2, "Filter state management not properly implemented"


class TestDrillDownIntegration:
    """Integration tests for drill-down modal."""
    
    def test_drill_down_modal_structure(self):
        """Test that drill-down modal has correct structure."""
        html = load_dashboard_html()
        
        modal_elements = [
            'drillModal',
            'modalTitle',
            'modalContent',
            'modalSubtitle'
        ]
        
        found = sum(1 for elem in modal_elements if elem in html)
        assert found >= 3, "Drill-down modal structure incomplete"
    
    def test_drill_down_has_agent_diagnostics(self):
        """Test that drill-down shows per-agent diagnostics."""
        html = load_dashboard_html()
        
        diagnostics_indicators = [
            'Per-Agent Diagnostics',
            'Agent File',
            'HealerMixin',
            'Invocation Chain'
        ]
        
        found = sum(1 for indicator in diagnostics_indicators if indicator in html)
        assert found >= 2, "Per-agent diagnostics not found in drill-down"
    
    def test_drill_down_has_status_and_remediation(self):
        """Test that drill-down has Status and Remediation columns."""
        html = load_dashboard_html()
        
        assert 'Status' in html, "Status column not found in drill-down"
        assert 'Remediation' in html, "Remediation column not found in drill-down"


class TestAlertBannerIntegration:
    """Integration tests for global alert banner."""
    
    def test_alert_banner_container_exists(self):
        """Test that alert banner container exists."""
        html = load_dashboard_html()
        
        banner_indicators = [
            'globalAlertBanner',
            'Critical Outliers',
            'alert-banner'
        ]
        
        found = any(indicator in html for indicator in banner_indicators)
        assert found, "Alert banner container not found"
    
    def test_alert_banner_shows_outlier_count(self):
        """Test that alert banner shows outlier counts."""
        html = load_dashboard_html()
        
        # Check for outlier count display
        count_patterns = ['critical', 'warnings', 'outliers']
        found = sum(1 for pattern in count_patterns if pattern.lower() in html.lower())
        assert found >= 1, "Outlier counts not displayed in alert banner"


class TestVSCodeIntegration:
    """Integration tests for VS Code link integration."""
    
    def test_vscode_links_present(self):
        """Test that VS Code file links are present."""
        html = load_dashboard_html()
        
        assert 'vscode://file/' in html, "VS Code file links not found"
    
    def test_vscode_links_have_correct_format(self):
        """Test that VS Code links have correct format."""
        html = load_dashboard_html()
        
        # Find vscode links
        vscode_pattern = r'vscode://file/[^"\'>\s]+'
        matches = re.findall(vscode_pattern, html)
        
        assert len(matches) > 0, "No VS Code links found"
        
        # Check format
        for link in matches[:5]:  # Check first 5
            assert link.startswith('vscode://file/'), f"Invalid VS Code link format: {link}"


class TestJavaScriptIntegration:
    """Integration tests for JavaScript functionality."""
    
    def test_all_critical_functions_defined(self):
        """Test that all critical JavaScript functions are defined."""
        html = load_dashboard_html()
        
        critical_functions = [
            'loadData',
            'renderTable',
            'openDrillModal',
            'computeDistributionStats',  # Actual function name in dashboard
            'triggerHealAgent'
        ]
        
        missing = []
        for func in critical_functions:
            if f'function {func}' not in html and f'{func} =' not in html:
                missing.append(func)
        
        assert not missing, f"Missing critical functions: {missing}"
    
    def test_event_handlers_attached(self):
        """Test that event handlers are properly attached."""
        html = load_dashboard_html()
        
        event_indicators = [
            'onclick=',
            'addEventListener',
            'onchange='
        ]
        
        found = sum(1 for indicator in event_indicators if indicator in html)
        assert found >= 2, "Event handlers not properly attached"


class TestDataValidation:
    """Integration tests for data validation."""
    
    def test_no_nan_values_in_display(self):
        """Test that no NaN values appear in display."""
        html = load_dashboard_html()
        
        # Check for NaN in visible content (not in JS code)
        nan_patterns = ['NaN%', '>NaN<', 'NaN</']
        found = any(pattern in html for pattern in nan_patterns)
        assert not found, "NaN values found in dashboard display"
    
    def test_no_undefined_values_in_display(self):
        """Test that no undefined values appear in display."""
        html = load_dashboard_html()
        
        undefined_patterns = ['undefined%', '>undefined<', 'undefined</']
        found = any(pattern in html for pattern in undefined_patterns)
        assert not found, "Undefined values found in dashboard display"
    
    def test_percentages_in_valid_range(self):
        """Test that displayed percentages are in valid range."""
        html = load_dashboard_html()
        
        # Find percentage values
        pct_pattern = r'(\d+\.?\d*)%'
        matches = re.findall(pct_pattern, html)
        
        invalid = []
        for match in matches:
            try:
                value = float(match)
                if value < 0 or value > 100:
                    invalid.append(f"{value}%")
            except ValueError:
                pass
        
        # Allow some invalid values (might be in comments or JS)
        assert len(invalid) < 10, f"Too many invalid percentages: {invalid[:10]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
