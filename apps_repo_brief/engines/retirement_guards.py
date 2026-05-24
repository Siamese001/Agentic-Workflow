"""W3 retirement guards — IngestionEngine, BriefAssemblyEngine, StyleGateValidator.

Consolidated from ingestion_retirement_notice.py and spine_restructure_notices.py.
"""

from __future__ import annotations

_RETIREMENT_REASON = (
    "IngestionEngine live-scan retired in W3. "
    "Use repo_brief_docs L4 surface via C0 retrieval lanes. "
    "See apps_repo_brief/engines/retirement_guards.py."
)

BRIEF_ASSEMBLY_ENGINE_OWNER = "PA (prompt) + L2 (render)"
BRIEF_ASSEMBLY_ENGINE_SPLIT_AT = "W3"

STYLE_GATE_VALIDATOR_OWNER = "L2.E4 heal + Exit v6 gate"
STYLE_GATE_VALIDATOR_SPLIT_AT = "W3 (L2.E4) + W4 (Exit gate)"


def ingestion_engine_retired() -> None:
    """Raise if called — hard guard against accidental IngestionEngine use."""
    raise RuntimeError(f"[apps_repo_brief] {_RETIREMENT_REASON}")


def brief_assembly_engine_retired() -> None:
    """Hard guard — apps_repo_brief must not instantiate BriefAssemblyEngine."""
    raise RuntimeError(
        "[apps_repo_brief] BriefAssemblyEngine is retired. "
        "Prompt slot composition: RepoBriefPACompiler. "
        "Narrative rendering: L2 governed gateway. See P3.5."
    )


def style_gate_validator_retired() -> None:
    """Hard guard — apps_repo_brief must not instantiate StyleGateValidator as pre-C0 gate."""
    raise RuntimeError(
        "[apps_repo_brief] StyleGateValidator as pre-C0 gate is retired. "
        "Same-authority repair: L2.E4 heal pass. "
        "Persistent violation gate: Exit v6 (W4). See P3.6."
    )
