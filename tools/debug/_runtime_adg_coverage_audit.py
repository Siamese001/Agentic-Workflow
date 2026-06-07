"""Runtime ADG coverage audit — read-only diagnostic.

Plan: `docs/archive/windsurf/legacy-tree/plans/runtime-adg-coverage-audit-4f7a21.md`

Produces a markdown report at `docs/reports/runtime_adg_coverage_<ts>.md`
answering: how many agents emit OTEL, how many snapshots are bound to a
trace_id, what schema compliance looks like, where the gaps are.
"""

from __future__ import annotations

import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Path to runtime ADG backend (resolved from otel_config, not hard-coded).
from tools.otel.otel_config import build_config  # noqa: E402

_RUNTIME_ADG_DIR = build_config(str(_REPO_ROOT / "tools" / "otel" / "otel_mcp_server.py")).runtime_adg_dir

# Patterns we search for in source trees.
_SCAN_ROOTS = (
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "system_learning",
    "infrastructure",
)

_AGENT_CLASS_RE = re.compile(r"^class\s+(\w*Agent)\s*[\(:]", re.MULTILINE)
_GET_TRACER_RE = re.compile(r"\bget_tracer\s*\(")
_START_SPAN_RE = re.compile(r"\b(?:start_span|start_as_current_span|as_current_span)\s*\(")
_LIFECYCLE_EMIT_RE = re.compile(r"\bemit_[a-z_]+\s*\(|\brecord_execution_trace\s*\(")
_PERSIST_RE = re.compile(r"\.persist\s*\(\s*[\w.]*(?:Snapshot|snapshot)")


def _iter_py_files() -> list[Path]:
    files: list[Path] = []
    for root in _SCAN_ROOTS:
        rp = _REPO_ROOT / root
        if not rp.exists():
            continue
        files.extend(rp.rglob("*.py"))
    return files


def scan_emitters() -> dict[str, Any]:
    """Scan source trees for OTEL-emit signatures."""
    agents: set[str] = set()
    files_with_get_tracer: list[str] = []
    files_with_start_span: list[str] = []
    files_with_lifecycle_emit: list[str] = []
    files_with_persist: list[str] = []

    for f in _iter_py_files():
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = f.relative_to(_REPO_ROOT).as_posix()
        for m in _AGENT_CLASS_RE.finditer(text):
            agents.add(m.group(1))
        if _GET_TRACER_RE.search(text):
            files_with_get_tracer.append(rel)
        if _START_SPAN_RE.search(text):
            files_with_start_span.append(rel)
        if _LIFECYCLE_EMIT_RE.search(text):
            files_with_lifecycle_emit.append(rel)
        if _PERSIST_RE.search(text):
            files_with_persist.append(rel)

    return {
        "agent_class_count": len(agents),
        "agent_classes": sorted(agents),
        "files_get_tracer": sorted(files_with_get_tracer),
        "files_start_span": sorted(files_with_start_span),
        "files_lifecycle_emit": sorted(files_with_lifecycle_emit),
        "files_persist_snapshot": sorted(files_with_persist),
    }


def inspect_trace_index() -> dict[str, Any]:
    """Integrity check on the trace-index + version-index JSON files."""
    idx_path = _RUNTIME_ADG_DIR / "_index.json"
    tidx_path = _RUNTIME_ADG_DIR / "_trace_index.json"
    if not idx_path.exists():
        return {"error": f"missing {idx_path}"}

    version_index: dict[str, str] = json.loads(idx_path.read_text(encoding="utf-8"))
    trace_index: dict[str, str] = (
        json.loads(tidx_path.read_text(encoding="utf-8")) if tidx_path.exists() else {}
    )

    # Verify every trace-index value points to a real version.
    tidx_dangling = [(k, v) for k, v in trace_index.items() if v not in version_index]
    # Verify every version has a content-addressed file on disk.
    missing_files: list[str] = []
    for _version_id, content_hash in version_index.items():
        p = _RUNTIME_ADG_DIR / content_hash[:2] / f"{content_hash}.json"
        if not p.exists():
            missing_files.append(content_hash)
    # Empty-string keys/values are a schema violation.
    empty_trace_keys = [k for k in trace_index.keys() if not k]
    empty_trace_vals = [k for k, v in trace_index.items() if not v]
    bound = {v for v in trace_index.values() if v in version_index}
    unbound_version_ids = [vid for vid in version_index if vid not in bound]

    return {
        "version_count": len(version_index),
        "trace_bound_count": len(bound),
        "trace_unbound_count": len(unbound_version_ids),
        "trace_unbound_pct": round(100.0 * len(unbound_version_ids) / max(1, len(version_index)), 1),
        "trace_index_empty_keys": len(empty_trace_keys),
        "trace_index_empty_values": len(empty_trace_vals),
        "trace_index_dangling": len(tidx_dangling),
        "snapshot_files_missing_on_disk": len(missing_files),
    }


def sample_snapshots(n: int = 5) -> list[dict[str, Any]]:
    """Load a handful of snapshot files to check schema compliance.

    Payload is double-wrapped: the file is `{"payload_hex": "<hex>"}` and
    the decoded hex is canonical bytes for `_deserialise_snapshot`. We
    unwrap both layers for an accurate schema view.
    """
    from agentic_core.L6_system_learning.store import _deserialise_snapshot

    idx_path = _RUNTIME_ADG_DIR / "_index.json"
    if not idx_path.exists():
        return []
    version_index: dict[str, str] = json.loads(idx_path.read_text(encoding="utf-8"))
    hashes = list(version_index.values())
    if not hashes:
        return []
    sampled = random.sample(hashes, min(n, len(hashes)))
    out: list[dict[str, Any]] = []
    for h in sampled:
        p = _RUNTIME_ADG_DIR / h[:2] / f"{h}.json"
        if not p.exists():
            continue
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
            snap = _deserialise_snapshot(bytes.fromhex(meta["payload_hex"]))
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            out.append({"hash": h[:16], "error": str(exc)})
            continue
        out.append(
            {
                "hash": h[:16],
                "size_bytes": p.stat().st_size,
                "has_trace_id": bool(snap.trace_id),
                "has_snapshot_id": bool(snap.snapshot_id),
                "node_count": len(snap.nodes),
                "edge_count": len(snap.edges),
                "top_level_keys": ["trace_id", "mission", "nodes", "edges"],
            }
        )
    return out


def write_report(emitters: dict[str, Any], integrity: dict[str, Any], samples: list[dict[str, Any]]) -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    report_path = _REPO_ROOT / "docs" / "reports" / f"runtime_adg_coverage_{ts}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Count emit-site overlap.
    emit_union = set(
        emitters["files_get_tracer"] + emitters["files_start_span"] + emitters["files_lifecycle_emit"]
    )
    persist_sites = set(emitters["files_persist_snapshot"])

    # Try to classify emit sites by top-level package.
    by_top_pkg: Counter[str] = Counter()
    for f in emit_union:
        top = f.split("/", 1)[0]
        by_top_pkg[top] += 1

    lines: list[str] = []
    lines.append(f"# Runtime ADG Coverage Audit — {ts}")
    lines.append("")
    lines.append("**Plan**: `docs/archive/windsurf/legacy-tree/plans/runtime-adg-coverage-audit-4f7a21.md`")
    lines.append(f"**Runtime ADG dir**: `{_RUNTIME_ADG_DIR.as_posix()}`")
    lines.append("")
    lines.append("## 1. Emitter inventory")
    lines.append("")
    lines.append(f"- Agent classes discovered: **{emitters['agent_class_count']}**")
    lines.append(f"- Files calling `get_tracer(`: **{len(emitters['files_get_tracer'])}**")
    lines.append(
        f"- Files calling `start_span(` / `as_current_span(`: **{len(emitters['files_start_span'])}**"
    )
    lines.append(
        f"- Files using lifecycle emit contract (`emit_*` / `record_execution_trace`): "
        f"**{len(emitters['files_lifecycle_emit'])}**"
    )
    lines.append(f"- Files calling `.persist(<snapshot>)`: **{len(emitters['files_persist_snapshot'])}**")
    lines.append(f"- Union of any emit signature: **{len(emit_union)}** files")
    lines.append("")
    lines.append("### Emit sites by top-level package")
    lines.append("")
    lines.append("| Package | Files with emit signature |")
    lines.append("|---|---|")
    for pkg, cnt in by_top_pkg.most_common():
        lines.append(f"| `{pkg}/` | {cnt} |")
    lines.append("")
    lines.append("### Snapshot persist() call sites")
    lines.append("")
    if persist_sites:
        for f in sorted(persist_sites):
            lines.append(f"- `{f}`")
    else:
        lines.append("_(none detected)_")
    lines.append("")

    lines.append("## 2. Trace-index integrity")
    lines.append("")
    if "error" in integrity:
        lines.append(f"**ERROR**: {integrity['error']}")
    else:
        lines.append(f"- Snapshots in `_index.json`: **{integrity['version_count']}**")
        lines.append(f"- Snapshots bound to a trace_id: **{integrity['trace_bound_count']}**")
        lines.append(
            f"- Snapshots UNBOUND (no trace_id): "
            f"**{integrity['trace_unbound_count']}** "
            f"(**{integrity['trace_unbound_pct']}%**)"
        )
        lines.append(f"- Empty-string keys in `_trace_index.json`: **{integrity['trace_index_empty_keys']}**")
        lines.append(
            f"- Empty-string values in `_trace_index.json`: **{integrity['trace_index_empty_values']}**"
        )
        lines.append(
            f"- Dangling trace-index entries "
            f"(value not in `_index.json`): **{integrity['trace_index_dangling']}**"
        )
        lines.append(
            f"- Missing content-addressed files on disk: **{integrity['snapshot_files_missing_on_disk']}**"
        )
    lines.append("")

    lines.append("## 3. Snapshot schema sampling (N=5)")
    lines.append("")
    if not samples:
        lines.append("_(no samples available)_")
    else:
        lines.append("| Hash | Size | trace_id? | snapshot_id? | Nodes | Edges |")
        lines.append("|---|---|---|---|---|---|")
        for s in samples:
            if "error" in s:
                lines.append(f"| `{s.get('hash', '?')}` | ERROR | — | — | — | {s['error']} |")
                continue
            lines.append(
                f"| `{s['hash']}` | {s['size_bytes']} | "
                f"{'✅' if s['has_trace_id'] else '❌'} | "
                f"{'✅' if s['has_snapshot_id'] else '❌'} | "
                f"{s['node_count']} | {s['edge_count']} |"
            )
    lines.append("")

    lines.append("## 4. Gap classification")
    lines.append("")
    if "error" not in integrity:
        unbound_pct = integrity["trace_unbound_pct"]
        if unbound_pct > 80:
            band = "P2"
            impact = (
                "Severe: the overwhelming majority of persisted snapshots cannot "
                "be joined back to a trace. Healing-chain and OTEL-driven "
                "meta-learning run on incomplete data."
            )
        elif unbound_pct > 30:
            band = "P3"
            impact = (
                "Moderate: substantial fraction of snapshots lack trace binding. "
                "Trace-scoped queries return low recall."
            )
        elif unbound_pct > 5:
            band = "P4"
            impact = "Minor: small fraction of snapshots unbound."
        else:
            band = "P5"
            impact = "Trace-index integrity is healthy."

        lines.append(f"- **Priority band**: {band}")
        lines.append(f"- **Impact**: {impact}")
        lines.append("")
        lines.append("### Recommended remediation (out of scope for this audit)")
        lines.append("")
        lines.append(
            "1. Audit `FileBackedRuntimeADGStore.persist()` callers; enforce "
            "`trace_id` is non-empty before commit."
        )
        lines.append(
            "2. Add a guardrail in `system_learning/runtime_adg/store.py` that "
            "rejects snapshots with empty or missing `trace_id`."
        )
        lines.append(
            "3. Back-fill `_trace_index.json` by inspecting snapshot payloads "
            "that DO contain a `trace_id` field even if the index didn't record it."
        )

    lines.append("")
    lines.append("## 5. DEFERRED_SCOPE marker")
    lines.append("")
    if "error" not in integrity and integrity["trace_unbound_pct"] > 30:
        # Emit a DEFERRED_SCOPE marker that the post-hook can parse.
        lines.append(
            "DEFERRED_SCOPE: plan=NEW:runtime-adg-trace-binding-remediation "
            "wave=RT1 phase=RT1.1 layer=L4 fan_in=3 surface=Observability "
            "coverage_gap_pct={gap} est_tokens=9000 "
            "reason=runtime ADG snapshots unbound from trace IDs".format(gap=integrity["trace_unbound_pct"])
        )
    else:
        lines.append("_(no deferred scope — coverage is healthy or unknown)_")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    print("Scanning emitters across repo...")
    emitters = scan_emitters()
    print(f"  -> {emitters['agent_class_count']} agent classes")
    print(f"  -> {len(emitters['files_get_tracer'])} files with get_tracer")
    print(f"  -> {len(emitters['files_persist_snapshot'])} files with snapshot.persist()")

    print("Inspecting trace-index integrity...")
    integrity = inspect_trace_index()
    if "error" in integrity:
        print(f"  !! {integrity['error']}")
    else:
        print(f"  -> {integrity['version_count']} snapshots; {integrity['trace_unbound_pct']}% unbound")

    print("Sampling snapshot payloads (N=5)...")
    samples = sample_snapshots(n=5)
    print(f"  -> {len(samples)} samples inspected")

    # Tier 1.5: full-corpus category analysis — distinguishes satisfied vs.
    # name_mismatch vs. emit_site_gap.
    print("Analyzing Tier 1 corpus coverage...")
    try:
        from agentic_core.L6_system_learning.span_contracts import (
            validate_tier1_corpus_coverage,
        )
        from agentic_core.L6_system_learning.store import _deserialise_snapshot

        version_index = json.loads((_RUNTIME_ADG_DIR / "_index.json").read_text(encoding="utf-8"))
        corpus: list[Any] = []
        for h in version_index.values():
            p = _RUNTIME_ADG_DIR / h[:2] / f"{h}.json"
            if not p.exists():
                continue
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
                corpus.append(_deserialise_snapshot(bytes.fromhex(meta["payload_hex"])))
            except (OSError, ValueError, KeyError):
                continue

        report = validate_tier1_corpus_coverage(corpus)
        integrity["tier1_corpus"] = report.to_dict()
        print(f"  -> Scanned {report.snapshots_scanned} snapshots / {report.nodes_scanned} nodes")
        print(
            f"  -> Tier 1 satisfied: {report.satisfied_count()}/5 ({round(report.satisfied_pct * 100, 1)}%)"
        )
        print(f"  -> Name mismatches: {report.name_mismatch_count()}")
        print(f"  -> Emit-site gaps:  {report.emit_site_gap_count()}")
        for cat, status in report.category_status.items():
            hits = report.category_example_hits.get(cat, ())
            marker = {
                "satisfied": "OK ",
                "name_mismatch": "NM ",
                "emit_site_gap": "GAP",
            }.get(status, "?? ")
            example = f"  (e.g. {hits[0]})" if hits else ""
            print(f"     [{marker}] {cat:<24} {status}{example}")
    except (ImportError, OSError, ValueError, KeyError) as exc:
        integrity["tier1_corpus_error"] = str(exc)
        print(f"  -> Tier 1 corpus analysis failed: {exc}")

    report_path = write_report(emitters, integrity, samples)
    print(f"\nReport written: {report_path.relative_to(_REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
