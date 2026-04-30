"""W4 + W5: Regenerate merkle root over upgraded bundles AND produce the
detailed post-remediation requirement matrix.

Plan: 10c-proof-depth-remediation-a9f9af.md, Waves W4 + W5.

Outputs
-------

1. ``artifacts/requirements/10c_pilot_merkle_root.json`` (UPDATED)
   - Recomputed SHA-256 Merkle over all 200 bundles using REQ_MERKLE_V1 scheme
   - evidence_mode_counts split by post-remediation depth

2. ``artifacts/requirements/10c_pilot_merkle_root.md`` (UPDATED)

3. ``docs/reports/design/10c_reconciliation/10c_post_remediation_matrix.csv`` (NEW)
   - Per-REQ row showing pre-remediation vs post-remediation depth
   - includes harness outcome, span_count, expected_seen, content_hash

4. ``docs/reports/design/10c_reconciliation/10c_post_remediation_matrix.md`` (NEW)
   - human-readable summary with band counts, depth distribution

This script is idempotent: re-running with no bundle changes produces the
same outputs (deterministic merkle root, same content hashes).
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BUNDLES_DIR = REPO / "artifacts" / "requirements" / "proof_bundles"
MERKLE_JSON = REPO / "artifacts" / "requirements" / "10c_pilot_merkle_root.json"
MERKLE_MD = REPO / "artifacts" / "requirements" / "10c_pilot_merkle_root.md"
LEDGER_CSV = REPO / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_semantic_requirement_ledger.csv"
MATRIX_CSV = REPO / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_post_remediation_matrix.csv"
MATRIX_MD = REPO / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_post_remediation_matrix.md"

LEAF_PREFIX = b"REQ_LEAF_V1\0"
NODE_PREFIX = b"REQ_NODE_V1\0"


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _leaf_hash(bundle: dict) -> str:
    return hashlib.sha256(LEAF_PREFIX + _canonical(bundle)).hexdigest()


def _node_hash(left: str, right: str) -> str:
    return hashlib.sha256(NODE_PREFIX + bytes.fromhex(left) + bytes.fromhex(right)).hexdigest()


def _merkle_root(leaves: list[str]) -> str:
    if not leaves:
        return ""
    nodes = list(leaves)
    while len(nodes) > 1:
        nodes = [
            _node_hash(nodes[i], nodes[i + 1] if i + 1 < len(nodes) else nodes[i])
            for i in range(0, len(nodes), 2)
        ]
    return nodes[0]


def _git_head() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            cwd=str(REPO), check=True, timeout=10,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _git_dirty() -> bool:
    try:
        return bool(subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True,
            cwd=str(REPO), check=True, timeout=10,
        ).stdout.strip())
    except (subprocess.SubprocessError, OSError):
        return True


def main() -> int:
    print("[regen] loading bundles...")
    bundle_paths = sorted(
        BUNDLES_DIR.glob("10c-req-*.json"),
        key=lambda p: int(p.stem.split("-")[-1]),
    )
    bundles: list[tuple[int, Path, dict]] = []
    for p in bundle_paths:
        with p.open(encoding="utf-8") as f:
            b = json.load(f)
        rid = int(p.stem.split("-")[-1])
        bundles.append((rid, p, b))
    print(f"[regen] {len(bundles)} bundles loaded")

    # Compute merkle leaves + root
    leaves = [_leaf_hash(b) for _, _, b in bundles]
    root = _merkle_root(leaves)
    print(f"[regen] new merkle root: {root}")

    # Tally evidence modes & depths
    proof_status_counts: dict[str, int] = {}
    depth_counts: dict[str, int] = {}
    harness_outcome_counts: dict[str, int] = {}
    span_seen_count = 0
    composition_satisfied_count = 0
    for _, _, b in bundles:
        proof_status_counts[b.get("proof_status", "UNKNOWN")] = (
            proof_status_counts.get(b.get("proof_status", "UNKNOWN"), 0) + 1
        )
        depth_counts[b.get("actual_proof_depth", "UNKNOWN")] = (
            depth_counts.get(b.get("actual_proof_depth", "UNKNOWN"), 0) + 1
        )
        op = b.get("otel_proof") or {}
        ho = op.get("status", "NO_HARNESS")
        harness_outcome_counts[ho] = harness_outcome_counts.get(ho, 0) + 1
        if op.get("expected_seen"):
            span_seen_count += 1
        if (b.get("composition_proof") or {}).get("status") == "SATISFIED":
            composition_satisfied_count += 1

    # Write merkle JSON + MD
    head = _git_head()
    dirty = _git_dirty()
    now = datetime.now(timezone.utc).isoformat()
    attestation = {
        "scheme": "REQ_MERKLE_V1",
        "leaf_prefix": "REQ_LEAF_V1",
        "node_prefix": "REQ_NODE_V1",
        "hash_algorithm": "SHA-256",
        "matrix_name": "10c_pilot_post_remediation",
        "computed_at_utc": now,
        "leaf_count": len(leaves),
        "expected_count": 200,
        "complete": len(leaves) == 200,
        "merkle_root": root,
        "first_leaf": {"req_id": f"10C-REQ-{bundles[0][0]:03d}", "leaf_hash": leaves[0]},
        "last_leaf": {"req_id": f"10C-REQ-{bundles[-1][0]:03d}", "leaf_hash": leaves[-1]},
        "evidence_mode_counts": proof_status_counts,
        "actual_proof_depth_counts": depth_counts,
        "harness_outcome_counts": harness_outcome_counts,
        "spans_seen_count": span_seen_count,
        "composition_satisfied_count": composition_satisfied_count,
        "git_head_at_attestation": head,
        "git_dirty_at_attestation": dirty,
        "attestation_caveat": (
            "This Merkle root attests the file-and-evidence state of the 10C "
            "pilot requirements matrix at the recorded git HEAD POST W1-W3 "
            "remediation. Per anti-cheat invariants in plan §8: "
            "(a) actual_proof_depth values reflect what the W1 OTel harness "
            "actually captured (not what the ledger metadata claimed); "
            "(b) E6.5/E5 depths require real OTel SDK span emission at run "
            "time, verified by SHA-256 over the canonical normalized span "
            "list; (c) NO_SPANS_EMITTED bundles preserve E4 depth honestly. "
            "The root does NOT claim live replay execution at attestation "
            "time; the harness re-ran the existing test suite under an "
            "InMemorySpanExporter and recorded what production code emitted."
        ),
    }
    MERKLE_JSON.write_text(json.dumps(attestation, indent=2), encoding="utf-8")
    print(f"[regen] wrote: {MERKLE_JSON.relative_to(REPO)}")

    md_lines = [
        "# 10C Pilot Requirements -- Merkle Root Attestation (Post-Remediation)",
        "",
        f"> **{len(leaves)}/200 requirements attested at recorded git HEAD.**",
        f"> Computed: {now}",
        f"> Git HEAD: `{head}` (dirty={dirty})",
        "",
        "## Merkle root",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Scheme | `REQ_MERKLE_V1` |",
        f"| Hash algorithm | SHA-256 |",
        f"| Leaf prefix | `b\"REQ_LEAF_V1\\0\"` |",
        f"| Node prefix | `b\"REQ_NODE_V1\\0\"` |",
        f"| Leaf count | **{len(leaves)}** |",
        f"| Expected count | 200 |",
        f"| Complete | **{attestation['complete']}** |",
        f"| **Merkle root** | `{root}` |",
        "",
        "## Evidence-mode split",
        "",
        "| Mode (proof_status) | Count |",
        "|---|---:|",
    ]
    for k, v in sorted(proof_status_counts.items(), key=lambda kv: -kv[1]):
        md_lines.append(f"| `{k}` | {v} |")
    md_lines += ["", "## actual_proof_depth distribution (post-remediation)", "",
                 "| Depth | Count |", "|---|---:|"]
    for k, v in sorted(depth_counts.items(), key=lambda kv: -kv[1]):
        md_lines.append(f"| `{k}` | {v} |")
    md_lines += ["", "## Harness outcome distribution", "",
                 "| outcome | count |", "|---|---:|"]
    for k, v in sorted(harness_outcome_counts.items(), key=lambda kv: -kv[1]):
        md_lines.append(f"| `{k}` | {v} |")
    md_lines += [
        "",
        f"- **Spans seen (expected_span match)**: {span_seen_count} of {len(bundles)}",
        f"- **Composition proofs SATISFIED**: {composition_satisfied_count}",
        "",
        "## Caveats (what this root does NOT claim)",
        "",
        "- No live replay execution at attestation time",
        "- No live OTEL emission validation",
        "- E6.5_INTEGRATED_RUNTIME and E5_COMPOSITION_PROOF rows reflect what",
        "  the W1 harness captured during a prior pytest run; re-running the",
        "  harness on the same code at this git HEAD will produce the same",
        "  replay_digest values.",
        "- E4_NEGATIVE_CONTROL rows mean the existing test_10c_req_*.py file",
        "  uses synthetic SpanReceipts (not real OTel SDK), so the harness",
        "  could not capture any production-emitted spans. Closing this gap",
        "  per-REQ requires upgrading each test to drive real production code.",
    ]
    MERKLE_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[regen] wrote: {MERKLE_MD.relative_to(REPO)}")

    # ── Build the post-remediation matrix CSV
    print("[regen] building post-remediation matrix CSV...")
    # Read original ledger to preserve REQ metadata
    ledger_rows: dict[str, dict[str, str]] = {}
    if LEDGER_CSV.exists():
        with LEDGER_CSV.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("req_id"):
                    ledger_rows[row["req_id"]] = row

    matrix_rows: list[dict[str, str]] = []
    for rid, p, b in bundles:
        req_id = b.get("req_id", f"10C-REQ-{rid:03d}")
        ledger = ledger_rows.get(req_id, {})
        op = b.get("otel_proof") or {}
        comp = b.get("composition_proof") or {}
        matrix_rows.append({
            "req_id": req_id,
            "canonical_owner_surface": b.get("canonical_owner_surface", ledger.get("canonical_owner_surface", "")),
            "layer_owner": ledger.get("layer_owner", ""),
            "expected_span": ledger.get("otel_span_expected", ""),
            "test_file_expected": ledger.get("test_file_expected", ""),
            "ci_gate_name": ledger.get("ci_gate_name", ""),
            "prior_proof_status": ledger.get("evidence_status", ""),
            "prior_final_status": ledger.get("final_acceptance_status", ""),
            "actual_proof_depth": b.get("actual_proof_depth", ""),
            "proof_status": b.get("proof_status", ""),
            "harness_outcome": op.get("status", "NO_HARNESS"),
            "span_count": str(op.get("span_count", 0)),
            "expected_seen": str(op.get("expected_seen", False)).lower(),
            "harness_replay_digest": op.get("replay_digest", ""),
            "composition_status": comp.get("status", "") if comp else "",
            "composition_components_reached": str(len(comp.get("components_reached", []))) if comp else "0",
            "content_hash": b.get("content_hash", ""),
            "git_head_at_test_time": b.get("git_head_at_test_time", ""),
            "caveat_class": b.get("caveat_class", ""),
            "caveat_reason": (b.get("caveat_reason", "") or "")[:200],
        })

    field_order = list(matrix_rows[0].keys()) if matrix_rows else []
    with MATRIX_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_order)
        writer.writeheader()
        for r in matrix_rows:
            writer.writerow(r)
    print(f"[regen] wrote: {MATRIX_CSV.relative_to(REPO)}")

    # MD summary of the matrix
    md = ["# 10C Post-Remediation Requirement Matrix",
          "",
          f"> Generated: {now}",
          f"> Git HEAD: `{head}` (dirty={dirty})",
          f"> Source bundles: `artifacts/requirements/proof_bundles/10c-req-*.json` (200 files)",
          f"> Merkle root: `{root}`",
          "",
          "## 1. Headline numbers",
          "",
          "| Metric | Count |",
          "|---|---:|",
          f"| Total rows | **{len(bundles)}** |",
          f"| EVIDENCE_PRESENT (any depth) | {proof_status_counts.get('EVIDENCE_PRESENT', 0)} |",
          f"| ACCEPTED_WITH_CAVEAT (pedagogical) | {proof_status_counts.get('ACCEPTED_WITH_CAVEAT', 0)} |",
          f"| Spans seen (expected_span captured) | **{span_seen_count}** |",
          f"| Composition proofs SATISFIED | **{composition_satisfied_count}** |",
          "",
          "## 2. actual_proof_depth distribution",
          "",
          "| Depth tier | Count | Meaning |",
          "|---|---:|---|"]
    depth_meanings = {
        "E0_REQUIREMENT_TEXT": "Requirement exists as text only / harness errored",
        "E1_SOURCE_MAPPING": "Mapped to source/reference",
        "E2_STATIC_CHECK": "Static schema/metadata check exists",
        "E3_COMPONENT_TEST": "Unit/component test exists",
        "E4_NEGATIVE_CONTROL": "Negative/fail-closed control in metadata; synthetic test fixtures",
        "E5_COMPOSITION_PROOF": "Production components composed with provenance chain (W2 harness)",
        "E6.5_INTEGRATED_RUNTIME": "Real OTel SDK + InMemorySpanExporter captured the expected span",
        "E7_REAL_OTEL_EXPORT": "Collector-backed export proven (deferred — strict E7 requires docker collector)",
    }
    for k, v in sorted(depth_counts.items(), key=lambda kv: -kv[1]):
        md.append(f"| `{k}` | {v} | {depth_meanings.get(k, '')} |")

    md += ["",
           "## 3. Harness outcome distribution (W3 sweep)",
           "",
           "| outcome | count |",
           "|---|---:|"]
    for k, v in sorted(harness_outcome_counts.items(), key=lambda kv: -kv[1]):
        md.append(f"| `{k}` | {v} |")

    md += ["",
           "## 4. Bundles upgraded by W2 composition harnesses",
           ""]
    for rid, p, b in bundles:
        comp = b.get("composition_proof") or {}
        if comp.get("status") == "SATISFIED":
            md.append(f"- **{b['req_id']}**: composition SATISFIED, depth=`{b.get('actual_proof_depth')}`. "
                      f"Components reached: {len(comp.get('components_reached', []))}.")
    md += ["",
           "## 5. Honest residuals (per anti-cheat §8)",
           "",
           "Most existing `test_10c_req_*.py` tests use synthetic `SpanReceipt` fixtures",
           "(see `tests/fixtures/proof_evidence/otel_span_receipt.py` docstring) and do",
           "not exercise real OTel SDK emit paths. The W1 harness ran cleanly against",
           f"all {len(bundles)} test files but captured zero spans for {harness_outcome_counts.get('NO_SPANS_EMITTED', 0)} of them.",
           "",
           "This is **honest residual gap**, not a harness defect. Closing the gap",
           "to `E6.5_INTEGRATED_RUNTIME` requires upgrading each affected test to:",
           "",
           "1. Install or attach to a real OTel `TracerProvider`",
           "2. Invoke production code (e.g., `L2SpanEmitter.span(...)`) instead of",
           "   constructing synthetic `SpanReceipt`s",
           "3. Assert the captured span matches the expected name + attributes",
           "",
           "The W2 composition harness pattern (see `tools/proof/composition_proof_*.py`)",
           "demonstrates one viable approach for individual REQs that justify the work.",
           "",
           "## 6. Reproduction",
           "",
           "```",
           "# Re-run sweep (idempotent at fixed git HEAD)",
           "python -m tools.proof.sweep_otel_evidence --no-progress",
           "",
           "# Re-apply W2 composition results",
           "python -m tools.proof.apply_composition_results",
           "",
           "# Re-compute merkle root + regenerate this matrix",
           "python -m tools.proof.regenerate_matrix_and_merkle",
           "```",
           "",
           "## 7. Provenance",
           "",
           f"- Plan: `.windsurf/plans/10c-proof-depth-remediation-a9f9af.md`",
           f"- Source overlay: `C:\\Users\\amita\\Documents\\10c_requirement_proof_depth_certification_overlay.xlsx`",
           f"- W1 harness: `tools/proof/otel_collector_proof.py` + `tools/proof/_pytest_otel_capture_plugin.py`",
           f"- W2 composition harnesses: `tools/proof/composition_proof_semantic_cache.py`, `tools/proof/composition_proof_provenance_chain.py`",
           f"- W3 sweep tool: `tools/proof/sweep_otel_evidence.py`",
           f"- W4+W5 generator: `tools/proof/regenerate_matrix_and_merkle.py` (this script)"]
    MATRIX_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"[regen] wrote: {MATRIX_MD.relative_to(REPO)}")
    print()
    print("=" * 60)
    print(f"FINAL MERKLE ROOT: {root}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
