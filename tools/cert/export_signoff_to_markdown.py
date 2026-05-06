"""Fort Knox v2 — Markdown READ-ONLY exporter.

Mirrors the JSON compiler report verbatim. Does not compute status.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "artifacts" / "certification"
REPORT_PATH = OUTPUT_DIR / "final_requirement_signoff_report.json"
MERKLE_PATH = OUTPUT_DIR / "final_requirement_signoff_report.merkle.json"
SIG_PATH = OUTPUT_DIR / "final_requirement_signoff_report.signature.json"
BUNDLE_VERIFY_PATH = OUTPUT_DIR / "final_requirement_signoff_bundle_verification.json"
OUT_MD = OUTPUT_DIR / "final_requirement_signoff_report.md"

BADGE = {
    "SIGNED_OFF":   "✅ SIGNED_OFF",
    "BLOCKED":      "🔒 BLOCKED",
    "NOT_VERIFIED": "⚠️ NOT_VERIFIED",
}


def main() -> int:
    if not REPORT_PATH.exists():
        print(f"FATAL: compiler report missing. Run scripts/compile_requirement_signoff.py.", file=sys.stderr)
        return 2

    # SSOT bundle-status discipline: the Markdown export is a READ-ONLY view
    # of the JSON compiler report PLUS the bundle verifier's JSON verdict.
    # Markdown is NEVER allowed to display PASS unless the verifier JSON
    # itself says PASS. If the verifier JSON is missing OR says FAIL, the
    # Markdown export fails closed (exit non-zero) and does NOT overwrite
    # the existing Markdown file. This prevents stale "PASS" Markdown from
    # contradicting a current FAIL bundle_verification.json on disk.
    if not BUNDLE_VERIFY_PATH.exists():
        print(f"FATAL: bundle verification JSON missing: {BUNDLE_VERIFY_PATH.relative_to(REPO_ROOT)}\n"
              f"       Run scripts/verify_final_requirement_signoff_bundle.py first.",
              file=sys.stderr)
        return 3
    bv = json.loads(BUNDLE_VERIFY_PATH.read_text(encoding="utf-8"))
    bv_status = bv.get("bundle_verification_status")
    if bv_status != "PASS":
        print(f"FATAL: bundle verification status is {bv_status!r}; refusing to "
              f"emit Markdown that could mis-state PASS.",
              file=sys.stderr)
        for f in (bv.get("failures") or [])[:5]:
            print(f"  failure: {f}", file=sys.stderr)
        return 4

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    merkle = json.loads(MERKLE_PATH.read_text(encoding="utf-8")) if MERKLE_PATH.exists() else None
    sig = json.loads(SIG_PATH.read_text(encoding="utf-8")) if SIG_PATH.exists() else None

    s = report["summary"]
    L: list[str] = []
    A = L.append
    A("# Fort Knox v2 — Runtime Certification Sign-off Report")
    A("")
    A("> ⚠️ **READ-ONLY VIEW.** JSON compiler report is the authority.")
    A("> Manual edits here do NOT affect certification status.")
    A("")
    A("## Trust & Provenance")
    A("")
    A("| Field | Value |")
    A("|---|---|")
    A(f"| Trust level | **`{report.get('trust_level')}`** |")
    A(f"| Run timestamp (UTC) | `{report.get('run_timestamp_utc')}` |")
    A(f"| Compiler version | `{report.get('compiler_version')}` |")
    A(f"| Compiler sha256 | `{report.get('compiler_sha256', '')}` |")
    A(f"| Git commit | `{report.get('git_commit')}` |")
    A(f"| Git dirty | `{report.get('git_dirty')}` |")
    A(f"| Requirements source SHA256 | `{report.get('requirements_source_sha256', '')}` |")
    A(f"| Evidence assertions SHA256 | `{report.get('evidence_assertions_sha256', '')}` |")
    A(f"| Row digest | `{report.get('row_digest', '')}` |")
    A(f"| Evidence digest | `{report.get('evidence_digest', '')}` |")
    if merkle:
        A(f"| Merkle root | `{merkle.get('root', '')}` |")
        A(f"| Merkle leaf count | `{merkle.get('leaf_count', 0)}` |")
    if sig:
        A(f"| Signature status | `{sig.get('signature_verification_status', '?')}` |")
    if bv:
        A(f"| Bundle verification | `{bv.get('bundle_verification_status', '?')}` "
          f"({bv.get('checks_run', 0)} checks, {len(bv.get('failures', []))} failures) |")
    A("")

    A("## Summary")
    A("")
    A(f"**Total**: {s['total']}")
    A("")
    A("| Status | Count | % |")
    A("|---|---:|---:|")
    A(f"| ✅ SIGNED_OFF | {s['signed_off']} | {s['percent_signed_off']}% |")
    A(f"| 🔒 BLOCKED | {s['blocked']} | "
      f"{round(100.0 * s['blocked'] / max(1, s['total']), 1)}% |")
    A(f"| ⚠️ NOT_VERIFIED | {s['not_verified']} | "
      f"{round(100.0 * s['not_verified'] / max(1, s['total']), 1)}% |")
    A("")

    if s.get("by_claim_type"):
        A("## By Claim Type")
        A("")
        A("| Claim Type | Total | SIGNED_OFF | BLOCKED | NOT_VERIFIED |")
        A("|---|---:|---:|---:|---:|")
        for ct in sorted(s["by_claim_type"]):
            b = s["by_claim_type"][ct]
            A(f"| {ct} | {b['total']} | {b['signed_off']} | {b['blocked']} | {b['not_verified']} |")
        A("")

    # Blockers
    open_rows = [r for r in report["rows"] if r["computed_status"] != "SIGNED_OFF"]
    if open_rows:
        A("## Open Rows (BLOCKED / NOT_VERIFIED)")
        A("")
        A("| req_id | Status | Claim Type | Blocking Gap |")
        A("|---|---|---|---|")
        for r in sorted(open_rows, key=lambda x: x["req_id"]):
            gap = (r.get("blocking_gap") or "").replace("|", "\\|").replace("\n", " ")
            A(f"| {r['req_id']} | {BADGE[r['computed_status']]} | {r['claim_type']} | {gap} |")
        A("")

    # All rows
    A("## All Rows")
    A("")
    A("| req_id | Status | Claim Type | Priority | Title |")
    A("|---|---|---|---|---|")
    for r in sorted(report["rows"], key=lambda x: x["req_id"]):
        title = (r.get("title", "") or "").replace("|", "\\|")
        A(f"| {r['req_id']} | {BADGE[r['computed_status']]} | {r['claim_type']} | "
          f"{r.get('priority', '')} | {title} |")
    A("")

    # Per-row controls
    A("## Per-Row Control Detail")
    A("")
    for r in sorted(report["rows"], key=lambda x: x["req_id"]):
        A(f"<details><summary><b>{r['req_id']}</b> — {BADGE[r['computed_status']]} — "
          f"{r.get('title', '')}</summary>")
        A("")
        A(f"- claim_type: `{r['claim_type']}`")
        if r.get("blocking_gap"):
            A(f"- blocking_gap: `{r['blocking_gap']}`")
        A(f"- row_digest: `{r.get('row_digest', '')}`")
        A(f"- row_evidence_sha256: `{r.get('row_evidence_sha256', '')}`")
        A("")
        A("| Control | Passed | Reason | Assertion | Artifact |")
        A("|---|:---:|---|---|---|")
        for c in r["controls"]:
            badge = "✓" if c["passed"] else "✗"
            reason = (c.get("reason") or "").replace("|", "\\|").replace("\n", " ")
            aid = c.get("assertion_id") or "-"
            art = c.get("artifact_path") or "-"
            A(f"| {c['name']} | {badge} | {reason} | `{aid[:16]}` | `{art}` |")
        A("")
        A("</details>")
        A("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"[export_signoff_to_markdown] wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"  rollup (read-only, from JSON): "
          f"signed_off={s['signed_off']} blocked={s['blocked']} not_verified={s['not_verified']}")
    print(f"  trust_level: {report.get('trust_level')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
