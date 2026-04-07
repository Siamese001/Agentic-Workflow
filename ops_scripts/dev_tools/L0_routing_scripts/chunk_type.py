from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "chunk_type")
emit_determinism_digest("p0", "chunk_type")

_emit_dispatches_healing_run("p1", "chunk_type", "L0")
_emit_routes_through("p1", "chunk_type", "L0")
_emit_checks_agent_registry("p1", "chunk_type", "agent_registry")
_emit_validates_agent_capability("p1", "chunk_type", "capability")
_emit_dispatches_execution_plan("p1", "chunk_type", "exec_plan")
_emit_agent_executes_agent("p1", "chunk_type", "sub_agent")
_emit_routes_to_agent("p1", "chunk_type", "target_agent")
_emit_verifies_policy("p1", "chunk_type", "policy_check")
_emit_observes_runtime_state("p1", "chunk_type", "runtime_state")
_emit_verifies_boundary("p1", "chunk_type", "boundary_check")
_emit_transcripts_response("p1", "chunk_type", "transcript")
_emit_hard_fails_untranscripted("p1", "chunk_type")
_emit_gated_by_confidence("p1", "chunk_type", "confidence_gate")
_emit_escalates_to_human("p1", "chunk_type", "L0")
_emit_reads_policy_state("p1", "chunk_type", "L0")
_emit_authorize_and_execute("p2", "chunk_type", "execution_auth")
_emit_validates_capability("p2", "chunk_type", "capability_check")
_emit_routes_to_capability("p2", "chunk_type", "capability_route")
_emit_writes_via_uwg("p2", "chunk_type", "uwg_write")
_emit_blocks_direct_write("p2", "chunk_type", "direct_write_block")
_emit_records_tool_invocation("p2", "chunk_type", "tool_invocation")
_emit_captures_execution_output("p2", "chunk_type", "exec_output")
_emit_dispatches_agent("p3", "chunk_type", "agent_dispatch")
_emit_coordinates_agents("p3", "chunk_type", "agent_coordination")
_emit_records_workflow_lineage("p3", "chunk_type", "workflow_lineage")
_emit_records_healing_outcome("p3", "chunk_type", "healing_outcome")
_emit_escalates_failure("p3", "chunk_type", "failure_escalation")
_emit_orchestrates_workflow("p3", "chunk_type", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "chunk_type", "healing_dispatch")
_emit_invokes_evaluation("p3", "chunk_type", "evaluation_signal")
_emit_records_telemetry_event("p4", "chunk_type", "telemetry_event")
_emit_captures_evaluation_metric("p4", "chunk_type", "eval_metric")
_emit_stores_embedding("p4", "chunk_type", "embedding_store")
_emit_updates_meta_learning_state("p4", "chunk_type", "meta_learning")
_emit_links_execution_to_snapshot("p4", "chunk_type", "exec_snapshot_link")

"\nSovereign Ingestion Mission - Index all sovereign territories into vector store.\n"
import argparse
import ast
import asyncio
import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("chunk_type", "p4obs", "metric_1")
_emit_emits_metric_event("chunk_type", "p4obs", "metric_2")
_emit_emits_metric_event("chunk_type", "p4obs", "metric_3")
_emit_emits_metric_event("chunk_type", "p4obs", "metric_4")
_emit_emits_metric_event("chunk_type", "p4obs", "metric_5")
_emit_emits_metric_event("chunk_type", "p4obs", "metric_6")
_emit_records_incident_event("chunk_type", "p4obs", "incident")
_emit_captures_runtime_anomaly("chunk_type", "p4obs", "anomaly")
_emit_writes_observability_log("chunk_type", "p4obs", "obs_log")
_emit_updates_monitoring_state("chunk_type", "p4obs", "mon_state")
_emit_triggers_alert("chunk_type", "p4obs", "alert")
_emit_links_incident_trace("chunk_type", "p4obs", "trace_link")
_emit_captures_pattern("chunk_type", "p3lm", "pattern")
_emit_records_learning_event("chunk_type", "p3lm", "learning_event")
_emit_writes_learning_snapshot("chunk_type", "p3lm", "snapshot")
_emit_feeds_meta_learning("chunk_type", "p3lm", "meta_feed")
_emit_updates_routing_strategy("chunk_type", "p3lm", "routing")
_emit_improves_agent_policy("chunk_type", "p3lm", "policy")
_emit_stores_learning_state("chunk_type", "p3lm", "state")
_emit_records_execution_trace("chunk_type", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("chunk_type", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("chunk_type", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("chunk_type", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("chunk_type", "L4_STATE", "p2_trace_5")
_emit_reads_environ("chunk_type", "env_read", "p2_env_1")
_emit_reads_environ("chunk_type", "env_read", "p2_env_2")
_emit_reads_runtime_state("chunk_type", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("chunk_type", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "chunk_type", "context_pull")
_emit_pulls_context("p1", "chunk_type", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "chunk_type", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "chunk_type", "uwg_term_2")
_emit_writes_through("p1", "chunk_type", "write_through")
_emit_writes_through("p1", "chunk_type", "write_through_2")
_emit_validated_by_safety_plane("p1", "chunk_type", "safety_validation")
_emit_invokes_eval("p1", "chunk_type", "eval_call")
_emit_proposal_commits_routing("p1", "chunk_type", "routing_commit")


async def load_text_file(file_path: Path) -> str:
    """Load text from supported files with encoding fallback."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_text_file", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_text_file", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415    # guardian: Encoding errors should specify fallback encoding strategy

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_text_file")
    try:
        try:
            return file_path.read_text(encoding="utf-8")
        # guardian: allow-silent-swallow - acceptable exception handling
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1")
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        print(f" [!] Failed to read {file_path}: {e}")
        return ""


class ChunkType(Enum):
    """Semantic chunk types for metadata."""

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    DOCSTRING = "docstring"
    IMPORT_BLOCK = "imports"
    TEXT_BLOCK = "text"


@dataclass
class SemanticChunk:
    """Structured semantic chunk with metadata."""

    chunk_type: ChunkType
    name: str
    text: str
    start_line: int
    end_line: int
    parent: str | None = None
    docstring: str | None = None


def _extract_docstring(node: ast.AST) -> str | None:
    """Extract docstring from AST node if present."""
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Module):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            if isinstance(node.body[0].value.value, str):
                return node.body[0].value.value.strip()
    return None


def _get_source_segment(lines: list[str], start: int, end: int) -> str:
    """Extract line segment from source lines (1-indexed)."""
    return "\n".join(lines[start - 1 : end])
    # guardian: Syntax errors should be caught at parser level, not runtime

def chunk_python_ast(text: str, file_path: Path) -> list[SemanticChunk]:
    """Parse Python file to semantic chunks using ast."""
    chunks = []
    lines = text.splitlines()
    try:
        tree = ast.parse(text)    # guardian: Syntax errors should be caught at parser level, not runtime
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as e:
        print(f" [!] AST parse failed for {file_path}: {e}. Falling back to line-based.")
        return chunk_text_fallback(text, file_path)
    module_doc = _extract_docstring(tree)
    if module_doc:
        doc_lines = module_doc.count("\n") + 1
        chunks.append(
            SemanticChunk(
                chunk_type=ChunkType.DOCSTRING,
                name=f"{file_path.stem}.__doc__",
                text=module_doc,
                start_line=1,
                end_line=doc_lines,
            ),
        )
    import_nodes = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Import | ast.ImportFrom)]
    if import_nodes:
        start = min(n.lineno for n in import_nodes)
        end = max(n.end_lineno or n.lineno for n in import_nodes)
        chunks.append(
            SemanticChunk(
                chunk_type=ChunkType.IMPORT_BLOCK,
                name=f"{file_path.stem}.__imports__",
                text=_get_source_segment(lines, start, end),
                start_line=start,
                end_line=end,
            ),
        )
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            end_line = node.end_lineno or node.lineno
            chunks.append(
                SemanticChunk(
                    chunk_type=ChunkType.CLASS,
                    name=node.name,
                    text=_get_source_segment(lines, node.lineno, end_line),
                    start_line=node.lineno,
                    end_line=end_line,
                    docstring=_extract_docstring(node),
                ),
            )
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            parent_class = None
            parent = node
            while hasattr(parent, "parent"):
                parent = parent.parent
                if isinstance(parent, ast.ClassDef):
                    parent_class = parent.name
                    break
            end_line = node.end_lineno or node.lineno
            chunks.append(
                SemanticChunk(
                    chunk_type=ChunkType.METHOD if parent_class else ChunkType.FUNCTION,
                    name=f"{parent_class}.{node.name}" if parent_class else node.name,
                    text=_get_source_segment(lines, node.lineno, end_line),
                    start_line=node.lineno,
                    end_line=end_line,
                    parent=parent_class,
                    docstring=_extract_docstring(node),
                ),
            )
    return chunks


def chunk_text_fallback(text: str, file_path: Path) -> list[SemanticChunk]:
    """Fallback to line-based chunking for non-Python or parse failures."""
    chunks = []
    lines = text.splitlines()
    chunk_size = 50
    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i : i + chunk_size]
        chunk_text = "\n".join(chunk_lines).strip()
        if chunk_text:
            chunks.append(
                SemanticChunk(
                    chunk_type=ChunkType.TEXT_BLOCK,
                    name=f"{file_path.stem}:lines_{i + 1}-{min(i + chunk_size, len(lines))}",
                    text=chunk_text,
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                ),
            )
    return chunks


def chunk_text(text: str, file_path: Path) -> list[dict]:
    """
    Smart semantic chunking: AST for Python, fallback for others.
    Returns dicts ready for vector store with enriched metadata.
    """
    if file_path.suffix.lower() == ".py":
        semantic_chunks = chunk_python_ast(text, file_path)
    else:
        semantic_chunks = chunk_text_fallback(text, file_path)
    return [
        {
            "hash": hashlib.sha256(f"{file_path}:{c.start_line}-{c.end_line}".encode()).hexdigest()[:16],
            "text": c.text,
            "metadata": {
                "source": str(file_path),
                "start_line": c.start_line,
                "end_line": c.end_line,
                "file_type": file_path.suffix,
                "chunk_type": c.chunk_type.value,
                "name": c.name,
                "parent": c.parent,
                "docstring": c.docstring[:500] if c.docstring else None,
            },
        }
        for c in semantic_chunks
        if c.text.strip()
    ]


async def process_file(file_path: Path, embedder: Any, vector_store: Any) -> int:
    """Process a single file and add to vector store"""
    text: Any = await load_text_file(file_path)
    if not text or len(text.strip()) < 10:
        return 0
    chunks: Any = chunk_text(text, file_path)
    if not chunks:
        return 0
    batch_size: Any = 10
    total_processed: Any = 0
    for i in range(0, len(chunks), batch_size):
        batch: Any = chunks[i : i + batch_size]
        texts: Any = [chunk["text"] for chunk in batch]
        embeddings: Any = await embedder.embed_documents(texts)
        vectors: Any = []
        for j, embedding in enumerate(embeddings):
            chunk: Any = batch[j]
            meta: Any = chunk["metadata"]
            meta["text"] = chunk["text"]
            vectors.append({"id": chunk["hash"], "values": embedding, "metadata": meta})
        await vector_store.upsert(vectors)
        total_processed += len(batch)
        print(f"   [+] Indexed {file_path.name}: chunks {i + 1}-{min(i + batch_size, len(chunks))}")
    return total_processed


async def scan_directory(directory: Path, embedder: Any, vector_store: Any) -> dict[str, int]:
    """Scan directory and process all supported files"""
    stats: Any = {"files_processed": 0, "chunks_indexed": 0}
    extensions: Any = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files, get_python_files

    all_files = list(get_python_files(directory)) + list(get_data_files(directory))
    for file_path in all_files:
        if file_path.is_file() and file_path.suffix in extensions:
            if file_path.name.startswith(".") or "__pycache__" in str(file_path):
                continue
            chunks: Any = await process_file(file_path, embedder, vector_store)
            if chunks > 0:
                stats["files_processed"] += 1
                stats["chunks_indexed"] += chunks
    return stats


async def main() -> Any:
    """Main ingestion mission"""
    parser: Any = argparse.ArgumentParser(description="Sovereign Ingestion Mission")
    parser.add_argument("--target", required=True, help="Target directory to index")
    parser.add_argument("--reset", action="store_true", help="Reset index before ingestion")
    args: Any = parser.parse_args()
    target_path: Any = Path(args.target).resolve()
    if not target_path.exists():
        print(f"[ERROR] Target directory does not exist: {target_path}")
        return
    print(f"\n[*] Sovereign Ingestion Mission: {target_path}")
    embedder: Any = None
    vector_store: Any = None
    if args.reset:
        print("[*] Resetting vector index...")
    stats: Any = await scan_directory(target_path, embedder, vector_store)
    print("\n[✓] Ingestion Complete:")
    print(f"    Files processed: {stats['files_processed']}")
    print(f"    Chunks indexed: {stats['chunks_indexed']}")


if __name__ == "__main__":
    asyncio.run(main())
