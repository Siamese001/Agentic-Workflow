"""Bullet judge-feedback pool reselection (W4.1, G14) — bounded, deterministic-first.

When the employment bullet lanes (ibm_bullets / unify_bullets) reach a MODEL_BACKED X1D
judge failure AFTER an all-pass X2 wall, the run today dies with unused pool candidates
sitting on disk (``self_consistency_path_{N}_parsed.json``). This module adds ONE bounded
repair rung between the adjudicator artifact writes and ``finalize_lane_product_quality``:
swap the implicated slot(s) to the first compliant on-disk alternate, re-run the FULL
deterministic X2 set (revert on any regression), and re-judge ONCE at the same
rubric/threshold. ZERO new generation calls — alternates only; the single re-judge is the
only provider call (mocked judge_mode short-circuits it upstream).

Trigger arms (decision recorded 2026-06-10, north star = 11/11 X3_ALLOW):

* ``decisive`` — a non-synthetic MODEL_BACKED row with ``decisive_failure=True``. If the
  re-judge decisively fails again the verdict stands (``rejudge_fail_final``, X3_BLOCK).
* ``soft_fail`` — the ``X3_REVIEW_JUDGE_SOFT_FAIL`` shape (below threshold, non-decisive)
  WITH a strict revert-on-worse rule: if the re-judge is decisive OR scores below the
  original row, content AND original judge rows are restored entirely
  (``reverted_rejudge_worse``) so the floor remains the original non-blocking REVIEW.

Both arms: synthetic selector rows (``employment_bullet_pool_selector`` /
``competencies_graph_pool_selector``) NEVER trigger, and X2 must be all-pass pre-swap.

Supersession scope (adversarial-verifier mandate): when the swap fires, ALL non-synthetic
MODEL_BACKED rows that judged the pre-swap content — decisive AND non-decisive (e.g.
adjudicator panel rows) — move to ``x1d_llm_judge_outputs_pre_reselection.json`` stamped
``superseded_by_reselection=True``; the union of their provider keys is re-judged in the
single re-judge invocation (policy-filtered; dropped non-required keys are recorded in the
receipt instead of silently re-judging a different panel).

Exactly-once: an existing ``reselection_receipt.json`` makes the seam a no-op.
Kill-switch: ``APPS_RG_BULLET_RESELECTION_DISABLE`` in ("1", "true", "yes").
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.exit.executive_summary_x3 import _is_model_backed_soft_fail
from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    _bullet_passes_line_discipline,
    _source_id_allowed,
)
from apps_rg.runtime.reasoning.bullet_fact_entailment import numeric_entailment_check
from apps_rg.runtime.section_judge_policy import get_section_judge_policy
from apps_rg.runtime.section_repair_ledger import KIND_DETERMINISTIC_REWRITE, record_repair

RESELECTION_DISABLE_ENV = "APPS_RG_BULLET_RESELECTION_DISABLE"
RESELECTION_RECEIPT_FILENAME = "reselection_receipt.json"
PRE_RESELECTION_X1D_SIDECAR_FILENAME = "x1d_llm_judge_outputs_pre_reselection.json"
PRE_RESELECTION_SELECTION_FILENAME = "bullet_pool_selection_pre_reselection.json"
RESELECTION_OPERATION = "bullet_judge_feedback_reselection"
RECEIPT_VERSION = 1

OUTCOME_DISABLED = "disabled_by_env"
OUTCOME_NOT_FIRED = "not_fired"
OUTCOME_NO_COMPLIANT_ALTERNATE = "no_compliant_alternate"
OUTCOME_REVERTED_X2_REGRESSION = "reverted_x2_regression"
OUTCOME_REVERTED_REJUDGE_WORSE = "reverted_rejudge_worse"
OUTCOME_REJUDGE_PASS = "rejudge_pass"
OUTCOME_REJUDGE_FAIL_FINAL = "rejudge_fail_final"

TRIGGER_ARM_DECISIVE = "decisive"
TRIGGER_ARM_SOFT_FAIL = "soft_fail"

SLOT_RESOLUTION_BULLET_ID_REGEX = "bullet_id_regex"
SLOT_RESOLUTION_CITED_SENTENCE_INDEXES = "cited_sentence_indexes"
SLOT_RESOLUTION_LOWEST_SELECTOR_SCORE = "lowest_selector_score"
SLOT_RESOLUTION_UNRESOLVED = "unresolved"

# Synthetic selector rows encode a selection-gate verdict, not a cross-provider judge
# verdict on the shipped content — their decisive fail is the selector-regen seam's job.
_SYNTHETIC_SELECTOR_JUDGE_ROLES: frozenset[str] = frozenset(
    {"employment_bullet_pool_selector", "competencies_graph_pool_selector"}
)

_SLOT_ID_RE = re.compile(r"bul_[a-z]+_\d{3}")
_PATH_FILE_RE = re.compile(r"^self_consistency_path_(\d+)_parsed\.json$")
_SLOT_PROSE_FIELDS = ("findings", "fail_reasons", "unsupported_claims", "remediation_suggestions")


def _sha16(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_json(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- optional artifact read is fail-soft; absence is handled by callers
        return None


def _bullet_by_id(parsed: dict[str, Any] | None, bullet_id: str) -> dict[str, Any] | None:
    for bullet in (parsed or {}).get("bullets") or []:
        if isinstance(bullet, dict) and str(bullet.get("bullet_id") or "").strip() == bullet_id:
            return bullet
    return None


def _is_synthetic_selector_row(row: dict[str, Any]) -> bool:
    return str(row.get("judge_role") or "") in _SYNTHETIC_SELECTOR_JUDGE_ROLES


def _is_model_backed(row: dict[str, Any]) -> bool:
    return str(row.get("evaluator_mode") or "") == "MODEL_BACKED"


def _is_decisive_row(row: dict[str, Any]) -> bool:
    return _is_model_backed(row) and bool(row.get("decisive_failure"))


def _row_passes(row: dict[str, Any]) -> bool:
    """Same MODEL_BACKED_PASS slice aggregate_x3 uses for X3_ALLOW."""
    if not _is_model_backed(row):
        return False
    if row.get("decisive_failure"):
        return False
    if row.get("pass") is False:
        return False
    if row.get("provider_status") not in (None, "MODEL_BACKED_PASS"):
        return False
    ns = row.get("normalized_score")
    nt = row.get("normalized_threshold")
    if ns is not None and nt is not None and float(ns) < float(nt):
        return False
    return True


def _trigger_row_receipt_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "judge_id": row.get("judge_id"),
        "provider_key": row.get("provider_key"),
        "judge_role": row.get("judge_role"),
        "score": row.get("score"),
        "threshold": row.get("threshold"),
        "normalized_score": row.get("normalized_score"),
        "normalized_threshold": row.get("normalized_threshold"),
        "decisive_failure": bool(row.get("decisive_failure")),
    }


# ---------------------------------------------------------------------------
# Pool loading
# ---------------------------------------------------------------------------


@dataclass
class PoolAlternates:
    """On-disk self-consistency pool projected per slot, plus the selection artifact."""

    alternates_by_slot: dict[str, list[tuple[int, dict[str, Any]]]]
    parsed_by_path_index: dict[int, dict[str, Any]]
    source_path_by_slot: dict[str, int]
    selection_scores_by_slot: dict[str, float]
    selection_doc: dict[str, Any]


def load_pool_alternates(
    artifact_dir: Path,
    required_bullet_ids: tuple[str, ...],
) -> PoolAlternates:
    """Load every persisted SC path candidate per required slot (ascending path_index)."""
    artifact_dir = Path(artifact_dir)
    parsed_by_path_index: dict[int, dict[str, Any]] = {}
    for path in sorted(artifact_dir.glob("self_consistency_path_*_parsed.json")):
        match = _PATH_FILE_RE.match(path.name)
        if match is None:
            continue
        doc = _load_json(path)
        if isinstance(doc, dict):
            parsed_by_path_index[int(match.group(1))] = doc

    alternates_by_slot: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for slot in required_bullet_ids:
        rows: list[tuple[int, dict[str, Any]]] = []
        for path_index in sorted(parsed_by_path_index):
            bullet = _bullet_by_id(parsed_by_path_index[path_index], slot)
            if bullet is not None:
                rows.append((path_index, dict(bullet)))
        alternates_by_slot[slot] = rows

    selection_doc = _load_json(artifact_dir / "bullet_pool_selection.json")
    selection_doc = selection_doc if isinstance(selection_doc, dict) else {}
    source_path_by_slot: dict[str, int] = {}
    for slot, path_index in (selection_doc.get("source_path_by_slot") or {}).items():
        try:
            source_path_by_slot[str(slot)] = int(path_index)
        except (TypeError, ValueError):
            continue
    selection_scores_by_slot: dict[str, float] = {}
    for row in selection_doc.get("selections") or []:
        if not isinstance(row, dict):
            continue
        slot = str(row.get("bullet_id") or "").strip()
        if not slot:
            continue
        try:
            selection_scores_by_slot[slot] = float(row.get("score") or 0.0)
        except (TypeError, ValueError):
            selection_scores_by_slot[slot] = 0.0

    return PoolAlternates(
        alternates_by_slot=alternates_by_slot,
        parsed_by_path_index=parsed_by_path_index,
        source_path_by_slot=source_path_by_slot,
        selection_scores_by_slot=selection_scores_by_slot,
        selection_doc=selection_doc,
    )


# ---------------------------------------------------------------------------
# Plan building (pure)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SlotSwap:
    slot: str
    old_path_index: int | None
    new_path_index: int
    old_text: str
    new_text: str
    alternate_basis: str
    compliance_checks: tuple[str, ...]

    def to_receipt_dict(self) -> dict[str, Any]:
        return {
            "slot": self.slot,
            "old_path_index": self.old_path_index,
            "new_path_index": self.new_path_index,
            "old_text_sha16": _sha16(self.old_text),
            "new_text_sha16": _sha16(self.new_text),
            "alternate_basis": self.alternate_basis,
            "compliance_checks": list(self.compliance_checks),
        }


@dataclass(frozen=True)
class ReselectionPlan:
    fired: bool
    outcome: str  # OUTCOME_NOT_FIRED / OUTCOME_NO_COMPLIANT_ALTERNATE; "" while fired
    trigger_arm: str
    x2_all_pass_pre: bool
    trigger_rows: tuple[dict[str, Any], ...]
    slot_resolution_method: str
    implicated_slots: tuple[str, ...]
    swaps: tuple[SlotSwap, ...]
    slots_without_alternate: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fired": self.fired,
            "outcome": self.outcome,
            "trigger_arm": self.trigger_arm,
            "x2_all_pass_pre": self.x2_all_pass_pre,
            "trigger_rows": [_trigger_row_receipt_fields(r) for r in self.trigger_rows],
            "slot_resolution_method": self.slot_resolution_method,
            "implicated_slots": list(self.implicated_slots),
            "swaps": [s.to_receipt_dict() for s in self.swaps],
            "slots_without_alternate": list(self.slots_without_alternate),
        }


def _resolve_implicated_slots(
    trigger_rows: list[dict[str, Any]],
    *,
    bullets: list[dict[str, Any]],
    required_bullet_ids: tuple[str, ...],
    selection_scores_by_slot: dict[str, float],
) -> tuple[list[str], str]:
    """Deterministic slot resolution: (i) bul_* regex, (ii) cited indexes, (iii) lowest score."""
    present_slots = [
        str(b.get("bullet_id") or "").strip()
        for b in bullets
        if isinstance(b, dict) and str(b.get("bullet_id") or "").strip() in required_bullet_ids
    ]
    present = set(present_slots)

    # (i) bul_<lane>_NNN ids in the trigger rows' prose fields.
    regex_hits: list[str] = []
    for row in trigger_rows:
        for fld in _SLOT_PROSE_FIELDS:
            for entry in row.get(fld) or []:
                for slot in _SLOT_ID_RE.findall(str(entry or "")):
                    if slot in present and slot not in regex_hits:
                        regex_hits.append(slot)
    if regex_hits:
        return regex_hits, SLOT_RESOLUTION_BULLET_ID_REGEX

    # (ii) cited_sentence_indexes — 1-based display order over the current bullets list.
    cited_hits: list[str] = []
    for row in trigger_rows:
        for raw in row.get("cited_sentence_indexes") or []:
            try:
                k = int(raw)
            except (TypeError, ValueError):
                continue
            if 1 <= k <= len(bullets):
                slot = str(bullets[k - 1].get("bullet_id") or "").strip()
                if slot in present and slot not in cited_hits:
                    cited_hits.append(slot)
    if cited_hits:
        return cited_hits, SLOT_RESOLUTION_CITED_SENTENCE_INDEXES

    # (iii) fallback — the single present slot with the LOWEST selector score.
    scored = [(score, slot) for slot, score in selection_scores_by_slot.items() if slot in present]
    if scored:
        scored.sort(key=lambda pair: (pair[0], pair[1]))
        return [scored[0][1]], SLOT_RESOLUTION_LOWEST_SELECTOR_SCORE

    return [], SLOT_RESOLUTION_UNRESOLVED


def _first_compliant_alternate(
    slot: str,
    *,
    current_text: str,
    pool: PoolAlternates,
    allowed_fact_ids: set[str],
    entailment_corpus: dict[str, str] | None,
) -> SlotSwap | None:
    """First alternate by ascending path_index passing every deterministic floor."""
    excluded_path = pool.source_path_by_slot.get(slot)
    corpus = (entailment_corpus or {}).get(slot, "")
    for path_index, bullet in pool.alternates_by_slot.get(slot) or []:
        if excluded_path is not None and path_index == excluded_path:
            continue
        text = str(bullet.get("bullet_text") or "").strip()
        if not text or text == current_text:
            continue
        candidate = {**bullet, "bullet_id": slot}
        checks: list[str] = []
        # Line-discipline + quality floors (same deterministic floors the selector uses).
        if not _bullet_passes_line_discipline(candidate):
            continue
        checks.extend(["line_discipline", "quality_floors"])
        # Source-fact scope: every cited id must resolve inside allowed_fact_ids.
        source_ids = [
            str(x).strip()
            for x in [*(bullet.get("source_fact_ids") or []), bullet.get("source_fact_id")]
            if str(x or "").strip()
        ]
        if allowed_fact_ids and source_ids and not all(
            _source_id_allowed(sid, allowed_fact_ids) for sid in source_ids
        ):
            continue
        checks.append("fact_scope")
        # Numeric fact-entailment (W4.3 drift class, e.g. cross-slot "$10M ARR"):
        # required when the slot corpus is available; fail-open (recorded) when missing.
        if corpus:
            entailed, _missing = numeric_entailment_check(text, corpus)
            if not entailed:
                continue
            checks.append("fact_entailment")
        else:
            checks.append("fact_entailment:skipped_no_corpus")
        return SlotSwap(
            slot=slot,
            old_path_index=excluded_path,
            new_path_index=path_index,
            old_text=current_text,
            new_text=text,
            alternate_basis="first_compliant_alternate",
            compliance_checks=tuple(checks),
        )
    return None


def build_reselection_plan(
    *,
    x1d_rows: list[dict[str, Any]],
    x2_failed_gate_ids: list[str],
    pool: PoolAlternates,
    bullets: list[dict[str, Any]],
    required_bullet_ids: tuple[str, ...],
    allowed_fact_ids: set[str],
    entailment_corpus: dict[str, str] | None = None,
) -> ReselectionPlan:
    """Pure trigger + slot-resolution + replacement plan. No I/O, no mutation."""
    x2_all_pass = not x2_failed_gate_ids
    eligible = [r for r in x1d_rows if _is_model_backed(r) and not _is_synthetic_selector_row(r)]
    decisive_rows = [r for r in eligible if _is_decisive_row(r)]
    soft_rows = [r for r in eligible if _is_model_backed_soft_fail(r)]

    if decisive_rows:
        trigger_arm = TRIGGER_ARM_DECISIVE
        trigger_rows = decisive_rows
    elif soft_rows:
        trigger_arm = TRIGGER_ARM_SOFT_FAIL
        trigger_rows = soft_rows
    else:
        trigger_arm = ""
        trigger_rows = []

    not_fired = ReselectionPlan(
        fired=False,
        outcome=OUTCOME_NOT_FIRED,
        trigger_arm=trigger_arm,
        x2_all_pass_pre=x2_all_pass,
        trigger_rows=tuple(trigger_rows),
        slot_resolution_method="",
        implicated_slots=(),
        swaps=(),
        slots_without_alternate=(),
    )
    if not trigger_rows:
        return not_fired
    if not x2_all_pass:
        # An X2 fail is already X3_BLOCK; reselection cannot help and must not mask it.
        return not_fired

    implicated, method = _resolve_implicated_slots(
        trigger_rows,
        bullets=bullets,
        required_bullet_ids=required_bullet_ids,
        selection_scores_by_slot=pool.selection_scores_by_slot,
    )
    if not implicated:
        return ReselectionPlan(
            fired=False,
            outcome=OUTCOME_NOT_FIRED,
            trigger_arm=trigger_arm,
            x2_all_pass_pre=x2_all_pass,
            trigger_rows=tuple(trigger_rows),
            slot_resolution_method=SLOT_RESOLUTION_UNRESOLVED,
            implicated_slots=(),
            swaps=(),
            slots_without_alternate=(),
        )

    swaps: list[SlotSwap] = []
    without_alternate: list[str] = []
    for slot in implicated:
        current = _bullet_by_id({"bullets": bullets}, slot) or {}
        swap = _first_compliant_alternate(
            slot,
            current_text=str(current.get("bullet_text") or "").strip(),
            pool=pool,
            allowed_fact_ids=set(allowed_fact_ids or set()),
            entailment_corpus=entailment_corpus,
        )
        if swap is None:
            without_alternate.append(slot)
        else:
            swaps.append(swap)

    if not swaps:
        return ReselectionPlan(
            fired=False,
            outcome=OUTCOME_NO_COMPLIANT_ALTERNATE,
            trigger_arm=trigger_arm,
            x2_all_pass_pre=x2_all_pass,
            trigger_rows=tuple(trigger_rows),
            slot_resolution_method=method,
            implicated_slots=tuple(implicated),
            swaps=(),
            slots_without_alternate=tuple(without_alternate),
        )
    return ReselectionPlan(
        fired=True,
        outcome="",
        trigger_arm=trigger_arm,
        x2_all_pass_pre=x2_all_pass,
        trigger_rows=tuple(trigger_rows),
        slot_resolution_method=method,
        implicated_slots=tuple(implicated),
        swaps=tuple(swaps),
        slots_without_alternate=tuple(without_alternate),
    )


# ---------------------------------------------------------------------------
# Swap application (pure)
# ---------------------------------------------------------------------------


def _row_cites_slot(row: dict[str, Any], slots: set[str], *, root_match: bool) -> bool:
    bid = str(row.get("bullet_id") or "").strip()
    if bid in slots:
        return True
    for raw in row.get("source_fact_ids") or []:
        sid = str(raw).strip()
        if sid in slots:
            return True
        if root_match and sid.split("_metric_", 1)[0] in slots:
            return True
    return False


def apply_reselection(
    parsed: dict[str, Any],
    plan: ReselectionPlan,
    parsed_by_path_index: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    """Swap the planned slots and pull their claim_ledger/change_log rows from the source path.

    Mirrors ``merge_bullet_selections``: pulled rows match on ``bullet_id`` or membership in
    ``source_fact_ids``; removal additionally root-matches ``<slot>_metric_*`` citations so a
    swapped slot cannot leave stale metric-suffixed rows behind.
    """
    out = dict(parsed or {})
    swap_by_slot = {s.slot: s for s in plan.swaps}
    swapped_slots = set(swap_by_slot)

    new_bullets: list[dict[str, Any]] = []
    for bullet in out.get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        slot = str(bullet.get("bullet_id") or "").strip()
        swap = swap_by_slot.get(slot)
        if swap is None:
            new_bullets.append(dict(bullet))
            continue
        source_doc = parsed_by_path_index.get(swap.new_path_index) or {}
        replacement = dict(_bullet_by_id(source_doc, slot) or {})
        replacement["bullet_id"] = slot
        if not replacement.get("bullet_text"):
            replacement["bullet_text"] = swap.new_text
        new_bullets.append(replacement)
    out["bullets"] = new_bullets

    for key in ("claim_ledger", "change_log"):
        rows = [dict(r) for r in (out.get(key) or []) if isinstance(r, dict)]
        kept = [r for r in rows if not _row_cites_slot(r, swapped_slots, root_match=True)]
        pulled: list[dict[str, Any]] = []
        for slot in swap_by_slot:
            source_doc = parsed_by_path_index.get(swap_by_slot[slot].new_path_index) or {}
            for r in source_doc.get(key) or []:
                if isinstance(r, dict) and _row_cites_slot(r, {slot}, root_match=False):
                    pulled.append(dict(r))
        if rows or pulled:
            out[key] = kept + pulled
    return out


# ---------------------------------------------------------------------------
# Lane glue
# ---------------------------------------------------------------------------


@dataclass
class LaneRebuildState:
    """Post-swap lane state rebuilt through the lane's own deterministic pipeline."""

    parsed: dict[str, Any]
    bullets: list[dict[str, Any]]
    claim_ledger: list[dict[str, Any]]
    coverage: dict[str, Any]
    parsed_for_x2: dict[str, Any] | None
    canon_doc: dict[str, Any]
    usage_doc: dict[str, Any]
    display_text: str
    parse_status: str = "OK"


@dataclass
class ReselectionResult:
    """What the lane rebinds after the seam. ``display_text`` is None when unchanged."""

    fired: bool
    outcome: str
    receipt: dict[str, Any]
    parsed: dict[str, Any] | None
    bullets: list[dict[str, Any]]
    claim_ledger: list[dict[str, Any]]
    parsed_for_x2: dict[str, Any] | None
    x2: list[dict[str, Any]]
    x1d: list[dict[str, Any]]
    usage_doc: dict[str, Any]
    canon_doc: dict[str, Any]
    display_text: str | None = None
    receipt_written: bool = field(default=True)


def _failed_gate_ids(x2_rows: list[dict[str, Any]]) -> list[str]:
    return [str(g.get("gate_id") or "") for g in x2_rows if not g.get("pass")]


def _snapshot_bytes(path: Path) -> bytes | None:
    if path.is_file():
        try:
            return path.read_bytes()
        except OSError:  # guardian: allow-return-none-swallow -- snapshot is best-effort; restore treats None as "file did not exist"
            return None
    return None


def _restore_bytes(path: Path, snapshot: bytes | None) -> None:
    if snapshot is None:
        if path.is_file():
            path.unlink()
        return
    path.write_bytes(snapshot)


def run_bullet_judge_reselection(
    *,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    required_bullet_ids: tuple[str, ...],
    parsed: dict[str, Any] | None,
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    parsed_for_x2: dict[str, Any] | None,
    x1d: list[dict[str, Any]],
    x2: list[dict[str, Any]],
    usage_doc: dict[str, Any],
    canon_doc: dict[str, Any],
    allowed_fact_ids: set[str],
    judge_mode: str,
    entailment_corpus: dict[str, str] | None,
    post_chain: Callable[[dict[str, Any]], dict[str, Any]],
    rebuild_state: Callable[[dict[str, Any]], LaneRebuildState],
    run_x2: Callable[[LaneRebuildState, list[dict[str, Any]]], list[dict[str, Any]]],
    run_judges: Callable[[LaneRebuildState, list[str]], list[dict[str, Any]]],
    write_usage_ledger: Callable[[LaneRebuildState], None],
    write_lane_artifacts: Callable[[LaneRebuildState, list[dict[str, Any]]], None],
) -> ReselectionResult:
    """Evaluate the reselection seam once. Deterministic except the single optional re-judge.

    Sequencing (deferred writes — nothing is mutated until the swap is proven):
      1. exactly-once / kill-switch guards
      2. plan (trigger + slot resolution + first compliant alternate)
      3. swap + lane post-chain + state rebuild (in memory)
      4. usage ledger written (X2 reads it from disk), FULL X2 re-run with the PRE-swap x1d
         set as ``x1d_judges`` — any gate that passed pre-swap now failing => byte-exact
         restore + ``reverted_x2_regression`` (re-judge skipped)
      5. single re-judge of the superseded providers' union (policy-filtered, recorded)
      6. soft arm only: revert-on-worse (decisive OR score below original)
      7. swap sticks: rewrite every downstream artifact + x1d sidecar + selection rewrite +
         repair-ledger row + receipt
    """
    artifact_dir = Path(artifact_dir)
    receipt_path = artifact_dir / RESELECTION_RECEIPT_FILENAME

    def _originals(outcome: str, receipt: dict[str, Any], *, written: bool) -> ReselectionResult:
        return ReselectionResult(
            fired=False,
            outcome=outcome,
            receipt=receipt,
            parsed=parsed,
            bullets=bullets,
            claim_ledger=claim_ledger,
            parsed_for_x2=parsed_for_x2,
            x2=x2,
            x1d=x1d,
            usage_doc=usage_doc,
            canon_doc=canon_doc,
            display_text=None,
            receipt_written=written,
        )

    disabled = os.environ.get(RESELECTION_DISABLE_ENV, "").strip().lower() in ("1", "true", "yes")

    def _base_receipt() -> dict[str, Any]:
        return {
            "receipt_version": RECEIPT_VERSION,
            "section_id": section_id,
            "run_id": run_id,
            "fired": False,
            "outcome": "",
            "kill_switch": {"env": RESELECTION_DISABLE_ENV, "disabled": disabled},
            "trigger": {"x2_all_pass_pre": None, "trigger_arm": "", "rows": []},
            "slot_resolution_method": "",
            "slots": [],
            "x2": {"failed_before": _failed_gate_ids(x2), "failed_after": None},
            "rejudge": {
                "provider_keys": [],
                "dropped_non_required_keys": [],
                "scores_before": {},
                "scores_after": {},
                "decisive_after": None,
                "pass_after": None,
            },
            "attempt": 1,
            "max_attempts": 1,
        }

    # Exactly-once: an existing receipt makes this seam a strict no-op (no rewrite).
    existing = _load_json(receipt_path)
    if isinstance(existing, dict):
        return _originals(str(existing.get("outcome") or OUTCOME_NOT_FIRED), existing, written=False)

    if disabled:
        receipt = _base_receipt()
        receipt["outcome"] = OUTCOME_DISABLED
        _write_json(receipt_path, receipt)
        return _originals(OUTCOME_DISABLED, receipt, written=True)

    pool = load_pool_alternates(artifact_dir, required_bullet_ids)
    plan = build_reselection_plan(
        x1d_rows=x1d,
        x2_failed_gate_ids=_failed_gate_ids(x2),
        pool=pool,
        bullets=bullets,
        required_bullet_ids=required_bullet_ids,
        allowed_fact_ids=set(allowed_fact_ids or set()),
        entailment_corpus=entailment_corpus,
    )

    receipt = _base_receipt()
    receipt["trigger"] = {
        "x2_all_pass_pre": plan.x2_all_pass_pre,
        "trigger_arm": plan.trigger_arm,
        "rows": [_trigger_row_receipt_fields(r) for r in plan.trigger_rows],
    }
    receipt["slot_resolution_method"] = plan.slot_resolution_method
    receipt["slots"] = [s.to_receipt_dict() for s in plan.swaps]
    receipt["slots_without_alternate"] = list(plan.slots_without_alternate)

    if not plan.fired:
        receipt["outcome"] = plan.outcome
        _write_json(receipt_path, receipt)
        return _originals(plan.outcome, receipt, written=True)

    # ----- swap + lane-deterministic post chain + state rebuild (in memory) -----
    swapped = apply_reselection(dict(parsed or {}), plan, pool.parsed_by_path_index)
    swapped = post_chain(swapped) or swapped
    state = rebuild_state(swapped)

    # The X2 usage gates read section_input_usage_ledger.json from disk — write the
    # post-swap ledger first (snapshotted; byte-restored on every revert path).
    usage_ledger_path = artifact_dir / "section_input_usage_ledger.json"
    usage_snapshot = _snapshot_bytes(usage_ledger_path)
    judge_packet_path = artifact_dir / f"{section_id}_judge_packet.json"
    judge_packet_snapshot = _snapshot_bytes(judge_packet_path)
    write_usage_ledger(state)

    # ----- FULL X2 re-run (deterministic, zero provider calls), PRE-swap x1d as arg -----
    x2_after = run_x2(state, x1d)
    passed_before = {
        str(g.get("gate_id") or "") for g in x2 if g.get("pass")
    }
    regressions = [g for g in _failed_gate_ids(x2_after) if g in passed_before]
    receipt["x2"]["failed_after"] = _failed_gate_ids(x2_after)
    if regressions:
        _restore_bytes(usage_ledger_path, usage_snapshot)
        receipt["outcome"] = OUTCOME_REVERTED_X2_REGRESSION
        receipt["x2"]["regressed_gates"] = regressions
        _write_json(receipt_path, receipt)
        return _originals(OUTCOME_REVERTED_X2_REGRESSION, receipt, written=True)

    # ----- supersession scope: ALL non-synthetic MODEL_BACKED rows judged old content -----
    superseded = [r for r in x1d if _is_model_backed(r) and not _is_synthetic_selector_row(r)]
    _superseded_ids = {id(r) for r in superseded}
    kept = [r for r in x1d if id(r) not in _superseded_ids]
    requested_keys = sorted(
        {str(r.get("provider_key") or "") for r in superseded if r.get("provider_key")}
    )
    policy = get_section_judge_policy(section_id)
    required = tuple(policy.required_judge_providers or ())
    if required:
        rejudge_keys = [k for k in requested_keys if k in required] or list(required)
    else:
        rejudge_keys = list(requested_keys)
    dropped_keys = [k for k in requested_keys if k not in rejudge_keys]
    baseline_scores: dict[str, float] = {}
    for r in superseded:
        pk = str(r.get("provider_key") or "")
        ns = r.get("normalized_score")
        if pk and ns is not None:
            baseline_scores[pk] = float(ns)

    # ----- single re-judge at the SAME rubric/threshold (the only provider call) -----
    new_rows = [dict(r) for r in run_judges(state, list(rejudge_keys))]
    for row in new_rows:
        row["reselection_rejudge_row"] = True
    new_scores: dict[str, Any] = {
        str(r.get("provider_key") or ""): r.get("normalized_score") for r in new_rows
    }
    decisive_after = any(_is_decisive_row(r) for r in new_rows)
    pass_after = bool(new_rows) and all(_row_passes(r) for r in new_rows)
    receipt["rejudge"] = {
        "provider_keys": list(rejudge_keys),
        "dropped_non_required_keys": dropped_keys,
        "scores_before": baseline_scores,
        "scores_after": new_scores,
        "decisive_after": decisive_after,
        "pass_after": pass_after,
    }

    # ----- soft arm: strict revert-on-worse (decisive OR below the original score) -----
    if plan.trigger_arm == TRIGGER_ARM_SOFT_FAIL:
        worse = decisive_after
        if not worse:
            for row in new_rows:
                ns = row.get("normalized_score")
                if ns is None:
                    continue
                base = baseline_scores.get(str(row.get("provider_key") or ""))
                if base is None and baseline_scores:
                    base = min(baseline_scores.values())
                if base is not None and float(ns) < float(base):
                    worse = True
                    break
        if worse:
            _restore_bytes(usage_ledger_path, usage_snapshot)
            _restore_bytes(judge_packet_path, judge_packet_snapshot)
            receipt["outcome"] = OUTCOME_REVERTED_REJUDGE_WORSE
            _write_json(receipt_path, receipt)
            # Content + original judge rows restored entirely: the floor remains the
            # original non-blocking REVIEW.
            return _originals(OUTCOME_REVERTED_REJUDGE_WORSE, receipt, written=True)

    # ----- swap sticks: persist everything against the post-swap content -----
    outcome = OUTCOME_REJUDGE_PASS if pass_after else OUTCOME_REJUDGE_FAIL_FINAL
    active_x1d = list(kept) + list(new_rows)

    sidecar_rows = [dict(r, superseded_by_reselection=True) for r in superseded]
    _write_json(
        artifact_dir / PRE_RESELECTION_X1D_SIDECAR_FILENAME,
        {
            "section_id": section_id,
            "run_id": run_id,
            "reason": "rows judged pre-reselection content; superseded by the re-judge",
            "judges": sidecar_rows,
        },
    )
    _write_json(
        artifact_dir / "x1d_llm_judge_outputs.json",
        {
            "judges": active_x1d,
            "sidecar_ref": PRE_RESELECTION_X1D_SIDECAR_FILENAME,
            "reselection_applied": True,
        },
    )

    # bullet_pool_selection.json: preserve the original, rewrite the post-swap slot map
    # (swapped slots: new path_index, score=null, reselection_applied=true).
    if pool.selection_doc:
        _write_json(artifact_dir / PRE_RESELECTION_SELECTION_FILENAME, pool.selection_doc)
    new_selection_doc = dict(pool.selection_doc or {})
    swap_by_slot = {s.slot: s for s in plan.swaps}
    new_selections: list[dict[str, Any]] = []
    for row in new_selection_doc.get("selections") or []:
        row = dict(row) if isinstance(row, dict) else {}
        slot = str(row.get("bullet_id") or "").strip()
        if slot in swap_by_slot:
            row["path_index"] = swap_by_slot[slot].new_path_index
            row["score"] = None
            row["reselection_applied"] = True
        new_selections.append(row)
    new_selection_doc["selections"] = new_selections
    source_map = dict(new_selection_doc.get("source_path_by_slot") or {})
    for slot, swap in swap_by_slot.items():
        source_map[slot] = swap.new_path_index
    new_selection_doc["source_path_by_slot"] = source_map
    new_selection_doc["reselection_applied"] = True
    new_selection_doc["reselection_receipt_ref"] = RESELECTION_RECEIPT_FILENAME
    _write_json(artifact_dir / "bullet_pool_selection.json", new_selection_doc)

    # Lane-owned downstream artifacts (parsed_output.json, <lane>_output.txt,
    # claim_ledger.json, text_claim_coverage.json, canonical_claim_ledger_v2.json,
    # section_input_usage_ledger.json, x2_gate_outputs.json, fact_check_result.json,
    # l2_output fields) — rewritten by the lane closure so X3 sees real post-swap content.
    write_lane_artifacts(state, x2_after)

    record_repair(
        artifact_dir,
        kind=KIND_DETERMINISTIC_REWRITE,
        operation=RESELECTION_OPERATION,
        reason="x1d judge-feedback pool reselection (G14)",
        replaced_l2=True,
        detail={
            "section_id": section_id,
            "trigger_arm": plan.trigger_arm,
            "outcome": outcome,
            "slots": [s.to_receipt_dict() for s in plan.swaps],
            "receipt": RESELECTION_RECEIPT_FILENAME,
        },
    )

    receipt["fired"] = True
    receipt["outcome"] = outcome
    _write_json(receipt_path, receipt)

    return ReselectionResult(
        fired=True,
        outcome=outcome,
        receipt=receipt,
        parsed=state.parsed,
        bullets=state.bullets,
        claim_ledger=state.claim_ledger,
        parsed_for_x2=state.parsed_for_x2,
        x2=x2_after,
        x1d=active_x1d,
        usage_doc=state.usage_doc,
        canon_doc=state.canon_doc,
        display_text=state.display_text,
        receipt_written=True,
    )


__all__ = [
    "LaneRebuildState",
    "OUTCOME_DISABLED",
    "OUTCOME_NOT_FIRED",
    "OUTCOME_NO_COMPLIANT_ALTERNATE",
    "OUTCOME_REJUDGE_FAIL_FINAL",
    "OUTCOME_REJUDGE_PASS",
    "OUTCOME_REVERTED_REJUDGE_WORSE",
    "OUTCOME_REVERTED_X2_REGRESSION",
    "PRE_RESELECTION_SELECTION_FILENAME",
    "PRE_RESELECTION_X1D_SIDECAR_FILENAME",
    "PoolAlternates",
    "RECEIPT_VERSION",
    "RESELECTION_DISABLE_ENV",
    "RESELECTION_OPERATION",
    "RESELECTION_RECEIPT_FILENAME",
    "ReselectionPlan",
    "ReselectionResult",
    "SLOT_RESOLUTION_BULLET_ID_REGEX",
    "SLOT_RESOLUTION_CITED_SENTENCE_INDEXES",
    "SLOT_RESOLUTION_LOWEST_SELECTOR_SCORE",
    "SLOT_RESOLUTION_UNRESOLVED",
    "SlotSwap",
    "TRIGGER_ARM_DECISIVE",
    "TRIGGER_ARM_SOFT_FAIL",
    "apply_reselection",
    "build_reselection_plan",
    "load_pool_alternates",
    "run_bullet_judge_reselection",
]
