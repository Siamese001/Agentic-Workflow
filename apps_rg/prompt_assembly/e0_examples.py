"""Hydrate E0 (approved examples) from section examples YAML — compile-time SSOT.

BOM ``section_example_authority`` maps sections to ``apps_rg/prompt_assembly/examples/*.yaml``.
Runtime ``*_pa.py`` modules call :func:`resolve_e0_for_section` instead of inline template stubs.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_PA_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _PA_ROOT.parent.parent

SECTION_EXAMPLES: dict[str, str] = {
    "executive_summary": "apps_rg/prompt_assembly/examples/executive_summary_examples.yaml",
    "competencies": "apps_rg/prompt_assembly/examples/competencies_examples.yaml",
    "unify": "apps_rg/prompt_assembly/examples/unify_examples.yaml",
}

# Lanes that share the unify examples catalog.
_UNIFY_LANE_SECTIONS = frozenset({"unify_bullets", "unify_narrative"})

# SVP strategy lane: two structurally diverse positives (thesis-arc + credibility-implied).
# Providing two avoids the single-example template-following trap where Qwen echoes metric
# values verbatim from the sole positive. Both examples use domain-transposed or abstract
# metrics — Qwen must retrieve real values from C0.
_EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED = (
    "exec_summary_pos_svp_it_strategy_001",
    "exec_summary_pos_credibility_implied_001",
)

_EXEC_SUMMARY_POSITIVE_COMPILE_IDS = (
    "exec_summary_pos_svp_it_strategy_001",
    "exec_summary_pos_credibility_implied_001",
    "exec_summary_pos_outcomes_led_001",
)

# Retired from default E0 compile: none currently (exec_summary_gold_base_resume_001
# is now category=negative so is handled by the negative-render path, not this list).
_EXEC_SUMMARY_POSITIVE_RETIRED_FROM_COMPILE: tuple[str, ...] = ()

_EXEC_SUMMARY_TEMPLATE_SUPPLEMENT = (
    _PA_ROOT / "templates" / "executive_summary.generate_scratch_v1.yaml"
)


def _examples_path(section: str) -> Path | None:
    key = section
    if section in _UNIFY_LANE_SECTIONS:
        key = "unify"
    rel = SECTION_EXAMPLES.get(key)
    if not rel:
        return None
    path = _REPO_ROOT / Path(rel)
    return path if path.is_file() else None


@lru_cache(maxsize=8)
def load_examples_by_id(section: str) -> dict[str, dict[str, Any]]:
    path = _examples_path(section)
    if path is None:
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = raw.get("examples") if isinstance(raw, dict) else []
    return {
        str(row["id"]): row
        for row in (rows or [])
        if isinstance(row, dict) and row.get("id")
    }


def example_after_text(section: str, example_id: str) -> str:
    """Return ``after`` prose for an example id (style-only; not proof)."""
    row = load_examples_by_id(section).get(example_id) or {}
    return str(row.get("after") or "").strip()


def _category_kind(category: str) -> str:
    cat = (category or "").lower()
    if cat.startswith("positive") or cat == "positive":
        return "positive"
    if cat == "negative":
        return "negative"
    if cat == "repair":
        return "repair"
    return "other"


def _render_positive_example(row: dict[str, Any]) -> str:
    eid = str(row.get("id") or "")
    authority = str(row.get("authority") or "E0_STYLE_EXAMPLE_NOT_PROOF")
    after = str(row.get("after") or "").strip()
    annotation = str(row.get("annotation") or "").strip()
    lines = [
        f'<positive_example id="{eid}" authority="{authority}">',
        "STYLE_EXAMPLE_NOT_PROOF - density and synthesis register only.",
        after,
    ]
    if annotation:
        lines.append(f"Note: {annotation.split(chr(10))[0].strip()}")
    lines.append("</positive_example>")
    return "\n".join(lines)


def _render_negative_example(row: dict[str, Any]) -> str:
    eid = str(row.get("id") or "")
    after = str(row.get("after") or "").strip()
    annotation = str(row.get("annotation") or "").strip()
    why = annotation.split("\n")[0].strip() if annotation else "See PRODUCT_SHAPE style gates."
    if "VIOLATION:" in why:
        why = why.replace("VIOLATION:", "Why bad:", 1).strip()
    return (
        f'<negative_example id="{eid}">\n'
        f"Bad pattern:\n{after}\n"
        f"Why bad: {why}\n"
        f"</negative_example>"
    )


def _render_repair_example(row: dict[str, Any]) -> str:
    eid = str(row.get("id") or "")
    before = str(row.get("before") or "").strip()
    after = str(row.get("after") or "").strip()
    return (
        f'<repair_example id="{eid}">\n'
        f"Before:\n{before}\n\n"
        f"After:\n{after}\n"
        f"</repair_example>"
    )


def _render_competencies_style_block(rows: list[dict[str, Any]]) -> str:
    parts = ["<examples>"]
    for row in rows:
        eid = str(row.get("id") or "")
        cat = str(row.get("category") or "")
        after = str(row.get("after") or "").strip()
        parts.append(f'<example id="{eid}" category="{cat}">')
        parts.append(after)
        ann = str(row.get("annotation") or "").strip()
        if ann:
            parts.append(f"<!-- {ann.split(chr(10))[0].strip()} -->")
        parts.append("</example>")
    parts.append("</examples>")
    return "\n".join(parts)


def _extract_template_supplement_blocks(template_path: Path, tags: tuple[str, ...]) -> str:
    if not template_path.is_file():
        return ""
    raw = template_path.read_text(encoding="utf-8")
    marker = "  E0: |"
    if marker not in raw:
        return ""
    start = raw.index(marker) + len(marker)
    rest = raw[start:]
    end = rest.find("\n  ") if "\n  " in rest else len(rest)
    e0_body = rest[:end]
    chunks: list[str] = []
    for tag in tags:
        pattern = rf"<{tag}\b[^>]*>.*?</{tag}>"
        chunks.extend(re.findall(pattern, e0_body, flags=re.DOTALL))
    return "\n\n".join(chunks)


def build_executive_summary_e0(
    *,
    template_supplement: bool = True,
    strategy_executive: bool = False,
) -> str:
    by_id = load_examples_by_id("executive_summary")
    positive_ids = (
        _EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED
        if strategy_executive
        else _EXEC_SUMMARY_POSITIVE_COMPILE_IDS
    )
    parts = [
        "<many_shot_examples>",
        "<!-- E0 SSOT: executive_summary_examples.yaml (hydrated at compile) -->",
    ]
    if strategy_executive:
        parts.append(
            "<e0_lane_note>SVP IT strategy lane: two structurally diverse judge-aligned positives — "
            "thesis-arc (exec_summary_pos_svp_it_strategy_001) and credibility-implied arc "
            "(exec_summary_pos_credibility_implied_001). Metric values in the positives are "
            "domain-transposed placeholders ([X]M, [Y]%, [A]->[B]): do NOT copy them — retrieve "
            "real values from C0 ALLOWED_SOURCE_FACT_IDS. "
            "Copy density, register, and S1-S6 arc structure only. "
            "Negatives teach stack/recap failures.</e0_lane_note>"
        )
    for eid in positive_ids:
        row = by_id.get(eid)
        if row:
            parts.append(_render_positive_example(row))
    for eid, row in sorted(by_id.items()):
        if eid in positive_ids or eid in _EXEC_SUMMARY_POSITIVE_RETIRED_FROM_COMPILE:
            continue
        kind = _category_kind(str(row.get("category") or ""))
        if kind == "negative":
            parts.append(_render_negative_example(row))
        elif kind == "repair":
            parts.append(_render_repair_example(row))
    if template_supplement:
        sup = _extract_template_supplement_blocks(
            _EXEC_SUMMARY_TEMPLATE_SUPPLEMENT,
            ("transformation_example",),
        )
        if sup:
            parts.append(sup)
    parts.append("</many_shot_examples>")
    return "\n".join(parts) + "\n"


def build_unify_e0() -> str:
    by_id = load_examples_by_id("unify")
    parts = [
        "<many_shot_examples>",
        "<!-- E0 SSOT: unify_examples.yaml (hydrated at compile) -->",
    ]
    for eid in sorted(by_id):
        row = by_id[eid]
        kind = _category_kind(str(row.get("category") or ""))
        if kind == "positive":
            parts.append(_render_positive_example(row))
        elif kind == "negative":
            parts.append(_render_negative_example(row))
        elif kind == "repair":
            parts.append(_render_repair_example(row))
    parts.append("</many_shot_examples>")
    return "\n".join(parts) + "\n"


def build_competencies_e0() -> str:
    by_id = load_examples_by_id("competencies")
    return _render_competencies_style_block(list(by_id.values())) + "\n"


def resolve_e0_for_section(
    section: str,
    template_e0: str | None = None,
    *,
    allow_template_fallback: bool = False,
    strategy_executive: bool = False,
) -> str:
    """Return compiled E0 body for a section/lane id."""
    if section == "executive_summary":
        body = build_executive_summary_e0(strategy_executive=strategy_executive)
        if body.strip():
            return body
    if section in _UNIFY_LANE_SECTIONS:
        body = build_unify_e0()
        if body.strip():
            return body
    if section == "competencies":
        body = build_competencies_e0()
        if body.strip():
            return body
    if allow_template_fallback and template_e0:
        return template_e0
    if template_e0 and template_e0.strip():
        return template_e0
    return ""


def shared_example_ids_inline_and_yaml(section: str, template_e0: str) -> list[str]:
    """IDs appearing in both template inline positives and examples YAML (drift sentinels)."""
    yaml_ids = set(load_examples_by_id(section))
    inline_ids = set(re.findall(r'<positive_example id="([^"]+)"', template_e0 or ""))
    return sorted(yaml_ids & inline_ids)


__all__ = [
    "SECTION_EXAMPLES",
    "build_competencies_e0",
    "build_executive_summary_e0",
    "build_unify_e0",
    "example_after_text",
    "load_examples_by_id",
    "resolve_e0_for_section",
    "shared_example_ids_inline_and_yaml",
]
