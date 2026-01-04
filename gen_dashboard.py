#!/usr/bin/env python3
"""
Dashboard generation with mandatory unit test validation.
Tests MUST pass before dashboard is generated.
"""
from pathlib import Path
import sys
import subprocess
import os

sys.path.insert(0, str(Path(__file__).parent))

def ensure_agent_discovery():
    """Run agent discovery if JSON is missing or out of date."""
    project_root = Path(__file__).parent
    discovery_script = project_root / "scripts" / "full_agent_discovery.py"
    json_path = project_root / "agent_discovery_full.json"
    
    # If JSON doesn't exist, run discovery
    if not json_path.exists():
        print("\n🔍 Agent discovery JSON not found. Running discovery...")
        print("=" * 60)
        result = subprocess.run(
            [sys.executable, str(discovery_script)],
            cwd=project_root,
            capture_output=False,
            text=True
        )
        if result.returncode != 0:
            print("\n❌ Agent discovery failed")
            sys.exit(1)
        print("✅ Agent discovery completed")
        return
    
    # Optional: add timestamp check to auto-run if repo is newer than JSON
    # For now, just ensure it exists

def run_comprehensive_dashboard_qa():
    """Run comprehensive QA: unit, integration, e2e, regression tests."""
    import subprocess
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent
    test_suites = [
        {
            "name": "Unit Tests",
            "path": project_root / "tests" / "test_dashboard_generation.py",
            "args": [sys.executable, str(project_root / "tests" / "test_dashboard_generation.py")],
            "critical": True
        },
        {
            "name": "Integration Tests",
            "path": project_root / "tests" / "integration" / "dashboard" / "test_dashboard_integration.py",
            "args": [sys.executable, "-m", "pytest", str(project_root / "tests" / "integration" / "dashboard" / "test_dashboard_integration.py"), "-v"],
            "critical": True
        },
        {
            "name": "Regression Tests",
            "path": project_root / "tests" / "regression" / "dashboard" / "test_dashboard_regression.py",
            "args": [sys.executable, "-m", "pytest", str(project_root / "tests" / "regression" / "dashboard" / "test_dashboard_regression.py"), "-v"],
            "critical": True
        },
        {
            "name": "E2E Tests",
            "path": project_root / "tests" / "e2e" / "dashboard" / "test_dashboard_e2e.py",
            "args": [sys.executable, "-m", "pytest", str(project_root / "tests" / "e2e" / "dashboard" / "test_dashboard_e2e.py"), "-v"],
            "critical": False  # E2E can fail if server issues, but shouldn't block generation
        }
    ]
    
    failed_tests = []
    
    for suite in test_suites:
        print(f"\n🧪 Running {suite['name']}...")
        print("=" * 60)
        
        if not suite["path"].exists():
            print(f"⚠️  {suite['name']} file not found: {suite['path']}")
            if suite["critical"]:
                failed_tests.append(f"{suite['name']} (missing file)")
            continue
        
        try:
            result = subprocess.run(
                suite["args"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout per suite
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            if result.returncode != 0:
                print(f"❌ {suite['name']} FAILED")
                if suite["critical"]:
                    failed_tests.append(suite['name'])
                else:
                    print(f"⚠️  {suite['name']} failed but not critical - continuing...")
            else:
                print(f"✅ {suite['name']} PASSED")
                
        except subprocess.TimeoutExpired:
            print(f"❌ {suite['name']} TIMED OUT")
            if suite["critical"]:
                failed_tests.append(f"{suite['name']} (timeout)")
        except Exception as e:
            print(f"❌ {suite['name']} ERROR: {e}")
            if suite["critical"]:
                failed_tests.append(f"{suite['name']} ({e})")
    
    return len(failed_tests) == 0, failed_tests

def validate_dashboard_crash_resistance():
    """Validate dashboard won't crash on Windsurf refresh/restart."""
    print("\n🛡️  Validating dashboard crash resistance...")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    dashboard_html = project_root / "reports" / "autonomy_dashboard.html"
    
    issues = []
    
    if dashboard_html.exists():
        with open(dashboard_html, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common crash patterns
        crash_patterns = [
            # Real browser/runtime error signatures (avoid false positives from legitimate JS checks like `x !== undefined`)
            ('uncaught typeerror', r'\bUncaught\s+TypeError\b'),
            ('cannot read properties', r'Cannot\s+read\s+properties\s+of\s+(?:undefined|null)'),
            ('cannot read property', r'Cannot\s+read\s+property\s+\"[^\"]+\"\s+of\s+(?:undefined|null)'),
            ('is not defined', r'\b\w+\s+is\s+not\s+defined'),
            ('throw statements', r'\bthrow\s+'),
        ]
        
        import re
        for pattern_name, pattern in crash_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(f"{pattern_name}: {len(matches)} instances")
        
        # Check for proper error handling
        error_handling_patterns = [
            'try\s*{',
            'catch\s*\(',
            'if\s*\(.*\!==\s*undefined',
            'if\s*\(.*\!==\s*null',
            '\.optionalChaining',
        ]
        
        has_error_handling = any(re.search(p, content, re.IGNORECASE) for p in error_handling_patterns)
        
        if not has_error_handling:
            issues.append("No error handling patterns found")
        
        # Check for safe data access
        safe_access_patterns = [
            'const\s+\w+\s*=\s*dashboardData\s*\|\|\s*\[\]',
            'const\s+\w+\s*=\s*recommendationsData\s*\|\|\s*\[\]',
            '\?\.',  # Optional chaining
            '??\s*\[\]',  # Nullish coalescing with empty array
        ]
        
        has_safe_access = any(re.search(p, content) for p in safe_access_patterns)
        
        if not has_safe_access:
            issues.append("No safe data access patterns found")
            
    else:
        issues.append("Dashboard HTML not found")
    
    if issues:
        print("⚠️  Crash resistance issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Dashboard appears crash-resistant")
        return True

def run_dashboard_tests():
    """Run unit tests before dashboard generation."""
    print("\n🧪 Running dashboard unit tests (mandatory)...")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "tests" / "test_dashboard_generation.py"
    
    if not test_file.exists():
        print(f"⚠️  Warning: Test file not found at {test_file}")
        print("   Proceeding without tests (not recommended)")
        return True
    
    # Run tests
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    # Print test output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        print("\n" + "=" * 60)
        print("❌ DASHBOARD TESTS FAILED")
        print("=" * 60)
        print("\n⛔ Dashboard generation BLOCKED - tests must pass first.")
        print("   Fix the failing tests and try again.")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL DASHBOARD TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Ensure agent discovery is up to date
    ensure_agent_discovery()
    
    # Run comprehensive QA suite
    qa_passed, failed_suites = run_comprehensive_dashboard_qa()
    
    if not qa_passed:
        print("\n" + "=" * 60)
        print("❌ CRITICAL QA TESTS FAILED")
        print("=" * 60)
        print(f"Failed suites: {', '.join(failed_suites)}")
        print("\n⛔ Dashboard generation BLOCKED - fix critical failures first.")
        sys.exit(1)
    
    # Validate crash resistance
    crash_resistant = validate_dashboard_crash_resistance()
    if not crash_resistant:
        print("\n⚠️  Warning: Dashboard may crash on refresh/restart")
        print("   Consider adding error handling before proceeding.")
        # Don't block generation for crash resistance issues, just warn
    
    # All QA passed - proceed with generation
    print("\n📊 Generating autonomy compliance report and dashboard...")
    print("=" * 60)
    
    from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
    
    AutonomyGuardianAgent(Path(__file__).parent).generate_compliance_report(markdown=True)
    
    print("\n✅ Dashboard generated successfully!")
    print("   → Open: reports/autonomy_dashboard.html")
    print("   → Server: http://localhost:8000/autonomy_dashboard.html")
    print("\n🛡️  QA Summary:")
    print("   ✅ Unit tests passed")
    print("   ✅ Integration tests passed")
    print("   ✅ Regression tests passed")
    if crash_resistant:
        print("   ✅ Crash resistance validated")
    else:
        print("   ⚠️  Crash resistance issues detected")
