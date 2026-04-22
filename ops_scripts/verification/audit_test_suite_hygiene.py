"""Phase 0 — Discovery audit of the tests/ tree.

Read-only audit. Classifies every `test_*.py` file under tests/ into hygiene
buckets so Phase 1 bulk deletion can target the right set.

Classification buckets:
    mechanical_twin     - byte-identical to another test file (e.g., X.py + X_adg.py)
    near_twin           - content-equal ignoring docstring/whitespace
    broken_assertions   - references symbols (CLASS_CANDIDATES / CALLABLE_CANDIDATES)
                          that DO NOT EXIST in the target module
    importorskip_smoke  - only contains `pytest.importorskip` + trivial shape asserts
                          (is not None, callable, isinstance type)
    substantive         - everything else (real behavioral coverage; do not touch)

Output:
    artifacts/test_audit/test_audit_<ts>.md   (human-readable report)
    artifacts/test_audit/test_audit_<ts>.json (machine-readable for Phase 1)

Usage:
    python ops_scripts/verification/audit_test_suite_hygiene.py
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests"
OUTPUT_DIR = REPO_ROOT / "artifacts" / "test_audit"

# Signals that a test file is "trivial" (shape/surface-only)
_TRIVIAL_ASSERT_PATTERNS = [
    re.compile(r"assert\s+\w+\s+is\s+not\s+None\b"),
    re.compile(r"assert\s+callable\s*\("),
    re.compile(r"assert\s+isinstance\s*\(\s*\w+\s*,\s*type\s*\)"),
    re.compile(r"assert\s+\w+\.__name__\s+in\s+"),
    re.compile(r"assert\s+public\b"),  # from auto-gen "assert public" pattern
]

_IMPORTORSKIP_RE = re.compile(r"""importorskip\(\s*['"]([\w\.]+)['"]""")
_CANDIDATE_LIST_RE = re.compile(
    r"""(?:CLASS_CANDIDATES|CALLABLE_CANDIDATES|MODULE_CANDIDATES)\s*=\s*\[([^\]]+)\]""",
    re.DOTALL,
)
_NAME_IN_LIST_RE = re.compile(r"""['"]([\w\.]+)['"]""")


def _progress(i: int, total: int, label: str, start: float) -> None:
    if total == 0:
        return
    pct = i / total
    width = 40
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    if pct >= 0.9:
        color = "\033[92m"
    elif pct >= 0.7:
        color = "\033[94m"
    elif pct >= 0.4:
        color = "\033[93m"
    else:
        color = "\033[91m"
    elapsed = time.monotonic() - start
    eta = ""
    if pct > 0 and pct < 1:
        remaining = elapsed * (1 - pct) / pct
        eta = f" - ETA: {int(remaining)}s"
    sys.stderr.write(
        f"\r{color}[{bar}]\033[0m {int(pct*100):3d}% ({i}/{total}) {label}{eta}   ",
    )
    sys.stderr.flush()
    if i >= total:
        sys.stderr.write("\n")


def _normalize_content(text: str) -> str:
    """Strip module docstring + whitespace-only lines for near-twin comparison."""
    lines = text.splitlines()
    # Drop module docstring: first triple-quoted block if file starts with it
    out: list[str] = []
    i = 0
    # Skip leading blank/comment lines
    while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    # If next non-blank/comment line starts a docstring, skip until its close
    if i < len(lines):
        stripped = lines[i].lstrip()
        for q in ('"""', "'''"):
            if stripped.startswith(q):
                if stripped.count(q) >= 2:  # one-line docstring
                    i += 1
                else:
                    i += 1
                    while i < len(lines) and q not in lines[i]:
                        i += 1
                    i += 1  # past closing
                break
    # Keep from i onward, stripping trailing whitespace and blank lines
    for ln in lines[i:]:
        s = ln.rstrip()
        if s:
            out.append(s)
    return "\n".join(out)


def _content_hash(text: str, normalized: bool = False) -> str:
    src = _normalize_content(text) if normalized else text
    return hashlib.sha256(src.encode("utf-8", errors="ignore")).hexdigest()


def _count_trivial_asserts(text: str) -> int:
    return sum(len(p.findall(text)) for p in _TRIVIAL_ASSERT_PATTERNS)


def _count_all_asserts(text: str) -> int:
    return len(re.findall(r"\bassert\s+", text))


def _extract_importorskip_targets(text: str) -> list[str]:
    return _IMPORTORSKIP_RE.findall(text)


def _extract_candidate_symbols(text: str) -> list[str]:
    """Pull names from CLASS_CANDIDATES / CALLABLE_CANDIDATES / MODULE_CANDIDATES lists."""
    names: list[str] = []
    for block in _CANDIDATE_LIST_RE.findall(text):
        names.extend(_NAME_IN_LIST_RE.findall(block))
    return names


def _check_broken_assertions(
    importorskip_targets: list[str],
    candidate_symbols: list[str],
) -> tuple[bool, list[str]]:
    """If test references candidate symbols, check they exist in any importorskip target.

    Returns (is_broken, missing_symbols). 'Broken' means: test has a candidate list
    and NONE of the candidates exist as attributes of any imported target module.
    """
    if not candidate_symbols or not importorskip_targets:
        return False, []
    # Filter out dotted candidates (those are module paths, not symbol names)
    symbol_candidates = [s for s in candidate_symbols if "." not in s]
    if not symbol_candidates:
        return False, []
    for target in importorskip_targets:
        try:
            mod = importlib.import_module(target)
        except Exception:  # noqa: BLE001 - defensive; target may be unavailable
            continue
        found = [s for s in symbol_candidates if hasattr(mod, s)]
        if found:
            return False, []  # At least one symbol resolves -> not broken
    # No importorskip target exposed any candidate -> broken
    return True, symbol_candidates


def classify_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {"path": str(path), "error": str(exc), "bucket": "unreadable"}

    rel = path.relative_to(REPO_ROOT).as_posix()
    size = len(text)
    exact_hash = _content_hash(text, normalized=False)
    normalized_hash = _content_hash(text, normalized=True)
    importorskip_targets = _extract_importorskip_targets(text)
    candidate_symbols = _extract_candidate_symbols(text)
    broken, missing = _check_broken_assertions(importorskip_targets, candidate_symbols)
    trivial_asserts = _count_trivial_asserts(text)
    total_asserts = _count_all_asserts(text)

    # Tentative bucket (mechanical_twin / near_twin assigned after pair-wise pass)
    if broken:
        bucket = "broken_assertions"
    elif (
        importorskip_targets
        and total_asserts > 0
        and trivial_asserts / max(total_asserts, 1) > 0.8
        and total_asserts <= 8
    ):
        bucket = "importorskip_smoke"
    else:
        bucket = "substantive"

    return {
        "path": rel,
        "size_bytes": size,
        "exact_hash": exact_hash,
        "normalized_hash": normalized_hash,
        "importorskip_targets": importorskip_targets,
        "candidate_symbols_referenced": candidate_symbols,
        "missing_candidates": missing,
        "trivial_asserts": trivial_asserts,
        "total_asserts": total_asserts,
        "bucket": bucket,
    }


def assign_twin_buckets(records: list[dict[str, Any]]) -> None:
    """Second pass — detect mechanical twins (exact hash) and near twins (normalized hash)."""
    # For twin pairs X.py + X_adg.py specifically: group by basename-stem-minus-suffix
    by_exact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_norm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        if r.get("bucket") == "unreadable":
            continue
        by_exact[r["exact_hash"]].append(r)
        by_norm[r["normalized_hash"]].append(r)

    # Exact-hash group of size >= 2 -> mechanical twin
    for group in by_exact.values():
        if len(group) >= 2:
            for r in group:
                # Only downgrade if bucket was "substantive" or "importorskip_smoke"
                if r["bucket"] in ("substantive", "importorskip_smoke"):
                    r["bucket"] = "mechanical_twin"
                    r["twin_group_exact_hash"] = r["exact_hash"]
                    r["twin_group_size"] = len(group)
                    r["twin_peers"] = [o["path"] for o in group if o is not r]

    # Normalized-hash-only match (not already mechanical_twin) -> near_twin
    for group in by_norm.values():
        if len(group) >= 2:
            if all(r["bucket"] == "mechanical_twin" for r in group):
                continue
            for r in group:
                if r["bucket"] in ("substantive", "importorskip_smoke"):
                    r["bucket"] = "near_twin"
                    r["twin_group_normalized_hash"] = r["normalized_hash"]
                    r["twin_group_size"] = len(group)
                    r["twin_peers"] = [o["path"] for o in group if o is not r]


def write_reports(records: list[dict[str, Any]]) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%m%d%Y_%H%M")
    json_path = OUTPUT_DIR / f"test_audit_{ts}.json"
    md_path = OUTPUT_DIR / f"test_audit_{ts}.md"

    # Summaries
    bucket_counts: dict[str, int] = defaultdict(int)
    for r in records:
        bucket_counts[r.get("bucket", "unreadable")] += 1

    # Top twin groups (size desc)
    twin_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        if r.get("bucket") in ("mechanical_twin", "near_twin"):
            key = r.get("twin_group_exact_hash") or r.get("twin_group_normalized_hash") or "?"
            twin_groups[key].append(r)

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "total_files": len(records),
                "bucket_counts": dict(bucket_counts),
                "records": records,
            },
            f,
            indent=2,
            sort_keys=True,
        )

    lines: list[str] = []
    lines.append("# Test Suite Hygiene Audit")
    lines.append("")
    lines.append(f"- **Generated (UTC)**: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"- **Tests root**: `tests/`")
    lines.append(f"- **Total test files scanned**: {len(records)}")
    lines.append("")
    lines.append("## Bucket Distribution")
    lines.append("")
    lines.append("| Bucket | Count | Phase 1 Action |")
    lines.append("|---|---:|---|")
    action_map = {
        "mechanical_twin": "**DELETE** — byte-identical duplicate",
        "near_twin": "DELETE (after spot-check) — content-identical modulo docstring",
        "broken_assertions": "DELETE — tests reference symbols not in target module",
        "importorskip_smoke": "Review per-surface in Phase 2",
        "substantive": "**KEEP** — real behavioral coverage",
        "unreadable": "Investigate — read error",
    }
    for bucket in ["mechanical_twin", "near_twin", "broken_assertions", "importorskip_smoke", "substantive", "unreadable"]:
        cnt = bucket_counts.get(bucket, 0)
        lines.append(f"| `{bucket}` | {cnt} | {action_map.get(bucket, '?')} |")
    lines.append("")

    # Twin group rollup
    lines.append("## Twin Groups (mechanical + near)")
    lines.append("")
    if twin_groups:
        lines.append("| Group size | # groups | Example files |")
        lines.append("|---:|---:|---|")
        size_to_count: dict[int, int] = defaultdict(int)
        size_to_example: dict[int, str] = {}
        for key, group in twin_groups.items():
            size = len(group)
            size_to_count[size] += 1
            if size not in size_to_example:
                size_to_example[size] = ", ".join(g["path"] for g in group[:3])
        for size in sorted(size_to_count.keys(), reverse=True):
            lines.append(f"| {size} | {size_to_count[size]} | `{size_to_example[size]}` |")
    else:
        lines.append("_No twin groups detected._")
    lines.append("")

    # Sample: broken_assertions files (first 20)
    broken = [r for r in records if r.get("bucket") == "broken_assertions"]
    if broken:
        lines.append("## Broken-Assertion Files (sample)")
        lines.append("")
        lines.append("These files reference candidate symbols that do NOT exist in the target module.")
        lines.append("")
        lines.append("| File | Missing symbols | Target(s) |")
        lines.append("|---|---|---|")
        for r in broken[:20]:
            missing = ", ".join(r.get("missing_candidates", [])[:5])
            targets = ", ".join(r.get("importorskip_targets", [])[:2])
            lines.append(f"| `{r['path']}` | `{missing}` | `{targets}` |")
        if len(broken) > 20:
            lines.append(f"")
            lines.append(f"_...and {len(broken) - 20} more._")
        lines.append("")

    # Sample: mechanical twin pairs (first 20)
    mech = [r for r in records if r.get("bucket") == "mechanical_twin"]
    seen_groups: set[str] = set()
    if mech:
        lines.append("## Mechanical-Twin Pairs (sample)")
        lines.append("")
        lines.append("Byte-identical files. One of each pair is pure waste.")
        lines.append("")
        lines.append("| Group | Files |")
        lines.append("|---|---|")
        for r in mech:
            key = r.get("twin_group_exact_hash", "?")
            if key in seen_groups:
                continue
            seen_groups.add(key)
            peers = [r["path"]] + r.get("twin_peers", [])
            lines.append(f"| `{key[:12]}...` | `{', '.join(peers)}` |")
            if len(seen_groups) >= 20:
                break
        if len(seen_groups) < sum(1 for _ in twin_groups):
            lines.append(f"")
            lines.append(f"_Showing first 20 groups._")
        lines.append("")

    # Phase 1 scope summary
    lines.append("## Phase 1 Proposed Deletion Scope")
    lines.append("")
    p1_delete = (
        bucket_counts.get("mechanical_twin", 0)
        + bucket_counts.get("broken_assertions", 0)
    )
    p1_review = bucket_counts.get("near_twin", 0)
    lines.append(f"- **Delete without review**: {bucket_counts.get('mechanical_twin', 0)} mechanical_twin + "
                 f"{bucket_counts.get('broken_assertions', 0)} broken_assertions = **{p1_delete}** files")
    lines.append(f"- **Delete after spot-check**: {p1_review} near_twin files")
    lines.append(f"- **Defer to Phase 2 per-surface**: {bucket_counts.get('importorskip_smoke', 0)} importorskip_smoke files")
    lines.append(f"- **Leave alone**: {bucket_counts.get('substantive', 0)} substantive files")
    lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def main() -> int:
    if not TESTS_DIR.is_dir():
        print(f"tests/ not found at {TESTS_DIR}", file=sys.stderr)
        return 1
    # Need agentic_core on sys.path for importlib-based candidate resolution
    repo_str = str(REPO_ROOT)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    all_test_files = [p for p in TESTS_DIR.rglob("test_*.py") if p.is_file()]
    print(f"[info] scanning {len(all_test_files)} test files...", file=sys.stderr)

    records: list[dict[str, Any]] = []
    start = time.monotonic()
    for i, path in enumerate(all_test_files, 1):
        if i % 25 == 0 or i == len(all_test_files):
            _progress(i, len(all_test_files), "classifying", start)
        records.append(classify_file(path))
    _progress(len(all_test_files), len(all_test_files), "classifying", start)

    print(f"[info] assigning twin buckets...", file=sys.stderr)
    assign_twin_buckets(records)

    md_path, json_path = write_reports(records)
    print(f"\nWrote: {md_path}", file=sys.stderr)
    print(f"Wrote: {json_path}", file=sys.stderr)

    # Short summary on stdout
    bucket_counts: dict[str, int] = defaultdict(int)
    for r in records:
        bucket_counts[r.get("bucket", "unreadable")] += 1
    print("\nSummary by bucket:")
    for bucket in ["mechanical_twin", "near_twin", "broken_assertions", "importorskip_smoke", "substantive", "unreadable"]:
        print(f"  {bucket:<22s} {bucket_counts.get(bucket, 0):>6d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
