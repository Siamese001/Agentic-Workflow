from pathlib import Path

"\n[PHASE 7/8] Sovereign Lockdown Check - CI/CD Entrypoint.\n\nThis script acts as the final gatekeeper for architectural purity.\nIt interfaces with the ArchitectureGovernorAgent in headless mode.\n\nUsage:\n    python scripts/ci/sovereign_lockdown_check_util.py\n\nExit Codes:\n    0 - Repository is sovereign-compliant (no violations)\n    1 - Violations detected (commit should be blocked)\n    2 - Error during verification\n\nPre-commit Hook Entry:\n    - id: sovereign-lockdown-verification\n      name: Sovereign Lockdown Verification (Phase 7)\n      entry: python\n      args: [scripts/ci/sovereign_lockdown_check_util.py]\n      language: python\n      pass_filenames: false\n      always_run: true\n"
import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def main() -> int:
    """Run sovereign lockdown verification."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
        from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor

        print("=" * 60)
        print("SOVEREIGN LOCKDOWN VERIFICATION")
        print("=" * 60)
        result = invoke_arch_governor(action="verify", project_root=project_root, auto_approve=True)
        raw_result = result.get("raw_result", result)
        passed = result.get("success", False)
        violations_found = raw_result.get("violations_found", result.get("violations_found", 0))
        roots_scanned = raw_result.get("roots_scanned", result.get("roots_scanned", []))
        print(f"\nRoots Scanned: {(', '.join(roots_scanned) if roots_scanned else 'None')}")
        print(f"Violations Found: {violations_found}")
        if passed:
            print("\n[OK] Sovereign Lockdown Verified: Repository is architecture-pure.")
            print("=" * 60)
            return 0
        else:
            print(f"\n[FAIL] Lockdown Failed: {violations_found} violations detected.")
            violations = raw_result.get("violations", [])
            if violations:
                print("\nViolations:")
                for v in violations[:10]:
                    if isinstance(v, dict):
                        print(f"  - [{v.get('type', 'UNKNOWN')}] {v.get('message', str(v))}")
                    else:
                        print(f"  - {v}")
            print(
                "\nTo fix: Run `python -m agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent --heal`"
            )
            print("=" * 60)
            return 1
    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Ensure agentic_core is properly installed.")
        return 2
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"[ERROR] Verification Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
