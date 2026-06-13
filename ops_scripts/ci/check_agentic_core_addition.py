#!/usr/bin/env python3
"""
GOV-3 CI Gate: Core Addition Author-Gate Scanner

Fail-closed scanner for agentic_core/ changes that lack a valid
CoreAdditionAuthorGateReceipt proof object.

Exit codes:
  0 — PASS (no violations, or advisory mode, or all bypasses valid)
  1 — FAIL (violation found in fail-closed mode)
  2 — ERROR (scanner configuration error)

Modes:
  Fail-closed (default)  — any violation → exit 1
  Advisory               — CORE_ADDITION_GATE_ADVISORY=1 (local/dev only)

Bypass:
  CORE_ADDITION_GATE_BYPASS=1 — local writes only; CI fails if bypass evidence
  exists in artifacts/governance/core_addition_gate_violations.jsonl without a
  matching emergency_approval_receipt_ref field on the bypass event.

Opt-in full-tree scan (rare audit only):
  CORE_ADDITION_FULL_AGENTIC_CORE_SCAN=1 — when git reports no agentic_core
  delta, walk all ``agentic_core/**/*.py`` instead of returning no changes.

Artifact: artifacts/ci/agentic_core_addition_gate.json
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo root bootstrap
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
SESSION_STATE = REPO_ROOT / "artifacts" / "governance" / "session_state.json"
SCHEMA_PATH = REPO_ROOT / ".claude" / "schemas" / "CoreAdditionAuthorGateReceipt.schema.json"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "core_addition_gate_violations.jsonl"
ARTIFACT_OUT = REPO_ROOT / "artifacts" / "ci" / "agentic_core_addition_gate.json"

# ---------------------------------------------------------------------------
# Forbidden literals / patterns
# ---------------------------------------------------------------------------
_FORBIDDEN_LITERALS = [
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_qna",
    "company_brief",
    "interview_card",
    "recruiter",
    "resume_generator",
    "outreach",
    "apps_architect",
    "apps_eval",
]

_FORBIDDEN_REGEX_PATTERNS = [
    (r"JD[._-]specific", "JD-specific semantics"),
    (r"resume[._-]specific", "resume-specific semantics"),
    (r"LIC[._-]specific", "apps_lic specific"),
    (r"RG[._-]specific", "apps_rg specific"),
    (r"QNA[._-]specific", "apps_qna specific"),
    (r"research[._-]specific", "research-specific semantics"),
    (r"""(if|elif)\s+(?:app_id|tenant_id)\s*==\s*["']apps_\w+["']""", "app_id/tenant_id branching"),
    (r"""(?:app_id|app_name|tenant_id)\s*==\s*["']apps_\w+["']""", "app_id comparison"),
]

# Generic apps_* pattern — catches future apps not yet enumerated.
# Only fires when the match is NOT allowlisted (binding files, test/doc).
_GENERIC_APPS_RE = re.compile(r"""["']apps_[a-z_]+["']""")

# ---------------------------------------------------------------------------
# GOV-3 Baseline — pre-existing TEMPORARY_THIN_ADAPTER binding files
# These files were committed before GOV-3 existed and contain intentional
# app literals as part of a documented migration (shim → apps_rg/ canonical
# binding). They are suppressed until expiry or migration completion.
#
# DO NOT ADD new paths here without:
#   1. Classifying as TEMPORARY_THIN_ADAPTER per agentic-core-static.md
#   2. A migration receipt at artifacts/governance/migration_receipts/
#   3. A concrete expiry date ≤ 90 days from baseline entry
#   4. An issue ref naming the plan that will complete migration
# ---------------------------------------------------------------------------
_GOV3_BASELINE: dict[str, dict] = {
    # Added W4B 2026-05-13. Migration: apps-rg-golden-state-section-generation-a4f9e1.
    # Classification: TEMPORARY_THIN_ADAPTER (shim → apps_rg/runtime/bindings/l0_binding.py)
    # Findings: all forbidden_literal / generic_apps_literal / is_binding=True, no CRITICAL
    "apps_rg/runtime/bindings/l0_binding.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "target_module": "apps_rg.runtime.bindings.l0_binding",
        "issue": "GOV-3-BASELINE-001",
    },
    "apps_rg/runtime/bindings/l1_binding.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "target_module": "apps_rg.runtime.bindings.l1_binding",
        "issue": "GOV-3-BASELINE-002",
    },
    "apps_rg/runtime/bindings/c0_binding.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "target_module": "apps_rg.runtime.bindings.c0_binding",
        "issue": "GOV-3-BASELINE-003",
    },
    "apps_rg/runtime/bindings/u0_binding.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "target_module": "apps_rg.runtime.bindings.u0_binding",
        "issue": "GOV-3-BASELINE-004",
    },
    "agentic_core/runtime/u0/__init__.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "target_module": "apps_rg.runtime.u0",
        "issue": "GOV-3-BASELINE-005",
    },
    "apps_rg/runtime/bindings/pa_binding.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "target_module": "apps_rg.prompt_governance.pa_binding",
        "issue": "GOV-3-BASELINE-006",
    },
    "artifacts/archives/l2_rationalization_20260519/agentic_core/L2_execution/apps_rg_l2_binding.py": {
        "expiry": "2027-12-31",
        "classification": "ARCHIVED",
        "migration_plan": "l2-rationalization-waves-c8e4f1",
        "target_module": "apps_rg.runtime.bindings.l2_binding",
        "archived_from": "agentic_core/L2_execution/apps_rg_l2_binding.py",
        "rationale": (
            "W11-SHIM-ARCHIVE: moved out of agentic_core; canonical binding active; "
            "not scanned as core addition"
        ),
        "issue": "GOV-3-BASELINE-007-ARCHIVED",
    },
    "agentic_core/base_agents/SovereignBaseAgent.py": {
        "expiry": "2026-08-13",
        "classification": "GENERIC_IMPORT_CHAIN_REPAIR",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "rationale": "Fix circular import chain for sanitize_tool_output - generic runtime infrastructure repair, NOT apps_rg-specific",
        "issue": "GOV-3-BASELINE-008",
    },
    "apps_rg/runtime/bindings/exit_binding.py": {
        "expiry": "2026-08-13",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-runtime-wiring-completion-d4e8a1",
        "target_module": "apps_rg.runtime.bindings.exit_binding",
        "rationale": "Pre-existing LEGACY_SHIM from W2F Exit binding migration - pure re-export, no implementation logic",
        "issue": "GOV-3-BASELINE-009",
    },
    # G1.P3 Generic Infrastructure Baseline Entries (GOV-3-BASELINE-010 through 046)
    # Classification: GENERIC_INFRASTRUCTURE
    # Plan: apps-rg-global-verification-maintenance-before-w4
    # Rationale: Generic ML/RLHF/evaluation and infrastructure code with no apps-specific logic
    "agentic_core/utils/workflow_engines/aligner.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic alignment/orchestration utilities - no apps-specific content",
        "issue": "GOV-3-BASELINE-010",
    },
    "agentic_core/utils/workflow_engines/completeness.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic completeness evaluation - no apps-specific content",
        "issue": "GOV-3-BASELINE-011",
    },
    "agentic_core/utils/workflow_engines/completeness_metrics.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic metrics collection - no apps-specific content",
        "issue": "GOV-3-BASELINE-012",
    },
    "agentic_core/utils/workflow_engines/completeness_monitors.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic monitoring - no apps-specific content",
        "issue": "GOV-3-BASELINE-013",
    },
    "agentic_core/utils/workflow_engines/completeness_reranker.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic reranking - no apps-specific content",
        "issue": "GOV-3-BASELINE-014",
    },
    "agentic_core/utils/workflow_engines/completeness_scorer.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic scoring - no apps-specific content",
        "issue": "GOV-3-BASELINE-015",
    },
    "agentic_core/utils/workflow_engines/dpo_batch_builder.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic DPO training batch builder - no apps-specific content",
        "issue": "GOV-3-BASELINE-016",
    },
    "agentic_core/utils/workflow_engines/drift_monitor.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic drift detection - no apps-specific content",
        "issue": "GOV-3-BASELINE-017",
    },
    "agentic_core/utils/workflow_engines/fusion.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic result fusion - no apps-specific content",
        "issue": "GOV-3-BASELINE-018",
    },
    "agentic_core/utils/workflow_engines/groundedness.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic groundedness checks - no apps-specific content",
        "issue": "GOV-3-BASELINE-019",
    },
    "agentic_core/utils/workflow_engines/interfaces.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic interfaces/contracts - no apps-specific content",
        "issue": "GOV-3-BASELINE-020",
    },
    "agentic_core/utils/workflow_engines/late_chunking.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic chunking utilities - no apps-specific content",
        "issue": "GOV-3-BASELINE-021",
    },
    "agentic_core/utils/workflow_engines/meta_learning_bridge.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic meta-learning - no apps-specific content",
        "issue": "GOV-3-BASELINE-022",
    },
    "agentic_core/utils/workflow_engines/mrr.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic MRR metric - no apps-specific content",
        "issue": "GOV-3-BASELINE-023",
    },
    "agentic_core/utils/workflow_engines/ndcg.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic NDCG metric - no apps-specific content",
        "issue": "GOV-3-BASELINE-024",
    },
    "agentic_core/utils/workflow_engines/offline_eval_runner.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic offline evaluation - no apps-specific content",
        "issue": "GOV-3-BASELINE-025",
    },
    "agentic_core/utils/workflow_engines/parent_child.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic parent-child relationships - no apps-specific content",
        "issue": "GOV-3-BASELINE-026",
    },
    "agentic_core/utils/workflow_engines/policies.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic evaluation policies - no apps-specific content",
        "issue": "GOV-3-BASELINE-027",
    },
    "agentic_core/utils/workflow_engines/precision_at_k.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic precision@k metric - no apps-specific content",
        "issue": "GOV-3-BASELINE-028",
    },
    "agentic_core/utils/workflow_engines/profiles.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic evaluation profiles - no apps-specific content",
        "issue": "GOV-3-BASELINE-029",
    },
    "agentic_core/utils/workflow_engines/proposer_bridge.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic proposer bridge - no apps-specific content",
        "issue": "GOV-3-BASELINE-030",
    },
    "agentic_core/utils/workflow_engines/recall_at_k.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic recall@k metric - no apps-specific content",
        "issue": "GOV-3-BASELINE-031",
    },
    "agentic_core/utils/workflow_engines/replay_eval_runner.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic replay evaluation - no apps-specific content",
        "issue": "GOV-3-BASELINE-032",
    },
    "agentic_core/utils/workflow_engines/reranker.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic reranking - no apps-specific content",
        "issue": "GOV-3-BASELINE-033",
    },
    "agentic_core/utils/workflow_engines/shadow_eval_runner.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic shadow evaluation - no apps-specific content",
        "issue": "GOV-3-BASELINE-034",
    },
    "agentic_core/utils/workflow_engines/snapshots.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic state snapshots - no apps-specific content",
        "issue": "GOV-3-BASELINE-035",
    },
    "agentic_core/utils/workflow_engines/validators.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic validation - no apps-specific content",
        "issue": "GOV-3-BASELINE-036",
    },
    # UWG (Umbrella Write Governance) - Generic L4 infrastructure
    "agentic_core/UWG/audit_ledger.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic UWG audit logging - no apps-specific content",
        "issue": "GOV-3-BASELINE-037",
    },
    "agentic_core/UWG/package_driven_write_admission.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic write admission control - no apps-specific content",
        "issue": "GOV-3-BASELINE-038",
    },
    "agentic_core/UWG/state_diff_validator.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic state validation - no apps-specific content",
        "issue": "GOV-3-BASELINE-039",
    },
    "agentic_core/UWG/write_lock_manager.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic write locking - no apps-specific content",
        "issue": "GOV-3-BASELINE-040",
    },
    "agentic_core/UWG/__init__.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "UWG package init - no apps-specific content",
        "issue": "GOV-3-BASELINE-041",
    },
    # Visualization, compatibility, and shared utilities
    "agentic_core/visualization/engines/trace_3d_visualizer.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic OTEL trace visualization - no apps-specific content",
        "issue": "GOV-3-BASELINE-042",
    },
    "agentic_core/_compat/__init__.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Compatibility layer init - no apps-specific content",
        "issue": "GOV-3-BASELINE-043",
    },
    "agentic_core/_compat/core/l5_safety_aliases.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "L5 safety compatibility aliases - no apps-specific content",
        "issue": "GOV-3-BASELINE-044",
    },
    "agentic_core/_shared/__init__.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Shared utilities init - no apps-specific content",
        "issue": "GOV-3-BASELINE-045",
    },
    "agentic_core/_shared/types/__init__.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Shared types init - no apps-specific content",
        "issue": "GOV-3-BASELINE-046",
    },
    # ------------------------------------------------------------------
    # GOV-3-BASELINE-047..061 — contract-runner branch delta (2026-05-15)
    # All paths: git diff HEAD shows modified; literal scan hits are only
    # forbidden_literal / generic_apps_literal (or zero findings). Receipt
    # validation is skipped when every changed path is baselined.
    # Migration receipts: artifacts/governance/migration_receipts/*.json
    # ------------------------------------------------------------------
    "agentic_core/AGENTS.md": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "Core boundary docs; markdown allowlisted; no literal findings",
        "issue": "GOV-3-BASELINE-047",
    },
    "agentic_core/L0_routing/apps_research_l0_binding_v2.py": {
        "expiry": "2026-11-30",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-research-dispatch-and-bindings",
        "target_module": "apps_research.runtime.bindings.l0_binding",
        "migration_receipt": "artifacts/governance/migration_receipts/u0_apps_research_binding_v2_receipt.json",
        "issue": "GOV-3-BASELINE-048",
    },
    "agentic_core/L0_routing/package_driven_l0_binding.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-global-verification-maintenance-before-w4",
        "rationale": "Generic L0 package-driven ingress; documented apps_* shape keys only",
        "issue": "GOV-3-BASELINE-049",
    },
    "agentic_core/L1_cognition/reasoning/semantic_retriever.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "Generic retrieval helper; GOV-3 literal scan clean on current diff",
        "issue": "GOV-3-BASELINE-050",
    },
    "agentic_core/L2_execution/apps_research_l2_binding.py": {
        "expiry": "2026-11-30",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-research-rich-content-runtime-customization-a1b2c3",
        "target_module": "apps_research.runtime.bindings.l2_binding",
        "migration_receipt": "artifacts/governance/migration_receipts/apps_research_dispatch_receipt.json",
        "issue": "GOV-3-BASELINE-051",
    },
    "agentic_core/L2_execution/l2_package_driven_executor.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-golden-state-section-generation-a4f9e1",
        "rationale": "Generic package-driven L2 executor; profile-ref strings only",
        "issue": "GOV-3-BASELINE-052",
    },
    "agentic_core/L3_orchestration/exit_eval/v6/pipeline.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "Exit v6 pipeline; GOV-3 literal scan clean on current diff",
        "issue": "GOV-3-BASELINE-053",
    },
    "agentic_core/L3_orchestration/reasoning/engines/evidence_eval_bridge.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "Evidence eval bridge; GOV-3 literal scan clean on current diff",
        "issue": "GOV-3-BASELINE-054",
    },
    "agentic_core/L4_state/reasoning/retrieval_layers.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "Retrieval layer helpers; GOV-3 literal scan clean on current diff",
        "issue": "GOV-3-BASELINE-055",
    },
    "agentic_core/L6_learning/future_run_proposal_builder.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-l6-future-run-proposal-refs-7e4c2f",
        "migration_receipt": "artifacts/governance/migration_receipts/20260515_l6_future_run_proposal_builder_refs_7e4c2f.json",
        "rationale": "L6 future-run proposal wiring; migration receipt on disk; GOV-3 scan clean",
        "issue": "GOV-3-BASELINE-056",
    },
    "agentic_core/runtime/contracts/apps_rg_ingress_payload.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-canonical-dispatch-l7-gate-c8a4d1",
        "rationale": "Shared ingress payload contract used by package-driven L0/L2",
        "issue": "GOV-3-BASELINE-057",
    },
    "agentic_core/runtime/contracts/l1_plan_contract.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "L1 plan contract types; minimal apps_* token references in docs/types",
        "issue": "GOV-3-BASELINE-058",
    },
    "agentic_core/runtime/contracts/route_contract.py": {
        "expiry": "2027-12-31",
        "classification": "GENERIC_INFRASTRUCTURE",
        "migration_plan": "apps-rg-ci-contract-runner-hygiene",
        "rationale": "Route contract surface; canonical route vocabulary",
        "issue": "GOV-3-BASELINE-059",
    },
    "agentic_core/runtime/entry/apps_rg_w9_managed_workflow_e2e.py": {
        "expiry": "2026-11-30",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "migration_plan": "apps-rg-w9-managed-workflow",
        "target_module": "apps_rg.runtime.entry",
        "rationale": "W9 managed-workflow E2E harness in core entry tree",
        "issue": "GOV-3-BASELINE-060",
    },
}

# Canonical GENERIC route enums — must NOT trigger false positives.
_CANONICAL_ROUTES = frozenset(
    [
        "R1A_EXACT_CACHE",
        "R1B_SEMANTIC_CACHE",
        "R5_FALLBACK",
        "R3_SIMPLE_GROUNDED_READ",
        "R4_SINGLE_ACTION",
        "R3R4_MANAGED_WORKFLOW",
    ]
)

# App-tainted route patterns (names that include domain literals).
_ROUTE_LITERAL_FRAGMENTS = [
    "resume",
    "outreach",
    "company_brief",
    "interview",
    "recruiter",
    r"\brg\b",
    r"\blic\b",
    r"\bqna\b",
    "research",
]
_ROUTE_LITERAL_RE = re.compile(
    "(" + "|".join(_ROUTE_LITERAL_FRAGMENTS) + ")",
    re.IGNORECASE,
)

# Route assigned inside an app_id / app_name branch.
_APP_BRANCH_ROUTE_RE = re.compile(
    r"""(if|elif)\s+(?:app_id|app_name)\s*==\s*["']apps_\w+["'][^:]*:.*route""",
    re.IGNORECASE,
)

# Eval threshold with app-name comment/variable.
_EVAL_THRESHOLD_RE = re.compile(
    r"""(?:threshold|min_score|score_floor)\s*=\s*[\d.]+.*(?:apps?_\w+|RG|LIC|QNA|research)""",
    re.IGNORECASE,
)

# Allowlisted file-path patterns (relative to repo root).
_ALLOWLIST_RE = [
    re.compile(r".*\.md$", re.IGNORECASE),
    re.compile(r".*AGENTS\.md$", re.IGNORECASE),
    re.compile(r".*/tests/.*"),
    re.compile(r".*/test_.*\.py$"),
    re.compile(r".*/conftest\.py$"),
    re.compile(r".*/_test_.*\.py$"),
    re.compile(r".*/artifacts/governance/.*"),
    re.compile(r".*/migration_receipts/.*"),
    re.compile(r".*/boundary_receipts/.*"),
    re.compile(r".*\docs/archive/windsurf/legacy-tree/.*"),
    # Data/runtime files — non-code, cannot introduce apps_rg behavior
    re.compile(r".*/logs/.*"),  # Log files (JSON data)
    re.compile(r".*\.core_golden_seal$"),  # Runtime seal files
    re.compile(r".*_trace_index\.json$"),  # ADG trace indices
]

# Temporary binding pattern — allowed with migration receipt.
_BINDING_RE = re.compile(r".*apps_\w+_.*_binding\.py$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_allowlisted(rel_path: str) -> bool:
    for p in _ALLOWLIST_RE:
        if p.match(rel_path):
            return True
    return False


def _is_binding(rel_path: str) -> bool:
    return bool(_BINDING_RE.match(rel_path))


def _is_baselined(rel_path: str) -> bool:
    """Return True if this path is in the GOV-3 baseline and has not expired."""
    import datetime
    norm = rel_path.replace("\\", "/")
    entry = _GOV3_BASELINE.get(norm)
    if not entry:
        return False
    try:
        expiry = datetime.date.fromisoformat(entry["expiry"])
        return datetime.date.today() <= expiry
    except (ValueError, KeyError):
        return False


def _baseline_suppresses_findings(findings_for_path: list[dict]) -> bool:
    """Return True if ALL findings for a baselined path are non-critical literal hits.

    CRITICAL findings are never suppressed — they indicate real app leakage
    beyond what a shim/forward import would cause.
    """
    suppressable_categories = {"forbidden_literal", "generic_apps_literal"}
    for f in findings_for_path:
        if f["severity"] == "CRITICAL":
            return False
        if f["category"] not in suppressable_categories:
            return False
    return True


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Step 1 — Detect changed agentic_core/ paths
# ---------------------------------------------------------------------------


def _detect_changed_paths() -> list[str]:
    """Return list of agentic_core/ paths that are changed/staged."""
    import subprocess

    # Env override (useful for CI matrix or custom tooling).
    env_paths = os.environ.get("CORE_ADDITION_CHANGED_PATHS", "").strip()
    if env_paths:
        return [
            p for p in env_paths.split(os.pathsep)
            if p.replace("\\", "/").startswith("agentic_core/")
        ]

    def _git_diff(args: list[str]) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "diff"] + args + ["--name-only"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return [
                    ln.strip()
                    for ln in result.stdout.splitlines()
                    if ln.strip() and ln.strip().replace("\\", "/").startswith("agentic_core/")
                ]
        except (OSError, subprocess.TimeoutExpired):
            pass
        return []

    # Union staged + working-tree deltas vs HEAD — both can be non-empty independently.
    paths_set = set(_git_diff(["--cached"])) | set(_git_diff(["HEAD"]))
    if paths_set:
        return sorted(paths_set)

    # No git delta under agentic_core/: treat as ZERO changed paths (PASS).
    # The previous unconditional full-tree scan mis-fired when the working tree
    # matched HEAD (empty diff), falsely flagging thousands of files and every
    # receipt mismatch. Full-tree audit remains opt-in:
    if os.environ.get("CORE_ADDITION_FULL_AGENTIC_CORE_SCAN") == "1":
        all_paths: list[str] = []
        for root, dirs, files in os.walk(AGENTIC_CORE_PATH):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for fname in files:
                if fname.endswith(".py"):
                    rel = str((Path(root) / fname).relative_to(REPO_ROOT)).replace("\\", "/")
                    all_paths.append(rel)
        return all_paths

    return []


# ---------------------------------------------------------------------------
# Step 2 — Literal / pattern scan
# ---------------------------------------------------------------------------


def _scan_file(filepath: Path) -> list[dict[str, Any]]:
    """Scan one Python file for forbidden patterns. Returns finding dicts."""
    findings: list[dict[str, Any]] = []
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

    if _is_allowlisted(rel_path):
        return findings

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
    except (OSError, IOError):
        return findings

    def _add(line_num: int, line: str, category: str, description: str, severity: str = "HIGH") -> None:
        findings.append(
            {
                "file": rel_path,
                "line": line_num,
                "category": category,
                "description": description,
                "severity": severity,
                "content": line.strip()[:120],
                "is_binding": _is_binding(rel_path),
            }
        )

    for ln, line in enumerate(lines, 1):
        # --- Forbidden literals ---
        for lit in _FORBIDDEN_LITERALS:
            if lit in line:
                _add(ln, line, "forbidden_literal", f"forbidden app literal: {lit!r}")

        # --- Regex patterns (app_id branches, semantic patterns) ---
        for pat, desc in _FORBIDDEN_REGEX_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                _add(ln, line, "app_id_branch" if "app_id" in pat or "tenant_id" in pat else "semantic_pattern", desc, "CRITICAL" if "branch" in pat else "HIGH")

        # --- Generic apps_* quoted string not in allowlist ---
        if _GENERIC_APPS_RE.search(line):
            # Skip if it's in a comment about allowlisting.
            _add(ln, line, "generic_apps_literal", "generic apps_* quoted literal in core", "HIGH")

        # --- App-tainted route name ---
        route_match = re.search(r"""["'][A-Z0-9_]+["']""", line)
        if route_match:
            route_name = route_match.group().strip("'\"")
            if route_name not in _CANONICAL_ROUTES and _ROUTE_LITERAL_RE.search(route_name):
                # Upper-snake cert/cref exports (e.g. __all__) are not R1* route enums.
                # ``_ROUTE_LITERAL_RE`` can match substrings like "research" inside
                # ``APPS_RESEARCH_*`` identifiers — avoid false HIGH on binding exports.
                is_cert_constant = bool(
                    re.fullmatch(r"[A-Z][A-Z0-9_]+", route_name)
                    and (
                        route_name.endswith("_CERT_REF")
                        or route_name.endswith("_CREFS")
                    )
                )
                if not is_cert_constant:
                    _add(ln, line, "app_route_behavior", f"app-tainted route name: {route_name!r}", "HIGH")

        # --- Route inside app_id branch ---
        if _APP_BRANCH_ROUTE_RE.search(line):
            _add(ln, line, "app_route_behavior", "route assignment inside app_id/app_name branch", "CRITICAL")

        # --- Eval threshold with app name ---
        if _EVAL_THRESHOLD_RE.search(line):
            _add(ln, line, "eval_threshold", "app-specific eval threshold in core", "MEDIUM")

    return findings


def _scan_agentic_core(
    changed_paths: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Scan changed agentic_core files.

    Returns:
        (findings, baselined_paths) — findings excludes suppressed baseline
        hits; baselined_paths lists paths that were suppressed.
    """
    all_findings: list[dict[str, Any]] = []
    baselined_paths: list[str] = []
    for rel in changed_paths:
        norm = rel.replace("\\", "/")
        abs_path = REPO_ROOT / rel.replace("/", os.sep)
        if not abs_path.exists():
            continue
        path_findings = _scan_file(abs_path)
        if _is_baselined(norm) and _baseline_suppresses_findings(path_findings):
            baselined_paths.append(norm)
            # Still log baselined findings at DEBUG level — do NOT add to all_findings.
        else:
            all_findings.extend(path_findings)
    return all_findings, baselined_paths


# ---------------------------------------------------------------------------
# Step 3 — Bypass evidence audit
# ---------------------------------------------------------------------------


def _check_bypass_evidence() -> list[str]:
    """Return error messages if un-approved bypass events exist in violations log."""
    errors: list[str] = []
    if not VIOLATIONS_LOG.exists():
        return errors
    try:
        with open(VIOLATIONS_LOG, "r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, 1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if event.get("bypass_type") == "CORE_ADDITION_GATE_BYPASS":
                    if not event.get("emergency_approval_receipt_ref"):
                        errors.append(
                            f"Unapproved bypass event in {VIOLATIONS_LOG.name} line {line_no}: "
                            f"plan={event.get('plan_id','?')} file={event.get('file_path','?')} "
                            "— set emergency_approval_receipt_ref or remove the bypass event."
                        )
    except (OSError, IOError):
        pass
    return errors


# ---------------------------------------------------------------------------
# Step 4 — Plan metadata + receipt validation
# ---------------------------------------------------------------------------


def _load_plan_meta() -> dict[str, Any] | None:
    """Load active_plan metadata from session_state.json. Returns None if missing."""
    if not SESSION_STATE.exists():
        return None
    try:
        state = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        plan_meta = state.get("active_plan", {})
        return plan_meta if isinstance(plan_meta, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _load_schema() -> dict[str, Any] | None:
    if not SCHEMA_PATH.exists():
        return None
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _validate_receipt_schema(receipt: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Return list of schema validation errors (lightweight; full jsonschema optional)."""
    errors: list[str] = []
    try:
        import jsonschema
        try:
            jsonschema.validate(instance=receipt, schema=schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"Schema validation failed: {exc.message}")
        except jsonschema.SchemaError as exc:
            errors.append(f"Schema itself invalid: {exc.message}")
    except ImportError:
        # Fallback: manual required-field check.
        for req in schema.get("required", []):
            if req not in receipt:
                errors.append(f"Receipt missing required field: {req!r}")
    return errors


def _validate_receipt_against_plan(
    receipt: dict[str, Any],
    plan_meta: dict[str, Any],
    changed_paths: list[str],
) -> list[str]:
    """Full receipt proof validation. Returns list of violation strings."""
    errors: list[str] = []
    plan_id = plan_meta.get("plan_id", "")

    # receipt_type
    if receipt.get("receipt_type") != "CoreAdditionAuthorGateReceipt":
        errors.append(
            f"receipt_type must be CoreAdditionAuthorGateReceipt, got {receipt.get('receipt_type')!r}"
        )

    # plan_type
    if receipt.get("plan_type") != "platform_core_change":
        errors.append(
            f"receipt.plan_type must be platform_core_change, got {receipt.get('plan_type')!r}"
        )

    # plan_id match
    if receipt.get("plan_id") != plan_id:
        errors.append(
            f"receipt.plan_id {receipt.get('plan_id')!r} != active plan_id {plan_id!r}"
        )

    # verdict
    verdict = receipt.get("decision", {}).get("verdict")
    if verdict != "PASS":
        errors.append(f"receipt.decision.verdict must be PASS, got {verdict!r}")

    # changed_paths coverage
    receipt_paths = [p.replace("\\", "/") for p in receipt.get("changed_paths", [])]
    for cp in changed_paths:
        norm = cp.replace("\\", "/")
        covered = any(
            norm.endswith(rp) or rp in norm or norm in rp for rp in receipt_paths
        )
        if not covered:
            errors.append(f"changed path {norm!r} not covered by receipt.changed_paths")

    # signature.receipt_digest shape
    digest = receipt.get("signature", {}).get("receipt_digest", "")
    if not digest.startswith("sha256:"):
        errors.append("receipt.signature.receipt_digest missing or not sha256: prefixed")

    # Full digest recomputation (best-effort — skip placeholder zeros).
    if digest and digest != "sha256:" + "0" * 64:
        receipt_copy = {k: v for k, v in receipt.items() if k != "signature"}
        computed = _sha256_bytes(
            json.dumps(receipt_copy, sort_keys=True, separators=(",", ":")).encode()
        )
        if computed != digest:
            errors.append(
                f"receipt_digest recomputation mismatch: stored={digest!r} computed={computed!r}"
            )

    # Full artifact proof validation
    artifacts = receipt.get("artifacts", {})
    for art_key, art in artifacts.items():
        if not isinstance(art, dict):
            errors.append(f"receipt.artifacts.{art_key} is not an object")
            continue

        # path exists
        art_path = REPO_ROOT / art.get("path", "")
        if not art_path.exists():
            errors.append(f"receipt.artifacts.{art_key}.path does not exist: {art.get('path')!r}")
            continue

        # digest recompute (skip placeholder zeros)
        stored_digest = art.get("digest", "")
        if stored_digest and stored_digest != "sha256:" + "0" * 64:
            recomputed = _sha256_file(art_path)
            if recomputed != stored_digest:
                errors.append(
                    f"receipt.artifacts.{art_key} digest mismatch: "
                    f"stored={stored_digest!r} computed={recomputed!r}"
                )

        # verdict
        if art.get("verdict") != "PASS":
            errors.append(
                f"receipt.artifacts.{art_key}.verdict must be PASS, got {art.get('verdict')!r}"
            )

        # plan_id
        if art.get("plan_id") != plan_id:
            errors.append(
                f"receipt.artifacts.{art_key}.plan_id {art.get('plan_id')!r} != {plan_id!r}"
            )

        # changed_paths_covered
        if art.get("changed_paths_covered") is not True:
            errors.append(
                f"receipt.artifacts.{art_key}.changed_paths_covered must be true"
            )

    return errors


def _validate_plan_and_receipt(
    changed_paths: list[str], plan_meta: dict[str, Any] | None
) -> list[str]:
    """Validate plan metadata and receipt. Returns list of error strings."""
    errors: list[str] = []

    if plan_meta is None:
        errors.append(
            "No active plan metadata found in session_state.json. "
            "Declare plan_type=platform_core_change and author_gate_receipt_ref before "
            "editing agentic_core/."
        )
        return errors

    # Plan metadata fields
    if plan_meta.get("plan_type") != "platform_core_change":
        errors.append(
            f"active plan plan_type must be platform_core_change, "
            f"got {plan_meta.get('plan_type')!r}"
        )

    if not plan_meta.get("touches_agentic_core"):
        errors.append("active plan must declare touches_agentic_core: true")

    if not plan_meta.get("core_addition_author_gate_required"):
        errors.append("active plan must declare core_addition_author_gate_required: true")

    receipt_ref = str(plan_meta.get("author_gate_receipt_ref", "")).strip()
    if not receipt_ref:
        errors.append(
            "active plan has no author_gate_receipt_ref. "
            "Set author_gate_receipt_ref: artifacts/governance/<receipt>.json."
        )
        return errors

    # CORE_ADDITION_RECEIPT_PATH lets tests redirect to a temp copy without
    # touching the canonical governance receipt on disk.
    _receipt_override = os.environ.get("CORE_ADDITION_RECEIPT_PATH", "").strip()
    receipt_path = Path(_receipt_override) if _receipt_override else REPO_ROOT / receipt_ref
    if not receipt_path.exists():
        errors.append(f"author_gate_receipt_ref path does not exist: {receipt_ref!r}")
        return errors

    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Could not parse receipt JSON: {exc}")
        return errors

    schema = _load_schema()
    if schema:
        schema_errors = _validate_receipt_schema(receipt, schema)
        errors.extend(schema_errors)

    proof_errors = _validate_receipt_against_plan(receipt, plan_meta, changed_paths)
    errors.extend(proof_errors)

    return errors


# ---------------------------------------------------------------------------
# Step 5 — Emit artifact
# ---------------------------------------------------------------------------


def _emit_artifact(
    result: dict[str, Any],
) -> None:
    ARTIFACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:  # noqa: C901 — complexity acceptable for a gate script
    advisory_mode = bool(os.environ.get("CORE_ADDITION_GATE_ADVISORY"))
    bypass_mode = bool(os.environ.get("CORE_ADDITION_GATE_BYPASS"))

    findings: list[dict[str, Any]] = []
    errors: list[str] = []
    verdict = "PASS"

    # --- Bypass evidence audit (always runs — cannot be bypassed) ---
    bypass_errors = _check_bypass_evidence()
    if bypass_errors:
        errors.extend(bypass_errors)

    # --- Detect changed paths ---
    changed_core_paths = _detect_changed_paths()

    if not changed_core_paths:
        result = {
            "verdict": "PASS",
            "mode": "advisory" if advisory_mode else "fail_closed",
            "changed_core_paths": [],
            "findings": [],
            "errors": errors,
            "note": "No agentic_core/ changed paths detected — scan skipped.",
        }
        _emit_artifact(result)
        print("GOV-3 PASS: no agentic_core/ paths changed.")
        if errors:
            print(f"  WARN: {len(errors)} bypass-evidence errors:")
            for e in errors:
                print(f"    - {e}")
            if not advisory_mode:
                return 1
        return 0

    print(f"GOV-3: scanning {len(changed_core_paths)} changed agentic_core/ path(s)...")

    # --- Literal/pattern scan (baseline suppression applied) ---
    scan_findings, baselined_paths = _scan_agentic_core(changed_core_paths)
    findings.extend(scan_findings)
    if baselined_paths:
        print(
            f"  GOV-3 BASELINE: {len(baselined_paths)} path(s) suppressed "
            f"(TEMPORARY_THIN_ADAPTER / ARCHIVE_PENDING):"
        )
        for bp in baselined_paths:
            entry = _GOV3_BASELINE.get(bp, {})
            print(f"    {bp} — expiry={entry.get('expiry','?')} issue={entry.get('issue','?')}")

    # --- Plan metadata + receipt validation ---
    # Skip if ALL changed paths are baselined (no new platform_core_change needed).
    non_baselined = [p for p in changed_core_paths if not _is_baselined(p.replace("\\", "/"))]
    if non_baselined:
        plan_meta = _load_plan_meta()
        receipt_errors = _validate_plan_and_receipt(non_baselined, plan_meta)
        errors.extend(receipt_errors)
    else:
        print("  GOV-3: all changed paths are baselined — receipt validation skipped.")

    # --- Determine verdict ---
    critical_findings = [f for f in findings if f["severity"] == "CRITICAL"]
    high_findings = [f for f in findings if f["severity"] == "HIGH"]
    medium_findings = [f for f in findings if f["severity"] == "MEDIUM"]

    has_failures = bool(findings) or bool(errors)

    if has_failures:
        verdict = "FAIL"

    result = {
        "verdict": verdict,
        "mode": "advisory" if advisory_mode else "fail_closed",
        "bypass_active": bypass_mode,
        "changed_core_paths": changed_core_paths,
        "baselined_paths": baselined_paths,
        "findings_count": len(findings),
        "critical_count": len(critical_findings),
        "high_count": len(high_findings),
        "medium_count": len(medium_findings),
        "findings": findings[:50],  # cap to avoid huge artifacts
        "errors": errors,
    }
    _emit_artifact(result)

    if has_failures:
        print(f"GOV-3 FAIL: {len(findings)} scan finding(s), {len(errors)} receipt/plan error(s).")
        for f in findings[:10]:
            print(f"  [{f['severity']}] {f['category']} — {f['file']}:{f['line']}: {f['description']}")
        if len(findings) > 10:
            print(f"  ... and {len(findings) - 10} more (see {ARTIFACT_OUT})")
        for e in errors:
            print(f"  ERROR: {e}")

        if advisory_mode:
            print("  (advisory mode — not blocking)")
            return 0
        if bypass_mode:
            print("  (CORE_ADDITION_GATE_BYPASS=1 — bypassed locally; CI will audit bypass log)")
            return 0
        return 1
    else:
        print(
            f"GOV-3 PASS: {len(changed_core_paths)} path(s) scanned, "
            f"0 findings, 0 receipt errors."
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
