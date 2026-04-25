"""Two-pass dry-run for Wave/Phase Convergence cleanup.

Pass 1 (rescore): assign P-bands to UNSCORED rows using constitutional formula.
Pass 2 (audit): classify ambiguous rows as LANDED/PARTIAL/MISSING/OBSOLETE.

Outputs (no Notion writes, dry-run only):
  artifacts/notion/_pending_rescore.json
  artifacts/notion/_pending_audit.json
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROWS_PATH = ROOT / "artifacts" / "notion" / "open_rows_with_ids.json"
ADG_PATH = ROOT / "artifacts" / "adg" / "adg_indexed_04242026_0513.sqlite"
HOOKS_JSON = ROOT / ".windsurf" / "hooks.json"
MCP_CFG = ROOT / ".windsurf" / "mcp_config.json"
CONST_RULE = ROOT / ".windsurf" / "rules" / "constitutional.md"
RULES_DIR = ROOT / ".windsurf" / "rules"

LAYER_MULT = {
    "L0": 2.0,
    "L5": 2.0,
    "L3": 1.75,
    "L4": 1.75,
    "L1": 1.0,
    "L2": 1.0,
    "L6": 0.75,
}
SURFACE_BOOST = {
    "Security": 1.5,
    "Write": 1.4,
    "Execution": 1.3,
    "State": 1.2,
    "Observability": 1.1,
    "None": 1.0,
    "": 1.0,
}
SURFACE_FROM_EDGE = {
    "writes_to": "Write",
    "writes_through": "Write",
    "emits_side_effect": "State",
    "reads_from": "State",
    "applies_guardrail": "Security",
    "validates_uwg_intent": "Security",
    "invokes_provider": "Execution",
    "resolves_callsite": "Execution",
    "controls_flow": "Execution",
    "escalates_to_human": "Observability",
    "orchestrates_healing": "Observability",
}

PATH_RE = re.compile(r"[a-zA-Z_][\w/.-]*\.py\b")

# ---- ADG lookups ----------------------------------------------------------


def adg_lookup(conn: sqlite3.Connection, file_rel: str) -> dict:
    """Return layer + fan_in + inferred surface for a file path (relative)."""
    cur = conn.cursor()
    # Find nodes whose adg_name or resolved_path mentions this file
    norm = file_rel.replace("\\", "/")
    cur.execute(
        "SELECT id, adg_name, layer, entity_type FROM nodes "
        "WHERE adg_name LIKE ? OR resolved_path LIKE ? LIMIT 50",
        (f"%{norm}%", f"%{norm}%"),
    )
    matches = cur.fetchall()
    if not matches:
        return {"matched": False}
    # Prefer module/file nodes; pick highest-level node
    layers = {m[2] for m in matches if m[2]}
    layer = ""
    for L in (
        "L0",
        "L5",
        "L3",
        "L4",
        "L1",
        "L2",
        "L6",
        "L_RUNTIME",
        "L_OPS",
        "L_TOOLS",
        "L_APP",
        "L_SHARED",
        "L_SL",
        "L_PG",
        "L_INFRA",
    ):
        if L in layers:
            layer = L
            break

    # Aggregate fan_in: count distinct src_id where dst_id in matched ids and relation=imports
    ids = tuple({m[0] for m in matches})
    placeholders = ",".join("?" * len(ids))
    cur.execute(
        f"SELECT COUNT(DISTINCT src_id) FROM edges "
        f"WHERE dst_id IN ({placeholders}) AND relation_type = 'imports'",
        ids,
    )
    fan_in = cur.fetchone()[0] or 0

    # Surface inference: look at outbound semantic edges from these nodes
    cur.execute(
        f"SELECT relation_type, COUNT(*) FROM edges WHERE src_id IN ({placeholders}) GROUP BY relation_type",
        ids,
    )
    rel_counts = dict(cur.fetchall())
    surface = "None"
    surface_score = 0
    for rel, cnt in rel_counts.items():
        s = SURFACE_FROM_EDGE.get(rel)
        if s and cnt > surface_score:
            surface = s
            surface_score = cnt

    return {
        "matched": True,
        "layer": layer or "L_UNKNOWN",
        "fan_in": int(fan_in),
        "surface": surface,
        "node_count": len(matches),
    }


# ---- Pass 1: Rescore ------------------------------------------------------


def extract_paths(row: dict) -> list[str]:
    blob = " ".join([row.get("title", ""), row.get("blocking", ""), row.get("phase", "")])
    return list(dict.fromkeys(PATH_RE.findall(blob)))


def compute_band(impact: float) -> str:
    if impact >= 300:
        return "P1"
    if impact >= 150:
        return "P2"
    if impact >= 75:
        return "P3"
    if impact >= 30:
        return "P4"
    return "P5"


def has_test_for(file_rel: str) -> bool:
    """Heuristic: is there a test file mirroring this prod file?"""
    if not file_rel.startswith(("agentic_core", "apps_", "ops_scripts", "tools/", "system_learning")):
        return False
    base = Path(file_rel).stem
    if base.startswith("__") or base.startswith("_"):
        return False
    # Search common test mirror locations
    for tdir in ("tests/unit", "tests/integration", "tests"):
        for hit in (ROOT / tdir).rglob(f"test_{base}.py"):
            return True
    return False


def rescore_pass(rows: list[dict], conn: sqlite3.Connection) -> list[dict]:
    out = []
    for r in rows:
        if r["band"] != "UNSCORED":
            continue
        if r["status"] in ("Done", "Descoped"):
            continue
        candidate_paths = extract_paths(r)
        adg_results = []
        layer = ""
        fan_in = 0
        surface = "None"
        for p in candidate_paths[:5]:
            res = adg_lookup(conn, p)
            adg_results.append({"path": p, **res})
            if res.get("matched"):
                if not layer or LAYER_MULT.get(res["layer"], 1.0) > LAYER_MULT.get(layer, 1.0):
                    layer = res["layer"]
                fan_in = max(fan_in, res["fan_in"])
                if SURFACE_BOOST[surface] < SURFACE_BOOST.get(res["surface"], 1.0):
                    surface = res["surface"]

        # Coverage gap heuristic
        if candidate_paths:
            tested = sum(1 for p in candidate_paths if has_test_for(p))
            coverage_gap = (1.0 - tested / max(1, len(candidate_paths))) * 100
        else:
            coverage_gap = 100.0  # no files identified

        layer_mult = LAYER_MULT.get(layer, 1.0)
        from math import log10

        impact = coverage_gap * layer_mult * (1 + log10(1 + fan_in)) * SURFACE_BOOST[surface]

        unscorable = not candidate_paths or not any(a.get("matched") for a in adg_results)
        verdict = {
            "id": r["id"],
            "url": r["url"],
            "wave": r["wave"],
            "phase": r["phase"],
            "title": r["title"][:120],
            "candidate_paths": candidate_paths,
            "adg_matches": adg_results,
            "computed_layer": layer or "(unknown)",
            "computed_fan_in": fan_in,
            "computed_surface": surface,
            "coverage_gap_pct": round(coverage_gap, 1),
            "impact": round(impact, 1) if not unscorable else None,
            "proposed_band": compute_band(impact) if not unscorable else "UNSCORABLE",
            "unscorable_reason": "no file paths in title/blocking, or no ADG match" if unscorable else None,
        }
        out.append(verdict)
    return out


# ---- Pass 2: Audit ambiguous rows ----------------------------------------


def hooks_json_text() -> str:
    if not HOOKS_JSON.exists():
        return ""
    return HOOKS_JSON.read_text(encoding="utf-8")


def constitutional_text() -> str:
    if not CONST_RULE.exists():
        return ""
    return CONST_RULE.read_text(encoding="utf-8")


def violations_log_recent(name_pattern: str, days: int = 30) -> int:
    """Count entries in artifacts/windsurf/*violations*.jsonl matching pattern."""
    folder = ROOT / "artifacts" / "windsurf"
    if not folder.exists():
        return 0
    count = 0
    for p in folder.glob("*violations*.jsonl"):
        if name_pattern.lower() in p.name.lower():
            try:
                count += sum(1 for _ in p.open(encoding="utf-8"))
            except OSError:
                pass
    return count


def audit_hook_gate(phase: str, title: str) -> dict:
    """Audit a hook-gate row (W1 phases 1.1-1.8 or similar)."""
    title_lower = title.lower()
    candidates = re.findall(r"[a-z_]+(?:_gate|_classifier|_audit|_cleanup|_dispatcher)\b", title_lower)
    found_files = []
    for cand in candidates:
        for p in (ROOT / ".windsurf" / "scripts").glob(f"*{cand}*.py"):
            found_files.append(p.name)
    hooks_text = hooks_json_text()
    in_hooks = [f for f in found_files if f in hooks_text]
    return {
        "candidates": candidates,
        "files_on_disk": found_files,
        "in_hooks_json": in_hooks,
        "verdict": "LANDED" if found_files and in_hooks else ("PARTIAL" if found_files else "MISSING"),
    }


def audit_governance_rule(phase: str, title: str) -> dict:
    """Audit a governance/policy row (W2 phases 2.1-2.10)."""
    title_lower = title.lower()
    keywords = re.findall(r"[a-z_-]{5,}", title_lower)
    keywords = [k for k in keywords if k not in {"governance", "rules", "policy", "config", "version"}][:3]
    rules_found = []
    for k in keywords:
        for p in RULES_DIR.glob(f"*{k}*.md"):
            rules_found.append(p.name)
    const_text = constitutional_text()
    referenced = [k for k in keywords if k in const_text.lower()]
    return {
        "keywords": keywords,
        "rules_files_found": rules_found[:5],
        "referenced_in_constitutional": referenced,
        "verdict": "LANDED"
        if rules_found and referenced
        else ("PARTIAL" if rules_found or referenced else "MISSING"),
    }


def audit_graph_edge(phase: str, title: str, conn: sqlite3.Connection) -> dict:
    """Audit a graph-edge row (W9-W13). Check if the proposed edge type exists."""
    title_lower = title.lower()
    # Extract edge-name candidates: snake_case identifiers
    edge_cands = re.findall(r"`?([a-z_]+(?:_to|_from|_through|_into|_edges?))`?", title_lower)
    edge_cands += re.findall(r"\b(reads_secret|hitl_decision|covers|emits)\b", title_lower)
    edge_cands = list(dict.fromkeys(edge_cands))
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT relation_type FROM edges")
    existing = {r[0] for r in cur.fetchall()}
    matched = [e for e in edge_cands if e in existing]
    return {
        "edge_candidates": edge_cands,
        "existing_in_adg": matched,
        "verdict": "LANDED"
        if matched and len(matched) == len(edge_cands)
        else ("PARTIAL" if matched else "MISSING"),
    }


def classify_ambiguous(row: dict) -> str | None:
    """Decide which audit recipe applies to this row, or None to skip."""
    wave = row["wave"]
    phase = row["phase"]
    title = row["title"].lower()
    if wave == "W1" and re.match(r"1\.\d+", phase):
        return "hook_gate"
    if wave == "W2" and re.match(r"2\.\d+", phase):
        return "governance"
    if wave in ("W9", "W10", "W11", "W12", "W13") and "edge" in title:
        return "graph_edge"
    if wave in ("Wave 1", "Wave 2", "Wave 3", "Wave 4"):
        return "filesystem"  # delete/cleanup ops
    return None


def audit_filesystem_op(title: str) -> dict:
    """For Wave 1/2/3/4 cleanup/delete rows — check if target symbols still exist."""
    syms = re.findall(r"`?([a-zA-Z_][a-zA-Z0-9_]+)`?", title)
    common = {"Delete", "Remove", "Clean", "Update", "Run", "files", "the"}
    syms = [s for s in syms if s not in common and len(s) > 4][:3]
    findings = {}
    import subprocess

    for s in syms:
        try:
            r = subprocess.run(
                ["git", "grep", "-l", s, "--", "*.py"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            hits = [ln for ln in r.stdout.splitlines() if "archives/" not in ln and "tools/debug/" not in ln]
            findings[s] = len(hits)
        except (subprocess.TimeoutExpired, OSError):
            findings[s] = -1
    if not findings:
        return {"symbols_checked": [], "verdict": "AMBIGUOUS"}
    if all(c == 0 for c in findings.values()):
        verdict = "LANDED"  # delete ops complete (symbol gone)
    elif all(c > 0 for c in findings.values()):
        verdict = "MISSING"  # symbol still present, work not done
    else:
        verdict = "PARTIAL"
    return {"symbols_checked": findings, "verdict": verdict}


def audit_pass(rows: list[dict], conn: sqlite3.Connection) -> list[dict]:
    out = []
    for r in rows:
        if r["status"] in ("Done", "Descoped"):
            continue
        cat = classify_ambiguous(r)
        if not cat:
            continue
        result = {
            "id": r["id"],
            "url": r["url"],
            "wave": r["wave"],
            "phase": r["phase"],
            "title": r["title"][:120],
            "category": cat,
        }
        if cat == "hook_gate":
            result.update(audit_hook_gate(r["phase"], r["title"]))
        elif cat == "governance":
            result.update(audit_governance_rule(r["phase"], r["title"]))
        elif cat == "graph_edge":
            result.update(audit_graph_edge(r["phase"], r["title"], conn))
        elif cat == "filesystem":
            result.update(audit_filesystem_op(r["title"]))
        out.append(result)
    return out


# ---- Main -----------------------------------------------------------------


def main():
    rows = json.loads(ROWS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(rows)} open rows")

    if not ADG_PATH.exists():
        print(f"FATAL: ADG snapshot missing: {ADG_PATH}", file=sys.stderr)
        return 1
    conn = sqlite3.connect(str(ADG_PATH))

    print("\n--- PASS 1: Rescore UNSCORED ---")
    rescore = rescore_pass(rows, conn)
    print(f"Rescored: {len(rescore)} rows")
    band_counts = {}
    for v in rescore:
        b = v["proposed_band"]
        band_counts[b] = band_counts.get(b, 0) + 1
    for b in sorted(band_counts):
        print(f"  {b}: {band_counts[b]}")
    out1 = ROOT / "artifacts" / "notion" / "_pending_rescore.json"
    out1.write_text(json.dumps(rescore, indent=2), encoding="utf-8")
    print(f"Wrote: {out1}")

    print("\n--- PASS 2: Audit ambiguous ---")
    audit = audit_pass(rows, conn)
    print(f"Audited: {len(audit)} rows")
    verdict_counts = {}
    for v in audit:
        verd = v.get("verdict", "?")
        verdict_counts[verd] = verdict_counts.get(verd, 0) + 1
    for v in sorted(verdict_counts):
        print(f"  {v}: {verdict_counts[v]}")
    out2 = ROOT / "artifacts" / "notion" / "_pending_audit.json"
    out2.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Wrote: {out2}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
