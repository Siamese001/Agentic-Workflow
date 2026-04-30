"""Append HITL-NEW-A..F (REQ-174..179) to the 10c semantic ledger and matrix."""
import csv
from pathlib import Path

ROOT = Path(r"c:\Git\Agentic-Workflow-FRESH")
ledger = ROOT / "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv"
matrix = ROOT / "docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv"

rows_ledger = list(csv.DictReader(ledger.open(encoding="utf-8")))
rows_matrix = list(csv.DictReader(matrix.open(encoding="utf-8")))
ledger_fields = list(rows_ledger[0].keys())
matrix_fields = list(rows_matrix[0].keys())

new_ledger = [
    {
        "req_id": "10C-REQ-174",
        "source_file": "agentic_process_mapping_v38.md + best-practice gap analysis 2026-04-29",
        "source_section": "HITL-NEW-A risk-tier classifier",
        "source_unit_type": "Derived requirement (Anthropic/OpenAI/Galileo HITL best-practice gap)",
        "source_text_short": "L1 plan emits risk_tier T1/T2/T3 from side_effect_class, reversibility, policy_sensitivity, confidence",
        "canonical_requirement_statement": (
            "L1 plan output contract MUST emit risk_tier in {T1_auto, T2_approve, T3_hard_stop} "
            "deterministically derived from (side_effect_class x reversibility x policy_sensitivity) "
            "AND auto-promoted one band when confidence_score < tau (HITL escalation threshold). "
            "risk_tier MUST be a first-class routing input consumed by L0 R3/R4 and by L2 E2 admission, "
            "not advisory. Suppression or hand-assignment of tier without policy override is forbidden."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "D. Governance / capability / replay / observability",
        "layer_owner": "L1 cognition",
        "runtime_phase": "Plan synthesis",
        "required_artifacts": "L1PlanContract.risk_tier; risk_tier_derivation_receipt",
        "required_controls": "RiskTierClassifier; ConfidencePromotionRule; TierOverrideAuditor",
        "required_tests": "Tier T1/T2/T3 derivation matrix; confidence-promotion edge cases; deterministic replay of tier under same inputs; refusal of hand-assigned tier",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.92",
    },
    {
        "req_id": "10C-REQ-175",
        "source_file": "agentic_process_mapping_v38.md + best-practice gap analysis 2026-04-29",
        "source_section": "HITL-NEW-B pre-execution approval gate at L2 E2",
        "source_unit_type": "Derived requirement (OpenAI Agents SDK needs_approval; MCP elicitation; Cloudflare waitForApproval)",
        "source_text_short": "L2 E2 refuses E3 admission until HITL clearance when risk_tier>=T2 or tool.requires_approval=true",
        "canonical_requirement_statement": (
            "L2 E2 Work-Order Check MUST refuse to admit a step into E3 execution when "
            "L1PlanContract.risk_tier in {T2_approve, T3_hard_stop} OR "
            "capability_registry[tool].requires_approval is true, until a valid HITL clearance receipt "
            "is bound to the step. Approval MUST occur before any side-effect-producing tool call. "
            "Post-hoc Exit-only HITL is insufficient for irreversible actions and is a contract violation."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "D. Governance / capability / replay / observability",
        "layer_owner": "L2 execution",
        "runtime_phase": "Pre-execution",
        "required_artifacts": "PreExecutionApprovalReceipt; SideEffectClassDeclaration; capability_registry.requires_approval",
        "required_controls": "PreExecutionHITLGate; SideEffectClassifier; ToolApprovalLookup",
        "required_tests": "T3 irreversible-tool blocked at E2; T1 auto-pass; tool with requires_approval=true blocked even at T1; receipt binding to step lineage",
        "severity_if_missing": "CRITICAL",
        "confidence_score": "0.95",
    },
    {
        "req_id": "10C-REQ-176",
        "source_file": "agentic_process_mapping_v38.md + best-practice gap analysis 2026-04-29",
        "source_section": "HITL-NEW-C durable HITL suspend/resume primitive",
        "source_unit_type": "Derived requirement (OpenAI RunState; Cloudflare durable workflow approval)",
        "source_text_short": "HITL supports serializable HITLPendingState with TTL, escalation_chain, default_disposition on timeout",
        "canonical_requirement_statement": (
            "HITL stage H2 MUST support a durable suspend primitive: a serializable HITLPendingState "
            "containing the bounded review packet, TTL, escalation_chain[], and default_disposition in "
            "{abstain, reject, return_to_l1}. The same run MUST be resumable from this state across "
            "process restarts and arbitrary wall-clock gaps (hours to weeks). Synchronous-only HITL is "
            "insufficient for regulated review workflows."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "D. Governance / capability / replay / observability",
        "layer_owner": "HITL L5",
        "runtime_phase": "Escalation",
        "required_artifacts": "HITLPendingState; HITLResumeReceipt; HITL_TTL_policy",
        "required_controls": "HITLPendingStateSerializer; HITLEscalationChainExecutor; HITLTimeoutDispositionResolver",
        "required_tests": "Suspend-restart-resume round trip; TTL expiry routes to default_disposition; escalation chain advances on timeout; resume preserves authority freeze (REQ-100)",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.93",
    },
    {
        "req_id": "10C-REQ-177",
        "source_file": "agentic_process_mapping_v38.md + best-practice gap analysis 2026-04-29",
        "source_section": "HITL-NEW-D UWG dual-control for regulated/irreversible commits",
        "source_unit_type": "Derived requirement (banking/sudo dual-control precedent; openclaw immutable approval gate)",
        "source_text_short": "UWG requires two distinct identities for commit_class in {regulated, irreversible_state}",
        "canonical_requirement_statement": (
            "UWG MUST require two distinct authenticated identities to admit a CommitRequest whose "
            "commit_class is in {regulated, irreversible_state}. The first identity proposes the commit "
            "(via Exit X3C); the second identity admits it at UWG. Same identity for both roles is a "
            "contract violation. Dual-control receipts MUST be hash-chained into the L4 audit log "
            "alongside the standard UWGCommitReceipt."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "D. Governance / capability / replay / observability",
        "layer_owner": "L4 UWG",
        "runtime_phase": "Durable commit",
        "required_artifacts": "DualControlReceipt; commit_class declaration; identity_proposer; identity_admitter",
        "required_controls": "DualControlEnforcer; CommitClassClassifier; SameIdentityRefuser",
        "required_tests": "Same identity rejected; two distinct identities accepted; non-regulated commits unaffected; audit chain includes both identities",
        "severity_if_missing": "CRITICAL",
        "confidence_score": "0.94",
    },
    {
        "req_id": "10C-REQ-178",
        "source_file": "agentic_process_mapping_v38.md + best-practice gap analysis 2026-04-29",
        "source_section": "HITL-NEW-E human-on-the-loop parallel surface (advisory only)",
        "source_unit_type": "Derived requirement (Cloudflare HITL parallel feedback; Knock Agents SDK)",
        "source_text_short": "Parallel HITL dashboard consumes BUS D/E and emits next-run-only override signals",
        "canonical_requirement_statement": (
            "A parallel human-on-the-loop surface MUST consume BUS D/E HITL trigger signals (REQ-133) "
            "and surface in-flight Tier-T1/T2 runs to a non-blocking review dashboard. Reviewer "
            "overrides emitted by this surface MUST be advisory only and MUST be consumed at the "
            "next-run boundary by L6 (treated as LearningProposal-class), never mutating the current "
            "run. This requirement preserves the L6-cannot-rescue-current-run invariant while "
            "extracting human signal from in-flight observation."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "E. Metrics / evaluation / shadow / learning",
        "layer_owner": "L6 observability",
        "runtime_phase": "Runtime + Post-run learning",
        "required_artifacts": "HOTLOverrideSignal; HOTL_DASHBOARD_consumer_contract",
        "required_controls": "HOTLAdvisoryRouter; CurrentRunMutationRefuser; NextRunPromotionBinder",
        "required_tests": "Override during current run does not mutate it; override appears in L6 ingest as LearningProposal; advisory signal not confused with HITL APPROVE/REJECT verdict",
        "severity_if_missing": "MEDIUM",
        "confidence_score": "0.85",
    },
    {
        "req_id": "10C-REQ-179",
        "source_file": "agentic_process_mapping_v38.md + best-practice gap analysis 2026-04-29",
        "source_section": "HITL-NEW-F HITLDecisionReceipt for closed-loop calibration",
        "source_unit_type": "Derived requirement (industry telemetry norm; Galileo confidence-threshold calibration)",
        "source_text_short": "Each HITL cycle emits HITLDecisionReceipt with reviewer_id, latency, override flag for L6 calibration",
        "canonical_requirement_statement": (
            "Every HITL cycle MUST emit a HITLDecisionReceipt artifact containing: decision_id, run_id, "
            "risk_tier, reviewer_id, verdict in {APPROVE, MODIFY_DIFF, REJECT, RETURN_TO_L1, "
            "TIMEOUT_DEFAULT}, decision_latency_ms, override_vs_recommendation (bool), evidence_refs[], "
            "escalation_chain_position, rationale_text. This receipt MUST be ingested by L6 6A and "
            "used by 6B to calibrate the risk-tier classifier (REQ-174) and the confidence-promotion "
            "threshold tau, closing the loop on Galileo target rates (10-15 percent escalation, 80-90 "
            "percent confidence). Missing or malformed receipts block 6D promotion of any related "
            "calibration update."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "E. Metrics / evaluation / shadow / learning",
        "layer_owner": "HITL L5 + L6 shadow eval",
        "runtime_phase": "Escalation + Post-run learning",
        "required_artifacts": "HITLDecisionReceipt; risk_tier_calibration_report",
        "required_controls": "HITLReceiptEmitter; HITLReceiptValidator; RiskTierCalibrator; ThresholdRetuner",
        "required_tests": "Receipt schema completeness; missing receipt blocks 6D promotion; calibration output adjusts tau within bounds; override telemetry feeds regret accounting",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.91",
    },
]

for r in new_ledger:
    assert set(r.keys()) == set(ledger_fields), f"key mismatch in {r['req_id']}"

with ledger.open("a", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=ledger_fields, lineterminator="\n")
    for r in new_ledger:
        w.writerow(r)

new_matrix = []
for r in new_ledger:
    new_matrix.append({
        "10c_req_id": r["req_id"],
        "10a_req_id": "",
        "covered_by_10a": "false",
        "10a_coverage_type": "none",
        "coverage_gap_reason": f"NEW best-practice gap (Anthropic/OpenAI/Galileo); see {r['source_section']}",
    })
for r in new_matrix:
    assert set(r.keys()) == set(matrix_fields), f"matrix key mismatch in {r['10c_req_id']}"
with matrix.open("a", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=matrix_fields, lineterminator="\n")
    for r in new_matrix:
        w.writerow(r)

rows_after = list(csv.DictReader(ledger.open(encoding="utf-8")))
print(f"ledger after append: {len(rows_after)} rows; last 6 ids:", [r["req_id"] for r in rows_after[-6:]])
rows_after_m = list(csv.DictReader(matrix.open(encoding="utf-8")))
print(f"matrix after append: {len(rows_after_m)} rows; last 6 ids:", [r["10c_req_id"] for r in rows_after_m[-6:]])
