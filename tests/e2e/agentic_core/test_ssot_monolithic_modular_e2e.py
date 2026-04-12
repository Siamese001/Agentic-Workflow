"""E2E test comparing monolithic vs modular SSOT execution."""

import sys

sys.path.insert(0, "c:/Git/Agentic-Workflow")

import subprocess


def run_monolithic():
    """Run monolithic version via entrypoint."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--targets",
            "agentic_core",
            "--heal",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="c:/Git/Agentic-Workflow",
    )
    return result


def run_modular():
    """Run modular version via entrypoint (without --legacy flag)."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--targets",
            "agentic_core",
            "--heal",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="c:/Git/Agentic-Workflow",
    )
    return result


def main():
    print("=" * 80)
    print("MONOLITHIC vs MODULAR E2E COMPARISON")
    print("=" * 80)

    # Run modular first
    print("\n[1] Running MODULAR version...")
    print("-" * 40)
    mod_result = None
    try:
        mod_result = run_modular()
        print(f"Return code: {mod_result.returncode}")
        print(f"Stdout ({len(mod_result.stdout)} chars):")
        print(mod_result.stdout[-3000:] if len(mod_result.stdout) > 3000 else mod_result.stdout)
        if mod_result.stderr:
            print(f"\nStderr ({len(mod_result.stderr)} chars):")
            print(mod_result.stderr[-1500:] if len(mod_result.stderr) > 1500 else mod_result.stderr)
    except subprocess.TimeoutExpired:
        print("TIMEOUT (>120s)")
    except Exception as e:
        print(f"ERROR: {e}")

    print("\n" + "=" * 80)

    # Run monolithic
    print("\n[2] Running MONOLITHIC version...")
    print("-" * 40)
    mono_result = None
    try:
        mono_result = run_monolithic()
        print(f"Return code: {mono_result.returncode}")
        print(f"Stdout ({len(mono_result.stdout)} chars):")
        print(mono_result.stdout[-3000:] if len(mono_result.stdout) > 3000 else mono_result.stdout)
        if mono_result.stderr:
            print(f"\nStderr ({len(mono_result.stderr)} chars):")
            print(mono_result.stderr[-1500:] if len(mono_result.stderr) > 1500 else mono_result.stderr)
    except subprocess.TimeoutExpired:
        print("TIMEOUT (>120s)")
    except Exception as e:
        print(f"ERROR: {e}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    # Analyze results
    mod_phases = []
    mono_phases = []

    if mod_result:
        mod_out = mod_result.stdout
        if "discovery phase" in mod_out.lower():
            mod_phases.append("Discovery")
        if "validation phase" in mod_out.lower():
            mod_phases.append("Validation")
        if "alignment phase" in mod_out.lower():
            mod_phases.append("Alignment")
        if "healing phase" in mod_out.lower():
            mod_phases.append("Healing")
        if "reporting phase" in mod_out.lower():
            mod_phases.append("Reporting")
        print(f"Modular phases: {mod_phases or 'Unknown/Discovery only'}")
    else:
        print("Modular: FAILED to run")

    if mono_result:
        mono_out = mono_result.stdout
        if "discovery phase" in mono_out.lower():
            mono_phases.append("Discovery")
        if "validation phase" in mono_out.lower():
            mono_phases.append("Validation")
        if "alignment phase" in mono_out.lower():
            mono_phases.append("Alignment")
        if "healing phase" in mono_out.lower():
            mono_phases.append("Healing")
        if "reporting phase" in mono_out.lower():
            mono_phases.append("Reporting")
        print(f"Monolithic phases: {mono_phases or 'Unknown'}")
    else:
        print("Monolithic: FAILED to run")

    # Final verdict
    mod_ok = mod_result and mod_result.returncode == 0 and len(mod_phases) >= 4
    mono_ok = mono_result and mono_result.returncode == 0 and len(mono_phases) >= 4

    print(f"\nModular: {'PASS' if mod_ok else 'FAIL'} (exit={getattr(mod_result, 'returncode', 'N/A')})")
    print(f"Monolithic: {'PASS' if mono_ok else 'FAIL'} (exit={getattr(mono_result, 'returncode', 'N/A')})")

    if mod_ok and mono_ok:
        print("\n✓ Both versions execute full workflow")
    elif mod_ok and not mono_ok:
        print("\n⚠ Modular works, monolithic needs fixes")
    elif not mod_ok and mono_ok:
        print("\n⚠ Monolithic works, modular needs fixes")
    else:
        print("\n✗ Both need fixes")


if __name__ == "__main__":
    main()
