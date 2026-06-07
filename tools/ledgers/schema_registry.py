"""tools.ledgers.schema_registry — Authoritative registry of all intelligence ledgers.

Each entry describes a ledger's DDL file, on-disk SQLite path, writer hook, and
consulting skill. The registry is the single source of truth consulted by:

    - tools/ledgers/apply_schema.py  : migrates every ledger in one pass
    - tools/ledgers/writer.py        : resolves db_path by ledger name
    - tools/ledgers/consulter.py     : resolves db_path by ledger name
    - ops_scripts/ci/check_ledger_writer_contract.py (W5): verifies hooks exist

To add a ledger:
    1. Write .cursor/schemas/<name>_ledger.schema.sql
    2. Add a LedgerSpec to LEDGER_REGISTRY below
    3. Run: python tools/ledgers/apply_schema.py
    4. Implement writer extension in the hook referenced by `writer_hook`
    5. Create consulting skill at .cursor/skills/ledger-consulter-<name>/SKILL.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGERS_DIR = REPO_ROOT / "artifacts" / "ledgers"
SCHEMAS_DIR = REPO_ROOT / ".cursor" / "schemas"
CURSOR_SCRIPTS_DIR = ".cursor/scripts"


@dataclass(frozen=True)
class LedgerSpec:
    """Immutable spec for one intelligence ledger."""

    name: str  # short name; becomes db filename stem
    purpose: str  # one-line human-readable purpose
    schema_file: str  # filename under .cursor/schemas/
    writer_hook: str  # repo-relative path of the post-hook that writes rows
    consulting_skill: str  # repo-relative path of the consulting skill SKILL.md
    wave: str  # W0–W5 assignment from the plan
    sunset_criterion: str  # observable condition that retires this ledger

    @property
    def db_path(self) -> Path:
        return LEDGERS_DIR / f"{self.name}.sqlite"

    @property
    def schema_path(self) -> Path:
        return SCHEMAS_DIR / self.schema_file


LEDGER_REGISTRY: tuple[LedgerSpec, ...] = (
    LedgerSpec(
        name="tool_routing",
        purpose="Retrieval-tool choice precision/recall; which query features → which tool.",
        schema_file="tool_routing_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/post_cursor_agent_adg_audit.py",
        consulting_skill=".cursor/skills/ledger-consulter-tool-routing/SKILL.md",
        wave="W1.1",
        sunset_criterion="grep-for-deps violation rate under 1% for 90 consecutive days",
    ),
    LedgerSpec(
        name="refactor_outcome",
        purpose="Predicted vs actual P-count delta per refactoring wave; rollback attribution.",
        schema_file="refactor_outcome_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/post_commit_outcome_binder.py",
        consulting_skill=".cursor/skills/ledger-consulter-refactor-outcome/SKILL.md",
        wave="W1.2",
        sunset_criterion="prediction accuracy ≥85% for 4 consecutive waves",
    ),
    LedgerSpec(
        name="prompt_classifier",
        purpose="T0/T1/T2/T3 prediction accuracy vs actual files-edited/lines/layers.",
        schema_file="prompt_classifier_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/pre_prompt_classifier.py",
        consulting_skill=".cursor/skills/ledger-consulter-prompt-classifier/SKILL.md",
        wave="W2.1",
        sunset_criterion="classifier F1 ≥0.90 across all tiers for 30 consecutive days",
    ),
    LedgerSpec(
        name="mcp_invocation",
        purpose="Per-MCP-server latency, retries, hang attribution; drives SLO.",
        schema_file="mcp_invocation_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/post_mcp_audit.py",
        consulting_skill=".cursor/skills/ledger-consulter-mcp-invocation/SKILL.md",
        wave="W2.2",
        sunset_criterion="upstream anthropics/claude-agent-sdk-typescript#41 closed AND p95 latency stable 30d",
    ),
    LedgerSpec(
        name="hotspot_defect",
        purpose="Hotspot rank vs actual 30-day defect/churn; drives impact-formula coefficients.",
        schema_file="hotspot_defect_ledger.schema.sql",
        writer_hook="ops_scripts/calibration/hotspot_defect_join.py",
        consulting_skill=".cursor/skills/ledger-consulter-hotspot-defect/SKILL.md",
        wave="W3.1",
        sunset_criterion="formula coefficients stable (no ADR change) for 2 consecutive quarters",
    ),
    LedgerSpec(
        name="deferred_scope_calibration",
        purpose="Computed P-band vs actual days-to-done for Wave/Phase rows; tunes scorer thresholds.",
        schema_file="deferred_scope_calibration_ledger.schema.sql",
        writer_hook="ops_scripts/calibration/deferred_scope_poller.py",
        consulting_skill=".cursor/skills/ledger-consulter-deferred-scope-calibration/SKILL.md",
        wave="W3.2",
        sunset_criterion="band-threshold drift under 5% for 2 consecutive quarters",
    ),
    LedgerSpec(
        name="guardian_exemption",
        purpose="Guardian-exemption lifecycle; RCA→exemption linkage for silent-failure attribution.",
        schema_file="guardian_exemption_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/post_write_audit.py",
        consulting_skill=".cursor/skills/ledger-consulter-guardian-exemption/SKILL.md",
        wave="W4.1",
        sunset_criterion="zero exemption-attributed defects for 180 days",
    ),
    LedgerSpec(
        name="progress_eta",
        purpose="ProgressReporter predicted vs actual duration; calibrates subprocess timeouts.",
        schema_file="progress_eta_ledger.schema.sql",
        writer_hook="tools/progress_display.py",
        consulting_skill=".cursor/skills/ledger-consulter-progress-eta/SKILL.md",
        wave="W4.2",
        sunset_criterion="ETA overrun ratio within ±20% for 90 consecutive days",
    ),
    LedgerSpec(
        name="memory_recall",
        purpose="Memory-MCP recalled entities vs session reference; shrinks context pollution.",
        schema_file="memory_recall_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/post_cursor_agent_writeback_audit.py",
        consulting_skill=".cursor/skills/ledger-consulter-memory-recall/SKILL.md",
        wave="W4.3",
        sunset_criterion="entity hit-rate ≥0.60 after 3 calibration rounds",
    ),
    LedgerSpec(
        name="test_selection",
        purpose="ADG-driven test triage precision/recall; actual regression coverage per change-set.",
        schema_file="test_selection_ledger.schema.sql",
        writer_hook=f"{CURSOR_SCRIPTS_DIR}/post_run_audit.py",
        consulting_skill=".cursor/skills/ledger-consulter-test-selection/SKILL.md",
        wave="W4.4",
        sunset_criterion="triage recall ≥0.95 for 2 consecutive quarters",
    ),
    LedgerSpec(
        name="router_l2_cascade",
        purpose=(
            "L2/cascade router (HealingRouter) decisions and outcomes — "
            "tier/provider/EU/Brier per constitutional §29 row #4."
        ),
        schema_file="router_l2_cascade_ledger.schema.sql",
        writer_hook="agentic_core/L2_execution/healers/healing_router.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l2-cascade/SKILL.md",
        wave="W5.1",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l1_c0",
        purpose=(
            "L1/c0 router (RetrievalRouter) decisions and outcomes — "
            "intent_class/dim_tier/Brier vs SLO budget per constitutional §29 row #3."
        ),
        schema_file="router_l1_c0_ledger.schema.sql",
        writer_hook="agentic_core/L1_cognition/reasoning/retrieval_router.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l1-c0/SKILL.md",
        wave="W5.2",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l6_promo",
        purpose=(
            "L6/promo router (promotion_decision) verdicts — Wilson CI floors "
            "+ candidate vs baseline (k, n) per constitutional §29 row #9."
        ),
        schema_file="router_l6_promo_ledger.schema.sql",
        writer_hook="agentic_core/L6_observability/promotion_gates.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l6-promo/SKILL.md",
        wave="W5.3",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l3_sovereign_mcp",
        purpose=(
            "L3/sovereign_mcp router (SovereignMcpRouter.resolve_violation) canon-key dispatches — "
            "L0/L1/L2/L3/L4/L5 layer routing decisions per constitutional §29 non-matrix."
        ),
        schema_file="router_l3_sovereign_mcp_ledger.schema.sql",
        writer_hook="agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l3-sovereign-mcp/SKILL.md",
        wave="W5.9",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l3_reroute",
        purpose=(
            "L3/reroute router (RerouteCeiling.attempt_reroute) ceiling decisions — "
            "allow/exceeded attribution per constitutional §29 row #6."
        ),
        schema_file="router_l3_reroute_ledger.schema.sql",
        writer_hook="agentic_core/L3_orchestration/exit_control/reroute_governance.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l3-reroute/SKILL.md",
        wave="W5.8",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l5_hitl",
        purpose=(
            "L5/hitl router (HITLApprovalGate.evaluate) human-approval decisions — "
            "approve/modify/reject/escalate per constitutional §29 row #8."
        ),
        schema_file="router_l5_hitl_ledger.schema.sql",
        writer_hook="agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l5-hitl/SKILL.md",
        wave="W5.8",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l4_uwg",
        purpose=(
            "L4/uwg router (DurableWriteGateway.commit) commit/blocked decisions — "
            "validation/lock-contention/happy-path attribution per constitutional §29 row #7."
        ),
        schema_file="router_l4_uwg_ledger.schema.sql",
        writer_hook="agentic_core/L4_state/uwg/durable_write_gateway.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l4-uwg/SKILL.md",
        wave="W5.7",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l0_ensemble",
        purpose=(
            "L0/ensemble router (EnsembleRouter.route + update_outcome) ensemble decisions — "
            "durable backing for in-memory MetaLearner per constitutional §29 non-matrix."
        ),
        schema_file="router_l0_ensemble_ledger.schema.sql",
        writer_hook="agentic_core/L0_routing/reasoning/ensemble_router.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l0-ensemble/SKILL.md",
        wave="W5.6",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l0_path",
        purpose=(
            "L0/path router (PathRouter.route_with_confidence) abstain decisions — "
            "A/B/C/D/R5 path selection per constitutional §29 non-matrix."
        ),
        schema_file="router_l0_path_ledger.schema.sql",
        writer_hook="agentic_core/L0_routing/reasoning/path_router.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l0-path/SKILL.md",
        wave="W5.5",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l0_agentic",
        purpose=(
            "L0/agentic router (AgenticRouter.route) intent-classified dispatches — "
            "min_confidence threshold + handler outcome per constitutional §29 non-matrix."
        ),
        schema_file="router_l0_agentic_ledger.schema.sql",
        writer_hook="agentic_core/L0_routing/reasoning/agentic_router.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l0-agentic/SKILL.md",
        wave="W5.5",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l0_bandit",
        purpose=(
            "L0/bandit router (NamespaceBandit) decisions and outcomes — "
            "Thompson sampling per (namespace, route) per constitutional §29 row #1."
        ),
        schema_file="router_l0_bandit_ledger.schema.sql",
        writer_hook="agentic_core/L0_routing/reasoning/namespace_bandit.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l0-bandit/SKILL.md",
        wave="W5.4",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="router_l6_regret",
        purpose=(
            "L6/regret router (RegretLedger.record) per-decision regret samples "
            "— top-offender layer attribution per constitutional §29 row #10."
        ),
        schema_file="router_l6_regret_ledger.schema.sql",
        writer_hook="agentic_core/L6_observability/regret_accounting.py",
        consulting_skill=".cursor/skills/ledger-consulter-router-l6-regret/SKILL.md",
        wave="W5.3",
        sunset_criterion=(
            "90 consecutive days with zero §29 router-enforcement violations "
            "AND 4 consecutive in-band weekly calibration reports"
        ),
    ),
    LedgerSpec(
        name="eval_harness_outcome",
        purpose=(
            "Per-run AppSpecificEvaluator results from the v6 Exit pipeline — "
            "bound/passed/score/hitl_policy/disposition per app. Evidence surface "
            "for audit BLOCKER #10 feedback loop and the apps_* harness-parity "
            "CI gate (plan apps-eval-harness-parity-f8d4a2 W5.P6/P7)."
        ),
        schema_file="eval_harness_outcome_ledger.schema.sql",
        writer_hook="agentic_core/L3_orchestration/exit_eval/v6/pipeline.py",
        consulting_skill=".cursor/skills/ledger-consulter-eval-harness-outcome/SKILL.md",
        wave="W5.P7",
        sunset_criterion=(
            "All 8 runtime apps green on check_app_domain_harness_parity "
            "AND 4 consecutive weekly rollups show zero fail-open LLM-judge dims"
        ),
    ),
    LedgerSpec(
        name="ask_user_question",
        purpose=(
            "Enriched ask_user_question decisions — recommendation vs selection tracking, "
            "confidence calibration, and UI invariant compliance for the shadow learning loop."
        ),
        schema_file="ask_user_question_ledger.schema.sql",
        writer_hook="tools/ledgers/ask_user_question_ledger.py",
        consulting_skill=".cursor/skills/ledger-consulter-ask-user-question/SKILL.md",
        wave="W1.5",
        sunset_criterion=(
            "recommendation acceptance rate stable ≥80% for 90 consecutive days "
            "AND confidence calibration drift under 5% for 2 consecutive quarters"
        ),
    ),
    LedgerSpec(
        name="apps_qna_pack_lifecycle",
        purpose=(
            "apps_qna pack build / lint / self-eval / route-select / paste-set "
            "/ promotion decisions — durable record surface that W4 NamespaceBandit "
            "+ Wilson CI promotion gates + W5 system_learning consume for "
            "cross-interview transfer per constitutional §29."
        ),
        schema_file="apps_qna_pack_lifecycle_ledger.schema.sql",
        writer_hook="apps_qna/builder/card_pack_builder.py",
        consulting_skill=".cursor/skills/ledger-consulter-apps-qna-pack-lifecycle/SKILL.md",
        wave="W1.4",
        sunset_criterion=(
            "apps_qna spine integration plan W5 closes "
            "AND 4 consecutive interview-outcome calibration reports stable"
        ),
    ),
)


def get(name: str) -> LedgerSpec:
    """Resolve a LedgerSpec by name; raise KeyError if not registered."""
    for spec in LEDGER_REGISTRY:
        if spec.name == name:
            return spec
    raise KeyError(f"Unknown ledger: {name!r}. Registered: {[s.name for s in LEDGER_REGISTRY]}")


def all_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in LEDGER_REGISTRY)
