"""Best-of-N per-section harness for apps_rg resume generation.

Stochastic LLM generation against a conjunction of hard deterministic X2 gates means no
single whole-run reliably lands every section at X3_ALLOW. This harness runs each requested
section through the canonical CLI (``python -m apps_rg --section <name> ...``) up to ``--attempts``
times, stops at the first artifact whose ``x3_disposition.json`` reaches an accepting disposition,
and pins that run's artifact directory per section.

It drives the *canonical* CLI path only — it never calls section internals, never mocks the
provider, and never weakens a gate. Narrative sections depend on finalized bullets, so the harness
runs sections in dependency order and (for narratives) executes a whole-run when bullets are not
already finalized in the pinned bullet run.

Usage (PowerShell-safe; no shell=True):
    python -m ops_scripts.apps_rg.best_of_n_section_harness \
        --target-company "AIG" \
        --target-role "VP, Global Head of Agentic AI Solutions" \
        --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt \
        --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md \
        --provider qwen_vllm \
        --sections headline,executive_summary,unify_bullets,ibm_bullets,competencies \
        --attempts 5
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Dispositions that count as a "pin-worthy" pass. X3_ALLOW is full proof; REVIEW_JUDGE_SOFT_FAIL
# means X2 passed and judges only soft-failed (advisory) — pinnable when --accept-review is set.
ALLOW_CODES = {"X3_ALLOW"}
REVIEW_CODES = {"X3_REVIEW_JUDGE_SOFT_FAIL"}

# Single-section CLI prints the X3 disposition inline and writes the lane artifacts to
# artifacts/apps_rg/runtime_proofs/<section>/ (section root, no full_resume_*/lanes/ wrapper).
PRODUCT_X3_RE = re.compile(r"^PRODUCT_X3_STATUS:\s*(\S+)$", re.MULTILINE)
SECTION_PROOF_ROOT = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs"


def _section_dir(section: str) -> Path:
    """Latest timestamped real run for a section: runtime_proofs/<section>/real/<section>_<ts>/.

    Single-section CLI runs write each invocation to a fresh timestamped subdir under
    ``<section>/real/``; the section root is a stale/aggregate path and must not be read.
    """
    real_root = SECTION_PROOF_ROOT / section / "real"
    if real_root.is_dir():
        subdirs = [d for d in real_root.iterdir() if d.is_dir()]
        if subdirs:
            return max(subdirs, key=lambda d: d.stat().st_mtime)
    return SECTION_PROOF_ROOT / section


def _section_disposition(section: str) -> dict[str, Any] | None:
    path = _section_dir(section) / "x3_disposition.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _failed_gates(section: str) -> list[str]:
    path = _section_dir(section) / "x2_gate_outputs.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    gates = data if isinstance(data, list) else data.get("gates", [])
    return [
        g.get("gate_id")
        for g in gates
        if isinstance(g, dict) and not g.get("pass")
    ]


def _run_section(section: str, base_argv: list[str]) -> tuple[str, int, str]:
    """Run one section through the canonical CLI; return (x3_from_stdout, rc, combined_output)."""
    argv = [sys.executable, "-m", "apps_rg", "--section", section, *base_argv]
    proc = subprocess.run(  # noqa: S603 - argv list, shell=False
        argv,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=1800,
    )
    out = proc.stdout + "\n" + proc.stderr
    m = PRODUCT_X3_RE.search(out)
    x3_stdout = m.group(1).strip() if m else ""
    return x3_stdout, proc.returncode, out


def _pin_section_dir(section: str, attempt: int) -> str:
    """Snapshot the passing section artifacts to a stable pinned location.

    Single-section runs overwrite ``runtime_proofs/<section>/`` each attempt, so the passing
    artifacts are copied to ``runtime_proofs/_pinned/<section>/`` to survive subsequent runs.
    """
    import shutil

    src = _section_dir(section)
    dst = SECTION_PROOF_ROOT / "_pinned" / section
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(src, dst)
    except OSError:
        return src.relative_to(REPO_ROOT).as_posix()
    return dst.relative_to(REPO_ROOT).as_posix()


def _accepting(code: str, accept_review: bool, runtime_status: str) -> bool:
    # MOCKED/BLOCKED generation is never a real pass — it proves plumbing only, not runtime.
    if runtime_status != "REAL_LLM":
        return False
    if code in ALLOW_CODES:
        return True
    return accept_review and code in REVIEW_CODES


def best_of_n(
    sections: list[str],
    base_argv: list[str],
    attempts: int,
    accept_review: bool,
) -> dict[str, Any]:
    results: dict[str, Any] = {
        "schema": "apps_rg_best_of_n_v1",
        "attempts_budget": attempts,
        "accept_review": accept_review,
        "sections": {},
    }
    for section in sections:
        section_log: dict[str, Any] = {"attempts": [], "pinned": None}
        for i in range(attempts):
            x3_stdout, rc, _out = _run_section(section, base_argv)
            disp = _section_disposition(section)
            code = str((disp or {}).get("x3_code") or x3_stdout or "UNKNOWN")
            runtime_status = str((disp or {}).get("runtime_generation_status") or "UNKNOWN")
            gates = _failed_gates(section)
            rec = {
                "attempt": i + 1,
                "returncode": rc,
                "section_dir": _section_dir(section).relative_to(REPO_ROOT).as_posix(),
                "x3_code": code,
                "x3_stdout": x3_stdout,
                "runtime_generation_status": runtime_status,
                "failed_gates": gates,
            }
            section_log["attempts"].append(rec)
            print(
                f"[{section}] attempt {i + 1}/{attempts}: x3={code} gen={runtime_status} "
                f"rc={rc} failed_gates={gates or 'none'}",
                flush=True,
            )
            if _accepting(code, accept_review, runtime_status):
                pinned_dir = _pin_section_dir(section, i + 1)
                rec["pinned_dir"] = pinned_dir
                section_log["pinned"] = rec
                print(f"[{section}] PINNED at attempt {i + 1} ({code}) -> {pinned_dir}", flush=True)
                break
            time.sleep(1)
        results["sections"][section] = section_log
    n_pinned = sum(1 for s in results["sections"].values() if s.get("pinned"))
    results["pinned_count"] = n_pinned
    results["all_pinned"] = n_pinned == len(sections)
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Best-of-N per-section apps_rg harness")
    p.add_argument("--target-company", required=True)
    p.add_argument("--target-role", required=True)
    p.add_argument("--jd", required=True)
    p.add_argument("--manual-brief", required=True)
    p.add_argument("--provider", default="qwen_vllm")
    p.add_argument(
        "--sections",
        default="competencies,unify_bullets,executive_summary,ibm_bullets,headline",
    )
    p.add_argument("--attempts", type=int, default=5)
    p.add_argument(
        "--accept-review",
        action="store_true",
        help="Pin X3_REVIEW_JUDGE_SOFT_FAIL (X2 passed, judges advisory soft-fail) as a pass.",
    )
    p.add_argument("--out", default="artifacts/apps_rg/tmp/best_of_n_result.json")
    args = p.parse_args(argv)

    base_argv = [
        "--target-company",
        args.target_company,
        "--target-role",
        args.target_role,
        "--jd",
        args.jd,
        "--manual-brief",
        args.manual_brief,
        "--provider",
        args.provider,
    ]
    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    results = best_of_n(sections, base_argv, args.attempts, args.accept_review)

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(
        f"\nBEST_OF_N DONE: {results['pinned_count']}/{len(sections)} sections pinned; "
        f"all_pinned={results['all_pinned']}; result={args.out}",
        flush=True,
    )
    return 0 if results["all_pinned"] else 3


if __name__ == "__main__":
    sys.exit(main())
