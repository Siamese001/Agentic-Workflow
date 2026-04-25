"""Cross-tabulate the overlay detector output vs the canonical tech_debt_audit.

For each tech-debt category we know about, this asks:
  * Did the overlay detector find the items the audit found?
  * Did the overlay detector find items the audit missed?
  * Did the audit find items the overlay missed (false negative)?

Outputs a markdown coverage report and a JSON evidence file.
"""

from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT_JSON = REPO / "docs" / "reports" / "plans" / "tech_debt_audit.json"
OUT_MD = REPO / "docs" / "reports" / "plans" / "adg_overlay_verification.md"
OUT_JSON = REPO / "docs" / "reports" / "plans" / "adg_overlay_verification.json"


def latest_overlay() -> Path:
    snaps = sorted(
        glob.glob(str(REPO / "artifacts/adg/adg_debt_overlay_*.sqlite")),
        key=os.path.getmtime,
    )
    if not snaps:
        raise SystemExit("No overlay snapshot")
    return Path(snaps[-1])


def load_audit() -> dict:
    return json.loads(AUDIT_JSON.read_text(encoding="utf-8"))


def overlay_signatures(con: sqlite3.Connection, category: str) -> set:
    """Return a set of (file, key) tuples representing the overlay's findings."""
    if category == "dead_import":
        return {
            (r[0], r[1])
            for r in con.execute("SELECT source_file, module FROM overlay_imports WHERE status='missing'")
        }
    if category == "namespace_pkg_import":
        return {
            (r[0], r[1])
            for r in con.execute(
                "SELECT source_file, module FROM overlay_imports WHERE status='namespace_pkg'"
            )
        }
    if category == "import_error_fallback_stub":
        return {
            (r[0], r[1])
            for r in con.execute(
                "SELECT file_path, evidence FROM overlay_violations "
                "WHERE category='import_error_fallback_stub'"
            )
        }
    if category == "module_duplicate":
        # Use hash as the cluster key
        return {
            (r[0], r[1])
            for r in con.execute(
                "SELECT file_path, evidence FROM overlay_violations "
                "WHERE category='module_duplicate' "
                "  AND evidence != 'da39a3ee5e6b'"
            )
        }
    if category == "stale_all_export":
        return {
            (r[0], r[1])
            for r in con.execute(
                "SELECT file_path, evidence FROM overlay_violations WHERE category='stale_all_export'"
            )
        }
    if category == "module_load_action_call":
        return {
            (r[0],)
            for r in con.execute(
                "SELECT file_path FROM overlay_violations WHERE category='module_load_action_call'"
            )
        }
    if category == "rename_shim_module":
        return {
            (r[0],)
            for r in con.execute(
                "SELECT file_path FROM overlay_violations WHERE category='rename_shim_module'"
            )
        }
    return set()


def audit_signatures(audit: dict, category: str) -> set:
    """Return a comparable set from the audit JSON."""
    if category == "dead_import":
        return {(r["file"], r["module"]) for r in audit["p3_dead_imports"] if r.get("status") == "missing"}
    if category == "namespace_pkg_import":
        return {
            (r["file"], r["module"]) for r in audit["p3_dead_imports"] if r.get("status") == "namespace_pkg"
        }
    if category == "import_error_fallback_stub":
        return {(r["file"], r["class"]) for r in audit["p2_import_error_stubs"]}
    if category == "module_duplicate":
        # Each duplicate pair has a hash and a list of files
        out: set = set()
        for r in audit["p4_duplicate_pairs"]:
            for f in r["files"]:
                out.add((f, r["hash"]))
        # Filter empty-body cluster (audit hashes use 12 chars too)
        out = {x for x in out if x[1] != "da39a3ee5e6b"}
        return out
    if category == "stale_all_export":
        out2: set = set()
        for r in audit["p7_stale_all"]:
            for missing in r["missing"]:
                out2.add((r["file"], missing))
        return out2
    if category == "module_load_action_call":
        # Original audit's p5 used >30% ratio threshold + >=20 calls
        return {(r["file"],) for r in audit["p5_synthetic_emit_files"]}
    if category == "rename_shim_module":
        return {(r["file"],) for r in audit["p1_rename_shims"]}
    return set()


def main() -> int:
    overlay_path = latest_overlay()
    print(f"# overlay: {overlay_path.name}", file=sys.stderr)
    print(f"# audit:   {AUDIT_JSON.name}", file=sys.stderr)
    audit = load_audit()
    con = sqlite3.connect(overlay_path)

    categories = [
        "dead_import",
        "namespace_pkg_import",
        "import_error_fallback_stub",
        "module_duplicate",
        "stale_all_export",
        "module_load_action_call",
        "rename_shim_module",
    ]

    rows = []
    json_evidence = {"overlay": overlay_path.name, "audit": AUDIT_JSON.name, "categories": {}}
    for cat in categories:
        ov = overlay_signatures(con, cat)
        au = audit_signatures(audit, cat)
        intersection = ov & au
        only_overlay = ov - au
        only_audit = au - ov
        union = ov | au
        prec = len(intersection) / len(ov) if ov else float("nan")
        rec = len(intersection) / len(au) if au else float("nan")
        rows.append((cat, len(au), len(ov), len(intersection), len(only_overlay), len(only_audit), prec, rec))
        json_evidence["categories"][cat] = {
            "audit_count": len(au),
            "overlay_count": len(ov),
            "intersection": len(intersection),
            "only_overlay": len(only_overlay),
            "only_audit": len(only_audit),
            "union": len(union),
            "precision": prec if prec == prec else None,
            "recall": rec if rec == rec else None,
            "examples_only_audit": list(only_audit)[:5],
            "examples_only_overlay": list(only_overlay)[:5],
        }

    # Markdown report
    out = []
    out.append("# Overlay Verification — vs `tech_debt_audit.json`")
    out.append("")
    out.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    out.append(f"**Overlay snapshot**: `artifacts/adg/{overlay_path.name}`")
    out.append(f"**Audit snapshot**:   `docs/reports/plans/{AUDIT_JSON.name}`")
    out.append("")
    out.append(
        "Each row asks: did the overlay detector and the canonical "
        "audit agree on what's debt? `intersection` is items both "
        "found; `only_audit` are items the audit found but the "
        "overlay missed (potential false negatives); `only_overlay` "
        "are items the overlay found that the audit missed "
        "(potential false positives, OR genuine new finds)."
    )
    out.append("")
    out.append("| Category | Audit | Overlay | ∩ | only_overlay | only_audit | Prec | Rec |")
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        cat, n_au, n_ov, n_x, n_oo, n_oa, prec, rec = r
        prec_s = f"{prec:.2f}" if prec == prec else "—"
        rec_s = f"{rec:.2f}" if rec == rec else "—"
        out.append(f"| `{cat}` | {n_au} | {n_ov} | {n_x} | {n_oo} | {n_oa} | {prec_s} | {rec_s} |")
    out.append("")

    # Per-category notes
    out.append("## Per-Category Notes")
    out.append("")
    for cat in categories:
        d = json_evidence["categories"][cat]
        out.append(f"### `{cat}`")
        out.append("")
        out.append(f"- audit found: **{d['audit_count']}**")
        out.append(f"- overlay found: **{d['overlay_count']}**")
        out.append(f"- intersection: **{d['intersection']}**")
        out.append(f"- precision: **{d['precision']}**, recall: **{d['recall']}**")
        if d["examples_only_audit"]:
            out.append("- examples in audit but missed by overlay (sample):")
            for ex in d["examples_only_audit"]:
                out.append(f"    - `{ex}`")
        if d["examples_only_overlay"]:
            out.append("- examples in overlay but missed by audit (sample):")
            for ex in d["examples_only_overlay"]:
                out.append(f"    - `{ex}`")
        out.append("")

    # Headline verdict
    out.append("## Verdict")
    out.append("")
    cov = []
    for cat in categories:
        d = json_evidence["categories"][cat]
        if d["audit_count"] == 0:
            continue
        rec = d["recall"]
        if rec is None:
            continue
        cov.append((cat, rec))
    cov.sort(key=lambda x: -x[1])
    for cat, rec in cov:
        verdict = (
            "✅ FULL"
            if rec >= 0.95
            else ("🟢 STRONG" if rec >= 0.80 else ("🟡 PARTIAL" if rec >= 0.50 else "🔴 WEAK"))
        )
        out.append(f"- `{cat}`: recall = {rec:.2%} → {verdict}")
    out.append("")
    out.append(
        "**Headline finding**: each detector category, by category, "
        "shows whether the overlay would have caught the canonical "
        "audit's findings. Recall ≥ 0.95 means the overlay would have "
        "surfaced essentially everything the audit did. Numbers below "
        "0.80 indicate detection logic that needs tuning before "
        "upstreaming into the canonical ADG generator."
    )

    OUT_MD.write_text("\n".join(out), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(json_evidence, indent=2, default=list), encoding="utf-8")
    print(f"\n# wrote {OUT_MD}", file=sys.stderr)
    print(f"# wrote {OUT_JSON}", file=sys.stderr)

    print()
    print("Coverage summary:")
    for cat, rec in cov:
        print(f"  {cat}: recall={rec:.2%}")

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
