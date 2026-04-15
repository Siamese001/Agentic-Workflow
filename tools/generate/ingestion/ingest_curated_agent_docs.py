"""Ingest a curated high-signal corpus into the ``curated_agent_docs`` ChromaDB collection.

This script is the authoritative entry-point for the curated collection.  It reuses the
Phase 2-3 metadata schema, canonical/historical rules, chunking policy, and dedup rules
verbatim.  Do NOT write to ``ext_knowledge`` or ``arch_docs``; those collections are managed
by their own ingestion scripts.

────────────────────────────────────────────────────────────────────────────────────────────
SCORING RUBRIC  (7 dimensions, weights sum to 1.0)
────────────────────────────────────────────────────────────────────────────────────────────
  Dimension                  Weight   Description
  ─────────────────────────  ──────   ──────────────────────────────────────────────────────
  canonicality               0.25     Is this the primary / authoritative source?
  arch_depth                 0.20     Does it contain deep architectural decisions?
  durability                 0.20     Will this remain accurate 12+ months from now?
  impl_specificity           0.15     Does it describe concrete implementation patterns?
  safety_eval_value          0.10     Does it address guardrails, evals, or safety?
  retrieval_usefulness       0.05     Will it produce useful answers for future queries?
  repo_alignment             0.05     Is it aligned with *this* repo's architecture?

  Final score = sum(weight_i × dim_i) / 5   (dims scored 0–5; result in [0.0, 1.0])

────────────────────────────────────────────────────────────────────────────────────────────
RANKED KEEP / EXCLUDE DECISIONS
────────────────────────────────────────────────────────────────────────────────────────────

  KEEP — 32 sources across 6 topic buckets

  rank  score  path / url (truncated)
  ────  ─────  ──────────────────────────────────────────────────────────────────────────
   1    0.97   docs/architecture/adr/adr-0043-structural-agentic-checks.md
   2    0.93   docs/architecture/adr/adr-002-interface-protocol-first.md
   3    0.95   docs/reference/agentic_process_mapping_exec.md
   4    0.92   docs/architecture/governed-app-contract.md
   5    0.91   docs/reference/agentic_process_mapping_v29.md
   6    0.90   docs/architecture/adr/adr-0042-skills-consolidation.md
   7    0.90   docs/architecture/eval_pipeline_acceptance.md
   8    0.89   docs/architecture/adr/ADR-018-chromadb-as-canonical-vector-store.md
   9    0.87   docs/architecture/adr/ADR-019-adg-materialized-views.md
  10    0.87   docs/svp/Retrieval_System_SVP.md
  11    0.85   docs/svp/Technical_Implementation_Guide.md
  12    0.84   docs/STANDARDS.md
  13    0.83   docs/architecture/adg-graph-projection.md
  14    0.78   AGENTS.md
  15    0.86   .../openai-agents-python/docs/guardrails.md        (GitHub raw)
  16    0.82   .../openai-agents-python/docs/agents.md            (GitHub raw)
  17    0.82   .../openai-agents-python/docs/tools.md             (GitHub raw)
  18    0.81   .../openai-agents-python/README.md                 (GitHub raw)
  19    0.80   .../openai-agents-python/docs/handoffs.md          (GitHub raw)
  20    0.80   .../anthropic-cookbook/patterns/agents/evaluator_optimizer.ipynb
  21    0.80   .../openai-agents-python/docs/running_agents.md    (GitHub raw)
  22    0.79   .../anthropic-cookbook/patterns/agents/orchestrator_workers.ipynb
  23    0.79   .../openai-agents-python/docs/tracing.md           (GitHub raw)
  24    0.77   .../anthropic-cookbook/patterns/agents/basic_workflows.ipynb
  25    0.87   .../modelcontextprotocol/python-sdk/README.md              (MCP SDK)
  26    0.85   .../openai-agents-python/docs/mcp.md                       (GitHub raw)
  27    0.81   .../openai-agents-python/docs/context.md                   (GitHub raw)
  28    0.79   .../openai-agents-python/docs/results.md                   (GitHub raw)
  29    0.78   .../langchain-ai/langgraph/README.md                       (GitHub raw)
  30    0.75   .../microsoft/autogen/README.md                            (GitHub raw)
  31    0.74   .../openai-agents-python/docs/models.md                    (GitHub raw)
  32    0.72   .../anthropic-cookbook/patterns/agents/subagent.ipynb      (conditional)

  EXCLUDE — version churn (superseded by v29 or exec):
    docs/reference/_archive/Agentic Process Mapping/agentic_process_mapping_v10.md … v28.md
    docs/reference/agentic_process_mapping_non_technical.md

  EXCLUDE — mirror collapse (same content as GitHub raw):
    openai.github.io/openai-agents-python/ (home)
    openai.github.io/openai-agents-python/agents/ … results/

  EXCLUDE — shallow / marketing / tutorial collapse:
    anthropics/anthropic-cookbook/main/README.md          → collapses to pattern notebooks
    anthropics/tool_use/customer_service_agent.ipynb      → tutorial, lower signal

────────────────────────────────────────────────────────────────────────────────────────────
FAIL-CLOSED RULES
────────────────────────────────────────────────────────────────────────────────────────────
  • required=True fetch failure   → raise IngestionError (abort, do not partial-write)
  • malformed metadata            → raise MetadataValidationError (abort)
  • duplicate canonical_url entry → raise IngestionError at startup (config error)
  • empty / too-short chunk       → skip silently (logged)

Usage:
    python tools/generate/ingestion/ingest_curated_agent_docs.py --dry-run
    python tools/generate/ingestion/ingest_curated_agent_docs.py [--store-path PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"

COLLECTION_NAME = "curated_agent_docs"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 32
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80
REQUEST_TIMEOUT = 20

# All 21 required metadata keys (Phase 2-3 schema + curated extras + authority contract)
REQUIRED_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "artifact_type",
        "doc_type",
        "doc_family",
        "file_path",
        "layer",
        "chunk_index",
        "canonical_digest",
        "source",
        "title",
        "heading_path",
        "authority_level",
        "canonical",
        "retrieval_weight",
        "source_area",
        "topic_bucket",
        "source_url",
        "collapse_group",
        "source_collection",
        "authority_tier",
        "normative_scope",
        "invalid_for_normative_use",
    }
)

_TOPIC_BUCKET_TO_TIER: dict[str, str] = {
    "tool_contracts": "T2_standard",
    "arch_standards": "T3_guidance",
    "orchestration": "T3_guidance",
    "rag_retrieval": "T3_guidance",
    "safety_eval": "T3_guidance",
    "observability": "T3_guidance",
}
_DEFAULT_AUTHORITY_TIER = "T3_guidance"

SourceType = Literal["local", "web"]
TopicBucket = Literal[
    "arch_standards",
    "orchestration",
    "rag_retrieval",
    "safety_eval",
    "observability",
    "tool_contracts",
]

# ─────────────────────────────────────────────────────────────────────────────
# Curated source catalogue
# ─────────────────────────────────────────────────────────────────────────────
# Each entry drives both scoring transparency (dry-run report) and ingestion.
# Fields:
#   source_type  "local" (file in repo) | "web" (fetched URL)
#   path         repo-relative path or full URL
#   title        human-readable title stored in metadata
#   doc_type     "markdown" | "web" | "notebook"
#   doc_family   Phase-2 taxonomy label
#   topic_bucket one of the 6 TopicBucket values
#   authority_level  float [0.0, 1.0] for reranking
#   canonical    bool — True for primary/authoritative sources
#   collapse_group   dedup cluster string (mirrors / version family)
#   keep_reason  one-line justification
#   score        pre-computed rubric score [0.0, 1.0]
#   required     bool — if True, fetch failure aborts with IngestionError

CURATED_SOURCES: list[dict] = [
    # ── Internal canonical ADRs ────────────────────────────────────────────
    {
        "source_type": "local",
        "path": "docs/architecture/adr/adr-0043-structural-agentic-checks.md",
        "title": "ADR-0043: Structural Conformance & Agentic Anti-Pattern Checks",
        "doc_type": "markdown",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_adr",
        "keep_reason": "Canonical ADR defining structural conformance + agentic anti-pattern checks; highest arch-depth + safety-eval value.",
        "score": 0.97,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/architecture/adr/adr-002-interface-protocol-first.md",
        "title": "ADR-002: Interface & Protocol-First Design",
        "doc_type": "markdown",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_adr",
        "keep_reason": "Foundational interface-first ADR; durable design principle governing all layer contracts.",
        "score": 0.93,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/architecture/adr/adr-0042-skills-consolidation.md",
        "title": "ADR-0042: Skills Consolidation",
        "doc_type": "markdown",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_adr",
        "keep_reason": "Documents skills architecture and consolidation decisions; durable standards for Cascade skill design.",
        "score": 0.90,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/architecture/adr/ADR-018-chromadb-as-canonical-vector-store.md",
        "title": "ADR-018: ChromaDB as Canonical Vector Store",
        "doc_type": "markdown",
        "doc_family": "adr",
        "topic_bucket": "rag_retrieval",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_adr",
        "keep_reason": "Canonical ADR for retrieval infrastructure; directly relevant to RAG architecture queries.",
        "score": 0.89,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/architecture/adr/ADR-019-adg-materialized-views.md",
        "title": "ADR-019: ADG Materialized Views",
        "doc_type": "markdown",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_adr",
        "keep_reason": "ADG architecture decision; critical for understanding structural analysis layer.",
        "score": 0.87,
        "required": True,
    },
    # ── Internal process mapping (latest + exec only) ──────────────────────
    {
        "source_type": "local",
        "path": "docs/reference/agentic_process_mapping_exec.md",
        "title": "Agentic System Process Map — Executive Summary",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_process_mapping",
        "keep_reason": "THE canonical executive process map; dense L0-L5 orchestration diagram, write gate, bounded autonomy rules.",
        "score": 0.95,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/reference/agentic_process_mapping_v29.md",
        "title": "Agentic System Process Map v29 — Routing & Dispatch Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.90,
        "canonical": True,
        "collapse_group": "repo_process_mapping",
        "keep_reason": "Latest version of the full routing/dispatch process map; collapses all v2-v28 (archived).",
        "score": 0.91,
        "required": True,
    },
    # ── Internal governance & eval ────────────────────────────────────────
    {
        "source_type": "local",
        "path": "docs/architecture/governed-app-contract.md",
        "title": "Governed App Contract",
        "doc_type": "markdown",
        "doc_family": "contract",
        "topic_bucket": "safety_eval",
        "authority_level": 0.85,
        "canonical": True,
        "collapse_group": "repo_architecture",
        "keep_reason": "Defines app-level governance contract; high safety_eval + arch_depth + durability.",
        "score": 0.92,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/architecture/eval_pipeline_acceptance.md",
        "title": "Eval Pipeline Acceptance Criteria",
        "doc_type": "markdown",
        "doc_family": "architecture",
        "topic_bucket": "safety_eval",
        "authority_level": 0.85,
        "canonical": True,
        "collapse_group": "repo_architecture",
        "keep_reason": "Defines eval acceptance criteria and gating rules; directly relevant to safety/eval queries.",
        "score": 0.90,
        "required": True,
    },
    # ── Internal retrieval + SVP ──────────────────────────────────────────
    {
        "source_type": "local",
        "path": "docs/svp/Retrieval_System_SVP.md",
        "title": "Retrieval System SVP",
        "doc_type": "markdown",
        "doc_family": "spec",
        "topic_bucket": "rag_retrieval",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "repo_svp",
        "keep_reason": "Authoritative retrieval system specification; best single doc for RAG architecture queries.",
        "score": 0.87,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/svp/Technical_Implementation_Guide.md",
        "title": "Technical Implementation Guide (SVP)",
        "doc_type": "markdown",
        "doc_family": "guide",
        "topic_bucket": "rag_retrieval",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "repo_svp",
        "keep_reason": "Detailed implementation guide complementing retrieval SVP; high impl_specificity.",
        "score": 0.85,
        "required": True,
    },
    # ── Constitutional rules (covers UWG, C0, L5 policy, determinism) ────
    {
        "source_type": "local",
        "path": ".windsurf/rules/constitutional.md",
        "title": "Constitutional Floor — Hard Constraints",
        "doc_type": "markdown",
        "doc_family": "standard",
        "topic_bucket": "safety_eval",
        "authority_level": 1.0,
        "canonical": True,
        "collapse_group": "repo_standards",
        "keep_reason": "Canonical constitutional constraints; covers UWG, C0, L5 policy plane, determinism, ADG gates — directly answers policy/safety queries.",
        "score": 0.88,
        "required": True,
    },
    {
        "source_type": "local",
        "path": ".windsurf/rules/global_rules.md",
        "title": "Global Rules — Always-On Policy",
        "doc_type": "markdown",
        "doc_family": "standard",
        "topic_bucket": "arch_standards",
        "authority_level": 0.90,
        "canonical": True,
        "collapse_group": "repo_standards",
        "keep_reason": "MCP authority table, subprocess discipline, exception handling — authoritative for tooling and architecture standards queries.",
        "score": 0.82,
        "required": True,
    },
    # ── Internal standards + ADG architecture ────────────────────────────
    {
        "source_type": "local",
        "path": "docs/STANDARDS.md",
        "title": "Repository Standards",
        "doc_type": "markdown",
        "doc_family": "standard",
        "topic_bucket": "arch_standards",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "repo_standards",
        "keep_reason": "Cross-cutting coding standards; durable and broadly applicable.",
        "score": 0.84,
        "required": True,
    },
    {
        "source_type": "local",
        "path": "docs/architecture/adg-graph-projection.md",
        "title": "ADG Graph Projection Architecture",
        "doc_type": "markdown",
        "doc_family": "architecture",
        "topic_bucket": "arch_standards",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "repo_architecture",
        "keep_reason": "Deep architectural doc on ADG projection; critical for structural analysis queries.",
        "score": 0.83,
        "required": False,
    },
    {
        "source_type": "local",
        "path": "AGENTS.md",
        "title": "Agents Guide",
        "doc_type": "markdown",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "authority_level": 0.65,
        "canonical": True,
        "collapse_group": "repo_standards",
        "keep_reason": "Primary on-boarding guide for Cascade; covers MCP authority table and constitutional rules.",
        "score": 0.78,
        "required": False,
    },
    # ── External: OpenAI Agents Python (GitHub raw — canonical source) ────
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/guardrails.md",
        "title": "OpenAI Agents Python — Guardrails Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "safety_eval",
        "authority_level": 0.85,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Canonical OpenAI guardrails reference; highest safety_eval value in external corpus.",
        "score": 0.86,
        "required": True,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/agents.md",
        "title": "OpenAI Agents Python — Agents Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.85,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Core agent architecture reference; collapses github.io HTML mirror.",
        "score": 0.82,
        "required": True,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tools.md",
        "title": "OpenAI Agents Python — Tools Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "tool_contracts",
        "authority_level": 0.85,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Canonical tool contract reference; collapses github.io HTML mirror.",
        "score": 0.82,
        "required": True,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md",
        "title": "OpenAI Agents Python README",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Primary overview of OpenAI agent framework; canonical entry point.",
        "score": 0.81,
        "required": True,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/handoffs.md",
        "title": "OpenAI Agents Python — Handoffs Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Canonical handoff patterns; critical for multi-agent orchestration queries.",
        "score": 0.80,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/running_agents.md",
        "title": "OpenAI Agents Python — Running Agents Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Runtime loop and lifecycle reference; complements agents.md.",
        "score": 0.80,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tracing.md",
        "title": "OpenAI Agents Python — Tracing Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "observability",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Canonical observability/tracing reference for OpenAI agent framework.",
        "score": 0.79,
        "required": False,
    },
    # ── External: Anthropic cookbook patterns (canonical pattern notebooks) ──
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/evaluator_optimizer.ipynb",
        "title": "Anthropic — Evaluator-Optimizer Pattern",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "safety_eval",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "anthropic_agent_patterns",
        "keep_reason": "Canonical Anthropic evaluator-optimizer pattern; best external source for eval-loop design.",
        "score": 0.80,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/orchestrator_workers.ipynb",
        "title": "Anthropic — Orchestrator-Workers Pattern",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "anthropic_agent_patterns",
        "keep_reason": "Canonical Anthropic orchestrator-workers pattern; deep architecture + impl_specificity.",
        "score": 0.79,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/basic_workflows.ipynb",
        "title": "Anthropic — Agent Basic Workflows",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "authority_level": 0.70,
        "canonical": True,
        "collapse_group": "anthropic_agent_patterns",
        "keep_reason": "Foundational Anthropic workflow patterns; broadens multi-provider coverage.",
        "score": 0.77,
        "required": False,
    },
    # ── External: MCP Python SDK (canonical FastMCP server authoring source) ──
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md",
        "title": "MCP Python SDK — FastMCP Server Authoring Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "tool_contracts",
        "authority_level": 0.90,
        "canonical": True,
        "collapse_group": "mcp_protocol_sdk",
        "keep_reason": "Only canonical external source for FastMCP server authoring pattern; directly fixes TOOL-01/TOOL-03/TOOL-05 retrieval failures.",
        "score": 0.87,
        "required": True,
    },
    # ── External: OpenAI Agents Python — supplementary docs not yet ingested ─
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/mcp.md",
        "title": "OpenAI Agents Python — MCP Integration Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "tool_contracts",
        "authority_level": 0.85,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "MCP client integration in agent SDK; covers tool contracts, server connections, MCP client pattern; fixes TOOL-01/03/04.",
        "score": 0.85,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/context.md",
        "title": "OpenAI Agents Python — Context Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "RunContext and dependency injection patterns; reduces MA-04 same-source redundancy and answers function-tool-vs-handoff queries.",
        "score": 0.81,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/results.md",
        "title": "OpenAI Agents Python — Results Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.80,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "RunResult, streaming, and tool call outputs; improves TOOL-04 and MA-05 parallel tool execution queries.",
        "score": 0.79,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/models.md",
        "title": "OpenAI Agents Python — Models Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "openai_agents_raw_github",
        "keep_reason": "Model selection and configuration; covers temperature/seed for determinism; marginal improvement on ARCH-04.",
        "score": 0.74,
        "required": False,
    },
    # ── External: Multi-agent framework diversity (reduces MA-01-05 redundancy) ──
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md",
        "title": "LangGraph — Multi-Agent Graph Orchestration",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "langgraph",
        "keep_reason": "Graph-based multi-agent orchestration framework; breaks MA-01-05 same-source redundancy by adding third framework family.",
        "score": 0.78,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/microsoft/autogen/main/README.md",
        "title": "AutoGen — Microsoft Multi-Agent Framework",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "authority_level": 0.75,
        "canonical": True,
        "collapse_group": "autogen",
        "keep_reason": "Fourth multi-agent framework reference; curated has zero AutoGen; adds MA source diversity beyond OpenAI+Anthropic.",
        "score": 0.75,
        "required": False,
    },
    {
        "source_type": "web",
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/subagent.ipynb",
        "title": "Anthropic — Sub-agent Delegation Pattern",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "authority_level": 0.70,
        "canonical": True,
        "collapse_group": "anthropic_agent_patterns",
        "keep_reason": "Sub-agent delegation patterns; complements orchestrator_workers.ipynb; helps MA-02 handoff queries. Conditional: skip silently if 404.",
        "score": 0.72,
        "required": False,
    },
]

# Collapsed / excluded sources (for dry-run report only — not ingested)
EXCLUDED_SOURCES: list[dict] = [
    {
        "path": "docs/reference/_archive/Agentic Process Mapping/agentic_process_mapping_v*.md",
        "reason": "version_churn — superseded by v29",
    },
    {
        "path": "docs/reference/agentic_process_mapping_non_technical.md",
        "reason": "lower_density — collapses to exec summary",
    },
    {
        "path": "https://openai.github.io/openai-agents-python/*",
        "reason": "mirror_collapse — HTML mirror of GitHub raw markdown",
    },
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/README.md",
        "reason": "shallow — README collapses to pattern notebooks",
    },
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/tool_use/customer_service_agent.ipynb",
        "reason": "tutorial_collapse — lower signal vs canonical patterns",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Source area mapping (doc_family → source_area for Phase-2 metadata compat)
# ─────────────────────────────────────────────────────────────────────────────
_SOURCE_AREA_MAP: dict[str, str] = {
    "adr": "arch",
    "architecture": "arch",
    "contract": "contract",
    "spec": "spec",
    "standard": "arch",
    "guide": "guide",
    "reference": "reference",
    "policy": "policy",
    "overview": "overview",
    "doc": "doc",
}


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class IngestionError(RuntimeError):
    """Raised on fail-closed conditions (required fetch failure, config error)."""


class MetadataValidationError(ValueError):
    """Raised when a chunk's metadata is missing required keys or has bad types."""


# ─────────────────────────────────────────────────────────────────────────────
# Dataclasses
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BucketStats:
    bucket: str
    source_count: int
    chunk_count: int


@dataclass
class DryRunReport:
    total_sources: int
    total_chunks: int
    required_ok: int
    required_fail: int
    optional_fail: int
    chunks_skipped_garbage: int
    dedup_collisions: int
    bucket_stats: list[BucketStats]
    excluded_count: int
    dedup_log: list[str]
    source_details: list[dict]


@dataclass
class IngestionReport:
    collection_name: str
    before_count: int
    after_count: int
    total_chunks: int
    elapsed_s: float
    bucket_stats: list[BucketStats]
    dedup_collisions: int


# ─────────────────────────────────────────────────────────────────────────────
# Utility functions  (inlined from Phase 2 for standalone operation)
# ─────────────────────────────────────────────────────────────────────────────


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_doc_id(id_parts: tuple[str, ...]) -> str:
    return hashlib.sha256(":".join(id_parts).encode("utf-8")).hexdigest()[:24]


def section_dedup_key(canonical_url: str, heading_path: str) -> str:
    """Stable hash key for canonical_url + section collision detection."""
    raw = f"{canonical_url.rstrip('/')}::{heading_path.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def chunk_by_headings(text: str) -> list[tuple[str, str]]:
    """Split markdown by H1-H3 headings; return list of (heading_path, chunk_text)."""
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    boundaries: list[tuple[int, int, str]] = []
    for m in heading_re.finditer(text):
        level = len(m.group(1))
        title = m.group(2).strip()
        boundaries.append((m.start(), level, title))
    boundaries.append((len(text), 0, ""))

    if len(boundaries) <= 1:
        chunks = chunk_text(text)
        return [("no-headings", c) for c in chunks]

    stack: list[str] = ["", "", ""]
    results: list[tuple[str, str]] = []

    for i, (pos, level, title) in enumerate(boundaries[:-1]):
        next_pos = boundaries[i + 1][0]
        stack[level - 1] = title
        for j in range(level, 3):
            stack[j] = ""
        heading_path = " > ".join(p for p in stack if p)
        section = text[pos:next_pos].strip()
        if len(section) < MIN_BODY_CHARS:
            continue
        for chunk_idx, chunk in enumerate(chunk_text(section)):
            results.append((heading_path, chunk))

    if not results:
        return [("no-headings", c) for c in chunk_text(text)]
    return results


def _extract_title(text: str, fallback: str = "") -> str:
    """Return first H1 title from markdown text, or fallback."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def ipynb_to_text(raw: str) -> str:
    """Extract concatenated cell source text from a Jupyter notebook JSON string."""
    try:
        nb = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw
    lines: list[str] = []
    for cell in nb.get("cells", []):
        source = cell.get("source", [])
        text = "".join(source) if isinstance(source, list) else str(source)
        if text.strip():
            lines.append(text.strip())
    return "\n\n".join(lines)


def html_to_text(html: str) -> str:
    """Lightweight HTML → plain text stripping."""
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<(br|p|div|h[1-6]|li|tr|td|th)[^>]*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    for ent, char in [
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&#39;", "'"),
        ("&nbsp;", " "),
    ]:
        html = html.replace(ent, char)
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r" {2,}", " ", html)
    return html.strip()


def is_garbage(text: str) -> bool:
    if not text or len(text.strip()) < MIN_BODY_CHARS:
        return True
    return "Loading..Loading.." in text or "Loading..." in text[:30]


def fetch_url(url: str) -> str | None:
    """Return raw response body or None on failure (never raises)."""
    try:
        import urllib.request

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; AgenticWorkflow/1.0; "
                "+https://github.com/Siamese001/Agentic-Workflow)"
            ),
            "Accept": "text/html,text/plain,*/*",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:  # noqa: S310
            raw = resp.read()
        charset = "utf-8"
        ct = resp.headers.get("Content-Type", "")
        if "charset=" in ct:
            charset = ct.split("charset=")[-1].strip().split(";")[0]
        return raw.decode(charset, errors="replace")
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"    FETCH ERROR {url}: {exc}", file=sys.stderr)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Metadata helpers
# ─────────────────────────────────────────────────────────────────────────────


def _source_area(doc_family: str) -> str:
    return _SOURCE_AREA_MAP.get(doc_family, "doc")


def _retrieval_weight(canonical: bool) -> float:
    return 1.0 if canonical else 0.4


def _derive_authority_tier(source_type: str, topic_bucket: str) -> str:
    """Derive authority_tier from source_type and topic_bucket."""
    if source_type == "local":
        return "T4_repo_canonical"
    return _TOPIC_BUCKET_TO_TIER.get(topic_bucket, _DEFAULT_AUTHORITY_TIER)


def _build_metadata(
    entry: dict,
    chunk_index: int,
    heading_path: str,
    canonical_digest: str,
    inferred_title: str,
    source_url: str,
) -> dict:
    doc_family = entry["doc_family"]
    canonical: bool = entry["canonical"]
    source_type: str = entry["source_type"]
    topic_bucket: str = entry["topic_bucket"]
    authority_tier = _derive_authority_tier(source_type, topic_bucket)
    normative_scope = "repo_internal" if source_type == "local" else "external_authority"
    return {
        "artifact_type": "curated_agent_doc",
        "doc_type": entry["doc_type"],
        "doc_family": doc_family,
        "file_path": source_url[:200],
        "layer": "ext" if source_type == "web" else "docs",
        "chunk_index": chunk_index,
        "canonical_digest": canonical_digest,
        "source": "curated_agent_docs",
        "title": inferred_title[:200],
        "heading_path": heading_path[:200],
        "authority_level": float(entry["authority_level"]),
        "canonical": canonical,
        "retrieval_weight": _retrieval_weight(canonical),
        "source_area": _source_area(doc_family),
        "topic_bucket": topic_bucket,
        "source_url": source_url[:200],
        "collapse_group": entry["collapse_group"],
        "source_collection": "curated_agent_docs",
        "authority_tier": authority_tier,
        "normative_scope": normative_scope,
        "invalid_for_normative_use": False,
    }


def validate_metadata(meta: dict) -> None:
    """Raise MetadataValidationError if required keys are missing or types are wrong."""
    missing = REQUIRED_METADATA_KEYS - set(meta.keys())
    if missing:
        raise MetadataValidationError(f"Missing metadata keys: {sorted(missing)}")
    if not isinstance(meta.get("authority_level"), float):
        raise MetadataValidationError(
            f"authority_level must be float, got {type(meta.get('authority_level'))}"
        )
    if not isinstance(meta.get("canonical"), bool):
        raise MetadataValidationError(f"canonical must be bool, got {type(meta.get('canonical'))}")
    if not isinstance(meta.get("chunk_index"), int):
        raise MetadataValidationError(f"chunk_index must be int, got {type(meta.get('chunk_index'))}")
    if not isinstance(meta.get("invalid_for_normative_use"), bool):
        raise MetadataValidationError(
            f"invalid_for_normative_use must be bool, got {type(meta.get('invalid_for_normative_use'))}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Source collection
# ─────────────────────────────────────────────────────────────────────────────


def collect_from_source(entry: dict, repo_root: Path) -> list[dict]:
    """Return list of chunk dicts for a single CURATED_SOURCES entry.

    Each dict has keys: ``text``, ``metadata``, ``id_parts``.
    Raises IngestionError if ``required=True`` and the source cannot be read.
    """
    source_url = entry["path"]
    doc_type = entry["doc_type"]
    required = entry["required"]
    inferred_title = entry["title"]

    if entry["source_type"] == "local":
        abs_path = repo_root / source_url
        try:
            body = abs_path.read_text(encoding="utf-8")
        except OSError as exc:
            msg = f"Cannot read local source {source_url}: {exc}"
            if required:
                raise IngestionError(msg) from exc
            print(f"    SKIP (optional, read error): {msg}", file=sys.stderr)
            return []
        domain = "local"
    else:
        raw = fetch_url(source_url)
        if raw is None:
            msg = f"Fetch failed for {source_url}"
            if required:
                raise IngestionError(msg)
            print(f"    SKIP (optional, fetch failed): {msg}", file=sys.stderr)
            return []
        if doc_type == "notebook":
            body = ipynb_to_text(raw)
        elif source_url.endswith(".md") or source_url.endswith(".txt"):
            body = raw  # already plain text
        else:
            body = html_to_text(raw)
        domain = entry.get("collapse_group", "ext")

    if is_garbage(body):
        msg = f"Body too short / garbage ({len(body.strip())} chars): {source_url}"
        if required:
            raise IngestionError(msg)
        print(f"    SKIP (garbage): {source_url}", file=sys.stderr)
        return []

    # Extract title from H1 if markdown
    if doc_type == "markdown":
        inferred_title = _extract_title(body, fallback=entry["title"])

    content_hash = compute_digest(body)

    # Choose chunking strategy
    if doc_type == "markdown":
        raw_chunks = chunk_by_headings(body)  # list of (heading_path, text)
    else:
        raw_chunks = [("no-headings", c) for c in chunk_text(body)]

    result: list[dict] = []
    for chunk_idx, (heading_path, chunk_text_content) in enumerate(raw_chunks):
        meta = _build_metadata(
            entry=entry,
            chunk_index=chunk_idx,
            heading_path=heading_path,
            canonical_digest=content_hash,
            inferred_title=inferred_title,
            source_url=source_url,
        )
        validate_metadata(meta)
        id_parts = (
            entry["source_type"],
            domain,
            content_hash,
            hashlib.sha256(heading_path.encode()).hexdigest()[:8],
            str(chunk_idx),
        )
        result.append({"text": chunk_text_content, "metadata": meta, "id_parts": id_parts})

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Startup validation
# ─────────────────────────────────────────────────────────────────────────────


def _validate_sources_unique() -> None:
    """Raise IngestionError if CURATED_SOURCES contains duplicate path values."""
    seen: dict[str, int] = {}
    for i, entry in enumerate(CURATED_SOURCES):
        p = entry["path"]
        if p in seen:
            raise IngestionError(f"Duplicate path in CURATED_SOURCES at indices {seen[p]} and {i}: {p}")
        seen[p] = i


# Run at import time to catch config errors early
_validate_sources_unique()


# ─────────────────────────────────────────────────────────────────────────────
# Report building
# ─────────────────────────────────────────────────────────────────────────────


def _compute_bucket_stats(all_docs: list[dict]) -> list[BucketStats]:
    bucket_chunks: dict[str, int] = {}
    bucket_sources: dict[str, set[str]] = {}
    for doc in all_docs:
        tb = doc["metadata"]["topic_bucket"]
        su = doc["metadata"]["source_url"]
        bucket_chunks[tb] = bucket_chunks.get(tb, 0) + 1
        bucket_sources.setdefault(tb, set()).add(su)
    return [
        BucketStats(bucket=b, source_count=len(bucket_sources[b]), chunk_count=bucket_chunks[b])
        for b in sorted(bucket_chunks)
    ]


def print_dry_run_report(report: DryRunReport) -> None:
    print("\n" + "=" * 80)
    print("DRY-RUN REPORT — curated_agent_docs")
    print("=" * 80)
    print(f"  Sources evaluated : {report.total_sources}  (excluded: {report.excluded_count})")
    print(f"  Total chunks      : {report.total_chunks}")
    print(f"  Required OK/FAIL  : {report.required_ok}/{report.required_fail}")
    print(f"  Optional FAIL     : {report.optional_fail}")
    print(f"  Garbage skipped   : {report.chunks_skipped_garbage}")
    print(f"  Dedup collisions  : {report.dedup_collisions}")
    print()
    print("  Source distribution by topic bucket:")
    for bs in report.bucket_stats:
        print(f"    {bs.bucket:<20}  {bs.source_count:>2} sources  {bs.chunk_count:>4} chunks")
    print()
    print("  Source details (path → chunks):")
    for sd in report.source_details:
        status = "OK" if sd["chunks"] > 0 else f"FAIL({'required' if sd['required'] else 'optional'})"
        print(f"    [{status}] {sd['score']:.2f}  {sd['path'][:70]:<70}  {sd['chunks']:>4} chunks")
    if report.dedup_log:
        print()
        print("  Dedup collisions:")
        for line in report.dedup_log[:10]:
            print(f"    {line}")
    print()
    print("  Excluded (collapsed) sources:")
    for ex in EXCLUDED_SOURCES:
        print(f"    EXCLUDE  {ex['path'][:65]:<65}  reason={ex['reason']}")
    print("=" * 80)
    if report.required_fail > 0:
        print(f"\nERROR: {report.required_fail} required source(s) failed — would abort live run.")
    else:
        print("\nDRY-RUN PASS — all required sources available.")


# ─────────────────────────────────────────────────────────────────────────────
# Main run
# ─────────────────────────────────────────────────────────────────────────────


def run(store_path: Path, dry_run: bool = False) -> DryRunReport | IngestionReport:
    sys.path.insert(0, str(REPO_ROOT))
    from tqdm import tqdm

    all_docs: list[dict] = []
    seen_section_keys: set[str] = set()
    dedup_log: list[str] = []
    fetch_stats: dict[str, int] = {"required_ok": 0, "required_fail": 0, "optional_fail": 0, "garbage": 0}
    source_details: list[dict] = []

    print(f"\nCollecting from {len(CURATED_SOURCES)} curated sources ...")

    for entry in tqdm(CURATED_SOURCES, desc="Collecting", unit="source"):
        path = entry["path"]
        required = entry["required"]
        print(f"  -> [{entry['topic_bucket']}] {path[:72]}")

        try:
            chunks = collect_from_source(entry, REPO_ROOT)
        except IngestionError as exc:
            if required:
                fetch_stats["required_fail"] += 1
                source_details.append(
                    {"path": path, "score": entry["score"], "chunks": 0, "required": required}
                )
                if not dry_run:
                    raise
                print(f"    REQUIRED FAIL: {exc}", file=sys.stderr)
                continue
            fetch_stats["optional_fail"] += 1
            source_details.append({"path": path, "score": entry["score"], "chunks": 0, "required": required})
            continue

        if not chunks and required:
            msg = f"Required source produced 0 chunks: {path}"
            fetch_stats["required_fail"] += 1
            source_details.append({"path": path, "score": entry["score"], "chunks": 0, "required": required})
            if not dry_run:
                raise IngestionError(msg)
            print(f"    REQUIRED FAIL: {msg}", file=sys.stderr)
            continue

        if not chunks:
            fetch_stats["optional_fail"] += 1
            source_details.append({"path": path, "score": entry["score"], "chunks": 0, "required": required})
            continue

        if required:
            fetch_stats["required_ok"] += 1

        dedup_before = len(all_docs)
        for doc in chunks:
            # Include chunk_index so multi-chunk sections aren't false-positive collapsed.
            # Real collisions are duplicate CURATED_SOURCES entries for the same url+section+idx.
            sk = (
                section_dedup_key(doc["metadata"]["source_url"], doc["metadata"]["heading_path"])
                + f"::{doc['metadata']['chunk_index']}"
            )
            if sk in seen_section_keys:
                dedup_log.append(
                    f"SECTION_DEDUP: {doc['metadata']['source_url'][:50]} :: {doc['metadata']['heading_path'][:30]}"
                )
                continue
            seen_section_keys.add(sk)
            all_docs.append(doc)

        added = len(all_docs) - dedup_before
        source_details.append({"path": path, "score": entry["score"], "chunks": added, "required": required})
        print(f"     OK: {added} chunks")

    bucket_stats = _compute_bucket_stats(all_docs)

    if dry_run:
        report = DryRunReport(
            total_sources=len(CURATED_SOURCES),
            total_chunks=len(all_docs),
            required_ok=fetch_stats["required_ok"],
            required_fail=fetch_stats["required_fail"],
            optional_fail=fetch_stats["optional_fail"],
            chunks_skipped_garbage=fetch_stats["garbage"],
            dedup_collisions=len(dedup_log),
            bucket_stats=bucket_stats,
            excluded_count=len(EXCLUDED_SOURCES),
            dedup_log=dedup_log,
            source_details=source_details,
        )
        print_dry_run_report(report)
        return report

    if fetch_stats["required_fail"] > 0:
        raise IngestionError(f"{fetch_stats['required_fail']} required source(s) failed — aborting.")

    if not all_docs:
        raise IngestionError("No documents collected — aborting.")

    # Embed + upsert
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb
    except ImportError as exc:
        raise SystemExit(f"Missing dependency: {exc}") from exc

    import torch

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nLoading embedding model: {EMBEDDING_MODEL} (device={_device}) ...")
    model = SentenceTransformer(EMBEDDING_MODEL, device=_device)
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise IngestionError(f"Model dim mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model ready. dim={actual_dim}")

    from tools.progress_display import ProgressReporter

    # ID dedup (last-wins for same ID)
    ids = [make_doc_id(tuple(d["id_parts"])) for d in all_docs]
    texts = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]
    seen_ids: dict[str, int] = {doc_id: i for i, doc_id in enumerate(ids)}
    keep = sorted(seen_ids.values())
    ids = [ids[i] for i in keep]
    texts = [texts[i] for i in keep]
    metadatas = [metadatas[i] for i in keep]
    print(f"After ID dedup: {len(ids)} unique chunks")

    client = chromadb.PersistentClient(path=str(store_path))
    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        before_count = collection.count()
        print(f"Collection '{COLLECTION_NAME}' exists ({before_count:,} docs) — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
            },
        )
        before_count = 0
        print(f"Created collection '{COLLECTION_NAME}'")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting curated_agent_docs")
    t0 = time.time()

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_embs = model.encode(
            texts[batch_start:batch_end],
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        ).tolist()
        batch_embs = [[float(x) for x in emb] for emb in batch_embs]
        for emb in batch_embs:
            if len(emb) != EMBEDDING_DIM:
                raise IngestionError(f"Embedding dim {len(emb)} != {EMBEDDING_DIM}")
        collection.upsert(
            ids=ids[batch_start:batch_end],
            embeddings=batch_embs,
            documents=texts[batch_start:batch_end],
            metadatas=metadatas[batch_start:batch_end],
        )
        reporter.update(batch_end - batch_start, label=f"batch {batch_end}/{total}")

    reporter.done()
    elapsed = time.time() - t0
    after_count = collection.count()

    ingestion_report = IngestionReport(
        collection_name=COLLECTION_NAME,
        before_count=before_count,
        after_count=after_count,
        total_chunks=total,
        elapsed_s=elapsed,
        bucket_stats=bucket_stats,
        dedup_collisions=len(dedup_log),
    )
    print(f"\nDone. collection='{COLLECTION_NAME}'")
    print(f"  Before : {before_count:,} docs")
    print(f"  After  : {after_count:,} docs  (+{after_count - before_count:,})")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\nSource distribution by bucket:")
    for bs in ingestion_report.bucket_stats:
        print(f"  {bs.bucket:<20}  {bs.source_count:>2} sources  {bs.chunk_count:>4} chunks")
    return ingestion_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest curated agent-best-practice docs into curated_agent_docs"
    )
    parser.add_argument(
        "--store-path",
        type=Path,
        default=CANONICAL_STORE,
        help=f"ChromaDB persistence directory (default: {CANONICAL_STORE})",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Collect + report only; do not write to Chroma"
    )
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
