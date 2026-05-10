"""CI gate: AG-4 Evidence Contract Carrier presence check.

Plan: ``ag4-evidence-contract-carrier-repair-d2f9a3``.

Static AST check that the AG-4 carrier fields are still declared on the
five contracts AG-4 extended.  Catches accidental field deletion in
follow-up PRs.

Bypass: ``EVIDENCE_CARRIER_BYPASS=1`` (logs warning, exits 0).

Usage::

    python ops_scripts/ci/check_evidence_contract_carriers.py

Exit codes:
    0 — all required fields present (or bypassed)
    1 — one or more required fields missing
    2 — could not import / parse a contract module
"""

from __future__ import annotations

import argparse
import ast
import os
import pathlib
import sys
from typing import Iterable

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# (relative_path, classname, required_fields)
REQUIREMENTS: tuple[tuple[str, str, frozenset[str]], ...] = (
    (
        "agentic_core/runtime/contracts/final_evidence_contract.py",
        "EvidenceItem",
        frozenset({
            "evidence_id", "source_id", "source_type", "source_version",
            "source_uri_or_ref", "source_owner_or_authority",
            "retrieved_span", "citation_anchor", "chunk_digest",
            "fact_vec_ref", "dense_score", "bm25_score", "metadata_score",
            "freshness_status", "acl_status", "origin_trust_label",
            "authority_class", "contradiction_status", "stratum",
            "allowed_prompt_slot", "support_score", "support_status",
            "retrieval_method", "retrieval_run_ref", "query_vec_ref",
            "graph_ref", "evidence_digest", "unknown_reason",
            "not_applicable_reason",
        }),
    ),
    (
        "agentic_core/runtime/contracts/final_evidence_contract.py",
        "FinalEvidenceContract",
        frozenset({
            "route_contract_ref", "retrieval_plan_ref", "query_vec_ref",
            "dense_search_refs", "sparse_search_refs",
            "metadata_filter_refs", "graph_expansion_refs",
            "evidence_strata", "citation_map", "source_lineage_map",
            "source_version_map", "acl_verification_receipts",
            "freshness_receipts", "contradiction_report", "support_status",
            "support_score_profile", "excluded_evidence_refs",
            "blocked_source_refs", "weak_support_refinement_attempts",
            "final_evidence_digest",
        }),
    ),
    (
        "agentic_core/runtime/contracts/sealed_l2_artifact.py",
        "SealedL2Artifact",
        frozenset({
            "evidence_refs", "prompt_refs", "tool_call_refs",
            "model_call_refs", "provider_receipts", "replay_manifest",
            "audit_manifest_ref",
        }),
    ),
    (
        "agentic_core/L3_orchestration/exit_eval/v6/types.py",
        "ExitReviewPacket",
        frozenset({
            "source_contract_ref", "route_contract_ref", "execution_form",
            "registry_digest_set", "evidence_refs",
            "final_evidence_contract_ref", "compiled_prompt_artifact_ref",
            "exec_trace_refs", "tool_call_refs", "model_call_refs",
            "provider_receipts", "proposed_state_diff_ref",
            "otel_span_refs", "hitl_packet_ref",
            "l5_certification_refs", "runtime_gate_refs",
            "audit_manifest_ref",
        }),
    ),
    (
        "agentic_core/runtime/contracts/x1_checkout_result.py",
        "X1CheckoutResult",
        frozenset({
            "x1a_todays_rules", "x1b_answered_it", "x1c_safe_to_leave",
            "x1d_answer_good", "x1e_trajectory_ok", "x1f_story_adds_up",
            "x1g_replay_eligible", "x1h_observable",
            "x1i_consistent_across_runs", "x1j_write_eligibility",
            "replay_manifest_ref", "otel_span_refs", "evidence_refs",
            "intent_ref", "output_ref",
        }),
    ),
    (
        "agentic_core/runtime/contracts/x1_checkout_result.py",
        "X1Item",
        frozenset({
            "gate_id", "verdict", "confidence", "evidence_refs",
            "evaluator_type", "decisive_reason", "policy_ref",
            "threshold_ref", "unknown_reason", "not_applicable_reason",
            "score", "threshold", "intent_ref", "output_ref",
        }),
    ),
)


def _extract_dataclass_fields(path: pathlib.Path, classname: str) -> set[str]:
    """Parse ``path`` and return the set of attribute names declared on
    the dataclass with the given ``classname``.

    Uses AST so we don't have to import the module (which would pull in
    contract __post_init__ chains).  Returns ``set()`` if the class is
    not found.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"check_evidence_contract_carriers: cannot read {path}: {exc}")
    except SyntaxError as exc:
        raise SystemExit(f"check_evidence_contract_carriers: syntax error in {path}: {exc}")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            attrs: set[str] = set()
            for stmt in node.body:
                # Pattern 1: AnnAssign — `field_name: T = default`
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    attrs.add(stmt.target.id)
                # Pattern 2: Assign without annotation — class-var (rare for
                # dataclass but still a field for our purposes).
                elif isinstance(stmt, ast.Assign):
                    for tgt in stmt.targets:
                        if isinstance(tgt, ast.Name):
                            attrs.add(tgt.id)
            return attrs
    return set()


def _check(verbose: bool = False) -> tuple[int, list[str]]:
    """Run all field-presence checks; return (exit_code, lines)."""
    lines: list[str] = []
    failures = 0
    for rel, classname, required in REQUIREMENTS:
        full = REPO_ROOT / rel
        if not full.exists():
            lines.append(f"  ❌ {rel} :: {classname} — file not found")
            failures += 1
            continue
        present = _extract_dataclass_fields(full, classname)
        if not present:
            lines.append(f"  ❌ {rel} :: {classname} — class not found by AST scan")
            failures += 1
            continue
        missing = required - present
        if missing:
            lines.append(
                f"  ❌ {rel} :: {classname} — missing {len(missing)} field(s): "
                f"{sorted(missing)}"
            )
            failures += 1
        elif verbose:
            lines.append(
                f"  ✅ {rel} :: {classname} — {len(required)} required field(s) present"
            )
        else:
            lines.append(f"  ✅ {classname} ({len(required)} fields)")
    return (1 if failures else 0), lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print full path for each contract.")
    args = parser.parse_args(argv)

    if os.environ.get("EVIDENCE_CARRIER_BYPASS") == "1":
        print(
            "[check_evidence_contract_carriers] BYPASS active "
            "(EVIDENCE_CARRIER_BYPASS=1) — skipping AG-4 carrier audit.",
            file=sys.stderr,
        )
        return 0

    print("[check_evidence_contract_carriers] AG-4 carrier presence check")
    print(f"[check_evidence_contract_carriers] repo_root={REPO_ROOT}")
    code, lines = _check(verbose=args.verbose)
    for line in lines:
        print(line)
    if code == 0:
        total = sum(len(req) for _, _, req in REQUIREMENTS)
        print(
            f"\n[check_evidence_contract_carriers] OK — "
            f"{total} required AG-4 fields present across "
            f"{len(REQUIREMENTS)} contracts."
        )
    else:
        print(
            "\n[check_evidence_contract_carriers] FAIL — one or more "
            "AG-4 carrier fields missing.  "
            "See plan ag4-evidence-contract-carrier-repair-d2f9a3."
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
