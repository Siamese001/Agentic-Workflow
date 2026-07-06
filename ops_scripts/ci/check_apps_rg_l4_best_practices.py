#!/usr/bin/env python3
"""Fail-closed apps_rg R1B/L4 best-practice regression gate."""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _failures() -> list[str]:
    failures: list[str] = []

    derived = _text("apps_rg/cache/r1b_derived_index.py")
    if "fixture_fallback_forbidden" not in derived or "_derived_index_unavailable_report" not in derived:
        failures.append("derived index missing fail-closed unavailable report")
    if "APPS_RG_R1B_ALLOW_FIXTURE_FALLBACK_FOR_TESTS" not in derived:
        failures.append("test-only fixture fallback env guard missing")
    if '"fixture_store_consulted": False' not in derived:
        failures.append("derived-index unavailable report does not prove fixture_store_consulted=false")

    promotion = _text("apps_rg/cache/r1b_uwg_promotion.py")
    if "mirror_fixture_on_blocked: bool = False" not in promotion:
        failures.append("mirror_fixture_on_blocked default is not false")
    if "_inject_uwg_commit_receipt_l5_fields" in promotion:
        failures.append("apps_rg UWG receipt monkeypatch helper present")
    if "patch(" in promotion and "UWGCommitReceipt" in promotion:
        failures.append("apps_rg patches UWGCommitReceipt")
    for needle in (
        "source_commit_receipt_ref",
        "core_uwg_commit_receipt",
        "audit_append_receipt_ref",
        "chain_hash",
    ):
        if needle not in promotion:
            failures.append(f"durable projection missing {needle}")

    records = _text("agentic_core/L4_state/contracts/records.py")
    for field in (
        "gate_verdict_refs",
        "cleared_exit_review_packet_ref",
        "registry_digest_set",
        "clearance_proof_id",
        "staged_diff_hash",
        "content_hash",
        "prev_chain_hash",
        "chain_hash",
    ):
        if field not in records:
            failures.append(f"core records missing {field}")

    audit = _text("agentic_core/L4_state/audit/audit_ledger.py")
    if "def chain_check" not in audit:
        failures.append("audit ledger missing chain_check")

    if 'no_mutation_assertion: str = "NO_MUTATION_APPLIED"' not in records:
        failures.append("blocked commit receipt missing NO_MUTATION_APPLIED default")

    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from agentic_core.L4_state.contracts.records import AuditLedgerRecord, CommitRequest, UWGCommitReceipt

        commit_fields = {f.name for f in dataclasses.fields(UWGCommitReceipt)}
        request_fields = {f.name for f in dataclasses.fields(CommitRequest)}
        audit_fields = {f.name for f in dataclasses.fields(AuditLedgerRecord)}
        for field in (
            "source_surface",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "gate_verdict_refs",
            "clearance_proof_id",
            "staged_diff_hash",
            "content_hash",
            "chain_hash",
        ):
            if field not in commit_fields:
                failures.append(f"UWGCommitReceipt dataclass missing {field}")
        for field in (
            "registry_digest_set",
            "capability_token_ref",
            "clearance_proof_id",
            "validator_receipt_id",
            "staged_diff_hash",
            "commit_request_signature",
        ):
            if field not in request_fields:
                failures.append(f"CommitRequest dataclass missing {field}")
        for field in ("prev_chain_hash", "chain_hash"):
            if field not in audit_fields:
                failures.append(f"AuditLedgerRecord dataclass missing {field}")
    except Exception as exc:  # guardian: explicit failure report for CI import/runtime drift
        failures.append(f"dataclass introspection failed: {type(exc).__name__}: {exc}")

    for needle in (
        "source_commit_receipt_refs",
        "source_refresh_receipt_refs",
        "read_surface_role",
        "read_surface_refresh_receipt_missing",
    ):
        if needle not in derived:
            failures.append(f"derived index missing {needle}")

    return failures


def main() -> int:
    failures = _failures()
    if failures:
        print("[check_apps_rg_l4_best_practices] FAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("[check_apps_rg_l4_best_practices] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
