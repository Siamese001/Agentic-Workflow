"""Post-agent runtime-RCA audit (Stop chain, constitutional §37).

Flags a repo-work response that reports a RUNTIME FAILURE without a mandatory RCA block,
and flags a green status (PASS/PARTIAL) stamped over a body that carries a runtime-failure
signal (the "green-theater" pattern). Violations land in
``artifacts/governance/runtime_rca_violations.jsonl``.

A response is "repo-work" when it carries a ``STATUS:`` line (the rule-001 response floor).
A "runtime failure" is ``STATUS: FAIL`` OR any failure signal in the receipt — ``X3_BLOCK``,
a Python traceback, a non-zero exit, a pytest ``N failed``, ``PRE_RUN_BLOCKED``, or a
``BLOCKED_*`` / ``MISSING_GRAPH_PATH`` verdict. ``BLOCKED`` status alone is not a failure
(the proof contract already makes it name its blocker); only a co-present failure signal
demands an RCA.

The RCA block (rule 001 § Runtime failure ⇒ RCA mandatory):
    RCA:
    - symptom: ...
    - root_cause: ... [DIRECTLY OBSERVED | DERIVED | UNRESOLVED]
    - evidence: ...
    - fix_or_next: ...
    - recurrence_guard: ...

On REFACTORING turns (code files changed / an edit tool invoked) the response MUST carry the
Outcome frame on EVERY turn (pass or fail) — "Did it run?" + verdict source + provenance,
What worked, Failure, Next. The frame proves the STATUS verdict (it does not re-vote pass/fail);
its presence is keyed on the ``Verdict source:`` line. Its absence is ``missing_refactor_outcome``. A failure
additionally requires the deep Layered RCA inside that frame — the failing layer isolated from
the surfacing layer, a multi-level why-chain (dig until root, >= 2 levels), a root cause
distinct from the symptom, a stated **confidence** in that root cause, and a **next step coupled
to the diagnosis** (not a bare platitude like "fix the bug"). A symptom-only / single-hop RCA, a
root cause asserted with no confidence, or a generic non-actionable next step is ``shallow_rca``.

It also flags a repo-work turn that dropped the response floor entirely: a final output carrying a
floor signal (FILES_CHANGED / COMMANDS_RUN / TESTS_GATES / ARTIFACTS / REPORTS_GENERATED) or an
edit-tool invocation but NO ``STATUS:`` line (rule 001 § Canonical post-turn output — one template).
High-precision: the dispatcher feeds only the final assistant prose, so this catches malformed/partial
floors, not every prose wrap-up after a code turn; pure prose with no floor signal stays clean.
``generate_full_adg`` / ``run_full_adg_audit`` / ``adg_gates`` runs are EXEMPT from this entire audit —
their BCG burndown + gates output supersedes both the floor and the Outcome frame and is owned by
post_agent_adg_burndown_inline_audit.py.

Violation kinds: missing_response_floor, missing_refactor_outcome, missing_plan_waves,
malformed_plan_waves, missing_rca, incomplete_rca, status_signal_mismatch, shallow_rca,
pass_without_proof, speculative_pass.

This audit is advisory and fail-open: it always exits 0 and never blocks the response.
Some matches are necessarily heuristic (a PASS summary that merely *discusses* a failure
token in prose can self-trigger); the JSONL is a review surface, not a hard gate.

Bypass: RUNTIME_RCA_AUDIT_BYPASS=1
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Sibling import of the SSOT payload extractor (check_post_agent_payload.py forbids a
# hand-rolled parser). Ensure this script's own dir is importable both as a subprocess
# (run by after_agent_governance_dispatch.py) and when importlib-loaded in tests.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _post_agent_payload import extract_response_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_FILE = REPO_ROOT / "artifacts" / "governance" / "runtime_rca_violations.jsonl"

# A response is a repo-work receipt when it carries a STATUS line.
_STATUS_RE = re.compile(r"(?im)^\s*STATUS:\s*(PASS|PARTIAL|FAIL|BLOCKED)\b")
# A green/optimistic status that must not sit over a failure signal.
_GREEN_STATUS_RE = re.compile(r"(?im)^\s*STATUS:\s*(?:PASS|PARTIAL)\b")

# Runtime-failure signals that demand an RCA when present in a repo-work receipt.
_FAILURE_SIGNALS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?im)^\s*STATUS:\s*FAIL\b"), "status_fail"),
    (re.compile(r"\bX3_BLOCK\b"), "x3_block"),
    (re.compile(r"\bPRE_RUN_BLOCKED\b"), "pre_run_blocked"),
    (re.compile(r"Traceback \(most recent call last\)"), "python_traceback"),
    (re.compile(r"\b[1-9]\d*\s+failed\b"), "pytest_failed"),
    (re.compile(r"(?i)\bexit(?:\s*code)?\s*[1-9]\d*\b"), "nonzero_exit"),
    (re.compile(r"\bMISSING_GRAPH_PATH\b"), "missing_graph_path"),
    (re.compile(r"\bBLOCKED_[A-Z_]{3,}\b"), "blocked_verdict"),
    (re.compile(r"\bAssertionError\b"), "assertion_error"),
)

# RCA block + its required sub-fields.
_RCA_MARKER_RE = re.compile(r"(?im)^\s*(?:\*\*\s*)?(?:layered\s+)?rca\b")
_RCA_ROOT_CAUSE_RE = re.compile(r"(?i)root[_ ]cause\s*:")
_RCA_EVIDENCE_RE = re.compile(r"(?i)\bevidence\s*:")
_RCA_FIXNEXT_RE = re.compile(r"(?i)(?:fix[_ ]or[_ ]next|fix|next[_ ]step|next)\s*:")
_RCA_SYMPTOM_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:immediate\s+)?symptom\s*:")

# Layered RCA (refactoring turns) — the deep symptom -> root descent.
_LAYERED_LAYER_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?failing\s+layer\s*:")
_LAYERED_MECH_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?mechanism\s*:")
_WHY_LEVEL_RE = re.compile(r"(?im)^\s*(?:└─\s*|[-*]\s*)?why\s*\d+\s*:")
# High confidence in the root cause must be *stated*, not implied — the frame's
# "Confidence / unknowns:" line. Its absence means the dig stopped without grading certainty.
_LAYERED_CONFIDENCE_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?confidence\b")
# A next step is "deep-reasoning-derived" only when it names a concrete action; a bare platitude
# (the WHOLE next-step value matches one of these) is decoupled from the diagnosis above it.
_GENERIC_NEXT_FULL_RE = re.compile(
    r"^(?:"
    r"fix(?:\s+(?:the|it|this))?(?:\s+(?:bug|code|issue|error|problem|tests?|it))?|"
    r"debug(?:\s+(?:it|this|further))?|"
    r"investigate(?:\s+(?:it|this|further|more))?|"
    r"look\s+into\s+(?:it|this)|"
    r"figure\s+(?:it|this)?\s*out|"
    r"resolve\s+(?:the\s+)?(?:issue|problem|error|bug)|"
    r"tbd|unclear|unknown|retry(?:\s+it)?"
    r")\.?$"
)

# Refactoring-turn signals: code files changed or an edit tool was invoked.
_FILES_CHANGED_RE = re.compile(r"(?im)^\s*FILES_CHANGED\s*:")
_CODE_FILE_RE = re.compile(r"\.(?:py|js|ts|tsx|jsx|go|rs|java|rb|c|cc|cpp|h|hpp|sql|sh|ps1)\b")
_EDIT_TOOL_RE = re.compile(r'<invoke\s+name="(?:Edit|Write|MultiEdit|NotebookEdit)"')

# Outcome frame: refactoring turns must carry it on EVERY turn (pass or fail). The frame
# proves the STATUS verdict (it does not re-vote pass/fail); "Verdict source:" is its
# load-bearing line — the runtime evidence the bare STATUS floor never carries — so frame
# presence keys on it, not on a duplicate pass/fail vote.
_OUTCOME_FRAME_RE = re.compile(r"(?i)verdict\s+source\s*:")

# Repo-work signals that should never appear WITHOUT a STATUS floor. A final message that
# carries any of these but no STATUS: line is a dropped/partial response floor — the dominant
# format-drift mode (rule 001 § Canonical post-turn output). High-precision by design: the
# dispatcher feeds only the final assistant prose (no tool history), so this catches malformed/
# partial floors, not every prose wrap-up after a code turn. Pure prose with no floor signal and
# no STATUS line stays clean (a question / T0 lookup is not repo work).
_REPO_WORK_SIGNALS: tuple[tuple[re.Pattern[str], str], ...] = (
    (_FILES_CHANGED_RE, "files_changed"),
    (re.compile(r"(?im)^\s*COMMANDS_RUN\s*:"), "commands_run"),
    (re.compile(r"(?im)^\s*TESTS_GATES\s*:"), "tests_gates"),
    (re.compile(r"(?im)^\s*PLAN_WAVES\s*:"), "plan_waves"),
    (re.compile(r"(?im)^\s*ARTIFACTS\s*:"), "artifacts"),
    (re.compile(r"(?im)^\s*REPORTS_GENERATED\s*:"), "reports_generated"),
    (_EDIT_TOOL_RE, "edit_tool_invoked"),
)

# ADG generate/audit runs have their OWN output contract — the BCG-grade burndown + gates table
# (adg-post-run-burndown.md § Completion Gate, audited by post_agent_adg_burndown_inline_audit.py).
# That output SUPERSEDES both the response floor AND the Outcome-frame requirement, so an ADG-run turn
# is exempt from this entire audit. Signal mirrors that audit's _RUN_PATTERNS (rule 001 § Canonical
# post-turn output, point 3).
_ADG_RUN_RE: tuple[re.Pattern[str], ...] = (
    re.compile(r"generate_full_adg\.py", re.IGNORECASE),
    re.compile(r"run_full_adg_audit\.py", re.IGNORECASE),
    re.compile(r"adg_gates[\\/]run\.py", re.IGNORECASE),
)

_REMEDY = (
    "Add an RCA: block to the response (symptom · root_cause[graded §20] · evidence · "
    "fix_or_next[§7] · recurrence_guard). Never stamp PASS/PARTIAL over a runtime-failure "
    "signal. SSOT: .claude/rules/001-runtime-seam-execution.md § Runtime failure ⇒ "
    "RCA mandatory; constitutional §37."
)

_SHALLOW_REMEDY = (
    "Refactoring turn: the 5-field RCA is not enough. Emit the Layered RCA — Immediate symptom "
    "-> Failing layer (isolate from the surfacing layer) -> Why-chain (dig until root, >=2 "
    "levels) -> Root cause (distinct from the symptom) -> Evidence -> Confidence/unknowns -> Next "
    "(a concrete action coupled to the root cause, not 'fix the bug'). Apply the 'but why?' test "
    "until you reach a cause you can act on, then state your confidence in it. SSOT: 001 § Runtime "
    "failure ⇒ RCA mandatory; constitutional §37."
)

_MISSING_OUTCOME_REMEDY = (
    "Refactoring turn: report it in the Outcome frame (Did it run? + verdict source + runtime "
    "provenance; What worked; Failure; Next) — the frame proves the STATUS verdict, it does not "
    "re-vote pass/fail — not the bare STATUS floor. On a failure the frame's Layered RCA is also "
    "required. SSOT: 001 § Runtime failure ⇒ RCA mandatory; constitutional §37."
)

_MISSING_FLOOR_REMEDY = (
    "Repo-work turn with no response floor: this output changed files / ran commands / exercised "
    "tests but carries no STATUS: line. End every repo-work turn with the rule-001 floor (STATUS · "
    "FILES_CHANGED · COMMANDS_RUN · TESTS_GATES · ARTIFACTS · NOTES) — it is the base template, not "
    "one option among several; domain/Outcome blocks layer on top, never replace it. SSOT: "
    ".claude/rules/001-runtime-seam-execution.md § Canonical post-turn output; § Response floor."
)


_PROOF_SECTIONS: tuple[str, ...] = ("FILES_CHANGED", "COMMANDS_RUN", "TESTS_GATES", "ARTIFACTS")
_PLAN_WAVES_RE = re.compile(r"(?im)^\s*PLAN_WAVES\s*:")
_PLAN_MARKER_RE = re.compile(
    r"(?im)^\s*(?:WAVE_START|WAVE_COMPLETE|PHASE_COMPLETE|PLAN_COMPLETE)\s*:"
)
_PLAN_STATE_RE = re.compile(r"(?im)^\s*(?:CURRENT_WAVE|LAST_COMPLETED_WAVE)\s*:")
_PLAN_FILE_RE = re.compile(
    r"(?im)^\s*-\s*(?:\[[^\]]+\]\()?\.?(?:plans|\.claude/plans)/[^)\s]+\.md\)?"
)
_RECEIPT_SECTION_RE = re.compile(
    r"(?im)^\s*(?:STATUS|BRANCH|FILES_CHANGED|COMMANDS_RUN|TESTS_GATES|RCA|ARTIFACTS|"
    r"REPORTS_GENERATED|NOTES)\s*:"
)
_SPECULATIVE_RE = re.compile(r"(?i)\bshould\s+pass\b|\blikely\s+pass\b")
_PASS_PROOF_REMEDY = (
    "STATUS: PASS is expensive — it requires every proof section (FILES_CHANGED · COMMANDS_RUN · "
    "TESTS_GATES · ARTIFACTS; use 'NONE' where empty). A PASS missing one is unproven. SSOT: "
    ".claude/rules/002-pass-blocked-proof-contract.md § PASS is expensive."
)
_SPECULATIVE_REMEDY = (
    "Speculative pass language ('should pass' / 'likely pass') is forbidden — either it passed, "
    "failed, is partial, or is blocked, with evidence. Emit STATUS: PASS|PARTIAL|FAIL|BLOCKED. "
    "SSOT: .claude/rules/002-pass-blocked-proof-contract.md § Forbidden status behavior."
)
_PLAN_WAVES_REMEDY = (
    "Active multi-wave work must include the Turn Receipt PLAN_WAVES mini table with columns "
    "Wave | State | Summary. Include completed waves (or NONE / COMPLETE / No completed waves yet) "
    "and the current OPEN wave with a brief description. This is post-turn output, not the plan "
    "file's disk-side status table. SSOT: .claude/rules/001-runtime-seam-execution.md § Response floor."
)


def _bypass_active() -> bool:
    return os.environ.get("RUNTIME_RCA_AUDIT_BYPASS", "").strip().lower() in ("1", "true", "yes")


def _append_violation(record: dict) -> None:
    try:
        VIOLATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _excerpt(text: str, pattern: re.Pattern[str]) -> str:
    m = pattern.search(text)
    if not m:
        return ""
    start = max(0, m.start() - 80)
    end = min(len(text), m.end() + 80)
    return text[start:end].strip()


def _is_refactor_turn(text: str) -> bool:
    """A code-change turn: an edit tool was invoked, or FILES_CHANGED lists a code file."""
    if _EDIT_TOOL_RE.search(text):
        return True
    return bool(_FILES_CHANGED_RE.search(text) and _CODE_FILE_RE.search(text))


def _line_value(text: str, pattern: re.Pattern[str]) -> str:
    """Normalized text from the end of the first label match to end-of-line."""
    m = pattern.search(text)
    if not m:
        return ""
    nl = text.find("\n", m.end())
    seg = text[m.end(): nl if nl != -1 else len(text)]
    return re.sub(r"\s+", " ", seg).strip().lower()


def _plan_activity_signals(text: str) -> list[str]:
    signals: list[str] = []
    if _PLAN_WAVES_RE.search(text):
        signals.append("plan_waves")
    if _PLAN_MARKER_RE.search(text):
        signals.append("wave_marker")
    if _PLAN_STATE_RE.search(text):
        signals.append("plan_state_marker")
    if _PLAN_FILE_RE.search(text):
        signals.append("plan_file_changed")
    return signals


def _extract_plan_waves_block(text: str) -> str:
    match = _PLAN_WAVES_RE.search(text)
    if not match:
        return ""
    lines: list[str] = []
    for line in text[match.end():].splitlines():
        if _RECEIPT_SECTION_RE.match(line):
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _state_family(cell: str) -> str:
    raw = cell.strip().lower().replace("-", "_")
    if any(token in raw for token in ("complete", "done", "pass")):
        return "complete"
    if any(token in raw for token in ("open", "current", "active", "in_progress", "in progress")):
        return "open"
    return ""


def _summary_present(cell: str) -> bool:
    raw = re.sub(r"\s+", " ", cell).strip()
    return len(raw) >= 8 and raw.lower() not in {"n/a", "na", "none", "-", "tbd"}


def _parse_plan_waves_rows(block: str) -> tuple[list[dict[str, str]], str]:
    wave_idx = state_idx = summary_idx = -1
    rows: list[dict[str, str]] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        lower = [cell.lower() for cell in cells]
        if wave_idx == -1:
            if "wave" in lower and "state" in lower and "summary" in lower:
                wave_idx = lower.index("wave")
                state_idx = lower.index("state")
                summary_idx = lower.index("summary")
            continue
        if len(cells) <= max(wave_idx, state_idx, summary_idx):
            continue
        rows.append(
            {
                "wave": cells[wave_idx],
                "state": cells[state_idx],
                "summary": cells[summary_idx],
            }
        )
    if wave_idx == -1:
        return [], "missing markdown table header: | Wave | State | Summary |"
    return rows, ""


def _plan_waves_issue(text: str) -> tuple[str, dict] | None:
    signals = _plan_activity_signals(text)
    if not signals:
        return None
    if not _PLAN_WAVES_RE.search(text):
        return (
            "missing_plan_waves",
            {
                "plan_wave_signals": signals,
                "plan_waves_reason": "multi-wave activity signal present but PLAN_WAVES is absent",
            },
        )
    block = _extract_plan_waves_block(text)
    if not block:
        return (
            "malformed_plan_waves",
            {
                "plan_wave_signals": signals,
                "plan_waves_reason": "PLAN_WAVES has no table body",
            },
        )
    rows, row_error = _parse_plan_waves_rows(block)
    if row_error:
        return (
            "malformed_plan_waves",
            {"plan_wave_signals": signals, "plan_waves_reason": row_error},
        )
    if not rows:
        return (
            "malformed_plan_waves",
            {
                "plan_wave_signals": signals,
                "plan_waves_reason": "PLAN_WAVES table has no data rows",
            },
        )
    has_complete = any(_state_family(row["state"]) == "complete" for row in rows)
    open_row_count = sum(1 for row in rows if _state_family(row["state"]) == "open")
    blank_summaries = [row["wave"] for row in rows if not _summary_present(row["summary"])]
    if not has_complete or open_row_count != 1 or blank_summaries:
        return (
            "malformed_plan_waves",
            {
                "plan_wave_signals": signals,
                "plan_waves_reason": "PLAN_WAVES must include completed rows and exactly one open row with summaries",
                "has_completed_row": has_complete,
                "has_open_row": open_row_count == 1,
                "open_row_count": open_row_count,
                "rows_missing_summary": blank_summaries,
            },
        )
    return None


def _rca_descent_depth(text: str) -> int:
    """Count distinct 'but why?' descent levels in a Layered RCA.

    Failing-layer and Mechanism each count as one descent level; every explicit
    ``whyN:`` ladder line adds another. A real root-cause dig traverses >= 2.
    """
    depth = len(_WHY_LEVEL_RE.findall(text))
    depth += 1 if _LAYERED_LAYER_RE.search(text) else 0
    depth += 1 if _LAYERED_MECH_RE.search(text) else 0
    return depth


def detect(text: str) -> tuple[str | None, list[dict]]:
    """Return (status_value_or_None, violation_records).

    status None => not a repo-work receipt (no STATUS line) => caller no-ops.
    """
    # generate_full_adg / run_full_adg_audit / adg_gates runs are governed SOLELY by the BCG burndown +
    # gates contract (adg-post-run-burndown.md, audited by post_agent_adg_burndown_inline_audit.py).
    # That output supersedes BOTH the response floor and the Outcome-frame requirement, so the
    # runtime-rca audit defers entirely for ADG runs (rule 001 § Canonical post-turn output, point 3).
    if any(rx.search(text) for rx in _ADG_RUN_RE):
        return None, []

    status_match = _STATUS_RE.search(text)
    if not status_match:
        # No STATUS floor. If the turn still carries a repo-work signal (a secondary floor label or
        # an edit-tool invocation) it is a dropped/partial response floor — flag missing_response_floor.
        # Pure prose with no repo-work signal is a question / non-repo turn and stays clean.
        repo_signals = [name for rx, name in _REPO_WORK_SIGNALS if rx.search(text)]
        if not repo_signals:
            return None, []
        first_rx = next(rx for rx, _name in _REPO_WORK_SIGNALS if rx.search(text))
        rec = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "kind": "missing_response_floor",
            "status": "NONE",
            "refactor_turn": _is_refactor_turn(text),
            "has_outcome_frame": bool(_OUTCOME_FRAME_RE.search(text)),
            "failure_signals": [],
            "repo_work_signals": repo_signals,
            "excerpt": _excerpt(text, first_rx),
            "remedy": _MISSING_FLOOR_REMEDY,
            "rule_ref": "constitutional §37 / 001 § Canonical post-turn output",
        }
        return None, [rec]
    status_value = status_match.group(1).upper()

    signals = [name for rx, name in _FAILURE_SIGNALS if rx.search(text)]
    has_rca = bool(_RCA_MARKER_RE.search(text))
    rca_complete = (
        has_rca
        and bool(_RCA_ROOT_CAUSE_RE.search(text))
        and (bool(_RCA_EVIDENCE_RE.search(text)) or bool(_RCA_FIXNEXT_RE.search(text)))
    )
    refactor_turn = _is_refactor_turn(text)
    has_outcome = bool(_OUTCOME_FRAME_RE.search(text))

    violations: list[dict] = []
    ts = datetime.now(timezone.utc).isoformat()
    rule_ref = "constitutional §37 / 001 § Runtime failure ⇒ RCA mandatory"

    def _record(kind: str, signal_set: list[str], extra: dict | None = None) -> dict:
        rec = {
            "ts_utc": ts,
            "kind": kind,
            "status": status_value,
            "refactor_turn": refactor_turn,
            "has_outcome_frame": has_outcome,
            "failure_signals": signal_set,
            "has_rca": has_rca,
            "rca_complete": rca_complete,
            "excerpt": _excerpt(text, _FAILURE_SIGNALS[0][0] if "status_fail" in signal_set else _STATUS_RE),
            "remedy": _REMEDY,
            "rule_ref": rule_ref,
        }
        if extra:
            rec.update(extra)
        return rec

    # speculative_pass: 'should pass' / 'likely pass' language is forbidden on any repo-work turn.
    if _SPECULATIVE_RE.search(text):
        violations.append({
            "ts_utc": ts,
            "kind": "speculative_pass",
            "status": status_value,
            "refactor_turn": refactor_turn,
            "has_outcome_frame": has_outcome,
            "failure_signals": [],
            "remedy": _SPECULATIVE_REMEDY,
            "rule_ref": "constitutional §37 / 002 § Forbidden status behavior",
        })

    # pass_without_proof: STATUS:PASS is expensive — requires all four proof sections.
    if status_value == "PASS":
        _missing_proof = [
            s for s in _PROOF_SECTIONS
            if not re.search(rf"(?im)^\s*{s}\s*:", text)
        ]
        if _missing_proof:
            violations.append(
                _record("pass_without_proof", [], extra={"missing_proof": _missing_proof, "remedy": _PASS_PROOF_REMEDY})
            )

    plan_waves_issue = _plan_waves_issue(text)
    if plan_waves_issue:
        kind, extra = plan_waves_issue
        extra.setdefault("remedy", _PLAN_WAVES_REMEDY)
        extra.setdefault("rule_ref", "001 § Response floor / PLAN_WAVES")
        violations.append(_record(kind, [], extra=extra))

    # Green-theater: an optimistic status over a body failure signal (excludes the
    # status_fail signal itself, which is not "green").
    body_signals = [s for s in signals if s != "status_fail"]
    if _GREEN_STATUS_RE.search(text) and body_signals:
        violations.append(_record("status_signal_mismatch", body_signals))

    # Refactoring turns must carry the Outcome frame on EVERY turn (pass or fail), not
    # only on failure — passing turns that fall back to the bare STATUS floor are the most
    # common gap. A frame-less refactor turn is flagged here and subsumes the failure-path
    # RCA checks below (the frame is where the Layered RCA would live).
    if refactor_turn and not has_outcome:
        violations.append(
            _record("missing_refactor_outcome", signals, extra={"remedy": _MISSING_OUTCOME_REMEDY})
        )
        return status_value, violations

    if not signals:
        return status_value, violations

    # Any failure signal demands an RCA block.
    if not has_rca:
        violations.append(_record("missing_rca", signals))
        return status_value, violations
    if not rca_complete:
        violations.append(_record("incomplete_rca", signals))
        return status_value, violations

    # Refactoring turns must carry the DEEP Layered RCA: the failing layer isolated
    # from the surfacing layer, a multi-level why-chain, and a root cause distinct
    # from the symptom. Stopping at the symptom (shallow descent) is non-compliant.
    if refactor_turn:
        depth = _rca_descent_depth(text)
        symptom_txt = _line_value(text, _RCA_SYMPTOM_RE)
        root_txt = _line_value(text, _RCA_ROOT_CAUSE_RE)
        symptom_equals_root = bool(symptom_txt) and bool(root_txt) and (
            symptom_txt == root_txt or symptom_txt in root_txt or root_txt in symptom_txt
        )
        missing_layer = not bool(_LAYERED_LAYER_RE.search(text))
        # High confidence in the root cause must be stated, not implied.
        missing_confidence = not bool(_LAYERED_CONFIDENCE_RE.search(text))
        # The next step must derive from the diagnosis; a bare platitude does not.
        next_txt = _line_value(text, _RCA_FIXNEXT_RE)
        next_step_generic = bool(next_txt) and bool(_GENERIC_NEXT_FULL_RE.match(next_txt))
        if (
            depth < 2
            or symptom_equals_root
            or missing_layer
            or missing_confidence
            or next_step_generic
        ):
            violations.append(
                _record(
                    "shallow_rca",
                    signals,
                    extra={
                        "descent_depth": depth,
                        "symptom_equals_root": symptom_equals_root,
                        "missing_failing_layer": missing_layer,
                        "missing_confidence": missing_confidence,
                        "next_step_generic": next_step_generic,
                        "remedy": _SHALLOW_REMEDY,
                    },
                )
            )

    return status_value, violations


def main() -> int:
    try:
        if _bypass_active():
            return 0
        raw = sys.stdin.read()
        text = extract_response_text(raw)
        if not text.strip():
            return 0

        _status, violations = detect(text)
        for record in violations:
            _append_violation(record)
            signals = record.get("failure_signals") or record.get("repo_work_signals") or []
            hint = {
                "missing_response_floor": "end the turn with the rule-001 STATUS floor",
                "pass_without_proof": "add all proof sections (FILES_CHANGED · COMMANDS_RUN · TESTS_GATES · ARTIFACTS; 'NONE' where empty)",
                "speculative_pass": "replace speculative language with STATUS: PASS|PARTIAL|FAIL|BLOCKED + evidence",
                "missing_plan_waves": "add the PLAN_WAVES completed/open mini table",
                "malformed_plan_waves": "fix PLAN_WAVES to a Wave | State | Summary table with completed and open rows",
            }.get(record["kind"], "add an RCA: block")
            print(
                f"[runtime-rca] {record['kind']}: status={record['status']} "
                f"signals={signals} — {hint} (rule 001 / constitutional §37).",
                file=sys.stderr,
            )
        return 0
    except Exception:  # guardian: allow-broad-exception -- hook fail-soft contract
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
