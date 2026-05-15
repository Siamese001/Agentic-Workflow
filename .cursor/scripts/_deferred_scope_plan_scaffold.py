"""Plan-file scaffolder for DEFERRED_SCOPE auto-capture.

When a DEFERRED_SCOPE marker uses ``plan=NEW:<slug>``, the capture hook must
also create the actual plan file on disk at
``.cursor/plans/<slug>-<6hex>.md``. This module owns that scaffolding so
the hook itself stays compact.

Design:

- **Idempotent**: if a plan matching ``<slug>-*.md`` already exists, return
  it unchanged (no overwrite, no duplicate 6hex rotation).
- **Stable 6hex suffix**: generated from ``secrets.token_hex(3)`` the first
  time the slug is seen, then persisted to disk via the filename itself.
- **Fail-soft**: callers get ``(path, False, error)`` on any failure. The
  hook is advisory (fail-open) so scaffolder failures are logged but never
  abort the response.
- **No subprocess / no network** — pure filesystem + template render.
- **Path SSOT**: respects the plan-location rule (``.cursor/plans/`` only;
  ``docs/reports/plans/`` is never used).

Template kept intentionally minimal. Cursor Agent will expand it on the next
session when the deferred item becomes active work; the scaffold is just
enough to satisfy the plan-location SSOT and the pre-commit marker gate.
"""

import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

# Relaxed slug pattern — lowercase, dash-separated, no path separators.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
_EXISTING_PATTERN = re.compile(r"^(?P<slug>[a-z0-9][a-z0-9-]{0,63})-(?P<hex>[0-9a-f]{6})\.md$")


@dataclass(frozen=True)
class ScaffoldResult:
    """Outcome of a scaffold attempt."""

    plan_path: Path
    plan_filename: str  # basename only — what Notion's "Plan File" should store
    created: bool  # True iff a new file was written
    reason: str  # human-readable description, stored in the capture log


def _sanitize_slug(raw: str) -> str | None:
    """Lowercase + strip; return ``None`` if the slug is unsafe."""

    cleaned = raw.strip().lower()
    if not _SLUG_RE.match(cleaned):
        return None
    return cleaned


def _resolve_existing_plan(plans_dir: Path, raw_plan_value: str) -> Path | None:
    """Look up an existing plan file matching ``raw_plan_value``.

    Tries, in order:
      1. Exact filename (``<value>.md``)
      2. Filename without extension stripping (for values that already end in .md)
      3. Glob match ``<value>-*.md`` (caller gave slug without 6hex suffix)
      4. Glob match ``<value>*.md`` as a last resort
    """

    value = raw_plan_value.strip()
    if not value:
        return None
    # Strip a leading directory if someone passes a path.
    value = Path(value).name

    candidates = []
    if value.endswith(".md"):
        candidates.append(plans_dir / value)
    else:
        candidates.append(plans_dir / f"{value}.md")

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    base = value[:-3] if value.endswith(".md") else value
    for suffix in (f"{base}-*.md", f"{base}*.md"):
        matches = sorted(plans_dir.glob(suffix))
        if matches:
            return matches[0]
    return None


def _render_template(
    *,
    slug: str,
    suffix: str,
    marker: Mapping[str, str],
) -> str:
    """Render the minimal scaffold template for a new plan file."""

    plan_id = f"{slug}-{suffix}"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reason = marker.get("reason", "").strip() or slug.replace("-", " ")
    wave = marker.get("wave", "W1").strip() or "W1"
    phase = marker.get("phase", f"{wave}.1").strip() or f"{wave}.1"
    layer = marker.get("layer", "").strip()
    fan_in = marker.get("fan_in", "").strip()
    surface = marker.get("surface", "").strip()
    coverage_gap_pct = marker.get("coverage_gap_pct", "").strip()
    est_tokens = marker.get("est_tokens", "").strip()

    return f"""---
plan_id: {plan_id}
plan_type: tracker
# Auto-scaffolded {now_iso} by .cursor/scripts/post_cursor_agent_deferred_scope_capture.py
# from a DEFERRED_SCOPE marker. Cursor Agent should expand this plan on the next
# session before execution starts.
---

# {reason.title() or slug.replace("-", " ").title()}

> **Status**: AUTO-SCAFFOLD — not yet authored. The paired Notion row in
> Wave/Phase Convergence owns the authoritative priority; this file exists
> so the plan-location SSOT is satisfied and the pre-commit deferred-scope
> gate sees a marker inside the plan file.

---

## Origin

This plan was created automatically from a DEFERRED_SCOPE marker. The full
marker is preserved below so that the next session can reconstruct context
and decide scope.

DEFERRED_SCOPE: plan={plan_id} wave={wave} phase={phase} layer={layer} \
fan_in={fan_in} surface={surface} coverage_gap_pct={coverage_gap_pct} \
est_tokens={est_tokens} reason={reason}

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|--------|
| {wave} | AUTO-SCAFFOLD | TBD — Cursor Agent to fill | A | ~{est_tokens or "?"} 🟡 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| {phase} | {reason or "TBD"} | TBD | AUTO-SCAFFOLD | ~{est_tokens or "?"} | 🔲 TODO |

---

## Gap Register

**GAP-1 (AUTO-SCAFFOLD):** {reason or "See Notion row for details."}

---

## Next Action

Cursor Agent must expand this plan on the first session that picks it up. The
authoritative backlog row lives in Notion Wave/Phase Convergence
(``Plan File = "{plan_id}.md"``).
"""


def scaffold_plan_if_needed(
    marker_fields: Mapping[str, str],
    repo_root: Path,
) -> ScaffoldResult:
    """Create a plan file on disk if the marker requests a new one.

    Returns a :class:`ScaffoldResult` whose ``plan_filename`` is what the
    caller should write to Notion's ``Plan File`` rich_text property. The
    filename always has the 6hex suffix form ``<slug>-<hex>.md`` so it is
    immediately discoverable by the plan-location SSOT.

    The function never raises — any internal error is folded into
    ``ScaffoldResult`` with ``created=False`` and a human-readable
    ``reason``. The caller decides whether to proceed.
    """

    plan_value = marker_fields.get("plan", "").strip()
    plans_dir = repo_root / ".cursor" / "plans"

    if not plan_value:
        return ScaffoldResult(
            plan_path=plans_dir / "UNKNOWN.md",
            plan_filename="UNKNOWN.md",
            created=False,
            reason="no plan field in marker",
        )

    try:
        plans_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return ScaffoldResult(
            plan_path=plans_dir / "UNKNOWN.md",
            plan_filename="UNKNOWN.md",
            created=False,
            reason=f"plans dir create failed: {exc}",
        )

    is_new_request = plan_value.upper().startswith("NEW:")

    if not is_new_request:
        existing = _resolve_existing_plan(plans_dir, plan_value)
        if existing is not None:
            return ScaffoldResult(
                plan_path=existing,
                plan_filename=existing.name,
                created=False,
                reason=f"existing plan resolved: {existing.name}",
            )
        # Marker referenced an existing slug but no disk file found.
        # Do NOT scaffold — the user said "existing", so a missing file is a
        # surfacing-worthy drift the CI gate will report.
        fallback_name = plan_value if plan_value.endswith(".md") else f"{plan_value}.md"
        return ScaffoldResult(
            plan_path=plans_dir / fallback_name,
            plan_filename=fallback_name,
            created=False,
            reason=f"plan referenced but not found on disk: {fallback_name}",
        )

    raw_slug = plan_value[4:]  # strip 'NEW:'
    slug = _sanitize_slug(raw_slug)
    if slug is None:
        return ScaffoldResult(
            plan_path=plans_dir / "UNKNOWN.md",
            plan_filename="UNKNOWN.md",
            created=False,
            reason=f"invalid slug after NEW:: {raw_slug!r}",
        )

    # Idempotency — if any file matches <slug>-*.md already, reuse it.
    existing_matches = sorted(plans_dir.glob(f"{slug}-*.md"))
    reusable: Path | None = None
    for path in existing_matches:
        if _EXISTING_PATTERN.match(path.name):
            reusable = path
            break
    if reusable is not None:
        return ScaffoldResult(
            plan_path=reusable,
            plan_filename=reusable.name,
            created=False,
            reason=f"NEW:{slug} resolved to existing {reusable.name}",
        )

    suffix = secrets.token_hex(3)  # 6 hex chars
    target = plans_dir / f"{slug}-{suffix}.md"
    try:
        content = _render_template(slug=slug, suffix=suffix, marker=marker_fields)
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        return ScaffoldResult(
            plan_path=target,
            plan_filename=target.name,
            created=False,
            reason=f"write failed: {exc}",
        )

    return ScaffoldResult(
        plan_path=target,
        plan_filename=target.name,
        created=True,
        reason=f"scaffolded NEW:{slug} → {target.name}",
    )
