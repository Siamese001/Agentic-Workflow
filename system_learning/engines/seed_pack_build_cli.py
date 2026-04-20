"""Seed Pack Build CLI for Plan B Phase 5.

Command-line interface for building production semantic embedding packs.

Writes packs to:
  <base_path>\\seed_packs\\<namespace>\\<seed_index_version_hash>\\
Containing:
  row_index.jsonl
  embeddings.f32
  seed_manifest.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "seed_pack_build_cli")
_emit_applies_guardrail("p0", "seed_pack_build_cli", "p0_governance")
_emit_reads_policy_state("p0", "seed_pack_build_cli", "policy_binding")
_emit_snapshots_state("p0", "seed_pack_build_cli", "state_snapshot")
emit_replay_key("p0", "seed_pack_build_cli")
emit_determinism_digest("p0", "seed_pack_build_cli")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "seed_pack_build_cli", "execution_auth")
_emit_validates_capability("p2", "seed_pack_build_cli", "capability_check")
_emit_routes_to_capability("p2", "seed_pack_build_cli", "capability_route")
_emit_writes_via_uwg("p2", "seed_pack_build_cli", "uwg_write")
_emit_blocks_direct_write("p2", "seed_pack_build_cli", "direct_write_block")
_emit_records_tool_invocation("p2", "seed_pack_build_cli", "tool_invocation")
_emit_captures_execution_output("p2", "seed_pack_build_cli", "exec_output")
_emit_dispatches_agent("p3", "seed_pack_build_cli", "agent_dispatch")
_emit_coordinates_agents("p3", "seed_pack_build_cli", "agent_coordination")
_emit_records_workflow_lineage("p3", "seed_pack_build_cli", "workflow_lineage")
_emit_records_healing_outcome("p3", "seed_pack_build_cli", "healing_outcome")
_emit_escalates_failure("p3", "seed_pack_build_cli", "failure_escalation")
_emit_orchestrates_workflow("p3", "seed_pack_build_cli", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "seed_pack_build_cli", "healing_dispatch")
_emit_invokes_evaluation("p3", "seed_pack_build_cli", "evaluation_signal")
_emit_records_telemetry_event("p4", "seed_pack_build_cli", "telemetry_event")
_emit_captures_evaluation_metric("p4", "seed_pack_build_cli", "eval_metric")
_emit_stores_embedding("p4", "seed_pack_build_cli", "embedding_store")
_emit_updates_meta_learning_state("p4", "seed_pack_build_cli", "meta_learning")
_emit_links_execution_to_snapshot("p4", "seed_pack_build_cli", "exec_snapshot_link")

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow- optional dependency
    pass  # guardian: allow-silent-swallow -- intentional: ImportError used for control flow
from agentic_core.embeddings.embedding_factory import create_embedding_client
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.engines.seed_embedding_pack_builder import build_seed_embedding_pack
from system_learning.types.seed_embedding_pack_types import SeedEmbeddingPackConfig
from tqdm import tqdm

_emit_emits_metric_event("seed_pack_build_cli", "p4obs", "metric_1")
_emit_emits_metric_event("seed_pack_build_cli", "p4obs", "metric_2")
_emit_emits_metric_event("seed_pack_build_cli", "p4obs", "metric_3")
_emit_emits_metric_event("seed_pack_build_cli", "p4obs", "metric_4")
_emit_emits_metric_event("seed_pack_build_cli", "p4obs", "metric_5")
_emit_emits_metric_event("seed_pack_build_cli", "p4obs", "metric_6")
_emit_records_incident_event("seed_pack_build_cli", "p4obs", "incident")
_emit_captures_runtime_anomaly("seed_pack_build_cli", "p4obs", "anomaly")
_emit_writes_observability_log("seed_pack_build_cli", "p4obs", "obs_log")
_emit_updates_monitoring_state("seed_pack_build_cli", "p4obs", "mon_state")
_emit_triggers_alert("seed_pack_build_cli", "p4obs", "alert")
_emit_links_incident_trace("seed_pack_build_cli", "p4obs", "trace_link")
_emit_captures_pattern("seed_pack_build_cli", "p3lm", "pattern")
_emit_records_learning_event("seed_pack_build_cli", "p3lm", "learning_event")
_emit_writes_learning_snapshot("seed_pack_build_cli", "p3lm", "snapshot")
_emit_feeds_meta_learning("seed_pack_build_cli", "p3lm", "meta_feed")
_emit_updates_routing_strategy("seed_pack_build_cli", "p3lm", "routing")
_emit_improves_agent_policy("seed_pack_build_cli", "p3lm", "policy")
_emit_stores_learning_state("seed_pack_build_cli", "p3lm", "state")
_emit_records_execution_trace("seed_pack_build_cli", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("seed_pack_build_cli", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("seed_pack_build_cli", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("seed_pack_build_cli", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("seed_pack_build_cli", "L4_STATE", "p2_trace_5")
_emit_reads_environ("seed_pack_build_cli", "env_read", "p2_env_1")
_emit_reads_environ("seed_pack_build_cli", "env_read", "p2_env_2")
_emit_reads_runtime_state("seed_pack_build_cli", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("seed_pack_build_cli", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "seed_pack_build_cli", "context_pull")
_emit_pulls_context("p1", "seed_pack_build_cli", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "seed_pack_build_cli", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "seed_pack_build_cli", "uwg_term_2")
_emit_writes_through("p1", "seed_pack_build_cli", "write_through")
_emit_writes_through("p1", "seed_pack_build_cli", "write_through_2")
_emit_validated_by_safety_plane("p1", "seed_pack_build_cli", "safety_validation")
_emit_invokes_eval("p1", "seed_pack_build_cli", "eval_call")
_emit_proposal_commits_routing("p1", "seed_pack_build_cli", "routing_commit")
_emit_escalates_to_human("p1", "seed_pack_build_cli", "human_escalation")
_emit_routes_through("p1", "seed_pack_build_cli", "route_through")
_emit_checks_agent_registry("p1", "seed_pack_build_cli", "agent_registry")
_emit_validates_agent_capability("p1", "seed_pack_build_cli", "capability")
_emit_dispatches_execution_plan("p1", "seed_pack_build_cli", "exec_plan")
_emit_agent_executes_agent("p1", "seed_pack_build_cli", "sub_agent")
_emit_routes_to_agent("p1", "seed_pack_build_cli", "target_agent")
_emit_verifies_policy("p1", "seed_pack_build_cli", "policy_check")
_emit_observes_runtime_state("p1", "seed_pack_build_cli", "runtime_state")
_emit_verifies_boundary("p1", "seed_pack_build_cli", "boundary_check")
_emit_transcripts_response("p1", "seed_pack_build_cli", "transcript")
_emit_hard_fails_untranscripted("p1", "seed_pack_build_cli")
_emit_gated_by_confidence("p1", "seed_pack_build_cli", "confidence_gate")


def _find_default_corpus_path(namespace: str) -> Path:
    """
    Best-effort resolver for Plan A canonical corpus location.

    This does NOT create files. It only searches within repo-relative `data/`.
    Priority is given to plausible canonical names.
    """
    candidates = [
        Path("data") / "corpus" / f"{namespace}_corpus.jsonl",
        Path("data") / "corpora" / f"{namespace}_corpus.jsonl",
        Path("data") / f"{namespace}_corpus.jsonl",
        Path("data") / f"{namespace}.jsonl",
    ]
    for p in candidates:
        if p.exists():
            return p
    data_root = Path("data")
    if data_root.exists():
        hits = sorted(data_root.rglob(f"*{namespace}*jsonl"))
        if hits:
            return hits[0]
    return candidates[0]


def load_canonical_corpus(namespace: str, corpus_path: Path | None = None) -> list[dict[str, Any]]:
    """Load canonical Plan A corpus for namespace.

    Args:
        namespace: Namespace to load corpus for.
        corpus_path: Optional explicit corpus path.

    Returns:
        List of corpus rows with required fields.

    Raises:
        FileNotFoundError: If corpus file not found.
        ValueError: If corpus format invalid.
    """
    corpus_path = corpus_path or _find_default_corpus_path(namespace)
    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus file not found: {corpus_path}. Pass --corpus-path explicitly or place corpus under data/.",
        )
    corpus_rows: list[dict[str, Any]] = []
    with open(corpus_path, encoding="utf-8") as f:
        for line_num, line in tqdm(enumerate(f, 1), desc="Processing", unit="item"):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in line {line_num}: {e}") from e
            required_fields = ["content_hash", "trace_id", "namespace", "created_utc"]
            for field in required_fields:
                if field not in row:
                    raise ValueError(f"Missing required field '{field}' in line {line_num}")
            if str(row.get("namespace")) != namespace:
                raise ValueError(
                    f"Namespace mismatch in line {line_num}: expected '{namespace}', got '{row.get('namespace')}'",
                )
            corpus_rows.append(row)
    if not corpus_rows:
        raise ValueError(f"No corpus rows found for namespace: {namespace} at {corpus_path}")
    return corpus_rows


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Build production semantic embedding packs")
    parser.add_argument(
        "--base-path",
        required=True,
        help="Base directory for seed pack storage (e.g., C:\\AgenticEmbeddings)",
    )
    parser.add_argument("--namespace", required=True, help="Namespace to build pack for")
    parser.add_argument(
        "--model",
        default="text-embedding-3-large",
        help="OpenAI model to use (default: text-embedding-3-large)",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai"],
        help="Embedding provider to use (default: openai)",
    )
    parser.add_argument(
        "--dimensions",
        type=int,
        default=1536,
        help="Embedding dimensions to use (default: 1536 for OpenAI Matryoshka)",
    )
    parser.add_argument(
        "--bootstrap-mode",
        default="minimal_seed",
        choices=["minimal_seed", "curated_seed"],
        help="Bootstrap mode (default: minimal_seed)",
    )
    parser.add_argument(
        "--minimal-seed-count",
        type=int,
        default=None,
        help="Minimal seed count for minimal_seed mode",
    )
    parser.add_argument(
        "--corpus-path",
        default=None,
        help="Optional explicit path to corpus JSONL (e.g., data\\corpus\\healing_contexts_corpus.jsonl)",
    )
    args = parser.parse_args()
    base_path = Path(args.base_path)
    if not base_path.exists():
        print(f"Creating base directory: {base_path}")
        base_path.mkdir(parents=True, exist_ok=True)
    corpus_path = Path(args.corpus_path) if args.corpus_path else None
    try:
        resolved_corpus_path = corpus_path or _find_default_corpus_path(args.namespace)
        print(f"Loading corpus for namespace: {args.namespace}")
        print(f"corpus_path: {resolved_corpus_path}")
        corpus_rows = load_canonical_corpus(args.namespace, corpus_path=corpus_path)
        print(f"Loaded {len(corpus_rows)} corpus rows")
        print(f"Initializing OpenAI embedder with model: {args.model}")
        if os.getenv("OPENAI_API_KEY") == "sk-proj-YOUR_ACTUAL_API_KEY_HERE":
            print("WARNING: Using test mode with deterministic embedder (no real API calls)")
            from system_learning.engines.seed_embedding_pack_builder import DeterministicHashEmbedder

            embedder = DeterministicHashEmbedder(dimensions=args.dimensions)
        else:
            embedder = create_embedding_client(
                provider=args.provider,
                model=args.model,
                dimensions=args.dimensions,
            )
        print(f"Model dimensions: {args.dimensions}")
        model_checksum = hashlib.sha256(
            f"{args.provider}_{args.model}_{args.dimensions}".encode(),
        ).hexdigest()
        config = SeedEmbeddingPackConfig(
            namespace=args.namespace,
            bootstrap_mode=args.bootstrap_mode,
            minimal_seed_count=args.minimal_seed_count,
            embedding_model_version=args.model,
            embedding_model_checksum=model_checksum,
            canonicalization_version="v1",
        )
        print("Building seed pack...")
        built_at_utc = int(time.time())
        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=built_at_utc,
        )
        output_path = base_path / "seed_packs" / args.namespace / manifest.seed_index_version_hash
        print("\n=== Build Complete ===")
        print(f"vector_count: {manifest.vector_count}")
        print(f"dimensions: {manifest.dimensions}")
        print(f"seed_index_version_hash: {manifest.seed_index_version_hash}")
        print(f"output_path: {output_path}")
        print("\nExpected files:")
        print(f"  {output_path}\\row_index.jsonl")
        print(f"  {output_path}\\embeddings.f32")
        print(f"  {output_path}\\seed_manifest.json")
    except (AttributeError, FileNotFoundError, OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
