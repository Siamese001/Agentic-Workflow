"""Emit ResearchBriefEnvelope sidecar for apps_research artifacts.

Plan: apps-cross-app-precursors-c94c71 Wave 3.2 (GAP-3).

Dual-write: research_brief_<trace>.md + source_register_<trace>.json are
untouched; a sibling research_brief_<trace>.envelope.json is produced.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from apps_shared.contracts.cross_app.research_brief import (
    ResearchBriefEnvelope,
    ResearchBriefPayload,
    ResearchClaimRow,
)

_DEFAULT_RESEARCH_DIR = Path("artifacts/apps_research")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)


def _section(brief_text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$\n?(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(brief_text)
    return m.group(1).strip() if m else ""


def _bullets(text: str) -> list[str]:
    return [m.group(1).strip() for m in _BULLET_RE.finditer(text)]


def _claims_from_register(rows: list[dict]) -> list[ResearchClaimRow]:
    out: list[ResearchClaimRow] = []
    for row in rows:
        claim = row.get("summary") or row.get("title") or ""
        if not claim:
            continue
        ct = row.get("claim_type", "direct_evidence")
        if ct not in {
            "direct_evidence",
            "interpretation",
            "analyst_inference",
            "assumption",
        }:
            ct = "analyst_inference"
        out.append(
            ResearchClaimRow(
                claim=claim,
                claim_type=ct,  # type: ignore[arg-type]
                source_id=row.get("source_id", "SRC-000"),
                section_id=row.get("section_id", ""),
            )
        )
    return out


def build_payload(brief_path: Path, register_path: Path | None) -> ResearchBriefPayload:
    brief_text = brief_path.read_text(encoding="utf-8")
    company_brief = _section(brief_text, "Executive Summary") or brief_text[:2000]
    role_areas = _bullets(_section(brief_text, "Key Findings"))
    industry_trends = _bullets(_section(brief_text, "Strategic Implications"))

    source_register: list[ResearchClaimRow] = []
    if register_path and register_path.is_file():
        try:
            rows = json.loads(register_path.read_text(encoding="utf-8"))
            if isinstance(rows, list):
                source_register = _claims_from_register(rows)
        except json.JSONDecodeError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass

    return ResearchBriefPayload(
        brief_path=str(brief_path).replace("\\", "/"),
        register_path=(
            str(register_path).replace("\\", "/") if register_path else None
        ),
        company_brief=company_brief.strip() or None,
        role_areas_of_focus=role_areas,
        industry_trends=industry_trends,
        source_register=source_register,
    )


def emit(
    *,
    trace_id: str,
    research_dir: Path | None = None,
    out_path: Path | None = None,
) -> Path:
    research_dir = research_dir or _DEFAULT_RESEARCH_DIR
    brief_path = research_dir / f"research_brief_{trace_id}.md"
    register_path = research_dir / f"source_register_{trace_id}.json"
    if not brief_path.is_file():
        raise FileNotFoundError(f"Research brief not found: {brief_path}")

    payload = build_payload(brief_path, register_path)
    env = ResearchBriefEnvelope.emit(trace_id=trace_id, payload=payload)
    if out_path is None:
        out_path = env.default_sidecar_path(research_dir)
    env.write_sidecar(out_path)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--research-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    written = emit(
        trace_id=args.trace_id,
        research_dir=args.research_dir,
        out_path=args.out,
    )
    print(f"Wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
