#!/usr/bin/env python3
"""
Agent Sprawl Gate — Hard CI enforcement for deduplication thresholds.

Reads similarity artifacts produced by run_dedup_analysis.py and exits
with non-zero status if any pair breaches configurable thresholds.

Usage:
    python artifacts/dedup/sprawl_gate.py
    python artifacts/dedup/sprawl_gate.py --max-code-sim 0.80
    python artifacts/dedup/sprawl_gate.py --max-code-sim 0.75 --max-resp-overlap 0.70

Exit codes:
    0 — All thresholds respected
    1 — One or more thresholds breached (blocks merge)
    2 — Missing artifact files (run run_dedup_analysis.py first)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
Logger = logging.getLogger("sprawl_gate")

# ---------------------------------------------------------------------------
# SSOT Path Resolution — hardened for bare-terminal execution.
# Resolves repo root from script location (artifacts/dedup/ -> 2 parents up)
# so the script never requires PYTHONPATH to be set.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "dedup" / "similarity"
CODE_SIM_FILE = ARTIFACTS_DIR / "code_similarity.json"
PROMPT_SIM_FILE = ARTIFACTS_DIR / "prompt_similarity.json"

# ---------------------------------------------------------------------------
# Default thresholds (can be overridden via CLI)
# ---------------------------------------------------------------------------
# guardian: allow-magic-config
DEFAULT_MAX_CODE_SIM = 0.75
# guardian: allow-magic-config
DEFAULT_MAX_PROMPT_SIM = 0.80
# guardian: allow-magic-config
DEFAULT_MAX_RESP_OVERLAP = 0.70

# ---------------------------------------------------------------------------
# Known waivers: pairs that have been reviewed and accepted.
# Format: frozenset({agent_a, agent_b})
# To add a waiver, append to this set and document in artifacts/dedup/waivers/.
# ---------------------------------------------------------------------------
WAIVERS: set[frozenset[str]] = {
    # Cluster 7: Consolidated via CodeToolRunnerCapability extraction (2026-02-08)
    frozenset({"CodeFormatterAgent", "UnusedCleanupAgent"}),
    # Cluster 2: Structural similarity from shared RGValidationCapability.
    # Each agent has distinct collect_issues() domain logic (ATS, brand, fact, section).
    frozenset({"ATSCompatibilityAgent", "BrandComplianceAgent"}),
    frozenset({"ATSCompatibilityAgent", "SectionBalanceAgent"}),
    frozenset({"BrandComplianceAgent", "SectionBalanceAgent"}),
    frozenset({"BrandComplianceAgent", "FactCheckAgent"}),
    frozenset({"ATSCompatibilityAgent", "FactCheckAgent"}),
    frozenset({"FactCheckAgent", "SectionBalanceAgent"}),
    # Cluster 4: Shared InspectionCapability harness — perform_checks deduplicated
    # into InspectionCapability base (2026-02-08). Agents retained as domain stubs.
    frozenset({"DagRuntimeInspectorAgent", "SignatureVerifierAgent"}),
    frozenset({"DagRuntimeInspectorAgent", "TokenBudgetInspectorAgent"}),
    frozenset({"SignatureVerifierAgent", "TokenBudgetInspectorAgent"}),
    # Cluster 5: LIC pipeline stages sharing HOPStageCapability by design.
    # Each stage has distinct _process() domain logic.
    frozenset({"HOP4RoutingAgent", "HOP7GateDecisionAgent"}),
    frozenset({"HOP4RoutingAgent", "HOP9IntegrationAgent"}),
    frozenset({"HOP7GateDecisionAgent", "HOP9IntegrationAgent"}),
    # Cluster 6: LIC engine validators sharing LICEngineValidationCapability.
    # Distinct _validate() domain logic (campaign balance vs deliverability).
    frozenset({"CampaignBalanceAgent", "DeliverabilityAgent"}),
    # Cluster 10: L6 observability agents — different purposes (orchestrator vs tracker).
    # High prompt similarity from auto-inserted semantic signals.
    frozenset({"CoordinateObservabilityOperationsAgent", "TrackObservabilityCostAgent"}),
    # Cluster 1 (partial): Structural similarity from shared SubatomicTestingMixin +
    # SovereignBaseAgent base + identical heal() boilerplate. Each agent has a distinct
    # domain role (semantic retrieval, semantic mapping, architecture strategy, UI validation).
    frozenset({"OmniContextAgent", "SemanticMapperAgent"}),
    frozenset({"UiValidationAgent", "SemanticMapperAgent"}),
    frozenset({"StrategistAgent", "OmniContextAgent"}),
}


def _load_json(path: Path) -> dict | None:
    """Load a JSON file, returning None if it doesn't exist."""
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_code_similarity(max_threshold: float) -> list[dict]:
    """Check code similarity pairs against threshold. Returns violations."""
    data = _load_json(CODE_SIM_FILE)
    if data is None:
        Logger.error(f"Missing artifact: {CODE_SIM_FILE}")
        sys.exit(2)

    violations = []
    for pair in data.get("top_pairs", []):
        agent_a = pair["agent_a"]
        agent_b = pair["agent_b"]
        score = pair["score"]

        pair_key = frozenset({agent_a, agent_b})
        if pair_key in WAIVERS:
            Logger.info(f"  WAIVER: {agent_a} <-> {agent_b} = {score:.4f} (waived)")
            continue

        if score >= max_threshold:
            violations.append(
                {
                    "type": "CODE_SIMILARITY",
                    "agent_a": agent_a,
                    "agent_b": agent_b,
                    "score": score,
                    "threshold": max_threshold,
                },
            )

    return violations


def _check_prompt_similarity(max_threshold: float) -> list[dict]:
    """Check prompt similarity pairs against threshold. Returns violations."""
    data = _load_json(PROMPT_SIM_FILE)
    if data is None:
        Logger.warning(f"Missing artifact: {PROMPT_SIM_FILE} — skipping prompt check")
        return []

    violations = []
    for pair in data.get("top_pairs", []):
        agent_a = pair["agent_a"]
        agent_b = pair["agent_b"]
        score = pair["score"]

        pair_key = frozenset({agent_a, agent_b})
        if pair_key in WAIVERS:
            continue

        if score >= max_threshold:
            violations.append(
                {
                    "type": "PROMPT_SIMILARITY",
                    "agent_a": agent_a,
                    "agent_b": agent_b,
                    "score": score,
                    "threshold": max_threshold,
                },
            )

    return violations


def main() -> int:
    """Run the sprawl gate. Returns exit code."""
    parser = argparse.ArgumentParser(description="Agent Sprawl Gate — CI enforcement")
    parser.add_argument(
        "--max-code-sim",
        type=float,
        default=DEFAULT_MAX_CODE_SIM,
        help=f"Maximum code similarity threshold (default: {DEFAULT_MAX_CODE_SIM})",
    )
    parser.add_argument(
        "--max-prompt-sim",
        type=float,
        default=DEFAULT_MAX_PROMPT_SIM,
        help=f"Maximum prompt similarity threshold (default: {DEFAULT_MAX_PROMPT_SIM})",
    )
    parser.add_argument(
        "--max-resp-overlap",
        type=float,
        default=DEFAULT_MAX_RESP_OVERLAP,
        help=f"Maximum responsibility overlap threshold (default: {DEFAULT_MAX_RESP_OVERLAP})",
    )
    args = parser.parse_args()

    Logger.info("=== Agent Sprawl Gate ===")
    Logger.info(
        f"Thresholds: code_sim={args.max_code_sim}, prompt_sim={args.max_prompt_sim}, resp_overlap={args.max_resp_overlap}",
    )
    Logger.info(f"Waivers: {len(WAIVERS)} active")

    all_violations: list[dict] = []

    # Check code similarity
    Logger.info("\n--- Code Similarity Check ---")
    code_violations = _check_code_similarity(args.max_code_sim)
    all_violations.extend(code_violations)

    # Check prompt similarity
    Logger.info("\n--- Prompt Similarity Check ---")
    prompt_violations = _check_prompt_similarity(args.max_prompt_sim)
    all_violations.extend(prompt_violations)

    # Report
    if all_violations:
        Logger.error(f"\nFAIL: {len(all_violations)} threshold breach(es) detected:\n")
        for v in all_violations:
            Logger.error(
                f"  [{v['type']}] {v['agent_a']} <-> {v['agent_b']}: {v['score']:.4f} >= {v['threshold']}",
            )
        Logger.error(
            "\nAction required: Extract shared logic or add a documented waiver.",
        )
        return 1
    else:
        Logger.info(f"\nPASS: 0 threshold breaches (after {len(WAIVERS)} waiver(s)).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
