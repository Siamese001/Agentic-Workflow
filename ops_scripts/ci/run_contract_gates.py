#!/usr/bin/env python3
"""
Contract Gates — Main CI Entrypoint

Runs all contract validation gates in deterministic order.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args, cwd=None):
    """Run a command and return result."""
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


# PRE-WRITE HOOKS INTEGRATION
def validate_pre_write_hooks():
    """Validate all pre-write hook skills."""
    skills_dir = Path(".windsurf/skills")
    failed_skills = []

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    for idx, skill_dir in enumerate(skill_dirs, 1):  # progress_bar: skill health checks
        print(f"  [{idx}/{len(skill_dirs)}] checking skill: {skill_dir.name}")
        main_script = skill_dir / "main.py"
        if main_script.exists():
            try:
                result = subprocess.run(
                    ["python", str(main_script), "--health-check"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    failed_skills.append(skill_dir.name)
            except Exception:  # guardian: allow-broad-exception -- skill health-check scripts raise heterogeneous errors across plugins; no shared catchable base
                failed_skills.append(skill_dir.name)

    if failed_skills:
        print(f"❌ Failed skills: {', '.join(failed_skills)}")
        return False

    print("✅ All pre-write hooks validated")
    return True


# MCP HEALTH CHECKS
def validate_mcp_health():
    """Validate MCP server health and hung process detection."""
    print("\n[MCP HEALTH CHECK]")

    # Gate: gate constants ↔ mcp_config.json key sync (prevents silent miss on new servers)
    returncode, stdout, stderr = run_cmd(
        ["python", "ops_scripts/ci/check_mcp_gate_sync.py"],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ MCP gate sync check failed")
        print(stdout or stderr)
        return False
    print("✅ MCP gate sync validated")

    # Gate: mcp_config.json sovereignty rules (filesystem scoping, _comment, no out-of-repo paths)
    returncode, stdout, stderr = run_cmd(
        ["python", "ops_scripts/ci/check_mcp_config_sovereignty.py"],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ MCP config sovereignty check failed")
        print(stdout or stderr)
        return False
    print("✅ MCP config sovereignty validated")

    # Gate: local Python MCP startup invariants (cwd, PYTHONPATH, env vars)
    returncode, stdout, stderr = run_cmd(
        ["python", "ops_scripts/ci/check_mcp_startup_invariant.py"],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ MCP startup invariant check failed")
        print(stdout or stderr)
        return False
    print("✅ MCP startup invariants validated")

    # Check MCP PyTest coverage
    returncode, stdout, stderr = run_cmd(
        ["python", "ops_scripts/ci/check_mcp_pytest_coverage.py"],
        cwd=ROOT,
    )

    if returncode != 0:
        print("❌ MCP PyTest coverage validation failed")
        print(stdout)
        return False

    print("✅ MCP PyTest coverage validated")

    # Check for hung MCP processes
    returncode, stdout, stderr = run_cmd(
        ["python", "ops_scripts/ci/mcp_hung_process_detector.py", "--check"],
        cwd=ROOT,
    )

    if returncode != 0:
        print("❌ MCP hung process detection failed")
        print(stdout)
        return False

    print("✅ MCP hung process check passed")

    # Gate: AGENTS.md Quick Reference must document every server in mcp_config.json
    returncode, stdout, stderr = run_cmd(
        ["python", "ops_scripts/ci/check_agents_mcp_coverage.py"],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ AGENTS.md MCP coverage check failed")
        print(stdout or stderr)
        return False
    print("✅ AGENTS.md MCP coverage validated")

    return True


def main():
    """Run all contract gates in deterministic order."""

    # Validate MCP health (critical for Redis/ADG)
    if not validate_mcp_health():
        sys.exit(1)

    # Validate pre-write hooks
    if not validate_pre_write_hooks():
        sys.exit(1)

    # Gate: No archives/ imports in production code (Rule 12)
    print("🔍 Checking for archives/ imports in production code...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(ROOT / "ops_scripts/ci/check_no_archives_imports.py")], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ No archives/ imports found")

    # Gate: Infrastructure wiring scan (Rule: no raw infra in forbidden layers)
    print("🔍 Running infrastructure wiring scan...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(ROOT / "ops_scripts/ci/infra_wiring_scan.py")], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Infrastructure wiring scan passed")

    # Gate: Executor theater (no fake parallelism in production code)
    print("🔍 Running executor theater gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(ROOT / "ops_scripts/ci/executor_theater_gate.py")], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Executor theater gate passed")

    # Gate: P0 two-pass (preflight + full ADG enforcement)
    print("\n[P0 TWO-PASS GATE]")
    try:
        from ops_scripts.ci.adg_gates.p0_runner import run_p0_two_pass

        p0_rc = run_p0_two_pass(emit_artifacts=True)
        if p0_rc == 1:
            print("❌ P0 two-pass gate BLOCKED — commit rejected")
            sys.exit(1)
        elif p0_rc == 2:
            print("⚠️  P0 two-pass gate ERROR — runner-level failure (see stderr)")
            sys.exit(1)
        else:
            print("✅ P0 two-pass gate passed")
    except ImportError as exc:
        print(f"⚠️  P0 runner import failed — {exc} (continuing as warn)")

    # Gate: P3 trend tracking (watch-only, never blocks)
    print("\n[P3 TREND RUNNER]")
    try:
        from ops_scripts.ci.adg_gates.p3_trend_runner import run_p3_trend

        p3_rc = run_p3_trend(emit_artifacts=True)
        if p3_rc == 2:
            print("⚠️  P3 trend runner ERROR — see stderr (non-blocking)")
        else:
            print("✅ P3 trend runner completed")
    except ImportError as exc:
        print(f"⚠️  P3 runner import failed — {exc} (non-blocking)")

    # Continue with existing logic...
    return 0


if __name__ == "__main__":
    sys.exit(main())
