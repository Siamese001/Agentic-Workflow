# Root-level conftest.py — loaded by pytest BEFORE any test collection
# This ensures the repo root is on sys.path so tools.adg, apps_*, etc. are importable
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT_PATH = Path(__file__).resolve().parent
_REPO_ROOT = str(_REPO_ROOT_PATH)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# ---------------------------------------------------------------------------
# ADG-driven test marker hook
# ---------------------------------------------------------------------------
# Reads `artifacts/test_inventory/test_adg_classification.json` (produced by
# `python tools/analysis/test_adg_classifier.py`) and applies markers to every
# collected test item based on its file's classification:
#
#   - adg_runtime    : file touches L2/L3 production AND has semantic edges
#   - adg_behavioral : file imports production AND has semantic edges
#   - adg_contract   : file imports production but only via `imports` edges
#   - adg_tooling    : file imports tools/ or ops_scripts/ only
#   - adg_stdlib     : file has no production or tooling imports
#   - adg_otel       : file imports an OTel/telemetry/trace node
#   - adg_safety     : file imports an L5 safety node
#
# These markers let you run signal-first slices without deleting any tests:
#
#   pytest -m adg_runtime                  # ~42 files, the strongest signal
#   pytest -m "adg_runtime or adg_behavioral"  # 97 files of real exercise
#   pytest -m "not adg_stdlib"             # everything except pure stdlib/fixtures
#   pytest -m adg_otel                     # OTel-touching tests only
#
# The hook is fail-soft: if the classification JSON is missing or malformed
# the suite collects normally without markers — discovery never breaks.
_ADG_CLASSIFICATION_PATH = _REPO_ROOT_PATH / "artifacts" / "test_inventory" / "test_adg_classification.json"
_ADG_FILE_MARKERS_CACHE: dict[str, list[str]] | None = None


def _load_adg_file_markers() -> dict[str, list[str]]:
    """Build {test_file_relpath: [marker_name, ...]} from the ADG classification JSON."""
    global _ADG_FILE_MARKERS_CACHE  # noqa: PLW0603 — module-level cache is intentional
    if _ADG_FILE_MARKERS_CACHE is not None:
        return _ADG_FILE_MARKERS_CACHE
    cache: dict[str, list[str]] = {}
    if not _ADG_CLASSIFICATION_PATH.is_file():
        _ADG_FILE_MARKERS_CACHE = cache
        return cache
    try:
        rows: list[dict[str, Any]] = json.loads(_ADG_CLASSIFICATION_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        _ADG_FILE_MARKERS_CACHE = cache
        return cache

    cls_to_marker = {
        "production_runtime": "adg_runtime",
        "production_behavioral": "adg_behavioral",
        "production_contract": "adg_contract",
        "tooling_only": "adg_tooling",
        "stdlib_only": "adg_stdlib",
    }
    for row in rows:
        if not isinstance(row, dict):
            continue
        rel = row.get("file")
        if not isinstance(rel, str) or not rel:
            continue
        markers: list[str] = []
        primary = cls_to_marker.get(row.get("test_class", ""))
        if primary:
            markers.append(primary)
        if row.get("touches_otel_node"):
            markers.append("adg_otel")
        if row.get("touches_safety_node"):
            markers.append("adg_safety")
        # Per-layer markers (adg_l0 .. adg_l6) from agentic_core/L<N>_* imports
        layers = row.get("agentic_core_layers", [])
        if isinstance(layers, list):
            for layer in layers:
                if (
                    isinstance(layer, str)
                    and len(layer) == 2
                    and layer.startswith("L")
                    and layer[1].isdigit()
                ):
                    markers.append(f"adg_{layer.lower()}")
        # Per-app markers (adg_apps_<name>) from apps_<name>/ imports
        apps = row.get("apps_targets", [])
        if isinstance(apps, list):
            for app in apps:
                if isinstance(app, str) and app.startswith("apps_"):
                    markers.append(f"adg_{app}")
        if markers:
            cache[rel] = markers
    _ADG_FILE_MARKERS_CACHE = cache
    return cache


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Apply ADG-derived markers to every collected test item by file."""
    file_markers = _load_adg_file_markers()
    if not file_markers:
        return
    for item in items:
        # item.nodeid is "tests/path/test_file.py::TestClass::test_fn[param]" or
        # "tests/path/test_file.py::test_fn"
        file_rel = item.nodeid.split("::", 1)[0]
        for marker_name in file_markers.get(file_rel, ()):
            item.add_marker(getattr(pytest.mark, marker_name))


# ---------------------------------------------------------------------------
# Discovery-time ignore list (now empty)
# ---------------------------------------------------------------------------
# Previously held ~80 paths whose imports failed against the current code base
# (modules removed in refactors, symbols renamed, planned APIs that never
# shipped). Those files have all been physically moved to
# `tests/_archived_obsolete/` and the directory is excluded via
# `norecursedirs` in `pytest.ini`. See that directory's README.md for the
# rationale and restoration procedure.
_collect_ignore_archived: list[str] = [  # kept for historical reference only
    # Broken conftest.py — entire directory uncollectable until module is restored
    "tests/agentic_core/L3_orchestration/exit_eval",
    "tests/agentic_core/L5_safety/identity",
    # Individual test modules with ImportError / ModuleNotFoundError
    "tests/agentic_core/L0_routing/enforcement/test_boot_sequence.py",
    "tests/agentic_core/L0_routing/test_boot_sequence.py",
    "tests/agentic_core/L1_cognition/enforcement/test_consensus_validator.py",
    "tests/agentic_core/L1_cognition/enforcement/test_plan_semantic_validators.py",
    "tests/agentic_core/L1_cognition/enforcement/test_reasoning_chokepoint.py",
    "tests/agentic_core/L1_cognition/enforcement/test_spiffe_validator.py",
    "tests/agentic_core/L1_cognition/enforcement/test_truth_keeper_validator.py",
    "tests/agentic_core/L1_cognition/reasoning/test_constitutional_rules_engine.py",
    "tests/agentic_core/L1_cognition/reasoning/test_intent_parser.py",
    "tests/agentic_core/L1_cognition/reasoning/test_knowledge_orchestrator.py",
    "tests/agentic_core/L1_cognition/reasoning/test_meta_client.py",
    "tests/agentic_core/L1_cognition/reasoning/test_reasoning_evaluation.py",
    "tests/agentic_core/L1_cognition/reasoning/test_reasoning_knowledge.py",
    "tests/agentic_core/L1_cognition/reasoning/test_reasoning_plan.py",
    "tests/agentic_core/L1_cognition/reasoning/test_reranking_engine.py",
    "tests/agentic_core/L1_cognition/reasoning/test_safety_evaluator.py",
    "tests/agentic_core/L1_cognition/reasoning/test_search_fusion_engine.py",
    "tests/agentic_core/L2_execution/enforcement/test_durable_write_wrapper.py",
    "tests/agentic_core/L2_execution/enforcement/test_egress_proxy.py",
    "tests/agentic_core/L2_execution/enforcement/test_execution_guardrail_chokepoint.py",
    "tests/agentic_core/L2_execution/enforcement/test_kill_switch.py",
    "tests/agentic_core/L2_execution/enforcement/test_network_egress_guard.py",
    "tests/agentic_core/L2_execution/enforcement/test_provider_substitution_prohibition.py",
    "tests/agentic_core/L2_execution/enforcement/test_runtime_interceptor.py",
    "tests/agentic_core/L3_orchestration/exit_control/test_ledger_integrity.py",
    "tests/agentic_core/L3_orchestration/test_exit_controller.py",
    "tests/agentic_core/L3_orchestration/test_hitl_escalation_e2e.py",
    "tests/agentic_core/L4_state/enforcement/test_blast_radius.py",
    "tests/agentic_core/L4_state/enforcement/test_change_tracker.py",
    "tests/agentic_core/L4_state/enforcement/test_metrics_emission.py",
    "tests/agentic_core/L4_state/enforcement/test_phase_lock_store.py",
    "tests/agentic_core/L4_state/enforcement/test_promotion_authority.py",
    "tests/agentic_core/L4_state/enforcement/test_proof_of_ledger.py",
    "tests/agentic_core/L4_state/enforcement/test_readonly_retrieval_scope.py",
    "tests/agentic_core/L4_state/enforcement/test_replay_bundle_store.py",
    "tests/agentic_core/L4_state/enforcement/test_state_lifecycle_policy.py",
    "tests/agentic_core/L4_state/enforcement/test_telemetry_recorder.py",
    "tests/agentic_core/L4_state/enforcement/test_uwg_committer.py",
    "tests/agentic_core/L4_state/enforcement/test_uwg_verifier.py",
    "tests/agentic_core/L4_state/enforcement/test_violation_event_store.py",
    "tests/agentic_core/L5_safety/adapters/test_email_magic_link_adapter.py",
    "tests/agentic_core/L5_safety/adapters/test_notion_adapter.py",
    "tests/agentic_core/L5_safety/adapters/test_orkes_adapter.py",
    "tests/agentic_core/L5_safety/adapters/test_slack_adapter.py",
    "tests/ci/test_check_ast_collection_compliance.py",
    "tests/eval/capability/test_seed_capability.py",
    "tests/eval/regression/test_seed_regression.py",
    "tests/governance/test_heal_telemetry_and_budgets.py",
    "tests/guardian/test_exemption_recognition.py",
    "tests/guardian/test_invalid_stub_detector.py",
    "tests/guardian/test_test_silent_skip_detector.py",
    "tests/integration/apps_exec/test_apps_exec_integration.py",
    "tests/integration/apps_exec/test_eval_to_learning_bridge.py",
    "tests/integration/apps_exec/test_ptc_full_integration.py",
    "tests/integration/apps_exec/test_shadow_replay_integration.py",
    "tests/integration/apps_rg/test_ingress_wiring.py",
    "tests/integration/retrieval_layers/test_golden_dataset_e2e.py",
    "tests/integration/test_coverage_signal_consumer_e2e.py",
    "tests/integration/tools/meta_learning/test_run_hitl_consumer.py",
    "tests/knowledge/test_intake_clerk.py",
    "tests/ops_scripts/ci/test_check_mcp_npx_windows.py",
    "tests/ops_scripts/ci/test_exclusion_sync_gate.py",
    "tests/ops_scripts/ci/test_graphdb_gates.py",
    "tests/ops_scripts/ci/test_mcp_health_monitor.py",
    "tests/ops_scripts/ci/test_plan_location_gate.py",
    "tests/ops_scripts/ci/test_pre_commit_issue_schema.py",
    "tests/ops_scripts/ci/test_pre_commit_summary_reporter.py",
    "tests/ops_scripts/pre_commit/test_pre_commit_issue_schema.py",
    "tests/performance/test_hardened_vllm.py",
    "tests/performance/test_qwen_vllm_performance.py",
    "tests/runtime/test_exit_x3_disposition_wireup.py",
    "tests/smoke/runtime/test_prompt_lifecycle_e2e.py",
    "tests/system_learning/integration/test_system_integrity_audit.py",
    "tests/system_learning/unit/test_heal_classifier_activation.py",
    "tests/system_learning/unit/test_heal_classifier_wiring.py",
    "tests/system_learning/unit/test_healing_confidence_scorer.py",
    "tests/tools/exit_eval/test_run_judge_calibration.py",
    # Individual broken modules under tests/unit (collected separately so listing each)
    "tests/unit/agentic_core/L1_cognition/reasoning/test_react_determinism.py",
    "tests/unit/agentic_core/L1_cognition/reasoning/test_react_policy_boundary.py",
    "tests/unit/agentic_core/L1_cognition/reasoning/test_react_prompt_provenance.py",
    "tests/unit/agentic_core/L1_cognition/reasoning/test_thought_engine_agent.py",
    "tests/unit/agentic_core/L1_cognition/test_plan_contract_v2_vendor_extensions.py",
    "tests/unit/agentic_core/L1_cognition/types/test_action_request_types.py",
    "tests/unit/agentic_core/L1_cognition/types/test_cache_types.py",
    "tests/unit/agentic_core/L1_cognition/types/test_client_types.py",
    "tests/unit/agentic_core/L3_orchestration/test_c0_hardening.py",
    "tests/unit/agentic_core/L4_state/exemplars/test_exemplars.py",
    "tests/unit/agentic_core/config/test_token_budget_loader.py",
    "tests/unit/agentic_core/runtime/entry/test_app_ingress_runner.py",
    "tests/unit/apps_exec/scripts/test_enterprise_brief.py",
    "tests/unit/ops_scripts/ci/test_check_mcp_gate_sync.py",
    "tests/unit/ops_scripts/ci/test_prompt_reception_gates.py",
    "tests/unit/ops_scripts/hooks/windsurf/test_pre_mcp_gate.py",
    "tests/unit/tools/mcp/test_vector_db_adapter.py",
    "tests/runtime/test_l6_observability_recorder_wireup.py",
    "tests/unit/tools/ingestion/test_adg_node_resolver.py",
    "tests/unit/tools/ingestion/test_ingest_code_contextualization.py",
]
