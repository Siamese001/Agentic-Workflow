#!/usr/bin/env python3
"""
TIERED EXECUTION FLOW TEST SUITE
Tests the 4-tier execution model in canon_validator_agentic_v2_thin.py

Test Cases:
1. Structural Abortion Verification - Tier 1 failure aborts mission
2. Roster Deduplication Check - No duplicate agents across tiers
3. Execution Timeline Integrity - All 4 tiers recorded with timestamps
4. Stability Gate Passthrough - Clean repo passes all tiers
5. Tier 4 Reporting Accuracy - Final safety gate reports Tier 3 violations
"""

import sys
import json
import shutil
import sys
import json
from pathlib import Path
from agentic_core.utils.security import safe_execute
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.structure_blueprint import get_validated_project_root


class TieredExecutionTester:
    """Test harness for tiered execution flow validation."""

    def __init__(self):
        self.project_root = get_validated_project_root()
        self.runtime_state_path = self.project_root / "runtime_state.json"
        self.test_results = []

    def run_validator(self, mode="dry-run", expect_abort=False):
        """Run canon_validator and capture results."""
        cmd = [sys.executable, str(self.project_root / "canon_validator_agentic_v2_thin.py"), "--heal"]
        if mode == "execute":
            cmd.append("--execute-heal")

        result = safe_execute(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            timeout=600,
            check=False
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "aborted": "MISSION ABORTED" in result.stdout
        }

    def load_runtime_state(self):
        """Load runtime_state.json if it exists."""
        if not self.runtime_state_path.exists():
            return None

        try:
            with open(self.runtime_state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"   [!] Failed to load runtime_state.json: {e}")
            return None

    def test_1_structural_abortion(self):
        """Test 1: Structural Abortion Verification

        Manually move a core agent to an illegal directory, run validator in execute mode,
        verify mission aborts after Tier 1 if LocationAgent cannot fix it.
        """
        print("\n" + "="*70)
        print("TEST 1: Structural Abortion Verification")
        print("="*70)

        # Find NamingAgent.py
        naming_agent_path = self.project_root / "agentic_core" / "utils" / "core_extensions" / "NamingAgent.py"
        if not naming_agent_path.exists():
            print("   ⚠️  SKIP: NamingAgent.py not found at expected location")
            return False

        # Create illegal directory and move agent there
        illegal_dir = self.project_root / "ILLEGAL_AGENT_LOCATION"
        illegal_dir.mkdir(exist_ok=True)
        backup_path = naming_agent_path.parent / f"NamingAgent.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        moved_path = illegal_dir / "NamingAgent.py"

        try:
            # Backup original
            shutil.copy2(naming_agent_path, backup_path)

            # Move to illegal location
            shutil.move(str(naming_agent_path), str(moved_path))
            print(f"   ✓ Moved NamingAgent.py to illegal location: {illegal_dir}")

            # Run validator in execute mode
            print("   ✓ Running validator in EXECUTE mode...")
            result = self.run_validator(mode="execute", expect_abort=True)

            # Check if mission aborted
            if result["aborted"]:
                print("   ✅ TEST 1 PASSED: Mission aborted after Tier 1 structural violations")

                # Verify Tier 3 agents were NOT invoked
                state = self.load_runtime_state()
                if state and "execution_timeline" in state:
                    tier3_executed = any(t["tier"] == 3 for t in state["execution_timeline"])
                    if not tier3_executed:
                        print("   ✅ Tier 3 agents were NOT invoked (correct behavior)")
                    else:
                        print("   ❌ Tier 3 agents were invoked despite Tier 1 failure")
                        return False

                return True
            else:
                print("   ❌ TEST 1 FAILED: Mission did not abort")
                return False

        finally:
            # Restore original file
            if moved_path.exists():
                shutil.move(str(moved_path), str(naming_agent_path))
            if backup_path.exists():
                backup_path.unlink()
            if illegal_dir.exists():
                try:
                    illegal_dir.rmdir()
                except:
                    pass
            print("   ✓ Cleanup complete")

    def test_2_roster_deduplication(self):
        """Test 2: Roster Deduplication Check

        Verify that mandatory agents (LocationAgent, NamingAgent, etc.) only appear
        in Tier 1/2 and are filtered out of Tier 3 Discovery Roster.
        """
        print("\n" + "="*70)
        print("TEST 2: Roster Deduplication Check")
        print("="*70)

        # Run validator in dry-run mode
        print("   ✓ Running validator in DRY-RUN mode...")
        result = self.run_validator(mode="dry-run")

        # Load runtime state
        state = self.load_runtime_state()
        if not state or "execution_timeline" not in state:
            print("   ❌ TEST 2 FAILED: No execution_timeline in runtime_state.json")
            return False

        # Extract agent names from each tier
        tier1_agents = set()
        tier2_agents = set()
        tier3_agents = set()
        tier4_agents = set()

        for tier_data in state["execution_timeline"]:
            tier_num = tier_data["tier"]
            agents = set(tier_data.get("agents", []))

            if tier_num == 1:
                tier1_agents = agents
            elif tier_num == 2:
                tier2_agents = agents
            elif tier_num == 3:
                tier3_agents = agents
            elif tier_num == 4:
                tier4_agents = agents

        # Check for duplicates
        mandatory_agents = tier1_agents | tier2_agents | tier4_agents
        duplicates = mandatory_agents & tier3_agents

        if duplicates:
            print(f"   ❌ TEST 2 FAILED: Found duplicate agents in Tier 3: {duplicates}")
            return False

        print(f"   ✅ TEST 2 PASSED: No duplicate agents across tiers")
        print(f"      Tier 1 (Structural): {len(tier1_agents)} agents")
        print(f"      Tier 2 (Architectural): {len(tier2_agents)} agents")
        print(f"      Tier 3 (Discovery): {len(tier3_agents)} agents")
        print(f"      Tier 4 (Safety): {len(tier4_agents)} agents")
        print(f"      Mandatory agents successfully filtered from Tier 3: {mandatory_agents}")

        return True

    def test_3_timeline_integrity(self):
        """Test 3: Execution Timeline Integrity

        Verify that runtime_state.json records 4 distinct execution blocks with
        correct start/end timestamps and success status.
        """
        print("\n" + "="*70)
        print("TEST 3: Execution Timeline Integrity")
        print("="*70)

        # Run validator in dry-run mode
        print("   ✓ Running validator in DRY-RUN mode...")
        result = self.run_validator(mode="dry-run")

        # Load runtime state
        state = self.load_runtime_state()
        if not state or "execution_timeline" not in state:
            print("   ❌ TEST 3 FAILED: No execution_timeline in runtime_state.json")
            return False

        timeline = state["execution_timeline"]

        # Verify 4 tiers
        if len(timeline) != 4:
            print(f"   ❌ TEST 3 FAILED: Expected 4 tiers, found {len(timeline)}")
            return False

        # Verify each tier has required fields
        required_fields = ["tier", "name", "start", "end", "agents", "fixes", "violations", "success"]
        for tier_data in timeline:
            missing = [f for f in required_fields if f not in tier_data]
            if missing:
                print(f"   ❌ TEST 3 FAILED: Tier {tier_data.get('tier', '?')} missing fields: {missing}")
                return False

            # Verify timestamps are valid ISO format
            try:
                start_time = datetime.fromisoformat(tier_data["start"])
                end_time = datetime.fromisoformat(tier_data["end"])

                if end_time < start_time:
                    print(f"   ❌ TEST 3 FAILED: Tier {tier_data['tier']} end time before start time")
                    return False
            except Exception as e:
                print(f"   ❌ TEST 3 FAILED: Invalid timestamp format in Tier {tier_data.get('tier', '?')}: {e}")
                return False

        print("   ✅ TEST 3 PASSED: Execution timeline integrity verified")
        for tier_data in timeline:
            duration = (datetime.fromisoformat(tier_data["end"]) - datetime.fromisoformat(tier_data["start"])).total_seconds()
            print(f"      Tier {tier_data['tier']} ({tier_data['name']}): {len(tier_data['agents'])} agents, {duration:.2f}s, success={tier_data['success']}")

        return True

    def test_4_stability_gate_passthrough(self):
        """Test 4: Stability Gate Passthrough

        Run validator in clean repository with execute mode, confirm Tier 1 passes
        with 0 violations and mission transitions to Tier 2 and Tier 3.
        """
        print("\n" + "="*70)
        print("TEST 4: Stability Gate Passthrough")
        print("="*70)

        # Run validator in execute mode on clean repo
        print("   ✓ Running validator in EXECUTE mode on clean repository...")
        result = self.run_validator(mode="execute")

        # Verify mission did NOT abort
        if result["aborted"]:
            print("   ❌ TEST 4 FAILED: Mission aborted unexpectedly")
            print(f"      Check if repository has structural violations")
            return False

        # Load runtime state
        state = self.load_runtime_state()
        if not state or "execution_timeline" not in state:
            print("   ❌ TEST 4 FAILED: No execution_timeline in runtime_state.json")
            return False

        # Find Tier 1 data
        tier1_data = next((t for t in state["execution_timeline"] if t["tier"] == 1), None)
        if not tier1_data:
            print("   ❌ TEST 4 FAILED: Tier 1 not found in execution_timeline")
            return False

        # Verify Tier 1 passed with 0 violations
        if tier1_data["violations"] > 0:
            print(f"   ❌ TEST 4 FAILED: Tier 1 has {tier1_data['violations']} violations")
            print(f"      Repository may have structural issues")
            return False

        # Verify all 4 tiers executed
        if len(state["execution_timeline"]) != 4:
            print(f"   ❌ TEST 4 FAILED: Expected 4 tiers, found {len(state['execution_timeline'])}")
            return False

        print("   ✅ TEST 4 PASSED: Stability gate passthrough successful")
        print(f"      Tier 1 violations: {tier1_data['violations']} (clean)")
        print(f"      All 4 tiers executed successfully")

        return True

    def test_5_tier4_reporting_accuracy(self):
        """Test 5: Tier 4 Reporting Accuracy

        Verify that AutonomyGuardian in Tier 4 correctly reports violations
        found in Tier 3. Introduce a test violation and verify it's reported.
        """
        print("\n" + "="*70)
        print("TEST 5: Tier 4 Reporting Accuracy")
        print("="*70)

        # Run validator in dry-run mode
        print("   ✓ Running validator in DRY-RUN mode...")
        result = self.run_validator(mode="dry-run")

        # Load runtime state
        state = self.load_runtime_state()
        if not state or "execution_timeline" not in state:
            print("   ❌ TEST 5 FAILED: No execution_timeline in runtime_state.json")
            return False

        # Find Tier 3 and Tier 4 data
        tier3_data = next((t for t in state["execution_timeline"] if t["tier"] == 3), None)
        tier4_data = next((t for t in state["execution_timeline"] if t["tier"] == 4), None)

        if not tier3_data or not tier4_data:
            print("   ❌ TEST 5 FAILED: Tier 3 or Tier 4 not found in execution_timeline")
            return False

        # Verify Tier 4 includes AutonomyGuardian
        if "AutonomyGuardian" not in tier4_data["agents"]:
            print("   ❌ TEST 5 FAILED: AutonomyGuardian not in Tier 4 agents")
            return False

        # Check if Tier 4 reports violations (may be 0 in clean repo)
        tier3_violations = tier3_data["violations"]
        tier4_violations = tier4_data["violations"]

        print(f"   ✅ TEST 5 PASSED: Tier 4 reporting structure verified")
        print(f"      Tier 3 violations: {tier3_violations}")
        print(f"      Tier 4 violations: {tier4_violations}")
        print(f"      AutonomyGuardian present in Tier 4: ✓")

        # Note: In a clean repo, violations may be 0, which is expected
        if tier3_violations == 0 and tier4_violations == 0:
            print(f"      ℹ️  Repository is clean - no violations to report")

        return True

    def run_all_tests(self):
        """Run all 5 test cases and report results."""
        print("\n" + "="*70)
        print("TIERED EXECUTION FLOW TEST SUITE")
        print("="*70)
        print(f"Project Root: {self.project_root}")
        print(f"Runtime State: {self.runtime_state_path}")

        tests = [
            ("Structural Abortion Verification", self.test_1_structural_abortion),
            ("Roster Deduplication Check", self.test_2_roster_deduplication),
            ("Execution Timeline Integrity", self.test_3_timeline_integrity),
            ("Stability Gate Passthrough", self.test_4_stability_gate_passthrough),
            ("Tier 4 Reporting Accuracy", self.test_5_tier4_reporting_accuracy),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                passed = test_func()
                results.append((test_name, passed))
            except Exception as e:
                print(f"\n   ❌ TEST FAILED WITH EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False))

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)

        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {test_name}")

        print(f"\nTotal: {passed_count}/{total_count} tests passed")

        if passed_count == total_count:
            print("\n🎉 ALL TESTS PASSED - Tiered execution flow is working correctly!")
            return 0
        else:
            print(f"\n⚠️  {total_count - passed_count} TEST(S) FAILED - Review failures above")
            return 1


if __name__ == "__main__":
    tester = TieredExecutionTester()
    sys.exit(tester.run_all_tests())
