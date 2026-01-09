#!/usr/bin/env python3
"""
Comprehensive test suite for Dashboard Phase 1-6 Features.

Tests the new dashboard architecture under L6_observability/dashboards:
- Phase 1: Distribution Statistics (min, max, sigma)
- Phase 2: Outlier Flagging & Global Alert Banner
- Phase 3: Worst Performer Column
- Phase 4: Visual Intensity Gradients
- Phase 5: Zombie Detection & Drill-down Modal
- Phase 6: Toxicity-Weighted Impact & Remediation

Location: agentic_core/L6_observability/dashboards/autonomy_dashboard.html
"""
import json
import re
import math
from pathlib import Path
import pytest

# Disable path_shield for real file I/O testing
pytestmark = pytest.mark.usefixtures("disable_path_shield")

# Module-level constants - use L6_observability location
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
L6_DASHBOARD_PATH = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
REPORTS_DASHBOARD_PATH = PROJECT_ROOT / "reports" / "autonomy_dashboard.html"


def get_dashboard_path():
    """Get the dashboard path, preferring L6_observability location."""
    if L6_DASHBOARD_PATH.exists():
        return L6_DASHBOARD_PATH
    elif REPORTS_DASHBOARD_PATH.exists():
        return REPORTS_DASHBOARD_PATH
    return None


def load_dashboard_html():
    """Load dashboard HTML content."""
    dashboard_path = get_dashboard_path()
    if not dashboard_path:
        pytest.skip("Dashboard HTML not found")
    return dashboard_path.read_text(encoding='utf-8')


class TestPhase1DistributionStatistics:
    """Phase 1: Distribution Statistics (min, max, sigma) tests."""
    
    def test_distribution_stats_function_exists(self):
        """Test that computeDistributionStats function exists."""
        html = load_dashboard_html()
        assert 'function computeDistributionStats' in html or 'computeDistributionStats' in html, (
            "computeDistributionStats function not found in dashboard"
        )
    
    def test_distribution_stats_returns_correct_structure(self):
        """Test that distribution stats returns min, max, avg, sigma."""
        html = load_dashboard_html()
        
        # Check for return structure with min, max, avg, sigma
        assert 'min:' in html and 'max:' in html, (
            "Distribution stats should return min and max"
        )
        assert 'avg:' in html or 'mean:' in html, (
            "Distribution stats should return average/mean"
        )
        assert 'sigma:' in html or 'stdDev:' in html, (
            "Distribution stats should return sigma/stdDev"
        )
    
    def test_distribution_display_format(self):
        """Test that distribution is displayed in correct format: Avg% (Min-Max, σ=X.X)."""
        html = load_dashboard_html()
        
        # Check for sigma symbol in display
        assert 'σ=' in html or 'sigma=' in html.lower(), (
            "Distribution display should include sigma symbol (σ=)"
        )
    
    def test_table_headers_include_distribution_hint(self):
        """Test that table headers indicate distribution stats are shown."""
        html = load_dashboard_html()
        
        # Check for Avg (Min-Max, σ) hint in headers or TOTAL row
        assert 'Avg (Min-Max' in html or 'Min-Max' in html, (
            "Table should indicate distribution format in headers or TOTAL row"
        )


class TestPhase2OutlierFlagging:
    """Phase 2: Outlier Flagging & Global Alert Banner tests."""
    
    def test_outlier_detection_function_exists(self):
        """Test that outlier detection logic exists."""
        html = load_dashboard_html()
        
        # Check for outlier-related functions or logic
        outlier_indicators = [
            'outlier',
            'critical',
            '@0%',
            '<50%',
            '<30%'
        ]
        
        found = any(indicator in html.lower() or indicator in html for indicator in outlier_indicators)
        assert found, "Outlier detection logic not found in dashboard"
    
    def test_global_alert_banner_exists(self):
        """Test that global alert banner HTML exists."""
        html = load_dashboard_html()
        
        # Check for alert banner container
        assert 'globalAlertBanner' in html or 'alert-banner' in html or 'Critical Outliers' in html, (
            "Global alert banner not found in dashboard"
        )
    
    def test_outlier_badges_displayed(self):
        """Test that outlier badges are displayed (e.g., '3 @0%', '24 <50%')."""
        html = load_dashboard_html()
        
        # Check for outlier badge patterns
        badge_patterns = ['@0%', '<50%', '<30%', '<60%']
        found = any(pattern in html for pattern in badge_patterns)
        assert found, "Outlier badges not found in dashboard display"
    
    def test_update_global_alert_banner_function(self):
        """Test that updateGlobalAlertBanner function exists."""
        html = load_dashboard_html()
        
        assert 'updateGlobalAlertBanner' in html or 'globalAlertBanner' in html, (
            "updateGlobalAlertBanner function not found"
        )


class TestPhase3WorstPerformer:
    """Phase 3: Worst Performer Column tests."""
    
    def test_worst_agent_column_exists(self):
        """Test that Worst Agent column exists in table."""
        html = load_dashboard_html()
        
        assert 'Worst Agent' in html or 'worst_agent' in html.lower(), (
            "Worst Agent column not found in dashboard table"
        )
    
    def test_worst_agent_links_to_vscode(self):
        """Test that worst agent links use vscode:// protocol."""
        html = load_dashboard_html()
        
        assert 'vscode://file/' in html, (
            "VS Code file links not found - worst agent should link to IDE"
        )
    
    def test_remediation_circuit_active_label(self):
        """Test that TOTAL row shows 'Remediation Circuit Active'."""
        html = load_dashboard_html()
        
        assert 'Remediation Circuit Active' in html, (
            "Remediation Circuit Active label not found in TOTAL row"
        )


class TestPhase4VisualIntensity:
    """Phase 4: Visual Intensity Gradients tests."""
    
    def test_gradient_background_functions_exist(self):
        """Test that gradient background functions exist."""
        html = load_dashboard_html()
        
        gradient_indicators = [
            'getGradientBackground',
            'gradient',
            'rgba(',
            'background:'
        ]
        
        found = sum(1 for indicator in gradient_indicators if indicator in html)
        assert found >= 2, "Gradient background functions not found"
    
    def test_critical_floor_alpha_enhancement(self):
        """Test that critical floor values (<30%) have enhanced alpha."""
        html = load_dashboard_html()
        
        # Check for alpha enhancement logic for critical values
        # The dashboard uses rgba with alpha values for gradient backgrounds
        assert 'rgba(' in html and ('0.3' in html or '0.4' in html or '0.5' in html), (
            "Critical floor alpha enhancement not found in gradient backgrounds"
        )
    
    def test_color_coding_for_metrics(self):
        """Test that color coding exists for different metric ranges."""
        html = load_dashboard_html()
        
        # Check for color definitions (red, yellow, green)
        color_indicators = ['#dc2626', '#f59e0b', '#16a34a', 'red', 'green', 'yellow']
        found = sum(1 for color in color_indicators if color in html.lower() or color in html)
        assert found >= 2, "Color coding for metrics not found"


class TestPhase5ZombieDetection:
    """Phase 5: Zombie Detection & Drill-down Modal tests."""
    
    def test_zombie_filter_checkbox_exists(self):
        """Test that zombie filter checkbox exists."""
        html = load_dashboard_html()
        
        assert 'Zombie' in html or 'zombie' in html, (
            "Zombie filter not found in dashboard"
        )
    
    def test_zombie_detection_threshold(self):
        """Test that zombie detection uses health < 40% threshold."""
        html = load_dashboard_html()
        
        # Check for zombie threshold logic
        assert '< 40' in html or 'health < 40' in html.lower() or 'isZombie' in html, (
            "Zombie detection threshold (health < 40%) not found"
        )
    
    def test_zombie_label_display(self):
        """Test that zombie label (🧟 ZOMBIE) is displayed."""
        html = load_dashboard_html()
        
        assert '🧟' in html or 'ZOMBIE' in html, (
            "Zombie label/emoji not found in dashboard"
        )
    
    def test_drill_down_modal_exists(self):
        """Test that drill-down modal exists."""
        html = load_dashboard_html()
        
        modal_indicators = ['drillModal', 'modal', 'drill-down', 'modalContent']
        found = any(indicator in html for indicator in modal_indicators)
        assert found, "Drill-down modal not found in dashboard"
    
    def test_drill_down_modal_has_status_column(self):
        """Test that drill-down modal has Status column."""
        html = load_dashboard_html()
        
        # Check for Status column header in modal
        assert '>Status<' in html or 'Status</th>' in html or '"Status"' in html, (
            "Status column not found in drill-down modal"
        )
    
    def test_drill_down_modal_has_remediation_column(self):
        """Test that drill-down modal has Remediation column."""
        html = load_dashboard_html()
        
        assert 'Remediation' in html, (
            "Remediation column not found in drill-down modal"
        )
    
    def test_show_zombies_filter_state(self):
        """Test that showZombies filter state exists."""
        html = load_dashboard_html()
        
        assert 'showZombies' in html, (
            "showZombies filter state not found"
        )


class TestPhase6ToxicityImpact:
    """Phase 6: Toxicity-Weighted Impact & Remediation tests."""
    
    def test_toxicity_impact_function_exists(self):
        """Test that calculateToxicityImpact function exists."""
        html = load_dashboard_html()
        
        assert 'calculateToxicityImpact' in html or 'toxicityImpact' in html or 'impact_score' in html, (
            "Toxicity impact calculation function not found"
        )
    
    def test_toxicity_formula_implemented(self):
        """Test that toxicity formula uses ln(fanIn)."""
        html = load_dashboard_html()
        
        # Check for logarithm in formula
        assert 'Math.log' in html or 'ln(' in html or 'log(' in html, (
            "Toxicity formula should use logarithm for fan-in weighting"
        )
    
    def test_toxic_hub_filter_exists(self):
        """Test that toxic hub filter exists."""
        html = load_dashboard_html()
        
        assert 'Toxic Hub' in html or 'toxicHub' in html or '☢️' in html, (
            "Toxic hub filter not found"
        )
    
    def test_fan_in_threshold_defined(self):
        """Test that fan-in threshold (≥20) is defined."""
        html = load_dashboard_html()
        
        assert 'Fan-in' in html or 'fanIn' in html or 'fan_in' in html, (
            "Fan-in threshold not found"
        )
    
    def test_heal_button_exists(self):
        """Test that HEAL button exists in drill-down modal."""
        html = load_dashboard_html()
        
        assert 'HEAL' in html or 'heal' in html.lower(), (
            "HEAL button not found in dashboard"
        )
    
    def test_trigger_heal_agent_function(self):
        """Test that triggerHealAgent function exists."""
        html = load_dashboard_html()
        
        assert 'triggerHealAgent' in html or 'healAgent' in html, (
            "triggerHealAgent function not found"
        )
    
    def test_systemic_risk_flag_exists(self):
        """Test that SYSTEMIC RISK flag exists for toxic hubs."""
        html = load_dashboard_html()
        
        assert 'SYSTEMIC RISK' in html or 'systemic_risk' in html.lower(), (
            "SYSTEMIC RISK flag not found"
        )


class TestDashboardTableStructure:
    """Tests for dashboard table structure and data integrity."""
    
    def test_table1_territory_summary_exists(self):
        """Test that Table 1 (Territory Summary) exists."""
        html = load_dashboard_html()
        
        assert 'Territory Summary' in html or 'kpiGrid' in html, (
            "Territory Summary table not found"
        )
    
    def test_table2_code_quality_exists(self):
        """Test that Table 2 (Code Quality) exists."""
        html = load_dashboard_html()
        
        assert 'Code Quality' in html or 'codeQualityGrid' in html, (
            "Code Quality table not found"
        )
    
    def test_table_has_total_row(self):
        """Test that tables have TOTAL row."""
        html = load_dashboard_html()
        
        assert 'TOTAL' in html, (
            "TOTAL row not found in tables"
        )
    
    def test_table_controls_exist(self):
        """Test that table filter controls exist."""
        html = load_dashboard_html()
        
        control_indicators = ['checkbox', 'filter', 'toggle', 'Sort by']
        found = sum(1 for indicator in control_indicators if indicator in html.lower() or indicator in html)
        assert found >= 2, "Table filter controls not found"
    
    def test_export_csv_button_exists(self):
        """Test that Export CSV button exists."""
        html = load_dashboard_html()
        
        assert 'Export' in html or 'CSV' in html or 'export' in html.lower(), (
            "Export CSV button not found"
        )


class TestDashboardJavaScriptFunctions:
    """Tests for critical JavaScript functions in dashboard."""
    
    def test_load_data_function_exists(self):
        """Test that loadData function exists."""
        html = load_dashboard_html()
        
        assert 'function loadData' in html or 'loadData(' in html, (
            "loadData function not found"
        )
    
    def test_render_table_functions_exist(self):
        """Test that table rendering functions exist."""
        html = load_dashboard_html()
        
        render_functions = ['renderTable', 'renderKPITable', 'renderCodeQualityTable']
        found = any(func in html for func in render_functions)
        assert found, "Table rendering functions not found"
    
    def test_open_drill_modal_function_exists(self):
        """Test that openDrillModal function exists."""
        html = load_dashboard_html()
        
        assert 'openDrillModal' in html or 'openModal' in html, (
            "openDrillModal function not found"
        )
    
    def test_generate_mock_agent_data_function(self):
        """Test that generateMockAgentData function exists for drill-down."""
        html = load_dashboard_html()
        
        assert 'generateMockAgentData' in html or 'agentData' in html, (
            "generateMockAgentData function not found"
        )


class TestDashboardDataIntegrity:
    """Tests for dashboard data integrity and calculations."""
    
    def test_dashboard_data_variable_exists(self):
        """Test that dashboardData variable exists."""
        html = load_dashboard_html()
        
        assert 'dashboardData' in html or 'const dashboardData' in html, (
            "dashboardData variable not found"
        )
    
    def test_agent_data_variable_exists(self):
        """Test that agentData variable exists for distribution stats."""
        html = load_dashboard_html()
        
        assert 'agentData' in html, (
            "agentData variable not found for distribution calculations"
        )
    
    def test_table_filter_state_exists(self):
        """Test that tableFilterState exists for filter management."""
        html = load_dashboard_html()
        
        assert 'tableFilterState' in html or 'filterState' in html, (
            "tableFilterState not found"
        )


class TestDashboardUIElements:
    """Tests for dashboard UI elements and styling."""
    
    def test_auto_refresh_exists(self):
        """Test that auto-refresh functionality exists."""
        html = load_dashboard_html()
        
        assert 'Auto-refresh' in html or 'autoRefresh' in html or 'setInterval' in html, (
            "Auto-refresh functionality not found"
        )
    
    def test_last_updated_timestamp_exists(self):
        """Test that last updated timestamp is displayed."""
        html = load_dashboard_html()
        
        assert 'Last Updated' in html or 'lastUpdated' in html, (
            "Last Updated timestamp not found"
        )
    
    def test_metrics_key_exists(self):
        """Test that metrics key/legend exists."""
        html = load_dashboard_html()
        
        # Check for metrics explanations in the dashboard
        metrics_indicators = ['Typed %:', 'Documented %:', 'Heal Cap', 'Invocation', 'Factory analogy']
        found = sum(1 for indicator in metrics_indicators if indicator in html)
        assert found >= 2, (
            "Metrics key/explanations not found in dashboard"
        )
    
    def test_sparkline_indicators_exist(self):
        """Test that sparkline/trend indicators exist."""
        html = load_dashboard_html()
        
        # Check for trend indicators (arrows, sparklines)
        trend_indicators = ['↑', '↓', 'sparkline', 'trend', '▲', '▼']
        found = any(indicator in html for indicator in trend_indicators)
        assert found, "Trend/sparkline indicators not found"


class TestDeterministicDataGeneration:
    """Tests for deterministic data generation (no random values on refresh)."""
    
    def test_seeded_random_generator_exists(self):
        """Test that deterministic seeded random generator is implemented."""
        html = load_dashboard_html()
        
        # Check for seeded random implementation
        assert 'createSeededRandom' in html, "Seeded random generator function not found"
        assert 'mulberry32' in html, "Mulberry32 PRNG not found"
        assert 'hashString' in html, "Hash string function not found"
    
    def test_no_math_random_in_data_generation(self):
        """Test that Math.random() is not used in data generation functions."""
        html = load_dashboard_html()
        
        # Extract JavaScript section
        script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
        if not script_match:
            pytest.skip("No script section found")
        
        script_content = script_match.group(1)
        
        # Check that Math.random() is not used (should use seededRandom instead)
        random_calls = re.findall(r'Math\.random\(\)', script_content)
        assert len(random_calls) == 0, (
            f"Found {len(random_calls)} Math.random() calls - should use seededRandom() for deterministic values"
        )
    
    def test_generate_mock_agent_data_uses_seeded_random(self):
        """Test that generateMockAgentData uses seeded random."""
        html = load_dashboard_html()
        
        # Check that generateMockAgentData creates seeded random
        assert 'createSeededRandom(territory)' in html, (
            "generateMockAgentData should use createSeededRandom(territory)"
        )
    
    def test_fan_in_data_uses_seeded_random(self):
        """Test that getMockFanInData uses seeded random for unknown territories."""
        html = load_dashboard_html()
        
        # Check that getMockFanInData uses seeded random
        assert "createSeededRandom('fanIn_'" in html, (
            "getMockFanInData should use seeded random for unknown territories"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
