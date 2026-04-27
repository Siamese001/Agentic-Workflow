"""Wave 1 gate demo — proves the new `reason_match` cross-check would have
caught BUG #1 (audit pass 1) before it shipped.

BUG #1 recap
============
Pre-fix, ``validate_artifact_inventory`` derived ``packet_path`` from
``packet.app_id`` / ``packet.scenario_id`` — fields that are *post-disk*
and therefore *attacker-influenced*. T2 (mutate ``app_id`` without
rehashing) "caught" the tamper only because the derived path didn't
exist on disk, NOT because the hash check fired. A move-and-tamper
attack would have slipped past undetected.

The fix made callers pass an explicit trusted ``packet_path`` derived
from the registered ``scenario_id`` (not the loaded packet object).

This demo
=========
``validate_artifact_inventory`` still preserves the legacy/buggy
derivation as the documented degraded fallback when ``packet_path=None``
(see ``validators.py`` lines 422-434, ``fail_path_source="trusted_path_unset"``).

So we can exercise BOTH code paths against the SAME T2-tampered tree and
show the difference in ``reason_match`` / ``fully_caught`` — no source
revert needed.

Run::

    python docs/reports/proof/wave1_gate_demo.py

Output: this file is self-contained; it writes the captured evidence to
``docs/reports/proof/wave1_gate_demo_output.md`` (overwriting any prior).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from apps_shared.proof.negative_controls import (  # noqa: E402
    _packet_from_disk,
    _t2_packet_field_mutation,
)
from apps_shared.proof.validators import validate_artifact_inventory  # noqa: E402


T2_EXPECTED_REASON = "hash mismatch"
APP_ID = "apps_underwriting_ai"
SCENARIO_ID = "uw_recommendation_only_v1"
PRIMARY_ROOT = REPO_ROOT / "artifacts" / "runtime" / "apps_proof" / "latest"
DEMO_ROOT = REPO_ROOT / "artifacts" / "runtime" / "apps_proof" / "wave1_gate_demo"
OUTPUT_MD = REPO_ROOT / "docs" / "reports" / "proof" / "wave1_gate_demo_output.md"


def _stage_tamper_tree(primary: Path, demo: Path) -> None:
    """Stage a fresh copy of the relevant subset of the primary export."""
    if demo.exists():
        shutil.rmtree(demo, ignore_errors=True)
    demo.mkdir(parents=True, exist_ok=True)
    for sub in (
        f"contracts/{APP_ID}",
        f"sandbox/{APP_ID}",
        f"uwg_pending/{APP_ID}",
    ):
        src = primary / sub
        if src.exists():
            shutil.copytree(src, demo / sub)
    # traces/gates/artifacts indexes for THIS app only
    for d in ("traces", "gates", "artifacts"):
        sd = primary / d
        dd = demo / d
        dd.mkdir(parents=True, exist_ok=True)
        if sd.exists():
            for fp in sd.glob(f"{APP_ID}_*.json"):
                shutil.copy2(fp, dd / fp.name)


def _run_validator(demo_root: Path, *, with_trusted_path: bool) -> dict:
    """Run validate_artifact_inventory once. with_trusted_path=False
    simulates BUG #1 (pre-fix path derivation from packet fields)."""
    trusted = demo_root / "contracts" / APP_ID / SCENARIO_ID / "evidence_packet.json"
    packet = _packet_from_disk(trusted)
    verdict = validate_artifact_inventory(
        packet=packet,
        export_root=demo_root,
        packet_path=trusted if with_trusted_path else None,
    )
    reasons = list(verdict.fail_reasons)
    reason_match = any(T2_EXPECTED_REASON in r for r in reasons)
    return {
        "scenario": "fixed (trusted packet_path)"
        if with_trusted_path
        else "BUG #1 reverted (packet_path=None → derived from tampered packet.app_id)",
        "validator_ok": verdict.ok,
        "caught": not verdict.ok,
        "expected_fail_reason_substring": T2_EXPECTED_REASON,
        "reason_match": reason_match,
        "fully_caught": (not verdict.ok) and reason_match,
        "fail_reasons": reasons,
        "packet_app_id_after_tamper": packet.app_id,
        "packet_hash_msg": verdict.details.get("packet_hash_msg"),
    }


def _render_md(buggy: dict, fixed: dict) -> str:
    def yn(b: bool) -> str:
        return "✅" if b else "❌"

    def _reason_lines(reasons: list[str]) -> list[str]:
        if not reasons:
            return ["(no fail_reasons)"]
        return [f"- {r}" for r in reasons]

    md = [
        "# Wave 1 Gate Demo — BUG #1 prevention proof",
        "",
        "## What this demonstrates",
        "",
        "Same T2-tampered tree (mutate `app_id` to `TAMPERED_APP_ID` without",
        "rehashing). Validator called twice:",
        "",
        "1. **BUG #1 reverted** — `packet_path=None`, so the validator falls",
        "   back to deriving the packet path from `packet.app_id` / "
        "`packet.scenario_id` (the legacy/pre-fix behavior).",
        "2. **Fixed** — caller passes the trusted `packet_path` derived from",
        "   the registered scenario, not from the loaded packet.",
        "",
        "## Result table",
        "",
        "| Field | BUG #1 reverted | Fixed |",
        "|---|---|---|",
        f"| Scenario | `packet_path=None` | trusted `packet_path` |",
        f"| `validator.ok` | {buggy['validator_ok']} | {fixed['validator_ok']} |",
        f"| `caught` (verdict) | {yn(buggy['caught'])} `{buggy['caught']}` | {yn(fixed['caught'])} `{fixed['caught']}` |",
        f"| `reason_match` (mechanism) | {yn(buggy['reason_match'])} `{buggy['reason_match']}` | {yn(fixed['reason_match'])} `{fixed['reason_match']}` |",
        f"| **`fully_caught`** | {yn(buggy['fully_caught'])} **`{buggy['fully_caught']}`** | {yn(fixed['fully_caught'])} **`{fixed['fully_caught']}`** |",
        f"| `packet.app_id` (post-tamper) | `{buggy['packet_app_id_after_tamper']}` | `{fixed['packet_app_id_after_tamper']}` |",
        f"| Expected fail-reason substring | `{T2_EXPECTED_REASON}` | `{T2_EXPECTED_REASON}` |",
        "",
        "## Fail-reason traces",
        "",
        "### BUG #1 reverted",
        "",
        "```",
        *_reason_lines(buggy["fail_reasons"]),
        "```",
        "",
        "### Fixed",
        "",
        "```",
        *_reason_lines(fixed["fail_reasons"]),
        "```",
        "",
        "## Interpretation",
        "",
        "Pre-fix audit-pass-1 wave: T2 reported `caught=True` and the harness",
        "marked it green. The new `reason_match` cross-check shows the catch",
        "was via `missing` / wrong-mechanism — `fully_caught=False`. The",
        "harness now gates on `all_fully_caught`, which would have flipped",
        "the build RED the moment BUG #1 was introduced.",
        "",
        "Same revert-and-prove pattern works for BUGs #2, #3, #6, #7, #9,",
        "#10, #11, #12, #13 against the property tests + reason-match check.",
        "",
        "## Reproduce",
        "",
        "```",
        "python docs/reports/proof/wave1_gate_demo.py",
        "```",
        "",
        "Inputs read from `artifacts/runtime/apps_proof/latest/` (last full",
        "harness run). Tamper tree staged at",
        "`artifacts/runtime/apps_proof/wave1_gate_demo/`.",
        "",
    ]
    return "\n".join(md) + "\n"


def main() -> int:
    if not (PRIMARY_ROOT / "contracts" / APP_ID / SCENARIO_ID / "evidence_packet.json").exists():
        print(
            f"ERROR: primary export missing at {PRIMARY_ROOT}.\n"
            f"Run `python -m apps_shared.proof.proof_runner` first.",
            file=sys.stderr,
        )
        return 2

    print(f"[1/4] Staging tamper tree at {DEMO_ROOT.relative_to(REPO_ROOT)}")
    _stage_tamper_tree(PRIMARY_ROOT, DEMO_ROOT)

    print("[2/4] Applying T2 mutation (app_id → TAMPERED_APP_ID, no rehash)")
    _t2_packet_field_mutation(DEMO_ROOT, APP_ID, SCENARIO_ID)

    print("[3/4] Running validator twice (BUG-reverted vs fixed)")
    buggy = _run_validator(DEMO_ROOT, with_trusted_path=False)
    fixed = _run_validator(DEMO_ROOT, with_trusted_path=True)

    print("[4/4] Writing evidence")
    OUTPUT_MD.write_text(_render_md(buggy, fixed), encoding="utf-8")
    json_out = OUTPUT_MD.with_suffix(".json")
    json_out.write_text(
        json.dumps({"bug_reverted": buggy, "fixed": fixed}, indent=2, default=str),
        encoding="utf-8",
    )

    # Console summary
    print()
    print(f"BUG #1 reverted → fully_caught={buggy['fully_caught']} reason_match={buggy['reason_match']}")
    print(f"Fixed           → fully_caught={fixed['fully_caught']} reason_match={fixed['reason_match']}")
    print(f"Evidence: {OUTPUT_MD.relative_to(REPO_ROOT)}")
    print(f"          {json_out.relative_to(REPO_ROOT)}")

    # Demo passes when the cross-check correctly distinguishes the two paths.
    expected = (not buggy["fully_caught"]) and fixed["fully_caught"]
    if not expected:
        print("\nERROR: demo did NOT distinguish reverted vs fixed.", file=sys.stderr)
        return 1
    print("\nDEMO PROVES: new `fully_caught` gate would have flipped RED on BUG #1 introduction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
