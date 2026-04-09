"""ADG Prompt Assembly — structured packet builders for ADG results.

Converts raw ADG canonical outputs (SQLite, JSON reports, graph DB queries,
infra wiring findings, P0-P3 gate outputs) into grounded, deterministic,
contradiction-aware, token-budgeted PromptEnvelope packets.

Architecture:
    retrieval/   — C0-side adapters that fetch raw data from canonical sources
    shaping/     — Evidence shaping pipeline (dedupe, normalize, reconcile)
    packets/     — Packet registry, templates, and builders
    budgeting/   — Token budget allocation and overflow handling
    cli.py       — CLI entrypoint

Usage:
    python -m tools.adg.prompt_assembly --packet executive_summary
    python -m tools.adg.prompt_assembly --packet determinism_rca --format markdown
    python -m tools.adg.prompt_assembly --all
"""

from tools.adg.prompt_assembly.contracts import (
    ContradictionFlag,
    EvidenceBundle,
    EvidenceItem,
    PromptAssemblyStatus,
    PromptEnvelope,
)

__all__ = [
    "ContradictionFlag",
    "EvidenceBundle",
    "EvidenceItem",
    "PromptAssemblyStatus",
    "PromptEnvelope",
]
