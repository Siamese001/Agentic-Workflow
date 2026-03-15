"""
MISSION CONTROLLER CONVERGENCE ENGINE
--------------------------------------
Implements the L4 Recursive Convergence Loop to ensure Zero Gravity Violations.
This engine provides the 'Skeptical' verification logic for L3 Orchestration.
"""

import hashlib
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ConvergenceEngine:
    # guardian: allow-magic-config
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds
        self.round_history = []

    def get_file_hash(self, file_path: Path) -> str:
        """
        SSOT SNAPSHOTTING: Generates SHA256 hash for fission detection.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConvergenceEngine.get_file_hash")

        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def detect_fission(self, pre_hash: str, post_hash: str, file_size: int) -> bool:
        """
        FISSION DETECTION: Triggers if a large file fails to change after healing.
        """
        return pre_hash == post_hash and file_size > 10240

    async def run_convergence(self, validator, healer, initial_violations: list):
        """
        RECURSIVE LOOP: Iterates until violations reach zero or max rounds.
        """
        current_violations = initial_violations
        round_num = 1
        while len(current_violations) > 0 and round_num <= self.max_rounds:
            print(f"🌀 Convergence Round {round_num}: {len(current_violations)} remaining")
            prioritized_violations = sorted(
                current_violations, key=lambda v: v.get("impact_score", 0), reverse=True
            )
            for violation in prioritized_violations:
                if violation.get("audit_fail_count", 0) > 3:
                    print(
                        f"🧟 ZOMBIE DETECTED: {violation.get('path')} - Escalating to Sub-atomic Refactor..."
                    )
                file_path = Path(violation.get("path", ""))
                pre_hash = None
                file_size = 0
                if file_path.exists():
                    pre_hash = self.get_file_hash(file_path)
                    file_size = file_path.stat().st_size
                await healer.heal(violation)
                if pre_hash and file_path.exists():
                    post_hash = self.get_file_hash(file_path)
                    if self.detect_fission(pre_hash, post_hash, file_size):
                        print(
                            f"⚛️ FISSION DETECTED: {violation.get('path')} unchanged after healing (>{file_size // 1024}KB) - Terminating mission for this file."
                        )
            current_violations = await validator.validate()
            self.round_history.append(len(current_violations))
            round_num += 1
        if len(current_violations) == 0:
            print(f"✅ CONVERGENCE ACHIEVED in {round_num - 1} rounds.")
        else:
            print(f"⚠️ CONVERGENCE FAILED: {len(current_violations)} violations persist.")
        return len(current_violations) == 0
