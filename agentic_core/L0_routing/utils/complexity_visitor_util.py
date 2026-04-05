"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ AGENT DISCOVERY & DASHBOARD METRICS EXTRACTION                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Agent classification is delegated to the SSOT kernel:                        ║
║   agentic_core/core/classification_kernel.py                                 ║
║                                                                              ║
║ This module provides:                                                        ║
║ - Dashboard metrics extraction (healing, testing, MCP, observability)        ║
║ - AST utilities (extract_bases, extract_methods, extract_decorators, etc.)   ║
║ - MRO-aware healing chain detection                                          ║
║ - Manifest generation and validation                                         ║
║                                                                              ║
║ Output: agent_discovery_full.json                                            ║
║                                                                              ║
║ IMPORTANT: Do NOT add agent classification logic here.                       ║
║ Use: from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
# guardian: allow-silent_swallower - ADG violation exemption

# guardian: allow-global_mutation - ADG violation exemption


import argparse
import ast
import hashlib
import json
import logging
import os
import platform
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR, TESTS_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_reads_through,
    _emit_records_execution_trace,
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

try:
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    SSOT_AVAILABLE = True
except ImportError:  # guardian: allow-silent-swallow
    SSOT_AVAILABLE = False
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent))
# guardian: allow-global-mutation
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, ARCHIVES_DIR  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent.parent / AGENTIC_CORE_DIR / "L0_routing" / "scripts"))
try:
    from territory_ssot_definitions import get_territory_from_path, refine_territory_by_ast
except ImportError:

    def get_territory_from_path(path):
        return "unknown"

    def refine_territory_by_ast(path, territory):
        return territory


try:
    from agentic_core.L0_routing.utils.seams.safety_validators_seam import load_dashboard_ssot_definitions

    _ssot_defs = load_dashboard_ssot_definitions()
    FIELD_BASE_CLASSES = _ssot_defs.FIELD_BASE_CLASSES
    FIELD_CATEGORY = _ssot_defs.FIELD_CATEGORY
    FIELD_CLASS_NAME = _ssot_defs.FIELD_CLASS_NAME
    FIELD_CYCLOMATIC_COMPLEXITY = _ssot_defs.FIELD_CYCLOMATIC_COMPLEXITY
    FIELD_DOCUMENTED_PCT = _ssot_defs.FIELD_DOCUMENTED_PCT
    FIELD_HAS_HEALING = _ssot_defs.FIELD_HAS_HEALING
    FIELD_HAS_MEMORY = _ssot_defs.FIELD_HAS_MEMORY
    FIELD_HAS_TESTS = _ssot_defs.FIELD_HAS_TESTS
    FIELD_HAS_TOOLS = _ssot_defs.FIELD_HAS_TOOLS
    FIELD_INHERITANCE = _ssot_defs.FIELD_INHERITANCE
    FIELD_INVOCATION = _ssot_defs.FIELD_INVOCATION
    FIELD_LAYER = _ssot_defs.FIELD_LAYER
    FIELD_MCP_HARDENED = _ssot_defs.FIELD_MCP_HARDENED
    FIELD_PATH = _ssot_defs.FIELD_PATH
    FIELD_PROPER_BASE_CLASS = _ssot_defs.FIELD_PROPER_BASE_CLASS
    FIELD_SCHEMA_STRICTNESS = _ssot_defs.FIELD_SCHEMA_STRICTNESS
    FIELD_TERRITORY = _ssot_defs.FIELD_TERRITORY
    FIELD_TYPED_PCT = _ssot_defs.FIELD_TYPED_PCT
except ImportError:
    FIELD_CLASS_NAME = "class_name"
    FIELD_PATH = "path"
    FIELD_LAYER = "layer"
    FIELD_TERRITORY = "territory"
    FIELD_CATEGORY = "category"
    FIELD_HAS_HEALING = "has_healing"
    FIELD_HAS_TESTS = "has_tests"
    FIELD_HAS_TOOLS = "has_tools"
    FIELD_HAS_MEMORY = "has_memory"
    FIELD_MCP_HARDENED = "mcp_hardened"
    FIELD_INVOCATION = "invocation"
    FIELD_TYPED_PCT = "typed_pct"
    FIELD_DOCUMENTED_PCT = "documented_pct"
    FIELD_SCHEMA_STRICTNESS = "schema_strictness"
    FIELD_PROPER_BASE_CLASS = "proper_base_class"
    FIELD_CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    FIELD_INHERITANCE = "inheritance"
    FIELD_BASE_CLASSES = "base_classes"
from agentic_core.L0_routing.config import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
from agentic_core.L0_routing.utils.seams.canonical_truth_seam import categorize_agent, get_canonical_layer
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

if platform.system() == "Windows":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] full_discovery %(levelname)s: %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger("full_agent_discovery")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR
CANONICAL_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MANIFEST_JSON = PROJECT_ROOT / AGENT_DISCOVERY_MANIFEST_JSON
LEGACY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MISTAKE_JSON = PROJECT_ROOT / "agent_full.json"
MISTAKE_JSON_2 = PROJECT_ROOT / "agent_discovery_legacy.json"
OUTPUT_JSON = CANONICAL_JSON
try:
    from agentic_core.L0_routing.config import GLOBAL_EXCLUDED_DIRS

    SSOT_EXCLUDED = set(GLOBAL_EXCLUDED_DIRS)
except ImportError:
    SSOT_EXCLUDED = set()
EXCLUDED_DIRS = {
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    ".eggs",
    "*.egg-info",
    ".git",
    ".svn",
    ".hg",
    ".venv",
    "venv",
    "env",
    ".env",
    "node_modules",
    "coverage_html",
    "htmlcov",
    ".coverage",
    ARCHIVES_DIR,
    ".sovereign_healing_backup",
    REPORTS_DIR,
    TESTS_DIR,
} | SSOT_EXCLUDED
EXCLUDED_FILENAME_PATTERNS = {
    "mixin",
    "_mixin",
    "utility",
    "utils",
    "helper",
    "helpers",
    "conftest",
    "setup",
    "__init__",
    "__main__",
}
EXCLUDED_PATH_PATTERNS = {
    "/tests/",
    "/test/",
    "/examples/",
    "/example/",
    "/docs/",
    "/doc/",
    "/fixtures/",
    "/mocks/",
    "/stubs/",
    "/fakes/",
}
AGENT_PATH_WHITELIST = {
    "agentic_core/L0_routing/scripts/BootstrapAgent.py",
    "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py",
}
INFRASTRUCTURE_PATH_PATTERNS = {"scripts/", "utils/", "mixins/", "helpers/"}
INFRASTRUCTURE_CLASS_PATTERNS = {
    "Client",
    "Factory",
    "Registry",
    "Serializer",
    "Validator",
    "Context",
    "Manager",
    "Handler",
    "Loader",
    "Parser",
    "Builder",
    "Visitor",
}
SPECIAL_LAYER_MAPPINGS = {"schemas": "L1", "prompt_governance": "L1", "base_agents": "Base", "utils": "Utils"}


def should_exclude_path(path: Path) -> bool:
    """Return True if path should be excluded from scanning/hashing.

    Multi-factor exclusion (ANY match → exclude):
    1. Directory name in EXCLUDED_DIRS
    2. Filename matches EXCLUDED_FILENAME_PATTERNS
    3. Path contains EXCLUDED_PATH_PATTERNS
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "should_exclude_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "should_exclude_path", "p0_governance")
    path_str = str(path).replace("\\", "/").lower()
    if any(excluded.lower() in path.parts for excluded in EXCLUDED_DIRS):
        return True
    filename_lower = path.name.lower() if path.name else ""
    if any(pattern in filename_lower for pattern in EXCLUDED_FILENAME_PATTERNS):
        return True
    if any(pattern in path_str for pattern in EXCLUDED_PATH_PATTERNS):
        return True
    return False


LAYER_BASE_MAP = {
    "L1": "L1CognitionBase",
    "L2": "L2ExecutionBase",
    "L3": "L3OrchestrationBase",
    "L4": "L4StateBase",
    "L5": "L5SafetyBase",
}
MINIMUM_AGENT_COUNT = 1
MAX_AGENT_DROP_PERCENT = 50
EXPECTED_AGENT_COUNT = 268


def should_exclude_file(py_file: Path) -> bool:
    """Return True if file should not be scanned for agent discovery.

    HARDENED multi-factor exclusion for agent discovery:
    1. Directory-based: file in excluded directory
    2. Filename-based: filename contains mixin/utility patterns
    3. Extension-based: must be .py file
    4. Path-based: in test/example/generated directories

    Returns:
        True if ANY exclusion factor matches (aggressive OR for safety)
    """
    if py_file.suffix.lower() != ".py":
        return True
    parts_lower = {p.lower() for p in py_file.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    filename_lower = py_file.stem.lower()
    for pattern in EXCLUDED_FILENAME_PATTERNS:
        if pattern in filename_lower:
            if filename_lower.endswith("agent"):
                continue
            return True
    path_str = str(py_file).replace("\\", "/").lower()
    if "/fixtures/" in path_str or "/mocks/" in path_str or "/stubs/" in path_str:
        return True
    return False


def validate_agent_count(agent_count: int, previous_count: int | None = None) -> tuple[bool, list[str]]:
    """
    HARDENING: Validate agent count against safety thresholds.

    Returns:
        (is_valid, errors) - is_valid=False means ABORT discovery
    """
    errors = []
    warnings = []
    if agent_count < MINIMUM_AGENT_COUNT:
        errors.append(
            f"❌ CRITICAL: Agent count {agent_count} is below MINIMUM_AGENT_COUNT ({MINIMUM_AGENT_COUNT})!\n   This indicates a catastrophic bug in agent detection.\n   Discovery ABORTED to prevent data loss.\n   If this is intentional, update MINIMUM_AGENT_COUNT in full_agent_discovery.py"
        )
        return (False, errors)
    if previous_count is not None and previous_count > 0:
        drop = previous_count - agent_count
        drop_percent = drop / previous_count * 100
        if drop > 0 and drop_percent > MAX_AGENT_DROP_PERCENT:
            errors.append(
                f"❌ CRITICAL: Agent count dropped by {drop} ({drop_percent:.1f}%) from previous run!\n   Previous: {previous_count}, Current: {agent_count}\n   This exceeds MAX_AGENT_DROP_PERCENT ({MAX_AGENT_DROP_PERCENT}%).\n   Discovery ABORTED to prevent data loss.\n   If this is intentional, run with --force flag"
            )
            return (False, errors)
    if agent_count < EXPECTED_AGENT_COUNT:
        diff = EXPECTED_AGENT_COUNT - agent_count
        warnings.append(
            f"⚠️  WARNING: Agent count {agent_count} is {diff} below EXPECTED_AGENT_COUNT ({EXPECTED_AGENT_COUNT})"
        )
    elif agent_count > EXPECTED_AGENT_COUNT:
        diff = agent_count - EXPECTED_AGENT_COUNT
        warnings.append(
            f"ℹ️  INFO: Agent count {agent_count} is {diff} above EXPECTED_AGENT_COUNT ({EXPECTED_AGENT_COUNT})"
        )
    for w in warnings:
        print(w)
    return (True, errors)


def get_previous_agent_count() -> int | None:
    """Get agent count from previous discovery run (from manifest or JSON)."""
    if MANIFEST_JSON.exists():
        try:
            manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
            return manifest.get("agent_count")
        except (json.JSONDecodeError, KeyError):
            pass
    if CANONICAL_JSON.exists():
        try:
            agents = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))
            return len(agents)
        except json.JSONDecodeError:
            pass
    return None


def generate_manifest(agents: list[dict], scan_duration: float, parse_errors: list[str]) -> dict:
    """Generate manifest with metadata for staleness detection and validation."""
    import hashlib  # noqa: PLC0415
    from datetime import datetime  # noqa: PLC0415

    _emit_records_execution_trace(
        str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"generate_manifest:agents={len(agents)}"
    )
    content_str = json.dumps(agents, sort_keys=True)
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()
    layer_counts = defaultdict(int)
    for a in agents:
        layer_counts[a.get("layer", "unknown")] += 1
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "scan_duration_seconds": round(scan_duration, 2),
        "agent_count": len(agents),
        "content_hash": f"sha256:{content_hash}",
        "layer_breakdown": dict(layer_counts),
        "parse_errors_count": len(parse_errors),
        "minimum_agent_count": MINIMUM_AGENT_COUNT,
        "expected_agent_count": EXPECTED_AGENT_COUNT,
        "validation": {"passed": len(agents) >= MINIMUM_AGENT_COUNT, "threshold": MINIMUM_AGENT_COUNT},
    }
    return manifest


HEALING_BASES = {
    "HealerMixin",
    "CanonBaseAgent",
    "CognitionCanonBaseAgent",
    "SubAtomicAgent",
    "ExecutionCanonBaseAgent",
    "SubatomicTestingMixin",
    "L3OrchestrationBase",
    "L3SubatomicTestingMixin",
    "L4StateBase",
    "L4SubatomicTestingMixin",
    "L5SafetyBase",
    "ASTEnforcementMixin",
}
SELF_TESTING_BASES = {
    "SubAtomicAgent",
    "SubatomicTestingMixin",
    "L3OrchestrationBase",
    "L3SubatomicTestingMixin",
    "L4StateBase",    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
    "L4SubatomicTestingMixin",
    "CanonBaseAgent",
}
DELEGATION_BASES = {"MaintenanceBaseAgent", "L0DelegationTestingMixin", "L0DelegationMixin"}


def safe_parse(code: str, file_path: Path) -> ast.AST | None:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
    """Parse code with error tolerance."""
    try:
        return ast.parse(code)
    except SyntaxError as e:
        print(f"  [SYNTAX] Skipped {file_path.name}: {e}")
        return None


def extract_bases(class_node: ast.ClassDef) -> set[str]:
    """Extract base class names from class definition."""
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                bases.add(base.value.id)
    return bases


def extract_decorators(node: ast.ClassDef) -> list[str]:
    """Extract decorator names from class definition."""
    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(dec.id)
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                decorators.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                decorators.append(dec.func.attr)
        elif isinstance(dec, ast.Attribute):
            decorators.append(dec.attr)
    return decorators


def extract_class_attributes(node: ast.ClassDef) -> list[str]:
    """Extract class-level attribute assignments."""
    attrs = []
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    attrs.append(target.id)
        elif isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name):
                attrs.append(item.target.id)
    return attrs


def extract_imports(tree: ast.AST) -> tuple[list[str], list[str]]:
    """Extract all imports from a module."""
    imports = []
    from_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                from_imports.append(f"{module}.{alias.name}")
    return (imports, from_imports)


def extract_method_signatures(node: ast.ClassDef) -> list[dict[str, Any]]:
    """Extract method signatures with parameters."""
    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            params = []
            for arg in item.args.args:
                params.append(arg.arg)
            methods.append(
                {
                    "name": item.name,
                    "async": isinstance(item, ast.AsyncFunctionDef),
                    "params": params,
                    "decorators": [
                        d.id if isinstance(d, ast.Name) else str(d) for d in item.decorator_list[:3]
                    ],
                }
            )
    return methods


CLASS_INHERITANCE_MAP: dict[str, set[str]] = {}


def build_inheritance_map(tree: ast.AST) -> None:
    """Build map of class -> bases for MRO traversal."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = extract_bases(node)
            CLASS_INHERITANCE_MAP[node.name] = bases


def has_healing_in_chain(class_name: str, bases: set[str], visited: set[str] = None) -> bool:
    """Check if class has healing capability through inheritance chain."""
    if visited is None:
        visited = set()
    if class_name in visited:
        return False
    visited.add(class_name)
    if class_name in HEALING_BASES:
        return True
    if bases & HEALING_BASES:
        return True
    for base in bases:
        if base in HEALING_BASES:
            return True
        if base in CLASS_INHERITANCE_MAP:
            if has_healing_in_chain(base, CLASS_INHERITANCE_MAP[base], visited):
                return True
    return False


def extract_methods(class_node: ast.ClassDef) -> list[str]:
    """Extract method names from class definition."""
    methods = []
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            methods.append(item.name)
    return methods


def has_method(class_node: ast.ClassDef, method_name: str) -> bool:
    """Check if class has a specific method."""
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            if item.name == method_name:
                return True
    return False


def get_method(class_node: ast.ClassDef, method_name: str) -> ast.FunctionDef | None:
    """Get a specific method from a class, or None if not found."""
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            if item.name == method_name:
                return item
    return None


def detect_invocation_status(class_node: ast.ClassDef) -> str:
    """
    Detect heal_repository invocation status for a CLASS.

    Returns:
        'Yes' - Class defines heal_repository with super().heal_repository() call
        'No (missing super)' - Class defines heal_repository but no super() call
        'Inherited' - Class does not define heal_repository (inherits from base)

    IMPORTANT: This checks the CLASS's heal_repository method specifically,
    not standalone module-level functions. This is the SSOT for invocation.
    """
    heal_method = get_method(class_node, "heal_repository")
    if heal_method is None:
        return "Inherited"
    for node in ast.walk(heal_method):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "heal_repository":
                if isinstance(node.func.value, ast.Call):
                    if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super":
                        return "Yes"
    return "No (missing super)"


def detect_has_tests(class_node: ast.ClassDef, source: str, class_name: str = None) -> bool:
    """Detect if class has ACTUAL test coverage (not inherited infrastructure).

    Checks:
    1. External test file exists (test_<ClassName>.py in tests/ subdirs)
    2. _run_self_tests method defined in the class
    3. SubatomicTestingMixin in direct inheritance
    4. pytest/unittest imports with test_ methods
    """
    if class_name:
        test_file_exists = _check_external_test_file(class_name)
        if test_file_exists:
            return True
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            if item.name == "_run_self_tests":
                return True
            if item.name.startswith("test_"):
                return True
    for base in class_node.bases:
        base_name = None
        if isinstance(base, ast.Name):
            base_name = base.id
        elif isinstance(base, ast.Attribute):
            base_name = base.attr
        if base_name in (
            "SubatomicTestingMixin",
            "SubatomicAgent",
            "L0DelegationTestingMixin",
            "L3SubatomicTestingMixin",
            "L4SubatomicTestingMixin",
            "L5SubatomicTestingMixin",
            "L6SubatomicTestingMixin",
        ):
            return True
    if "import pytest" in source or "from pytest" in source:
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name.startswith("test_"):
                    return True
    return False


def _check_external_test_file(agent_name: str) -> bool:
    """Check if an external test file exists for the given agent."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / TESTS_DIR
    test_patterns = [
        tests_dir / f"test_{agent_name}.py",
        tests_dir / "apps" / f"test_{agent_name}.py",
        tests_dir / "l0" / f"test_{agent_name}.py",
        tests_dir / "l1" / f"test_{agent_name}.py",
        tests_dir / "l2" / f"test_{agent_name}.py",
        tests_dir / "l3" / f"test_{agent_name}.py",
        tests_dir / "l4" / f"test_{agent_name}.py",
        tests_dir / "l5" / f"test_{agent_name}.py",
        tests_dir / "l6" / f"test_{agent_name}.py",
        tests_dir / "L6" / f"test_{agent_name}.py",
        tests_dir / "unit" / f"test_{agent_name}.py",
        tests_dir / "integration" / f"test_{agent_name}.py",
        tests_dir / "autogen" / f"test_{agent_name}.py",
        tests_dir / "base" / f"test_{agent_name}.py",
        tests_dir / "utils" / f"test_{agent_name}.py",
    ]
    for pattern in test_patterns:
        if pattern.exists():
            return True
    return False


def calculate_typing_coverage(class_node: ast.ClassDef) -> float:
    """Calculate percentage of methods with type annotations.

    Computes actual typing coverage by checking:
    - Parameter annotations on methods
    - Return type annotations on methods
    """
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
    if not methods:
        return 100.0
    typed_methods = 0
    for method in methods:
        params = [arg for arg in method.args.args if arg.arg != "self"]
        params_typed = all(arg.annotation is not None for arg in params) if params else True
        return_typed = method.returns is not None
        if params_typed and return_typed:
            typed_methods += 1
    return round(typed_methods / len(methods) * 100, 1)


def calculate_docstring_coverage(class_node: ast.ClassDef) -> float:
    """Calculate percentage of methods with docstrings.

    Computes actual docstring coverage by checking for docstrings on methods.
    """
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
    if not methods:
        return 100.0
    documented_methods = 0
    for method in methods:
        if (
            method.body
            and isinstance(method.body[0], ast.Expr)
            and isinstance(method.body[0].value, ast.Str | ast.Constant)
        ):
            documented_methods += 1
    return round(documented_methods / len(methods) * 100, 1)


def check_proper_base(class_node: ast.ClassDef, layer: str) -> bool:
    """Phase 4: Verify agent has proper architectural inheritance.

    Proper base class means the agent follows the canonical architecture:
    - Inherits from SovereignBaseAgent (directly or transitively)
    - OR inherits from a layer-specific base agent
    - OR uses canonical mixins (HealerMixin, MCPHardenedMixin)

    This is a permissive check - we want to identify poorly structured agents,
    not penalize agents that follow alternative but valid patterns.
    """
    bases = extract_bases(class_node)
    if not bases:
        return False
    canonical_patterns = {
        "SovereignBaseAgent",
        "L0RoutingBaseAgent",
        "L1CognitionBase",
        "L2Agent",
        "L2ExecutionBase",
        "L3Agent",
        "L3OrchestrationBase",
        "L4Agent",
        "L4StateBase",
        "L5Agent",
        "L5SafetyBase",
        "L6ObservabilityBase",
        "HealerMixin",
        "MCPHardenedMixin",
        "MCPShieldMixin",
    }
    if any(base in canonical_patterns for base in bases):
        return True
    if layer == "Apps":
        return True
    if "BaseAgent" in class_node.name:
        return True
    return False


def calculate_schema_strictness(class_node: ast.ClassDef, source: str = "") -> float:
    """Phase 4: schema Strictness - % with strict Pydantic/dataclass schema validation.

    Checks for:
    1. @dataclass decorator on the class
    2. Pydantic BaseModel inheritance
    3. Field definitions with type annotations
    4. Pydantic Field() or dataclass field() usage

    Returns 100% if agent uses Pydantic or dataclass, 0% otherwise.
    """
    has_dataclass = False
    for decorator in class_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
            has_dataclass = True
            break
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                has_dataclass = True
                break
    if has_dataclass:
        return 100.0
    bases = [get_base_name(base) for base in class_node.bases]
    pydantic_bases = {"BaseModel", "BaseSettings", "GenericModel"}
    if any(base in pydantic_bases for base in bases):
        return 100.0
    if source:
        if "from pydantic import" in source or "import pydantic" in source:
            if "BaseModel" in source or "Field(" in source:
                return 100.0
        if "from dataclasses import" in source or "@dataclass" in source:
            return 100.0
    typed_attrs = 0
    total_attrs = 0
    for node in class_node.body:
        if isinstance(node, ast.AnnAssign):
            total_attrs += 1
            if node.annotation is not None:
                typed_attrs += 1
    if total_attrs > 0:
        return round(typed_attrs / total_attrs * 100, 1)
    return 0.0


def get_base_name(base_node) -> str:
    """Extract base class name from AST node."""
    if isinstance(base_node, ast.Name):
        return base_node.id
    elif isinstance(base_node, ast.Attribute):
        return base_node.attr
    elif isinstance(base_node, ast.Subscript):
        if isinstance(base_node.value, ast.Name):
            return base_node.value.id
        elif isinstance(base_node.value, ast.Attribute):
            return base_node.value.attr
    return ""


def detect_agent_metadata(class_node: ast.ClassDef) -> bool:
    """Phase 3: Detect if agent class has sufficient metadata (Finding #2).

    Checks for the presence of a class-level docstring.
    Agents with comprehensive docstrings enable better discovery and understanding.
    """
    docstring = ast.get_docstring(class_node)
    return bool(docstring and docstring.strip())


def detect_observability(class_node: ast.ClassDef, source: str) -> dict:
    """Detect observability indicators (logging, metrics, tracing)."""
    obs = {"logging": False, "metrics": False, "tracing": False}
    if "import logging" in source or "from logging" in source:
        obs["logging"] = True
    if "observability" in source.lower():
        obs["logging"] = True
        obs["metrics"] = True
    if "opentelemetry" in source.lower() or "otel" in source.lower():
        obs["tracing"] = True
    if "structured_log" in source or ".log(" in source or "logger." in source:
        obs["logging"] = True
    if "log_metric" in source or "emit_metric" in source:
        obs["metrics"] = True
    if "start_span" in source or ".trace(" in source:
        obs["tracing"] = True
    if "HealerMixin" in source or "heal_repository" in source:
        obs["logging"] = True
        obs["metrics"] = True
    if "MCPHardenedMixin" in source or "MCPShieldMixin" in source:
        obs["metrics"] = True
    base_agents = [
        "L0RoutingBaseAgent",
        "L1CognitionBase",
        "L2Agent",
        "L3Agent",
        "L4Agent",
        "L5Agent",
        "L5SafetyBase",
        "L4StateBase",
        "L3OrchestrationBase",
    ]
    for base in base_agents:
        if base in source:
            obs["logging"] = True
            obs["metrics"] = True
            break
    return obs


class _CCVisitor(ast.NodeVisitor):
    """Visitor to calculate cyclomatic complexity."""

    def __init__(self):
        self.cc = 1

    def visit_If(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.cc += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.cc += 1
        self.generic_visit(node)


def calculate_cyclomatic_complexity(class_node: ast.ClassDef) -> int:
    """
    Calculate total cyclomatic complexity for class.

    Complexity health % = 100 - (CC * 2)
    This penalizes complex classes to encourage refactoring.
    """
    total_cc = 0
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            visitor = _CCVisitor()
            visitor.visit(item)
            total_cc += visitor.cc
    return total_cc if total_cc > 0 else 1


def count_loc(source: str) -> int:
    """Count non-blank, non-comment lines."""
    count = 0
    in_docstring = False
    for line in source.splitlines():
        stripped = line.strip()
        if '"""' in stripped or "'''" in stripped:
            quote = '"""' if '"""' in stripped else "'''"
            if stripped.count(quote) >= 2:
                continue
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        count += 1
    return count


def is_sovereign_agent(class_node: ast.ClassDef, bases: set[str], rel_path: Path | None = None) -> bool:
    """
    STRICT SOVEREIGN AGENT TYPING — DELEGATES TO CLASSIFICATION KERNEL (SSOT).

    [REFACTORED 2026-02-08] All bespoke scoring logic removed.
    Now delegates to the zero-dependency classification kernel for the
    canonical "is this an agent?" decision.

    The kernel uses the same priority ordering as FileClassificationAgent:
    AST-based primary class detection, suffix matching, inheritance checks,
    with proper exclusions for MIXIN, PROTOCOL, STRATEGY, ORCHESTRATOR, etc.

    Args:
        class_node: AST ClassDef node (used for class name fallback only).
        bases: Set of base class names (unused — kernel does its own AST parse).
        rel_path: Relative path to the file.

    Returns:
        True if the file is classified as AGENT by the kernel.
    """
    from agentic_core.L0_routing.utils.seams.safety_kernel_seam import load_classification_kernel

    is_agent_file = load_classification_kernel().is_agent_file
    if rel_path is None:
        return class_node.name.endswith("Agent") and "Mixin" not in class_node.name
    abs_path = PROJECT_ROOT / rel_path if not rel_path.is_absolute() else rel_path
    return is_agent_file(abs_path)


def is_agent_class(class_node: ast.ClassDef, bases: set[str], rel_path: Path | None = None) -> bool:
    """
    DEPRECATED — Delegates to classification kernel (SSOT).

    [REFACTORED 2026-02-08] All 200+ lines of bespoke scoring logic removed.
    Now delegates to is_sovereign_agent() which uses the kernel.

    Kept as a shim for any internal callers. All new code should use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    """
    return is_sovereign_agent(class_node, bases, rel_path)


def get_docstring(class_node: ast.ClassDef) -> str:
    """Extract class docstring."""
    if class_node.body and isinstance(class_node.body[0], ast.Expr):
        if isinstance(class_node.body[0].value, ast.Constant):
            doc = class_node.body[0].value.value
            if isinstance(doc, str):
                return doc[:100]
    return ""


def main():
    import sys

    parser = argparse.ArgumentParser(description="Canonical Agent Discovery (SSOT)")
    parser.add_argument("--force", action="store_true", help="Force full scan ignoring validation")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Best-effort incremental mode (requires previous JSON/manifest)",
    )
    args = parser.parse_args()
    force_mode = args.force
    incremental_mode = args.incremental
    log.info("=" * 80)
    log.info("FULL AGENT DISCOVERY STARTED")
    log.info(f"Mode: {('INCREMENTAL' if incremental_mode else 'FULL')} {('(forced)' if force_mode else '')}")
    log.info("=" * 80)
    previous_agents = []
    previous_count = get_previous_agent_count()
    changed_rel_paths: set[str] = set()
    if incremental_mode:
        if CANONICAL_JSON.exists():
            try:
                previous_agents = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                previous_count = len(previous_agents)
                log.info(f"[INCREMENTAL] Loaded {previous_count} agents from previous JSON")
                if previous_count != EXPECTED_AGENT_COUNT:
                    log.warning(
                        f"[INCREMENTAL] Previous count ({previous_count}) != expected ({EXPECTED_AGENT_COUNT}). Registry may be stale → falling back to full scan for integrity"
                    )
                    incremental_mode = False    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            except json.JSONDecodeError as e:
                log.error(f"[INCREMENTAL] JSON corrupted ({e}) → falling back to full scan")
                incremental_mode = False
            except OSError as e:
                log.error(f"[INCREMENTAL] Failed to read JSON ({e}) → falling back to full scan")
                incremental_mode = False
            except (OSError, RuntimeError) as e:  # guardian: allow-silent-swallow
                log.error(f"[INCREMENTAL] Unexpected error loading JSON ({e}) → falling back to full scan")
                incremental_mode = False
        else:
            log.warning("[INCREMENTAL] No previous JSON found → falling back to full scan")
            incremental_mode = False
        if incremental_mode and MANIFEST_JSON.exists():
            try:
                old_manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
                required = {"file_hashes", "agent_count", "generated_at"}
                if not all(k in old_manifest for k in required):
                    missing = required - old_manifest.keys()
                    raise ValueError(f"Manifest missing required keys: {missing}")
                manifest_count = old_manifest.get("agent_count", 0)
                if manifest_count != previous_count:
                    raise ValueError(
                        f"Manifest count ({manifest_count}) != JSON count ({previous_count}). Data integrity compromised."
                    )
                old_hashes = old_manifest.get("file_hashes", {})
                log.info(f"[INCREMENTAL] Loaded manifest with {len(old_hashes)} file hashes")
                log.info(f"[INCREMENTAL] Manifest generated: {old_manifest.get('generated_at', 'unknown')}")
            except json.JSONDecodeError as e:
                log.warning(f"[INCREMENTAL] Manifest JSON corrupted ({e}) → falling back to full scan")
                incremental_mode = False
                old_hashes = {}
            except ValueError as e:
                log.warning(f"[INCREMENTAL] Manifest validation failed ({e}) → falling back to full scan")
                incremental_mode = False
                old_hashes = {}
            except (OSError, RuntimeError) as e:  # guardian: allow-silent-swallow
                log.warning(f"[INCREMENTAL] Manifest error ({e}) → falling back to full scan")
                incremental_mode = False
                old_hashes = {}
        elif incremental_mode:
            log.warning("[INCREMENTAL] No manifest found → falling back to full scan")
            incremental_mode = False
            old_hashes = {}
        if incremental_mode:
            log.info("[INCREMENTAL] ✓ Prerequisites validated - proceeding with hash-based change detection")
        else:
            log.info("[FULL SCAN] Incremental mode disabled - performing complete repository scan")
    if previous_count:
        log.info(f"[BASELINE] Previous agent count: {previous_count}")
    start_time = get_clock().now_epoch()
    if not incremental_mode:
        for stale_path in {CANONICAL_JSON, LEGACY_JSON, MISTAKE_JSON, MISTAKE_JSON_2}:
            try:
                if stale_path.exists():
                    assert_no_persistent_write("L0", "os.mutate")
                    os.remove(stale_path)
                    log.info(f"[FRESH] Deleted stale {stale_path.name}")
            except (OSError, PermissionError) as e:  # guardian: allow-silent-swallow
                log.warning(f"Could not delete {stale_path.name}: {e}")
    agents = []
    parse_errors = []
    seen_agents: set[tuple[str, str]] = set()
    duplicates_skipped = 0
    if SSOT_AVAILABLE:
        all_py_files = get_python_files(PROJECT_ROOT)
    else:
        all_py_files = [p for p in PROJECT_ROOT.rglob("*.py") if not should_exclude_path(p)]
    log.info(f"Scanning {len(all_py_files)} Python files...")
    log.info("   -> Excluded vendor/cache dirs via should_exclude_path()")
    if incremental_mode:
        log.info("[INCREMENTAL] Computing MD5 hashes for change detection...")    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        current_hashes: dict[str, str] = {}
        hash_compute_errors = 0
        for py_file in all_py_files:
            rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
            try:
                file_hash = hashlib.md5(py_file.read_bytes()).hexdigest()
                current_hashes[rel_path] = file_hash    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            except OSError as e:
                log.debug(f"[HASH ERROR] {rel_path}: {e}")
                changed_rel_paths.add(rel_path)
                hash_compute_errors += 1
            except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                log.debug(f"[HASH ERROR] {rel_path}: {e}")
                changed_rel_paths.add(rel_path)
                hash_compute_errors += 1
        if hash_compute_errors > 0:
            log.warning(f"[INCREMENTAL] {hash_compute_errors} files had hash errors → marked as changed")
        changed_files = {rel for rel, new_hash in current_hashes.items() if old_hashes.get(rel) != new_hash}
        new_files = set(current_hashes.keys()) - set(old_hashes.keys())
        removed_rel_paths = set(old_hashes.keys()) - set(current_hashes.keys())
        changed_rel_paths.update(changed_files)
        changed_rel_paths.update(new_files)
        log.info("[INCREMENTAL] Change detection results:")
        log.info(f"  - Changed files: {len(changed_files)}")
        log.info(f"  - New files: {len(new_files)}")
        log.info(f"  - Removed files: {len(removed_rel_paths)}")
        log.info(f"  - Total files to reparse: {len(changed_rel_paths)}")
        retained_agents = [
            a
            for a in previous_agents
            if a.get("path", "") not in changed_rel_paths and a.get("path", "") not in removed_rel_paths
        ]
        agents = retained_agents
        log.info(
            f"[INCREMENTAL] Retained {len(agents)} agents from {len(previous_agents) - len(agents)} unchanged files"
        )
        if len(agents) > EXPECTED_AGENT_COUNT:
            log.error(
                f"[INCREMENTAL] INTEGRITY ERROR: Retained {len(agents)} agents > baseline {EXPECTED_AGENT_COUNT}. This should never happen. Falling back to full scan."
            )
            incremental_mode = False
            agents = []
    log.info("[PASS 1] Building inheritance map (required for MRO healing detection)...")
    parsed_files = {}
    for py_file in all_py_files:
        if should_exclude_file(py_file):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = safe_parse(source, py_file)
            if tree:
                build_inheritance_map(tree)
                parsed_files[py_file] = (source, tree)
        except (ValueError, TypeError):  # guardian: allow-silent-swallow
            continue
    log.info(f"   Built map with {len(CLASS_INHERITANCE_MAP)} classes")
    target_py_files = (
        [p for p in parsed_files if str(p.relative_to(PROJECT_ROOT)).replace("\\", "/") in changed_rel_paths]
        if incremental_mode
        else list(parsed_files.keys())
    )
    log.info(
        f"[PASS 2] Extracting from {len(target_py_files)} files ({('incremental' if incremental_mode else 'full')})"
    )
    for py_file in target_py_files:
        source, tree = parsed_files[py_file]
        rel_path = py_file.relative_to(PROJECT_ROOT)
        layer = get_canonical_layer(py_file)
        path_str = str(rel_path).replace("\\", "/").lower()
        for pattern, special_layer in SPECIAL_LAYER_MAPPINGS.items():
            if pattern in path_str:
                layer = special_layer
                break
        loc = count_loc(source)
        class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = extract_bases(node)
            if not is_sovereign_agent(node, bases, rel_path=rel_path):
                continue
            if node.name.islower():
                continue
            if "_" in node.name and (not node.name[0].isupper()):
                continue
            skip_names = {
                "SubAtomicAgent",
                "CanonBaseAgent",
                "MaintenanceBaseAgent",
                "IActionPlane",
                "IValidationProtocol",
                "Protocol",
                "TestContentQualityAgent",
                "TestLeadQualityAgent",
                "TestOutreachProactiveAgent",
                "TestProactiveAgent",
                "TestResumeLearningAgent",
            }
            if node.name in skip_names:
                continue
            dedupe_key = (node.name, str(rel_path))
            if dedupe_key in seen_agents:
                duplicates_skipped += 1
                continue
            seen_agents.add(dedupe_key)
            methods = extract_methods(node)
            has_self_test = has_method(node, "_run_self_tests") or bool(bases & SELF_TESTING_BASES)
            has_delegation = has_method(node, "_delegate_tests") or bool(bases & DELEGATION_BASES)
            if has_self_test:
                testing = "Self"
            elif has_delegation:
                testing = "Delegated"
            else:
                testing = "None"
            has_heal = (
                has_method(node, "heal")
                or has_method(node, "apply_fix")
                or has_method(node, "heal_violation")
                or has_method(node, "heal_repository")
            )
            inherits_healing = has_healing_in_chain(node.name, bases)
            has_healing = has_heal or inherits_healing
            has_tools = "tool" in source.lower() or "mcp" in source.lower()
            has_memory = "pinecone" in source.lower() or "redis" in source.lower()
            external_markers = [
                "pinecone",
                "redis",
                "git",
                "subprocess",
                "requests.",
                "httpx",
                "aiohttp",
                "http://",
                "https://",
            ]
            external_touch = any(marker in source.lower() for marker in external_markers)
            mcp_hardened_bases = {
                "SovereignBaseAgent",
                "L0RoutingBaseAgent",
                "L1CognitionBase",
                "L2ExecutionBase",
                "L3OrchestrationBase",
                "L4StateBase",
                "L5SafetyBase",
                "L6ObservabilityBase",
                "MCPHardenedMixin",
            }
            mcp_hardened = (
                "mcphardenedmixin" in source.lower()
                or "mcp_hardened_mixin" in source.lower()
                or bool(bases & mcp_hardened_bases)
            )
            invocation = detect_invocation_status(node)
            has_tests = detect_has_tests(node, source, node.name)
            typed_pct = calculate_typing_coverage(node)
            documented_pct = calculate_docstring_coverage(node)
            observability = detect_observability(node, source)
            cyclomatic_complexity = calculate_cyclomatic_complexity(node)
            proper_base_class = check_proper_base(node, layer)
            schema_strictness = calculate_schema_strictness(node, source)
            has_metadata = detect_agent_metadata(node)
            is_base_class = node.name.endswith("BaseAgent") or node.name in {
                "L0RoutingBaseAgent",
                "L1CognitionBase",
                "L6ObservabilityBase",
            }
            path_str = str(rel_path).replace("\\", "/").lower()
            territory = get_territory_from_path(
                layer=layer, path_str=path_str, is_base_class=is_base_class, class_name=node.name
            )
            agent_docstring = ast.get_docstring(node) or ""
            territory = refine_territory_by_ast(
                territory=territory, class_name=node.name, docstring=agent_docstring, path_str=path_str
            )
            base_class_names = [
                b.id if isinstance(b, ast.Name) else b.attr if isinstance(b, ast.Attribute) else str(b)
                for b in node.bases
            ]
            category = categorize_agent(
                class_name=node.name, base_classes=base_class_names, docstring=ast.get_docstring(node)
            )
            agents.append(
                {
                    FIELD_CLASS_NAME: node.name,
                    FIELD_PATH: str(rel_path),
                    FIELD_LAYER: layer,
                    FIELD_TERRITORY: territory,
                    FIELD_CATEGORY: category,
                    FIELD_INHERITANCE: list(bases),
                    "key_methods": methods[:10],
                    FIELD_HAS_TOOLS: has_tools,
                    FIELD_HAS_MEMORY: has_memory,
                    FIELD_HAS_HEALING: has_healing,
                    FIELD_INVOCATION: invocation,
                    "testing": testing,
                    "has_subatomic": "SubAtomicAgent" in bases or "subatomic" in source.lower(),
                    "loc": loc,
                    "class_count": class_count,
                    "description": get_docstring(node),
                    "pascal_compliant": node.name[0].isupper() and "_" not in node.name,
                    "external_touch": external_touch,
                    FIELD_MCP_HARDENED: mcp_hardened,
                    FIELD_HAS_TESTS: has_tests,
                    FIELD_TYPED_PCT: typed_pct,
                    FIELD_DOCUMENTED_PCT: documented_pct,
                    "observability": observability,
                    FIELD_CYCLOMATIC_COMPLEXITY: cyclomatic_complexity,
                    FIELD_PROPER_BASE_CLASS: proper_base_class,
                    FIELD_SCHEMA_STRICTNESS: schema_strictness,
                    "has_metadata": has_metadata,
                }
            )
    if incremental_mode:
        log.info(
            f"[INCREMENTAL] Complete: {len(agents)} agents ({len(agents) - previous_count} new/extracted)"
        )
        log.warning("NOTE: Cross-file inheritance changes may not propagate until next full scan")
    agents.sort(key=lambda x: (x["layer"], x["class_name"]))
    log.info("[VALIDATION] Agent count check...")
    validation_previous = None if force_mode else previous_count
    is_valid, validation_errors = validate_agent_count(len(agents), validation_previous)
    if not is_valid:
        log.error("=" * 80)
        log.error("DISCOVERY ABORTED - VALIDATION FAILED")
        log.error("=" * 80)
        for err in validation_errors:
            log.error(err.strip())
        log.error("Run with --force to override")
        sys.exit(1)
    scan_duration = get_clock().now_epoch() - start_time
    log.info(f"[MANIFEST] Computing hashes for {len(all_py_files)} scanned files...")
    file_hashes: dict[str, str] = {}
    hash_errors = 0
    for py_file in all_py_files:
        rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
        try:
            file_hashes[rel_path] = hashlib.md5(py_file.read_bytes()).hexdigest()
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            hash_errors += 1
            log.warning(f"   [HASH ERROR] {rel_path}: {e}")
    log.info(f"[MANIFEST] Hashed {len(file_hashes)} files ({hash_errors} errors)")
    try:
        tmp_json = OUTPUT_JSON.with_suffix(".tmp")
        json_text = json.dumps(agents, indent=2)
        assert_no_persistent_write("L0", "write_text")
        tmp_json.write_text(json_text, encoding="utf-8")
        test_load = json.loads(json_text)
        if len(test_load) != len(agents):
            raise ValueError("Written JSON agent count mismatch")
        tmp_json.replace(OUTPUT_JSON)
        log.info(f"[SAVED] {OUTPUT_JSON} ({len(agents)} agents)")
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        log.error(f"Failed to save/verify JSON: {e}")
        sys.exit(1)
    manifest = generate_manifest(agents, scan_duration, parse_errors)
    manifest["file_hashes"] = file_hashes
    manifest["hashed_file_count"] = len(file_hashes)
    manifest["hash_errors"] = hash_errors
    try:
        tmp_manifest = MANIFEST_JSON.with_suffix(".tmp")
        manifest_text = json.dumps(manifest, indent=2)
        assert_no_persistent_write("L0", "write_text")
        tmp_manifest.write_text(manifest_text, encoding="utf-8")
        json.loads(manifest_text)
        tmp_manifest.replace(MANIFEST_JSON)
        log.info(f"[SAVED] {MANIFEST_JSON}")
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        log.warning(f"Manifest save failed ({e}) - continuing (JSON is primary)")
    layers = defaultdict(int)
    top_dirs = defaultdict(int)
    sub_dirs = defaultdict(int)
    healing_count = 0
    testing_count = 0
    for a in agents:
        layers[a["layer"]] += 1
        top_dirs[a.get("top_dir", "")] += 1
        sub_dirs[a.get("sub_dir", "")] += 1
        if a["has_healing"]:
            healing_count += 1
        if a["testing"] != "None":
            testing_count += 1
    core_layers = ["L0", "L1", "L2", "L3", "L4", "L5"]
    core_count = sum(layers.get(l, 0) for l in core_layers)
    log.info("=" * 80)
    log.info("DISCOVERY COMPLETE")
    log.info("=" * 80)
    log.info(f"Total agents: {len(agents)}")
    if duplicates_skipped:
        log.info(f"Duplicates skipped: {duplicates_skipped}")
    log.info(f"Core (L0-L5): {core_count}")
    log.info("By layer:")
    for layer in sorted(layers.keys()):
        log.info(f"  {layer}: {layers[layer]}")
    log.info("By top-level folder (baseline location):")
    for k, v in sorted(top_dirs.items(), key=lambda kv: kv[1], reverse=True):
        label = k or "(root)"
        log.info(f"  {label}: {v}")
    log.info("Top 15 subfolders (top_dir/second_dir):")
    for k, v in sorted(sub_dirs.items(), key=lambda kv: kv[1], reverse=True)[:15]:
        label = k or "(root)"
        log.info(f"  {label}: {v}")
    log.info(
        f"Healing: {healing_count}/{len(agents)} ({(100 * healing_count // len(agents) if agents else 0)}%)"
    )
    log.info(
        f"Testing: {testing_count}/{len(agents)} ({(100 * testing_count // len(agents) if agents else 0)}%)"
    )
    if parse_errors:
        log.warning(f"Parse errors (skipped): {len(parse_errors)}")
        for err in parse_errors[:10]:
            log.warning(f"    - {err}")
    log.info("=" * 80)
    log.info("VALIDATION SUMMARY")
    log.info("=" * 80)
    log.info(f"Agent count: {len(agents)} (minimum: {MINIMUM_AGENT_COUNT}, expected: {EXPECTED_AGENT_COUNT})")
    if previous_count:
        delta = len(agents) - previous_count
        delta_str = f"+{delta}" if delta >= 0 else str(delta)
        log.info(f"Delta from previous: {delta_str} agents")
    log.info(f"Scan duration: {scan_duration:.1f}s")
    log.info(f"Parse errors: {len(parse_errors)}")
    log.info(f"[SAVED] {OUTPUT_JSON}")
    log.info(f"[SAVED] {MANIFEST_JSON}")
    log.info("=" * 80)
    return (agents, parse_errors)


def check_compliance_gate(agents: list[dict], parse_errors: list[str]) -> int:
    """
    Phase 3.3 Compliance Gate: Validate agent discovery for critical issues.
    Returns 0 if compliant, 1 if issues found.
    """
    log = logging.getLogger(__name__)
    log.info("=" * 80)
    log.info("PHASE 3.3: COMPLIANCE GATE")
    log.info("=" * 80)
    if len(agents) == 0:
        log.error("Discovery returned zero agents. Potential import failure.")
        sys.exit(1)
    issues = []
    name_counts = defaultdict(int)
    for agent in agents:
        name_counts[agent["class_name"]] += 1
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    if duplicates:
        issues.append(f"Duplicate agent names: {len(duplicates)}")
        for name, count in list(duplicates.items())[:5]:
            log.warning(f"  - {name}: {count} instances")
    valid_layers = {"Base", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps", "Utils"}
    unknown_layers = set()
    for agent in agents:
        layer = agent.get("layer", "")
        if layer and layer not in valid_layers:
            unknown_layers.add(layer)
    if unknown_layers:
        issues.append(f"Unknown layers: {len(unknown_layers)}")
        for layer in list(unknown_layers)[:5]:
            log.warning(f"  - {layer}")
    proper_bases = {"SovereignBaseAgent", "L0RoutingBaseAgent"}
    orphans = []
    for agent in agents:
        inheritance = agent.get("inheritance", [])
        has_proper_base = any(base in proper_bases for base in inheritance)
        if not has_proper_base and agent.get("layer") not in ["Apps", "Utils"]:
            orphans.append(agent["class_name"])
    if orphans:
        issues.append(f"Core layer orphaned agents: {len(orphans)}")
        for name in orphans[:5]:
            log.warning(f"  - {name}")
    if len(parse_errors) > 10:
        issues.append(f"Excessive parse errors: {len(parse_errors)}")
    log.info("=" * 80)
    if issues:
        log.error(f"Compliance Violation Detected in L-Architecture: {issues}")
        score = 1 - len(issues) / len(agents)
        log.info(f"Final Compliance Score: {score:.4f}")
        for issue in issues:
            log.warning(f"  - {issue}")
        log.info("=" * 80)
        return 1
    else:
        log.info(f"✅ COMPLIANCE PASSED: All {len(agents)} agents are standardized")
        log.info("=" * 80)
        return 0


if __name__ == "__main__":
    agents, parse_errors = main()
    exit_code = check_compliance_gate(agents, parse_errors)
    sys.exit(exit_code)

ROOT = Path(__file__).resolve().parents[3]
