"""Deterministic cross-section SRFS structural audit aggregator (apps_rg-local)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES

PROOF_LEVEL = "SECTION_SRFS_STRUCTURAL_AUDIT_ONLY"
AUDIT_REPORT_SCHEMA = "apps_rg.srfs_audit_report.v1"
RECEIPT_MANIFEST_SCHEMA = "apps_rg.srfs_receipt_manifest.v1"
CANONICAL_RECEIPT_SCHEMA = "apps_rg.canonical_section_metric_receipt.v1"

W6_REQUIRED_FIELDS = (
    "proof_pool_type",
    "selected_role_fact_set_used",
    "srfs_section_id",
    "candidate_fact_pool_count",
    "allowed_fact_ids_count",
    "required_fact_ids_count",
    "claim_ledger_union_matches_required_fact_ids",
    "out_of_slice_fact_ids",
    "fallback_used",
    "fallback_reason",
    "x2_srfs_gate_status",
    "srfs_allowed_fact_ids_count",
    "full_resume_srfs_supported",
)

ENVELOPE_CORE_KEYS = frozenset(
    {
        "run_id",
        "lane_id",
        "prompt_id",
        "prompt_hash",
        "input_payload_hash",
        "output_payload_hash",
        "claim_ledger_hash",
        "runtime_generation_status",
        "product_quality_status",
        "x2_failed_gates",
        "x3_code",
        "proof_eligible",
        "judge_proof_eligible",
        "status",
        "srfs_section_id",
        *W6_REQUIRED_FIELDS,
    }
)

DEFAULT_EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "proof_level is SECTION_SRFS_STRUCTURAL_AUDIT_ONLY only.",
    "This report does not assert runtime certification.",
    "This report does not assert live Qwen or vLLM output quality.",
    "This report does not assert real-judge X3 ALLOW or product release.",
    "This report does not assert full résumé R4 SRFS or modular_resume_generation wiring.",
    "Section x3_code and product_quality_status are informational only, not aggregate PASS criteria.",
    "Advisory LLM judge output does not override deterministic status.",
)

FORBIDDEN_AFFIRMATIVE_PHRASES = (
    "release proof",
    "product allow",
    "certified",
    "runtime certified",
    "full resume srfs",
)


class AggregatorOperationalError(Exception):
    """CLI / IO failure (nonzero exit)."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_srfs_active(raw: dict[str, Any]) -> bool:
    if raw.get("selected_role_fact_set_used") is True:
        return True
    return str(raw.get("proof_pool_type") or "") == "selected_role_fact_set"


def _resolve_section_id(raw: dict[str, Any]) -> str | None:
    srfs_id = raw.get("srfs_section_id")
    lane_id = raw.get("lane_id")
    if srfs_id is not None and lane_id is not None:
        s, l = str(srfs_id).strip(), str(lane_id).strip()
        if s and l and s != l:
            return None
        return s or l or None
    if srfs_id is not None and str(srfs_id).strip():
        return str(srfs_id).strip()
    if lane_id is not None and str(lane_id).strip():
        return str(lane_id).strip()
    return None


def normalize_section_receipt(
    raw: dict[str, Any] | Any,
    *,
    receipt_path: str | Path,
) -> dict[str, Any]:
    """Normalize one ``section_metric_receipt.json`` to canonical row."""
    path_str = str(receipt_path)
    if not isinstance(raw, dict):
        return {
            "schema_version": CANONICAL_RECEIPT_SCHEMA,
            "section_id": "",
            "receipt_path": path_str,
            "receipt_completeness": "malformed",
            "srfs_active": False,
            "extensions": {},
            "had_extra_top_level_keys": False,
        }

    if str(raw.get("status") or "").lower() == "pending":
        ph = str(raw.get("prompt_hash") or "")
        return {
            "schema_version": CANONICAL_RECEIPT_SCHEMA,
            "section_id": _resolve_section_id(raw) or "",
            "receipt_path": path_str,
            "receipt_completeness": "pending",
            "prompt_hash": ph,
            "srfs_active": _is_srfs_active(raw),
            "prompt_reflection_status": "UNKNOWN",
            "extensions": {k: v for k, v in raw.items() if k not in {"status", "prompt_hash"}},
            "had_extra_top_level_keys": len(raw) > 2,
        }

    section_id = _resolve_section_id(raw)
    if not section_id:
        return {
            "schema_version": CANONICAL_RECEIPT_SCHEMA,
            "section_id": "",
            "receipt_path": path_str,
            "receipt_completeness": "malformed",
            "srfs_active": False,
            "extensions": dict(raw),
            "had_extra_top_level_keys": False,
        }

    srfs_active = _is_srfs_active(raw)
    x2_status = str(raw.get("x2_srfs_gate_status") or "NOT_APPLICABLE")
    if not srfs_active:
        srfs_structural = "NOT_APPLICABLE"
    elif x2_status == "UNKNOWN":
        srfs_structural = "UNKNOWN"
    else:
        srfs_structural = x2_status

    prompt_hash = str(raw.get("prompt_hash") or "")
    if srfs_active and prompt_hash.strip():
        prompt_reflection = "PASS"
    elif srfs_active:
        prompt_reflection = "FAIL"
    else:
        prompt_reflection = "NOT_APPLICABLE"

    extensions: dict[str, Any] = {}
    had_extra = False
    for k, v in raw.items():
        if k not in ENVELOPE_CORE_KEYS:
            extensions[k] = v
            had_extra = True

    row: dict[str, Any] = {
        "schema_version": CANONICAL_RECEIPT_SCHEMA,
        "section_id": section_id,
        "receipt_path": path_str,
        "receipt_completeness": "complete",
        "run_id": raw.get("run_id"),
        "prompt_hash": prompt_hash,
        "srfs_active": srfs_active,
        "proof_pool_type": str(raw.get("proof_pool_type") or ""),
        "selected_role_fact_set_used": bool(raw.get("selected_role_fact_set_used")),
        "x2_srfs_gate_status": x2_status,
        "srfs_structural_status": srfs_structural,
        "prompt_reflection_status": prompt_reflection,
        "full_resume_srfs_supported": bool(raw.get("full_resume_srfs_supported")),
        "required_fact_ids_count": int(raw.get("required_fact_ids_count") or 0),
        "allowed_fact_ids_count": int(raw.get("allowed_fact_ids_count") or 0),
        "candidate_fact_pool_count": int(raw.get("candidate_fact_pool_count") or 0),
        "claim_ledger_union_matches_required_fact_ids": bool(
            raw.get("claim_ledger_union_matches_required_fact_ids", False)
        ),
        "out_of_slice_fact_ids": list(raw.get("out_of_slice_fact_ids") or []),
        "fallback_used": bool(raw.get("fallback_used")),
        "fallback_reason": str(raw.get("fallback_reason") or ""),
        "x3_code": raw.get("x3_code"),
        "product_quality_status": raw.get("product_quality_status"),
        "x2_failed_gates": list(raw.get("x2_failed_gates") or []),
        "extensions": extensions,
        "had_extra_top_level_keys": had_extra,
    }
    return row


def _load_receipt_file(path: Path) -> dict[str, Any]:
    if path.name != "section_metric_receipt.json":
        raise AggregatorOperationalError(
            f"Refusing non-receipt file (expected section_metric_receipt.json): {path}"
        )
    try:
        data = _read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise AggregatorOperationalError(f"Cannot read receipt {path}: {exc}") from exc
    if not isinstance(data, dict):
        return {"__malformed_json_type__": True}
    return data


def load_section_receipts(
    *,
    receipt_manifest_path: str | Path | None = None,
    receipt_root: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> dict[str, tuple[Path, dict[str, Any]]]:
    """
    Load receipts from manifest (preferred) or recursive root discovery.

    Returns mapping section_id -> (path, raw_dict).
    Raises AggregatorOperationalError on IO/arg errors.
    """
    if receipt_manifest_path is not None and receipt_root is not None:
        raise AggregatorOperationalError("Use only one of receipt_manifest_path or receipt_root")
    if receipt_manifest_path is None and receipt_root is None:
        raise AggregatorOperationalError("receipt_manifest_path or receipt_root is required")

    base = Path(repo_root) if repo_root is not None else Path.cwd()
    loaded: dict[str, tuple[Path, dict[str, Any]]] = {}

    if receipt_manifest_path is not None:
        manifest_path = Path(receipt_manifest_path)
        if not manifest_path.is_file():
            raise AggregatorOperationalError(f"Receipt manifest not found: {manifest_path}")
        try:
            manifest = _read_json(manifest_path)
        except (OSError, json.JSONDecodeError) as exc:
            raise AggregatorOperationalError(f"Invalid receipt manifest: {exc}") from exc
        if not isinstance(manifest, dict):
            raise AggregatorOperationalError("Receipt manifest must be a JSON object")
        receipts = manifest.get("receipts")
        if not isinstance(receipts, dict):
            raise AggregatorOperationalError("Receipt manifest missing 'receipts' object")
        for section_key, rel_path in receipts.items():
            manifest_key = str(section_key)
            p = Path(rel_path)
            if not p.is_absolute():
                p = (base / p).resolve()
            raw = _load_receipt_file(p)
            norm = normalize_section_receipt(raw, receipt_path=p)
            sid = str(norm.get("section_id") or "")
            if norm.get("receipt_completeness") == "complete" and sid != manifest_key:
                raise AggregatorOperationalError(
                    f"Manifest key {manifest_key!r} does not match receipt section_id {sid!r}"
                )
            if not sid:
                sid = manifest_key
            if sid in loaded:
                raise AggregatorOperationalError(f"Duplicate section_id: {sid}")
            loaded[sid] = (p, raw)
        return loaded

    root = Path(receipt_root).resolve()
    if not root.is_dir():
        raise AggregatorOperationalError(f"Receipt root not a directory: {root}")

    for path in sorted(root.rglob("section_metric_receipt.json")):
        raw = _load_receipt_file(path)
        norm = normalize_section_receipt(raw, receipt_path=path)
        sid = str(norm.get("section_id") or "")
        if not sid:
            raise AggregatorOperationalError(f"Cannot resolve section_id for receipt: {path}")
        if sid in loaded:
            raise AggregatorOperationalError(f"Duplicate section_id from discovery: {sid}")
        loaded[sid] = (path, raw)
    return loaded


def validate_section_inventory(
    loaded: dict[str, tuple[Path, dict[str, Any]]],
    *,
    expected_sections: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    """Return inventory summary: observed, missing, unexpected, duplicate section ids."""
    expected = tuple(expected_sections or GENERATED_LANES)
    expected_set = set(expected)
    observed = sorted(loaded.keys())
    missing = sorted(expected_set - set(observed))
    unexpected = sorted(set(observed) - expected_set)
    duplicates: list[str] = []
  # duplicates caught at load; keep empty unless pre-merged caller passes dup list
    return {
        "expected_sections": list(expected),
        "observed_sections": observed,
        "missing_sections": missing,
        "unexpected_sections": unexpected,
        "duplicate_sections": duplicates,
    }


def _pass_guard_violations(
    norm: dict[str, Any],
    *,
    srfs_required: bool,
    missing_w6: list[str] | None = None,
) -> list[str]:
    violations: list[str] = []
    completeness = norm.get("receipt_completeness")
    if completeness == "pending":
        violations.append("G-pending")
    if completeness == "malformed":
        violations.append("G-malformed")
    if missing_w6:
        violations.append(f"G-missing-srfs-fields:{','.join(missing_w6)}")
    if completeness == "complete" and srfs_required and not norm.get("srfs_active"):
        violations.append("G-srfs-required")
    if norm.get("srfs_active"):
        if norm.get("x2_srfs_gate_status") == "UNKNOWN":
            violations.append("G-unknown-srfs")
        if norm.get("srfs_structural_status") == "UNKNOWN":
            violations.append("G-unknown-structural")
        if norm.get("prompt_reflection_status") == "FAIL":
            violations.append("G-prompt")
    if norm.get("full_resume_srfs_supported") is True:
        violations.append("G-full-resume")
    return violations


def _check_complete_srfs_fields(raw: dict[str, Any], norm: dict[str, Any]) -> list[str]:
    """Missing W6 keys on complete SRFS-active receipt."""
    missing: list[str] = []
    if norm.get("receipt_completeness") != "complete" or not norm.get("srfs_active"):
        return missing
    if not isinstance(raw, dict):
        return list(W6_REQUIRED_FIELDS)
    for field in W6_REQUIRED_FIELDS:
        if field not in raw:
            missing.append(field)
    return missing


def build_srfs_audit_report(
    loaded: dict[str, tuple[Path, dict[str, Any]]],
    *,
    source_manifest_ref: str | None = None,
    receipt_manifest_ref: str | None = None,
    receipt_root: str | None = None,
    run_id: str | None = None,
    expected_sections: tuple[str, ...] | list[str] | None = None,
    srfs_required: bool = True,
) -> dict[str, Any]:
    """Build deterministic audit report dict."""
    inventory = validate_section_inventory(loaded, expected_sections=expected_sections)
    expected = inventory["expected_sections"]
    normalized: dict[str, dict[str, Any]] = {}
    deterministic_findings: list[str] = []
    any_extra_keys = False
    any_x2_fail = False
    sections_srfs_active = 0

    for section_id, (path, raw) in loaded.items():
        if isinstance(raw, dict) and raw.get("__malformed_json_type__"):
            norm = normalize_section_receipt({}, receipt_path=path)
            norm["section_id"] = section_id
        else:
            norm = normalize_section_receipt(raw, receipt_path=path)
            if not norm.get("section_id"):
                norm["section_id"] = section_id
        missing_w6 = _check_complete_srfs_fields(raw if isinstance(raw, dict) else {}, norm)
        violations = _pass_guard_violations(norm, srfs_required=srfs_required, missing_w6=missing_w6)
        if missing_w6:
            norm["receipt_completeness"] = "malformed"
        if norm.get("had_extra_top_level_keys"):
            any_extra_keys = True
        if norm.get("srfs_active"):
            sections_srfs_active += 1
        if norm.get("x2_srfs_gate_status") == "FAIL":
            any_x2_fail = True
        normalized[section_id] = norm
        if violations:
            deterministic_findings.extend(f"{section_id}:{v}" for v in violations)

    section_results: dict[str, Any] = {}
    for sid, norm in normalized.items():
        raw_dict = loaded[sid][1] if sid in loaded and isinstance(loaded[sid][1], dict) else {}
        missing_w6 = _check_complete_srfs_fields(raw_dict, norm)
        violations = _pass_guard_violations(norm, srfs_required=srfs_required, missing_w6=missing_w6)
        section_results[sid] = {
            "receipt_path": norm.get("receipt_path"),
            "receipt_completeness": norm.get("receipt_completeness"),
            "srfs_active": norm.get("srfs_active"),
            "srfs_structural_status": norm.get("srfs_structural_status"),
            "x2_srfs_gate_status": norm.get("x2_srfs_gate_status"),
            "prompt_reflection_status": norm.get("prompt_reflection_status"),
            "selected_role_fact_set_used": norm.get("selected_role_fact_set_used"),
            "full_resume_srfs_supported": norm.get("full_resume_srfs_supported"),
            "x3_code": norm.get("x3_code"),
            "pass_guard_violations": violations,
        }

    cross_section = {
        "all_expected_sections_present": not inventory["missing_sections"],
        "any_pending_receipt": any(
            normalized.get(s, {}).get("receipt_completeness") == "pending" for s in normalized
        ),
        "any_malformed_receipt": any(
            normalized.get(s, {}).get("receipt_completeness") == "malformed" for s in normalized
        ),
        "any_unknown_srfs_status": any(
            normalized.get(s, {}).get("srfs_active") and normalized[s].get("x2_srfs_gate_status") == "UNKNOWN"
            for s in normalized
        ),
        "any_full_resume_srfs_true": any(
            normalized.get(s, {}).get("full_resume_srfs_supported") is True for s in normalized
        ),
        "any_section_x2_srfs_fail": any_x2_fail,
        "sections_srfs_active_count": sections_srfs_active,
    }

    explicit_non_claims = list(DEFAULT_EXPLICIT_NON_CLAIMS)
    fail_reasons: list[str] = []

    if inventory["missing_sections"]:
        fail_reasons.append("missing_sections")
    if inventory["unexpected_sections"] and srfs_required:
        pass  # unexpected alone is WARN not FAIL
    if inventory["duplicate_sections"]:
        fail_reasons.append("duplicate_sections")
    if cross_section["any_pending_receipt"]:
        fail_reasons.append("pending_receipt")
    if cross_section["any_malformed_receipt"]:
        fail_reasons.append("malformed_receipt")
    if cross_section["any_unknown_srfs_status"]:
        fail_reasons.append("unknown_srfs_status")
    if cross_section["any_full_resume_srfs_true"]:
        fail_reasons.append("full_resume_srfs_supported_true")
    if any(section_results[s].get("pass_guard_violations") for s in section_results):
        fail_reasons.append("pass_guard_violation")
    if not explicit_non_claims:
        fail_reasons.append("empty_explicit_non_claims")

    warn_reasons: list[str] = []
    if inventory["unexpected_sections"]:
        warn_reasons.append("unexpected_sections")
    if any_extra_keys:
        warn_reasons.append("extra_top_level_keys_normalized")

    if fail_reasons:
        status = "FAIL"
        decisive = "Aggregate FAIL: " + ", ".join(fail_reasons)
    elif warn_reasons:
        status = "WARN"
        decisive = "Aggregate WARN: " + ", ".join(warn_reasons)
    else:
        status = "PASS"
        decisive = (
            "All expected sections present with structurally complete SRFS receipts; "
            "PASS guard satisfied at SECTION_SRFS_STRUCTURAL_AUDIT_ONLY."
        )

    report = {
        "schema_version": AUDIT_REPORT_SCHEMA,
        "status": status,
        "proof_level": PROOF_LEVEL,
        "run_id": run_id or f"aggregator_run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "created_at_utc": _utc_now_iso(),
        "source_manifest_ref": source_manifest_ref,
        "receipt_manifest_ref": receipt_manifest_ref,
        "receipt_root": receipt_root,
        "expected_sections": expected,
        "observed_sections": inventory["observed_sections"],
        "missing_sections": inventory["missing_sections"],
        "unexpected_sections": inventory["unexpected_sections"],
        "duplicate_sections": inventory["duplicate_sections"],
        "section_results": section_results,
        "cross_section_findings": cross_section,
        "deterministic_findings": deterministic_findings,
        "advisory_judge_review": {
            "enabled": False,
            "status": "NOT_RUN",
            "mocked_or_live": "not_run",
            "can_change_deterministic_status": False,
            "findings": [],
            "limitations": ["Advisory review disabled (default)."],
            "scope": "apps_rg_local_heuristic_audit_review_v1",
        },
        "explicit_non_claims": explicit_non_claims,
        "decisive_reason": decisive,
    }
    return report


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# apps_rg SRFS structural audit report",
        "",
        f"- **status:** {report.get('status')}",
        f"- **proof_level:** {report.get('proof_level')}",
        f"- **run_id:** {report.get('run_id')}",
        f"- **created_at_utc:** {report.get('created_at_utc')}",
        "",
        "## Section matrix",
        "",
        "| section | completeness | srfs_active | x2_srfs | prompt_refl | pass_guard |",
        "|---------|--------------|-------------|---------|-------------|------------|",
    ]
    for sid in report.get("expected_sections") or []:
        row = (report.get("section_results") or {}).get(sid) or {}
        pg = row.get("pass_guard_violations") or []
        lines.append(
            f"| {sid} | {row.get('receipt_completeness')} | {row.get('srfs_active')} | "
            f"{row.get('x2_srfs_gate_status')} | {row.get('prompt_reflection_status')} | "
            f"{len(pg)} violations |"
        )
    lines.extend(
        [
            "",
            "## explicit_non_claims",
            "",
        ]
    )
    for claim in report.get("explicit_non_claims") or []:
        lines.append(f"- {claim}")
    aj = report.get("advisory_judge_review") or {}
    lines.extend(
        [
            "",
            "## advisory_judge_review",
            "",
            f"- **enabled:** {aj.get('enabled')}",
            f"- **status:** {aj.get('status')}",
            f"- **mocked_or_live:** {aj.get('mocked_or_live')}",
            f"- **can_change_deterministic_status:** {aj.get('can_change_deterministic_status')}",
        ]
    )
    for finding in aj.get("findings") or []:
        lines.append(f"- finding: {finding}")
    lines.extend(["", "## decisive_reason", "", str(report.get("decisive_reason")), ""])
    return "\n".join(lines)


def write_srfs_audit_report(report: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    """Write JSON + Markdown audit report. Returns (json_path, md_path)."""
    out = Path(output_dir)
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise AggregatorOperationalError(f"Cannot create output dir {out}: {exc}") from exc
    json_path = out / "apps_rg_srfs_audit_report.json"
    md_path = out / "apps_rg_srfs_audit_report.md"
    try:
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path.write_text(_render_markdown(report), encoding="utf-8")
    except OSError as exc:
        raise AggregatorOperationalError(f"Cannot write report: {exc}") from exc
    return json_path, md_path


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate section_metric_receipt.json files into SRFS structural audit report.",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--receipt-manifest", dest="receipt_manifest", help="JSON manifest section_id -> receipt path")
    src.add_argument("--receipt-root", dest="receipt_root", help="Recursive discovery root (convenience)")
    parser.add_argument(
        "--manifest",
        dest="source_manifest",
        default="docs/reports/apps_rg/srfs_per_section_w1_w7_closeout_manifest.json",
        help="Closeout / expected-sections reference (not used to resolve receipt paths)",
    )
    parser.add_argument("--out", dest="output_dir", required=True, help="Output directory for audit report")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Optional aggregator run id")
    parser.add_argument("--repo-root", dest="repo_root", default=".", help="Base for relative manifest paths")
    parser.add_argument(
        "--enable-advisory-judge",
        action="store_true",
        help="Run optional apps_rg-local advisory review (does not change deterministic status)",
    )
    parser.add_argument(
        "--judge-mock",
        action="store_true",
        help="Use mock heuristic advisory review (required for W6 local path)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_cli_parser().parse_args(argv)
    try:
        loaded = load_section_receipts(
            receipt_manifest_path=args.receipt_manifest,
            receipt_root=args.receipt_root,
            repo_root=args.repo_root,
        )
        report = build_srfs_audit_report(
            loaded,
            source_manifest_ref=args.source_manifest,
            receipt_manifest_ref=args.receipt_manifest,
            receipt_root=args.receipt_root,
            run_id=args.run_id,
        )
        from apps_rg.audit.srfs_audit_advisory_judge import attach_advisory_judge_review

        report = attach_advisory_judge_review(
            report,
            enable=bool(args.enable_advisory_judge),
            mock=bool(args.judge_mock),
        )
        json_path, _md_path = write_srfs_audit_report(report, args.output_dir)
    except AggregatorOperationalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    aj = report.get("advisory_judge_review") or {}
    print(f"report_path={json_path}")
    print(f"deterministic_status={report['status']}")
    print(f"proof_level={report['proof_level']}")
    print(f"advisory_judge_status={aj.get('status')}")
    print(f"advisory_judge_mocked_or_live={aj.get('mocked_or_live')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
