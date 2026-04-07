"""Deterministic cross-repo system-learning artifact importer.

This module discovers candidate learning artifacts under a Git root (e.g. C:/Git),
classifies them into strict buckets, emits typed manifests, and produces an
informational-only context payload for system_learning proposal stages.

Hardening guarantees:
- Deterministic discovery (lexicographic walk order)
- Fail-closed parsing/normalization for accepted textual artifacts
- Explicit UNSAFE_OR_UNSCOPED bucket for weakly classified artifacts
- Proposal-only context output (no live routing/policy mutation authority)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "cross_repo_system_learning_import", "uwg_governed_write")
_emit_writes_through("p1", "cross_repo_system_learning_import", "uwg_governed_write_2")
_emit_pulls_context("p1", "cross_repo_system_learning_import", "context_retrieval")
_emit_pulls_context("p1", "cross_repo_system_learning_import", "context_retrieval_2")
emit_determinism_digest("trace_cross_repo_system_learning_import", "cross_repo_system_learning_import_dispatch")
emit_determinism_digest("trace_cross_repo_system_learning_import", "cross_repo_system_learning_import_complete")
_emit_validated_by_safety_plane("p1", "cross_repo_system_learning_import", "safety_validation")

ArtifactBucket = Literal[
    "TELEMETRY_EVENT_SOURCE",
    "AUDIT_SNAPSHOT_SOURCE",
    "RCA_SOURCE",
    "HEALING_OUTCOME_SOURCE",
    "PATTERN_MEMORY_SOURCE",
    "EMBEDDING_MEMORY_SOURCE",
    "RETRIEVAL_EVAL_SOURCE",
    "PROMPT_EVAL_SOURCE",
    "CONFIG_OR_SCHEMA_REFERENCE",
    "UNSAFE_OR_UNSCOPED",
]

Disposition = Literal["ignore", "ingest-as-C0", "ingest-as-L4-memory", "inspect-manually"]

_ALLOWED_BUCKETS = {
    "TELEMETRY_EVENT_SOURCE",
    "AUDIT_SNAPSHOT_SOURCE",
    "RCA_SOURCE",
    "HEALING_OUTCOME_SOURCE",
    "PATTERN_MEMORY_SOURCE",
    "EMBEDDING_MEMORY_SOURCE",
    "RETRIEVAL_EVAL_SOURCE",
    "PROMPT_EVAL_SOURCE",
    "CONFIG_OR_SCHEMA_REFERENCE",
    "UNSAFE_OR_UNSCOPED",
}

_TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".csv",
    ".xml",
    ".log",
}

_CANDIDATE_EXTENSIONS = _TEXT_EXTENSIONS | {".sqlite", ".db", ".faiss", ".f32", ".npy", ".npz"}

_EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
    "tmp",
    "temp",
    "logs",
    "cache",
    ".cache",
}

_EXCLUDED_PATH_SUBSTRINGS = (
    "/artifacts/system_learning/cross_repo_import/",
    "/docs/reports/plans/cross-repo-system-learning-incorporation-",
)

_REQUIRED_ACCEPTED_FIELDS = {
    "source_path",
    "source_repo",
    "content_hash",
    "schema_version",
    "ingestion_timestamp",
    "provenance_tag",
    "disposition",
    "bucket",
    "artifact_kind",
}

_FORBIDDEN_MUTATION_SURFACES = (
    "routing_rules",
    "safety_thresholds",
    "execution_tiers",
    "prompt_authority_slots",
    "live_policy",
    "healer_path_selection",
)


@dataclass(frozen=True, slots=True)
class DiscoveredArtifact:
    absolute_path: str
    source_repo: str
    artifact_type_guess: str
    confidence: float
    content_hash: str
    normalized_content_hash: str
    bucket: ArtifactBucket
    disposition: Disposition
    reason: str


@dataclass(frozen=True, slots=True)
class AcceptedArtifact:
    source_path: str
    source_repo: str
    content_hash: str
    schema_version: str
    ingestion_timestamp: int
    provenance_tag: str
    disposition: Disposition
    bucket: ArtifactBucket
    artifact_kind: str


@dataclass(frozen=True, slots=True)
class EmbeddingImportRecord:
    artifact_kind: str
    source_repo: str
    source_path: str
    content_hash: str
    created_from_import: bool
    namespace: str
    target_dimension: int
    text: str


@dataclass(frozen=True, slots=True)
class ImportDigests:
    discovery_manifest_digest: str
    accepted_manifest_digest: str
    normalized_content_digest_set: str
    embedding_import_digest: str
    system_learning_incorporation_digest: str


@dataclass(frozen=True, slots=True)
class ImportRunResult:
    discovered: tuple[DiscoveredArtifact, ...]
    accepted: tuple[AcceptedArtifact, ...]
    rejected: tuple[DiscoveredArtifact, ...]
    embedding_records: tuple[EmbeddingImportRecord, ...]
    digests: ImportDigests
    wiring_map: dict[str, list[str]]
    unresolved_unsafe_artifacts: tuple[DiscoveredArtifact, ...]


def _canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_candidate(path: Path) -> bool:
    p = str(path).lower()
    if path.suffix.lower() in _CANDIDATE_EXTENSIONS:
        return True
    keywords = (
        "rca",
        "healing",
        "telemetry",
        "audit",
        "drift",
        "embedding",
        "faiss",
        "vector",
        "retrieval",
        "prompt_eval",
        "policy_eval",
        "benchmark",
        "manifest",
        "schema",
        "registry",
        "snapshot",
    )
    return any(k in p for k in keywords)


def _artifact_guess_and_bucket(path: Path) -> tuple[str, ArtifactBucket, float, str]:
    p = str(path).replace("\\", "/").lower()

    def _has(*tokens: str) -> bool:
        return any(t in p for t in tokens)

    if _has("telemetry"):
        return ("telemetry_snapshot", "TELEMETRY_EVENT_SOURCE", 0.95, "telemetry token match")
    if _has("audit"):
        return ("audit_snapshot", "AUDIT_SNAPSHOT_SOURCE", 0.93, "audit token match")
    if _has("rca"):
        return ("rca_artifact", "RCA_SOURCE", 0.95, "rca token match")
    if _has("healing") and _has("outcome", "snapshot", "aggregate"):
        return ("healing_outcome", "HEALING_OUTCOME_SOURCE", 0.92, "healing+outcome token match")
    if _has("pattern"):
        return ("pattern_memory", "PATTERN_MEMORY_SOURCE", 0.90, "pattern token match")
    if _has("faiss", "embedding", "vector", "seed_pack") or path.suffix.lower() in {".faiss", ".f32", ".npy"}:
        return ("embedding_memory", "EMBEDDING_MEMORY_SOURCE", 0.90, "embedding/vector token match")
    if _has("retrieval") and _has("eval", "benchmark", "score"):
        return ("retrieval_eval", "RETRIEVAL_EVAL_SOURCE", 0.88, "retrieval eval token match")
    if _has("prompt") and _has("eval", "benchmark", "score"):
        return ("prompt_eval", "PROMPT_EVAL_SOURCE", 0.88, "prompt eval token match")
    if _has("schema", "manifest", "registry"):
        return (
            "config_or_schema",
            "CONFIG_OR_SCHEMA_REFERENCE",
            0.84,
            "schema/manifest/registry token match",
        )
    return ("unscoped_candidate", "UNSAFE_OR_UNSCOPED", 0.25, "no strong classifier signal")


def _classify_disposition(bucket: ArtifactBucket, confidence: float) -> tuple[Disposition, str]:
    if bucket == "UNSAFE_OR_UNSCOPED" or confidence < 0.67:
        return ("inspect-manually", "weak confidence or unscoped bucket")
    if bucket in {"EMBEDDING_MEMORY_SOURCE", "HEALING_OUTCOME_SOURCE"}:
        return ("ingest-as-L4-memory", "memory-oriented artifact")
    if bucket in {
        "TELEMETRY_EVENT_SOURCE",
        "AUDIT_SNAPSHOT_SOURCE",
        "RCA_SOURCE",
        "PATTERN_MEMORY_SOURCE",
        "RETRIEVAL_EVAL_SOURCE",
        "PROMPT_EVAL_SOURCE",
        "CONFIG_OR_SCHEMA_REFERENCE",
    }:
        return ("ingest-as-C0", "informational-only analysis artifact")
    return ("inspect-manually", "default fail-closed disposition")


def _normalize_text_bytes(raw: bytes) -> bytes:
    text = raw.decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    return "\n".join(lines).encode("utf-8")


def _hash_file(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    raw_hash = _sha256_hex(raw)
    if path.suffix.lower() in _TEXT_EXTENSIONS:
        try:
            normalized = _normalize_text_bytes(raw)
        except UnicodeDecodeError:    # guardian: Encoding errors should specify fallback encoding strategy
            return raw_hash, raw_hash
        return raw_hash, _sha256_hex(normalized)
    return raw_hash, raw_hash


def _derive_repo_name(path: Path, git_root: Path) -> str:
    rel = path.relative_to(git_root)
    return rel.parts[0] if rel.parts else git_root.name


def _derive_ingestion_timestamp_from_path(path: str) -> int:
    matches = re.findall(r"(\d{10,14})", path)
    if matches:
        return int(matches[-1][:10])
    ymd_matches = re.findall(r"(20\d{2})(\d{2})(\d{2})", path)
    if ymd_matches:
        y, m, d = ymd_matches[-1]
        return int(f"{y}{m}{d}00")
    return 0


def discover_artifacts(git_root: Path) -> tuple[DiscoveredArtifact, ...]:
    artifacts: list[DiscoveredArtifact] = []
    for current, dirnames, filenames in os.walk(git_root, topdown=True):
        dirnames[:] = sorted(d for d in dirnames if d not in _EXCLUDED_DIR_NAMES)
        filenames.sort()
        current_path = Path(current)
        for filename in filenames:
            path = current_path / filename
            normalized_path = str(path).replace("\\", "/").lower()
            if any(token in normalized_path for token in _EXCLUDED_PATH_SUBSTRINGS):
                continue
            if not _is_candidate(path):
                continue
            raw_hash, normalized_hash = _hash_file(path)
            guess, bucket, confidence, reason = _artifact_guess_and_bucket(path)
            disposition, disposition_reason = _classify_disposition(bucket, confidence)
            artifacts.append(
                DiscoveredArtifact(
                    absolute_path=str(path.resolve()),
                    source_repo=_derive_repo_name(path, git_root),
                    artifact_type_guess=guess,
                    confidence=round(confidence, 3),
                    content_hash=normalized_hash,
                    normalized_content_hash=normalized_hash,
                    bucket=bucket,
                    disposition=disposition,
                    reason=f"{reason}; {disposition_reason}",
                ),
            )

    artifacts.sort(key=lambda a: a.absolute_path)

    # Deterministic duplicate suppression by normalized content hash
    canonical_by_hash: dict[str, str] = {}
    deduped: list[DiscoveredArtifact] = []
    for item in artifacts:
        canonical = canonical_by_hash.get(item.content_hash)
        if canonical is None:
            canonical_by_hash[item.content_hash] = item.absolute_path
            deduped.append(item)
            continue
        deduped.append(
            replace(
                item,
                disposition="ignore",
                reason=f"duplicate content hash; canonical={canonical}",
            ),
        )

    return tuple(deduped)


def build_accepted_manifest(discovered: tuple[DiscoveredArtifact, ...]) -> tuple[AcceptedArtifact, ...]:
    accepted: list[AcceptedArtifact] = []
    for item in discovered:
        if item.disposition not in {"ingest-as-C0", "ingest-as-L4-memory"}:
            continue
        if item.bucket not in _ALLOWED_BUCKETS or item.bucket == "UNSAFE_OR_UNSCOPED":
            continue
        accepted.append(
            AcceptedArtifact(
                source_path=item.absolute_path,
                source_repo=item.source_repo,
                content_hash=item.content_hash,
                schema_version="v1",
                ingestion_timestamp=_derive_ingestion_timestamp_from_path(item.absolute_path),
                provenance_tag=f"cross_repo_import::{item.bucket.lower()}",
                disposition=item.disposition,
                bucket=item.bucket,
                artifact_kind=item.artifact_type_guess,
            ),
        )

    accepted.sort(key=lambda x: (x.source_repo, x.source_path, x.content_hash))
    return tuple(accepted)


def _namespace_and_dimension_for_bucket(bucket: ArtifactBucket) -> tuple[str, int]:
    if bucket == "TELEMETRY_EVENT_SOURCE":
        return ("cross_repo_telemetry_events", 384)
    if bucket in {"RETRIEVAL_EVAL_SOURCE", "PROMPT_EVAL_SOURCE"}:
        return ("cross_repo_eval_corpus", 768)
    return ("cross_repo_healing_contexts", 768)


def build_embedding_import_records(accepted: tuple[AcceptedArtifact, ...]) -> tuple[EmbeddingImportRecord, ...]:
    records: list[EmbeddingImportRecord] = []
    seen_hashes: set[str] = set()

    for item in accepted:
        path = Path(item.source_path)
        if path.suffix.lower() not in _TEXT_EXTENSIONS:
            continue
        raw = path.read_bytes()
        try:
            normalized = _normalize_text_bytes(raw)
        except UnicodeDecodeError as exc:    # guardian: Encoding errors should specify fallback encoding strategy
            raise RuntimeError(f"HARD FAIL: UTF-8 decode failed for accepted artifact {item.source_path}: {exc}") from exc

        text_hash = _sha256_hex(normalized)
        if text_hash in seen_hashes:
            continue
        seen_hashes.add(text_hash)

        namespace, dimension = _namespace_and_dimension_for_bucket(item.bucket)
        records.append(
            EmbeddingImportRecord(
                artifact_kind=item.artifact_kind,
                source_repo=item.source_repo,
                source_path=item.source_path,
                content_hash=item.content_hash,
                created_from_import=True,
                namespace=namespace,
                target_dimension=dimension,
                text=normalized.decode("utf-8"),
            ),
        )

    records.sort(key=lambda r: (r.namespace, r.content_hash, r.source_path))
    _validate_embedding_dimensions(records)
    return tuple(records)


def _validate_embedding_dimensions(records: list[EmbeddingImportRecord] | tuple[EmbeddingImportRecord, ...]) -> None:
    by_namespace: dict[str, set[int]] = {}
    for record in records:
        by_namespace.setdefault(record.namespace, set()).add(record.target_dimension)

    for namespace, dims in sorted(by_namespace.items()):
        if len(dims) > 1:
            raise RuntimeError(
                f"HARD FAIL: vector dimension mismatch in namespace {namespace}: {sorted(dims)}",
            )


def _digest_of_dataclasses(items: list[Any] | tuple[Any, ...]) -> str:
    payload = [asdict(i) for i in items]
    return _sha256_hex(_canonical_json_bytes(payload))


def _build_wiring_map() -> dict[str, list[str]]:
    return {
        "TELEMETRY_EVENT_SOURCE": [
            "proposal_generation_evidence_inputs",
            "retrieval_evaluation_corpus_inputs",
        ],
        "AUDIT_SNAPSHOT_SOURCE": ["audit_rca_blast_radius_context_inputs", "meta_learning_snapshot_assembly_inputs"],
        "RCA_SOURCE": ["failure_fingerprinter_inputs", "proposal_generation_evidence_inputs"],
        "HEALING_OUTCOME_SOURCE": ["healing_outcome_history_inputs", "meta_learning_snapshot_assembly_inputs"],
        "PATTERN_MEMORY_SOURCE": ["pattern_analysis_engine_inputs", "failure_fingerprinter_inputs"],
        "EMBEDDING_MEMORY_SOURCE": ["local_faiss_seed_pack_memory_inputs"],
        "RETRIEVAL_EVAL_SOURCE": ["retrieval_evaluation_corpus_inputs"],
        "PROMPT_EVAL_SOURCE": ["proposal_generation_evidence_inputs"],
        "CONFIG_OR_SCHEMA_REFERENCE": ["audit_rca_blast_radius_context_inputs"],
        "UNSAFE_OR_UNSCOPED": [],
    }


def run_import(git_root: Path) -> ImportRunResult:
    discovered = discover_artifacts(git_root)
    accepted = build_accepted_manifest(discovered)
    rejected = tuple(d for d in discovered if d.disposition in {"inspect-manually", "ignore"})
    unsafe = tuple(d for d in discovered if d.bucket == "UNSAFE_OR_UNSCOPED")
    embedding_records = build_embedding_import_records(accepted)

    discovery_digest = _digest_of_dataclasses(discovered)
    accepted_digest = _digest_of_dataclasses(accepted)
    normalized_set_digest = _sha256_hex(
        _canonical_json_bytes(sorted({r.content_hash for r in embedding_records})),
    )
    embedding_digest = _digest_of_dataclasses(embedding_records)
    wiring_map = _build_wiring_map()

    incorporation_digest = _sha256_hex(
        _canonical_json_bytes(
            {
                "discovery_manifest_digest": discovery_digest,
                "accepted_manifest_digest": accepted_digest,
                "normalized_content_digest_set": normalized_set_digest,
                "embedding_import_digest": embedding_digest,
                "accepted_count": len(accepted),
                "embedding_record_count": len(embedding_records),
                "proposal_only": True,
                "wiring_map": wiring_map,
            },
        ),
    )

    digests = ImportDigests(
        discovery_manifest_digest=discovery_digest,
        accepted_manifest_digest=accepted_digest,
        normalized_content_digest_set=normalized_set_digest,
        embedding_import_digest=embedding_digest,
        system_learning_incorporation_digest=incorporation_digest,
    )

    return ImportRunResult(
        discovered=discovered,
        accepted=accepted,
        rejected=rejected,
        embedding_records=embedding_records,
        digests=digests,
        wiring_map=wiring_map,
        unresolved_unsafe_artifacts=unsafe,
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_json_bytes(payload))


def write_run_artifacts(repo_root: Path, result: ImportRunResult) -> dict[str, str]:
    artifacts_dir = repo_root / "artifacts" / "system_learning" / "cross_repo_import"
    docs_dir = repo_root / "docs" / "reports" / "plans"
    suffix = result.digests.system_learning_incorporation_digest[:6]

    discovery_path = artifacts_dir / "discovery_inventory.json"
    accepted_path = artifacts_dir / "accepted_manifest.json"
    rejected_path = artifacts_dir / "rejected_manifest.json"
    embedding_path = artifacts_dir / "embedding_import_manifest.json"
    digests_path = artifacts_dir / "determinism_digests.json"
    wiring_path = artifacts_dir / "wiring_map.json"
    context_path = artifacts_dir / "latest_context.json"

    _write_json(discovery_path, [asdict(x) for x in result.discovered])
    _write_json(accepted_path, [asdict(x) for x in result.accepted])
    _write_json(rejected_path, [asdict(x) for x in result.rejected])
    _write_json(embedding_path, [asdict(x) for x in result.embedding_records])
    _write_json(digests_path, asdict(result.digests))
    _write_json(wiring_path, result.wiring_map)

    context_payload = {
        "schema_version": "v1",
        "proposal_only": True,
        "status": "READY" if result.accepted else "NO_ACCEPTED_ARTIFACTS",
        "accepted_count": len(result.accepted),
        "embedding_record_count": len(result.embedding_records),
        "accepted_manifest_digest": result.digests.accepted_manifest_digest,
        "embedding_import_digest": result.digests.embedding_import_digest,
        "forbidden_mutation_surfaces_blocked": list(_FORBIDDEN_MUTATION_SURFACES),
        "wiring_map": result.wiring_map,
        "accepted_by_bucket": {
            bucket: sum(1 for a in result.accepted if a.bucket == bucket) for bucket in sorted(_ALLOWED_BUCKETS)
        },
    }
    _write_json(context_path, context_payload)

    report_path = docs_dir / f"cross-repo-system-learning-incorporation-{suffix}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Cross-Repo System Learning Incorporation Report")
    lines.append("")
    lines.append("## Deterministic Discovery Inventory")
    lines.append("")
    lines.append("| Absolute Path | Artifact Type Guess | Confidence | Content Hash | Proposed Disposition |")
    lines.append("|---|---:|---:|---|---|")
    for item in result.discovered:
        lines.append(
            f"| `{item.absolute_path}` | `{item.artifact_type_guess}` | {item.confidence:.3f} | `{item.content_hash}` | `{item.disposition}` |",
        )

    lines.append("")
    lines.append("## Accepted vs Rejected")
    lines.append("")
    lines.append(f"- Accepted: {len(result.accepted)}")
    lines.append(f"- Rejected/Manual: {len(result.rejected)}")
    lines.append(f"- Unsafe/Unscoped: {len(result.unresolved_unsafe_artifacts)}")

    lines.append("")
    lines.append("## Wiring Map")
    lines.append("")
    for bucket, targets in sorted(result.wiring_map.items()):
        rendered = ", ".join(f"`{t}`" for t in targets) if targets else "`<none>`"
        lines.append(f"- `{bucket}` -> {rendered}")

    lines.append("")
    lines.append("## Determinism Digests")
    lines.append("")
    lines.append(f"- discovery_manifest_digest: `{result.digests.discovery_manifest_digest}`")
    lines.append(f"- accepted_manifest_digest: `{result.digests.accepted_manifest_digest}`")
    lines.append(f"- normalized_content_digest_set: `{result.digests.normalized_content_digest_set}`")
    lines.append(f"- embedding_import_digest: `{result.digests.embedding_import_digest}`")
    lines.append(
        f"- system_learning_incorporation_digest: `{result.digests.system_learning_incorporation_digest}`",
    )

    lines.append("")
    lines.append("## Blockers and Unresolved Unsafe Artifacts")
    lines.append("")
    if result.unresolved_unsafe_artifacts:
        for item in result.unresolved_unsafe_artifacts:
            lines.append(f"- `{item.absolute_path}` :: `{item.reason}`")
    else:
        lines.append("- None")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "discovery_manifest": str(discovery_path),
        "accepted_manifest": str(accepted_path),
        "rejected_manifest": str(rejected_path),
        "embedding_manifest": str(embedding_path),
        "digests": str(digests_path),
        "wiring_map": str(wiring_path),
        "latest_context": str(context_path),
        "report": str(report_path),
    }


def load_cross_repo_learning_context(repo_root: Path) -> dict[str, Any]:
    context_path = repo_root / "artifacts" / "system_learning" / "cross_repo_import" / "latest_context.json"
    accepted_path = repo_root / "artifacts" / "system_learning" / "cross_repo_import" / "accepted_manifest.json"

    if not context_path.exists() or not accepted_path.exists():
        return {
            "schema_version": "v1",
            "proposal_only": True,
            "status": "MISSING_CONTEXT",
            "reason": "cross-repo import manifests not found",
            "accepted_count": 0,
            "embedding_record_count": 0,
            "forbidden_mutation_surfaces_blocked": list(_FORBIDDEN_MUTATION_SURFACES),
            "wiring_map": _build_wiring_map(),
        }

    context = json.loads(context_path.read_text(encoding="utf-8"))
    accepted = json.loads(accepted_path.read_text(encoding="utf-8"))

    if context.get("schema_version") != "v1":
        raise RuntimeError("HARD FAIL: cross-repo context schema_version mismatch")
    if context.get("proposal_only") is not True:
        raise RuntimeError("HARD FAIL: cross-repo context proposal_only must remain True")

    seen_paths: dict[str, str] = {}
    for row in accepted:
        missing = sorted(_REQUIRED_ACCEPTED_FIELDS - set(row.keys()))
        if missing:
            raise RuntimeError(f"HARD FAIL: accepted manifest row missing fields: {missing}")
        source_path = str(row["source_path"])
        content_hash = str(row["content_hash"])
        previous = seen_paths.get(source_path)
        if previous is not None and previous != content_hash:
            raise RuntimeError(
                f"HARD FAIL: duplicate conflicting manifests for {source_path}: {previous} vs {content_hash}",
            )
        seen_paths[source_path] = content_hash

    return context


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-repo system-learning importer")
    parser.add_argument("--git-root", required=True, help="Root containing sibling repos (e.g. C:/Git)")
    parser.add_argument("--repo-root", required=True, help="Agentic-Workflow root path")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    git_root = Path(args.git_root).resolve()
    repo_root = Path(args.repo_root).resolve()

    result = run_import(git_root)
    paths = write_run_artifacts(repo_root, result)

    print(f"DISCOVERED={len(result.discovered)}")
    print(f"ACCEPTED={len(result.accepted)}")
    print(f"REJECTED={len(result.rejected)}")
    print(f"UNSAFE={len(result.unresolved_unsafe_artifacts)}")
    print(f"DISCOVERY_DIGEST={result.digests.discovery_manifest_digest}")
    print(f"ACCEPTED_DIGEST={result.digests.accepted_manifest_digest}")
    print(f"NORMALIZED_DIGEST={result.digests.normalized_content_digest_set}")
    print(f"EMBEDDING_DIGEST={result.digests.embedding_import_digest}")
    print(f"INCORPORATION_DIGEST={result.digests.system_learning_incorporation_digest}")
    print(f"REPORT_PATH={paths['report']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
