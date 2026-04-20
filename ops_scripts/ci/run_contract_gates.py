#!/usr/bin/env python3
"""
Contract Gates — Main CI Entrypoint

Runs all contract validation gates in deterministic order.
"""

import subprocess
import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


ROOT = _bootstrap_repo_root()
DEFAULT_SUBPROCESS_TIMEOUT = 300


def run_cmd(args, cwd=None, timeout: int = DEFAULT_SUBPROCESS_TIMEOUT):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return 124, stdout, f"Command timed out after {timeout}s\n{stderr}".strip()
    except (OSError, ValueError) as exc:
        return 2, "", f"{type(exc).__name__}: {exc}"


def _script(rel_path: str) -> Path:
    return ROOT / rel_path


# PRE-WRITE HOOKS INTEGRATION
def validate_pre_write_hooks():
    """Validate all pre-write hook skills."""
    skills_dir = ROOT / ".windsurf" / "skills"
    failed_skills: list[str] = []
    if not skills_dir.is_dir():
        print(f"❌ Skills directory missing: {skills_dir}")
        return False

    skill_dirs = sorted((d for d in skills_dir.iterdir() if d.is_dir()), key=lambda p: p.name)
    for idx, skill_dir in enumerate(skill_dirs, 1):  # progress_bar: skill health checks
        print(f"  [{idx}/{len(skill_dirs)}] checking skill: {skill_dir.name}")
        main_script = skill_dir / "main.py"
        if main_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(main_script), "--health-check"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                    cwd=ROOT,
                )
                if result.returncode != 0:
                    failed_skills.append(f"{skill_dir.name} (rc={result.returncode})")
            except (subprocess.TimeoutExpired, OSError) as exc:
                failed_skills.append(f"{skill_dir.name} ({type(exc).__name__})")

    if failed_skills:
        print(f"❌ Failed skills: {', '.join(failed_skills)}")
        return False

    print("✅ All pre-write hooks validated")
    return True


# MCP HEALTH CHECKS
def validate_mcp_health():
    """Validate MCP server health."""
    print("\n[MCP HEALTH CHECK]")

    # Gate: AGENTS.md Quick Reference must document every server in mcp_config.json
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_agents_mcp_coverage.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ AGENTS.md MCP coverage check failed")
        print(stdout or stderr)
        return False
    print("✅ AGENTS.md MCP coverage validated")

    # Gate: every .windsurf/skills/<name>/SKILL.md must conform to Anthropic's
    # Agent Skills authoring spec (frontmatter, name/description rules, 500-line
    # budget, third person, when-trigger, forward-slash paths).
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_skill_frontmatter.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Skill frontmatter check failed (Anthropic spec)")
        print(stdout or stderr)
        return False
    print("✅ Skill frontmatter validated (Anthropic spec)")

    return True


def main():
    """Run all contract gates in deterministic order."""

    # Validate MCP health (critical for Redis/ADG)
    if not validate_mcp_health():
        sys.exit(1)

    # Validate pre-write hooks
    if not validate_pre_write_hooks():
        sys.exit(1)

    # Gate: Infrastructure wiring scan (Rule: no raw infra in forbidden layers)
    print("🔍 Running infrastructure wiring scan...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/infra_wiring_scan.py"))], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Infrastructure wiring scan passed")

    # Gate: Executor theater (no fake parallelism in production code)
    print("🔍 Running executor theater gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/executor_theater_gate.py"))], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Executor theater gate passed")

    # Gate: ADG graph-layer evidence in refactoring plans (Constitutional §22)
    print("🔍 Running graph-layer evidence gate (refactoring plans)...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_graph_layer_evidence.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Graph-layer evidence gate passed")

    # Gate: Severity<->Band SSOT (Constitutional §22/§23 — no hardcoded mappings)
    print("🔍 Running severity<->band SSOT gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_severity_band_ssot.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Severity<->band SSOT gate passed")

    # Gate: Repository structure policy (config/structure_blueprint/structure_policy.yaml)
    print("🔍 Running structure policy gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_structure_policy.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Structure policy gate passed")

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
        print(f"❌ P0 runner import failed: {exc}")
        sys.exit(1)

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
