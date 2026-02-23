"""
Phase 3 Integration Validation Runner.

Executes dry-run and full-heal integration runs twice each (determinism proof),
captures all outputs, and writes a single evidence file.

Usage:
    python tools/run_phase3_integration.py

Output:
    docs/evidence/phase_execute_ssot_integration_phase3.md
"""

import json
import os
import pathlib
import subprocess
import sys
import time

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
EVIDENCE_PATH = REPO_ROOT / "docs" / "evidence" / "phase_execute_ssot_integration_phase3.md"
TIMEOUT_SECONDS = 300  # guardian: allow-magic-configuration  # 5-minute hard timeout per run

# ---------------------------------------------------------------------------
# Safety guard: forbid pwsh/powershell in argv0
# ---------------------------------------------------------------------------


def _check_argv0(argv: list) -> None:
    if not argv:
        raise ValueError("Empty argv")
    a0 = argv[0].lower()
    if "pwsh" in a0 or "powershell" in a0:
        raise RuntimeError(f"FORBIDDEN: argv0 contains pwsh/powershell: {argv[0]!r}")


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------


def run_cmd(argv: list, env: dict | None = None, label: str = "") -> dict:
    _check_argv0(argv)
    merged_env = {**os.environ}
    if env:
        merged_env.update(env)
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            argv,
            check=False,
            text=True,
            capture_output=True,
            shell=False,
            cwd=str(REPO_ROOT),
            env=merged_env,
            timeout=TIMEOUT_SECONDS,
            encoding="utf-8",
            errors="replace",
        )
        elapsed = time.monotonic() - t0
        return {
            "label": label,
            "argv": argv,
            "env_overrides": env or {},
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed": elapsed,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - t0
        return {
            "label": label,
            "argv": argv,
            "env_overrides": env or {},
            "returncode": -999,
            "stdout": (exc.stdout or ""),
            "stderr": (exc.stderr or "") + f"\n[TIMEOUT after {TIMEOUT_SECONDS}s]",
            "elapsed": elapsed,
            "timed_out": True,
        }


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------


def _check_termination(run: dict) -> list:
    issues = []
    if run["timed_out"]:
        issues.append(f"FAIL: timed out after {TIMEOUT_SECONDS}s (non-terminating loop suspected)")
    else:
        issues.append(f"OK: terminated in {run['elapsed']:.1f}s (exit {run['returncode']})")
    return issues


def _check_no_mutation_spam(run: dict) -> list:
    combined = run["stdout"] + run["stderr"]
    lines = combined.splitlines()
    mutation_lines = [l for l in lines if "MUTATION_PROHIBITED" in l]
    if len(mutation_lines) > 3:
        return [f"WARN: {len(mutation_lines)} MUTATION_PROHIBITED lines (possible spam — check for loop)"]
    if mutation_lines:
        return [f"OK: {len(mutation_lines)} MUTATION_PROHIBITED line(s) (within acceptable threshold)"]
    return ["OK: no MUTATION_PROHIBITED lines"]


def _check_plan_only(run: dict) -> list:
    combined = run["stdout"] + run["stderr"]
    plan_hits = [l for l in combined.splitlines() if "PLAN-ONLY" in l or "plan_only" in l.lower()]
    if plan_hits:
        return [f"OK: {len(plan_hits)} PLAN-ONLY emission(s) found — L0 files not mutated"]
    return ["INFO: no PLAN-ONLY emissions (no L0 gravity targets encountered, or dry-run)"]


def _check_persistence_latch(run: dict) -> list:
    combined = run["stdout"] + run["stderr"]
    lines = combined.splitlines()
    critical_latch = [l for l in lines if "persistence disabled" in l.lower() or "PERSISTENCE_LATCH" in l]
    mutation_prohibited = [l for l in lines if "MUTATION_PROHIBITED" in l]
    if len(mutation_prohibited) > 3:
        return [f"WARN: {len(mutation_prohibited)} MUTATION_PROHIBITED lines — latch may not be active"]
    if critical_latch:
        return [f"OK: latch activated — {len(critical_latch)} latch log line(s)"]
    return ["INFO: no persistence latch activation (no prohibited save attempted, or dry-run)"]


# ---------------------------------------------------------------------------
# Evidence formatting
# ---------------------------------------------------------------------------


def _fmt_run_section(run: dict, run_index: int) -> str:
    label = run["label"]
    argv_str = " ".join(run["argv"])
    env_str = (
        "\n".join(f"  {k}={v}" for k, v in run["env_overrides"].items())
        if run["env_overrides"]
        else "  (none)"
    )
    stdout_trimmed = run["stdout"][:8000] if len(run["stdout"]) > 8000 else run["stdout"]
    stderr_trimmed = run["stderr"][:4000] if len(run["stderr"]) > 4000 else run["stderr"]
    if len(run["stdout"]) > 8000:
        stdout_trimmed += f"\n... [truncated {len(run['stdout']) - 8000} chars]"
    if len(run["stderr"]) > 4000:
        stderr_trimmed += f"\n... [truncated {len(run['stderr']) - 4000} chars]"

    assertions = []
    assertions += _check_termination(run)
    assertions += _check_no_mutation_spam(run)
    assertions += _check_plan_only(run)
    assertions += _check_persistence_latch(run)

    assertion_block = "\n".join(f"- {a}" for a in assertions)

    return f"""
### Run {run_index}: {label}

**argv:** `{argv_str}`

**env overrides:**
```
{env_str}
```

**exit code:** `{run["returncode"]}`
**elapsed:** `{run["elapsed"]:.1f}s`
**timed_out:** `{run["timed_out"]}`

**assertions:**
{assertion_block}

**stdout:**
```
{stdout_trimmed}
```

**stderr:**
```
{stderr_trimmed}
```
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    # --- preflight ---
    git_head = run_cmd(["git", "rev-parse", "HEAD"], label="git rev-parse HEAD")
    git_status = run_cmd(["git", "status", "--porcelain"], label="git status")
    python_v = run_cmd([sys.executable, "-V"], label="python -V")

    # LongPaths check
    longpaths_active = False
    longpaths_note = ""
    try:
        import winreg  # noqa: PLC0415

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
        )
        val, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        longpaths_active = val == 1
        longpaths_note = f"LongPathsEnabled registry value = {val}"
    # guardian: allow-silent-swallower
    except Exception as exc:
        longpaths_note = f"Could not read LongPathsEnabled: {exc}"

    code_commit = git_head["stdout"].strip()

    # --- define commands ---
    dry_run_argv = [
        sys.executable,
        "-m",
        "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
        "--legacy",
        "--domains",
        "--dry-run",
        "-v",
    ]

    # Full heal requires AGENTIC_BYPASS_LONGPATHS_CHECK=1 when LongPathsEnabled=0
    heal_env = {}
    bypass_note = ""
    if not longpaths_active:
        heal_env["AGENTIC_BYPASS_LONGPATHS_CHECK"] = "1"
        bypass_note = (
            "BYPASS RECORDED: AGENTIC_BYPASS_LONGPATHS_CHECK=1 set because "
            "Windows LongPathsEnabled registry value is 0 (not active). "
            "This bypass is documented in execute_ssot.py and is the OS-correct "
            "workaround for this environment."
        )

    heal_argv = [
        sys.executable,
        "-m",
        "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
        "--legacy",
        "--allow-protected-root-mutation",
        "--domains",
        "-v",
    ]

    # --- execute all 4 runs ---
    print("[Phase3] Run 1/4: dry-run (first pass)...")
    dry1 = run_cmd(dry_run_argv, label="Phase3A dry-run run-1")
    print(f"  exit={dry1['returncode']} elapsed={dry1['elapsed']:.1f}s timed_out={dry1['timed_out']}")

    print("[Phase3] Run 2/4: full heal (first pass)...")
    heal1 = run_cmd(heal_argv, env=heal_env, label="Phase3B full-heal run-1")
    print(f"  exit={heal1['returncode']} elapsed={heal1['elapsed']:.1f}s timed_out={heal1['timed_out']}")

    print("[Phase3] Run 3/4: dry-run (second pass — determinism)...")
    dry2 = run_cmd(dry_run_argv, label="Phase3A dry-run run-2")
    print(f"  exit={dry2['returncode']} elapsed={dry2['elapsed']:.1f}s timed_out={dry2['timed_out']}")

    print("[Phase3] Run 4/4: full heal (second pass — determinism)...")
    heal2 = run_cmd(heal_argv, env=heal_env, label="Phase3B full-heal run-2")
    print(f"  exit={heal2['returncode']} elapsed={heal2['elapsed']:.1f}s timed_out={heal2['timed_out']}")

    # --- post-run hygiene ---
    post_status = run_cmd(["git", "status", "--porcelain"], label="post-run git status")

    # --- determinism diffs ---
    def _normalize_stdout(raw: str) -> str:
        """Normalize stdout for determinism comparison.

        Strategy: parse each top-level JSON object/array in the output
        and re-dump with sort_keys=True so trailing-comma / key-order
        differences are eliminated.  Non-JSON lines are kept verbatim.
        """
        normalized_lines = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith(("{", "[", '"')):
                try:
                    obj = json.loads(stripped)
                    normalized_lines.append(json.dumps(obj, sort_keys=True))
                    continue
                except json.JSONDecodeError:
                    pass
            normalized_lines.append(line)
        return "\n".join(normalized_lines)

    def _diff_outputs(r1: dict, r2: dict) -> str:
        if r1["returncode"] != r2["returncode"]:
            return f"FAIL: EXIT CODE DIFFERS: run1={r1['returncode']} run2={r2['returncode']}"
        # Raw match
        if r1["stdout"] == r2["stdout"]:
            return "IDENTICAL: exit codes and stdout match exactly (raw)."
        # Normalized match
        n1 = _normalize_stdout(r1["stdout"])
        n2 = _normalize_stdout(r2["stdout"])
        if n1 == n2:
            return (
                "DIFF: JSON formatting-only; normalized match. "
                "Exit codes identical. Termination behavior identical. "
                "Normalization: json.loads + json.dumps(sort_keys=True) per line."
            )
        # True non-determinism
        lines1 = set(n1.splitlines())
        lines2 = set(n2.splitlines())
        only1 = sorted(lines1 - lines2)[:5]
        only2 = sorted(lines2 - lines1)[:5]
        parts = [f"FAIL: STDOUT DIFFERS after normalization: {len(lines1 ^ lines2)} unique lines differ"]
        if only1:
            parts.append("  Only in run1: " + "; ".join(only1[:3]))
        if only2:
            parts.append("  Only in run2: " + "; ".join(only2[:3]))
        return "\n".join(parts)

    dry_diff = _diff_outputs(dry1, dry2)
    heal_diff = _diff_outputs(heal1, heal2)

    # --- overall pass/fail ---
    all_runs = [dry1, dry2, heal1, heal2]
    any_timeout = any(r["timed_out"] for r in all_runs)
    overall = "FAIL: at least one run timed out" if any_timeout else "PASS: all 4 runs terminated"

    # --- write evidence ---
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Phase 3 Integration Validation Evidence")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "Validate that Phase 1+2 fixes (GravityLeakRepairAgent circuit breaker + "
        "RuntimeStateManager persistence latch) produce deterministic, terminating "
        "behaviour during both dry-run and full-heal execute_ssot runs."
    )
    lines.append("")
    lines.append("## CODE_COMMIT")
    lines.append("")
    lines.append(code_commit)
    lines.append("")
    lines.append("## EVIDENCE_COMMIT")
    lines.append("")
    lines.append("PENDING")
    lines.append("")
    lines.append("## Environment")
    lines.append("")
    lines.append(f"- Python: `{python_v['stdout'].strip()}`")
    lines.append(f"- git HEAD: `{code_commit}`")
    lines.append(f"- LongPaths: `{longpaths_note}`")
    if bypass_note:
        lines.append(f"- **{bypass_note}**")
    lines.append("")
    lines.append("## Pre-Run git status")
    lines.append("")
    lines.append("```")
    lines.append(git_status["stdout"].strip() or "(clean)")
    lines.append("```")
    lines.append("")
    lines.append("## Overall Result")
    lines.append("")
    lines.append(f"**{overall}**")
    lines.append("")
    lines.append("## Determinism Check")
    lines.append("")
    lines.append("### dry-run run-1 vs run-2")
    lines.append("")
    lines.append(dry_diff)
    lines.append("")
    lines.append("### full-heal run-1 vs run-2")
    lines.append("")
    lines.append(heal_diff)
    lines.append("")
    lines.append("## Run Outputs")
    lines.append("")
    for i, run in enumerate([dry1, heal1, dry2, heal2], 1):
        lines.append(_fmt_run_section(run, i))
    lines.append("")
    lines.append("## Post-Run git status")
    lines.append("")
    lines.append("```")
    lines.append(post_status["stdout"].strip() or "(clean)")
    lines.append("```")
    lines.append("")
    lines.append("## INSPECTED_FILES")
    lines.append("")
    lines.append("- agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py")
    lines.append("- agentic_core/L0_routing/scripts/execute_ssot.py")
    lines.append("- agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py")
    lines.append("- tests/agentic_core/L5_safety/gravity/test_gravity_leak_repair_agent.py")
    lines.append("")

    content = "\n".join(lines)
    # ASCII-only enforcement
    non_ascii = [(i, c) for i, c in enumerate(content) if ord(c) > 0x7F]
    if non_ascii:
        for idx, ch in non_ascii[:5]:
            content = content.replace(ch, "?")

    EVIDENCE_PATH.write_text(content, encoding="utf-8")
    print(f"\n[Phase3] Evidence written to: {EVIDENCE_PATH}")
    print(f"[Phase3] Overall: {overall}")
    return 0 if not any_timeout else 1


if __name__ == "__main__":
    sys.exit(main())
