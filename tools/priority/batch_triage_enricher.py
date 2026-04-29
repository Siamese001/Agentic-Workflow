#!/usr/bin/env python3
"""
batch_triage_enricher.py — Auto-enrich the 55 manual-triage rows.

Strategy: regex-infer Layer + Surface + Fan-In + Coverage Gap from row title +
blocking-items text. Conservative defaults — fan_in=1, coverage_gap=100.0,
explicit-count extraction when title mentions "N rows" / "N violations".
Every enrichment is recorded in audit log so a human can review.

Usage:
    python tools/priority/batch_triage_enricher.py             # dry-run
    python tools/priority/batch_triage_enricher.py --apply     # patch Notion
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.priority.deferred_scope_scorer import score_deferred_scope  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"

TRIAGE_CSV = REPO_ROOT / "docs" / "reports" / "maintenance" / "unscored_manual_triage.csv"
ENRICHED_CSV = REPO_ROOT / "docs" / "reports" / "maintenance" / "unscored_enriched.csv"
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "notion_triage_enrichment_audit.jsonl"

# Layer inference: ordered priority — first match wins
LAYER_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bL([0-6])\b"), r"L\1"),  # captures L0..L6 literally
    (re.compile(r"\b(router|routing|dispatch|namespace[_ ]bandit|path[_ ]router)\b", re.I), "L0"),
    (re.compile(r"\b(cognition|reasoning|context[_ ]engine|prompt[_ ]assembly)\b", re.I), "L1"),
    (re.compile(r"\b(execution|orchestrator|exec[_ ]agent|sovereign[_ ]agent)\b", re.I), "L2"),
    (re.compile(r"\b(handoff|step[_ ]checkpoint|workflow[_ ]graph)\b", re.I), "L3"),
    (re.compile(r"\b(memory|UWG|durable|state[_ ]write|cache|canonical[_ ]store|checkpoint)\b", re.I), "L4"),
    (re.compile(r"\b(safety|guardrail|HITL|policy|exit[_ ]control|approval[_ ]gate|injection|firewall)\b", re.I), "L5"),
    (re.compile(r"\b(observability|trace|telemetry|OTEL|ADG|graph[_ -]layer|metric|span)\b", re.I), "L6"),
    (re.compile(r"\b(gate|CI|baseline|burndown|ratchet|pre[_-]commit|wiring[_ ]gate)\b", re.I), "L_OPS"),
    (re.compile(r"\b(test|harness|coverage|pytest|adg[_ ]test)\b", re.I), "L_TOOLS"),
    (re.compile(r"\b(scoring|wave|backlog|score[_ ]row)\b", re.I), "L_OPS"),
]

SURFACE_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(security|guardrail|HITL|injection|firewall|safety|exemption)\b", re.I), "Security"),
    (re.compile(r"\b(write|UWG|commit|durable|state[_ -]write|writes[_ ]through)\b", re.I), "Write"),
    (re.compile(r"\b(execution|orchestrator|dispatch|exec|raw[_ ]execution)\b", re.I), "Execution"),
    (re.compile(r"\b(memory|cache|state|canonical[_ ]store|index|materialized[_ ]view)\b", re.I), "State"),
    (re.compile(r"\b(trace|telemetry|OTEL|ADG|graph[_ -]layer|metric|span|observability)\b", re.I), "Observability"),
]

# Extract numeric counts: "22 governance rows", "17 cross-layer breaches", "153 undeclared env flags"
COUNT_RE = re.compile(r"\b(\d{1,4})\s+(?:rows?|violations?|breaches?|flags?|leaks?|files?|gaps?|exemptions?|sites?)\b", re.I)


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
                return result
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 2:
                time.sleep(int(err.headers.get("Retry-After", "2")))
                continue
            body_txt = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {body_txt}") from err
        except urllib.error.URLError as err:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error: {err}") from err
    raise RuntimeError(f"Exhausted retries: {method} {url}")


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def infer_layer(text: str) -> str:
    for pat, layer in LAYER_RULES:
        m = pat.search(text)
        if m:
            # Handle the L\d capture group case
            try:
                return m.expand(layer) if "\\" in layer else layer
            except (re.error, IndexError):
                return layer
    return "L_OPS"  # default


def infer_surface(text: str) -> str:
    for pat, surface in SURFACE_RULES:
        if pat.search(text):
            return surface
    return "None"  # neutral default


def infer_fan_in(text: str) -> int:
    m = COUNT_RE.search(text)
    if m:
        return min(int(m.group(1)), 100)  # cap at 100 to avoid skew
    return 1


def fetch_row_blocking_items(tok: str, page_id: str) -> str:
    """Fetch the row's Blocking Items text for richer inference."""
    try:
        page = _http("GET", f"{NOTION_API}/pages/{page_id}", tok)
        blocking = page.get("properties", {}).get("Blocking Items", {}).get("rich_text", [])
        return " ".join(p.get("plain_text", "") for p in blocking)
    except RuntimeError:
        return ""


def patch_row(tok: str, page_id: str, layer: str, surface: str, fan_in: int, cov_gap: float, band: str, new_title: str, dry_run: bool) -> None:
    if dry_run:
        return
    props: dict[str, Any] = {
        "Phase Title": {"title": [{"text": {"content": new_title}}]},
        "P-Band": {"select": {"name": band}},
        "Layer": {"select": {"name": layer}},
        "Surface": {"select": {"name": surface}},
        "Fan-In": {"number": fan_in},
        "Coverage Gap %": {"number": cov_gap},
    }
    _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, {"properties": props})


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-enrich UNSCORED triage rows")
    parser.add_argument("--apply", action="store_true", help="Patch Notion (default: dry-run)")
    parser.add_argument("--with-blocking", action="store_true", help="Fetch each row's Blocking Items text for richer inference (slower)")
    args = parser.parse_args()

    dry_run = not args.apply
    tok = _token()

    if not TRIAGE_CSV.exists():
        print(f"ERROR: {TRIAGE_CSV} not found. Run batch_rescore_notion.py first.", file=sys.stderr)
        return 1

    rows = list(csv.DictReader(TRIAGE_CSV.open(encoding="utf-8")))
    enriched: list[dict] = []
    band_counts: dict[str, int] = {}

    for row in rows:
        page_id = row["page_id"]
        title = row["title"]
        text = title
        if args.with_blocking:
            text = title + " " + fetch_row_blocking_items(tok, page_id)

        layer = infer_layer(text)
        surface = infer_surface(text)
        fan_in = infer_fan_in(text)
        cov_gap = 100.0  # sensible default for backlog items

        result = score_deferred_scope(
            layer=layer, fan_in=fan_in, surface=surface, coverage_gap_pct=cov_gap,
        )
        band = str(result.band)
        band_counts[band] = band_counts.get(band, 0) + 1

        new_title = f"[{band}] {title}" if not title.startswith("[") else title

        enriched.append({
            "page_id": page_id,
            "title": title,
            "inferred_layer": layer,
            "inferred_surface": surface,
            "inferred_fan_in": fan_in,
            "coverage_gap_pct": cov_gap,
            "band": band,
            "impact_score": result.impact_score,
            "new_title": new_title,
        })

        patch_row(tok, page_id, layer, surface, fan_in, cov_gap, band, new_title, dry_run)

    # Write enriched CSV
    ENRICHED_CSV.parent.mkdir(parents=True, exist_ok=True)
    with ENRICHED_CSV.open("w", encoding="utf-8", newline="") as fh:
        if enriched:
            writer = csv.DictWriter(fh, fieldnames=list(enriched[0].keys()))
            writer.writeheader()
            writer.writerows(enriched)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run" if dry_run else "apply",
        "rows_enriched": len(enriched),
        "band_distribution": band_counts,
        "enriched_csv": str(ENRICHED_CSV.relative_to(REPO_ROOT)),
    }
    _audit(summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
