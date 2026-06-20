# `L6_system_learning/engines/` — Chapter Map

**Layer:** L6 (active) · **Surface:** `__l6_chapter__` empty on package `__init__.py` (cross-chapter bucket)  
**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../../.codex/plans/l6-reorg-deferred-followup-f3a9c2.md) W4.1

This directory is a **flat cross-chapter engine bucket** (~128 modules). Do not assume a single doctrinal chapter; use the map below when placing new modules.

## Chapter ownership (primary)

| Chapter | Representative engines | Notes |
|---------|------------------------|-------|
| **06.3** Outcome / trajectory | `outcome_evaluation_engine`, `trajectory_evaluation_engine`, `g_gate_regression_checker` | Eval spine |
| **06.5** Fusion / RCA | `signal_aggregator_engine`, `rca_cluster_engine`, `meta_learning_bus` | Pattern synthesis |
| **06.6** Proposals | `optimization_proposal_engine`, `proposal_validation_engine`, `rule_drafting_engine` | Admission drafting |
| **06.7** Promotion / gauntlet | `approval_gauntlet_engine`, `live_exit_control_gate` | UWG-facing gates |
| **06.8** KPIs / quality | `prompt_drift_detector`, `prompt_safety_validator`, `governance_reward_model` | Quality repair |

## Cross-cutting subpackages

| Subdir | Role |
|--------|------|
| `governance_v4/` | MCP / egress / identity governance helpers |
| `v7_kpi_board/` | KPI board engines (v7 contract) |

## Related surfaces

- **Passive eval:** `agentic_core/L6_observability/shadow_eval/` (canonical shadow pipeline)
- **Legacy eval utils:** `agentic_core/L6_observability/utils/evaluation/` — see [ADR-086](../../../docs/architecture/adr/ADR-086-l6-eval-surface-consolidation.md)
- **Active validators:** `agentic_core/L6_system_learning/validators/` (06.2)

## Physical split (deferred)

Directory restructure into `engines/06.3/`, `engines/06.6/`, etc. is **out of scope** for follow-up W4 — requires dedicated plan after [ADR-086](../../../docs/architecture/adr/ADR-086-l6-eval-surface-consolidation.md) acceptance.
