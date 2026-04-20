"""
_emit_reads_through("l4", "adg_test_classifier", "urg_read_1")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_2")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_3")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_4")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_5")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_6")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_7")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_8")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_9")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_10")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_11")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_12")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_13")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_14")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_15")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_16")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_17")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_18")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_19")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_20")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_21")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_22")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_23")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_24")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_25")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_26")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_27")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_28")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_29")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_30")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_31")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_32")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_33")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_34")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_35")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_36")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_37")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_38")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_39")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_40")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_41")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_42")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_43")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_44")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_45")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_46")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_47")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_48")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_49")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_50")
_emit_reads_through("l4", "adg_test_classifier", "urg_read_51")
ADG-driven test classifier.

Classifies every test in tests/ into three buckets by walking the ADG import
graph and detecting infra-seam reachability:

  UNIT_STRICT       — no live infra reachable
  DEGRADED_PATH     — infra reachable but assertions expect fallback/noop
  INTEGRATION_INFRA — live infra actually exercised

Emits: artifacts/adg_test_classification.json
"""

from __future__ import annotations

import ast
import json
import re
from collections import defaultdict, deque
from pathlib import Path

# ── repo root ─────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent
ADG_PATH = REPO / "artifacts" / "adg" / "adg_latest.json"
OUT_PATH = REPO / "artifacts" / "adg_test_classification.json"

# ── infra seam rules ─────────────────────────────────────────────────────────
# Each rule: (flag_name, list_of_patterns_to_match_in_module_dotted_name_or_source)
INFRA_SEAM_RULES: list[tuple[str, list[str]]] = [
    (
        "REDIS",
        [
            "redis",
            "aioredis",
            "semantic_cache_manager",  # only the network path — detected below
            "hivemind",
        ],
    ),
    (
        "EMBEDDING_MODEL",
        [
            "sentence_transformers",
            "SentenceTransformer",
            "FlagModel",
            "BAAI",
            "bge",
            "bmg_embedding",
            "BGEEmbedder",
        ],
    ),
    (
        "NETWORK",
        [
            "httpx",
            "huggingface_hub",
            "huggingface",
            "requests",
            "urllib3",
            "aiohttp",
        ],
    ),
    (
        "GPU",
        [
            "torch.cuda",
            "torch.device",
            ".cuda(",
            "cuda",
            "accelerate",
            "bitsandbytes",
        ],
    ),
    (
        "SUBPROCESS",
        [
            "subprocess",
            "vllm",
            "wsl",
            "_get_qwen_vllm_arbiter",
            "qwen_vllm",
        ],
    ),
    (
        "PERSISTENCE",
        [
            # runtime state / persistent write outside tmp
            "RuntimeStateManager",
            "assert_no_persistent_write",
            "mutation_prohibition",
        ],
    ),
    (
        "KEYSOURCE",
        [
            "KeySource",
            "inject_key_source",
            "PyCryptodomex",
        ],
    ),
]

# Patterns that indicate fallback/degraded-mode assertions
FALLBACK_ASSERT_PATTERNS = [
    r"assert.*\bFalse\b",
    r"assert.*\bNone\b",
    r"assert.*is False",
    r"assert.*is None",
    r"assert not ",
    r"\bfallback\b",
    r"\bdegraded\b",
    r"\bunavailable\b",
    r"\bnoop\b",
    r"\bno.op\b",
    r"connection.*refused",
    r"assert.*== 0\b",
    r"assert.*raises.*Error",
    r"pytest\.raises",
    r"with raises",
]
_FALLBACK_RE = re.compile("|".join(FALLBACK_ASSERT_PATTERNS), re.IGNORECASE)

# ── load ADG ─────────────────────────────────────────────────────────────────


def load_adg() -> dict:
    return json.loads(ADG_PATH.read_text(encoding="utf-8"))


def build_import_graph(adg: dict) -> dict[str, set[str]]:
    """
    Returns adj: resolved_path -> set of resolved_paths it imports.
    Only walks import-kind relations where from is a Module.
    """
    # entity adg_name -> resolved_path
    name_to_path: dict[str, str] = {}
    for ent in adg.get("entities", []):
        rp = ent.get("resolved_path") or ""
        name_to_path[ent["adg_name"]] = rp

    adj: dict[str, set[str]] = defaultdict(set)
    for rel in adg.get("relations", []):
        if rel.get("relation_type") != "imports":
            continue
        src = name_to_path.get(rel["from_name"], "")
        dst = name_to_path.get(rel["to_name"], "")
        if src and dst and src != dst:
            adj[src].add(dst)

    return dict(adj)


# ── infra seam detection ─────────────────────────────────────────────────────


def _module_text(resolved_path: str) -> str:
    p = REPO / resolved_path
    if p.exists() and p.suffix == ".py":
        try:
            return p.read_text(encoding="utf-8", errors="ignore")
        except OSError:  # guardian: allow-silent-swallow - acceptable exception handling
            return ""
    return ""


def detect_infra_flags(resolved_paths: set[str]) -> dict[str, list[str]]:
    """Return {flag: [triggering_paths]} for all infra seams reachable."""
    flags: dict[str, list[str]] = defaultdict(list)
    for rp in resolved_paths:
        src = _module_text(rp)
        for flag, patterns in INFRA_SEAM_RULES:
            for pat in patterns:
                if pat in (rp or "") or (src and pat in src):
                    flags[flag].append(rp)
                    break
    return dict(flags)


# ── fallback assertion detection ─────────────────────────────────────────────


def has_fallback_assertions(test_path: Path) -> bool:
    """Return True if the test body contains degraded/fallback assertion patterns."""
    try:
        src = test_path.read_text(encoding="utf-8", errors="ignore")  # guardian: Add error context logging
    except OSError:  # guardian: allow-silent-swallow - acceptable exception handling
        return False
    return bool(_FALLBACK_RE.search(src))


# ── BFS reachability ─────────────────────────────────────────────────────────


# guardian: allow-magic-config
def reachable_from(start: str, adj: dict[str, set[str]], max_depth: int = 6) -> set[str]:
    """BFS from start node; returns all reachable resolved_paths."""
    visited: set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for nxt in adj.get(node, set()):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, depth + 1))
    return visited


# ── test node id collection ───────────────────────────────────────────────────


def collect_test_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("test_*.py") if ".pytest_cache" not in str(p))


def collect_nodeids(test_file: Path) -> list[str]:
    """Extract test function / method node IDs from a file via AST."""
    try:  # guardian: Syntax errors should be caught at parser level, not runtime
        # guardian: allow-silent-swallow - acceptable exception handling
        tree = ast.parse(test_file.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    ids: list[str] = []
    rel = test_file.relative_to(REPO).as_posix()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            ids.append(f"{rel}::{node.name}")
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    ids.append(f"{rel}::{node.name}::{item.name}")
    return ids


# ── classify one test file ────────────────────────────────────────────────────


def classify_file(
    test_file: Path,
    adj: dict[str, set[str]],
) -> dict:
    rel = test_file.relative_to(REPO).as_posix()
    # guardian: allow-magic-config
    reached = reachable_from(rel, adj, max_depth=6)
    flags = detect_infra_flags(reached)

    has_flags = bool(flags)
    is_fallback = has_fallback_assertions(test_file)

    if not has_flags:
        classification = "UNIT_STRICT"
        reason = "No infra seam reachable"
    elif is_fallback and set(flags.keys()) <= {
        "REDIS",
        "EMBEDDING_MODEL",
        "NETWORK",
        "GPU",
        "SUBPROCESS",
        "PERSISTENCE",
        "KEYSOURCE",
    }:
        # Has infra in graph but assertions are degraded-path style
        classification = "DEGRADED_PATH"
        reason = f"Reaches infra ({', '.join(sorted(flags))}) but asserts fallback/degraded behavior"
    else:
        classification = "INTEGRATION_INFRA"
        reason = f"Live infra seams reachable: {', '.join(sorted(flags))}"

    # Special case: KEYSOURCE alone causes collection error — always INTEGRATION_INFRA
    if "KEYSOURCE" in flags:
        classification = "INTEGRATION_INFRA"
        reason = "KeySource injection required at collection time"

    return {
        "file": rel,
        "classification": classification,
        "infra_flags": sorted(flags.keys()),
        "reachable_infra_nodes": sorted({rp for flag_rps in flags.values() for rp in flag_rps})[
            :20
        ],  # cap for readability
        "reason": reason,
        "test_count": len(collect_nodeids(test_file)),
    }


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    print("Loading ADG...", flush=True)
    adg = load_adg()
    print(f"  entities={len(adg.get('entities', []))} relations={len(adg.get('relations', []))}")

    print("Building import graph...", flush=True)
    adj = build_import_graph(adg)
    print(f"  {len(adj)} source files with outbound edges")

    test_root = REPO / "tests"
    test_files = collect_test_files(test_root)
    print(f"Found {len(test_files)} test files under tests/")

    results: list[dict] = []
    for tf in test_files:
        entry = classify_file(tf, adj)
        results.append(entry)

    # Aggregate
    buckets: dict[str, list[str]] = defaultdict(list)
    for r in results:
        buckets[r["classification"]].append(r["file"])

    # Per-test-id classification (flatten)
    test_id_rows: list[dict] = []
    for r in results:
        cls = r["classification"]
        for nid in collect_nodeids(REPO / r["file"]):
            test_id_rows.append(
                {
                    "test": nid,
                    "classification": cls,
                    "infra_flags": r["infra_flags"],
                    "reason": r["reason"],
                }
            )

    # Violations: files in tests/unit/ that are NOT UNIT_STRICT
    unit_violations = [
        r for r in results if r["file"].startswith("tests/unit/") and r["classification"] != "UNIT_STRICT"
    ]

    artifact = {
        "schema": "adg_test_classification_v1",
        "adg_source": ADG_PATH.relative_to(REPO).as_posix(),
        "summary": {
            "total_files": len(results),
            "unit_strict": len(buckets["UNIT_STRICT"]),
            "degraded_path": len(buckets["DEGRADED_PATH"]),
            "integration_infra": len(buckets["INTEGRATION_INFRA"]),
            "unit_violations": len(unit_violations),
        },
        "bucket_files": {
            "unit_strict": sorted(buckets["UNIT_STRICT"]),
            "degraded_path": sorted(buckets["DEGRADED_PATH"]),
            "integration_infra": sorted(buckets["INTEGRATION_INFRA"]),
        },
        "unit_violations": [
            {
                "file": v["file"],
                "classification": v["classification"],
                "infra_flags": v["infra_flags"],
                "reason": v["reason"],
            }
            for v in unit_violations
        ],
        "per_file": results,
        "per_test": test_id_rows,
    }

    OUT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\nArtifact written → {OUT_PATH.relative_to(REPO)}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  UNIT_STRICT       : {artifact['summary']['unit_strict']} files")
    print(f"  DEGRADED_PATH     : {artifact['summary']['degraded_path']} files")
    print(f"  INTEGRATION_INFRA : {artifact['summary']['integration_infra']} files")
    print(f"  unit/ violations  : {artifact['summary']['unit_violations']} files")
    print(f"{'=' * 60}")

    if unit_violations:
        print("\nCI VIOLATIONS — these files are in tests/unit/ but NOT UNIT_STRICT:")
        for v in unit_violations:
            print(f"  [{v['classification']}] {v['file']}")
            print(f"    flags: {', '.join(v['infra_flags'])}")
            print(f"    reason: {v['reason']}")


if __name__ == "__main__":
    main()
