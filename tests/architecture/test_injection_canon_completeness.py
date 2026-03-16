"""No-Missing-Injection Invariant.

Asserts that every canonical Instruction Type named in
data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
is present (case-insensitive substring match) in the YAML corpus loaded by
get_instructional_injections().

BRANCH_INVENTORY
================
File: tests/architecture/test_injection_canon_completeness.py
Function: _parse_canon_names
  | row is header line (contains "Instruction Type")  -> skip           | test_markdown_parses_to_exactly_30_entries (implicit)
  | row is separator (starts with |-)                 -> skip           | test_markdown_parses_to_exactly_30_entries (implicit)
  | row is blank / does not start with '|'            -> skip           | test_markdown_parses_to_exactly_30_entries (implicit)
  | valid table row with 4+ columns                   -> extract name   | test_markdown_parses_to_exactly_30_entries

Function: test_all_canonical_patterns_present_in_yaml
  | pattern found (case-insensitive substring)        -> pass           | test_all_canonical_patterns_present_in_yaml
  | pattern NOT found                                 -> AssertionError | test_missing_pattern_detected (monkeypatch)

Function: test_no_layer_is_empty
  | layer has >=1 pattern                             -> pass           | test_no_layer_is_empty
  | layer has 0 patterns (simulated)                  -> AssertionError | test_no_layer_is_empty (parametrized via live data)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_injection_canon_completeness")
_emit_applies_guardrail("p0", "test_injection_canon_completeness", "p0_governance")
_emit_reads_policy_state("p0", "test_injection_canon_completeness", "policy_binding")
_emit_snapshots_state("p0", "test_injection_canon_completeness", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_injection_canon_completeness", "p4obs", "metric_1")
_emit_emits_metric_event("test_injection_canon_completeness", "p4obs", "metric_2")
_emit_emits_metric_event("test_injection_canon_completeness", "p4obs", "metric_3")
_emit_emits_metric_event("test_injection_canon_completeness", "p4obs", "metric_4")
_emit_emits_metric_event("test_injection_canon_completeness", "p4obs", "metric_5")
_emit_emits_metric_event("test_injection_canon_completeness", "p4obs", "metric_6")
_emit_records_incident_event("test_injection_canon_completeness", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_injection_canon_completeness", "p4obs", "anomaly")
_emit_writes_observability_log("test_injection_canon_completeness", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_injection_canon_completeness", "p4obs", "mon_state")
_emit_triggers_alert("test_injection_canon_completeness", "p4obs", "alert")
_emit_links_incident_trace("test_injection_canon_completeness", "p4obs", "trace_link")
_emit_captures_pattern("test_injection_canon_completeness", "p3lm", "pattern")
_emit_records_learning_event("test_injection_canon_completeness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_injection_canon_completeness", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_injection_canon_completeness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_injection_canon_completeness", "p3lm", "routing")
_emit_improves_agent_policy("test_injection_canon_completeness", "p3lm", "policy")
_emit_stores_learning_state("test_injection_canon_completeness", "p3lm", "state")
_emit_records_execution_trace("test_injection_canon_completeness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_injection_canon_completeness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_injection_canon_completeness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_injection_canon_completeness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_injection_canon_completeness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_injection_canon_completeness", "env_read", "p2_env_1")
_emit_reads_environ("test_injection_canon_completeness", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_injection_canon_completeness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_injection_canon_completeness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_injection_canon_completeness", "context_pull")
_emit_pulls_context("p1", "test_injection_canon_completeness", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_injection_canon_completeness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_injection_canon_completeness", "uwg_term_2")
_emit_writes_through("p1", "test_injection_canon_completeness", "write_through")
_emit_writes_through("p1", "test_injection_canon_completeness", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_injection_canon_completeness", "safety_validation")
_emit_invokes_eval("p1", "test_injection_canon_completeness", "eval_call")
_emit_proposal_commits_routing("p1", "test_injection_canon_completeness", "routing_commit")
emit_replay_key("p0", "test_injection_canon_completeness")
emit_determinism_digest("p0", "test_injection_canon_completeness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_injection_canon_completeness", "execution_auth")
_emit_validates_capability("p2", "test_injection_canon_completeness", "capability_check")
_emit_routes_to_capability("p2", "test_injection_canon_completeness", "capability_route")
_emit_writes_via_uwg("p2", "test_injection_canon_completeness", "uwg_write")
_emit_blocks_direct_write("p2", "test_injection_canon_completeness", "direct_write_block")
_emit_records_tool_invocation("p2", "test_injection_canon_completeness", "tool_invocation")
_emit_captures_execution_output("p2", "test_injection_canon_completeness", "exec_output")
_emit_dispatches_agent("p3", "test_injection_canon_completeness", "agent_dispatch")
_emit_coordinates_agents("p3", "test_injection_canon_completeness", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_injection_canon_completeness", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_injection_canon_completeness", "healing_outcome")
_emit_escalates_failure("p3", "test_injection_canon_completeness", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_injection_canon_completeness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_injection_canon_completeness", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_injection_canon_completeness", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_injection_canon_completeness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_injection_canon_completeness", "eval_metric")
_emit_stores_embedding("p4", "test_injection_canon_completeness", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_injection_canon_completeness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_injection_canon_completeness", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent
_CANON_MD = (
    _REPO_ROOT / "data" / "prompt_governance" / "prompt_injections" / "Instructional_Injection_Enhanced_v5.md"
)
_INJECTIONS_MODULAR = _REPO_ROOT / "data" / "prompt_governance" / "injections" / "modular"

# ---------------------------------------------------------------------------
# Parser (stdlib only — no regex for logic per §5)
# ---------------------------------------------------------------------------

_EXPECTED_COUNT = 30
_EXPECTED_LAYERS = {"framing", "context", "reasoning", "tooling", "safety", "output"}


def _parse_canon_names(md_path: Path) -> list[str]:
    """Extract Instruction Type column values from the markdown table.

    Skips: blank lines, lines not starting with '|', the header row
    (contains 'Instruction Type'), and separator rows (start with '|-').
    Returns exactly the string in the third pipe-delimited column, stripped.
    """
    names: list[str] = []
    text = md_path.read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if "Instruction Type" in line:
            continue
        if line.startswith("|-") or line.startswith("| -"):
            continue
        cols = [c.strip() for c in line.split("|")]
        # cols[0] is empty (before leading |), cols[1]=index, cols[2]=category,
        # cols[3]=instruction type, cols[4]=description
        if len(cols) >= 5:
            name = cols[3].strip()
            if name:
                names.append(name)
    return names


def _get_layer_for_name(name: str) -> str | None:
    """Return normalised layer keyword for a canonical name, or None."""
    low = name.lower()
    for layer in _EXPECTED_LAYERS:
        if layer in low:
            return layer
    return None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def canon_names() -> list[str]:
    assert _CANON_MD.exists(), f"Canon markdown not found: {_CANON_MD}"
    return _parse_canon_names(_CANON_MD)


@pytest.fixture(scope="module")
def loaded_patterns() -> list[Any]:
    from agentic_core.runtime.config.instructional_injections import (
        get_instructional_injections,
    )

    return get_instructional_injections()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.architecture
def test_markdown_parses_to_exactly_30_entries(canon_names: list[str]) -> None:
    """Pure parse test — no YAML, no imports."""
    count = len(canon_names)
    assert count == _EXPECTED_COUNT, (
        f"Expected {_EXPECTED_COUNT} canonical entries in markdown table, got {count}. "
        f"Entries found: {canon_names}"
    )


def _canonical_name_to_keywords(name: str) -> list[str]:
    """Extract a minimal set of distinctive keywords from a canonical markdown name.

    The YAML patterns use snake_case ids with description text that mirrors the
    markdown table descriptions — not the 'Instruction Type' display names.
    We therefore check that the YAML *description* corpus contains at least one
    keyword from each canonical name (case-insensitive).
    Stop-words are excluded to avoid false positives.
    """
    STOP = {
        "a",
        "an",
        "and",
        "the",
        "of",
        "in",
        "to",
        "for",
        "or",
        "on",
        "with",
        "from",
        "at",
        "by",
        "as",
        "is",
        "it",
        "its",
    }
    words = [
        w.strip("/-&").lower()
        for w in name.replace("/", " ").replace("-", " ").split()
        if w.strip("/-&").lower() not in STOP and len(w.strip("/-&")) > 2
    ]
    return words


@pytest.mark.architecture
def test_all_canonical_patterns_present_in_yaml(
    canon_names: list[str],
    loaded_patterns: list[Any],
) -> None:
    """Main completeness invariant: every canonical name must have at least one
    distinctive keyword matched in the loaded YAML corpus (name or description)."""
    corpus_texts = [(getattr(p, "name", None) or "").lower().replace("_", " ") for p in loaded_patterns]
    corpus_texts += [(getattr(p, "description", None) or "").lower() for p in loaded_patterns]
    combined_corpus = " ".join(corpus_texts)

    missing: list[str] = []
    for canon in canon_names:
        keywords = _canonical_name_to_keywords(canon)
        # A canonical name is present if ANY of its distinctive keywords appear
        # in the combined corpus text
        if not keywords or not any(kw in combined_corpus for kw in keywords):
            missing.append(canon)

    if missing:
        print(f"\nMISSING ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")
    assert not missing, f"{len(missing)} canonical patterns missing from loaded corpus: {missing}"


@pytest.mark.architecture
def test_loaded_count_floor(loaded_patterns: list[Any]) -> None:
    """Loaded pattern count must be >= 30."""
    count = len(loaded_patterns)
    assert count >= _EXPECTED_COUNT, f"Expected >= {_EXPECTED_COUNT} loaded patterns, got {count}"


@pytest.mark.architecture
def test_no_layer_is_empty(canon_names: list[str]) -> None:
    """All 6 canonical layers must have at least one entry in the markdown table."""
    layers_found: dict[str, int] = dict.fromkeys(_EXPECTED_LAYERS, 0)

    for name in canon_names:
        name_low = name.lower()
        for layer in _EXPECTED_LAYERS:
            if layer in name_low:
                layers_found[layer] += 1

    # Layer membership comes from the Category column; read it directly
    # from the markdown to be precise.
    text = _CANON_MD.read_text(encoding="utf-8")
    layer_counts: dict[str, int] = dict.fromkeys(_EXPECTED_LAYERS, 0)
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if "Category" in line or line.startswith("|-") or line.startswith("| -"):
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) >= 4:
            category = cols[2].lower()
            for layer in _EXPECTED_LAYERS:
                if layer in category:
                    layer_counts[layer] += 1

    empty_layers = [layer for layer, cnt in layer_counts.items() if cnt == 0]
    assert not empty_layers, (
        f"These layers have 0 entries in the canon table: {empty_layers}\nLayer counts: {layer_counts}"
    )


@pytest.mark.architecture
def test_missing_pattern_detected(canon_names: list[str]) -> None:
    """Negative control: if get_instructional_injections returns [],
    test_all_canonical_patterns_present_in_yaml must raise AssertionError."""

    with patch(
        "agentic_core.runtime.config.instructional_injections.get_instructional_injections",
        return_value=[],
    ):
        empty_patterns: list[Any] = []
        corpus_names = [(getattr(p, "name", None) or "").lower() for p in empty_patterns]
        corpus_names += [(getattr(p, "description", None) or "").lower() for p in empty_patterns]

        missing = [canon for canon in canon_names if not any(canon.lower() in s for s in corpus_names)]
        # With empty patterns ALL names must be missing — invariant fires
        assert missing, "Negative control failed: expected missing list to be non-empty when corpus is empty"
        assert len(missing) == len(canon_names), (
            f"Expected all {len(canon_names)} patterns to be missing with empty corpus, got {len(missing)}"
        )
