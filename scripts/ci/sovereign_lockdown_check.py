#!/usr/bin/env python3
"""
[PHASE 7/8] Sovereign Lockdown Check - CI/CD Entrypoint.

This script acts as the final gatekeeper for architectural purity.
It interfaces with the ArchitectureGovernorAgent in headless mode.

Usage:
    python scripts/ci/sovereign_lockdown_check.py

Exit Codes:
    0 - Repository is sovereign-compliant (no violations)
    1 - Violations detected (commit should be blocked)
    2 - Error during verification

Pre-commit Hook Entry:
    - id: sovereign-lockdown-verification
      name: Sovereign Lockdown Verification (Phase 7)
      entry: python
      args: [scripts/ci/sovereign_lockdown_check.py]
      language: python
      pass_filenames: false
      always_run: true
"""


import sys


def main() -> int:
    """Run sovereign lockdown verification."""
    try:
        # Add project root to path for imports
        project_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(project_root))

            ArchitectureGovernorAgent,
        )

        print("=" * 60)
        print("SOVEREIGN LOCKDOWN VERIFICATION")
        print("=" * 60)

        # Initialize the Governor in headless/auto-approve mode
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            auto_approve=True,  # Force non-interactive sovereignty
        )

        # Execute final sync verification
        passed, results = agent.run_ci_verification_sync()

        # Extract details
        raw_result = results.get("_raw_result", results)
        violations_found = raw_result.get("violations_found", 0)
        roots_scanned = raw_result.get("roots_scanned", [])

        print(f"\nRoots Scanned: {', '.join(roots_scanned) if roots_scanned else 'None'}")
        print(f"Violations Found: {violations_found}")

        if passed:
            print("\n[OK] Sovereign Lockdown Verified: Repository is architecture-pure.")
            print("=" * 60)
            return 0
        else:
            # Output findings for CI logs
            print(f"\n[FAIL] Lockdown Failed: {violations_found} violations detected.")

            # Show violation details if available
            violations = raw_result.get("violations", [])
            if violations:
                print("\nViolations:")
                for v in violations[:10]:  # Limit to first 10
                    if isinstance(v, dict):
                        print(f"  - [{v.get('type', 'UNKNOWN')}] {v.get('message', str(v))}")
                    else:
                        print(f"  - {v}")

            print(
                "\nTo fix: Run `python -m agentic_core.L5_safety.validators.ArchitectureGovernorAgent --heal`"
            )
            print("=" * 60)
            return 1

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Ensure agentic_core is properly installed.")
        return 2
    except Exception as e:
        print(f"[ERROR] Verification Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
