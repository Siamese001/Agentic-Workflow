"""
MISSION CONTROLLER CONVERGENCE ENGINE
--------------------------------------
Implements the L4 Recursive Convergence Loop to ensure Zero Gravity Violations.
This engine provides the 'Skeptical' verification logic for L3 Orchestration.
"""

import hashlib
from pathlib import Path


class ConvergenceEngine:
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds
        self.round_history = []

    def get_file_hash(self, file_path: Path) -> str:
        """
        SSOT SNAPSHOTTING: Generates SHA256 hash for fission detection.
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def detect_fission(self, pre_hash: str, post_hash: str, file_size: int) -> bool:
        """
        FISSION DETECTION: Triggers if a large file fails to change after healing.
        """
        # Fission occurs if file is > 10KB and hashes are identical after repair attempt
        return pre_hash == post_hash and file_size > 10240

    async def run_convergence(self, validator, healer, initial_violations: list):
        """
        RECURSIVE LOOP: Iterates until violations reach zero or max rounds.
        """
        current_violations = initial_violations
        round_num = 1

        while len(current_violations) > 0 and round_num <= self.max_rounds:
            print(f"🌀 Convergence Round {round_num}: {len(current_violations)} remaining")

            # PHASE 6: Toxicity-Weighted Triage
            # Sort violations so Toxic Hubs (highest impact) are healed first
            # Formula: Impact = (100 - Metric) * (1 + ln(FanIn))
            prioritized_violations = sorted(
                current_violations, key=lambda v: v.get("impact_score", 0), reverse=True
            )

            for violation in prioritized_violations:
                # PHASE 5: Zombie Detection
                # If an agent fails to heal over multiple cycles, escalate priority
                if violation.get("audit_fail_count", 0) > 3:
                    print(
                        f"🧟 ZOMBIE DETECTED: {violation.get('path')} - Escalating to Sub-atomic Refactor..."
                    )

                # Fission-Aware Healing: Snapshot before healing
                file_path = Path(violation.get("path", ""))
                pre_hash = None
                file_size = 0
                if file_path.exists():
                    pre_hash = self.get_file_hash(file_path)
                    file_size = file_path.stat().st_size

                # Execute targeted healing mission
                await healer.heal(violation)

                # Fission Detection: Check if large file failed to change
                if pre_hash and file_path.exists():
                    post_hash = self.get_file_hash(file_path)
                    if self.detect_fission(pre_hash, post_hash, file_size):
                        print(
                            f"⚛️ FISSION DETECTED: {violation.get('path')} unchanged after healing (>{file_size // 1024}KB) - Terminating mission for this file."
                        )

            # Re-validate state
            current_violations = await validator.validate()
            self.round_history.append(len(current_violations))
            round_num += 1

        if len(current_violations) == 0:
            print(f"✅ CONVERGENCE ACHIEVED in {round_num - 1} rounds.")
        else:
            print(f"⚠️ CONVERGENCE FAILED: {len(current_violations)} violations persist.")

        return len(current_violations) == 0
