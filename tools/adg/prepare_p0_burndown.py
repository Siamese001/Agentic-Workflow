"""Generate a fresh, receipt-bound P0 execution plan for the burndown lane.

The producer handoff remains the release authority.  This command is the
consumer-side planning gate: it validates the producer pointer, re-reads the
exact immutable artifacts, and emits a new timestamped plan before edits.

The local wave engine uses the digest-bound SQLite snapshot only as an explicit
recovery fallback when the ADG MCP wave-plan call is unavailable.  The emitted
provenance makes that fallback visible instead of presenting it as MCP output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.core import p0_wave_plan  # noqa: E402
from tools.adg.run_full_adg_audit import (  # noqa: E402
    RECEIPT_SCHEMA_VERSION,
    REPAIR_HANDOFF_POINTER_SCHEMA_VERSION,
    REPAIR_HANDOFF_SCHEMA_VERSION,
    validate_repair_handoff_pointer,
)
from tools.reports.gate_signal_catalog import display_verdict  # noqa: E402

REQUIRED_ARTIFACT_KEYS = (
    "snapshot",
    "gate_results",
    "action_queue",
    "burndown_report",
    "burndown_table",
    "generation_manifest",
    "gate_manifest",
)
PLAN_SCHEMA_VERSION = "adg-p0-execution-plan/v1"
DEFAULT_LIMIT = 100
DEFAULT_FALLBACK_REASON = (
    "DEGRADED_FALLBACK: reason=adg_p0_wave_plan MCP timeout after health green; "
    "digest-bound SQLite snapshot used"
)


class P0PlanError(RuntimeError):
    """Raised when the direct handoff cannot produce a safe fresh plan."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P0PlanError(f"JSON artifact unreadable or malformed: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise P0PlanError(f"JSON artifact must be an object: {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_path(raw_path: str, *, base: Path) -> Path:
    path = Path(raw_path)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def _require_digest_ref(ref: Any, *, key: str, run_id: str) -> tuple[Path, str]:
    if not isinstance(ref, dict):
        raise P0PlanError(f"repair_handoff artifact ref missing: {key}")
    raw_path = ref.get("path")
    expected = ref.get("sha256")
    if not isinstance(raw_path, str) or not raw_path:
        raise P0PlanError(f"repair_handoff artifact path missing: {key}")
    if not isinstance(expected, str) or len(expected) != 64:
        raise P0PlanError(f"repair_handoff artifact sha256 malformed: {key}")
    path = _resolve_path(raw_path, base=REPO_ROOT)
    if not path.is_file():
        raise P0PlanError(f"repair_handoff artifact missing: {key}: {path}")
    actual = _sha256(path)
    if actual != expected:
        raise P0PlanError(f"repair_handoff artifact sha256 mismatch: {key}: {path}")
    return path, expected


def _validate_pointer_files(pointer_path: Path, *, receipt: dict[str, Any], run_id: str) -> dict[str, Any]:
    pointer = _load_json(pointer_path)
    if pointer.get("schema_version") != REPAIR_HANDOFF_POINTER_SCHEMA_VERSION:
        raise P0PlanError("handoff pointer schema_version is not adg-repair-handoff-pointer/v1")
    if pointer.get("adg_run_id") != run_id:
        raise P0PlanError("handoff pointer adg_run_id does not match validated receipt")

    handoff_path = _resolve_path(str(pointer.get("handoff_path", "")), base=pointer_path.parent)
    receipt_path = _resolve_path(str(pointer.get("receipt_path", "")), base=pointer_path.parent)
    if not handoff_path.is_file() or not receipt_path.is_file():
        raise P0PlanError("handoff pointer does not resolve to immutable handoff and receipt files")
    if _sha256(handoff_path) != pointer.get("handoff_sha256"):
        raise P0PlanError("handoff pointer handoff_sha256 mismatch")
    if _sha256(receipt_path) != pointer.get("receipt_sha256"):
        raise P0PlanError("handoff pointer receipt_sha256 mismatch")

    handoff = _load_json(handoff_path)
    disk_receipt = _load_json(receipt_path)
    if handoff.get("schema_version") != REPAIR_HANDOFF_SCHEMA_VERSION:
        raise P0PlanError("immutable handoff schema_version is not adg-repair-handoff/v1")
    if disk_receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise P0PlanError("immutable receipt schema_version is not adg-audit-pipeline-receipt/v1")
    if disk_receipt != receipt:
        raise P0PlanError("validated receipt differs from immutable receipt on disk")
    if handoff.get("repair_handoff") != receipt.get("repair_handoff"):
        raise P0PlanError("immutable handoff differs from receipt repair_handoff")
    if receipt.get("artifact_status_source") != "direct":
        raise P0PlanError("artifact_status_source must be direct")
    if receipt.get("artifact_status") not in {"certified", "repair_ready"}:
        raise P0PlanError(f"artifact_status not consumable: {receipt.get('artifact_status')!r}")

    return {
        "pointer_path": str(pointer_path.resolve()),
        "pointer_sha256": _sha256(pointer_path),
        "handoff_path": str(handoff_path),
        "handoff_sha256": str(pointer["handoff_sha256"]),
        "receipt_path": str(receipt_path),
        "receipt_sha256": str(pointer["receipt_sha256"]),
        "pointer": pointer,
        "handoff": handoff,
    }


def _open_actions(action_queue: dict[str, Any]) -> list[dict[str, Any]]:
    actions = action_queue.get("actions", [])
    if not isinstance(actions, list) or any(not isinstance(item, dict) for item in actions):
        raise P0PlanError("action_queue.actions is missing or malformed")
    return actions


def _p0_buckets(actions: list[dict[str, Any]], gate_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "P0_FIX": [
            item
            for item in actions
            if item.get("verdict_cluster") == "FIX"
            and item.get("sort_band") == "P0"
            and item.get("disposition") == "open"
        ],
        "P0_WAVE": [
            item
            for item in actions
            if item.get("verdict_cluster") in {"CANDIDATE_BLOCKER_TRIAGE", "P0_WAVE"}
            and item.get("sort_band") == "P0"
            and item.get("disposition") == "open"
        ],
        "P0_TRACKED_BACKLOG": [
            item for item in gate_rows if item.get("verdict") == "TRACK"
        ],
    }


def _p0_gate_rows(gate_results: dict[str, Any]) -> list[dict[str, Any]]:
    gates = gate_results.get("gates", [])
    if not isinstance(gates, list) or any(not isinstance(item, dict) for item in gates):
        raise P0PlanError("gate_results.gates is missing or malformed")
    return [
        {
            "gate_id": item.get("gate_id"),
            "band": item.get("band"),
            "enforcement": item.get("enforcement"),
            "status": item.get("status"),
            "classification": item.get("classification"),
            "violation_count": item.get("violation_count"),
            "baseline_count": item.get("baseline_count"),
            "exit_code": item.get("exit_code"),
            "verdict": display_verdict(item),
        }
        for item in gates
        if item.get("band") == "P0"
    ]


def _bounded_waves(buckets: dict[str, list[dict[str, Any]]], gate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "wave_id": "p0_wave_0_receipt_lock",
            "goal": "Validate the direct pointer and bind all edits to the exact immutable artifacts.",
            "items": [],
            "exit_criteria": "The generated plan and all source artifact digests remain unchanged before edits.",
        },
        {
            "wave_id": "p0_wave_1_fix_gates",
            "goal": "Resolve every released P0 FIX item before touching candidate wave work.",
            "items": buckets["P0_FIX"],
            "exit_criteria": "All P0 FIX items are tested and the corresponding gates are no longer failing.",
        },
        {
            "wave_id": "p0_wave_2_released_wave",
            "goal": "Process the released P0 WAVE candidates in rank order, one bounded batch at a time.",
            "items": buckets["P0_WAVE"],
            "exit_criteria": "No released P0 WAVE item remains actionable, or a concrete blocker stops the lane.",
        },
        {
            "wave_id": "p0_wave_3_replay_and_gate",
            "goal": "Replay targeted tests and the G_REACH gate against a fresh post-fix artifact set.",
            "items": gate_rows,
            "exit_criteria": "A fresh direct receipt proves P0_FIX=0 and P0_WAVE=0 before merge.",
        },
    ]


def _markdown(plan: dict[str, Any]) -> str:
    counts = plan["p0_counts"]
    lines = [
        "# P0 Burndown Execution Plan",
        "",
        f"- ADG run: `{plan['adg_run_id']}`",
        f"- Generated: `{plan['generated_at_utc']}`",
        f"- Artifact status: `{plan['artifact_status']}` (`{plan['artifact_status_source']}`)",
        f"- P0 FIX / WAVE / TRACKED BACKLOG: **{counts['P0_FIX']} / {counts['P0_WAVE']} / {counts['P0_TRACKED_BACKLOG']}**",
        "",
        "## Provenance",
        "",
        f"- Backend: `{plan['provenance']['backend']}`",
        f"- {plan['provenance']['fallback_reason']}",
        f"- Snapshot: `{plan['artifacts']['snapshot']['path']}` (`{plan['artifacts']['snapshot']['sha256']}`)",
        "",
        "## Bounded Waves",
        "",
    ]
    for wave in plan["bounded_waves"]:
        lines.extend(
            [
                f"### {wave['wave_id']}",
                "",
                f"{wave['goal']}",
                "",
                f"- Items: **{len(wave['items'])}**",
                f"- Exit criteria: {wave['exit_criteria']}",
                "",
            ]
        )
    lines.extend(["## Stop Conditions", "", *[f"- {item}" for item in plan["stop_conditions"]], ""])
    return "\n".join(lines)


def create_p0_execution_plan(
    handoff_pointer: Path,
    *,
    output_dir: Path,
    limit: int = DEFAULT_LIMIT,
    fallback_reason: str = DEFAULT_FALLBACK_REASON,
) -> tuple[Path, Path, dict[str, Any]]:
    """Validate the direct handoff and emit a new immutable execution plan."""
    pointer_path = handoff_pointer.resolve()
    receipt, _counts, errors = validate_repair_handoff_pointer(pointer_path)
    if errors or receipt is None:
        detail = "; ".join(errors) if errors else "validator returned no receipt"
        raise P0PlanError(f"direct handoff validation failed: {detail}")

    run_id = receipt.get("adg_run_id")
    if not isinstance(run_id, str) or not run_id:
        raise P0PlanError("validated receipt has no adg_run_id")
    pointer_files = _validate_pointer_files(pointer_path, receipt=receipt, run_id=run_id)
    handoff = receipt.get("repair_handoff")
    if not isinstance(handoff, dict):
        raise P0PlanError("validated receipt has no repair_handoff")
    refs = handoff.get("artifacts")
    if not isinstance(refs, dict):
        raise P0PlanError("validated repair_handoff has no artifacts")

    artifact_paths: dict[str, Path] = {}
    artifact_refs: dict[str, dict[str, str]] = {}
    for key in REQUIRED_ARTIFACT_KEYS:
        path, digest = _require_digest_ref(refs.get(key), key=key, run_id=run_id)
        artifact_paths[key] = path
        artifact_refs[key] = {"path": str(path), "sha256": digest}

    action_queue = _load_json(artifact_paths["action_queue"])
    gate_results = _load_json(artifact_paths["gate_results"])
    gate_rows = _p0_gate_rows(gate_results)
    buckets = _p0_buckets(_open_actions(action_queue), gate_rows)
    legacy_counts = handoff.get("legacy_counts") or {}
    p0_counts = {key: len(value) for key, value in buckets.items()}
    reported_counts = {
        key: int(legacy_counts.get(key, p0_counts[key]) or 0)
        for key in p0_counts
    }
    count_consistency = {
        key: {"reported": reported_counts[key], "recomputed": p0_counts[key], "matches": reported_counts[key] == p0_counts[key]}
        for key in p0_counts
    }
    if not all(item["matches"] for item in count_consistency.values()):
        raise P0PlanError(f"P0 count mismatch between handoff and action queue: {count_consistency}")

    wave_engine = p0_wave_plan.build_p0_remediation_wave_plan(artifact_paths["snapshot"], limit=limit)
    generated_at = datetime.now(timezone.utc)
    generated_at_utc = generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = generated_at.strftime("%Y%m%d_%H%M%S")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"p0_burndown_execution_plan_{run_id}_{stamp}.json"
    markdown_path = output_dir / f"p0_burndown_execution_plan_{run_id}_{stamp}.md"

    plan = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc,
        "adg_run_id": run_id,
        "artifact_status": receipt.get("artifact_status"),
        "artifact_status_source": receipt.get("artifact_status_source"),
        "handoff": {
            "pointer": {
                "path": pointer_files["pointer_path"],
                "sha256": pointer_files["pointer_sha256"],
            },
            "immutable_handoff": {
                "path": pointer_files["handoff_path"],
                "sha256": pointer_files["handoff_sha256"],
            },
            "receipt": {
                "path": pointer_files["receipt_path"],
                "sha256": pointer_files["receipt_sha256"],
            },
        },
        "artifacts": artifact_refs,
        "p0_counts": p0_counts,
        "reported_p0_counts": reported_counts,
        "count_consistency": count_consistency,
        "p0_fix_items": buckets["P0_FIX"],
        "p0_wave_items": buckets["P0_WAVE"],
        "p0_tracked_backlog_items": buckets["P0_TRACKED_BACKLOG"],
        "p0_gate_rows": gate_rows,
        "bounded_waves": _bounded_waves(buckets, gate_rows),
        "wave_engine": {
            "schema_version": wave_engine.get("schema_version"),
            "generated_via": wave_engine.get("generated_via"),
            "plan_required": wave_engine.get("plan_required"),
            "summary": wave_engine.get("summary", {}),
            "top_files": wave_engine.get("top_files", []),
            "waves": wave_engine.get("waves", []),
        },
        "provenance": {
            "backend": "degraded_sqlite",
            "snapshot": artifact_paths["snapshot"].name,
            "fallback_reason": fallback_reason,
        },
        "validation_commands": [
            "python tools/adg/consume_adg_repair_handoff.py --handoff-pointer "
            + str(pointer_path)
            + " --json",
            "python -m pytest tests/unit/tools_adg/test_p0_wave_plan.py -q",
            f"$env:ADG_SNAPSHOT='{artifact_paths['snapshot']}'; python ops_scripts/ci/check_graph_reach.py",
        ],
        "rollback_criteria": [
            "Revert the current bounded wave if its targeted tests fail or the gate count increases.",
            "Do not continue to the next wave after a failed validation or changed artifact digest.",
        ],
        "skip_criteria": [
            "Skip only a candidate with a documented ownership or design blocker while an independent P0 item remains safe.",
            "Never skip a P0 FIX item or silently convert it to tracked backlog.",
        ],
        "stop_conditions": [
            "Any required artifact is missing, stale, timestamp-inconsistent, or digest-invalid.",
            "A fresh post-fix direct receipt cannot prove P0_FIX=0 and P0_WAVE=0.",
            "A source edit requires a broad refactor, public contract change, or unresolved ownership decision.",
        ],
    }
    json_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(plan), encoding="utf-8")
    return json_path, markdown_path, plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff-pointer", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--fallback-reason", default=DEFAULT_FALLBACK_REASON)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        json_path, markdown_path, plan = create_p0_execution_plan(
            args.handoff_pointer,
            output_dir=args.output_dir,
            limit=args.limit,
            fallback_reason=args.fallback_reason,
        )
    except P0PlanError as exc:
        payload = {"ok": False, "error": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"error={exc}", file=sys.stderr)
        return 1
    payload = {
        "ok": True,
        "plan_json": str(json_path),
        "plan_markdown": str(markdown_path),
        "adg_run_id": plan["adg_run_id"],
        "p0_counts": plan["p0_counts"],
        "artifact_status": plan["artifact_status"],
        "artifact_status_source": plan["artifact_status_source"],
        "provenance": plan["provenance"],
    }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "\n".join(f"{k}={v}" for k, v in payload.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
