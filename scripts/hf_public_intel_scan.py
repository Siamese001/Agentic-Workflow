#!/usr/bin/env python3
"""Pull public Hugging Face signal into the Agentic-Workflow repo.

This script intentionally uses public Hugging Face metadata only. It does not
require an HF token and does not download model weights or datasets.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterable

import requests
from dateutil import parser as dateparser
from huggingface_hub import HfApi


SCAN_DAYS = int(os.getenv("SCAN_DAYS", "7"))
TOP_N = int(os.getenv("TOP_N", "10"))
NOW = datetime.now(timezone.utc)
RUN_DATE = NOW.date().isoformat()
CUTOFF = NOW - timedelta(days=SCAN_DAYS)

OUT_JSON_LATEST = Path("data/huggingface/latest_agentic_public_signal.json")
OUT_JSON_ARCHIVE = Path(f"data/huggingface/archive/{RUN_DATE}.json")
OUT_MD_LATEST = Path("docs/intelligence/huggingface/latest_agentic_public_signal.md")
OUT_MD_ARCHIVE = Path(f"docs/intelligence/huggingface/archive/{RUN_DATE}.md")

SEARCH_TERMS = [
    "agentic",
    "ai agents",
    "autonomous agents",
    "agent workflow",
    "tool use",
    "function calling",
    "multi-agent",
    "llm evaluation",
    "evals",
    "rag evaluation",
    "guardrails",
    "governance",
    "observability",
    "red teaming",
    "enterprise ai",
]

DEPLOYMENT_KEYWORDS = [
    "agent",
    "agentic",
    "tool",
    "function",
    "workflow",
    "orchestration",
    "multi-agent",
    "eval",
    "evaluation",
    "benchmark",
    "reliability",
    "monitor",
    "monitoring",
    "observability",
    "guardrail",
    "governance",
    "risk",
    "compliance",
    "audit",
    "red team",
    "safety",
    "rag",
    "retrieval",
    "provenance",
    "trace",
    "replay",
]

CONTROL_PLANE_MAP = {
    "route_authority": {
        "terms": ["workflow", "orchestration", "agent", "multi-agent"],
        "repo_surface": "L0 routing / L3 orchestration",
        "question": "Does this create or clarify bounded route authority rather than model-led control flow?",
    },
    "programmatic_tool_calling": {
        "terms": ["tool", "function", "schema"],
        "repo_surface": "Programmatic Tool Calling / L2 execution",
        "question": "Does this strengthen schema-enforced tool use or expose unsafe free-form action patterns?",
    },
    "context_grounding": {
        "terms": ["rag", "retrieval", "provenance"],
        "repo_surface": "C0 context / RAG evaluation / Final Evidence Contract",
        "question": "Does this improve retrieval grounding, provenance, or evidence sufficiency checks?",
    },
    "exit_evaluation": {
        "terms": ["eval", "evaluation", "benchmark", "red team", "safety"],
        "repo_surface": "apps_eval / Exit pipeline / L6 observability",
        "question": "Can this become an eval fixture, adversarial case, benchmark adapter, or shadow-eval input?",
    },
    "governance_audit": {
        "terms": ["governance", "risk", "compliance", "audit", "trace", "replay"],
        "repo_surface": "L5 safety / L7 auditability / signed proof bundles",
        "question": "Does this support policy evidence, replayability, audit trace, or compliance controls?",
    },
    "runtime_observability": {
        "terms": ["monitor", "monitoring", "observability", "reliability"],
        "repo_surface": "L6 observer / telemetry / promotion gates",
        "question": "Does this expose measurable failure modes, telemetry hooks, or promotion-gate evidence?",
    },
}


@dataclass
class SignalItem:
    kind: str
    identifier: str
    title: str
    url: str
    summary: str
    tags: list[str]
    last_modified: str | None
    likes: int
    downloads: int
    matched_terms: list[str]
    matched_keywords: list[str]
    repo_surfaces: list[str]
    integration_questions: list[str]
    score: float
    fingerprint: str


def parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        parsed = dateparser.parse(str(value))
    except Exception:
        return None
    if parsed is None:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def clean(text: Any, limit: int = 280) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


def normalize_tags(tags: Iterable[Any] | None) -> list[str]:
    if not tags:
        return []
    return sorted({clean(tag, 80) for tag in tags if str(tag or "").strip()})[:20]


def score_keywords(text: str) -> tuple[int, list[str]]:
    low = text.lower()
    hits: list[str] = []
    score = 0
    for keyword in DEPLOYMENT_KEYWORDS:
        if keyword in low:
            hits.append(keyword)
            if keyword in {"eval", "evaluation", "benchmark", "governance", "audit", "observability", "reliability", "replay"}:
                score += 4
            else:
                score += 2
    return score, sorted(set(hits))


def map_to_repo_surfaces(text: str) -> tuple[list[str], list[str]]:
    low = text.lower()
    surfaces: list[str] = []
    questions: list[str] = []
    for mapping in CONTROL_PLANE_MAP.values():
        if any(term in low for term in mapping["terms"]):
            surfaces.append(mapping["repo_surface"])
            questions.append(mapping["question"])
    return sorted(set(surfaces)), sorted(set(questions))


def fingerprint(kind: str, identifier: str, title: str) -> str:
    raw = f"{kind}|{identifier}|{title}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def build_item(
    *,
    kind: str,
    identifier: str | None,
    title: str | None,
    url: str | None,
    summary: str = "",
    tags: Iterable[Any] | None = None,
    last_modified: Any = None,
    likes: Any = 0,
    downloads: Any = 0,
    source_term: str = "",
) -> SignalItem | None:
    if not identifier:
        return None

    norm_tags = normalize_tags(tags)
    combined = " ".join([title or "", summary or "", " ".join(norm_tags), source_term])
    keyword_score, keyword_hits = score_keywords(combined)
    if keyword_score == 0:
        return None

    parsed_date = parse_dt(last_modified)
    is_recent = parsed_date is None or parsed_date >= CUTOFF

    try:
        likes_i = int(likes or 0)
    except Exception:
        likes_i = 0
    try:
        downloads_i = int(downloads or 0)
    except Exception:
        downloads_i = 0

    recency_bonus = 10 if is_recent else 0
    engagement_bonus = math.log1p(likes_i) + 0.25 * math.log1p(downloads_i)
    score = keyword_score + recency_bonus + engagement_bonus

    surfaces, questions = map_to_repo_surfaces(combined)

    return SignalItem(
        kind=kind,
        identifier=identifier,
        title=clean(title or identifier, 180),
        url=url or "",
        summary=clean(summary, 320),
        tags=norm_tags,
        last_modified=parsed_date.isoformat() if parsed_date else None,
        likes=likes_i,
        downloads=downloads_i,
        matched_terms=sorted({source_term} if source_term else set()),
        matched_keywords=keyword_hits,
        repo_surfaces=surfaces,
        integration_questions=questions,
        score=round(score, 4),
        fingerprint=fingerprint(kind, identifier, title or identifier),
    )


def merge_item(items: dict[str, SignalItem], item: SignalItem | None) -> None:
    if item is None:
        return
    key = f"{item.kind}:{item.identifier}"
    existing = items.get(key)
    if existing is None:
        items[key] = item
        return

    merged_terms = sorted(set(existing.matched_terms + item.matched_terms))
    merged_keywords = sorted(set(existing.matched_keywords + item.matched_keywords))
    merged_surfaces = sorted(set(existing.repo_surfaces + item.repo_surfaces))
    merged_questions = sorted(set(existing.integration_questions + item.integration_questions))

    if item.score > existing.score:
        winner = item
    else:
        winner = existing

    winner.matched_terms = merged_terms
    winner.matched_keywords = merged_keywords
    winner.repo_surfaces = merged_surfaces
    winner.integration_questions = merged_questions
    winner.score = max(existing.score, item.score)
    items[key] = winner


def safe_list(callable_obj: Any, **kwargs: Any) -> list[Any]:
    attempts = [
        kwargs,
        {k: v for k, v in kwargs.items() if k not in {"sort", "direction"}},
        {"search": kwargs.get("search"), "limit": kwargs.get("limit")},
    ]
    for attempt in attempts:
        cleaned = {k: v for k, v in attempt.items() if v is not None}
        try:
            return list(callable_obj(**cleaned))
        except Exception:
            continue
    return []


def scan_hub(items: dict[str, SignalItem]) -> None:
    api = HfApi()

    for term in SEARCH_TERMS:
        for model in safe_list(api.list_models, search=term, sort="lastModified", direction=-1, limit=16):
            model_id = getattr(model, "modelId", None) or getattr(model, "id", None)
            tags = list(getattr(model, "tags", None) or [])
            summary = " ".join([str(getattr(model, "pipeline_tag", "") or ""), " ".join(tags[:10])])
            merge_item(
                items,
                build_item(
                    kind="model",
                    identifier=model_id,
                    title=model_id,
                    url=f"https://huggingface.co/{model_id}" if model_id else "",
                    summary=summary,
                    tags=tags,
                    last_modified=getattr(model, "last_modified", None) or getattr(model, "created_at", None),
                    likes=getattr(model, "likes", 0),
                    downloads=getattr(model, "downloads", 0),
                    source_term=term,
                ),
            )

        for dataset in safe_list(api.list_datasets, search=term, sort="lastModified", direction=-1, limit=16):
            dataset_id = getattr(dataset, "id", None)
            tags = list(getattr(dataset, "tags", None) or [])
            merge_item(
                items,
                build_item(
                    kind="dataset",
                    identifier=dataset_id,
                    title=dataset_id,
                    url=f"https://huggingface.co/datasets/{dataset_id}" if dataset_id else "",
                    summary=" ".join(tags[:12]),
                    tags=tags,
                    last_modified=getattr(dataset, "last_modified", None) or getattr(dataset, "created_at", None),
                    likes=getattr(dataset, "likes", 0),
                    downloads=getattr(dataset, "downloads", 0),
                    source_term=term,
                ),
            )

        if hasattr(api, "list_spaces"):
            for space in safe_list(api.list_spaces, search=term, sort="lastModified", direction=-1, limit=10):
                space_id = getattr(space, "id", None)
                tags = list(getattr(space, "tags", None) or [])
                summary = " ".join([str(getattr(space, "sdk", "") or ""), " ".join(tags[:10])])
                merge_item(
                    items,
                    build_item(
                        kind="space",
                        identifier=space_id,
                        title=space_id,
                        url=f"https://huggingface.co/spaces/{space_id}" if space_id else "",
                        summary=summary,
                        tags=tags,
                        last_modified=getattr(space, "last_modified", None) or getattr(space, "created_at", None),
                        likes=getattr(space, "likes", 0),
                        downloads=0,
                        source_term=term,
                    ),
                )


def scan_daily_papers(items: dict[str, SignalItem]) -> None:
    session = requests.Session()
    seen: set[str] = set()

    for offset in range(SCAN_DAYS):
        day = (NOW - timedelta(days=offset)).date().isoformat()
        candidate_urls = [
            f"https://huggingface.co/api/daily_papers?date={day}",
            f"https://huggingface.co/api/daily-papers?date={day}",
        ]

        for api_url in candidate_urls:
            try:
                response = session.get(api_url, timeout=20)
                if response.status_code != 200:
                    continue
                payload = response.json()
            except Exception:
                continue

            rows = (
                payload.get("papers")
                or payload.get("dailyPapers")
                or payload.get("data")
                or []
                if isinstance(payload, dict)
                else payload
            )

            if not rows:
                continue

            for row in rows:
                paper = row.get("paper", row) if isinstance(row, dict) else {}
                if not isinstance(paper, dict):
                    continue

                paper_id = paper.get("id") or paper.get("paperId") or paper.get("arxivId") or paper.get("url")
                if not paper_id or paper_id in seen:
                    continue
                seen.add(paper_id)

                title = paper.get("title") or (row.get("title") if isinstance(row, dict) else None) or paper_id
                summary = (
                    paper.get("summary")
                    or paper.get("abstract")
                    or (row.get("summary") if isinstance(row, dict) else "")
                    or ""
                )
                url = paper.get("url") or f"https://huggingface.co/papers/{paper_id}"
                published = (
                    paper.get("publishedAt")
                    or paper.get("published_at")
                    or (row.get("date") if isinstance(row, dict) else None)
                    or day
                )
                likes = row.get("likes", 0) if isinstance(row, dict) else 0

                merge_item(
                    items,
                    build_item(
                        kind="paper",
                        identifier=str(paper_id),
                        title=str(title),
                        url=str(url),
                        summary=str(summary),
                        tags=[],
                        last_modified=published,
                        likes=likes,
                        downloads=0,
                        source_term="daily papers",
                    ),
                )
            break


def rank_items(items: dict[str, SignalItem]) -> list[SignalItem]:
    return sorted(items.values(), key=lambda item: item.score, reverse=True)[:TOP_N]


def markdown_report(ranked: list[SignalItem]) -> str:
    lines: list[str] = [
        "# Hugging Face Public Signal — Agentic AI / Evals / Governance",
        "",
        f"Generated: `{NOW.isoformat()}`",
        f"Lookback window: `{SCAN_DAYS}` days",
        f"Items retained: `{len(ranked)}`",
        "",
        "> This file is generated from public Hugging Face metadata. It is a triage queue, not an endorsement.",
        "",
        "## Why this belongs in Agentic-Workflow",
        "",
        "The repo position is that enterprise agentic AI needs governed runtime control: route authority, verified context, bounded execution, runtime gates, single-door writes, replay, and auditability. This weekly pull adds outside-market signal that can be reviewed for eval fixtures, observability hooks, governance evidence, and runtime-control patterns.",
        "",
        "## Ranked signal",
        "",
    ]

    if not ranked:
        lines.extend(
            [
                "No matching public Hugging Face items were found for this run.",
                "",
                "Consider widening `SEARCH_TERMS` or increasing `SCAN_DAYS`.",
                "",
            ]
        )
        return "\n".join(lines)

    for index, item in enumerate(ranked, start=1):
        lines.extend(
            [
                f"### {index}. {item.title}",
                "",
                f"- **Type:** `{item.kind}`",
                f"- **Source:** {item.url}",
                f"- **Last modified / published:** `{item.last_modified or 'unknown'}`",
                f"- **Score:** `{item.score}`",
                f"- **Matched search terms:** {', '.join(f'`{term}`' for term in item.matched_terms) or '`n/a`'}",
                f"- **Matched keywords:** {', '.join(f'`{kw}`' for kw in item.matched_keywords) or '`n/a`'}",
                f"- **Repo surfaces:** {', '.join(f'`{surface}`' for surface in item.repo_surfaces) or '`review manually`'}",
            ]
        )
        if item.summary:
            lines.append(f"- **Signal:** {item.summary}")
        if item.integration_questions:
            lines.append("- **Integration questions:**")
            for question in item.integration_questions[:5]:
                lines.append(f"  - {question}")
        lines.append("")

    lines.extend(
        [
            "## Recommended review flow",
            "",
            "1. Triage any `apps_eval`, L6 observability, or L7 auditability candidates first.",
            "2. Convert strong datasets/papers into eval fixtures or benchmark adapters only after checking licensing and provenance.",
            "3. Promote only artifacts that improve deterministic replay, exit evaluation, governance evidence, or runtime control.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(ranked: list[SignalItem]) -> None:
    payload = {
        "generated_at": NOW.isoformat(),
        "lookback_days": SCAN_DAYS,
        "top_n": TOP_N,
        "search_terms": SEARCH_TERMS,
        "items": [asdict(item) for item in ranked],
    }
    md = markdown_report(ranked)

    for path in [OUT_JSON_LATEST, OUT_JSON_ARCHIVE, OUT_MD_LATEST, OUT_MD_ARCHIVE]:
        path.parent.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    OUT_JSON_LATEST.write_text(json_text, encoding="utf-8")
    OUT_JSON_ARCHIVE.write_text(json_text, encoding="utf-8")
    OUT_MD_LATEST.write_text(md, encoding="utf-8")
    OUT_MD_ARCHIVE.write_text(md, encoding="utf-8")


def main() -> None:
    items: dict[str, SignalItem] = {}
    scan_hub(items)
    scan_daily_papers(items)
    ranked = rank_items(items)
    write_outputs(ranked)

    print(f"Wrote {len(ranked)} Hugging Face public signal items.")
    print(f"- {OUT_MD_LATEST}")
    print(f"- {OUT_JSON_LATEST}")
    print(f"- {OUT_MD_ARCHIVE}")
    print(f"- {OUT_JSON_ARCHIVE}")


if __name__ == "__main__":
    main()
