"""Aggressive parallel E2E comparison - like-for-like runs with metrics."""

import sys

sys.path.insert(0, "c:/Git/Agentic-Workflow")

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_version(name: str, use_legacy: bool) -> dict:
    """Run a version and capture detailed metrics."""
    start = time.time()

    cmd = [sys.executable, "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint"]
    if use_legacy:
        cmd.append("--legacy")
    cmd.extend(["--targets", "agentic_core", "--heal", "-v"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd="c:/Git/Agentic-Workflow",
    )

    elapsed = time.time() - start
    out = result.stdout

    # Detect phases
    phases = []
    if "discovery phase" in out.lower():
        phases.append("Discovery")
    if "validation phase" in out.lower():
        phases.append("Validation")
    if "alignment phase" in out.lower():
        phases.append("Alignment")
    if "healing phase" in out.lower():
        phases.append("Healing")
    if "reporting phase" in out.lower():
        phases.append("Reporting")

    # Detect errors/warnings
    warnings = out.count("WARNING")
    errors = out.count("ERROR")

    # Detect agent count
    agents_discovered = 0
    if "Discovered" in out and "agents" in out:
        for line in out.split("\n"):
            if "Discovered" in line and "agents" in line:
                try:
                    agents_discovered = int([w for w in line.split() if w.isdigit()][0])
                except Exception:
                    pass
                break

    return {
        "name": name,
        "exit": result.returncode,
        "time": elapsed,
        "phases": phases,
        "phase_count": len(phases),
        "warnings": warnings,
        "errors": errors,
        "agents": agents_discovered,
        "stdout_chars": len(out),
        "stderr_chars": len(result.stderr),
        "success": result.returncode == 0 and len(phases) >= 4,
    }


def run_parallel(runs: int = 3):
    """Run both versions in parallel multiple times."""
    print("=" * 90)
    print(f"PARALLEL AGGRESSIVE TEST - {runs} LIKE-FOR-LIKE RUNS")
    print("=" * 90)

    all_results = []

    for run_num in range(1, runs + 1):
        print(f"\n{'─' * 90}")
        print(f"RUN #{run_num}/{runs}")
        print("─" * 90)

        # Run both in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(run_version, "MODULAR", False): "modular",
                executor.submit(run_version, "MONOLITHIC", True): "monolithic",
            }

            results = {}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {"name": key.upper(), "error": str(e), "success": False}

            all_results.append(results)

            # Display side-by-side
            mod = results.get("modular", {})
            mono = results.get("monolithic", {})

            print(f"\n{'METRIC':<25} | {'MODULAR':<30} | {'MONOLITHIC':<30}")
            print(f"{'─' * 25}─┼─{'─' * 30}─┼─{'─' * 30}")
            print(f"{'Exit Code':<25} | {mod.get('exit', 'N/A'):<30} | {mono.get('exit', 'N/A'):<30}")
            print(
                f"{'Runtime (s)':<25} | {mod.get('time', 0):.2f}{'':<26} | {mono.get('time', 0):.2f}{'':<26}"
            )
            print(
                f"{'Phases Executed':<25} | {mod.get('phase_count', 0)}/5{'':<25} | {mono.get('phase_count', 0)}/5{'':<25}"
            )
            print(
                f"{'Phases List':<25} | {', '.join(mod.get('phases', []))[:28]:<30} | {', '.join(mono.get('phases', []))[:28]:<30}"
            )
            print(f"{'Agents Discovered':<25} | {mod.get('agents', 0):<30} | {mono.get('agents', 0):<30}")
            print(f"{'Warnings':<25} | {mod.get('warnings', 0):<30} | {mono.get('warnings', 0):<30}")
            print(f"{'Errors':<25} | {mod.get('errors', 0):<30} | {mono.get('errors', 0):<30}")
            print(
                f"{'Output Size (chars)':<25} | {mod.get('stdout_chars', 0):<30} | {mono.get('stdout_chars', 0):<30}"
            )
            print(
                f"{'Result':<25} | {'✓ PASS' if mod.get('success') else '✗ FAIL':<30} | {'✓ PASS' if mono.get('success') else '✗ FAIL':<30}"
            )

    # Summary stats
    print(f"\n{'=' * 90}")
    print("AGGREGATE STATISTICS")
    print(f"{'=' * 90}")

    mod_times = [r["modular"]["time"] for r in all_results if "modular" in r and "time" in r["modular"]]
    mono_times = [
        r["monolithic"]["time"] for r in all_results if "monolithic" in r and "time" in r["monolithic"]
    ]

    mod_passes = sum(1 for r in all_results if r.get("modular", {}).get("success"))
    mono_passes = sum(1 for r in all_results if r.get("monolithic", {}).get("success"))

    if mod_times and mono_times:
        print(f"\n{'METRIC':<25} | {'MODULAR':<30} | {'MONOLITHIC':<30}")
        print(f"{'─' * 25}─┼─{'─' * 30}─┼─{'─' * 30}")
        print(f"{'Runs Completed':<25} | {len(mod_times):<30} | {len(mono_times):<30}")
        print(f"{'Passes / Runs':<25} | {mod_passes}/{runs}{'':<25} | {mono_passes}/{runs}{'':<25}")
        print(
            f"{'Avg Runtime (s)':<25} | {sum(mod_times) / len(mod_times):.2f}{'':<26} | {sum(mono_times) / len(mono_times):.2f}{'':<26}"
        )
        print(f"{'Min Runtime (s)':<25} | {min(mod_times):.2f}{'':<26} | {min(mono_times):.2f}{'':<26}")
        print(f"{'Max Runtime (s)':<25} | {max(mod_times):.2f}{'':<26} | {max(mono_times):.2f}{'':<26}")

        # Parity check
        if mod_passes == mono_passes == runs:
            print(f"\n{'=' * 90}")
            print("✓ PERFECT PARITY - Both versions pass all runs")
            print(f"{'=' * 90}")
        elif mod_passes > mono_passes:
            print(f"\n{'=' * 90}")
            print(f"⚠ MODULAR ADVANTAGE - {mod_passes - mono_passes} more passes")
            print(f"{'=' * 90}")
        elif mono_passes > mod_passes:
            print(f"\n{'=' * 90}")
            print(f"⚠ MONOLITHIC ADVANTAGE - {mono_passes - mod_passes} more passes")
            print(f"{'=' * 90}")
        else:
            print(f"\n{'=' * 90}")
            print(f"✗ BOTH FAILING - {runs - mod_passes} failed runs each")
            print(f"{'=' * 90}")


if __name__ == "__main__":
    run_parallel(runs=5)
