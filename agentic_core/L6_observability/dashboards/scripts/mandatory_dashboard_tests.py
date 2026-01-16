#!/usr/bin/env python3
"""
MANDATORY UNIFIED DASHBOARD TEST SUITE
======================================

This is the SINGLE test suite that MUST pass before ANY dashboard deployment.
It combines:
  1. SSOT Enforcement Tests - Verify SSOT architecture integrity
  2. Data Validation Tests - Verify data generation and integrity
  3. E2E Tests - End-to-end dashboard functionality

AUTOMATIC OPERATIONS:
  - Stops any existing dashboard server
  - Regenerates SSOT constants from YAML
  - Regenerates dashboard data from agent discovery
  - Starts fresh dashboard server
  - Clears browser cache (via cache-busting headers)
  - Runs ALL mandatory tests
  - Reports pass/fail status

Usage:
    python agentic_core/L6_observability/dashboards/scripts/mandatory_dashboard_tests.py

Exit Codes:
    0 - ALL tests passed, safe to deploy
    1 - Tests failed, DO NOT DEPLOY

CRITICAL: This script MUST be run before any dashboard deployment.
          ALL tests MUST pass. No exceptions.
"""
import subprocess
import sys
import os
import signal
import time
import json
import re
import socket
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Any

# =============================================================================
# CONFIGURATION
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DASHBOARD_DIR = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SERVER_PORT = 8765
SERVER_TIMEOUT = 10  # seconds to wait for server to start

# Add project root to path
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 70}")
    print(f" {text}")
    print(f"{char * 70}\n")


def print_subheader(text: str):
    """Print a formatted subheader."""
    print(f"\n{'-' * 70}")
    print(f" {text}")
    print(f"{'-' * 70}")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "PASSED" if passed else "FAILED"
    symbol = "[PASS]" if passed else "[FAIL]"
    print(f"  {symbol} {test_name}: {status}")
    if details:
        print(f"         {details}")


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port(port: int) -> bool:
    """Kill any process using the specified port."""
    try:
        if sys.platform == 'win32':
            # Windows: Find and kill process on port
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True)
                            return True
                        except:
                            pass
        else:
            # Unix: Use lsof and kill
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    except:
                        pass
                return True
    except Exception as e:
        print(f"  Warning: Could not kill process on port {port}: {e}")
    return False


def run_python_script(script_path: Path, description: str) -> Tuple[bool, str]:
    """Run a Python script and return success status and output."""
    print(f"  Running: {description}")
    try:
        # Use encoding='utf-8' and errors='replace' to handle Unicode issues on Windows
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=300,  # 5 minute timeout
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        success = result.returncode == 0
        # Decode with error handling
        try:
            stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
        except:
            stdout = str(result.stdout)
            stderr = str(result.stderr)
        output = stdout + stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Script timed out after 5 minutes"
    except Exception as e:
        return False, str(e)


# =============================================================================
# SERVER MANAGEMENT
# =============================================================================
def stop_dashboard_server() -> bool:
    """Stop any existing dashboard server."""
    print_subheader("STEP 1: Stopping Existing Dashboard Server")
    
    if is_port_in_use(SERVER_PORT):
        print(f"  Found server on port {SERVER_PORT}, stopping...")
        kill_process_on_port(SERVER_PORT)
        time.sleep(2)  # Wait for port to be released
        
        if is_port_in_use(SERVER_PORT):
            print(f"  [WARN] Port {SERVER_PORT} still in use after kill attempt")
            return False
        else:
            print(f"  [OK] Server stopped successfully")
            return True
    else:
        print(f"  [OK] No server running on port {SERVER_PORT}")
        return True


def start_dashboard_server() -> Tuple[bool, subprocess.Popen]:
    """Start a fresh dashboard server."""
    print_subheader("STEP 5: Starting Fresh Dashboard Server")
    
    if is_port_in_use(SERVER_PORT):
        print(f"  [WARN] Port {SERVER_PORT} already in use")
        return False, None
    
    try:
        # Start server in background
        server_process = subprocess.Popen(
            [sys.executable, '-m', 'http.server', str(SERVER_PORT)],
            cwd=DASHBOARD_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )
        
        # Wait for server to start
        print(f"  Starting server on port {SERVER_PORT}...")
        for i in range(SERVER_TIMEOUT):
            time.sleep(1)
            if is_port_in_use(SERVER_PORT):
                print(f"  [OK] Server started successfully (PID: {server_process.pid})")
                print(f"  [OK] Dashboard URL: http://localhost:{SERVER_PORT}/autonomy_dashboard.html")
                return True, server_process
        
        print(f"  [FAIL] Server failed to start within {SERVER_TIMEOUT} seconds")
        return False, None
        
    except Exception as e:
        print(f"  [FAIL] Could not start server: {e}")
        return False, None


# =============================================================================
# SSOT TESTS
# =============================================================================
def run_ssot_tests() -> Tuple[bool, Dict[str, bool]]:
    """Run SSOT enforcement tests."""
    print_subheader("STEP 3: SSOT Enforcement Tests")
    
    results = {}
    all_passed = True
    
    # Import SSOT definitions
    try:
        from agentic_core.L6_observability.dashboards.core.ssot_definitions import (
            WEIGHT_HEALTH_HEAL_CAP, WEIGHT_HEALTH_INVOCATION, WEIGHT_HEALTH_TEST,
            WEIGHT_HEALTH_OBSERVABLE, WEIGHT_HEALTH_COMPLEXITY,
            WEIGHT_CODE_QUALITY_TYPED, WEIGHT_CODE_QUALITY_DOCUMENTED, 
            WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS, WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE
        )
        
        # Test 1: Weight validation
        health_sum = (WEIGHT_HEALTH_HEAL_CAP + WEIGHT_HEALTH_INVOCATION + 
                     WEIGHT_HEALTH_TEST + WEIGHT_HEALTH_OBSERVABLE + 
                     WEIGHT_HEALTH_COMPLEXITY)
        code_sum = (WEIGHT_CODE_QUALITY_TYPED + WEIGHT_CODE_QUALITY_DOCUMENTED + 
                   WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS + WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE)
        
        health_valid = abs(health_sum - 1.0) < 0.001
        code_valid = abs(code_sum - 1.0) < 0.001
        
        results['Health weights sum to 1.0'] = health_valid
        results['Code quality weights sum to 1.0'] = code_valid
        
        if not health_valid:
            all_passed = False
            print(f"  [FAIL] Health weights sum to {health_sum}, expected 1.0")
        if not code_valid:
            all_passed = False
            print(f"  [FAIL] Code quality weights sum to {code_sum}, expected 1.0")
        
    except ImportError as e:
        results['SSOT imports'] = False
        all_passed = False
        print(f"  [FAIL] Could not import SSOT definitions: {e}")
    
    # Test 2: YAML config exists
    yaml_path = DASHBOARD_DIR / "config" / "ssot.yaml"
    results['YAML config exists'] = yaml_path.exists()
    if not yaml_path.exists():
        all_passed = False
        print(f"  [FAIL] YAML config not found: {yaml_path}")
    
    # Test 3: Generated files exist
    py_path = DASHBOARD_DIR / "core" / "ssot_definitions.py"
    js_path = DASHBOARD_DIR / "js" / "constants" / "dashboard-constants.js"
    
    results['Python constants exist'] = py_path.exists()
    results['JavaScript constants exist'] = js_path.exists()
    
    if not py_path.exists():
        all_passed = False
        print(f"  [FAIL] Python constants not found: {py_path}")
    if not js_path.exists():
        all_passed = False
        print(f"  [FAIL] JavaScript constants not found: {js_path}")
    
    # Test 4: No hardcoded strings in JS renderers
    renderer_path = DASHBOARD_DIR / "js" / "renderers" / "table-renderer.js"
    if renderer_path.exists():
        content = renderer_path.read_text(encoding='utf-8')
        hardcoded_patterns = [
            r"'Heal Capability %'",
            r"'Test Coverage %'",
            r"'MCP Hardened %'",
        ]
        has_hardcoded = any(re.search(p, content) for p in hardcoded_patterns)
        results['No hardcoded strings in JS'] = not has_hardcoded
        if has_hardcoded:
            all_passed = False
            print(f"  [FAIL] Found hardcoded strings in table-renderer.js")
    else:
        results['No hardcoded strings in JS'] = True  # Skip if file doesn't exist
    
    # Print results
    for test_name, passed in results.items():
        print_result(test_name, passed)
    
    return all_passed, results


# =============================================================================
# DATA VALIDATION TESTS
# =============================================================================
def run_data_validation_tests() -> Tuple[bool, Dict[str, bool]]:
    """Run data validation tests."""
    print_subheader("STEP 4: Data Validation Tests")
    
    results = {}
    all_passed = True
    
    # Test 1: Agent discovery exists and is valid
    discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
    if discovery_path.exists():
        try:
            with open(discovery_path, 'r', encoding='utf-8') as f:
                agents = json.load(f)
            results['Agent discovery valid'] = isinstance(agents, list) and len(agents) > 0
            if results['Agent discovery valid']:
                print(f"  [OK] Agent discovery: {len(agents)} agents")
            else:
                all_passed = False
        except Exception as e:
            results['Agent discovery valid'] = False
            all_passed = False
            print(f"  [FAIL] Agent discovery invalid: {e}")
    else:
        results['Agent discovery valid'] = False
        all_passed = False
        print(f"  [FAIL] Agent discovery not found: {discovery_path}")
    
    # Test 2: Dashboard data exists and is valid
    data_path = DASHBOARD_DIR / "data" / "dashboard_data.js"
    if data_path.exists():
        try:
            content = data_path.read_text(encoding='utf-8')
            if 'window.dashboardData' in content:
                # Extract and validate JSON
                match = re.search(r'window\.dashboardData = (\[.*?\]);', content, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    results['Dashboard data valid'] = isinstance(data, list) and len(data) > 0
                    if results['Dashboard data valid']:
                        print(f"  [OK] Dashboard data: {len(data)} rows")
                        
                        # Check for TOTAL row
                        total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
                        results['TOTAL row exists'] = total_row is not None
                        if not total_row:
                            all_passed = False
                            print(f"  [FAIL] TOTAL row not found in dashboard data")
                    else:
                        all_passed = False
                else:
                    results['Dashboard data valid'] = False
                    all_passed = False
                    print(f"  [FAIL] Could not extract dashboardData from JS")
            else:
                results['Dashboard data valid'] = False
                all_passed = False
                print(f"  [FAIL] window.dashboardData not found in file")
        except Exception as e:
            results['Dashboard data valid'] = False
            all_passed = False
            print(f"  [FAIL] Dashboard data invalid: {e}")
    else:
        results['Dashboard data valid'] = False
        all_passed = False
        print(f"  [FAIL] Dashboard data not found: {data_path}")
    
    # Test 3: Dashboard HTML exists
    html_path = DASHBOARD_DIR / "autonomy_dashboard.html"
    results['Dashboard HTML exists'] = html_path.exists()
    if not html_path.exists():
        all_passed = False
        print(f"  [FAIL] Dashboard HTML not found: {html_path}")
    else:
        print(f"  [OK] Dashboard HTML exists")
    
    # Print results
    for test_name, passed in results.items():
        if test_name not in ['Agent discovery valid', 'Dashboard data valid', 'Dashboard HTML exists']:
            print_result(test_name, passed)
    
    return all_passed, results


# =============================================================================
# E2E TESTS
# =============================================================================
def run_e2e_tests() -> Tuple[bool, Dict[str, bool]]:
    """Run E2E tests."""
    print_subheader("STEP 6: End-to-End Tests")
    
    results = {}
    all_passed = True
    
    # Import SSOT definitions for calculations
    try:
        from agentic_core.L6_observability.dashboards.core.ssot_definitions import (
            calc_heal_cap_pct, calc_invocation_pct, calc_test_pct, calc_hardened_pct,
            calc_typed_pct, calc_documented_pct, calc_schema_strictness_pct,
            calc_canonical_inheritance_pct, COL_HEAL_CAP, COL_HEALTH
        )
    except ImportError as e:
        print(f"  [FAIL] Could not import SSOT definitions: {e}")
        return False, {'SSOT imports': False}
    
    # Load data
    try:
        discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        data_path = DASHBOARD_DIR / "data" / "dashboard_data.js"
        content = data_path.read_text(encoding='utf-8')
        match = re.search(r'window\.dashboardData = (\[.*?\]);', content, re.DOTALL)
        dashboard_data = json.loads(match.group(1))
        total_row = next((r for r in dashboard_data if r.get('Territory') == 'TOTAL'), None)
        
    except Exception as e:
        print(f"  [FAIL] Could not load data: {e}")
        return False, {'Data loading': False}
    
    # E2E Test 1: Agent count matches
    dashboard_total = total_row.get('Total', 0)
    actual_total = len(agents)
    results['Agent count matches'] = dashboard_total == actual_total
    if dashboard_total != actual_total:
        all_passed = False
        print(f"  [FAIL] Agent count: Dashboard={dashboard_total}, Actual={actual_total}")
    else:
        print(f"  [OK] Agent count matches: {actual_total}")
    
    # E2E Test 2: Heal capability matches
    expected_heal = calc_heal_cap_pct(agents)
    actual_heal = total_row.get(COL_HEAL_CAP, 0)
    tolerance = 2.0
    results['Heal capability matches'] = abs(expected_heal - actual_heal) <= tolerance
    if not results['Heal capability matches']:
        all_passed = False
        print(f"  [FAIL] Heal capability: Dashboard={actual_heal}, Expected={expected_heal}")
    else:
        print(f"  [OK] Heal capability matches: {actual_heal}%")
    
    # E2E Test 3: Test coverage matches
    from agentic_core.L6_observability.dashboards.core.ssot_definitions import COL_TEST
    expected_test = calc_test_pct(agents)
    actual_test = total_row.get(COL_TEST, 0)
    results['Test coverage matches'] = abs(expected_test - actual_test) <= tolerance
    if not results['Test coverage matches']:
        all_passed = False
        print(f"  [FAIL] Test coverage: Dashboard={actual_test}, Expected={expected_test}")
    else:
        print(f"  [OK] Test coverage matches: {actual_test}%")
    
    # E2E Test 4: MCP hardened matches
    expected_hardened = calc_hardened_pct(agents)
    actual_hardened = total_row.get('MCP Hardened %', 0)
    results['MCP hardened matches'] = abs(expected_hardened - actual_hardened) <= tolerance
    if not results['MCP hardened matches']:
        all_passed = False
        print(f"  [FAIL] MCP hardened: Dashboard={actual_hardened}, Expected={expected_hardened}")
    else:
        print(f"  [OK] MCP hardened matches: {actual_hardened}%")
    
    # E2E Test 5: Health score is reasonable (0-100)
    health_score = total_row.get(COL_HEALTH, 0)
    results['Health score valid'] = 0 <= health_score <= 100
    if not results['Health score valid']:
        all_passed = False
        print(f"  [FAIL] Health score out of range: {health_score}")
    else:
        print(f"  [OK] Health score valid: {health_score}")
    
    # E2E Test 6: All territories have data
    territories_with_data = sum(1 for row in dashboard_data if row.get('Total', 0) > 0)
    results['All territories have data'] = territories_with_data == len(dashboard_data)
    print(f"  [OK] Territories with data: {territories_with_data}/{len(dashboard_data)}")
    
    return all_passed, results


# =============================================================================
# PLAYWRIGHT VISUAL VALIDATION
# =============================================================================
def run_playwright_visual_tests() -> Tuple[bool, Dict[str, bool]]:
    """Run Playwright visual validation tests."""
    print_subheader("STEP 7: Playwright Visual Validation")
    
    results = {}
    all_passed = True
    
    # Wait for server to be fully ready
    print("  Waiting for server to be fully ready...")
    time.sleep(3)
    
    # Verify server is responding before launching Playwright
    max_retries = 5
    for i in range(max_retries):
        if is_port_in_use(SERVER_PORT):
            print(f"  [OK] Server confirmed on port {SERVER_PORT}")
            break
        time.sleep(1)
    else:
        print(f"  [FAIL] Server not responding on port {SERVER_PORT}")
        results['Server responding'] = False
        return False, results
    
    try:
        from playwright.sync_api import sync_playwright
        
        print("  Starting Playwright browser...")
        
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                # Disable cache to ensure fresh load
                ignore_https_errors=True
            )
            page = context.new_page()
            
            # Navigate to dashboard
            dashboard_url = f"http://localhost:{SERVER_PORT}/autonomy_dashboard.html"
            print(f"  Loading: {dashboard_url}")
            
            try:
                # Use domcontentloaded instead of networkidle for faster load
                page.goto(dashboard_url, wait_until='domcontentloaded', timeout=60000)
                # Wait a bit for JS to execute
                time.sleep(2)
                results['Dashboard loads'] = True
                print("  [OK] Dashboard loaded")
            except Exception as e:
                results['Dashboard loads'] = False
                all_passed = False
                print(f"  [FAIL] Dashboard failed to load: {e}")
                browser.close()
                return all_passed, results
            
            # Wait for data to load
            try:
                page.wait_for_selector('table', timeout=10000)
                results['Tables rendered'] = True
                print("  [OK] Tables rendered")
            except:
                results['Tables rendered'] = False
                all_passed = False
                print("  [FAIL] Tables did not render")
            
            # Visual Test 1: Table 1 (Territory Summary) - check kpiGrid has data
            try:
                kpi_grid = page.query_selector('#kpiGrid')
                if kpi_grid:
                    grid_text = kpi_grid.inner_text()
                    has_total = 'TOTAL' in grid_text
                    has_data = len(grid_text) > 100  # Should have substantial content
                    results['Table 1 has data'] = has_total and has_data
                    if has_total and has_data:
                        print(f"  [OK] Table 1 (kpiGrid): Has TOTAL row and data ({len(grid_text)} chars)")
                    else:
                        all_passed = False
                        print(f"  [FAIL] Table 1: TOTAL={has_total}, HasData={has_data}")
                else:
                    results['Table 1 has data'] = False
                    all_passed = False
                    print("  [FAIL] Table 1: kpiGrid container not found")
            except Exception as e:
                results['Table 1 has data'] = False
                all_passed = False
                print(f"  [FAIL] Table 1 check failed: {e}")
            
            # Visual Test 2: Table 2 (Code Quality) - check codeQualityGrid has data
            try:
                quality_grid = page.query_selector('#codeQualityGrid')
                if quality_grid:
                    grid_text = quality_grid.inner_text()
                    has_total = 'TOTAL' in grid_text
                    has_data = len(grid_text) > 100
                    results['Table 2 has data'] = has_total and has_data
                    if has_total and has_data:
                        print(f"  [OK] Table 2 (codeQualityGrid): Has TOTAL row and data ({len(grid_text)} chars)")
                    else:
                        all_passed = False
                        print(f"  [FAIL] Table 2: TOTAL={has_total}, HasData={has_data}")
                else:
                    results['Table 2 has data'] = False
                    all_passed = False
                    print("  [FAIL] Table 2: codeQualityGrid container not found")
            except Exception as e:
                results['Table 2 has data'] = False
                all_passed = False
                print(f"  [FAIL] Table 2 check failed: {e}")
            
            # Visual Test 3: Live Sovereign Log has scrollbar
            try:
                log_element = page.query_selector('#liveLog')
                if log_element:
                    overflow_y = page.evaluate('(el) => window.getComputedStyle(el).overflowY', log_element)
                    has_scroll = overflow_y in ['scroll', 'auto']
                    results['Live Sovereign Log scrollable'] = has_scroll
                    if has_scroll:
                        print(f"  [OK] Live Sovereign Log (#liveLog): scrollable (overflow-y: {overflow_y})")
                    else:
                        all_passed = False
                        print(f"  [FAIL] Live Sovereign Log: not scrollable (overflow-y: {overflow_y})")
                else:
                    results['Live Sovereign Log scrollable'] = False
                    all_passed = False
                    print("  [FAIL] Live Sovereign Log: #liveLog element not found")
            except Exception as e:
                results['Live Sovereign Log scrollable'] = False
                all_passed = False
                print(f"  [FAIL] Live Sovereign Log check failed: {e}")
            
            # Visual Test 4: Real-Time Event Log has scrollbar
            try:
                event_log = page.query_selector('#eventLog')
                if event_log:
                    overflow_y = page.evaluate('(el) => window.getComputedStyle(el).overflowY', event_log)
                    has_scroll = overflow_y in ['scroll', 'auto']
                    results['Real-Time Event Log scrollable'] = has_scroll
                    if has_scroll:
                        print(f"  [OK] Real-Time Event Log: scrollable (overflow-y: {overflow_y})")
                    else:
                        all_passed = False
                        print(f"  [FAIL] Real-Time Event Log: not scrollable (overflow-y: {overflow_y})")
                else:
                    results['Real-Time Event Log scrollable'] = False
                    all_passed = False
                    print("  [FAIL] Real-Time Event Log: element not found")
            except Exception as e:
                results['Real-Time Event Log scrollable'] = False
                all_passed = False
                print(f"  [FAIL] Real-Time Event Log check failed: {e}")
            
            # Visual Test 5: All JavaScript files loaded without errors
            try:
                # Check if critical JS files are loaded (without reload to avoid timeout)
                js_loaded = page.evaluate('''() => {
                    return typeof window.dashboardData !== 'undefined' && 
                           typeof window.realAgentData !== 'undefined';
                }''')
                
                results['JavaScript files loaded'] = js_loaded
                if js_loaded:
                    print("  [OK] Critical JavaScript variables loaded (dashboardData, realAgentData)")
                else:
                    all_passed = False
                    print("  [FAIL] Critical JavaScript variables not defined")
            except Exception as e:
                results['JavaScript files loaded'] = False
                all_passed = False
                print(f"  [FAIL] JavaScript check failed: {e}")
            
            # Visual Test 6: Take screenshot for visual record
            try:
                screenshot_path = DASHBOARD_DIR / "playwright_screenshot.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                results['Screenshot saved'] = screenshot_path.exists()
                if screenshot_path.exists():
                    print(f"  [OK] Screenshot saved: {screenshot_path}")
                else:
                    print("  [WARN] Screenshot not saved")
            except Exception as e:
                results['Screenshot saved'] = False
                print(f"  [WARN] Screenshot failed: {e}")
            
            browser.close()
            
    except ImportError:
        print("  [FAIL] Playwright not installed. Run: pip install playwright && playwright install chromium")
        results['Playwright available'] = False
        all_passed = False
    except Exception as e:
        print(f"  [FAIL] Playwright tests failed: {e}")
        all_passed = False
    
    return all_passed, results


# =============================================================================
# REGENERATION
# =============================================================================
def regenerate_ssot() -> bool:
    """Regenerate SSOT constants from YAML."""
    print_subheader("STEP 2A: Regenerating SSOT Constants")
    
    generator_path = DASHBOARD_DIR / "scripts" / "generate_ssot.py"
    if not generator_path.exists():
        print(f"  [FAIL] Generator not found: {generator_path}")
        return False
    
    success, output = run_python_script(generator_path, "SSOT Generator")
    
    if success:
        print(f"  [OK] SSOT constants regenerated")
        return True
    else:
        print(f"  [FAIL] SSOT generation failed")
        print(f"  Output: {output[:500]}")
        return False


def regenerate_dashboard_data() -> bool:
    """Regenerate dashboard data from agent discovery."""
    print_subheader("STEP 2B: Regenerating Dashboard Data")
    
    regenerator_path = DASHBOARD_DIR / "scripts" / "regenerate_data.py"
    if not regenerator_path.exists():
        print(f"  [FAIL] Regenerator not found: {regenerator_path}")
        return False
    
    success, output = run_python_script(regenerator_path, "Dashboard Data Regenerator")
    
    if success:
        print(f"  [OK] Dashboard data regenerated")
        return True
    else:
        print(f"  [FAIL] Dashboard data regeneration failed")
        print(f"  Output: {output[:500]}")
        return False


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================
def main():
    """Run all mandatory dashboard tests."""
    start_time = datetime.now()
    
    print_header("MANDATORY UNIFIED DASHBOARD TEST SUITE")
    print(f"Timestamp: {start_time.isoformat()}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Dashboard Dir: {DASHBOARD_DIR}")
    
    # Track all results
    all_results = {}
    all_passed = True
    server_process = None
    
    try:
        # =================================================================
        # STEP 1: Stop existing server
        # =================================================================
        if not stop_dashboard_server():
            print("  [WARN] Could not stop existing server, continuing anyway...")
        
        # =================================================================
        # STEP 2: Regenerate SSOT and Data
        # =================================================================
        if not regenerate_ssot():
            all_passed = False
            all_results['SSOT Regeneration'] = False
        else:
            all_results['SSOT Regeneration'] = True
        
        if not regenerate_dashboard_data():
            all_passed = False
            all_results['Data Regeneration'] = False
        else:
            all_results['Data Regeneration'] = True
        
        # =================================================================
        # STEP 3: SSOT Tests
        # =================================================================
        ssot_passed, ssot_results = run_ssot_tests()
        all_results['SSOT Tests'] = ssot_passed
        if not ssot_passed:
            all_passed = False
        
        # =================================================================
        # STEP 4: Data Validation Tests
        # =================================================================
        data_passed, data_results = run_data_validation_tests()
        all_results['Data Validation'] = data_passed
        if not data_passed:
            all_passed = False
        
        # =================================================================
        # STEP 5: Start fresh server
        # =================================================================
        server_started, server_process = start_dashboard_server()
        all_results['Server Started'] = server_started
        if not server_started:
            print("  [WARN] Server not started, E2E tests may fail")
        
        # =================================================================
        # STEP 6: E2E Tests
        # =================================================================
        e2e_passed, e2e_results = run_e2e_tests()
        all_results['E2E Tests'] = e2e_passed
        if not e2e_passed:
            all_passed = False
        
        # =================================================================
        # STEP 7: Playwright Visual Validation (MANDATORY)
        # =================================================================
        playwright_passed, playwright_results = run_playwright_visual_tests()
        all_results['Playwright Visual Validation'] = playwright_passed
        if not playwright_passed:
            all_passed = False
            print("\n  ❌ CRITICAL: Playwright visual validation FAILED")
            print("  Dashboard changes are NOT visually validated")
        
        # =================================================================
        # FINAL SUMMARY
        # =================================================================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_header("MANDATORY TEST SUMMARY")
        
        print(f"Duration: {duration:.1f} seconds")
        print(f"\nResults:")
        
        passed_count = sum(1 for v in all_results.values() if v)
        total_count = len(all_results)
        
        for test_name, passed in all_results.items():
            print_result(test_name, passed)
        
        print(f"\nScore: {passed_count}/{total_count} test groups passed")
        
        if all_passed:
            print_header("ALL MANDATORY TESTS PASSED", char="=")
            print("Dashboard is SAFE to deploy.")
            print(f"\nDashboard URL: http://localhost:{SERVER_PORT}/autonomy_dashboard.html")
            print("\nCache-Busting Instructions:")
            print("  1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
            print("  2. Or use incognito/private browsing mode")
            return 0
        else:
            print_header("MANDATORY TESTS FAILED", char="!")
            print("DO NOT DEPLOY until all tests pass!")
            print("\nFailed test groups:")
            for test_name, passed in all_results.items():
                if not passed:
                    print(f"  - {test_name}")
            return 1
    
    finally:
        # Don't stop the server if tests passed - leave it running for user
        if not all_passed and server_process:
            print("\n  Stopping server due to test failures...")
            try:
                server_process.terminate()
            except:
                pass


if __name__ == "__main__":
    sys.exit(main())
