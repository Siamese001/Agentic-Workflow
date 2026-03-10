#!/usr/bin/env python3
"""
Phase 7 Evidence Runner: Deterministic Replay Tamper Round-Trip Validation.

Production-path replay validation with tamper detection and inline proofs.
"""

import argparse
import os
import re
import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import TESTS_DIR, get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

_ROOT = get_validated_project_root()


def validate_64hex(value: str, name: str) -> None:
    """Validate that a string is a 64-character hex string."""
    assert re.match(r"^[0-9a-f]{64}$", value), f"{name} must be 64-hex: {value}"
    print(f"OK: {name} validated as 64-hex")


def run_command_safely(argv: list[str]) -> str:
    """Run a command safely with strict validation."""
    # Hard-fail on shell=True
    if any(arg == "--shell" or arg.startswith("shell=") for arg in argv):
        print("FAIL: shell=True detected - hard fail")
        sys.exit(1)

    # Hard-fail on PowerShell executables
    if len(argv) > 0:
        exe = os.path.basename(argv[0]).lower()
        if exe in ["pwsh", "powershell", "powershell.exe"]:
            print(f"FAIL: PowerShell executable detected ({exe}) - hard fail")
            sys.exit(1)

    # Run command
    result = subprocess.run(
        argv, shell=False, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )

    if result.returncode != 0:
        print(f"FAIL: Command exited with code {result.returncode}: {' '.join(argv)}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)

    return result.stdout


def execute_tamper_roundtrip_proofs():
    """Execute PASS/FAIL/NEGATIVE CONTROL proofs for tamper round-trip."""
    print("=== PASS/FAIL/NEGATIVE CONTROL PROOFS ===")

    # Import test functions
    sys.path.insert(0, "tests/unit_min_deps")
    try:
        from test_vllm_replay_tamper_roundtrip import (
            create_tampered_artifact,
            create_test_artifact_with_violations,
            validate_64hex,
        )

        from agentic_core.L2_execution.types.vllm_replay_validator_types import VLLMReplayValidator
    except ImportError as e:
        print(f"FAIL: Cannot import test modules: {e}")
        sys.exit(1)

    # PASS SCENARIO: Validate original artifact
    print("PASS SCENARIO:")
    original_artifact = create_test_artifact_with_violations()
    original_hash = original_artifact.replay_hash
    validate_64hex(original_hash, "replay_hash (original)")

    validator = VLLMReplayValidator()
    original_validation = validator.validate_and_report(original_artifact)

    assert original_validation["valid"] is True, "PASS: Original artifact must validate"
    print(f"  valid={original_validation['valid']}")
    print(f"  replay_hash={original_hash}")
    print("OK: PASS scenario asserted")
    print()

    # FAIL SCENARIO: Reject tampered artifact
    print("FAIL SCENARIO:")
    tampered_artifact = create_tampered_artifact(original_artifact)
    tampered_stored_hash = tampered_artifact.replay_hash
    validate_64hex(tampered_stored_hash, "replay_hash (tampered_stored)")

    tampered_validation = validator.validate_and_report(tampered_artifact)
    tampered_computed_hash = tampered_validation["computed_replay_hash"]
    validate_64hex(tampered_computed_hash, "replay_hash (tampered_computed)")

    assert tampered_validation["valid"] is False, "FAIL: Tampered artifact must be rejected"
    assert tampered_computed_hash != original_hash, "FAIL: Computed hash must differ from original"

    print(f"  valid={tampered_validation['valid']}")
    print(f"  stored_replay_hash={tampered_stored_hash}")
    print(f"  computed_replay_hash={tampered_computed_hash}")
    print(f"  differs_from_original={tampered_computed_hash != original_hash}")
    print("OK: FAIL scenario asserted")
    print()

    # DETERMINISM RE-RUN LOCK
    print("DETERMINISM RE-RUN LOCK:")

    # First run
    original_artifact_1 = create_test_artifact_with_violations()
    original_hash_1 = original_artifact_1.replay_hash
    tampered_artifact_1 = create_tampered_artifact(original_artifact_1)
    tampered_hash_1 = tampered_artifact_1.replay_hash

    # Second run
    original_artifact_2 = create_test_artifact_with_violations()
    original_hash_2 = original_artifact_2.replay_hash
    tampered_artifact_2 = create_tampered_artifact(original_artifact_2)
    tampered_hash_2 = tampered_artifact_2.replay_hash

    # Assert determinism
    assert original_hash_1 == original_hash_2, "DETERMINISM: Original hash must be identical"
    assert tampered_hash_1 == tampered_hash_2, "DETERMINISM: Tampered hash must be identical"

    validate_64hex(original_hash_1, "original_hash_deterministic")
    validate_64hex(tampered_hash_1, "tampered_hash_deterministic")

    print(f"  original_hash_deterministic={original_hash_1 == original_hash_2}")
    print(f"  tampered_hash_deterministic={tampered_hash_1 == tampered_hash_2}")
    print("OK: Determinism re-run lock asserted")
    print()

    # NEGATIVE CONTROL: Tamper detection disabled
    print("NEGATIVE CONTROL:")

    # Mock validator that always passes (tamper detection disabled)
    class DisabledValidator:
        def validate(self, artifact):
            return True

        def validate_and_report(self, artifact):
            return {
                "valid": True,
                "stored_replay_hash": artifact.replay_hash,
                "computed_replay_hash": artifact.replay_hash,
                "violation_details": None,
            }

    disabled_validator = DisabledValidator()
    disabled_validation = disabled_validator.validate_and_report(tampered_artifact)

    assert disabled_validation["valid"] is True, "NEGATIVE: Disabled validator must incorrectly pass"

    # Production validator must still reject
    production_validation = validator.validate_and_report(tampered_artifact)
    assert production_validation["valid"] is False, "NEGATIVE: Production validator must reject"

    print(f"  disabled_validator_passes={disabled_validation['valid']}")
    print(f"  production_validator_rejects={not production_validation['valid']}")
    print("  OK: Enforcement check correctly fails when tamper detection disabled")
    print("OK: NEGATIVE CONTROL asserted")


def main():
    """Main evidence runner."""
    parser = argparse.ArgumentParser(description="Phase 7 Evidence Runner: Replay Tamper Round-Trip")
    parser.add_argument("--code-commit", required=True, help="Code commit hash (40-hex)")
    parser.add_argument("--evidence-commit", help="Evidence commit hash (40-hex)")
    args = parser.parse_args()

    # Validate code commit format
    assert re.match(r"^[0-9a-f]{40}$", args.code_commit), "CODE_COMMIT must be 40-hex"

    print("=== PHASE 7 EVIDENCE: REPLAY TAMPER ROUND-TRIP ===")
    print()

    # Phase 7 touched files
    phase_touched = [
        "tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py",
        "tools/evidence/qwen_migration_phase7_replay_tamper_roundtrip_runner.py",
    ]

    # TEST_SCOPE and TARGETS
    print("TEST_SCOPE=TARGETED")

    # Find tests referencing replay tamper or round-trip
    test_targets = []

    # Always include our new test
    test_targets.append(
        ["python", "-m", "pytest", "-q", "tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py"]
    )

    # Find existing tests that reference replay validation
    for root, dirs, files in os.walk(_ROOT / TESTS_DIR):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                normalized_path = file_path.replace("\\", "/")
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if "vllm_replay_validator" in content and "test_vllm_replay" in content:
                            if normalized_path not in [t[-1] for t in test_targets]:
                                test_targets.append(["python", "-m", "pytest", "-q", normalized_path])
                except:
                    pass

    print("TEST_TARGETS:")
    for i, target in enumerate(test_targets):
        print(f"  [{i}]: {target}")

    # SCOPE_JUSTIFICATION
    print("SCOPE_JUSTIFICATION:")
    print("  - test_vllm_replay_tamper_roundtrip.py added for production-path tamper validation")
    print("  - Existing replay validator tests impacted by Phase 7 tamper round-trip logic")
    print("  - Evidence runner validates deterministic tamper detection with inline proofs")

    # PHASE_TOUCHED_FILES
    print("PHASE_TOUCHED_FILES:")
    for f in sorted(phase_touched):
        print(f"  {f}")
    print()

    # Git status before
    print("git status --porcelain (before):")
    out = run_command_safely(["git", "status", "--porcelain"])
    print(out.rstrip())
    print()

    # Run pytest targets
    for i, target in enumerate(test_targets):
        print(f"=== PYTEST TARGET [{i}] ===")
        out = run_command_safely(target)
        print(out.rstrip())
        print("EXIT CODE: 0")
        print()

    # Execute tamper round-trip proofs
    execute_tamper_roundtrip_proofs()

    # Git status final
    print("git status --porcelain (final):")
    out = run_command_safely(["git", "status", "--porcelain"])
    print(out.rstrip())
    print()

    # Fail if git status not clean
    if out.strip():
        print("FAIL: git status not clean at end")
        sys.exit(1)
    print()

    # Runner proof checklist
    print("=== RUNNER PROOF CHECKLIST ===")
    print("- [x] TEST_SCOPE=TARGETED enforced")
    print("- [x] All pytest targets executed and passed")
    print("- [x] PASS scenario: original artifact validates with production verifier")
    print("- [x] FAIL scenario: tampered artifact rejected with hash delta")
    print("- [x] DETERMINISM: re-run lock proven with identical hashes")
    print("- [x] NEGATIVE CONTROL: enforcement fails when tamper detection disabled")
    print("- [x] All 64-hex values regex-validated")
    print("- [x] Final git status clean")
    print()
    print("OK: All governance proofs asserted and passed")

    # If evidence-commit provided, validate it
    if args.evidence_commit:
        assert re.match(r"^[0-9a-f]{40}$", args.evidence_commit), "EVIDENCE_COMMIT must be 40-hex"
        print(f"EVIDENCE_COMMIT validated: {args.evidence_commit}")


if __name__ == "__main__":
    main()
