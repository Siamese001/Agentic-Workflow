"""Evidence runner for L2.3 Healing Tier Router.

Commit+amend flow captures Git Proof Completeness Gate AFTER
evidence-only HEAD exists, eliminating the chicken-and-egg problem.

Sequence:
  1. Preflight: assert clean porcelain
  2. CODE_COMMIT = git rev-parse HEAD (current code commit)
  3. Run pytest
  4. Write initial evidence (CODE_COMMIT + SEALED_FROM only)
  5. git add + commit (with pre-commit retry)  -> evidence-only HEAD
  6. Capture 6 git commands verbatim AFTER evidence-only HEAD exists
  7. Run assertions (hard-fail on any mismatch)
  8. Rewrite evidence with git proof + assertions
  9. git add + commit --amend --no-edit (with pre-commit retry)
  10. Re-verify post-amend invariants
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / "docs" / "reports" / "plans" / "healing_tier_router_evidence.md"
EVIDENCE_REL = "docs/reports/plans/healing_tier_router_evidence.md"

_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _write_lf(lines: list[str]) -> None:
    """Write evidence file with explicit LF line endings (no CRLF)."""
    with open(EVIDENCE_PATH, "w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")


def _clean(text: str) -> str:
    """Strip ANSI escapes and non-ASCII bytes."""
    text = _ANSI_RE.sub("", text)
    return text.encode("ascii", errors="replace").decode("ascii")


def run(argv: list[str]) -> tuple[int, str]:
    """Run command, return (exit_code, combined_output)."""
    r = subprocess.run(
        argv,
        cwd=str(REPO_ROOT),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    return r.returncode, _clean((r.stdout or "") + (r.stderr or ""))


def stdout(argv: list[str]) -> str:
    """Run command, return stripped stdout. Hard-fail on non-zero exit."""
    r = subprocess.run(
        argv,
        cwd=str(REPO_ROOT),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    if r.returncode != 0:
        print(f"FAIL: {' '.join(argv)} exited {r.returncode}", file=sys.stderr)
        print(_clean(r.stderr or ""), file=sys.stderr)
        sys.exit(1)
    return _clean((r.stdout or "").strip())


def validate_40hex(label: str, value: str) -> str:
    """Validate 40-hex. Returns the OK line. Hard-fails on mismatch."""
    if _HEX40_RE.match(value):
        line = f"OK: {label} validated as 40-hex: {value}"
        print(line)
        return line
    print(f"FAIL: {label} is not valid 40-hex: '{value}'", file=sys.stderr)
    sys.exit(1)


def git_add_commit(message: str) -> None:
    """Stage evidence file and commit. Retries once for pre-commit hook fixes."""
    for attempt in range(2):
        rc_add, _ = run(["git", "add", EVIDENCE_REL])
        if rc_add != 0:
            print(f"FAIL: git add exited {rc_add}", file=sys.stderr)
            sys.exit(1)
        rc_commit, out = run(["git", "commit", "-m", message])
        if rc_commit == 0:
            return
        # Pre-commit hooks may fix line endings on first attempt; retry
        if attempt == 0:
            print("INFO: Pre-commit hooks modified files, retrying commit...")
            continue
        print(f"FAIL: git commit exited {rc_commit}\n{out}", file=sys.stderr)
        sys.exit(1)


def git_add_amend() -> None:
    """Stage evidence file and amend. Retries once for pre-commit hook fixes."""
    for attempt in range(2):
        rc_add, _ = run(["git", "add", EVIDENCE_REL])
        if rc_add != 0:
            print(f"FAIL: git add exited {rc_add}", file=sys.stderr)
            sys.exit(1)
        rc_amend, out = run(["git", "commit", "--amend", "--no-edit"])
        if rc_amend == 0:
            return
        if attempt == 0:
            print("INFO: Pre-commit hooks modified files, retrying amend...")
            continue
        print(f"FAIL: git commit --amend exited {rc_amend}\n{out}", file=sys.stderr)
        sys.exit(1)


def hard_assert(condition: bool, ok_msg: str, fail_msg: str) -> str:
    """Assert condition. Print OK line and return it, or hard-fail."""
    if condition:
        print(ok_msg)
        return ok_msg
    print(f"FAIL: {fail_msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    evidence_lines: list[str] = []  # rebuilt from scratch every run
    assertion_lines: list[str] = []

    # ── Step 1: Preflight ─────────────────────────────────────────────
    print("=== Step 1: Preflight ===")
    porcelain_pre = stdout(["git", "status", "--porcelain"])
    hard_assert(
        len(porcelain_pre) == 0,
        "OK: Preflight git status --porcelain is empty",
        f"Working tree not clean: {porcelain_pre}",
    )

    # ── Step 2: CODE_COMMIT = current HEAD ────────────────────────────
    print("\n=== Step 2: CODE_COMMIT ===")
    code_commit = stdout(["git", "rev-parse", "HEAD"])
    sealed_from = code_commit
    validate_40hex("CODE_COMMIT", code_commit)
    validate_40hex("SEALED_FROM", sealed_from)

    # ── Step 3: Run pytest ────────────────────────────────────────────
    print("\n=== Step 3: Pytest ===")
    test_argv = [
        sys.executable,
        "-m",
        "pytest",
        "tests/agentic_core/L2_execution/healers/test_healing_tier_router.py",
        "-v",
        "--color=no",
        "--tb=short",
        "-m",
        "unit_min_deps",
    ]
    test_cmd_str = " ".join(test_argv)
    print(f"$ {test_cmd_str}")
    test_rc, test_out = run(test_argv)
    test_out = test_out.strip()
    print(test_out)
    if test_rc != 0:
        print(f"FAIL: pytest exited {test_rc}", file=sys.stderr)
        sys.exit(1)
    print("OK: pytest passed")

    # ── Step 4: Write initial evidence ────────────────────────────────
    print("\n=== Step 4: Write initial evidence ===")
    evidence_lines = [
        "# L2.3 Healing Tier Router - Evidence",
        "",
        "## Scope",
        "",
        "Implement centralized L2.3 healing tier router with:",
        "- HealingInput/HealingDecision/FailureSignal contracts",
        "- L4-backed config (X/Y thresholds, model IDs)",
        "- Deterministic heal_confidence scoring",
        "- Single choke point tier routing",
        "- Tiering allowlist (10 YES_TIERING agents)",
        "- AST-based enforcement (NO_TIERING prohibition)",
        "- Determinism proof (byte-identical decisions)",
        "",
        f"CODE_COMMIT={code_commit}",
        f"SEALED_FROM={sealed_from}",
        "",
        "## Config Values",
        "",
        "```",
        "HEAL_CONFIDENCE_X=0.75",
        "HEAL_CONFIDENCE_Y=0.40",
        "MAX_HEAL_RETRIES=3",
        "MODEL_QWEN_VLLM_ID=qwen2.5-coder-32b-instruct",
        "MODEL_GEMINI_2_5_PRO_ID=gemini-2.5-pro",
        "```",
        "",
        "## Test Execution",
        "",
        f"$ {test_cmd_str}",
        "",
        "```",
        test_out,
        "```",
        "",
    ]
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_lf(evidence_lines)
    print(f"OK: Initial evidence written to {EVIDENCE_PATH}")

    # ── Step 5: Create evidence-only commit ───────────────────────────
    print("\n=== Step 5: Create evidence-only commit ===")
    git_add_commit("docs: healing tier router evidence (sealed)")
    print("OK: Evidence-only commit created")

    # ── Step 6: Capture 6 git commands AFTER evidence-only HEAD ───────
    print("\n=== Step 6: Git Proof Completeness Gate ===")
    git_cmds: list[tuple[str, str]] = []

    for label, argv in [
        ("git log -1 --format=%H", ["git", "log", "-1", "--format=%H"]),
        ("git rev-parse HEAD", ["git", "rev-parse", "HEAD"]),
        ("git rev-parse HEAD~1", ["git", "rev-parse", "HEAD~1"]),
        ("git rev-parse HEAD~2", ["git", "rev-parse", "HEAD~2"]),
        (
            "git show --name-only --pretty=format: HEAD",
            ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
        ),
        ("git status --porcelain", ["git", "status", "--porcelain"]),
    ]:
        out = stdout(argv)
        git_cmds.append((label, out))
        print(f"$ {label}")
        print(out if out else "")

    # Unpack for assertions
    v_log = git_cmds[0][1]
    v_head = git_cmds[1][1]
    v_head1 = git_cmds[2][1]
    _ = git_cmds[3][1]  # HEAD~2 captured in git_cmds for evidence
    v_show = git_cmds[4][1]
    v_porcelain = git_cmds[5][1]

    # ── Step 7: Assertions ────────────────────────────────────────────
    print("\n=== Step 7: Assertions ===")

    assertion_lines.append(
        hard_assert(
            v_log == v_head,
            f"OK: git log -1 == git rev-parse HEAD: {v_log}",
            f"git log -1 ({v_log}) != git rev-parse HEAD ({v_head})",
        )
    )
    assertion_lines.append(
        hard_assert(
            len(v_porcelain) == 0,
            "OK: len(porcelain_stdout) == 0",
            f"porcelain not empty: {v_porcelain}",
        )
    )
    assertion_lines.append(
        hard_assert(
            v_show.strip() == EVIDENCE_REL,
            f"OK: git show --name-only HEAD lists only: {EVIDENCE_REL}",
            f"git show --name-only HEAD unexpected: {v_show.strip()}",
        )
    )

    # Read evidence file directly (no git subprocess)
    ev_content = EVIDENCE_PATH.read_text(encoding="utf-8")
    ex_code = ex_sealed = None
    for ln in ev_content.splitlines():
        if ln.startswith("CODE_COMMIT="):
            ex_code = ln.split("=", 1)[1]
        elif ln.startswith("SEALED_FROM="):
            ex_sealed = ln.split("=", 1)[1]
    if ex_code is None or ex_sealed is None:
        print("FAIL: Could not extract CODE_COMMIT/SEALED_FROM", file=sys.stderr)
        sys.exit(1)

    assertion_lines.append(validate_40hex("CODE_COMMIT", ex_code))
    assertion_lines.append(validate_40hex("SEALED_FROM", ex_sealed))

    assertion_lines.append(
        hard_assert(
            v_head1 == ex_code == ex_sealed,
            f"OK: HEAD~1 == CODE_COMMIT == SEALED_FROM: {v_head1}",
            f"HEAD~1 ({v_head1}) != CODE_COMMIT ({ex_code}) != SEALED_FROM ({ex_sealed})",
        )
    )

    # ── Step 8: Rewrite evidence with git proof + assertions ──────────
    print("\n=== Step 8: Rewrite evidence with git proof ===")

    # Append git proof section
    evidence_lines.append("## Git Proof Completeness Gate (post evidence-only HEAD)")
    evidence_lines.append("")
    for label, out in git_cmds:
        evidence_lines.append(f"$ {label}")
        evidence_lines.append(out if out else "")
        evidence_lines.append("")

    # Append assertions
    evidence_lines.append("## Assertions")
    evidence_lines.append("")
    for a in assertion_lines:
        evidence_lines.append(a)
    evidence_lines.append("")

    # FILES_CHANGED_CODE
    code_files = stdout(["git", "show", "--name-only", "--pretty=format:", code_commit])
    evidence_lines.extend(
        [
            "## FILES_CHANGED_CODE",
            "",
            "```",
            code_files.strip(),
            "```",
            "",
        ]
    )

    # INSPECTED_FILES
    evidence_lines.extend(
        [
            "## INSPECTED_FILES",
            "",
            "```",
            "agentic_core/L2_execution/healers/healing_tier_types.py",
            "agentic_core/L2_execution/healers/healing_tier_config.py",
            "agentic_core/L2_execution/healers/healing_tier_router.py",
            "agentic_core/L2_execution/healers/tiering_allowlist.py",
            "tests/agentic_core/L2_execution/healers/test_healing_tier_router.py",
            "docs/technical/agent_confidence_tiering_recommendations.csv",
            "docs/technical/agent_confidence_tiering_recommendations.md",
            "```",
            "",
        ]
    )

    _write_lf(evidence_lines)
    print(f"OK: Complete evidence written to {EVIDENCE_PATH}")

    # ── Step 9: Amend the commit ──────────────────────────────────────
    print("\n=== Step 9: Amend evidence commit ===")
    git_add_amend()
    print("OK: Evidence commit amended")

    # ── Step 10: Re-verify post-amend ─────────────────────────────────
    print("\n=== Step 10: Post-amend re-verification ===")
    post_head = stdout(["git", "rev-parse", "HEAD"])
    post_head1 = stdout(["git", "rev-parse", "HEAD~1"])
    post_show = stdout(["git", "show", "--name-only", "--pretty=format:", "HEAD"])
    post_porcelain = stdout(["git", "status", "--porcelain"])

    hard_assert(
        post_show.strip() == EVIDENCE_REL,
        f"OK: Post-amend HEAD is evidence-only: {EVIDENCE_REL}",
        f"Post-amend HEAD not evidence-only: {post_show.strip()}",
    )
    hard_assert(
        post_head1 == code_commit,
        f"OK: Post-amend HEAD~1 == CODE_COMMIT: {post_head1}",
        f"Post-amend HEAD~1 ({post_head1}) != CODE_COMMIT ({code_commit})",
    )
    hard_assert(
        len(post_porcelain) == 0,
        "OK: Post-amend git status --porcelain is empty",
        f"Post-amend porcelain not empty: {post_porcelain}",
    )

    print("\n=== SUCCESS ===")
    print(f"Evidence file: {EVIDENCE_PATH}")
    print(f"HEAD (evidence-only): {post_head}")
    print(f"HEAD~1 (CODE_COMMIT): {post_head1}")


if __name__ == "__main__":
    main()
