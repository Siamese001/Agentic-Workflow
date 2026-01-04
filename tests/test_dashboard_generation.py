#!/usr/bin/env python3
"""
Unit tests for dashboard generation.
These tests MUST pass before any dashboard update is allowed.
"""
import unittest
import json
import re
from pathlib import Path
from html.parser import HTMLParser


class DashboardHTMLParser(HTMLParser):
    """Parse HTML to validate structure."""
    def __init__(self):
        super().__init__()
        self.elements = {}
        self.scripts = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if 'id' in attrs_dict:
            self.elements[attrs_dict['id']] = tag
        if tag == 'script':
            self.in_script = True
            
    def handle_data(self, data):
        if hasattr(self, 'in_script') and self.in_script:
            self.scripts.append(data)
            
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False


class TestDashboardGeneration(unittest.TestCase):
    """Test suite for dashboard generation - must pass before updates."""
    
    @classmethod
    def setUpClass(cls):
        """Load the dashboard template and generated file."""
        cls.template_path = Path(__file__).parent.parent / "agentic_core" / "L5_safety" / "validators" / "dashboard_template.html"
        cls.output_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        
        # Load template
        if cls.template_path.exists():
            with open(cls.template_path, 'r', encoding='utf-8') as f:
                cls.template_content = f.read()
        else:
            cls.template_content = None
            
        # Load generated dashboard if exists
        if cls.output_path.exists():
            with open(cls.output_path, 'r', encoding='utf-8') as f:
                cls.dashboard_content = f.read()
        else:
            cls.dashboard_content = None
    
    def test_01_template_exists(self):
        """Test 1: Template file must exist."""
        self.assertTrue(
            self.template_path.exists(),
            f"Dashboard template not found at {self.template_path}"
        )
    
    def test_02_template_has_required_elements(self):
        """Test 2: Template must have all required DOM elements."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        
        required_elements = [
            'kpiGrid',
            'riskMatrix',
            'interviewQuestions',
            'recommendationsList',
            'macroObservations',
            'metricObservations',
            'lastUpdated'
        ]
        
        for element_id in required_elements:
            self.assertIn(
                f'id="{element_id}"',
                self.template_content,
                f"Required element '{element_id}' not found in template"
            )

    def test_02b_template_code_quality_has_sub_territory_column(self):
        """Template Code Quality table must include Sub-Territory column."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        self.assertIn(
            'Sub-Territory within the territory',
            self.template_content,
            "Sub-Territory column not found in Code Quality table"
        )

    def test_02c_template_didactic_config_observability_are_territories(self):
        """Template should clarify Config/Observability are territories (rows), not table columns."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        self.assertIn(
            'Config</strong> and <strong>Observability</strong> are territories too (rows), not special table columns.',
            self.template_content,
            "Didactic clarification about Config/Observability as territories not found"
        )

    def test_02d_template_agents_tools_column_present(self):
        """Template Territory Summary should include Agents / Tools header and legend."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        self.assertIn(
            '>Agents / Tools<',
            self.template_content,
            "Agents / Tools column header not found in template"
        )
        self.assertIn(
            '<strong>Agents / Tools:</strong>',
            self.template_content,
            "Agents / Tools legend not found in template"
        )
    
    def test_03_template_has_data_injection_points(self):
        """Test 3: Template must have data injection placeholders."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        
        required_placeholders = [
            'const dashboardData = [];',
            'const recommendationsData = [];',
            'const lastUpdatedStr = "";',
            'const gaugeData = {};'
        ]
        
        for placeholder in required_placeholders:
            self.assertIn(
                placeholder,
                self.template_content,
                f"Data injection placeholder '{placeholder}' not found in template"
            )
    
    def test_04_template_has_required_functions(self):
        """Test 4: Template must define all required JavaScript functions."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        
        required_functions = [
            'function renderKPIBoxes(',
            'function renderHealthChart(',
            'function renderHealingChart(',
            'function renderRiskMatrix(',
            'function renderComplianceChart(',
            'function renderObservabilityChart(',
            'function renderComplexityChart(',
            'function renderInterviewQuestions(',
            'function renderRecommendations(',
            'function renderStrategicObservations(',
            'function loadData('
        ]
        
        for func in required_functions:
            self.assertIn(
                func,
                self.template_content,
                f"Required function '{func}' not defined in template"
            )
    
    def test_05_template_calls_loadData(self):
        """Test 5: Template must call loadData() on page load."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        self.assertIn(
            'loadData();',
            self.template_content,
            "loadData() is not called in template"
        )
    
    def test_06_template_no_gauge_rendering(self):
        """Test 6: Template must NOT call gauge rendering functions (they cause errors)."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        
        # These functions should NOT be called in loadData
        forbidden_calls = [
            'renderHealthGauge(',
            'renderComplianceGauge('
        ]
        
        # Extract loadData function
        loaddata_match = re.search(
            r'function loadData\(\).*?\n\s*\}',
            self.template_content,
            re.DOTALL
        )
        
        if loaddata_match:
            loaddata_code = loaddata_match.group(0)
            for call in forbidden_calls:
                self.assertNotIn(
                    call,
                    loaddata_code,
                    f"Forbidden call '{call}' found in loadData() - this causes rendering errors"
                )
    
    def test_07_template_has_plotly_cdn(self):
        """Test 7: Template must include Plotly.js CDN."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        self.assertIn(
            'plotly',
            self.template_content.lower(),
            "Plotly.js CDN not found in template"
        )
    
    def test_08_template_has_auto_refresh(self):
        """Test 8: Template must have auto-refresh meta tag set to 30 seconds."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        self.assertIn(
            'content="30"',
            self.template_content,
            "Auto-refresh meta tag not set to 30 seconds"
        )
    
    def test_09_template_has_all_tabs(self):
        """Test 9: Template must have all 6 navigation tabs."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        
        required_tabs = [
            'data-target="executive"',
            'data-target="recommendations"',
            'data-target="interview"'
        ]
        
        for tab in required_tabs:
            self.assertIn(
                tab,
                self.template_content,
                f"Required tab '{tab}' not found in template"
            )
    
    def test_10_generated_dashboard_data_injected(self):
        """Test 10: Generated dashboard must have data injected (not empty arrays)."""
        if self.dashboard_content is None:
            self.skipTest("Generated dashboard not found - run gen_dashboard.py first")
        
        # Check that data arrays are NOT empty
        self.assertNotIn(
            'const dashboardData = [];',
            self.dashboard_content,
            "dashboardData was not injected - still empty array"
        )
        
        self.assertNotIn(
            'const recommendationsData = [];',
            self.dashboard_content,
            "recommendationsData was not injected - still empty array"
        )
    
    def test_11_generated_dashboard_has_valid_json(self):
        """Test 11: Generated dashboard must have valid JSON data."""
        if self.dashboard_content is None:
            self.skipTest("Generated dashboard not found - run gen_dashboard.py first")
        
        # Extract dashboardData
        match = re.search(
            r'const dashboardData = (\[.*?\]);',
            self.dashboard_content,
            re.DOTALL
        )
        
        if match:
            try:
                data = json.loads(match.group(1))
                self.assertIsInstance(data, list, "dashboardData is not a list")
                self.assertGreater(len(data), 0, "dashboardData is empty")
                
                # Check TOTAL row exists
                total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
                self.assertIsNotNone(total_row, "TOTAL row not found in dashboardData")
                
                # Check required fields
                required_fields = ['Total', 'Health', 'Invocation %', 'Test %', 'Avg CC', 'Risk']
                for field in required_fields:
                    self.assertIn(
                        field,
                        total_row,
                        f"Required field '{field}' not found in TOTAL row"
                    )
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON in dashboardData: {e}")
    
    def test_12_template_css_variables_defined(self):
        """Test 12: Template must define all required CSS variables."""
        self.assertIsNotNone(self.template_content, "Template content not loaded")
        
        required_css_vars = [
            '--primary',
            '--success',
            '--warning',
            '--danger',
            '--background',
            '--card-bg',
            '--border',
            '--text',
            '--text-light'
        ]
        
        for var in required_css_vars:
            self.assertIn(
                var,
                self.template_content,
                f"Required CSS variable '{var}' not defined in template"
            )


def run_dashboard_tests():
    """Run all dashboard tests and return True if all pass."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDashboardGeneration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_dashboard_tests()
    sys.exit(0 if success else 1)
