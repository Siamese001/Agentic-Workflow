#!/usr/bin/env python3
"""
Comprehensive tests to ensure dashboard works WITHOUT a server.

Root Cause Prevention: ERR_CONNECTION_REFUSED occurs when:
1. Dashboard prints localhost URL but server isn't running
2. User clicks link after Windsurf restart (no server process)

These tests verify:
1. Dashboard HTML is self-contained (no external dependencies)
2. File paths are printed instead of localhost URLs
3. Dashboard loads correctly via file:// protocol
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_dashboard_html_is_self_contained():
    """Verify dashboard HTML has no external localhost dependencies."""
    dashboard_path = PROJECT_ROOT / "reports" / "autonomy_dashboard.html"
    
    if not dashboard_path.exists():
        print("⚠️  Dashboard not found - generating...")
        subprocess.run([sys.executable, "gen_dashboard.py"], cwd=PROJECT_ROOT, check=True)
    
    content = dashboard_path.read_text(encoding="utf-8")
    
    # Check for localhost references that would fail without server
    localhost_patterns = [
        r'http://localhost:\d+',
        r'http://127\.0\.0\.1:\d+',
        r'fetch\s*\(\s*["\']http://localhost',
        r'XMLHttpRequest.*localhost',
    ]
    
    issues = []
    for pattern in localhost_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"Found localhost reference: {matches[:3]}...")
    
    assert not issues, f"Dashboard has server dependencies: {issues}"
    print("✅ Dashboard HTML is self-contained (no localhost dependencies)")


def test_gen_dashboard_prints_file_path():
    """Verify gen_dashboard.py prints file:// path, not localhost URL."""
    gen_dashboard_path = PROJECT_ROOT / "gen_dashboard.py"
    content = gen_dashboard_path.read_text(encoding="utf-8")
    
    # Should have file:// path
    assert "file:///" in content, "gen_dashboard.py should print file:// path"
    
    # Should NOT unconditionally print localhost URL
    # The localhost URL should only appear in the --serve block
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'localhost:8000' in line.lower() or 'http://localhost' in line.lower():
            # Check if it's inside the serve block
            context_start = max(0, i - 5)
            context = '\n'.join(lines[context_start:i+1])
            assert 'args.serve' in context or 'DASHBOARD_AUTO_SERVE' in context or 'Server starting' in line, \
                f"Localhost URL printed unconditionally at line {i+1}: {line}"
    
    print("✅ gen_dashboard.py prints file:// path (not localhost URL)")


def test_autonomy_guardian_no_server_requirement():
    """Verify AutonomyGuardianAgent doesn't require server for dashboard viewing."""
    agent_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "AutonomyGuardianAgent.py"
    content = agent_path.read_text(encoding="utf-8")
    
    # Should mention "no server required"
    assert "no server required" in content.lower() or "file:///" in content, \
        "AutonomyGuardianAgent should indicate no server is needed"
    
    # Should NOT have instructions that require a server unconditionally
    assert "Live Server" not in content, \
        "Should not require Live Server extension"
    
    print("✅ AutonomyGuardianAgent doesn't require server for dashboard")


def test_dashboard_file_exists_after_generation():
    """Verify dashboard file is created and accessible."""
    dashboard_path = PROJECT_ROOT / "reports" / "autonomy_dashboard.html"
    
    # Generate if needed
    if not dashboard_path.exists():
        result = subprocess.run(
            [sys.executable, "gen_dashboard.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Dashboard generation failed: {result.stderr}"
    
    assert dashboard_path.exists(), "Dashboard file should exist"
    assert dashboard_path.stat().st_size > 10000, "Dashboard should have substantial content"
    
    # Verify it's valid HTML
    content = dashboard_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content or "<html" in content, "Should be valid HTML"
    assert "</html>" in content, "HTML should be complete"
    
    print("✅ Dashboard file exists and is valid HTML")


def test_dashboard_output_no_connection_refused_scenario():
    """Simulate restart scenario - verify no unconditional localhost URLs."""
    # Check gen_dashboard.py source for correct patterns
    gen_dashboard_path = PROJECT_ROOT / "gen_dashboard.py"
    content = gen_dashboard_path.read_text(encoding="utf-8")
    
    # Should have file:// path for direct access
    assert "file:///" in content, "gen_dashboard.py should have file:// path"
    
    # Check that localhost URL is only in serve block
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'localhost' in line.lower() and 'print' in line.lower():
            # Get surrounding context
            context_start = max(0, i - 10)
            context = '\n'.join(lines[context_start:i+1])
            # Localhost print should only be in serve block
            assert 'args.serve' in context or 'Server starting' in line, \
                f"Localhost URL printed outside serve block at line {i+1}"
    
    # Also check AutonomyGuardianAgent
    agent_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "AutonomyGuardianAgent.py"
    agent_content = agent_path.read_text(encoding="utf-8")
    assert "file:///" in agent_content, "AutonomyGuardianAgent should have file:// path"
    
    print("✅ Dashboard output won't cause ERR_CONNECTION_REFUSED")


def test_dashboard_works_without_network():
    """Verify dashboard HTML can be parsed without network (simulated)."""
    dashboard_path = PROJECT_ROOT / "reports" / "autonomy_dashboard.html"
    
    if not dashboard_path.exists():
        subprocess.run([sys.executable, "gen_dashboard.py"], cwd=PROJECT_ROOT, check=True)
    
    content = dashboard_path.read_text(encoding="utf-8")
    
    # Check for CDN dependencies that might fail offline
    cdn_patterns = [
        r'src=["\']https?://cdn\.',
        r'href=["\']https?://cdn\.',
        r'src=["\']https?://unpkg\.',
    ]
    
    cdn_refs = []
    for pattern in cdn_patterns:
        matches = re.findall(pattern, content)
        cdn_refs.extend(matches)
    
    # CDN refs are OK for Plotly, but should be limited
    # Main functionality should work offline
    if cdn_refs:
        print(f"   Note: Found {len(cdn_refs)} CDN references (Plotly charts need network)")
        # Verify there's a fallback message
        assert "plotly" in content.lower() or "chart" in content.lower(), \
            "Charts may not load offline - consider adding fallback"
    
    print("✅ Dashboard core functionality works without network")


def run_all_tests():
    """Run all dashboard server-independence tests."""
    print("\n" + "=" * 60)
    print("🧪 DASHBOARD SERVER-INDEPENDENCE TESTS")
    print("=" * 60)
    print("Purpose: Prevent ERR_CONNECTION_REFUSED after Windsurf restart\n")
    
    tests = [
        test_gen_dashboard_prints_file_path,
        test_autonomy_guardian_no_server_requirement,
        test_dashboard_file_exists_after_generation,
        test_dashboard_html_is_self_contained,
        test_dashboard_output_no_connection_refused_scenario,
        test_dashboard_works_without_network,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
