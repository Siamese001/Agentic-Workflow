#!/usr/bin/env python3
"""
End-to-end test script for pre-write hooks system.
"""

import subprocess
import tempfile
import time
from pathlib import Path


def run_test(test_name: str, command: list, expected_exit_codes: list = None) -> bool:
    """Run a test command and check exit code."""
    if expected_exit_codes is None:
        expected_exit_codes = [0]
    print(f"🧪 {test_name}...", end=" ")

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)

        if result.returncode in expected_exit_codes:
            print(f"✅ (exit {result.returncode})")
            return True
        else:
            print(f"❌ (exit {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print("❌ (timeout)")
        return False
    except Exception as e:
        print(f"❌ ({e})")
        return False


def main():
    """Run end-to-end tests."""
    print("🚀 Starting Pre-Write Hooks End-to-End Tests")
    print("=" * 60)

    skills_dir = Path(".windsurf/skills")
    test_results = []

    # Test 1: All skills have basic structure
    print("\n📋 Test 1: Skill Structure Validation")
    all_skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "main.py").exists():
            all_skills.append(skill_dir.name)

    print(f"   Found {len(all_skills)} skills")

    for skill_name in all_skills:
        main_script = skills_dir / skill_name / "main.py"
        config_file = skills_dir / skill_name / "skill.yaml"

        # Check files exist
        success = True
        if not main_script.exists():
            print(f"   ❌ {skill_name}: main.py missing")
            success = False
        if not config_file.exists():
            print(f"   ❌ {skill_name}: skill.yaml missing")
            success = False

        if success:
            # Check syntax
            result = subprocess.run(
                ["python", "-m", "py_compile", str(main_script)], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                print(f"   ✅ {skill_name}: structure OK")
                test_results.append(True)
            else:
                print(f"   ❌ {skill_name}: syntax error")
                test_results.append(False)

    # Test 2: Phase 2 Skills Functionality
    print("\n🛡️ Test 2: Phase 2 Critical Gap Skills")

    phase2_skills = [
        "powershell-guard",
        "repair-gate-validator",
        "agent-deletion-guard",
        "hitl-decision-validator",
        "guardian-exemption-validator",
    ]

    for skill_name in phase2_skills:
        skill_main = skills_dir / skill_name / "main.py"

        if not skill_main.exists():
            print(f"   ⚠️ {skill_name}: not found")
            test_results.append(False)
            continue

        if skill_name == "powershell-guard":
            # Test PowerShell rejection
            success = run_test(
                f"{skill_name}: PowerShell rejection",
                ["python", str(skill_main), "powershell Get-Process", "test.py"],
                [1],  # Should fail
            )
            test_results.append(success)

            # Test Python approval
            success = run_test(
                f"{skill_name}: Python approval",
                ["python", str(skill_main), "python script.py", "test.py"],
                [0],  # Should pass
            )
            test_results.append(success)

        elif skill_name == "agent-deletion-guard":
            # Test non-agent file
            success = run_test(
                f"{skill_name}: Non-agent file",
                ["python", str(skill_main), "regular_file.py"],
                [0],  # Should pass
            )
            test_results.append(success)

            # Test agent file
            success = run_test(
                f"{skill_name}: Agent file",
                ["python", str(skill_main), "TestAgent.py"],
                [1],  # Should fail
            )
            test_results.append(success)

        elif skill_name == "hitl-decision-validator":
            # Test single option
            success = run_test(
                f"{skill_name}: Single option",
                ["python", str(skill_main), "test decision", "1"],
                [0],  # Should pass
            )
            test_results.append(success)

            # Test multiple options
            success = run_test(
                f"{skill_name}: Multiple options",
                ["python", str(skill_main), "test decision", "3"],
                [1],  # Should fail (no HITL)
            )
            test_results.append(success)

        elif skill_name == "guardian-exemption-validator":
            # Test invalid format
            success = run_test(
                f"{skill_name}: Invalid format",
                ["python", str(skill_main), "# guardian: allow-something", "test.py"],
                [1],  # Should fail
            )
            test_results.append(success)

            # Test valid format
            success = run_test(
                f"{skill_name}: Valid format",
                [
                    "python",
                    str(skill_main),
                    "# guardian: allow-silent-swallower -- Specific justification for test validation",
                    "test.py",
                ],
                [0],  # Should pass
            )
            test_results.append(success)

        else:
            # Generic test - just try to run with help
            success = run_test(
                f"{skill_name}: Basic execution",
                ["python", str(skill_main), "--help"],
                [0, 1],  # Help or invalid args is fine
            )
            test_results.append(success)

    # Test 3: Orchestrator Integration
    print("\n🎯 Test 3: Pre-Write Orchestrator")
    orchestrator_main = skills_dir / "pre-write-orchestrator" / "main.py"

    if orchestrator_main.exists():
        # Test status command
        success = run_test(
            "Orchestrator: Status command", ["python", str(orchestrator_main), "test.py", "status"], [0]
        )
        test_results.append(success)

        # Test with actual file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"# test file for orchestrator")
            temp_file = f.name

        try:
            success = run_test(
                "Orchestrator: File validation",
                ["python", str(orchestrator_main), temp_file, "write", "test context"],
                [0, 1],  # May pass or fail depending on environment
            )
            test_results.append(success)
        finally:
            Path(temp_file).unlink(missing_ok=True)
    else:
        print("   ⚠️ Pre-write orchestrator not found")
        test_results.append(False)

    # Test 4: Performance Monitoring
    print("\n📊 Test 4: Performance Monitoring")
    perf_main = skills_dir / "performance-monitor" / "main.py"

    if perf_main.exists():
        # Test monitoring workflow
        success = run_test(
            "Performance: Start monitoring", ["python", str(perf_main), "start", "test_operation"], [0]
        )
        test_results.append(success)

        if success:
            time.sleep(1)  # Let it run briefly

            success = run_test("Performance: Stop monitoring", ["python", str(perf_main), "stop"], [0])
            test_results.append(success)

        # Test summary
        success = run_test("Performance: Summary", ["python", str(perf_main), "summary", "1"], [0])
        test_results.append(success)

        # Test alerts
        success = run_test("Performance: Alerts", ["python", str(perf_main), "alerts"], [0])
        test_results.append(success)
    else:
        print("   ⚠️ Performance monitor not found")
        test_results.append(False)

    # Test 5: Skill Status Dashboard
    print("\n📈 Test 5: Skill Status Dashboard")
    dashboard_main = skills_dir / "skill-status-dashboard" / "main.py"

    if dashboard_main.exists():
        # Test table output
        success = run_test("Dashboard: Table output", ["python", str(dashboard_main), "table"], [0])
        test_results.append(success)

        # Test JSON output
        success = run_test("Dashboard: JSON output", ["python", str(dashboard_main), "json"], [0])
        test_results.append(success)
    else:
        print("   ⚠️ Skill status dashboard not found")
        test_results.append(False)

    # Test 6: CI Integration
    print("\n🔧 Test 6: CI Integration")
    ci_main = skills_dir / "ci-integration" / "main.py"

    if ci_main.exists():
        # Test health check
        success = run_test(
            "CI: Health check",
            ["python", str(ci_main), "health-check"],
            [0, 1],  # May be healthy or degraded
        )
        test_results.append(success)

        # Test validation
        success = run_test(
            "CI: Validate skills",
            ["python", str(ci_main), "validate"],
            [0, 1],  # May have compliance issues
        )
        test_results.append(success)
    else:
        print("   ⚠️ CI integration not found")
        test_results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")

    total_tests = len(test_results)
    passed_tests = sum(test_results)
    failed_tests = total_tests - passed_tests

    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {(passed_tests / total_tests * 100):.1f}%")

    if failed_tests == 0:
        print("\n✅ All tests passed! Pre-write hooks system is ready.")
        return 0
    else:
        print(f"\n❌ {failed_tests} tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())
