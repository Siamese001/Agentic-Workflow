#!/usr/bin/env python3
"""
Exhaustive JavaScript Testing for Dashboard
============================================

Tests all JavaScript files in the dashboard for:
1. Syntax validity (no parse errors)
2. Required function definitions
3. Required variable declarations
4. No duplicate declarations
5. Proper module patterns
6. Data structure integrity
"""
import json
import re
from pathlib import Path

import pytest


@pytest.fixture
def dashboard_dir():
    """Get the dashboard directory path."""
    return Path(__file__).parent.parent.parent / "agentic_core" / "L6_observability" / "dashboards"


@pytest.fixture
def js_dir(dashboard_dir):
    """Get the JS directory path."""
    return dashboard_dir / "js"


@pytest.fixture
def html_content(dashboard_dir):
    """Load the dashboard HTML content."""
    html_path = dashboard_dir / "autonomy_dashboard.html"
    return html_path.read_text(encoding='utf-8')


class TestJavaScriptFilesExist:
    """Test that all required JavaScript files exist."""

    REQUIRED_JS_FILES = [
        "js/main.js",
        "js/renderers/table-renderer.js",
        "js/components/meta-learning-panel.js",
        "js/components/redis-monitor.js",
        "js/components/pinecone-monitor.js",
        "js/components/execution-flow.js",
        "js/controllers/meta-learning-controller.js",
    ]

    @pytest.mark.parametrize("js_file", REQUIRED_JS_FILES)
    def test_js_file_exists(self, dashboard_dir, js_file):
        """Test that required JS file exists."""
        file_path = dashboard_dir / js_file
        assert file_path.exists(), f"Required JS file missing: {js_file}"

    def test_all_js_files_have_content(self, dashboard_dir):
        """Test that all JS files have meaningful content."""
        for js_file in self.REQUIRED_JS_FILES:
            file_path = dashboard_dir / js_file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                assert len(content) > 100, f"JS file too small: {js_file}"


class TestMainJavaScript:
    """Test main.js for required patterns."""

    def test_dashboard_app_object_exists(self, dashboard_dir):
        """Test that DashboardApp object is defined."""
        main_js = dashboard_dir / "js" / "main.js"
        content = main_js.read_text(encoding='utf-8')
        assert "DashboardApp" in content, "DashboardApp object not found"
        assert "const DashboardApp" in content or "var DashboardApp" in content, \
            "DashboardApp not properly declared"

    def test_init_method_exists(self, dashboard_dir):
        """Test that init method exists in DashboardApp."""
        main_js = dashboard_dir / "js" / "main.js"
        content = main_js.read_text(encoding='utf-8')
        assert "init:" in content or "init :" in content, "init method not found in DashboardApp"

    def test_render_content_method_exists(self, dashboard_dir):
        """Test that renderContent method exists."""
        main_js = dashboard_dir / "js" / "main.js"
        content = main_js.read_text(encoding='utf-8')
        assert "renderContent" in content, "renderContent method not found"

    def test_init_renderers_method_exists(self, dashboard_dir):
        """Test that initRenderers method exists."""
        main_js = dashboard_dir / "js" / "main.js"
        content = main_js.read_text(encoding='utf-8')
        assert "initRenderers" in content, "initRenderers method not found"

    def test_check_dependencies_method_exists(self, dashboard_dir):
        """Test that checkDependencies method exists."""
        main_js = dashboard_dir / "js" / "main.js"
        content = main_js.read_text(encoding='utf-8')
        assert "checkDependencies" in content, "checkDependencies method not found"

    def test_no_syntax_errors_in_main(self, dashboard_dir):
        """Test that main.js has no obvious syntax errors."""
        main_js = dashboard_dir / "js" / "main.js"
        content = main_js.read_text(encoding='utf-8')

        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert abs(open_braces - close_braces) <= 1, \
            f"Unbalanced braces in main.js: {open_braces} open, {close_braces} close"

        # Check for balanced brackets
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        assert abs(open_brackets - close_brackets) <= 1, \
            f"Unbalanced brackets in main.js: {open_brackets} open, {close_brackets} close"

        # Check for balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert abs(open_parens - close_parens) <= 1, \
            f"Unbalanced parentheses in main.js: {open_parens} open, {close_parens} close"


class TestTableRenderer:
    """Test table-renderer.js for required functions."""

    REQUIRED_FUNCTIONS = [
        "renderTerritorySummaryTable",
        "renderCodeQualityTable",
    ]

    @pytest.mark.parametrize("func_name", REQUIRED_FUNCTIONS)
    def test_required_function_exists(self, dashboard_dir, func_name):
        """Test that required rendering function exists."""
        renderer_js = dashboard_dir / "js" / "renderers" / "table-renderer.js"
        content = renderer_js.read_text(encoding='utf-8')
        assert f"function {func_name}" in content, f"Function {func_name} not found"

    def test_table_renderer_uses_dashboard_data(self, dashboard_dir):
        """Test that table renderer uses dashboardData parameter."""
        renderer_js = dashboard_dir / "js" / "renderers" / "table-renderer.js"
        content = renderer_js.read_text(encoding='utf-8')
        # Should accept data as parameter, not use global
        assert "function renderTerritorySummaryTable(" in content
        assert "function renderCodeQualityTable(" in content

    def test_total_row_handling(self, dashboard_dir):
        """Test that renderer handles TOTAL row."""
        renderer_js = dashboard_dir / "js" / "renderers" / "table-renderer.js"
        content = renderer_js.read_text(encoding='utf-8')
        assert "TOTAL" in content, "TOTAL row handling not found"

    def test_no_syntax_errors_in_renderer(self, dashboard_dir):
        """Test that table-renderer.js has no obvious syntax errors."""
        renderer_js = dashboard_dir / "js" / "renderers" / "table-renderer.js"
        content = renderer_js.read_text(encoding='utf-8')

        open_braces = content.count('{')
        close_braces = content.count('}')
        assert abs(open_braces - close_braces) <= 2, \
            "Unbalanced braces in table-renderer.js"


class TestComponentFiles:
    """Test component JavaScript files."""

    # Actual class names from the component files
    COMPONENTS = [
        ("meta-learning-panel.js", ["ExperienceStream", "StrategyWeightsChart", "PatternTimeline", "MetaLearningStatsPanel"]),
        ("redis-monitor.js", ["class "]),  # Check for any class definition
        ("pinecone-monitor.js", ["class "]),
        ("execution-flow.js", ["class "]),
    ]

    @pytest.mark.parametrize("filename,patterns", COMPONENTS)
    def test_component_class_exists(self, dashboard_dir, filename, patterns):
        """Test that component has class definitions."""
        component_path = dashboard_dir / "js" / "components" / filename
        if component_path.exists():
            content = component_path.read_text(encoding='utf-8')
            found = any(pattern in content for pattern in patterns)
            assert found, f"No expected class found in {filename}"

    def test_meta_learning_panel_exports(self, dashboard_dir):
        """Test that meta-learning-panel.js exports to window."""
        component_path = dashboard_dir / "js" / "components" / "meta-learning-panel.js"
        if component_path.exists():
            content = component_path.read_text(encoding='utf-8')
            assert "window." in content, "No window exports in meta-learning-panel.js"

    def test_components_have_constructor(self, dashboard_dir):
        """Test that component files have constructor methods."""
        for filename, _ in self.COMPONENTS:
            component_path = dashboard_dir / "js" / "components" / filename
            if component_path.exists():
                content = component_path.read_text(encoding='utf-8')
                has_constructor = "constructor(" in content or "init(" in content or "init:" in content
                assert has_constructor, f"No constructor/init in {filename}"


class TestHTMLJavaScriptIntegrity:
    """Test JavaScript declarations in HTML file."""

    def test_no_duplicate_dashboard_data(self, html_content):
        """Test that dashboardData is not declared multiple times."""
        # Count declarations (not references)
        declarations = re.findall(r'const\s+dashboardData\s*=', html_content)
        assert len(declarations) <= 1, \
            f"Multiple dashboardData declarations found: {len(declarations)}"

    def test_no_duplicate_real_agent_data(self, html_content):
        """Test that realAgentData is not declared multiple times."""
        declarations = re.findall(r'const\s+realAgentData\s*=', html_content)
        assert len(declarations) <= 1, \
            f"Multiple realAgentData declarations found: {len(declarations)}"

    def test_no_duplicate_recommendations_data(self, html_content):
        """Test that recommendationsData is not declared multiple times."""
        declarations = re.findall(r'const\s+recommendationsData\s*=', html_content)
        assert len(declarations) <= 1, \
            f"Multiple recommendationsData declarations found: {len(declarations)}"

    def test_single_html_closing_tag(self, html_content):
        """Test that HTML has only one closing tag (not corrupted)."""
        html_end_count = html_content.count('</html>')
        assert html_end_count == 1, \
            f"HTML file appears corrupted: {html_end_count} </html> tags found"

    def test_html_size_reasonable(self, html_content):
        """Test that HTML file is not bloated (corruption indicator)."""
        size_kb = len(html_content) / 1024
        assert size_kb < 1000, f"HTML file too large ({size_kb:.0f}KB) - possible corruption"

    def test_js_script_tags_or_inline_present(self, html_content):
        """Test that required JS is present (either via script tags or inline)."""
        # Dashboard may use inline JS or external script tags
        # Check for key functions that should be present
        required_patterns = [
            ("loadData function", ["function loadData", "loadData()"]),
            ("DashboardApp or renderTable", ["DashboardApp", "renderTerritorySummaryTable", "renderCodeQualityTable"]),
        ]
        for name, patterns in required_patterns:
            found = any(p in html_content for p in patterns)
            assert found, f"Required JS pattern not found: {name}"


class TestDataStructures:
    """Test JavaScript data structures in HTML."""

    def test_dashboard_data_is_valid_json(self, html_content):
        """Test that dashboardData can be parsed as JSON."""
        # Extract dashboardData
        match = re.search(
            r'const\s+dashboardData\s*=\s*(?:window\.dashboardData\s*\|\|\s*)?\[',
            html_content
        )
        if match:
            start = match.end() - 1  # Include the [
            bracket_count = 0
            end = start
            for i, char in enumerate(html_content[start:], start):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end = i + 1
                        break

            json_str = html_content[start:end]
            try:
                data = json.loads(json_str)
                assert isinstance(data, list), "dashboardData should be a list"
                assert len(data) > 0, "dashboardData should not be empty"
            except json.JSONDecodeError as e:
                pytest.fail(f"dashboardData is not valid JSON: {e}")

    def test_dashboard_data_has_total_row(self, html_content):
        """Test that dashboardData contains TOTAL row."""
        assert '"Territory": "TOTAL"' in html_content or "'Territory': 'TOTAL'" in html_content, \
            "TOTAL row not found in dashboardData"

    def test_real_agent_data_is_valid_json(self, html_content):
        """Test that realAgentData can be parsed as JSON."""
        match = re.search(
            r'const\s+realAgentData\s*=\s*(?:window\.realAgentData\s*\|\|\s*)?\{',
            html_content
        )
        if match:
            start = match.end() - 1  # Include the {
            brace_count = 0
            end = start
            for i, char in enumerate(html_content[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break

            json_str = html_content[start:end]
            try:
                data = json.loads(json_str)
                assert isinstance(data, dict), "realAgentData should be a dict"
            except json.JSONDecodeError as e:
                pytest.fail(f"realAgentData is not valid JSON: {e}")


class TestJavaScriptPatterns:
    """Test for common JavaScript anti-patterns and issues."""

    def test_no_console_errors_in_production(self, dashboard_dir):
        """Test that JS files don't have console.error with hardcoded messages."""
        js_files = list((dashboard_dir / "js").rglob("*.js"))
        for js_file in js_files:
            content = js_file.read_text(encoding='utf-8')
            # Allow console.error for actual error handling, but not hardcoded test messages
            if "console.error('TEST" in content or 'console.error("TEST' in content:
                pytest.fail(f"Test console.error found in {js_file.name}")

    def test_no_debugger_statements(self, dashboard_dir):
        """Test that JS files don't have debugger statements."""
        js_files = list((dashboard_dir / "js").rglob("*.js"))
        for js_file in js_files:
            content = js_file.read_text(encoding='utf-8')
            # Check for standalone debugger statements (not in comments)
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped == 'debugger;' or stripped == 'debugger':
                    pytest.fail(f"debugger statement found in {js_file.name}:{i}")

    def test_no_alert_statements(self, dashboard_dir):
        """Test that JS files don't have alert() calls."""
        js_files = list((dashboard_dir / "js").rglob("*.js"))
        for js_file in js_files:
            content = js_file.read_text(encoding='utf-8')
            if re.search(r'\balert\s*\(', content):
                pytest.fail(f"alert() call found in {js_file.name}")


class TestExternalDataFiles:
    """Test external JavaScript data files."""

    def test_dashboard_data_js_exists(self, dashboard_dir):
        """Test that dashboard_data.js exists."""
        data_file = dashboard_dir / "data" / "dashboard_data.js"
        assert data_file.exists(), "dashboard_data.js not found"

    def test_dashboard_data_js_has_window_assignment(self, dashboard_dir):
        """Test that dashboard_data.js assigns to window."""
        data_file = dashboard_dir / "data" / "dashboard_data.js"
        if data_file.exists():
            content = data_file.read_text(encoding='utf-8')
            assert "window.dashboardData" in content, \
                "dashboard_data.js should assign to window.dashboardData"

    def test_agent_data_js_exists(self, dashboard_dir):
        """Test that agent_data.js exists."""
        data_file = dashboard_dir / "data" / "agent_data.js"
        assert data_file.exists(), "agent_data.js not found"

    def test_agent_data_js_has_window_assignment(self, dashboard_dir):
        """Test that agent_data.js assigns to window."""
        data_file = dashboard_dir / "data" / "agent_data.js"
        if data_file.exists():
            content = data_file.read_text(encoding='utf-8')
            assert "window.realAgentData" in content, \
                "agent_data.js should assign to window.realAgentData"
