"""
Stress Test: Movement & Archival Boundaries
============================================

Tests the boundary between:
1. Automatic structural moves (in-repo depth alignment)
2. Terminal-prompted archival moves (to archives/)

Test Cases:
- A: Structural re-alignment (should be automatic)
- B: Archival enforcement (should prompt)
- C: CLI flag interaction with environment variables
"""

import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class BoundaryStressTest:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.results = {
            "test_a_structural": {"status": "PENDING", "details": []},
            "test_b_archival": {"status": "PENDING", "details": []},
            "test_c_cli_interaction": {"status": "PENDING", "details": []},
        }
        self.test_files = {
            "rogue_script": self.project_root
            / "agentic_core"
            / "L0_maintenance"
            / "rogue_script.py",
            "rogue_root": self.project_root / "rogue_root_file.py",
        }

    def verify_test_files_exist(self) -> bool:
        """Verify that test files were created."""
        print("\n" + "=" * 80)
        print("STEP 0: Verifying Test Files")
        print("=" * 80)

        all_exist = True
        for name, path in self.test_files.items():
            exists = path.exists()
            status = "✅" if exists else "❌"
            print(f"{status} {name}: {path}")
            if not exists:
                all_exist = False

        return all_exist

    def test_a_structural_realignment(self) -> dict:
        """
        Test Case A: Structural Re-alignment (Automatic)

        Expected: rogue_script.py should be moved automatically without prompts.
        """
        print("\n" + "=" * 80)
        print("TEST CASE A: Structural Re-alignment (Automatic)")
        print("=" * 80)

        result = {"status": "PENDING", "details": [], "violations": []}

        # Run hierarchy agent with --execute --yes
        cmd = [
            sys.executable,
            str(self.project_root / "canon_validator_agentic_v2_thin.py"),
            "--agent",
            "hierarchy",
            "--execute",
            "--yes",
        ]

        print(f"\n🔧 Running command: {' '.join(cmd)}")
        result["details"].append(f"Command: {' '.join(cmd)}")

        try:
            process = subprocess.run(
                cmd, cwd=str(self.project_root), capture_output=True, text=True, timeout=60
            )

            stdout = process.stdout
            stderr = process.stderr

            # Save output for analysis
            result["details"].append(f"Exit Code: {process.returncode}")
            result["details"].append(f"STDOUT Length: {len(stdout)} chars")
            result["details"].append(f"STDERR Length: {len(stderr)} chars")

            # Check for key indicators
            has_healed_nested = "[HEALED] NESTED" in stdout or "HEALED.*NESTED" in stdout
            has_prompt = "Approve" in stdout or "[y/n" in stdout or "y/n/s" in stdout
            has_moved = "rogue_script.py" in stdout and (
                "moved" in stdout.lower() or "HEALED" in stdout
            )

            result["details"].append(f"Has [HEALED] NESTED: {has_healed_nested}")
            result["details"].append(f"Has Terminal Prompt: {has_prompt}")
            result["details"].append(f"Has Move Indication: {has_moved}")

            # Verify file was moved
            original_exists = self.test_files["rogue_script"].exists()
            potential_targets = [
                self.project_root
                / "agentic_core"
                / "L0_maintenance"
                / "depth_aligned"
                / "rogue_script.py",
                self.project_root
                / "agentic_core"
                / "L0_maintenance"
                / "scripts"
                / "rogue_script.py",
            ]

            moved_location = None
            for target in potential_targets:
                if target.exists():
                    moved_location = target
                    break

            result["details"].append(f"Original file still exists: {original_exists}")
            result["details"].append(f"Moved to: {moved_location}")

            # Evaluation
            if has_prompt:
                result["status"] = "FAIL"
                result["violations"].append(
                    "❌ FAIL: Structural move triggered a terminal prompt (should be automatic)"
                )
            elif not has_moved and original_exists:
                result["status"] = "WARN"
                result["violations"].append(
                    "⚠️ WARN: File was not moved (may need manual inspection)"
                )
            elif moved_location:
                result["status"] = "PASS"
                result["violations"].append(
                    f"✅ PASS: File moved automatically to {moved_location.relative_to(self.project_root)}"
                )
            else:
                result["status"] = "UNKNOWN"
                result["violations"].append("❓ UNKNOWN: Cannot determine if move occurred")

            # Save full output for debugging
            output_file = self.project_root / "test_output_case_a.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=== STDOUT ===\n")
                f.write(stdout)
                f.write("\n\n=== STDERR ===\n")
                f.write(stderr)
            result["details"].append(f"Full output saved to: {output_file}")

        except subprocess.TimeoutExpired:
            result["status"] = "ERROR"
            result["violations"].append("❌ ERROR: Command timed out after 60 seconds")
        except Exception as e:
            result["status"] = "ERROR"
            result["violations"].append(f"❌ ERROR: {str(e)}")

        return result

    def test_b_archival_enforcement(self) -> dict:
        """
        Test Case B: Archival Enforcement (Manual Prompt)

        Expected: rogue_root_file.py should trigger a terminal prompt.
        """
        print("\n" + "=" * 80)
        print("TEST CASE B: Archival Enforcement (Manual Prompt)")
        print("=" * 80)

        result = {"status": "PENDING", "details": [], "violations": []}

        # Run hierarchy agent WITHOUT --yes (to see if it prompts)
        cmd = [
            sys.executable,
            str(self.project_root / "canon_validator_agentic_v2_thin.py"),
            "--agent",
            "hierarchy",
            "--execute",
        ]

        print(f"\n🔧 Running command: {' '.join(cmd)}")
        print("⚠️ This test will timeout if a prompt appears (expected behavior)")
        result["details"].append(f"Command: {' '.join(cmd)}")

        try:
            # Use a short timeout since we expect it to hang on a prompt
            process = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10,
                input="n\n",  # Send 'n' to reject if prompt appears
            )

            stdout = process.stdout
            stderr = process.stderr

            result["details"].append(f"Exit Code: {process.returncode}")
            result["details"].append(f"STDOUT Length: {len(stdout)} chars")

            # Check for prompt indicators
            has_prompt = any(
                indicator in stdout
                for indicator in ["Approve archive?", "[y/n/s", "y/n/skip", "Approve", "archive"]
            )

            has_automatic_archive = (
                "rogue_root_file.py" in stdout and "archived" in stdout.lower() and not has_prompt
            )

            result["details"].append(f"Has Terminal Prompt: {has_prompt}")
            result["details"].append(f"Has Automatic Archive: {has_automatic_archive}")

            # Evaluation
            if has_automatic_archive:
                result["status"] = "FAIL"
                result["violations"].append(
                    "❌ FAIL: Archival move bypassed terminal prompt (should require approval)"
                )
            elif has_prompt:
                result["status"] = "PASS"
                result["violations"].append(
                    "✅ PASS: Archival move triggered terminal prompt as expected"
                )
            else:
                result["status"] = "UNKNOWN"
                result["violations"].append(
                    "❓ UNKNOWN: Cannot determine if prompt logic was triggered"
                )

            # Save output
            output_file = self.project_root / "test_output_case_b.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=== STDOUT ===\n")
                f.write(stdout)
                f.write("\n\n=== STDERR ===\n")
                f.write(stderr)
            result["details"].append(f"Full output saved to: {output_file}")

        except subprocess.TimeoutExpired:
            # Timeout is EXPECTED if a prompt appears
            result["status"] = "PASS"
            result["violations"].append(
                "✅ PASS: Command timed out waiting for input (prompt appeared as expected)"
            )
            result["details"].append("Command timed out after 10s (expected - prompt appeared)")
        except Exception as e:
            result["status"] = "ERROR"
            result["violations"].append(f"❌ ERROR: {str(e)}")

        return result

    def test_c_cli_flag_interaction(self) -> dict:
        """
        Test Case C: CLI Flag Interaction

        Test: ARCHIVE_BATCH_ACCEPT=0 in env but --yes in CLI
        Expected: CLI flag should override environment variable
        """
        print("\n" + "=" * 80)
        print("TEST CASE C: CLI Flag Interaction with Environment Variables")
        print("=" * 80)

        result = {"status": "PENDING", "details": [], "violations": []}

        # Run with ARCHIVE_BATCH_ACCEPT=0 but --yes flag
        cmd = [
            sys.executable,
            str(self.project_root / "canon_validator_agentic_v2_thin.py"),
            "--agent",
            "hierarchy",
            "--execute",
            "--yes",
        ]

        env = os.environ.copy()
        env["ARCHIVE_BATCH_ACCEPT"] = "0"

        print(f"\n🔧 Running command: {' '.join(cmd)}")
        print("🔧 Environment: ARCHIVE_BATCH_ACCEPT=0")
        result["details"].append(f"Command: {' '.join(cmd)}")
        result["details"].append("Environment: ARCHIVE_BATCH_ACCEPT=0")

        try:
            process = subprocess.run(
                cmd, cwd=str(self.project_root), capture_output=True, text=True, timeout=60, env=env
            )

            stdout = process.stdout
            stderr = process.stderr

            result["details"].append(f"Exit Code: {process.returncode}")
            result["details"].append(f"STDOUT Length: {len(stdout)} chars")

            # Check if --yes overrode the environment variable
            has_prompt = "Approve" in stdout or "[y/n" in stdout
            has_auto_accept = (
                "--yes" in stdout
                or "auto-accepting" in stdout.lower()
                or "batch accept" in stdout.lower()
            )

            result["details"].append(f"Has Terminal Prompt: {has_prompt}")
            result["details"].append(f"Has Auto-Accept Indication: {has_auto_accept}")

            # Evaluation
            if has_prompt:
                result["status"] = "FAIL"
                result["violations"].append(
                    "❌ FAIL: CLI --yes flag did not override ARCHIVE_BATCH_ACCEPT=0"
                )
            else:
                result["status"] = "PASS"
                result["violations"].append(
                    "✅ PASS: CLI --yes flag correctly overrode environment variable"
                )

            # Save output
            output_file = self.project_root / "test_output_case_c.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=== STDOUT ===\n")
                f.write(stdout)
                f.write("\n\n=== STDERR ===\n")
                f.write(stderr)
            result["details"].append(f"Full output saved to: {output_file}")

        except subprocess.TimeoutExpired:
            result["status"] = "FAIL"
            result["violations"].append(
                "❌ FAIL: Command timed out (CLI flag did not override env var)"
            )
        except Exception as e:
            result["status"] = "ERROR"
            result["violations"].append(f"❌ ERROR: {str(e)}")

        return result

    def generate_findings_report(self) -> str:
        """Generate comprehensive findings report."""
        print("\n" + "=" * 80)
        print("GENERATING FINDINGS REPORT")
        print("=" * 80)

        report_lines = [
            "# Stress Test: Movement & Archival Boundaries - Findings Report",
            "",
            f"**Test Date:** {subprocess.check_output(['date', '/t'], shell=True, text=True).strip() if os.name == 'nt' else subprocess.check_output(['date'], text=True).strip()}",
            "",
            "## Executive Summary",
            "",
        ]

        # Count results
        passed = sum(1 for r in self.results.values() if r["status"] == "PASS")
        failed = sum(1 for r in self.results.values() if r["status"] == "FAIL")
        errors = sum(1 for r in self.results.values() if r["status"] == "ERROR")
        unknown = sum(1 for r in self.results.values() if r["status"] in ["UNKNOWN", "PENDING"])

        report_lines.extend(
            [
                f"- **Total Tests:** {len(self.results)}",
                f"- **Passed:** {passed} ✅",
                f"- **Failed:** {failed} ❌",
                f"- **Errors:** {errors} 🔥",
                f"- **Unknown/Pending:** {unknown} ❓",
                "",
                "---",
                "",
            ]
        )

        # Test Case A
        report_lines.extend(
            [
                "## Test Case A: Structural Re-alignment (Automatic)",
                "",
                "**Goal:** Verify that in-repo structural moves happen automatically without terminal prompts.",
                "",
                f"**Status:** {self.results['test_a_structural']['status']}",
                "",
                "**Violations:**",
            ]
        )
        for violation in self.results["test_a_structural"]["violations"]:
            report_lines.append(f"- {violation}")
        report_lines.extend(
            [
                "",
                "**Details:**",
            ]
        )
        for detail in self.results["test_a_structural"]["details"]:
            report_lines.append(f"- {detail}")
        report_lines.extend(["", "---", ""])

        # Test Case B
        report_lines.extend(
            [
                "## Test Case B: Archival Enforcement (Manual Prompt)",
                "",
                "**Goal:** Verify that archival moves trigger terminal prompts for user approval.",
                "",
                f"**Status:** {self.results['test_b_archival']['status']}",
                "",
                "**Violations:**",
            ]
        )
        for violation in self.results["test_b_archival"]["violations"]:
            report_lines.append(f"- {violation}")
        report_lines.extend(
            [
                "",
                "**Details:**",
            ]
        )
        for detail in self.results["test_b_archival"]["details"]:
            report_lines.append(f"- {detail}")
        report_lines.extend(["", "---", ""])

        # Test Case C
        report_lines.extend(
            [
                "## Test Case C: CLI Flag Interaction",
                "",
                "**Goal:** Verify that CLI --yes flag correctly overrides ARCHIVE_BATCH_ACCEPT environment variable.",
                "",
                f"**Status:** {self.results['test_c_cli_interaction']['status']}",
                "",
                "**Violations:**",
            ]
        )
        for violation in self.results["test_c_cli_interaction"]["violations"]:
            report_lines.append(f"- {violation}")
        report_lines.extend(
            [
                "",
                "**Details:**",
            ]
        )
        for detail in self.results["test_c_cli_interaction"]["details"]:
            report_lines.append(f"- {detail}")
        report_lines.extend(["", "---", ""])

        # Logic Monitoring Table
        report_lines.extend(
            [
                "## Logic Monitoring Summary",
                "",
                "| Operation | Expected Logic | Actual Behavior | Status |",
                "| --- | --- | --- | --- |",
            ]
        )

        # Determine actual behaviors
        structural_behavior = (
            "Automatic"
            if self.results["test_a_structural"]["status"] == "PASS"
            else "Prompted (FAIL)"
        )
        archival_behavior = (
            "Prompted"
            if self.results["test_b_archival"]["status"] == "PASS"
            else "Automatic (FAIL)"
        )
        cli_behavior = (
            "Override"
            if self.results["test_c_cli_interaction"]["status"] == "PASS"
            else "Ignored (FAIL)"
        )

        report_lines.extend(
            [
                f"| In-Repo Move | Automatic | {structural_behavior} | {self.results['test_a_structural']['status']} |",
                f"| Archival Move | Terminal Prompt | {archival_behavior} | {self.results['test_b_archival']['status']} |",
                f"| CLI --yes Flag | Override Env Var | {cli_behavior} | {self.results['test_c_cli_interaction']['status']} |",
                "",
            ]
        )

        # Critical Failures
        critical_failures = []
        if self.results["test_a_structural"]["status"] == "FAIL":
            critical_failures.append(
                "❌ **CRITICAL:** Structural moves are triggering prompts (should be automatic)"
            )
        if self.results["test_b_archival"]["status"] == "FAIL":
            critical_failures.append(
                "❌ **CRITICAL:** Archival moves are bypassing prompts (should require approval)"
            )
        if self.results["test_c_cli_interaction"]["status"] == "FAIL":
            critical_failures.append(
                "❌ **CRITICAL:** CLI flags are not overriding environment variables"
            )

        if critical_failures:
            report_lines.extend(
                [
                    "## ⚠️ Critical Failures",
                    "",
                ]
            )
            report_lines.extend(critical_failures)
            report_lines.append("")

        # Recommendations
        report_lines.extend(
            [
                "## Recommendations",
                "",
            ]
        )

        if failed > 0 or errors > 0:
            report_lines.extend(
                [
                    "1. **Review Full Output Files:** Check `test_output_case_*.txt` files for detailed logs",
                    "2. **Inspect HierarchyAgent Logic:** Verify the boundary detection between structural and archival moves",
                    "3. **Check ArchivalGatekeeper:** Ensure prompt logic is correctly integrated",
                    "4. **Verify CLI Flag Parsing:** Confirm --yes flag properly sets ARCHIVE_BATCH_ACCEPT=1",
                ]
            )
        else:
            report_lines.extend(
                [
                    "✅ All tests passed! The boundary between automatic structural moves and prompted archival moves is working correctly.",
                ]
            )

        report_lines.extend(
            [
                "",
                "---",
                "",
                "## Test Files Used",
                "",
            ]
        )
        for name, path in self.test_files.items():
            exists = "✅ Exists" if path.exists() else "❌ Missing"
            report_lines.append(f"- **{name}:** `{path.relative_to(self.project_root)}` ({exists})")

        report = "\n".join(report_lines)

        # Save report
        report_file = self.project_root / "STRESS_TEST_MOVEMENT_ARCHIVAL_FINDINGS.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 Report saved to: {report_file}")

        return report

    def run_all_tests(self):
        """Run all stress tests."""
        print("\n" + "=" * 80)
        print("STRESS TEST: MOVEMENT & ARCHIVAL BOUNDARIES")
        print("=" * 80)

        # Step 0: Verify test files
        if not self.verify_test_files_exist():
            print("\n❌ ERROR: Test files are missing. Cannot proceed.")
            return

        # Test Case A
        self.results["test_a_structural"] = self.test_a_structural_realignment()

        # Test Case B
        self.results["test_b_archival"] = self.test_b_archival_enforcement()

        # Test Case C
        self.results["test_c_cli_interaction"] = self.test_c_cli_flag_interaction()

        # Generate report
        self.generate_findings_report()

        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        for test_name, result in self.results.items():
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "ERROR": "🔥",
                "UNKNOWN": "❓",
                "PENDING": "⏳",
            }.get(result["status"], "❓")
            print(f"{status_icon} {test_name}: {result['status']}")

        print("\n" + "=" * 80)
        print("📄 Full report: STRESS_TEST_MOVEMENT_ARCHIVAL_FINDINGS.md")
        print("=" * 80)


if __name__ == "__main__":
    tester = BoundaryStressTest()
    tester.run_all_tests()
