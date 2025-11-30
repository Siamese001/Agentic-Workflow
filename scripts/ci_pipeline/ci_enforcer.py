#!/usr/bin/env python3
"""
ci_enforcer.py

Agentic L5 CI Orchestrator & Pillar Compliance Reporter
=======================================================

This script is the L3 orchestration layer for repository validation. It:

- Runs all lower-level L2 validators:
    - manifest_validator.py
    - ast_purity_scanner.py
    - contract_registry_validator.py
    - test_matrix_validator.py
    - golden_trace_auditor.py

- Aggregates their results into a single Agentic L5 pillar compliance view.

Pillars covered (via the validator mapping below):

    P1  Structural / Layering Model
    P2  Structural / Agent Boundaries (via structural + purity constraints)
    P3  Structural / Typed Contracts
    P4  Structural / Workflow (DAGs)
    P5  Behavioral / Capability Maturity
    P6  Behavioral / Reasoning Models
    P7  Behavioral / Context Engineering (via structural underpinnings)
    P8  Tool Ecosystem & Resilience
    P9  Safety & Policy Control Plane
    P10 Operational / Observability
    P11 Operational / Cost & Optimization
    P12 Operational / Testing (Golden State)
    P13 Operational / Prompt Governance
    P14 Operational / Execution Sandbox

For each validator:
- Exit code 0 => validator PASS
- Non-zero   => validator FAIL

For each pillar:
- PASS iff all mapped validators passed and at least one validator covers it.
- FAIL otherwise (including coverage gaps).

Outputs:
- Human-readable summary to stdout
- Machine-readable JSON report:
      ci_reports/agentic_l5_ci_report.json

Exit code:
- 0: all validators passed AND all pillars satisfied
- 1: any validator or pillar failed
"""

import json
import os
import sys
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Set


# =====================================================================
# CONFIG
# =====================================================================

DEFAULT_REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
REPO_ROOT = os.getenv("AGENTIC_REPO_ROOT", DEFAULT_REPO_ROOT)

CI_REPORT_DIR = os.path.join(REPO_ROOT, "ci_reports")
CI_REPORT_PATH = os.path.join(CI_REPORT_DIR, "agentic_l5_ci_report.json")

# Per-validator timeout (seconds)
VALIDATOR_TIMEOUT_SEC = 600

# If True, stop running further validators on first failure
FAIL_FAST = False


# =====================================================================
# DATA MODELS
# =====================================================================

@dataclass
class ValidatorConfig:
    name: str
    script: str
    description: str
    # Pillar IDs this validator contributes to (1..14)
    pillars: List[int]


@dataclass
class ValidatorResult:
    name: str
    script: str
    description: str
    exit_code: int
    duration_sec: float
    stdout: str
    stderr: str


@dataclass
class PillarStatus:
    pillar_id: int
    name: str
    validators: List[str]
    passed: bool


# =====================================================================
# PILLAR LABELS
# =====================================================================

PILLAR_LABELS: Dict[int, str] = {
    1: "Structural / Layering Model",
    2: "Structural / Agent Boundaries",
    3: "Structural / Typed Contracts",
    4: "Structural / Workflow (DAGs)",
    5: "Behavioral / Capability Maturity",
    6: "Behavioral / Reasoning Models",
    7: "Behavioral / Context Engineering",
    8: "Tool Ecosystem & Resilience",
    9: "Safety & Policy Control Plane",
    10: "Operational / Observability",
    11: "Operational / Cost & Optimization",
    12: "Testing (Golden State)",
    13: "Prompt Governance",
    14: "Execution Sandbox",
}

# =====================================================================
# VALIDATOR REGISTRY
# =====================================================================

VALIDATORS: List[ValidatorConfig] = [
    ValidatorConfig(
        name="manifest_validator",
        script="manifest_validator.py",
        description=(
            "Filesystem / repo structure validator: root allowlist, depth limits, "
            "hidden policy, forbidden test extensions, empty dirs, agentic_core/apps/tests "
            "and prompt_governance structure, manifest parity."
        ),
        pillars=[1, 3, 4, 8, 11, 12, 13, 14],
    ),
    ValidatorConfig(
        name="ast_purity_scanner",
        script="ast_purity_scanner.py",
        description=(
            "AST-based L1–L5 purity validator: forbidden imports, unsafe calls, "
            "inline prompt governance, type hints, safety isolation, sandboxing invariants."
        ),
        pillars=[1, 2, 3, 4, 6, 8, 9, 11, 14],
    ),
    ValidatorConfig(
        name="contract_registry_validator",
        script="contract_registry_validator.py",
        description=(
            "contracts.yaml validator: tools/planners/executors/agents/mcp_servers "
            "have typed schemas, semver versions, timeouts, retries, cost_tier, "
            "and safety_policy with references to safety_policies."
        ),
        pillars=[3, 8, 9, 11],
    ),
    ValidatorConfig(
        name="test_matrix_validator",
        script="test_matrix_validator.py",
        description=(
            "test_matrix.yaml validator: module<->test mapping completeness, "
            "layer-aligned tests, orphan test detection, observability and golden "
            "runner coverage, test category presence."
        ),
        pillars=[1, 4, 5, 8, 10, 12],
    ),
    ValidatorConfig(
        name="golden_trace_auditor",
        script="golden_trace_auditor.py",
        description=(
            "Golden-flow trace auditor: compares canonical golden_traces.json "
            "with current run traces (id sets and per-flow hashes, schema_version)."
        ),
        pillars=[4, 5, 6, 10, 11, 12],
    ),
]


# =====================================================================
# HELPERS
# =====================================================================

def ensure_report_dir() -> None:
    os.makedirs(CI_REPORT_DIR, exist_ok=True)


def run_validator(cfg: ValidatorConfig) -> ValidatorResult:
    """
    Run a validator as a subprocess and capture results.
    """
    script_path = os.path.join(REPO_ROOT, "scripts", cfg.script)
    start = time.time()

    if not os.path.isfile(script_path):
        duration = time.time() - start
        msg = f"[ci_enforcer] SCRIPT NOT FOUND: {script_path}"
        return ValidatorResult(
            name=cfg.name,
            script=cfg.script,
            description=cfg.description,
            exit_code=999,
            duration_sec=duration,
            stdout="",
            stderr=msg,
        )

    try:
        proc = subprocess.run(
            [sys.executable, script_path],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=VALIDATOR_TIMEOUT_SEC,
            check=False,
        )
        duration = time.time() - start
        return ValidatorResult(
            name=cfg.name,
            script=cfg.script,
            description=cfg.description,
            exit_code=proc.returncode,
            duration_sec=duration,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        msg = (
            f"[ci_enforcer] TIMEOUT: {cfg.script} exceeded {VALIDATOR_TIMEOUT_SEC}s; "
            f"partial stdout={e.stdout!r}, stderr={e.stderr!r}"
        )
        return ValidatorResult(
            name=cfg.name,
            script=cfg.script,
            description=cfg.description,
            exit_code=998,
            duration_sec=duration,
            stdout=e.stdout or "",
            stderr=msg,
        )


def build_pillar_index(validators: List[ValidatorConfig]) -> Dict[int, Set[str]]:
    """
    Build mapping from pillar_id -> set of validator names that cover it.
    """
    index: Dict[int, Set[str]] = {pid: set() for pid in PILLAR_LABELS.keys()}
    for cfg in validators:
        for pid in cfg.pillars:
            if pid in index:
                index[pid].add(cfg.name)
    return index


def evaluate_pillars(
    pillar_index: Dict[int, Set[str]],
    results: Dict[str, ValidatorResult],
) -> Dict[int, PillarStatus]:
    """
    Evaluate each pillar's status based on the mapped validators.
    A pillar is:
      - PASS if it has >=1 validator AND all those validators passed.
      - FAIL otherwise (including if no validators mapped).
    """
    pillar_status: Dict[int, PillarStatus] = {}

    for pid, validator_names in pillar_index.items():
        if not validator_names:
            # Coverage gap => FAIL
            pillar_status[pid] = PillarStatus(
                pillar_id=pid,
                name=PILLAR_LABELS.get(pid, f"Pillar {pid}"),
                validators=[],
                passed=False,
            )
            continue

        all_pass = True
        for vname in validator_names:
            res = results.get(vname)
            if res is None or res.exit_code != 0:
                all_pass = False
                break

        pillar_status[pid] = PillarStatus(
            pillar_id=pid,
            name=PILLAR_LABELS.get(pid, f"Pillar {pid}"),
            validators=sorted(validator_names),
            passed=all_pass,
        )

    return pillar_status


def summarize_to_stdout(
    validator_results: List[ValidatorResult],
    pillars: Dict[int, PillarStatus],
) -> None:
    """
    Human-readable CI summary.
    """
    print("=" * 80)
    print("AGENTIC-WORKFLOW — L5 CI ENFORCER")
    print("Repo Root  :", REPO_ROOT)
    print("Timestamp  :", datetime.now().isoformat())
    print("Fail Fast  :", FAIL_FAST)
    print("Timeout/Validator (s):", VALIDATOR_TIMEOUT_SEC)
    print("=" * 80)
    print()

    # Validator summaries
    print("=== VALIDATOR RESULTS ===")
    for res in validator_results:
        status = "PASS" if res.exit_code == 0 else f"FAIL ({res.exit_code})"
        print(f"- {res.name:<26} [{status}]  ({res.duration_sec:.2f}s)")
        if res.stdout.strip():
            print("  [stdout]")
            for line in res.stdout.strip().splitlines():
                print("    " + line)
        if res.stderr.strip():
            print("  [stderr]")
            for line in res.stderr.strip().splitlines():
                print("    " + line)
        print()

    # Pillar summaries
    print("=== AGENTIC L5 PILLAR STATUS ===")
    any_pillar_fail = False
    for pid in sorted(pillars.keys()):
        p = pillars[pid]
        status = "PASS" if p.passed else "FAIL"
        if not p.passed:
            any_pillar_fail = True
        print(f"P{pid:02d} {p.name:<40} [{status}]")
        if p.validators:
            print("   Validators:", ", ".join(p.validators))
        else:
            print("   Validators: NONE (coverage gap)")
    print()

    if any_pillar_fail:
        print("At least one Agentic L5 pillar is NOT satisfied.")
    else:
        print("All Agentic L5 pillars are satisfied.")
    print("=" * 80)


def write_json_report(
    validator_results: List[ValidatorResult],
    pillars: Dict[int, PillarStatus],
) -> None:
    """
    Machine-readable JSON report for external tools / Agent Ops.
    """
    ensure_report_dir()
    report = {
        "repo_root": REPO_ROOT,
        "generated_at": datetime.now().isoformat(),
        "validators": [asdict(v) for v in validator_results],
        "pillars": {pid: asdict(p) for pid, p in pillars.items()},
    }
    with open(CI_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)


# =====================================================================
# MAIN
# =====================================================================

def main() -> None:
    validator_results: List[ValidatorResult] = []
    results_by_name: Dict[str, ValidatorResult] = {}
    all_validators_passed = True

    print("=" * 80)
    print("Starting Agentic L5 CI Enforcement")
    print("=" * 80)
    print()

    for cfg in VALIDATORS:
        print(f"--- Running validator: {cfg.name} ({cfg.script}) ---")
        res = run_validator(cfg)
        validator_results.append(res)
        results_by_name[cfg.name] = res

        if res.exit_code != 0:
            all_validators_passed = False
            print(f"[ci_enforcer] {cfg.name} FAILED (exit={res.exit_code}).")
            if FAIL_FAST:
                print("[ci_enforcer] Fail-fast enabled; stopping other validators.")
                break
        else:
            print(f"[ci_enforcer] {cfg.name} PASSED.")
        print()

    pillar_index = build_pillar_index(VALIDATORS)
    pillar_status = evaluate_pillars(pillar_index, results_by_name)

    summarize_to_stdout(validator_results, pillar_status)
    write_json_report(validator_results, pillar_status)

    any_pillar_fail = any(not p.passed for p in pillar_status.values())
    if not all_validators_passed or any_pillar_fail:
        print("CI ENFORCER: VALIDATION FAILURES DETECTED.")
        sys.exit(1)

    print("CI ENFORCER: ALL VALIDATORS AND L5 PILLARS PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
