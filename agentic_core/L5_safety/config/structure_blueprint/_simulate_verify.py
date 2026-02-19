"""
Simulation harness for _verify.py — runs A–F style tests using temp copies.

Never edits committed lock files in-place. Uses backup/restore pattern
with a TemporaryDirectory to guarantee repo cleanliness.
Enforces byte-equal restoration of all lock files after simulations.

Run: python -m agentic_core.L5_safety.config.structure_blueprint._simulate_verify
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

from agentic_core.L2_execution.tools import write_gateway as _wg


def _repo_root() -> str:
    # guardian: allow-path-string
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _read_bytes(path: str) -> bytes | None:
    """Read file as bytes, return None if missing."""
    # guardian: allow-path-string
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def _run_verify(*extra_args: str) -> tuple[int, str]:
    """Run the verifier as a subprocess, return (exit_code, combined_output)."""
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L5_safety.config.structure_blueprint._verify",
        *extra_args,
    ]
    # guardian: allow-magic-config
    result = subprocess.run(
        cmd,
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    root = _repo_root()
    # guardian: allow-path-string
    baseline_path = os.path.join(root, "docs", "reports", "plans", "phantom_baseline.json")
    # guardian: allow-path-string
    hash_path = os.path.join(root, "docs", "reports", "plans", "allowlist_hash.txt")
    # guardian: allow-path-string
    debt_path = os.path.join(root, "docs", "reports", "plans", "phantom_debt.md")
    results: list[tuple[str, bool, str]] = []  # (name, passed, detail)

    # Snapshot lock file bytes at start
    snap_baseline = _read_bytes(baseline_path)
    snap_hash = _read_bytes(hash_path)
    snap_debt = _read_bytes(debt_path)

    with tempfile.TemporaryDirectory(prefix="ssot_sim_") as tmpdir:
        # Backup originals
        # guardian: allow-path-string
        backup_baseline = os.path.join(tmpdir, "phantom_baseline.json")
        # guardian: allow-path-string
        backup_hash = os.path.join(tmpdir, "allowlist_hash.txt")
        # guardian: allow-path-string
        backup_debt = os.path.join(tmpdir, "phantom_debt.md")
        # guardian: allow-path-string
        if os.path.isfile(baseline_path):
            _wg.copy_file(baseline_path, backup_baseline)
        # guardian: allow-path-string
        if os.path.isfile(hash_path):
            _wg.copy_file(hash_path, backup_hash)
        # guardian: allow-path-string
        if os.path.isfile(debt_path):
            _wg.copy_file(debt_path, backup_debt)

        def _restore() -> None:
            """Restore original lock files from backup."""
            # guardian: allow-path-string
            if os.path.isfile(backup_baseline):
                _wg.copy_file(backup_baseline, baseline_path)
            # guardian: allow-path-string
            if os.path.isfile(backup_hash):
                _wg.copy_file(backup_hash, hash_path)
            # guardian: allow-path-string
            if os.path.isfile(backup_debt):
                _wg.copy_file(backup_debt, debt_path)

        # ── SIM 1: Allowlist mismatch → FAIL, then ack → exit 0 ──
        try:
            _wg.open_write(hash_path, "TAMPERED_SIM_HASH\n")
            rc, out = _run_verify()
            sim1_fail = rc != 0 and "MISMATCH" in out
            rc2, out2 = _run_verify("--acknowledge-import-change")
            sim1_ack = rc2 == 0 and "UPDATED" in out2
            passed = sim1_fail and sim1_ack
            detail = f"mismatch_fail={sim1_fail}, ack_ok={sim1_ack}"
            results.append(("SIM1: Allowlist mismatch + ack", passed, detail))
        finally:
            _restore()

        # ── SIM 2: Corrupt baseline → FAIL, then repair → exit 0 ──
        try:
            _wg.open_write(baseline_path, "NOT VALID JSON")
            rc, out = _run_verify()
            sim2_fail = rc != 0 and "CORRUPT" in out
            rc2, out2 = _run_verify("--repair-phantom-baseline")
            sim2_repair = rc2 == 0 and "REPAIRED" in out2
            passed = sim2_fail and sim2_repair
            detail = f"corrupt_fail={sim2_fail}, repair_ok={sim2_repair}"
            results.append(("SIM2: Corrupt baseline + repair", passed, detail))
        finally:
            _restore()

        # ── SIM 3: Absolute path in baseline → FAIL with guidance ──
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                data = json.load(bf)
            data[0][0] = "/absolute/path/file.py"
            _wg.write_json(baseline_path, data, indent=2)
            rc, out = _run_verify()
            passed = rc != 0 and "repo-relative-normalized" in out
            detail = f"rc={rc}, has_guidance={'repo-relative-normalized' in out}"
            results.append(("SIM3: Absolute path in baseline", passed, detail))
        finally:
            _restore()

        # ── SIM 4: SyntaxError in scanned file → FAIL with location ──
        # guardian: allow-path-string
        syntax_err_path = os.path.join(root, "tests", "_tmp_syntax_err_sim.py")
        try:
            _wg.open_write(
                syntax_err_path,
                "from agentic_core.L5_safety.config.structure_blueprint import FAKE\ndef broken(\n",
            )
            rc, out = _run_verify()
            passed = rc != 0 and "SyntaxError" in out and "_tmp_syntax_err_sim" in out
            detail = f"rc={rc}, syntax_detected={'SyntaxError' in out}"
            results.append(("SIM4: SyntaxError in tests/", passed, detail))
        finally:
            # guardian: allow-path-string
            if os.path.isfile(syntax_err_path):
                _wg.remove_file(syntax_err_path)
            _restore()

        # ── SIM 5: Remove one baseline entry → FAIL with Baseline-only ──
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                data = json.load(bf)
            if len(data) > 1:
                data.pop()
                _wg.write_json(baseline_path, data, indent=2)
                rc, out = _run_verify()
                has_current_only = "Current-only entries" in out
                passed = rc != 0 and has_current_only
                detail = f"rc={rc}, current_only={has_current_only}"
            else:
                passed = False
                detail = "baseline too small to test"
            results.append(("SIM5: Baseline entry removal → diff", passed, detail))
        finally:
            _restore()

        # ── SIM 6: Backslash path in baseline → FAIL with canonical msg ──
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                data = json.load(bf)
            data[0][0] = "agentic_core\\L0_routing\\scripts\\fake.py"
            _wg.write_json(baseline_path, data, indent=2)
            rc, out = _run_verify()
            passed = rc != 0 and "repo-relative-normalized" in out
            detail = f"rc={rc}, canonical_fail={'repo-relative-normalized' in out}"
            results.append(("SIM6: Backslash path in baseline", passed, detail))
        finally:
            _restore()

        # ── SIM 7: CI guard self-test (in-memory, no repo modification) ──
        try:
            MODULE = "agentic_core.L5_safety.config.structure_blueprint._verify"
            FORBIDDEN = [
                "--init-phantom-baseline",
                "--update-phantom-baseline",
                "--repair-phantom-baseline",
                "--acknowledge-import-change",
            ]

            def _find_invoke_lines(text: str) -> list[str]:
                """Same logic as CI guard: exact module path, line-level."""
                found = []
                for line in text.splitlines():
                    s = line.strip()
                    if s.startswith("#") or s.startswith('"') or s.startswith("'"):
                        continue
                    if "python" in s and "-m" in s and MODULE in s:
                        found.append(s)
                return found

            # guardian: allow-path-string
            wf_path = os.path.join(root, ".github", "workflows", "ssot_verify.yml")
            with open(wf_path, encoding="utf-8") as wf:
                wf_text = wf.read()

            # Clean workflow: must have >=1 invocation, 0 violations
            clean_invoke = _find_invoke_lines(wf_text)
            clean_count = len(clean_invoke)
            clean_violations = []
            for line in clean_invoke:
                for flag in FORBIDDEN:
                    if flag in line:
                        clean_violations.append(flag)
            clean_pass = clean_count >= 1 and len(clean_violations) == 0

            # Tampered workflow: inject forbidden flag on invocation line
            tampered = wf_text.replace(
                f"python -m {MODULE}",
                f"python -m {MODULE} --init-phantom-baseline",
            )
            tampered_invoke = _find_invoke_lines(tampered)
            tampered_count = len(tampered_invoke)
            tampered_violations = []
            for line in tampered_invoke:
                for flag in FORBIDDEN:
                    if flag in line:
                        tampered_violations.append(flag)
            tampered_detected = len(tampered_violations) > 0

            passed = clean_pass and tampered_detected and tampered_count >= 1
            detail = (
                f"clean_invocations={clean_count}, "
                f"clean_pass={clean_pass}, "
                f"tampered_invocations={tampered_count}, "
                f"tampered_detected={tampered_detected}"
            )
            results.append(("SIM7: CI guard self-test (in-memory)", passed, detail))
        # guardian: allow-silent-swallow
        except Exception as exc:
            results.append(("SIM7: CI guard self-test (in-memory)", False, str(exc)))

    # ── Report ──
    print("=" * 60)
    print("SIMULATION HARNESS — RESULTS")
    print("=" * 60)
    all_pass = True
    for name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  {status}: {name} ({detail})")

    # ── Enforced byte-equal restoration ──
    print()
    print("  BYTE-EQUAL RESTORATION CHECK:")
    artifacts = [
        ("phantom_baseline.json", baseline_path, snap_baseline),
        ("allowlist_hash.txt", hash_path, snap_hash),
        ("phantom_debt.md", debt_path, snap_debt),
    ]
    for label, path, original_bytes in artifacts:
        current_bytes = _read_bytes(path)
        if original_bytes == current_bytes:
            print(f"    {label}: BYTE-EQUAL \u2714")
        else:
            orig_len = len(original_bytes) if original_bytes is not None else "MISSING"
            curr_len = len(current_bytes) if current_bytes is not None else "MISSING"
            print(f"    {label}: DIFFERS (original={orig_len}, current={curr_len})")
            all_pass = False

    # Verify temp files deleted
    # guardian: allow-path-string
    syntax_leftover = os.path.join(root, "tests", "_tmp_syntax_err_sim.py")
    # guardian: allow-path-string
    if os.path.isfile(syntax_leftover):
        print("    Temp syntax file: WARNING — not cleaned up")
        all_pass = False
    else:
        print("    Temp syntax file: CLEAN \u2714")

    # Optional git diff check
    try:
        # guardian: allow-magic-config
        git_result = subprocess.run(
            [
                "git",
                "diff",
                "--exit-code",
                "--",
                "docs/reports/plans/phantom_baseline.json",
                "docs/reports/plans/allowlist_hash.txt",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if git_result.returncode == 0:
            print("    git diff lock files: CLEAN \u2714")
        else:
            print("    git diff lock files: DIRTY")
            print(git_result.stdout[:500] if git_result.stdout else "")
            all_pass = False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("    git diff: SKIPPED (git not available)")

    print()
    if all_pass:
        print("OVERALL: PASS — all simulations green, repo byte-equal clean")
    else:
        print("OVERALL: FAIL — see above")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
