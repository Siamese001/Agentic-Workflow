"""Semantic Gap Analyzer for Agentic Architecture Major Arteries.

Traces actual execution flows through L0-L6 layers and identifies where
architectural intent (lower latency, deterministic lookups, cache-first patterns)
diverges from implementation reality.

Usage:
    python tools/semantic_gap_analyzer.py --output docs/reports/plans/semantic_gap_analysis.md
"""

from __future__ import annotations

import ast
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).parent.parent
AGENTIC_CORE = REPO_ROOT / "agentic_core"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PRIORITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
PYTHON_FILE_GLOB = "*.py"
EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "site-packages",
}
EXCLUDED_FILE_SUFFIXES = {".pyi"}

PROMPT_SLOT_ORDER = ("S0", "D0", "I0", "C0", "U0")
PROMPT_SLOT_DESCRIPTIONS = {
    "S0": "System / state rulebooks and hard invariants",
    "D0": "Injections, semantic fences, and tool constraints",
    "I0": "Instructional identity and governed behavior",
    "C0": "Dependency context such as RAG or Elevator Shaft injected knowledge",
    "U0": "Raw user prompt / intent",
}
PROMPT_TAXONOMY_PATTERNS = {
    "S0": (
        "S0",
        "system",
        "system_prompt",
        "constitution",
        "invariant",
        "rulebook",
        "state_prompt",
    ),
    "D0": (
        "D0",
        "injection",
        "guardrail",
        "tool_constraint",
        "safety_fence",
        "semantic_fence",
        "policy_injection",
    ),
    "I0": (
        "I0",
        "instruction",
        "instructional",
        "identity_prompt",
        "role_prompt",
        "persona",
        "behavior",
    ),
    "C0": (
        "C0",
        "dependency",
        "context",
        "rag",
        "retrieval",
        "elevator_shaft",
        "knowledge_pack",
        "injected_context",
    ),
    "U0": (
        "U0",
        "user_prompt",
        "user_input",
        "raw_intent",
        "request_text",
        "prompt_text",
        "query_text",
    ),
}
PROMPT_ASSEMBLER_HINTS = (
    "assemble",
    "assembler",
    "build_prompt",
    "compose_prompt",
    "prompt_package",
    "instruction_packet",
    "governed_prompt",
)


@dataclass
class ImportTrace:
    """Tracks an import statement and its usage context."""

    module: str
    imported_names: list[str]
    file_path: Path
    line_number: int
    is_used: bool = False


@dataclass
class CacheOpportunity:
    """Represents a potential caching opportunity."""

    layer: str
    hot_path: str
    current_pattern: str
    cache_candidate: str
    impact: str
    priority: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class SemanticGap:
    """Represents a gap between architectural intent and implementation."""

    gap_id: str
    layer: str
    artery: str
    intent: str
    reality: str
    impact: str
    priority: str
    evidence_files: list[str] = field(default_factory=list)
    recommended_fix: str = ""


@dataclass(frozen=True)
class ParseFailure:
    """Represents a file that could not be analyzed."""

    file_path: Path
    error_type: str
    message: str


@dataclass
class FileAnalysis:
    """Typed analysis result for a single file."""

    file_path: Path
    imports: list[ImportTrace] = field(default_factory=list)
    calls: list[tuple[str, int]] = field(default_factory=list)
    cache_reads: list[int] = field(default_factory=list)
    cache_writes: list[int] = field(default_factory=list)
    l4_state_accesses: list[int] = field(default_factory=list)
    imported_module_names: set[str] = field(default_factory=set)
    imported_symbol_names: set[str] = field(default_factory=set)
    used_names: set[str] = field(default_factory=set)
    string_literals: list[str] = field(default_factory=list)
    prompt_slot_hits: dict[str, list[str]] = field(default_factory=dict)
    manifest_hash_mentions: list[int] = field(default_factory=list)
    boundary_snapshot_mentions: list[int] = field(default_factory=list)
    prompt_assembly_markers: list[str] = field(default_factory=list)
    parse_failure: ParseFailure | None = None

    @property
    def ok(self) -> bool:
        return self.parse_failure is None


class ASTAnalyzer:
    """AST-based code analyzer for tracing execution flows."""

    def __init__(self, root: Path):
        self.root = root
        self.import_graph: dict[str, list[ImportTrace]] = {}
        self.function_calls: dict[str, list[tuple[str, int]]] = {}
        self.parse_failures: list[ParseFailure] = []

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a Python file and extract imports, calls, and patterns."""
        analysis = FileAnalysis(file_path=file_path)

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            failure = ParseFailure(
                file_path=file_path,
                error_type=type(e).__name__,
                message=str(e),
            )
            self.parse_failures.append(failure)
            logger.warning(f"Failed to parse {file_path}: {e}")
            analysis.parse_failure = failure
            return analysis

        analysis.used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        analysis.string_literals = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
        analysis.prompt_slot_hits = {slot: [] for slot in PROMPT_SLOT_ORDER}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_name = alias.asname or alias.name.split(".")[-1]
                    trace = ImportTrace(
                        module=alias.name,
                        imported_names=[imported_name],
                        file_path=file_path,
                        line_number=node.lineno,
                    )
                    trace.is_used = imported_name in analysis.used_names
                    analysis.imports.append(trace)
                    analysis.imported_module_names.add(alias.name)
                    analysis.imported_symbol_names.add(imported_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names: list[str] = []
                    for alias in node.names:
                        imported_name = alias.asname or alias.name
                        imported_names.append(imported_name)
                        analysis.imported_symbol_names.add(imported_name)

                    trace = ImportTrace(
                        module=node.module,
                        imported_names=imported_names,
                        file_path=file_path,
                        line_number=node.lineno,
                    )
                    trace.is_used = any(name in analysis.used_names for name in imported_names)
                    analysis.imports.append(trace)
                    analysis.imported_module_names.add(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    call_name = node.func.id
                else:
                    continue

                analysis.calls.append((call_name, node.lineno))

                # Detect cache patterns
                if call_name in {"get_json", "get", "hget", "mget"}:
                    analysis.cache_reads.append(node.lineno)
                elif call_name in {"set_json", "set", "hset", "mset"}:
                    analysis.cache_writes.append(node.lineno)

                # Detect probable L4 state accesses
                lowered = call_name.lower()
                if any(token in lowered for token in ("ledger", "blob", "state", "memory", "registry")):
                    analysis.l4_state_accesses.append(node.lineno)

        for literal in analysis.string_literals:
            literal_lower = literal.lower()
            for slot, patterns in PROMPT_TAXONOMY_PATTERNS.items():
                if any(pattern.lower() in literal_lower for pattern in patterns):
                    analysis.prompt_slot_hits[slot].append(literal)

            if "manifest hash" in literal_lower or "manifest_hash" in literal_lower:
                analysis.manifest_hash_mentions.append(1)
            if "boundary_snapshot" in literal_lower:
                analysis.boundary_snapshot_mentions.append(1)
            if any(hint in literal_lower for hint in PROMPT_ASSEMBLER_HINTS):
                analysis.prompt_assembly_markers.append(literal)

        for name in analysis.used_names:
            lowered_name = name.lower()
            for slot, patterns in PROMPT_TAXONOMY_PATTERNS.items():
                if any(pattern.lower() in lowered_name for pattern in patterns):
                    analysis.prompt_slot_hits[slot].append(name)

            if "manifest_hash" in lowered_name:
                analysis.manifest_hash_mentions.append(1)
            if "boundary_snapshot" in lowered_name:
                analysis.boundary_snapshot_mentions.append(1)
            if any(hint in lowered_name for hint in PROMPT_ASSEMBLER_HINTS):
                analysis.prompt_assembly_markers.append(name)

        return analysis

    def find_hot_paths(self, layer_dir: Path, pattern: str) -> list[Path]:
        """Find files matching a pattern in a layer directory."""
        if not layer_dir.exists():
            return []

        paths = (
            path
            for path in layer_dir.rglob(pattern)
            if path.is_file()
            and path.suffix not in EXCLUDED_FILE_SUFFIXES
            and not any(part in EXCLUDED_DIR_NAMES for part in path.parts)
        )
        return sorted(paths, key=lambda p: str(p.relative_to(self.root)).lower())


def _stable_relpath(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _stable_gap_id(prefix: str, file_path: Path) -> str:
    digest = hashlib.sha1(_stable_relpath(file_path).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def _priority_sort_key(gap: SemanticGap) -> tuple[int, str]:
    return (PRIORITY_RANK.get(gap.priority, 99), gap.gap_id)


def _contains_module_reference(analysis: FileAnalysis, module_hint: str) -> bool:
    return any(module_hint in module_name for module_name in analysis.imported_module_names)


def _contains_symbol_reference(analysis: FileAnalysis, symbol_hint: str) -> bool:
    return any(symbol_hint in symbol_name for symbol_name in analysis.imported_symbol_names)


def _analysis_mentions_cache(
    analysis: FileAnalysis, module_hint: str, symbol_hint: str | None = None
) -> bool:
    if _contains_module_reference(analysis, module_hint):
        return True
    if symbol_hint and _contains_symbol_reference(analysis, symbol_hint):
        return True
    return False


def _slot_coverage_score(slot_hits: dict[str, list[str]]) -> int:
    return sum(1 for slot in PROMPT_SLOT_ORDER if slot_hits.get(slot))


def _missing_slots(slot_hits: dict[str, list[str]]) -> list[str]:
    return [slot for slot in PROMPT_SLOT_ORDER if not slot_hits.get(slot)]


def _looks_like_prompt_assembler(file_path: Path, analysis: FileAnalysis) -> bool:
    rel = _stable_relpath(file_path).lower()
    if "prompt" in file_path.name.lower() and any(
        token in rel for token in ("assemble", "assembler", "builder", "compose", "packet")
    ):
        return True
    if analysis.prompt_assembly_markers:
        return True
    return False


def _report_slot_status(slot_hits: dict[str, list[str]]) -> str:
    parts = []
    for slot in PROMPT_SLOT_ORDER:
        status = "present" if slot_hits.get(slot) else "missing"
        parts.append(f"{slot}={status}")
    return ", ".join(parts)


class SemanticGapAnalyzer:
    """Main analyzer for detecting semantic gaps in the architecture."""

    def __init__(self):
        self.ast_analyzer = ASTAnalyzer(AGENTIC_CORE)
        self.gaps: list[SemanticGap] = []
        self.cache_opportunities: list[CacheOpportunity] = []
        self.parse_failures: list[ParseFailure] = []
        self.prompt_taxonomy_findings: list[dict[str, Any]] = []

    def analyze_l0_routing_gate(self) -> list[SemanticGap]:
        """Analyze L0 routing gate for semantic gaps."""
        logger.info("Analyzing L0 Routing Gate...")
        gaps = []

        # Check if discovery_cache is wired into full_agent_discovery
        discovery_py = AGENTIC_CORE / "utils" / "full_agent_discovery.py"
        if discovery_py.exists():
            analysis = self.ast_analyzer.analyze_file(discovery_py)
            if not analysis.ok:
                return gaps

            cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="discovery_cache",
                symbol_hint="AgentDiscoveryCache",
            )

            if not cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L0-GAP-001",
                        layer="L0",
                        artery="Agent Discovery Hot Path",
                        intent="Cache agent discovery results to avoid repeated file I/O and AST parsing",
                        reality="full_agent_discovery.py does not import or use discovery_cache.py",
                        impact="Every agent discovery call re-scans filesystem and re-parses Python files",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(discovery_py)],
                        recommended_fix="Import AgentDiscoveryCache and wrap get_all_agents() with cache.get_or_fetch()",
                    )
                )

        # Check reasoning_policy_engine for policy registry cache usage
        policy_engine = AGENTIC_CORE / "L0_routing" / "engines" / "reasoning_policy_engine.py"
        if policy_engine.exists():
            analysis = self.ast_analyzer.analyze_file(policy_engine)
            if not analysis.ok:
                return gaps

            policy_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="policy_registry_cache",
                symbol_hint="PolicyRegistryCache",
            )

            if not policy_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L0-GAP-002",
                        layer="L0",
                        artery="Reasoning Policy Engine",
                        intent="Cache immutable policy configurations to avoid repeated L4 state lookups",
                        reality="reasoning_policy_engine.py does not use policy_registry_cache.py",
                        impact="Policy config fetched from L4 state on every request",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(policy_engine)],
                        recommended_fix="Wrap policy_config retrieval with PolicyRegistryCache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l1_cognition(self) -> list[SemanticGap]:
        """Analyze L1 cognition layer for semantic gaps."""
        logger.info("Analyzing L1 Cognition Layer...")
        gaps = []

        # Check cognitive_engine for tool embedding cache
        cognitive_engine = AGENTIC_CORE / "L1_cognition" / "engines" / "cognitive_engine.py"
        if cognitive_engine.exists():
            analysis = self.ast_analyzer.analyze_file(cognitive_engine)
            if not analysis.ok:
                return gaps

            tool_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="tool_embedding_cache",
                symbol_hint="ToolEmbeddingCache",
            )

            if not tool_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L1-GAP-001",
                        layer="L1",
                        artery="Cognitive Engine Tool Resolution",
                        intent="Cache expensive tool embedding computations to avoid repeated API calls",
                        reality="cognitive_engine.py does not use tool_embedding_cache.py",
                        impact="Tool embeddings recomputed on every cognition cycle",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(cognitive_engine)],
                        recommended_fix="Import ToolEmbeddingCache and wrap embedding generation with cache.get_or_fetch()",
                    )
                )

        # Check for prompt artifact cache usage
        prompt_files = self.ast_analyzer.find_hot_paths(AGENTIC_CORE / "L1_cognition", "*prompt*.py")
        for prompt_file in prompt_files:
            analysis = self.ast_analyzer.analyze_file(prompt_file)
            if not analysis.ok:
                continue

            prompt_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="prompt_artifact_cache",
                symbol_hint="PromptArtifactCache",
            )

            if not prompt_cache_imported and "cache" not in prompt_file.name:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L1-GAP-PROMPT", prompt_file),
                        layer="L1",
                        artery="Prompt Artifact Retrieval",
                        intent="Cache parsed prompt templates to avoid repeated file I/O and parsing",
                        reality=f"{prompt_file.name} does not use prompt_artifact_cache",
                        impact="Prompt templates re-read and re-parsed on every request",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(prompt_file)],
                        recommended_fix="Wrap prompt loading with prompt_artifact_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_prompt_taxonomy_coverage(self) -> list[SemanticGap]:
        """Analyze prompt assemblers for S0/D0/I0/C0/U0 taxonomy coverage."""
        logger.info("Analyzing Prompt Taxonomy Coverage...")
        gaps = []

        candidate_files = []
        for base_dir in (
            AGENTIC_CORE / "L0_routing",
            AGENTIC_CORE / "L1_cognition",
            AGENTIC_CORE / "L2_execution",
            AGENTIC_CORE / "utils",
        ):
            candidate_files.extend(self.ast_analyzer.find_hot_paths(base_dir, PYTHON_FILE_GLOB))

        seen: set[str] = set()
        for prompt_file in candidate_files:
            rel = _stable_relpath(prompt_file)
            if rel in seen:
                continue
            seen.add(rel)

            analysis = self.ast_analyzer.analyze_file(prompt_file)
            if not analysis.ok:
                continue
            if not _looks_like_prompt_assembler(prompt_file, analysis):
                continue

            coverage_score = _slot_coverage_score(analysis.prompt_slot_hits)
            missing_slots = _missing_slots(analysis.prompt_slot_hits)
            slot_status = _report_slot_status(analysis.prompt_slot_hits)

            self.prompt_taxonomy_findings.append(
                {
                    "file": rel,
                    "coverage_score": coverage_score,
                    "slot_status": slot_status,
                    "manifest_hash": bool(analysis.manifest_hash_mentions),
                    "boundary_snapshot": bool(analysis.boundary_snapshot_mentions),
                }
            )

            if missing_slots:
                priority = "HIGH" if {"S0", "C0", "U0"} & set(missing_slots) else "MEDIUM"
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("PROMPT-TAXONOMY-GAP", prompt_file),
                        layer="L1",
                        artery="Prompt Taxonomy Assembly Coverage",
                        intent=(
                            "Assembled prompts should cover canonical taxonomy slots "
                            "S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture."
                        ),
                        reality=(
                            f"{prompt_file.name} appears to assemble or package prompts but has incomplete "
                            f"taxonomy evidence: {slot_status}"
                        ),
                        impact=(
                            "Prompt packages may omit required rulebooks, fences, instructional identity, "
                            "dependency context, or raw user intent, causing drift from the governed prompt model."
                        ),
                        priority=priority,
                        evidence_files=[rel],
                        recommended_fix=(
                            "Add explicit slot assembly or manifest fields for the missing taxonomy slots: "
                            + ", ".join(missing_slots)
                        ),
                    )
                )

            if not analysis.manifest_hash_mentions:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("PROMPT-MANIFEST-GAP", prompt_file),
                        layer="L1",
                        artery="Prompt Package Manifest Integrity",
                        intent="Governed prompt assembly should emit a manifest hash for parity and auditability.",
                        reality=f"{prompt_file.name} shows no manifest hash evidence.",
                        impact="You cannot prove deterministic prompt-package parity across runs.",
                        priority="MEDIUM",
                        evidence_files=[rel],
                        recommended_fix="Emit and persist a manifest hash for the final governed prompt package.",
                    )
                )

            if not analysis.boundary_snapshot_mentions:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("PROMPT-VALIDATOR-GAP", prompt_file),
                        layer="L2",
                        artery="Prompt Pre-flight Validation",
                        intent="Prompt execution paths should support validator boundary snapshots before execution.",
                        reality=f"{prompt_file.name} shows no boundary_snapshot evidence.",
                        impact="Prompt healing and pre-flight diagnostics may be blind to assembly defects.",
                        priority="LOW",
                        evidence_files=[rel],
                        recommended_fix="Wire validator output to emit boundary_snapshot.json for prompt-package inspection.",
                    )
                )

        return gaps

    def analyze_l2_execution(self) -> list[SemanticGap]:
        """Analyze L2 execution layer for semantic gaps."""
        logger.info("Analyzing L2 Execution Layer...")
        gaps = []

        # Check for schema validator cache usage
        validator_files = self.ast_analyzer.find_hot_paths(AGENTIC_CORE / "L2_execution", "*validator*.py")
        for validator_file in validator_files:
            if "cache" in validator_file.name:
                continue

            analysis = self.ast_analyzer.analyze_file(validator_file)
            if not analysis.ok:
                continue

            schema_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="schema_validator_cache",
                symbol_hint="SchemaValidatorCache",
            )

            if not schema_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L2-GAP-VALIDATOR", validator_file),
                        layer="L2",
                        artery="Schema Validation Hot Path",
                        intent="Cache compiled JSON schema validators to avoid repeated compilation",
                        reality=f"{validator_file.name} does not use schema_validator_cache",
                        impact="Schema validators recompiled on every validation request",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(validator_file)],
                        recommended_fix="Wrap validator compilation with schema_validator_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l3_orchestration(self) -> list[SemanticGap]:
        """Analyze L3 orchestration layer for semantic gaps."""
        logger.info("Analyzing L3 Orchestration Layer...")
        gaps = []

        # Check orchestrator_engine for plan caching
        orchestrator = AGENTIC_CORE / "L3_orchestration" / "engines" / "orchestrator_engine.py"
        if orchestrator.exists():
            analysis = self.ast_analyzer.analyze_file(orchestrator)
            if not analysis.ok:
                return gaps

            plan_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="orchestration_plan_cache",
                symbol_hint="OrchestrationPlanCache",
            )

            if not plan_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L3-GAP-001",
                        layer="L3",
                        artery="Orchestration Plan Construction",
                        intent="Cache orchestration plans to avoid repeated planning for identical requests",
                        reality="orchestrator_engine.py does not use orchestration_plan_cache",
                        impact="Orchestration plans recomputed on every request",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(orchestrator)],
                        recommended_fix="Wrap plan construction with orchestration_plan_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l4_state(self) -> list[SemanticGap]:
        """Analyze L4 state layer for semantic gaps."""
        logger.info("Analyzing L4 State Layer...")
        gaps = []

        # Check blob_storage_provider for repeated lookups
        blob_storage = AGENTIC_CORE / "L4_state" / "memory" / "blob_storage_provider.py"
        if blob_storage.exists():
            analysis = self.ast_analyzer.analyze_file(blob_storage)
            if not analysis.ok:
                return gaps
            l4_accesses = analysis.l4_state_accesses

            if len(l4_accesses) > 10:
                gaps.append(
                    SemanticGap(
                        gap_id="L4-GAP-001",
                        layer="L4",
                        artery="Blob Storage Provider",
                        intent="Minimize repeated blob lookups via caching layer",
                        reality=f"blob_storage_provider.py has {len(l4_accesses)} direct state accesses",
                        impact="Repeated blob fetches increase latency and L4 state pressure",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(blob_storage)],
                        recommended_fix="Add read-through cache layer for frequently accessed blobs",
                    )
                )

        return gaps

    def analyze_l5_safety(self) -> list[SemanticGap]:
        """Analyze L5 safety layer for semantic gaps."""
        logger.info("Analyzing L5 Safety Layer...")
        gaps = []

        # Check safety enforcement for policy cache usage
        enforcement_files = self.ast_analyzer.find_hot_paths(
            AGENTIC_CORE / "L5_safety" / "enforcement",
            PYTHON_FILE_GLOB,
        )
        for enf_file in enforcement_files:
            if "cache" in enf_file.name:
                continue

            analysis = self.ast_analyzer.analyze_file(enf_file)
            if not analysis.ok:
                continue

            policy_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="policy_registry_cache",
                symbol_hint="PolicyRegistryCache",
            )

            if not policy_cache_imported and "policy" in enf_file.name.lower():
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L5-GAP-POLICY", enf_file),
                        layer="L5",
                        artery="Safety Policy Enforcement",
                        intent="Cache immutable safety policies to avoid repeated L4 lookups",
                        reality=f"{enf_file.name} does not use policy_registry_cache",
                        impact="Safety policies fetched from L4 on every enforcement check",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(enf_file)],
                        recommended_fix="Wrap policy retrieval with policy_registry_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l6_observability(self) -> list[SemanticGap]:
        """Analyze L6 observability layer for semantic gaps."""
        logger.info("Analyzing L6 Observability Layer...")
        gaps = []

        # Check telemetry engine for config caching
        telemetry_files = self.ast_analyzer.find_hot_paths(
            AGENTIC_CORE / "L6_observability", "*telemetry*.py"
        )
        for telem_file in telemetry_files:
            analysis = self.ast_analyzer.analyze_file(telem_file)
            if not analysis.ok:
                continue

            config_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="config_file_cache",
                symbol_hint="ConfigFileCache",
            )

            if not config_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L6-GAP-CONFIG", telem_file),
                        layer="L6",
                        artery="Telemetry Configuration",
                        intent="Cache parsed telemetry config files to avoid repeated I/O",
                        reality=f"{telem_file.name} does not use config_file_cache",
                        impact="Config files re-read and re-parsed on every telemetry event",
                        priority="LOW",
                        evidence_files=[_stable_relpath(telem_file)],
                        recommended_fix="Wrap config loading with config_file_cache.get_or_fetch()",
                    )
                )

        return gaps

    def _dedupe_gaps(self, gaps: Iterable[SemanticGap]) -> list[SemanticGap]:
        """Deduplicate gaps deterministically by semantic identity."""
        deduped: dict[tuple[str, str, str], SemanticGap] = {}
        for gap in gaps:
            key = (
                gap.layer,
                gap.artery,
                tuple(sorted(gap.evidence_files))[0] if gap.evidence_files else gap.gap_id,
            )
            existing = deduped.get(key)
            if existing is None or PRIORITY_RANK.get(gap.priority, 99) < PRIORITY_RANK.get(
                existing.priority, 99
            ):
                deduped[key] = gap
        return sorted(deduped.values(), key=_priority_sort_key)

    def run_analysis(self) -> dict[str, Any]:
        """Run full semantic gap analysis across all layers."""
        logger.info("Starting Semantic Gap Analysis...")

        all_gaps = []
        all_gaps.extend(self.analyze_l0_routing_gate())
        all_gaps.extend(self.analyze_l1_cognition())
        all_gaps.extend(self.analyze_prompt_taxonomy_coverage())
        all_gaps.extend(self.analyze_l2_execution())
        all_gaps.extend(self.analyze_l3_orchestration())
        all_gaps.extend(self.analyze_l4_state())
        all_gaps.extend(self.analyze_l5_safety())
        all_gaps.extend(self.analyze_l6_observability())

        self.gaps = self._dedupe_gaps(all_gaps)
        self.parse_failures = sorted(
            self.ast_analyzer.parse_failures,
            key=lambda pf: _stable_relpath(pf.file_path).lower(),
        )

        # Categorize by priority
        high_priority = [g for g in self.gaps if g.priority == "HIGH"]
        medium_priority = [g for g in self.gaps if g.priority == "MEDIUM"]
        low_priority = [g for g in self.gaps if g.priority == "LOW"]

        logger.info("\nAnalysis Complete:")
        logger.info(f"  Total Gaps: {len(self.gaps)}")
        logger.info(f"  HIGH Priority: {len(high_priority)}")
        logger.info(f"  MEDIUM Priority: {len(medium_priority)}")
        logger.info(f"  LOW Priority: {len(low_priority)}")
        logger.info(f"  Parse Failures: {len(self.parse_failures)}")

        return {
            "total_gaps": len(self.gaps),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
            "parse_failures": self.parse_failures,
            "prompt_taxonomy_findings": self.prompt_taxonomy_findings,
            "gaps": self.gaps,
        }

    def generate_report(self, output_path: Path) -> None:
        """Generate markdown report of semantic gaps."""
        logger.info(f"Generating report: {output_path}")

        lines = []

        def h(text: str) -> None:
            lines.append(text)

        def blank() -> None:
            lines.append("")

        h("# Semantic Gap Analysis - Agentic Architecture Major Arteries")
        blank()
        h("## Executive Summary")
        blank()
        h(f"**Total Gaps Identified:** {len(self.gaps)}")
        h(f"**High Priority:** {len([g for g in self.gaps if g.priority == 'HIGH'])}")
        h(f"**Medium Priority:** {len([g for g in self.gaps if g.priority == 'MEDIUM'])}")
        h(f"**Low Priority:** {len([g for g in self.gaps if g.priority == 'LOW'])}")
        h(f"**Parse Failures:** {len(self.parse_failures)}")
        blank()
        h("## Analysis Methodology")
        blank()
        h("This analysis traces actual execution flows through L0-L6 layers using AST-based")
        h("code scanning to identify where architectural intent (lower latency, deterministic")
        h("lookups, cache-first patterns) diverges from implementation reality.")
        blank()
        h("**Approach:**")
        h("1. Map critical hot paths across each layer")
        h("2. AST scan for import statements and cache usage patterns")
        h("3. Detect prompt assemblers and score canonical slot coverage for S0/D0/I0/C0/U0")
        h("4. Check for manifest-hash and boundary-snapshot evidence on prompt execution paths")
        h("5. Identify missing wirings between cache modules and consumers")
        h("6. Categorize gaps by layer, artery, and priority")
        h("7. Surface parse failures explicitly instead of silently dropping files from analysis")
        blank()

        if self.prompt_taxonomy_findings:
            h("## Prompt Taxonomy Coverage")
            blank()
            h("| File | Slot Coverage | Manifest Hash | Boundary Snapshot |")
            h("|------|---------------|---------------|-------------------|")
            for finding in sorted(self.prompt_taxonomy_findings, key=lambda item: item["file"]):
                manifest = "yes" if finding["manifest_hash"] else "no"
                boundary = "yes" if finding["boundary_snapshot"] else "no"
                h(f"| `{finding['file']}` | {finding['slot_status']} | {manifest} | {boundary} |")
            blank()

        if self.parse_failures:
            h("## Parse Failures")
            blank()
            h("| File | Error Type | Message |")
            h("|------|------------|---------|")
            for failure in self.parse_failures:
                message = failure.message.replace("\n", " ").replace("|", "\\|")
                h(f"| `{_stable_relpath(failure.file_path)}` | {failure.error_type} | {message} |")
            blank()

        # Group gaps by layer
        layers = {}
        for gap in self.gaps:
            if gap.layer not in layers:
                layers[gap.layer] = []
            layers[gap.layer].append(gap)

        for layer in sorted(layers.keys()):
            h(f"## {layer} Layer Gaps")
            blank()

            for gap in sorted(layers[layer], key=_priority_sort_key):
                h(f"### {gap.gap_id}: {gap.artery}")
                blank()
                h(f"**Priority:** {gap.priority}")
                blank()
                h("**Architectural Intent:**")
                h(f"{gap.intent}")
                blank()
                h("**Implementation Reality:**")
                h(f"{gap.reality}")
                blank()
                h("**Impact:**")
                h(f"{gap.impact}")
                blank()
                h("**Evidence Files:")
                for ef in sorted(set(gap.evidence_files)):
                    h(f"- `{ef}`")
                blank()
                h("**Recommended Fix:**")
                h(f"{gap.recommended_fix}")
                blank()
                h("---")
                blank()

        h("## Priority Matrix")
        blank()
        h("| Layer | High | Medium | Low | Total |")
        h("|-------|------|--------|-----|-------|")
        for layer in sorted(layers.keys()):
            layer_gaps = layers[layer]
            high = len([g for g in layer_gaps if g.priority == "HIGH"])
            medium = len([g for g in layer_gaps if g.priority == "MEDIUM"])
            low = len([g for g in layer_gaps if g.priority == "LOW"])
            total = len(layer_gaps)
            h(f"| {layer} | {high} | {medium} | {low} | {total} |")
        blank()

        h("## Next Steps")
        blank()
        h("1. **High Priority Gaps:** Address immediately - these cause repeated expensive operations")
        h("2. **Medium Priority Gaps:** Schedule for next sprint - moderate latency impact")
        h("3. **Low Priority Gaps:** Backlog - minor optimizations")
        h("4. **Parse Failures:** Fix or explicitly waive broken files so analysis coverage is auditable")
        blank()
        h("## Validation")
        blank()
        h("After implementing fixes, rerun semantic gap analysis to verify:")
        h("- Cache modules are imported in hot path files")
        h("- Prompt assemblers explicitly cover S0, D0, I0, C0, and U0")
        h("- Governed prompt assembly emits a manifest hash")
        h("- Validator paths emit boundary_snapshot.json for prompt-package inspection")
        h("- `get_or_fetch` pattern is used consistently")
        h("- Replay mode tests pass with warm cache (no redundant fetches)")
        h("- Side-effect envelope tests confirm cache-first behavior")
        h("- Parse failure count is zero or intentionally documented")
        blank()

        content = "\n".join(lines)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Report written to {output_path}")


def main() -> None:
    """Main entry point."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Semantic Gap Analyzer")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "reports" / "plans" / "semantic_gap_analysis.md",
        help="Output path for the analysis report",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit non-zero if any file fails AST analysis.",
    )
    args = parser.parse_args()

    analyzer = SemanticGapAnalyzer()
    result = analyzer.run_analysis()
    analyzer.generate_report(args.output)

    if args.fail_on_parse_errors and result["parse_failures"]:
        logger.error("Parse failures detected. Failing due to --fail-on-parse-errors.")
        sys.exit(2)


if __name__ == "__main__":
    main()
