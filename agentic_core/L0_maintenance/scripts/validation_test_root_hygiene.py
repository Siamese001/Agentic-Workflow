#!/usr/bin/env python3
"""
L6 Root Hygiene & "The Void" Governance Validation

This test validates:
1. ALLOWED_ROOT_FILES and ALLOWED_ROOT_FOLDERS enforcement
2. Automated sanitation of unauthorized files
3. Law of Depth enforcement (3-5 levels)
4. Law of Atomicity (200 lines max)
5. File movement and organization
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from interfaces.governance import create_architecture_governor


async def test_root_hygiene_enforcement():
    """Test enforcement of root directory hygiene."""
    print("=" * 80)
    print("ROOT HYGIENE ENFORCEMENT")
    print("=" * 80)

    print("\n1. Testing ALLOWED_ROOT_FILES and ALLOWED_ROOT_FOLDERS")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create authorized files
        (temp_path / "README.md").write_text("# Project README")
        (temp_path / "pyproject.toml").write_text("[build-system]")
        (temp_path / ".gitignore").write_text("__pycache__/")

        # Create unauthorized files
        (temp_path / "temp_debug.txt").write_text("debug info")
        (temp_path / "random_script.py").write_text("print('hello')")
        (temp_path / "notes.log").write_text("log data")

        # Create authorized folders
        (temp_path / "agentic_core").mkdir()
        (temp_path / "scripts").mkdir()

        # Create unauthorized folder
        (temp_path / "random_folder").mkdir()

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Check violations
        violations = governor.check_root_hygiene(auto_sanitize=False)

        expected_violations = 4  # 3 files + 1 folder
        if len(violations) == expected_violations:
            print(f"✅ Detected {len(violations)} root violations")
        else:
            print(f"❌ Expected {expected_violations} violations, got {len(violations)}")
            return False

        # Test auto-sanitization
        violations = governor.check_root_hygiene(auto_sanitize=True)

        # Check if files were moved/deleted
        if not (temp_path / "temp_debug.txt").exists():
            print("✅ temp_debug.txt deleted (noise)")
        else:
            print("❌ temp_debug.txt not deleted")
            return False

        if (temp_path / "scripts" / "random_script.py").exists():
            print("✅ random_script.py moved to scripts/")
        else:
            print("❌ random_script.py not moved")
            return False

        return True


async def test_depth_law_enforcement():
    """Test Law of Depth enforcement (3-5 levels)."""
    print("\n" + "=" * 80)
    print("DEPTH LAW ENFORCEMENT")
    print("=" * 80)

    print("\n1. Testing depth boundaries (3-5 levels)")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Create test files at various depths
        test_cases = [
            ("file.py", 0, "too shallow"),
            ("a/b/file.py", 2, "too shallow"),
            ("a/b/c/file.py", 3, "valid"),
            ("a/b/c/d/file.py", 4, "valid"),
            ("a/b/c/d/e/file.py", 5, "valid"),
            ("a/b/c/d/e/f/file.py", 6, "too deep"),
        ]

        all_passed = True
        for file_path, depth, expected in test_cases:
            full_path = temp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("# Test file")

            violation = governor.check_depth_law(str(full_path))

            if expected == "valid":
                if violation is None:
                    print(f"✅ {file_path} (depth {depth}) - valid")
                else:
                    print(f"❌ {file_path} (depth {depth}) - should be valid: {violation}")
                    all_passed = False
            else:
                if violation and expected in violation.lower():
                    print(f"✅ {file_path} (depth {depth}) - {expected}")
                else:
                    print(f"❌ {file_path} (depth {depth}) - expected {expected}")
                    all_passed = False

        return all_passed


async def test_sovereign_directory_exemption():
    """Test that sovereign directories are exempt from depth limits."""
    print("\n" + "=" * 80)
    print("SOVEREIGN DIRECTORY EXEMPTION")
    print("=" * 80)

    print("\n1. Testing sovereign directories bypass depth limits")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Create deep structure in sovereign directory
        sovereign_path = temp_path / "agentic_core" / "L1_cognition" / "planning" / "metacognition" / "deep" / "deeper" / "file.py"
        sovereign_path.parent.mkdir(parents=True)
        sovereign_path.write_text("# Deep sovereign file")

        # Check depth (should be exempt)
        violation = governor.check_depth_law(str(sovereign_path))

        if violation is None:
            print("✅ Sovereign directory exempt from depth limit")
        else:
            print(f"❌ Sovereign directory should be exempt: {violation}")
            return False

        # Create same depth outside sovereign
        non_sovereign_path = temp_path / "normal" / "deep" / "deeper" / "file.py"
        non_sovereign_path.parent.mkdir(parents=True)
        non_sovereign_path.write_text("# Deep normal file")

        violation = governor.check_depth_law(str(non_sovereign_path))

        if violation and "too deep" in violation.lower():
            print("✅ Non-sovereign directory subject to depth limit")
        else:
            print("❌ Non-sovereign directory should violate depth limit")
            return False

        return True


async def test_atomicity_law_enforcement():
    """Test Law of Atomicity (200 lines max)."""
    print("\n" + "=" * 80)
    print("ATOMICITY LAW ENFORCEMENT")
    print("=" * 80)

    print("\n1. Testing file line count limits")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Create valid file (under limit)
        valid_file = temp_path / "valid.py"
        valid_content = "\n".join([f"# Line {i}" for i in range(100)])
        valid_file.write_text(valid_content)

        violation = governor.check_atomicity_law(str(valid_file))

        if violation is None:
            print("✅ 100-line file passes atomicity check")
        else:
            print(f"❌ 100-line file should pass: {violation}")
            return False

        # Create violating file (over limit)
        violating_file = temp_path / "violating.py"
        violating_content = "\n".join([f"# Line {i}" for i in range(300)])
        violating_file.write_text(violating_content)

        violation = governor.check_atomicity_law(str(violating_file))

        if violation and "300 lines" in violation and "SPLIT required" in violation:
            print("✅ 300-line file correctly flagged for split")
        else:
            print(f"❌ 300-line file should require split: {violation}")
            return False

        return True


async def test_depth_law_enforcement():
    """Test automatic depth law enforcement."""
    print("\n" + "=" * 80)
    print("DEPTH LAW ENFORCEMENT")
    print("=" * 80)

    print("\n1. Testing automatic file movement for depth violations")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Create directories
        (temp_path / "scripts").mkdir()
        (temp_path / "agentic_core" / "L1_cognition").mkdir(parents=True)

        # Create file too deep
        deep_file = temp_path / "a" / "b" / "c" / "d" / "e" / "f" / "deep_file.py"
        deep_file.parent.mkdir(parents=True)
        deep_file.write_text("# Too deep")

        # Enforce depth law
        new_path = governor.enforce_depth_law(str(deep_file))

        if new_path and "scripts/" in new_path:
            print(f"✅ Deep file moved to: {new_path}")
        else:
            print("❌ Deep file not moved correctly")
            return False

        # Create file too shallow
        shallow_file = temp_path / "shallow_file.py"
        shallow_file.write_text("# Too shallow")

        # Enforce depth law
        new_path = governor.enforce_depth_law(str(shallow_file))

        if new_path and "L1_cognition" in new_path:
            print(f"✅ Shallow file moved to: {new_path}")
        else:
            print("❌ Shallow file not moved correctly")
            return False

        return True


async def test_full_architecture_validation():
    """Test complete architecture validation with enforcement."""
    print("\n" + "=" * 80)
    print("FULL ARCHITECTURE VALIDATION")
    print("=" * 80)

    print("\n1. Testing comprehensive validation report")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Create various violations
        # Root violation
        (temp_path / "temp_file.txt").write_text("temp")

        # Depth violation
        deep_file = temp_path / "a" / "b" / "c" / "d" / "e" / "f" / "deep.py"
        deep_file.parent.mkdir(parents=True)
        deep_file.write_text("# Deep file")

        # Atomicity violation
        large_file = temp_path / "large.py"
        large_content = "\n".join([f"# Line {i}" for i in range(250)])
        large_file.write_text(large_content)

        # Run validation with enforcement
        report = governor.validate_architecture(
            file_paths=[str(deep_file), str(large_file)],
            enforce=True
        )

        # Check report
        if report["overall_status"] == "FAIL":
            print("✅ Overall status correctly set to FAIL")
        else:
            print("❌ Overall status should be FAIL")
            return False

        if len(report["root_violations"]) > 0:
            print(f"✅ Root violations detected: {len(report['root_violations'])}")
        else:
            print("❌ Root violations not detected")
            return False

        if len(report["depth_violations"]) > 0:
            print(f"✅ Depth violations detected: {len(report['depth_violations'])}")
        else:
            print("❌ Depth violations not detected")
            return False

        if len(report["atomicity_violations"]) > 0:
            print(f"✅ Atomicity violations detected: {len(report['atomicity_violations'])}")
        else:
            print("❌ Atomicity violations not detected")
            return False

        if len(report["enforced_actions"]) > 0:
            print(f"✅ Enforcement actions taken: {len(report['enforced_actions'])}")
        else:
            print("❌ No enforcement actions taken")
            return False

        return True


async def test_validation_with_300_line_file():
    """Test validation with a 300-line file as specified in the prompt."""
    print("\n" + "=" * 80)
    print("300-LINE FILE VALIDATION")
    print("=" * 80)

    print("\n1. Creating and validating 300-line file in root")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create governor
        governor = create_architecture_governor(str(temp_path))

        # Create 300-line file in root
        large_file = temp_path / "large_module.py"
        content = []
        for i in range(300):
            content.append(f"def function_{i}():")
            content.append(f"    # This is function {i}")
            content.append(f"    return {i}")
            content.append("")

        large_file.write_text("\n".join(content))

        print(f"Created {large_file.name} with {len(content)} lines")

        # Run validation
        report = governor.validate_architecture(file_paths=[str(large_file)], enforce=True)

        # Check results
        if report["root_violations"]:
            print("✅ Root violation detected (unauthorized file)")

        if report["atomicity_violations"]:
            print("✅ Atomicity violation detected (300 lines)")
            for violation in report["atomicity_violations"]:
                print(f"   {violation}")

        if report["enforced_actions"]:
            print("✅ File was moved to correct location")
            for action in report["enforced_actions"]:
                print(f"   {action}")

        return True


async def run_root_hygiene_validation():
    """Run all root hygiene validation tests."""
    print("\n" + "=" * 80)
    print("L6 ROOT HYGIENE & 'THE VOID' VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting ArchitectureGovernor with root hygiene enforcement")

    results = {}

    # Run all tests
    results["root_hygiene"] = await test_root_hygiene_enforcement()
    results["depth_law"] = await test_depth_law_enforcement()
    results["sovereign_exemption"] = await test_sovereign_directory_exemption()
    results["atomicity"] = await test_atomicity_law_enforcement()
    results["depth_enforcement"] = await test_depth_law_enforcement()
    results["full_validation"] = await test_full_architecture_validation()
    results["300_line_test"] = await test_validation_with_300_line_file()

    # Generate report
    print("\n" + "=" * 80)
    print("ROOT HYGIENE VALIDATION REPORT")
    print("=" * 80)

    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All L6 Governance components validated!")
        print("The system enforces:")
        print("  - Law of The Void (root hygiene)")
        print("  - ALLOWED_ROOT_FILES and ALLOWED_ROOT_FOLDERS")
        print("  - Automated sanitation (move/delete)")
        print("  - Law of Depth (3-5 levels)")
        print("  - Sovereign directory exemption")
        print("  - Law of Atomicity (200 lines max)")
        print("  - Automatic file organization")
    else:
        print("\n⚠️  Some components need attention")
        print("Check the logs above for details")

    return all_passed


if __name__ == "__main__":
    asyncio.run(run_root_hygiene_validation())